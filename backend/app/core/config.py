"""Configuración centralizada (variables de entorno).

Prefijo `EVA_` para lo propio de la app y alias para las variables que inyecta
la plataforma EVAS Admin (`DATABASE_URL`, `EVAS_*`). Sin secretos por defecto.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EVA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "HAPMED Admon"
    environment: str = "local"
    debug: bool = False

    # Inyectadas por la plataforma EVAS Admin.
    version: str = Field(default="dev", alias="EVAS_VERSION")
    eva_code: str = Field(default="admon", alias="EVAS_EVA_CODE")
    installation_id: str = Field(default="", alias="EVAS_INSTALLATION_ID")
    client_ref: str = Field(default="", alias="EVAS_CLIENT_REF")
    database_url: str = Field(
        default="postgresql+psycopg://eva:eva@localhost:5432/admon",
        alias="DATABASE_URL",
    )

    # Autenticación (JWT). El secreto se inyecta como variable de entorno.
    jwt_secret: str = "dev-insecure-change-me-use-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 480

    # Bootstrap del primer usuario admin (opcional).
    admin_email: str = ""
    admin_password: str = ""
    admin_name: str = "Administrador"

    # Folios y consecutivos.
    cliente_prefijo: str = "CLI-"
    cotizacion_prefijo: str = "COT-"
    consecutivo_digitos: int = 4

    # Reglas de negocio por defecto.
    iva_porcentaje: float = 16.0
    moneda: str = "MXN"
    logo_dir: str = "/data/branding"

    # Carpeta del frontend compilado (SPA). Vacío = no se sirve (desarrollo).
    static_dir: str = ""

    @property
    def is_local(self) -> bool:
        return self.environment in {"local", "test"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
