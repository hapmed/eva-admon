"""Bootstrap de la aplicación FastAPI de la EVA."""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.health import router as health_router
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

# Rutas que nunca deben devolver el SPA (API, salud, docs).
_RESERVED_PREFIXES = ("/api", "/healthz", "/readyz", "/docs", "/redoc", "/openapi.json")


def _mount_spa(app: FastAPI, static_dir: str) -> None:
    """Sirve el frontend compilado (SPA) con respaldo a index.html."""
    index = Path(static_dir) / "index.html"

    @app.exception_handler(404)
    async def spa_fallback(request: Request, exc: Exception) -> JSONResponse | FileResponse:
        detail = getattr(exc, "detail", "Not Found")
        path = request.url.path
        if path.startswith(_RESERVED_PREFIXES) or not index.is_file():
            return JSONResponse({"detail": detail}, status_code=404)
        return FileResponse(index)

    app.mount("/", StaticFiles(directory=static_dir, html=True), name="spa")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging("DEBUG" if settings.debug else "INFO")

    app = FastAPI(title=settings.app_name, version=settings.version)
    app.include_router(health_router)
    app.include_router(api_router)

    if settings.static_dir and os.path.isdir(settings.static_dir):
        _mount_spa(app, settings.static_dir)

    return app


app = create_app()
