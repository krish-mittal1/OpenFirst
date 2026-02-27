
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total_items: int
    total_pages: int


class CacheMeta(BaseModel):
    cached: bool = False
    cache_expires_at: str | None = None


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    status_code: int


class PaginatedResponse(BaseModel):
    data: list
    pagination: PaginationMeta
    meta: CacheMeta = CacheMeta()
