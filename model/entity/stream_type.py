from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.entity.base import Base

if TYPE_CHECKING:
    from model.entity.proposal import Proposal  # pragma: no cover
    from model.entity.radio_source import RadioSource  # pragma: no cover
    from model.entity.stream_analysis import StreamAnalysis  # pragma: no cover


class StreamType(Base):  # type: ignore[name-defined]
    __tablename__ = 'stream_types'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    protocol: Mapped[str] = mapped_column(String(10), nullable=False)  # HTTP, HTTPS, HLS
    format: Mapped[str] = mapped_column(String(10), nullable=False)    # MP3, AAC, OGG
    metadata_type: Mapped[str] = mapped_column(String(15), nullable=False)  # Icecast, Shoutcast, None
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)   # Human-readable name
    
    # Relationship with RadioSource
    radio_sources: Mapped[List["RadioSource"]] = relationship("RadioSource", back_populates="stream_type")
    # Relationship with StreamAnalysis (plural)
    stream_analyses: Mapped[List["StreamAnalysis"]] = relationship("StreamAnalysis", back_populates="stream_type")   
    # Relationship with Proposals
    proposals: Mapped[List["Proposal"]] = relationship("Proposal", back_populates="stream_type")   
    

    def __repr__(self):
        return f"<StreamType(id={self.id}, protocol='{self.protocol}', format='{self.format}', metadata_type='{self.metadata_type}')>"

    @property
    def type_key(self):
        """Returns the type key in format: PROTOCOL-FORMAT-METADATA"""
        return f"{self.protocol}-{self.format}-{self.metadata_type}"