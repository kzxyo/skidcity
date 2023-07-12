import datetime
import random
import logging
from ast import List
from asyncio import Queue
from contextlib import suppress
from typing import Literal

from discord import (Attachment, Embed, HTTPException, Member, Message,
                     VoiceState)
from discord.ext.commands import CommandError, command
from humanfriendly import parse_timespan
from pomice import (NodePool, NoNodesAvailable, Player, Playlist, QueueEmpty,
                    Track)

from utilities import config
from utilities.managers import Wrench, Context
from pomice.enums import LogLevel
logger = logging.getLogger(__name__)

class CustomPlayer(Player):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.queue: Queue = Queue()
        self.track: Track = None
        self.loop: Literal["track", "queue", False] = False
        self.controller: Message = None
        self.context: Context = None
        self.wait: bool = False

    async def insert(self, track: Track, first: bool = False) -> Track:
        if first:
            queue = self.queue._queue
            queue.insert(0, track)
        else:
            await self.queue.put(track)

        return track

    async def teardown(self):
        with suppress((HTTPException), (KeyError)):
            await self.destroy()
            if self.controller:
                await self.controller.delete()

    async def poop(self, option: str) -> None:
        self.loop = option

    async def next(self) -> Embed:
        if self.is_playing or self.wait:
            return

        if self.controller:
            with suppress(HTTPException):
                await self.controller.delete()

        self.wait = True
        if self.loop == "track" and self.track:
            pass

        else:
            try:
                self.track = await self.queue.get()
            except QueueEmpty:
                return await self.teardown()

        self.wait = False

        if self.loop == "queue":
            await self.queue.put(self.track)

        await self.play(self.track)

        if self.track.is_stream:
            self.controller = await self.context.music(
                f"Now playing [**{self.track.title} - {self.track.author}**]({self.track.uri}), Requested by **{str(self.track.requester)}**."
            )
        else:
            self.controller = await self.context.music(
                f"Now playing [**{self.track.title} - {self.track.author}**]({self.track.uri}), Requested by **{str(self.track.requester)}**."
            )

    async def set_context(self, ctx: Context) -> None:
        self.context = ctx

    async def skip(self) -> Track:
        if self.is_paused:
            await self.set_pause(False)

        return await self.stop()


class Music(Wrench):
    async def lavalink(self):
        self.bot.node = await NodePool().create_node(
            bot=self.bot,
            identifier="lairv2",
            host="0.0.0.0",
            port=2333,
            password="youshallnotpass",
            spotify_client_id="a9b56c0aa9a7408db8911a6a5dbbc5e8",
            spotify_client_secret="f3ff4fd9a2de48229bad9bbe635c51dc",
            log_level=LogLevel.CRITICAL
        )
        logger.info("Initialized pomice node")

    def mili_to_min(self, m: int | float):
        total = int(m / 1000)
        min = int(total / 60)
        sec = int(total - min * 60)
        return "{}:{:02}".format(min, sec)

    @Wrench.listener()
    async def on_pomice_track_end(
        self,
        player: CustomPlayer,
        track: Track,
        reason: str,
    ) -> None:
        await player.next()

    @Wrench.listener()
    async def on_pomice_track_stuck(
        self, player: CustomPlayer, track: Track, _
    ) -> None:
        await player.next()

    @Wrench.listener()
    async def on_pomice_track_exception(
        self, player: CustomPlayer, track: Track, _
    ) -> None:
        await player.next()

    @Wrench.listener("on_voice_state_update")
    async def monitor_voice(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        if not member.id == self.bot.user.id:
            return

        if not hasattr(self.bot, "node") or not (
            player := self.bot.node.get_player(member.guild.id)
        ):
            return

        if not after.channel:
            await player.teardown()

    async def get_player(
        self, ctx: Context, *, connection: bool = False
    ) -> CustomPlayer:
        if not hasattr(self.bot, "node"):
            raise CommandError("Couldn't establish **connection** to the node.")

        if not (voice := ctx.author.voice):
            raise CommandError("You are not connected to a **Voice Channel**.")

        elif (bot_voice := ctx.guild.me.voice) and (
            voice.channel.id != bot_voice.channel.id
        ):
            raise CommandError("You are not connected to **my** Voice Channel.")

        if not ctx.guild.me.voice or not (
            player := self.bot.node.get_player(ctx.guild.id)
        ):
            if not connection:
                raise CommandError("I'm not connected to a **Voice Channel**.")

            else:
                try:
                    await ctx.author.voice.channel.connect(
                        cls=CustomPlayer, self_deaf=True
                    )
                except NoNodesAvailable:
                    raise CommandError("Couldn't establish **connection** to the node.")

                player = self.bot.node.get_player(ctx.guild.id)
                await player.set_volume(100)

        return player
    
    @command(name='shuffle', aliases=['shfl'], brief='Shuffle the current queue.')
    async def shuffle(self, ctx: Context):
        player: CustomPlayer = await self.get_player(ctx, connection=True)
        await player.set_context(ctx=ctx)

        if not (queue := player.queue._queue):
            return await ctx.warn("**Queue** is empty.")
        
        random.shuffle(queue)
        await ctx.message.add_reaction("🔀")

    @command(
        name="play", aliases=["p"], brief="Play a song/playlist in the voice channel."
    )
    async def play(
        self, ctx: Context, *, query: str | Attachment = None
    ) -> Embed | None:
        player: CustomPlayer = await self.get_player(ctx, connection=True)
        await player.set_context(ctx=ctx)

        if not query:
            return

        elif not isinstance(query, str):
            query = query.url

        try:
            result: List[Track] | Playlist = await player.get_tracks(
                query=query, ctx=ctx
            )
        except Exception:
            return await ctx.warn("No results were **found**")

        if not result:
            return await ctx.warn("No results were **found**")

        if isinstance(result, Playlist):
            for track in result.tracks:
                await player.insert(track)

            await ctx.music(
                f"Added **{len(result.tracks)} {'song' if len(result.tracks) == 1 else 'songs'}** to the queue."
            )

        else:
            track = result[0]
            await player.insert(track)
            if player.is_playing:
                await ctx.music(f"Added [**{track.title}**]({track.uri}) to the queue.")

        if not player.is_playing:
            await player.next()

    @command(name="skip", aliases=["sk"], brief="Skip a song in the voice channel.")
    async def skip(self, ctx: Context) -> Embed | None:
        player: CustomPlayer = await self.get_player(ctx)
        await player.set_context(ctx=ctx)

        if not player.queue._queue:
            return await ctx.warn("**Queue** is empty.")

        await player.skip()
        await ctx.message.add_reaction("⏭️")

    @command(
        name="pause", aliases=["ps", "stop"], brief="Pause a song in the voice channel."
    )
    async def pause(self, ctx: Context) -> None:
        player: CustomPlayer = await self.get_player(ctx)
        await player.set_context(ctx=ctx)

        if player.is_paused:
            return await ctx.warn("Current track is **already** paused.")

        await player.set_pause(True)
        await ctx.message.add_reaction("⏸️")

    @command(
        name="seek", aliases=["pos"], brief="Seek a song in the voice channel."
    )
    async def seek(self, ctx: Context, *, position: str) -> Message:
        player: CustomPlayer = await self.get_player(ctx)
        await player.set_context(ctx=ctx)

        if not player.is_playing:
            return await ctx.warn("I'm not playing anything.")

        if not (position := parse_timespan(position)):
            return await ctx.warn("Invalid **position**.")

        await player.seek(position)
        await ctx.music(f"Seeked to **{position}**.")

    @command(
        name="nowplaying",
        aliases=["np", "current", "currentsong", "playing"],
        brief="Show the current song in the voice channel.",
    )
    async def nowplaying(self, ctx: Context) -> None:
        player: CustomPlayer = await self.get_player(ctx)
        await player.set_context(ctx=ctx)

        if not player.current:
            return await ctx.error('There is nothing **playing**.')
        embed = Embed()
        embed.color = config.Color.music
        embed.title = player.current.title
        embed.description = f"[**{player.current.author}**]({player.current.uri})"
        embed.set_thumbnail(url=player.current.thumbnail)
        embed.add_field(
            name="Duration",
            value=f"{player.position}/{player.current.length}",
            inline=False,
        )
        await ctx.reply(embed=embed)
        
    @command(
        name="resume",
        aliases=["unpause"],
        brief="Resume the current song in the voice channel.",
    )
    async def resume(self, ctx: Context) -> None:
        player: CustomPlayer = await self.get_player(ctx)
        await player.set_context(ctx=ctx)

        if not player.is_paused:
            return await ctx.warn("Current track is **already** playing.")

        await player.set_pause(False)
        return await ctx.message.add_reaction("⏯️")
    
    @command(
        name="volume",
        aliases=["vol"],
        brief="Change the volume of the current song in the voice channel.",
    )
    async def volume(self, ctx: Context, *, volume: int) -> None:
        player: CustomPlayer = await self.get_player(ctx)
        await player.set_context(ctx=ctx)

        if not 0 < volume < 101:
            return await ctx.warn("Volume must be between **1** and **100**.")

        await player.set_volume(volume)
        return await ctx.music(f"Volume set to **{volume}%**.")
    

    @command(
        name="disconnect",
        aliases=["dc", "bye"],
        brief="Disconnect the bot from the voice channel",
    )
    async def disconnect(self, ctx: Context) -> None:
        player: CustomPlayer = await self.get_player(ctx=ctx)
        await player.set_context(ctx=ctx)

        await player.teardown()
        return await ctx.message.add_reaction("👋")
    
    @command(
        name='loop',
        brief='Loop the current track/queue.'
    )
    async def loop(self, ctx: Context, option: Literal['queue', 'track']):
        player: CustomPlayer = await self.get_player(ctx)
        await player.set_context(ctx=ctx)

        if not option:
            if not player.loop:
                return await ctx.error('There is no **active** loop.')
        if option == "queue":
            if not (player.queue._queue):
                return await ctx.error('**Queue** is empty.')
            
        await player.poop(option if option else False)
        return await ctx.message.add_reaction("➿")
    

    @command(
        name='queue',
        aliases=['q'],
        brief='View the current voice channel queue.'
    )
    async def queue(self, ctx: Context) -> Embed:
        player: CustomPlayer = await self.get_player(ctx)
        await player.set_context(ctx=ctx)
        if not (queue := player.queue._queue):
            return await ctx.warn('**Queue** is empty.')
        
        tracks = []
        embeds = []
        num = 0
        for track in queue:
            tracks.append(
                f"`{len(tracks)}` [**{track.title} - {track.author}**]({track.uri}): **{self.mili_to_min(track.length)}**"
            )
        
        for page in ctx.as_chunks(tracks, 10):
            num += 1
            embeds.append(
                Embed(
                    color=config.Color.main,
                    description="\n".join(page),
                    timestamp=datetime.datetime.now()
                )

                .set_footer(
                    text=f"Page {num}/{len(list(ctx.as_chunks(tracks, 10)))}  ({len(tracks)} total entries)"
                )
            )

        return await ctx.paginate(embeds)


async def setup(bot):
    await bot.add_cog(Music(bot=bot))
