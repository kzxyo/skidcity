--- GLOBAL --- 
CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE IF NOT EXISTS traceback (
    id SERIAL PRIMARY KEY NOT NULL,
    command TEXT NOT NULL,
    error_code TEXT NOT NULL,
    error_message TEXT NOT NULL,
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

--- Servers ---
CREATE TABLE IF NOT EXISTS config (
    guild_id BIGINT UNIQUE NOT NULL,
    prefix VARCHAR (10) DEFAULT ',',
    lastfm_reactions JSONB[] NOT NULL DEFAULT '{}'::JSONB[]
);

CREATE TABLE IF NOT EXISTS join_messages (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    self_destruct BIGINT,
    PRIMARY KEY (guild_id, channel_id)
);

CREATE TABLE IF NOT EXISTS leave_messages (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    self_destruct BIGINT,
    PRIMARY KEY (guild_id, channel_id)
);

CREATE TABLE IF NOT EXISTS boost_messages (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    self_destruct BIGINT,
    PRIMARY KEY (guild_id, channel_id)
);


--- Antinuke ---
CREATE TABLE IF NOT EXISTS antinuke (
    guild_id BIGINT UNIQUE NOT NULL,
    whitelist BIGINT[] NOT NULL DEFAULT '{}'::BIGINT[],
    admins BIGINT[] NOT NULL DEFAULT '{}'::BIGINT[],
    botadd JSONB NOT NULL DEFAULT '{}'::JSONB,
    webhook JSONB NOT NULL DEFAULT '{}'::JSONB,
    emoji JSONB NOT NULL DEFAULT '{}'::JSONB,
    ban JSONB NOT NULL DEFAULT '{}'::JSONB,
    kick JSONB NOT NULL DEFAULT '{}'::JSONB,
    channel JSONB NOT NULL DEFAULT '{}'::JSONB,
    role JSONB NOT NULL DEFAULT '{}'::JSONB,
    permissions JSONB[] NOT NULL DEFAULT '{}'::JSONB[]
);

--- Boosters ---
CREATE TABLE IF NOT EXISTS boosters_lost (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expired_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, user_id)
);

--- AFK ---
CREATE TABLE IF NOT EXISTS afk (
    user_id BIGINT UNIQUE NOT NULL,
    status TEXT,
    date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

--- VoiceMaster ---
CREATE SCHEMA IF NOT EXISTS voicemaster;

CREATE TABLE IF NOT EXISTS voicemaster.configuration (
    guild_id BIGINT UNIQUE NOT NULL,
    category_id BIGINT NOT NULL,
    interface_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    role_id BIGINT,
    region TEXT,
    bitrate BIGINT
);

CREATE TABLE IF NOT EXISTS voicemaster.channels (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    owner_id BIGINT NOT NULL
);