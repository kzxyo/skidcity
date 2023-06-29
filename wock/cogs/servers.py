import asyncio
import contextlib

from datetime import timedelta
from typing import Literal

import discord

from discord.ext import commands, tasks

from helpers import checks, functions, humanize, regex, wock


class servers(commands.Cog, name="Servers"):
    def __init__(self, bot):
        self.bot: wock.wockSuper = bot
        self.sticky_locks = {}
        self.counter_update.start()

    def cog_unload(self):
        self.counter_update.stop()

    @tasks.loop(minutes=10)
    async def counter_update(self):
        """Update all counter channels"""

        async for counter in self.bot.db.fetchiter("SELECT * FROM counter_channels"):
            if rl_until := counter.get("rate_limited"):
                if rl_until > discord.utils.utcnow():
                    continue
            if last_updated := counter.get("last_updated"):
                if (discord.utils.utcnow() - last_updated) < timedelta(minutes=10):
                    continue

            if channel := self.bot.get_channel(counter.get("channel_id")):
                if not channel.guild.me.guild_permissions.manage_channels:
                    await self.bot.db.execute("DELETE FROM counter_channels WHERE channel_id = $1", counter.get("channel_id"))

                new_name = regex.NUMBER.sub(
                    humanize.comma(len(channel.guild.members) if counter.get("option") == "members" else channel.guild.premium_subscription_count),
                    channel.name,
                )
                if not channel.name == new_name:
                    try:
                        await channel.edit(name=new_name)
                    except discord.RateLimited as error:
                        self.bot.logger.info(f"Rate limited for {error.retry_after} seconds on counter {channel.id}")
                        await self.bot.db.execute(
                            "UPDATE counter_channels SET rate_limited = $2 WHERE channel_id = $1",
                            counter.get("channel_id"),
                            (discord.utils.utcnow() + timedelta(seconds=error.retry_after)),
                        )
                    except:
                        await self.bot.db.execute("DELETE FROM counter_channels WHERE channel_id = $1", counter.get("channel_id"))
                    else:
                        await self.bot.db.execute(
                            "UPDATE counter_channels SET last_updated = $2 WHERE channel_id = $1", counter.get("channel_id"), discord.utils.utcnow()
                        )
            else:
                await self.bot.db.execute("DELETE FROM counter_channels WHERE channel_id = $1", counter.get("channel_id"))

    @counter_update.before_loop
    async def counter_update_before(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_member_remove")  # AUTOROLE REASSIGN (CACHE)
    async def role_caching(self, member: discord.Member):
        """Save the roles of the member which left the server"""

        if not member:
            return

        if roles := list(
            filter(
                lambda role: role.is_assignable(),
                member.roles,
            )
        ):
            reassign = await self.bot.db.fetch_config(member.guild.id, "reassign_roles")
            if reassign:
                bucket = functions.hash(f"{member.guild.id}:{member.id}")
                await self.bot.redis.set(f"roles:{bucket}", [role.id for role in roles], ex=60 * 60 * 2)

    @commands.Cog.listener("on_member_agree")  # AUTOROLE REASSIGN
    async def role_reassigning(self, member: discord.Member):
        """Reassign previous roles to a member which rejoin the server"""

        _bucket = functions.hash(f"{member.guild.id}:{member.id}")
        if bucket := await self.bot.redis.get(f"roles:{_bucket}"):
            roles = list(
                filter(
                    lambda role: role.is_assignable()
                    and not list(
                        filter(
                            lambda permission: getattr(role.permissions, permission),
                            wock.DANGEROUS_PERMISSIONS,
                        )
                    ),
                    [member.guild.get_role(role) for role in bucket if member.guild.get_role(role)],
                )
            )
            if roles:
                with contextlib.suppress(discord.HTTPException):
                    await member.add_roles(*roles, reason="Role Reassignment", atomic=False)

            await self.bot.redis.delete(f"roles:{_bucket}")

    @commands.Cog.listener("on_member_agree")  # AUTOROLE GRANT
    async def autorole_assigning(self, member: discord.Member):
        """Assign roles to a member which joins the server"""

        roles = [
            member.guild.get_role(row.get("role_id"))
            async for row in self.bot.db.fetchiter("SELECT role_id, discriminator, humans, bots FROM auto_roles WHERE guild_id = $1", member.guild.id)
            if member.guild.get_role(row.get("role_id"))
            and member.guild.get_role(row.get("role_id")).is_assignable()
            and (row.get("discriminator") is None or row.get("discriminator") == member.discriminator)
            and (row.get("humans") is None or member.bot is False)
            and (row.get("bots") is None or row.get("bots") == member.bot)
        ]
        if roles:
            with contextlib.suppress(discord.HTTPException):
                await member.add_roles(*roles, reason="Role Assignment", atomic=False)

    @commands.Cog.listener("on_member_agree")  # WELCOME MESSAGE
    async def welcome_message(self, member: discord.Member):
        """Send a welcome message for a member which joins the server"""

        async for row in self.bot.db.fetchiter(
            "SELECT channel_id, message, self_destruct FROM welcome_channels WHERE guild_id = $1",
            member.guild.id,
        ):
            channel = self.bot.get_channel(row.get("channel_id"))
            if channel:
                await functions.ensure_future(
                    wock.EmbedScript(row["message"]).send(
                        channel,
                        bot=self.bot,
                        guild=member.guild,
                        channel=channel,
                        user=member,
                        allowed_mentions=discord.AllowedMentions(everyone=True, users=True, roles=True, replied_user=False),
                        delete_after=row.get("self_destruct"),
                    )
                )

    @commands.Cog.listener("on_member_remove")  # GOODBYE MESSAGE
    async def goodbye_message(self, member: discord.Member):
        """Send a goodbye message for a member which leaves the server"""

        async for row in self.bot.db.fetchiter(
            "SELECT channel_id, message, self_destruct FROM goodbye_channels WHERE guild_id = $1",
            member.guild.id,
        ):
            channel = self.bot.get_channel(row.get("channel_id"))
            if channel:
                await functions.ensure_future(
                    wock.EmbedScript(row["message"]).send(
                        channel,
                        bot=self.bot,
                        guild=member.guild,
                        channel=channel,
                        user=member,
                        allowed_mentions=discord.AllowedMentions(everyone=True, users=True, roles=True, replied_user=False),
                        delete_after=row.get("self_destruct"),
                    )
                )

    @commands.Cog.listener("on_member_boost")  # BOOST MESSAGE
    async def boost_message(self, member: discord.Member):
        """Send a boost message for a member which boosts the server"""

        async for row in self.bot.db.fetchiter(
            "SELECT channel_id, message, self_destruct FROM boost_channels WHERE guild_id = $1",
            member.guild.id,
        ):
            channel = self.bot.get_channel(row.get("channel_id"))
            if channel:
                await functions.ensure_future(
                    wock.EmbedScript(row["message"]).send(
                        channel,
                        bot=self.bot,
                        guild=member.guild,
                        channel=channel,
                        user=member,
                        allowed_mentions=discord.AllowedMentions(everyone=True, users=True, roles=True, replied_user=False),
                        delete_after=row.get("self_destruct"),
                    )
                )

    @commands.Cog.listener("on_user_message")  # STICKY MESSAGE DISPATCHER
    async def sticky_message_dispatcher(self, ctx: wock.Context, message: discord.Message):
        """Dispatch the sticky message event while waiting for the activity scheduler"""

        data = await self.bot.db.fetchrow(
            "SELECT * FROM sticky_messages WHERE guild_id = $1 AND channel_id = $2", message.guild.id, message.channel.id
        )
        if not data:
            return

        if data["message_id"] == message.id:
            return

        key = functions.hash(f"{message.guild.id}:{message.channel.id}")
        if not self.sticky_locks.get(key):
            self.sticky_locks[key] = asyncio.Lock()
        bucket = self.sticky_locks.get(key)

        async with bucket:
            try:
                await self.bot.wait_for("message", check=lambda m: m.channel == message.channel, timeout=data.get("schedule") or 2)
            except asyncio.TimeoutError:
                pass
            else:
                return

            with contextlib.suppress(discord.HTTPException):
                await message.channel.get_partial_message(data["message_id"]).delete()

            message = await functions.ensure_future(
                wock.EmbedScript(data["message"]).send(
                    message.channel,
                    bot=self.bot,
                    guild=message.guild,
                    channel=message.channel,
                    user=message.author,
                )
            )
            await self.bot.db.execute(
                "UPDATE sticky_messages SET message_id = $3 WHERE guild_id = $1 AND channel_id = $2",
                message.guild.id,
                message.channel.id,
                message.id,
            )

    @commands.Cog.listener("on_raw_reaction_add")
    async def reactionrole_assigning(self, payload: discord.RawReactionActionEvent):
        """Assign roles to a member which reacts to a message"""

        guild = self.bot.get_guild(payload.guild_id)
        if guild and (member := guild.get_member(payload.user_id)) and not member.bot:
            role_id = await self.bot.db.fetchval(
                "SELECT role_id FROM reaction_roles WHERE message_id = $1 AND emoji = $2", payload.message_id, str(payload.emoji)
            )
            if role_id and (role := guild.get_role(role_id)) and role.is_assignable():
                with contextlib.suppress(discord.HTTPException):
                    await member.add_roles(role, reason="Reaction Role Assignment", atomic=False)

    @commands.Cog.listener("on_raw_reaction_remove")
    async def reactionrole_unassigning(self, payload: discord.RawReactionActionEvent):
        """Unassign roles from a member which removes a reaction from a message"""

        guild = self.bot.get_guild(payload.guild_id)
        if guild and (member := guild.get_member(payload.user_id)) and not member.bot:
            role_id = await self.bot.db.fetchval(
                "SELECT role_id FROM reaction_roles WHERE message_id = $1 AND emoji = $2 AND oneway IS NULL",
                payload.message_id,
                str(payload.emoji),
            )
            if role_id and (role := guild.get_role(role_id)) and role.is_assignable():
                with contextlib.suppress(discord.HTTPException):
                    await member.remove_roles(role, reason="Reaction Role Unassignment", atomic=False)

    @commands.Cog.listener("on_youtube_post")  # YOUTUBE POST NOTIFICATION
    async def youtube_notification(self, post: dict):
        """Send post notifications for a YouTube channel"""

        async for row in self.bot.db.fetchiter(
            "SELECT channel_id, message FROM youtube_channels WHERE youtube_id = $1",
            post["channel"].get("id"),
        ):
            channel = self.bot.get_channel(row.get("channel_id"))
            if channel:
                await functions.ensure_future(
                    (
                        channel.send(
                            content=f"**{post['channel'].get('name')}** just posted a new video!\n{post['url']}",
                            allowed_mentions=discord.AllowedMentions(
                                everyone=True,
                                users=True,
                                roles=True,
                                replied_user=False,
                            ),
                        )
                        if not row.get("message")
                        else wock.EmbedScript(row["message"]).send(
                            channel,
                            bot=self.bot,
                            guild=channel.guild,
                            channel=channel,
                            youtube=post,
                            allowed_mentions=discord.AllowedMentions(
                                everyone=True,
                                users=True,
                                roles=True,
                                replied_user=False,
                            ),
                        )
                    )
                )

    @commands.Cog.listener("on_user_message")  # RESPONSE TRIGGER
    async def response_trigger(self, ctx: wock.Context, message: discord.Message):
        """Respond to trigger words"""

        if not message.content:
            return

        async for row in self.bot.db.fetchiter(
            "SELECT * FROM auto_responses WHERE guild_id = $1",
            message.guild.id,
        ):
            if not row.get("trigger").lower() in message.content.lower():
                continue
            if not row.get("not_strict") and not row.get("trigger").lower() == message.content.lower():
                continue
            if not row.get("ignore_command_check") and ctx.command:
                continue
            bucket = self.bot.buckets.get("response_triggers").get_bucket(message)
            if bucket.update_rate_limit():
                return

            await functions.ensure_future(
                wock.EmbedScript(row["response"]).send(
                    message.channel,
                    bot=self.bot,
                    guild=message.guild,
                    channel=message.channel,
                    user=message.author,
                    allowed_mentions=discord.AllowedMentions(everyone=True, users=True, roles=True, replied_user=False),
                    delete_after=row.get("self_destruct"),
                    reference=(message if row.get("reply") else None),
                )
            )

            if not row.get("reply") and row.get("delete"):
                with contextlib.suppress(discord.HTTPException):
                    await message.delete()

    @commands.Cog.listener("on_user_message")
    async def reaction_trigger(self, ctx: wock.Context, message: discord.Message):
        """React to trigger words"""

        if not message.content or ctx.command:
            return

        bucket_update = False

        async for row in self.bot.db.fetchiter(
            "SELECT trigger, array_agg(emoji) AS emojis, strict FROM reaction_triggers WHERE guild_id = $1 GROUP BY trigger, strict",
            message.guild.id,
        ):
            if not row.get("trigger").lower() in message.content.lower():
                continue
            if row.get("strict") and not row.get("trigger").lower() == message.content.lower():
                continue

            bucket_update = True
            for emoji in row.get("emojis"):
                await functions.ensure_future(message.add_reaction(emoji))

        if bucket_update:
            bucket = self.bot.buckets.get("reaction_triggers").get_bucket(message)
            if bucket.update_rate_limit():
                return

    @commands.Cog.listener("on_thread_update")  # THREAD ARCHIVED
    async def thread_archived(self, before: discord.Thread, thread: discord.Thread):
        """Automatically reopen threads when they're archived"""

        if before.archived or not thread.archived or thread.locked:
            return

        watcher = await self.bot.db.fetchrow(
            "SELECT * FROM thread_watcher WHERE guild_id = $1 AND thread_id = $2",
            thread.guild.id,
            thread.id,
        )
        if not watcher:
            return

        with contextlib.suppress(discord.HTTPException):
            await thread.edit(
                archived=False,
                reason="Thread watcher",
            )

    @commands.group(
        name="prefix",
        usage="(subcommand) <args>",
        example="set ;",
        invoke_without_command=True,
    )
    async def prefix(self, ctx: wock.Context):
        """View the server prefix"""

        prefix = await self.bot.get_prefix(ctx.message, mention=False)
        await ctx.neutral(f"Prefix: `{prefix}`")

    @prefix.command(name="set", usage="(prefix)", example=";")
    @commands.has_permissions(manage_messages=True)
    async def prefix_set(self, ctx: wock.Context, *, prefix: str):
        """Set the server prefix"""

        await self.bot.db.update_config(ctx.guild.id, "prefix", prefix)
        await ctx.approve(f"Set the **prefix** to `{prefix}`")

    @commands.command(name="jaillog", usage="<channel>", example="#jail-log", aliases=["modlog"])
    @commands.has_permissions(manage_guild=True)
    async def jaillog(self, ctx: wock.Context, *, channel: discord.TextChannel | discord.Thread = None):
        """Set the moderation log channel"""

        if not channel:
            jail_log = await self.bot.db.fetch_config(ctx.guild.id, "jail_log")
            channel = self.bot.get_channel(jail_log)
            if not channel:
                await ctx.send_help()
            else:
                await ctx.neutral(f"The `jail-log` channel is bound to {channel.mention}")
        else:
            await self.bot.db.update_config(ctx.guild.id, "jail_log", channel.id)
            await ctx.react_check()

    @commands.command(
        name="resetcases",
        aliases=["resetcs"],
    )
    @commands.has_permissions(manage_guild=True)
    async def resetcases(self, ctx: wock.Context):
        """Reset the all moderation cases"""

        try:
            await self.bot.db.execute(
                "DELETE FROM cases WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("There aren't any **moderation cases** to reset")
        else:
            await ctx.approve("Reset all **moderation cases**")

    @commands.group(
        name="fakepermissions",
        usage="(subcommand) <args>",
        example="grant @Moderator manage_messages",
        aliases=["fakeperms", "fp"],
        invoke_without_command=True,
    )
    @commands.has_permissions(guild_owner=True)
    async def fakepermissions(self, ctx: wock.Context):
        """Set up fake permissions for roles"""

        await ctx.send_help()

    @fakepermissions.command(
        name="grant",
        usage="(role) (permission)",
        example="@Moderator manage_messages",
        aliases=["allow", "add"],
    )
    @commands.has_permissions(guild_owner=True)
    async def fakepermissions_grant(self, ctx: wock.Context, role: wock.Role, *, permission: str):
        """Grant a role a fake permission"""

        permission = permission.replace(" ", "_").lower()
        if not permission in dict(ctx.author.guild_permissions):
            return await ctx.warn(f"Permission `{permission}` doesn't exist")

        try:
            await self.bot.db.execute(
                "INSERT INTO fake_permissions (guild_id, role_id, permission) VALUES ($1, $2, $3)",
                ctx.guild.id,
                role.id,
                permission,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The role {role.mention} already has fake permission `{permission}`")
        else:
            await ctx.approve(f"Granted {role.mention} fake permission `{permission}`")

    @fakepermissions.command(
        name="revoke",
        usage="(role) (permission)",
        example="@Moderator manage_messages",
        aliases=["remove", "delete", "del", "rm"],
    )
    @commands.has_permissions(guild_owner=True)
    async def fakepermissions_revoke(self, ctx: wock.Context, role: wock.Role, *, permission: str):
        """Revoke a fake permission from a role"""

        permission = permission.replace(" ", "_").lower()
        if not permission in dict(ctx.author.guild_permissions):
            return await ctx.warn(f"Permission `{permission}` doesn't exist")

        try:
            await self.bot.db.execute(
                "DELETE FROM fake_permissions WHERE guild_id = $1 AND role_id = $2 AND permission = $3",
                ctx.guild.id,
                role.id,
                permission,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The role {role.mention} doesn't have fake permission `{permission}`")
        else:
            await ctx.approve(f"Revoked fake permission `{permission}` from {role.mention}")

    @fakepermissions.command(name="reset", aliases=["clear"])
    @commands.has_permissions(guild_owner=True)
    async def fakepermissions_reset(self, ctx: wock.Context):
        """Remove every fake permission from every role"""

        await ctx.prompt("Are you sure you want to remove all **fake permissions**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM fake_permissions WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("There aren't any **fake permissions** to remove")
        else:
            await ctx.approve("Removed all **fake permissions**")

    @fakepermissions.command(name="list", aliases=["show", "all"])
    @commands.has_permissions(guild_owner=True)
    async def fakepermissions_list(self, ctx: wock.Context):
        """View all roles with fake permissions"""

        roles = [
            f"{role.mention} - {', '.join([f'`{permission}`' for permission in permissions])}"
            async for row in self.bot.db.fetchiter(
                "SELECT role_id, array_agg(permission) AS permissions FROM fake_permissions WHERE guild_id = $1 GROUP BY role_id",
                ctx.guild.id,
            )
            if (role := ctx.guild.get_role(row["role_id"])) and (permissions := row["permissions"])
        ]
        if not roles:
            return await ctx.warn("There aren't any roles with **fake permissions**")

        await ctx.paginate(
            discord.Embed(
                title="Fake Permissions",
                description=roles,
            )
        )

    @commands.group(
        name="ignore",
        usage="(subcommand) <args>",
        example="add rx#1337",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def ignore(self, ctx: wock.Context):
        """Ignore commands from a member"""

        await ctx.send_help()

    @ignore.command(
        name="add",
        usage="(member or channel)",
        example="rx#1337",
        aliases=["create"],
    )
    @commands.has_permissions(manage_guild=True)
    async def ignore_add(self, ctx: wock.Context, *, target: wock.Member | discord.TextChannel):
        """Add a member to be ignored"""

        if isinstance(target, discord.Member):
            await wock.Member().hierarchy(ctx, target)
            if target.guild_permissions.administrator:
                return await ctx.warn(f"You can't ignore **administrators**")

        try:
            await self.bot.db.execute(
                "INSERT INTO commands.ignored VALUES ($1, $2)",
                ctx.guild.id,
                target.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The {'member' if isinstance(target, discord.Member) else 'channel'} {target.mention} is already being **ignored**")
        else:
            await ctx.approve(f"Now ignoring commands {'from' if isinstance(target, discord.Member) else 'in'} {target.mention}")

    @ignore.command(
        name="remove",
        usage="(member or channel)",
        example="rx#1337",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_guild=True)
    async def ignore_remove(self, ctx: wock.Context, *, target: wock.Member | discord.TextChannel):
        """Remove a member from being ignored"""

        try:
            await self.bot.db.execute(
                "DELETE FROM commands.ignored WHERE guild_id = $1 AND target_id = $2",
                ctx.guild.id,
                target.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The {'member' if isinstance(target, discord.Member) else 'channel'} {target.mention} is not being **ignored**")
        else:
            await ctx.approve(f"No longer ignoring commands {'from' if isinstance(target, discord.Member) else 'in'} {target.mention}")

    @ignore.command(name="reset", aliases=["clear"])
    @commands.has_permissions(manage_guild=True)
    async def ignore_reset(self, ctx: wock.Context):
        """Reset all ignored members"""

        await ctx.prompt("Are you sure you want to **reset** the ignore list?")

        try:
            await self.bot.db.execute(
                "DELETE FROM commands.ignored WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No members are being **ignored**")
        else:
            await ctx.approve("No longer **ignoring** any members")

    @ignore.command(name="list", aliases=["show", "all"])
    @commands.has_permissions(manage_guild=True)
    async def ignore_list(self, ctx: wock.Context):
        """View all ignored members"""

        ignored = [
            target.mention
            async for row in self.bot.db.fetchiter("SELECT target_id FROM commands.ignored WHERE guild_id = $1", ctx.guild.id)
            if (target := ctx.guild.get_member(row.get("target_id")) or ctx.guild.get_channel(row.get("target_id")))
        ]
        if not ignored:
            return await ctx.warn("No members are being **ignored**")

        await ctx.paginate(
            discord.Embed(
                title="Ignored",
                description=ignored,
            )
        )

    @commands.group(
        name="command",
        usage="(subcommand) <args>",
        example="disable #spam blunt",
        aliases=["cmd"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def command(self, ctx: wock.Context):
        """Manage command usability"""

        await ctx.send_help()

    @command.group(
        name="enable",
        usage="(channel or 'all') (command)",
        example="all blunt",
        aliases=["unlock"],
    )
    @commands.has_permissions(manage_guild=True)
    async def command_enable(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread | Literal["all"], *, command: wock.Command):
        """Enable a previously disabled command"""

        disabled_channels = await self.bot.db.fetch(
            "SELECT channel_id FROM commands.disabled WHERE guild_id = $1 AND command = $2",
            ctx.guild.id,
            command.qualified_name,
        )

        if channel == "all":
            try:
                await self.bot.db.execute(
                    "DELETE FROM commands.disabled WHERE guild_id = $1 AND command = $2",
                    ctx.guild.id,
                    command.qualified_name,
                    raise_exceptions=True,
                )
            except:
                return await ctx.warn(f"Command `{command.qualified_name}` is already enabled in every channel")
        else:
            try:
                await self.bot.db.execute(
                    "DELETE FROM commands.disabled WHERE guild_id = $1 AND channel_id = $2 AND command = $3",
                    ctx.guild.id,
                    channel.id,
                    command.qualified_name,
                    raise_exceptions=True,
                )
            except:
                return await ctx.warn(f"Command `{command.qualified_name}` is already enabled in {channel.mention}")

        await ctx.approve(
            f"Command `{command.qualified_name}` has been enabled in "
            + (f"{functions.plural(len(disabled_channels), bold=True):channel}" if channel == "all" else channel.mention)
        )

    @command.group(
        name="disable",
        usage="(channel or 'all') (command)",
        example="#spam blunt",
        aliases=["lock"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def command_disable(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread | Literal["all"], *, command: wock.Command):
        """Disable a command in a channel"""

        if command.qualified_name.startswith("command"):
            return await ctx.warn(f"You can't disable this **command**")

        disabled_channels = await self.bot.db.fetch(
            "SELECT channel_id FROM commands.disabled WHERE guild_id = $1 AND command = $2",
            ctx.guild.id,
            command.qualified_name,
        )

        if channel == "all":
            await self.bot.db.executemany(
                "INSERT INTO commands.disabled (guild_id, channel_id, command) VALUES($1, $2, $3) ON CONFLICT (guild_id, channel_id, command) DO"
                " NOTHING",
                [
                    (
                        ctx.guild.id,
                        _channel.id,
                        command.qualified_name,
                    )
                    for _channel in ctx.guild.text_channels
                ],
            )
        else:
            try:
                await self.bot.db.execute(
                    "INSERT INTO commands.disabled (guild_id, channel_id, command) VALUES($1, $2, $3)",
                    ctx.guild.id,
                    channel.id,
                    command.qualified_name,
                    raise_exceptions=True,
                )
            except:
                return await ctx.warn(f"Command `{command.qualified_name}` is already disabled in {channel.mention}")

        if channel == "all" and len(ctx.guild.text_channels) == len(disabled_channels):
            return await ctx.warn(f"Command `{command.qualified_name}` is already disabled in every channel")

        await ctx.approve(
            f"Command `{command.qualified_name}` has been disabled in "
            + (
                f"{functions.plural(len(disabled_channels) - len(ctx.guild.text_channels), bold=True):channel} "
                + (f"(already disabled in {len(disabled_channels)})" if disabled_channels else "")
                if channel == "all"
                else channel.mention
            )
        )

    @command_disable.command(
        name="list",
        aliases=["show", "view"],
    )
    @commands.has_permissions(manage_guild=True)
    async def command_disable_list(self, ctx: wock.Context):
        """View all disabled commands"""

        commands = [
            f"`{row['command']}` - {self.bot.get_channel(row['channel_id']).mention}"
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id, command FROM commands.disabled WHERE guild_id = $1",
                ctx.guild.id,
            )
            if self.bot.get_command(row["command"]) and self.bot.get_channel(row["channel_id"])
        ]
        if not commands:
            return await ctx.warn(f"No commands have been **disabled**")

        await ctx.paginate(
            discord.Embed(
                title="Disabled Commands",
                description=commands,
            )
        )

    @command.group(
        name="restrict",
        usage="(role) (command)",
        example="Moderator snipe",
        aliases=["permit"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def command_restrict(self, ctx: wock.Context, role: wock.Role, *, command: wock.Command):
        """Restrict a command to certain roles"""

        if command.qualified_name.startswith("command"):
            return await ctx.warn(f"You can't restrict this **command**")

        try:
            await self.bot.db.execute(
                "INSERT INTO commands.restricted (guild_id, role_id, command) VALUES($1, $2, $3)",
                ctx.guild.id,
                role.id,
                command.qualified_name,
                raise_exceptions=True,
            )
        except:
            await self.bot.db.execute(
                "DELETE FROM commands.restricted WHERE guild_id = $1 AND role_id = $2 AND command = $3",
                ctx.guild.id,
                role.id,
                command.qualified_name,
            )
            return await ctx.approve(f"Removed restriction for {role.mention} on `{command.qualified_name}`")

        await ctx.approve(f"Allowing users with {role.mention} to use `{command.qualified_name}`")

    @command_restrict.command(
        name="list",
        aliases=["show", "view"],
    )
    @commands.has_permissions(manage_guild=True)
    async def command_restrict_list(self, ctx: wock.Context):
        """View all restricted commands"""

        commands = [
            f"`{row['command']}` - {ctx.guild.get_role(row['role_id']).mention}"
            async for row in self.bot.db.fetchiter(
                "SELECT role_id, command FROM commands.restricted WHERE guild_id = $1",
                ctx.guild.id,
            )
            if self.bot.get_command(row["command"]) and ctx.guild.get_role(row["role_id"])
        ]
        if not commands:
            return await ctx.warn(f"No commands have been **restricted**")

        await ctx.paginate(
            discord.Embed(
                title="Restricted Commands",
                description=commands,
            )
        )

    @commands.group(
        name="alias",
        usage="(subcommand) <args>",
        example="add deport ban",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def alias(self, ctx: wock.Context):
        """Set a custom alias for commands"""

        await ctx.send_help()

    @alias.command(
        name="add",
        usage="(alias) (command)",
        example="deport ban",
        aliases=["create"],
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_add(self, ctx: wock.Context, alias: str, *, command: str):
        """Add a custom alias for a command"""

        alias = alias.lower().replace(" ", "")
        if self.bot.get_command(alias):
            return await ctx.warn(f"Command for alias `{alias}` already exists")

        _command = self.bot.get_command(regex.STRING.match(command).group())
        if not _command:
            return await ctx.warn(f"Command `{command}` does not exist")

        try:
            await self.bot.db.execute(
                "INSERT INTO aliases (guild_id, alias, command, invoke) VALUES ($1, $2, $3, $4)",
                ctx.guild.id,
                alias,
                _command.qualified_name,
                command,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"Alias `{alias}` already exists")
        else:
            await ctx.approve(f"Added alias `{alias}` for command `{_command}`")

    @alias.command(
        name="remove",
        usage="(alias)",
        example="deport",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_remove(self, ctx: wock.Context, alias: str):
        """Remove a bound alias"""

        alias = alias.lower().replace(" ", "")

        try:
            await self.bot.db.execute(
                "DELETE FROM aliases WHERE guild_id = $1 AND alias = $2",
                ctx.guild.id,
                alias,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The alias `{alias}` doesn't exist")
        else:
            await ctx.approve(f"Removed alias `{alias}`")

    @alias.command(
        name="reset",
        usage="<command>",
        example="ban",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_reset(self, ctx: wock.Context, *, command: wock.Command = None):
        """Remove every bound alias"""

        if command:
            try:
                await self.bot.db.execute(
                    "DELETE FROM aliases WHERE guild_id = $1 AND command = $2",
                    ctx.guild.id,
                    command.qualified_name,
                    raise_exceptions=True,
                )
            except:
                await ctx.warn(f"There aren't any aliases for command `{command}`")
            else:
                await ctx.approve(f"Removed all aliases for command `{command}`")
        else:
            try:
                await self.bot.db.execute(
                    "DELETE FROM aliases WHERE guild_id = $1",
                    ctx.guild.id,
                    raise_exceptions=True,
                )
            except:
                await ctx.warn("There aren't any **aliases** to reset")
            else:
                await ctx.approve(f"Reset all **aliases**")

    @alias.command(
        name="list",
        usage="<command>",
        example="ban",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_list(self, ctx: wock.Context, *, command: wock.Command = None):
        """View all bound aliases"""

        if command:
            aliases = [
                f"`{row['alias']}` bound to `{row['command']}`"
                async for row in self.bot.db.fetchiter(
                    "SELECT alias, command FROM aliases WHERE guild_id = $1 AND command = $2",
                    ctx.guild.id,
                    command.qualified_name,
                )
                if not self.bot.get_command(row["alias"])
            ]
            if not aliases:
                return await ctx.warn(f"No aliases have been **assigned** to command `{command.qualified_name}`")
        else:
            aliases = [
                f"`{row['alias']}` bound to `{row['command']}`"
                async for row in self.bot.db.fetchiter(
                    "SELECT alias, command FROM aliases WHERE guild_id = $1",
                    ctx.guild.id,
                )
                if self.bot.get_command(row["command"]) and not self.bot.get_command(row["alias"])
            ]
            if not aliases:
                return await ctx.warn(f"No aliases have been **assigned**")

        await ctx.paginate(discord.Embed(title="Command Aliases", description=aliases))

    @commands.group(
        name="invoke",
        usage="(command) (embed script)",
        example="ban 🚬 - {reason}",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def invoke(self, ctx: wock.Context, command: str, *, script: wock.EmbedScriptValidator):
        """Set a custom message for a moderation command"""

        _command = command.replace(".", " ")
        if command := self.bot.get_command(_command, "Moderation"):
            if command.qualified_name in ("role", "emoji"):
                return await ctx.warn(f"You must specify a **subcommand** for the `{command.qualified_name}` command")
            elif command.qualified_name in (
                "audit",
                "role icon",
                "emoji list",
                "emoji remove duplicates",
                "sticker list",
            ) or command.qualified_name.startswith(("purge", "lockdown ignore", "history")):
                return await ctx.warn(f"You aren't allowed to set an **invoke message** for the `{command.qualified_name}` command")

            configuration = await self.bot.db.fetch_config(ctx.guild.id, "invoke") or {}
            configuration[command.qualified_name.replace(" ", ".")] = str(script)
            await self.bot.db.update_config(ctx.guild.id, "invoke", configuration)

            await ctx.approve(f"Set the **{command.qualified_name}** invoke message to {script.type()}")
        else:
            await ctx.warn(f"Command `{_command}` doesn't exist")

    @invoke.command(
        name="reset",
        usage="(command)",
        example="ban",
        aliases=["remove"],
    )
    @commands.has_permissions(manage_guild=True)
    async def invoke_reset(self, ctx: wock.Context, *, command: str):
        """Reset the custom message for a moderation command"""

        _command = command.replace(".", " ")
        if command := self.bot.get_command(_command, "Moderation"):
            if command.qualified_name == "role":
                return await ctx.warn(f"You must specify a **subcommand** for the `role` command")

            configuration = await self.bot.db.fetch_config(ctx.guild.id, "invoke") or {}
            if command.qualified_name.replace(" ", ".") in configuration:
                del configuration[command.qualified_name.replace(" ", ".")]
                await self.bot.db.update_config(ctx.guild.id, "invoke", configuration)

                await ctx.approve(f"Reset the **{command.qualified_name}** invoke message")
            else:
                await ctx.warn(f"The **{command.qualified_name}** invoke message is not set")
        else:
            await ctx.warn(f"Command `{_command}` doesn't exist")

    @commands.group(
        name="boosterrole",
        usage="(color) <name>",
        example="#BBAAEE 4PF",
        aliases=["boostrole", "br"],
        invoke_without_command=True,
    )
    @checks.require_boost()
    @commands.max_concurrency(1, commands.BucketType.member)
    async def boosterrole(
        self,
        ctx: wock.Context,
        color: wock.Color,
        *,
        name: str = None,
    ):
        """Create your own color role"""

        base_role = ctx.guild.get_role(await self.bot.db.fetch_config(ctx.guild.id, "base_role_id"))
        if not base_role:
            return await ctx.warn(f"The **base role** has not been set yet!\n> Use `{ctx.prefix}boosterrole base` to set it")

        role_id = await self.bot.db.fetchval("SELECT role_id FROM booster_roles WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
        if not role_id or not ctx.guild.get_role(role_id):
            if len(ctx.guild.roles) >= 250:
                return await ctx.warn("The **role limit** has been reached")

            role = await ctx.guild.create_role(
                name=(name[:100] if name else f"booster:{functions.hash(ctx.author.id)}"),
                color=color,
            )
            await ctx.guild.edit_role_positions(
                {
                    role: base_role.position - 1,
                }
            )

            try:
                await ctx.author.add_roles(role, reason="Booster role")
            except discord.Forbidden:
                await role.delete(reason="Booster role failed to assign")
                return await ctx.warn("I don't have permission to **assign roles** to you")

            await self.bot.db.execute(
                "INSERT INTO booster_roles (guild_id, user_id, role_id) VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id) DO UPDATE SET role_id"
                " = $3",
                ctx.guild.id,
                ctx.author.id,
                role.id,
            )
        else:
            role = ctx.guild.get_role(role_id)
            await role.edit(
                name=(name[:100] if name else role.name),
                color=color,
            )
            if not role in ctx.author.roles:
                try:
                    await ctx.author.add_roles(role, reason="Booster role")
                except discord.Forbidden:
                    await role.delete(reason="Booster role failed to assign")
                    return await ctx.warn("I don't have permission to **assign roles** to you")

        await ctx.neutral(f"Your **booster role color** has been set to `{color}`", emoji="🎨", color=color)

    @boosterrole.command(
        name="base",
        usage="(role)",
        example="@Booster",
        aliases=["set"],
    )
    async def boosterrole_base(self, ctx: wock.Context, *, role: wock.Role):
        """Set the base role for booster roles"""

        await wock.Role().manageable(ctx, role, booster=True)

        await self.bot.db.update_config(ctx.guild.id, "base_role_id", role.id)
        await ctx.approve(f"Set the **base role** to {role.mention}")

    @boosterrole.command(
        name="color",
        usage="(color)",
        example="#BBAAEE",
        aliases=["colour"],
    )
    @checks.require_boost()
    async def boosterrole_color(self, ctx: wock.Context, *, color: wock.Color):
        """Change the color of your booster role"""

        role_id = await self.bot.db.fetchval("SELECT role_id FROM booster_roles WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
        if not role_id or not ctx.guild.get_role(role_id):
            return await self.bot.get_command("boosterrole")(ctx, color=color)

        role = ctx.guild.get_role(role_id)
        await role.edit(
            color=color,
        )
        await ctx.neutral(f"Changed the **color** of your **booster role** to `{color}`", emoji="🎨", color=color)

    @boosterrole.command(
        name="rename",
        usage="(name)",
        example="4PF",
        aliases=["name"],
    )
    @checks.require_boost()
    async def boosterrole_rename(self, ctx: wock.Context, *, name: str):
        """Rename your booster role"""

        role_id = await self.bot.db.fetchval("SELECT role_id FROM booster_roles WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
        if not role_id or not ctx.guild.get_role(role_id):
            return await ctx.warn("You don't have a **booster role** yet")

        role = ctx.guild.get_role(role_id)
        await role.edit(
            name=name[:100],
        )
        await ctx.approve(f"Renamed your **booster role** to **{name}**")

    @boosterrole.command(
        name="icon",
        usage="(icon)",
        example="🦅",
        aliases=["emoji"],
    )
    @checks.require_boost()
    async def boosterrole_icon(
        self,
        ctx: wock.Context,
        *,
        icon: Literal["remove", "reset", "off"] | wock.EmojiFinder | wock.ImageFinder = None,
    ):
        """Change the icon of your booster role"""

        if "ROLE_ICONS" not in ctx.guild.features:
            return await ctx.warn("This server doesn't have enough **boosts** to use **role icons**")
        if not icon:
            icon = await wock.ImageFinder.search(ctx)
        elif isinstance(icon, str) and icon in ("remove", "reset", "off"):
            icon = None

        role_id = await self.bot.db.fetchval("SELECT role_id FROM booster_roles WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
        if not role_id or not ctx.guild.get_role(role_id):
            return await ctx.warn("You don't have a **booster role** yet")

        role = ctx.guild.get_role(role_id)

        _icon = None
        if type(icon) in (wock.Emoji, str):
            response = await ctx.bot.session.get(icon if not isinstance(icon, wock.Emoji) else icon.url)
            _icon = await response.read()
        else:
            if not role.display_icon:
                return await ctx.warn(f"Your **booster role** doesn't have an **icon** yet")

        await role.edit(
            display_icon=_icon,
        )
        if icon:
            await ctx.approve(
                f"Changed the **icon** of your **booster role** to {f'{icon}' if isinstance(icon, wock.Emoji) else f'[**image**]({icon})'}"
            )
        else:
            await ctx.approve("Removed the **icon** of your **booster role**")

    @boosterrole.command(
        name="dominant",
        aliases=["dom", "avatar", "pfp"],
    )
    @checks.require_boost()
    async def boosterrole_dominant(self, ctx: wock.Context):
        """Match your booster role color to your avatar"""

        color = await functions.extract_color(
            self.bot.redis,
            ctx.author.display_avatar.url,
        )
        await self.bot.get_command("boosterrole")(ctx, color=color)

    @boosterrole.command(
        name="remove",
        aliases=["delete", "del", "rm"],
    )
    @checks.require_boost()
    async def boosterrole_remove(self, ctx: wock.Context):
        """Remove your booster role"""

        role_id = await self.bot.db.fetchval("SELECT role_id FROM booster_roles WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
        if not role_id or not ctx.guild.get_role(role_id):
            return await ctx.warn("You don't have a **booster role** yet")

        role = ctx.guild.get_role(role_id)
        await role.delete(reason="Booster role removed")
        await self.bot.db.execute("DELETE FROM booster_roles WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
        await ctx.approve("Removed your **booster role**")

    @boosterrole.command(
        name="cleanup",
        parameters={"boosters": {"require_value": False, "description": "Whether to include boosters", "aliases": ["all"]}},
        aliases=["clean", "purge"],
    )
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def boosterrole_cleanup(self, ctx: wock.Context):
        """Clean up booster roles which aren't boosting"""

        if ctx.parameters.get("boosters"):
            await ctx.prompt(
                "Are you sure you want to **remove all booster roles** in this server?\n> This includes members which are still **boosting** the"
                " serverw!"
            )

        async with ctx.typing():
            cleaned = []
            async for row in self.bot.db.fetchiter("SELECT user_id, role_id FROM booster_roles WHERE guild_id = $1", ctx.guild.id):
                member = ctx.guild.get_member(row["user_id"])
                role = ctx.guild.get_role(row["role_id"])
                if not role:
                    cleaned.append(row)
                    continue
                if ctx.parameters.get("boosters"):
                    with contextlib.suppress(discord.HTTPException):
                        await role.delete(reason=f"Booster role cleanup ({ctx.author})")

                    cleaned.append(row)
                elif not member or not member.premium_since:
                    with contextlib.suppress(discord.HTTPException):
                        await role.delete(reason="Member no longer boosting")

                    cleaned.append(row)
                elif member and not role in member.roles:
                    with contextlib.suppress(discord.HTTPException):
                        await role.delete(reason="Member doesn't have role")

                    cleaned.append(row)

            if cleaned:
                await self.bot.db.execute(
                    "DELETE FROM booster_roles WHERE guild_id = $1 AND user_id = ANY($2)",
                    ctx.guild.id,
                    [row["user_id"] for row in cleaned],
                )
                await ctx.approve(f"Cleaned up {functions.plural(cleaned, bold=True):booster role}")
            else:
                await ctx.warn("There are no **booster roles** to clean up")

    @boosterrole.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_roles=True)
    async def boosterrole_list(self, ctx: wock.Context):
        """View all booster roles"""

        roles = [
            f"**{member}** - {role.mention}"
            async for row in self.bot.db.fetchiter("SELECT user_id, role_id FROM booster_roles WHERE guild_id = $1", ctx.guild.id)
            if (role := ctx.guild.get_role(row["role_id"])) and (member := ctx.guild.get_member(row["user_id"]))
        ]
        if not roles:
            return await ctx.warn("There are no **booster roles** in this server")

        await ctx.paginate(
            discord.Embed(
                title="Booster Roles",
                description=roles,
            )
        )

    @commands.group(
        name="response",
        usage="(subcommand) <args>",
        example="add Hi, Hey {user} -reply",
        aliases=["autoresponder", "autoresponse", "ar"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_channels=True)
    async def response(self, ctx: wock.Context):
        """Set up automatic trigger responses"""

        await ctx.send_help()

    @response.command(
        name="add",
        usage="(trigger), (response)",
        example="Hi, Hey {user} -reply",
        parameters={
            "self_destruct": {
                "converter": int,
                "description": "The time in seconds to wait before deleting the response",
                "minimum": 1,
                "maximum": 120,
                "aliases": ["delete_after", "delete"],
            },
            "not_strict": {
                "require_value": False,
                "description": "Whether the trigger can be anywhere in the message",
            },
            "ignore_command_check": {
                "require_value": False,
                "description": "Whether to allow the trigger if it exists as a command",
                "aliases": ["ignore_command"],
            },
            "reply": {
                "require_value": False,
                "description": "Whether to reply to the trigger message",
                "aliases": ["reply_trigger"],
            },
            "delete": {
                "require_value": False,
                "description": "Whether to delete the trigger message",
                "aliases": ["delete_trigger"],
            },
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_channels=True)
    async def response_add(
        self,
        ctx: wock.Context,
        *,
        message: str,
    ):
        """Add a response trigger"""

        message = message.split(", ", 1)
        if len(message) != 2:
            return await ctx.warn("You must specify a **trigger** and **response**")

        trigger = message[0].strip()
        response = message[1].strip()
        if not trigger:
            return await ctx.warn("You must specify a **trigger**")
        elif not response:
            return await ctx.warn("You must specify a **response**")

        if not (response := await wock.EmbedScriptValidator().convert(ctx, response)):
            return

        try:
            await self.bot.db.execute(
                "INSERT INTO auto_responses (guild_id, trigger, response, self_destruct, not_strict, ignore_command_check, reply, delete) VALUES ($1,"
                " $2, $3, $4, $5, $6, $7, $8)",
                ctx.guild.id,
                trigger,
                str(response),
                ctx.parameters.get("self_destruct"),
                ctx.parameters.get("not_strict"),
                ctx.parameters.get("ignore_command_check"),
                ctx.parameters.get("reply"),
                ctx.parameters.get("delete"),
            )
        except:
            await ctx.warn(f"There is already a **response trigger** for `{trigger}`")
        else:
            await ctx.approve(
                f"Created {response.type(bold=False)} **response trigger** for `{trigger}` "
                + " ".join(f"({key.replace('_', ' ')})" for key, value in ctx.parameters.items() if value and key != "not_strict")
                + (" (strict match)" if not ctx.parameters.get("not_strict") else "")
            )

    @response.command(
        name="remove",
        usage="(trigger)",
        example="Hi",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_channels=True)
    async def response_remove(self, ctx: wock.Context, *, trigger: str):
        """Remove a response trigger"""

        try:
            await self.bot.db.execute(
                "DELETE FROM auto_responses WHERE guild_id = $1 AND lower(trigger) = $2",
                ctx.guild.id,
                trigger.lower(),
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There isn't a **response trigger** for `{trigger}`")
        else:
            await ctx.approve(f"Removed **response trigger** for `{trigger}`")

    @response.command(
        name="view",
        usage="(trigger)",
        example="Hi",
        aliases=["check", "test", "emit"],
    )
    @commands.has_permissions(manage_channels=True)
    async def response_view(self, ctx: wock.Context, *, trigger: str):
        """View a response trigger"""

        data = await self.bot.db.fetchrow(
            "SELECT * FROM auto_responses WHERE guild_id = $1 AND lower(trigger) = $2",
            ctx.guild.id,
            trigger.lower(),
        )
        if not data:
            return await ctx.warn(f"There isn't a **response trigger** for `{trigger}`")

        await wock.EmbedScript(data["response"]).send(
            ctx.channel,
            bot=self.bot,
            guild=ctx.guild,
            channel=ctx.channel,
            user=ctx.author,
        )

    @response.command(
        name="reset",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_channels=True)
    async def response_reset(self, ctx: wock.Context):
        """Remove all response triggers"""

        await ctx.prompt("Are you sure you want to remove all **response triggers**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM auto_responses WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("There are no **response triggers**")
        else:
            await ctx.approve("Removed all **response triggers**")

    @response.command(name="list", aliases=["show", "all"])
    @commands.has_permissions(manage_channels=True)
    async def response_list(self, ctx: wock.Context):
        """View all response triggers"""

        data = await self.bot.db.fetch(
            "SELECT * FROM auto_responses WHERE guild_id = $1",
            ctx.guild.id,
        )
        if not data:
            return await ctx.warn("There are no **response triggers**")

        await ctx.paginate(
            discord.Embed(
                title="Response Triggers",
                description=list(f"**{data['trigger']}** (strict: {'yes' if not data['not_strict'] else 'no'})" for data in data),
            )
        )

    @commands.group(
        name="autorole",
        usage="(subcommand) <args>",
        example="add @Member",
        aliases=["welcrole"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx: wock.Context):
        """Automatically assign roles to new members"""

        await ctx.send_help()

    @autorole.command(
        name="add",
        usage="(role)",
        example="@Member",
        parameters={
            "discriminator": {
                "converter": wock.DiscriminatorValidator,
                "description": "The discriminator to assign the role to",
                "aliases": ["discrim", "tag"],
            },
            "humans": {
                "require_value": False,
                "description": "Only assign the role to humans",
                "aliases": ["human"],
            },
            "bots": {
                "require_value": False,
                "description": "Only assign the role to bots",
                "aliases": ["bot"],
            },
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_roles=True)
    async def autorole_add(self, ctx: wock.Context, role: wock.Role):
        """Add a role to be assigned to new members"""

        await wock.Role().manageable(ctx, role)
        if not ctx.parameters.get("bots"):
            await wock.Role().dangerous(ctx, role, "assign")

        try:
            await self.bot.db.execute(
                "INSERT INTO auto_roles (guild_id, role_id, discriminator, humans, bots) VALUES ($1, $2, $3, $4, $5)",
                ctx.guild.id,
                role.id,
                ctx.parameters.get("discriminator"),
                ctx.parameters.get("humans"),
                ctx.parameters.get("bots"),
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The role {role.mention} is already being **assigned** to new members")
        else:
            await ctx.approve(
                f"Now assigning {role.mention} to new members"
                + (f" (`{ctx.parameters.get('discriminator')}`)" if ctx.parameters.get("discriminator") else "")
                + (f" (humans)" if ctx.parameters.get("humans") else "")
                + (f" (bots)" if ctx.parameters.get("bots") else "")
            )

    @autorole.command(
        name="remove",
        usage="(role)",
        example="@Member",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_roles=True)
    async def autorole_remove(self, ctx: wock.Context, *, role: wock.Role):
        """Remove a role from being assigned to new members"""

        try:
            await self.bot.db.execute(
                "DELETE FROM auto_roles WHERE guild_id = $1 AND role_id = $2",
                ctx.guild.id,
                role.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The role {role.mention} is not being **assigned** to new members")
        else:
            await ctx.approve(f"No longer assigning {role.mention} to new members")

    # @autorole.command(name="reassign", aliases=["sticky"])
    # @commands.has_permissions(manage_roles=True)
    # async def autorole_reassign(self, ctx: wock.Context):
    #     """Toggle whether or not to reassign roles to members which rejoin the server"""

    #     reassign = await self.bot.db.fetch_config(ctx.guild.id, "reassign_roles")
    #     await self.bot.db.update_config(ctx.guild.id, "reassign_roles", not reassign)
    #     await ctx.approve(f"{'Now' if not reassign else 'No longer'} **reassigning** roles to members which rejoin the server")

    @autorole.command(name="reset", aliases=["clear"])
    @commands.has_permissions(manage_roles=True)
    async def autorole_reset(self, ctx: wock.Context):
        """Remove every role which is being assigned to new members"""

        await ctx.prompt("Are you sure you want to remove all **assigned roles**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM auto_roles WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No roles are being **assigned** to new members")
        else:
            await ctx.approve("No longer **assigning** any roles to new members")

    @autorole.command(name="list", aliases=["show", "all"])
    @commands.has_permissions(manage_roles=True)
    async def autorole_list(self, ctx: wock.Context):
        """View all the roles being assigned to new members"""

        roles = [
            ctx.guild.get_role(row.get("role_id")).mention
            + (f" (`{row.get('discriminator')}`)" if row.get("discriminator") else "")
            + (f" (humans)" if row.get("humans") else "")
            + (f" (bots)" if row.get("bots") else "")
            async for row in self.bot.db.fetchiter("SELECT role_id, discriminator, humans, bots FROM auto_roles WHERE guild_id = $1", ctx.guild.id)
            if ctx.guild.get_role(row.get("role_id"))
        ]
        if not roles:
            return await ctx.warn("No roles are being **assigned** to new members")

        await ctx.paginate(
            discord.Embed(
                title="Auto Roles",
                description=roles,
            )
        )

    @commands.group(
        name="reactionrole",
        usage="(subcommand) <args>",
        example="dscord.com/chnls/999/.. ✅ Member",
        aliases=["rr"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_roles=True)
    async def reactionrole(self, ctx: wock.Context):
        """Set up self assignable roles"""

        await ctx.send_help()

    @reactionrole.command(
        name="add",
        usage="(message) (emoji) (role)",
        example="dscord.com/chnls/999/.. ✅ Member",
        parameters={
            "oneway": {
                "require_value": False,
                "description": "Disable the ability to remove the role",
                "aliases": ["one-way", "one_way"],
            }
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_roles=True)
    async def reactionrole_add(self, ctx: wock.Context, message: discord.Message, emoji: str, role: wock.Role):
        """Add a reaction role to a message"""

        if message.guild != ctx.guild:
            return await ctx.warn("The **message** must be in this server")

        await wock.Role().manageable(ctx, role)
        await wock.Role().dangerous(ctx, role, "assign")

        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            return await ctx.warn(f"**{emoji}** is not a valid emoji")

        try:
            await self.bot.db.execute(
                "INSERT INTO reaction_roles (guild_id, channel_id, message_id, role_id, emoji, oneway) VALUES ($1, $2, $3, $4, $5, $6)",
                ctx.guild.id,
                message.channel.id,
                message.id,
                role.id,
                emoji,
                ctx.parameters.get("oneway"),
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The role {role.mention} is already being **assigned** for {emoji}")
        else:
            await ctx.approve(
                f"Now assigning {role.mention} for {emoji} on [`{message.id}`]({message.jump_url})"
                f" {'(one-way)' if ctx.parameters.get('oneway') else ''}"
            )

    @reactionrole.group(
        name="remove",
        usage="(message) (emoji)",
        example="dscord.com/chnls/999/.. ✅",
        aliases=["delete", "del", "rm"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_roles=True)
    async def reactionrole_remove(self, ctx: wock.Context, message: discord.Message, emoji: str):
        """Remove a reaction role from a message"""

        if message.guild != ctx.guild:
            return await ctx.warn("The **message** must be in this server")

        try:
            await self.bot.db.execute(
                "DELETE FROM reaction_roles WHERE guild_id = $1 AND message_id = $2 AND emoji = $3",
                ctx.guild.id,
                message.id,
                emoji,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"No roles are being **assigned** for **{emoji}**")
        else:
            await ctx.approve(f"Removed the **reaction role** for **{emoji}** on [`{message.id}`]({message.jump_url})")

    @reactionrole_remove.command(
        name="all",
        usage="(message)",
        example="dscord.com/chnls/999/..",
    )
    @commands.has_permissions(manage_roles=True)
    async def reactionrole_remove_all(self, ctx: wock.Context, message: discord.Message):
        """Remove all reaction roles from a message"""

        if message.guild != ctx.guild:
            return await ctx.warn("The **message** must be in this server")

        try:
            await self.bot.db.execute(
                "DELETE FROM reaction_roles WHERE guild_id = $1 AND message_id = $2",
                ctx.guild.id,
                message.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"No roles are being **assigned** on [`{message.id}`]({message.jump_url})")
        else:
            await ctx.approve(f"Removed all **reaction roles** on [`{message.id}`]({message.jump_url})")

    @reactionrole.command(name="reset", aliases=["clear"])
    @commands.has_permissions(manage_roles=True)
    async def reactionrole_reset(self, ctx: wock.Context):
        """Reset all reaction roles"""

        await ctx.prompt("Are you sure you want to reset all **reaction roles**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM reaction_roles WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No roles are being **assigned**")
        else:
            await ctx.approve("Reset all **reaction roles**")

    @reactionrole.command(
        name="list",
        aliases=["show"],
    )
    @commands.has_permissions(manage_roles=True)
    async def reactionrole_list(self, ctx: wock.Context):
        """View all reaction roles"""

        messages = [
            f"[`{row['message_id']}`]({channel.get_partial_message(row['message_id']).jump_url}) - {role.mention} |"
            f" {row['emoji']} {'(one-way)' if row['oneway'] else ''}"
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id, message_id, emoji, role_id, oneway FROM reaction_roles WHERE guild_id = $1",
                ctx.guild.id,
            )
            if (channel := ctx.guild.get_channel(row["channel_id"])) and (role := ctx.guild.get_role(row["role_id"]))
        ]
        if not messages:
            return await ctx.warn("No roles are being **assigned**")

        await ctx.paginate(
            discord.Embed(
                title="Reaction Roles",
                description=messages,
            )
        )

    @commands.group(
        name="reaction",
        usage="(subcommand) <args>",
        example="add 🐐 rx",
        aliases=["reactiontrigger", "react", "rt"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_channels=True)
    async def reaction(self, ctx: wock.Context):
        """Set up reaction triggers"""

        await ctx.send_help()

    @reaction.command(
        name="add",
        usage="(emoji) (trigger)",
        example="🐐 rx",
        parameters={
            "strict": {
                "require_value": False,
                "description": "Only react to exact matches",
            }
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_channels=True)
    async def reaction_add(
        self,
        ctx: wock.Context,
        emoji: str,
        *,
        trigger: str,
    ):
        """Add a reaction trigger"""

        try:
            await ctx.message.add_reaction(emoji)
        except discord.HTTPException:
            return await ctx.warn(f"**{emoji}** is not a valid emoji")

        if (
            await self.bot.db.fetchval("SELECT COUNT(*) FROM reaction_triggers WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, trigger.lower())
        ) >= 3:
            return await ctx.warn(f"You're only allowed to have **3** reactions per **trigger**")

        try:
            await self.bot.db.execute(
                "INSERT INTO reaction_triggers VALUES ($1, $2, $3, $4)",
                ctx.guild.id,
                trigger.lower(),
                emoji,
                ctx.parameters.get("strict"),
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There is already a **reaction trigger** for **{emoji}** on `{trigger}`")
        else:
            await ctx.approve(
                f"Added **{emoji}** as a **reaction trigger** on `{trigger}`" + (f" (strict match)" if ctx.parameters.get("strict") else "")
            )

    @reaction.command(
        name="remove",
        usage="(emoji) (trigger)",
        example="🐐 rx",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_channels=True)
    async def reaction_remove(
        self,
        ctx: wock.Context,
        emoji: str,
        *,
        trigger: str,
    ):
        """Remove a reaction trigger"""

        try:
            await self.bot.db.execute(
                "DELETE FROM reaction_triggers WHERE guild_id = $1 AND emoji = $3 AND trigger = $2",
                ctx.guild.id,
                trigger.lower(),
                emoji,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There isn't a **reaction trigger** for **{emoji}** on `{trigger}`")
        else:
            await ctx.approve(f"Removed **reaction trigger** for **{emoji}** on `{trigger}`")

    @reaction.command(
        name="reset",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_channels=True)
    async def reaction_reset(self, ctx: wock.Context):
        """Remove all reaction triggers"""

        await ctx.prompt("Are you sure you want to remove all **reaction triggers**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM reaction_triggers WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("There are no **reaction triggers**")
        else:
            await ctx.approve("Removed all **reaction triggers**")

    @reaction.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_channels=True)
    async def reaction_list(self, ctx: wock.Context):
        """View all reaction triggers"""

        data = [
            f"**{row['trigger']}** - {', '.join(row['emojis'])} {'(strict)' if row['strict'] else ''}"
            async for row in self.bot.db.fetchiter(
                "SELECT trigger, array_agg(emoji) AS emojis, strict FROM reaction_triggers WHERE guild_id = $1 GROUP BY trigger, strict",
                ctx.guild.id,
            )
        ]
        if not data:
            return await ctx.warn("There are no **reaction triggers**")

        await ctx.paginate(
            discord.Embed(
                title="Reaction Triggers",
                description=data,
            )
        )

    @commands.group(
        name="thread",
        usage="(subcommand) <args>",
        example="add #rules",
        aliases=["watcher"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_threads=True)
    async def thread(self, ctx: wock.Context):
        """Prevent threads from archiving"""

        await ctx.send_help()

    @thread.command(
        name="add",
        usage="(thread)",
        example="#rules",
        aliases=["create"],
    )
    @commands.has_permissions(manage_threads=True)
    async def thread_add(self, ctx: wock.Context, *, thread: discord.Thread):
        """Add a thread to be watched"""

        try:
            await self.bot.db.execute(
                "INSERT INTO thread_watcher VALUES ($1, $2)",
                ctx.guild.id,
                thread.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The thread {thread.mention} is already being **watched**")
        else:
            await ctx.approve(f"Now watching {thread.mention} for archival")

    @thread.command(
        name="remove",
        usage="(thread)",
        example="#rules",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_threads=True)
    async def thread_remove(self, ctx: wock.Context, *, thread: discord.Thread):
        """Remove a thread from being watched"""

        try:
            await self.bot.db.execute(
                "DELETE FROM thread_watcher WHERE guild_id = $1 AND thread_id = $2",
                ctx.guild.id,
                thread.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"The thread {thread.mention} is not being **watched**")
        else:
            await ctx.approve(f"No longer watching {thread.mention} for archival")

    @thread.command(name="reset", aliases=["clear"])
    @commands.has_permissions(manage_threads=True)
    async def thread_reset(self, ctx: wock.Context):
        """Reset all watched threads"""

        await ctx.prompt("Are you sure you want to stop **watching** all threads?")

        try:
            await self.bot.db.execute(
                "DELETE FROM thread_watcher WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No threads are being **watched**")
        else:
            await ctx.approve("No longer **watching** any threads")

    @thread.command(name="list", aliases=["show", "all"])
    @commands.has_permissions(manage_threads=True)
    async def thread_list(self, ctx: wock.Context):
        """View all the threads being watched"""

        threads = [
            ctx.guild.get_thread(row.get("thread_id")).mention
            async for row in self.bot.db.fetchiter("SELECT thread_id FROM thread_watcher WHERE guild_id = $1", ctx.guild.id)
            if ctx.guild.get_thread(row.get("thread_id"))
        ]
        if not threads:
            return await ctx.warn("No threads are being **watched**")

        await ctx.paginate(
            discord.Embed(
                title="Thread Watcher",
                description=threads,
            )
        )

    @commands.group(
        name="counter",
        usage="(subcommand) <args>",
        example="add members voice",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_channels=True)
    async def counter(self, ctx: wock.Context):
        """Set up public channel statistics"""

        await ctx.send_help()

    @counter.command(
        name="add",
        usage="(option) (type of channel)",
        example="members voice",
        aliases=["create"],
    )
    @commands.has_permissions(manage_channels=True)
    async def counter_add(
        self, ctx: wock.Context, option: Literal["members", "boosts"], channel: Literal["voice", "text", "category", "announce", "stage"]
    ):
        """Add a counter channel"""

        if counter_id := await self.bot.db.fetchval(
            "SELECT channel_id FROM counter_channels WHERE guild_id = $1 AND option = $2", ctx.guild.id, option
        ):
            counter = self.bot.get_channel(counter_id)
            if counter:
                return await ctx.warn(f"The `{option}` counter is already being displayed on {counter.mention}")

        try:
            if channel in ("text", "announce"):
                channel = await ctx.guild.create_text_channel(
                    name=(
                        f"Members: {humanize.comma(len(ctx.guild.members))}"
                        if option == "members"
                        else f"Boosts: {humanize.comma(ctx.guild.premium_subscription_count)}"
                    ),
                    news=(channel == "announce"),
                    overwrites={
                        ctx.guild.default_role: discord.PermissionOverwrite(
                            view_channel=True,
                            read_message_history=True,
                            send_messages=False,
                        )
                    },
                )
            else:
                if not channel in ("stage"):
                    channel = await getattr(ctx.guild, ("create_voice_channel" if channel == "voice" else "create_category"))(
                        name=(
                            f"Members: {humanize.comma(len(ctx.guild.members))}"
                            if option == "members"
                            else f"Boosts: {humanize.comma(ctx.guild.premium_subscription_count)}"
                        ),
                        overwrites={ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=False)},
                    )
                else:
                    channel = await ctx.guild.create_stage_channel(
                        name=(
                            f"Members: {humanize.comma(len(ctx.guild.members))}"
                            if option == "members"
                            else f"Boosts: {humanize.comma(ctx.guild.premium_subscription_count)}"
                        ),
                        topic=f"This channel displays the number of {option} in the server",
                        overwrites={ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=False)},
                    )

        except Exception as error:
            return await ctx.warn(f"Couldn't create the **counter channel**\n>>> {error}")

        await self.bot.db.execute(
            "INSERT INTO counter_channels (guild_id, channel_id, option, last_updated) VALUES($1, $2, $3, $4) ON CONFLICT(guild_id, option) DO UPDATE"
            " SET channel_id = $2",
            ctx.guild.id,
            channel.id,
            option,
            channel.created_at,
        )
        await ctx.approve(f"Created a **counter** bound to [**{channel.mention}**]({channel.jump_url}) for `{option}`")

    @counter.command(
        name="remove",
        usage="(channel)",
        example="#Members",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_channels=True)
    async def counter_remove(
        self, ctx: wock.Context, channel: discord.VoiceChannel | discord.TextChannel | discord.Thread | discord.CategoryChannel | discord.StageChannel
    ):
        """Remove a counter channel"""

        try:
            await self.bot.db.execute(
                "DELETE FROM counter_channels WHERE guild_id = $1 AND channel_id = $2",
                ctx.guild.id,
                channel.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"[**{channel.name}**]({channel.jump_url}) isn't a **counter channel**")
        else:
            await ctx.approve(f"[**{channel.name}**]({channel.jump_url}) is no longer a **counter channel**")

            with contextlib.suppress(discord.HTTPException):
                await channel.delete()

    @counter.command(
        name="reset",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_channels=True)
    async def counter_reset(self, ctx: wock.Context):
        """Reset all counter channels"""

        await ctx.prompt("Are you sure you want to remove all **counter channels**?")

        try:
            counter_channels = await self.bot.db.execute(
                "DELETE FROM counter_channels WHERE guild_id = $1 RETURNING channel_id",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No **counter channels** have been set up")
        else:
            await ctx.approve("Removed all **counter channels**")

            for channel_id in counter_channels:
                if channel := self.bot.get_channel(channel_id):
                    with contextlib.suppress(discord.HTTPException):
                        await channel.delete()

    @counter.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_channels=True)
    async def counter_list(self, ctx: wock.Context):
        """View all counter channels"""

        channels = [
            f"[**{self.bot.get_channel(row.get('channel_id')).mention}**]({self.bot.get_channel(row.get('channel_id')).jump_url})"
            f" (`{row.get('option')}`)"
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id, option FROM counter_channels WHERE guild_id = $1",
                ctx.guild.id,
            )
            if self.bot.get_channel(row.get("channel_id"))
        ]
        if not channels:
            return await ctx.warn("No **counter channels** have been set up")

        await ctx.paginate(
            discord.Embed(
                title="Counter Channels",
                description=channels,
            )
        )

    @commands.group(
        name="welcome",
        usage="(subcommand) <args>",
        example="add #chat Hi {user.mention} <3",
        aliases=["welc"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx: wock.Context):
        """Set up welcome messages in one or multiple channels"""

        await ctx.send_help()

    @welcome.command(
        name="add",
        usage="(channel) (message)",
        example="#chat Hi {user.mention} <3",
        parameters={
            "self_destruct": {
                "converter": int,
                "description": "The amount of seconds to wait before deleting the message",
                "minimum": 6,
                "maximum": 120,
                "aliases": ["delete_after", "delete"],
            }
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_add(
        self,
        ctx: wock.Context,
        channel: discord.TextChannel | discord.Thread,
        *,
        message: wock.EmbedScriptValidator,
    ):
        """Add a welcome message for a channel"""

        self_destruct = ctx.parameters.get("self_destruct")

        try:
            await self.bot.db.execute(
                "INSERT INTO welcome_channels VALUES($1, $2, $3, $4)",
                ctx.guild.id,
                channel.id,
                str(message),
                self_destruct,
            )
        except:
            await ctx.warn(f"There is already a **welcome message** for {channel.mention}")
        else:
            await ctx.approve(
                f"Created {message.type(bold=False)} **welcome message** for {channel.mention}"
                + (f"\n> Which will self destruct after {functions.plural(self_destruct, bold=True):second}" if self_destruct else "")
            )

    @welcome.command(
        name="remove",
        usage="(channel)",
        example="#chat",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_remove(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread | discord.Thread):
        """Remove a welcome message for a channel"""

        try:
            await self.bot.db.execute(
                "DELETE FROM welcome_channels WHERE guild_id = $1 AND channel_id = $2",
                ctx.guild.id,
                channel.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There isn't a **welcome message** for {channel.mention}")
        else:
            await ctx.approve(f"Removed the **welcome message** for {channel.mention}")

    @welcome.command(
        name="view",
        usage="(channel)",
        example="#chat",
        aliases=["check", "test", "emit"],
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_view(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread):
        """View a welcome message for a channel"""

        data = await self.bot.db.fetchrow(
            "SELECT message, self_destruct FROM welcome_channels WHERE guild_id = $1 AND channel_id = $2",
            ctx.guild.id,
            channel.id,
        )
        if not data:
            return await ctx.warn(f"There isn't a **welcome message** for {channel.mention}")

        message = data.get("message")
        self_destruct = data.get("self_destruct")

        await wock.EmbedScript(message).send(
            ctx.channel,
            bot=self.bot,
            guild=ctx.guild,
            channel=ctx.channel,
            user=ctx.author,
            delete_after=self_destruct,
        )

    @welcome.command(
        name="reset",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_reset(self, ctx: wock.Context):
        """Reset all welcome channels"""

        await ctx.prompt("Are you sure you want to remove all **welcome channels**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM welcome_channels WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No **welcome channels** have been set up")
        else:
            await ctx.approve("Removed all **welcome channels**")

    @welcome.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_list(self, ctx: wock.Context):
        """View all welcome channels"""

        channels = [
            self.bot.get_channel(row.get("channel_id")).mention
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id FROM welcome_channels WHERE guild_id = $1",
                ctx.guild.id,
            )
            if self.bot.get_channel(row.get("channel_id"))
        ]
        if not channels:
            return await ctx.warn("No **welcome channels** have been set up")

        await ctx.paginate(
            discord.Embed(
                title="Welcome Channels",
                description=channels,
            )
        )

    @commands.group(
        name="goodbye",
        usage="(subcommand) <args>",
        example="add #chat Bye {user.mention} </3",
        aliases=["bye"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye(self, ctx: wock.Context):
        """Set up goodbye messages in one or multiple channels"""

        await ctx.send_help()

    @goodbye.command(
        name="add",
        usage="(channel) (message)",
        example="#chat Bye {user.mention} </3",
        parameters={
            "self_destruct": {
                "converter": int,
                "description": "The amount of seconds to wait before deleting the message",
                "minimum": 6,
                "maximum": 120,
                "aliases": ["delete_after", "delete"],
            }
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_add(
        self,
        ctx: wock.Context,
        channel: discord.TextChannel | discord.Thread,
        *,
        message: wock.EmbedScriptValidator,
    ):
        """Add a goodbye message for a channel"""

        self_destruct = ctx.parameters.get("self_destruct")

        try:
            await self.bot.db.execute(
                "INSERT INTO goodbye_channels VALUES($1, $2, $3, $4)",
                ctx.guild.id,
                channel.id,
                str(message),
                self_destruct,
            )
        except:
            await ctx.warn(f"There is already a **goodbye message** for {channel.mention}")
        else:
            await ctx.approve(
                f"Created {message.type(bold=False)} **goodbye message** for {channel.mention}"
                + (f"\n> Which will self destruct after {functions.plural(self_destruct, bold=True):second}" if self_destruct else "")
            )

    @goodbye.command(
        name="remove",
        usage="(channel)",
        example="#chat",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_remove(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread):
        """Remove a goodbye message for a channel"""

        try:
            await self.bot.db.execute(
                "DELETE FROM goodbye_channels WHERE guild_id = $1 AND channel_id = $2",
                ctx.guild.id,
                channel.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There isn't a **goodbye message** for {channel.mention}")
        else:
            await ctx.approve(f"Removed the **goodbye message** for {channel.mention}")

    @goodbye.command(
        name="view",
        usage="(channel)",
        example="#chat",
        aliases=["check", "test", "emit"],
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_view(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread):
        """View a goodbye message for a channel"""

        data = await self.bot.db.fetchrow(
            "SELECT message, self_destruct FROM goodbye_channels WHERE guild_id = $1 AND channel_id = $2",
            ctx.guild.id,
            channel.id,
        )
        if not data:
            return await ctx.warn(f"There isn't a **goodbye message** for {channel.mention}")

        message = data.get("message")
        self_destruct = data.get("self_destruct")

        await wock.EmbedScript(message).send(
            ctx.channel,
            bot=self.bot,
            guild=ctx.guild,
            channel=ctx.channel,
            user=ctx.author,
            delete_after=self_destruct,
        )

    @goodbye.command(
        name="reset",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_reset(self, ctx: wock.Context):
        """Reset all goodbye channels"""

        await ctx.prompt("Are you sure you want to remove all **goodbye channels**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM goodbye_channels WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No **goodbye channels** have been set up")
        else:
            await ctx.approve("Removed all **goodbye channels**")

    @goodbye.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_list(self, ctx: wock.Context):
        """View all goodbye channels"""

        channels = [
            self.bot.get_channel(row.get("channel_id")).mention
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id FROM goodbye_channels WHERE guild_id = $1",
                ctx.guild.id,
            )
            if self.bot.get_channel(row.get("channel_id"))
        ]
        if not channels:
            return await ctx.warn("No **goodbye channels** have been set up")

        await ctx.paginate(
            discord.Embed(
                title="Goodbye Channels",
                description=channels,
            )
        )

    @commands.group(
        name="boost",
        usage="(subcommand) <args>",
        example="add #chat Thx {user.mention} :3",
        aliases=["bst"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def boost(self, ctx: wock.Context):
        """Set up boost messages in one or multiple channels"""

        await ctx.send_help()

    @boost.command(
        name="add",
        usage="(channel) (message)",
        example="#chat Thx {user.mention} :3",
        parameters={
            "self_destruct": {
                "converter": int,
                "description": "The amount of seconds to wait before deleting the message",
                "minimum": 6,
                "maximum": 120,
                "aliases": ["delete_after", "delete"],
            }
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_add(
        self,
        ctx: wock.Context,
        channel: discord.TextChannel | discord.Thread,
        *,
        message: wock.EmbedScriptValidator,
    ):
        """Add a boost message for a channel"""

        self_destruct = ctx.parameters.get("self_destruct")

        try:
            await self.bot.db.execute(
                "INSERT INTO boost_channels VALUES($1, $2, $3, $4)",
                ctx.guild.id,
                channel.id,
                str(message),
                self_destruct,
            )
        except:
            await ctx.warn(f"There is already a **boost message** for {channel.mention}")
        else:
            await ctx.approve(
                f"Created {message.type(bold=False)} **boost message** for {channel.mention}"
                + (f"\n> Which will self destruct after {functions.plural(self_destruct, bold=True):second}" if self_destruct else "")
            )

    @boost.command(
        name="remove",
        usage="(channel)",
        example="#chat",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_remove(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread):
        """Remove a boost message for a channel"""

        try:
            await self.bot.db.execute(
                "DELETE FROM boost_channels WHERE guild_id = $1 AND channel_id = $2",
                ctx.guild.id,
                channel.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There isn't a **boost message** for {channel.mention}")
        else:
            await ctx.approve(f"Removed the **boost message** for {channel.mention}")

    @boost.command(
        name="view",
        usage="(channel)",
        example="#chat",
        aliases=["check", "test", "emit"],
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_view(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread):
        """View a boost message for a channel"""

        data = await self.bot.db.fetchrow(
            "SELECT message, self_destruct FROM boost_channels WHERE guild_id = $1 AND channel_id = $2",
            ctx.guild.id,
            channel.id,
        )
        if not data:
            return await ctx.warn(f"There isn't a **boost message** for {channel.mention}")

        message = data.get("message")
        self_destruct = data.get("self_destruct")

        await wock.EmbedScript(message).send(
            ctx.channel,
            bot=self.bot,
            guild=ctx.guild,
            channel=ctx.channel,
            user=ctx.author,
            delete_after=self_destruct,
        )

    @boost.command(
        name="reset",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_reset(self, ctx: wock.Context):
        """Reset all boost channels"""

        await ctx.prompt("Are you sure you want to remove all **boost channels**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM boost_channels WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No **boost channels** have been set up")
        else:
            await ctx.approve("Removed all **boost channels**")

    @boost.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_list(self, ctx: wock.Context):
        """View all boost channels"""

        channels = [
            self.bot.get_channel(row.get("channel_id")).mention
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id FROM boost_channels WHERE guild_id = $1",
                ctx.guild.id,
            )
            if self.bot.get_channel(row.get("channel_id"))
        ]
        if not channels:
            return await ctx.warn("No **boost channels** have been set up")

        await ctx.paginate(
            discord.Embed(
                title="Boost Channels",
                description=channels,
            )
        )

    @commands.group(
        name="sticky",
        usage="(subcommand) <args>",
        example="add #selfie Oh look at me!",
        aliases=["stickymessage", "sm"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def sticky(self, ctx: wock.Context):
        """Set up sticky messages in one or multiple channels"""

        await ctx.send_help()

    @sticky.command(
        name="add",
        usage="(channel) (message)",
        example="#selfie Oh look at me!",
        parameters={
            "schedule": {
                "converter": str,
                "description": "Waits until chat is inactive to repost the message",
                "aliases": ["timer", "time", "activity"],
            }
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_guild=True)
    async def sticky_add(
        self,
        ctx: wock.Context,
        channel: discord.TextChannel | discord.Thread,
        *,
        message: wock.EmbedScriptValidator,
    ):
        """Add a sticky message for a channel"""

        if schedule := ctx.parameters.get("schedule"):
            schedule = await wock.TimeConverter().convert(ctx, schedule)
            if schedule.seconds < 30 or schedule.seconds > 3600:
                return await ctx.warn("The **activity schedule** must be between **30 seconds** and **1 hour**")
        else:
            schedule = None

        _message = await message.send(
            channel,
            bot=self.bot,
            guild=ctx.guild,
            channel=channel,
            user=ctx.author,
        )

        try:
            await self.bot.db.execute(
                "INSERT INTO sticky_messages (guild_id, channel_id, message_id, message, schedule) VALUES ($1, $2, $3, $4, $5)",
                ctx.guild.id,
                channel.id,
                _message.id,
                str(message),
                schedule.seconds if schedule else None,
            )
        except:
            await ctx.warn(f"There is already a **sticky message** for {channel.mention}")
        else:
            await ctx.approve(
                f"Created {message.type(bold=False)} [**sticky message**]({_message.jump_url}) for {channel.mention}"
                + (f" with an **activity schedule** of **{schedule}**" if schedule else "")
            )

    @sticky.command(
        name="remove",
        usage="(channel)",
        example="#selfie",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_guild=True)
    async def sticky_remove(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread):
        """Remove a sticky message for a channel"""

        try:
            await self.bot.db.execute(
                "DELETE FROM sticky_messages WHERE guild_id = $1 AND channel_id = $2",
                ctx.guild.id,
                channel.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"There isn't a **sticky message** for {channel.mention}")
        else:
            await ctx.approve(f"Removed the **sticky message** for {channel.mention}")

    @sticky.command(
        name="view",
        usage="(channel)",
        example="#selfie",
        aliases=["check", "test", "emit"],
    )
    @commands.has_permissions(manage_guild=True)
    async def sticky_view(self, ctx: wock.Context, channel: discord.TextChannel | discord.Thread):
        """View a sticky message for a channel"""

        data = await self.bot.db.fetchrow(
            "SELECT message FROM sticky_messages WHERE guild_id = $1 AND channel_id = $2",
            ctx.guild.id,
            channel.id,
        )
        if not data:
            return await ctx.warn(f"There isn't a **sticky message** for {channel.mention}")

        message = data.get("message")

        await wock.EmbedScript(message).send(
            ctx.channel,
            bot=self.bot,
            guild=ctx.guild,
            channel=ctx.channel,
            user=ctx.author,
        )

    @sticky.command(
        name="reset",
        aliases=["clear"],
    )
    @commands.has_permissions(manage_guild=True)
    async def sticky_reset(self, ctx: wock.Context):
        """Reset all sticky messages"""

        await ctx.prompt("Are you sure you want to remove all **sticky messages**?")

        try:
            await self.bot.db.execute(
                "DELETE FROM sticky_messages WHERE guild_id = $1",
                ctx.guild.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn("No **sticky messages** have been set up")
        else:
            await ctx.approve("Removed all **sticky messages**")

    @sticky.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_guild=True)
    async def sticky_list(self, ctx: wock.Context):
        """View all sticky messages"""

        messages = [
            f"{channel.mention} - [`{row['message_id']}`]({channel.get_partial_message(row['message_id']).jump_url})"
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id, message_id FROM sticky_messages WHERE guild_id = $1",
                ctx.guild.id,
            )
            if (channel := self.bot.get_channel(row.get("channel_id")))
        ]
        if not messages:
            return await ctx.warn("No **sticky messages** have been set up")

        await ctx.paginate(
            discord.Embed(
                title="Sticky Messages",
                description=messages,
            )
        )

    @commands.group(
        name="youtube",
        usage="(query)",
        example="Gas price increase",
        aliases=["yt"],
        invoke_without_command=True,
    )
    async def youtube(self, ctx: wock.Context, *, query: str):
        """Search for something on YouTube"""

        async with ctx.typing():
            response = await self.bot.session.get(
                "https://dev.wock.cloud/youtube/search",
                params=dict(query=query),
                headers=dict(
                    Authorization=self.bot.config["api"].get("wock"),
                ),
            )
            data = await response.json()

            if not data.get("results"):
                return await ctx.warn(f"Couldn't find any results for **{query}**")

        result = data["results"][0]
        await ctx.reply(result.get("url"))

    @youtube.command(
        name="add",
        usage="(channel) (channel URL)",
        example="#notis @MrBeast",
        parameters={
            "message": {
                "converter": str,
                "description": "The message to send when a video is posted",
                "aliases": ["embed", "msg"],
            }
        },
        aliases=["create"],
    )
    @commands.has_permissions(manage_guild=True)
    async def youtube_add(
        self,
        ctx: wock.Context,
        channel: discord.TextChannel | discord.Thread,
        *,
        youtube_channel: wock.YouTubeChannel,
    ):
        """Send post notifications for a YouTube channel"""

        try:
            await self.bot.db.execute(
                "INSERT INTO youtube_channels VALUES($1, $2, $3, $4, $5)",
                ctx.guild.id,
                channel.id,
                youtube_channel["id"],
                youtube_channel["name"],
                (str(ctx.parameters.get("message")) if ctx.parameters.get("message") else None),
            )
        except:
            await ctx.warn(f"Already sending **notifications** for [**{youtube_channel['name']}**]({youtube_channel['url']}) in {channel.mention}")
        else:
            await self.bot.session.post(
                "https://webhook.wock.cloud/youtube/subscribe",
                params=dict(channel_id=youtube_channel["id"]),
                headers=dict(Authorization=self.bot.config.get("secret")),
            )
            await ctx.approve(f"Now sending **notifications** for [**{youtube_channel['name']}**]({youtube_channel['url']}) in {channel.mention}")

    @youtube.command(
        name="remove",
        usage="(channel) (channel URL)",
        example="#notis @MrBeast",
        aliases=["delete", "del", "rm"],
    )
    @commands.has_permissions(manage_guild=True)
    async def youtube_remove(
        self,
        ctx: wock.Context,
        channel: discord.TextChannel | discord.Thread,
        *,
        youtube_channel: wock.YouTubeChannel,
    ):
        """Stop sending post notifications for a YouTube channel"""

        try:
            await self.bot.db.execute(
                "DELETE FROM youtube_channels WHERE guild_id = $1 AND channel_id = $2 AND youtube_id = $3",
                ctx.guild.id,
                channel.id,
                youtube_channel["id"],
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"Not sending **notifications** for [**{youtube_channel['name']}**]({youtube_channel['url']}) in {channel.mention}")
        else:
            await ctx.approve(
                f"No longer sending **notifications** for [**{youtube_channel['name']}**]({youtube_channel['url']}) in {channel.mention}"
            )

    @youtube.command(
        name="list",
        aliases=["show", "all"],
    )
    @commands.has_permissions(manage_guild=True)
    async def youtube_list(self, ctx: wock.Context):
        """View all YouTube channel notifications"""

        channels = [
            f"[**{row['youtube_name']}**](https://www.youtube.com/channel/{row['youtube_id']}) in {self.bot.get_channel(row['channel_id']).mention}"
            async for row in self.bot.db.fetchiter(
                "SELECT channel_id, youtube_id, youtube_name FROM youtube_channels WHERE guild_id = $1",
                ctx.guild.id,
            )
            if self.bot.get_channel(row.get("channel_id"))
        ]
        if not channels:
            return await ctx.warn("No **YouTube channels** are being **notified**")

        await ctx.paginate(
            discord.Embed(
                title="YouTube Notifications",
                description=channels,
            )
        )

    @commands.group(
        name="reskin",
        usage="(subcommand) <args>",
        example="name Destroy Lonely",
        invoke_without_command=True,
    )
    async def reskin(self, ctx: wock.Context):
        """Customize the bot's appearance"""

        await ctx.send_help()

    @reskin.command(
        name="setup",
        aliases=["webhooks"],
    )
    @checks.donator()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 600, commands.BucketType.guild)
    async def reskin_setup(self, ctx: wock.Context):
        """Set up the reskin webhooks"""

        await ctx.prompt("Are you sure you want to set up the **reskin webhooks**?\n> This will create a webhook in **every channel** in the server!")

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        configuration["status"] = True
        webhooks = configuration.get("webhooks", {})

        async with ctx.typing():
            tasks = list()
            for channel in ctx.guild.text_channels:
                if any(ext in channel.name.lower() for ext in ("ticket", "log", "discrim", "bleed")) or (
                    channel.category
                    and any(ext in channel.category.name.lower() for ext in ("tickets", "logs", "pfps", "pfp", "icons", "icon", "banners", "banner"))
                ):
                    continue

                tasks.append(functions.configure_reskin(self.bot, channel, webhooks))

            gathered = await asyncio.gather(*tasks)
            created = [webhook for webhook in gathered if webhook]

        configuration["webhooks"] = webhooks
        await self.bot.db.update_config(ctx.guild.id, "reskin", configuration)

        if not created:
            return await ctx.warn("No **webhooks** were created" + (str(gathered) if ctx.author.id in self.bot.owner_ids and any(gathered) else ""))

        await ctx.approve(f"The **reskin webhooks** have been set across {functions.plural(created, bold=True):channel}")

    @reskin.command(
        name="disable",
    )
    @commands.has_permissions(manage_guild=True)
    async def reskin_disable(self, ctx: wock.Context):
        """Disable the reskin webhooks"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn("Reskin webhooks are already **disabled**")

        configuration["status"] = False
        await self.bot.db.update_config(ctx.guild.id, "reskin", configuration)
        await ctx.approve("Disabled **reskin** across the server")

    @reskin.group(
        name="server",
        usage="(subcommand) <args>",
        example="name opium bot",
        aliases=["event"],
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def reskin_server(self, ctx: wock.Context):
        """Customize the appearance of events"""

        await ctx.send_help()

    @reskin_server.command(
        name="name",
        usage="(username)",
        example="Destroy Lonely",
        aliases=["username"],
    )
    @checks.donator()
    @commands.has_permissions(manage_guild=True)
    async def reskin_server_name(self, ctx: wock.Context, *, username: str):
        """Change the server reskin username"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn(f"Reskin webhooks are **disabled**\n> Use `{ctx.prefix}reskin setup` to set them up")

        if len(username) > 32:
            return await ctx.warn("Your name can't be longer than **32 characters**")

        configuration["username"] = username
        await self.bot.db.update_config(ctx.guild.id, "reskin", configuration)
        await wock.cache.delete_match(f"reskin:channel:{ctx.guild.id}:*")
        await ctx.approve(f"Set the **server reskin username** to **{username}**")

    @reskin_server.command(
        name="avatar",
        usage="(image)",
        example="https://i.imgur.com/0X0X0X0.png",
        aliases=["icon", "av"],
    )
    @checks.donator()
    @commands.has_permissions(manage_guild=True)
    async def reskin_server_avatar(self, ctx: wock.Context, *, image: wock.ImageFinderStrict = None):
        """Change the server reskin avatar"""

        image = image or await wock.ImageFinderStrict.search(ctx)

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn(f"Reskin webhooks are **disabled**\n> Use `{ctx.prefix}reskin setup` to set them up")

        configuration["avatar_url"] = image
        await self.bot.db.update_config(ctx.guild.id, "reskin", configuration)
        await wock.cache.delete_match(f"reskin:channel:{ctx.guild.id}:*")
        await ctx.approve(f"Changed the **server reskin avatar** to [**image**]({image})")

    @reskin_server.command(
        name="remove",
        aliases=["delete", "reset"],
    )
    @commands.has_permissions(manage_guild=True)
    async def reskin_server_remove(self, ctx: wock.Context):
        """Remove the server reskin"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not (configuration.get("username") or configuration.get("avatar_url")):
            return await ctx.warn("The **server reskin** hasn't been set")

        configuration["username"] = None
        configuration["avatar_url"] = None
        configuration["colors"] = {}
        configuration["emojis"] = {}
        await self.bot.db.update_config(ctx.guild.id, "reskin", configuration)
        await wock.cache.delete_match(f"reskin:channel:{ctx.guild.id}:*")
        await ctx.approve("Removed the **server reskin**")

    @reskin.command(
        name="name",
        usage="(username)",
        example="Destroy Lonely",
        aliases=["username"],
    )
    @checks.donator()
    async def reskin_name(self, ctx: wock.Context, *, username: str):
        """Change your personal reskin username"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn(f"Reskin webhooks are **disabled**\n> Use `{ctx.prefix}reskin setup` to set them up")

        if len(username) > 32:
            return await ctx.warn("Your name can't be longer than **32 characters**")

        await self.bot.db.execute(
            "INSERT INTO reskin (user_id, username) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET username = $2",
            ctx.author.id,
            username,
        )
        await ctx.approve(f"Changed your **reskin username** to **{username}**")

    @reskin.command(
        name="avatar",
        usage="(image)",
        example="https://i.imgur.com/0X0X0X0.png",
        aliases=["icon", "av"],
    )
    @checks.donator()
    async def reskin_avatar(self, ctx: wock.Context, *, image: wock.ImageFinderStrict = None):
        """Change your personal reskin avatar"""

        image = image or await wock.ImageFinderStrict.search(ctx)

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn(f"Reskin webhooks are **disabled**\n> Use `{ctx.prefix}reskin setup` to set them up")

        await self.bot.db.execute(
            "INSERT INTO reskin (user_id, avatar_url) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET avatar_url = $2",
            ctx.author.id,
            image,
        )
        await ctx.approve(f"Changed your **reskin avatar** to [**image**]({image})")

    @reskin.group(
        name="color",
        usage="(option) (color)",
        example="main #BBAAEE",
        aliases=["colour"],
        invoke_without_command=True,
    )
    @checks.donator()
    async def reskin_color(
        self,
        ctx: wock.Context,
        option: Literal["main", "approve", "warn", "search", "load", "all"],
        color: wock.Color,
    ):
        """Change your personal reskin embed colors"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn(f"Reskin webhooks are **disabled**\n> Use `{ctx.prefix}reskin setup` to set them up")

        colors = await self.bot.db.fetchval("SELECT colors FROM reskin WHERE user_id = $1", ctx.author.id) or {}
        if option == "all":
            colors = {
                "main": color.value,
                "approve": color.value,
                "warn": color.value,
                "search": color.value,
                "load": color.value,
            }
        else:
            colors[option] = color.value

        await self.bot.db.execute(
            "INSERT INTO reskin (user_id, colors) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET colors = $2",
            ctx.author.id,
            colors,
        )
        await ctx.approve(
            f"Changed your **reskin color** for " + (f"**{option}** to `{color}`" if option != "all" else f"all **embeds** to `{color}`")
        )

    @reskin_color.command(
        name="reset",
        usage="(option)",
        example="all",
        aliases=["clear"],
    )
    @checks.donator()
    async def reskin_color_reset(
        self,
        ctx: wock.Context,
        option: Literal["main", "approve", "warn", "search", "load", "all"],
    ):
        """Reset your personal reskin embed colors"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn(f"Reskin webhooks are **disabled**\n> Use `{ctx.prefix}reskin setup` to set them up")

        colors = await self.bot.db.fetchval("SELECT colors FROM reskin WHERE user_id = $1", ctx.author.id) or {}
        if option == "all":
            colors = {}
        else:
            colors.pop(option, None)

        await self.bot.db.execute(
            "INSERT INTO reskin (user_id, colors) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET colors = $2",
            ctx.author.id,
            colors,
        )
        await ctx.approve(f"Reset your **reskin color** for " + (f"**{option}**" if option != "all" else f"all **embeds**"))

    @reskin.group(
        name="emoji",
        usage="(option) (emoji)",
        example="approve ✨",
        invoke_without_command=True,
    )
    @checks.donator()
    async def reskin_emoji(
        self,
        ctx: wock.Context,
        option: Literal["approve", "warn", "search", "load", "all"],
        emoji: str,
    ):
        """Change your personal reskin embed emojis"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn(f"Reskin webhooks are **disabled**\n> Use `{ctx.prefix}reskin setup` to set them up")

        try:
            await ctx.message.add_reaction(emoji)
        except discord.HTTPException:
            return await ctx.warn(f"**{emoji}** is not a valid emoji")

        emojis = await self.bot.db.fetchval("SELECT emojis FROM reskin WHERE user_id = $1", ctx.author.id) or {}
        if option == "all":
            emojis = {
                "approve": emoji,
                "warn": emoji,
                "search": emoji,
                "load": emoji,
            }
        else:
            emojis[option] = emoji

        await self.bot.db.execute(
            "INSERT INTO reskin (user_id, emojis) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET emojis = $2",
            ctx.author.id,
            emojis,
        )
        await ctx.approve(f"Changed your **reskin emoji** for " + (f"**{option}** to {emoji}" if option != "all" else f"all **embeds** to {emoji}"))

    @reskin_emoji.command(
        name="reset",
        usage="(option)",
        example="all",
        aliases=["clear"],
    )
    @checks.donator()
    async def reskin_emoji_reset(
        self,
        ctx: wock.Context,
        option: Literal["approve", "warn", "search", "load", "all"],
    ):
        """Reset your personal reskin embed emojis"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "reskin") or {}
        if not configuration.get("status"):
            return await ctx.warn(f"Reskin webhooks are **disabled**\n> Use `{ctx.prefix}reskin setup` to set them up")

        emojis = await self.bot.db.fetchval("SELECT emojis FROM reskin WHERE user_id = $1", ctx.author.id) or {}
        if option == "all":
            emojis = {}
        else:
            emojis.pop(option, None)

        await self.bot.db.execute(
            "INSERT INTO reskin (user_id, emojis) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET emojis = $2",
            ctx.author.id,
            emojis,
        )
        await ctx.approve(f"Reset your **reskin emoji** for " + (f"**{option}**" if option != "all" else f"all **embeds**"))

    @reskin.command(
        name="remove",
        aliases=["delete", "reset"],
    )
    @checks.donator()
    async def reskin_remove(self, ctx: wock.Context):
        """Remove your personal reskin"""

        try:
            await self.bot.db.execute("DELETE FROM reskin WHERE user_id = $1", ctx.author.id)
        except:
            await ctx.warn("You haven't set a **reskin**")
        else:
            await ctx.approve("Removed your **reskin**")


async def setup(bot: wock.wockSuper):
    await bot.add_cog(servers(bot))
