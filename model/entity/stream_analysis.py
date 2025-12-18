from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from model.entity.base import Base

if TYPE_CHECKING:
    from model.entity.stream_type import StreamType  # pragma: no cover
    from model.entity.user import User  # pragma: no cover


class StreamAnalysis(Base):  # type: ignore[name-defined]
    __tablename__ = 'stream_analyses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stream_url: Mapped[str] = mapped_column(String(200), nullable=False)
    stream_type_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('stream_types.id'), nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_secure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    detection_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_content_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_ffmpeg_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship with StreamTypes
    stream_type: Mapped[Optional["StreamType"]] = relationship("StreamType", back_populates="stream_analyses")
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped[Optional["User"]] = relationship("User", back_populates="stream_analyses")

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<StreamAnalysis(id={self.id}, url='{self.stream_url}', type='{self.stream_type_id}', valid={self.is_valid})>"

