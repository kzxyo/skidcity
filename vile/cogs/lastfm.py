from inspect import trace
from re import A
import discord, os, sys, asyncio, aiohttp, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class lastfm(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        #
        self.done = utils.emoji("done")
        self.fail = utils.emoji("fail")
        self.warn = utils.emoji("warn")
        self.reply = utils.emoji("reply")
        self.dash = utils.emoji("dash")
        #
        self.success = utils.color("done")
        self.error = utils.color("fail")
        self.warning = utils.color("warn")
        #
        self.av = "https://cdn.discordapp.com/attachments/989422588340084757/1008195005317402664/vile.png"

    @commands.Cog.listener()
    async def on_message(self, message):

        customcmd=await self.bot.db2.execute('SELECT name FROM lastfm_command WHERE user_id = %s', ctx.author.id, one_value=True)
        if customcmd:
            async with message.channel.typing():
                context = await self.bot.get_context(message)
                await context.invoke(self.bot.get_command("fm"))

    @commands.hybrid_group(aliases=["lf", "lfm"], invoke_without_command=True)
    async def lastfm(self, ctx):

        embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        embed.set_author(name="lastfm", icon_url=self.bot.user.avatar)
        embed.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** connect your last.fm account to vile\n{self.reply} **aliases:** lf, lfm\n{self.reply} **sub commands:** set, reset",
        )
        embed1 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        embed1.set_author(name="lastfm", icon_url=self.bot.user.avatar)
        embed1.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** connect your last.fm account to vile\n{self.reply} **aliases:** lf, lfm\n{self.reply} **sub commands:** set, reset",
        )
        embed1.add_field(
            name=f"{self.dash} Setup",
            value=f"{self.reply} Create a [lastfm](https://www.last.fm/home) acccount\n{self.reply} Connect your streaming platform to lastfm from [here](https://www.last.fm/settings/applications)\n{self.reply} You're good to go, start scrobbling tracks and get it's statistics from vile",
            inline=False,
        )
        embed1.set_footer(
            text="1/2",
            icon_url=None,
        )
        embed2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        embed2.set_author(name="lastfm", icon_url=self.bot.user.avatar)
        embed2.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** connect your last.fm account to vile\n{self.reply} **aliases:** lf, lfm\n{self.reply} **sub commands:** set, reset",
        )
        embed2.add_field(
            name=f"{self.dash} Sub Cmds",
            value=f"```YAML\n,lastfm set <username> - sets your lastfm username\n,lastfm reset - unlinks your previous lastfm username```",
            inline=False,
        )
        embed2.add_field(
            name=f"{self.dash} Others",
            value=f"```YAML\n{', '.join([c.name for c in self.bot.get_command('lf').commands])}```",
            inline=False,
        )
        embed2.set_footer(
            text="2/2",
            icon_url=None,
        )
        from modules import paginator as pg

        paginator = pg.Paginator(
            self.bot, [embed1, embed2], ctx, timeout=30, invoker=None
        )
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        await paginator.start()

    @lastfm.command(name="set")
    async def lastfm_set(self, ctx, username=None):

        if not username:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** you must provide a **last.fm** username",
                )
            )
            
        try:
            if await self.bot.db2.execute('SELECT * FROM lastfm WHERE user_id = %s', ctx.author.id):
                currentfm=await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id)
                if currentfm == username:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=self.warning,
                            description=f"{self.warn} {ctx.author.mention}**:** your **last.fm** profile is already set to **{username}**"
                        )
                    )
            
            await self.bot.db2.execute('INSERT INTO lastfm (user_id, lastfm_username) VALUES (%s, %s)', ctx.author.id, username)
        except:
            pass

        await ctx.reply(":thumbsup:")


    @lastfm.command(name="reset")
    async def lastfm_reset(self, ctx):

        await self.bot.db2.execute('DELETE FROM lastfm WHERE user_id = %s', ctx.author.id)
        await ctx.reply(":thumbsup:")
    @lastfm.command(name="customcommand", aliases=["cc", "customcmd"])
    async def lastfm_customcommand(self, ctx, *, name: str = None):

        if name == "none":
            await self.bot.db2.execute('DELETE FROM lastfm_command WHERE user_id = %s', ctx.author.id)
            return await ctx.reply(":thumbsup:")
        if not name:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** you must provide a **name**",
                )
            )

        customcmd=await self.bot.db2.execute('SELECT name FROM lastfm_command WHERE user_id = %s', ctx.author.id) 
        if customcmd == name:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** your **custom** command is already set to **{name}**",
                )
            )

        await self.bot.db2.execute('INSERT INTO lastfm_command (user_id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = %s', ctx.author.id, name, name)

        await ctx.reply(":thumbsup:")


    @lastfm.command(
        name="reaction", 
        aliases=["react", "customreact"],
        description='set your nowplaying reactions',
        syntax=',lf reaction [emoji]',
        example=',lf reaction :fireeee:'
    )
    async def lastfm_reaction(
        self, ctx, reaction: discord.Emoji = None
    ):

        if not reaction:
            await self.bot.db2.execute('DELETE FROM lastfm_reactions WHERE user_id = %s', ctx.author.id)
            return await ctx.reply(":thumbsup:")

        reactions = await self.bot.db2.execute('SELECT reaction FROM lastfm_reactions WHERE user_id = %s', ctx.author.id, as_list=True)
        
        if reaction.id in reactions:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** your **custom** command is already set to **{reaction.name}**",
                )
            )
                    
        await self.bot.db2.execute('INSERT INTO lastfm_reactions (user_id, reaction) VALUES (%s, %s)', ctx.author.id, reaction.id)

        return await ctx.reply(":thumbsup:")

    @lastfm.group(name="embed", invoke_without_command=True)
    async def lastfm_embed(self, ctx, *, code: str = None):

        if not code:

            subcmds = "\nartistName\nartistURL\ntrackName\ntrackURL\nimage\nalbum\nfmUser\nplayCount\ntotalScrobbles"
            subcmds = f"```{subcmds}```"
            variableusage = "${variable}"
            note1 = discord.Embed(color=utils.color("main"), timestamp=datetime.now())
            note1.set_author(
                name=f"lastfm embed", icon_url=self.bot.user.display_avatar
            )
            note1.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** manage your last.fm embed using json\n{self.reply} **variable usage:** {variableusage}\n{self.reply} **sub commands:** code",
            )
            note1.add_field(name=f"{self.dash} Variables", value=subcmds, inline=False)
            note1.set_footer(
                text=f"lastfm",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            return await ctx.reply(embed=note1)

        async with ctx.channel.typing():

            if not await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )

            if code == "none":
                await self.bot.db2.execute('DELETE FROM lastfm_embed WHERE user_id = %s', ctx.author.id)

            else:
                await self.bot.db2.execute('INSERT INTO lastfm_embed (user_id, code) VALUES (%s, %s) ON DUPLICATE KEY UPDATE code = %s', ctx.author.id, code, code)

        await ctx.reply(":thumbsup:")

    @lastfm_embed.command(name="code")
    async def lastfm_embed_code(self, ctx):

        async with ctx.channel.typing():

            if not await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
            if not await self.bot.db2.execute('SELECT code FROM lastfm_embed WHERE user_id = %s', ctx.author.id):
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **custom** embed set",
                    )
                )
                
            code=await self.bot.db2.execute('SELECT code FROM lastfm_embed WHERE user_id = %s', ctx.author.id, one_value=True)

        if '--mobile' not in ctx.message.content.split():
            return await ctx.reply(
                embed=discord.Embed(
                    color=0x2F3136, description=f"```{code}```"
                )
            )
        return await ctx.reply(code)

    @lastfm_embed.command(name="copy")
    async def lastfm_embed_copy(self, ctx, user: discord.User | discord.Member):

        async with ctx.channel.typing():

            if not await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id):
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )

            if not await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id):
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: {user.name} doesn't have a **last.fm** account connected",
                    )
                )

            theircode=await self.bot.db2.execute('SELECT code FROM lastfm_embed WHERE user_id = %s', user.id)
            if not theircode:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.bot.color,
                        description=f"{self.fail} {ctx.author.mention}**:** {user.name} doesn't have a  **custom** embed"
                    )
                )

            await self.bot.db2.execute('INSERT INTO lastfm_embed (user_id, code) VALUES (%s, %s) ON DUPLICATE KEY UPDATE code = %s', ctx.author.id, theircode, theircode)
                
        await ctx.reply(":thumbsup:")

    @lastfm.command(name="chart", aliases=["collage"])
    async def lastfm_chart(
        self,
        ctx,
        time: typing.Literal["week", "month"] = "week",
        size: typing.Literal["2x2", "3x3", "5x5"] = "3x3",
    ):

        async with ctx.channel.typing():
            user=await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id, one_value=True)
            
            if not user:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )

            file = await utils.file(
                f"https://lastfm-collage.herokuapp.com/collage?username={user}&method=album&period={'7day' if time == 'week' else '1month'}&column={size.split('x')[0]}&row={size.split('x')[1]}&caption=true&scrobble=true",
                "fmchart.png",
            )
        await ctx.send(
            content=f"{'7 day' if time == 'week' else '30 day'} chart for {user}",
            file=file,
        )

    @lastfm.command(name="nowplaying", aliases=["np", "fm"])
    async def lastfm_nowplaying(self, ctx):

        await ctx.invoke(self.bot.get_command("fm"))

    @lastfm.command(name="topartists", aliases=["ta"])
    async def lastfm_topartists(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=10"
                ) as ret:
                    topartists = await ret.json()

            rows = []
            async for artist in utils.aiter(topartists["topartists"]["artist"]):
                rows.append(
                    f"`{artist['@attr']['rank']}` [**{artist['name']}**](https://www.last.fm/music/{artist['name'].replace(' ', '+')}) — {int(artist['playcount']):,}\n"
                )

        await ctx.reply(
            embed=discord.Embed(color=utils.color("main"), description="".join(rows))
            .set_author(name=f"lastfm: {fmuser}", icon_url=ctx.author.display_avatar)
            .set_thumbnail(url=artist["image"][3]["#text"])
            .set_footer(text="top artists")
        )

    @lastfm.command(name="topalbums")
    async def lastfm_topalbums(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=10"
                ) as ret:
                    topalbums = await ret.json()

            rows = []
            async for album in utils.aiter(topalbums["topalbums"]["album"]):
                rows.append(
                    f"`{album['@attr']['rank']}` [**{album['name']}**]({album['url']}) — {int(album['playcount']):,}\n"
                )

        await ctx.reply(
            embed=discord.Embed(color=utils.color("main"), description="".join(rows))
            .set_author(name=f"lastfm: {fmuser}", icon_url=ctx.author.display_avatar)
            .set_thumbnail(url=album["image"][3]["#text"])
            .set_footer(text="top albums")
        )

    @lastfm.command(name="toptracks", aliases=["tt"])
    async def lastfm_toptracks(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=10"
                ) as ret:
                    toptracks = await ret.json()

            rows = []
            async for track in utils.aiter(toptracks["toptracks"]["track"]):
                rows.append(
                    f"`{track['@attr']['rank']}` [**{track['name']}**]({track['url']}) — {int(track['playcount']):,}\n"
                )

        await ctx.reply(
            embed=discord.Embed(color=utils.color("main"), description="".join(rows))
            .set_author(name=f"lastfm: {fmuser}", icon_url=ctx.author.display_avatar)
            .set_thumbnail(url=track["image"][3]["#text"])
            .set_footer(text="top tracks")
        )

    @lastfm.command(name="recenttracks", aliases=["rt"])
    async def lastfm_recenttracks(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=10"
                ) as ret:
                    recenttracks = await ret.json()

            rows = []
            rank = 0
            async for track in utils.aiter(recenttracks["recenttracks"]["track"]):
                rank += 1
                rows.append(f"`{rank}` [**{track['name']}**]({track['url']}) — ?\n")

        await ctx.reply(
            embed=discord.Embed(color=utils.color("main"), description="".join(rows))
            .set_author(name=f"lastfm: {fmuser}", icon_url=ctx.author.display_avatar)
            .set_thumbnail(url=track["image"][3]["#text"])
            .set_footer(text="recent tracks")
        )

    @lastfm.command(name="plays")
    async def lastfm_plays(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=1"
                ) as ret:
                    track = await ret.json()
                    track = track["recenttracks"]["track"][0]

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&username={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&artist={track['artist']['#text']}&track={track['name']}&format=json&autocorrect=1"
                ) as ret:
                    ginfo = await ret.json()
                    playcount = ginfo["track"]["userplaycount"]

        msg = await ctx.reply(
            embed=discord.Embed(
                color=utils.color("done"),
                description=f"{self.done} {ctx.author.mention}**:** {'you' if user == ctx.author else user.name} {'have' if user == ctx.author else 'has'} **{int(playcount):,}** plays for the track [**{track['name']}**]({track['url']}) by [**{track['artist']['#text']}**]({ginfo['track']['artist']['url']})",
            )
        )
        try:
            if (
                not utils.read_json("fmuser")[str(ctx.author.id)]["reaction"]
                or not utils.read_json("fmuser")[str(ctx.author.id)]["reaction"][0]
            ):
                await msg.add_reaction("👍")
                await msg.add_reaction("👎")
            else:
                async for reaction in utils.aiter(
                    utils.read_json("fmuser")[str(ctx.author.id)]["reaction"]
                ):
                    x = self.bot.get_emoji(reaction)
                    await msg.add_reaction(x)
        except:
            pass

    @lastfm.command(name="userinfo", aliases=["ui"])
    async def lastfm_userinfo(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json"
                ) as ret:
                    info = await ret.json()

            i = info["user"]
            registered = datetime.fromtimestamp(i["registered"]["#text"])
            registered = utils.moment(registered)
            name = i["name"]
            age = int(i["age"])
            subscriber = f"{'false' if i['subscriber'] == '0' else 'true'}"
            realname = i["realname"]
            playcount = int(i["playcount"])
            artistcount = int(i["artist_count"])
            playlists = int(i["playlists"])
            trackcount = int(i["track_count"])
            albumcount = int(i["album_count"])
            image = i["image"][3]["#text"]

            embed = discord.Embed(color=utils.color("main"))
            embed.set_footer(text=f"{playcount:,} total scrobbles")
            embed.set_thumbnail(url=image)
            embed.set_author(name=f"{name} ( {realname} )", icon_url=image)
            embed.add_field(
                name=f"{self.dash} Count",
                value=f"{self.reply} **artists:** {artistcount:,}\n{self.reply} **plays:** {playcount:,}\n{self.reply} **tracks:** {trackcount:,}\n{self.reply} **albums:** {albumcount:,}",
            )
            embed.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **name:** {realname}\n{self.reply} **registered:** {registered} ago\n{self.reply} **subscriber:** {subscriber}\n{self.reply} **age:** {age:,}",
            )

        await ctx.reply(embed=embed)

    @commands.hybrid_command(aliases=["np", "nowplaying"])
    async def fm(self, ctx, user: discord.User | discord.Member = None):

        uu = ctx.author if not user else user
        async with ctx.channel.typing():
            user = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', uu.id, one_value=True)
            if not user:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )

            res = await self.bot.session.get(
                f"http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={user}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=1"
            )
            track = await res.json()
            track = track["recenttracks"]["track"][0]
            l2 = await self.bot.session.get(
                f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&username={user}&api_key=43693facbb24d1ac893a7d33846b15cc&artist={track['artist']['#text'].replace(' ', '+')}&track={track['name'].replace(' ', '+')}&format=json&autocorrect=1"
            )
            l2 = await l2.json()

            try:
                playCount = "?"
                if l2["track"]["userplaycount"] != None:
                    playCount = l2["track"]["userplaycount"]
            except:
                playCount = "?"

            artist = track["artist"]["#text"]
            artistURL = f"https://www.last.fm/music/undefined"
            trackName = track["name"]
            album = track["album"]["#text"]
            # total = track['@attr']['total']
            artistName = track["artist"]["#text"].replace(" ", "+")
            trackURL = f"https://www.last.fm/music/{artistName}/_/{trackName}".replace(
                " ", "+"
            )
            if playCount != "?":
                r1 = f"{int(playCount):,}"
            else:
                r1 = playCount
            fmuser = user
            image = track["image"][3]["#text"]
            playCount = r1
            totalScrobbles = (
                f"{int((await res.json())['recenttracks']['@attr']['total']):,}"
            )
            
            customembedcode=await self.bot.db2.execute('SELECT code FROM lastfm_embed WHERE user_id = %s', uu.id, one_value=True)
            
            if customembedcode:

                x = customembedcode
                x = (
                    x.replace("{artistName}", artist)
                    .replace("{artistURL}", artistURL)
                    .replace("{trackName}", trackName)
                    .replace("{album}", album)
                    .replace("{trackURL}", trackURL)
                    .replace("{fmUser}", fmuser)
                    .replace("{image}", image)
                    .replace("{playCount}", playCount)
                    .replace("{totalScrobbles}", totalScrobbles)
                )

                objects = await utils.to_object(x)
                msg = await ctx.reply(**objects)
            else:
                embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
                embed.set_author(name=f"last.fm: {fmuser}", icon_url=uu.display_avatar)
                embed.set_thumbnail(url=track["image"][3]["#text"])
                embed.description = f'***Listening to [{trackName}]({trackURL.replace(" ", "+")}) by [{artist}]({artistURL})***'
                embed.add_field(name="Album", value=album)
                embed.add_field(name="Artist", value=f"[{artist}]({artistURL})")
                embed.set_footer(
                    text=f"{playCount} out of {totalScrobbles} total scrobbles",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )

                msg = await ctx.reply(embed=embed)

        try:
            if not self.bot.db("fmuser")[str(ctx.author.id)]["reaction"]:
                await msg.add_reaction("👍")
                await msg.add_reaction("👎")
            else:
                async for reaction in utils.aiter(
                    self.bot.db("fmuser")[str(ctx.author.id)]["reaction"]
                ):
                    x = self.bot.get_emoji(reaction)
                    await msg.add_reaction(x)
        except:
            pass

    @commands.command(aliases=["fmchart"])
    @commands.max_concurrency(1, commands.BucketType.default, wait=True)
    async def collage(
        self,
        ctx,
        time: typing.Literal["week", "month"] = "week",
        size: typing.Literal["2x2", "3x3", "5x5"] = "3x3",
    ):

        async with ctx.channel.typing():
            user = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
            file = await utils.file(
                f"https://lastfm-collage.herokuapp.com/collage?username={user}&method=album&period={'7day' if time == 'week' else '1month'}&column={size.split('x')[0]}&row={size.split('x')[1]}&caption=true&scrobble=true",
                "fmchart.png",
            )
        await ctx.send(
            content=f"{'7 day' if time == 'week' else '30 day'} chart for {user}",
            file=file,
        )

    @commands.command(aliases=["ta"])
    async def topartists(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=10"
                ) as ret:
                    topartists = await ret.json()

            rows = []
            async for artist in utils.aiter(topartists["topartists"]["artist"]):
                rows.append(
                    f"`{artist['@attr']['rank']}` [**{artist['name']}**](https://www.last.fm/music/{artist['name'].replace(' ', '+')}) — {int(artist['playcount']):,}\n"
                )

        await ctx.reply(
            embed=discord.Embed(color=utils.color("main"), description="".join(rows))
            .set_author(name=f"lastfm: {fmuser}", icon_url=ctx.author.display_avatar)
            .set_thumbnail(url=artist["image"][3]["#text"])
            .set_footer(text="top artists")
        )

    @commands.command()
    async def topalbums(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=10"
                ) as ret:
                    topalbums = await ret.json()

            rows = []
            async for album in utils.aiter(topalbums["topalbums"]["album"]):
                rows.append(
                    f"`{album['@attr']['rank']}` [**{album['name']}**]({album['url']}) — {int(album['playcount']):,}\n"
                )

        await ctx.reply(
            embed=discord.Embed(color=utils.color("main"), description="".join(rows))
            .set_author(name=f"lastfm: {fmuser}", icon_url=ctx.author.display_avatar)
            .set_thumbnail(url=album["image"][3]["#text"])
            .set_footer(text="top albums")
        )

    @commands.command(aliases=["tt"])
    async def toptracks(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=10"
                ) as ret:
                    toptracks = await ret.json()

            rows = []
            async for track in utils.aiter(toptracks["toptracks"]["track"]):
                rows.append(
                    f"`{track['@attr']['rank']}` [**{track['name']}**]({track['url']}) — {int(track['playcount']):,}\n"
                )

        await ctx.reply(
            embed=discord.Embed(color=utils.color("main"), description="".join(rows))
            .set_author(name=f"lastfm: {fmuser}", icon_url=ctx.author.display_avatar)
            .set_thumbnail(url=track["image"][3]["#text"])
            .set_footer(text="top tracks")
        )

    @commands.command(aliases=["rt"])
    async def recenttracks(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=10"
                ) as ret:
                    recenttracks = await ret.json()

            rows = []
            async for track in utils.aiter(recenttracks["recenttracks"]["track"]):
                rows.append(
                    f"`{track['@attr']['rank']}` [**{track['name']}**]({track['url']}) — {int(track['playcount']):,}\n"
                )

        await ctx.reply(
            embed=discord.Embed(color=utils.color("main"), description="".join(rows))
            .set_author(name=f"lastfm: {fmuser}", icon_url=ctx.author.display_avatar)
            .set_thumbnail(url=track["image"][3]["#text"])
            .set_footer(text="recent tracks")
        )

    @commands.command()
    async def plays(self, ctx, user: discord.User | discord.Member = commands.Author):

        async with ctx.channel.typing():
            fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', user.id, one_value=True)
            if not fmuser:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                    )
                )
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=1"
                ) as ret:
                    track = await ret.json()
                    track = track["recenttracks"]["track"][0]

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&username={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&artist={track['artist']['#text']}&track={track['name']}&format=json&autocorrect=1"
                ) as ret:
                    ginfo = await ret.json()
                    playcount = ginfo["track"]["userplaycount"]

        msg = await ctx.reply(
            embed=discord.Embed(
                color=utils.color("done"),
                description=f"{self.done} {ctx.author.mention}**:** {'you' if user == ctx.author else user.name} {'have' if user == ctx.author else 'has'} **{int(playcount):,}** plays for the track [**{track['name']}**]({track['url']}) by [**{track['artist']['#text']}**]({ginfo['track']['artist']['url']})",
            )
        )
        try:
            if (
                not utils.read_json("fmuser")[str(ctx.author.id)]["reaction"]
                or not utils.read_json("fmuser")[str(ctx.author.id)]["reaction"][0]
            ):
                await msg.add_reaction("👍")
                await msg.add_reaction("👎")
            else:
                async for reaction in utils.aiter(
                    utils.read_json("fmuser")[str(ctx.author.id)]["reaction"]
                ):
                    x = self.bot.get_emoji(reaction)
                    await msg.add_reaction(x)
        except:
            pass

    async def get_artist_playcount(self, user: str, artist: str):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                f"https://ws.audioscrobbler.com/2.0/?method=artist.getInfo&api_key=43693facbb24d1ac893a7d33846b15cc&artist={artist.replace(' ', '+')}&format=json&username={user}"
            ) as response:
                r = await response.json()
        return r["artist"]["stats"]["userplaycount"]

    @lastfm.command(name="whoknows", aliases=["wk"])
    async def lastfm_whoknows(self, ctx, *, artist: str = None):

        await ctx.typing()
        fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id, one_value=True)
        if not fmuser:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                )
            )

        if not artist:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=1"
                    ) as resp:
                        artist = (await resp.json()
            )["recenttracks"]["track"][0]["artist"]["#text"]

        tuples = []
        rows = []
        for user_id, lastfm_username in await self.bot.db2.execute('SELECT user_id, lastfm_username FROM lastfm'):

            try:
                us = ctx.guild.get_member(user_id)
                if not us: 
                    continue
                fmuser2 = lastfm_username
                z = await self.get_artist_playcount(fmuser2, artist.replace(" ", "+"))
                tuples.append((str(us), int(z)))
            except:
                continue

        num = 0
        for x in sorted(tuples, key=lambda n: n[1])[::-1][:10]:
            if x[1] != 0:
                num += 1
                rows.append(f"`{num}` **{x[0]}** -- {x[1]}")

        embed = discord.Embed(color=utils.color("main"), description="\n".join(rows))
        embed.set_author(name=f"last.fm: {fmuser}", icon_url=ctx.author.display_avatar)
        embed.set_footer(text="who knows")
        embed.title = f"who knows {artist.lower()}"
        embed.set_thumbnail(url=ctx.guild.icon)
        return await ctx.reply(embed=embed)

    @lastfm.command(name="globalwhoknows", aliases=["gwk"])
    async def lastfm_globalwhoknows(self, ctx, *, artist: str = None):

        await ctx.typing()
        fmuser = await self.bot.db2.execute('SELECT lastfm_username FROM lastfm WHERE user_id = %s', ctx.author.id, one_value=True)
        if not fmuser:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}: you don't have a **last.fm** account connected\n{self.reply} connect your **last.fm** using **,lastfm set <username>**",
                )
            )

        if not artist:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=1"
                    ) as resp:
                        artist = (await resp.json()
            )["recenttracks"]["track"][0]["artist"]["#text"]

        tuples = []
        rows = []
        for user_id, lastfm_username in await self.bot.db2.execute('SELECT user_id, lastfm_username FROM lastfm'):

            try:
                us = self.bot.get_user(user_id)
                if not us: 
                    continue
                fmuser2 = lastfm_username
                z = await self.get_artist_playcount(fmuser2, artist.replace(" ", "+"))
                tuples.append((str(us), int(z)))
            except:
                continue

        num = 0
        for x in sorted(tuples, key=lambda n: n[1])[::-1][:10]:
            if x[1] != 0:
                num += 1
                rows.append(f"`{num}` **{x[0]}** -- {x[1]}")
                    
        embed = discord.Embed(color=utils.color("main"), description="\n".join(rows))
        embed.set_author(name=f"last.fm: {fmuser}", icon_url=ctx.author.display_avatar)
        embed.set_footer(text="who knows")
        embed.title = f"who knows {artist.lower()}"
        embed.set_thumbnail(url=ctx.guild.icon)
        return await ctx.reply(embed=embed)



async def setup(bot):
    await bot.add_cog(lastfm(bot))
