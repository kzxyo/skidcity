import discord, typing, time, arrow, psutil, copy, aiohttp, random
from datetime import datetime, timedelta
from typing import Optional, Union
from utilities import utils
from utilities.baseclass import Vile
from discord.ext import commands


class AntinukeEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot


    # async def punish(self, action: discord.AuditLogAction, name: str, guild: discord.Guild, reason: str = 'undefined') -> None:

    #     if guild.me.guild_permissions.view_audit_log is True:
    #         if self.bot.cache.antinuke.get(guild.id) is not None:
    #             if self.bot.cache.antinuke[guild.id][name] == True:
    #                 async for entry in guild.audit_logs(limit=1, after=datetime.now() - timedelta(seconds=3), action=action):
    #                     if entry.user.id not in (self.bot.cache.whitelist.get(guild.id, list()) or self.bot.cache.admin.get(guild.id, list())):
    #                         if self.bot.cache.punishment[guild.id] == 'stripstaff':
    #                             try:
    #                                 await entry.user.edit(
    #                                     roles=[role for role in entry.user.roles if role.is_assignable() and not role.is_dangerous()],
    #                                     reason=f'vile antinuke: {reason}'
    #                                 )
    #                             except Exception:
    #                                 pass
    #                             if entry.user.bot:
    #                                 for role in [role for role in entry.user.roles if role.is_assignable() and role.is_bot_managed()]:
    #                                     try:
    #                                         await role.edit(permissions=discord.Permissions(0))
    #                                     except:
    #                                         continue
    #                             return
                                

    #                         if self.bot.cache.punishment[guild.id] == 'striproles':
    #                             await entry.user.edit(
    #                                 roles=[role for role in entry.user.roles if not role.is_assignable()],
    #                                 reason=f'vile antinuke: {reason}'
    #                             )
    #                             if entry.user.bot:
    #                                 for role in [role for role in entry.user.roles if role.is_assignable() and role.is_dangerous()]:
    #                                     await role.edit(permissions=discord.Permissions(0))
    #                             return

    #                         if self.bot.cache.punishment[guild.id] == 'ban':
    #                             return await entry.user.ban(reason=f'vile antinuke: {reason}')

    #                         if self.bot.cache.punishment[guild.id] == 'kick':
    #                             return await entry.user.kick(reason=f'vile antinuke: {reason}')

    
    # @commands.Cog.listener()
    # async def on_member_ban(self, guild: discord.Guild, user: Union[discord.Member, discord.User]):
    #     return await self.punish(discord.AuditLogAction.ban, 'ban', guild, 'anti ban is enabled')


    # @commands.Cog.listener()
    # async def on_member_remove(self, member: discord.Member):
    #     return await self.punish(discord.AuditLogAction.kick, 'kick', member.guild, 'anti kick is enabled')


    # @commands.Cog.listener()
    # async def on_guild_role_create(self, role: discord.Role):
    #     return await self.punish(discord.AuditLogAction.role_create, 'rolecreate', role.guild, 'anti role create is enabled')


    # @commands.Cog.listener()
    # async def on_guild_role_delete(self, role: discord.Role):
    #     return await self.punish(discord.AuditLogAction.role_create, 'roledelete', role.guild, 'anti role delete is enabled')


    # @commands.Cog.listener()
    # async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
    #     return await self.punish(discord.AuditLogAction.channel_create, 'channelcreate', channel.guild, 'anti channel create is enabled')


    # @commands.Cog.listener()
    # async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
    #     return await self.punish(discord.AuditLogAction.channel_delete, 'channeldelete', channel.guild, 'anti channel delete is enabled')


    # @commands.Cog.listener()
    # async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
    #     return await self.punish(discord.AuditLogAction.guild_update, 'webhook', after, 'anti guild update is enabled')


    # @commands.Cog.listener()
    # async def on_webhooks_update(self, channel: discord.abc.GuildChannel):
        
    #     if channel.guild.me.guild_permissions.view_audit_log:
    #         if [log async for log in channel.guild.audit_logs(limit=1, after=datetime.now() - timedelta(seconds=3), action=discord.AuditLogAction.webhook_create)]:
    #             return await self.punish(discord.AuditLogAction.webhook_create, 'webhook', channel.guild, 'anti webhook create is enabled')

    #         if [log async for log in channel.guild.audit_logs(limit=1, after=datetime.now() - timedelta(seconds=3), action=discord.AuditLogAction.webhook_delete)]:
    #             return await self.punish(discord.AuditLogAction.webhook_delete, 'webhook', channel.guild, 'anti webhook delete is enabled')


async def setup(bot: Vile):
    await bot.add_cog(AntinukeEvents(bot))