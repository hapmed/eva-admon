"""Cotizaciones de servicio y materiales."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.configuracion import get_or_create as get_empresa
from app.api.pagination import paginate
from app.core.roles import Role
from app.deps import current_user, get_session, require_roles
from app.models.cliente import Cliente
from app.models.cotizacion import Cotizacion, EstadoCotizacion
from app.models.usuario import Usuario
from app.schemas.common import Page
from app.schemas.cotizacion import (
    CotizacionCreate,
    CotizacionEnviarRequest,
    CotizacionListItem,
    CotizacionRead,
    CotizacionUpdate,
)
from app.services.cotizaciones import create_cotizacion, update_cotizacion
from app.services.mailer import MailError, send_email
from app.services.pdf import render_cotizacion_pdf

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])
_writer = require_roles(Role.ADMIN, Role.VENTAS)


def _load(db: Session, cotizacion_id: int) -> Cotizacion:
    stmt = (
        select(Cotizacion)
        .options(selectinload(Cotizacion.items), selectinload(Cotizacion.cliente))
        .where(Cotizacion.id == cotizacion_id)
    )
    cotizacion = db.scalar(stmt)
    if cotizacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotización no encontrada")
    return cotizacion


@router.get("", response_model=Page[CotizacionListItem], summary="Listar cotizaciones")
def list_cotizaciones(
    search: str | None = Query(default=None),
    estado: EstadoCotizacion | None = Query(default=None),
    cliente_id: int | None = Query(default=None),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_session),
    _: Usuario = Depends(current_user),
) -> dict:
    stmt = select(Cotizacion).options(selectinload(Cotizacion.cliente))
    if estado is not None:
        stmt = stmt.where(Cotizacion.estado == estado)
    if cliente_id is not None:
        stmt = stmt.where(Cotizacion.cliente_id == cliente_id)
    if desde is not None:
        stmt = stmt.where(Cotizacion.fecha >= desde)
    if hasta is not None:
        stmt = stmt.where(Cotizacion.fecha <= hasta)
    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.join(Cliente).where(
            func.lower(Cotizacion.folio).like(like) | func.lower(Cliente.nombre).like(like)
        )
    return paginate(db, stmt.order_by(Cotizacion.id.desc()), page, page_size)


@router.post(
    "", response_model=CotizacionRead, status_code=status.HTTP_201_CREATED, summary="Crear cotización"
)
def post_cotizacion(
    data: CotizacionCreate, db: Session = Depends(get_session), user: Usuario = Depends(_writer)
) -> Cotizacion:
    if db.get(Cliente, data.cliente_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    cotizacion = create_cotizacion(db, data, user.id)
    return _load(db, cotizacion.id)


@router.get("/{cotizacion_id}", response_model=CotizacionRead, summary="Consultar cotización")
def get_cotizacion(
    cotizacion_id: int, db: Session = Depends(get_session), _: Usuario = Depends(current_user)
) -> Cotizacion:
    return _load(db, cotizacion_id)


@router.patch("/{cotizacion_id}", response_model=CotizacionRead, summary="Editar cotización")
def patch_cotizacion(
    cotizacion_id: int,
    data: CotizacionUpdate,
    db: Session = Depends(get_session),
    _: Usuario = Depends(_writer),
) -> Cotizacion:
    cotizacion = _load(db, cotizacion_id)
    if data.cliente_id is not None and db.get(Cliente, data.cliente_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    update_cotizacion(db, cotizacion, data)
    return _load(db, cotizacion_id)


@router.delete("/{cotizacion_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Cancelar cotización")
def delete_cotizacion(
    cotizacion_id: int, db: Session = Depends(get_session), _: Usuario = Depends(_writer)
) -> None:
    cotizacion = _load(db, cotizacion_id)
    cotizacion.estado = EstadoCotizacion.CANCELADA
    db.commit()


@router.get("/{cotizacion_id}/pdf", summary="Descargar PDF")
def get_cotizacion_pdf(
    cotizacion_id: int, db: Session = Depends(get_session), _: Usuario = Depends(current_user)
) -> Response:
    cotizacion = _load(db, cotizacion_id)
    empresa = get_empresa(db)
    content = render_cotizacion_pdf(cotizacion, empresa)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="cotizacion-{cotizacion.folio}.pdf"'},
    )


@router.post("/{cotizacion_id}/enviar", summary="Enviar cotización por correo")
def enviar_cotizacion(
    cotizacion_id: int,
    data: CotizacionEnviarRequest,
    db: Session = Depends(get_session),
    _: Usuario = Depends(_writer),
) -> dict[str, str]:
    cotizacion = _load(db, cotizacion_id)
    empresa = get_empresa(db)
    content = render_cotizacion_pdf(cotizacion, empresa)
    remitente = empresa.nombre_comercial or empresa.razon_social or "HAPMED"
    asunto = data.asunto or f"Cotización {cotizacion.folio} - {remitente}"
    mensaje = data.mensaje or (
        f"Estimado(a) cliente:\n\nAdjuntamos la cotización {cotizacion.folio}.\n\nSaludos,\n{remitente}"
    )
    try:
        send_email(
            empresa,
            to=[str(dest) for dest in data.destinatarios],
            cc=[str(dest) for dest in data.cc],
            subject=asunto,
            body=mensaje,
            attachments=[(f"cotizacion-{cotizacion.folio}.pdf", content, "application/pdf")],
        )
    except MailError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    cotizacion.estado = EstadoCotizacion.ENVIADA
    db.commit()
    return {"status": "ok", "mensaje": "Cotización enviada por correo."}
