from typing import TYPE_CHECKING, Type
from database import db

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model as _Model
    BaseModel: Type[_Model] = _Model
else:
    BaseModel = db.Model  # type: ignore[assignment]


class StreamType(db.Model):  # type: ignore[name-defined]
    __tablename__ = 'stream_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    protocol = db.Column(db.String(10), nullable=False)  # HTTP, HTTPS, HLS
    format = db.Column(db.String(10), nullable=False)    # MP3, AAC, OGG
    metadata_type = db.Column(db.String(15), nullable=False)  # Icecast, Shoutcast, None
    display_name = db.Column(db.String(100), nullable=False)   # Human-readable name

    # Relationship with RadioSource
    radio_sources = db.relationship("RadioSource", back_populates="stream_type")
     # Relationship with StreamAnalysis (plural)
    stream_analyses = db.relationship("StreamAnalysis", back_populates="stream_type")   
    # Relationship with Proposals
    proposals = db.relationship("Proposal", back_populates="stream_type")   
    
    def __repr__(self):
        return f"<StreamType(id={self.id}, protocol='{self.protocol}', format='{self.format}', metadata_type='{self.metadata_type}')>"

    @property
    def type_key(self):
        """Returns the type key in format: PROTOCOL-FORMAT-METADATA"""
        return f"{self.protocol}-{self.format}-{self.metadata_type}"