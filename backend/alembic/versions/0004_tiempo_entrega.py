"""Tiempo de entrega por partida y general de la cotización.

Revision ID: 0004_tiempo_entrega
Revises: 0003_cliente_rfc
Create Date: 2026-10-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_tiempo_entrega"
down_revision: str | None = "0003_cliente_rfc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "cotizacion",
        sa.Column("tiempo_entrega_dias", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "cotizacion_item",
        sa.Column("tiempo_entrega_dias", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("cotizacion_item", "tiempo_entrega_dias")
    op.drop_column("cotizacion", "tiempo_entrega_dias")
