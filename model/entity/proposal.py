from sqlalchemy import func
from database import db


class Proposal(db.Model):
    __tablename__ = "proposals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stream_url = db.Column(db.String(500), nullable=False, unique=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    website_url = db.Column(db.String(500))

    # Classification data from analysis
    stream_type_id = db.Column(
        db.Integer, db.ForeignKey("stream_types.id"), nullable=False
    )
    is_secure = db.Column(db.Boolean, nullable=False, default=False)

    # User-editable fields
    country = db.Column(db.String(50))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))

    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationship
    stream_type = db.relationship("StreamType", back_populates="proposals")

    def __repr__(self):
        return f"<Proposal(id={self.id}, name='{self.name}', stream_url='{self.stream_url}', is_secure={self.is_secure})>"
