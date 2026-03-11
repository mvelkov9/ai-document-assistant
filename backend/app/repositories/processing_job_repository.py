from datetime import UTC, datetime

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.processing_job import ProcessingJob


class ProcessingJobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        owner_id: str,
        document_id: str,
        job_type: str,
        job_input: str | None = None,
    ) -> ProcessingJob:
        job = ProcessingJob(
            owner_id=owner_id,
            document_id=document_id,
            job_type=job_type,
            job_input=job_input,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_for_owner(self, job_id: str, owner_id: str) -> ProcessingJob | None:
        statement = select(ProcessingJob).where(
            ProcessingJob.id == job_id,
            ProcessingJob.owner_id == owner_id,
        )
        return self.db.scalar(statement)

    def get_by_id(self, job_id: str) -> ProcessingJob | None:
        statement = select(ProcessingJob).where(ProcessingJob.id == job_id)
        return self.db.scalar(statement)

    def mark_running(self, job: ProcessingJob) -> ProcessingJob:
        job.status = "running"
        job.error_message = None
        job.result_text = None
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_completed(self, job: ProcessingJob, result_text: str | None = None) -> ProcessingJob:
        job.status = "completed"
        job.error_message = None
        job.result_text = result_text
        job.completed_at = datetime.now(UTC)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_failed(self, job: ProcessingJob, error_message: str) -> ProcessingJob:
        job.status = "failed"
        job.error_message = error_message
        job.completed_at = datetime.now(UTC)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_for_document(self, document_id: str, *, auto_commit: bool = True) -> None:
        statement = sa_delete(ProcessingJob).where(ProcessingJob.document_id == document_id)
        self.db.execute(statement)
        if auto_commit:
            self.db.commit()
