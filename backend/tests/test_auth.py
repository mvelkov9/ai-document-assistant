"""Tests for authentication edge cases: validation errors, bad credentials, token issues."""


def test_register_short_password(client) -> None:
    resp = client.post(
        '/api/v1/auth/register',
        json={'email': 'short@example.com', 'password': 'Ab1', 'full_name': 'Short Pw'},
    )
    assert resp.status_code == 422


def test_register_invalid_email(client) -> None:
    resp = client.post(
        '/api/v1/auth/register',
        json={'email': 'not-an-email', 'password': 'VerySecure123', 'full_name': 'Bad Email'},
    )
    assert resp.status_code == 422


def test_register_missing_full_name(client) -> None:
    resp = client.post(
        '/api/v1/auth/register',
        json={'email': 'noname@example.com', 'password': 'VerySecure123'},
    )
    assert resp.status_code == 422


def test_login_wrong_password(client) -> None:
    client.post(
        '/api/v1/auth/register',
        json={'email': 'wrongpw@example.com', 'password': 'VerySecure123', 'full_name': 'WP User'},
    )
    resp = client.post(
        '/api/v1/auth/login',
        json={'email': 'wrongpw@example.com', 'password': 'WrongPassword999'},
    )
    assert resp.status_code == 401
    assert 'Invalid' in resp.json()['detail']


def test_login_nonexistent_user(client) -> None:
    resp = client.post(
        '/api/v1/auth/login',
        json={'email': 'ghost@example.com', 'password': 'VerySecure123'},
    )
    assert resp.status_code == 401


def test_me_without_token(client) -> None:
    resp = client.get('/api/v1/auth/me')
    assert resp.status_code == 403


def test_me_with_invalid_token(client) -> None:
    resp = client.get(
        '/api/v1/auth/me',
        headers={'Authorization': 'Bearer invalid.jwt.token'},
    )
    assert resp.status_code == 401


def test_register_duplicate_email(client) -> None:
    payload = {
        'email': 'dup@example.com',
        'password': 'VerySecure123',
        'full_name': 'Dup User',
    }
    first = client.post('/api/v1/auth/register', json=payload)
    second = client.post('/api/v1/auth/register', json=payload)
    assert first.status_code == 201
    assert second.status_code == 409
