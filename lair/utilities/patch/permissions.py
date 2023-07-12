from discord.ext.commands._types import Check
from typing import Any
from discord import Permissions
from ..managers import Context
from discord.ext import commands

def has_permissions(**perms: bool) -> Check[Any]:

    async def predicate(ctx: Context):
        if ctx.author.id in ctx.bot.owner_ids:
            return True
        if isinstance(ctx, int):
            return [perm for perm, value in perms.items() if value is True]

        if "guild_owner" in perms:
            if ctx.author.id != ctx.guild.owner.id:
                return commands.CommandError(f'Missing **guild owner** permissions to execute {ctx.command.qualified_name}')
            else:
                return True

        if ctx.author.guild_permissions.administrator:
            return True

        missing = []
        for perm in perms:
            if not getattr(ctx.author.guild_permissions, perm, False):
                missing.append(perm)

            fakeperms = await ctx.bot.redis.lget(f"fakeperms:{ctx.guild.id}")
            if fakeperms:
                for fake in fakeperms:
                    if fake.get("role") in [role.id for role in ctx.author.roles]:
                        try:
                            missing.remove(fake.get('perm'))
                        except ValueError:
                            continue

            if missing:
                raise commands.MissingPermissions(missing)

        return True

    return commands.check(predicate)

commands.has_permissions = has_permissions