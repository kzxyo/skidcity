import discord

from discord.ext import commands


def has_permissions(**permissions):
    """Check if the user has permissions to execute the command (fake permissions included)"""

    async def predicate(ctx: commands.Context):
        if isinstance(ctx, int):
            return [permission for permission, value in permissions.items() if value == True]

        if "guild_owner" in permissions:
            if ctx.author.id != ctx.guild.owner_id:
                raise commands.CommandError(f"You must be the **server owner** to use `{ctx.command.qualified_name}`")
            else:
                return True

        if ctx.author.guild_permissions.administrator:
            return True

        for permission in permissions:
            missing_permissions = []
            if not (getattr(ctx.author.guild_permissions, permission) == True):
                missing_permissions.append(permission)

            if missing_permissions:
                fake_permissions = await ctx.bot.db.fetch(
                    "SELECT * FROM fake_permissions WHERE guild_id = $1 AND permission = ANY($2::text[])",
                    ctx.guild.id,
                    missing_permissions,
                )
                for fake_permission in fake_permissions:
                    if fake_permission["role_id"] in [role.id for role in ctx.author.roles]:
                        try:
                            missing_permissions.remove(fake_permission["permission"])
                        except ValueError:
                            continue

            if missing_permissions:
                raise commands.MissingPermissions(missing_permissions)

        return True

    return commands.check(predicate)


def voicemaster_channel():
    """Check if the channel is a voicemaster channel"""

    async def predicate(ctx: commands.Context, claim: bool = False):
        if not ctx.author.voice:
            raise commands.CommandError("You're not in a **voice channel**")
        if owner_id := await ctx.bot.db.fetchval(
            "SELECT owner_id FROM voicemaster WHERE guild_id = $1 AND channel_id = $2",
            ctx.guild.id,
            ctx.author.voice.channel.id,
        ):
            if claim:
                if ctx.author.id == owner_id:
                    raise commands.CommandError("You're already the **owner** of this **voice channel**")
                return owner_id

            if ctx.author.id != owner_id:
                raise commands.CommandError("You're not the **owner** of this **voice channel**")
        else:
            raise commands.CommandError("You're not in a **VoiceMaster channel**")

        return True

    return commands.check(predicate)


def donator(booster: bool = False):
    """Check if the user is a donator"""

    async def predicate(ctx: commands.Context):
        guild = ctx.bot.get_guild(1004857168761204746)
        role = guild.get_role(1086452534132093041)
        user = guild.get_member(ctx.author.id)

        if booster:
            if not user or not user.premium_since:
                raise commands.CommandError(
                    f"You must **boost** the wock [**Discord Server**](https://discord.gg/wock) to use `{ctx.command.qualified_name}`"
                )

            return True

        if not user or not role in user.roles:
            raise commands.CommandError(
                f"You must be a **donator** to use `{ctx.command.qualified_name}` - [**Discord Server**](https://discord.gg/wock)"
            )

        return True

    return commands.check(predicate)


def require_boost():
    """Check if the user has boosted the server"""

    async def predicate(ctx: commands.Context):
        if not ctx.author.premium_since:
            raise commands.CommandError(f"You must **boost** the server to use `{ctx.command.qualified_name}`")

        return True

    return commands.check(predicate)


def require_dm():
    """Check if the bot can DM the user"""

    async def predicate(ctx: commands.Context):
        try:
            await ctx.author.send()
        except discord.HTTPException as error:
            if error.code == 50007:
                raise commands.CommandError("You need to enable **DMs** to use this command")

        return True

    return commands.check(predicate)


commands.has_permissions = has_permissions
