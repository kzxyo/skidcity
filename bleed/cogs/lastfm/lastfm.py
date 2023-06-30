from asyncspotify import Client as SpotifyClient
from asyncspotify import ClientCredentialsFlow as SpotifyClientCredentialsFlow
from discord import Message
from discord.ext.commands import (
    BucketType,
    Cog,
    command,
    cooldown,
    group,
    has_permissions,
)

import config

from helpers import services
from helpers.bleed import Bleed
from helpers.managers import Context


class Lastfm(Cog, name="Last.fm"):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot
        self.spotify_client: SpotifyClient = SpotifyClient(
            SpotifyClientCredentialsFlow(
                client_id=config.Authorization.Spotify.client_id,
                client_secret=config.Authorization.Spotify.client_secret,
            )
        )

    async def cog_load(self) -> None:
        await self.spotify_client.authorize()

    @group(
        name="lastfm",
        aliases=["lfm", "lf"],
        invoke_without_command=True,
    )
    async def lastfm(self, ctx: Context) -> Message:
        """Interact with Last.fm through bleed"""

        return await ctx.neutral(
            "View the **Last.fm** commands at https://bleed.bot/help",
            emoji=":information_source:",
        )

    @lastfm.command(
        name="set", usage="(username)", example="a_valid_username", aliases=["link"]
    )
    @cooldown(1, 30, BucketType.user)
    async def lastfm_set(self, ctx: Context, username: str) -> Message:
        """
        Set your Last.fm username
        """

        profile = await services.lastfm.profile(
            self.bot.session,
            username=username,
        )

        message = await ctx.neutral(
            "Updating new account **Last.fm library**...", emoji=":gear:"
        )
        await ctx.approve(
            f"Success, your **Last.fm** username has been set set to [**{profile.username}**]({profile.url})",
            previous_message=message,
        )

    @lastfm.command(
        name="react",
        usage="(upvote reaction) (downvote reaction)",
        example="👍 👎",
        aliases=[
            "reaction",
            "reactions",
        ],
    )
    @has_permissions(manage_guild=True)
    async def lastfm_react(self, ctx: Context, upvote: str, downvote: str) -> Message:
        """
        Set server upvote and downvote reaction for Now Playing
        """

        try:
            for reaction in (upvote, downvote):
                await ctx.message.add_reaction(reaction)
        except:
            return await ctx.warn(
                "An **invalid** emote or emoji was passed. Ensure that the emotes being passed are in a server **shared** with me."
            )

        await self.bot.db.execute(
            """
            INSERT INTO config (
                guild_id,
                lastfm_reactions
            ) VALUES($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET 
                lastfm_reactions = EXCLUDED.lastfm_reactions;
            """,
            ctx.guild.id,
            [upvote, downvote],
        )

        return await ctx.approve(
            f"Enabled **reactions** for `nowplaying` to {upvote} and {downvote}"
        )

    @command(
        name="itunes",
        usage="<query>",
        example="Lucki Politics",
        aliases=[
            "it",
        ],
    )
    async def itunes(self, ctx: Context, *, query: str = None) -> Message:
        """
        Finds a song from the iTunes API
        """

        if not query:
            return await ctx.send_help()

        data = await self.bot.session.request(
            "GET",
            "https://itunes.apple.com/search",
            params={
                "term": query,
                "media": "music",
                "limit": 1,
            },
        )
        if not data.results:
            return await ctx.warn(f"No results found on iTunes for **{query}**")

        return await ctx.send(data.results[0].trackViewUrl)

    @command(
        name="spotifyalbum",
        usage="<query>",
        example="Lucki Freewave 3",
        aliases=["spalbum"],
    )
    async def spotifyalbum(self, ctx: Context, *, query: str = None) -> Message:
        """
        Finds album results from the Spotify API
        """

        if not query:
            return await ctx.send_help()

        data = await self.spotify_client.search_album(q=query)
        if not data:
            return await ctx.warn(f"No results found on Spotify for **{query}**")

        return await ctx.send(data.link)

    @command(
        name="spotifytrack",
        usage="<query>",
        example="Lucki Geek Monster",
        aliases=[
            "sptrack",
            "spotify",
            "sp",
        ],
    )
    async def spotifytrack(self, ctx: Context, *, query: str = None) -> Message:
        """
        Finds track results from the Spotify API
        """

        if not query:
            return await ctx.send_help()

        data = await self.spotify_client.search_track(q=query)
        if not data:
            return await ctx.warn(f"No results found on Spotify for **{query}**")

        return await ctx.send(data.link)
