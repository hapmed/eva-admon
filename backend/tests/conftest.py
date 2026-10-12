"""Configuración de pruebas: base de datos SQLite en memoria."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registra los modelos)
from app.core.roles import Role
from app.core.security import hash_password
from app.db.base import Base
from app.deps import get_session
from app.main import app
from app.models.usuario import Usuario

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def db_session() -> Iterator[Session]:
    Base.metadata.create_all(engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    def override() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_session] = override
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    db_session.add(
        Usuario(
            email="admin@test.com",
            nombre="Admin",
            password_hash=hash_password("Secreta123"),
            rol=Role.ADMIN,
            activo=True,
        )
    )
    db_session.commit()
    response = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "Secreta123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
