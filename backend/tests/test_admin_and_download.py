"""Tests for admin endpoints and document download."""
from io import BytesIO


def _register_and_login(client, email='test@example.com', password='VerySecure123'):
    client.post(
        '/api/v1/auth/register',
        json={'email': email, 'password': password, 'full_name': 'Test User'},
    )
    resp = client.post(
        '/api/v1/auth/login',
        json={'email': email, 'password': password},
    )
    token = resp.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def _make_admin(email):
    """Promote a user to admin directly in the test DB."""
    from app.db import session as session_module
    from app.models.user import User

    db = session_module.SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        user.role = 'admin'
        db.commit()
    finally:
        db.close()


# ── Admin Tests ──


def test_admin_stats_as_admin(client, mock_storage):
    headers = _register_and_login(client, 'admin@example.com', 'VerySecure123')
    _make_admin('admin@example.com')
    resp = client.get('/api/v1/admin/stats', headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert 'users' in data
    assert 'documents' in data
    assert 'summaries' in data
    assert 'questions' in data
    assert 'jobs' in data
    assert data['users'] >= 1


def test_admin_users_as_admin(client, mock_storage):
    headers = _register_and_login(client, 'admin2@example.com', 'VerySecure123')
    _make_admin('admin2@example.com')
    resp = client.get('/api/v1/admin/users', headers=headers)
    assert resp.status_code == 200
    users = resp.json()
    assert len(users) >= 1
    assert users[0]['email'] == 'admin2@example.com'


def test_admin_stats_forbidden_for_regular_user(client):
    headers = _register_and_login(client, 'regular@example.com', 'VerySecure123')
    resp = client.get('/api/v1/admin/stats', headers=headers)
    assert resp.status_code == 403


def test_admin_users_forbidden_for_regular_user(client):
    headers = _register_and_login(client, 'regular2@example.com', 'VerySecure123')
    resp = client.get('/api/v1/admin/users', headers=headers)
    assert resp.status_code == 403


def test_admin_stats_unauthorized(client):
    resp = client.get('/api/v1/admin/stats')
    assert resp.status_code == 403


# ── Download Tests ──


def test_download_document(client, auth_headers, mock_storage):
    files = {'file': ('report.pdf', BytesIO(b'%PDF-1.4 sample'), 'application/pdf')}
    upload_resp = client.post('/api/v1/documents/upload', headers=auth_headers, files=files)
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json()['id']

    resp = client.get(f'/api/v1/documents/{doc_id}/download', headers=auth_headers)
    assert resp.status_code == 200
    assert 'report.pdf' in resp.headers.get('content-disposition', '')


def test_download_nonexistent_document(client, auth_headers, mock_storage):
    resp = client.get('/api/v1/documents/nonexistent-id/download', headers=auth_headers)
    assert resp.status_code == 404


def test_download_other_users_document(client, mock_storage):
    headers_a = _register_and_login(client, 'usera@example.com', 'VerySecure123')
    files = {'file': ('secret.pdf', BytesIO(b'%PDF-1.4 secret'), 'application/pdf')}
    upload_resp = client.post('/api/v1/documents/upload', headers=headers_a, files=files)
    doc_id = upload_resp.json()['id']

    headers_b = _register_and_login(client, 'userb@example.com', 'VerySecure123')
    resp = client.get(f'/api/v1/documents/{doc_id}/download', headers=headers_b)
    assert resp.status_code == 404


# ── Metrics Tests ──


def test_metrics_endpoint(client):
    resp = client.get('/metrics')
    # 200 if prometheus-fastapi-instrumentator is installed, 404 otherwise
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        body = resp.text
        assert 'http_request' in body or 'HELP' in body or 'TYPE' in body
