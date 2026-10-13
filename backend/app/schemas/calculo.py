"""Esquemas de cálculos."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.cotizacion import TipoItem
from app.schemas.cotizacion import ClienteResumen


class CalculoItemIn(BaseModel):
    partida: str = Field(default="", max_length=120)
    tipo: TipoItem = TipoItem.MATERIAL
    descripcion: str = ""
    modelo: str = Field(default="", max_length=200)
    cantidad: float = Field(gt=0)
    precio_compra_unitario: float = Field(default=0, ge=0)
    porcentaje_aumento: float = Field(default=25, ge=0, le=1000)
    # Solo para servicio: precio de venta capturado manualmente.
    precio_venta_unitario: float | None = Field(default=None, ge=0)
    proveedor: str = Field(default="", max_length=200)
    tiempo_entrega_dias: int = Field(default=0, ge=0, le=3650)


class CalculoItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    partida: str
    tipo: TipoItem
    descripcion: str
    modelo: str
    cantidad: float
    precio_compra_unitario: float
    precio_compra_total: float
    porcentaje_aumento: float
    precio_venta_unitario: float
    precio_venta_total: float
    proveedor: str
    tiempo_entrega_dias: int


class CalculoCreate(BaseModel):
    cliente_id: int
    fecha: date | None = None
    moneda: str = Field(default="MXN", max_length=3)
    notas: str = ""
    items: list[CalculoItemIn] = Field(default_factory=list)


class CalculoUpdate(BaseModel):
    cliente_id: int | None = None
    fecha: date | None = None
    moneda: str | None = Field(default=None, max_length=3)
    notas: str | None = None
    items: list[CalculoItemIn] | None = None


class CalculoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    cliente_id: int
    cliente: ClienteResumen
    fecha: date
    moneda: str = "MXN"
    notas: str
    venta_total: float
    costo_total: float
    ganancia_total: float
    items: list[CalculoItemRead] = Field(default_factory=list)


class CalculoListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    cliente: ClienteResumen
    fecha: date
    moneda: str = "MXN"
    venta_total: float
    ganancia_total: float


class GenerarCotizacionRequest(BaseModel):
    item_ids: list[int] = Field(min_length=1)
    valida_hasta: date | None = None
    notas: str = ""
