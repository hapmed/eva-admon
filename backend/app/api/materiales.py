"""Catálogo de materiales."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.pagination import paginate
from app.core.roles import Role
from app.deps import current_user, get_session, require_roles
from app.models.catalogo import Material
from app.models.usuario import Usuario
from app.schemas.catalogo import CatalogoCreate, CatalogoRead, CatalogoUpdate
from app.schemas.common import Page

router = APIRouter(prefix="/materiales", tags=["materiales"])
_writer = require_roles(Role.ADMIN, Role.VENTAS)


def _get(db: Session, item_id: int) -> Material:
    item = db.get(Material, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado")
    return item


@router.get("", response_model=Page[CatalogoRead], summary="Listar materiales")
def list_materiales(
    search: str | None = Query(default=None),
    activo: bool | None = Query(default=True),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_session),
    _: Usuario = Depends(current_user),
) -> dict:
    stmt = select(Material)
    if activo is not None:
        stmt = stmt.where(Material.activo.is_(activo))
    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(
            func.lower(Material.nombre).like(like) | func.lower(Material.codigo).like(like)
        )
    return paginate(db, stmt.order_by(Material.codigo), page, page_size)


@router.post("", response_model=CatalogoRead, status_code=status.HTTP_201_CREATED, summary="Crear material")
def create_material(
    data: CatalogoCreate, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> Material:
    item = Material(**data.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código ya existe") from None
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=CatalogoRead, summary="Editar material")
def update_material(
    item_id: int,
    data: CatalogoUpdate,
    db: Session = Depends(get_session),
    _: Usuario = Depends(_writer),
) -> Material:
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


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar material")
def delete_material(
    item_id: int, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> None:
    item = _get(db, item_id)
    item.activo = False
    db.commit()
