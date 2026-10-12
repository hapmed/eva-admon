# Admon — EVA de HAPMED (sistema administrativo)

Aplicación de negocio de HAPMED (`code: admon`) administrable y desplegable por
**EVAS Admin**. Primer módulo funcional: **cotizaciones de servicios y
materiales**, con clientes, usuarios/roles y configuración de la empresa.

> Contrato obligatorio: `docs/EVAS_APPS/` del repositorio de referencia
> <https://github.com/hapmed/eva_Admin> — `REQUISITOS_EVA.md`, `DISENO_EVA.md`,
> `MANIFEST_EJEMPLO.yaml`.

## Módulos

| Módulo | Descripción | Roles |
|--------|-------------|-------|
| Dashboard | Indicadores (clientes, usuarios, cotizaciones, total cotizado). | Todos |
| Clientes | Altas, bajas (desactivación) y cambios; identificados por **RFC** (único); contactos (nombre y correo). | admin, ventas |
| Servicios | Catálogo de servicios (código, unidad, precio). | admin, ventas |
| Materiales | Catálogo de materiales. | admin, ventas |
| Cotizaciones | Cotizaciones de servicio y materiales con partidas, descuento por partida, IVA configurable, **PDF profesional** (logo y colores de marca) y **envío por correo (SMTP)**. | admin, ventas |
| Usuarios | Usuarios y roles (`admin`, `ventas`, `consulta`). | admin |
| Configuración | Razón social, nombre comercial, logo, RFC, teléfono, correo, WhatsApp, IVA, moneda, **SMTP por cliente** y **colores de marca** del PDF. | admin |

Los listados incluyen **paginación** (servidor) y **filtros** (búsqueda, estado, rol, fechas).

Roles: `admin` (todo), `ventas` (catálogos y cotizaciones), `consulta` (solo lectura).

## Estructura

```
admon/
├─ eva.yaml              # manifiesto (contrato con EVAS Admin)
├─ Dockerfile            # imagen única (frontend SPA + backend)
├─ .env.example          # variables de entorno (ficticias)
├─ backend/              # FastAPI + SQLAlchemy + Alembic
│  └─ app/{api,models,schemas,services,core,db}
├─ frontend/             # SvelteKit + TypeScript + Tailwind v4 (adapter-static, SPA)
│  └─ src/{app.css, lib/{components,auth.ts,nav.ts,api}, routes}
├─ ops/compose.yaml      # desarrollo (sin PostgreSQL productivo)
└─ .github/workflows/    # CI + publicación en GHCR
```

## Puesta en marcha (local)

```bash
# 1) Configuración
cp .env.example .env

# 2) Backend → http://localhost:8000/docs
cd backend
uv sync
uv run alembic upgrade head
uv run python -m app.cli create-admin --email admin@ejemplo.com --password "CambiarEsta123"
uv run uvicorn app.main:app --reload

# 3) Frontend → http://localhost:5173 (proxy /api → backend)
cd frontend
npm install
npm run dev
```

Sin PostgreSQL local puedes usar un `.env` con
`DATABASE_URL=postgresql+psycopg://...`. La UI redirige a `/login`; entra con el
usuario administrador creado en el paso 2.

## Calidad

```bash
# Backend
cd backend && uv run ruff check . && uv run mypy app && uv run pytest

# Frontend
cd frontend && npm run check && npm run lint && npm run test && npm run build
```

## Despliegue

La EVA se empaqueta como **una sola imagen** (contrato de contenedor): el
`Dockerfile` de la raíz compila el frontend (SPA) y el backend lo sirve junto con
la API en el mismo puerto.

- Publica la imagen en GHCR (`.github/workflows/publish.yml`):
  `ghcr.io/<owner>/<repo>` (p. ej. `ghcr.io/hapmed/eva-admon`).
- Registra la EVA (`code: admon`) en EVAS Admin con las versiones `approved`.
- La plataforma inyecta `EVAS_VERSION`, `EVAS_EVA_CODE`, `EVAS_INSTALLATION_ID`,
  `EVAS_CLIENT_REF`, `DATABASE_URL`, `PORT` y `DB_PASSWORD`.
- Migraciones: `alembic upgrade head` (idempotente).
- Cada despliegue se confirma con `GET /healthz` (debe responder `200`).

### Variables de entorno

| Variable | Uso |
|----------|-----|
| `DATABASE_URL` | Conexión a la PostgreSQL del cliente (la inyecta EVAS Admin). |
| `PORT` | Puerto HTTP (por defecto `8000`). |
| `EVAS_VERSION`, `EVAS_EVA_CODE`, `EVAS_INSTALLATION_ID`, `EVAS_CLIENT_REF` | Metadatos de la instalación. |
| `EVA_JWT_SECRET` | Secreto de firma de los JWT (obligatorio en producción). |
| `EVA_ADMIN_EMAIL`, `EVA_ADMIN_PASSWORD` | Bootstrap opcional del primer administrador. |
| `EVA_IVA_PORCENTAJE`, `EVA_MONEDA` | Valores por defecto (editables en Configuración). |
| `EVA_FOLIO_RANDOM_CHARS` | Caracteres aleatorios del folio (base36). Por defecto `2`. |
| `EVA_LOGO_DIR` | Carpeta donde se guardan los logos subidos. |

> Los secretos se inyectan como variables de entorno. Nunca se versionan ni se
> registran en logs.

## Branding por cliente

Reemplaza los activos en `frontend/static/brand/` y ajusta los tokens de color en
`frontend/src/app.css`. El `code`/`image` de `eva.yaml` se mantienen estables.
