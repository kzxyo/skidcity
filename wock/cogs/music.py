from typing import Literal
from asyncio import Queue, TimeoutError
from async_timeout import timeout

from pomice import NodePool, NoNodesAvailable, Player, Playlist, Track
from discord import Member, VoiceState, Message

from discord.ext.commands import Cog, command, CommandError
import re

from helpers.wonder import Wonder
from helpers.patch.context import Context
import config

class regex:
    TIME = re.compile(r"(?P<time>\d+)(?P<unit>[smhdw])")
    TIME_HHMMSS = re.compile(r"(?P<h>\d{1,2}):(?P<m>\d{1,2}):(?P<s>\d{1,2})")
    TIME_SS = re.compile(r"(?P<m>\d{1,2}):(?P<s>\d{1,2})")
    TIME_HUMAN = re.compile(r"(?:(?P<m>\d+)\s*m\s*)?(?P<s>\d+)\s*[sm]")
    TIME_OFFSET = re.compile(r"(?P<s>(?:\-|\+)\d+)\s*s", re.IGNORECASE)

class Player(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue: Queue = Queue()
        self.waiting: bool = False
        self.loop: Literal["track", "queue", False] = False 
        self.invoke_id: int = None

    async def next(self) -> Track:
        if self.is_playing or self.waiting:
            return

        self.waiting = True
        if self.loop == "track" and self.track:
            pass

        else:
            try:
                async with timeout(180):
                    self.track = await self.queue.get()
            except TimeoutError:
                if text_channel := self.guild.get_channel(self.invoke_id):
                    return await self.destroy()

        self.waiting = False

        if self.loop == "queue":
            await self.queue.put(self.track)

        await self.play(self.track)
        if (
            text_channel := self.guild.get_channel(self.invoke_id)
        ) and self.loop != "track":
            await text_channel.neutral(
                f"Now playing [**{self.track.title}**]({self.track.uri}) [{self.track.requester.mention}]"
            )
        
    async def insert(self, 
                    track: Track,
                    bump: bool = False):
        
        if bump:
            self.queue._queue.insert(0, track)
        
        else:
            self.queue._queue.append(track)

        return track
    
    async def insert(self, track: Track, bump: bool = False):
        if bump:
            queue = self.queue._queue
            queue.insert(0, track)
        else:
            await self.queue.put(track)

    async def skip(self) -> Track:
        if self.is_paused:
            await self.set_pause(False)

        return await self.stop()

class Music(Cog, name = "Music"):
    def __init__(self, bot: Wonder):
        self.bot: Wonder = bot

    async def cog_load(self) -> None:
        if not hasattr(self.bot, "node") and hasattr(config, "Lavalink"):
            self.bot.node = await NodePool().create_node(
                bot=self.bot,
                identifier="wonder",
                **dict(
                    (key.lower(), value)
                    for key, value in vars(config.Lavalink).items()
                    if not key.startswith("_")
                ),
            )

    @Cog.listener()
    async def on_pomice_track_end(
        self,
        player: Player,
        track: Track,
        reason: str,
    ) -> None:
        await player.next()

    @Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ) -> None:
        if not member.id == self.bot.user.id:
            return

        if not hasattr(self.bot, "node") or not (
            player := self.bot.node.get_player(member.guild.id)
        ):
            return

        if not after.channel:
            await player.destroy()

    async def get_player(self, ctx: Context, *, connect: bool = False) -> Player:
        if not hasattr(self.bot, "node"):
            raise CommandError(
                "I am not **connected** to the node yet, please try again in a few seconds."
            )

        if not (voice := ctx.author.voice):
            raise CommandError("You're not **connected** to a voice channel.")

        elif (bot_voice := ctx.guild.me.voice) and (
            voice.channel.id != bot_voice.channel.id
        ):
            raise CommandError("You're not **connected** to my voice channel.")

        if not ctx.guild.me.voice or not (
            player := self.bot.node.get_player(ctx.guild.id)
        ):
            if not connect:
                raise CommandError("I'm not **connected** to a voice channel.")
            else:
                try:
                    await ctx.author.voice.channel.connect(
                        cls=Player, self_deaf=True
                    )
                except NoNodesAvailable:
                    raise CommandError(
                        "I am not **connected** to the node yet, please try again in a few seconds."
                    )

                player = self.bot.node.get_player(ctx.guild.id)
                player.invoke_id = ctx.channel.id
                await player.set_volume(65)

        return player

    @command(
        name = "play",
        usage = "(query)",
        example = "I Choose Violence",
        aliases = ["p"]
    )
    async def play(self, 
                   ctx: Context, 
                   *,
                   query: str = None) -> Message:
        """Play a track or playlist"""
        
        player: Player = await self.get_player(ctx, connect=True)

        if not query:
            raise CommandError("You didn't specify a **query** to search for.")

        try:
            result: list[Track] | Playlist = await player.get_tracks(
                query=query, ctx=ctx
            )
        except:
            raise CommandError("I could not find anything for that **query**.")

        if not result:
            raise CommandError("I could not find anything for that **query**.")

        if isinstance(result, Playlist):
            for track in result.tracks:
                await player.insert(track)

            await ctx.neutral(f"Added **{len(result.tracks)}** tracks from [**{result.name}**]({result.uri}) to the queue.") 

        else:
            track = result[0]
            await player.insert(track)
            if player.is_playing:
                await ctx.neutral(f"Enqueued [**{track.title}**]({track.uri})")

        if not player.is_playing:
            await player.next()
            if player.invoke_id != ctx.channel.id:
                await ctx.message.add_reaction("👍")

    @command(
        name = "remove",
        usage = "(index)",
        example = "1",
        aliases = ["rm"]
    )
    async def remove(self,
                     ctx: Context,
                     index: int) -> Message:
        """Remove a track from the queue"""
        
        player: Player = await self.get_player(ctx, connect=False)

        if not player.queue._queue:
            raise CommandError("The **queue** is empty.")
        
        if index > len(player.queue._queue):
            raise CommandError("That track is not in the **queue**.")
        
        track = player.queue._queue[index - 1]
        await ctx.neutral(f"Removed [**{track.title}**]({track.uri}) from the queue.")
        player.queue._queue.remove(track)
        

    @command(
        name = "skip",
        aliases = ["s", "next", "sk"]
    )
    async def skip(self, 
                   ctx: Context) -> Message:
        """Skip the current track"""

        player: Player = await self.get_player(ctx, connect=False)

        if not player.queue._queue:
            raise CommandError("The **queue** is empty.")
        
        if not player.is_playing:
            raise CommandError("There is nothing **playing**.")
        
        await ctx.neutral(f"Skipped [**{player.track.title}**]({player.track.uri})")
        await player.skip()

    @command(
        name="seek",
        usage="(time)",
        example="+30s",
        aliases=["forward", "ff"]
    )
    async def seek(self, 
                   ctx: Context, 
                   position: str) -> Message:
        """Seek to a position in the current track"""
        
        player: Player = await self.get_player(ctx, connect=False)

        if not player.is_playing:
            raise CommandError("There is nothing **playing**.")

        if ctx.invoked_with == "ff" and not position.startswith("+"):
            position = f"+{position}"
        elif ctx.invoked_with == "rw" and not position.startswith("-"):
            position = f"-{position}"

        milliseconds = 0
        if match := regex.TIME_HHMMSS.fullmatch(position):
            milliseconds += int(match.group("h")) * 3600000
            milliseconds += int(match.group("m")) * 60000
            milliseconds += int(match.group("s")) * 1000
            new_position = milliseconds
        elif match := regex.TIME_SS.fullmatch(position):
            milliseconds += int(match.group("m")) * 60000
            milliseconds += int(match.group("s")) * 1000
            new_position = milliseconds
        elif match := regex.TIME_OFFSET.fullmatch(position):
            milliseconds += int(match.group("s")) * 1000
            position = player.position
            new_position = position + milliseconds
        elif match := regex.TIME_HUMAN.fullmatch(position):
            if m := match.group("m"):
                if match.group("s") and position.lower().endswith("m"):
                    raise CommandError(f"`{position}` is invalid")
                milliseconds += int(m) * 60000
            if s := match.group("s"):
                if position.lower().endswith("m"):
                    milliseconds += int(s) * 60000
                else:
                    milliseconds += int(s) * 1000
            new_position = milliseconds
        else:
            raise CommandError(f"`{position}` is invalid")

        new_position = max(0, min(new_position, player.current.length))
        await player.seek(new_position)
        await ctx.neutral(f"Fast forwarded to `{new_position}`")

    @command(
        name="volume",
        usage="(percentage)",
        example="50",
        aliases=["vol", "v"]
    )
    async def volume(self, 
                     ctx: Context, 
                     percentage: int) -> Message:
        """Change the volume"""

        player: Player = await self.get_player(ctx, connect=False)

        if not percentage:
            raise CommandError("You didn't specify a **volume** to set.")

        if not player.is_playing:
            raise CommandError("There is nothing **playing**.")
        
        if not 0 <= percentage <= 100:
            raise CommandError("Invalid percentage, must be between `1` and `100`.")
        
        await player.set_volume(percentage)
        await ctx.neutral(f"Set the volume to `{percentage}%`")

    @command(
        name="pause",
        aliases=["ps"]
    )
    async def pause(self,
                     ctx: Context) -> Message:
        """Pause the current track"""

        player: Player = await self.get_player(ctx, connect=False)

        if not player.is_playing:
            raise CommandError("There is nothing **playing**.")
        
        if player.is_paused:
            raise CommandError("Track is already **paused**")
        
        await player.set_pause(True)
        await ctx.neutral(f"Paused [**{player.current.title}**]({player.current.uri})")

    @command(
        name="resume",
        aliases=["r", "res"]
    )
    async def resume(self, 
                     ctx: Context) -> Message:
        """Resume the current track"""

        player: Player = await self.get_player(ctx, connect=False)

        if not player.is_playing:
            raise CommandError("There is nothing **playing**.")
        
        if not player.is_paused:
            raise CommandError("Track is already **playing**.")
        
        await player.set_pause(False)
        await ctx.neutral(f"Resumed [**{player.current.title}**]({player.current.uri})")
    
    @command(
        name="stop",
        aliases=["dc", "disconnect"]
    )
    async def stop(self, 
                   ctx: Context) -> Message:
        """Disconnect wonder"""

        player: Player = await self.get_player(ctx, connect=False)

        if not player.is_playing:
            raise CommandError("There is nothing **playing**.")
        
        await player.destroy()
        await ctx.message.add_reaction("👋")

async def setup(bot: Wonder):
    await bot.add_cog(Music(bot))