
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    github_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    repo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    html_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    state: Mapped[str] = mapped_column(String(10), default="open")
    labels: Mapped[dict] = mapped_column(JSONB, default=list)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    difficulty_estimate: Mapped[str | None] = mapped_column(String(20), nullable=True)
    assignee_login: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_assigned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_good_first_issue: Mapped[bool] = mapped_column(Boolean, default=False)
    is_help_wanted: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    synced_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    repository = relationship("Repository", back_populates="issues")

    __table_args__ = (
        Index("idx_issues_repo", "repo_id"),
        Index("idx_issues_gfi", "is_good_first_issue", postgresql_where="is_good_first_issue = true"),
        Index("idx_issues_open", "state", postgresql_where="state = 'open'"),
        Index("idx_issues_difficulty", "difficulty_estimate"),
    )

    def __repr__(self) -> str:
        return f"<Issue #{self.github_id} '{self.title[:40]}...'>"
