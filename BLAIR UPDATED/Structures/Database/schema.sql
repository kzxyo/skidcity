-- Guild --

CREATE SCHEMA IF NOT EXISTS system;

CREATE TABLE IF NOT EXISTS system.welcomes (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    self_destruct INTEGER,
    PRIMARY KEY (guild_id, channel_id)
);

CREATE SCHEMA IF NOT EXISTS commands;

CREATE TABLE IF NOT EXISTS commands.disabled (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    command TEXT NOT NULL,
    PRIMARY KEY (guild_id, channel_id, command)
);

-- Users --
CREATE SCHEMA IF NOT EXISTS history;

CREATE TABLE IF NOT EXISTS history.names (
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    PRIMARY KEY (user_id, timestamp)
);

CREATE TABLE IF NOT EXISTS history.avatars (
    user_id BIGINT NOT NULL,
    avatar_url TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    PRIMARY KEY (user_id, timestamp)
);

-- Last.fm Integration
CREATE SCHEMA IF NOT EXISTS lastfm;

CREATE TABLE IF NOT EXISTS lastfm.usernames (
    username TEXT NOT NULL,
    user_id BIGINT NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS lastfm.crowns (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    artist TEXT NOT NULL,
    plays INTEGER NOT NULL,
    PRIMARY KEY (guild_id, artist)
);

CREATE TABLE IF NOT EXISTS lastfm.modes (
    user_id BIGINT NOT NULL,
    embed_code TEXT NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS lastfm.reactions (
    user_id BIGINT NOT NULL,
    upvote TEXT NOT NULL,
    downvote TEXT NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS lastfm.commands (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    command TEXT NOT NULL,
    public BOOLEAN NOT NULL,
    disabled BOOLEAN NOT NULL,
    PRIMARY KEY (guild_id, user_id)
);

CREATE SCHEMA IF NOT EXISTS lastfm_library;

CREATE TABLE IF NOT EXISTS lastfm_library.artists (
    username TEXT NOT NULL,
    user_id BIGINT NOT NULL,
    artist TEXT NOT NULL,
    plays INTEGER NOT NULL,
    PRIMARY KEY (user_id, artist)
);

CREATE TABLE IF NOT EXISTS lastfm_library.albums (
    username TEXT NOT NULL,
    user_id BIGINT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT NOT NULL,
    plays INTEGER NOT NULL,
    PRIMARY KEY (user_id, artist, album)
);

CREATE TABLE IF NOT EXISTS lastfm_library.tracks (
    username TEXT NOT NULL,
    user_id BIGINT NOT NULL,
    artist TEXT NOT NULL,
    track TEXT NOT NULL,
    plays INTEGER NOT NULL,
    PRIMARY KEY (user_id, artist, track)
);