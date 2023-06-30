import random

from asyncio import Queue, TimeoutError
from datetime import datetime, timedelta
from time import time
from typing import Literal

from async_timeout import timeout
from discord import Attachment, Embed, Member, Message, VoiceState
from discord.ext.commands import Cog, CommandError, command
from pomice import NodePool, NoNodesAvailable, Player, Playlist, Track

import config

from helpers.bleed import Bleed
from helpers.converters import Percentage, Position
from helpers.managers import Context
from helpers.utilities import format_duration, human_timedelta, shorten


class BleedPlayer(Player):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.queue: Queue = Queue()
        self.track: Track = None
        self.loop: Literal["track", "queue", False] = False
        self.waiting: bool = False
        self.invoke_id: int = None

    async def insert(self, track: Track, bump: bool = False) -> Track:
        if bump:
            queue = self.queue._queue
            queue.insert(0, track)
        else:
            await self.queue.put(track)

        return track

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
                    await text_channel.neutral(
                        # Minutes
                        f"Left {self.channel.mention} due to **3 minutes** of inactivity",
                        color=config.Color.bleed,
                    )
                return await self.destroy()

        self.waiting = False

        if self.loop == "queue":
            await self.queue.put(self.track)

        await self.play(self.track)
        if (
            text_channel := self.guild.get_channel(self.invoke_id)
        ) and self.loop != "track":
            await text_channel.neutral(
                f"Now playing [**{self.track.title}**]({self.track.uri}) in {self.channel.mention} [{self.track.requester.mention}]",
                color=config.Color.bleed,
                emoji=config.Emoji.Music.neutral,
            )

    async def skip(self) -> Track:
        if self.is_paused:
            await self.set_pause(False)

        return await self.stop()


class Music(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot

    async def cog_load(self) -> None:
        if not hasattr(self.bot, "node") and hasattr(config, "Lavalink"):
            self.bot.node = await NodePool().create_node(
                bot=self.bot,
                identifier="bleed" + str(time()),
                **dict(
                    (key.lower(), value)
                    for key, value in vars(config.Lavalink).items()
                    if not key.startswith("_")
                ),
            )

    @Cog.listener()
    async def on_pomice_track_end(
        self,
        player: BleedPlayer,
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

    async def get_player(self, ctx: Context, *, connect: bool = False) -> BleedPlayer:
        if not hasattr(self.bot, "node"):
            raise CommandError(
                "The **connection** to the **node** hasn't been established!"
            )

        if not (voice := ctx.author.voice):
            raise CommandError("You're not connected to a **voice channel**!")

        elif (bot_voice := ctx.guild.me.voice) and (
            voice.channel.id != bot_voice.channel.id
        ):
            raise CommandError("You're not connected to my **voice channel**!")

        if not ctx.guild.me.voice or not (
            player := self.bot.node.get_player(ctx.guild.id)
        ):
            if not connect:
                raise CommandError("I'm not connected to a **voice channel**!")
            else:
                try:
                    await ctx.author.voice.channel.connect(
                        cls=BleedPlayer, self_deaf=True
                    )
                except NoNodesAvailable:
                    raise CommandError(
                        "The **connection** to the **node** hasn't been established!"
                    )

                player = self.bot.node.get_player(ctx.guild.id)
                player.invoke_id = ctx.channel.id
                await player.set_volume(65)

        return player

    @command(name="current")
    async def current(self, ctx: Context) -> Message:
        """
        View the current track
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not player.current:
            return await ctx.warn("Nothing is **currently** playing!")

        return await ctx.channel.neutral(
            f"Currently playing [**{player.current.title}**]({player.current.uri}) in {player.channel.mention} [{player.current.requester.mention}]",
            color=config.Color.bleed,
            emoji=config.Emoji.Music.neutral,
        )

    @command(
        name="play",
        usage="(query)",
        example="Yung Kayo YEET",
        aliases=[
            "queue",
            "q",
            "p",
        ],
    )
    async def play(self, ctx: Context, *, query: str | Attachment = None) -> None:
        """
        Queue a track
        """

        player: BleedPlayer = await self.get_player(ctx, connect=True)

        if not query and ctx.invoked_with in ("queue", "q"):
            if not (queue := player.queue._queue):
                return await ctx.send_help()

            tracks = list()
            if track := player.current:
                tracks.append(
                    f"Listening to: [**{shorten(track.title, 23)}**]({track.uri}) "
                    + (
                        f"by **{track.author}** "
                        if track.track_type.value == "spotify"
                        else ""
                    )
                    + f"[{track.requester.mention}]\n"
                    + (
                        (
                            "**"
                            + human_timedelta(
                                datetime.now()
                                - timedelta(
                                    seconds=(
                                        int(track.length / 1000)
                                        - int(player.position / 1000)
                                    )
                                ),
                                suffix=False,
                            )
                            + f"** left of this track `{format_duration(player.position)}`/`{format_duration(track.length)}`\n"
                        )
                        if not track.is_stream
                        else ""
                    )
                )

            for track in queue:
                tracks.append(
                    f"`{len(tracks)}` [**{shorten(track.title, 23)}**]({track.uri}) - {track.requester.mention}"
                )

            return await ctx.paginate(
                Embed(
                    title=f"Queue in {player.channel.name}",
                    description=tracks,
                ),
                chunk_after=11,
                entry_difference=1,
                display_entries=False,
                text="track queued|tracks queued",
            )

        elif not query:
            return await ctx.send_help()

        elif not isinstance(query, str):
            query = query.url

        try:
            result: list[Track] | Playlist = await player.get_tracks(
                query=query, ctx=ctx
            )
        except:
            return await ctx.warn("No **results** were found")

        if not result:
            return await ctx.warn("No **results** were found")

        if isinstance(result, Playlist):
            for track in result.tracks:
                await player.insert(track)

            await ctx.channel.neutral(
                f"Enqueued **{result.track_count} tracks** from [**{result.name}**]({result.uri}) [{track.requester.mention}]",
                color=config.Color.bleed,
            )

        else:
            track = result[0]
            await player.insert(track)
            if player.is_playing:
                await ctx.channel.neutral(
                    f"Enqueued [**{track.title}**]({track.uri}) [{track.requester.mention}]",
                    color=config.Color.bleed,
                )

        if not player.is_playing:
            await player.next()
            if player.invoke_id != ctx.channel.id:
                await ctx.message.add_reaction(config.Emoji.checkmark)

    @command(
        name="seek",
        usage="(position)",
        example="+30s",
        aliases=[
            "ff",
            "rw",
        ],
    )
    async def seek(self, ctx: Context, position: Position) -> None:
        """
        Seek to a specific position
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not player.current:
            return await ctx.warn("Nothing is **currently** playing!")

        await player.seek(max(0, min(position, player.current.length)))
        await ctx.message.add_reaction(config.Emoji.checkmark)

    @command(
        name="skip",
        aliases=["sk"],
    )
    async def skip(self, ctx: Context) -> None:
        """
        Skip the current track
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not player.queue._queue:
            return await ctx.warn("The **queue** is empty!")

        await player.skip()
        await ctx.message.add_reaction(config.Emoji.Music.skip)

    @command(name="pause", aliases=["stop"])
    async def pause(self, ctx: Context) -> None:
        """
        Pause the track
        """

        player: BleedPlayer = await self.get_player(ctx)

        if player.is_paused:
            return await ctx.warn("There isn't a **track** playing")

        await player.set_pause(True)
        await ctx.message.add_reaction("⏸️")

    @command(
        name="resume",
        aliases=["unpause"],
    )
    async def resume(self, ctx: Context) -> None:
        """
        Resume the track
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not player.is_paused:
            return await ctx.warn("The **track** isn't paused")

        await player.set_pause(False)
        await ctx.message.add_reaction("⏯️")

    @command(
        name="shuffle",
        aliases=["mix"],
    )
    async def shuffle(self, ctx: Context) -> None:
        """
        Shuffle the music queue
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not (queue := player.queue._queue):
            return await ctx.warn("The **queue** is empty!")

        random.shuffle(queue)
        await ctx.message.add_reaction("🔀")

    @command(
        name="move",
        usage="(track index) (new index)",
        example="2 1",
    )
    async def move(self, ctx: Context, index: int, new_index: int) -> Message:
        """
        Move a track in the queue
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not (queue := player.queue._queue):
            return await ctx.warn("The **queue** is empty!")

        if index < 1 or index > len(queue):
            return await ctx.warn(
                f"The **index** must be between `1` and `{len(queue)}`"
            )

        if new_index < 1 or new_index > len(queue):
            return await ctx.warn(
                f"The **new index** must be between `1` and `{len(queue)}`"
            )

        track = queue[index - 1]
        del queue[index - 1]
        queue.insert(new_index - 1, track)

        return await ctx.approve(
            f"Moved [**{track.title}**]({track.uri}) to index `{new_index}`"
        )

    @command(
        name="remove",
        usage="(track index)",
        example="2",
    )
    async def remove(self, ctx: Context, index: int) -> Message:
        """
        Remove a track from the queue
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not (queue := player.queue._queue):
            return await ctx.warn("The **queue** is empty!")

        if index < 1 or index > len(queue):
            return await ctx.warn(
                f"The **index** must be between `1` and `{len(queue)}`"
            )

        track = queue[index - 1]
        del queue[index - 1]

        return await ctx.approve(
            f"Removed [**{track.title}**]({track.uri}) from the queue"
        )

    @command(
        name="volume",
        usage="<percentage>",
        example="45%",
        aliases=[
            "vol",
            "v",
        ],
    )
    async def volume(self, ctx: Context, volume: Percentage = None) -> Message:
        """
        Adjust the track volume
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not player.is_playing:
            return await ctx.warn("There isn't a **track** playing")

        elif not volume:
            return await ctx.neutral(f"Volume: `{player.volume}%`")

        await player.set_volume(volume)
        await ctx.approve(f"Set the **volume** to `{volume}%`")

    @command(name="clear")
    async def clear(self, ctx: Context) -> None:
        """
        Clear the queue
        """

        player: BleedPlayer = await self.get_player(ctx)

        if not (queue := player.queue._queue):
            return await ctx.warn("The **queue** is empty!")

        queue.clear()
        await ctx.message.add_reaction("🧹")

    @command(name="disconnect", aliases=["dc"])
    async def disconnect(self, ctx: Context) -> None:
        """
        Disconnect the player
        """

        player: BleedPlayer = await self.get_player(ctx)

        await player.destroy()
        await ctx.message.add_reaction(config.Emoji.wave)
