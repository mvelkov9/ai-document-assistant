"""Tests for document endpoints: upload validation, access control, pagination, 404s."""

from io import BytesIO

from tests.conftest import _register_and_login

# ── Upload validation ──


def test_upload_non_pdf_rejected(client, auth_headers, mock_storage) -> None:
    files = {"file": ("readme.txt", BytesIO(b"plain text"), "text/plain")}
    resp = client.post("/api/v1/documents/upload", headers=auth_headers, files=files)
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]


def test_upload_without_auth(client) -> None:
    files = {"file": ("test.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")}
    resp = client.post("/api/v1/documents/upload", files=files)
    assert resp.status_code == 403


# ── Document retrieval ──


def test_get_nonexistent_document(client, auth_headers) -> None:
    resp = client.get("/api/v1/documents/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


def test_get_other_users_document(client, mock_storage) -> None:
    """User B cannot access User A's document."""
    headers_a = _register_and_login(client, email="usera@example.com")
    files = {"file": ("a.pdf", BytesIO(b"%PDF-1.4 A"), "application/pdf")}
    upload = client.post("/api/v1/documents/upload", headers=headers_a, files=files)
    doc_id = upload.json()["id"]

    headers_b = _register_and_login(client, email="userb@example.com")
    resp = client.get(f"/api/v1/documents/{doc_id}", headers=headers_b)
    assert resp.status_code == 404


# ── Pagination ──


def test_list_documents_pagination(client, auth_headers, mock_storage) -> None:
    for i in range(5):
        files = {"file": (f"doc{i}.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")}
        client.post("/api/v1/documents/upload", headers=auth_headers, files=files)

    resp = client.get("/api/v1/documents?skip=0&limit=3", headers=auth_headers)
    body = resp.json()
    assert resp.status_code == 200
    assert len(body["items"]) == 3
    assert body["total"] == 5
    assert body["skip"] == 0
    assert body["limit"] == 3


def test_list_documents_empty(client, auth_headers) -> None:
    resp = client.get("/api/v1/documents", headers=auth_headers)
    body = resp.json()
    assert resp.status_code == 200
    assert body["items"] == []
    assert body["total"] == 0


def test_list_documents_limit_capped(client, auth_headers) -> None:
    resp = client.get("/api/v1/documents?limit=999", headers=auth_headers)
    body = resp.json()
    assert resp.status_code == 200
    assert body["limit"] <= 100


def test_document_insights_empty_workspace(client, auth_headers) -> None:
    resp = client.get("/api/v1/documents/insights", headers=auth_headers)
    body = resp.json()

    assert resp.status_code == 200
    assert body["overview"]["total_documents"] == 0
    assert body["overview"]["workspace_score"] == 0
    assert body["action_items"][0]["severity"] == "low"
    assert body["action_items"][0]["key"] == "start-workspace"


def test_document_insights_aggregate_workspace_metrics(client, auth_headers, mock_storage, mock_ai) -> None:
    first_upload = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("analysis.pdf", BytesIO(b"%PDF-1.4 first"), "application/pdf")},
    )
    second_upload = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("notes.pdf", BytesIO(b"%PDF-1.4 second"), "application/pdf")},
    )
    first_id = first_upload.json()["id"]
    second_id = second_upload.json()["id"]

    tag_resp = client.patch(
        f"/api/v1/documents/{first_id}/tags",
        headers=auth_headers,
        json={"tags": ["analiza", "porocilo"]},
    )
    summary_resp = client.post(f"/api/v1/documents/{first_id}/summarize", headers=auth_headers)
    question_resp = client.post(
        f"/api/v1/documents/{first_id}/ask",
        headers=auth_headers,
        json={"question": "Kaj je glavno sporocilo dokumenta?"},
    )

    assert tag_resp.status_code == 200
    assert summary_resp.status_code == 200
    assert question_resp.status_code == 200

    insights_resp = client.get("/api/v1/documents/insights", headers=auth_headers)
    body = insights_resp.json()

    assert insights_resp.status_code == 200
    assert body["overview"]["total_documents"] == 2
    assert body["overview"]["ready_documents"] == 1
    assert body["overview"]["summary_documents"] == 1
    assert body["overview"]["tagged_documents"] == 1
    assert body["overview"]["documents_with_questions"] == 1
    assert body["overview"]["total_questions"] == 1
    assert body["activity"]["uploads_last_7_days"] == 2
    assert body["activity"]["questions_last_7_days"] == 1
    assert body["most_active_documents"][0]["id"] == first_id
    assert all(item["id"] != second_id or item["has_summary"] is False for item in body["recently_uploaded"])
    assert any(item["label"] == "ready" and item["count"] == 1 for item in body["status_breakdown"])
    assert any(item["label"] == "uploaded" and item["count"] == 1 for item in body["status_breakdown"])
    assert any(item["label"] == "analiza" and item["count"] == 1 for item in body["tag_breakdown"])
    assert any(item["key"] == "generate-missing-summaries" and item["count"] == 1 for item in body["action_items"])
    assert any(item["reason_key"] == "next-step" for item in body["recently_uploaded"] if item["id"] == second_id)


# ── Summarize / Q&A errors ──


def test_summarize_nonexistent_document(client, auth_headers) -> None:
    resp = client.post("/api/v1/documents/fake-id/summarize", headers=auth_headers)
    assert resp.status_code == 404


def test_ask_question_too_short(client, auth_headers, mock_storage, upload_document) -> None:
    doc_id = upload_document["id"]
    resp = client.post(
        f"/api/v1/documents/{doc_id}/ask",
        headers=auth_headers,
        json={"question": "Ab"},
    )
    assert resp.status_code == 422


def test_ask_question_too_long(client, auth_headers, mock_storage, upload_document) -> None:
    doc_id = upload_document["id"]
    resp = client.post(
        f"/api/v1/documents/{doc_id}/ask",
        headers=auth_headers,
        json={"question": "A" * 501},
    )
    assert resp.status_code == 422


# ── Jobs ──


def test_get_nonexistent_job(client, auth_headers) -> None:
    resp = client.get("/api/v1/jobs/nonexistent-job-id", headers=auth_headers)
    assert resp.status_code == 404
