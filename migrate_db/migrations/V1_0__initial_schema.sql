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
    PRIMARY KEY (id)
);
CREATE INDEX idx_radio_sources_stream_url ON radio_sources(stream_url);
CREATE INDEX idx_radio_sources_stream_type_id ON radio_sources(stream_type_id);
CREATE INDEX idx_radio_sources_is_secure ON radio_sources(is_secure);

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
    PRIMARY KEY (id),
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id)
);
CREATE INDEX idx_proposals_url ON proposals(stream_url);
CREATE INDEX idx_proposals_stream_type_id ON proposals(stream_type_id);
CREATE INDEX idx_proposals_is_secure ON proposals(is_secure);
