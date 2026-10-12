"""Reglas de negocio de clientes."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente, ContactoCliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ContactoCreate
from app.services.folios import next_cliente_numero


def list_clientes(db: Session, search: str | None = None, include_inactive: bool = False) -> list[Cliente]:
    stmt = select(Cliente)
    if not include_inactive:
        stmt = stmt.where(Cliente.activo.is_(True))
    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(
            func.lower(Cliente.nombre).like(like)
            | func.lower(Cliente.numero_cliente).like(like)
            | func.lower(Cliente.rfc).like(like)
        )
    return list(db.scalars(stmt.order_by(Cliente.numero_cliente)))


def create_cliente(db: Session, data: ClienteCreate) -> Cliente:
    cliente = Cliente(
        numero_cliente=next_cliente_numero(db),
        nombre=data.nombre,
        rfc=data.rfc,
        condiciones_pago=data.condiciones_pago,
        activo=data.activo,
    )
    _set_contactos(cliente, data.contactos)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def update_cliente(db: Session, cliente: Cliente, data: ClienteUpdate) -> Cliente:
    payload = data.model_dump(exclude_unset=True)
    contactos = payload.pop("contactos", None)
    for field, value in payload.items():
        setattr(cliente, field, value)
    if contactos is not None:
        _set_contactos(cliente, [ContactoCreate(**c) for c in contactos])
    db.commit()
    db.refresh(cliente)
    return cliente


def _set_contactos(cliente: Cliente, contactos: list[ContactoCreate]) -> None:
    cliente.contactos = [
        ContactoCliente(nombre=c.nombre, email=c.email) for c in contactos
    ]
