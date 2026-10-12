"""Clientes y sus contactos."""

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Cliente(TimestampMixin, Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    rfc: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(255), index=True)
    condiciones_pago: Mapped[str] = mapped_column(Text, default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    contactos: Mapped[list["ContactoCliente"]] = relationship(
        back_populates="cliente",
        cascade="all, delete-orphan",
        order_by="ContactoCliente.id",
    )


class ContactoCliente(TimestampMixin, Base):
    __tablename__ = "cliente_contacto"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("cliente.id", ondelete="CASCADE"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(255))

    cliente: Mapped[Cliente] = relationship(back_populates="contactos")
