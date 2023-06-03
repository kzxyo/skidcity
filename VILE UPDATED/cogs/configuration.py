import discord, typing, time, arrow, psutil, copy, aiohttp, unicodedata, json
from datetime import datetime
from typing import Optional, Union
from utilities import utils
from utilities.baseclass import Vile
from utilities.advancedutils import parse_timespan
from utilities.context import Context
from discord.ext import commands, tasks


class Configuration(commands.Cog):
    def __init__(self, bot: Vile) -> None:
        self.bot = bot


    @commands.hybrid_group(
        name='guildprefix',
        aliases=['serverprefix', 'sp'],
        description="set up this server's custom prefix",
        syntax='!guildprefix <sub command>',
        help='guildprefix set ;',
        invoke_without_command=True
    )
    async def guildprefix(self, ctx: Context):

        return await ctx.send_help()

    @guildprefix.command(
        name='set',
        aliases=['add'],
        description="set this server's custom prefix",
        brief='guildprefix set <prefix>',
        help='guildprefix set ;'
    )
    async def guildprefix_set(self, ctx: Context, prefix: str):

        if len(prefix) > 5:
            return await ctx.send_error('please provide a **valid** prefix under 5 characters')

        if prefix == await self.bot.db.fetchval('SELECT prefix FROM guildprefix WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error(f"this server's prefix is already set to **`{prefix}`**")

        await self.bot.db.execute('INSERT INTO guildprefix (guild_id, prefix) VALUES (%s, %s) ON DUPLICATE KEY UPDATE prefix = VALUES(prefix)', ctx.guild.id, prefix)
        self.bot.cache.guildprefixes[ctx.guild.id] = prefix

        return await ctx.send_success(f"successfully **binded** the server's prefix to `{prefix}`")


    @guildprefix.command(
        name='delete',
        aliases=['del', 'remove'],
        description='delete your server prefix'
    )
    async def guildprefix_delete(self, ctx: Context):

        if not await self.bot.db.fetchval('SELECT prefix FROM guildprefix WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("this server doesnt have a custom prefix")

        await self.bot.db.execute('DELETE FROM guildprefix WHERE guild_id = %s', ctx.guild.id)
        self.bot.cache.guildprefixes.pop(ctx.guild.id)

        return await ctx.send_success("successfully **removed** the server's prefix")


    @commands.hybrid_group(
        name='customprefix',
        aliases=['prefix', 'cp', 'selfprefix'],
        description='set up your own custom prefix',
        syntax='!customprefix <sub command>',
        help='custmprefix set ;',
        invoke_without_command=True
    )
    async def customprefix(self, ctx: Context):

        return await ctx.send_help()

    @customprefix.command(
        name='set',
        aliases=['add'],
        description='set your custom prefix',
        brief='customprefix set <prefix>',
        help='customprefix set ;'
    )
    async def customprefix_set(self, ctx: Context, prefix: str):

        if len(prefix) > 10:
            return await ctx.send_error('please provide a **valid** prefix under 10 characters')

        if prefix == await self.bot.db.fetchval('SELECT prefix FROM customprefix WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error(f'your prefix is already set to **`{prefix}`**')

        await self.bot.db.execute('INSERT INTO customprefix (user_id, prefix) VALUES (%s, %s) ON DUPLICATE KEY UPDATE prefix = VALUES(prefix)', ctx.author.id, prefix)
        self.bot.cache.customprefixes[ctx.author.id] = prefix

        return await ctx.send_success(f'successfully **binded** your prefix to `{prefix}`')


    @customprefix.command(
        name='delete',
        aliases=['del', 'remove'],
        description='delete your custom prefix'
    )
    async def customprefix_delete(self, ctx: Context):

        if not await self.bot.db.fetchval('SELECT prefix FROM customprefix WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you don't have a custom prefix")

        await self.bot.db.execute('DELETE FROM customprefix WHERE user_id = %s', ctx.author.id)
        self.bot.cache.customprefixes.pop(ctx.author.id)

        return await ctx.send_success('successfully **removed** your prefix')


    @commands.group(
        name='set',
        description='update the server',
        brief='set <sub command>',
        help='set icon ...',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx: Context): 
        return await ctx.send_help()


    @_set.command(
        name='icon',
        description='update the server icon',
        brief='set icon <link or attachment>',
        help='set icon ...',
        extras={'permissions': 'manage guild'}
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def set_icon(self, ctx: Context, image: Optional[str] = None): 

        if image is None:
            if not ctx.message.attachments:
                return await ctx.send_help()
            
            image = ctx.message.attachments[0].url


        await ctx.guild.edit(icon=await self.bot.session.read(image, proxy=True), reason=f'seticon: used by {ctx.author}')
        return await ctx.send_success('successfully **updated** the server icon')


    @_set.command(
        name='banner',
        description='update the server banner',
        brief='set banner <link or attachment>',
        help='set banner ...',
        extras={'permissions': 'manage guild'}
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def set_banner(self, ctx: Context, image: Union[discord.Attachment, str]): 
        
        if image is None:
            if not ctx.message.attachments:
                return await ctx.send_help()
            
            image = ctx.message.attachments[0].url

        if ctx.guild.premium_tier < 2:
            return await ctx.send_error("this server doesn't have the boost requirements for a banner")
            
        await ctx.guild.edit(banner=await self.bot.session.read(image, proxy=True), reason=f'setbanner: used by {ctx.author}')
        return await ctx.send_success('successfully **updated** the server banner')


    @_set.command(
        name='splash',
        description='update the server splash',
        brief='set splash <link or attachment>',
        help='set splash ...',
        extras={'permissions': 'manage guild'}
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def set_splash(self, ctx: Context, image: Union[discord.Attachment, str]): 
        
        if image is None:
            if not ctx.message.attachments:
                return await ctx.send_help()
            
            image = ctx.message.attachments[0].url

        if ctx.guild.premium_tier < 1:
            return await ctx.send_error("this server doesn't have the boost requirements for a splash")
            
        await ctx.guild.edit(splash=await self.bot.session.read(image, proxy=True), reason=f'setsplash: used by {ctx.author}')
        return await ctx.send_success('successfully **updated** the server splash')


    @commands.command(
        name='seticon',
        description="set the server's icon",
        brief='seticon <link or attachment>',
        help='seticon ...',
        extras={'permissions': 'manage guild'}
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def seticon(self, ctx: Context, image: Optional[str] = None):
        return await ctx.invoke(self.bot.get_command('set icon'), image=image)


    @commands.command(
        name='setbanner',
        description="set the server's banner",
        brief='setbanner <link or attachment>',
        help='setbanner ...',
        extras={'permissions': 'manage guild'}
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def setbanner(self, ctx: Context, image: Optional[str] = None):
        return await ctx.invoke(self.bot.get_command('set banner'), image=image)


    @commands.command(
        name='setsplash',
        description="set the server's splash",
        brief='setsplash <link or attachment>',
        help='setsplash ...',
        extras={'permissions': 'manage guild'}
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def setsplash(self, ctx: Context, image: Optional[str] = None):
        return await ctx.invoke(self.bot.get_command('set splash'), image=image)


    @commands.group(
        name='chatfilter',
        aliases=['cf', 'filter'],
        description="manage the server's chat filters",
        brief='chatfilter <sub command>',
        help='chatfilter add nig*',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def chatfilter(self, ctx: Context):

        return await ctx.send_help()
    
    @chatfilter.command(
        name='add',
        aliases=['create'],
        description='add a new chat filter',
        brief='chatfilter add <trigger>',
        help='chatfilter add nig*',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def chatfilter_add(self, ctx: Context, trigger: str):
        
        if await self.bot.db.fetchrow('SELECT * FROM chatfilter WHERE guild_id = %s AND strr = %s', ctx.guild.id, trigger):
            return await ctx.send_error('a chat filter with that trigger **already exists**')
            
        await self.bot.db.execute('INSERT INTO chatfilter (guild_id, strr) VALUES (%s, %s)', ctx.guild.id, trigger)

        self.bot.cache.chatfilter.setdefault(ctx.guild.id, set()).add(trigger)
        return await ctx.send_success(f'successfully **added** filter with the trigger **`{trigger}`**')
        
    @chatfilter.command(
        name='remove',
        aliases=['delete'],
        description='remove a chat filter',
        brief='chatfilter remove <trigger>',
        help='chatfilter remove nig*',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def chatfilter_remove(self, ctx: Context, trigger: str):
        
        if not await self.bot.db.fetchrow('SELECT * FROM chatfilter WHERE guild_id = %s AND strr = %s', ctx.guild.id, trigger):
            return await ctx.send_error('a filter with that trigger **does not exist**')
            
        await self.bot.db.execute('DELETE FROM chatfilter WHERE guild_id = %s AND strr = %s', ctx.guild.id, trigger)

        self.bot.cache.chatfilter.setdefault(ctx.guild.id, set()).discard(trigger)
        return await ctx.send_success(f'successfully **removed** filter with the trigger **`{trigger}`**')
        
    @chatfilter.command(
        name='clear',
        aliases=['c'],
        description='clear all the chat filters',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def chatfilter_clear(self, ctx: Context):
            
        await self.bot.db.execute('DELETE FROM chatfilter WHERE guild_id = %s', ctx.guild.id)
        self.bot.cache.chatfilter[ctx.guild.id] = list()
        return await ctx.send_success('successfully **cleared** all filters')
        
    @chatfilter.command(
        name='list',
        aliases=['show'],
        description='show all the chat filters',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def chatfilter_list(self, ctx: Context):
        
        if not await self.bot.db.fetch('SELECT strr FROM chatfilter WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **chat filters** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Chat filters in {ctx.guild.name}',
            description=list()
        )
        for trig in set(await self.bot.db.fetch('SELECT strr FROM chatfilter WHERE guild_id = %s', ctx.guild.id)):
            embed.description.append(f'**{trig}**')
            
        return await ctx.paginate(embed)


    @commands.group(
        name='settings',
        aliases=['config'],
        description='manage the bot settings',
        brief='settings <sub command>',
        help='settings googlesafe true',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx: Context):

        return await ctx.send_help()

    
    @settings.command(
        name='googlesafe',
        aliases=['safesearch', 'gs', 'ss'],
        description='toggle safesearch for google image searching',
        brief='settings googlesafe <state>',
        help='settings googlesafe true',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def settings_googlesafe(self, ctx: Context, state: str):
    
        if state == 'true':
            await self.bot.db.execute(
                'INSERT INTO safesearch (guild_id, state) VALUES (%s, 1) ON DUPLICATE KEY UPDATE state = 1',
                ctx.guild.id
            )
            return await ctx.send_success('successfully **enabled** google safe search')
        elif state == 'false':
            await self.bot.db.execute(
                'INSERT INTO safesearch (guild_id, state) VALUES (%s, 0) ON DUPLICATE KEY UPDATE state = 0',
                ctx.guild.id
            )
            return await ctx.send_success('successfully **disabled** google safe search')
        else:
            return await ctx.send_error('please provide a **valid** state')


    @settings.command(
        name='tiktok',
        aliases=['tiktokreposting', 'tiktokembedding', 'tt'],
        description='toggle tiktok embedding in this server',
        brief='settings tiktok <state>',
        help='settings tiktok false',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def settings_tiktok(self, ctx: Context, state: str):
    
        if state == 'true':
            await self.bot.db.execute(
                'INSERT INTO tiktok_reposting (guild_id, state) VALUES (%s, 1) ON DUPLICATE KEY UPDATE state = 1',
                ctx.guild.id
            )
            self.bot.cache.tiktok_reposting[ctx.guild.id] = 1
            return await ctx.send_success('successfully **enabled** tiktok reposting')
        elif state == 'false':
            await self.bot.db.execute(
                'INSERT INTO tiktok_reposting (guild_id, state) VALUES (%s, 0) ON DUPLICATE KEY UPDATE state = 0',
                ctx.guild.id
            )
            self.bot.cache.tiktok_reposting[ctx.guild.id] = 0
            return await ctx.send_success('successfully **disabled** tiktok reposting')
        else:
            return await ctx.send_error('please provide a **valid** state')


    @settings.command(
        name='youtube',
        aliases=['youtubereposting', 'youtubeembedding', 'yt'],
        description='toggle youtube embedding in this server',
        brief='settings youtube <state>',
        help='settings youtube false',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def settings_youtube(self, ctx: Context, state: str):
    
        if state == 'true':
            await self.bot.db.execute(
                'INSERT INTO youtube_reposting (guild_id, state) VALUES (%s, 1) ON DUPLICATE KEY UPDATE state = 1',
                ctx.guild.id
            )
            self.bot.cache.youtube_reposting[ctx.guild.id] = 1
            return await ctx.send_success('successfully **enabled** youtube reposting')
        elif state == 'false':
            await self.bot.db.execute(
                'INSERT INTO youtube_reposting (guild_id, state) VALUES (%s, 0) ON DUPLICATE KEY UPDATE state = 0',
                ctx.guild.id
            )
            self.bot.cache.youtube_reposting[ctx.guild.id] = 0
            return await ctx.send_success('successfully **disabled** youtube reposting')
        else:
            return await ctx.send_error('please provide a **valid** state')


    @settings.command(
        name='levels',
        aliases=['leveling'],
        description='toggle leveling in this server',
        brief='settings leveling <state>',
        help='settings leveling false',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def settings_levels(self, ctx: Context, state: str):
    
        if state == 'true':
            await self.bot.db.execute(
                'INSERT INTO level_settings (guild_id, state, message) VALUES (%s, 1, 1) ON DUPLICATE KEY UPDATE state = 1',
                ctx.guild.id
            )
                
            self.bot.cache.leveling[ctx.guild.id] = {'state': 1, 'message': 1}
            return await ctx.send_success('successfully **enabled** leveling in this server')
        elif state == 'false':
            await self.bot.db.execute(
                'INSERT INTO level_settings (guild_id, state, message) VALUES (%s, 0, 1) ON DUPLICATE KEY UPDATE state = 0',
                ctx.guild.id
            )
                
            self.bot.cache.leveling[ctx.guild.id] = {'state': 0, 'message': 1}
            return await ctx.send_success('successfully **disabled** leveling in this server')
        else:
            return await ctx.send_error('please provide a **valid** state')


    # @settings.command(
    #     name='modconfirmations',
    #     aliases=['modconf', 'modconfirm', 'mc'],
    #     description='toggle confirmation for mod commands',
    #     brief='settings !modconfirmations <state>',
    #     help='settings modconfirmations true'
    # )
    # @commands.has_permissions(manage_guild=True)
    # async def settings_modconfirmations(self, ctx: Context, state: str):
            
    #     if state == 'true':
    #         await self.bot.db.execute('INSERT INTO mod_confirmations (guild_id, state) VALUES (%s, 1) ON DUPLICATE KEY UPDATE state = 1', ctx.guild.id)
    #         await ctx.send_success('successfully **enabled** moderation command confirmations')

    #     elif state == 'false':
    #         await self.bot.db.execute('INSERT INTO mod_confirmations (guild_id, state) VALUES (%s, 0) ON DUPLICATE KEY UPDATE state = 0', ctx.guild.id)
    #         await ctx.send_success('successfully **enabled** moderation command confirmations')
    #     else:
    #         return await ctx.send_error('please provide a **valid** state')


    @settings.command(
        name='moddms',
        aliases=['mdms', 'mdm'],
        description='toggle dms for mod commands',
        brief='settings moddms <state>',
        help='settings moddms true',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def settings_moddms(self, ctx: Context, state: str):
            
        if state == 'true':
            await self.bot.db.execute('INSERT INTO mod_dms (guild_id, state) VALUES (%s, 1) ON DUPLICATE KEY UPDATE state = 1', ctx.guild.id)
            await ctx.send_success('successfully **enabled** moderation command dms')

        elif state == 'false':
            await self.bot.db.execute('INSERT INTO mod_dms (guild_id, state) VALUES (%s, 0) ON DUPLICATE KEY UPDATE state = 0', ctx.guild.id)
            await ctx.send_success('successfully **enabled** moderation command dms')
        else:
            return await ctx.send_error('please provide a **valid** state')

    
    @settings.command(
        name='banmessage',
        aliases=['banmsg', 'bm'],
        description='set your own custom ban message',
        brief='settings banmessage <message>',
        help='settings banmessage {content: :VilePack:}',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def settings_banmessage(self, ctx: Context, *, message: str):

        await self.bot.db.execute('INSERT INTO ban_message (guild_id, message) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message)', ctx.guild.id, message)
        return await ctx.send_success(f'successfully **binded** the custom ban message to:\n\n```{message}```')


    @settings.command(
        name='disable',
        aliases=['dis'],
        description='disable commands in this server',
        brief='settings disable <command>',
        help='settings disable ban',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def settings_disable(self, ctx: Context, *, command: str):

        if self.bot.get_command(command) is None:
            return await ctx.send_error('please provide a **valid** command')
        
        command = self.bot.get_command(command).name

        if command in ['settings enable', 'settings disable', 'enable', 'disable']:
            return await ctx.send_error("you can't **disable** this command")

        if command in set(await self.bot.db.fetch('SELECT command FROM disabled_commands WHERE guild_id = %s', ctx.guild.id)):
            return await ctx.send_error('that command is already **disabled**')

        await self.bot.db.execute('INSERT INTO disabled_commands (guild_id, command) VALUES (%s, %s)', ctx.guild.id, command)
        if ctx.guild.id not in self.bot.cache.disabled_commands:
            self.bot.cache.disabled_commands[ctx.guild.id] = list()

        self.bot.cache.disabled_commands[ctx.guild.id].append(command)
        return await ctx.send_success(f'successfully **disabled** the command `{command}`')


    @settings.command(
        name='enable',
        aliases=['en'],
        description='enable commands in this server',
        brief='settings enable <command>',
        help='settings enable ban',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def settings_enable(self, ctx: Context, *, command: str):

        if self.bot.get_command(command) is None:
            return await ctx.send_error('please provide a **valid** command')
        
        command = self.bot.get_command(command).name
        if command not in set(await self.bot.db.fetch('SELECT command FROM disabled_commands WHERE guild_id = %s', ctx.guild.id)):
            return await ctx.send_error('that command is already **enabled**')

        await self.bot.db.execute('DELETE FROM disabled_commands WHERE guild_id = %s AND command = %s', ctx.guild.id, command)

        self.bot.cache.disabled_commands[ctx.guild.id].remove(command)
        return await ctx.send_success(f'successfully **enabled** the command `{command}`')


    @commands.command(
        name='googlesafe',
        aliases=['safesearch', 'gs'],
        description='toggle safesearch for google image searching',
        brief='settings googlesafe <state>',
        help='settings googlesafe true',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def googlesafe(self, ctx: Context, state: str):
        return await ctx.invoke(self.bot.get_command('settings googlesafe'), state)


    @commands.command(
        name='tiktok',
        aliases=['tiktokreposting', 'tiktokembedding'],
        description='toggle tiktok embedding in this server',
        brief='settings tiktok <state>',
        help='settings tiktok false',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def tiktok(self, ctx: Context, state: str):
        return await ctx.invoke(self.bot.get_command('settings tiktok'), state)


    @commands.command(
        name='levels',
        aliases=['leveling'],
        description='toggle leveling in this server',
        brief='settings leveling <state>',
        help='settings leveling false',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def levels(self, ctx: Context, state: str):
        return await ctx.invoke(self.bot.get_command('settings levels'), state)


    @commands.command(
        name='moddms',
        aliases=['mdms', 'mdm'],
        description='toggle dms for mod commands',
        brief='settings moddms <state>',
        help='settings moddms true',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def moddms(self, ctx: Context, state: str):
        return await ctx.invoke(self.bot.get_command('settings moddms'), state)

    
    @commands.command(
        name='banmessage',
        aliases=['banmsg', 'bm'],
        description='set your own custom ban message',
        brief='settings banmessage <message>',
        help='settings banmessage {content: :VilePack:}',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def banmessage(self, ctx: Context, *, message: str):
        return await ctx.invoke(self.bot.get_command('settings banmessage'), message)


    @commands.command(
        name='disable',
        aliases=['dis'],
        description='disable commands in this server',
        brief='settings disable <command>',
        help='settings disable ban',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx: Context, *, command: str):
        return await ctx.invoke(self.bot.get_command('settings disable'), command=command)


    @commands.command(
        name='enable',
        aliases=['en'],
        description='enable commands in this server',
        brief='settings enable <command>',
        help='settings enable ban',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx: Context, *, command: str):
        return await ctx.invoke(self.bot.get_command('settings enable'), command=command)


    @commands.group(
        name='imageonly',
        aliases=['imgonly', 'io', 'mo', 'mediaonly'],
        description="manage the server's media-only channels",
        brief='imageonly <sub command>',
        help='imageonly add #images',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def imageonly(self, ctx: Context):

        return await ctx.send_help()
    
    @imageonly.command(
        name='add',
        aliases=['create'],
        description='add a new media-only channel',
        brief='imageonly add <channel>',
        help='imageonly add #images',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def imageonly_add(self, ctx: Context, channel: discord.TextChannel):
        
        if await self.bot.db.fetchrow('SELECT * FROM image_only WHERE guild_id = %s AND channel_id = %s', ctx.guild.id, channel.id):
            return await ctx.send_error('image-only is already enabled in that channel')
            
        await self.bot.db.execute('INSERT INTO image_only (guild_id, channel_id) VALUES (%s, %s)', ctx.guild.id, channel.id)

        self.bot.cache.image_only.setdefault(ctx.guild.id, list()).append(channel.id)
        return await ctx.send_success(f'successfully **binded** #{channel.name} as a media-only channel')
        
    @imageonly.command(
        name='remove',
        aliases=['delete'],
        description='remove a media-only channel',
        brief='imageonly remove <channel>',
        help='imageonly remove #images',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def imageonly_remove(self, ctx: Context, channel: discord.TextChannel):
        
        if not await self.bot.db.fetchrow('SELECT * FROM image_only WHERE guild_id = %s AND channel_id = %s', ctx.guild.id, channel.id):
            return await ctx.send_error('image-only is not enabled in that channel')
            
        await self.bot.db.execute('DELETE FROM image_only WHERE guild_id = %s AND channel_id = %s', ctx.guild.id, channel.id)

        try:
            self.bot.cache.image_only.setdefault(ctx.guild.id, list()).remove(channel.id)
        except:
            pass
        return await ctx.send_success(f'successfully **unbinded** #{channel.name} as a media-only channel')
        
    @imageonly.command(
        name='clear',
        aliases=['c'],
        description='clear all the media-only channels',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def imageonly_clear(self, ctx: Context):
            
        await self.bot.db.execute('DELETE FROM image_only WHERE guild_id = %s', ctx.guild.id)
        self.bot.cache.image_only[ctx.guild.id] = list()
        return await ctx.send_success('successfully **cleared** all media-only channels')
        
    @imageonly.command(
        name='list',
        aliases=['show'],
        description='show all the image-only channels',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def imageonly_list(self, ctx: Context):
        
        if not await self.bot.db.fetch('SELECT channel_id FROM image_only WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **media-only channels** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Media-only channels in {ctx.guild.name}',
            description=list()
        )
        for channel_id in set(await self.bot.db.fetch('SELECT channel_id FROM image_only WHERE guild_id = %s', ctx.guild.id)):
            if ctx.guild.get_channel(channel_id) is not None:
                embed.description.append(f'{ctx.guild.get_channel(channel_id).mention} ( `{channel_id}` )')
            
        return await ctx.paginate(embed)


    @commands.group(
        name='boost',
        aliases=['bst'],
        description='manage the boost module for the server',
        brief='boost <sub command>',
        help='boost channel #boosts',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def boost(self, ctx: Context):

        return await ctx.send_help()

    
    @boost.command(
        name='channel',
        aliases=['ch', 'chnnl'],
        description='set the boost channel',
        brief='boost channel <channel>',
        help='boost channel #boosts',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_channel(self, ctx: Context, *, channel: discord.TextChannel):

        await self.bot.db.execute('INSERT INTO boost_channel (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)', ctx.guild.id, channel.id)
        self.bot.cache.boostchannel[ctx.guild.id] = channel.id
        
        return await ctx.send_success(f'successfully **binded** #{channel.name} as the boost channel')


    @boost.command(
        name='message',
        aliases=['msg'],
        description='set the boost message',
        brief='boost message <text>',
        help='boost message {content: {user.mention} thank you for boosting}',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_message(self, ctx: Context, *, message: str):

        await self.bot.db.execute('INSERT INTO boost_message (guild_id, message) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message)', ctx.guild.id, message)
        self.bot.cache.boostmessage[ctx.guild.id] = message
        
        return await ctx.send_success(f'successfully **binded** the boost message to:\n\n```{message}```')


    @boost.command(
        name='clear',
        aliases=['c'],
        description='clear the boost configuration',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM boost_channel WHERE guild_id = %s', ctx.guild.id)
        await self.bot.db.execute('DELETE FROM boost_message WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.boostmessage.pop(ctx.guild.id)
        except:
            pass
        try:
            self.bot.cache.boostchannel.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f'successfully **cleared** the boost configuration')


    @boost.command(
        name='test',
        aliases=['t'],
        description='test the boost message',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_test(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM boost_channel WHERE guild_id = %s', ctx.guild.id) or not await self.bot.db.fetchrow('SELECT * FROM boost_message WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the boost module is not **set up** in this server')

        self.bot.dispatch('boost', ctx.author)
        return await ctx.send_success('successfully **dispatched** the boost message')


    @boost.command(
        name='settings',
        aliases=['conf', 'config', 'cfg', 'configuration'],
        description="view the server's current boost configuration",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_settings(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM boost_channel WHERE guild_id = %s', ctx.guild.id) or not await self.bot.db.fetchrow('SELECT * FROM boost_message WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the boost module is not **set up** in this server')

        channel, message = (await self.bot.db.fetchval('SELECT channel_id FROM boost_channel WHERE guild_id = %s', ctx.guild.id), await self.bot.db.fetchval('SELECT message FROM boost_message WHERE guild_id = %s', ctx.guild.id))

        embed = discord.Embed(
            color=self.bot.color,
            title='Boost Configuration',
            timestamp=datetime.now()
        )    
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar
        )
        embed.add_field(
            name=f'{self.bot.dash} Channel',
            value=ctx.guild.get_channel(channel).mention
        )
        embed.add_field(
            name=f'{self.bot.dash} Message',
            value=f'```{message}```',
            inline=False
        )
        
        return await ctx.reply(embed=embed)


    @commands.group(
        name='welcome',
        aliases=['wlc', 'welc'],
        description='manage the welcome module for the server',
        brief='welcome <sub command>',
        help='welcome channel #joins',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx: Context):
        return await ctx.send_help()

    
    @welcome.command(
        name='channel',
        aliases=['ch', 'chnnl'],
        description='set the welcome channel',
        brief='welcome channel <channel>',
        help='welcome channel #joins',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_channel(self, ctx: Context, *, channel: discord.TextChannel):

        await self.bot.db.execute('INSERT INTO welcome_channel (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)', ctx.guild.id, channel.id)
        self.bot.cache.welcomechannel[ctx.guild.id] = channel.id
        
        return await ctx.send_success(f'successfully **binded** #{channel.name} as the welcome channel')


    @welcome.command(
        name='message',
        aliases=['msg'],
        description='set the welcome message',
        brief='welcome message <text>',
        help="welcome message {content: {user.mention} welcome to {guild.name}, you're the {guild.count.format} member}",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(self, ctx: Context, *, message: str):

        await self.bot.db.execute('INSERT INTO welcome_message (guild_id, message) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message)', ctx.guild.id, message)
        self.bot.cache.welcomemessage[ctx.guild.id] = message
        
        return await ctx.send_success(f'successfully **binded** the welcome message to:\n\n```{message}```')


    @welcome.command(
        name='clear',
        aliases=['c'],
        description='clear the welcome configuration',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM welcome_channel WHERE guild_id = %s', ctx.guild.id)
        await self.bot.db.execute('DELETE FROM welcome_message WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.welcomemessage.pop(ctx.guild.id)
        except:
            pass
        try:
            self.bot.cache.welcomechannel.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f'successfully **cleared** the welcome configuration')


    @welcome.command(
        name='test',
        aliases=['t'],
        description='test the welcome message',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_test(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM welcome_channel WHERE guild_id = %s', ctx.guild.id) or not await self.bot.db.fetchrow('SELECT * FROM welcome_message WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the welcome module is not **set up** in this server')

        channel = self.bot.cache.welcomechannel[ctx.guild.id]
        msg = self.bot.cache.welcomemessage[ctx.guild.id]
                
        await ctx.guild.get_channel(channel).send(
            **await utils.to_object(await utils.embed_replacement(ctx.author, msg))
        )

        return await ctx.send_success('successfully **dispatched** the welcome message')


    @welcome.command(
        name='settings',
        aliases=['conf', 'config', 'cfg', 'configuration'],
        description="view the server's current welcome configuration",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_settings(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM welcome_channel WHERE guild_id = %s', ctx.guild.id) or not await self.bot.db.fetchrow('SELECT * FROM welcome_message WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the welcome module is not **set up** in this server')

        channel, message = (await self.bot.db.fetchval('SELECT channel_id FROM welcome_channel WHERE guild_id = %s', ctx.guild.id), await self.bot.db.fetchval('SELECT message FROM welcome_message WHERE guild_id = %s', ctx.guild.id))

        embed = discord.Embed(
            color=self.bot.color,
            title='Welcome Configuration',
            timestamp=datetime.now()
        )    
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar
        )
        embed.add_field(
            name=f'{self.bot.dash} Channel',
            value=ctx.guild.get_channel(channel).mention
        )
        embed.add_field(
            name=f'{self.bot.dash} Message',
            value=f'```{message}```',
            inline=False
        )
        
        return await ctx.reply(embed=embed)


    @commands.group(
        name='goodbye',
        aliases=['gb', 'gbye'],
        description='manage the goodbye module for the server',
        brief='goodbye <sub command>',
        help='goodbye channel #joins',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye(self, ctx: Context):
        return await ctx.send_help()

    
    @goodbye.command(
        name='channel',
        aliases=['ch', 'chnnl'],
        description='set the goodbye channel',
        brief='goodbye channel <channel>',
        help='goodbye channel #leaves',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_channel(self, ctx: Context, *, channel: discord.TextChannel):

        await self.bot.db.execute('INSERT INTO goodbye_channel (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)', ctx.guild.id, channel.id)
        self.bot.cache.goodbyechannel[ctx.guild.id] = channel.id
        
        return await ctx.send_success(f'successfully **binded** #{channel.name} as the goodbye channel')


    @goodbye.command(
        name='message',
        aliases=['msg'],
        description='set the goodbye message',
        brief='goodbye message <text>',
        help="goodbye message {content: {user.mention} you wont be missed!}",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_message(self, ctx: Context, *, message: str):

        await self.bot.db.execute('INSERT INTO goodbye_message (guild_id, message) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message)', ctx.guild.id, message)
        self.bot.cache.goodbyemessage[ctx.guild.id] = message
        
        return await ctx.send_success(f'successfully **binded** the goodbye message to:\n\n```{message}```')


    @goodbye.command(
        name='clear',
        aliases=['c'],
        description='clear the goodbye configuration',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM goodbye_channel WHERE guild_id = %s', ctx.guild.id)
        await self.bot.db.execute('DELETE FROM goodbye_message WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.boostmessage.pop(ctx.guild.id)
        except:
            pass
        try:
            self.bot.cache.boostmessage.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f'successfully **cleared** the goodbye configuration')


    @goodbye.command(
        name='test',
        aliases=['t'],
        description='test the goodbye message',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_test(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM goodbye_channel WHERE guild_id = %s', ctx.guild.id) or not await self.bot.db.fetchrow('SELECT * FROM goodbye_message WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the goodbye module is not **set up** in this server')

        channel = self.bot.cache.goodbyechannel[ctx.guild.id]
        msg = self.bot.cache.goodbyemessage[ctx.guild.id]
                
        await ctx.guild.get_channel(channel).send(
            **await utils.to_object(await utils.embed_replacement(ctx.author, msg))
        )

        return await ctx.send_success('successfully **dispatched** the goodbye message')


    @goodbye.command(
        name='settings',
        aliases=['conf', 'config', 'cfg', 'configuration'],
        description="view the server's current goodbye configuration",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_settings(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM goodbye_channel WHERE guild_id = %s', ctx.guild.id) or not await self.bot.db.fetchrow('SELECT * FROM goodbye_message WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the welcome module is not **set up** in this server')

        channel, message = (await self.bot.db.fetchval('SELECT channel_id FROM goodbye_channel WHERE guild_id = %s', ctx.guild.id), await self.bot.db.fetchval('SELECT message FROM goodbye_message WHERE guild_id = %s', ctx.guild.id))

        embed = discord.Embed(
            color=self.bot.color,
            title='Goodbye Configuration',
            timestamp=datetime.now()
        )    
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar
        )
        embed.add_field(
            name=f'{self.bot.dash} Channel',
            value=ctx.guild.get_channel(channel).mention
        )
        embed.add_field(
            name=f'{self.bot.dash} Message',
            value=f'```{message}```',
            inline=False
        )
        
        return await ctx.reply(embed=embed)


    @commands.group(
        name='autoreact',
        aliases=['react'],
        description="manage the server's auto-reactions",
        brief='autoreact <sub command>',
        help='autoreact add welcome :f_welc:',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def autoreact(self, ctx: Context):

        return await ctx.send_help()


    @autoreact.command(
        name='add',
        aliases=['create'],
        description='add an auto-reaction',
        brief='autoreact add <trigger> <emoji>',
        help='autoreact add welcome :f_welc:',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoreact_add(self, ctx: Context, trigger: str, emoji: Union[discord.Emoji, str]):
        
        if isinstance(emoji, str):
            try:
                unicodedata.name(emoji)
            except:
                return await ctx.send_error('please provide a **valid** emoji')

        if await self.bot.db.fetchrow('SELECT * FROM autoreact WHERE guild_id = %s AND trig = %s AND reaction = %s', ctx.guild.id, trigger, str(emoji)):
            return await ctx.send_error('an auto-reaction like that **already exists**')

        await self.bot.db.execute('INSERT INTO autoreact (guild_id, trig, reaction) VALUES (%s, %s, %s)', ctx.guild.id, trigger, str(emoji))

        self.bot.cache.autoreact.setdefault(ctx.guild.id, list()).append((trigger, str(emoji)))
        return await ctx.send_success(f'successfully **binded** {trigger} with the emoji {emoji}')


    @autoreact.command(
        name='remove',
        aliases=['delete'],
        description='remove an auto-reaction',
        brief='autoreact remove <trigger> <emoji>',
        help='autoreact remove welcome :f_welc:',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoreact_remove(self, ctx: Context, trigger: str, emoji: discord.Emoji):

        if not await self.bot.db.fetchrow('SELECT * FROM autoreact WHERE guild_id = %s AND trig = %s AND reaction = %s', ctx.guild.id, trigger, emoji.id):
            return await ctx.send_error("an auto-reaction like that **doesnt't exists**")

        await self.bot.db.execute('DELETE FROM autoreact WHERE guild_id = %s AND trig = %s AND reaction = %s', ctx.guild.id, trigger, emoji.id)

        try:
            self.bot.cache.autoreact.setdefault(ctx.guild.id, list()).remove((trigger, emoji.id))
        except:
            pass
        return await ctx.send_success(f'successfully **unbinded** {trigger} from the emoji {emoji}')


    @autoreact.command(
        name='edit',
        aliases=['update', 'change'],
        description='edit an auto-reaction',
        brief='autoreact edit <trigger> <emoji>',
        help='autoreact edit welcome :whalecum:',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoreact_edit(self, ctx: Context, trigger: str, emoji: discord.Emoji):

        if await self.bot.db.fetchrow('SELECT * FROM autoreact WHERE guild_id = %s AND trig = %s AND reaction = %s', ctx.guild.id, trigger, emoji.id):
            return await ctx.send_error('an auto-reaction like that **already exists**')

        await self.bot.db.execute('UPDATE autoreact SET reaction = %s WHERE trig = %s AND guild_id = %s', emoji.id, trigger, ctx.guild.id)
        
        await self.bot.cache.cache_autoreact()
        return await ctx.send_success(f'successfully **binded** {trigger} with the emoji {emoji}')

    
    @autoreact.command(
        name='clear',
        aliases=['c'],
        description="clear the server's auto-reactions",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoreact_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM autoreact WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.autoreact.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f"successfully **cleared** the server's auto-reactions")


    @autoreact.command(
        name='list',
        aliases=['show'],
        description="show all the server's auto-reactions",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoreact_list(self, ctx: Context):
        
        if not await self.bot.db.execute('SELECT trig, reaction FROM autoreact WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **auto-reactions** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Auto-reactions in {ctx.guild.name}',
            description=list()
        )
        for trigger, reaction in await self.bot.db.execute('SELECT trig, reaction FROM autoreact WHERE guild_id = %s', ctx.guild.id):
            if self.bot.get_emoji(reaction) is not None:
                embed.description.append(f'{trigger}: {self.bot.get_emoji(reaction)}')
            
        return await ctx.paginate(embed)


    @commands.group(
        name='autoresponder',
        aliases=['ar'],
        description="manage the server's auto-responses",
        brief='autoresponder <sub command>',
        help='autoresponder add welcome {content: welcome to the server}',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def autoresponder(self, ctx: Context):

        return await ctx.send_help()


    @autoresponder.command(
        name='add',
        aliases=['create'],
        description='add an auto-response',
        brief='autoresponder add <trigger> <response>',
        help='autoresponder add welcome {content: welcome to the server}',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoresponder_add(self, ctx: Context, trigger: str, *, response: str):

        if await self.bot.db.fetchrow('SELECT * FROM autoresponder WHERE guild_id = %s AND trig = %s AND content = %s', ctx.guild.id, trigger, response):
            return await ctx.send_error('an auto-response like that **already exists**')

        await self.bot.db.execute('INSERT INTO autoresponder (guild_id, trig, content) VALUES (%s, %s, %s)', ctx.guild.id, trigger, response)

        self.bot.cache.autoresponder.setdefault(ctx.guild.id, list()).append((trigger, response))
        return await ctx.send_success(f'successfully **binded** {trigger} with the response:\n\n```{response}```')


    @autoresponder.command(
        name='remove',
        aliases=['delete'],
        description='remove an auto-response',
        brief='autoresponder remove <trigger>',
        help='autoresponder remove welcome',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoresponder_remove(self, ctx: Context, trigger: str):

        if not await self.bot.db.fetchrow('SELECT * FROM autoresponder WHERE guild_id = %s AND trig = %s', ctx.guild.id, trigger):
            return await ctx.send_error("an auto-response like that **doesnt't exists**")

        await self.bot.db.execute('DELETE FROM autoresponder WHERE guild_id = %s AND trig = %s', ctx.guild.id, trigger)

        await self.bot.cache.cache_autoresponder()
        return await ctx.send_success(f'successfully **removed** auto-reaction **`{trigger}`**')


    @autoresponder.command(
        name='edit',
        aliases=['update', 'change'],
        description='edit an auto-response',
        brief='autoresponder edit <trigger> <emoji>',
        help='autoresponder edit welcome {content: check out #rules}',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoresponder_edit(self, ctx: Context, trigger: str, response: str):

        if await self.bot.db.fetchrow('SELECT * FROM autoresponder WHERE guild_id = %s AND trig = %s AND content = %s', ctx.guild.id, trigger, response):
            return await ctx.send_error('an auto-response like that **already exists**')

        await self.bot.db.execute('UPDATE autoresponder SET content = %s WHERE trig = %s AND guild_id = %s', response, trigger, ctx.guild.id)
        
        await self.bot.cache.cache_autoreact()
        return await ctx.send_success(f'successfully **binded** {trigger} with the response:\n\n```{response}```')

    
    @autoresponder.command(
        name='clear',
        aliases=['c'],
        description="clear the server's auto-responses",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoresponder_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM autoresponder WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.autoresponder.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f"successfully **cleared** the server's auto-responses")


    @autoresponder.command(
        name='list',
        aliases=['show'],
        description="show all the server's auto-responses",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autoresponder_list(self, ctx: Context):
        
        if not await self.bot.db.execute('SELECT trig, content FROM autoresponder WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **auto-responses** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Auto-responses in {ctx.guild.name}',
            description=list()
        )
        for trigger, response in await self.bot.db.execute('SELECT trig, content FROM autoresponder WHERE guild_id = %s', ctx.guild.id):
            embed.description.append(f'{trigger}\n{self.bot.reply} **response:** {response}')
            
        return await ctx.paginate(embed)


    @commands.group(
        name='joindm',
        aliases=['welcomedm', 'jdm'],
        description='manage the join-dm module for the server',
        brief='joindm <sub command>',
        help='joindm message {content: welcome to {guild.name}, make sure to check out ...}',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def joindm(self, ctx: Context):

        return await ctx.send_help()
    

    @joindm.command(
        name='message',
        aliases=['msg'],
        description='set the join-dm message',
        brief='joindm message <text>',
        help="joindm message {content: welcome to {guild.name}, make sure to check out ...}",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def joindm_message(self, ctx: Context, *, message: str):

        await self.bot.db.execute('INSERT INTO joindm (guild_id, message) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message)', ctx.guild.id, message)
        self.bot.cache.joindm[ctx.guild.id] = message
        
        return await ctx.send_success(f'successfully **binded** the join-dm message to:\n\n```{message}```')


    @joindm.command(
        name='clear',
        aliases=['c'],
        description='clear the joindm configuration',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def joindm_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM joindm WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.joindm.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f'successfully **cleared** the joindm configuration')


    @joindm.command(
        name='test',
        aliases=['t'],
        description='test the join-dm',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def joindm_test(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM joindm WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the join-dm module is not **set up** in this server')

        msg = self.bot.cache.joindm[ctx.guild.id]
                
        if 15 >= self.bot.cache.limits['dms'].get(ctx.guild.id, 0):
            await ctx.author.send(
                **await utils.to_object(await utils.embed_replacement(ctx.author, msg))
            )

        return await ctx.send_success('successfully **dispatched** the join-dm')


    @joindm.command(
        name='settings',
        aliases=['conf', 'config', 'cfg', 'configuration'],
        description="view the server's current join-dm configuration",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def joindm_settings(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM joindm WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the join-dm module is not **set up** in this server')

        message = await self.bot.db.fetchval('SELECT message FROM joindm WHERE guild_id = %s', ctx.guild.id)

        embed = discord.Embed(
            color=self.bot.color,
            title='Join-DM Configuration',
            timestamp=datetime.now()
        )    
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar
        )
        embed.add_field(
            name=f'{self.bot.dash} Message',
            value=f'```{message}```',
            inline=False
        )
        
        return await ctx.reply(embed=embed)


    @commands.group(
        name='pingonjoin',
        aliases=['poj'],
        description='manage the ping-on-join module for the server',
        brief='pingonjoin <sub command>',
        help='pingonjoin add #rules',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def pingonjoin(self, ctx: Context):

        return await ctx.send_help()


    @pingonjoin.command(
        name='add',
        aliases=['create'],
        description='add a ping-on-join channel',
        brief='pingonjoin add <channel>',
        help='pingonjoin add #rules',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def pingonjoin_add(self, ctx: Context, channel: discord.TextChannel):

        if await self.bot.db.fetchrow('SELECT * FROM ping_on_join WHERE guild_id = %s AND channel_id = %s', ctx.guild.id, channel.id):
            return await ctx.send_error('an ping-on-join channel like that **already exists**')

        await self.bot.db.execute('INSERT INTO ping_on_join (guild_id, channel_id) VALUES (%s, %s)', ctx.guild.id, channel.id)

        self.bot.cache.pingonjoin.setdefault(ctx.guild.id, list()).append(channel.id)
        return await ctx.send_success(f'successfully **binded** {channel.mention} as a ping-on-join channel')


    @pingonjoin.command(
        name='remove',
        aliases=['delete'],
        description='remove a ping-on-join channel',
        brief='pingonjoin remove <channel>',
        help='pingonjoin remove #rules',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def pingonjoin_remove(self, ctx: Context, channel: discord.TextChannel):

        if not await self.bot.db.fetchrow('SELECT * FROM ping_on_join WHERE guild_id = %s AND channel_id = %s', ctx.guild.id, channel.id):
            return await ctx.send_error("a ping-on-join channel like that **doesnt't exists**")

        await self.bot.db.execute('DELETE FROM ping_on_join WHERE guild_id = %s AND channel_id = %s', ctx.guild.id, channel.id)

        await self.bot.cache.cache_pingonjoin()
        return await ctx.send_success(f'successfully **removed** ping-on-join in {channel.mention}')



    @pingonjoin.command(
        name='clear',
        aliases=['c'],
        description='clear the ping-on-join channels',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def pingonjoin_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM ping_on_join WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.pingonjoin.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f'successfully **cleared** the ping-on-join channels')


    @pingonjoin.command(
        name='test',
        aliases=['t'],
        description='test the ping-on-join',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def pingonjoin_test(self, ctx: Context):

        if not await self.bot.db.fetch('SELECT channel_id FROM ping_on_join WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('there are no ping-on-join channels in this server')

        channel_ids = self.bot.cache.pingonjoin[ctx.guild.id]
        await ctx.send_success('successfully **dispatched** ping-on-join')

        for channel_id in channel_ids:
            if ctx.guild.get_channel(channel_id):
                await ctx.guild.get_channel(channel_id).send(ctx.author.mention, delete_after=0)
        
        return


    @pingonjoin.command(
        name='list',
        aliases=['show'],
        description="view the server's current ping-on-join configuration",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def pingonjoin_list(self, ctx: Context):

        if not await self.bot.db.fetch('SELECT channel_id FROM ping_on_join WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there are no ping-on-join channels in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Ping-on-join channels in {ctx.guild.name}',
            description=list()
        )
        for channel_id in set(await self.bot.db.fetch('SELECT channel_id FROM ping_on_join WHERE guild_id = %s', ctx.guild.id)):
            if ctx.guild.get_channel(channel_id) is not None:
                embed.description.append(f'{ctx.guild.get_channel(channel_id)} ( `{channel_id}` )')
            
        return await ctx.paginate(embed)


    @commands.group(
        name='skullboard',
        aliases=['skull'],
        description='manage the skull-board module for the server',
        brief='skullboard <sub command>',
        help='skullboard channel #skull',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def skullboard(self, ctx: Context):

        return await ctx.send_help()

    @skullboard.command(
        name='channel',
        aliases=['ch'],
        description='set the skull-board channek',
        brief='skullboard channel <channel>',
        help="skullboard channel #skull",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def skullboard_channel(self, ctx: Context, *, channel: discord.TextChannel):

        if channel.id == await self.bot.db.fetchval('SELECT channel_id FROM skullboard WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error(f'the skull-board channel is already set to #{channel.name}')

        await self.bot.db.execute('INSERT INTO skullboard (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)', ctx.guild.id, channel.id)
        self.bot.cache.skullboard[ctx.guild.id] = channel.id
        
        return await ctx.send_success(f'successfully **binded** #{channel.name} as the skull-board channel')


    @skullboard.command(
        name='clear',
        aliases=['c'],
        description='clear the skullboard configuration',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def skullboard_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM skullboard WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.skullboard.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f'successfully **cleared** the skullboard configuration')


    @skullboard.command(
        name='settings',
        aliases=['conf', 'config', 'cfg', 'configuration'],
        description="view the server's current skull-board configuration",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def skullboard_settings(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM skullboard WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the skull-board module is not **set up** in this server')

        channel_id = await self.bot.db.fetchval('SELECT channel_id FROM skullboard WHERE guild_id = %s', ctx.guild.id)

        if ctx.guild.get_channel(channel_id) is None:
            return await ctx.send_error("i couldn't get the skull-board channel. make sure it wasn't deleted")

        embed = discord.Embed(
            color=self.bot.color,
            title='Skull-board Configuration',
            timestamp=datetime.now()
        )    
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar
        )
        embed.add_field(
            name=f'{self.bot.dash} Channel',
            value=ctx.guild.get_channel(channel_id).mention,
            inline=False
        )
        
        return await ctx.reply(embed=embed)


    @commands.group(
        name='ranks',
        aliases=['selfroles'],
        description='set up ranks that members can give to themselves',
        brief='ranks <sub command>',
        help='ranks add Developer',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def ranks(self, ctx: Context):
        return await ctx.send_help()

    
    @ranks.command(
        name='add',
        description="add a role to the server's rank",
        brief='ranks add <role>',
        help='ranks add Developer',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def ranks_add(self, ctx: Context, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if role.is_dangerous():
            return await ctx.send_success(f'that role has **dangerous permissions**')

        if role.id in set(await self.bot.db.fetch('SELECT role_id FROM ranks WHERE guild_id = %s', ctx.guild.id)):
            return await ctx.send_error(f'{role.name} is **already a rank** in this server')
        
        await self.bot.db.execute('INSERT INTO ranks (guild_id, role_id) VALUES (%s, %s)', ctx.guild.id, role.id)
        return await ctx.send_success(f"successfully **added** {role.name} to the server's ranks")

    
    @ranks.command(
        name='remove',
        aliases=['delete', 'del'],
        description="remove a role from the server's ranks",
        brief='ranks remove <role>',
        help='ranks remove Developer',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def ranks_remove(self, ctx: Context, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = await ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if role.id not in set(await self.bot.db.fetch('SELECT role_id FROM ranks WHERE guild_id = %s', ctx.guild.id)):
            return await ctx.send_error("that role **isn't a rank** in this server")

        await self.bot.db.execute('DELETE FROM ranks WHERE guild_id = %s AND role_id = %s', ctx.guild.id, role.id)
        return await ctx.send_success(f"successfully **removed** {role.name} from the server's ranks")


    @ranks.command(
        name='clear',
        aliases=['c'],
        description="clear the server's ranks",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def ranks_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM ranks WHERE guild_id = %s', ctx.guild.id)
        return await ctx.send_success("successfully **cleared** the server's ranks")

    
    @ranks.command(
        name='list',
        aliases=['show'],
        description="show all the server's ranks",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(send_messages=True)
    async def ranks_list(self, ctx: Context):
        
        if not await self.bot.db.fetch('SELECT role_id FROM ranks WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **ranks** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Ranks in {ctx.guild.name}',
            description=list()
        )
        for role_id in set(await self.bot.db.fetch('SELECT role_id FROM ranks WHERE guild_id = %s', ctx.guild.id)):
            if ctx.guild.get_role(role_id):
                embed.description.append(ctx.guild.get_role(role_id).mention)
            
        return await ctx.paginate(embed)


    @commands.group(
        name='alias',
        description="manage the server's custom aliases",
        brief='alias <sub command>',
        help='alias add ban pack',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def alias(self, ctx: Context):
        return await ctx.send_help()
        
        
    @alias.command(
        name='add',
        description='add an alias to a command',
        brief='alias add <command> <alias>',
        help='alias add ban pack',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_add(self, ctx: Context, command: str, alias: str):
        
        if self.bot.get_command(command) is None:
            return await ctx.send_error('please provide a **valid** command')
            
        if self.bot.get_command(alias) is not None:
            return await ctx.send_error(f'there is already a command with the name/alias {alias}')
            
        if len(alias) > 32:
            return await ctx.send_error('please provide a **valid** alias under 32 characters')
            
        await self.bot.db.execute('INSERT INTO aliases (guild_id, alias, command) VALUES (%s, %s, %s)', ctx.guild.id, alias, self.bot.get_command(command).name)
        if ctx.guild.id not in self.bot.cache.aliases:
            self.bot.cache.aliases[ctx.guild.id] = dict()
            
        self.bot.cache.aliases[ctx.guild.id][alias] = self.bot.get_command(command).name
        return await ctx.send_success(f'successfully **binded** {alias} with the command {self.bot.get_command(command).name}')
        
        
    @alias.command(
        name='remove',
        description='remove an alias',
        brief='alias remove <alias>',
        help='alias remove pack',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_remove(self, ctx: Context, alias: str):
            
        if alias not in set(await self.bot.db.fetch('SELECT alias FROM aliases WHERE guild_id = %s AND command = %s', ctx.guild.id, self.bot.get_command(command).name)):
            return await ctx.send_error('please provide a **valid** alias')
            
        await self.bot.db.execute('DELETE FROM aliases WHERE guild_id = %s AND alias = %s', ctx.guild.id, alias)
        if ctx.guild.id not in self.bot.cache.aliases:
            self.bot.cache.aliases[ctx.guild.id] = list()
            
        await self.bot.cache.cache_aliases()
        return await ctx.send_success(f'successfully **removed** the alias {alias}')
        
        
    @alias.command(
        name='clear',
        description='clear every alias in this server',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_clear(self, ctx: Context):
        
        await self.bot.db.execute('DELETE FROM aliases WHERE guild_id = %s', ctx.guild.id)
        await self.bot.cache.cache_aliases()
        
        return await ctx.send_success('successfully **cleared** all aliases in this server')
        
        
    @alias.command(
        name='list',
        aliases=['show'],
        description='view every alias in this server',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_list(self, ctx: Context):
        
        if not await self.bot.db.fetch('SELECT alias FROM aliases WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **aliases** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Aliases in {ctx.guild.name}',
            description=list()
        )
        for alias, command in await self.bot.db.execute('SELECT alias, command FROM aliases WHERE guild_id = %s', ctx.guild.id):
            if self.bot.get_command(command):
                embed.description.append(alias)
            
        return await ctx.paginate(embed)


    @commands.command(
        name='tasks',
        description='view every running task in this server',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def tasks(self, ctx: Context):

        if not self.bot.tasks.get(ctx.guild.id, list()):
            return await ctx.send_error("there aren't any running tasks in this server")

        embed = discord.Embed(color=self.bot.color, title=f'Tasks in {ctx.guild.name}', description=list())
        
        for task in self.bot.tasks[ctx.guild.id]:
            embed.description.append(task.ctx.command.qualified_name)

        return await ctx.paginate(embed)


    @commands.command(
        name='cancel',
        description='cancel a running task in this server',
        brief='cancel [index]',
        help='cancel 1',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def cancel(self, ctx: Context, index: Optional[int] = 1):

        if not self.bot.tasks.get(ctx.guild.id, list()):
            return await ctx.send_error("there aren't any running tasks in this server")
            
        if index < 1 or index > len(self.bot.tasks[ctx.guild.id]):
            return await ctx.send_error('please provide a **valid** index')

        task = self.bot.tasks[ctx.guild.id][index - 1]
        task.task.cancel()

        self.bot.tasks[ctx.guild.id].remove(task)

        return await ctx.send_success(f'successfully **cancelled** `{task.ctx.command.qualified_name}`')

    
    @commands.group(
        name='reactionrole',
        aliases=['rr', 'reactionroles'],
        description="manage the server's reaction roles",
        brief='reactionrole <sub command>',
        help='reactionrole add 1073199913061597254 1069320886097817651 :50DollaLemonade:',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def reactionrole(self, ctx: Context):
        return await ctx.send_help()
        
        
    @reactionrole.command(
        name='add',
        description='add an reaction role to a message',
        brief='reactionrole add <message> <role> <emoji>',
        help='reactionrole add 1073199913061597254 1069320886097817651 :50DollaLemonade:',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def reactionrole_add(self, ctx: Context, message: discord.Message, role: Union[str, discord.Role], emoji: Union[str, discord.Emoji]):
        
        if isinstance(role, str):
            role = ctx.find_role(role)
            
            if role is None:
                return await ctx.send_error('please provide a **valid** role')
            
        try:
            await message.add_reaction(emoji)
        except:
            return await ctx.send_error("couldn't **react** to that message")
            
        await self.bot.db.execute(
            'INSERT INTO reaction_roles (guild_id, message_id, role_id, emoji) VALUES (%s, %s, %s, %s)', 
            ctx.guild.id, message.id, role.id, str(emoji)
        )
        if ctx.guild.id not in self.bot.cache.reactionroles:
            self.bot.cache.reactionroles[ctx.guild.id] = dict()

        if message.id not in self.bot.cache.reactionroles[ctx.guild.id]:
            self.bot.cache.reactionroles[ctx.guild.id][message.id] = list()
            
        self.bot.cache.reactionroles[ctx.guild.id][message.id].append({'role_id': role.id, 'emoji': str(emoji)})
        return await ctx.send_success(f'successfully **binded** {role.mention} with the emoji {str(emoji)}')
        
        
    @reactionrole.command(
        name='remove',
        description='remove a reaction role',
        brief='reactionrole remove <message> <role> <emoji>',
        help='reactionrole remove 1073199913061597254 1069320886097817651 :50DollaLemonade:',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def reactionrole_remove(self, ctx: Context, message: discord.Message, role: Union[str, discord.Role], emoji: Union[str, discord.Emoji]):
        
        if isinstance(role, str):
            role = ctx.find_role(role)
            
            if role is None:
                return await ctx.send_error('please provide a **valid** role')
        
        if not await self.bot.db.fetchrow('SELECT * FROM reaction_roles WHERE guild_id = %s AND message_id = %s AND role_id = %s AND emoji = %s', ctx.guild.id, message.id, role.id, str(emoji)):
            return await ctx.send_error("couldn't find a **reaction role** like that")

        await self.bot.db.execute(
            'DELETE FROM reaction_roles WHERE guild_id = %s AND message_id = %s AND role_id = %s AND emoji = %s', 
            ctx.guild.id, message.id, role.id, str(emoji)
        )
            
        self.bot.cache.reactionroles[ctx.guild.id][message.id].remove({'role_id': role.id, 'emoji': str(emoji)})
        return await ctx.send_success(f'successfully **removed** {str(emoji)} from {role.mention}')
        
        
    @reactionrole.command(
        name='clear',
        description='clear every reaction role in this server',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def reactionrole_clear(self, ctx: Context):
        
        await self.bot.db.execute('DELETE FROM reaction_roles WHERE guild_id = %s', ctx.guild.id)
        await self.bot.cache.cache_reactionroles()
        
        return await ctx.send_success('successfully **cleared** all reaction roles in this server')


    @commands.group(
        name='automod',
        aliases=['am'],
        description='manage the automod module',
        brief='automod <sub command>',
        help='automod setup',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx: Context):
        return await ctx.send_help()

    
    @automod.command(
        name='setup',
        description='setup the default automod configurations',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def automod_setup(self, ctx: Context):

        if await self.bot.db.fetchrow('SELECT * FROM automod WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('automod is already **set up** in this server')

        to_delete = await ctx.send_success('setting up **automod** in this server')

        async with ctx.handle_response():
            await self.bot.db.execute(
                'INSERT INTO automod (guild_id, spam, invites, massmention) VALUES (%s, 1, 1, 1)',
                ctx.guild.id
            )
            self.bot.cache.automod[ctx.guild.id] = {'spam': 1, 'invites': 1, 'massmention': 1}

            await to_delete.delete()
            return await ctx.send_success('successfully **set up** automod in this server')


    @automod.command(
        name='spam',
        description='punish members for spamming',
        brief='automod spam <state>',
        help='automod spam true',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def automod_spam(self, ctx: Context, state: str):

        if state == 'true':
            await self.bot.db.execute(
                'INSERT INTO automod (guild_id, spam, invites, massmention) VALUES (%s, 1, 0, 0) ON DUPLICATE KEY UPDATE spam = 1', ctx.guild.id
            )
            if ctx.guild.id not in self.bot.cache.automod:
                self.bot.cache.automod[ctx.guild.id] = {'spam': 0, 'invites': 0, 'massmention': 0}

            self.bot.cache.automod[ctx.guild.id]['spam'] = 1
            return await ctx.send_success('automod spam has been **enabled**')

        elif state == 'false':
            await self.bot.db.execute(
                'INSERT INTO automod (guild_id, spam, invites, massmention) VALUES (%s, 0, 0, 0) ON DUPLICATE KEY UPDATE spam = 0', ctx.guild.id
            )
            if ctx.guild.id not in self.bot.cache.automod:
                self.bot.cache.automod[ctx.guild.id] = {'spam': 0, 'invites': 0, 'massmention': 0}

            self.bot.cache.automod[ctx.guild.id]['spam'] = 0
            return await ctx.send_success('automod spam has been **disabled**')
        
        else:
            return await ctx.send_error('please provide a **valid** state')


    @automod.command(
        name='invites',
        description='punish members for sending invites',
        brief='automod invites <state>',
        help='automod invites true',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def automod_invites(self, ctx: Context, state: str):

        if state == 'true':
            await self.bot.db.execute(
                'INSERT INTO automod (guild_id, spam, invites, massmention) VALUES (%s, 0, 1, 0) ON DUPLICATE KEY UPDATE invites = 1', ctx.guild.id
            )
            if ctx.guild.id not in self.bot.cache.automod:
                self.bot.cache.automod[ctx.guild.id] = {'spam': 0, 'invites': 0, 'massmention': 0}

            self.bot.cache.automod[ctx.guild.id]['invites'] = 1
            return await ctx.send_success('automod invites has been **enabled**')

        elif state == 'false':
            await self.bot.db.execute(
                'INSERT INTO automod (guild_id, spam, invites, massmention) VALUES (%s, 0, 0, 0) ON DUPLICATE KEY UPDATE invites = 0', ctx.guild.id
            )
            if ctx.guild.id not in self.bot.cache.automod:
                self.bot.cache.automod[ctx.guild.id] = {'spam': 0, 'invites': 0, 'massmention': 0}

            self.bot.cache.automod[ctx.guild.id]['invites'] = 0
            return await ctx.send_success('automod invites has been **disabled**')
        
        else:
            return await ctx.send_error('please provide a **valid** state')


    @automod.command(
        name='massmention',
        aliases=['pings'],
        description='punish members for mass mention',
        brief='automod massmention <state>',
        help='automod massmention true',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def automod_massmention(self, ctx: Context, state: str):

        if state == 'true':
            await self.bot.db.execute(
                'INSERT INTO automod (guild_id, spam, invites, massmention) VALUES (%s, 0, 0, 1) ON DUPLICATE KEY UPDATE massmention = 1', ctx.guild.id
            )
            if ctx.guild.id not in self.bot.cache.automod:
                self.bot.cache.automod[ctx.guild.id] = {'spam': 0, 'invites': 0, 'massmention': 0}

            self.bot.cache.automod[ctx.guild.id]['massmention'] = 1
            return await ctx.send_success('automod massmention has been **enabled**')

        elif state == 'false':
            await self.bot.db.execute(
                'INSERT INTO automod (guild_id, spam, invites, massmention) VALUES (%s, 0, 0, 0) ON DUPLICATE KEY UPDATE massmention = 0', ctx.guild.id
            )
            if ctx.guild.id not in self.bot.cache.automod:
                self.bot.cache.automod[ctx.guild.id] = {'spam': 0, 'invites': 0, 'massmention': 0}

            self.bot.cache.automod[ctx.guild.id]['massmention'] = 0
            return await ctx.send_success('automod massmention has been **disabled**')
        
        else:
            return await ctx.send_error('please provide a **valid** state')


    @automod.command(
        name='clear',
        aliases=['c'],
        description='clear the automod configuration',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def automod_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM automod WHERE guild_id = %s', ctx.guild.id)
        await self.bot.db.execute('DELETE FROM automod_whitelist WHERE guild_id = %s', ctx.guild.id)
        await self.bot.cache.cache_automod()

        return await ctx.send_error('successfully **cleared** the automod configuration')


    @automod.command(
        name='whitelist',
        aliases=['exempt'],
        description='whitelist members from being punished',
        brief='automod whitelist <source member/channel/role>',
        help='automod whitelist @glory#0007',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def automod_whitelist(self, ctx: Context, source: Union[discord.Member, discord.TextChannel, discord.Role, str]):
        
        if isinstance(source, discord.Member) and await ctx.can_moderate(source, 'whitelist') is not None:
            return

        if isinstance(source, str):
            source = ctx.find_role(source)
            
            if source is None:
                return await ctx.send_error('please provide a **valid** role')

        if source.id in set(await self.bot.db.fetch('SELECT user_id FROM automod_whitelist WHERE guild_id = %s', ctx.guild.id)):
            await self.bot.db.execute(
                'DELETE FROM automod_whitelist WHERE guild_id = %s AND user_id = %s', ctx.guild.id, source.id
            )
            if ctx.guild.id not in self.bot.cache.automod_whitelist:
                self.bot.cache.automod_whitelist[ctx.guild.id] = set()

            try:
                self.bot.cache.automod_whitelist[ctx.guild.id].remove(source.id)
            except:
                pass

            return await ctx.send_success(f'successfully **unwhitelisted** {source.mention}')

        await self.bot.db.execute(
            'INSERT INTO automod_whitelist (guild_id, user_id) VALUES (%s, %s)', ctx.guild.id, source.id
        )
        if ctx.guild.id not in self.bot.cache.automod_whitelist:
            self.bot.cache.automod_whitelist[ctx.guild.id] = set()

        self.bot.cache.automod_whitelist[ctx.guild.id].add(source.id)
        return await ctx.send_success(f'successfully **whitelisted** {source.mention}')


    @automod.command(
        name='whitelisted',
        description='see every whitelisted member',
    )
    async def automod_whitelisted(self, ctx: Context):

        if not await self.bot.db.fetch('SELECT user_id FROM automod_whitelist WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('there are no **whitelisted** users in this server')

        embed = discord.Embed(
            color=self.bot.color,
            title=f'Whitelisted Users in {ctx.guild.name}',
            description=list()
        )

        for user_id in set(await self.bot.db.fetch('SELECT user_id FROM automod_whitelist WHERE guild_id = %s AND user_id IN %s', ctx.guild.id, list(map(lambda m: m.id, ctx.guild.members)))):
            member = ctx.guild.get_member(user_id)
            embed.description.append(f'{member.mention}: **{member}** ( `{member.id}` )')

        return await ctx.paginate(embed)


    @automod.command(
        name='settings',
        aliases=['conf', 'config', 'cfg', 'configuration'],
        description="view the server's current auto-mod configuration",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def automod_settings(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM automod WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the auto-mod module is not **set up** in this server')

        spam, invites, massmention = await self.bot.db.fetchrow('SELECT spam, invites, massmention FROM automod WHERE guild_id = %s', ctx.guild.id)

        embed = discord.Embed(color=self.bot.color, title='Auto-Mod Configuration', timestamp=datetime.now())    
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.add_field(name=f'{self.bot.dash} Spam', value=f"{self.bot.reply} {'true' if spam else 'false'}")
        embed.add_field(name=f'{self.bot.dash} Invites', value=f"{self.bot.reply} {'true' if invites else 'false'}")
        embed.add_field(name=f'{self.bot.dash} Mass Mention', value=f"{self.bot.reply} {'true' if massmention else 'false'}")
        
        return await ctx.reply(embed=embed)


    @commands.group(
        name='tracker',
        aliases=['track'],
        description="manage the server's discriminator trackers",
        brief='tracker <sub subcommand>',
        help='tracker add 0001 #tags',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def tracker(self, ctx: Context):

        return await ctx.send_help()


    @tracker.command(
        name='add',
        aliases=['create'],
        description='add a discriminator tracker',
        brief='tracker add <discriminator> <channel>',
        help='tracker add 0001 #tags',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def tracker_add(self, ctx: Context, discriminator: str, channel: discord.TextChannel):
        
        if len(discriminator) != 4 or not discriminator.isdigit():
            return await ctx.send_error('please provide a **valid** discriminator')
            
        if await self.bot.db.fetchrow('SELECT * FROM tracker WHERE guild_id = %s AND channel_id = %s AND discriminator = %s', ctx.guild.id, channel.id, discriminator):
            return await ctx.send_error('a discriminator tracker like that **already exists**')

        await self.bot.db.execute('INSERT INTO tracker (guild_id, channel_id, discriminator) VALUES (%s, %s, %s)', ctx.guild.id, channel.id, discriminator)

        self.bot.cache.tracker.setdefault(ctx.guild.id, list()).append({'channel_id': channel.id, 'discriminator': discriminator})
        return await ctx.send_success(f'successfully **binded** {channel.mention} to `#{discriminator}`')


    @tracker.command(
        name='remove',
        aliases=['delete'],
        description='remove a discriminator tracker',
        brief='tracker remove <role>',
        help='tracker remove 0001 #tags',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def tracker_remove(self, ctx: Context, discriminator: str, channel: discord.TextChannel):
        
        if len(discriminator) != 4 or not discriminator.isdigit():
            return await ctx.send_error('please provide a **valid** discriminator')
            
        if not await self.bot.db.fetchrow('SELECT * FROM tracker WHERE guild_id = %s AND channel_id = %s AND discriminator = %s', ctx.guild.id, channel.id, discriminator):
            return await ctx.send_error("a discriminator tracker like that **doesnt't exists**")

        await self.bot.db.execute('DELETE FROM tracker WHERE guild_id = %s AND channel_id = %s AND discriminator = %s', ctx.guild.id, channel.id, discriminator)

        try:
            self.bot.cache.tracker.setdefault(ctx.guild.id, list()).remove({'channel_id': channel.id, 'discriminator': discriminator})
        except:
            pass
        return await ctx.send_success(f'successfully **removed** {channel.mention} from `#{discriminator}`')

    
    @tracker.command(
        name='clear',
        aliases=['c'],
        description="clear the server's discriminator trackers",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def tracker_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM tracker WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.tracker.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f"successfully **cleared** the server's discriminator trackers")


    @tracker.command(
        name='list',
        aliases=['show'],
        description="show all the server's discriminator trackers",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def tracker_list(self, ctx: Context):
        
        if not await self.bot.db.execute('SELECT channel_id FROM tracker WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **discriminator trackers** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Discriminator Trackers in {ctx.guild.name}',
            description=list()
        )
        for channel_id, discriminator in await self.bot.db.execute('SELECT channel_id, discriminator FROM tracker WHERE guild_id = %s', ctx.guild.id):
            if ctx.guild.get_channel(channel_id) is not None:
                embed.description.append(f'{self.bot.get_channel(channel_id).mention} {discriminator} ( `{channel_id}` )')
            
        return await ctx.paginate(embed)


    @commands.group(
        name='verification',
        aliases=['verify'],
        description="manage the server's verification channels",
        brief='verification <sub subcommand>',
        help='verification add #verify @Member verify me',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def verification(self, ctx: Context):
        return await ctx.send_help()


    @verification.command(
        name='add',
        aliases=['create'],
        description='add a verification channel',
        brief='verification add <channel> <role> <text>',
        help='verification add #verify @Member verify me',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def verification_add(self, ctx: Context, channel: discord.TextChannel, role: discord.Role, *, text: str):
            
        if await self.bot.db.fetchrow('SELECT * FROM verification WHERE guild_id = %s AND channel_id = %s AND text = %s', ctx.guild.id, channel.id, text):
            return await ctx.send_error('a verification channel like that **already exists**')

        await self.bot.db.execute('INSERT INTO verification (guild_id, channel_id, role_id, text) VALUES (%s, %s, %s, %s)', ctx.guild.id, channel.id, role.id, text)
        if ctx.guild.id not in self.bot.cache.verification:
            self.bot.cache.verification[ctx.guild.id] = dict()
            
        self.bot.cache.verification[ctx.guild.id][channel.id] = {'role_id': role.id, 'text': text}
        return await ctx.send_success(f'successfully **binded** {channel.mention} to `{text}`')


    @verification.command(
        name='remove',
        aliases=['delete'],
        description='remove a verification channel',
        brief='verification remove <channel> <text>',
        help='verification remove #verify verify me',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def verification_remove(self, ctx: Context, channel: discord.TextChannel, role: discord.Role, *, text: str):
            
        if not await self.bot.db.fetchrow('SELECT * FROM verification WHERE guild_id = %s AND channel_id = %s AND text = %s', ctx.guild.id, channel.id, text):
            return await ctx.send_error("a verification channel like that **doesnt't exists**")

        await self.bot.db.execute('DELETE FROM verification WHERE guild_id = %s AND channel_id = %s AND text = %s', ctx.guild.id, channel.id, text)

        self.bot.cache.verification[ctx.guild.id].pop(channel.id)
        return await ctx.send_success(f'successfully **removed** {channel.mention} ({role.mention}, `{text}`)')

    
    @verification.command(
        name='clear',
        aliases=['c'],
        description="clear the server's verification channels",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def verification_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM verification WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.verification.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f"successfully **cleared** the server's verification channels")


    @verification.command(
        name='list',
        aliases=['show'],
        description="show all the server's verification channels",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def verification_list(self, ctx: Context):
        
        if not await self.bot.db.execute('SELECT channel_id FROM verification WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **verification channels** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Verification Channels in {ctx.guild.name}',
            description=list()
        )
        for channel_id, role_id, text in await self.bot.db.execute('SELECT channel_id, role_id, text FROM verification WHERE guild_id = %s', ctx.guild.id):
            if (ctx.guild.get_channel(channel_id) is not None) and (ctx.guild.get_role(role_id) is not None):
                embed.description.append(f'{self.bot.get_channel(channel_id).mention}**:** {text} ({ctx.guild.get_role(role_id).mention})')
            
        return await ctx.paginate(embed)


async def setup(bot: Vile):
    await bot.add_cog(Configuration(bot))
