"""Generación del PDF de una cotización.

Renderiza HTML/CSS con WeasyPrint: tipografía neutra, mucho aire, tarjetas
redondeadas y jerarquía clara (Apple HIG), con los colores de marca de la
empresa emisora.

Los ceros de las columnas de partidas no se imprimen: la celda queda vacía.
"""

from __future__ import annotations

import base64
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.core.config import get_settings
from app.models.cotizacion import Cotizacion
from app.models.empresa import EmpresaConfig

DEFAULT_PRIMARY = "#2e6bff"
DEFAULT_SECONDARY = "#00c2b8"

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
MONTHS_ES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)
ESTADO_LABELS = {
    "borrador": "Borrador",
    "enviada": "Enviada",
    "aceptada": "Aceptada",
    "rechazada": "Rechazada",
    "cancelada": "Cancelada",
}

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _decimal(value: Decimal | float | int | None) -> Decimal:
    return Decimal(str(value or 0))


def _money(value: Decimal | float | int | None, moneda: str = "MXN") -> str:
    amount = _decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    symbol = "US$" if (moneda or "").upper() == "USD" else "$"
    return f"{symbol}{amount:,.2f}"


def _money_blank(value: Decimal | float | int | None, moneda: str = "MXN") -> str:
    """Importe, pero un cero se muestra como celda vacía (solo partidas)."""
    if _decimal(value) == 0:
        return ""
    return _money(value, moneda)


def _qty(value: Decimal | float | int | None) -> str:
    amount = _decimal(value)
    if amount == 0:
        return ""
    text = format(amount.normalize(), "f")
    return text


def _pct(value: Decimal | float | int | None) -> str:
    amount = _decimal(value)
    if amount == 0:
        return ""
    return f"{format(amount.normalize(), 'f')}%"


def _days(value: int | None) -> str:
    return f"{value} d" if value else ""


def _date(value: date | None) -> str:
    if not value:
        return "—"
    return f"{value.day} de {MONTHS_ES[value.month - 1]} de {value.year}"


_env.filters["money"] = _money
_env.filters["money_blank"] = _money_blank
_env.filters["qty"] = _qty
_env.filters["pct"] = _pct
_env.filters["days"] = _days
_env.filters["fecha"] = _date


def _color(value: str | None, fallback: str) -> str:
    if value and len(value) == 7 and value.startswith("#"):
        return value
    return fallback


def _logo_data_uri(empresa: EmpresaConfig) -> str | None:
    if not empresa.logo_filename:
        return None
    path = Path(get_settings().logo_dir) / empresa.logo_filename
    if not path.is_file():
        return None
    content_type = empresa.logo_content_type or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:{content_type};base64,{encoded}"


def _contact_lines(empresa: EmpresaConfig) -> list[str]:
    lines: list[str] = []
    if empresa.direccion:
        lines.append(empresa.direccion)
    city = " ".join(
        part for part in (empresa.ciudad, empresa.estado, empresa.codigo_postal) if part
    )
    if city:
        lines.append(city)
    if empresa.pais:
        lines.append(empresa.pais)
    return lines


def render_cotizacion_html(cotizacion: Cotizacion, empresa: EmpresaConfig) -> str:
    template = _env.get_template("cotizacion.html")
    return template.render(
        cotizacion=cotizacion,
        empresa=empresa,
        cliente=cotizacion.cliente,
        primary=_color(empresa.color_primary, DEFAULT_PRIMARY),
        secondary=_color(empresa.color_secondary, DEFAULT_SECONDARY),
        logo=_logo_data_uri(empresa),
        contact_lines=_contact_lines(empresa),
        estado_label=ESTADO_LABELS.get(cotizacion.estado, cotizacion.estado),
        descuento=_decimal(cotizacion.descuento_total) > 0,
    )


def render_cotizacion_pdf(cotizacion: Cotizacion, empresa: EmpresaConfig) -> bytes:
    html = render_cotizacion_html(cotizacion, empresa)
    return HTML(string=html, base_url=str(TEMPLATES)).write_pdf()
