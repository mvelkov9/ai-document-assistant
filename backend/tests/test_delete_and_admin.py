"""Tests for delete endpoint, admin set-role endpoint, and cascade operations."""

from io import BytesIO

from tests.conftest import _register_and_login


def _make_admin(email):
    """Promote a user to admin directly in the test DB."""
    from app.db import session as session_module
    from app.models.user import User

    db = session_module.SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        user.role = "admin"
        db.commit()
    finally:
        db.close()


# ── Delete Document ──────────────────────────────────────────────


def test_delete_document_success(client, auth_headers, mock_storage, monkeypatch):
    from app.services import document_service as ds_mod

    monkeypatch.setattr(ds_mod.StorageService, "delete_object", lambda self, key: None)

    files = {"file": ("del.pdf", BytesIO(b"%PDF-1.4 del"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    assert upload.status_code == 201
    doc_id = upload.json()["id"]

    resp = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert resp.status_code == 204

    # Verify it's actually gone
    get_resp = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_delete_nonexistent_document(client, auth_headers, mock_storage):
    resp = client.delete("/api/v1/documents/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_other_users_document(client, mock_storage, monkeypatch):
    from app.services import document_service as ds_mod

    monkeypatch.setattr(ds_mod.StorageService, "delete_object", lambda self, key: None)

    headers_a = _register_and_login(client, "delete-a@example.com")
    files = {"file": ("a.pdf", BytesIO(b"%PDF-1.4 A"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=headers_a, files=files)
    doc_id = upload.json()["id"]

    headers_b = _register_and_login(client, "delete-b@example.com")
    resp = client.delete(f"/api/v1/documents/{doc_id}", headers=headers_b)
    assert resp.status_code == 404


def test_delete_document_without_auth(client, mock_storage):
    resp = client.delete("/api/v1/documents/some-id")
    assert resp.status_code == 403


def test_delete_cascades_qa_and_jobs(client, auth_headers, mock_storage, mock_ai, monkeypatch):
    """Deleting a document also removes associated Q&A records and jobs."""
    from app.services import document_service as ds_mod
    from app.services import processing_service as ps_mod

    monkeypatch.setattr(ds_mod.StorageService, "delete_object", lambda self, key: None)

    async def _noop(self, job_id):
        return None

    monkeypatch.setattr(ps_mod.ProcessingService, "run_summary_job", _noop)
    monkeypatch.setattr(ps_mod.ProcessingService, "run_question_job", _noop)

    files = {"file": ("cascade.pdf", BytesIO(b"%PDF-1.4 cascade"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    doc_id = upload.json()["id"]

    # Ask a question (creates a Q&A record)
    client.post(
        f"/api/v1/documents/{doc_id}/ask",
        headers=auth_headers,
        json={"question": "What is this document about?"},
    )

    # Create a job
    client.post(f"/api/v1/documents/{doc_id}/summarize-jobs", headers=auth_headers)

    # Now delete
    resp = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert resp.status_code == 204

    # Document gone
    get_resp = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_delete_document_storage_failure_still_deletes(client, auth_headers, mock_storage, monkeypatch):
    """Even if storage delete fails, the DB records should be deleted."""
    from app.services import document_service as ds_mod

    def _fail_delete(self, key):
        raise RuntimeError("Storage gone")

    monkeypatch.setattr(ds_mod.StorageService, "delete_object", _fail_delete)

    files = {"file": ("fail-storage.pdf", BytesIO(b"%PDF-1.4 fail"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    doc_id = upload.json()["id"]

    # Should still succeed (storage error is swallowed)
    resp = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert resp.status_code == 204


# ── Admin Set Role ───────────────────────────────────────────────


def test_admin_set_user_role(client, mock_storage):
    admin_headers = _register_and_login(client, "role-admin@example.com")
    _make_admin("role-admin@example.com")

    user_headers = _register_and_login(client, "role-target@example.com")
    # Get target user info
    user_resp = client.get("/api/v1/auth/me", headers=user_headers)
    target_user_id = user_resp.json()["id"]

    # Promote to admin
    resp = client.patch(
        f"/api/v1/admin/users/{target_user_id}/role",
        headers=admin_headers,
        json={"role": "admin"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"

    # Demote back to user
    resp = client.patch(
        f"/api/v1/admin/users/{target_user_id}/role",
        headers=admin_headers,
        json={"role": "user"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "user"


def test_admin_cannot_change_own_role(client, mock_storage):
    admin_headers = _register_and_login(client, "selfchange@example.com")
    _make_admin("selfchange@example.com")

    me_resp = client.get("/api/v1/auth/me", headers=admin_headers)
    admin_id = me_resp.json()["id"]

    resp = client.patch(
        f"/api/v1/admin/users/{admin_id}/role",
        headers=admin_headers,
        json={"role": "user"},
    )
    assert resp.status_code == 400
    assert "own role" in resp.json()["detail"].lower()


def test_admin_invalid_role_rejected(client, mock_storage):
    admin_headers = _register_and_login(client, "invalidrole@example.com")
    _make_admin("invalidrole@example.com")

    user_headers = _register_and_login(client, "target-invalid@example.com")
    user_resp = client.get("/api/v1/auth/me", headers=user_headers)
    target_id = user_resp.json()["id"]

    resp = client.patch(
        f"/api/v1/admin/users/{target_id}/role",
        headers=admin_headers,
        json={"role": "superadmin"},
    )
    assert resp.status_code == 400
    assert "Invalid role" in resp.json()["detail"]


def test_admin_set_role_nonexistent_user(client, mock_storage):
    admin_headers = _register_and_login(client, "roleadmin2@example.com")
    _make_admin("roleadmin2@example.com")

    resp = client.patch(
        "/api/v1/admin/users/nonexistent-user-id/role",
        headers=admin_headers,
        json={"role": "admin"},
    )
    assert resp.status_code == 404


def test_set_role_forbidden_for_regular_user(client, mock_storage):
    _register_and_login(client, "target-norole@example.com")
    user_headers = _register_and_login(client, "norole@example.com")

    resp = client.patch(
        "/api/v1/admin/users/some-user-id/role",
        headers=user_headers,
        json={"role": "admin"},
    )
    assert resp.status_code == 403
