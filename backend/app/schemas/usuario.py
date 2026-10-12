"""Esquemas de usuarios."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.roles import Role


class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=1, max_length=200)
    rol: Role = Role.CONSULTA
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=8, max_length=128)


class UsuarioUpdate(BaseModel):
    email: EmailStr | None = None
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    rol: Role | None = None
    activo: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nombre: str
    rol: Role
    activo: bool
