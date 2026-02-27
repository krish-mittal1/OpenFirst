
from datetime import datetime

from pydantic import BaseModel, Field


class RepoScores(BaseModel):
    activity: float
    beginner_friendliness: float
    combined: float
    trend: str | None = None


class RepoMetrics(BaseModel):
    last_commit_at: datetime | None = None
    last_pushed_at: datetime | None = None
    avg_pr_merge_hours: float | None = None
    avg_issue_response_hours: float | None = None
    contributor_count: int = 0
    open_pr_count: int = 0
    closed_pr_count: int = 0
    merged_pr_count: int = 0
    open_closed_pr_ratio: float | None = None
    good_first_issue_count: int = 0


class RepoLanguageOut(BaseModel):
    language: str
    percentage: float


class IssueBrief(BaseModel):
    id: int
    title: str
    difficulty_estimate: str | None = None
    comment_count: int = 0
    is_assigned: bool = False
    created_at: datetime | None = None
    labels: list[str] = []
    html_url: str | None = None


class RepositoryListItem(BaseModel):
    id: int
    full_name: str
    description: str | None = None
    primary_language: str | None = None
    stars: int = 0
    forks: int = 0
    license: str | None = None
    topics: list[str] = []
    scores: RepoScores
    metrics: RepoMetrics
    synced_at: datetime | None = None

    class Config:
        from_attributes = True


class RepositoryDetail(BaseModel):
    id: int
    full_name: str
    owner: str
    name: str
    description: str | None = None
    primary_language: str | None = None
    stars: int = 0
    forks: int = 0
    open_issues_count: int = 0
    watchers: int = 0
    license: str | None = None
    topics: list[str] = []
    created_at: datetime | None = None
    scores: RepoScores
    metrics: RepoMetrics
    languages: list[RepoLanguageOut] = []
    recent_good_first_issues: list[IssueBrief] = []
    has_contributing_guide: bool = False
    has_code_of_conduct: bool = False
    has_readme: bool = True
    has_issue_templates: bool = False
    has_pr_templates: bool = False
    synced_at: datetime | None = None

    class Config:
        from_attributes = True


class RepositoryQueryParams(BaseModel):
    language: str | None = None
    min_stars: int | None = Field(default=None, ge=0)
    max_stars: int | None = Field(default=None, ge=0)
    min_activity_score: float | None = Field(default=None, ge=0, le=100)
    min_bf_score: float | None = Field(default=None, ge=0, le=100)
    sort_by: str = Field(
        default="combined_score",
        pattern="^(combined_score|activity_score|beginner_friendliness_score|stars|last_commit_at)$",
    )
    order: str = Field(default="desc", pattern="^(asc|desc)$")
    search: str | None = None
    topics: str | None = None
    has_issues: bool | None = None
    actively_merging: bool | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def topic_list(self) -> list[str]:
        if not self.topics:
            return []
        return [t.strip().lower() for t in self.topics.split(",") if t.strip()]
