CREATE TABLE IF NOT EXISTS guild_prefixes (
    guild_id BIGINT NOT NULL,
    prefixes TEXT[],
    PRIMARY KEY(guild_id)
);

CREATE TABLE IF NOT EXISTS errors (
    id TEXT NOT NULL UNIQUE,
    error TEXT NOT NULL,
    command TEXT NOT NULL,
    message_url TEXT NOT NULL,
    user_id BIGINT NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS snipe (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT NOW()
);

-- user bigint, time_expires, time_added, added_by bigint postgres
CREATE TABLE IF NOT EXISTS donors (
    user_id BIGINT NOT NULL,
    time_expires TIMESTAMP NOT NULL,
    time_added TIMESTAMP NOT NULL DEFAULT NOW(),
    added_by BIGINT NOT NULL,
    PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS guild_perms (
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    command TEXT NOT NULL,
    allowed BOOLEAN NOT NULL,
    PRIMARY KEY(guild_id, role_id, command)
);

CREATE TABLE IF NOT EXISTS user_uwulock (
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    added_by BIGINT NOT NULL,
    PRIMARY KEY(user_id, guild_id)
);

CREATE TABLE IF NOT EXISTS fm (
    user_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    PRIMARY KEY(user_id, username)
);