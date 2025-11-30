-- V4_0__load_radio_sources_examples.sql
-- Create some examples of radio sources to browse in main page

-- Insert examples of radio sources
INSERT INTO radio_sources (name, stream_type_id, stream_url, website_url, is_secure, created_at) VALUES
('radio caroline', 1, 'http://78.129.202.200:8040/index.html?sid=1', 'http://www.radiocaroline.co.uk/', False, datetime('now')),
('radio nova', 1, 'http://stream.radionova.fi:8000/radionova128', 'http://www.radionova.fi/', False, datetime('now')),
('radio rock', 1, 'http://stream.radiorock.fi:8000/radiorock128', 'http://www.radiorock.fi/', False, datetime('now')),
('radio x', 1, 'http://stream.radiox.co.uk:80/radiox.mp3', 'http://www.radiox.co.uk/', False, datetime('now')),
('radio 1', 1, 'http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p', 'http://www.bbc.co.uk/radio1/', True, datetime('now')),
('radio 2', 1, 'http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p', 'http://www.bbc.co.uk/radio2/', True, datetime('now')),
('radio 3', 1, 'http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio3_mf_p', 'http://www.bbc.co.uk/radio3/', True, datetime('now')),
('radio 4', 1, 'http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4fm_mf_p', 'http://www.bbc.co.uk/radio4/', True, datetime('now')),
('radio 5 live', 1, 'http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio5live_mf_p', 'http://www.bbc.co.uk/5live/', True, datetime('now')),
('radio 6 music', 1, 'http://bbcmedia.ic.llnwd.net/stream/bbcmedia_6music_mf_p', 'http://www.bbc.co.uk/6music/', True, datetime('now')),
('radio paradise', 1, 'http://stream.radioparadise.com/mp3-192', 'http://www.radioparadise.com/', False, datetime('now')),
('radio swiss jazz', 1, 'https://stream.srg-ssr.ch/m/radiojazz/aacp_96', 'https://www.radioswissjazz.ch/', True, datetime('now')),
('radio swiss classic', 1, 'https://stream.srg-ssr.ch/m/radioclassic/aacp_96', 'https://www.radioswissclassic.ch/', True, datetime('now'));