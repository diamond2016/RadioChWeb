"""
Service to fetch live stream metadata via ffprobe for listen-time UI/API.
"""

import json
import re
import shutil
import subprocess
from typing import Optional

from model.dto.stream_metadata import StreamMetadataDTO


class StreamMetadataService:
    """Helper that wraps ffprobe and extracts bitrate/genre/current track info."""

    _METADATA_REGEX = re.compile(r"^\s*([^:]+):\s*(.+)$")

    def __init__(self, ffprobe_path: Optional[str] = None):
        self.ffprobe_path = ffprobe_path or shutil.which("ffprobe")

    @property
    def is_available(self) -> bool:
        return bool(self.ffprobe_path)

    def get_metadata(self, url: str, timeout_seconds: int = 10) -> StreamMetadataDTO:
        if not self.is_available:
            return StreamMetadataDTO(available=False, error_message="ffprobe executable not found")

        try:
            result = subprocess.run(
                [self.ffprobe_path, "-v", "quiet", "-print_format", "json", "-show_format", url],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False
            )
        except subprocess.TimeoutExpired as exc:
            return StreamMetadataDTO(available=False, error_message=f"ffprobe timed out ({exc})")
        except Exception as exc:
            return StreamMetadataDTO(available=False, error_message=str(exc))

        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip()
            return StreamMetadataDTO(available=False, error_message=f"ffprobe failed: {err}")

        payload = None
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback to parsing stderr if json is broken
            tags = self._parse_metadata_block(result.stderr)
            return self._build_dto_from_tags(tags, raw_output=result.stderr)

        format_section = payload.get("format", {}) or {}
        tags = format_section.get("tags") or {}
        bitrate = self._parse_int(format_section.get("bit_rate"))
        return StreamMetadataDTO(
            available=True,
            bitrate=bitrate,
            genre=self._pick_first(tags, ["icy-genre", "genre"]),
            current_track=self._pick_first(tags, ["StreamTitle", "title"])
        )

    def _build_dto_from_tags(self, tags: dict[str, str], raw_output: str) -> StreamMetadataDTO:
        return StreamMetadataDTO(
            available=bool(tags),
            bitrate=None,
            genre=self._pick_first(tags, ["icy-genre", "genre"]),
            current_track=self._pick_first(tags, ["StreamTitle", "title"]),
            error_message="metadata parsed from ffprobe text output" if tags else "metadata not found"
        )

    def _parse_metadata_block(self, content: str) -> dict[str, str]:
        if not content or "metadata" not in content.lower():
            return {}
        tags = {}
        started = False
        for line in content.splitlines():
            if not started:
                if line.strip().lower().startswith("metadata"):
                    started = True
                continue
            match = self._METADATA_REGEX.match(line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                tags[key] = value
            elif line.strip() == "":
                break
        return tags

    def _pick_first(self, tags: dict[str, str], keys: list[str]) -> Optional[str]:
        for key in keys:
            value = tags.get(key)
            if value:
                return value.strip()
        return None

    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            digits = re.sub(r"\D", "", value)
            return int(digits) if digits else None
