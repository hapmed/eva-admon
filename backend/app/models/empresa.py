"""Configuración de la empresa emisora (registro único)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
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
    sitio_web: Mapped[str] = mapped_column(String(255), default="")

    # Domicilio fiscal (se imprime en la cotización).
    direccion: Mapped[str] = mapped_column(String(255), default="")
    ciudad: Mapped[str] = mapped_column(String(120), default="")
    estado: Mapped[str] = mapped_column(String(120), default="")
    codigo_postal: Mapped[str] = mapped_column(String(20), default="")
    pais: Mapped[str] = mapped_column(String(120), default="México")

    logo_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Colores de marca (extraídos del logo o definidos manualmente).
    color_primary: Mapped[str] = mapped_column(String(7), default="")
    color_secondary: Mapped[str] = mapped_column(String(7), default="")

    # SMTP (por cliente/instalación). La contraseña se guarda en la BD del cliente.
    smtp_activo: Mapped[bool] = mapped_column(Boolean, default=False)
    smtp_host: Mapped[str] = mapped_column(String(255), default="")
    smtp_port: Mapped[int] = mapped_column(Integer, default=587)
    smtp_security: Mapped[str] = mapped_column(String(10), default="tls")
    smtp_username: Mapped[str] = mapped_column(String(255), default="")
    smtp_password: Mapped[str] = mapped_column(String(255), default="")
    smtp_from_email: Mapped[str] = mapped_column(String(255), default="")
    smtp_from_name: Mapped[str] = mapped_column(String(255), default="")

    iva_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=16)
    moneda: Mapped[str] = mapped_column(String(3), default="MXN")

    # Tipo de cambio USD -> MXN (referencia, por defecto).
    tipo_cambio_usd: Mapped[float] = mapped_column(Numeric(14, 4), default=0)
    tipo_cambio_actualizado: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
