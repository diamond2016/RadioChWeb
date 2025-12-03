-- V4_0__load_radio_sources_examples.sql
-- Create some examples of radio sources to browse in main page

-- Insert examples of radio sources
INSERT INTO radio_sources (name, stream_type_id, stream_url, website_url, is_secure, created_at) VALUES
('Radio Caroline', 1, 'http://sc6.radiocaroline.net:8040/stream.mp3', 'https://www.radiocaroline.co.uk/#home.html', False, datetime('now')),
('NPR News', 2, 'https://npr-ice.streamguys1.com/live.mp3', 'https://www.npr.org/', False, datetime('now')),
('Radio Paradise', 1, 'http://stream.radioparadise.com/mp3-192', 'https://www.radioparadise.com/', False, datetime('now'));
