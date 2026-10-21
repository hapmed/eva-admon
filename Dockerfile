# syntax=docker/dockerfile:1
# Imagen única de la EVA: el backend (FastAPI) sirve la API y el frontend SPA.

# --- Frontend (SPA estática) ---
FROM node:22-slim AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

# --- Backend + frontend ---
FROM python:3.12-slim AS api
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# WeasyPrint (PDF): Pango, Cairo y fuentes.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libcairo2 \
        libgdk-pixbuf-2.0-0 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --no-dev --frozen

COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./
COPY --from=web /web/build ./static

RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

ENV EVA_STATIC_DIR=/app/static
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
