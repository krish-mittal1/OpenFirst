
from datetime import datetime

from sqlalchemy import Boolean, Float, Index, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    github_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    open_issues_count: Mapped[int] = mapped_column(Integer, default=0)
    watchers: Mapped[int] = mapped_column(Integer, default=0)
    license: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    last_pushed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    last_commit_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    activity_score: Mapped[float] = mapped_column(Float, default=0.0)
    beginner_friendliness_score: Mapped[float] = mapped_column(Float, default=0.0)
    combined_score: Mapped[float] = mapped_column(Float, default=0.0)

    good_first_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    contributor_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_pr_merge_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_issue_response_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    open_pr_count: Mapped[int] = mapped_column(Integer, default=0)
    closed_pr_count: Mapped[int] = mapped_column(Integer, default=0)
    merged_pr_count: Mapped[int] = mapped_column(Integer, default=0)

    has_contributing_guide: Mapped[bool] = mapped_column(Boolean, default=False)
    has_code_of_conduct: Mapped[bool] = mapped_column(Boolean, default=False)
    has_readme: Mapped[bool] = mapped_column(Boolean, default=True)
    has_issue_templates: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pr_templates: Mapped[bool] = mapped_column(Boolean, default=False)

    last_merged_pr_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    pr_merge_rate: Mapped[float] = mapped_column(Float, default=0.0)
    recent_commit_count_30d: Mapped[int] = mapped_column(Integer, default=0)
    recent_merged_pr_count_30d: Mapped[int] = mapped_column(Integer, default=0)
    is_actively_merging: Mapped[bool] = mapped_column(Boolean, default=False)

    topics: Mapped[dict] = mapped_column(JSONB, default=list)
    raw_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    synced_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_in_db: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )
    updated_in_db: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")
    languages = relationship("RepoLanguage", back_populates="repository", cascade="all, delete-orphan")
    metrics_history = relationship("RepoMetricsHistory", back_populates="repository", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_repos_combined_score", "combined_score", postgresql_using="btree"),
        Index("idx_repos_activity_score", "activity_score", postgresql_using="btree"),
        Index("idx_repos_bf_score", "beginner_friendliness_score", postgresql_using="btree"),
        Index("idx_repos_language", "primary_language"),
        Index("idx_repos_stars", "stars"),
        Index("idx_repos_synced", "synced_at"),
    )

    def __repr__(self) -> str:
        return f"<Repository {self.full_name} ⭐{self.stars}>"
