"""
Test configuration and fixtures for RadioChWeb tests.
"""

import pytest
import sys
from pathlib import Path
from flask import Flask
from unittest.mock import Mock

# Add current directory to Python path for tests
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import db
from model.entity.stream_type import StreamType

@pytest.fixture(scope="session")
def test_app():
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Required for session/flash in tests
    app.secret_key = 'test-secret'
    # Disable CSRF in tests for simplicity (we assert behavior, not CSRF infra)
    app.config['WTF_CSRF_ENABLED'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        # Initialize stream types
        _initialize_stream_types()
        # ensure LoginManager is configured early
        from service.auth_service import AuthService
        AuthService(app)
        yield app


@pytest.fixture
def test_db(test_app):
    """Create a test database session."""
    with test_app.app_context():
        db.session.begin_nested()  # Start a nested transaction
        yield db.session
        db.session.rollback()  # Rollback changes after test


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for testing external commands."""
    mock = Mock()
    mock.return_value.returncode = 0
    mock.return_value.stdout = ""
    mock.return_value.stderr = ""
    return mock


@pytest.fixture
def sample_urls():
    """Sample URLs for testing."""
    return {
        "valid_https_mp3": "https://stream.example.com/radio.mp3",
        "valid_http_aac": "http://stream.example.com:8000/stream.aac",
        "invalid_html": "https://example.com/index.html",
        "rtmp_unsupported": "rtmp://stream.example.com/live",
        "hls_playlist": "https://stream.example.com/playlist.m3u8"
    }


def _initialize_stream_types():
    """Initialize stream types in test database."""
    # Ensure related entity classes are imported so SQLAlchemy can configure relationships

    stream_types_data = [
        {"protocol": "HTTP", "format": "MP3", "metadata_type": "Icecast", "display_name": "HTTP MP3 Icecast"},
        {"protocol": "HTTP", "format": "MP3", "metadata_type": "Shoutcast", "display_name": "HTTP MP3 Shoutcast"},
        {"protocol": "HTTP", "format": "AAC", "metadata_type": "Icecast", "display_name": "HTTP AAC Icecast"},
        {"protocol": "HTTP", "format": "AAC", "metadata_type": "Shoutcast", "display_name": "HTTP AAC Shoutcast"},
        {"protocol": "HTTPS", "format": "MP3", "metadata_type": "Icecast", "display_name": "HTTPS MP3 Icecast"},
        {"protocol": "HTTPS", "format": "MP3", "metadata_type": "Shoutcast", "display_name": "HTTPS MP3 Shoutcast"},
        {"protocol": "HTTPS", "format": "AAC", "metadata_type": "Icecast", "display_name": "HTTPS AAC Icecast"},
        {"protocol": "HTTPS", "format": "AAC", "metadata_type": "Shoutcast", "display_name": "HTTPS AAC Shoutcast"},
        {"protocol": "HLS", "format": "AAC", "metadata_type": "None", "display_name": "HLS AAC"},
        {"protocol": "HLS", "format": "MP3", "metadata_type": "None", "display_name": "HLS MP3"},
        {"protocol": "HTTP", "format": "OGG", "metadata_type": "Icecast", "display_name": "HTTP OGG Icecast"},
        {"protocol": "HTTPS", "format": "OGG", "metadata_type": "Icecast", "display_name": "HTTPS OGG Icecast"},
        {"protocol": "HTTP", "format": "FLAC", "metadata_type": "None", "display_name": "HTTP FLAC"},
        {"protocol": "HTTPS", "format": "FLAC", "metadata_type": "None", "display_name": "HTTPS FLAC"},
    ]

    for st_data in stream_types_data:
        stream_type = StreamType(**st_data)
        db.session.add(stream_type)

    db.session.commit()