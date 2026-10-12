"""Configuración de la empresa emisora (registro único)."""

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class EmpresaConfig(TimestampMixin, Base):
    __tablename__ = "empresa_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(255), default="")
    nombre_comercial: Mapped[str] = mapped_column(String(255), default="")
    rfc: Mapped[str] = mapped_column(String(20), default="")
    telefono: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    whatsapp: Mapped[str] = mapped_column(String(40), default="")

    logo_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    iva_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=16)
    moneda: Mapped[str] = mapped_column(String(3), default="MXN")
