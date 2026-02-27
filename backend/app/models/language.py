
from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RepoLanguage(Base):
    __tablename__ = "repo_languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    bytes_count: Mapped[int] = mapped_column(Integer, default=0)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)

    repository = relationship("Repository", back_populates="languages")

    __table_args__ = (
        UniqueConstraint("repo_id", "language", name="uq_repo_language"),
    )

    def __repr__(self) -> str:
        return f"<RepoLanguage {self.language} {self.percentage:.1f}%>"
