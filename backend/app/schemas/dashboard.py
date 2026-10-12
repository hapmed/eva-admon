"""Esquema del resumen del dashboard."""

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    clientes: int
    usuarios: int
    cotizaciones: int
    cotizaciones_borrador: int
    total_cotizado: float
