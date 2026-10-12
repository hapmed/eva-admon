"""SMTP por cliente y colores de marca del logo.

Revision ID: 0002_smtp_colores
Revises: 0001_initial
Create Date: 2026-10-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_smtp_colores"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_COLUMNS = [
    sa.Column("color_primary", sa.String(7), nullable=False, server_default=""),
    sa.Column("color_secondary", sa.String(7), nullable=False, server_default=""),
    sa.Column("smtp_activo", sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column("smtp_host", sa.String(255), nullable=False, server_default=""),
    sa.Column("smtp_port", sa.Integer(), nullable=False, server_default="587"),
    sa.Column("smtp_security", sa.String(10), nullable=False, server_default="tls"),
    sa.Column("smtp_username", sa.String(255), nullable=False, server_default=""),
    sa.Column("smtp_password", sa.String(255), nullable=False, server_default=""),
    sa.Column("smtp_from_email", sa.String(255), nullable=False, server_default=""),
    sa.Column("smtp_from_name", sa.String(255), nullable=False, server_default=""),
]


def upgrade() -> None:
    for column in _COLUMNS:
        op.add_column("empresa_config", column)


def downgrade() -> None:
    for column in reversed(_COLUMNS):
        op.drop_column("empresa_config", column.name)
