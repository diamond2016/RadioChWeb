from typing import TYPE_CHECKING, List

from flask_login import UserMixin
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.entity.base import Base

if TYPE_CHECKING:
    from model.entity.proposal import Proposal  # pragma: no cover
    from model.entity.stream_analysis import StreamAnalysis  # pragma: no cover
    from model.entity.radio_source import RadioSource  # pragma: no cover


class User(UserMixin, Base):  # type: ignore[name-defined]
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hash_password: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default='user')

    # Timestamps: keep `created_at` and `updated_at`
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    proposals: Mapped[List["Proposal"]] = relationship("Proposal", back_populates="user")
    stream_analyses: Mapped[List["StreamAnalysis"]] = relationship("StreamAnalysis", back_populates="user")
    radio_sources: Mapped[List["RadioSource"]] = relationship("RadioSource", back_populates="user")

    def get_id(self) -> str:
        return str(self.id)

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    @property
    def is_active(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
