from fastapi.testclient import TestClient


def _cliente(client: TestClient, headers: dict[str, str], rfc: str = "COT010101AAA") -> int:
    return client.post(
        "/api/v1/clientes", headers=headers, json={"nombre": "Cliente Cot", "rfc": rfc}
    ).json()["id"]


def test_cotizacion_calcula_totales(client: TestClient, admin_headers: dict[str, str]) -> None:
    cliente_id = _cliente(client, admin_headers)
    response = client.post(
        "/api/v1/cotizaciones",
        headers=admin_headers,
        json={
            "cliente_id": cliente_id,
            "iva_porcentaje": 16,
            "items": [
                {
                    "tipo": "servicio",
                    "descripcion": "Instalación",
                    "unidad": "Servicio",
                    "cantidad": 2,
                    "precio_unitario": 1000,
                    "descuento_porcentaje": 10,
                },
                {
                    "tipo": "material",
                    "descripcion": "Cable",
                    "unidad": "m",
                    "cantidad": 10,
                    "precio_unitario": 50,
                    "descuento_porcentaje": 0,
                },
            ],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["folio"]) == 8
    assert body["folio"].isalnum()
    # Bruto servicios = 2000, descuento 10% = 200; materiales = 500 -> subtotal 2500
    assert body["subtotal"] == 2500.0
    assert body["descuento_total"] == 200.0
    assert body["iva_total"] == 368.0  # (2500 - 200) * 0.16
    assert body["total"] == 2668.0


def test_cotizacion_cliente_inexistente(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/cotizaciones", headers=admin_headers, json={"cliente_id": 999, "items": []}
    )
    assert response.status_code == 404


def test_cotizacion_folios_unicos(client: TestClient, admin_headers: dict[str, str]) -> None:
    cliente_id = _cliente(client, admin_headers)
    folios = set()
    for _ in range(5):
        body = client.post(
            "/api/v1/cotizaciones",
            headers=admin_headers,
            json={"cliente_id": cliente_id, "items": []},
        ).json()
        folios.add(body["folio"])
    assert len(folios) == 5


def test_tiempo_entrega_general_es_el_mayor(client: TestClient, admin_headers: dict[str, str]) -> None:
    cliente_id = _cliente(client, admin_headers)
    body = client.post(
        "/api/v1/cotizaciones",
        headers=admin_headers,
        json={
            "cliente_id": cliente_id,
            "items": [
                {
                    "tipo": "servicio",
                    "descripcion": "A",
                    "cantidad": 1,
                    "precio_unitario": 100,
                    "tiempo_entrega_dias": 5,
                },
                {
                    "tipo": "material",
                    "descripcion": "B",
                    "cantidad": 1,
                    "precio_unitario": 100,
                    "tiempo_entrega_dias": 12,
                },
            ],
        },
    ).json()
    assert body["tiempo_entrega_dias"] == 12
    assert body["items"][0]["tiempo_entrega_dias"] == 5


def test_cotizacion_pdf(client: TestClient, admin_headers: dict[str, str]) -> None:
    cliente_id = _cliente(client, admin_headers)
    created = client.post(
        "/api/v1/cotizaciones",
        headers=admin_headers,
        json={
            "cliente_id": cliente_id,
            "items": [
                {
                    "tipo": "servicio",
                    "descripcion": "Servicio",
                    "cantidad": 1,
                    "precio_unitario": 100,
                }
            ],
        },
    )
    cotizacion_id = created.json()["id"]
    pdf = client.get(f"/api/v1/cotizaciones/{cotizacion_id}/pdf", headers=admin_headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")
