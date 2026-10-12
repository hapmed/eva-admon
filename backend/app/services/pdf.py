"""Generación del PDF de una cotización con diseño profesional y colores de marca."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from app.core.config import get_settings
from app.models.cotizacion import Cotizacion
from app.models.empresa import EmpresaConfig

DEFAULT_PRIMARY = (46, 107, 255)  # acento HAPMED
DEFAULT_SECONDARY = (0, 194, 184)
DEFAULT_LOGO = Path(__file__).resolve().parent.parent / "assets" / "logo-hapmed.png"
_MARGIN = 15
_USABLE = 210 - 2 * _MARGIN
_WIDTHS = [84, 16, 16, 24, 14, 26]  # desc, unidad, cant, precio, desc, importe


def _safe(text: str | None) -> str:
    return (text or "").encode("latin-1", "replace").decode("latin-1")


def _money(value: float) -> str:
    return f"${float(value):,.2f}"


def _hex_to_rgb(value: str | None, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    if value and len(value) == 7 and value.startswith("#"):
        try:
            return (int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16))
        except ValueError:
            return fallback
    return fallback


def _tint(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(int(c * factor + 255 * (1 - factor)) for c in color)  # type: ignore[return-value]


class _QuotePDF(FPDF):
    folio = ""
    accent: tuple[int, int, int] = DEFAULT_PRIMARY

    def footer(self) -> None:
        self.set_y(-13)
        self.set_draw_color(*self.accent)
        self.set_line_width(0.4)
        self.line(_MARGIN, self.get_y(), 210 - _MARGIN, self.get_y())
        self.set_font("Helvetica", size=8)
        self.set_text_color(120, 120, 128)
        self.cell(_USABLE / 2, 6, _safe(f"Cotizacion {self.folio}"), align="L")
        self.cell(_USABLE / 2, 6, f"Pagina {self.page_no()} de {{nb}}", align="R")


def _logo_path(empresa: EmpresaConfig) -> Path | None:
    settings = get_settings()
    if empresa.logo_filename:
        candidate = Path(settings.logo_dir) / empresa.logo_filename
        if candidate.is_file():
            return candidate
    return DEFAULT_LOGO if DEFAULT_LOGO.is_file() else None


def _empresa_lines(empresa: EmpresaConfig) -> list[str]:
    lines: list[str] = []
    if empresa.razon_social:
        lines.append(empresa.razon_social)
    if empresa.rfc:
        lines.append(f"RFC: {empresa.rfc}")
    contact = "  |  ".join(p for p in [empresa.telefono, empresa.email, empresa.whatsapp] if p)
    if contact:
        lines.append(contact)
    return lines


def render_cotizacion_pdf(cotizacion: Cotizacion, empresa: EmpresaConfig) -> bytes:
    primary = _hex_to_rgb(empresa.color_primary, DEFAULT_PRIMARY)
    secondary = _hex_to_rgb(empresa.color_secondary, DEFAULT_SECONDARY)

    pdf = _QuotePDF(format="A4")
    pdf.folio = cotizacion.folio
    pdf.accent = primary
    pdf.set_margins(_MARGIN, _MARGIN, _MARGIN)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.alias_nb_pages()
    pdf.add_page()

    _header(pdf, empresa, cotizacion, primary)
    _parties(pdf, cotizacion, primary)
    _items(pdf, cotizacion, primary, secondary)
    _totals(pdf, cotizacion, primary)
    _notes(pdf, cotizacion, primary)

    return bytes(pdf.output())


def _header(pdf: FPDF, empresa: EmpresaConfig, cotizacion: Cotizacion, primary: tuple[int, int, int]) -> None:
    y0 = pdf.get_y()
    logo = _logo_path(empresa)
    if logo is not None:
        try:
            pdf.image(str(logo), x=_MARGIN, y=y0, w=24)
        except Exception:  # noqa: BLE001 - logo inválido
            pass

    pdf.set_xy(_MARGIN + 28, y0)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*primary)
    pdf.cell(0, 7, _safe(empresa.nombre_comercial or empresa.razon_social or "HAPMED"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(110, 110, 115)
    for line in _empresa_lines(empresa):
        pdf.set_x(_MARGIN + 28)
        pdf.cell(0, 4.5, _safe(line), new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(max(pdf.get_y(), y0 + 22))
    pdf.ln(2)
    band_y = pdf.get_y()
    pdf.set_fill_color(*primary)
    pdf.rect(_MARGIN, band_y, _USABLE, 10, style="F")
    pdf.set_xy(_MARGIN, band_y)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(105, 10, "COTIZACION", align="L")
    pdf.cell(_USABLE - 105, 10, _safe(f"Folio: {cotizacion.folio}"), align="R")
    pdf.set_y(band_y + 14)


def _parties(pdf: FPDF, cotizacion: Cotizacion, primary: tuple[int, int, int]) -> None:
    y0 = pdf.get_y()
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*primary)
    pdf.set_xy(_MARGIN, y0)
    pdf.cell(105, 6, "Cliente", new_x="RIGHT", new_y="TOP")
    pdf.set_xy(_MARGIN + 110, y0)
    pdf.cell(_USABLE - 110, 6, "Detalles", new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(60, 60, 65)
    pdf.set_font("Helvetica", size=10)
    cliente = cotizacion.cliente
    if cliente is not None:
        pdf.set_x(_MARGIN)
        pdf.cell(105, 5, _safe(cliente.nombre), new_x="LMARGIN", new_y="NEXT")
        if cliente.rfc:
            pdf.set_x(_MARGIN)
            pdf.cell(105, 5, _safe(f"RFC: {cliente.rfc}"), new_x="LMARGIN", new_y="NEXT")
        if cliente.condiciones_pago:
            pdf.set_x(_MARGIN)
            pdf.multi_cell(105, 5, _safe(f"Condiciones de pago: {cliente.condiciones_pago}"))
        for contacto in cliente.contactos[:2]:
            pdf.set_x(_MARGIN)
            pdf.cell(105, 5, _safe(f"{contacto.nombre} <{contacto.email}>"), new_x="LMARGIN", new_y="NEXT")

    meta_y = y0 + 6
    for label, value in [
        ("Fecha", cotizacion.fecha.isoformat()),
        ("Valida hasta", cotizacion.valida_hasta.isoformat() if cotizacion.valida_hasta else "-"),
        ("Estado", cotizacion.estado.capitalize()),
    ]:
        pdf.set_xy(_MARGIN + 110, meta_y)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(28, 5, _safe(label), new_x="RIGHT", new_y="TOP")
        pdf.set_font("Helvetica", size=9)
        pdf.cell(_USABLE - 110 - 28, 5, _safe(value), new_x="LMARGIN", new_y="NEXT")
        meta_y += 5

    pdf.set_y(max(pdf.get_y(), meta_y) + 3)


def _items(
    pdf: FPDF,
    cotizacion: Cotizacion,
    primary: tuple[int, int, int],
    secondary: tuple[int, int, int],
) -> None:
    header = ["Descripcion", "Unidad", "Cant.", "P. unit.", "Desc.", "Importe"]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*primary)
    pdf.set_text_color(255, 255, 255)
    pdf.set_x(_MARGIN)
    for width, title in zip(_WIDTHS, header, strict=True):
        align = "L" if title == "Descripcion" else "C"
        pdf.cell(width, 7, _safe(title), border="TB", fill=True, align=align)
    pdf.ln(7)

    zebra = _tint(secondary, 0.12)
    pdf.set_text_color(40, 40, 45)
    for index, item in enumerate(cotizacion.items):
        fill = index % 2 == 1
        _item_row(pdf, item, primary, zebra if fill else None)


def _item_row(pdf: FPDF, item, primary: tuple[int, int, int], fill: tuple[int, int, int] | None) -> None:
    line_h = 5
    pdf.set_font("Helvetica", size=9)
    max_width = _WIDTHS[0] - 4
    lines: list[str] = []
    current = ""
    for word in (item.descripcion or "").split():
        candidate = f"{current} {word}".strip()
        if pdf.get_string_width(candidate) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    row_h = line_h * len(lines) + 2

    x0, y0 = _MARGIN, pdf.get_y()
    if fill is not None:
        pdf.set_fill_color(*fill)
        pdf.rect(x0, y0, sum(_WIDTHS), row_h, style="F")

    pdf.set_xy(x0 + 2, y0 + 1)
    for line in lines:
        pdf.cell(_WIDTHS[0] - 2, line_h, _safe(line), new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(x0 + 2)

    values = [
        (_safe(item.unidad), "C", _WIDTHS[1]),
        (f"{float(item.cantidad):g}", "C", _WIDTHS[2]),
        (_money(item.precio_unitario), "R", _WIDTHS[3]),
        (f"{float(item.descuento_porcentaje):g}%", "R", _WIDTHS[4]),
        (_money(item.importe), "R", _WIDTHS[5]),
    ]
    cx = x0 + _WIDTHS[0]
    pdf.set_xy(cx, y0 + 1)
    for text, align, width in values:
        pdf.cell(width, line_h * len(lines), text, align=align)

    pdf.set_draw_color(*_tint(primary, 0.55))
    pdf.set_line_width(0.2)
    pdf.rect(x0, y0, sum(_WIDTHS), row_h)
    cx = x0
    for width in _WIDTHS[:-1]:
        cx += width
        pdf.line(cx, y0, cx, y0 + row_h)
    pdf.set_xy(x0, y0 + row_h)


def _totals(pdf: FPDF, cotizacion: Cotizacion, primary: tuple[int, int, int]) -> None:
    box_w = 70
    x = 210 - _MARGIN - box_w
    y = pdf.get_y() + 3
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(60, 60, 65)
    rows = [
        ("Subtotal", _money(cotizacion.subtotal)),
        ("Descuento", _money(cotizacion.descuento_total)),
        (f"IVA {float(cotizacion.iva_porcentaje):g}%", _money(cotizacion.iva_total)),
    ]
    for label, value in rows:
        pdf.set_xy(x, y)
        pdf.cell(box_w - 30, 6, label, align="R")
        pdf.cell(30, 6, value, align="R", new_x="LMARGIN", new_y="NEXT")
        y += 6
    pdf.set_fill_color(*primary)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_xy(x, y)
    pdf.cell(box_w - 30, 8, "TOTAL", align="R", fill=True)
    pdf.cell(30, 8, _money(cotizacion.total), align="R", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(y + 12)


def _notes(pdf: FPDF, cotizacion: Cotizacion, primary: tuple[int, int, int]) -> None:
    if not cotizacion.notas:
        return
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*primary)
    pdf.set_x(_MARGIN)
    pdf.cell(0, 6, "Notas", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(60, 60, 65)
    pdf.set_x(_MARGIN)
    pdf.multi_cell(_USABLE, 5, _safe(cotizacion.notas))
