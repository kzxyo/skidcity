import asyncio
import contextlib
import re
import sys

from weakref import WeakValueDictionary

import discord

from asyncpg import Record
from discord.ext import commands

from helpers import functions, wock


class starboard(commands.Cog, name="Starboard"):
    def __init__(self, bot):
        self.bot: wock.wockSuper = bot
        self._locks: WeakValueDictionary[int, asyncio.Lock] = WeakValueDictionary()
        self._about_to_be_deleted: set[int] = set()

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    async def reaction_logic(self, fmt: str, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        channel = guild.get_channel(payload.channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            return

        if not (method := getattr(self, f"{fmt}_message", None)):
            return

        if (
            not (
                starboard := await self.bot.db.fetchrow(
                    "SELECT channel_id, emoji, threshold FROM starboard WHERE guild_id = $1 AND emoji = $2",
                    guild.id,
                    str(payload.emoji),
                )
            )
            or not (starboard_channel := guild.get_channel(starboard["channel_id"]))
            or channel.id == starboard_channel.id
            or not starboard_channel.permissions_for(guild.me).send_messages
        ):
            return

        if not (member := payload.member or guild.get_member(payload.user_id)):
            return

        try:
            await method(starboard, starboard_channel, guild, channel, member, payload.message_id)
        except:
            return

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return

        await self.bot.db.execute(
            "DELETE FROM starboard WHERE guild_id = $1 AND channel_id = $2",
            channel.guild.id,
            channel.id,
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.reaction_logic("star", payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.reaction_logic("unstar", payload)

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload: discord.RawReactionClearEmojiEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        channel = guild.get_channel(payload.channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            return

        starboard_entry = await self.bot.db.fetchrow(
            "DELETE FROM starboard_entries WHERE message_id = $1 RETURNING emoji, starboard_message_id",
            payload.message_id,
        )
        if not starboard_entry:
            return

        if not (
            starboard := await self.bot.db.fetchrow(
                "SELECT channel_id FROM starboard WHERE guild_id = $1 AND emoji = $2",
                guild.id,
                starboard_entry["emoji"],
            )
        ):
            return

        if not (starboard_channel := guild.get_channel(starboard["channel_id"])):
            return

        with contextlib.suppress(discord.HTTPException):
            await starboard_channel.delete_messages([discord.Object(id=starboard_entry["starboard_message_id"])])

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if payload.message_id in self._about_to_be_deleted:
            self._about_to_be_deleted.discard(payload.message_id)
            return

        await self.bot.db.execute(
            "DELETE FROM starboard_entries WHERE guild_id = $1 AND starboard_message_id = $2",
            payload.guild_id,
            payload.message_id,
        )

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent):
        if payload.message_ids <= self._about_to_be_deleted:
            self._about_to_be_deleted.difference_update(payload.message_ids)
            return

        await self.bot.db.execute(
            "DELETE FROM starboard_entries WHERE guild_id = $1 AND starboard_message_id = ANY($2::BIGINT[])",
            payload.guild_id,
            list(payload.message_ids),
        )

    async def star_message(
        self,
        starboard: Record,
        starboard_channel: discord.TextChannel | discord.Thread,
        guild: discord.Guild,
        channel: discord.TextChannel,
        member: discord.Member,
        message_id: int,
    ):
        lock = self._locks.get(guild.id)
        if not lock:
            self._locks[guild.id] = lock = asyncio.Lock()

        async with lock:
            if channel.is_nsfw() and not starboard_channel.is_nsfw():
                return

            if not (message := await channel.fetch_message(message_id)):
                return

            if message.author.id == member.id and not starboard.get("self_star", True):
                return

            if (len(message.content) == 0 and len(message.attachments) == 0) or message.type not in (
                discord.MessageType.default,
                discord.MessageType.reply,
            ):
                return

            reaction = [reaction for reaction in message.reactions if str(reaction.emoji) == starboard["emoji"]]
            if reaction:
                reaction = reaction[0]
            else:
                return

            starboard_message_id = await self.bot.db.fetchval(
                "SELECT starboard_message_id FROM starboard_entries WHERE guild_id = $1 AND channel_id = $2 AND message_id = $3 AND emoji = $4",
                guild.id,
                channel.id,
                message.id,
                starboard["emoji"],
            )

            content, embed, files = await self.render_starboard_entry(starboard, reaction, message)

            if starboard_message_id and (starboard_message := starboard_channel.get_partial_message(starboard_message_id)):
                try:
                    await starboard_message.edit(
                        content=content,
                    )
                except discord.HTTPException:
                    pass
                else:
                    return

            try:
                starboard_message = await starboard_channel.send(
                    content=content,
                    embed=embed,
                    files=files,
                )
            except discord.HTTPException:
                return

            await self.bot.db.execute(
                "INSERT INTO starboard_entries (guild_id, channel_id, message_id, emoji, starboard_message_id) VALUES ($1, $2, $3, $4, $5) ON"
                " CONFLICT (guild_id, channel_id, message_id, emoji) DO UPDATE SET starboard_message_id = $5",
                guild.id,
                channel.id,
                message.id,
                starboard["emoji"],
                starboard_message.id,
            )

    async def unstar_message(
        self,
        starboard: Record,
        starboard_channel: discord.TextChannel | discord.Thread,
        guild: discord.Guild,
        channel: discord.TextChannel,
        member: discord.Member,
        message_id: int,
    ):
        lock = self._locks.get(guild.id)
        if not lock:
            self._locks[guild.id] = lock = asyncio.Lock()

        async with lock:
            starboard_message_id = await self.bot.db.fetchval(
                "SELECT starboard_message_id FROM starboard_entries WHERE guild_id = $1 AND channel_id = $2 AND message_id = $3 AND emoji = $4",
                guild.id,
                channel.id,
                message_id,
                starboard["emoji"],
            )
            if not starboard_message_id:
                return

            if not (message := await channel.fetch_message(message_id)):
                return

            reaction = [reaction for reaction in message.reactions if str(reaction.emoji) == starboard["emoji"]]
            if reaction:
                reaction = reaction[0]
            else:
                with contextlib.suppress(discord.HTTPException):
                    await starboard_channel.delete_messages([discord.Object(id=starboard_message_id)])

                await self.bot.db.execute(
                    "DELETE FROM starboard_entries WHERE starboard_message_id = $1",
                    starboard_message_id,
                )
                return

            content, embed, files = await self.render_starboard_entry(starboard, reaction, message)

            try:
                await starboard_channel.get_partial_message(starboard_message_id).edit(
                    content=content,
                )
            except discord.HTTPException:
                await self.bot.db.execute(
                    "DELETE FROM starboard_entries WHERE starboard_message_id = $1",
                    starboard_message_id,
                )

    async def render_starboard_entry(
        self,
        starboard: Record,
        reaction: discord.Reaction,
        message: discord.Message,
    ):
        if message.embeds and (embed := message.embeds[0]) and not embed.type in ("image", "gifv"):
            embed = embed
        else:
            embed = discord.Embed(color=starboard.get("color"))

        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.display_avatar,
            url=message.jump_url,
        )
        embed.description = (
            f"{functions.shorten(message.content, 2048) if message.system_content else ''}\n{functions.shorten(embed.description, 2048) if embed.description else ''}"
        )

        if message.embeds and (_embed := message.embeds[0]) and (_embed.url and _embed.type in ("image", "gifv")):
            embed.description = embed.description.replace(_embed.url, "")
            if _embed.type == "image":
                embed.set_image(url=_embed.url)
            elif _embed.type == "gifv":
                response = await self.bot.session.get(_embed.url)
                if response.status == 200:
                    data = await response.text()
                    try:
                        tenor_url = re.findall(r"(?i)\b((https?://c[.]tenor[.]com/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))[.]gif)", data)[
                            0
                        ][0]
                    except IndexError:
                        pass
                    else:
                        embed.set_image(url=tenor_url)
                else:
                    embed.set_image(url=_embed.thumbnail.url)

        files = list()
        for attachment in message.attachments:
            if attachment.url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                embed.set_image(url=attachment.url)
            elif attachment.url.lower().endswith((".mp4", ".mov", ".webm", "mp3", ".ogg", ".wav")):
                attachment = await attachment.to_file()
                if not sys.getsizeof(attachment.fp) > message.guild.filesize_limit:
                    files.append(attachment)

        if message.reference and (reference := message.reference.resolved):
            embed.add_field(
                name=f"**Replying to {reference.author.display_name}**",
                value=f"[Jump to reply]({reference.jump_url})",
                inline=False,
            )

        embed.add_field(
            name=f"**#{message.channel}**",
            value=f"[Jump to message]({message.jump_url})",
            inline=False,
        )
        embed.timestamp = message.created_at

        reactions = f"#{reaction.count:,}"
        if str(reaction.emoji) == "⭐":
            if 5 > reaction.count >= 0:
                reaction = "⭐"
            elif 10 > reaction.count >= 5:
                reaction = "🌟"
            elif 25 > reaction.count >= 10:
                reaction = "💫"
            else:
                reaction = "✨"
        else:
            reaction = str(reaction.emoji)

        return f"{reaction} **{reactions}**", embed, files

    @commands.group(
        name="starboard",
        usage="(subcommand) <args>",
        example="add #shame 🤡",
        aliases=["board", "star", "sb"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def starboard(self, ctx: wock.Context):
        """Save important messages to a designated channel"""

        await ctx.send_help()

    @starboard.command(
        name="add",
        usage="(channel) (emoji)",
        example="#shame 🤡 --threshold 4",
        parameters={
            "threshold": {
                "converter": int,
                "description": "The number of reactions required to be saved",
                "default": 3,
                "minimum": 1,
                "maximum": 120,
                "aliases": ["amount", "count"],
            }
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_guild=True)
    async def starboard_add(
        self,
        ctx: wock.Context,
        channel: discord.TextChannel | discord.Thread,
        emoji: str,
    ):
        """Add a starboard for a channel"""

        try:
            await ctx.message.add_reaction(emoji)
        except discord.HTTPException:
            return await ctx.warn(f"**{emoji}** is not a valid emoji")

        try:
            await self.bot.db.execute(
                "INSERT INTO starboard (guild_id, channel_id, emoji, threshold) VALUES ($1, $2, $3, $4)",
                ctx.guild.id,
                channel.id,
                emoji,
                ctx.parameters.get("threshold"),
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There is already a **starboard** using **{emoji}**")
        else:
            await ctx.approve(f"Added a **starboard** for {channel.mention} using **{emoji}**")

    @starboard.command(
        name="remove",
        usage="(channel) (emoji)",
        example="#shame 🤡",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_guild=True)
    async def starboard_remove(
        self,
        ctx: wock.Context,
        channel: discord.TextChannel | discord.Thread,
        emoji: str,
    ):
        """Remove a starboard from a channel"""

        try:
            await self.bot.db.execute(
                "DELETE FROM starboard WHERE guild_id = $1 AND channel_id = $2 AND emoji = $3",
                ctx.guild.id,
                channel.id,
                emoji,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There isn't a **starboard** using **{emoji}**")
        else:
            await ctx.approve(f"Removed the **starboard** for {channel.mention} using **{emoji}**")

    @starboard.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_guild=True)
    async def starboard_list(self, ctx: wock.Context):
        """View all starboards"""

        starboards = [
            f"{channel.mention} - **{row['emoji']}** (threshold: `{row['threshold']}`)"
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id, emoji, threshold FROM starboard WHERE guild_id = $1",
                ctx.guild.id,
            )
            if (channel := ctx.guild.get_channel(row["channel_id"]))
        ]
        if not starboards:
            return await ctx.warn("No **starboards** have been set up")

        await ctx.paginate(
            discord.Embed(
                title="Starboards",
                description=starboards,
            )
        )


async def setup(bot: wock.wockSuper):
    await bot.add_cog(starboard(bot))
