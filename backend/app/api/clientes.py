"""Clientes: altas, bajas (desactivación) y cambios."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.pagination import paginate
from app.core.roles import Role
from app.deps import current_user, get_session, require_roles
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteRead, ClienteUpdate
from app.schemas.common import Page
from app.services.clientes import clientes_query, create_cliente, update_cliente

router = APIRouter(prefix="/clientes", tags=["clientes"])
_writer = require_roles(Role.ADMIN, Role.VENTAS)
_DUP = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El RFC ya está registrado")


def _get(db: Session, cliente_id: int) -> Cliente:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return cliente


@router.get("", response_model=Page[ClienteRead], summary="Listar clientes")
def get_clientes(
    search: str | None = Query(default=None),
    activo: bool | None = Query(default=True),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_session),
    _: Usuario = Depends(current_user),
) -> dict:
    return paginate(db, clientes_query(search=search, activo=activo), page, page_size)


@router.post("", response_model=ClienteRead, status_code=status.HTTP_201_CREATED, summary="Crear cliente")
def post_cliente(
    data: ClienteCreate, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> Cliente:
    try:
        return create_cliente(db, data)
    except IntegrityError:
        db.rollback()
        raise _DUP from None


@router.get("/{cliente_id}", response_model=ClienteRead, summary="Consultar cliente")
def get_cliente(
    cliente_id: int, db: Session = Depends(get_session), _: Usuario = Depends(current_user)
) -> Cliente:
    return _get(db, cliente_id)


@router.patch("/{cliente_id}", response_model=ClienteRead, summary="Editar cliente")
def patch_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    db: Session = Depends(get_session),
    _: Usuario = Depends(_writer),
) -> Cliente:
    try:
        return update_cliente(db, _get(db, cliente_id), data)
    except IntegrityError:
        db.rollback()
        raise _DUP from None


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar cliente")
def delete_cliente(
    cliente_id: int, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> None:
    cliente = _get(db, cliente_id)
    cliente.activo = False
    db.commit()
