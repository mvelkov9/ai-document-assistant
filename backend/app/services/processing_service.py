from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.schemas.job import ProcessingJobPublic
from app.services.document_service import DocumentService


class ProcessingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ProcessingJobRepository(db)

    def create_summary_job(self, owner_id: str, document_id: str) -> ProcessingJobPublic:
        job = self.repository.create(owner_id=owner_id, document_id=document_id, job_type="summary")
        return ProcessingJobPublic.model_validate(job)

    def create_question_job(self, owner_id: str, document_id: str, question: str) -> ProcessingJobPublic:
        job = self.repository.create(
            owner_id=owner_id,
            document_id=document_id,
            job_type="question",
            job_input=question,
        )
        return ProcessingJobPublic.model_validate(job)

    def get_job(self, owner_id: str, job_id: str) -> ProcessingJobPublic | None:
        job = self.repository.get_for_owner(job_id, owner_id)
        if not job:
            return None
        return ProcessingJobPublic.model_validate(job)

    async def run_summary_job(self, job_id: str) -> None:
        db = SessionLocal()
        try:
            repository = ProcessingJobRepository(db)
            job = repository.get_by_id(job_id)
            if not job:
                return

            repository.mark_running(job)
            try:
                document_service = DocumentService(db)
                document = await document_service.summarize_document_for_owner(job.owner_id, job.document_id)
                repository.mark_completed(job, document.summary_text)
            except Exception as exc:
                job = repository.get_by_id(job_id)
                if job:
                    repository.mark_failed(job, str(exc))
        finally:
            db.close()

    async def run_question_job(self, job_id: str) -> None:
        db = SessionLocal()
        try:
            repository = ProcessingJobRepository(db)
            job = repository.get_by_id(job_id)
            if not job:
                return

            repository.mark_running(job)
            try:
                document_service = DocumentService(db)
                answer = await document_service.ask_document_question_for_owner(
                    job.owner_id,
                    job.document_id,
                    job.job_input or "",
                )
                repository.mark_completed(job, answer.answer_text)
            except Exception as exc:
                job = repository.get_by_id(job_id)
                if job:
                    repository.mark_failed(job, str(exc))
        finally:
            db.close()
