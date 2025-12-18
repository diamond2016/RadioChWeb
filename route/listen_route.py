from flask import Blueprint, render_template, abort
from model.repository.radio_source_repository import RadioSourceRepository
from database import db, get_db_session

listen_bp = Blueprint("listen", __name__, url_prefix="/listen")

@listen_bp.route("/<int:source_id>")
def player(source_id: int):
    repo = RadioSourceRepository(get_db_session())
    source = repo.find_by_id(source_id)
    if source is None:
        abort(404)
    # Ensure stream_url exists and is a string; further validation/sanitization can be added here
    return render_template("listen_player.html", source=source)