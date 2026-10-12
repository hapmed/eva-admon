"""Esquemas de cotizaciones."""

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.cotizacion import EstadoCotizacion, TipoItem


class ItemIn(BaseModel):
    tipo: TipoItem
    descripcion: str = Field(min_length=1, max_length=500)
    unidad: str = Field(default="", max_length=40)
    cantidad: float = Field(gt=0)
    precio_unitario: float = Field(ge=0)
    descuento_porcentaje: float = Field(default=0, ge=0, le=100)
    tiempo_entrega_dias: int = Field(default=0, ge=0, le=3650)


class ItemRead(ItemIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    importe: float


class CotizacionCreate(BaseModel):
    cliente_id: int
    fecha: date | None = None
    valida_hasta: date | None = None
    iva_porcentaje: float | None = Field(default=None, ge=0, le=100)
    estado: EstadoCotizacion = EstadoCotizacion.BORRADOR
    notas: str = ""
    items: list[ItemIn] = Field(default_factory=list)


class CotizacionUpdate(BaseModel):
    cliente_id: int | None = None
    fecha: date | None = None
    valida_hasta: date | None = None
    iva_porcentaje: float | None = Field(default=None, ge=0, le=100)
    estado: EstadoCotizacion | None = None
    notas: str | None = None
    items: list[ItemIn] | None = None


class ClienteResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rfc: str
    nombre: str


class CotizacionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    cliente_id: int
    cliente: ClienteResumen
    fecha: date
    valida_hasta: date | None
    estado: EstadoCotizacion
    iva_porcentaje: float
    subtotal: float
    descuento_total: float
    iva_total: float
    total: float
    tiempo_entrega_dias: int = 0
    notas: str
    items: list[ItemRead] = Field(default_factory=list)


class CotizacionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    cliente: ClienteResumen
    fecha: date
    estado: EstadoCotizacion
    total: float


class CotizacionEnviarRequest(BaseModel):
    destinatarios: list[EmailStr] = Field(min_length=1)
    cc: list[EmailStr] = Field(default_factory=list)
    asunto: str | None = None
    mensaje: str | None = None
