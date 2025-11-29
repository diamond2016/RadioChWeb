# Implementation Plan: Spec 003 - Analyze and Classify Stream

**Feature Branch**: `003-analyze-and-classify-stream`  
**Created**: 2025-11-08  
**Status**: Planning Complete  
**Dependencies**: None (foundational spec)

## 1. Technical Context

### Environment
- **Python Version**: 3.13.9 ✓ (verified)
- **Virtual Environment**: Active ✓
- **Operating System**: Linux (Fedora)

### External Dependencies (Verified)
- **ffmpeg**: 7.1.2 ✓ (installed at /usr/bin/ffmpeg)
- **curl**: 8.11.1 ✓ (installed at /usr/bin/curl)
- **Status**: Both tools documented as prerequisites (not auto-checked at startup)

### Python Dependencies
- **Flask**: 2.3.2 ✓
- **Flask-SQLAlchemy**: 3.1.1 ✓
- **SQLAlchemy**: 2.0.43 ✓
- **Textual**: 6.5.0 ✓ (for future CLI interface)
- **pytest**: Need to add to requirements.txt
- **Missing**: None identified

### Testing Framework
- **Selected**: pytest
- **Rationale**: More Pythonic, better fixtures, widespread adoption

## 2. Architecture Decisions

### Service Layer Design
**Decision**: Dual interface approach
- **Service Class**: `src/services/stream_analyzer.py` - Core business logic, callable internally
- **Flask API Endpoint**: `POST /api/analyze-stream` - REST endpoint for external/CLI calls
- **Rationale**: Enables both programmatic calls (from spec 001) and independent testing via CLI tools (curl, Postman)

### StreamType Management
**Decision**: SQLAlchemy model with initialization module
- **Model**: `StreamType` in `src/models.py`
- **Data Loader**: `src/init_data.py` - Loads 14 predefined StreamTypes on first run
- **Future Additions**: Manual patches (no automated migration system required)
- **Seed Data Script Explanation**: A Python script that runs once to populate the StreamType table with the 14 predefined stream configurations. It checks if data exists before inserting to avoid duplicates.

### Error Handling Strategy
**Decision**: HTTP status codes + structured logging
- **For API**: Return standard HTTP codes (200, 400, 500) with JSON error details
- **For Service**: Raise custom exceptions with specific error codes
- **Logging**: Python logging module with file-based structured logs (JSON format recommended)
  - Level: ERROR and above
  - Location: `logs/stream_analyzer.log`
  - Not user-facing (for programmers/admins only)

### Result Data Structure
**Decision**: Python dataclass
- **Type**: `@dataclass StreamAnalysisResult`
- **Rationale**: Type-safe, clean, built-in serialization support
- **Location**: `src/models.py` or `src/services/stream_analyzer.py`

### Raw FFmpeg Output Storage
**Decision**: Temporary files with cleanup
- **Location**: `/tmp/radioch_ffmpeg_*.log` (or system temp dir)
- **Lifetime**: Deleted after analysis complete (kept on error for debugging)
- **Logging**: Path logged to structured log file for troubleshooting

## 3. Timeout Configuration

### Dual Timeout Strategy
- **curl timeout**: 5 seconds (header fetch only)
- **ffmpeg timeout**: 25 seconds (deep stream analysis)
- **Total max**: 30 seconds (per spec requirement)
- **Handling**: Kill process (SIGTERM then SIGKILL) on timeout, return error code "TIMEOUT"

## 4. Concurrency Model

### Processing Mode
**Decision**: Sequential, one-at-a-time
- **v1 Scope**: Single URL analysis per request
- **Rationale**: Simpler implementation, sufficient for discovery workflow
- **Future**: Spec 001 may batch URLs, but each calls spec 003 sequentially

## 5. Data Model Details

### StreamType Table Schema
```sql
CREATE TABLE stream_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol VARCHAR(10) NOT NULL,      -- HTTP, HTTPS, HLS
    format VARCHAR(10) NOT NULL,        -- MP3, AAC, OGG
    metadata VARCHAR(20) NOT NULL,      -- Icecast, Shoutcast, None
    display_name VARCHAR(100) NOT NULL, -- "HTTP MP3 with Icecast metadata"
    created_at DATETIME NOT NULL,       -- Added field
    is_active BOOLEAN NOT NULL DEFAULT TRUE -- Added field
);
```

**Predefined Data** (14 entries loaded by `init_data.py`):
1. HTTP-MP3-Icecast
2. HTTP-MP3-Shoutcast
3. HTTP-MP3-None
4. HTTP-AAC-Icecast
5. HTTP-AAC-Shoutcast
6. HTTP-AAC-None
7. HTTPS-MP3-Icecast
8. HTTPS-MP3-Shoutcast
9. HTTPS-MP3-None
10. HTTPS-AAC-Icecast
11. HTTPS-AAC-Shoutcast
12. HTTPS-AAC-None
13. HLS-AAC-None
14. PLAYLIST (special type)

### StreamAnalysisResult Dataclass
```python
@dataclass
class StreamAnalysisResult:
    is_valid: bool
    stream_type_id: Optional[int]
    is_secure: bool
    error_code: Optional[str]  # "TIMEOUT", "UNSUPPORTED_PROTOCOL", "UNREACHABLE", "INVALID_FORMAT"
    detection_method: str  # "HEADER", "FFMPEG", "BOTH"
    raw_content_type: Optional[str]
    raw_ffmpeg_output: Optional[str]
    analyzed_url: str
```

### PLAYLIST Handling
**Decision**: Defer to recommendation - treat as special StreamType
- **Type ID**: 14 (PLAYLIST)
- **Behavior**: Mark as valid, but parsing not implemented in v1
- **Response**: `isValid: true`, `streamTypeId: 14`, note in documentation
- **Future**: Spec 001 will handle "playlist not supported" message to user

## 6. Implementation Checklist

### Phase 1: Foundation (Day 1)
- [ ] Add pytest to `requirements.txt`
- [ ] Create `src/services/` directory
- [ ] Create `logs/` directory (with .gitignore entry)
- [ ] Define `StreamType` SQLAlchemy model in `src/models.py`
- [ ] Create `StreamAnalysisResult` dataclass in `src/services/stream_analyzer.py`
- [ ] Create `src/init_data.py` with 14 StreamType seed data

### Phase 2: Core Service (Day 2-3)
- [ ] Implement `StreamAnalyzerService` class:
  - [ ] `analyze_url(url: str) -> StreamAnalysisResult` main method
  - [ ] `_validate_protocol(url: str)` - Check HTTP/HTTPS only, reject RTMP/RTSP
  - [ ] `_check_security(url: str) -> bool` - Extract protocol, set isSecure flag
  - [ ] `_curl_analyze(url: str, timeout: int = 5) -> dict` - Header analysis
  - [ ] `_ffmpeg_analyze(url: str, timeout: int = 25) -> dict` - Deep analysis
  - [ ] `_compare_results(curl_result, ffmpeg_result) -> dict` - FFmpeg authoritative
  - [ ] `_detect_playlist(curl_result, ffmpeg_result) -> bool` - .m3u/.pls/.m3u8
  - [ ] `_classify_stream(analysis_data) -> int` - Match to StreamType ID
- [ ] Implement timeout handling with subprocess.Popen + threading
- [ ] Implement structured logging (JSON format to `logs/stream_analyzer.log`)
- [ ] Handle temp file creation/cleanup for ffmpeg output

### Phase 3: Flask API (Day 4)
- [ ] Create Flask route `POST /api/analyze-stream`
  - [ ] Request schema: `{ "url": "http://..." }`
  - [ ] Response schema: JSON serialized `StreamAnalysisResult`
  - [ ] HTTP codes: 200 (success), 400 (bad request), 500 (server error)
- [ ] Add input validation (URL format check)
- [ ] Add error handling middleware

### Phase 4: Testing (Day 5)
- [ ] Write pytest test cases (TDD approach):
  - [ ] `test_valid_http_mp3_stream()` - Test case 2 from spec
  - [ ] `test_valid_https_aac_stream()` - Test case 1 from spec
  - [ ] `test_invalid_html_page()` - Test case 3 from spec
  - [ ] `test_unsupported_rtmp()` - Test case 4 from spec
  - [ ] `test_curl_ffmpeg_mismatch()` - Test case 5 from spec (FFmpeg wins)
  - [ ] `test_playlist_detection()` - Test case 6 from spec
  - [ ] `test_timeout_handling()` - Verify 30s max
  - [ ] `test_unreachable_url()` - Network error case
- [ ] Create mock fixtures for curl/ffmpeg output
- [ ] Test Flask endpoint with test client

### Phase 5: Integration & Documentation (Day 6)
- [ ] Run `init_data.py` to populate StreamType table
- [ ] Test end-to-end with real stream URLs
- [ ] Create API documentation (usage examples)
- [ ] Update main README with spec 003 status
- [ ] Verify SC-001 through SC-005 success criteria

## 7. File Structure

```
RadioCh/
├── src/
│   ├── services/
│   │   ├── __init__.py
│   │   └── stream_analyzer.py       # Core service class
│   ├── models.py                     # StreamType model + dataclass
│   ├── init_data.py                  # StreamType seed data loader
│   ├── app.py                        # Flask app with /api/analyze-stream route
│   └── database.py                   # SQLAlchemy setup (existing)
├── tests/
│   ├── __init__.py
│   ├── test_stream_analyzer.py       # Service layer tests
│   ├── test_api_analyze.py           # Flask API tests
│   └── fixtures/
│       ├── mock_curl_output.json
│       └── mock_ffmpeg_output.txt
├── logs/
│   └── stream_analyzer.log           # Structured logs (gitignored)
├── requirements.txt                  # Add pytest
└── specs/
    └── 003-analyze-and-classify-stream/
        ├── spec.md                   # Original spec
        └── plan.md                   # This file
```

## 8. Testing Strategy

### Unit Tests (pytest)
- Test each private method in isolation with mocks
- Test timeout handling with controlled delays
- Test StreamType classification logic with all 14 types
- Test error code generation for each failure scenario

### Integration Tests
- Test full analyze_url() flow with real subprocess calls (using known test streams)
- Test Flask API endpoint with test client
- Verify database queries for StreamType lookup

### Manual Testing Checklist
- [ ] Test with known HTTP MP3 stream
- [ ] Test with known HTTPS AAC stream
- [ ] Test with HTML page URL
- [ ] Test with unreachable URL
- [ ] Test with RTMP URL (should reject)
- [ ] Test with .m3u playlist URL
- [ ] Test timeout with very slow stream
- [ ] Test via curl: `curl -X POST http://localhost:5000/api/analyze-stream -H "Content-Type: application/json" -d '{"url":"http://example.com/stream.mp3"}'`

## 9. Success Criteria Validation

### SC-001: Analysis under 30 seconds
- **Implementation**: Hard timeout at 30s (5s curl + 25s ffmpeg)
- **Test**: Measure execution time in unit tests, assert < 30s

### SC-002: 95% invalid URL rejection
- **Implementation**: Protocol validation + FFmpeg error detection
- **Test**: Run against dataset of 100 mixed URLs (20 invalid), assert ≥95% correct rejection

### SC-003: 100% correct classification for valid streams
- **Implementation**: StreamType lookup table with all 14 predefined types
- **Test**: Test all 14 stream type combinations, assert correct ID returned

### SC-004: 100% HTTP security flagging
- **Implementation**: URL protocol parsing (http vs https)
- **Test**: Test 10 HTTP streams, assert all return `isSecure: false`

### SC-005: FFmpeg authoritative on mismatch
- **Implementation**: In `_compare_results()`, always use ffmpeg data over curl
- **Test**: Mock curl as audio/mpeg, ffmpeg as AAC, assert AAC classification

## 10. Known Limitations (v1)

- Playlist parsing not implemented (detected but not expanded)
- RTMP/RTSP protocols not supported
- No retry logic on transient network errors
- Sequential processing only (no parallel analysis)
- No caching of analysis results

## 11. Future Enhancements (v2+)

- Playlist expansion (.m3u/.pls parsing with "best popularity" selection)
- RTMP/RTSP protocol support
- Caching layer for recently analyzed URLs
- Parallel analysis for batch operations
- More audio formats (OGG, FLAC, Opus)
- Enhanced metadata extraction (bitrate, sample rate, tags)

## 12. Dependencies on Other Specs

### Upstream (Specs that depend on 003)
- **Spec 001** (Discover): Calls spec 003 to validate URLs
- **Spec 002** (Validate and Add): Uses streamTypeId from spec 003 results

### Downstream (Specs 003 depends on)
- None (this is foundational)

## 13. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| FFmpeg output format changes | Low | High | Parse conservatively, log raw output for debugging |
| Timeout too short for slow streams | Medium | Medium | Allow configuration, document 30s limit |
| StreamType coverage incomplete | Low | High | Test with diverse real-world streams, expand list if needed |
| Playlist detection false positives | Low | Low | Conservative content-type checks, manual review of edge cases |

## 14. Approval & Sign-off

- [ ] Technical approach reviewed
- [ ] File structure approved
- [ ] Testing strategy confirmed
- [ ] Success criteria measurable
- [ ] Ready to begin implementation

---

**Next Steps**: 
1. Review this plan with stakeholder
2. Create feature branch: `git checkout -b 003-analyze-and-classify-stream`
3. Begin Phase 1 implementation
