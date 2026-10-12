from fastapi.testclient import TestClient


def test_smtp_password_no_se_expone(client: TestClient, admin_headers: dict[str, str]) -> None:
    updated = client.put(
        "/api/v1/configuracion",
        headers=admin_headers,
        json={
            "smtp_host": "smtp.ejemplo.com",
            "smtp_port": 587,
            "smtp_username": "usuario",
            "smtp_password": "secreto-smtp",
            "smtp_from_email": "no-responder@ejemplo.com",
        },
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["smtp_password_set"] is True
    assert "smtp_password" not in body


def test_envio_sin_smtp_configurado(client: TestClient, admin_headers: dict[str, str]) -> None:
    cliente = client.post("/api/v1/clientes", headers=admin_headers, json={"nombre": "X"}).json()
    cot = client.post(
        "/api/v1/cotizaciones",
        headers=admin_headers,
        json={"cliente_id": cliente["id"], "items": []},
    ).json()
    response = client.post(
        f"/api/v1/cotizaciones/{cot['id']}/enviar",
        headers=admin_headers,
        json={"destinatarios": ["destino@ejemplo.com"]},
    )
    assert response.status_code == 400


def test_logo_colores(
    client: TestClient, admin_headers: dict[str, str], tmp_path, monkeypatch
) -> None:
    import io

    from PIL import Image

    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "logo_dir", str(tmp_path))

    image = Image.new("RGB", (64, 64), (200, 20, 20))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    response = client.post(
        "/api/v1/configuracion/logo",
        headers=admin_headers,
        files={"file": ("logo.png", buffer.getvalue(), "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tiene_logo"] is True
    assert body["color_primary"].startswith("#")
