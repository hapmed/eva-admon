# PENDIENTES — EVA Admon

Documento vivo con el estado y lo que falta. Última revisión: 2026-10-12.

## Estado actual

| Elemento | Estado |
|----------|--------|
| Repositorio | `https://github.com/hapmed/eva-admon` (público) |
| Rama / tag | `main` + tag `v0.1.0` |
| Imagen | `ghcr.io/hapmed/eva-admon` — tags `0.1.0`, `sha-…`, `latest` (**pública**, pull anónimo OK) |
| EVA en EVAS Admin | `code: admon`, versión `0.1.0` **`approved`** |
| Instalación por cliente | **pendiente** (no hay clientes aún en EVAS Admin) |

## Pendientes

### 1. Rotar el PAT de GitHub (seguridad)
El token fine-grained quedó expuesto en un chat durante la configuración.
- GitHub → *Settings → Developer settings → Personal access tokens → Fine-grained tokens* → revocar el token usado y generar uno nuevo.
- Guardar el nuevo valor solo en el gestor de secretos / archivo local no versionado.

### 2. Crear la instalación del primer cliente
Cuando exista un cliente real, en EVAS Admin:
1. Registrar el **cliente** (nombre, RFC, contactos).
2. Crear la **suscripción** (plan: `EarlyMensual` / `EarlyTrimestral` / `EarlyAnual`).
3. Crear la **instalación**: cliente + EVA `admon` + versión `0.1.0` + **dominio** + **base de datos**.
4. Definir la **configuración** del cliente (valida contra `config_schema`): `locale`, `moneda`, `iva_porcentaje`, `cliente_prefijo`, `cotizacion_prefijo`.
5. Desplegar (el agente inyecta `EVAS_*`, `DATABASE_URL`, `PORT`, `DB_PASSWORD`).

### 3. Registrar nuevas versiones
Al publicar una nueva versión (ver "Publicar una versión"), registrarla en el catálogo
de EVAS Admin como `approved` para que sea desplegable.

## Cómo desplegar

### Imagen
La EVA es **una sola imagen**: el backend (FastAPI) sirve la API y el frontend SPA en
el puerto `PORT` (por defecto `8000`). `GET /healthz` responde `200` cuando está lista.

### Variables de entorno
| Variable | Origen | Uso |
|----------|--------|-----|
| `DATABASE_URL` | EVAS Admin | PostgreSQL del cliente (una BD por cliente). |
| `PORT` | EVAS Admin | Puerto HTTP. |
| `EVAS_VERSION`, `EVAS_EVA_CODE`, `EVAS_INSTALLATION_ID`, `EVAS_CLIENT_REF` | EVAS Admin | Metadatos de la instalación. |
| `DB_PASSWORD` | Secreto (env) | Secreto de la BD. |
| `EVA_JWT_SECRET` | Secreto (env) | **Obligatorio**: secreto de firma de los JWT. |
| `EVA_LOGO_DIR` | Opcional | Carpeta de logos subidos (por defecto `/data/branding`). |
| `EVA_ADMIN_EMAIL` / `EVA_ADMIN_PASSWORD` | Opcional | Bootstrap del primer administrador. |

### Migraciones
Idempotentes, comando declarado en `eva.yaml`:
```bash
alembic upgrade head
```

### Compose de producción (referencia)
```bash
# Con la imagen publicada:
docker compose -f ops/compose.yaml up -d        # ajustar imagen/tags si aplica
```
En EVAS Admin la plataforma gestiona el despliegue (proxy/túnel, dominio y TLS), por
lo que el contenedor **no** publica puertos al host.

## Publicar una versión

```bash
git tag -a vX.Y.Z -m "EVA Admon X.Y.Z"
git push origin vX.Y.Z
```
Esto dispara `publish.yml` y publica `ghcr.io/hapmed/eva-admon:X.Y.Z` (+ `sha-…`).
Después, registrarla como `approved` en EVAS Admin.
