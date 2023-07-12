from typing import Any, Coroutine
import discord
from discord.ext.commands import RoleConverter, RoleNotFound, Converter, MemberConverter, BadArgument, MemberNotFound, CommandError
import re
import datetime

def can_execute_action(
    ctx, user: discord.Member, target: discord.Member
) -> bool:
    return (
        user.id == ctx.bot.owner_id
        or user == ctx.guild.owner
        or user.top_role > target.top_role
    )


class Role(RoleConverter):

    async def convert(self, ctx, argument: str) -> Coroutine[Any, Any, discord.Role]:
        argument = argument.lower()
        
        def role_filter(role):
            return role.name.lower() == argument
        
        role = discord.utils.find(role_filter, ctx.guild.roles)
        
        if not role:
            def role_filter(role):
                return argument in role.name.lower()
            
            role = discord.utils.find(role_filter, ctx.guild.roles)
        
        if not role:
            def role_filter(role):
                return role.name.lower().startswith(argument)
            
            role = discord.utils.find(role_filter, ctx.guild.roles)
        
        if not role or role.is_default():
            raise RoleNotFound(argument)
        
        return role

DISCORD_ID = re.compile(r"(\d+)")
DISCORD_DISCRIMINATOR = re.compile(r"(\d{4})")
DISCORD_USER_MENTION = re.compile(r"<@?(\d+)>")
DISCORD_ROLE_MENTION = re.compile(r"<@&(\d+)>")
DISCORD_CHANNEL_MENTION = re.compile(r"<#(\d+)>")

class cMember(MemberConverter):
    async def convert(self, ctx, argument: str):
        member = None
        argument = str(argument)
        if match := DISCORD_ID.match(argument):
            member = ctx.guild.get_member(int(match.group(1)))
        elif match := DISCORD_USER_MENTION.match(argument):
            member = ctx.guild.get_member(int(match.group(1)))
        else:
            member = (
                discord.utils.find(
                    lambda m: m.name.lower() == argument.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in m.name.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.name.lower().startswith(argument.lower()),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.display_name.lower() == argument.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in m.display_name.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.display_name.lower().startswith(argument.lower()),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: str(m).lower() == argument.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in str(m).lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: str(m).lower().startswith(argument.lower()),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.name.lower() == argument.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in m.name.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.name.lower().startswith(argument.lower()),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.display_name.lower() == argument.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in m.display_name.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.display_name.lower().startswith(argument.lower()),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: str(m).lower() == argument.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in str(m).lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: str(m).lower().startswith(argument.lower()),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
            )
        if not member:
            raise MemberNotFound(argument)
        return member

class DurationConverter(Converter):
    async def convert(self, ctx, argument: str):
        match = re.match(r"(\d+)\s*(\w+)", argument)
        if not match:
            raise BadArgument(
                "Invalid duration format. Please provide a valid duration, e.g. '1d' or '2h'."
            )

        amount = int(match.group(1))
        unit = match.group(2).lower()

        now = datetime.datetime.now()

        if unit in ("s", "sec", "secs", "second", "seconds"):
            return now + datetime.timedelta(seconds=amount)
        elif unit in ("m", "min", "mins", "minute", "minutes"):
            return now + datetime.timedelta(minutes=amount)
        elif unit in ("h", "hr", "hrs", "hour", "hours"):
            return now + datetime.timedelta(hours=amount)
        elif unit in ("d", "day", "days"):
            return now + datetime.timedelta(days=amount)
        elif unit in ("w", "week", "weeks"):
            return now + datetime.timedelta(weeks=amount)
        elif unit in ("mo", "month", "months"):
            return now + datetime.timedelta(days=30 * amount)
        elif unit in ("y", "year", "years"):
            return now + datetime.timedelta(days=365 * amount)

        raise BadArgument(
            "Invalid duration unit. Please provide a valid unit, e.g. 's' or 'day'."
        )
    

class CollageSize(Converter):
    async def convert(self, ctx, argument: str):
        argument = str(argument)
        if not "x" in argument:
            raise CommandError("Incorrect collage size. Example Format: **3x3**")
        if not len(argument.split("x")) == 2:
            raise CommandError("Incorrect collage size. Example Format: **3x3**")
        row, col = argument.split("x")
        if not row.isdigit() or not col.isdigit():
            raise CommandError("Incorrect collage size. Example Format: **3x3**")
        if (int(row) + int(col)) < 2:
            raise CommandError("Minimum collage size is **1x1**")
        elif (int(row) + int(col)) > 20:
            raise CommandError("Maximum collage size is **10x10**")

        return row + "x" + col
    
class Reason(Converter):
    async def convert(self, ctx, argument: str):
        ret = f"{ctx.author} (ID: {ctx.author.id}): {argument}"

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise BadArgument(
                f"Reason is too long ({len(argument)}/{reason_max})"
            )
        return ret
    
class FetchBannedUser(Converter):
    async def convert(self, ctx, argument: str):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise BadArgument(
                    "This member does not have previous ban records."
                ) from None

        entity = await discord.utils.find(
            lambda u: str(u.user) == argument, ctx.guild.bans(limit=None)
        )

        if entity is None:
            raise BadArgument(
                "This member does not have previous ban records."
            )
        return entity
    
class Roles(RoleConverter):
    async def convert(self, ctx, argument: str):
        roles = []
        argument = str(argument)
        for role in argument.split(","):
            try:
                role = await Role().convert(ctx, role.strip())
                if role not in roles:
                    roles.append(role)
            except RoleNotFound:
                continue

        if not roles:
            raise RoleNotFound(argument)
        return roles