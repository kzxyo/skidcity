--- Blacklists ---


CREATE TABLE IF NOT EXISTS blacklisted_object (
    object_id BIGINT,
    reason VARCHAR(1024),
    PRIMARY KEY (object_id)
);


CREATE TABLE IF NOT EXISTS blacklisted_command (
    guild_id BIGINT,
    command_name VARCHAR(32),
    PRIMARY KEY (guild_id, command_name)
);


CREATE TABLE IF NOT EXISTS starboard_blacklist (
    guild_id BIGINT,
    channel_id BIGINT,
    PRIMARY KEY (guild_id, channel_id)
);


--- User Data ---


CREATE TABLE IF NOT EXISTS notification (
    guild_id BIGINT,
    user_id BIGINT,
    keyword VARCHAR(32),
    PRIMARY KEY (guild_id, user_id, keyword)
);


CREATE TABLE IF NOT EXISTS starboard_message (
    original_message_id BIGINT,
    starboard_message_id BIGINT,
    PRIMARY KEY (original_message_id)
);


CREATE TABLE IF NOT EXISTS artist_crown (
    guild_id BIGINT,
    user_id BIGINT,
    artist_name VARCHAR(256),
    cached_playcount INTEGER,
    PRIMARY KEY (guild_id, artist_name)
);


CREATE TABLE IF NOT EXISTS chatgpt_usage (
    user_id BIGINT,
    uses INTEGER DEFAULT 1,
    PRIMARY KEY (user_id)
);


CREATE TABLE IF NOT EXISTS donator (
    user_id BIGINT,
    donation_tier TINYINT,
    total_donated FLOAT DEFAULT 0.0,
    donating_since BIGINT,
    PRIMARY KEY (user_id)
);


CREATE TABLE IF NOT EXISTS lastfm_vote_setting (
    user_id BIGINT,
    is_enabled BOOLEAN DEFAULT 1,
    upvote_emoji VARCHAR(128) DEFAULT NULL,
    downvote_emoji VARCHAR(128) DEFAULT NULL,
    PRIMARY KEY (user_id)
);


CREATE TABLE IF NOT EXISTS command_usage (
    user_id BIGINT,
    command_name VARCHAR(64),
    uses INTEGER DEFAULT 1,
    PRIMARY KEY (user_id, command_name)
);


CREATE TABLE IF NOT EXISTS afk (
    guild_id BIGINT,
    user_id BIGINT,
    status VARCHAR(512),
    left_at DATETIME,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS notes (
    guild_id BIGINT,
    user_id BIGINT,
    note VARCHAR(64),
    note_id INTEGER,
    PRIMARY KEY (guild_id, user_id, note)
);


CREATE TABLE IF NOT EXISTS guild_prefix (
    guild_id BIGINT,
    prefix VARCHAR(32) NOT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS custom_prefix (
    user_id BIGINT,
    prefix VARCHAR(32) NOT NULL,
    PRIMARY KEY (user_id)
);


CREATE TABLE IF NOT EXISTS name_history (
    user_id BIGINT,
    name VARCHAR(256) NOT NULL,
    updated_on DATETIME NOT NULL,
    PRIMARY KEY (user_id, name)
);


CREATE TABLE IF NOT EXISTS taken_roles (
    guild_id BIGINT,
    user_id BIGINT,
    role_id BIGINT,
    PRIMARY KEY (guild_id, user_id, role_id)
);


CREATE TABLE IF NOT EXISTS hard_banned (
    guild_id BIGINT,
    user_id BIGINT,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS soft_muted (
    guild_id BIGINT,
    user_id BIGINT,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS restricted_command (
    guild_id BIGINT,
    command_name VARCHAR(32),
    role_id BIGINT,
    PRIMARY KEY (guild_id, command_name, role_id)
);


CREATE TABLE IF NOT EXISTS pagination (
    guild_id BIGINT,
    channel_id BIGINT,
    message_id BIGINT,
    current_page INTEGER
);


CREATE TABLE IF NOT EXISTS pagination_pages (
    guild_id BIGINT,
    channel_id BIGINT,
    message_id BIGINT,
    page VARCHAR(1024),
    page_number INTEGER
);


CREATE TABLE IF NOT EXISTS temporary_bans (
    guild_id BIGINT,
    user_id BIGINT,
    unban_on DATETIME,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS hard_banned (
    guild_id BIGINT,
    user_id BIGINT,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS moderation_history (
    guild_id BIGINT,
    moderator_id BIGINT,
    member_id BIGINT,
    type VARCHAR(64),
    reason VARCHAR(256),
    created_on DATETIME,
    case_id INTEGER AUTO_INCREMENT,
    KEY (case_id),
    PRIMARY KEY (guild_id, moderator_id, created_on)
);


CREATE TABLE IF NOT EXISTS reminder (
    guild_id BIGINT,
    user_id BIGINT,
    created_on DATETIME,
    reminder_date BIGINT,
    content VARCHAR(255),
    original_message_url VARCHAR(128),
    PRIMARY KEY (guild_id, user_id, content)
);


CREATE TABLE IF NOT EXISTS boosters_lost (
    guild_id BIGINT,
    user_id BIGINT,
    expired DATETIME,
    PRIMARY KEY (guild_id, user_id)
);


--- Settings ---


CREATE TABLE IF NOT EXISTS user_settings (
    user_id BIGINT,
    lastfm_username VARCHAR(15) DEFAULT NULL,
    sunsign VARCHAR(32) DEFAULT NULL,
    location_string VARCHAR(128) DEFAULT NULL,
    timezone VARCHAR(32) DEFAULT NULL,
    PRIMARY KEY (user_id)
);


CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT,
    mute_role_id BIGINT DEFAULT NULL,
	jail_role_id BIGINT DEFAULT NULL,
	jail_channel_id BIGINT DEFAULT NULL,
    levelup_messages BOOLEAN DEFAULT 0,
    autoresponses BOOLEAN DEFAULT 1,
    restrict_custom_commands BOOLEAN DEFAULT 0,
    delete_blacklisted_usage BOOLEAN DEFAULT 0,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS media_auto_embed_settings (
    guild_id BIGINT,
    medal BOOLEAN DEFAULT 1,
    twitter BOOLEAN DEFAULT 1,
    tiktok BOOLEAN DEFAULT 1,
    soundcloud BOOLEAN DEFAULT 1,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS starboard_settings (
    guild_id BIGINT,
    channel_id BIGINT DEFAULT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    attachments_allowed BOOLEAN DEFAULT 1,
    selfstar_allowed BOOLEAN DEFAULT 1,
    show_jumpurl BOOLEAN DEFAULT 1,
    embed_color INTEGER DEFAULT 11643608,
    show_timestamp BOOLEAN DEFAULT 1,
    reaction_count INTEGER DEFAULT 3,
    emoji_name VARCHAR(64) DEFAULT '\u2b50' NOT NULL,
    emoji_id BIGINT DEFAULT NULL,
    emoji_type ENUM('unicode', 'custom') DEFAULT 'unicode' NOT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS clownboard_settings (
    guild_id BIGINT,
    channel_id BIGINT DEFAULT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    attachments_allowed BOOLEAN DEFAULT 1,
    selfclown_allowed BOOLEAN DEFAULT 1,
    show_jumpurl BOOLEAN DEFAULT 1,
    embed_color INTEGER DEFAULT 11643608,
    show_timestamp BOOLEAN DEFAULT 1,
    reaction_count INTEGER DEFAULT 3,
    emoji_name VARCHAR(64) DEFAULT '\U0001F921' NOT NULL,
    emoji_id BIGINT DEFAULT NULL,
    emoji_type ENUM('unicode', 'custom') DEFAULT 'unicode' NOT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS welcome_settings (
    guild_id BIGINT,
    channel_id BIGINT DEFAULT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    message VARCHAR(1024) DEFAULT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS boost_settings (
    guild_id BIGINT,
    channel_id BIGINT DEFAULT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    message VARCHAR(1024) DEFAULT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS unboost_settings (
    guild_id BIGINT,
    channel_id BIGINT DEFAULT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    message VARCHAR(1024) DEFAULT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS booster_role (
    guild_id BIGINT,
    user_id BIGINT DEFAULT NULL,
    role_id BIGINT DEFAULT NULL,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS booster_role_award (
    guild_id BIGINT,
    role_id BIGINT DEFAULT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS booster_role_base (
    guild_id BIGINT,
    role_id BIGINT DEFAULT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS sticky_message (
    channel_id BIGINT,
    message_id BIGINT,
    PRIMARY KEY (channel_id)
);


CREATE TABLE IF NOT EXISTS sticky_message_settings (
    guild_id BIGINT,
    channel_id BIGINT DEFAULT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    message VARCHAR(1024) DEFAULT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS leave_settings (
    guild_id BIGINT,
    channel_id BIGINT DEFAULT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    message VARCHAR(1024) DEFAULT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS logging_settings (
    -- # Every event column stores a channel ID (this isn't explained in it's name) # --
    guild_id BIGINT,
    channel_create BIGINT DEFAULT NULL,
    channel_update BIGINT DEFAULT NULL,
    channel_delete BIGINT DEFAULT NULL,
    role_create BIGINT DEFAULT NULL,
    role_update BIGINT DEFAULT NULL,
    role_delete BIGINT DEFAULT NULL,
    guild_update BIGINT DEFAULT NULL,
    message_delete BIGINT DEFAULT NULL,
    message_delete_bulk BIGINT DEFAULT NULL,
    message_update BIGINT DEFAULT NULL,
    member_ban BIGINT DEFAULT NULL,
    member_unban BIGINT DEFAULT NULL,
    member_join BIGINT DEFAULT NULL,
    member_kick BIGINT DEFAULT NULL,
    member_nickname_update BIGINT DEFAULT NULL,
    member_remove BIGINT DEFAULT NULL,
    member_update BIGINT DEFAULT NULL,
    voicechannel_leave BIGINT DEFAULT NULL,
    voicechannel_join BIGINT DEFAULT NULL,
    voicechannel_switch BIGINT DEFAULT NULL,
    emojis_add BIGINT DEFAULT NULL,
    emojis_update BIGINT DEFAULT NULL,
    emojis_remove BIGINT DEFAULT NULL,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS ranks (
    guild_id BIGINT,
    role_id BIGINT,
    PRIMARY KEY (guild_id, role_id)
);


CREATE TABLE IF NOT EXISTS sticky_roles (
    guild_id BIGINT,
    role_id BIGINT,
    PRIMARY KEY (guild_id, role_id)
);


CREATE TABLE IF NOT EXISTS message_log_ignore (
    guild_id BIGINT,
    channel_id BIGINT,
    PRIMARY KEY (channel_id)
);


CREATE TABLE IF NOT EXISTS autorole (
    guild_id BIGINT,
    role_id BIGINT,
    PRIMARY KEY (guild_id, role_id)
);


CREATE TABLE IF NOT EXISTS filter (
    guild_id BIGINT,
    keyword VARCHAR(32) NOT NULL,
    PRIMARY KEY (guild_id, keyword)
);


CREATE TABLE IF NOT EXISTS filter_whitelist (
    guild_id BIGINT,
    user_id BIGINT,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS filter_event (
    guild_id BIGINT,
    event VARCHAR(32) NOT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    threshold TINYINT DEFAULT 2,
    PRIMARY KEY (guild_id, event)
);


CREATE TABLE IF NOT EXISTS filter_snipe (
    guild_id BIGINT,
    invites BOOLEAN DEFAULT 0,
    links BOOLEAN DEFAULT 0,
    images BOOLEAN DEFAULT 0,
    words BOOLEAN DEFAULT 0,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS moderation_confirmations (
    guild_id BIGINT,
    is_enabled BOOLEAN DEFAULT 1,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS autoresponder (
    guild_id BIGINT,
    keyword VARCHAR(32) NOT NULL,
    response VARCHAR(1024) NOT NULL,
    created_by BIGINT,
    PRIMARY KEY (guild_id, keyword)
);


CREATE TABLE IF NOT EXISTS autoresponder_event (
    guild_id BIGINT,
    event VARCHAR(32) NOT NULL,
    response VARCHAR(1024) NOT NULL,
    PRIMARY KEY (guild_id, event)
);


CREATE TABLE IF NOT EXISTS autoreact (
    guild_id BIGINT,
    keyword VARCHAR(32),
    reaction VARCHAR(128),
    PRIMARY KEY (guild_id, keyword, reaction)
);


CREATE TABLE IF NOT EXISTS autoreact_event (
    guild_id BIGINT,
    event VARCHAR(32) NOT NULL,
    reaction VARCHAR(128),
    PRIMARY KEY (guild_id, event, reaction)
);


CREATE TABLE IF NOT EXISTS disabled_feature (
    guild_id BIGINT,
    name VARCHAR(64),
    type ENUM('module', 'command'),
    PRIMARY KEY (guild_id, name, type)
);


CREATE TABLE IF NOT EXISTS highlight (
    guild_id BIGINT,
    user_id BIGINT,
    keyword VARCHAR(32),
    PRIMARY KEY (guild_id, keyword)
);


CREATE TABLE IF NOT EXISTS highlight_ignore (
    guild_id BIGINT,
    user_id BIGINT,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS ignore_object (
	guild_id BIGINT,
	object_id BIGINT,
	type ENUM('member', 'channel', 'role'),
	PRIMARY KEY (guild_id, object_id)
);


CREATE TABLE IF NOT EXISTS pin_archive (
	guild_id BIGINT,
	channel_id BIGINT,
	is_enabled BOOLEAN DEFAULT 1,
	PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS webhooks (
	guild_id BIGINT,
	identifier VARCHAR(32),
	webhook_url TINYTEXT,
	channel_id BIGINT,
	PRIMARY KEY (guild_id, identifier)
);


CREATE TABLE IF NOT EXISTS webhook_messages (
	identifier VARCHAR(32),
	webhook_url TINYTEXT,
	message_id BIGINT,
	PRIMARY KEY (message_id)
);


CREATE TABLE IF NOT EXISTS fake_permissions (
    guild_id BIGINT,
    role_id BIGINT,
    permission VARCHAR(64),
    PRIMARY KEY (role_id, permission)
);


CREATE TABLE IF NOT EXISTS invoke_message (
    guild_id BIGINT,
    command_name VARCHAR(64),
    message VARCHAR(1024),
    PRIMARY KEY (guild_id, command_name)
);


CREATE TABLE IF NOT EXISTS aliases (
    guild_id BIGINT,
    command_name VARCHAR(64),
    alias VARCHAR(64),
    PRIMARY KEY (guild_id, command_name, alias)
);


CREATE TABLE IF NOT EXISTS muted_user (
    guild_id BIGINT,
    user_id BIGINT,
    unmute_on DATETIME DEFAULT NULL,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS jailed_user (
    guild_id BIGINT,
    user_id BIGINT,
    unjail_on DATETIME DEFAULT NULL,
    PRIMARY KEY (guild_id, user_id)
);


--- Caches ---

CREATE TABLE IF NOT EXISTS image_color_cache (
    image_hash VARCHAR(32),
    color INTEGER NOT NULL,
    PRIMARY KEY (image_hash)
);


CREATE TABLE IF NOT EXISTS audio_track_cache (
    image_hash VARCHAR(32),
    track BLOB NOT NULL,
    PRIMARY KEY (image_hash)
);


CREATE TABLE IF NOT EXISTS artist_image_cache (
    artist_name VARCHAR(255),
    image_hash VARCHAR(32),
    scrape_date BIGINT,
    PRIMARY KEY (artist_name)
);


CREATE TABLE IF NOT EXISTS album_image_cache (
    artist_name VARCHAR(255),
    album_name VARCHAR(255),
    image_hash VARCHAR(32),
    scrape_date BIGINT,
    PRIMARY KEY (artist_name, album_name)
);


CREATE TABLE IF NOT EXISTS marriage (
    first_user_id BIGINT,
    second_user_id BIGINT,
    marriage_date BIGINT,
    PRIMARY KEY (first_user_id, second_user_id)
);


--- Containers ---

CREATE TABLE IF NOT EXISTS container (
		name VARCHAR(10),
		hostname VARCHAR(10),
		address VARCHAR(16),
		customer_id BIGINT,
		customer_name VARCHAR(32),
		created_on DATETIME
)
