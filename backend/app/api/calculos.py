"""Cálculos (estimaciones de costo) y generación de cotizaciones."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.pagination import paginate
from app.core.roles import Role
from app.deps import current_user, get_session, require_roles
from app.models.calculo import Calculo
from app.models.cliente import Cliente
from app.models.cotizacion import Cotizacion
from app.models.usuario import Usuario
from app.schemas.calculo import (
    CalculoCreate,
    CalculoListItem,
    CalculoRead,
    CalculoUpdate,
    GenerarCotizacionRequest,
)
from app.schemas.common import Page
from app.schemas.cotizacion import CotizacionRead
from app.services.calculos import create_calculo, generar_cotizacion, update_calculo

router = APIRouter(prefix="/calculos", tags=["calculos"])
_writer = require_roles(Role.ADMIN, Role.VENTAS)


def _load(db: Session, calculo_id: int) -> Calculo:
    stmt = (
        select(Calculo)
        .options(selectinload(Calculo.items), selectinload(Calculo.cliente))
        .where(Calculo.id == calculo_id)
    )
    calculo = db.scalar(stmt)
    if calculo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cálculo no encontrado")
    return calculo


@router.get("", response_model=Page[CalculoListItem], summary="Listar cálculos")
def list_calculos(
    search: str | None = Query(default=None),
    cliente_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_session),
    _: Usuario = Depends(current_user),
) -> dict:
    stmt = select(Calculo).options(selectinload(Calculo.cliente))
    if cliente_id is not None:
        stmt = stmt.where(Calculo.cliente_id == cliente_id)
    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.join(Cliente).where(
            func.lower(Calculo.folio).like(like) | func.lower(Cliente.nombre).like(like)
        )
    return paginate(db, stmt.order_by(Calculo.id.desc()), page, page_size)


@router.post("", response_model=CalculoRead, status_code=status.HTTP_201_CREATED, summary="Crear cálculo")
def post_calculo(
    data: CalculoCreate, db: Session = Depends(get_session), user: Usuario = Depends(_writer)
) -> Calculo:
    if db.get(Cliente, data.cliente_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    calculo = create_calculo(db, data, user.id)
    return _load(db, calculo.id)


@router.get("/{calculo_id}", response_model=CalculoRead, summary="Consultar cálculo")
def get_calculo(
    calculo_id: int, db: Session = Depends(get_session), _: Usuario = Depends(current_user)
) -> Calculo:
    return _load(db, calculo_id)


@router.patch("/{calculo_id}", response_model=CalculoRead, summary="Editar cálculo")
def patch_calculo(
    calculo_id: int,
    data: CalculoUpdate,
    db: Session = Depends(get_session),
    _: Usuario = Depends(_writer),
) -> Calculo:
    calculo = _load(db, calculo_id)
    if data.cliente_id is not None and db.get(Cliente, data.cliente_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    update_calculo(db, calculo, data)
    return _load(db, calculo_id)


@router.delete("/{calculo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar cálculo")
def delete_calculo(
    calculo_id: int, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> None:
    calculo = _load(db, calculo_id)
    db.delete(calculo)
    db.commit()


@router.post("/{calculo_id}/cotizacion", response_model=CotizacionRead, summary="Generar cotización")
def post_generar_cotizacion(
    calculo_id: int,
    data: GenerarCotizacionRequest,
    db: Session = Depends(get_session),
    user: Usuario = Depends(_writer),
) -> Cotizacion:
    calculo = _load(db, calculo_id)
    try:
        cotizacion = generar_cotizacion(db, calculo, data, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    result = db.scalar(
        select(Cotizacion)
        .options(selectinload(Cotizacion.items), selectinload(Cotizacion.cliente))
        .where(Cotizacion.id == cotizacion.id)
    )
    if result is None:  # pragma: no cover - recién creada
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno")
    return result
