CREATE SCHEMA IF NOT EXISTS lastfm;

CREATE TABLE IF NOT EXISTS lastfm.user (
    user_id BIGINT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    embed TEXT,
    command TEXT,
    reactions JSONB[] NOT NULL DEFAULT ARRAY[]::JSONB[]
);
