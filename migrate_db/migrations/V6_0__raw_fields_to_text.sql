-- V6_0__raw_fields_to_text.sql
-- Convert raw_content_type and raw_ffmpeg_output columns to TEXT for SQLite.
-- This migration recreates the stream_analysis table to change column types.

PRAGMA foreign_keys=off;
BEGIN TRANSACTION;

CREATE TABLE stream_analysis_new (
    id INTEGER NOT NULL,
    stream_url VARCHAR(200) NOT NULL,
    stream_type_id INTEGER,
    is_valid BOOLEAN NOT NULL,
    is_secure BOOLEAN NOT NULL,
    error_code VARCHAR(200),
    detection_method VARCHAR(200),
    raw_content_type TEXT,
    raw_ffmpeg_output TEXT,
    extracted_metadata TEXT,
    PRIMARY KEY (id)
);

INSERT INTO stream_analysis_new (
    id, stream_url, stream_type_id, is_valid, is_secure,
    error_code, detection_method, raw_content_type, raw_ffmpeg_output, extracted_metadata
)
SELECT
    id, stream_url, stream_type_id, is_valid, is_secure,
    error_code, detection_method, raw_content_type, raw_ffmpeg_output, extracted_metadata
FROM stream_analysis;

DROP TABLE stream_analysis;
ALTER TABLE stream_analysis_new RENAME TO stream_analysis;

COMMIT;
PRAGMA foreign_keys=on;

-- Note: For MySQL production, prefer:
-- ALTER TABLE stream_analysis MODIFY COLUMN raw_content_type TEXT NULL;
-- ALTER TABLE stream_analysis MODIFY COLUMN raw_ffmpeg_output TEXT NULL;
