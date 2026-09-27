"""Shared request/response schemas used by every resource's list endpoint:
pagination parameters, sort direction, and a generic paginated envelope.
"""

from enum import Enum
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PaginationParams:
    """FastAPI dependency: parses `?page=&page_size=` into offset/limit.

    Used as `params: PaginationParams = Depends()` — every list endpoint
    shares this exact contract rather than each re-declaring page/page_size
    query parameters by hand.
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="1-indexed page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta

    @classmethod
    def build(cls, items: list[T], *, total_items: int, params: PaginationParams) -> "PaginatedResponse[T]":
        total_pages = max(1, (total_items + params.page_size - 1) // params.page_size)
        return cls(
            items=items,
            meta=PageMeta(
                page=params.page,
                page_size=params.page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=params.page < total_pages,
                has_previous=params.page > 1,
            ),
        )


class SortParams:
    """FastAPI dependency: `?sort_by=created_at&sort_dir=desc`.

    `allowed_fields` is enforced per-endpoint (passed by the caller, not
    hardcoded here) so each resource controls what it's safe/indexed to
    sort by — sorting on an unindexed column is a footgun waiting to
    happen at scale, so callers opt in explicitly.
    """

    def __init__(
        self,
        sort_by: str | None = Query(None, description="Field name to sort by"),
        sort_dir: SortDirection = Query(SortDirection.DESC, description="Sort direction"),
    ) -> None:
        self.sort_by = sort_by
        self.sort_dir = sort_dir
