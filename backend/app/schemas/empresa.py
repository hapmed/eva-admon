"""Esquemas de configuración de la empresa."""

from pydantic import BaseModel, ConfigDict


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


class EmpresaUpdate(BaseModel):
    razon_social: str | None = None
    nombre_comercial: str | None = None
    rfc: str | None = None
    telefono: str | None = None
    email: str | None = None
    whatsapp: str | None = None
    iva_porcentaje: float | None = None
    moneda: str | None = None
