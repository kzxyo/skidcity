-- Core
CREATE TABLE IF NOT EXISTS whitelist (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS tracebacks (
    id SERIAL,
    command TEXT NOT NULL,
    error TEXT NOT NULL,
    error_id TEXT NOT NULL,
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    timestamp TEXT NOT NULL,
    PRIMARY KEY (id)
);

-- Guild
CREATE TABLE IF NOT EXISTS prefixes (
    guild_id BIGINT NOT NULL,
    prefix TEXT NOT NULL,
    PRIMARY KEY (guild_id)
);

-- User
CREATE TABLE IF NOT EXISTS timezone (
    user_id BIGINT NOT NULL,
    location TEXT NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS boosters_lost (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    started TEXT NOT NULL,
    stopped TEXT NOT NULL,
    PRIMARY KEY (guild_id, user_id, started, stopped)
);