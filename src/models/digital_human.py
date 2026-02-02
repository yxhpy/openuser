"""Digital Human model for storing digital human configurations"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class DigitalHuman(Base, TimestampMixin):
    """Digital Human model for storing digital human information"""

    __tablename__ = "digital_humans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    voice_model_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="digital_humans")

    def __repr__(self) -> str:
        return f"<DigitalHuman(id={self.id}, name='{self.name}', user_id={self.user_id})>"
