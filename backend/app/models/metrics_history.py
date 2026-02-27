
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RepoMetricsHistory(Base):
    __tablename__ = "repo_metrics_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    activity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    beginner_friendliness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    stars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    forks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    good_first_issue_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_pr_merge_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_date: Mapped[date] = mapped_column(Date, default=date.today)

    repository = relationship("Repository", back_populates="metrics_history")

    __table_args__ = (
        UniqueConstraint("repo_id", "recorded_date", name="uq_repo_metrics_date"),
    )

    def __repr__(self) -> str:
        return f"<MetricsHistory repo={self.repo_id} date={self.recorded_date}>"
