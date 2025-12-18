
from flask import Blueprint, render_template

from model.repository.radio_source_repository import RadioSourceRepository
from database import db, get_db_session

main_bp = Blueprint('main', __name__, url_prefix='/')

# Repository initialization functions
def get_radio_source_repo() -> RadioSourceRepository:
    return RadioSourceRepository(get_db_session())


@main_bp.route('/')
def index():
    """Main index page - list all radio sources."""
    radio_source_repo: RadioSourceRepository = get_radio_source_repo()
    sources = radio_source_repo.find_all()
    # Get a server-side formatted current day string from radio_source helper
    try:
        from route.radio_source_route import get_current_day_str
        current_day = get_current_day_str()
    except Exception:
        current_day = None

    return render_template('index.html', sources=sources, current_day=current_day)