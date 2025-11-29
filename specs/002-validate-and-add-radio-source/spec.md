# Feature Specification: Validate and Add a new Radio Source

**Feature Branch**: `002-validate-and-add-radio-source`
**Created**: 2025-10-26
**Status**: Draft
**Input**: User description: "System has discovered a potential new radio source, so the User verifies the data discovered, adds, if any, other infos (e.g. a brief description), and confirms or rejects the proposal of a new radio source in the repository of radio sources"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a new radio source from a URL (Priority: P1)

As a user, I want to check new potential radio sources (proposals) provided by system, check for every proposal if it is a valid radio stream source, complte if neede with other informations, and make system adds to the database the new source.

**Why this priority**: This is the second phase of the core functionality of the "discover" feature, and the primary mechanism for populating the radio source database.

**Independent Test**: This can be tested by providing a URL to a CLI command and triggering discover functionality. If the radio source is proposed in the list of proposals to te user, selecting it and ask the system save info to the database, the test passes if a new, valid entry is created in the `RadioSourceNode` table in the database.

**Acceptance Scenarios**:

1.  **Given** a user receives a proposal for a valid audio stream from spec 001 (which has been validated by spec 003),
    **When** the user checks the proposal, adds additional info if needed, and confirms to save,
    **Then** a new `RadioSourceNode` is created in the database, containing `streamUrl`, `name`, `streamTypeId`, `isSecure`, and any user-provided data (`description`, `country`, `image`).

2.  **Given** a user receives a proposal with `isSecure: false` flag (HTTP stream),
    **When** the user reviews the proposal,
    **Then** the CLI MUST display a security warning: "⚠️ This stream uses HTTP (not secure). Proceed with caution." and require explicit confirmation before saving.

3.  **Given** a user asks for new proposals of radio sources discovered by the system,
    **When** the discover process (spec 001) is completed and one or more proposals are available,
    **Then** the user may read and modify via CLI all data of each proposal: `streamUrl`, `name`, `websiteUrl`, `country`, `description`, `image`. The `streamTypeId` and `isSecure` fields are read-only (set by spec 003).

4.  **Given** a user attempts to save a proposal with a duplicate `streamUrl` that already exists in the database,
    **When** the validation process runs,
    **Then** the system MUST reject the save operation and inform the user that this stream is already in the database.

---

## Edge Cases

- **Duplicate stream URLs**: System checks database for existing `streamUrl` before saving. If found, reject with error message: "This stream already exists in the database."
- **HTTP security warnings**: Proposals with `isSecure: false` trigger explicit warning dialog, requiring user confirmation
- **How logo/image is loaded**: User can provide image URL or local file path (implementation details TBD)
- **Missing required fields**: System validates that at minimum `streamUrl`, `name`, and `websiteUrl` are present before allowing save
- **Read-only classification data**: User cannot modify `streamTypeId` or `isSecure` fields (set by spec 003) - these are displayed for information only


## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST receive validated proposals from spec 001 (which includes spec 003 classification data).
- **FR-002**: The system MUST display all proposal data to the user via CLI: `streamUrl`, `name`, `websiteUrl`, `streamTypeId` (read-only), `isSecure` (read-only), and user-editable fields.
- **FR-003**: The system MUST allow user to edit the following fields: `name`, `websiteUrl`, `country`, `description`, `image`.
- **FR-004**: The system MUST display a security warning if `isSecure: false` and require explicit confirmation before saving.
- **FR-005**: The system MUST validate that `streamUrl` does not already exist in the database (duplicate check).
- **FR-006**: The system MUST require minimum fields before saving: `streamUrl`, `name`, `websiteUrl` (all non-null).
- **FR-007**: Upon successful validation and user confirmation, the system MUST persist the new `RadioSourceNode` to the database.
- **FR-008**: The system MUST provide clear feedback to the user via CLI, indicating success or the reason for failure (e.g., duplicate URL, missing required fields).


### Key Entities

- **RadioSourceNode**: Represents a single radio stream source. Key attributes include:
    - `id` (Primary Key)
    - `streamUrl` (The direct URL to the audio stream - validated by spec 003, unique constraint)
    - `name` (A user-friendly name for the station - user editable)
    - `websiteUrl` (The source URL provided by the user - user editable)
    - `streamTypeId` (Foreign key to StreamType from spec 003 - READ ONLY, set during classification)
    - `isSecure` (Boolean flag from spec 003 - READ ONLY, false for HTTP, true for HTTPS)
    - `createdAt` (Timestamp of when the node was created)
    - `modifiedAt` (Timestamp of when the node was last modified)
    - `country` (Country name of radio source - user editable)
    - `description` (Brief description of radio source - user editable)
    - `image` (Logo or image URL/path - user editable)


## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The system can successfully validate and save a new radio source from a proposal in under 15 seconds (user interaction time excluded).
- **SC-002**: The system correctly rejects 100% of duplicate `streamUrl` entries before database insertion.
- **SC-003**: All saved `RadioSourceNode` entries in the database MUST have valid, non-null values for: `streamUrl`, `name`, `websiteUrl`, `streamTypeId`, `isSecure`.
- **SC-004**: 100% of HTTP stream proposals (isSecure: false) display security warning and require explicit user confirmation.