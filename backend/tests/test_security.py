"""Tests for security module and auth edge cases: token expiry, password hashing."""

from datetime import UTC, datetime, timedelta

from fastapi import Request
from jose import jwt

from app.core.rate_limit import get_client_ip
from app.core.security import create_access_token, hash_password, verify_password

# Must match the SECRET_KEY set by the autouse test_environment fixture in conftest.py
_TEST_SECRET = "test-secret-key"


# ── Password Hashing ─────────────────────────────────────────────


def test_hash_password_returns_different_hash():
    h1 = hash_password("password123")
    h2 = hash_password("password123")
    assert h1 != h2  # bcrypt uses random salt


def test_verify_password_correct():
    hashed = hash_password("TestPass123")
    assert verify_password("TestPass123", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("TestPass123")
    assert verify_password("WrongPass", hashed) is False


# ── Token Creation ───────────────────────────────────────────────


def test_create_access_token_contains_subject():
    token = create_access_token("user@example.com")
    payload = jwt.decode(token, _TEST_SECRET, algorithms=["HS256"])
    assert payload["sub"] == "user@example.com"


def test_create_access_token_has_expiry():
    token = create_access_token("user@example.com")
    payload = jwt.decode(token, _TEST_SECRET, algorithms=["HS256"])
    assert "exp" in payload


def test_create_access_token_custom_expiry():
    token = create_access_token("user@example.com", expires_minutes=1)
    payload = jwt.decode(token, _TEST_SECRET, algorithms=["HS256"])
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    now = datetime.now(UTC)
    # Should expire within 2 minutes
    assert exp - now < timedelta(minutes=2)


# ── Expired Token via API ────────────────────────────────────────


def test_expired_token_rejected(client):
    """An expired JWT should be rejected with 401."""
    expired_token = jwt.encode(
        {"sub": "expired@example.com", "exp": datetime.now(UTC) - timedelta(hours=1)},
        _TEST_SECRET,
        algorithm="HS256",
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401


def test_token_missing_subject_rejected(client):
    """A JWT without 'sub' claim should be rejected."""
    token = jwt.encode(
        {"exp": datetime.now(UTC) + timedelta(hours=1)},
        _TEST_SECRET,
        algorithm="HS256",
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_token_nonexistent_user_rejected(client):
    """A valid JWT for a non-existent user should be rejected."""
    token = create_access_token("nonexistent@example.com")
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_rate_limit_uses_forwarded_for_when_present():
    request = Request(
        {
            "type": "http",
            "headers": [
                (b"x-forwarded-for", b"203.0.113.5, 10.0.0.2"),
                (b"x-real-ip", b"10.0.0.2"),
            ],
            "client": ("10.0.0.2", 8080),
        }
    )

    assert get_client_ip(request) == "203.0.113.5"
