import discord
from discord.ext import commands
import aiohttp

color = 0x2b2d31


class LastFM(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.group(
        invoke_without_command=True,
        name='lastfm',
        description='Interact with Last.fm using void',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: whoknows',
        aliases=['lfm', 'lf']
    )
    async def lastfm(self, ctx):
        await ctx.send_help(ctx.command)

    @lastfm.group(
        name='set',
        description='Connect to your Last.fm account',
        brief='username',
        usage=
        'Syntax: (username)\n'
        'Example: void',
        aliases=['link']
    )
    async def lastfm_set(self, ctx, username):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getInfo&user={username}&api_key=1b6567ff20617da36b3f7e5b335651c8&format=json') as response:
                check = await response.json()
                if not check:
                    await ctx.success(f'[{username}](https://last.fm/user/{username}) is not a valid **LastFM** username')
                else:
                    await self.bot.db.execute('INSERT INTO lastfm VALUES ($1, $2) ON CONFLICT (author) DO UPDATE SET username = EXCLUDED.username', ctx.author.id, username)
                    await ctx.success(f'Your **username** has been set to [{username}](https://last.fm/user/{username})')
    
    @commands.command(
        name='nowplaying',
        description="lastfm",
        usage='Syntax: ',
        aliases=['np', 'fm']
    )
    async def nowplaying(self,ctx):
        username = await self.bot.db.fetchval("SELECT username FROM lastfm WHERE author = $1", ctx.author.id)
        if username:
            track_info = await LastFM.now_playing()
            if track_info is None:
                await ctx.send(f"{username} is not currently playing anything.")
            else:
                artist_name = track_info['artist']['name']
                track_name = track_info['track']['name']
                await ctx.send(f"{username} is currently playing {track_name} by {artist_name}.")
                
async def setup(bot):
    await bot.add_cog(LastFM(bot))
