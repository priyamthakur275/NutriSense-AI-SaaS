"""Generic repository providing CRUD + pagination/search/filter/sort for any
SQLAlchemy model. Resource-specific repositories subclass this and only add
methods for genuinely resource-specific queries (e.g. "find by enrollment
number") — the common 90% is written exactly once, here.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.schemas.common import PaginationParams, SortDirection, SortParams

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """`model` must be a SQLAlchemy declarative class. If it has a
    `deleted_at` column (soft-delete support, per the SoftDeleteMixin),
    every read method here automatically excludes soft-deleted rows unless
    `include_deleted=True` is passed — callers never need to remember to
    filter it themselves.
    """

    model: type[ModelType]

    def __init__(self, db: Session) -> None:
        self.db = db

    @property
    def _supports_soft_delete(self) -> bool:
        return hasattr(self.model, "deleted_at")

    def _base_query(self, *, include_deleted: bool = False) -> Select:
        stmt = select(self.model)
        if self._supports_soft_delete and not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))
        return stmt

    def get(self, id_: Any, *, include_deleted: bool = False) -> ModelType | None:
        stmt = self._base_query(include_deleted=include_deleted).where(self.model.id == id_)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_or_404(self, id_: Any) -> ModelType:
        obj = self.get(id_)
        if obj is None:
            from app.core.exceptions import NotFoundError

            raise NotFoundError(f"{self.model.__name__} with id '{id_}' not found")
        return obj

    def get_deleted_or_404(self, id_: Any) -> ModelType:
        """Like `get_or_404`, but specifically for restoring a soft-deleted
        row — looks it up *including* deleted rows, then confirms it's
        actually in the deleted state (so restoring an active row, or an
        id that never existed at all, both fail clearly rather than
        silently succeeding as a no-op)."""
        from app.core.exceptions import NotFoundError, ValidationAppError

        obj = self.get(id_, include_deleted=True)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} with id '{id_}' not found")
        if not self._supports_soft_delete:
            raise ValidationAppError(f"{self.model.__name__} does not support soft delete/restore")
        if getattr(obj, "deleted_at", None) is None:
            raise ValidationAppError(f"{self.model.__name__} with id '{id_}' is not deleted")
        return obj

    def create(self, obj_in: dict[str, Any]) -> ModelType:
        obj = self.model(**obj_in)
        self.db.add(obj)
        self.db.flush()
        return obj

    def update(self, obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(obj, field, value)
        self.db.flush()
        return obj

    def delete(self, obj: ModelType, *, hard: bool = False) -> None:
        """Soft-deletes by default (if the model supports it); pass
        `hard=True` to actually remove the row (audit-relevant tables like
        AuditLog don't support soft delete at all, so hard delete is the
        only option there — and is intentionally never exposed via API)."""
        if self._supports_soft_delete and not hard:
            obj.soft_delete()
            self.db.flush()
        else:
            self.db.delete(obj)
            self.db.flush()

    def restore(self, obj: ModelType) -> ModelType:
        """Reverses a soft-delete. Callers should fetch `obj` via
        `get_deleted_or_404` (not `get_or_404`, which excludes deleted
        rows and would 404 before this method is ever reached)."""
        obj.restore()
        self.db.flush()
        return obj

    def list(
        self,
        *,
        pagination: PaginationParams,
        sort: SortParams | None = None,
        allowed_sort_fields: set[str] | None = None,
        default_sort_field: str = "created_at",
        search: str | None = None,
        search_fields: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[ModelType], int]:
        """Returns (items, total_count) for the given page. `filters` is an
        exact-match dict of {column_name: value}; `search` does a
        case-insensitive substring match OR'd across `search_fields`.
        """
        stmt = self._base_query(include_deleted=include_deleted)

        if filters:
            for field, value in filters.items():
                if value is not None:
                    stmt = stmt.where(getattr(self.model, field) == value)

        if search and search_fields:
            like_pattern = f"%{search}%"
            conditions = [
                getattr(self.model, field).ilike(like_pattern) for field in search_fields
            ]
            stmt = stmt.where(or_(*conditions))

        # Count before pagination is applied.
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        sort_field = default_sort_field
        sort_dir = SortDirection.DESC
        if sort and sort.sort_by:
            if allowed_sort_fields is None or sort.sort_by in allowed_sort_fields:
                sort_field = sort.sort_by
                sort_dir = sort.sort_dir

        column = getattr(self.model, sort_field, None)
        if column is not None:
            stmt = stmt.order_by(column.desc() if sort_dir == SortDirection.DESC else column.asc())

        stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total
