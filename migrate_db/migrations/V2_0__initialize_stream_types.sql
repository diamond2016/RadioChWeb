-- V2_0__initialize_stream_types.sql
-- Initialize the stream_types table with predefined classifications from spec 003
-- This creates the 14 predefined stream type combinations

-- Insert predefined stream types
INSERT INTO stream_types (protocol, format, metadata_type, display_name) VALUES
('HTTP', 'MP3', 'Icecast', 'HTTP MP3 with Icecast metadata'),
('HTTP', 'MP3', 'Shoutcast', 'HTTP MP3 with Shoutcast metadata'),
('HTTP', 'MP3', 'None', 'HTTP MP3 direct stream'),
('HTTP', 'AAC', 'Icecast', 'HTTP AAC with Icecast metadata'),
('HTTP', 'AAC', 'Shoutcast', 'HTTP AAC with Shoutcast metadata'),
('HTTP', 'AAC', 'None', 'HTTP AAC direct stream'),
('HTTPS', 'MP3', 'Icecast', 'HTTPS MP3 with Icecast metadata'),
('HTTPS', 'MP3', 'Shoutcast', 'HTTPS MP3 with Shoutcast metadata'),
('HTTPS', 'MP3', 'None', 'HTTPS MP3 direct stream'),
('HTTPS', 'AAC', 'Icecast', 'HTTPS AAC with Icecast metadata'),
('HTTPS', 'AAC', 'Shoutcast', 'HTTPS AAC with Shoutcast metadata'),
('HTTPS', 'AAC', 'None', 'HTTPS AAC direct stream'),
('HLS', 'AAC', 'None', 'HTTP Live Streaming (HLS) with AAC'),
('PLAYLIST', 'PLAYLIST', 'None', 'Playlist file (.m3u, .pls, .m3u8) - parsing not implemented');