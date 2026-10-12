"""Generación del PDF de una cotización (sin dependencias externas de red)."""

from pathlib import Path

from fpdf import FPDF

from app.core.config import get_settings
from app.models.cotizacion import Cotizacion
from app.models.empresa import EmpresaConfig

_LINE = 7


def _money(value: float) -> str:
    return f"${float(value):,.2f}"


def _safe(text: str | None) -> str:
    """fpdf con fuentes core usa latin-1; se eliminan caracteres fuera de rango."""
    return (text or "").encode("latin-1", "replace").decode("latin-1")


def render_cotizacion_pdf(cotizacion: Cotizacion, empresa: EmpresaConfig) -> bytes:
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    _header(pdf, empresa)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _safe(f"Cotizacion {cotizacion.folio}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(
        0,
        6,
        _safe(
            f"Fecha: {cotizacion.fecha.isoformat()}"
            + (f"   Vigencia: {cotizacion.valida_hasta.isoformat()}" if cotizacion.valida_hasta else "")
        ),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(0, 6, _safe(f"Estado: {cotizacion.estado}", ), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    _cliente_block(pdf, cotizacion)
    _items_table(pdf, cotizacion)
    _totals_block(pdf, cotizacion)

    if cotizacion.notas:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Notas", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 5, _safe(cotizacion.notas))

    return bytes(pdf.output())


def _header(pdf: FPDF, empresa: EmpresaConfig) -> None:
    settings = get_settings()
    logo_path = Path(settings.logo_dir) / empresa.logo_filename if empresa.logo_filename else None
    if logo_path and logo_path.is_file():
        try:
            pdf.image(str(logo_path), x=15, y=15, w=28)
        except Exception:  # pragma: no cover - imagen inválida
            pass
    pdf.set_x(48)
    pdf.set_font("Helvetica", "B", 14)
    titulo = empresa.nombre_comercial or empresa.razon_social or "HAPMED"
    pdf.cell(0, 7, _safe(titulo), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(48)
    pdf.set_font("Helvetica", size=9)
    for line in _empresa_lines(empresa):
        pdf.set_x(48)
        pdf.cell(0, 5, _safe(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)


def _empresa_lines(empresa: EmpresaConfig) -> list[str]:
    lines = []
    if empresa.razon_social:
        lines.append(f"Razon social: {empresa.razon_social}")
    if empresa.rfc:
        lines.append(f"RFC: {empresa.rfc}")
    contact = " | ".join(p for p in [empresa.telefono, empresa.email, empresa.whatsapp] if p)
    if contact:
        lines.append(contact)
    return lines


def _cliente_block(pdf: FPDF, cotizacion: Cotizacion) -> None:
    cliente = cotizacion.cliente
    if cliente is None:
        return
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Cliente", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 5, _safe(f"{cliente.numero_cliente} - {cliente.nombre}"), new_x="LMARGIN", new_y="NEXT")
    if cliente.rfc:
        pdf.cell(0, 5, _safe(f"RFC: {cliente.rfc}"), new_x="LMARGIN", new_y="NEXT")
    if cliente.condiciones_pago:
        pdf.multi_cell(0, 5, _safe(f"Condiciones de pago: {cliente.condiciones_pago}"))
    pdf.ln(2)


def _items_table(pdf: FPDF, cotizacion: Cotizacion) -> None:
    widths = (90, 22, 32, 30)
    headers = ("Descripcion", "Unidad", "Cantidad x Precio", "Importe")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(242, 242, 247)
    for width, title in zip(widths, headers, strict=True):
        align = "L" if title == "Descripcion" else "C"
        pdf.cell(width, _LINE, _safe(title), border=1, fill=True, align=align)
    pdf.ln(_LINE)
    pdf.set_font("Helvetica", size=9)
    for item in cotizacion.items:
        desc = item.descripcion
        if item.descuento_porcentaje:
            desc += f" (desc. {float(item.descuento_porcentaje):g}%)"
        pdf.cell(widths[0], _LINE, _safe(desc)[:60], border=1)
        pdf.cell(widths[1], _LINE, _safe(item.unidad)[:12], border=1, align="C")
        pdf.cell(
            widths[2],
            _LINE,
            _safe(f"{float(item.cantidad):g} x {_money(item.precio_unitario)}"),
            border=1,
            align="R",
        )
        pdf.cell(widths[3], _LINE, _money(item.importe), border=1, align="R")
        pdf.ln(_LINE)
    pdf.ln(2)


def _totals_block(pdf: FPDF, cotizacion: Cotizacion) -> None:
    pdf.set_font("Helvetica", size=10)
    rows = [
        ("Subtotal", _money(cotizacion.subtotal)),
        ("Descuento", _money(cotizacion.descuento_total)),
        (f"IVA {float(cotizacion.iva_porcentaje):g}%", _money(cotizacion.iva_total)),
    ]
    for label, value in rows:
        pdf.set_x(120)
        pdf.cell(40, _LINE, label, align="R")
        pdf.cell(30, _LINE, value, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_x(120)
    pdf.cell(40, _LINE, "Total", align="R")
    pdf.cell(30, _LINE, _money(cotizacion.total), align="R", new_x="LMARGIN", new_y="NEXT")
