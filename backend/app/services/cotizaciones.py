"""Reglas de negocio de cotizaciones (cálculo de importes y persistencia)."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.cotizacion import Cotizacion, CotizacionItem, EstadoCotizacion
from app.schemas.cotizacion import CotizacionCreate, CotizacionUpdate, ItemIn
from app.services.folios import next_cotizacion_folio

_CENT = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def item_bruto(item: ItemIn) -> Decimal:
    return Decimal(str(item.cantidad)) * Decimal(str(item.precio_unitario))


def item_descuento(item: ItemIn) -> Decimal:
    descuento = Decimal(str(item.descuento_porcentaje)) / Decimal("100")
    return _money(item_bruto(item) * descuento)


def item_importe(item: ItemIn) -> Decimal:
    cantidad = Decimal(str(item.cantidad))
    precio = Decimal(str(item.precio_unitario))
    descuento = Decimal(str(item.descuento_porcentaje)) / Decimal("100")
    return _money(cantidad * precio * (Decimal("1") - descuento))


def totals(items: list[ItemIn], iva_porcentaje: Decimal) -> dict[str, Decimal]:
    subtotal = _money(sum((item_bruto(i) for i in items), Decimal("0")))
    descuento_total = _money(sum((item_descuento(i) for i in items), Decimal("0")))
    base = subtotal - descuento_total
    iva_total = _money(base * (iva_porcentaje / Decimal("100")))
    total = _money(base + iva_total)
    return {
        "subtotal": subtotal,
        "descuento_total": descuento_total,
        "iva_total": iva_total,
        "total": total,
    }


def _apply_items(cotizacion: Cotizacion, items: list[ItemIn]) -> None:
    cotizacion.items = [
        CotizacionItem(
            tipo=item.tipo,
            descripcion=item.descripcion,
            unidad=item.unidad,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            descuento_porcentaje=item.descuento_porcentaje,
            importe=item_importe(item),
        )
        for item in items
    ]


def _recalc(cotizacion: Cotizacion, items: list[ItemIn]) -> None:
    iva = Decimal(str(cotizacion.iva_porcentaje))
    result = totals(items, iva)
    cotizacion.subtotal = float(result["subtotal"])
    cotizacion.descuento_total = float(result["descuento_total"])
    cotizacion.iva_total = float(result["iva_total"])
    cotizacion.total = float(result["total"])


def create_cotizacion(db: Session, data: CotizacionCreate, user_id: int | None) -> Cotizacion:
    settings = get_settings()
    iva = data.iva_porcentaje if data.iva_porcentaje is not None else settings.iva_porcentaje
    cotizacion = Cotizacion(
        folio=next_cotizacion_folio(db),
        cliente_id=data.cliente_id,
        fecha=data.fecha or date.today(),
        valida_hasta=data.valida_hasta,
        estado=data.estado,
        iva_porcentaje=iva,
        notas=data.notas,
        created_by_id=user_id,
    )
    _apply_items(cotizacion, data.items)
    _recalc(cotizacion, data.items)
    db.add(cotizacion)
    db.commit()
    db.refresh(cotizacion)
    return cotizacion


def update_cotizacion(db: Session, cotizacion: Cotizacion, data: CotizacionUpdate) -> Cotizacion:
    payload = data.model_dump(exclude_unset=True)
    items = payload.pop("items", None)
    for field, value in payload.items():
        if value is not None:
            setattr(cotizacion, field, value)
    if items is not None:
        item_models = [ItemIn(**item) for item in items]
        _apply_items(cotizacion, item_models)
        _recalc(cotizacion, item_models)
    elif any(f in payload for f in ("iva_porcentaje",)):
        _recalc(cotizacion, [ItemIn.model_validate(i) for i in cotizacion.items])
    db.commit()
    db.refresh(cotizacion)
    return cotizacion


def set_estado(cotizacion: Cotizacion, estado: EstadoCotizacion) -> Cotizacion:
    cotizacion.estado = estado
    return cotizacion
