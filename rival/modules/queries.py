from modules import exceptions, log

import logging
logger = logging.getLogger(__name__)


async def save_command_usage(ctx):
    await ctx.bot.db.execute(
        """
        INSERT INTO command_usage (guild_id, user_id, command_name, command_type)
            VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            uses = uses + 1
        """,
        ctx.guild.id,
        ctx.author.id,
        ctx.command.qualified_name,
        "internal",
    )


async def update_setting(ctx, table, setting, new_value):
    await ctx.bot.db.execute(
        f"""
        INSERT INTO {table} (guild_id, {setting})
            VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            {setting} = %s
        """,
        ctx.guild.id,
        new_value,
        new_value,
    )


async def is_donator(ctx, user):
    if user==None:
        user=ctx.author
    if user.id in ctx.bot.owner_ids:
        return True

    #user = await ctx.bot.db.execute(
        """
        SELECT FROM dnr
        WHERE user_id = %s
        """,
    #    user.id,)
    #if await ctx.bot.db.execute("""SELECT * FROM dnr WHERE user_id = %s""", user.id):
        #return True
    if user.id in ctx.bot.cache.donators:
        return  True
    #return False

async def owner_donor(ctx, user):
    if user==None:
        user=ctx.author
    if user.id in ctx.bot.owner_ids:
        return True
    if await ctx.bot.db.execute("""SELECT * FROM dnr WHERE user_id = %s""", ctx.guild.owner.id, one_value=True):
        return True


async def is_blacklisted(ctx):
    """Check command invocation context for blacklist triggers."""
    data = await ctx.bot.db.execute(
        """
        SELECT
        EXISTS (
            SELECT user_id FROM blacklisted_user WHERE user_id = %s
        ) AS global,
        EXISTS (
            SELECT guild_id FROM blacklisted_guild WHERE guild_id = %s
        ) AS guild,
        EXISTS (
            SELECT user_id FROM blacklisted_member WHERE user_id = %s AND guild_id = %s
        ) AS user,
        EXISTS (
            SELECT command_name FROM blacklisted_command WHERE command_name = %s AND guild_id = %s
        ) AS command,
        EXISTS (
            SELECT channel_id FROM blacklisted_channel WHERE channel_id = %s
        ) AS channel
        """,
        ctx.author.id,
        ctx.guild.id if ctx.guild is not None else None,
        ctx.author.id,
        ctx.guild.id if ctx.guild is not None else None,
        ctx.command.qualified_name,
        ctx.guild.id if ctx.guild is not None else None,
        ctx.channel.id,
        one_row=True,
    )

    if data[0]:
        raise exceptions.BlacklistedUser()
    if data[1]:
        raise exceptions.BlacklistedGuild()
    if data[2]:
        raise exceptions.BlacklistedMember()
    if data[3]:
        raise exceptions.BlacklistedCommand()
    if data[4]:
        raise exceptions.BlacklistedChannel()

    return True



async def get_filter(db):
    data = await db.execute("SELECT DISTINCT twitter_user_id FROM follow")
    return [str(x[0]) for x in data]


async def get_all_users(db):
    data = await db.execute(
        """
        SELECT DISTINCT username
            FROM follow
            JOIN twitter_user
            ON twitter_user_id=user_id
    """
    )
    return [x[0] for x in data]


async def get_channels(db, twitter_user_id):
    data = await db.execute(
        "SELECT DISTINCT channel_id FROM follow WHERE twitter_user_id = %s", twitter_user_id
    )
    return [x[0] for x in data]


async def unlock_guild(db, guild_id):
    await db.execute(
        "UPDATE guild SET follow_limit = %s WHERE guild_id = %s",
        10,
        guild_id,
    )


async def get_follow_limit(db, guild_id):
    await db.execute(
        "INSERT INTO guild VALUES (%s, %s) ON DUPLICATE KEY UPDATE guild_id = guild_id",
        guild_id,
        20,
    )
    limit = await db.execute(
        "SELECT follow_limit FROM guild WHERE guild_id = %s", guild_id, one_row=True
    )

    current = await db.execute(
        "SELECT COUNT(DISTINCT twitter_user_id) FROM follow WHERE guild_id = %s",
        guild_id,
        one_row=True,
    )
    current = current[0] if current else 0
    return current, limit[0]


async def set_config_guild(db, guild_id, setting, value):
    # just in case, dont allow anything else inside the sql string
    if setting not in ["media_only"]:
        logger.error(f"Ignored configtype {setting} from executing in the database!")
    else:
        await db.execute(
            "INSERT INTO guild_setting(guild_id, " + setting + ") VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE " + setting + " = %s",
            guild_id,
            value,
            value,
        )


async def set_config_channel(db, channel, setting, value):
    # just in case, dont allow anything else inside the sql string
    if setting not in ["media_only"]:
        logger.error(f"Ignored configtype {setting} from executing in the database!")
    else:
        await db.execute(
            "INSERT INTO channel_setting(channel_id, guild_id, "
            + setting
            + ") VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE " + setting + " = %s",
            channel.id,
            channel.guild.id,
            value,
            value,
        )


async def set_config_user(db, guild_id, user_id, setting, value):
    # just in case, dont allow anything else inside the sql string
    if setting not in ["media_only"]:
        logger.error(f"Ignored configtype {setting} from executing in the database!")
    else:
        await db.execute(
            "INSERT INTO user_setting(guild_id, twitter_user_id, "
            + setting
            + ") VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE " + setting + " = %s",
            guild_id,
            user_id,
            value,
            value,
        )


async def tweet_config(db, channel, user_id):
    channel_setting = await db.execute(
        "SELECT media_only FROM channel_setting WHERE channel_id = %s",
        channel.id,
        one_value=True,
    )
    guild_setting = await db.execute(
        "SELECT media_only FROM guild_setting WHERE guild_id = %s",
        channel.guild.id,
        one_value=True,
    )
    user_setting = await db.execute(
        "SELECT media_only FROM user_setting WHERE twitter_user_id = %s AND guild_id = %s",
        user_id,
        channel.guild.id,
        one_value=True,
    )
    config = {}

    if user_setting in (True, False):
        value = user_setting
    elif channel_setting in (True, False):
        value = channel_setting
    elif guild_setting in (True, False):
        value = guild_setting
    else:
        value = False

    config["media_only"] = value

    return config


async def clear_config(db, guild):
    await db.execute("DELETE FROM channel_setting WHERE guild_id = %s", guild.id)
    await db.execute("DELETE FROM user_setting WHERE guild_id = %s", guild.id)
    await db.execute("DELETE FROM guild_setting WHERE guild_id = %s", guild.id)
