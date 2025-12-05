-- V6_0__add_created_by_fields.sql
-- Rebuild `proposals` and `stream_analysis` to add `created_by` columns
-- with foreign key constraints referencing `users(id)`.

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- Rebuild proposals table with created_by FK
CREATE TABLE proposals_new (
    id INTEGER NOT NULL,
    stream_url VARCHAR(200) NOT NULL,
    name VARCHAR(200) NOT NULL,
    website_url VARCHAR(200),
    image_url VARCHAR(200),
    stream_type_id INTEGER NOT NULL,
    is_secure BOOLEAN NOT NULL DEFAULT 1,
    country VARCHAR(50),
    description VARCHAR(200),
    created_at DATETIME,
    created_by INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- copy existing data (created_by will be NULL for existing rows)
INSERT INTO proposals_new (id, stream_url, name, website_url, image_url, stream_type_id, is_secure, country, description, created_at)
    SELECT id, stream_url, name, website_url, image_url, stream_type_id, is_secure, country, description, created_at
    FROM proposals;

DROP TABLE proposals;
ALTER TABLE proposals_new RENAME TO proposals;

CREATE INDEX IF NOT EXISTS idx_proposals_url ON proposals(stream_url);
CREATE INDEX IF NOT EXISTS idx_proposals_stream_type_id ON proposals(stream_type_id);
CREATE INDEX IF NOT EXISTS idx_proposals_is_secure ON proposals(is_secure);
CREATE INDEX IF NOT EXISTS idx_proposals_created_by ON proposals(created_by);

-- Rebuild stream_analysis table with created_by FK
CREATE TABLE stream_analysis_new (
    id INTEGER NOT NULL,
    stream_url VARCHAR(200) NOT NULL,
    stream_type_id INTEGER,
    is_valid BOOLEAN NOT NULL,
    is_secure BOOLEAN NOT NULL,
    error_code VARCHAR(200),
    detection_method VARCHAR(200),
    raw_content_type TEXT NULL,
    raw_ffmpeg_output TEXT NULL,
    extracted_metadata TEXT NULL,
    created_by INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

INSERT INTO stream_analysis_new (id, stream_url, stream_type_id, is_valid, is_secure, error_code, detection_method, raw_content_type, raw_ffmpeg_output, extracted_metadata)
    SELECT id, stream_url, stream_type_id, is_valid, is_secure, error_code, detection_method, raw_content_type, raw_ffmpeg_output, extracted_metadata
    FROM stream_analysis;

DROP TABLE stream_analysis;
ALTER TABLE stream_analysis_new RENAME TO stream_analysis;

CREATE INDEX IF NOT EXISTS idx_stream_analysis_stream_url ON stream_analysis(stream_url);
CREATE INDEX IF NOT EXISTS idx_stream_analysis_created_by ON stream_analysis(created_by);

COMMIT;
PRAGMA foreign_keys = ON;

-- End of migration V6_0
