"""Router raíz de la API (`/api/v1`)."""

from fastapi import APIRouter

from app.api import (
    auth,
    clientes,
    configuracion,
    cotizaciones,
    dashboard,
    materiales,
    servicios,
    usuarios,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(clientes.router)
api_router.include_router(servicios.router)
api_router.include_router(materiales.router)
api_router.include_router(cotizaciones.router)
api_router.include_router(configuracion.router)
api_router.include_router(usuarios.router)
