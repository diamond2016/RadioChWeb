from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.entity.base import Base

if TYPE_CHECKING:
    from model.entity.stream_type import StreamType  # pragma: no cover
    from model.entity.user import User  # pragma: no cover


class Proposal(Base):  # type: ignore[name-defined]
    __tablename__ = 'proposals'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stream_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    website_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Classification data from analysis
    stream_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("stream_types.id"), nullable=False)
    is_secure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # User-editable fields
    country: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    stream_type: Mapped["StreamType"] = relationship("StreamType", back_populates="proposals")
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped[Optional["User"]] = relationship("User", back_populates="proposals")

    def __repr__(self) -> str:
        return f"<Proposal(id={self.id}, name='{self.name}', stream_url='{self.stream_url}', is_secure={self.is_secure})>"