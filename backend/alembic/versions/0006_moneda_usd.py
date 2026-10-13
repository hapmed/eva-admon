"""Moneda por documento y tipo de cambio USD.

Revision ID: 0006_moneda_usd
Revises: 0005_calculos
Create Date: 2026-10-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_moneda_usd"
down_revision: str | None = "0005_calculos"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "empresa_config",
        sa.Column("tipo_cambio_usd", sa.Numeric(14, 4), nullable=False, server_default="0"),
    )
    op.add_column(
        "empresa_config", sa.Column("tipo_cambio_actualizado", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "cotizacion", sa.Column("moneda", sa.String(3), nullable=False, server_default="MXN")
    )
    op.add_column("calculo", sa.Column("moneda", sa.String(3), nullable=False, server_default="MXN"))


def downgrade() -> None:
    op.drop_column("calculo", "moneda")
    op.drop_column("cotizacion", "moneda")
    op.drop_column("empresa_config", "tipo_cambio_actualizado")
    op.drop_column("empresa_config", "tipo_cambio_usd")
