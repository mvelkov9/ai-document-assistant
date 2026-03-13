from contextlib import asynccontextmanager
from time import perf_counter

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.rate_limit import get_client_ip
from app.db.session import SessionLocal, init_db
from app.services.storage_service import StorageService

settings = get_settings()

# ── Structured logging ──
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger("docassist")

limiter = Limiter(
    key_func=get_client_ip,
    enabled=settings.app_env != "test",
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.project_name,
    version="1.5.3",
    lifespan=lifespan,
    description=(
        "REST API for the AI Document Assistant — a semester project at ALMA MATER EUROPAEA.\n\n"
        "**Core features:**\n"
        "- JWT authentication with role-based access control (user / admin)\n"
        "- PDF document upload, storage (MinIO), download and in-app viewing\n"
        "- Portfolio command center with document rankings, readiness insights and action items\n"
        "- AI-powered document summarization (Groq → Gemini → OpenAI → heuristic fallback)\n"
        "- RAG-lite document Q&A with BM25 segment ranking\n"
        "- Async background job processing with polling\n"
        "- Tristage PDF text extraction: PyMuPDF → pypdf → Tesseract OCR\n"
        "- Admin dashboard with system statistics and user management\n"
        "- Prometheus metrics, structured logging, health & readiness checks\n"
        "- Rate limiting on auth and AI endpoints\n\n"
        "**Endpoints:** 25 REST endpoints organized in auth, documents, jobs, admin, health and monitoring groups."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error. Check your request parameters."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred."},
    )


app.include_router(api_router, prefix=settings.api_prefix)

# ── Prometheus metrics ──
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["monitoring"])
except ImportError:
    pass  # Optional dependency


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    started_at = perf_counter()
    response = await call_next(request)
    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
    )
    return response


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Return a simple health status to confirm the backend is running.",
)
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.get(
    "/ready",
    tags=["health"],
    summary="Readiness check",
    description="Verify database and object storage connectivity. Returns 503 if a dependency is unavailable.",
)
def readiness() -> JSONResponse:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        storage = StorageService()
        storage.check_connection()
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not-ready",
                "detail": str(exc),
            },
        )
    finally:
        db.close()

    return JSONResponse(content={"status": "ready", "environment": settings.app_env})
