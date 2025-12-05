"""
Radio source routes - Flask blueprint for managing radio sources.
Provides CRUD operations for radio sources.
"""

from typing import List
from flask import Blueprint, request, render_template, redirect, url_for, flash
from model.entity.stream_type import StreamType
from model.repository.stream_type_repository import StreamTypeRepository
from service.authorization import admin_required
from service.radio_source_service import RadioSourceService
from model.repository.radio_source_repository import RadioSourceRepository
from database import db

radio_source_bp = Blueprint("radio_source", __name__, url_prefix="/source")


# Repository and service initialization functions
def get_radio_source_repo() -> RadioSourceRepository:
    from database import db

    return RadioSourceRepository(db.session)


def get_radio_source_service() -> RadioSourceService:
    radio_source_repo = get_radio_source_repo()
    from service.radio_source_service import RadioSourceService

    return RadioSourceService(
        None, radio_source_repo, None
    )  # Validation service will be injected if needed


def get_stream_type_repo() -> StreamTypeRepository:
    from database import db

    return StreamTypeRepository(db.session)


@radio_source_bp.route("/<int:source_id>")
def source_detail(source_id):
    """Display radio source details."""
    radio_source_repo = get_radio_source_repo()
    source = radio_source_repo.find_by_id(source_id)
    if not source:
        flash("Radio source not found", "error")
        return redirect(url_for("main.index"))

    return render_template("source_detail.html", source=source)


# only admin users can edit or delete radio sources
@admin_required
@radio_source_bp.route("/edit/<int:source_id>", methods=["GET", "POST"])
def edit_source(source_id):
    """Edit radio source."""
    radio_source_repo: RadioSourceRepository = get_radio_source_repo()
    stream_type_repo: StreamTypeRepository = get_stream_type_repo()
    source = radio_source_repo.find_by_id(source_id)

    if not source:
        flash("Radio source not found", "error")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        source.name = request.form.get("name")
        source.stream_url = request.form.get("url")
        source.description = request.form.get("description", "")
        source.stream_type_id = int(request.form.get("stream_type_id"))

        try:
            radio_source_repo.save(source)
            flash("Radio source updated successfully!", "success")
            return redirect(url_for("radio_source.source_detail", source_id=source.id))

        except Exception as e:
            flash(f"Error updating source: {str(e)}", "error")

    # For GET request, show edit form
    stream_types: List[StreamType] = stream_type_repo.find_all()

    return render_template("edit_source.html", source=source, stream_types=stream_types)


@admin_required
@radio_source_bp.route("/delete/<int:source_id>", methods=["POST"])
def delete_source(source_id):
    """Delete radio source."""
    radio_source_service: RadioSourceService = get_radio_source_service()

    if radio_source_service.delete_radio_source(source_id):
        flash("Radio source deleted successfully!", "success")
    else:
        flash("Error deleting source", "error")

    return redirect(url_for("main.index"))
