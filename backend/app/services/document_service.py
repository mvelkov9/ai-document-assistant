from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories.document_repository import DocumentRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.repositories.question_answer_repository import QuestionAnswerRepository
from app.schemas.auth import UserPublic
from app.schemas.document import DocumentPublic, QuestionAnswerPublic
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

        document = self.repository.create(
            owner_id=current_user.id,
            original_filename=filename,
            storage_key=storage_key,
            content_type=content_type,
            size_bytes=len(content),
        )
        return DocumentPublic.model_validate(document)

    def list_documents(
        self, current_user: UserPublic, *, skip: int = 0, limit: int = 20
    ) -> tuple[list[DocumentPublic], int]:
        documents = self.repository.list_for_owner(current_user.id, skip=skip, limit=limit)
        total = self.repository.count_for_owner(current_user.id)
        return [DocumentPublic.model_validate(d) for d in documents], total

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
