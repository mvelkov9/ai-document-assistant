from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.auth import UserPublic
from app.schemas.document import (
    DocumentListResponse,
    DocumentPublic,
    DocumentQuestionRequest,
    QuestionAnswerPublic,
)
from app.services.document_service import DocumentService
from app.services.processing_service import ProcessingService

_settings = get_settings()
router = APIRouter(prefix="/documents")
limiter = Limiter(key_func=get_remote_address, enabled=_settings.app_env != "test")


@router.post(
    "/upload",
    response_model=DocumentPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF document",
    description="Upload a PDF file (max 10 MB). The file is stored in MinIO and metadata persisted in PostgreSQL.",
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
) -> DocumentPublic:
    service = DocumentService(db)
    return await service.upload_document(current_user, file)


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List user documents",
    description="Return a paginated list of documents owned by the authenticated user.",
)
def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
) -> DocumentListResponse:
    if limit > 100:
        limit = 100
    service = DocumentService(db)
    items, total = service.list_documents(current_user, skip=skip, limit=limit)
    return DocumentListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/{document_id}",
    response_model=DocumentPublic,
    summary="Get a single document",
    description="Retrieve metadata and summary of a specific document by ID.",
)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
) -> DocumentPublic:
    service = DocumentService(db)
    document = service.get_document(current_user, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return document


@router.post(
    "/{document_id}/summarize",
    response_model=DocumentPublic,
    summary="Summarize a document (sync)",
    description="Extract text from the PDF and generate an AI summary synchronously.",
)
@limiter.limit("10/minute")
async def summarize_document(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
) -> DocumentPublic:
    service = DocumentService(db)
    return await service.summarize_document(current_user, document_id)


@router.post(
    "/{document_id}/summarize-jobs",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Summarize a document (async job)",
    description="Queue a background job to summarize the document. Poll GET /jobs/{id} for status.",
)
@limiter.limit("10/minute")
async def create_summary_job(
    document_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    document_service = DocumentService(db)
    document = document_service.get_document(current_user, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    processing_service = ProcessingService(db)
    job = processing_service.create_summary_job(current_user.id, document_id)
    background_tasks.add_task(processing_service.run_summary_job, job.id)
    return job


@router.post(
    "/{document_id}/ask",
    response_model=QuestionAnswerPublic,
    summary="Ask a question about a document (sync)",
    description="Submit a question and receive an AI-generated answer based on the document content.",
)
@limiter.limit("10/minute")
async def ask_document_question(
    document_id: str,
    payload: DocumentQuestionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
) -> QuestionAnswerPublic:
    service = DocumentService(db)
    return await service.ask_document_question(current_user, document_id, payload.question)


@router.post(
    "/{document_id}/ask-jobs",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ask a question (async job)",
    description="Queue a background job to answer a question about the document. Poll GET /jobs/{id}.",
)
@limiter.limit("10/minute")
async def create_question_job(
    document_id: str,
    payload: DocumentQuestionRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    document_service = DocumentService(db)
    document = document_service.get_document(current_user, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    processing_service = ProcessingService(db)
    job = processing_service.create_question_job(current_user.id, document_id, payload.question)
    background_tasks.add_task(processing_service.run_question_job, job.id)
    return job


@router.get(
    "/{document_id}/download",
    summary="Download a document",
    description="Download the original PDF file from storage. Only the document owner can download.",
)
def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
) -> StreamingResponse:
    service = DocumentService(db)
    content, filename, content_type = service.download_document(current_user, document_id)
    from io import BytesIO
    return StreamingResponse(
        BytesIO(content),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Delete a document by ID, including its file in MinIO and all related Q&A records and jobs.",
)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
) -> None:
    service = DocumentService(db)
    service.delete_document(current_user, document_id)
