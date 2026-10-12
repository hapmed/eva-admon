"""Catálogos de servicios y materiales."""

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Servicio(TimestampMixin, Base):
    __tablename__ = "servicio"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    unidad: Mapped[str] = mapped_column(String(40), default="Servicio")
    precio_unitario: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Material(TimestampMixin, Base):
    __tablename__ = "material"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    unidad: Mapped[str] = mapped_column(String(40), default="Pieza")
    precio_unitario: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
