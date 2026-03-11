from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.status import StatusResponse



router = APIRouter()


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="API status and capabilities",
    description="Return current service status, environment info, and supported features.",
)
def get_status() -> StatusResponse:
    settings = get_settings()
    return StatusResponse(
        service="backend",
        project_name=settings.project_name,
        app_env=settings.app_env,
        api_prefix=settings.api_prefix,
        features=[
            "healthcheck and readiness endpoints",
            "structured JSON logging (structlog)",
            "Prometheus metrics (/metrics)",
            "JWT authentication (register/login/me)",
            "role-based admin endpoints (users, stats)",
            "PDF document upload, download, and paginated listing",
            "AI summary generation (provider + fallback)",
            "RAG-lite document Q&A (BM25 chunk ranking)",
            "async processing jobs with polling",
            "rate limiting (auth 5/min, AI 10/min)",
            "OpenAPI docs with endpoint descriptions",
        ],
    )

