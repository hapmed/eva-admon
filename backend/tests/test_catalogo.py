from fastapi.testclient import TestClient


def test_servicio_crud_y_codigo_duplicado(client: TestClient, admin_headers: dict[str, str]) -> None:
    created = client.post(
        "/api/v1/servicios",
        headers=admin_headers,
        json={"codigo": "SRV-001", "nombre": "Mantenimiento", "precio_unitario": 500},
    )
    assert created.status_code == 201

    duplicated = client.post(
        "/api/v1/servicios",
        headers=admin_headers,
        json={"codigo": "SRV-001", "nombre": "Otro", "precio_unitario": 1},
    )
    assert duplicated.status_code == 409

    listed = client.get("/api/v1/servicios", headers=admin_headers).json()
    assert any(s["codigo"] == "SRV-001" for s in listed)


def test_material_crud(client: TestClient, admin_headers: dict[str, str]) -> None:
    created = client.post(
        "/api/v1/materiales",
        headers=admin_headers,
        json={"codigo": "MAT-001", "nombre": "Tornillo", "unidad": "Pieza", "precio_unitario": 2.5},
    )
    assert created.status_code == 201
    material_id = created.json()["id"]
    patched = client.patch(
        f"/api/v1/materiales/{material_id}", headers=admin_headers, json={"precio_unitario": 3}
    )
    assert patched.json()["precio_unitario"] == 3.0
