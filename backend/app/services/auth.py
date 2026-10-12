"""Autenticación y bootstrap del administrador."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.roles import Role
from app.core.security import hash_password, verify_password
from app.models.usuario import Usuario


def authenticate(db: Session, email: str, password: str) -> Usuario | None:
    user = db.scalar(select(Usuario).where(func.lower(Usuario.email) == email.lower()))
    if user is None or not user.activo:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def ensure_admin(db: Session, email: str, password: str, nombre: str) -> Usuario | None:
    """Crea el admin inicial si no existe ningún usuario. Idempotente."""
    if not email or not password:
        return None
    existing = db.scalar(select(func.count()).select_from(Usuario))
    if existing:
        return None
    user = Usuario(
        email=email.lower(),
        nombre=nombre or "Administrador",
        password_hash=hash_password(password),
        rol=Role.ADMIN,
        activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
