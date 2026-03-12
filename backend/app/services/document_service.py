from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories.document_repository import DocumentRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.repositories.question_answer_repository import QuestionAnswerRepository
from app.schemas.auth import UserPublic
from app.schemas.document import (
    DocumentInsightEntry,
    DocumentInsightsActivity,
    DocumentInsightsOverview,
    DocumentInsightsResponse,
    DocumentPublic,
    InsightActionItem,
    InsightBreakdownItem,
    QuestionAnswerPublic,
)
from app.services.pdf_service import PdfService
from app.services.storage_service import StorageService
from app.services.summary_service import SummaryService


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = DocumentRepository(db)
        self.qa_repository = QuestionAnswerRepository(db)
        self.job_repository = ProcessingJobRepository(db)
        self.storage = StorageService()
        self.settings = get_settings()
        self.pdf_service = PdfService()
        self.summary_service = SummaryService()

    @staticmethod
    def _resolve_idle_processing_status(summary_text: str | None) -> str:
        return "ready" if summary_text else "uploaded"

    @staticmethod
    def _pct(part: int, total: int) -> int:
        if total <= 0:
            return 0
        return round((part / total) * 100)

    def _build_document_insight(
        self,
        document,
        *,
        answer_count: int,
        now: datetime,
    ) -> DocumentInsightEntry:
        age_days = max((now - document.created_at).days, 0)
        recency_points = max(0, 15 - min(age_days, 15))
        summary_points = 35 if document.summary_text else 0
        answer_points = min(answer_count * 8, 24)
        tag_points = min(len(document.tags or []) * 5, 15)
        ready_points = 10 if document.processing_status == "ready" else 0
        score = min(summary_points + answer_points + tag_points + ready_points + recency_points, 100)

        badge = "fresh"
        reason_key = "fresh"
        if document.processing_status.endswith("failed"):
            badge = "attention"
            reason_key = "attention"
        elif not document.summary_text:
            badge = "next-step"
            reason_key = "next-step"
        elif answer_count >= 3:
            badge = "hot"
            reason_key = "hot"
        elif document.processing_status == "ready":
            badge = "ready"
            reason_key = "ready"

        return DocumentInsightEntry(
            id=document.id,
            original_filename=document.original_filename,
            processing_status=document.processing_status,
            size_bytes=document.size_bytes,
            created_at=document.created_at,
            tags=list(document.tags or []),
            has_summary=bool(document.summary_text),
            answer_count=answer_count,
            insight_score=score,
            badge=badge,
            reason_key=reason_key,
        )

    def _build_action_items(
        self,
        *,
        total_documents: int,
        failed_documents: int,
        summary_gap: int,
        tag_gap: int,
        question_gap: int,
    ) -> list[InsightActionItem]:
        if total_documents == 0:
            return [
                InsightActionItem(
                    key="start-workspace",
                    count=0,
                    severity="low",
                )
            ]

        action_items: list[InsightActionItem] = []
        if failed_documents:
            action_items.append(
                InsightActionItem(
                    key="resolve-failed-processing",
                    count=failed_documents,
                    severity="high",
                )
            )
        if summary_gap:
            action_items.append(
                InsightActionItem(
                    key="generate-missing-summaries",
                    count=summary_gap,
                    severity="high" if summary_gap >= max(2, total_documents // 2) else "medium",
                )
            )
        if tag_gap:
            action_items.append(
                InsightActionItem(
                    key="improve-document-labeling",
                    count=tag_gap,
                    severity="medium",
                )
            )
        if question_gap:
            action_items.append(
                InsightActionItem(
                    key="expand-document-interrogation",
                    count=question_gap,
                    severity="low",
                )
            )
        return action_items[:4]

    async def upload_document(self, current_user: UserPublic, upload_file: UploadFile) -> DocumentPublic:
        filename = upload_file.filename or "document.pdf"
        content_type = upload_file.content_type or "application/octet-stream"

        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF uploads are allowed.",
            )

        if content_type not in {"application/pdf", "application/x-pdf"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type. Expected PDF.",
            )

        content = await upload_file.read()
        max_size_bytes = self.settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds {self.settings.max_upload_size_mb} MB limit.",
            )

        safe_name = Path(filename).name.replace(" ", "-")
        storage_key = f"{current_user.id}/{uuid4()}-{safe_name}"

        try:
            self.storage.upload_bytes(storage_key, content, content_type)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

        try:
            document = self.repository.create(
                owner_id=current_user.id,
                original_filename=filename,
                storage_key=storage_key,
                content_type=content_type,
                size_bytes=len(content),
            )
        except Exception as exc:
            self.db.rollback()
            try:
                self.storage.delete_object(storage_key)
            except RuntimeError:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document metadata could not be persisted.",
            ) from exc

        return DocumentPublic.model_validate(document)

    def list_documents(
        self, current_user: UserPublic, *, skip: int = 0, limit: int = 20
    ) -> tuple[list[DocumentPublic], int]:
        documents = self.repository.list_for_owner(current_user.id, skip=skip, limit=limit)
        total = self.repository.count_for_owner(current_user.id)
        return [DocumentPublic.model_validate(d) for d in documents], total

    def get_document_insights(self, current_user: UserPublic) -> DocumentInsightsResponse:
        documents = self.repository.list_all_for_owner(current_user.id)
        document_ids = [document.id for document in documents]
        answers = self.qa_repository.list_for_documents(document_ids)
        answer_counts = Counter(answer.document_id for answer in answers)
        tag_counts = Counter(tag for document in documents for tag in (document.tags or []))
        status_counts = Counter(document.processing_status for document in documents)

        total_documents = len(documents)
        summary_documents = sum(1 for document in documents if document.summary_text)
        ready_documents = sum(1 for document in documents if document.processing_status == "ready")
        tagged_documents = sum(1 for document in documents if document.tags)
        documents_with_questions = sum(1 for document in documents if answer_counts.get(document.id, 0) > 0)
        total_questions = len(answers)
        total_size_bytes = sum(document.size_bytes for document in documents)

        summary_coverage_pct = self._pct(summary_documents, total_documents)
        tag_coverage_pct = self._pct(tagged_documents, total_documents)
        question_coverage_pct = self._pct(documents_with_questions, total_documents)
        ready_coverage_pct = self._pct(ready_documents, total_documents)
        workspace_score = round(
            (summary_coverage_pct * 0.35)
            + (question_coverage_pct * 0.25)
            + (tag_coverage_pct * 0.2)
            + (ready_coverage_pct * 0.2)
        )

        now = datetime.now(UTC)
        recent_cutoff = now - timedelta(days=7)
        uploads_last_7_days = sum(1 for document in documents if document.created_at >= recent_cutoff)
        questions_last_7_days = sum(1 for answer in answers if answer.created_at >= recent_cutoff)
        last_upload_at = max((document.created_at for document in documents), default=None)
        last_question_at = max((answer.created_at for answer in answers), default=None)

        enriched_documents = [
            self._build_document_insight(document, answer_count=answer_counts.get(document.id, 0), now=now)
            for document in documents
        ]

        needs_attention = [
            item
            for item in enriched_documents
            if item.processing_status.endswith("failed") or not item.has_summary or not item.tags
        ]
        ready_for_review = [
            item for item in enriched_documents if item.processing_status == "ready" and item.has_summary
        ]
        most_active_documents = sorted(
            enriched_documents,
            key=lambda item: (item.answer_count, item.insight_score, item.created_at),
            reverse=True,
        )
        recently_uploaded = sorted(enriched_documents, key=lambda item: item.created_at, reverse=True)

        failed_documents = sum(1 for document in documents if document.processing_status.endswith("failed"))
        action_items = self._build_action_items(
            total_documents=total_documents,
            failed_documents=failed_documents,
            summary_gap=total_documents - summary_documents,
            tag_gap=total_documents - tagged_documents,
            question_gap=total_documents - documents_with_questions,
        )

        return DocumentInsightsResponse(
            overview=DocumentInsightsOverview(
                total_documents=total_documents,
                ready_documents=ready_documents,
                summary_documents=summary_documents,
                tagged_documents=tagged_documents,
                documents_with_questions=documents_with_questions,
                total_questions=total_questions,
                total_size_bytes=total_size_bytes,
                workspace_score=workspace_score,
                summary_coverage_pct=summary_coverage_pct,
                tag_coverage_pct=tag_coverage_pct,
                question_coverage_pct=question_coverage_pct,
            ),
            activity=DocumentInsightsActivity(
                uploads_last_7_days=uploads_last_7_days,
                questions_last_7_days=questions_last_7_days,
                last_upload_at=last_upload_at,
                last_question_at=last_question_at,
            ),
            status_breakdown=[
                InsightBreakdownItem(label=label, count=count)
                for label, count in sorted(status_counts.items(), key=lambda item: (-item[1], item[0]))
            ],
            tag_breakdown=[
                InsightBreakdownItem(label=label, count=count)
                for label, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))[:8]
            ],
            action_items=action_items,
            most_active_documents=most_active_documents[:4],
            ready_for_review=sorted(
                ready_for_review,
                key=lambda item: (item.insight_score, item.answer_count, item.created_at),
                reverse=True,
            )[:4],
            needs_attention=sorted(
                needs_attention,
                key=lambda item: (item.badge == "attention", 100 - item.insight_score, item.created_at),
                reverse=True,
            )[:4],
            recently_uploaded=recently_uploaded[:4],
        )

    def get_document(self, current_user: UserPublic, document_id: str) -> DocumentPublic | None:
        document = self.repository.get_for_owner(document_id, current_user.id)
        if not document:
            return None
        return DocumentPublic.model_validate(document)

    def download_document(self, current_user: UserPublic, document_id: str) -> tuple[bytes, str, str]:
        document = self.repository.get_for_owner(document_id, current_user.id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
        content = self.storage.download_bytes(document.storage_key)
        return content, document.original_filename, document.content_type

    async def summarize_document_for_owner(self, owner_id: str, document_id: str) -> DocumentPublic:
        document = self.repository.get_for_owner(document_id, owner_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

        self.repository.update_processing(document, "summary-processing")

        try:
            content = self.storage.download_bytes(document.storage_key)
            extracted_text = self.pdf_service.extract_text(content)

            if not extracted_text.strip():
                self.repository.update_processing(document, "summary-failed")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Document does not contain enough machine-readable text for summarization. "
                    "The PDF may be scanned or image-based. OCR is not yet supported.",
                )

            summary_text = await self.summary_service.summarize(extracted_text)
            updated = self.repository.update_summary(document, summary_text, "ready")
        except HTTPException:
            raise
        except RuntimeError as exc:
            self.repository.update_processing(document, "summary-failed")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            self.repository.update_processing(document, "summary-failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document summarization failed: {exc}",
            ) from exc

        return DocumentPublic.model_validate(updated)

    async def summarize_document(self, current_user: UserPublic, document_id: str) -> DocumentPublic:
        return await self.summarize_document_for_owner(current_user.id, document_id)

    async def ask_document_question(
        self,
        current_user: UserPublic,
        document_id: str,
        question: str,
    ) -> QuestionAnswerPublic:
        return await self.ask_document_question_for_owner(current_user.id, document_id, question)

    def list_answers(self, document_id: str) -> list[QuestionAnswerPublic]:
        records = self.qa_repository.list_for_document(document_id)
        return [QuestionAnswerPublic.model_validate(r) for r in records]

    def delete_answer(self, document_id: str, answer_id: str) -> bool:
        record = self.qa_repository.get_by_id(answer_id)
        if not record or record.document_id != document_id:
            return False
        return self.qa_repository.delete_by_id(answer_id)

    def clear_answers(self, document_id: str) -> None:
        self.qa_repository.delete_for_document(document_id)

    def update_tags(self, current_user: UserPublic, document_id: str, tags: list[str]) -> DocumentPublic:
        document = self.repository.get_for_owner(document_id, current_user.id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
        cleaned = list(dict.fromkeys(t.strip() for t in tags if t.strip()))[:20]
        updated = self.repository.update_tags(document, cleaned)
        return DocumentPublic.model_validate(updated)

    async def ask_document_question_for_owner(
        self,
        owner_id: str,
        document_id: str,
        question: str,
    ) -> QuestionAnswerPublic:
        cleaned_question = question.strip()
        if len(cleaned_question) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question must contain at least 3 characters.",
            )

        document = self.repository.get_for_owner(document_id, owner_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

        idle_status = self._resolve_idle_processing_status(document.summary_text)
        self.repository.update_processing(document, "question-processing")

        try:
            content = self.storage.download_bytes(document.storage_key)
            extracted_text = self.pdf_service.extract_text(content)

            if not extracted_text.strip():
                self.repository.update_processing(document, idle_status)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Document does not contain enough machine-readable text to answer questions. "
                    "The PDF may be scanned or image-based. OCR is not yet supported.",
                )

            answer_text, source_mode = await self.summary_service.answer_question(
                extracted_text,
                cleaned_question,
            )
            answer = self.qa_repository.create(
                document_id=document.id,
                question_text=cleaned_question,
                answer_text=answer_text,
                source_mode=source_mode,
            )
            self.repository.update_processing(document, idle_status)
        except HTTPException:
            raise
        except RuntimeError as exc:
            self.repository.update_processing(document, "question-failed")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            self.repository.update_processing(document, "question-failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document question-answer failed: {exc}",
            ) from exc

        return QuestionAnswerPublic.model_validate(answer)

    def delete_document(self, current_user: UserPublic, document_id: str) -> None:
        document = self.repository.get_for_owner(document_id, current_user.id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

        # Single transaction to avoid deadlocks
        self.qa_repository.delete_for_document(document.id, auto_commit=False)
        self.job_repository.delete_for_document(document.id, auto_commit=False)
        self.repository.delete(document, auto_commit=False)
        self.db.commit()

        try:
            self.storage.delete_object(document.storage_key)
        except RuntimeError:
            pass  # File may already be gone from storage
