"""Indicadores del dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import current_user, get_session
from app.models.cliente import Cliente
from app.models.cotizacion import Cotizacion, EstadoCotizacion
from app.models.usuario import Usuario
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummary, summary="Resumen")
def get_dashboard(
    db: Session = Depends(get_session), _: Usuario = Depends(current_user)
) -> DashboardSummary:
    total_clientes = db.scalar(select(func.count()).select_from(Cliente).where(Cliente.activo.is_(True))) or 0
    total_usuarios = db.scalar(select(func.count()).select_from(Usuario).where(Usuario.activo.is_(True))) or 0
    total_cotizaciones = db.scalar(select(func.count()).select_from(Cotizacion)) or 0
    borradores = (
        db.scalar(
            select(func.count())
            .select_from(Cotizacion)
            .where(Cotizacion.estado == EstadoCotizacion.BORRADOR)
        )
        or 0
    )
    total_cotizado = db.scalar(select(func.coalesce(func.sum(Cotizacion.total), 0))) or 0
    return DashboardSummary(
        clientes=total_clientes,
        usuarios=total_usuarios,
        cotizaciones=total_cotizaciones,
        cotizaciones_borrador=borradores,
        total_cotizado=float(total_cotizado),
    )
