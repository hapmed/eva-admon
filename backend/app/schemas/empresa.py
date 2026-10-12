"""Esquemas de configuración de la empresa."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmpresaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    razon_social: str
    nombre_comercial: str
    rfc: str
    telefono: str
    email: str
    whatsapp: str
    iva_porcentaje: float
    moneda: str
    tiene_logo: bool = False
    color_primary: str = ""
    color_secondary: str = ""
    smtp_activo: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_security: str = "tls"
    smtp_username: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = ""
    smtp_password_set: bool = False


class EmpresaUpdate(BaseModel):
    razon_social: str | None = None
    nombre_comercial: str | None = None
    rfc: str | None = None
    telefono: str | None = None
    email: str | None = None
    whatsapp: str | None = None
    iva_porcentaje: float | None = None
    moneda: str | None = None
    color_primary: str | None = None
    color_secondary: str | None = None
    smtp_activo: bool | None = None
    smtp_host: str | None = None
    smtp_port: int | None = Field(default=None, ge=1, le=65535)
    smtp_security: str | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str | None = None


class SmtpTestRequest(BaseModel):
    destino: EmailStr
