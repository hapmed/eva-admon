"""Clientes: altas, bajas (desactivación) y cambios."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.roles import Role
from app.deps import current_user, get_session, require_roles
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteRead, ClienteUpdate
from app.services.clientes import create_cliente, list_clientes, update_cliente

router = APIRouter(prefix="/clientes", tags=["clientes"])
_writer = require_roles(Role.ADMIN, Role.VENTAS)


def _get(db: Session, cliente_id: int) -> Cliente:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return cliente


@router.get("", response_model=list[ClienteRead], summary="Listar clientes")
def get_clientes(
    search: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_session),
    _: Usuario = Depends(current_user),
) -> list[Cliente]:
    return list_clientes(db, search=search, include_inactive=include_inactive)


@router.post("", response_model=ClienteRead, status_code=status.HTTP_201_CREATED, summary="Crear cliente")
def post_cliente(
    data: ClienteCreate, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> Cliente:
    return create_cliente(db, data)


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
    return update_cliente(db, _get(db, cliente_id), data)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar cliente")
def delete_cliente(
    cliente_id: int, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> None:
    cliente = _get(db, cliente_id)
    cliente.activo = False
    db.commit()
