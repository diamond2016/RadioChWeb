"""
Database configuration and session dependencies for API.
Proxies to the unified database configuration in the project root.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path so we can import from root
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import the unified database configuration and type
from database import get_db_session, db, StandaloneSession
from sqlalchemy.orm import Session as SessionType

# Ensure all models are registered in the SQLAlchemy metadata for relationships
import model.entity

# Export get_db_session for use in API services
# It will now correctly fall back to StandaloneSession when outside Flask context




