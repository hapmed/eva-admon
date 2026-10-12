"""Generación de folios compactos.

Esquema: `<día del año><segundos del día><aleatorio>` en base36.
- día del año (1..366)  → 2 caracteres
- segundos del día (0..86399) → 4 caracteres
- aleatorio → N caracteres (para evitar colisiones dentro del mismo segundo)

Total por defecto: 8 caracteres (p. ej. `A61UNZ7Q`). Ordenable cronológicamente.
"""

import secrets
from datetime import UTC, datetime

from app.core.config import get_settings

_B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def to_base36(value: int) -> str:
    if value <= 0:
        return "0"
    out: list[str] = []
    while value:
        value, remainder = divmod(value, 36)
        out.append(_B36[remainder])
    return "".join(reversed(out))


def generate_folio() -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    day = now.timetuple().tm_yday
    seconds = now.hour * 3600 + now.minute * 60 + now.second
    suffix = "".join(
        secrets.choice(_B36) for _ in range(max(0, settings.folio_random_chars))
    )
    return f"{to_base36(day).zfill(2)}{to_base36(seconds).zfill(4)}{suffix}"
