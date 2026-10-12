"""Cotizaciones (servicios y materiales) y sus partidas."""

from datetime import date
from enum import StrEnum

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.cliente import Cliente
from app.models.mixins import TimestampMixin


class TipoItem(StrEnum):
    SERVICIO = "servicio"
    MATERIAL = "material"


class EstadoCotizacion(StrEnum):
    BORRADOR = "borrador"
    ENVIADA = "enviada"
    ACEPTADA = "aceptada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"


class Cotizacion(TimestampMixin, Base):
    __tablename__ = "cotizacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    folio: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    valida_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="borrador")
    iva_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=16)
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    descuento_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    iva_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    # Tiempo de entrega general = el mayor de las partidas (días).
    tiempo_entrega_dias: Mapped[int] = mapped_column(Integer, default=0)
    notas: Mapped[str] = mapped_column(Text, default="")
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id"), nullable=True
    )

    items: Mapped[list["CotizacionItem"]] = relationship(
        back_populates="cotizacion",
        cascade="all, delete-orphan",
        order_by="CotizacionItem.id",
    )
    cliente: Mapped[Cliente] = relationship()


class CotizacionItem(TimestampMixin, Base):
    __tablename__ = "cotizacion_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    cotizacion_id: Mapped[int] = mapped_column(
        ForeignKey("cotizacion.id", ondelete="CASCADE"), index=True
    )
    tipo: Mapped[str] = mapped_column(String(20), default="servicio")
    descripcion: Mapped[str] = mapped_column(String(500))
    unidad: Mapped[str] = mapped_column(String(40), default="")
    cantidad: Mapped[float] = mapped_column(Numeric(14, 3), default=1)
    precio_unitario: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    descuento_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    importe: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    # Tiempo de entrega de esta partida (días).
    tiempo_entrega_dias: Mapped[int] = mapped_column(Integer, default=0)

    cotizacion: Mapped[Cotizacion] = relationship(back_populates="items")
