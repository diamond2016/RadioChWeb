from database import db


class StreamAnalysis(db.Model):
    __tablename__ = "stream_analysis"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stream_url = db.Column(db.String(200), nullable=False)
    stream_type_id = db.Column(
        db.Integer, db.ForeignKey("stream_types.id"), nullable=True
    )  # Foreign key to StreamType, null if invalid
    is_valid = db.Column(db.Boolean, nullable=False, default=False)
    is_secure = db.Column(
        db.Boolean, nullable=False, default=False
    )  # False for HTTP, true for HTTPS
    error_code = db.Column(db.String(50), nullable=True)  # Null if valid
    detection_method = db.Column(
        db.String(50), nullable=True
    )  # How the stream was detected
    raw_content_type = db.Column(db.Text, nullable=True)  # String from curl headers
    raw_ffmpeg_output = db.Column(
        db.Text, nullable=True
    )  # String from ffmpeg detection
    extracted_metadata = db.Column(db.Text, nullable=True)

    # Relationship with StreamTypes
    stream_type = db.relationship("StreamType", back_populates="stream_analysis")

    def __repr__(self):
        return f"<StreamAnalysis(id={self.id}, url='{self.stream_url}', type='{self.stream_type_id}', valid={self.is_valid})>"
