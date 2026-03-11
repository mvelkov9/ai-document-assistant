from app.services.storage_service import StorageService


def test_healthcheck(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_status(client) -> None:
    response = client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json()["service"] == "backend"


def test_readiness(client, monkeypatch) -> None:
    monkeypatch.setattr(StorageService, 'check_connection', lambda self: True)

    response = client.get('/ready')

    assert response.status_code == 200
    assert response.json()['status'] == 'ready'


def test_register_login_and_me_flow(client) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "student@example.com",
            "password": "VerySecure123",
            "full_name": "Demo Student",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "student@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "student@example.com",
            "password": "VerySecure123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["full_name"] == "Demo Student"


def test_duplicate_registration_is_rejected(client) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "VerySecure123",
        "full_name": "Duplicate User",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)
    second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409

