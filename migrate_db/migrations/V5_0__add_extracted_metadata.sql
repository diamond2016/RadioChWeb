-- V5_0__add_extracted_metadata.sql
-- Adds extracted_metadata column to stream_analysis

-- Add a nullable TEXT column for extracted metadata parsed from ffmpeg stderr
ALTER TABLE stream_analysis ADD COLUMN extracted_metadata TEXT;

-- No default; existing rows will have NULL in this column.
