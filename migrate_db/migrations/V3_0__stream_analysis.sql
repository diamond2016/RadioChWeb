-- V3_0__stream_analysis.sql
-- Creates new table for stream analysis: stream_analysis

-- Create stream_analysis table
DROP TABLE IF EXISTS stream_analysis;
CREATE TABLE stream_analysis (
    id INTEGER NOT NULL,
    stream_url VARCHAR(200) NOT NULL,
    stream_type_id INTEGER,
    is_valid BOOLEAN NOT NULL,
    is_secure BOOLEAN NOT NULL,
    error_code VARCHAR(200),
    detection_method VARCHAR(200),
    raw_content_type VARCHAR(200),
    raw_ffmpeg_output VARCHAR(200),
    PRIMARY KEY (id),
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id)
);

-- Create indexes
CREATE INDEX idx_stream_analysis_stream_url ON stream_analysis(stream_url);

