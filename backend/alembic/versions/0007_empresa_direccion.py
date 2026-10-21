"""Domicilio fiscal y sitio web de la empresa emisora.

Revision ID: 0007_empresa_direccion
Revises: 0006_moneda_usd
Create Date: 2026-10-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_empresa_direccion"
down_revision: str | None = "0006_moneda_usd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_COLUMNS = (
    ("sitio_web", sa.String(255)),
    ("direccion", sa.String(255)),
    ("ciudad", sa.String(120)),
    ("estado", sa.String(120)),
    ("codigo_postal", sa.String(20)),
    ("pais", sa.String(120)),
)


def upgrade() -> None:
    for name, type_ in _COLUMNS:
        op.add_column(
            "empresa_config",
            sa.Column(name, type_, nullable=False, server_default=""),
        )
    op.execute("UPDATE empresa_config SET pais = 'México' WHERE pais = ''")


def downgrade() -> None:
    for name, _ in reversed(_COLUMNS):
        op.drop_column("empresa_config", name)
