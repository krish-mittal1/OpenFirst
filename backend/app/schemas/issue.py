
from datetime import datetime

from pydantic import BaseModel, Field


class IssueOut(BaseModel):
    id: int
    github_id: str
    repo_id: int
    repo_full_name: str | None = None
    title: str
    body_preview: str | None = None
    html_url: str | None = None
    state: str = "open"
    labels: list[str] = []
    comment_count: int = 0
    difficulty_estimate: str | None = None
    is_assigned: bool = False
    is_good_first_issue: bool = False
    is_help_wanted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class IssueQueryParams(BaseModel):
    language: str | None = None
    difficulty: str | None = Field(
        default=None, pattern="^(easy|medium|hard)$"
    )
    is_assigned: bool | None = None
    search: str | None = None
    sort_by: str = Field(
        default="created_at",
        pattern="^(created_at|comment_count)$",
    )
    order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
