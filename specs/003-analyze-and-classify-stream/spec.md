# Feature Specification: [Analyze and classify stream]

**Feature Branch**: `003-analyze-and-classify stream`  
**Created**: 2025-10-28
**Status**: Draft  
**Input**: System analyze and classify an url of a potential new radio source, in order to decide if suitable and classify its type.

## System Prerequisites *(mandatory)*

This feature requires the following dependencies to be installed and functional:

- **Operating System**: Linux/Unix environment (primary support)
- **Required Tools**:
  - `ffmpeg` - Must be installed and accessible in system PATH
  - `curl` - For HTTP header analysis
- **Python Libraries** (to be determined during implementation):
  - Subprocess handling for external command execution
  - URL parsing and validation

**Installation verification**: The system SHOULD check for ffmpeg availability at startup and provide clear error if missing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Analyze and classify stream (Priority: P1)

This a system user story. System must analyze a candidate url stream. It analyzes automatically the stream and, if validated, classify the stream adding info into the proposal for next stages.

**Why this priority**: This is P1 because it is the first module to implement, being the base on which the application builds the database of radio stream sources. This user story is incliuded in spec-001, providing analysis of a potential radio source.

**Independent Test**: This can be tested by providing a URL to a CLI command and analyzing response of function: ok/ko, if ok data of classification

**Acceptance Scenarios**:

1. **Given** a user provides a known HTTPS URL pointing directly to a valid audio stream (e.g., `https://stream.example.com/radio.mp3`),
    **When** the analyze and classify process is triggered,
    **Then** the system performs dual validation (curl + ffmpeg), returns `isValid: true`, correct `streamTypeId`, and `isSecure: true`

2. **Given** a user provides a known HTTP URL pointing to a valid audio stream (e.g., `http://stream.example.com:8000/`),
    **When** the analyze and classify process is triggered,
    **Then** the system returns `isValid: true`, correct `streamTypeId`, and `isSecure: false` (security warning flag)

3. **Given** a user provides a URL pointing to an HTML page (e.g., `https://radiostation.com/listen`),
    **When** the analyze and classify process is triggered,
    **Then** the system returns `isValid: false` with appropriate `errorCode`

4. **Given** a user provides an RTMP URL (e.g., `rtmp://stream.example.com/live`),
    **When** the analyze and classify process is triggered,
    **Then** the system returns `isValid: false` with `errorCode: "UNSUPPORTED_PROTOCOL"`

5. **Given** curl detects content-type as `audio/mpeg` but ffmpeg detects AAC format,
    **When** the analyze and classify process is triggered,
    **Then** the system uses ffmpeg's AAC detection as authoritative and classifies accordingly

6. **Given** a user provides a playlist file URL (e.g., `http://station.com/stream.m3u`),
    **When** the analyze and classify process is triggered,
    **Then** the system returns `isValid: true` with `streamTypeId` pointing to special "PLAYLIST" type (parsing not performed in v1)



### Edge Cases

- **Unreachable URL or 404 error**: Analysis returns KO with error code indicating network failure
- **Header/FFmpeg mismatch**: When `curl -I` content-type differs from `ffmpeg -i` detection, FFmpeg is authoritative
- **Timeout during analysis**: If dual validation (curl + ffmpeg) exceeds timeout threshold, return KO with timeout error
- **Unsupported protocols**: RTMP/RTSP URLs are explicitly rejected with clear error message (not supported in v1)
- **HTTP (non-secure) streams**: Accepted but flagged with `isSecure: false` metadata field
- **Playlist files (.m3u, .pls, .m3u8)**: Detected and classified as "PLAYLIST" type - parsing deferred to future iteration

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a URL as an input parameter (called from spec 001 discover process).
- **FR-002**: The system MUST perform dual validation: first `curl -I` to check headers/content-type, then `ffmpeg -i` for deep analysis.
- **FR-003**: The system MUST compare results from both curl and ffmpeg; if they differ, ffmpeg detection is authoritative.
- **FR-004**: The system MUST support HTTP/HTTPS protocols only. RTMP/RTSP URLs MUST be rejected with error "Unsupported protocol".
- **FR-005**: The system MUST flag HTTP (non-HTTPS) streams with `isSecure: false` metadata, but accept them as valid.
- **FR-006**: The system MUST detect playlist files (.m3u, .pls, .m3u8) and classify them as type "PLAYLIST" (parsing deferred to future iteration).
- **FR-007**: The system MUST classify valid streams using predefined StreamType lookup table (see Key Entities).
- **FR-008**: The system MUST return classification result within 30 seconds (as per SC-001), including both curl and ffmpeg analysis time.

### Non-Functional Requirements

- **NFR-001**: The system REQUIRES `ffmpeg` to be installed and accessible in system PATH (Linux/Unix environments).
- **NFR-002**: The system SHOULD handle analysis timeouts gracefully, returning KO status if validation exceeds time limits.

### Testing Requirements

- **TR-001**: The system MUST include comprehensive unit tests for all service layer components, especially `StreamAnalysisService` and `StreamTypeService`.
- **TR-002**: The system MUST use `pytest-cov` for code coverage analysis, targeting minimum 85% coverage for business logic.
- **TR-003**: The system MUST include integration tests that validate the complete dual validation workflow (curl + ffmpeg).
- **TR-004**: The system MUST provide a Textual TUI test interface (`test_spec_003.py`) for manual testing and demonstration.
- **TR-005**: Test coverage reports MUST exclude external dependencies (ffmpeg, curl subprocess calls) from coverage calculations.


### Key Entities *(include if feature involves data)*

- **StreamType**: Lookup table with predefined stream type combinations. Each entry represents a known stream configuration:
    - `id` (Primary Key)
    - `protocol` (HTTP, HTTPS, HLS - enum values only)
    - `format` (MP3, AAC, OGG - enum values only)
    - `metadata` (Icecast, Shoutcast, None - enum values only)
    - `displayName` (Human-readable name, e.g., "HTTP MP3 with Icecast metadata")
    
    **Predefined StreamTypes** (initial set):
    1. `HTTP-MP3-Icecast`
    2. `HTTP-MP3-Shoutcast`
    3. `HTTP-MP3-None`
    4. `HTTP-AAC-Icecast`
    5. `HTTP-AAC-Shoutcast`
    6. `HTTP-AAC-None`
    7. `HTTPS-MP3-Icecast`
    8. `HTTPS-MP3-Shoutcast`
    9. `HTTPS-MP3-None`
    10. `HTTPS-AAC-Icecast`
    11. `HTTPS-AAC-Shoutcast`
    12. `HTTPS-AAC-None`
    13. `HLS-AAC-None` (for .m3u8 HLS streams)
    14. `PLAYLIST` (special type for playlist files - parsing not implemented in v1)

- **StreamAnalysisResult**: Temporary data structure returned by analysis process (not persisted):
    - `isValid` (boolean)
    - `streamTypeId` (foreign key to StreamType, null if invalid)
    - `isSecure` (boolean - false for HTTP, true for HTTPS)
    - `errorCode` (string, null if valid - e.g., "TIMEOUT", "UNSUPPORTED_PROTOCOL", "UNREACHABLE")
    - `detectionMethod` (string - "HEADER", "FFMPEG", "BOTH")
    - `rawContentType` (string from curl headers)
    - `rawFFmpegOutput` (string from ffmpeg detection)

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: The system can successfully analyze a radio stream URL (including dual curl + ffmpeg validation) in under 30 seconds.
- **SC-002**: The system correctly identifies and rejects over 95% of invalid URLs (e.g., links to HTML pages, images, RTMP/RTSP streams).
- **SC-003**: The system correctly classifies 100% of valid streams that match predefined StreamType combinations.
- **SC-004**: The system correctly flags HTTP streams with `isSecure: false` while accepting them as valid (100% accuracy).
- **SC-005**: When curl and ffmpeg results differ, ffmpeg classification is used in 100% of cases. 
