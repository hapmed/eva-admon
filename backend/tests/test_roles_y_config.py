from fastapi.testclient import TestClient


def _login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_crea_usuario_y_ventas_no_gestiona(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/usuarios",
        headers=admin_headers,
        json={
            "email": "ventas@test.com",
            "nombre": "Vendedor",
            "rol": "ventas",
            "password": "Secreta123",
        },
    )
    assert created.status_code == 201

    ventas_headers = _login(client, "ventas@test.com", "Secreta123")
    # ventas no puede listar usuarios
    assert client.get("/api/v1/usuarios", headers=ventas_headers).status_code == 403
    # pero sí crear clientes
    assert (
        client.post("/api/v1/clientes", headers=ventas_headers, json={"nombre": "X"}).status_code
        == 201
    )


def test_email_duplicado(client: TestClient, admin_headers: dict[str, str]) -> None:
    payload = {"email": "dup@test.com", "nombre": "Uno", "rol": "consulta", "password": "Secreta123"}
    assert client.post("/api/v1/usuarios", headers=admin_headers, json=payload).status_code == 201
    assert client.post("/api/v1/usuarios", headers=admin_headers, json=payload).status_code == 409


def test_configuracion(client: TestClient, admin_headers: dict[str, str]) -> None:
    updated = client.put(
        "/api/v1/configuracion",
        headers=admin_headers,
        json={"razon_social": "HAPMED SA", "iva_porcentaje": 8, "moneda": "MXN"},
    )
    assert updated.status_code == 200
    assert updated.json()["razon_social"] == "HAPMED SA"
    assert updated.json()["iva_porcentaje"] == 8.0
