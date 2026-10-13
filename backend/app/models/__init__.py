"""Modelos SQLAlchemy. Importar aquí registra todo en `Base.metadata`."""

from app.models.calculo import Calculo, CalculoItem
from app.models.catalogo import Material, Servicio
from app.models.cliente import Cliente, ContactoCliente
from app.models.consecutivo import Consecutivo
from app.models.cotizacion import Cotizacion, CotizacionItem
from app.models.empresa import EmpresaConfig
from app.models.usuario import Usuario

__all__ = [
    "Calculo",
    "CalculoItem",
    "Cliente",
    "Consecutivo",
    "ContactoCliente",
    "Cotizacion",
    "CotizacionItem",
    "EmpresaConfig",
    "Material",
    "Servicio",
    "Usuario",
]
