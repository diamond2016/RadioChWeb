#!/usr/bin/env python3
"""
Database Initialization Script
Creates the instance directory and runs initial migrations for a fresh database.
"""

import os
import sys
from pathlib import Path
DBPATH = Path(__file__).parent.parent / ".instance" / "radio_sources.db"

def init_database():
    """Initialize a fresh database with all migrations."""
    print("🗄️  Initializing RadioChWeb database...")

    # Create instance directory if it doesn't exist
    instance_dir = Path("./instance")
    instance_dir.mkdir(exist_ok=True)

    # Remove existing database if it exists (for clean init)
    db_path = DBPATH
    if db_path.exists():
        print("🗑️  Removing existing database for clean initialization...")
        db_path.unlink()

    print("🚀 Running database migrations...")
    # Import and run the migration script
    from migrate import run_migrations
    run_migrations()

    print("✅ Database initialization completed!")
    print(f"📍 Database location: {db_path.absolute()}")


if __name__ == "__main__":
    init_database()
