DROP TABLE IF EXISTS stream_types;
CREATE TABLE stream_types (
    id INTEGER NOT NULL,
    protocol VARCHAR(10) NOT NULL,
    format VARCHAR(10) NOT NULL,
    metadata_type VARCHAR(15) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX idx_stream_types_protocol ON stream_types(protocol);
CREATE INDEX idx_stream_types_format ON stream_types(format);
CREATE INDEX idx_stream_types_metadata_type ON stream_types(metadata_type);

DROP TABLE IF EXISTS radio_sources;
CREATE TABLE radio_sources (
    id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    stream_url VARCHAR(200) NOT NULL,
    website_url VARCHAR(200),
    stream_type_id INTEGER NOT NULL,
    is_secure BOOLEAN,
    country VARCHAR(50),
    description VARCHAR(200),
    image_url VARCHAR(200),
    created_at DATETIME,
    updated_at DATETIME,
    created_by INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE INDEX idx_radio_sources_stream_url ON radio_sources(stream_url);
CREATE INDEX idx_radio_sources_stream_type_id ON radio_sources(stream_type_id);
CREATE INDEX idx_radio_sources_is_secure ON radio_sources(is_secure);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    hash_password VARCHAR(512) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at DATETIME,
    updated_at DATETIME
);
CREATE INDEX idx_users_email ON users(email);

DROP TABLE IF EXISTS proposals;
CREATE TABLE proposals (
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
    updated_at DATETIME,
    created_by INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE INDEX idx_proposals_url ON proposals(stream_url);
CREATE INDEX idx_proposals_stream_type_id ON proposals(stream_type_id);
CREATE INDEX idx_proposals_is_secure ON proposals(is_secure);
CREATE INDEX idx_proposals_created_by ON proposals(created_by);

DROP TABLE IF EXISTS stream_analyses;
CREATE TABLE stream_analyses (
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
    created_at DATETIME,
    updated_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE INDEX idx_stream_analyses_stream_url ON stream_analyses(stream_url);
CREATE INDEX idx_stream_analyses_created_by ON stream_analyses(created_by);