"""Cálculos (estimaciones de costo) y sus partidas.

Un cálculo es interno: sirve para estimar costos y márgenes y, a partir de él,
generar una cotización al cliente (manteniendo el precio de venta del cálculo).
"""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.cliente import Cliente
from app.models.mixins import TimestampMixin


class Calculo(TimestampMixin, Base):
    __tablename__ = "calculo"

    id: Mapped[int] = mapped_column(primary_key=True)
    folio: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    moneda: Mapped[str] = mapped_column(String(3), default="MXN")
    notas: Mapped[str] = mapped_column(Text, default="")
    venta_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    costo_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    ganancia_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)

    items: Mapped[list["CalculoItem"]] = relationship(
        back_populates="calculo",
        cascade="all, delete-orphan",
        order_by="CalculoItem.id",
    )
    cliente: Mapped[Cliente] = relationship()


class CalculoItem(TimestampMixin, Base):
    __tablename__ = "calculo_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    calculo_id: Mapped[int] = mapped_column(
        ForeignKey("calculo.id", ondelete="CASCADE"), index=True
    )
    partida: Mapped[str] = mapped_column(String(120), default="")
    tipo: Mapped[str] = mapped_column(String(20), default="material")
    descripcion: Mapped[str] = mapped_column(Text, default="")
    modelo: Mapped[str] = mapped_column(String(200), default="")
    cantidad: Mapped[float] = mapped_column(Numeric(14, 3), default=1)
    precio_compra_unitario: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    precio_compra_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    porcentaje_aumento: Mapped[float] = mapped_column(Numeric(5, 2), default=25)
    precio_venta_unitario: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    precio_venta_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    proveedor: Mapped[str] = mapped_column(String(200), default="")
    tiempo_entrega_dias: Mapped[int] = mapped_column(Integer, default=0)

    calculo: Mapped[Calculo] = relationship(back_populates="items")
