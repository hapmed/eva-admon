"""Gestión de usuarios y roles (solo administradores)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.roles import Role
from app.core.security import hash_password
from app.deps import get_session, require_roles
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])
_admin = require_roles(Role.ADMIN)


def _get(db: Session, user_id: int) -> Usuario:
    user = db.get(Usuario, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


def _ensure_email_free(db: Session, email: str, exclude_id: int | None = None) -> None:
    stmt = select(Usuario).where(func.lower(Usuario.email) == email.lower())
    if exclude_id is not None:
        stmt = stmt.where(Usuario.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado")


@router.get("", response_model=list[UsuarioRead], summary="Listar usuarios")
def list_usuarios(db: Session = Depends(get_session), _: Usuario = Depends(_admin)) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.id)))


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED, summary="Crear usuario")
def create_usuario(
    data: UsuarioCreate, db: Session = Depends(get_session), _: Usuario = Depends(_admin)
) -> Usuario:
    _ensure_email_free(db, data.email)
    user = Usuario(
        email=data.email.lower(),
        nombre=data.nombre,
        password_hash=hash_password(data.password),
        rol=data.rol,
        activo=data.activo,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UsuarioRead, summary="Consultar usuario")
def get_usuario(
    user_id: int, db: Session = Depends(get_session), _: Usuario = Depends(_admin)
) -> Usuario:
    return _get(db, user_id)


@router.patch("/{user_id}", response_model=UsuarioRead, summary="Editar usuario")
def update_usuario(
    user_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_session),
    actor: Usuario = Depends(_admin),
) -> Usuario:
    user = _get(db, user_id)
    payload = data.model_dump(exclude_unset=True)
    if "email" in payload and payload["email"]:
        _ensure_email_free(db, payload["email"], exclude_id=user_id)
        payload["email"] = payload["email"].lower()
    if "password" in payload:
        password = payload.pop("password")
        if password:
            user.password_hash = hash_password(password)
    for field, value in payload.items():
        setattr(user, field, value)
    _guard_last_admin(db, user, actor)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar usuario")
def delete_usuario(
    user_id: int, db: Session = Depends(get_session), actor: Usuario = Depends(_admin)
) -> None:
    user = _get(db, user_id)
    if user.id == actor.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes desactivar tu propio usuario"
        )
    user.activo = False
    db.commit()


def _guard_last_admin(db: Session, user: Usuario, actor: Usuario) -> None:
    """Evita quedarse sin administradores activos."""
    if user.rol == Role.ADMIN and user.activo:
        return
    if user.id == actor.id and user.rol == Role.ADMIN:
        return
    admins = db.scalar(
        select(func.count())
        .select_from(Usuario)
        .where(Usuario.rol == Role.ADMIN, Usuario.activo.is_(True), Usuario.id != user.id)
    )
    if not admins:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe existir al menos un administrador activo",
        )
