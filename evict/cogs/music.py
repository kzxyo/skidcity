
from contextlib import suppress
import discord
from discord.ext import commands
from discord import Embed, utils
from patches.classes import Player
from typing import Optional, Literal
from discord.ext.commands import Context
import pomice

class plural:
    def __init__(self, value: int, bold: bool = False, code: bool = False):
        self.value: int = value
        self.bold: bool = bold
        self.code: bool = code

    def __format__(self, format_spec: str) -> str:
        v = self.value
        if isinstance(v, list):
            v = len(v)
        if self.bold:
            value = f"**{v:,}**"
        elif self.code:
            value = f"`{v:,}`"
        else:
            value = f"{v:,}"

        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"

        if abs(v) != 1:
            return f"{value} {plural}"

        return f"{value} {singular}"

    def do_plural(self, format_spec: str) -> str:
        v = self.value
        if isinstance(v, list):
            v = len(v)
        if self.bold:
            value = f"**{v:,}**"
        elif self.code:
            value = f"`{v:,}`"
        else:
            value = f"{v:,}"

        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"

        if abs(v) != 1:
            return f"{value} {plural}"

        return f"{value} {singular}"


def shorten(value: str, length: int = 20):
    if len(value) > length:
        value = value[: length - 2] + \
            (".." if len(value) > length else "").strip()
    return value


def format_duration(duration: int, ms: bool = True):
    if ms:
        seconds = int((duration / 1000) % 60)
        minutes = int((duration / (1000 * 60)) % 60)
        hours = int((duration / (1000 * 60 * 60)) % 24)
    else:
        seconds = int(duration % 60)
        minutes = int((duration / 60) % 60)
        hours = int((duration / (60 * 60)) % 24)

    if any((hours, minutes, seconds)):
        result = ""
        if hours:
            result += f"{hours:02d}:"
        result += f"{minutes:02d}:"
        result += f"{seconds:02d}"
        return result
    else:
        return "00:00"

class Player(pomice.Player):
    """Custom pomice Player class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = pomice.Queue()
        self.controller: discord.Message = None
        # Set context here so we can send a now playing embed
        self.context: commands.Context = None
        self.dj: discord.Member = None

        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()
        
    async def set_loop(self, state: str):
        self.loop = state
        self._queue = self.queue._queue

    async def do_next(self) -> None:
        # Clear the votes for a new song
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()

        # Check if theres a controller still active and deletes it
        if self.controller:
            with suppress(discord.HTTPException):
                await self.controller.delete()

        # Queue up the next track, else teardown the player
        try:
            track: pomice.Track = self.queue.get()
        except pomice.QueueEmpty:
            return await self.teardown()

        await self.play(track)

        # Call the controller (a.k.a: The "Now Playing" embed) and check if one exists

        if track.is_stream:
            embed = discord.Embed(
                title="Now playing",
                description=f"**LIVE** [{track.title}]({track.uri}) [{track.requester.mention}]",
                color = self.bot.color
            )
            self.controller = await self.context.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Now playing",
                description=f"[{track.title}]({track.uri}) [{track.requester.mention}]",
                color = self.bot.color
            )
            self.controller = await self.context.send(embed=embed)

    async def teardown(self):
        """Clear internal states, remove player controller and disconnect."""
        with suppress((discord.HTTPException), (KeyError)):
            await self.destroy()
            if self.controller:
                await self.controller.delete()

    async def set_context(self, ctx: commands.Context):
        """Set context for the player"""
        self.context = ctx
        self.dj = ctx.author


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # In order to initialize a node, or really do anything in this library,
        # you need to make a node pool
        self.pomice = pomice.NodePool()

        # Start the node
        bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        # Waiting for the bot to get ready before connecting to nodes.
        await self.bot.wait_until_ready()

        # You can pass in Spotify credentials to enable Spotify querying.
        # If you do not pass in valid Spotify credentials, Spotify querying will not work
        await self.pomice.create_node(
            bot=self.bot,
            host="127.0.0.1",
            port=2333,
            password="youshallnotpass",
            identifier="MAIN",
        )
        print(f"Node is ready!")


    # The following are events from pomice.events
    # We are using these so that if the track either stops or errors,
    # we can just skip to the next track

    # Of course, you can modify this to do whatever you like

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track, _):
        await player.do_next()

    @commands.Cog.listener()
    async def on_pomice_track_stuck(self, player: Player, track, _):
        await player.do_next()

    @commands.Cog.listener()
    async def on_pomice_track_exception(self, player: Player, track, _):
        await player.do_next()

    @commands.command(aliases=["joi", "j", "summon", "su", "con", "connect"])
    async def join(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None) -> None:
        if not channel:
            channel = getattr(ctx.author.voice, "channel", None)
            if not channel:
                return await ctx.warning(
                    "You must be in a voice channel in order to use this command.",
                )
                
        await ctx.author.voice.channel.connect(cls=Player)
        player: Player = ctx.voice_client

        await player.set_context(ctx=ctx)
        await ctx.success(f"I have **joined** `{channel.mention}`")

    @commands.command(aliases=["dc", "disc", "lv", "fuckoff"])
    async def disconnect(self, ctx: commands.Context):
        if not (player := ctx.voice_client):
            return await ctx.warning(
                "You **must** have the bot in a channel in order to use this command")

        await player.destroy()
        await ctx.success("I have **left** the voice channel.")

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        # Checks if the player is in the channel before we play anything
        if not (player := ctx.voice_client): 
            await ctx.author.voice.channel.connect(cls=Player)
       
        player: Player = ctx.voice_client
        await player.set_context(ctx=ctx)

        results = await player.get_tracks(search, ctx=ctx)

        if not results:
            return await ctx.warning("I found **no** results with that search term.")

        if isinstance(results, pomice.Playlist):
            for track in results.tracks:
                player.queue.put(track)
        else:
            track = results[0]
            player.queue.put(track)

        if not player.is_playing:
            await player.do_next()
            
        if player.is_playing:
            await ctx.success(f"I have **added** [**{track.title}**]({track.uri}) to the queue.")

    @commands.command(aliases=["pau", "pa"])
    async def pause(self, ctx: commands.Context):
        
        if not (player := ctx.voice_client):
            return await ctx.warning(
                "You **must** have the bot in a channel in order to use this command",
                
            )

        await player.set_pause(True)
        await ctx.success("I have **paused** the song.")

    @commands.command(aliases=["res"])
    async def resume(self, ctx: commands.Context):
        """Resume a currently paused player."""
        if not (player := ctx.voice_client):
            return await ctx.warning(
                "You **must** have the bot in a channel in order to use this command",
                
            )

        await player.set_pause(False)
        await ctx.success("I have **resumed** the player.")

    @commands.command(aliases=["n", "nex", "next", "sk"])
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""
        if not (player := ctx.voice_client):
            return await ctx.warning(
                "You **must** have the bot in a channel in order to use this command",
                
            )

        if not player.is_connected:
            return

        await player.stop()
        await ctx.success("I have **skipped** the song.")

    @commands.command()
    async def stop(self, ctx: commands.Context):
        """Stop the player and clear all internal states."""
        if not (player := ctx.voice_client):
            return await ctx.warning(
                "You **must** have the bot in a channel in order to use this command",
                
            )

        if not player.is_connected:
            return

        await player.teardown()
        await ctx.success("I **stopped** playing music and **cleared** the queue.")

    @commands.command(aliases=["mix", "shuf"])
    async def shuffle(self, ctx: commands.Context):
        
        player: Player = ctx.voice_client

        if not (player := ctx.voice_client):
            return await ctx.warning(
                "You **must** have the bot in a channel in order to use this command")

        if not player.is_connected:
            return
        
        await player.set_context(ctx=ctx)

        if player.queue.size < 3:
            return await ctx.warning("The queue is **empty**. Add some songs to shuffle the queue.")
        
        player.queue.shuffle()
        await ctx.success("I have **shuffled** the queue.")
        
    @commands.command(name="loop", usage="(track, queue, or off)", aliases=["repeat", "lp"])
    async def loop(self, ctx: Context, option: Literal["track", "queue", "off"]):

        player: Player = ctx.voice_client

        if option == "off":
            if not player.loop:
                return await ctx.warning("There isn't an active **loop**")
        
        elif option == "track":
            if not player.is_playing:
                return await ctx.warning("There isn't an active **track**")
        
        elif option == "queue":
            if not player.queue._queue:
                return await ctx.warning("There aren't any **tracks** in the queue")

        await ctx.message.add_reaction(
            "✅" if option == "off" else "🔂" if option == "track" else "🔁"
        )
        await player.set_loop(option if option != "off" else False)

    @commands.command(aliases=["v", "vol"])
    async def volume(self, ctx: commands.Context, *, vol: int):
        """Change the players volume, between 1 and 100."""
        
        if not (player := ctx.voice_client):
            return await ctx.warning(
                "You **must** have the bot in a channel in order to use this command")
            
        if not player.is_connected:
            return

        if not 0 < vol < 101:
            return await ctx.warning("Please enter a value between 1 and 100.")

        await player.set_volume(vol)
        await ctx.success(f"Set the **volume** to **{vol}**%")
        
    @commands.command(descirption='check the queue', aliases=['q'])
    async def queue(self, ctx: commands.Context):
        
        if not (player := ctx.voice_client):
            return await ctx.warning(
                "You **must** have the bot in a channel in order to use this command")
        
        player: Player = ctx.voice_client
        
        if player.queue.is_empty:
            return await ctx.warning("The queue is **empty**.")
        
        await player.set_context(ctx=ctx)
        
        playing = f"{'Playing'} {player.current.title} by {player.current.author}"
    
        if player.queue.get_queue():
            tracks = [f"[**{track.title}**]({track.uri})" for track in player.queue.get_queue()]

        for m in utils.as_chunks(tracks, 10):
            embed = Embed(color=self.bot.color, title=f"queued in {ctx.guild.name}")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name=f"Tracks:", value='\n'.join([l for l in m]))
            embed.set_footer(text=f"{playing}")
            
            if player.current.thumbnail:
                embed.set_thumbnail(url=player.current.thumbnail)
            
            await ctx.reply(embed=embed)  
            
    @commands.command(name="current", brief="show current playing song")
    async def nowplaying(
        self, ctx: commands.Context, member: Optional[discord.Member] = Context.author):
        
        player: Player = ctx.voice_client
        
        if player == None:
            return await ctx.invoke(self.bot.get_command("nowplaying"))
        
        elif player.current:
            embed = discord.Embed(title=f"**Currently Playing:**", color=self.bot.color)
            embed.description = f"> **Playing: ** [**{shorten(player.current.title, 23)}**]({player.current.uri})\n > **Time: ** `{format_duration(player.position)}/{format_duration(player.current.length)}`"
            embed.set_footer(text=f"Queue: 1/{player.queue.count}")
            if player.current.thumbnail:
                embed.set_thumbnail(url=player.current.thumbnail)

            return await ctx.reply(embed=embed)
        else:
            return await ctx.warning(f"no current playing track : {player.current}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))