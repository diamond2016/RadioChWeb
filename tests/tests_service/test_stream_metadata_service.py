from unittest.mock import patch, MagicMock

from service.stream_metadata_service import StreamMetadataService
from model.dto.stream_metadata import StreamMetadataDTO


@patch("service.stream_metadata_service.shutil.which", return_value="/usr/bin/ffprobe")
@patch("service.stream_metadata_service.subprocess.run")
def test_get_metadata_with_json_output(mock_run, mock_which):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"format":{"bit_rate":"128000","tags":{"icy-genre":"Jazz","StreamTitle":"Test Song"}}}',
        stderr=""
    )
    service = StreamMetadataService()
    metadata = service.get_metadata("http://example.com/stream")
    assert isinstance(metadata, StreamMetadataDTO)
    assert metadata.available is True
    assert metadata.bitrate == 128000
    assert metadata.genre == "Jazz"
    assert metadata.current_track == "Test Song"


@patch("service.stream_metadata_service.shutil.which", return_value="/usr/bin/ffprobe")
@patch("service.stream_metadata_service.subprocess.run")
def test_get_metadata_text_fallback(mock_run, mock_which):
    text_stderr = "\nMetadata:\n    icy-genre       : Rock\n    StreamTitle     : Fallback Tune\n"
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="not-json",
        stderr=text_stderr
    )
    service = StreamMetadataService()
    metadata = service.get_metadata("http://example.com/stream")
    assert metadata.available is True
    assert metadata.genre == "Rock"
    assert metadata.current_track == "Fallback Tune"
