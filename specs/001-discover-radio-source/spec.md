# Feature Specification: Discover Radio Source

**Feature Branch**: `001-discover-radio-source`
**Created**: 2025-10-26
**Status**: Draft
**Input**: User description: "A way, starting from an URL provided by user, to scrape resource information from Internet, and load in the database a new radio source"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover a new radio source from a URL (Priority: P1)

This user story begins when as a user, I have provided an URL, so that the system can scrape it, identify if it's a valid radio stream, and if it, propose to the user to add it to the database, as a new source. So I provide an URL (CLI) or a list of candidates Urls in a JSON file, and launch the discover session.
- The system analyzes the stream (see # 003 analyze-and classify-stream)
- Th system collcts data e make a "proposal" for a new radio strem to add to the database
- The use in this story completes data and inserts the proposal as a new radio Source Node.

**Why this priority**: This is the core functionality, and first step, of the "discover" feature and the primary mechanism for populating the radio source database.

**Independent Test**: This can be tested by providing a URL to a CLI command or a file with list of URLs. The test passes if one/any new, valid entries are proposed to the user, for validation and storing in the `RadioSourceNode` table in the database.

**Acceptance Scenarios**:

1.  **Given** a user provides a URL pointing directly to a valid audio stream (e.g., `.mp3`, `.aac`),
    **When** the discover process is initiated,
    **Then** spec 003 classifies the stream, and if valid, a new proposal of radio souce is created (in spec 002). Here use confirms proposal and the system creates a nes `RadioSourceNode` record.

2.  **Given** a user provides a URL to a public playlist file (e.g., `.m3u`, `.pls`),
    **When** the discover process is initiated,
    **Then** spec 003 detects it as "PLAYLIST" type, and the system defers playlist parsing to future iteration (v2). User is notified that playlist support is not yet implemented.

4.  **Given** a user provides a URL that is not a valid audio stream or supported playlist,
    **When** the discover process is initiated,
    **Then** spec 003 returns invalid status, and the system reports that no valid source was found and does not create a radio source proposal

---

## Edge Cases

- What happens when the provided URL is unreachable or returns a 404 error? → Spec 003 returns KO status, discover process reports failure
- How does the system handle different streaming formats and codecs? (e.g., MP3, AAC, HLS) → Spec 003 handles all format detection and classification
- What is the timeout for scraping a URL? → To be defined, but must account for spec 003's 30-second analysis time
- What if the user wants to trigger a new search manually (a new discover)? → CLI command can be re-run with new URL
- **Playlist files (.m3u, .pls)**: Detected by spec 003 as "PLAYLIST" type → Not supported in v1, user receives "playlist parsing not yet implemented" message
## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a URL as an input parameter via the CLI.
- **FR-002**: The system MUST call spec 003 (analyze-and-classify-stream) to validate and classify the provided URL.
- **FR-003**: The system MUST handle spec 003 response: if valid, proceed with discovery; if invalid, report error to user.
- **FR-004**: If a valid stream is found (spec 003 returns `isValid: true`), the system MUST create a proposal for a new `RadioSourceNode` entity, to be passed to spec 002 (validate-and-add).
- **FR-005**: The system MUST provide clear feedback to the user via the CLI, indicating success or the reason for failure (based on spec 003 errorCode).
- **FR-006**: The system MUST extract or generate initial data for the proposal: `streamUrl` (from spec 003), `name` (derived from URL), `websiteUrl` (original URL provided).
- **FR-007**: If spec 003 returns `isSecure: false` (HTTP stream), the system MUST include this flag in the proposal for user review in spec 002.
- **FR-008**: If spec 003 returns "PLAYLIST" type, the system MUST notify user that playlist parsing is not supported in v1 and not create a proposal.


### Key Entities

- **RadioSourceNode**: Represents a single radio stream source. Key attributes include:
    - `id` (Primary Key)
    - `streamUrl` (The direct URL to the audio stream - validated by spec 003)
    - `name` (A user-friendly name for the station)
    - `websiteUrl` (The source URL provided by the user)
    - `streamTypeId` (Foreign key to StreamType from spec 003 - indicates protocol/format/metadata)
    - `isSecure` (Boolean flag from spec 003 - false for HTTP, true for HTTPS)
    - `createdAt` (Timestamp of when the node was created)
    - `modifiedAt` (Timestamp of when the node was last modified)
    - `country` (Country name of radio source)
    - `description` (Brief description of radio source)
    - `image` (Logo or image to be used as miniature in display of node)


## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The system can successfully discover and propose a new radio source from a valid URL in under 60 seconds (including spec 003 analysis time of ~30s).
- **SC-002**: The system correctly identifies and rejects over 95% of invalid URLs (delegated to spec 003 validation).
- **SC-003**: All created `RadioSourceNode` proposals MUST have a valid, non-null `streamUrl` that has been validated by spec 003.
- **SC-004**: HTTP (non-secure) streams are correctly flagged with `isSecure: false` and passed to spec 002 with security warning.