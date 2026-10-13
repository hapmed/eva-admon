from fastapi.testclient import TestClient


def _cliente(client: TestClient, headers: dict[str, str], rfc: str = "CAL010101AAA") -> int:
    return client.post(
        "/api/v1/clientes", headers=headers, json={"nombre": "Cliente Calc", "rfc": rfc}
    ).json()["id"]


def test_calculo_totales_y_generar_cotizacion(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    cliente_id = _cliente(client, admin_headers)
    created = client.post(
        "/api/v1/calculos",
        headers=admin_headers,
        json={
            "cliente_id": cliente_id,
            "items": [
                {
                    "partida": "1",
                    "tipo": "material",
                    "descripcion": "Cable",
                    "cantidad": 10,
                    "precio_compra_unitario": 100,
                    "porcentaje_aumento": 25,
                    "proveedor": "Prov A",
                    "tiempo_entrega_dias": 3,
                },
                {
                    "partida": "2",
                    "tipo": "servicio",
                    "descripcion": "Instalación",
                    "cantidad": 1,
                    "precio_compra_unitario": 0,
                    "precio_venta_unitario": 2000,
                    "tiempo_entrega_dias": 5,
                },
            ],
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert len(body["folio"]) == 8
    assert body["items"][0]["precio_venta_unitario"] == 125  # 100 * 1.25
    assert body["items"][0]["precio_venta_total"] == 1250
    assert body["venta_total"] == 3250  # 1250 + 2000
    assert body["costo_total"] == 1000
    assert body["ganancia_total"] == 2250

    item_id = body["items"][0]["id"]
    cot = client.post(
        f"/api/v1/calculos/{body['id']}/cotizacion",
        headers=admin_headers,
        json={"item_ids": [item_id]},
    )
    assert cot.status_code == 200
    cot_body = cot.json()
    assert cot_body["calculo_id"] == body["id"]
    assert cot_body["items"][0]["precio_unitario"] == 125
    assert cot_body["items"][0]["cantidad"] == 10
    assert cot_body["subtotal"] == 1250


def test_calculo_item_requerido(client: TestClient, admin_headers: dict[str, str]) -> None:
    cliente_id = _cliente(client, admin_headers, rfc="CAL010101BBB")
    body = client.post(
        "/api/v1/calculos",
        headers=admin_headers,
        json={"cliente_id": cliente_id, "items": []},
    ).json()
    response = client.post(
        f"/api/v1/calculos/{body['id']}/cotizacion",
        headers=admin_headers,
        json={"item_ids": [999]},
    )
    assert response.status_code == 400
