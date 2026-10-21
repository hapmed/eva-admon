"""Diseño y contenido del PDF de cotización."""

import re
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.pdf import render_cotizacion_html


def _empresa(**overrides):
    data = {
        "razon_social": "HAPMED Soluciones S.A. de C.V.",
        "nombre_comercial": "HAPMED",
        "rfc": "HAP200101ABC",
        "telefono": "55 1234 5678",
        "email": "hola@hapmed.mx",
        "whatsapp": "55 8765 4321",
        "sitio_web": "hapmed.mx",
        "direccion": "Av. Reforma 123, Col. Centro",
        "ciudad": "Ciudad de México",
        "estado": "CDMX",
        "codigo_postal": "06000",
        "pais": "México",
        "logo_filename": None,
        "logo_content_type": None,
        "color_primary": "#2e6bff",
        "color_secondary": "#00c2b8",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _cotizacion(items):
    return SimpleNamespace(
        folio="COT-2026-0001",
        fecha=date(2026, 10, 21),
        valida_hasta=date(2026, 11, 20),
        estado="enviada",
        moneda="MXN",
        subtotal=Decimal("1000.00"),
        descuento_total=Decimal("0"),
        iva_porcentaje=Decimal("16"),
        iva_total=Decimal("160.00"),
        total=Decimal("1160.00"),
        tiempo_entrega_dias=5,
        notas="Incluye instalación.",
        items=items,
        cliente=SimpleNamespace(
            nombre="Cliente Demo",
            rfc="CLI010101XYZ",
            condiciones_pago="Pago a 15 días",
            contactos=[],
        ),
    )


def _item(**overrides):
    data = {
        "descripcion": "Servicio de ejemplo",
        "unidad": "Servicio",
        "cantidad": Decimal("1"),
        "precio_unitario": Decimal("1000"),
        "descuento_porcentaje": Decimal("0"),
        "tiempo_entrega_dias": 0,
        "importe": Decimal("1000"),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_pdf_incluye_datos_fiscales_del_emisor():
    html = render_cotizacion_html(_cotizacion([_item()]), _empresa())

    assert "HAPMED Soluciones S.A. de C.V." in html
    assert "HAP200101ABC" in html
    assert "Av. Reforma 123, Col. Centro" in html
    assert "Ciudad de México" in html
    assert "06000" in html
    assert "México" in html
    assert "hola@hapmed.mx" in html
    assert "55 1234 5678" in html


def test_ceros_de_partidas_no_se_imprimen():
    items = [
        _item(
            descripcion="Cortesía",
            cantidad=Decimal("0"),
            precio_unitario=Decimal("0"),
            importe=Decimal("0"),
        ),
        _item(descripcion="Servicio", importe=Decimal("1000")),
    ]
    html = render_cotizacion_html(_cotizacion(items), _empresa())

    fila = re.search(r"<tr>\s*<td class=\"desc\">Cortesía</td>.*?</tr>", html, re.S)
    assert fila is not None
    fila_text = fila.group(0)
    assert "$0.00" not in fila_text
    assert "0%" not in fila_text
    assert "0 d" not in fila_text


def test_pdf_muestra_totales_y_moneda():
    html = render_cotizacion_html(_cotizacion([_item()]), _empresa())

    assert "$1,000.00" in html
    assert "$160.00" in html
    assert "$1,160.00" in html
    assert "MXN" in html
