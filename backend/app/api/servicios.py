"""Catálogo de servicios."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.pagination import paginate
from app.core.roles import Role
from app.deps import current_user, get_session, require_roles
from app.models.catalogo import Servicio
from app.models.usuario import Usuario
from app.schemas.catalogo import CatalogoCreate, CatalogoRead, CatalogoUpdate
from app.schemas.common import Page

router = APIRouter(prefix="/servicios", tags=["servicios"])
_writer = require_roles(Role.ADMIN, Role.VENTAS)


def _get(db: Session, item_id: int) -> Servicio:
    item = db.get(Servicio, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    return item


@router.get("", response_model=Page[CatalogoRead], summary="Listar servicios")
def list_servicios(
    search: str | None = Query(default=None),
    activo: bool | None = Query(default=True),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_session),
    _: Usuario = Depends(current_user),
) -> dict:
    stmt = select(Servicio)
    if activo is not None:
        stmt = stmt.where(Servicio.activo.is_(activo))
    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(
            func.lower(Servicio.nombre).like(like) | func.lower(Servicio.codigo).like(like)
        )
    return paginate(db, stmt.order_by(Servicio.codigo), page, page_size)


@router.post("", response_model=CatalogoRead, status_code=status.HTTP_201_CREATED, summary="Crear servicio")
def create_servicio(
    data: CatalogoCreate, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> Servicio:
    item = Servicio(**data.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código ya existe") from None
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=CatalogoRead, summary="Editar servicio")
def update_servicio(
    item_id: int,
    data: CatalogoUpdate,
    db: Session = Depends(get_session),
    _: Usuario = Depends(_writer),
) -> Servicio:
    item = _get(db, item_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código ya existe") from None
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar servicio")
def delete_servicio(
    item_id: int, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> None:
    item = _get(db, item_id)
    item.activo = False
    db.commit()
