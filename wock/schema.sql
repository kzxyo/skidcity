--- Configuration
CREATE EXTENSION IF NOT EXISTS citext;

--- Global tables

CREATE TABLE IF NOT EXISTS traceback (
    id TEXT UNIQUE NOT NULL,
    command TEXT NOT NULL,
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    traceback TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS whitelist (
    user_id BIGINT,
    guild_id BIGINT
);

CREATE TABLE IF NOT EXISTS blacklist (
    user_id BIGINT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY (user_id)
);

--- User tables

CREATE TABLE IF NOT EXISTS afk (
    user_id BIGINT UNIQUE NOT NULL,
    message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS timezone (
    user_id BIGINT UNIQUE NOT NULL,
    location TEXT
);

CREATE TABLE IF NOT EXISTS highlight_words (
    user_id BIGINT NOT NULL,
    word TEXT NOT NULL,
    strict BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (user_id, word)
);

CREATE TABLE IF NOT EXISTS highlight_block (
    user_id BIGINT NOT NULL,
    entity_id BIGINT NOT NULL,
    PRIMARY KEY (user_id, entity_id)
);

CREATE TABLE IF NOT EXISTS btc_subscriptions (
    user_id BIGINT NOT NULL,
    transaction TEXT NOT NULL,
    PRIMARY KEY (user_id, transaction)
);

CREATE TABLE IF NOT EXISTS reminders (
    user_id BIGINT NOT NULL,
    text CITEXT NOT NULL,
    jump_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS lastfm (
    user_id BIGINT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    config JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS lastfm_commands (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    command TEXT NOT NULL,
    public BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS lastfm_crowns (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    artist CITEXT NOT NULL,
    plays BIGINT NOT NULL,
    PRIMARY KEY (guild_id, artist)
);

CREATE SCHEMA IF NOT EXISTS lastfm_library;

CREATE TABLE IF NOT EXISTS lastfm_library.artists (
    user_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    artist CITEXT NOT NULL,
    plays BIGINT NOT NULL,
    PRIMARY KEY (user_id, artist)
);

CREATE TABLE IF NOT EXISTS lastfm_library.albums (
    user_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    artist CITEXT NOT NULL,
    album CITEXT NOT NULL,
    plays BIGINT NOT NULL,
    PRIMARY KEY (user_id, artist, album)
);

CREATE TABLE IF NOT EXISTS lastfm_library.tracks (
    user_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    artist CITEXT NOT NULL,
    track CITEXT NOT NULL,
    plays BIGINT NOT NULL,
    PRIMARY KEY (user_id, artist, track)
);

--- Guild tables
CREATE TABLE IF NOT EXISTS config (
    guild_id BIGINT UNIQUE,
    prefix TEXT,
    base_role_id BIGINT,
    voicemaster JSONB NOT NULL DEFAULT '{}'::JSONB,
    reassign_roles BOOLEAN DEFAULT FALSE,
    jail_log BIGINT DEFAULT NULL,
    invoke JSONB NOT NULL DEFAULT '{}'::JSONB,
    lock_ignore JSONB[] NOT NULL DEFAULT '{}'::JSONB[],
    reskin JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS starboard (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    threshold INTEGER NOT NULL DEFAULT 3,
    emoji TEXT NOT NULL DEFAULT '⭐',
    PRIMARY KEY (guild_id, emoji)
);


CREATE TABLE IF NOT EXISTS starboard_entries (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    emoji TEXT NOT NULL,
    starboard_message_id BIGINT NOT NULL,
    PRIMARY KEY (guild_id, channel_id, message_id, emoji),
    FOREIGN KEY (guild_id, emoji) REFERENCES starboard (guild_id, emoji) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reskin (
    user_id BIGINT NOT NULL,
    username TEXT,
    avatar_url TEXT,
    colors JSONB NOT NULL DEFAULT '{}'::JSONB,
    emojis JSONB NOT NULL DEFAULT '{}'::JSONB,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS tiktok (
    username TEXT NOT NULL,
    post_id BIGINT NOT NULL,
    channel_ids BIGINT[] NOT NULL DEFAULT '{}'::BIGINT[],
    PRIMARY KEY (username)
);

CREATE TABLE IF NOT EXISTS welcome_channels (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    self_destruct BIGINT,
    PRIMARY KEY (guild_id, channel_id)
);

CREATE TABLE IF NOT EXISTS goodbye_channels (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    self_destruct BIGINT,
    PRIMARY KEY (guild_id, channel_id)
);

CREATE TABLE IF NOT EXISTS boost_channels (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    self_destruct BIGINT,
    PRIMARY KEY (guild_id, channel_id)
);

CREATE TABLE IF NOT EXISTS sticky_messages (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    schedule BIGINT,
    PRIMARY KEY (guild_id, channel_id)
);

CREATE TABLE IF NOT EXISTS youtube_channels (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    youtube_id TEXT NOT NULL,
    youtube_name TEXT NOT NULL,
    message TEXT,
    PRIMARY KEY (guild_id, channel_id, youtube_id)
);

CREATE TABLE IF NOT EXISTS auto_responses (
    guild_id BIGINT NOT NULL,
    trigger TEXT NOT NULL,
    response TEXT NOT NULL,
    self_destruct BIGINT,
    not_strict BOOLEAN DEFAULT FALSE,
    ignore_command_check BOOLEAN DEFAULT FALSE,
    reply BOOLEAN DEFAULT FALSE,
    delete BOOLEAN DEFAULT FALSE,
    exclusive_channels JSONB[] NOT NULL DEFAULT '{}'::JSONB[],
    exclusive_roles JSONB[] NOT NULL DEFAULT '{}'::JSONB[],
    PRIMARY KEY (guild_id, trigger)
);

CREATE TABLE IF NOT EXISTS reaction_triggers (
    guild_id BIGINT NOT NULL,
    trigger TEXT NOT NULL,
    emoji TEXT NOT NULL,
    strict BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (guild_id, trigger, emoji)
);

CREATE TABLE IF NOT EXISTS voicemaster (
    guild_id BIGINT NOT NULL,
    owner_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS auto_roles (
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    discriminator TEXT,
    humans BOOLEAN DEFAULT FALSE,
    bots BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (guild_id, role_id)
);

CREATE TABLE IF NOT EXISTS reaction_roles (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    emoji TEXT NOT NULL,
    oneway BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (guild_id, message_id, role_id)
);

CREATE TABLE IF NOT EXISTS booster_roles (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS boosters_lost (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    lasted TIMESTAMP WITH TIME ZONE NOT NULL,
    expired TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS fake_permissions (
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    permission TEXT NOT NULL,
    PRIMARY KEY (guild_id, role_id, permission)
);

CREATE SCHEMA IF NOT EXISTS commands;

CREATE TABLE IF NOT EXISTS commands.ignored (
    guild_id BIGINT NOT NULL,
    target_id BIGINT NOT NULL,
    PRIMARY KEY (guild_id, target_id)
);

CREATE TABLE IF NOT EXISTS commands.disabled (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    command TEXT NOT NULL,
    PRIMARY KEY (guild_id, channel_id, command)
);

CREATE TABLE IF NOT EXISTS commands.restricted (
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    command TEXT NOT NULL,
    PRIMARY KEY (guild_id, role_id, command)
);

CREATE TABLE IF NOT EXISTS aliases (
    guild_id BIGINT NOT NULL,
    alias TEXT NOT NULL,
    command TEXT NOT NULL,
    invoke TEXT NOT NULL,
    PRIMARY KEY (guild_id, alias)
);

CREATE TABLE IF NOT EXISTS cases (
    guild_id BIGINT NOT NULL,
    case_id BIGINT NOT NULL,
    case_type TEXT NOT NULL,
    message_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    target_id BIGINT NOT NULL,
    moderator TEXT,
    target TEXT, 
    reason TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (guild_id, case_id)
);

CREATE TABLE IF NOT EXISTS counter_channels (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    option TEXT NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE,
    rate_limited TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (guild_id, option)
);

CREATE TABLE IF NOT EXISTS thread_watcher (
    guild_id BIGINT NOT NULL,
    thread_id BIGINT NOT NULL,
    PRIMARY KEY (guild_id, thread_id)
);

CREATE TABLE IF NOT EXISTS blunt (
    guild_id BIGINT UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    hits BIGINT NOT NULL DEFAULT 0,
    passes BIGINT NOT NULL DEFAULT 0,
    members JSONB[] NOT NULL DEFAULT '{}'::JSONB[]
);

CREATE SCHEMA IF NOT EXISTS metrics;

CREATE TABLE IF NOT EXISTS metrics.commands (
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    command TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics.guilds (
    guild_id BIGINT NOT NULL,
    members BIGINT DEFAULT 0,
    messages BIGINT DEFAULT 0,
    PRIMARY KEY (guild_id)
);

-- CREATE TABLE IF NOT EXISTS metrics.messages (
--     guild_id BIGINT NOT NULL,
--     channel_id BIGINT NOT NULL,
--     user_id BIGINT NOT NULL,
--     content TEXT NOT NULL,
--     timestamp TIMESTAMP WITH TIME ZONE NOT NULL
-- );

CREATE TABLE IF NOT EXISTS metrics.emojis (
    guild_id BIGINT NOT NULL,
    emoji_id BIGINT NOT NULL,
    uses BIGINT DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (guild_id, emoji_id)
);

CREATE TABLE IF NOT EXISTS metrics.names (
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics.avatars (
    user_id BIGINT NOT NULL,
    avatar TEXT NOT NULL,
    hash TEXT NOT NULL,
    timestamp BIGINT NOT NULL,
    PRIMARY KEY (user_id, hash)
);

CREATE TABLE IF NOT EXISTS metrics.seen (
    user_id BIGINT NOT NULL,
    timestamp BIGINT NOT NULL,
    PRIMARY KEY (user_id)
);
