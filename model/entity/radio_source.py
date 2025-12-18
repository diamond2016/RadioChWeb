from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from model.entity.base import Base

if TYPE_CHECKING:
    from model.entity.stream_type import StreamType  # pragma: no cover
    from model.entity.user import User  # pragma: no cover


class RadioSource(Base):  # type: ignore[name-defined]
    __tablename__ = 'radio_sources'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stream_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Classification data
    stream_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("stream_types.id"), nullable=False)
    is_secure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # User-editable fields
    website_url: Mapped[str | None] = mapped_column(String(500))
    country: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    stream_type: Mapped["StreamType"] = relationship(
        "model.entity.stream_type.StreamType",
        back_populates="radio_sources",
        lazy="select",
    )
    user: Mapped["User"] = relationship(
        "model.entity.user.User",
        back_populates="radio_sources",
        lazy="select",
    )
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    def __repr__(self) -> str:
        return f"<RadioSource(id={self.id}, name='{self.name}', stream_url='{self.stream_url}', is_secure={self.is_secure})>"