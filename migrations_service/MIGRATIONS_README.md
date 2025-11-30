# Database Migrations

This directory contains database migration scripts managed by [PyWay](https://github.com/juancarlospaco/pyway), the Python equivalent of Flyway.

## Migration Files

Migration files follow the naming convention: `V{version}__{description}.sql`

### V1__initial_schema.sql
- Creates the initial database schema
- Tables: `stream_types`, `radio_source_nodes`, `proposals`
- Includes all necessary indexes and foreign key constraints

### V2__initialize_stream_types.sql
- Populates the `stream_types` table with 14 predefined classifications
- Required for spec 003 (analyze-and-classify-stream) functionality

## Usage

### Initialize Fresh Database
```bash
python init_db.py
```

### Run Migrations on Existing Database
```bash
python migrate.py
```

### Check Migration Status
```bash
python migrate.py status
```

## Migration Rules

1. **Version Numbers**: Use sequential integers (V1, V2, V3, etc.)
2. **Descriptions**: Use snake_case with underscores
3. **Idempotent**: Migrations should be safe to run multiple times
4. **Transactional**: Each migration file is executed as a single transaction
5. **Backward Compatible**: New migrations should not break existing functionality

## Adding New Migrations

1. Create a new SQL file: `V{next_version}__{description}.sql`
2. Test the migration on a copy of production data
3. Commit the migration file to version control
4. Update this README if needed

## Configuration

## NOTES
Migration settings are configured in `pyway.ini`:
- Database type: SQLite
- Database location: `./instance/radio_sources.db`
- Migration table: `pyway` (tracks applied migrations)

✅ Database Migration Refactoring Complete!
I've successfully refactored the database migration system to use PyWay (Python equivalent of Flyway). Here's what was accomplished:

🔄 What Was Refactored:
Replaced: create_db.py + migrate_db.py → PyWay migration system
Created: Proper version-controlled database migrations

📁 New Migration Structure:
migrations/
    ├── V1_0__initial_schema.sql          # Creates all base tables
    └── V2_0__initialize_stream_types.sql # Populates predefined classifications

🛠️ New Scripts:
- migrate.py - PyWay wrapper for running migrations
- init_db.py - Fresh database initialization
- pyway.yaml - PyWay configuration

📋 Migration Commands:
# Initialize fresh database
python init_db.py

# Run pending migrations
python migrate.py

# Check migration status  
python migrate.py status

# Validate migrations
python migrate.py validate

✅ Verified Working:
✅ Both migrations apply successfully
✅ All tables created: stream_types, radio_source_nodes, proposals, pyway
✅ 14 predefined stream types inserted
✅ Migration tracking table (pyway) maintains history
✅ Original database restored and functional

🎯 Benefits:
Version Control: Database schema changes are now tracked in git
Repeatable: Migrations can be safely re-run
Auditable: Migration history is maintained
Standard: Uses industry-standard Flyway/PyWay patterns
Future-Proof: Easy to add new migrations as the project grows