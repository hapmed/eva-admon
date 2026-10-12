from fastapi.testclient import TestClient


def test_cliente_consecutivo_y_contactos(client: TestClient, admin_headers: dict[str, str]) -> None:
    first = client.post(
        "/api/v1/clientes",
        headers=admin_headers,
        json={
            "nombre": "ACME S.A. de C.V.",
            "rfc": "ACM010101AAA",
            "condiciones_pago": "30 días",
            "contactos": [{"nombre": "Ana", "email": "ana@acme.com"}],
        },
    )
    assert first.status_code == 201
    body = first.json()
    assert body["numero_cliente"] == "CLI-0001"
    assert len(body["contactos"]) == 1

    second = client.post("/api/v1/clientes", headers=admin_headers, json={"nombre": "Otra, S.A."})
    assert second.json()["numero_cliente"] == "CLI-0002"


def test_cliente_baja_logica(client: TestClient, admin_headers: dict[str, str]) -> None:
    created = client.post("/api/v1/clientes", headers=admin_headers, json={"nombre": "Baja"})
    cliente_id = created.json()["id"]
    assert client.delete(f"/api/v1/clientes/{cliente_id}", headers=admin_headers).status_code == 204
    activos = client.get("/api/v1/clientes", headers=admin_headers).json()["items"]
    assert all(c["id"] != cliente_id for c in activos)
    inactivos = client.get("/api/v1/clientes?activo=false", headers=admin_headers).json()["items"]
    assert any(c["id"] == cliente_id for c in inactivos)


def test_cliente_no_encontrado(client: TestClient, admin_headers: dict[str, str]) -> None:
    assert client.get("/api/v1/clientes/999", headers=admin_headers).status_code == 404
