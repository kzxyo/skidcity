CREATE TABLE IF NOT EXISTS guildprefix (
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS message_store (
    guild_name TEXT,
    guild_id BIGINT,
    user_id BIGINT,
    user_name TEXT,
    timestamp TEXT,
    message_content TEXT
);

CREATE TABLE IF NOT EXISTS api_keys (
    user_id BIGINT,
    api_key TEXT,
    expiry TIMESTAMP
);

CREATE TABLE IF NOT EXISTS avatars (
    user_id BIGINT,
    username TEXT,
    avatar TEXT,
    hash TEXT,
    time BIGINT,
    PRIMARY KEY (user_id, hash)
);


CREATE TABLE IF NOT EXISTS fakepermissions (
    guild_id BIGINT,
    permission TEXT,
    role_id BIGINT
);

CREATE TABLE IF NOT EXISTS theme (
    guild_id BIGINT,
    embeds BOOLEAN DEFAULT true,
    color TEXT DEFAULT NULL,
    PRIMARY KEY (guild_id)
);

CREATE TABLE IF NOT EXISTS screentime (
    user_id BIGINT,
    online BIGINT DEFAULT 0,
    idle BIGINT DEFAULT 0,
    dnd BIGINT DEFAULT 0,
    offline BIGINT DEFAULT 0,
    time TEXT,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS lastfm (
    user_id BIGINT,
    username TEXT,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS lastfm_artists_index (
    user_id BIGINT,
    artist TEXT DEFAULT 0,
    playcount BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lastfm_track_index (
    user_id BIGINT,
    track TEXT DEFAULT 0,
    playcount BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS custom_ban_response (
    guild_id BIGINT,
    response TEXT,
    PRIMARY KEY (guild_id)
);

CREATE TABLE IF NOT EXISTS custom_kick_response (
    guild_id BIGINT,
    response TEXT,
    PRIMARY KEY (guild_id)
);