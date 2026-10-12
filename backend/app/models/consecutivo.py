"""Contadores consecutivos (folio de cliente y de cotización).

Garantiza números consecutivos sin huecos ni colisiones ante concurrencia
mediante bloqueo de fila (`SELECT ... FOR UPDATE`).
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Consecutivo(Base):
    __tablename__ = "consecutivo"

    scope: Mapped[str] = mapped_column(String(40), primary_key=True)
    last_value: Mapped[int] = mapped_column(Integer, default=0)
