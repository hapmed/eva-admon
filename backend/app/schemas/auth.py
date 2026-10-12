"""Esquemas de autenticación."""

from pydantic import BaseModel, EmailStr

from app.schemas.usuario import UsuarioRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioRead
