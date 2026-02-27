
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    labels: Mapped[list] = mapped_column(JSONB, default=list)

    notify_on_new_match: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_inactive: Mapped[bool] = mapped_column(Boolean, default=True)
    only_actively_merging: Mapped[bool] = mapped_column(Boolean, default=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )

    notifications = relationship("Notification", back_populates="subscription", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Subscription {self.email}: {self.language}/{self.labels}>"
