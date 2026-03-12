import os

# Disable rate limiting for tests — must be set before app modules are imported
os.environ["APP_ENV"] = "test"

# Resolve the database host: CI uses localhost, Docker uses the 'postgres' hostname.
_DB_HOST = os.environ.get("DB_TEST_HOST", "postgres")
_BASE_URL = f"postgresql+psycopg://docassist:docassist@{_DB_HOST}:5432"

# Point to a dedicated test database BEFORE any app module is imported.
os.environ["DATABASE_URL"] = f"{_BASE_URL}/docassist_test"

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.services import document_service as document_service_module
from app.services import pdf_service as pdf_service_module
from app.services import processing_service as processing_service_module
from app.services import summary_service as summary_service_module

# ── Create the test database if it doesn't exist yet ─────────────
_admin_engine = create_engine(f"{_BASE_URL}/docassist", isolation_level="AUTOCOMMIT", future=True)
with _admin_engine.connect() as _conn:
    exists = _conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'docassist_test'")).scalar()
    if not exists:
        _conn.execute(text("CREATE DATABASE docassist_test"))
_admin_engine.dispose()


_TEST_DB_URL = f"{_BASE_URL}/docassist_test"


@pytest.fixture(autouse=True)
def test_environment(monkeypatch):
    from app.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("DATABASE_URL", _TEST_DB_URL)
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("MINIO_ENDPOINT", "localhost:9000")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "minioadmin")
    monkeypatch.setenv("MINIO_SECRET_KEY", "minioadmin")
    monkeypatch.setenv("MINIO_BUCKET", "documents")
    monkeypatch.setenv("MINIO_SECURE", "false")
    monkeypatch.setenv("SUMMARY_MAX_CHARS", "6000")
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()


@pytest.fixture
def client(test_environment):
    from app.core.config import get_settings
    from app.db import session as session_module
    from app.db.base import Base
    from app.main import app

    get_settings.cache_clear()

    # Build a fresh engine targeting the dedicated test database
    test_engine = create_engine(_TEST_DB_URL, future=True)
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    # Swap into the session module so the app uses the test DB
    orig_engine = session_module.engine
    orig_session = session_module.SessionLocal
    session_module.engine = test_engine
    session_module.SessionLocal = test_session_local

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with TestClient(app) as test_client:
        yield test_client

    # Restore originals
    session_module.engine = orig_engine
    session_module.SessionLocal = orig_session
    get_settings.cache_clear()


@pytest.fixture
def mock_storage(monkeypatch):
    """Mock MinIO storage upload/download so tests don't need a live bucket."""
    monkeypatch.setattr(
        document_service_module.StorageService,
        "upload_bytes",
        lambda self, key, content, ct: None,
    )
    monkeypatch.setattr(
        document_service_module.StorageService,
        "download_bytes",
        lambda self, key: b"%PDF-1.4 test-content",
    )


@pytest.fixture
def mock_ai(monkeypatch):
    """Mock PDF extraction and AI summary/Q&A services."""
    monkeypatch.setattr(
        pdf_service_module.PdfService,
        "extract_text",
        lambda self, content: "Extracted document text for testing purposes.",
    )

    async def _fake_summarize(self, text):
        return "Test summary of the document."

    async def _fake_answer(self, text, question):
        return ("Test answer to the question.", "fallback")

    monkeypatch.setattr(summary_service_module.SummaryService, "summarize", _fake_summarize)
    monkeypatch.setattr(summary_service_module.SummaryService, "answer_question", _fake_answer)


@pytest.fixture
def mock_background_jobs(monkeypatch):
    """Mock background job runners so they don't actually execute."""

    async def _noop(self, job_id):
        return None

    monkeypatch.setattr(processing_service_module.ProcessingService, "run_summary_job", _noop)
    monkeypatch.setattr(processing_service_module.ProcessingService, "run_question_job", _noop)


def _register_and_login(client, email="test@example.com", password="VerySecure123"):
    """Helper: register a user and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client):
    """Return auth headers for a default test user."""
    return _register_and_login(client)


@pytest.fixture
def upload_document(client, auth_headers, mock_storage):
    """Upload a sample PDF and return the document JSON."""
    files = {"file": ("test.pdf", BytesIO(b"%PDF-1.4 sample"), "application/pdf")}
    resp = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    assert resp.status_code == 201
    return resp.json()
