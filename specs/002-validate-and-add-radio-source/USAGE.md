# Usage Guide: Spec 002 - Validate and Add Radio Source

This guide explains how to use the Validate and Add Radio Source functionality in the RadioCh application.

## Overview

Spec 002 provides the ability to:
- View discovered radio source proposals
- Review and edit proposal metadata
- Validate proposals before saving
- Save proposals as permanent radio sources
- Reject unwanted proposals

## Getting Started

### Launching the Application

```bash
# Ensure you're in the project directory with virtual environment activated
source .venv/bin/activate

# Run the application
python radioch_app.py
```

### Navigating to Validate & Add Tab

When the application launches, navigate to the "Validate & Add (Spec 002)" tab to view and manage proposals.

## Features

### 1. Viewing Proposals

The main Validate & Add tab displays a DataTable with all pending proposals:

| Column | Description |
|--------|-------------|
| ID | Unique proposal identifier |
| Name | Radio station name |
| Stream URL | Direct URL to the audio stream (truncated) |
| Type ID | StreamType classification ID |
| Secure | Security status (✅ for HTTPS, ⚠️ for HTTP) |
| Country | Country of origin |

Click "🔄 Refresh Proposals" to reload the list.

### 2. Editing a Proposal

Click on any row in the proposal table to open the edit screen:

#### Read-Only Fields (Set by Stream Analysis)
- **Stream URL**: The direct URL to the audio stream
- **Stream Type ID**: Classification from the 14 predefined types
- **Secure**: Security status (true for HTTPS, false for HTTP)

#### Editable Fields
- **Name**: Human-readable station name
- **Website URL**: Station's website URL
- **Country**: Country of origin
- **Description**: Brief description
- **Image URL**: Logo or image URL

### 3. Security Warnings

For HTTP (non-secure) streams, the application displays:
- A prominent warning banner in the edit screen
- A confirmation dialog when saving

**Warning message**: "⚠️ This stream uses HTTP (not secure). Proceed with caution."

### 4. Saving a Proposal

When you click "💾 Save to Database":

1. The system validates required fields:
   - Stream URL (non-empty)
   - Name (non-empty)
   - Website URL (non-empty)

2. Checks for duplicate stream URLs in the database

3. For HTTP streams, requires explicit confirmation

4. Creates a new RadioSourceNode in the database

5. Deletes the proposal (prevents duplicates)

6. Returns to the proposal list (automatically refreshed)

### 5. Rejecting a Proposal

Click "❌ Reject Proposal" to delete a proposal:

1. A confirmation dialog appears
2. Upon confirmation, the proposal is permanently deleted
3. The list refreshes automatically

**Note**: Rejected proposals cannot be recovered.

### 6. Canceling

Click "↩️ Cancel" or press `Escape` to return to the proposal list without changes.

## Database Management Tab

The Database tab provides additional functionality:

### Run Migration
Executes database migrations to set up or update the schema.

### View Stream Types
Displays all 14 predefined stream type classifications:
- Protocol (HTTP, HTTPS, HLS)
- Format (MP3, AAC, OGG)
- Metadata type (Icecast, Shoutcast, None)

### View Radio Sources
Shows all saved radio sources in the database.

## Validation Rules

### Required Fields
- `streamUrl`: Must be non-empty and valid URL format
- `name`: Must be non-empty
- `websiteUrl`: Must be non-empty and valid URL format

### URL Validation
URLs must have:
- Valid scheme (http or https)
- Valid domain (netloc)

### Duplicate Detection
The system rejects proposals where the stream URL already exists in the RadioSourceNode table.

**Error message**: "This stream URL already exists in the database"

## Error Messages

| Error | Cause | Resolution |
|-------|-------|------------|
| "Stream URL is required" | Empty stream URL | Proposal must have stream URL |
| "Name is required" | Empty name field | Enter a name for the station |
| "Website URL is required" | Empty website URL | Enter the station's website |
| "Invalid URL format" | Malformed URL | Ensure URL starts with http:// or https:// |
| "Stream URL already exists" | Duplicate URL | This stream is already in the database |
| "Proposal not found" | Invalid proposal ID | Refresh the list |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Escape` | Cancel editing / Close dialog |
| `Tab` | Navigate between fields |
| `Enter` | Confirm selection / Submit form |

## API Usage (Programmatic)

The services can also be used programmatically:

```python
from src.database import SessionLocal
from src.repositories.proposal_repository import ProposalRepository
from src.repositories.radio_source_repository import RadioSourceRepository
from src.services.proposal_validation_service import ProposalValidationService
from src.services.radio_source_service import RadioSourceService

# Create session
db = SessionLocal()

# Initialize repositories and services
proposal_repo = ProposalRepository(db)
radio_source_repo = RadioSourceRepository(db)
validation_service = ProposalValidationService(proposal_repo, radio_source_repo)
radio_source_service = RadioSourceService(
    proposal_repo, radio_source_repo, validation_service
)

# Get all proposals
proposals = radio_source_service.get_all_proposals()

# Validate a proposal
result = validation_service.validate_proposal(proposal_id=1)
if result.is_valid:
    print("Proposal is valid")
else:
    print(f"Errors: {result.errors}")

# Save a proposal
saved_source = radio_source_service.save_from_proposal(proposal_id=1)
print(f"Saved as RadioSourceNode ID: {saved_source.id}")

# Reject a proposal
success = radio_source_service.reject_proposal(proposal_id=2)

# Clean up
db.close()
```

## Troubleshooting

### No proposals showing
- Ensure the database has been migrated
- Check that proposals have been created (via Spec 001 or manually)
- Click the refresh button

### Services not initialized
- Check database file exists in `./instance/radio_sources.db`
- Run migrations: `python migrate.py`

### Validation failures
- Review the error messages displayed
- Ensure all required fields are filled
- Verify URL formats are correct

## Related Documentation

- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Overall project architecture
- [Spec 002 Specification](spec.md) - Full feature specification
- [Implementation Tasks](IMPLEMENTATION_TASKS.md) - Development tasks
