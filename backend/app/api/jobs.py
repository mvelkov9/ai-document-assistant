from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.schemas.auth import UserPublic
from app.schemas.job import ProcessingJobPublic
from app.services.processing_service import ProcessingService

router = APIRouter(prefix="/jobs")


@router.get(
    "/{job_id}",
    response_model=ProcessingJobPublic,
    summary="Get processing job status",
    description="Check the status of an async processing job (queued, running, completed, failed).",
)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
) -> ProcessingJobPublic:
    service = ProcessingService(db)
    job = service.get_job(current_user.id, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job
