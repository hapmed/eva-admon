from fastapi.testclient import TestClient


def test_paginacion_y_filtros_clientes(client: TestClient, admin_headers: dict[str, str]) -> None:
    for index in range(25):
        client.post("/api/v1/clientes", headers=admin_headers, json={"nombre": f"Cliente {index:02d}"})

    page1 = client.get("/api/v1/clientes?page=1&page_size=10", headers=admin_headers).json()
    assert page1["total"] == 25
    assert page1["pages"] == 3
    assert page1["page_size"] == 10
    assert len(page1["items"]) == 10

    page3 = client.get("/api/v1/clientes?page=3&page_size=10", headers=admin_headers).json()
    assert len(page3["items"]) == 5

    filtered = client.get("/api/v1/clientes?search=Cliente 1", headers=admin_headers).json()
    assert filtered["total"] >= 1
    assert all("Cliente 1" in c["nombre"] for c in filtered["items"])
