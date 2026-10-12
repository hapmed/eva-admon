"""Esquemas de catálogos (servicios y materiales)."""

from pydantic import BaseModel, ConfigDict, Field


class CatalogoBase(BaseModel):
    codigo: str = Field(min_length=1, max_length=40)
    nombre: str = Field(min_length=1, max_length=255)
    descripcion: str = ""
    unidad: str = Field(default="", max_length=40)
    precio_unitario: float = Field(default=0, ge=0)
    activo: bool = True


class CatalogoCreate(CatalogoBase):
    pass


class CatalogoUpdate(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=40)
    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    descripcion: str | None = None
    unidad: str | None = Field(default=None, max_length=40)
    precio_unitario: float | None = Field(default=None, ge=0)
    activo: bool | None = None


class CatalogoRead(CatalogoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
