"""Módulo de cálculos (estimación de costo → cotización).

Revision ID: 0005_calculos
Revises: 0004_tiempo_entrega
Create Date: 2026-10-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_calculos"
down_revision: str | None = "0004_tiempo_entrega"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calculo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("folio", sa.String(30), nullable=False),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("cliente.id"), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("notas", sa.Text(), nullable=False, server_default=""),
        sa.Column("venta_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("costo_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("ganancia_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_calculo_folio", "calculo", ["folio"], unique=True)
    op.create_index("ix_calculo_cliente_id", "calculo", ["cliente_id"])

    op.create_table(
        "calculo_item",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "calculo_id",
            sa.Integer(),
            sa.ForeignKey("calculo.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("partida", sa.String(120), nullable=False, server_default=""),
        sa.Column("tipo", sa.String(20), nullable=False, server_default="material"),
        sa.Column("descripcion", sa.Text(), nullable=False, server_default=""),
        sa.Column("modelo", sa.String(200), nullable=False, server_default=""),
        sa.Column("cantidad", sa.Numeric(14, 3), nullable=False, server_default="1"),
        sa.Column("precio_compra_unitario", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("precio_compra_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("porcentaje_aumento", sa.Numeric(5, 2), nullable=False, server_default="25"),
        sa.Column("precio_venta_unitario", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("precio_venta_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("proveedor", sa.String(200), nullable=False, server_default=""),
        sa.Column("tiempo_entrega_dias", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_calculo_item_calculo_id", "calculo_item", ["calculo_id"])

    op.add_column("cotizacion", sa.Column("calculo_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_cotizacion_calculo", "cotizacion", "calculo", ["calculo_id"], ["id"])
    op.create_index("ix_cotizacion_calculo_id", "cotizacion", ["calculo_id"])


def downgrade() -> None:
    op.drop_index("ix_cotizacion_calculo_id", table_name="cotizacion")
    op.drop_constraint("fk_cotizacion_calculo", "cotizacion", type_="foreignkey")
    op.drop_column("cotizacion", "calculo_id")
    op.drop_table("calculo_item")
    op.drop_table("calculo")
