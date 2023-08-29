import asyncio, random, discord, pomice, async_timeout
from typing import Literal
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music = "🎵"
    
    async def start_node(self):
      await self.bot.wait_until_ready()
      self.bot.node = await pomice.NodePool().create_node(bot=self.bot, host="us.lavalink.alexanderof.xyz", port=2333, password="lavalink", identifier="MAIN", secure=False, spotify_client_id="38e4713253e147359a8c049425cdfff1", spotify_client_secret="c82c5d45ec4741f58b780b3a13cd8b44", apple_music=True)
    
    async def music_send(self, ctx: commands.Context, message: str) -> discord.Message:
      return await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"{self.music} {ctx.author.mention}: {message}"))
    
    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: pomice.Player, track: pomice.Track, reason: str):
        await player.next()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.id != self.bot.user.id: return
        if not hasattr(self.bot, "node") or (player := self.bot.node.get_player(member.guild.id)) is None: return
        if not after.channel:
            await player.destroy()

    async def get_player(self, ctx: commands.Context, *, connect: bool = True):
        if not hasattr(self.bot, "node"):
            return await ctx.send_warning("No nodes available")
        if not ctx.author.voice:
            return await ctx.send_warning("You're not **connected** to a voice channel")
        if ctx.guild.me.voice and ctx.guild.me.voice.channel != ctx.author.voice.channel:
            return await ctx.send_warning("I'm **already** connected to a voice channel")
        if (player := self.bot.node.get_player(ctx.guild.id)) is None or not ctx.guild.me.voice:
            if not connect:
                return await ctx.send_warning("I'm not **connected** to a voice channel")
            else:
                await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
                player = self.bot.node.get_player(ctx.guild.id)
                player.invoke_id = ctx.channel.id
                await player.set_volume(65)

        return player

    @commands.command(description="play a song", help="music", usage="[url / name]")
    async def play(self, ctx: commands.Context, *, query: str):
        player: Player = await self.get_player(ctx)
        result = await player.node.get_tracks(query=query, ctx=ctx)
        if not result:
            return await ctx.send_warning(f"No results found for **{query}**")
        elif isinstance(result, pomice.Playlist):
            for track in result.tracks:
                await player.insert(track)
        else:
            track = result[0]
            await player.insert(track)
            if player.is_playing:
                await self.music_send(ctx, f"Added [{track.title}]({track.uri}) to the queue")
            
        if not player.is_playing:
            await player.next()

    @commands.command(description="skip the song", help="music")
    async def skip(self, ctx: commands.Context):
        player: Player = await self.get_player(ctx, connect=False)
        if player.is_playing:
            await self.music_send(ctx, "Skipped the song")
            await player.skip()
        else:
            await ctx.send_warning("There isn't a track playing")

    @commands.command(description="set a loop for the track", help="music", usage="[type]\ntypes: off, track, queue")
    async def loop(self, ctx: commands.Context, option: Literal["track", "queue", "off"]):
        player: Player = await self.get_player(ctx, connect=False)
        if option == "off":
            if not player.loop:
                return await ctx.warn("**Loop** isn't set")
        elif option == "track":
            if not player.is_playing:
                return await ctx.send_warning("No **tracks** playing")
        elif option == "queue":
            if not player.queue._queue:
                return await ctx.warn("There aren't any **tracks** in the queue")

        await self.music_send(ctx, f"**{option}** looping the queue")
        await player.set_loop(option if option != "off" else False)

    @commands.command(description="pause the player", help="music")
    async def pause(self, ctx: commands.Context):
        player: Player = await self.get_player(ctx, connect=False)
        if player.is_playing and not player.is_paused:
            await self.music_send(ctx, "Paused the player")
            await player.set_pause(True)
        else:
            await ctx.sene_warning("No **track** is playing")

    @commands.command(description="resume the player", help="music")
    async def resume(self, ctx: commands.Context):
        player: Player = await self.get_player(ctx, connect=False)
        if player.is_playing and player.is_paused:
            await self.music_send(ctx, "Resumed the player")
            await player.set_pause(False)
        else:
            await ctx.send_warning("No **track** playing")

    @commands.command(description="set player volume", help="music", usage="[volume]")
    async def volume(self, ctx: commands.Context, vol: int):
        player: Player = await self.get_player(ctx, connect=False)
        if not 0 <= vol <= 150:
            return await ctx.send_warning("Volume should be between 0 and 150")
        await player.set_volume(vol)
        await self.music_send(ctx, f"Volume set to **{vol}**")

    @commands.command(description="stop the player", help="music", aliases=["dc"])
    async def stop(self, ctx: commands.Context):
        player: Player = await self.get_player(ctx, connect=False)
        await player.teardown()
        await self.music_send(ctx, "Stopped the player")

async def setup(bot):
    await bot.add_cog(Music(bot))

class Player(pomice.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoke_id: int = None
        self.track: pomice.Track = None
        self.queue: asyncio.Queue = asyncio.Queue()
        self.waiting: bool = False
        self.loop: str = False

    async def play(self, track: pomice.Track):
        await super().play(track)

    async def insert(self, track: pomice.Track):
        await self.queue.put(track)

        return True

    async def next(self, no_vc: bool = False):
        if no_vc:
            if self.is_playing or self.waiting: return
        
        self.waiting = True
        if self.loop == "track" and self.track:
            track = self.track
        else:
            try:
                with async_timeout.timeout(300):
                    track = await self.queue.get()
                    if self.loop == "queue":
                        await self.queue.put(track)
            except asyncio.TimeoutError:
                return await self.teardown()

        await self.play(track)
        self.track = track
        self.waiting = False
        if (channel := self.guild.get_channel(self.invoke_id)):
            await channel.send(embed=discord.Embed(color=self.bot.color, description=f"🎵 {track.requester.mention}: Now Playing [{track.title}]({track.uri})"))

        return track

    async def skip(self):
        if self.is_paused:
            await self.set_pause(False)

        return await self.stop()

    async def set_loop(self, state: str):
        self.loop = state

    async def teardown(self):
        try:
            self.queue._queue.clear()
            await self.destroy()
        except:
            pass