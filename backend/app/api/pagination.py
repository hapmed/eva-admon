"""Paginación de listados."""

from math import ceil
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings


def paginate(
    db: Session, stmt: Select[Any], page: int, page_size: int
) -> dict[str, Any]:
    settings = get_settings()
    page = max(1, page)
    page_size = max(1, min(page_size, settings.page_size_max))
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    rows = list(db.scalars(stmt.limit(page_size).offset((page - 1) * page_size)))
    pages = ceil(total / page_size) if total else 0
    return {"items": rows, "total": total, "page": page, "page_size": page_size, "pages": pages}
