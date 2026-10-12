"""Clientes por RFC (único) y sin número consecutivo.

Revision ID: 0003_cliente_rfc
Revises: 0002_smtp_colores
Create Date: 2026-10-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_cliente_rfc"
down_revision: str | None = "0002_smtp_colores"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Evita duplicados vacíos antes de crear el índice único.
    op.execute("UPDATE cliente SET rfc = 'SINRFC' || id WHERE rfc IS NULL OR rfc = ''")
    op.create_index("ix_cliente_rfc", "cliente", ["rfc"], unique=True)
    op.drop_column("cliente", "numero_cliente")


def downgrade() -> None:
    op.add_column("cliente", sa.Column("numero_cliente", sa.String(30), nullable=True))
    op.drop_index("ix_cliente_rfc", table_name="cliente")
