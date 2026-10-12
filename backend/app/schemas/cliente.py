"""Esquemas de clientes y contactos."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactoBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    email: EmailStr


class ContactoCreate(ContactoBase):
    pass


class ContactoRead(ContactoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ClienteBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    rfc: str = Field(min_length=1, max_length=20)
    condiciones_pago: str = ""
    activo: bool = True


class ClienteCreate(ClienteBase):
    contactos: list[ContactoCreate] = Field(default_factory=list)


class ClienteUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    rfc: str | None = Field(default=None, min_length=1, max_length=20)
    condiciones_pago: str | None = None
    activo: bool | None = None
    contactos: list[ContactoCreate] | None = None


class ClienteRead(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contactos: list[ContactoRead] = Field(default_factory=list)
