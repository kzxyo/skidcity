from discord.ext import commands

from helpers import wock


bot = wock.wockSuper()


# @bot.check
# async def permission_check(ctx: wock.Context):
#     """Check if the bot has permissions before invoking"""

#     if not hasattr(ctx.bot, "debug"):
#         setattr(ctx.bot, "debug", False)

#     if ctx.bot.debug == True and not ctx.guild.id == 1004857168761204746:
#         return False

#     if (
#         not ctx.guild.me.guild_permissions.send_messages
#         or not ctx.guild.me.guild_permissions.embed_links
#         or not ctx.guild.me.guild_permissions.read_message_history
#     ):
#         with contextlib.suppress(discord.HTTPException):
#             await ctx.guild.leave()

#     # if not ctx.guild.me.guild_permissions.administrator:
#     #     raise commands.CommandError(
#     #         "Please grant me the **Administrator** permission\n> Practically all commands require some sort of **permission**"
#     #     )

#     return True


@bot.check
async def disabled_check(ctx: wock.Context):
    """Checks if the command is disabled in the channel"""

    if not ctx.author.guild_permissions.administrator:
        if parent := ctx.command.parent:
            if await ctx.bot.db.fetchrow(
                "SELECT * FROM commands.ignored WHERE guild_id = $1 AND target_id = ANY($2::BIGINT[])",
                ctx.guild.id,
                [
                    ctx.author.id,
                    ctx.channel.id,
                ],
            ):
                return False
            elif await ctx.bot.db.fetchrow(
                "SELECT * FROM commands.disabled WHERE guild_id = $1 AND channel_id = $2 AND command = $3",
                ctx.guild.id,
                ctx.channel.id,
                parent.qualified_name,
            ):
                raise commands.CommandError(f"Command `{ctx.command.qualified_name}` is disabled in {ctx.channel.mention}")
            elif await ctx.bot.db.fetchrow(
                "SELECT * FROM commands.restricted WHERE guild_id = $1 AND command = $2 AND NOT role_id = ANY($3::BIGINT[])",
                ctx.guild.id,
                parent.qualified_name,
                [role.id for role in ctx.author.roles],
            ):
                raise commands.CommandError(f"You don't have a **permitted role** to use `{parent.qualified_name}`")

        if await ctx.bot.db.fetchrow(
            "SELECT * FROM commands.ignored WHERE guild_id = $1 AND target_id = ANY($2::BIGINT[])",
            ctx.guild.id,
            [
                ctx.author.id,
                ctx.channel.id,
            ],
        ):
            return False
        elif await ctx.bot.db.fetchrow(
            "SELECT * FROM commands.disabled WHERE guild_id = $1 AND channel_id = $2 AND command = $3",
            ctx.guild.id,
            ctx.channel.id,
            ctx.command.qualified_name,
        ):
            raise commands.CommandError(f"Command `{ctx.command.qualified_name}` is disabled in {ctx.channel.mention}")
        elif await ctx.bot.db.fetchrow(
            "SELECT * FROM commands.restricted WHERE guild_id = $1 AND command = $2 AND NOT role_id = ANY($3::BIGINT[])",
            ctx.guild.id,
            ctx.command.qualified_name,
            [role.id for role in ctx.author.roles],
        ):
            raise commands.CommandError(f"You don't have a **permitted role** to use `{ctx.command.qualified_name}`")

    return True


@bot.check
async def blacklist_check(ctx: wock.Context):
    """Checks if the author is blacklisted"""

    if await ctx.bot.db.fetchrow("SELECT * FROM blacklist WHERE user_id = $1", ctx.author.id):
        return False

    return True


@bot.check
async def developer_check(ctx: wock.Context):
    """Check if the author of the command is a developer"""

    if ctx.command.qualified_name in ("jishaku shell", "jishaku py", "jishaku cat", "jishaku debug"):
        if not ctx.author.id == 1004836998151950358:
            return False

    if ctx.command.hidden:
        if not await ctx.bot.is_owner(ctx.author):
            return False

    return True


bot.run(token=bot.config.get("token"), reconnect=True)
