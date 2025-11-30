#!/usr/bin/env python3
"""
Database Migration Runner using PyWay
Replaces the old create_db.py and migrate_db.py scripts with proper migration management.
"""

import subprocess
import sys
from pathlib import Path

PYWAY_PATH = Path(__file__).parent.parent / ".venv" / "bin" / "pyway"

def run_command(cmd: list) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode != 0:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Failed to run command: {e}")
        return False


def run_migrations():
    """Run all pending database migrations using sqlite3."""
    print("🚀 Starting database migrations with sqlite3...")

    # Ensure instance directory exists
    instance_dir = Path("../instance")
    instance_dir.mkdir(exist_ok=True)

    # Run migrations
    import sqlite3
    db_path = Path("../instance/radio_sources.db")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get list of migration files
    migration_dir = Path("migrations")
    migration_files = sorted([f for f in migration_dir.iterdir() if f.is_file() and f.name.endswith('.sql')])

    for migration_file in migration_files:
        print(f"Applying migration: {migration_file.name}")
        with open(migration_file, 'r') as f:
            sql = f.read()
        cursor.executescript(sql)

    conn.commit()
    conn.close()

    print("✅ All migrations completed successfully!")


def show_migration_status():
    """Show current migration status."""
    print("\n📊 Migration Status:")

    cmd = [
        PYWAY_PATH.as_posix(),
        "--config", "pyway.yaml",
        "info"
    ]

    run_command(cmd)


def validate_migrations():
    """Validate migration checksums."""
    print("🔍 Validating migrations...")

    cmd = [
        PYWAY_PATH.as_posix(),
        "--config", "pyway.yaml",
        "validate"
    ]

    if run_command(cmd):
        print("✅ All migrations are valid!")
    else:
        print("❌ Migration validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            show_migration_status()
        elif sys.argv[1] == "validate":
            validate_migrations()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python migrate.py [status|validate]")
            sys.exit(1)
    else:
        run_migrations()