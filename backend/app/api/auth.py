"""Autenticación: inicio de sesión y usuario actual."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.deps import current_user, get_session
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.usuario import UsuarioRead
from app.services.auth import authenticate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(payload: LoginRequest, db: Session = Depends(get_session)) -> TokenResponse:
    user = authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    token = create_access_token(str(user.id), role=user.rol)
    return TokenResponse(access_token=token, user=UsuarioRead.model_validate(user))


@router.get("/me", response_model=UsuarioRead, summary="Usuario actual")
def me(user: Usuario = Depends(current_user)) -> Usuario:
    return user
