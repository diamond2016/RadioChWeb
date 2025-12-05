"""
Database routes - Flask blueprint for database operations and main listings.
Provides the main index and source listings.
"""

from flask import Blueprint, request, jsonify, render_template
from model.repository.radio_source_repository import RadioSourceRepository
from model.repository.stream_type_repository import StreamTypeRepository
from model.repository.proposal_repository import ProposalRepository
from database import db

database_bp = Blueprint("database", __name__, url_prefix="/database")


# Repository initialization functions
def get_radio_source_repo():
    from database import db

    return RadioSourceRepository(db.session)


def get_stream_type_repo():
    from database import db

    return StreamTypeRepository(db.session)


def get_proposal_repo():
    from database import db

    return ProposalRepository(db.session)


@database_bp.route("/sources")
def list_sources():
    """List all radio sources with filtering options."""
    radio_source_repo = get_radio_source_repo()
    stream_type_repo = get_stream_type_repo()

    stream_type_filter = request.args.get("stream_type")
    search_query = request.args.get("search")

    if stream_type_filter:
        sources = radio_source_repo.find_by_stream_type(int(stream_type_filter))
    elif search_query:
        sources = radio_source_repo.search_by_name(search_query)
    else:
        sources = radio_source_repo.find_all()

    stream_types = stream_type_repo.find_all()

    return render_template(
        "sources.html",
        sources=sources,
        stream_types=stream_types,
        current_filter=stream_type_filter,
        search_query=search_query,
    )


@database_bp.route("/proposals")
def list_proposals():
    """List all pending proposals."""
    proposal_repo = get_proposal_repo()
    proposals = proposal_repo.find_all()
    return render_template("proposals.html", proposals=proposals)


@database_bp.route("/database")
def index():
    """Database management page with overview of all entities."""
    radio_source_repo = get_radio_source_repo()
    stream_type_repo = get_stream_type_repo()
    proposal_repo = get_proposal_repo()

    stream_types = stream_type_repo.find_all()
    proposals = proposal_repo.find_all()
    radio_sources = radio_source_repo.find_all()

    return render_template(
        "database.html",
        stream_types=stream_types,
        proposals=proposals,
        radio_sources=radio_sources,
    )


@database_bp.route("/api/stats")
def get_stats():
    """API endpoint to get database statistics."""
    radio_source_repo = get_radio_source_repo()
    proposal_repo = get_proposal_repo()
    stream_type_repo = get_stream_type_repo()

    source_count = radio_source_repo.count()
    proposal_count = proposal_repo.count()
    stream_type_count = stream_type_repo.count()

    return jsonify(
        {
            "total_sources": source_count,
            "total_proposals": proposal_count,
            "total_stream_types": stream_type_count,
        }
    )
