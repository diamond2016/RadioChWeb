-- Migration: create users table
DROP TABLE IF EXISTS stream_analysis;
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    hash_password VARCHAR(512) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME,
    last_modified_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);