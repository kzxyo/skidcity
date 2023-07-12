import datetime
from typing import Optional
from utilities.managers import Context, Wrench, Writing
from utilities.lair import Lair
from discord.ext.commands import command, group, Author
from discord import User, Member
from discord import Embed
from utilities import config
from utilities.general.converters import CollageSize, cMember


class Request:
    def __init__(self, user: str, bot: Lair, **kwargs) -> None:
        self.user = user
        self.bot = bot
        self.url = "http://ws.audioscrobbler.com/2.0/"

    async def get(self, params: dict):
        tries = 0
        params["api_key"] = "57f7afd71c1758f9beecf112e7971de0"
        params['format'] = 'json'
        params['user'] = self.user
        max_tries = 5
        while tries < max_tries:
            try:
                response = await self.bot.session.request("GET", self.url, params=params)
                if not response:
                    tries += 1
                    raise Exception("No response received")
                return response
            except:
                raise
            
        

class LastFM(Wrench):

    @group(name='lastfm', aliases=['lf'], brief='LastFM commands')
    async def lastfm(self, ctx: Context):
        pass

    @lastfm.command(name='set', aliases=['sign'], brief='Set your LastFM username')
    async def set(self, ctx: Context, *, username: str):
        async with ctx.typing():
            embed = await ctx.main(f'Configuring your LastFM username to `{username}`.')
            await self.bot.db.execute('INSERT INTO lastfm (user_id, username) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET username = $2', ctx.author.id, username)
            await embed.edit(
                content="Indexing your library. This may take a while...",
            )
            await self.bot.db.execute('DELETE FROM lastfm_artists_index WHERE user_id = $1', ctx.author.id)
            request = Request(username, self.bot)
            artists = await request.get(
                {'method': 'user.gettopartists', 'limit': 1000}
            )
            playcount = artists.topartists.artist[0].playcount
            name = artists.topartists.artist[0].name
            await self.bot.db.execute('INSERT INTO lastfm_artists_index (user_id, artist, playcount) VALUES ($1, $2, $3)', ctx.author.id, name, int(playcount))
            await self.bot.db.execute('DELETE FROM lastfm_track_index WHERE user_id = $1', ctx.author.id)
            tracks = await request.get(
                {'method': 'user.gettoptracks', 'limit': 1000}
            )
            playcount = tracks.toptracks.track[0].playcount
            name = tracks.toptracks.track[0].name
            await self.bot.db.execute('INSERT INTO lastfm_track_index (user_id, track, playcount) VALUES ($1, $2, $3)', ctx.author.id, name, int(playcount))
            await embed.edit(
                embed=Embed(
                description=f"> Successfully configured your LastFM username to `{username}`.",
                color=config.Color.main
                )
            )


    @lastfm.command(
        name='collage', aliases=['c'], brief='Get your LastFM collage.'
    )
    async def collage(self, ctx: Context, member: Optional[cMember] = None, size: CollageSize = "1x1", period: str = "month"):
        async with ctx.typing():
            username = await self.bot.db.fetchval('SELECT username FROM lastfm WHERE user_id = $1', member.id)
            if not username:
                return await ctx.error(f"{member.mention} does not have a LastFM username set.")
            request = await self.bot.session.get("https://api.lair.one/lastfm/collage", params={"user": username, "size": size, "period": period}, headers={"Authorization": config.LairAPIKey})
            if not request.status == 200:
                return await ctx.error(f"An error occurred while fetching the collage.")
            request = await request.json()
            if request:
                embed = Embed(
                    title=f"{member.name}'s LastFM collage",
                    color=config.Color.main,
                    timestamp=datetime.datetime.now()
                )
                embed.set_image(url=request.get("url", None))
                return await ctx.reply(embed=embed)


async def setup(bot: Lair):
    await bot.add_cog(LastFM(bot))