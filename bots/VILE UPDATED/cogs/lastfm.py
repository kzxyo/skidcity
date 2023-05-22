import discord, typing, time, arrow, psutil, copy, aiohttp, random
from datetime import datetime
from typing import Optional, Union, Literal
from rivalapi import RivalAPI
from utilities import utils
from utilities.baseclass import Vile
from utilities.lastfm import LastFM
from utilities.context import Context
from discord.ext import commands


class LastFM_Integration(commands.Cog):
    def __init__(self, bot: Vile) -> None:
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if self.bot.cache.lastfm.get(message.author.id) is None:
            return
        
        if self.bot.cache.lastfm[message.author.id].get('command') is not None:
            if message.content == self.bot.cache.lastfm[message.author.id]['command']:
                async with (await self.bot.get_context(message)).handle_response():
                    context = await self.bot.get_context(message)
                    await context.invoke(self.bot.get_command('fm'))


    @commands.group(
        name='lastfm',
        aliases=['lf'],
        description='interfact with last.fm using vile',
        brief='lastfm <sub command>',
        help='lastfm set glory0007',
        invoke_without_command=True
    )
    async def lastfm(self, ctx: Context):

        return await ctx.send_help()

    @lastfm.command(
        name='set',
        description='set your last.fm username',
        brief='lastfm set <username>',
        help='lastfm set glory0007'
    )
    async def lastfm_set(self, ctx: Context, username: str):

        if username is None or len(username) > 15:
            return await ctx.send_error('please provide a **valid** last.fm username'),
            
        async with ctx.handle_response():

            to_edit = await ctx.send_success(f'**binding** your last.fm username to **`{username}`**')

            await self.bot.db.execute('INSERT INTO lastfm (user_id, lastfm_username) VALUES (%s, %s) ON DUPLICATE KEY UPDATE lastfm_username = VALUES(lastfm_username)', ctx.author.id, username)
            self.bot.cache.lastfm.setdefault(ctx.author, {})['username'] = username
            
            await to_edit.edit(embed=discord.Embed(
                color=self.bot.color, 
                description=f'{self.bot.done} {ctx.author.mention}**:** **indexing** your last.fm library'
            ))
            await self.bot.db.execute('DELETE FROM lastfm_playcount WHERE user_id = %s', ctx.author.id)

            artists = await LastFM(username=username).top_artists(limit=1000)
            if artists is None:
                return await to_edit.edit(embed=discord.Embed(
                    color=self.bot.color, 
                    description=f"{self.bot.done} {ctx.author.mention}**:** couldn't **fetch** your top artists"
                ))


            for artist in artists:
                await self.bot.db.execute(
                    'INSERT INTO lastfm_playcount (user_id, artist, play_count) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE play_count = VALUES(play_count)',
                    ctx.author.id, artist['name'], artist['plays']
                )

            return await to_edit.edit(embed=discord.Embed(
                color=self.bot.color, 
                description=f'{self.bot.done} {ctx.author.mention}**:** successfully **binded** your last.fm username to **`{username}`**'
            ))


    @lastfm.command(
        name='index',
        aliases=['update'],
        description='index your last.fm library'
    )
    async def lastfm_index(self, ctx: Context):

        if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you don't have a **last.fm** username linked")
            
        async with ctx.handle_response():

            to_edit = await ctx.send_success(f'**indexing** your last.fm library')

            artists = await LastFM(username=await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)).top_artists(limit=1000)
            if artists is None:
                return await to_edit.edit(embed=discord.Embed(
                    color=self.bot.color, 
                    description=f"{self.bot.done} {ctx.author.mention}**:** couldn't **fetch** your top artists"
                ))


            for artist in artists:
                await self.bot.db.execute(
                    'INSERT INTO lastfm_playcount (user_id, artist, play_count) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE play_count = VALUES(play_count)',
                    ctx.author.id, artist['name'], artist['plays']
                )

            return await to_edit.edit(embed=discord.Embed(
                color=self.bot.color, 
                description=f'{self.bot.done} {ctx.author.mention}**:** successfully **indexed** your last.fm library'
            ))


    @lastfm.command(
        name='reset',
        description='reset your last.fm configurations'
    )
    async def lastfm_reset(self, ctx: Context):

        if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you don't have a **last.fm** username linked")

        await self.bot.db.execute('DELETE FROM lastfm WHERE user_id = %s', ctx.author.id)
        await self.bot.db.execute('DELETE FROM lastfm_command WHERE user_id = %s', ctx.author.id)
        await self.bot.db.execute('DELETE FROM lastfm_embed WHERE user_id = %s', ctx.author.id)
        await self.bot.db.execute('DELETE FROM lastfm_reactions WHERE user_id = %s', ctx.author.id)
        await self.bot.db.execute('DELETE FROM lastfm_playcount WHERE user_id = %s', ctx.author.id)

        await self.bot.cache.cache_lastfm()
        
        return await ctx.send_success('successfully **reset** your last.fm configuations')


    @lastfm.command(
        name='customcommand',
        aliases=['cc'],
        description='set your custom last.fm nowplaying command',
        brief='lastfm customcommand <name>',
        help='lastfm customcommand kitten'
    )
    async def lastfm_customcommand(self, ctx: Context, *, name: str):
        
        if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you don't have a **last.fm** username linked")

        if name == 'clear':
            await self.bot.db.execute('DELETE FROM lastfm_command WHERE user_id = %s', ctx.author.id)
            await self.bot.cache.cache_lastfm()
            return await ctx.send_success('successfully **reset** your last.fm nowplaying command')

        await self.bot.db.execute('INSERT INTO lastfm_command (user_id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name)', ctx.author.id, name)
        self.bot.cache.lastfm[ctx.author.id]['command'] = name

        return await ctx.send_success(f'successfully **binded** your last.fm command to **`{discord.utils.escape_markdown(name)}`**')


    @lastfm.command(
        name='reaction', 
        aliases=['react'],
        description='set your last.fm nowplaying reactions',
        brief='lastfm reaction <emoji>',
        help='lastfm reaction :fire:'
    )
    async def lastfm_reaction(self, ctx: Context, reaction: discord.Emoji = None):

        if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you don't have a **last.fm** username linked")

        if reaction is None:
            await self.bot.db.execute('DELETE FROM lastfm_reactions WHERE user_id = %s', ctx.author.id)
            await self.bot.cache.cache_lastfm()
            return await ctx.send_success('successfully **cleared** your last.fm nowplaying reactions')            

        if reaction.id in set(await self.bot.db.fetch('SELECT emoji_id FROM lastfm_reactions WHERE user_id = %s', ctx.author.id)):
            return await ctx.send_error(f'your last.fm reaction is already set to {reaction}')
                    
        await self.bot.db.execute('INSERT INTO lastfm_reactions (user_id, emoji_id) VALUES (%s, %s)', ctx.author.id, reaction.id)
        await self.bot.cache.cache_lastfm()

        return await ctx.send_success(f'successfully **binded** your last.fm nowplaying reaction to {reaction}')


    @lastfm.group(
        name='embed',
        aliases=['mode'],
        description='set your custom last.fm nowplaying embed',
        brief='lastfm embed <code>',
        help='lastfm embed ...\n<:vile_reply:997487959093825646> **embed builder:** https://vilebot.xyz/embed\n<:vile_reply:997487959093825646> **variables:** https://vilebot.xyz/variables'
    )
    async def lastfm_embed(self, ctx: Context, *, code: str):


        if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you don't have a **last.fm** username linked")

        if code == 'clear':
            await self.bot.db.execute('DELETE FROM lastfm_embed WHERE user_id = %s', ctx.author.id)
            await self.bot.cache.cache_lastfm()
            return await ctx.send_success('successfully **reset** your custom last.fm embed')

        await self.bot.db.execute('INSERT INTO lastfm_embed (user_id, code) VALUES (%s, %s) ON DUPLICATE KEY UPDATE code = VALUES(code)', ctx.author.id, code)
        self.bot.cache.lastfm.setdefault(ctx.author, {})['embed'] = code
            
        return await ctx.send_success(f'successfully **binded** your custom last.fm embed code to:\n\n```{discord.utils.escape_markdown(code)}```')


    @lastfm_embed.command(
        name='code',
        aliases=['current'],
        description='view your current last.fm embed code'
    )
    async def lastfm_embed_code(self, ctx: Context, extras: Optional[str] = None):

        if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you don't have a **last.fm** username linked")
                
        code = await self.bot.db.fetchval('SELECT code FROM lastfm_embed WHERE user_id = %s', ctx.author.id)

        if not code:
            return await ctx.send_error("you don't have a custom **last.fm** embed")

        if extras is not None:
            if '--mobile' in extras.split():
                return await ctx.send(code, allowed_mentions=discord.AllowedMentions.none)

        return await ctx.reply(
            embed=discord.Embed(
                color=self.bot.color, 
                description=f'```{discord.utils.escape_markdown(code)}```'
            )
        )


    @lastfm_embed.command(
        name='copy',
        aliases=['steal'],
        description=f"copy another user's custom last.fm embed",
        brief='lastfm embed copy <user>',
        help='lastfm embed copy @glory#0007'
    )
    async def lastfm_embed_copy(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you don't have a **last.fm** username linked")

        if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id):
            return await ctx.send_error(f"{user.name} don't have a **last.fm** username linked")
                
        to_steal = await self.bot.db.fetchval('SELECT code FROM lastfm_embed WHERE user_id = %s', user.id)

        if not to_steal:
            return await ctx.send_error(f"{user.name} don't have a custom **last.fm** embed")

        await self.bot.db.execute('INSERT INTO lastfm_embed (user_id, code) VALUES (%s, %s) ON DUPLICATE KEY UPDATE code = VALUES(code)', ctx.author.id, theircode)
        self.bot.cache.lastfm.setdefault(ctx.author, {})['embed'] = code

        return await ctx.send_success(f'successfully **binded** your custom last.fm embed code to:\n\n```{discord.utils.escape_markdown(to_steal)}```')


    @lastfm.command(
        name='nowplaying',
        aliases=['np'],
        description='view your most recent scrobble'
    )
    async def lastfm_nowplaying(self, ctx: Context):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            data = await LastFM(username=lastfm_username).now_playing()

            if data is None:
                return await ctx.send_error('could not get information on the current track')

            custom_embed = await self.bot.db.fetchval('SELECT code FROM lastfm_embed WHERE user_id = %s', ctx.author.id)
            if custom_embed:

                custom_embed = utils.multi_replace(custom_embed, {
                    '{track}': data['track']['name'],
                    '{artist}': data['artist']['name'],
                    '{user}': str(ctx.author),
                    '{avatar}': ctx.author.display_avatar.url,
                    '{track.url}': data['track']['url'],
                    '{artist.url}': data['artist']['url'],
                    '{scrobbles}': data['scrobbles'],
                    '{track.image}': data['track']['image'],
                    '{lastfm.user}': lastfm_username,
                    '{artist.plays}': data['artist']['plays'],
                    '{track.plays}': data['track']['plays'],
                    '{track.lower}': data['track']['name'].lower(),
                    '{artist.lower}': data['artist']['name'].lower(),
                    '{track.hyper.lower}': data['track']['hyper.lower'],
                    '{artist.hyper.lower}': data['artist']['hyper.lower'],
                    '{track.hyper}': data['track']['hyper'],
                    '{artist.hyper}': data['artist']['hyper'],
                    '{track.color}': f"#{str(hex(data['track']['color'])).replace('0x', '')}",
                    '{artist.color}': f"#{str(hex(data['artist']['color'])).replace('0x', '')}"
                })

                msg = await ctx.reply(**await utils.to_object(custom_embed))
            else:
                embed = discord.Embed(
                    color=data['track']['color'], 
                    timestamp=datetime.now()
                )
                embed.set_author(
                    name=f'last.fm: {lastfm_username}', 
                    icon_url=ctx.author.display_avatar
                )
                embed.set_thumbnail(url=data['track']['image'])
                embed.description = f"***Listening to {data['track']['hyper']} by {data['artist']['hyper']}***"
                embed.add_field(
                    name='Album', 
                    value=data['track']['album'] or 'none'
                )
                embed.add_field(
                    name="Artist", 
                    value=data['artist']['hyper'] or 'none'
                )
                embed.set_footer(text=f"{int(data['track']['plays']):,} out of {int(data['scrobbles']):,} total scrobbles",)

                msg = await ctx.reply(embed=embed)

            custom_reactions = await self.bot.db.fetch('SELECT emoji_id FROM lastfm_reactions WHERE user_id = %s', ctx.author.id)
            if custom_reactions:
                for emoji_id in custom_reactions:
                    if self.bot.get_emoji(emoji_id) is not None:
                        await msg.add_reaction(self.bot.get_emoji(emoji_id))

                return

            await msg.add_reaction('🔥')
            await msg.add_reaction('🗑️')
            return

    @lastfm.command(
        name='topartists',
        aliases=['ta'],
        description='view your top artists'
    )
    async def lastfm_topartists(self, ctx: Context):

        async with ctx.handle_response():
            
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            data = await LastFM(username=lastfm_username).top_artists()

            rows = list()
            for artist in data:
                rows.append(f"`{artist['rank']}` **{artist['hyper']}** ({artist['plays']:,} plays)")

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Last.FM: {lastfm_username}',
                description='\n'.join(rows),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar
            )
            embed.set_footer(text=f"Accumulated plays: {sum([a['plays'] for a in data]):,}")
            embed.set_thumbnail(url=data[0]['image'])

            return await ctx.reply(embed=embed)


    @lastfm.command(
        name='topalbums',
        description='view your top albums'
    )
    async def lastfm_topalbums(self, ctx: Context):

        async with ctx.handle_response():
            
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            data = await LastFM(username=lastfm_username).top_albums()

            rows = list()
            for album in data:
                rows.append(f"`{album['rank']}` **{album['hyper']}** by **{album['artist.hyper']}** ({album['plays']:,} plays)")

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Last.FM: {lastfm_username}',
                description='\n'.join(rows),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar
            )
            embed.set_footer(text=f"Accumulated plays: {sum([a['plays'] for a in data]):,}")
            embed.set_thumbnail(url=data[0].get('image'))

            return await ctx.reply(embed=embed)


    @lastfm.command(
        name='toptracks',
        aliases=['tt', 'top'],
        description='view your top tracks'
    )
    async def lastfm_toptracks(self, ctx: Context):

        async with ctx.handle_response():
            
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            data = await LastFM(username=lastfm_username).top_tracks()

            rows = list()
            for track in data:
                rows.append(f"`{track['rank']}` **{track['hyper']}** by **{track['artist.hyper']}** ({track['plays']:,} plays)")

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Last.FM: {lastfm_username}',
                description='\n'.join(rows),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar
            )
            embed.set_footer(text=f"Accumulated plays: {sum([t['plays'] for t in data]):,}")
            embed.set_thumbnail(url=data[0].get('image'))

            return await ctx.reply(embed=embed)


    @lastfm.command(
        name='recenttracks',
        aliases=['rt', 'recent'],
        description='view your recent tracks'
    )
    async def lastfm_recenttracks(self, ctx: Context):

        async with ctx.handle_response():
            
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            data = await LastFM(username=lastfm_username).recent_tracks()

            rows = list()
            for track in data:
                rows.append(f"`{track['rank']}` **{track['hyper']}** by **{track['artist.hyper']}** ({track['plays']:,} plays)")

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Last.FM: {lastfm_username}',
                description='\n'.join(rows),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar
            )
            embed.set_footer(text=f"Accumulated plays: {sum([t['plays'] for t in data]):,}")
            embed.set_thumbnail(url=data[0].get('image'))

            return await ctx.reply(embed=embed)


    @lastfm.command(
        name='plays',
        description='view your play count for the current track'
    )
    async def lastfm_plays(self, ctx: Context):

        async with ctx.handle_response():

            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            data = await LastFM(username=lastfm_username).now_playing()

            msg = await ctx.send_success(f"you have **{data['track']['plays']:,}** plays for the track **{data['track']['hyper']}** by **{data['artist']['hyper']}**")
            custom_reactions = await self.bot.db.fetch('SELECT emoji_id FROM lastfm_reactions WHERE user_id = %s', ctx.author.id)
            if custom_reactions:
                for emoji_id in custom_reactions:
                    if self.bot.get_emoji(emoji_id) is not None:
                        await msg.add_reaction(self.bot.get_emoji(emoji_id))

                return

            await msg.add_reaction('🔥')
            await msg.add_reaction('🗑️')
            return


    @commands.command(
        name='nowplaying',
        aliases=['np', 'fm'],
        description='view your most recent scrobble'
    )
    async def nowplaying(self, ctx: Context):

        return await ctx.invoke(self.bot.get_command('lastfm nowplaying'))


    @commands.command(
        name='topartists',
        aliases=['ta'],
        description='view your top artists'
    )
    async def topartists(self, ctx: Context):
        
        return await ctx.invoke(self.bot.get_command('lastfm topartists'))


    @commands.command(
        name='topalbums',
        description='view your top albums'
    )
    async def topalbums(self, ctx: Context):
        
        return await ctx.invoke(self.bot.get_command('lastfm topalbums'))


    @commands.command(
        name='toptracks',
        aliases=['tt'],
        description='view your top tracks'
    )
    async def toptracks(self, ctx: Context):
        
        return await ctx.invoke(self.bot.get_command('lastfm toptracks'))


    @commands.command(
        name='recenttracks',
        aliases=['ra'],
        description='view your recent tracks'
    )
    async def recenttracks(self, ctx: Context):
        
        return await ctx.invoke(self.bot.get_command('lastfm recenttracks'))


    @commands.command(
        name='plays',
        description='view the play count for the current track'
    )
    async def plays(self, ctx: Context):
        
        return await ctx.invoke(self.bot.get_command('lastfm plays'))


    @lastfm.command(
        name='whoknows',
        aliases=['wk'],
        description='see who has listened to the given artist the most',
        brief='lastfm whoknows [artist]',
        help='lastfm whoknows lucki'
    )
    async def lastfm_whoknows(self, ctx: Context, *, artist: Optional[str] = None):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lf_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            if artist is None:
                nowplaying = await LastFM(username=lf_username).now_playing()
                if nowplaying is None or isinstance(nowplaying, str):
                    return await ctx.send_error('please provide a **valid** last.fm artist')

                artist = nowplaying['artist']['name']

            tuples = list()
            rows = list()
            num = 0
            for user_id, lastfm_username in await self.bot.db.execute('SELECT user_id, lastfm_username FROM lastfm WHERE user_id IN %s', list(map(lambda m: m.id, ctx.guild.members))):
                plays = await self.bot.db.fetchval('SELECT play_count FROM lastfm_playcount WHERE user_id = %s AND artist = %s', user_id, artist) or 0
                if plays != 0:
                    tuples.append((str(ctx.guild.get_member(user_id)), lastfm_username, plays))

            if len(tuples) == 0:
                return await ctx.send_error('nobody I know of has listened to that artist')

            for t in reversed(sorted(tuples, key=lambda t: t[2])[:10]):
                num += 1
                rows.append(f'`{num}` [**{t[0]}**](https://last.fm/user/{t[1]}) - **{t[2]:,} plays**')

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Who Knows {artist}',
                description='\n'.join(rows),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar
            )
            embed.set_footer(text=f"Accumulated plays: {sum([t[2] for t in reversed(sorted(tuples, key=lambda t: t[2])[:10])]):,}")
            embed.set_thumbnail(url=(await LastFM(username=lf_username, artist=artist).artist_info())['artist']['image'])

            return await ctx.reply(embed=embed)

    @lastfm.command(
        name='globalwhoknows',
        aliases=['gwk'],
        description='see who has listened to the given artist the most globally',
        brief='lastfm globalwhoknows [artist]',
        help='lastfm globalwhoknows lucki'
    )
    async def lastfm_globalwhoknows(self, ctx: Context, *, artist: Optional[str] = None):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lf_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            if artist is None:
                nowplaying = await LastFM(username=lf_username).now_playing()
                if nowplaying is None or isinstance(nowplaying, str):
                    return await ctx.send_error('please provide a **valid** last.fm artist')

                artist = nowplaying['artist']['name']

            tuples = list()
            rows = list()
            num = 0
            for user_id, lastfm_username in await self.bot.db.execute('SELECT user_id, lastfm_username FROM lastfm WHERE user_id IN %s', list(map(lambda u: u.id, self.bot.users))):
                plays = await self.bot.db.fetchval('SELECT play_count FROM lastfm_playcount WHERE user_id = %s AND artist = %s', user_id, artist) or 0
                if plays != 0:
                    tuples.append((str(self.bot.get_user(user_id)), lastfm_username, plays))

            if len(tuples) == 0:
                return await ctx.send_error('nobody I know of has listened to that artist')

            for t in reversed(sorted(tuples, key=lambda t: t[2])[:10]):
                num += 1
                rows.append(f'`{num}` [**{t[0]}**](https://last.fm/user/{t[1]}) - **{t[2]:,} plays**')

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Who Knows {artist} (Global)',
                description='\n'.join(rows),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar
            )
            embed.set_footer(text=f"Accumulated plays: {sum([t[2] for t in reversed(sorted(tuples, key=lambda t: t[2])[:10])]):,}")
            embed.set_thumbnail(url=(await LastFM(username=lf_username, artist=artist).artist_info())['artist']['image'])

            return await ctx.reply(embed=embed)


    @lastfm.command(
        name='whoknowstrack',
        aliases=['wkt'],
        description='see who has listened to the given track the most',
        brief='lastfm whoknows [artist | track]',
        help='lastfm whoknows lucki | new drank'
    )
    async def lastfm_whoknowstrack(self, ctx: Context, *, track: Optional[str] = None):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lf_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            if track is None:
                nowplaying = await LastFM(username=lf_username).now_playing()
                if nowplaying is None or isinstance(nowplaying, str):
                    return await ctx.send_error('please provide a **valid** last.fm artist')

                artist, track = nowplaying['artist']['name'], nowplaying['track']['name']

            else:
                if len(track.split(' | ')) == 1 or len(track.split(' | ')) > 2:
                    return await ctx.send_error('please provide a **valid** track')

                artist, track = track.split(' | ')

            tuples = list()
            rows = list()
            num = 0
            for user_id, lastfm_username in await self.bot.db.execute('SELECT user_id, lastfm_username FROM lastfm WHERE user_id IN %s', list(map(lambda m: m.id, ctx.guild.members))):
                plays = await LastFM(username=lastfm_username, artist=artist, track=track).track_plays()
                if plays != 0:
                    tuples.append((str(ctx.guild.get_member(user_id)), lastfm_username, plays))

            if len(tuples) == 0:
                return await ctx.send_error('nobody I know of has listened to that track')

            for t in reversed(sorted(tuples, key=lambda t: t[2])[:10]):
                num += 1
                rows.append(f'`{num}` [**{t[0]}**](https://last.fm/user/{t[1]}) - **{t[2]:,} plays**')

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Who Knows Track {track}',
                description='\n'.join(rows),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar
            )
            embed.set_footer(text=f"Accumulated plays: {sum([t[2] for t in reversed(sorted(tuples, key=lambda t: t[2])[:10])]):,}")
            embed.set_thumbnail(url=(await LastFM(username=lf_username, artist=artist).artist_info())['artist']['image'])

            return await ctx.reply(embed=embed)


    @lastfm.command(
        name='globalwhoknowstrack',
        aliases=['gwkt'],
        description='see who has listened to the given track the most globally',
        brief='lastfm globalwhoknows [artist | track]',
        help='lastfm globalwhoknows lucki | new drank'
    )
    async def lastfm_globalwhoknowstrack(self, ctx: Context, *, track: Optional[str] = None):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lf_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            if track is None:
                nowplaying = await LastFM(username=lf_username).now_playing()
                if nowplaying is None or isinstance(nowplaying, str):
                    return await ctx.send_error('please provide a **valid** last.fm artist')

                artist, track = nowplaying['artist']['name'], nowplaying['track']['name']

            else:
                if len(track.split(' | ')) == 1 or len(track.split(' | ')) > 2:
                    return await ctx.send_error('please provide a **valid** track')

                artist, track = track.split(' | ')

            tuples = list()
            rows = list()
            num = 0
            for user_id, lastfm_username in await self.bot.db.execute('SELECT user_id, lastfm_username FROM lastfm WHERE user_id IN %s', list(map(lambda u: u.id, self.bot.users))):
                plays = await LastFM(username=lastfm_username, artist=artist, track=track).track_plays()
                if plays != 0:
                    tuples.append((str(self.bot.get_user(user_id)), lastfm_username, plays))

            if len(tuples) == 0:
                return await ctx.send_error('nobody I know of has listened to that track')

            for t in reversed(sorted(tuples, key=lambda t: t[2])[:10]):
                num += 1
                rows.append(f'`{num}` [**{t[0]}**](https://last.fm/user/{t[1]}) - **{t[2]:,} plays**')

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Who Knows Track {track} (Global)',
                description='\n'.join(rows),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar
            )
            embed.set_footer(text=f"Accumulated plays: {sum([t[2] for t in reversed(sorted(tuples, key=lambda t: t[2])[:10])]):,}")
            embed.set_thumbnail(url=(await LastFM(username=lf_username, artist=artist).artist_info())['artist']['image'])

            return await ctx.reply(embed=embed)


    @lastfm.command(
        name='cover',
        description='view the album cover for the currently playing song'
    )
    async def lastfm_cover(self, ctx: Context, user: Union[discord.Member, discord.User] = commands.Author):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id)
            data = await LastFM(username=lastfm_username).now_playing()

            albuminfo = await LastFM(username=lastfm_username, artist=data['artist']['name'], album=data['track']['album']).album_info()
            
            embed = discord.Embed(color=albuminfo['album']['color'])
            embed.set_footer(text=albuminfo['album']['name'])

            return await ctx.reply(
                embed=embed,
                file=await utils.file(albuminfo['album']['image'])
            )


    @lastfm.command(
        name='recommendation',
        aliases=['recommend', 'suggest'],
        description='recommend a random artist',
        brief='!lastfm recommendation <user>',
        help='!lastfm recommendation @glory#0007'
    )
    async def lastfm_recommendation(self, ctx: Context, user: Union[discord.Member, discord.User] = commands.Author):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id):
                return await ctx.send_error(f"{'you' if user == ctx.author else user.name} don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id)
            data = await LastFM(username=lastfm_username).top_tracks()

            return await ctx.reply(random.choice(data)['artist'])


    @lastfm.command(
        name='lyrics',
        description='get the lyrics for the current track'
    )
    async def lastfm_lyrics(self, ctx: Context, user: Union[discord.Member, discord.User] = commands.Author):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id):
                return await ctx.send_error(f"{'you' if user == ctx.author else user.name} don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id)
            data = await LastFM(username=lastfm_username).now_playing()

            return await ctx.invoke(self.bot.get_command('lyrics'), song=f"{data['track']['name']} by {data['artist']['name'].replace('Lucky Twice', 'Lucki')}")


    @lastfm.command(
        name='youtube',
        aliases=['yt'],
        description='get the youtube video for the current track'
    )
    async def lastfm_youtube(self, ctx: Context, user: Union[discord.Member, discord.User] = commands.Author):

        async with ctx.handle_response():
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id):
                return await ctx.send_error(f"{'you' if user == ctx.author else user.name} don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id)
            data = await LastFM(username=lastfm_username).now_playing()

            return await ctx.invoke(self.bot.get_command('youtube'), query=f"{data['track']['name']} by {data['artist']['name'].replace('Lucky Twice', 'Lucki')}")


    @lastfm.command(
        name='collage',
        aliases=['chart'],
        description='generate a collage of your top albums',
        brief='lastfm collage [size 3x3/6x6/9x9] [timeperiod 7day/1month/3month/6month/12month/overall]',
        help='lastfm collage 3x3 overall'
    )
    async def lastfm_chart(self, ctx: Context, size: Literal['3x3', '6x6', '9x9'] = '3x3', timeperiod: Literal['7day', '1month', '3month', '6month', '12month', 'overall'] = 'overall'):
        
        async with ctx.handle_response():
            
            if not await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.send_error("you don't have a **last.fm** username linked")

            lastfm_username = await self.bot.db.fetchval('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
            
            chart = await RivalAPI(self.bot.config.authorization.rival_api).lastfm_chart(
                username=lastfm_username,
                chart_size=size,
                timeperiod=timeperiod
            )
            return await ctx.reply(
                content=f"Successfully generated a **{size} {timeperiod} last.fm collage** for {lastfm_username}",
                file=chart
            )


async def setup(bot: Vile):
    await bot.add_cog(LastFM_Integration(bot))
