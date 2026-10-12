"""Consecutivos y folios.

Los contadores se guardan en la tabla `consecutivo` y se incrementan bajo
bloqueo de fila para evitar duplicados con concurrencia.
"""

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.consecutivo import Consecutivo


def next_value(db: Session, scope: str) -> int:
    counter = db.get(Consecutivo, scope, with_for_update=True)
    if counter is None:
        counter = Consecutivo(scope=scope, last_value=0)
        db.add(counter)
        db.flush()
    counter.last_value += 1
    db.flush()
    return counter.last_value


def format_folio(prefix: str, value: int) -> str:
    digits = get_settings().consecutivo_digitos
    return f"{prefix}{value:0{digits}d}"


def next_cliente_numero(db: Session) -> str:
    return format_folio(get_settings().cliente_prefijo, next_value(db, "cliente"))


def next_cotizacion_folio(db: Session) -> str:
    return format_folio(get_settings().cotizacion_prefijo, next_value(db, "cotizacion"))
