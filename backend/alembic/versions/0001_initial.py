"""Migración inicial: usuarios, empresa, clientes, catálogos y cotizaciones.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False, server_default="consulta"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_usuario_email", "usuario", ["email"], unique=True)

    op.create_table(
        "empresa_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("razon_social", sa.String(255), nullable=False, server_default=""),
        sa.Column("nombre_comercial", sa.String(255), nullable=False, server_default=""),
        sa.Column("rfc", sa.String(20), nullable=False, server_default=""),
        sa.Column("telefono", sa.String(40), nullable=False, server_default=""),
        sa.Column("email", sa.String(255), nullable=False, server_default=""),
        sa.Column("whatsapp", sa.String(40), nullable=False, server_default=""),
        sa.Column("logo_filename", sa.String(255), nullable=True),
        sa.Column("logo_content_type", sa.String(100), nullable=True),
        sa.Column("iva_porcentaje", sa.Numeric(5, 2), nullable=False, server_default="16"),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="MXN"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "cliente",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numero_cliente", sa.String(30), nullable=False),
        sa.Column("rfc", sa.String(20), nullable=False, server_default=""),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("condiciones_pago", sa.Text(), nullable=False, server_default=""),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cliente_numero_cliente", "cliente", ["numero_cliente"], unique=True)
    op.create_index("ix_cliente_nombre", "cliente", ["nombre"])

    op.create_table(
        "cliente_contacto",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "cliente_id",
            sa.Integer(),
            sa.ForeignKey("cliente.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cliente_contacto_cliente_id", "cliente_contacto", ["cliente_id"])

    op.create_table(
        "servicio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(40), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False, server_default=""),
        sa.Column("unidad", sa.String(40), nullable=False, server_default="Servicio"),
        sa.Column("precio_unitario", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_servicio_codigo", "servicio", ["codigo"], unique=True)

    op.create_table(
        "material",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(40), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False, server_default=""),
        sa.Column("unidad", sa.String(40), nullable=False, server_default="Pieza"),
        sa.Column("precio_unitario", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_material_codigo", "material", ["codigo"], unique=True)

    op.create_table(
        "consecutivo",
        sa.Column("scope", sa.String(40), primary_key=True),
        sa.Column("last_value", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "cotizacion",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("folio", sa.String(30), nullable=False),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("cliente.id"), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("valida_hasta", sa.Date(), nullable=True),
        sa.Column("estado", sa.String(20), nullable=False, server_default="borrador"),
        sa.Column("iva_porcentaje", sa.Numeric(5, 2), nullable=False, server_default="16"),
        sa.Column("subtotal", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("descuento_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("iva_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("notas", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cotizacion_folio", "cotizacion", ["folio"], unique=True)
    op.create_index("ix_cotizacion_cliente_id", "cotizacion", ["cliente_id"])

    op.create_table(
        "cotizacion_item",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "cotizacion_id",
            sa.Integer(),
            sa.ForeignKey("cotizacion.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo", sa.String(20), nullable=False, server_default="servicio"),
        sa.Column("descripcion", sa.String(500), nullable=False),
        sa.Column("unidad", sa.String(40), nullable=False, server_default=""),
        sa.Column("cantidad", sa.Numeric(14, 3), nullable=False, server_default="1"),
        sa.Column("precio_unitario", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("descuento_porcentaje", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("importe", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cotizacion_item_cotizacion_id", "cotizacion_item", ["cotizacion_id"])


def downgrade() -> None:
    op.drop_table("cotizacion_item")
    op.drop_table("cotizacion")
    op.drop_table("consecutivo")
    op.drop_table("material")
    op.drop_table("servicio")
    op.drop_table("cliente_contacto")
    op.drop_table("cliente")
    op.drop_table("empresa_config")
    op.drop_table("usuario")
