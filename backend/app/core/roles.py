"""Roles de usuario de la EVA."""

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    VENTAS = "ventas"
    CONSULTA = "consulta"


ALL_ROLES: tuple[str, ...] = (Role.ADMIN, Role.VENTAS, Role.CONSULTA)
