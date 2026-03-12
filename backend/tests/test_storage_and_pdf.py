"""Tests for StorageService error handling and PdfService extraction."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from minio.error import S3Error

from app.services.pdf_service import PdfService
from app.services.storage_service import StorageService

# ── StorageService ───────────────────────────────────────────────


class TestStorageService:
    @patch("app.services.storage_service.Minio")
    def test_upload_bytes_calls_put_object(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_cls.return_value = mock_client

        svc = StorageService()
        svc.upload_bytes("test/key.pdf", b"content", "application/pdf")

        mock_client.put_object.assert_called_once()
        args = mock_client.put_object.call_args
        assert args.kwargs["bucket_name"] == svc.bucket_name
        assert args.kwargs["object_name"] == "test/key.pdf"

    @patch("app.services.storage_service.Minio")
    def test_download_bytes_success(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_response = MagicMock()
        mock_response.read.return_value = b"file-content"
        mock_client.get_object.return_value = mock_response
        mock_minio_cls.return_value = mock_client

        svc = StorageService()
        result = svc.download_bytes("test/key.pdf")

        assert result == b"file-content"
        mock_response.close.assert_called_once()
        mock_response.release_conn.assert_called_once()

    @patch("app.services.storage_service.Minio")
    def test_download_bytes_s3_error(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_client.get_object.side_effect = S3Error("NoSuchKey", "Object not found", "test", "test", "test", "test")
        mock_minio_cls.return_value = mock_client

        svc = StorageService()
        with pytest.raises(RuntimeError, match="Storage download failed"):
            svc.download_bytes("missing/key.pdf")

    @patch("app.services.storage_service.Minio")
    def test_delete_object_success(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_cls.return_value = mock_client

        svc = StorageService()
        svc.delete_object("test/key.pdf")

        mock_client.remove_object.assert_called_once_with(svc.bucket_name, "test/key.pdf")

    @patch("app.services.storage_service.Minio")
    def test_delete_object_s3_error(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_client.remove_object.side_effect = S3Error("AccessDenied", "Access denied", "test", "test", "test", "test")
        mock_minio_cls.return_value = mock_client

        svc = StorageService()
        with pytest.raises(RuntimeError, match="Storage delete failed"):
            svc.delete_object("test/key.pdf")

    @patch("app.services.storage_service.Minio")
    def test_check_connection_success(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_cls.return_value = mock_client

        svc = StorageService()
        assert svc.check_connection() is True

    @patch("app.services.storage_service.Minio")
    def test_ensure_bucket_creates_when_missing(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = False
        mock_minio_cls.return_value = mock_client

        svc = StorageService()
        svc._ensure_bucket()

        mock_client.make_bucket.assert_called_once_with(svc.bucket_name)

    @patch("app.services.storage_service.Minio")
    def test_ensure_bucket_s3_error(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.side_effect = S3Error(
            "NetworkError", "Connection refused", "test", "test", "test", "test"
        )
        mock_minio_cls.return_value = mock_client

        svc = StorageService()
        with pytest.raises(RuntimeError, match="Storage initialization failed"):
            svc._ensure_bucket()


# ── PdfService ───────────────────────────────────────────────────


class TestPdfService:
    def test_extract_text_returns_string(self):
        """PdfService.extract_text returns a string for valid PDF content."""
        from unittest.mock import MagicMock
        from unittest.mock import patch as _patch

        svc = PdfService()
        # Mock PdfReader to avoid needing a real PDF with proper fonts
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Hello world from PDF"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        with _patch("app.services.pdf_service.PdfReader", return_value=mock_reader):
            result = svc.extract_text(b"fake-pdf-bytes")

        assert "Hello world from PDF" in result

    def test_extract_text_layout_fallback_when_short(self):
        """When standard extraction yields < 50 chars, layout mode is tried."""
        from unittest.mock import MagicMock
        from unittest.mock import patch as _patch

        svc = PdfService()
        mock_page = MagicMock()
        # Standard mode returns short text, layout mode returns longer text
        mock_page.extract_text.side_effect = lambda **kw: (
            "Longer text in layout mode that exceeds fifty chars threshold easily"
            if kw.get("extraction_mode") == "layout"
            else "Short"
        )
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        with _patch("app.services.pdf_service.PdfReader", return_value=mock_reader):
            result = svc.extract_text(b"fake-pdf-bytes")

        assert "layout mode" in result

    def test_extract_text_corrupted_pdf(self):
        """Test that corrupted PDF raises an exception."""
        svc = PdfService()
        with pytest.raises(Exception):
            svc.extract_text(b"not a pdf at all")

    def test_extract_text_empty_bytes(self):
        """Test that empty bytes raises an exception."""
        svc = PdfService()
        with pytest.raises(Exception):
            svc.extract_text(b"")


# ── Integration: summarize with empty PDF text ───────────────────


def test_summarize_empty_pdf_returns_422(client, auth_headers, mock_storage, monkeypatch):
    """Summarizing a PDF with no extractable text should return 422."""
    from app.services import pdf_service as pdf_mod

    monkeypatch.setattr(pdf_mod.PdfService, "extract_text", lambda self, c: "")

    files = {"file": ("empty.pdf", BytesIO(b"%PDF-1.4 empty"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    doc_id = upload.json()["id"]

    resp = client.post(f"/api/v1/documents/{doc_id}/summarize", headers=auth_headers)
    assert resp.status_code == 422
    assert "machine-readable text" in resp.json()["detail"]


def test_ask_empty_pdf_returns_422(client, auth_headers, mock_storage, monkeypatch):
    """Asking a question on a PDF with no text should return 422."""
    from app.services import pdf_service as pdf_mod

    monkeypatch.setattr(pdf_mod.PdfService, "extract_text", lambda self, c: "   ")

    files = {"file": ("empty-qa.pdf", BytesIO(b"%PDF-1.4 empty"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    doc_id = upload.json()["id"]

    resp = client.post(
        f"/api/v1/documents/{doc_id}/ask",
        headers=auth_headers,
        json={"question": "What is this about?"},
    )
    assert resp.status_code == 422


def test_summarize_storage_failure_returns_503(client, auth_headers, monkeypatch):
    """If storage download fails during summarization, should return 503."""
    from app.services import document_service as ds_mod

    monkeypatch.setattr(ds_mod.StorageService, "upload_bytes", lambda self, k, c, ct: None)
    monkeypatch.setattr(
        ds_mod.StorageService,
        "download_bytes",
        lambda self, k: (_ for _ in ()).throw(RuntimeError("MinIO is down")),
    )

    files = {"file": ("fail.pdf", BytesIO(b"%PDF-1.4 fail"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    doc_id = upload.json()["id"]

    resp = client.post(f"/api/v1/documents/{doc_id}/summarize", headers=auth_headers)
    assert resp.status_code == 503


def test_ask_storage_failure_returns_503(client, auth_headers, monkeypatch):
    """If storage download fails during Q&A, should return 503."""
    from app.services import document_service as ds_mod

    monkeypatch.setattr(ds_mod.StorageService, "upload_bytes", lambda self, k, c, ct: None)
    monkeypatch.setattr(
        ds_mod.StorageService,
        "download_bytes",
        lambda self, k: (_ for _ in ()).throw(RuntimeError("Storage error")),
    )

    files = {"file": ("fail-qa.pdf", BytesIO(b"%PDF-1.4 fail"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    doc_id = upload.json()["id"]

    resp = client.post(
        f"/api/v1/documents/{doc_id}/ask",
        headers=auth_headers,
        json={"question": "What happens on failure?"},
    )
    assert resp.status_code == 503
