import discord, difflib, re
from .paginator import Paginator
from .context import Context
from typing import Optional, Union, Iterable, Iterator, Any
from datetime import datetime
from .utils import aiter
from discord.ext import commands


# discord.Role

def is_dangerous(self) -> bool:

    permissions = self.permissions
    return any([
        permissions.kick_members, permissions.ban_members,
        permissions.administrator, permissions.manage_channels,
        permissions.manage_guild, permissions.manage_messages,
        permissions.manage_roles, permissions.manage_webhooks,
        permissions.manage_emojis_and_stickers, permissions.manage_threads,
        permissions.mention_everyone, permissions.moderate_members
    ])


# discord.ext.commands

def has_permissions(**perms: bool) -> Any:

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    async def predicate(ctx: Context) -> bool:
        
        author_roles = list(map(lambda r: r.id, ctx.author.roles))
        permissions = [p[0] for p in ctx.author.guild_permissions if p[1]]
        fake_permissions = list()

        if ctx.bot.cache.fakepermissions.get(ctx.guild.id) is not None:
            fake_permissions = [
                list(p)[0] for p in list(map(
                    lambda r: ctx.bot.cache.fakepermissions[ctx.guild.id][r], 
                    [r for r in ctx.bot.cache.fakepermissions[ctx.guild.id] if r in author_roles]
                ))
            ] 

        for perm, value in perms.items():
            if perm in set(permissions + fake_permissions):
                return True

        raise commands.MissingPermissions([perm])

    return commands.check(predicate)


# discord.Message

def invites(self) -> aiter:
	
    DISCORD_INVITE = r'(?:https?://)?(?:www.:?)?discord(?:(?:app)?.com/invite|.gg)/?[a-zA-Z0-9]+/?'
    DSG = r'(https|http)://(dsc.gg|discord.gg|discord.io|dsc.lol)/?[\S]+/?'

    regex1 = re.compile(DISCORD_INVITE)
    regex2 = re.compile(DSG)

    invites = regex1.findall(self.content)
    invites2 = regex2.findall(self.content)

    return aiter(invites + invites2)