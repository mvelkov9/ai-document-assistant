from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.models.question_answer import QuestionAnswer
from app.models.user import User
from app.schemas.auth import UserPublic

router = APIRouter(prefix="/admin")

VALID_ROLES = {"user", "admin"}


class SetRoleRequest(BaseModel):
    role: str = Field(..., examples=["admin"], description="New role: user or admin")


def require_admin(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user


@router.get(
    "/users",
    summary="List all users (admin only)",
    description="Return a list of all registered users. Requires admin role.",
)
def list_users(
    db: Session = Depends(get_db),
    admin: UserPublic = Depends(require_admin),
) -> list[UserPublic]:
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserPublic.model_validate(u) for u in users]


@router.get(
    "/stats",
    summary="System statistics (admin only)",
    description="Return rich aggregate statistics: counts, storage usage, status breakdown, per-source Q&A counts.",
)
def system_stats(
    db: Session = Depends(get_db),
    admin: UserPublic = Depends(require_admin),
) -> dict:
    user_count = db.query(func.count(User.id)).scalar()
    doc_count = db.query(func.count(Document.id)).scalar()
    summary_count = db.query(func.count(Document.id)).filter(Document.summary_text.isnot(None)).scalar()
    qa_count = db.query(func.count(QuestionAnswer.id)).scalar()
    job_count = db.query(func.count(ProcessingJob.id)).scalar()

    # Storage usage
    total_bytes = db.query(func.coalesce(func.sum(Document.size_bytes), 0)).scalar()

    # Document status breakdown
    status_rows = (
        db.query(Document.processing_status, func.count(Document.id))
        .group_by(Document.processing_status)
        .all()
    )
    status_breakdown = {row[0]: row[1] for row in status_rows}

    # Q&A source mode breakdown
    source_rows = (
        db.query(QuestionAnswer.source_mode, func.count(QuestionAnswer.id))
        .group_by(QuestionAnswer.source_mode)
        .all()
    )
    source_breakdown = {row[0]: row[1] for row in source_rows}

    # Job status breakdown
    job_rows = (
        db.query(ProcessingJob.status, func.count(ProcessingJob.id))
        .group_by(ProcessingJob.status)
        .all()
    )
    job_breakdown = {row[0]: row[1] for row in job_rows}

    # Admin vs user count
    admin_count = db.query(func.count(User.id)).filter(User.role == "admin").scalar()

    return {
        "users": user_count,
        "admins": admin_count,
        "documents": doc_count,
        "summaries": summary_count,
        "questions": qa_count,
        "jobs": job_count,
        "total_storage_bytes": total_bytes,
        "status_breakdown": status_breakdown,
        "source_breakdown": source_breakdown,
        "job_breakdown": job_breakdown,
    }


@router.patch(
    "/users/{user_id}/role",
    response_model=UserPublic,
    summary="Set user role (admin only)",
    description="Change a user's role. Valid roles: user, admin.",
)
def set_user_role(
    user_id: str,
    payload: SetRoleRequest,
    db: Session = Depends(get_db),
    admin: UserPublic = Depends(require_admin),
) -> UserPublic:
    if payload.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Choose from: {', '.join(sorted(VALID_ROLES))}",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role.",
        )
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)
