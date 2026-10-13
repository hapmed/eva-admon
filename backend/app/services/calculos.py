"""Reglas de negocio de cálculos y generación de cotizaciones."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.calculo import Calculo, CalculoItem
from app.models.cotizacion import Cotizacion, CotizacionItem, TipoItem
from app.schemas.calculo import CalculoCreate, CalculoItemIn, CalculoUpdate, GenerarCotizacionRequest
from app.services.cotizaciones import item_importe, totals, unique_folio
from app.services.folios import generate_folio

_CENT = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _unique_calculo_folio(db: Session) -> str:
    for _ in range(10):
        folio = generate_folio()
        en_cot = db.scalar(select(Cotizacion).where(Cotizacion.folio == folio))
        en_cal = db.scalar(select(Calculo).where(Calculo.folio == folio))
        if en_cot is None and en_cal is None:
            return folio
    raise RuntimeError("No se pudo generar un folio único")


def _compute_item(data: CalculoItemIn) -> dict:
    cantidad = Decimal(str(data.cantidad))
    compra_u = Decimal(str(data.precio_compra_unitario))
    compra_total = _money(cantidad * compra_u)
    if data.tipo == TipoItem.MATERIAL:
        pct = Decimal(str(data.porcentaje_aumento))
        venta_u = _money(compra_u * (Decimal("1") + pct / Decimal("100")))
    else:
        venta_u = _money(Decimal(str(data.precio_venta_unitario or 0)))
    venta_total = _money(venta_u * cantidad)
    return {
        "partida": data.partida,
        "tipo": data.tipo,
        "descripcion": data.descripcion,
        "modelo": data.modelo,
        "cantidad": float(cantidad),
        "precio_compra_unitario": float(compra_u),
        "precio_compra_total": float(compra_total),
        "porcentaje_aumento": float(data.porcentaje_aumento),
        "precio_venta_unitario": float(venta_u),
        "precio_venta_total": float(venta_total),
        "proveedor": data.proveedor,
        "tiempo_entrega_dias": data.tiempo_entrega_dias,
    }


def _apply_items(calculo: Calculo, items: list[CalculoItemIn]) -> None:
    calculo.items = [CalculoItem(**_compute_item(item)) for item in items]


def _recalc(calculo: Calculo) -> None:
    venta = sum((Decimal(str(i.precio_venta_total)) for i in calculo.items), Decimal("0"))
    costo = sum((Decimal(str(i.precio_compra_total)) for i in calculo.items), Decimal("0"))
    calculo.venta_total = float(_money(venta))
    calculo.costo_total = float(_money(costo))
    calculo.ganancia_total = float(_money(venta - costo))


def create_calculo(db: Session, data: CalculoCreate, user_id: int | None) -> Calculo:
    calculo = Calculo(
        folio=_unique_calculo_folio(db),
        cliente_id=data.cliente_id,
        fecha=data.fecha or date.today(),
        moneda=data.moneda,
        notas=data.notas,
        created_by_id=user_id,
    )
    _apply_items(calculo, data.items)
    _recalc(calculo)
    db.add(calculo)
    db.commit()
    db.refresh(calculo)
    return calculo


def update_calculo(db: Session, calculo: Calculo, data: CalculoUpdate) -> Calculo:
    payload = data.model_dump(exclude_unset=True)
    items = payload.pop("items", None)
    for field, value in payload.items():
        if value is not None:
            setattr(calculo, field, value)
    if items is not None:
        _apply_items(calculo, [CalculoItemIn(**item) for item in items])
    _recalc(calculo)
    db.commit()
    db.refresh(calculo)
    return calculo


def generar_cotizacion(
    db: Session, calculo: Calculo, data: GenerarCotizacionRequest, user_id: int | None
) -> Cotizacion:
    seleccionados = [item for item in calculo.items if item.id in set(data.item_ids)]
    if not seleccionados:
        raise ValueError("Selecciona al menos una partida del cálculo")

    from app.schemas.cotizacion import ItemIn

    items_in = [
        ItemIn(
            tipo=TipoItem(item.tipo),
            descripcion=item.descripcion or item.partida or "Partida",
            unidad="Servicio" if item.tipo == TipoItem.SERVICIO else "Pieza",
            cantidad=float(item.cantidad),
            precio_unitario=float(item.precio_venta_unitario),
            descuento_porcentaje=0,
            tiempo_entrega_dias=item.tiempo_entrega_dias,
        )
        for item in seleccionados
    ]
    iva = Decimal(str(get_settings().iva_porcentaje))
    result = totals(items_in, iva)

    cotizacion = Cotizacion(
        folio=unique_folio(db),
        cliente_id=calculo.cliente_id,
        fecha=date.today(),
        valida_hasta=data.valida_hasta,
        estado="borrador",
        moneda=calculo.moneda,
        iva_porcentaje=get_settings().iva_porcentaje,
        notas=data.notas,
        created_by_id=user_id,
        calculo_id=calculo.id,
        tiempo_entrega_dias=max((i.tiempo_entrega_dias for i in items_in), default=0),
        subtotal=float(result["subtotal"]),
        descuento_total=float(result["descuento_total"]),
        iva_total=float(result["iva_total"]),
        total=float(result["total"]),
    )
    cotizacion.items = [
        CotizacionItem(
            tipo=item.tipo,
            descripcion=item.descripcion,
            unidad=item.unidad,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            descuento_porcentaje=item.descuento_porcentaje,
            importe=float(item_importe(item)),
            tiempo_entrega_dias=item.tiempo_entrega_dias,
        )
        for item in items_in
    ]
    db.add(cotizacion)
    db.commit()
    db.refresh(cotizacion)
    return cotizacion
