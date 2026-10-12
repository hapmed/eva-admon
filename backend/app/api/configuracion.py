"""Configuración de la empresa emisora y su logo."""

import re
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.roles import Role
from app.deps import current_user, get_session, require_roles
from app.models.empresa import EmpresaConfig
from app.models.usuario import Usuario
from app.schemas.empresa import EmpresaRead, EmpresaUpdate

router = APIRouter(prefix="/configuracion", tags=["configuracion"])
_admin = require_roles(Role.ADMIN)

_ALLOWED_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
_MAX_LOGO_BYTES = 2 * 1024 * 1024


def get_or_create(db: Session) -> EmpresaConfig:
    config = db.get(EmpresaConfig, 1)
    if config is None:
        settings = get_settings()
        config = EmpresaConfig(id=1, iva_porcentaje=settings.iva_porcentaje, moneda=settings.moneda)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def _to_read(config: EmpresaConfig) -> EmpresaRead:
    data = EmpresaRead.model_validate(config)
    data.tiene_logo = bool(config.logo_filename)
    return data


@router.get("", response_model=EmpresaRead, summary="Consultar configuración")
def read_configuracion(
    db: Session = Depends(get_session), _: Usuario = Depends(current_user)
) -> EmpresaRead:
    return _to_read(get_or_create(db))


@router.put("", response_model=EmpresaRead, summary="Editar configuración")
def update_configuracion(
    data: EmpresaUpdate, db: Session = Depends(get_session), _: Usuario = Depends(_admin)
) -> EmpresaRead:
    config = get_or_create(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    db.commit()
    db.refresh(config)
    return _to_read(config)


@router.post("/logo", response_model=EmpresaRead, summary="Subir logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    _: Usuario = Depends(_admin),
) -> EmpresaRead:
    extension = _ALLOWED_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no permitido (usa PNG, JPG o WEBP)",
        )
    content = await file.read()
    if len(content) > _MAX_LOGO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El logo no debe exceder 2 MB",
        )
    config = get_or_create(db)
    directory = Path(get_settings().logo_dir)
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"logo-{secrets.token_hex(8)}{extension}"
    (directory / filename).write_bytes(content)
    if config.logo_filename and config.logo_filename != filename:
        old = directory / config.logo_filename
        if old.is_file():
            old.unlink(missing_ok=True)
    config.logo_filename = filename
    config.logo_content_type = file.content_type
    db.commit()
    db.refresh(config)
    return _to_read(config)


@router.get("/logo", summary="Descargar logo")
def download_logo(db: Session = Depends(get_session)) -> FileResponse:
    config = get_or_create(db)
    if not config.logo_filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sin logo")
    path = Path(get_settings().logo_dir) / config.logo_filename
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sin logo")
    media_type = re.sub(r"[^a-zA-Z0-9/+.-]", "", config.logo_content_type or "image/png")
    return FileResponse(path, media_type=media_type, filename=config.logo_filename)
