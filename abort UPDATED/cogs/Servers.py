from discord.ext import commands  # For Discord
import discord
from utils.embed import to_object, embed_replacement
import re

color = 0x2b2d31


class Servers(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot 



    @commands.group(
        invoke_without_command=True,
        name='vanity',
        description='Award users for advertising your server',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: set /voidbot'
    )
    async def vanity(self, ctx):
        await ctx.send_help(ctx.command)

    @vanity.group(
        name='set',
        description='Set a substring to detect in a status',
        brief='substring',
        usage=
        'Syntax: (substring)\n'
        'Example: /voidbot',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    @commands.has_permissions(manage_guild=True, manage_roles=True)
    async def vanity_set(self, ctx, *, substring: str):
        data = await self.bot.db.execute('SELECT * FROM vanity WHERE guild_id = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO vanity (guild_id, substring) VALUES ($1, $2)', ctx.guild.id, substring)
            await ctx.success(f'Vanity substring set to `{substring}`')
        if data:
            await self.bot.db.execute('UPDATE vanity SET substring = $1 WHERE guild_id = $2', substring, ctx.guild.id)
            await ctx.success(f'Vanity substring updated to `{substring}`')
        if not substring:
            await ctx.send_help(ctx.command)

    # @vanity_set.group(
    #     name='view',
    #     description='View the settings for vanity',
    #     usage='Syntax: ',
    #     aliases=['check']
    # )
    # async def vanity_set_view(self, ctx):
    #     await ctx.send_help(ctx.command)

    @vanity.group(
        invoke_without_command=True,
        name='role',
        description='Award members with a role for advertising your server',
        usage=
        'Syntax: (role)\n'
        'Example: Promoter',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    @commands.has_permissions(manage_guild=True)
    async def vanity_role(self, ctx, role: discord.Role):
        data = await self.bot.db.execute('SELECT * FROM vanity WHERE guild_id = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO vanity (guild_id, role) VALUES ($1, $2)', ctx.guild.id, role.id)
            await ctx.success(f'Vanity role set to {role.mention}')
        if data:
            await self.bot.db.execute('UPDATE vanity SET role = $1 WHERE guild_id = $2', role.id, ctx.guild.id)
            await ctx.success(f'Vanity role updated to {role.mention}')
        if not role:
            await ctx.send_help(ctx.command)

    @vanity.group(
        name='channel',
        description='Set an award channel for advertising members',
        brief='channel',
        usage=
        'Syntax: (channel)\n'
        'Example: #rep',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    async def vanity_channel(self, ctx, channel: discord.TextChannel):
        data = await self.bot.db.execute('SELECT * FROM vanity WHERE guild_id = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO vanity (guild_id, channel) VALUES ($1, $2)', ctx.guild.id, channel.id)
            await ctx.success(f'Vanity award channel set to {channel.mention}')
        if data:
            await self.bot.db.execute('UPDATE vanity SET channel = $1 WHERE guild_id = $2', channel.id, ctx.guild.id)
            await ctx.success(f'Vanity award channel updated to {channel.mention}')
        if not channel:
            await ctx.send_help(ctx.command)

    @vanity.group(
        name='message',
        description='Set an award message for advertising members',
        brief='message',
        usage=
        'Syntax: (message)\n'
        'Example: thanks for repping /voidbot!',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    async def vanity_message(self, ctx, *, message: str):
        data = await self.bot.db.execute('SELECT * FROM vanity WHERE guild_id = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO vanity (guild_id, message) VALUES ($1, $2)', ctx.guild.id, message)
            await ctx.success(f'Vanity message set to `{message}`')
        if data:
            await self.bot.db.execute('UPDATE vanity SET message = $1 WHERE guild_id = $2', message, ctx.guild.id)
            await ctx.success(f'Vanity message updated to `{message}`')
        if not message:
            await ctx.send_help(ctx.command)
            
    @vanity.group(
        name='reset',
        description='Reset all the vanity settings of your guild',
        usage='Syntax: ',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    async def vanity_reset(self, ctx):
        await self.bot.db.execute('DELETE FROM vanity WHERE guild = $1', ctx.guild.id)
        await ctx.success('Vanity configuration has been **reset**')


async def setup(bot):
    await bot.add_cog(Servers(bot))