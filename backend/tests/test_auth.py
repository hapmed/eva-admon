from fastapi.testclient import TestClient


def test_login_ok_and_me(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "admin@test.com"
    assert body["rol"] == "admin"


def test_login_bad_credentials(client: TestClient, db_session) -> None:
    response = client.post(
        "/api/v1/auth/login", json={"email": "nadie@test.com", "password": "x"}
    )
    assert response.status_code == 401


def test_endpoint_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/clientes").status_code == 401
