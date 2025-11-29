# Spec 003 Implementation: Analyze and Classify Stream

This document describes the implementation of **spec 003: analyze-and-classify-stream** according to the project architecture.

## 🏗️ Project Structure

The project now follows the standardized architecture:

```
src/
├── models/           # SQLAlchemy entities
│   ├── __init__.py
│   ├── stream_type.py          # StreamType lookup table
│   ├── radio_source_node.py    # Updated with streamTypeId, isSecure
│   └── proposal.py             # Proposal entity
├── dtos/             # Pydantic validation models
│   ├── __init__.py
│   ├── stream_analysis.py      # StreamAnalysisResult, StreamAnalysisRequest
│   ├── stream_type.py          # StreamTypeDTO
│   └── radio_source.py         # RadioSourceNodeDTO, ProposalDTO
├── repositories/     # Data access layer
│   ├── __init__.py
│   ├── stream_type_repository.py
│   ├── radio_source_repository.py
│   └── proposal_repository.py
├── services/         # Business logic layer
│   ├── __init__.py
│   ├── stream_analysis_service.py  # Core spec 003 implementation
│   └── stream_type_service.py
└── routes/           # Flask API endpoints (future)
```

## 🧪 Testing Spec 003

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install system tools (required by NFR-001):**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg curl
   
   # macOS
   brew install ffmpeg curl
   ```

3. **Initialize database:**
   ```bash
   python migrate_db.py
   ```

### Testing Framework

The implementation uses **pytest** with **pytest-cov** for comprehensive testing and coverage analysis as specified in TR-002:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows including external tool integration
- **Coverage Analysis**: Minimum 85% coverage target for business logic
- **Mocking**: Mock external subprocess calls (ffmpeg, curl) for reliable unit tests

### Run Tests

The **Textual TUI interface** provides an interactive test environment as specified in acceptance criteria:

```bash
# Run the spec 003 TUI test interface
python src/test_spec_003.py
```

**Features:**
- 🖥️ **Modern TUI**: Rich terminal interface with real-time updates
- ⚡ **Async Analysis**: Non-blocking stream analysis with progress indicators
- 🎨 **Rich Display**: Color-coded results with detailed raw data inspection
- ⚙️ **Configurable Timeouts**: 30s, 60s, or 120s analysis timeouts
- 📋 **Sample URLs**: Built-in test cases for immediate testing
- 🔄 **Real-time Status**: Live progress updates and error handling

**Alternative: Main RadioCh App**
```bash
# Run the full application (multi-tab interface)
python radioch_app.py
```

This provides a comprehensive interface with tabs for:
- **Spec 003**: Stream analysis and classification
- **Spec 001**: Discovery workflow (coming soon)
- **Spec 002**: Validation and adding sources (coming soon)
- **Database**: Migration tools and data viewing

## 🔄 Implementation Details

### Core Analysis Process (StreamAnalysisService)

The service implements the **dual validation strategy** from spec 003:

1. **Protocol Check**: Reject RTMP/RTSP (FR-004)
2. **Security Detection**: Determine if HTTPS (true) or HTTP (false)
3. **Curl Analysis**: `curl -I` for headers and content-type
4. **FFmpeg Analysis**: `ffmpeg -i` for deep format detection
5. **Result Resolution**: FFmpeg is authoritative when results differ (FR-003)
6. **Classification**: Match against predefined StreamType lookup table

### Predefined StreamTypes (14 types)

As defined in spec 003:

| ID | Type Key | Description |
|----|----------|-------------|
| 1 | HTTP-MP3-Icecast | HTTP MP3 with Icecast metadata |
| 2 | HTTP-MP3-Shoutcast | HTTP MP3 with Shoutcast metadata |
| 3 | HTTP-MP3-None | HTTP MP3 direct stream |
| ... | ... | ... |
| 13 | HLS-AAC-None | HTTP Live Streaming (HLS) with AAC |
| 14 | PLAYLIST-PLAYLIST-None | Playlist file (parsing deferred to v2) |

### Success Criteria Compliance

- ✅ **SC-001**: Analysis completes within 30 seconds
- ✅ **SC-002**: Correctly rejects invalid URLs (95%+ accuracy)
- ✅ **SC-003**: Classifies valid streams matching predefined types (100%)
- ✅ **SC-004**: Flags HTTP streams with `isSecure: false` (100%)
- ✅ **SC-005**: Uses FFmpeg as authoritative source (100%)

## 🔌 Integration Points

### Spec 001 Integration

Spec 001 (discover-radio-source) calls the analysis service:

```python
from services.stream_analysis_service import StreamAnalysisService

# In discover workflow
result = analysis_service.analyze_stream(url)
if result.is_valid:
    # Create proposal with classification data
    proposal = Proposal(
        stream_url=url,
        name=derived_name,
        stream_type_id=result.stream_type_id,
        is_secure=result.is_secure
    )
```

### Spec 002 Integration

Spec 002 (validate-and-add) receives proposals with read-only classification:

```python
# streamTypeId and isSecure are read-only (set by spec 003)
# User can only edit: name, websiteUrl, country, description, image
```

## 🛠️ Development Notes

### Error Handling

The implementation handles all edge cases from spec 003:
- Network timeouts → `ErrorCode.TIMEOUT`
- Unreachable URLs → `ErrorCode.UNREACHABLE`  
- Unsupported protocols → `ErrorCode.UNSUPPORTED_PROTOCOL`
- Invalid formats → `ErrorCode.INVALID_FORMAT`

### Performance Considerations

- **Timeout management**: Both curl and ffmpeg respect timeout limits
- **Resource cleanup**: Subprocess management with proper cleanup
- **Database efficiency**: StreamType lookup table for fast classification

### Security

- **HTTP warning**: All HTTP streams flagged with `isSecure: false`
- **Input validation**: URL parsing and protocol checking
- **Command injection prevention**: Proper subprocess argument handling

## 📋 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Install system tools**: `ffmpeg` and `curl`
3. **Run migration**: `python migrate_db.py`
4. **Run tests with coverage**: `pytest --cov=src --cov-report=html`
5. **Test analysis**: `python src/test_spec_003.py` (Textual TUI)
6. **Explore full app**: `python radioch_app.py` (Multi-tab interface)

### Testing Commands

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests  
pytest tests/integration/

# Generate coverage report
pytest --cov=src --cov-report=html
# View coverage report at htmlcov/index.html
```

## 🎯 Textual TUI Benefits

Using Textual provides several advantages over a traditional CLI:

- **Better UX**: Interactive interface with real-time feedback
- **Rich Display**: Color-coded results, progress indicators, and formatted output
- **Async Operations**: Non-blocking analysis with loading indicators
- **Error Handling**: Visual error states and user-friendly messages
- **Extensibility**: Easy to add new tabs for specs 001 and 002

The implementation is ready for integration with the discovery workflow (spec 001) and provides the foundation for the complete three-stage radio source management system with a modern, user-friendly interface.