"""Utilidades de línea de comandos (bootstrap, etc.).

Uso:
    uv run python -m app.cli create-admin --email admin@ejemplo.com --password "Secreta123"
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.roles import Role
from app.core.security import hash_password
from app.db.session import get_session_factory
from app.models.usuario import Usuario


def create_admin(email: str, password: str, nombre: str) -> int:
    session = get_session_factory()()
    try:
        existing = session.scalar(select(Usuario).where(func.lower(Usuario.email) == email.lower()))
        if existing is not None:
            print(f"Ya existe un usuario con el correo {email}.")  # noqa: T201
            return 0
        user = Usuario(
            email=email.lower(),
            nombre=nombre,
            password_hash=hash_password(password),
            rol=Role.ADMIN,
            activo=True,
        )
        session.add(user)
        session.commit()
        print(f"Administrador creado: {email}")  # noqa: T201
        return 0
    finally:
        session.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.cli", description="Utilidades de la EVA")
    sub = parser.add_subparsers(dest="command", required=True)

    admin = sub.add_parser("create-admin", help="Crea un usuario administrador")
    settings = get_settings()
    admin.add_argument("--email", default=settings.admin_email)
    admin.add_argument("--password", default=settings.admin_password)
    admin.add_argument("--name", default=settings.admin_name)

    args = parser.parse_args(argv)
    if args.command == "create-admin":
        if not args.email or not args.password:
            parser.error("Se requieren --email y --password (o EVA_ADMIN_EMAIL / EVA_ADMIN_PASSWORD)")
        return create_admin(args.email, args.password, args.name)
    return 1


if __name__ == "__main__":
    sys.exit(main())
