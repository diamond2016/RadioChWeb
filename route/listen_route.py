from flask import Blueprint, render_template, abort
from model.repository.radio_source_repository import RadioSourceRepository
from database import db, get_db_session
from service.stream_metadata_service import StreamMetadataService

listen_bp = Blueprint("listen", __name__, url_prefix="/listen")

metadata_service = StreamMetadataService()

@listen_bp.route("/<int:source_id>")
def player(source_id: int):
    repo = RadioSourceRepository(get_db_session())
    source = repo.find_by_id(source_id)
    if source is None:
        abort(404)
    metadata = None
    if getattr(metadata_service, "is_available", False):
        try:
            metadata = metadata_service.get_metadata(source.stream_url)
        except Exception:
            metadata = None
    return render_template("listen_player.html", source=source, metadata=metadata)