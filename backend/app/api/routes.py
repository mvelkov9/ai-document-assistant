from fastapi import APIRouter

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.jobs import router as jobs_router
from app.api.status import router as status_router



api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(documents_router, tags=["documents"])
api_router.include_router(jobs_router, tags=["jobs"])
api_router.include_router(status_router, tags=["status"])
api_router.include_router(admin_router, tags=["admin"])
