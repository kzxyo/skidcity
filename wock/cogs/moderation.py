import asyncio
import contextlib
import io
import os
import re
import tempfile

from copy import copy
from datetime import timedelta
from typing import Literal, Optional, Union

import discord

from discord.ext import commands
from PIL import Image

from helpers import functions, regex, views, wock


class moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot: wock.wockSuper = bot
        self.case_lock: asyncio.Lock = asyncio.Lock()
        self.pretty_actions: dict = {
            "guild_update": "updated server",
            "channel_create": "created channel",
            "channel_update": "updated channel",
            "channel_delete": "deleted channel",
            "overwrite_create": "created channel permission",
            "overwrite_update": "updated channel permission",
            "overwrite_delete": "deleted channel permission",
            "kick": "kicked member",
            "member_prune": "pruned members",
            "ban": "banned member",
            "unban": "unbanned member",
            "member_update": "updated member",
            "member_role_update": "updated member roles",
            "member_disconnect": "disconnected member",
            "bot_add": "added bot",
            "role_create": "created role",
            "role_update": "updated role",
            "role_delete": "deleted role",
            "invite_create": "created invite",
            "invite_update": "updated invite",
            "invite_delete": "deleted invite",
            "webhook_create": "created webhook",
            "webhook_update": "updated webhook",
            "webhook_delete": "deleted webhook",
            "emoji_create": "created emoji",
            "emoji_update": "updated emoji",
            "emoji_delete": "deleted emoji",
            "message_delete": "deleted message by",
            "message_bulk_delete": "bulk deleted messages in",
            "message_pin": "pinned message by",
            "message_unpin": "unpinned message by",
            "integration_create": "created integration",
            "integration_update": "updated integration",
            "integration_delete": "deleted integration",
            "sticker_create": "created sticker",
            "sticker_update": "updated sticker",
            "sticker_delete": "deleted sticker",
            "thread_create": "created thread",
            "thread_update": "updated thread",
            "thread_delete": "deleted thread",
        }

    async def moderation_entry(
        self,
        ctx: wock.Context,
        target: discord.Member | discord.User | discord.Role | discord.TextChannel | str,
        action: str,
        reason: str = "No reason provided",
    ):
        """Create a log entry for moderation actions"""

        jail_log = await self.bot.db.fetch_config(ctx.guild.id, "jail_log")
        channel = self.bot.get_channel(jail_log)
        if not channel:
            return

        async with self.case_lock:
            case = await self.bot.db.fetchval("SELECT COUNT(*) FROM cases WHERE guild_id = $1", ctx.guild.id) + 1

            if type(target) in (discord.Member, discord.User):
                _TARGET = "Member"
            elif type(target) is discord.Role:
                _TARGET = "Role"
            elif type(target) is discord.TextChannel:
                _TARGET = "Channel"
            else:
                _TARGET = "Target"

            embed = discord.Embed(
                description=(discord.utils.format_dt(discord.utils.utcnow(), "F") + " (" + discord.utils.format_dt(discord.utils.utcnow(), "R") + ")")
            )
            embed.set_author(name="Moderation Entry", icon_url=ctx.author.avatar)
            embed.add_field(
                name=f"**Case #{case:,} | {action.title()}** ",
                value=f"""
                > **Moderator:** {ctx.author} (`{ctx.author.id}`)
                > **{_TARGET}:** {target} (`{target.id}`)
                > **Reason:** {reason}
                """,
            )

            try:
                message = await channel.send(embed=embed)
            except discord.Forbidden:
                await self.bot.db.update_config(ctx.guild.id, "jail_log", None)
            else:
                await self.bot.db.execute(
                    "INSERT INTO cases (guild_id, case_id, case_type, message_id, moderator_id, target_id, moderator, target, reason, timestamp)"
                    " VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
                    ctx.guild.id,
                    case,
                    action.lower(),
                    message.id,
                    ctx.author.id,
                    target.id,
                    str(ctx.author),
                    str(target),
                    reason,
                    message.created_at,
                )

    async def invoke_message(
        self,
        ctx: wock.Context,
        default_function: str,
        default_message: str = None,
        **kwargs,
    ):
        """Send the moderation invoke message"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "invoke") or {}
        if script := configuration.get((kwargs.pop("command", None) or ctx.command.qualified_name).replace(" ", ".")):
            script = wock.EmbedScript(script)
            try:
                await script.send(
                    ctx,
                    bot=self.bot,
                    guild=ctx.guild,
                    channel=kwargs.pop("channel", None) or ctx.channel,
                    moderator=ctx.author,
                    **kwargs,
                )
            except:
                return
        else:
            if default_message:
                await default_function(default_message)
            else:
                await default_function()

    @commands.Cog.listener("on_member_update")
    async def force_nickname(self, before: discord.Member, after: discord.Member):
        """Listen for nickname changes and force them back"""

        if before.nick == after.nick:
            return

        if nick := await self.bot.redis.get(f"nickname:{functions.hash(f'{after.guild.id}-{after.id}')}"):
            if nick != after.nick:
                with contextlib.suppress(discord.Forbidden):
                    await after.edit(nick=nick, reason="Nickname locked")

    @commands.Cog.listener("on_member_join")
    async def force_nickname_rejoin(self, member: discord.Member):
        """Listen for members joining and force their nickname"""

        if nick := await self.bot.redis.get(f"nickname:{functions.hash(f'{member.guild.id}-{member.id}')}"):
            with contextlib.suppress(discord.Forbidden):
                await member.edit(nick=nick, reason="Nickname locked")

    @commands.command(
        name="audit",
        usage="<user> <action>",
        example="@rx#1337 ban",
    )
    @commands.has_permissions(view_audit_log=True)
    async def audit(self, ctx: wock.Context, user: Optional[Union[discord.Member, discord.User]] = None, action: Optional[str] = None):
        """View audit log entries"""

        if action and not self.pretty_actions.get(action.lower().replace(" ", "_")):
            return await ctx.warn(f"`{action}` isn't a recognized **action**")

        entries = list()
        METHOD = (
            ctx.guild.audit_logs(limit=100, user=user, action=getattr(discord.AuditLogAction, action.lower().replace(" ", "_")))
            if action and user
            else ctx.guild.audit_logs(limit=100, user=user)
            if user
            else ctx.guild.audit_logs(limit=100, action=getattr(discord.AuditLogAction, action.lower().replace(" ", "_")))
            if action
            else ctx.guild.audit_logs(limit=100)
        )
        async for entry in METHOD:
            pretty_action = self.pretty_actions.get(entry.action.name)
            if not pretty_action:
                continue

            target = None
            with contextlib.suppress(TypeError):
                if target := getattr(entry, "target", None):
                    if type(target) is discord.TextChannel:
                        target = f"#{target.name}"
                    elif type(target) is discord.Role:
                        target = f"@{target.name}"
                    elif type(target) is discord.Emoji:
                        target = target.name
                    else:
                        if isinstance(target, discord.Object):
                            target = target.id
                        else:
                            target = str(target)

            entries.append(f"**{entry.user}** {pretty_action}" + (f" `{target}`" if target else ""))

        if not entries:
            return await ctx.warn(
                "No **audit log** entries found" + (f" for **{user}**" if user else "") + (f" with action **{action.name}**" if action else "")
            )

        await ctx.paginate(
            discord.Embed(
                title="Audit Log",
                description=entries,
            ),
        )

    @commands.command(
        name="nuke",
        usage="<channel>",
        example="#chat",
    )
    @commands.has_permissions(guild_owner=True)
    async def nuke(self, ctx: wock.Context, *, channel: discord.TextChannel = None):
        """Clone the channel"""

        channel = channel or ctx.channel

        try:
            await channel.delete()
        except Exception as error:
            return await ctx.warn(f"Couldn't delete {channel.mention}\n```\n{error}```")

        _channel = await channel.clone()
        await _channel.edit(position=channel.position)
        ctx = copy(ctx)
        ctx.channel = _channel

        await self.invoke_message(ctx, _channel.send, "first", channel=_channel)
        await self.moderation_entry(ctx, _channel, "nuke")
        if channel != ctx.channel:
            await ctx.react_check()

        await self.bot.db.execute(
            f"""
            UPDATE welcome_channels SET channel_id = {_channel.id} WHERE channel_id = {channel.id};
            UPDATE goodbye_channels SET channel_id = {_channel.id} WHERE channel_id = {channel.id};
            UPDATE boost_channels SET channel_id = {_channel.id} WHERE channel_id = {channel.id};
            UPDATE sticky_messages SET channel_id = {_channel.id} WHERE channel_id = {channel.id};
            UPDATE youtube_channels SET channel_id = {_channel.id} WHERE channel_id = {channel.id};
            UPDATE commands.ignored SET target_id = {_channel.id} WHERE target_id = {channel.id};
            UPDATE commands.disabled SET channel_id = {_channel.id} WHERE channel_id = {channel.id};
        """
        )

    @commands.group(
        name="set",
        usage="(subcommand) <args>",
        example="banner dscord.com/chnls/999/..png",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx: wock.Context):
        """Set server settings through wock"""

        await ctx.send_help()

    @_set.command(
        name="name",
        usage="(text)",
        example="wock guild",
        aliases=["n"],
    )
    @commands.has_permissions(manage_guild=True)
    async def set_name(self, ctx: wock.Context, *, text: str):
        """Set the server name"""

        if len(text) > 100:
            return await ctx.warn("The **server name** can't be longer than **100** characters")

        try:
            await ctx.guild.edit(name=text, reason=f"Name set by {ctx.author} ({ctx.author.id})")
        except discord.HTTPException:
            return await ctx.warn(f"Couldn't set the **server name** to **{text}**")

        await self.invoke_message(ctx, ctx.approve, f"Set the **server name** to **{text}**", text=text)

    @_set.command(
        name="icon",
        usage="(image)",
        example="https://dscord.com/chnls/999/..png",
        aliases=["i"],
    )
    @commands.has_permissions(manage_guild=True)
    async def set_icon(self, ctx: wock.Context, *, image: wock.ImageFinder = None):
        """Set the server icon"""

        image = image or await wock.ImageFinder.search(ctx)

        async with ctx.typing():
            response = await self.bot.session.get(image)
            buffer = await response.read()

            try:
                await ctx.guild.edit(
                    icon=buffer,
                    reason=f"Banner set by {ctx.author} ({ctx.author.id})",
                )
            except discord.HTTPException:
                return await ctx.warn(f"Couldn't set the **server icon** to [**image**]({image})")

        await self.invoke_message(ctx, ctx.approve, f"Set the **server icon** to [**image**]({image})", image=image)

    @_set.command(
        name="banner",
        usage="(image)",
        example="https://dscord.com/chnls/999/..png",
        aliases=["background", "b"],
    )
    @commands.has_permissions(manage_guild=True)
    async def set_banner(self, ctx: wock.Context, *, image: wock.ImageFinder = None):
        """Set the server banner"""

        image = image or await wock.ImageFinder.search(ctx)

        async with ctx.typing():
            response = await self.bot.session.get(image)
            buffer = await response.read()

            try:
                await ctx.guild.edit(
                    banner=buffer,
                    reason=f"Banner set by {ctx.author} ({ctx.author.id})",
                )
            except discord.HTTPException:
                return await ctx.warn(f"Couldn't set the **server banner** to [**image**]({image})")

        await self.invoke_message(ctx, ctx.approve, f"Set the **server banner** to [**image**]({image})", image=image)

    @_set.command(
        name="channel",
        usage="<name or topic> (text)",
        example="name bots",
    )
    @commands.has_permissions(manage_channels=True)
    async def set_channel(
        self,
        ctx: wock.Context,
        option: Literal["name", "topic"],
        *,
        text: str,
    ):
        """Set the channel name or topic"""

        if not isinstance(ctx.channel, discord.TextChannel):
            return await ctx.warn("This command can only be used in a **text channel**")

        try:
            if option == "name":
                await ctx.channel.edit(name=text)
            else:
                await ctx.channel.edit(topic=text)
        except discord.HTTPException:
            return await ctx.warn(f"Couldn't set the **channel {option}** to **{text}**")
        except discord.RateLimited as error:
            return await ctx.warn(f"Couldn't set the **channel {option}** because of a **rate limit** (`{error.retry_after:.2f}s`)")

        await self.invoke_message(ctx, ctx.approve, f"Set the **channel {option}** to `{text}`", option=option, text=text)

    @commands.group(
        name="nickname",
        usage="<member> (text)",
        example="rx#1337 daddy rx",
        aliases=["nick", "n"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(
        self,
        ctx: wock.Context,
        member: Optional[wock.Member] = None,
        *,
        text: str,
    ):
        """Set the nickname of a user"""

        member = member or ctx.author
        await wock.Member().hierarchy(ctx, member, author=True)

        if len(text) > 32:
            return await ctx.warn("The **nickname** can't be longer than **32** characters")

        if await self.bot.redis.exists(f"nickname:{functions.hash(f'{ctx.guild.id}-{member.id}')}"):
            return await ctx.warn(f"**{member}**'s nickname is currently **locked**\n> Use `{ctx.prefix}nickname force cancel` to unlock it")

        try:
            await member.edit(nick=text, reason=f"Nickname set by {ctx.author} ({ctx.author.id})")
        except discord.HTTPException:
            return await ctx.warn(f"Couldn't set the **nickname** to **{text}**")

        await self.invoke_message(ctx, ctx.approve, f"Set **{member}**'s nickname to `{text}`", user=member, text=text)

    @nickname.command(
        name="remove",
        usage="<member>",
        example="rx#1337",
        aliases=["reset", "rm"],
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nickname_remove(
        self,
        ctx: wock.Context,
        member: Optional[wock.Member] = None,
    ):
        """Remove the nickname of a user"""

        member = member or ctx.author
        await wock.Member().hierarchy(ctx, member, author=True)

        if not member.nick:
            return await ctx.warn(f"**{member}** doesn't have a **nickname**")

        if await self.bot.redis.exists(f"nickname:{functions.hash(f'{ctx.guild.id}-{member.id}')}"):
            return await ctx.warn(f"**{member}**'s nickname is currently **locked**\n> Use `{ctx.prefix}nickname force cancel` to unlock it")

        try:
            await member.edit(nick=None, reason=f"Nickname removed by {ctx.author} ({ctx.author.id})")
        except discord.HTTPException:
            return await ctx.warn(f"Couldn't remove **{member}**'s nickname")

        await self.invoke_message(ctx, ctx.approve, f"Removed **{member}**'s nickname", user=member)

    @nickname.group(
        name="force",
        usage="(member) <duration> (text)",
        example="eeepy#1993 4h slut",
        aliases=["lock"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nickname_force(
        self,
        ctx: wock.Context,
        member: wock.Member,
        duration: Optional[wock.TimeConverter],
        *,
        text: str,
    ):
        """Restrict the user from changing their nickname"""

        await wock.Member().hierarchy(ctx, member)

        if len(text) > 32:
            return await ctx.warn("The **nickname** can't be longer than **32** characters")

        if text:
            try:
                await member.edit(nick=text, reason=f"Nickname locked by {ctx.author} ({ctx.author.id})")
            except discord.HTTPException:
                return await ctx.warn(f"Couldn't set the **nickname** to **{text}**")

            await self.bot.redis.set(f"nickname:{functions.hash(f'{ctx.guild.id}-{member.id}')}", text, ex=(duration.seconds if duration else None))
            await self.invoke_message(ctx, ctx.approve, f"Now **forcing nickname** for **{member}**", user=member, text=text)

    @nickname_force.command(
        name="cancel",
        usage="(member)",
        example="eeepy#1993",
        aliases=["stop", "end"],
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nickname_force_cancel(
        self,
        ctx: wock.Context,
        *,
        member: wock.Member,
    ):
        """Cancel the nickname lock"""

        await wock.Member().hierarchy(ctx, member, author=True)

        if not await self.bot.redis.exists(f"nickname:{functions.hash(f'{ctx.guild.id}-{member.id}')}"):
            return await ctx.warn(f"Not **forcing nickname** for **{member}**")

        await self.bot.redis.delete(f"nickname:{functions.hash(f'{ctx.guild.id}-{member.id}')}")
        try:
            await member.edit(nick=None, reason=f"Nickname lock cancelled by {ctx.author} ({ctx.author.id})")
        except discord.HTTPException:
            pass

        await self.invoke_message(ctx, ctx.approve, f"No longer **forcing nickname** for **{member}**", user=member)

    @commands.command(
        name="reason",
        usage="<case ID> (reason)",
        example="User was spamming",
        aliases=["rsn"],
    )
    @commands.has_permissions(manage_messages=True)
    async def reason(self, ctx: wock.Context, case_id: Optional[int], *, reason: str):
        """Update a moderation case reason"""

        case = await self.bot.db.fetchrow(
            "SELECT * FROM cases WHERE guild_id = $1 AND (case_id = $2 OR case_id = (SELECT MAX(case_id) FROM cases WHERE guild_id = $1))",
            ctx.guild.id,
            case_id or 0,
        )
        if not case:
            return await ctx.warn("There aren't any **cases** in this server")
        elif case_id and case["case_id"] != case_id:
            return await ctx.warn(f"Couldn't find a **case** with the ID `{case_id}`")

        try:
            jail_log = await self.bot.db.fetch_config(ctx.guild.id, "jail_log")
            if channel := self.bot.get_channel(jail_log):
                message = await channel.fetch_message(case["message_id"])

                embed = message.embeds[0]
                field = embed.fields[0]
                embed.set_field_at(0, name=field.name, value=(field.value.replace(f"**Reason:** {case['reason']}", f"**Reason:** {reason}")))
                await message.edit(embed=embed)
        except:
            pass

        await self.bot.db.execute("UPDATE cases SET reason = $3 WHERE guild_id = $1 AND case_id = $2", ctx.guild.id, case["case_id"], reason)
        await self.invoke_message(ctx, ctx.react_check, case_id=case["case_id"], reason=reason)

    @commands.group(
        name="history",
        usage="(user)",
        example="eeepy#1993",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_messages=True)
    async def history(self, ctx: wock.Context, *, user: wock.Member | wock.User):
        """View punishment history for a user"""

        cases = await self.bot.db.fetch(
            "SELECT * FROM cases WHERE guild_id = $1 AND target_id = $2 ORDER BY case_id DESC",
            ctx.guild.id,
            user.id,
        )
        if not cases:
            return await ctx.warn(f"**{user}** doesn't have any **cases** in this server")

        embed = discord.Embed(
            title=f"Punishment History for {user}",
        )
        embeds = []

        for case in cases:
            embed.add_field(
                name=f"**Case #{case['case_id']} | {case['case_type'].title()}**",
                value=(
                    f"{(discord.utils.format_dt(case['timestamp'], 'F') + ' (' + discord.utils.format_dt(case['timestamp'], 'R') + ')')}\n>>>"
                    f" **Moderator:** {self.bot.get_user(case['moderator_id'] or case['moderator'])}\n**Reason:** {case['reason']}"
                ),
                inline=False,
            )

            if len(embed.fields) == 3:
                embeds.append(embed.copy())
                embed.clear_fields()

        if embed.fields:
            embeds.append(embed.copy())

        await ctx.paginate(embeds)

    @history.command(
        name="remove",
        usage="(user) (case ID)",
        example="eeepy#1993 9",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_messages=True)
    async def history_remove(
        self,
        ctx: wock.Context,
        user: wock.Member | wock.User,
        case_id: int,
    ):
        """Remove a punishment from a user's history"""

        try:
            await self.bot.db.execute(
                "DELETE FROM cases WHERE guild_id = $1 AND target_id = $2 AND case_id = $3",
                ctx.guild.id,
                user.id,
                case_id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"Couldn't find a **case** with the ID `{case_id}` for **{user}**")
        else:
            await ctx.react_check()

    @history.command(
        name="reset",
        usage="(user)",
        example="eeepy#1993",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_messages=True)
    async def history_reset(self, ctx: wock.Context, user: wock.Member | wock.User):
        """Reset a user's punishment history"""

        await ctx.prompt(f"Are you sure you want to **reset** all punishment history for **{user}**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM cases WHERE guild_id = $1 AND target_id = $2",
                ctx.guild.id,
                user.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"**{user}** doesn't have any **cases** in this server")
        else:
            await ctx.react_check()

    @commands.command(
        name="timeout",
        usage="(member) (duration) <reason>",
        example="rx#1337 7d bullying members",
        aliases=["tmout", "tmo", "to"],
    )
    @commands.has_permissions(manage_messages=True)
    async def timeout(
        self,
        ctx: wock.Context,
        member: wock.Member,
        duration: wock.TimeConverter,
        *,
        reason: str = "No reason provided",
    ):
        """Temporary timeout a member from the server"""

        await wock.Member().hierarchy(ctx, member)

        if duration.seconds < 60:
            return await ctx.warn("The **duration** can't be shorter than **1 minute**")
        elif duration.seconds > 2332800:
            return await ctx.warn("The **duration** can't be longer than **27 days**")

        try:
            await member.timeout(duration.delta, reason=f"{ctx.author}: {reason}")
        except discord.HTTPException:
            return await ctx.warn(f"Couldn't timeout **{member}**")

        await self.invoke_message(ctx, ctx.approve, f"Timed out **{member}** for **{duration}**", user=member, duration=duration, reason=reason)
        await self.moderation_entry(ctx, member, "timeout", reason)

    @commands.command(
        name="untimeout",
        usage="(member) <reason>",
        example="rx#1337 forgiven",
        aliases=["untmout", "untmo", "unto", "uto"],
    )
    @commands.has_permissions(manage_messages=True)
    async def untimeout(
        self,
        ctx: wock.Context,
        member: wock.Member,
        *,
        reason: str = "No reason provided",
    ):
        """Lift the timeout from a member"""

        await wock.Member().hierarchy(ctx, member)

        if not member.timed_out_until:
            return await ctx.warn(f"**{member}** isn't **timed out**")

        try:
            await member.timeout(None, reason=f"{ctx.author}: {reason}")
        except discord.HTTPException:
            return await ctx.warn(f"Couldn't remove the timeout from **{member}**")

        await self.invoke_message(ctx, ctx.approve, f"Lifted timeout for **{member}**", user=member, reason=reason)
        await self.moderation_entry(ctx, member, "timeout lifted", reason)

    @commands.command(
        name="ban",
        usage="(user) <delete history> <reason>",
        example="rx#1337 7 flooding chat",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Silently ban the user",
                "aliases": ["s"],
            }
        },
        aliases=["b"],
    )
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: wock.Context,
        user: wock.Member | wock.User,
        days: Optional[Literal[0, 1, 7]] = 0,
        *,
        reason: str = "No reason provided",
    ):
        """Ban a user from the server"""

        await wock.Member().hierarchy(ctx, user)

        if isinstance(user, discord.Member) and user.premium_since:
            await ctx.prompt(f"Are you sure you want to ban {user.mention}?\n> They're currently **boosting** the server")

        if isinstance(user, discord.Member) and not ctx.parameters.get("silent") and not user.bot:
            embed = discord.Embed(
                color=functions.config_color("main"),
                title="Banned",
                description=f"> You've been banned from {ctx.guild.name}",
            )
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

            embed.add_field(name="Moderator", value=ctx.author)
            embed.add_field(name="Reason", value=reason)
            embed.set_thumbnail(url=ctx.guild.icon)

            with contextlib.suppress(discord.HTTPException):
                await user.send(embed=embed)

        try:
            await ctx.guild.ban(user, reason=f"{ctx.author}: {reason}", delete_message_days=days)
        except discord.Forbidden:
            await ctx.warn(f"I don't have **permissions** to ban {user.mention}")
        else:
            await self.invoke_message(ctx, ctx.check, user=user, reason=reason)
            await self.moderation_entry(ctx, user, "ban", reason)

    @commands.command(
        name="kick",
        usage="(member) <reason>",
        example="rx#1337 trolling",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Silently kick the member",
                "aliases": ["s"],
            }
        },
        aliases=["boot", "k"],
    )
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        ctx: wock.Context,
        member: discord.Member,
        *,
        reason: str = "No reason provided",
    ):
        """Kick a member from the server"""

        await wock.Member().hierarchy(ctx, member)

        if member.premium_since:
            await ctx.prompt(f"Are you sure you want to kick {member.mention}?\n> They're currently **boosting** the server")

        if not ctx.parameters.get("silent") and not member.bot:
            embed = discord.Embed(
                color=functions.config_color("main"),
                title="Kicked",
                description=f"> You've been kicked from {ctx.guild.name}",
            )
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

            embed.add_field(name="Moderator", value=ctx.author)
            embed.add_field(name="Reason", value=reason)
            embed.set_thumbnail(url=ctx.guild.icon)

            try:
                await member.send(embed=embed)
            except:
                pass

        try:
            await ctx.guild.kick(member, reason=f"{ctx.author}: {reason}")
        except discord.Forbidden:
            await ctx.warn(f"I don't have **permissions** to kick {member.mention}")
        else:
            await self.invoke_message(ctx, ctx.check, user=member, reason=reason)
            await self.moderation_entry(ctx, member, "kick", reason)

    @commands.command(
        name="unban",
        usage="(user) <reason>",
        example="rx#1337 forgiven",
    )
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        ctx: wock.Context,
        user: discord.User,
        *,
        reason: str = "No reason provided",
    ):
        """Unban a user from the server"""

        try:
            await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
        except discord.NotFound:
            await ctx.warn(f"Unable to find a ban for **{user}**")
        except discord.Forbidden:
            await ctx.warn(f"I don't have **permissions** to unban **{user}**")
        else:
            await self.invoke_message(ctx, ctx.check, user=user, reason=reason)
            await self.moderation_entry(ctx, user, "unban", reason)

    @commands.group(
        name="role",
        usage="(member) (role)",
        example="rx#1337 @Administrator",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_roles=True)
    async def role(
        self,
        ctx: wock.Context,
        member: wock.Member,
        *,
        roles: wock.Roles,
    ):
        """Add or remove a role from a member"""

        await wock.Member().hierarchy(ctx, member, author=True)
        await wock.Roles().manageable(ctx, roles)
        await wock.Roles().dangerous(ctx, roles)

        _roles_add, _roles_remove, _result = list(), list(), list()
        for role in roles:
            if role not in member.roles:
                _roles_add.append(role)
            else:
                _roles_remove.append(role)

        if _roles_add:
            try:
                await member.add_roles(*_roles_add, reason=f"{ctx.author}: Role added", atomic=False)
            except discord.Forbidden:
                return await ctx.warn(f"I don't have **permissions** to add {', '.join([role.mention for role in _roles_add])} to {member.mention}")
            else:
                _result.extend(f"**+{role}**" for role in _roles_add)
        if _roles_remove:
            try:
                await member.remove_roles(*_roles_remove, reason=f"{ctx.author}: Role removed", atomic=False)
            except discord.Forbidden:
                await ctx.warn(f"I don't have **permissions** to remove {', '.join([role.mention for role in _roles_remove])} from {member.mention}")
            else:
                _result.extend(f"**-{role}**" for role in _roles_remove)

        if _result:
            if len(_result) > 1:
                await self.invoke_message(
                    ctx,
                    ctx.approve,
                    f"Updated roles for {member.mention}: {' '.join(_result)}",
                    command="role multiple",
                    user=member,
                    roles=_result,
                )
            elif _roles_add:
                await self.invoke_message(
                    ctx,
                    ctx.approve,
                    f"Added {_roles_add[0].mention} to {member.mention}",
                    command="role add",
                    user=member,
                    role=_roles_add[0],
                )
            else:
                await self.invoke_message(
                    ctx,
                    ctx.approve,
                    f"Removed {_roles_remove[0].mention} from {member.mention}",
                    command="role remove",
                    user=member,
                    role=_roles_remove[0],
                )
        else:
            await ctx.warn(f"{member.mention} already has all of those roles")

    @role.command(
        name="add",
        usage="(member) (role)",
        example="rx#1337 @Administrator",
        aliases=["grant"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_add(
        self,
        ctx: wock.Context,
        member: wock.Member,
        *,
        role: wock.Role,
    ):
        """Add a role to a member"""

        await wock.Member().hierarchy(ctx, member, author=True)
        await wock.Role().manageable(ctx, role)
        await wock.Role().dangerous(ctx, role)

        if role not in member.roles:
            try:
                await member.add_roles(role, reason=f"{ctx.author}: Role added")
            except discord.Forbidden:
                await ctx.warn(f"I don't have **permissions** to add {role.mention} to {member.mention}")
            else:
                await self.invoke_message(
                    ctx,
                    ctx.approve,
                    f"Added {role.mention} to {member.mention}",
                    user=member,
                    role=role,
                )
        else:
            await ctx.warn(f"{member.mention} already has {role.mention}")

    @role.command(
        name="remove",
        usage="(member) (role)",
        example="rx#1337 @Administrator",
        aliases=["revoke"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_remove(
        self,
        ctx: wock.Context,
        member: wock.Member,
        *,
        role: wock.Role,
    ):
        """Remove a role from a member"""

        await wock.Member().hierarchy(ctx, member, author=True)
        await wock.Role().manageable(ctx, role)
        await wock.Role().dangerous(ctx, role)

        if role in member.roles:
            try:
                await member.remove_roles(role, reason=f"{ctx.author}: Role removed")
            except discord.Forbidden:
                await ctx.warn(f"I don't have **permissions** to remove {role.mention} from {member.mention}")
            else:
                await self.invoke_message(
                    ctx,
                    ctx.approve,
                    f"Removed {role.mention} from {member.mention}",
                    user=member,
                    role=role,
                )
        else:
            await ctx.warn(f"{member.mention} doesn't have {role.mention}")

    @role.command(
        name="multiple",
        usage="(member) (roles)",
        example="rx#1337 @Administrator @Moderator",
        aliases=["multi"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_multiple(
        self,
        ctx: wock.Context,
        member: wock.Member,
        *,
        roles: wock.Roles,
    ):
        """Add or remove multiple roles from a member"""

        await ctx.command.parent.command(ctx, member=member, roles=roles)

    @role.command(
        name="restore",
        usage="(member)",
        example="rx#1337",
    )
    @commands.has_permissions(manage_roles=True)
    async def role_restore(
        self,
        ctx: wock.Context,
        *,
        member: wock.Member,
    ):
        """Restore a member's roles"""

        await wock.Member().hierarchy(ctx, member, author=False)

        _bucket = functions.hash(f"{ctx.guild.id}-{member.id}")
        bucket = await self.bot.redis.get(f"roles:{_bucket}") or []
        roles = list(
            filter(
                lambda role: role.is_assignable() and role not in member.roles,
                [ctx.guild.get_role(role) for role in bucket if member.guild.get_role(role)],
            )
        )
        for role in roles:
            await wock.Role().manageable(ctx, role)

        if not roles:
            return await ctx.warn(f"There are no roles to **restore** for {member.mention}")

        try:
            await member.add_roles(*roles, reason=f"{ctx.author}: Roles restored", atomic=False)
        except discord.Forbidden:
            await ctx.warn(f"I don't have **permissions** to restore {member.mention}'s roles")
        else:
            await self.invoke_message(
                ctx,
                ctx.approve,
                f"Restored {member.mention}'s roles",
                user=member,
                roles=list(role.mention for role in roles),
            )

    @role.command(
        name="create",
        usage="(name)",
        example="Member",
        aliases=["new"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_create(self, ctx: wock.Context, *, name: str):
        """Create a role"""

        role = await ctx.guild.create_role(name=name, reason=f"{ctx.author}: Role created")
        await self.invoke_message(ctx, ctx.approve, f"Created {role.mention}", role=role)

    @role.command(
        name="delete",
        usage="(role)",
        example="@Member",
        aliases=["del"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_delete(self, ctx: wock.Context, *, role: wock.Role):
        """Delete a role"""

        await wock.Role().manageable(ctx, role)

        await role.delete(reason=f"{ctx.author}: Role deleted")
        await self.invoke_message(ctx, ctx.approve, f"Deleted **{role.name}**", role=role)

    @role.command(
        name="color",
        usage="(role) (color)",
        example="@Member #ff0000",
        aliases=["colour"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_color(self, ctx: wock.Context, role: wock.Role, *, color: wock.Color):
        """Change the color of a role"""

        await wock.Role().manageable(ctx, role, booster=True)

        await role.edit(color=color, reason=f"{ctx.author}: Role color changed")
        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Changed the color of {role.mention} to `{color}`",
            role=role,
            color=color,
        )

    @role.command(
        name="name",
        usage="(role) (name)",
        example="@Member Guest",
        aliases=["rename"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_name(self, ctx: wock.Context, role: wock.Role, *, name: str):
        """Change the name of a role"""

        await wock.Role().manageable(ctx, role, booster=True)

        await role.edit(name=name, reason=f"{ctx.author}: Role name changed")
        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Changed the name of {role.mention} to `{name}`",
            role=role,
            name=name,
        )

    @role.command(
        name="icon",
        usage="(role) (icon)",
        example="@Member 🦅",
        aliases=["emoji"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_icon(
        self,
        ctx: wock.Context,
        role: wock.Role,
        *,
        icon: Literal["remove", "reset", "off"] | wock.EmojiFinder | wock.ImageFinder = None,
    ):
        """Change the icon of a role"""

        await wock.Role().manageable(ctx, role, booster=True)

        if "ROLE_ICONS" not in ctx.guild.features:
            return await ctx.warn("This server doesn't have enough **boosts** to use **role icons**")
        if not icon:
            icon = await wock.ImageFinder.search(ctx)
        elif isinstance(icon, str) and icon in ("remove", "reset", "off"):
            icon = None

        _icon = None
        if type(icon) in (wock.Emoji, str):
            response = await ctx.bot.session.get(icon if not isinstance(icon, wock.Emoji) else icon.url)
            _icon = await response.read()
        else:
            if not role.display_icon:
                return await ctx.warn(f"**{role.name}** doesn't have an icon")

        await role.edit(display_icon=_icon, reason=f"{ctx.author}: Role icon changed")
        if icon:
            await ctx.approve(f"Changed the icon of {role.mention} to {f'{icon}' if isinstance(icon, wock.Emoji) else f'[**image**]({icon})'}")
        else:
            await ctx.approve(f"Removed the icon of {role.mention}")

    @role.command(
        name="hoist",
        usage="(role)",
        example="@Member",
        aliases=["display"],
    )
    @commands.has_permissions(manage_roles=True)
    async def role_hoist(self, ctx: wock.Context, *, role: wock.Role):
        """Toggle if a role is hoisted"""

        await wock.Role().manageable(ctx, role, booster=True)

        await role.edit(hoist=not role.hoist, reason=f"{ctx.author}: Role hoist toggled")
        await self.invoke_message(
            ctx,
            ctx.approve,
            f"{'Now hoisting' if role.hoist else 'No longer hoisting'} {role.mention}",
            role=role,
            hoist=role.hoist,
        )

    @role.command(
        name="mentionable",
        usage="(role)",
        example="@Member",
        aliases=["mention"],
    )
    @commands.has_permissions(manage_roles=True, mention_everyone=True)
    async def role_mentionable(self, ctx: wock.Context, *, role: wock.Role):
        """Toggle if a role is mentionable"""

        await wock.Role().manageable(ctx, role, booster=True)

        await role.edit(
            mentionable=not role.mentionable,
            reason=f"{ctx.author}: Role mentionable toggled",
        )
        await self.invoke_message(
            ctx,
            ctx.approve,
            f"{'Now allowing' if role.mentionable else 'No longer allowing'} {role.mention} to be mentioned",
            role=role,
            mentionable=role.mentionable,
        )

    @commands.group(
        name="emoji",
        usage="(subcommand) <args>",
        example="🔥",
        invoke_without_command=True,
    )
    async def emoji(self, ctx: wock.Context, *, emoji: wock.EmojiFinder):
        """Enlarge an emoji"""

        response = await self.bot.session.get(emoji.url)
        image = await response.read()
        image = io.BytesIO(image)

        if emoji.id:
            if emoji.animated:
                return await ctx.warn(f"Fuck you lol, you can't enlarge animated emojis")

            _image = Image.open(image)
            _image = _image.resize((_image.width * 5, _image.height * 5), Image.LANCZOS)
            image = io.BytesIO()
            _image.save(image, format="PNG")
            image.seek(0)

        await ctx.send(file=discord.File(image, filename="emoji.png"))

    @emoji.command(
        name="add",
        usage="(emoji or url) <name>",
        example="cdn.drapp/emojis/473.png daddy",
        aliases=["create", "copy"],
    )
    @commands.has_permissions(manage_emojis=True)
    async def emoji_add(
        self,
        ctx: wock.Context,
        emoji: Optional[discord.Emoji | discord.PartialEmoji | wock.ImageFinder],
        *,
        name: str = None,
    ):
        """Add an emoji to the server"""

        if not emoji:
            try:
                emoji = await wock.ImageFinder.search(ctx, history=False)
            except:
                return await ctx.send_help()

        if isinstance(emoji, discord.Emoji):
            if emoji.guild_id == ctx.guild.id:
                return await ctx.warn("That **emoji** is already in this server")
        if type(emoji) in (discord.Emoji, discord.PartialEmoji):
            name = name or emoji.name

        if not name:
            return await ctx.warn("Please **provide** a name for the emoji")

        if len(name) < 2:
            return await ctx.warn("The emoji name must be **2 characters** or longer")
        name = name[:32].replace(" ", "_")

        response = await self.bot.session.get(emoji if isinstance(emoji, str) else emoji.url)
        image = await response.read()

        try:
            emoji = await ctx.guild.create_custom_emoji(name=name, image=image, reason=f"{ctx.author}: Emoji added")
        except discord.RateLimited as error:
            return await ctx.warn(f"Please try again in **{error.retry_after:.2f} seconds**")
        except discord.HTTPException:
            if len(ctx.guild.emojis) == ctx.guild.emoji_limit:
                return await ctx.warn(f"The maximum amount of **emojis** has been reached (`{ctx.guild.emoji_limit}`)")
            else:
                return await ctx.warn(f"Failed to add [**{name}**]({response.url}) to the server")

        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Added [**{emoji.name}**]({emoji.url}) to the server",
            emoji=emoji,
        )

    @emoji.command(
        name="addmany",
        usage="(emojis)",
        example=":uhh: :erm:",
        aliases=["am"],
    )
    @commands.has_permissions(manage_emojis=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def emoji_add_many(self, ctx: wock.Context, *, emojis: str):
        """Bulk add emojis to the server"""

        emojis = list(
            set(
                [
                    wock.Emoji(
                        match.group("name"),
                        "https://cdn.discordapp.com/emojis/" + match.group("id") + (".gif" if match.group("animated") else ".png"),
                        id=int(match.group("id")),
                        animated=bool(match.group("animated")),
                    )
                    for match in re.finditer(regex.DISCORD_EMOJI, emojis)
                    if int(match.group("id")) not in (emoji.id for emoji in ctx.guild.emojis)
                ]
            )
        )
        if not emojis:
            return await ctx.send_help()

        emojis_added = list()
        async with ctx.typing():
            for emoji in emojis:
                image = await emoji.read()
                try:
                    emoji = await ctx.guild.create_custom_emoji(
                        name=emoji.name,
                        image=image,
                        reason=f"{ctx.author}: Emoji added (bulk)",
                    )
                except discord.RateLimited as error:
                    await ctx.warn(
                        f"Rate limited for **{error.retry_after:.2f} seconds**" + (f", stopping at {emojis_added[0]}" if emojis_added else "")
                    )
                    break
                except discord.HTTPException:
                    await ctx.warn(f"Failed to add [**{emoji.name}**]({emoji.url}) to the server")
                    break
                else:
                    emojis_added.append(emoji)

        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Added **{functions.plural(len(emojis_added)):emoji}** to the server",
            emojis=", ".join(str(emoji) for emoji in emojis_added),
        )

    @emoji.group(
        name="remove",
        usage="(emoji)",
        example=":uhh:",
        aliases=["delete", "del", "rm"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_emojis=True)
    async def emoji_remove(self, ctx: wock.Context, *, emoji: discord.Emoji):
        """Remove an emoji from the server"""

        if emoji.guild_id != ctx.guild.id:
            return await ctx.warn("That **emoji** isn't in this server")

        await emoji.delete(reason=f"{ctx.author}: Emoji deleted")
        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Removed [**{emoji.name}**]({emoji.url}) from the server",
            emoji=emoji,
        )

    @emoji_remove.command(
        name="duplicates",
        aliases=["dupes"],
    )
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_permissions(manage_emojis=True)
    async def emoji_remove_duplicates(self, ctx: wock.Context):
        """Sort and remove duplicate emojis"""

        if not ctx.guild.emojis:
            return await ctx.warn("There are no **emojis** in this server")

        async with ctx.typing():
            emoji_hashes = dict()
            for emoji in ctx.guild.emojis:
                image = await emoji.read()
                emoji_hashes.update({emoji: await functions.image_hash(image)})

            duplicates = {}
            for emoji, hash in emoji_hashes.items():
                if not list(emoji_hashes.values()).count(hash) > 1:
                    continue

                if hash in duplicates:
                    duplicates[hash].append(emoji)
                else:
                    duplicates[hash] = [emoji]

        if not duplicates:
            return await ctx.warn("There are no **duplicate emojis** in this server")

        await views.RemoveDuplicates(ctx, duplicates).start()

    @emoji.command(
        name="rename",
        usage="(emoji) (name)",
        example=":uhh: erm..",
        aliases=["name"],
    )
    @commands.has_permissions(manage_emojis=True)
    async def emoji_rename(self, ctx: wock.Context, emoji: discord.Emoji, *, name: str):
        """Rename an emoji in the server"""

        if emoji.guild_id != ctx.guild.id:
            return await ctx.warn("That **emoji** isn't in this server")

        name = name.replace(" ", "_")[:32]
        _emoji = emoji
        await _emoji.edit(name=name, reason=f"{ctx.author}: Emoji renamed")
        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Renamed [**{emoji.name}**]({emoji.url}) to **{name}**",
            emoji=emoji,
            name=name,
        )

    @emoji.command(
        name="list",
        aliases=["all"],
    )
    async def emoji_list(self, ctx: wock.Context):
        """View all emojis in the server"""

        await self.bot.get_command("emojis")(ctx)

    # @emoji.command(
    #     name="metrics",
    #     aliases=["stats"],
    # )
    # @commands.cooldown(1, 30, commands.BucketType.member)
    # async def emoji_metrics(self, ctx: wock.Context):
    #     """View server emoji metrics"""

    #     record = await self.bot.db.fetchrow(
    #         "SELECT COALESCE(SUM(uses), 0) AS uses, COUNT(*) AS emojis, MIN(timestamp) AS tracking_since FROM metrics.emojis WHERE emoji_id = ANY($1::BIGINT[])"
    #         " GROUP BY emoji_id",
    #         [emoji.id for emoji in ctx.guild.emojis],
    #     )
    #     if not record:
    #         return await ctx.warn(f"No **emojis** have been tracked yet!")

    #     data = await self.bot.db.fetch(
    #         "SELECT emoji_id, uses FROM metrics.emojis WHERE emoji_id = ANY($1::BIGINT[]) ORDER BY uses DESC",
    #         [emoji.id for emoji in ctx.guild.emojis],
    #     )

    #     per_day = functions.per_day(record.get("tracking_since"), record.get("uses"))

    #     await ctx.paginate(
    #         discord.Embed(
    #             title=f"Emoji Metrics for {ctx.guild}",
    #             description=list(
    #                 f"[{self.bot.get_emoji(row['emoji_id']) or '❔'}](https://cdn.discordapp.com/emojis/{row['emoji_id']}.png) -"
    #                 f" {functions.plural(row.get('uses')):use} ({functions.per_day(record.get('tracking_since'), row['uses']):.2f} per day)"
    #                 for row in data
    #             ),
    #         ).set_footer(
    #             text=f" {functions.plural(record.get('emojis')):emoji} used {functions.plural(record.get('uses')):time} ({per_day:.2f} per day)"
    #         ),
    #         footer_override=False,
    #     )

    @commands.group(
        name="sticker",
        usage="(subcommand) <args>",
        example="add dscord.com/chnls/999/.. mommy",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_emojis=True)
    async def sticker(self, ctx: wock.Context):
        """Manage stickers in the server"""

        await ctx.send_help()

    @sticker.command(
        name="add",
        usage="(image or url) <name>",
        example="dscord.com/chnls/999/.. mommy",
        aliases=["create", "copy"],
    )
    @commands.has_permissions(manage_emojis=True)
    async def sticker_add(
        self,
        ctx: wock.Context,
        image: Optional[wock.StickerFinder | wock.ImageFinderStrict],
        *,
        name: str = None,
    ):
        """Add a sticker to the server"""

        if not image:
            try:
                image = await wock.StickerFinder.search(ctx)
            except:
                try:
                    image = await wock.ImageFinder.search(ctx, history=False)
                except:
                    return await ctx.send_help()

        if isinstance(image, discord.GuildSticker):
            if image.guild_id == ctx.guild.id:
                return await ctx.warn("That **sticker** is already in this server")
            name = name or image.name
            image = image.url
        # elif isinstance(image, (discord.Emoji, discord.PartialEmoji)):
        #     name = name or image.name
        #     image = image.url

        if not name:
            return await ctx.warn("Please provide a **name** for the sticker")
        name = name[:30]

        if match := regex.DISCORD_ATTACHMENT.match(image):
            if match.group("mime") in ("png", "jpg", "jpeg", "webp"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        terminal = await asyncio.wait_for(
                            asyncio.create_subprocess_shell(f"cd {temp_dir} && ffmpeg -i {image} -vf scale=320:320 image.png -nostats -loglevel 0"),
                            timeout=25,
                        )
                        stdout, stderr = await terminal.communicate()
                    except asyncio.TimeoutError:
                        return await ctx.warn(f"Couldn't converter [**image**]({image}) to a **png** - Timeout")

                    if not os.path.exists(f"{temp_dir}/image.png"):
                        return await ctx.warn(f"Couldn't converter [**image**]({image}) to a **png**")

                    image = discord.File(
                        f"{temp_dir}/image.png",
                    )
            else:
                return await ctx.warn("Invalid **image** type")
        else:
            response = await self.bot.session.get(image)
            if response.status != 200:
                return await ctx.warn("Invalid **image** url")

            image = discord.File(
                io.BytesIO(await response.read()),
            )

        try:
            sticker = await ctx.guild.create_sticker(
                name=name,
                description=name,
                emoji="🥤",
                file=image,
                reason=f"{ctx.author}: Sticker added",
            )
        except discord.HTTPException:
            if len(ctx.guild.stickers) == ctx.guild.sticker_limit:
                return await ctx.warn(f"The maximum amount of **stickers** has been reached (`{ctx.guild.sticker_limit}`)")
            else:
                return await ctx.warn("Failed to add **sticker** to the server")

        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Added [**{sticker.name}**]({sticker.url}) to the server",
            sticker=sticker,
        )

    @sticker.command(
        name="remove",
        usage="(sticker)",
        example="mommy",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_emojis=True)
    async def sticker_remove(
        self,
        ctx: wock.Context,
        *,
        sticker: wock.StickerFinder = None,
    ):
        """Remove a sticker from the server"""

        if not sticker:
            try:
                sticker = await wock.StickerFinder.search(ctx)
            except:
                return await ctx.send_help()

        if sticker.guild_id != ctx.guild.id:
            return await ctx.warn("That **sticker** isn't in this server")

        await sticker.delete(reason=f"{ctx.author}: Sticker deleted")
        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Removed [**{sticker.name}**]({sticker.url}) from the server",
            sticker=sticker,
        )

    @sticker.command(
        name="rename",
        usage="(sticker) (name)",
        example="mommy daddy",
        aliases=["name"],
    )
    @commands.has_permissions(manage_emojis=True)
    async def sticker_rename(
        self,
        ctx: wock.Context,
        sticker: Optional[wock.StickerFinder],
        *,
        name: str,
    ):
        """Rename a sticker in the server"""

        if not sticker:
            try:
                sticker = await wock.StickerFinder.search(ctx)
            except:
                return await ctx.send_help()

        if sticker.guild_id != ctx.guild.id:
            return await ctx.warn("That **sticker** isn't in this server")

        name = name[:30]
        _sticker = sticker
        await _sticker.edit(name=name, reason=f"{ctx.author}: Sticker renamed")
        await self.invoke_message(
            ctx,
            ctx.approve,
            f"Renamed [**{sticker.name}**]({sticker.url}) to **{name}**",
            sticker=sticker,
            name=name,
        )

    @sticker.command(
        name="list",
        aliases=["all"],
    )
    async def sticker_list(self, ctx: wock.Context):
        """View all stickers in the server"""

        await self.bot.get_command("stickers")(ctx)

    @commands.command(
        name="cleanup",
        usage="<amount>",
        example="15",
        aliases=["mud", "bc"],
    )
    @commands.has_permissions(manage_messages=True)
    async def cleanup(
        self,
        ctx: wock.Context,
        amount: int = 50,
    ):
        """Clean up messages from wock"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.content and message.content.startswith(ctx.prefix):
                return True

            return message.author == self.bot.user or message.webhook_id is not None

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Cleanup",
        )

    @commands.group(
        name="purge",
        usage="<user> (amount)",
        example="rx#1337 15",
        aliases=["clear", "prune", "c"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(
        self,
        ctx: wock.Context,
        user: Optional[wock.Member | wock.User] = None,
        amount: int = None,
    ):
        """Purge a specified amount of messages"""

        if user and not amount:
            if user.name.isdigit():
                amount = int(user.name)
                user = None
            else:
                return await ctx.send_help()

        if not amount:
            return await ctx.send_help()
        else:
            amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if user:
                return message.author.id == user.id
            else:
                return True

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge",
        )

    @purge.command(
        name="after",
        usage="(message)",
        example="dscord.com/chnls/999/..",
        aliases=["upto", "to"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_after(
        self,
        ctx: wock.Context,
        message: discord.Message,
    ):
        """Purge messages after a specified message"""

        if message.channel != ctx.channel:
            return await ctx.warn("That **message** isn't in this channel")

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return True

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=300,
            check=check,
            after=message,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge after",
        )

    @purge.command(
        name="between",
        usage="(start message) (end message)",
        example="dscord.com/chnls/999/.. ../..",
        aliases=["inside", "btw", "bt"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_between(
        self,
        ctx: wock.Context,
        start_message: discord.Message,
        end_message: discord.Message,
    ):
        """Purge messages between two specified messages"""

        if start_message.channel != ctx.channel:
            return await ctx.warn("That **start message** isn't in this channel")
        if end_message.channel != ctx.channel:
            return await ctx.warn("That **end message** isn't in this channel")

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return True

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=300,
            check=check,
            after=start_message,
            before=end_message,
            bulk=True,
            reason=f"{ctx.author}: Purge between",
        )

    @purge.command(
        name="startswith",
        usage="(substring) <amount>",
        example="poop 15",
        aliases=["sw", "sws"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_startswith(
        self,
        ctx: wock.Context,
        substring: str,
        amount: int = 15,
    ):
        """Purge a specified amount of messages that start with a substring"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.content and message.content.lower().startswith(substring.lower()):
                return True

            return False

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge startswith",
        )

    @purge.command(
        name="endswith",
        usage="(substring) <amount>",
        example="poop 15",
        aliases=["ew", "ews"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_endswith(
        self,
        ctx: wock.Context,
        substring: str,
        amount: int = 15,
    ):
        """Purge a specified amount of messages that end with a substring"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.content and message.content.lower().endswith(substring.lower()):
                return True

            return False

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge endswith",
        )

    @purge.command(
        name="contains",
        usage="(substring) <amount>",
        example="poop 15",
        aliases=["contain", "c", "cs"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_contains(
        self,
        ctx: wock.Context,
        substring: str,
        amount: int = 15,
    ):
        """Purge a specified amount of messages that contain a substring"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.content and substring.lower() in message.content.lower():
                return True

            return False

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge contains",
        )

    @purge.command(
        name="emojis",
        usage="<amount>",
        example="15",
        aliases=["emoji", "emotes", "emote"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_emojis(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of emoji messages"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.emojis:
                return True

            return False

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge",
        )

    @purge.command(
        name="stickers",
        usage="<amount>",
        example="15",
        aliases=["sticker"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_stickers(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of sticker messages"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return message.stickers

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge",
        )

    @purge.command(
        name="humans",
        usage="<amount>",
        example="15",
        aliases=["human"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_humans(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of human messages"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return not message.author.bot

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge humans",
        )

    @purge.command(
        name="bots",
        usage="<amount>",
        example="15",
        aliases=["bot"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_bots(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of bot messages"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.content and message.content.startswith(
                (
                    ctx.prefix,
                    ",",
                    ".",
                    "!",
                    "?",
                    ";",
                    "?",
                    "$",
                    "-",
                )
            ):
                return True

            return message.author.bot

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge bots",
        )

    @purge.command(
        name="embeds",
        usage="<amount>",
        example="15",
        aliases=["embed"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_embeds(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of embeds"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return message.embeds

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge embeds",
        )

    @purge.command(
        name="files",
        usage="<amount>",
        example="15",
        aliases=["file", "attachments", "attachment"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_files(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of files"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return message.attachments

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge files",
        )

    @purge.command(
        name="images",
        usage="<amount>",
        example="15",
        aliases=["image", "imgs", "img", "pics", "pic"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_images(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of images"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.attachments:
                for attachment in message.attachments:
                    if str(attachment.content_type) in (
                        "image/png",
                        "image/jpeg",
                        "image/gif",
                        "image/webp",
                    ):
                        return True

            return False

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge images",
        )

    @purge.command(
        name="links",
        usage="<amount>",
        example="15",
        aliases=["link"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_links(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of links"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.content:
                if "http" in message.content or regex.DISCORD_INVITE.match(message.content):
                    return True

            return False

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge links",
        )

    @purge.command(
        name="invites",
        usage="<amount>",
        example="15",
        aliases=["invite"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_invites(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of invites"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            if message.content:
                if regex.DISCORD_INVITE.match(message.content):
                    return True

            return False

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge invites",
        )

    @purge.command(
        name="mentions",
        usage="<amount>",
        example="15",
        aliases=["mention", "pings", "ping"],
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_mentions(self, ctx: wock.Context, amount: int = 15):
        """Purge a specified amount of mentions"""

        amount = min(amount, 2000)

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return message.mentions

        with contextlib.suppress(discord.HTTPException):
            await ctx.message.delete()

        await ctx.channel.purge(
            limit=amount,
            check=check,
            before=ctx.message,
            bulk=True,
            reason=f"{ctx.author}: Purge mentions",
        )

    @commands.command(
        name="moveall",
        usage="(voice channel)",
        example="#voice",
        aliases=["mvall"],
    )
    @commands.has_permissions(manage_channels=True)
    @commands.max_concurrency(1, commands.BucketType.member)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def move(
        self,
        ctx: wock.Context,
        *,
        channel: discord.VoiceChannel,
    ):
        """Move all members to another voice channel"""

        if not ctx.author.voice:
            return await ctx.warn("You're not **connected** to a voice channel")
        elif not channel.permissions_for(ctx.author).connect:
            return await ctx.warn("You don't have **permission** to connect to that channel")
        elif ctx.author.voice.channel == channel:
            return await ctx.warn("You're already **connected** to that channel")

        tasks = list()
        for member in ctx.author.voice.channel.members:
            tasks.append(member.move_to(channel))

        async with ctx.typing():
            moved = await asyncio.gather(*tasks)
            await ctx.approve(f"Moved {functions.plural(moved, bold=True):member} to {channel.mention}")

    @commands.command(
        name="hide",
        usage="<channel> <reason>",
        example="#chat",
        aliases=["private", "priv"],
    )
    @commands.has_permissions(manage_channels=True)
    async def hide(
        self,
        ctx: wock.Context,
        channel: Optional[discord.TextChannel] = None,
        *,
        reason: str = "No reason provided",
    ):
        """Hide a channel from regular members"""

        channel = channel or ctx.channel

        if channel.overwrites_for(ctx.guild.default_role).read_messages is False:
            return await ctx.warn(f"The channel {channel.mention} is already hidden")

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.read_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"{ctx.author}: {reason}")

        await self.invoke_message(ctx, ctx.approve, f"Set channel {channel.mention} as hidden", channel=channel, reason=reason)
        await self.moderation_entry(ctx, channel, "hide", reason)

    @commands.command(
        name="reveal",
        usage="<channel> <reason>",
        example="#chat",
        aliases=["unhide", "public"],
    )
    @commands.has_permissions(manage_channels=True)
    async def unhide(
        self,
        ctx: wock.Context,
        channel: Optional[discord.TextChannel] = None,
        *,
        reason: str = "No reason provided",
    ):
        """Reveal a channel to regular members"""

        channel = channel or ctx.channel

        if channel.overwrites_for(ctx.guild.default_role).read_messages is True:
            return await ctx.warn(f"The channel {channel.mention} isn't hidden")

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.read_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"{ctx.author}: {reason}")

        await self.invoke_message(ctx, ctx.approve, f"Revealed channel {channel.mention}", channel=channel, reason=reason)
        await self.moderation_entry(ctx, channel, "reveal", reason)

    @commands.group(
        name="lockdown",
        usage="<channel> <reason>",
        example="#chat spamming",
        aliases=["lock"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown(
        self,
        ctx: wock.Context,
        channel: Optional[discord.TextChannel] = None,
        *,
        reason: str = "No reason provided",
    ):
        """Prevent regular members from typing"""

        channel = channel or ctx.channel

        if channel.overwrites_for(ctx.guild.default_role).send_messages is False:
            return await ctx.warn(f"The channel {channel.mention} is already locked")

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"{ctx.author}: {reason}")

        await self.invoke_message(ctx, ctx.approve, f"Locked channel {channel.mention}", channel=channel, reason=reason)
        await self.moderation_entry(ctx, channel, "lockdown", reason)

    @lockdown.command(
        name="all",
        usage="<reason>",
    )
    @commands.has_permissions(manage_channels=True)
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def lockdown_all(self, ctx: wock.Context, *, reason: str = "No reason provided"):
        """Prevent regular members from typing in all channels"""

        ignored_channels = await self.bot.db.fetch_config(ctx.guild.id, "lock_ignore") or []
        if not ignored_channels:
            await ctx.prompt(
                f"Are you sure you want to lock all channels?\n> You haven't set any ignored channels with `{ctx.prefix}lock ignore` yet"
            )

        async with ctx.typing():
            for channel in ctx.guild.text_channels:
                if channel.overwrites_for(ctx.guild.default_role).send_messages is False or channel.id in ignored_channels:
                    continue

                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"{ctx.author}: {reason} (lockdown all)")

            await self.invoke_message(ctx, ctx.approve, "Locked all channels", reason=reason)
            await self.moderation_entry(ctx, ctx.guild, "lockdown all", reason)

    @lockdown.group(
        name="ignore",
        usage="(subcommand) <args>",
        example="add #psa",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown_ignore(self, ctx: wock.Context):
        """Prevent channels from being altered"""

        await ctx.send_help()

    @lockdown_ignore.command(
        name="add",
        usage="(channel)",
        example="#psa",
        aliases=["create"],
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown_ignore_add(self, ctx: wock.Context, *, channel: discord.TextChannel):
        """Add a channel to the ignore list"""

        ignored_channels = await self.bot.db.fetch_config(ctx.guild.id, "lock_ignore") or []
        if channel.id in ignored_channels:
            return await ctx.warn(f"{channel.mention} is already ignored")

        ignored_channels.append(channel.id)
        await self.bot.db.update_config(ctx.guild.id, "lock_ignore", ignored_channels)

        await ctx.approve(f"Now ignoring {channel.mention}")

    @lockdown_ignore.command(
        name="remove",
        usage="(channel)",
        example="#psa",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown_ignore_remove(self, ctx: wock.Context, *, channel: discord.TextChannel):
        """Remove a channel from the ignore list"""

        ignored_channels = await self.bot.db.fetch_config(ctx.guild.id, "lock_ignore") or []
        if channel.id not in ignored_channels:
            return await ctx.warn(f"{channel.mention} isn't ignored")

        ignored_channels.remove(channel.id)
        await self.bot.db.update_config(ctx.guild.id, "lock_ignore", ignored_channels)

        await ctx.approve(f"No longer ignoring {channel.mention}")

    @lockdown_ignore.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown_ignore_list(self, ctx: wock.Context):
        """List all ignored channels"""

        channels = [
            ctx.guild.get_channel(channel_id).mention
            for channel_id in await self.bot.db.fetch_config(ctx.guild.id, "lock_ignore") or []
            if ctx.guild.get_channel(channel_id)
        ]
        if not channels:
            return await ctx.warn("No **ignored channels** have been set up")

        await ctx.paginate(
            discord.Embed(
                title="Ignored Channels",
                description=channels,
            )
        )

    @commands.group(
        name="unlockdown",
        usage="<channel> <reason>",
        example="#chat behave",
        aliases=["unlock"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_channels=True)
    async def unlockdown(
        self,
        ctx: wock.Context,
        channel: Optional[discord.TextChannel] = None,
        *,
        reason: str = "No reason provided",
    ):
        """Allow regular members to type"""

        channel = channel or ctx.channel

        if channel.overwrites_for(ctx.guild.default_role).send_messages is True:
            return await ctx.warn(f"The channel {channel.mention} isn't locked")

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"{ctx.author}: {reason}")

        await self.invoke_message(ctx, ctx.approve, f"Unlocked channel {channel.mention}", channel=channel, reason=reason)
        await self.moderation_entry(ctx, channel, "unlockdown", reason)

    @unlockdown.command(
        name="all",
        usage="<reason>",
        example="raid over",
    )
    @commands.has_permissions(manage_channels=True)
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def unlockdown_all(self, ctx: wock.Context, *, reason: str = "No reason provided"):
        """Allow regular members to type in all channels"""

        ignored_channels = await self.bot.db.fetch_config(ctx.guild.id, "lock_ignore") or []
        if not ignored_channels:
            await ctx.prompt(
                f"Are you sure you want to unlock all channels?\n> You haven't set any ignored channels with `{ctx.prefix}lock ignore` yet"
            )

        async with ctx.typing():
            for channel in ctx.guild.text_channels:
                if channel.overwrites_for(ctx.guild.default_role).send_messages is True or channel.id in ignored_channels:
                    continue

                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = True
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"{ctx.author}: {reason} (unlockdown all)")

            await self.invoke_message(ctx, ctx.approve, "Unlocked all channels", reason=reason)
            await self.moderation_entry(ctx, ctx.guild, "unlockdown all", reason)

    @commands.group(
        name="slowmode",
        usage="<channel> (delay time)",
        example="#chat 10s",
        aliases=["slowmo", "slow"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_channels=True)
    async def slowmode(
        self,
        ctx: wock.Context,
        channel: Optional[discord.TextChannel],
        *,
        delay: wock.TimeConverter,
    ):
        """Set the slowmode delay for a channel"""

        channel = channel or ctx.channel

        if channel.slowmode_delay == delay.seconds:
            return await ctx.warn(f"The slowmode for {channel.mention} is already set to **{delay}**")

        try:
            await channel.edit(slowmode_delay=delay.seconds)
        except discord.HTTPException:
            return await ctx.error(f"Coudn't set the slowmode for {channel.mention} to **{delay}**")

        if delay.seconds:
            await ctx.approve(f"Set the slowmode for {channel.mention} to **{delay}**")
        else:
            await ctx.approve(f"Disabled slowmode for {channel.mention}")

    @slowmode.command(
        name="disable",
        usage="<channel>",
        example="#chat",
        aliases=["off"],
    )
    @commands.has_permissions(manage_channels=True)
    async def slowmode_disable(self, ctx: wock.Context, channel: Optional[discord.TextChannel]):
        """Disable slowmode for a channel"""

        channel = channel or ctx.channel

        if not channel.slowmode_delay:
            return await ctx.warn(f"The slowmode for {channel.mention} is already **disabled**")

        await channel.edit(slowmode_delay=0)
        await ctx.approve(f"Disabled slowmode for {channel.mention}")

    @commands.command(
        name="nsfw",
        usage="<channel>",
        example="#chat",
        aliases=["naughty"],
    )
    @commands.has_permissions(manage_channels=True)
    async def nsfw(self, ctx: wock.Context, channel: discord.TextChannel = None):
        """Temporarily mark a channel as NSFW"""

        channel = channel or ctx.channel

        if channel.is_nsfw():
            return await ctx.warn(f"The channel {channel.mention} is already marked as **NSFW**")

        await channel.edit(nsfw=True)
        await ctx.approve(f"Temporarily marked {channel.mention} as **NSFW** for **60 seconds**")

        await asyncio.sleep(60)
        await channel.edit(nsfw=False)


async def setup(bot: wock.wockSuper):
    await bot.add_cog(moderation(bot))
