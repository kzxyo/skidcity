import asyncio
import random

from contextlib import suppress
from typing import Literal

import async_timeout
import discord
import pomice

from discord.ext import commands

from helpers import functions, regex, wock


class music(commands.Cog, name="Music"):
    def __init__(self, bot):
        self.bot: wock.wockSuper = bot
        self.bot.loop.create_task(self.authenticate_node())

    async def authenticate_node(self):
        if not hasattr(self.bot, "node"):
            lavalink = self.bot.config.get("lavalink")
            spotify = self.bot.config["api"].get("spotify")
            try:
                self.bot.node = await pomice.NodePool().create_node(
                    bot=self.bot,
                    host=lavalink.get("host"),
                    port=lavalink.get("port"),
                    password=lavalink.get("password"),
                    identifier="wock-" + functions.unique_id(16),
                    secure=lavalink.get("secure"),
                    spotify_client_id=spotify.get("client_id"),
                    spotify_client_secret=spotify.get("client_secret"),
                    apple_music=True,
                )
            except Exception as error:
                self.bot.logger.info(f"Couldn't initiate Lavalink ({error})")

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: pomice.Player, track: pomice.Track, reason: str):
        await player.next_track()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member.id != self.bot.user.id:
            return

        if not hasattr(self.bot, "node") or (player := self.bot.node.get_player(member.guild.id)) is None:
            return

        if not after.channel:
            await player.destroy()

    async def get_player(self, ctx: wock.Context, *, connect: bool = True):
        if not hasattr(self.bot, "node"):
            raise commands.CommandError("The **Lavalink** node hasn't been **initialized** yet")

        if not ctx.author.voice:
            raise commands.CommandError("You're not **connected** to a voice channel")

        if ctx.guild.me.voice and ctx.guild.me.voice.channel != ctx.author.voice.channel:
            raise commands.CommandError("I'm **already** connected to another voice channel")

        if (player := self.bot.node.get_player(ctx.guild.id)) is None or not ctx.guild.me.voice:
            if not connect:
                raise commands.CommandError("I'm not **connected** to a voice channel")
            else:
                await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
                player = self.bot.node.get_player(ctx.guild.id)
                player.bound_channel = ctx.channel
                await player.set_volume(65)

        return player

    @commands.command(
        name="play",
        usage="(query)",
        example="Penthouse Shordy",
        parameters={
            "bump": {
                "require_value": False,
                "description": "Bump the track to the front of the queue",
                "aliases": ["b", "next"],
            },
            "shuffle": {
                "require_value": False,
                "description": "Shuffle the queue after adding the track",
                "aliases": ["s"],
            },
        },
        aliases=["queue", "p", "q"],
    )
    async def play(self, ctx: wock.Context, *, query: str = None):
        """Queue a track"""

        if query is None:
            if ctx.invoked_with in ("play", "p"):
                return await ctx.send_help()
            else:
                if (player := self.bot.node.get_player(ctx.guild.id)) is None:
                    return await ctx.warn("Please **provide** a query")
                else:
                    queue = player.queue._queue.copy()
                    if not queue:
                        if not player.current:
                            return await ctx.warn("There isn't an active **track**")

                    embed = discord.Embed(title=f"Queue for {player.channel.name}", description=list())

                    if player.current:
                        embed.description.append(
                            f"Playing [**{functions.shorten(player.current.title, 23)}**]({player.current.uri})"
                            f" `{functions.format_duration(player.position)}/{functions.format_duration(player.current.length)}`\n> Requested by"
                            f" {player.current.requester.mention}\n"
                        )
                    for track in queue:
                        embed.description.append(
                            f"`{len(embed.description)}` [**{functions.shorten(track.title, 23)}**]({track.uri}) - {track.requester.mention}"
                        )

                    return await ctx.paginate(embed, max_entries=11, counter=False)

        player: Player = await self.get_player(ctx)
        try:
            result = await player.node.get_tracks(query=query, ctx=ctx)
        except pomice.TrackLoadError:
            if match := regex.SOUNDCLOUD_TRACK_URL.match(query) or regex.SOUNDCLOUD_PLAYLIST_URL.match(query):
                result = await player.node.get_tracks(query=f"ytsearch:{match.group('slug')}", ctx=ctx)
            else:
                result = None

        if not result:
            return await ctx.warn("No **results** were found")
        elif isinstance(result, pomice.Playlist):
            for track in result.tracks:
                await player.insert(track, filter=False, bump=ctx.parameters.get("bump"))
            await ctx.neutral(
                f"Added **{functions.plural(result.track_count):track}** from [**{result.name}**]({result.uri}) to the queue",
                emoji="🎵",
            )
        else:
            track = result[0]
            await player.insert(track, bump=ctx.parameters.get("bump"))
            if player.is_playing:
                await ctx.neutral(f"Added [**{track.title}**]({track.uri}) to the queue", emoji="🎵")

        if ctx.parameters.get("shuffle"):
            if queue := player.queue._queue:
                random.shuffle(queue)
                with suppress(discord.HTTPException):
                    await ctx.message.add_reaction("🔀")

        if not player.is_playing:
            await player.next_track()

        if bound_channel := player.bound_channel:
            if bound_channel != ctx.channel:
                with suppress(discord.HTTPException):
                    await ctx.message.add_reaction("✅")

    @commands.command(
        name="move",
        usage="(from) (to)",
        example="6 2",
        aliases=["mv"],
    )
    async def move(self, ctx: wock.Context, track: int, to: int):
        """Move a track to a different position"""

        player: Player = await self.get_player(ctx, connect=False)
        queue = player.queue._queue

        if track == to:
            return await ctx.warn(f"Track position `{track}` is invalid")
        try:
            queue[track - 1]
            queue[to - 1]
        except IndexError:
            return await ctx.warn(f"Track position `{track}` is invalid (`1`/`{len(queue)}`)")

        _track = queue[track - 1]
        del queue[track - 1]
        queue.insert(to - 1, _track)
        await ctx.approve(f"Moved [**{_track.title}**]({_track.uri}) to position `{to}`")

    @commands.command(
        name="remove",
        usage="(index)",
        example="3",
        aliases=["rmv"],
    )
    async def remove(self, ctx: wock.Context, track: int):
        """Remove a track from the queue"""

        player: Player = await self.get_player(ctx, connect=False)
        queue = player.queue._queue

        if track < 1 or track > len(queue):
            return await ctx.warn(f"Track position `{track}` is invalid (`1`/`{len(queue)}`)")

        _track = queue[track - 1]
        del queue[track - 1]
        await ctx.approve(f"Removed [**{_track.title}**]({_track.uri}) from the queue")

    @commands.command(
        name="shuffle",
        aliases=["mix"],
    )
    async def shuffle(self, ctx: wock.Context):
        """Shuffle the queue"""

        player: Player = await self.get_player(ctx, connect=False)

        if queue := player.queue._queue:
            random.shuffle(queue)
            await ctx.message.add_reaction("🔀")
        else:
            await ctx.warn("There aren't any **tracks** in the queue")

    @commands.command(name="skip", aliases=["next", "sk"])
    async def skip(self, ctx: wock.Context):
        """Skip the current track"""

        player: Player = await self.get_player(ctx, connect=False)

        if player.is_playing:
            await ctx.message.add_reaction("⏭️")
            await player.skip()
        else:
            await ctx.warn("There isn't an active **track**")

    @commands.command(
        name="loop",
        usage="(track, queue, or off)",
        example="queue",
        aliases=["repeat", "lp"],
    )
    async def loop(self, ctx: wock.Context, option: Literal["track", "queue", "off"]):
        """Toggle looping for the current track or queue"""

        player: Player = await self.get_player(ctx, connect=False)

        if option == "off":
            if not player.loop:
                return await ctx.warn("There isn't an active **loop**")
        elif option == "track":
            if not player.is_playing:
                return await ctx.warn("There isn't an active **track**")
        elif option == "queue":
            if not player.queue._queue:
                return await ctx.warn("There aren't any **tracks** in the queue")

        await ctx.message.add_reaction("✅" if option == "off" else "🔂" if option == "track" else "🔁")
        await player.set_loop(option if option != "off" else False)

    @commands.command(name="pause")
    async def pause(self, ctx: wock.Context):
        """Pause the current track"""

        player: Player = await self.get_player(ctx, connect=False)

        if player.is_playing and not player.is_paused:
            await ctx.message.add_reaction("⏸️")
            await player.set_pause(True)
        else:
            await ctx.warn("There isn't an active **track**")

    @commands.command(name="resume", aliases=["rsm"])
    async def resume(self, ctx: wock.Context):
        """Resume the current track"""

        player: Player = await self.get_player(ctx, connect=False)

        if player.is_playing and player.is_paused:
            await ctx.message.add_reaction("✅")
            await player.set_pause(False)
        else:
            await ctx.warn("There isn't an active **track**")

    @commands.command(
        name="seek",
        usage="(position)",
        example="+30s",
        aliases=["ff", "rw"],
    )
    async def seek(self, ctx: wock.Context, position: str):
        """Seek to a specified position"""

        player: Player = await self.get_player(ctx, connect=False)

        if not player.is_playing:
            return await ctx.warn("There isn't an active **track**")

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
                    return await ctx.warn(f"Position `{position}` is invalid")
                milliseconds += int(m) * 60000
            if s := match.group("s"):
                if position.lower().endswith("m"):
                    milliseconds += int(s) * 60000
                else:
                    milliseconds += int(s) * 1000
            new_position = milliseconds
        else:
            return await ctx.warn(f"Position `{position}` is invalid")

        new_position = max(0, min(new_position, player.current.length))
        await player.seek(new_position)
        await ctx.message.add_reaction("✅")

    @commands.command(
        name="volume",
        usage="<percentage>",
        example="75",
        aliases=["vol", "v"],
    )
    async def volume(self, ctx: wock.Context, percentage: wock.Percentage = None):
        """Set the player volume"""

        player: Player = await self.get_player(ctx, connect=False)

        if percentage is None:
            return await ctx.neutral(f"Current volume: `{player.volume}%`")

        if not 0 <= percentage <= 100:
            return await ctx.warn("Please **provide** a **valid** percentage")

        await player.set_volume(percentage)
        await ctx.approve(f"Set **volume** to `{percentage}%`")

    @commands.command(name="disconnect", aliases=["dc", "stop"])
    async def disconnect(self, ctx: wock.Context):
        """Disconnect the music player"""

        player: Player = await self.get_player(ctx, connect=False)

        await player.teardown()
        await ctx.message.add_reaction("👋🏾")


async def setup(bot: wock.wockSuper):
    await bot.add_cog(music(bot))


class Player(pomice.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bound_channel: discord.TextChannel = None
        self.message: discord.Message = None
        self.track: pomice.Track = None
        self.queue: asyncio.Queue = asyncio.Queue()
        self.waiting: bool = False
        self.loop: str = False

    def _format_socket_track(self, track: pomice.Track):
        return {
            "url": track.uri,
            "title": track.title,
            "author": track.author,
            "length": functions.format_duration(track.length),
            "image": track.thumbnail,
        }

    def _format_socket_channel(self):
        return {
            "voice": {
                "id": self.channel.id,
                "name": self.channel.name,
                "members": [
                    {"id": member.id, "name": str(member), "avatar": (member.display_avatar.url if member.display_avatar else None)}
                    for member in self.channel.members
                    if not member.bot
                ],
            }
            if self.channel
            else None,
            "text": {"id": self.bound_channel.id, "name": self.bound_channel.name},
        }

    async def play(self, track: pomice.Track):
        await super().play(track)
        # await self.bot.socket.emit(
        #     {
        #         "type": "MUSIC",
        #         "guild_id": self.guild.id,
        #         "data": {
        #             "event": "TRACK-START",
        #             "track": self._format_socket_track(track),
        #             "queue": [self._format_socket_track(track) for track in self.queue._queue],
        #             "channel": self._format_socket_channel(),
        #         },
        #     }
        # )

    async def insert(self, track: pomice.Track, filter: bool = True, bump: bool = False):
        if filter and track.info.get("sourceName", "Spotify") == "youtube":
            response = await self.bot.session.get(
                "https://metadata-filter.vercel.app/api/youtube",
                params=dict(track=track.title),
            )
            data = await response.json()

            if data.get("status") == "success":
                track.title = data["data"].get("track")

        if bump:
            queue = self.queue._queue
            queue.insert(0, track)
        else:
            await self.queue.put(track)

        # await self.bot.socket.emit(
        #     {
        #         "type": "MUSIC",
        #         "guild_id": self.guild.id,
        #         "data": {
        #             "event": "TRACK-QUEUE",
        #             "track": self._format_socket_track(track),
        #             "queue": [self._format_socket_track(track) for track in self.queue._queue],
        #             "channel": self._format_socket_channel(),
        #         },
        #     }
        # )

        return True

    async def next_track(self, ignore_playing: bool = False):
        if not ignore_playing:
            if self.is_playing or self.waiting:
                return

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
        if self.bound_channel and self.loop != "track":
            try:
                if self.message:
                    async for message in self.bound_channel.history(limit=15):
                        if message.id == self.message.id:
                            with suppress(discord.HTTPException):
                                await message.delete()
                            break

                self.message = await track.ctx.neutral(f"Now playing [**{track.title}**]({track.uri})")
            except:
                self.bound_channel = None

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
            await self.reset_filters()
            await self.destroy()
        except:
            pass

    def __repr__(self):
        return f"<wock.Player guild={self.guild.id} connected={self.is_connected} playing={self.is_playing}>"
