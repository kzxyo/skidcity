from asyncio import (
    TimeoutError, 
    ensure_future, 
    gather, 
    sleep, 
    wait_for
)

from contextlib import suppress
from datetime import datetime as Date
from datetime import timedelta
from itertools import chain
from time import time
from typing_extensions import NoReturn

from typing import (
    AsyncIterator, 
    Literal, 
    Optional, 
    Union
)

from discord import (
    AuditLogAction, 
    AuditLogEntry, 
    Embed, 
    Emoji, 
    Forbidden,
    Member as _Member, 
    PartialEmoji, 
    PermissionOverwrite, 
    Permissions,
    StickerItem, 
    TextChannel, 
    Thread, 
    VoiceChannel, 
    utils
)

from discord.errors import HTTPException
from discord.ext import tasks

from discord.ext.commands import (
    Author, 
    bot_has_permissions,
    BotMissingPermissions, 
    BucketType,
    Cog, 
    Greedy, 
    command as Command,
    CommandError,
    cooldown,
    group as Group,
    has_permissions, 
    is_guild_owner,
    max_concurrency
)

from pymysql.err import IntegrityError
from utilities import expressions

from utilities.vile import (
    Attachment, 
    Color, 
    Context, 
    Member, 
    Message, 
    Role,
    Timespan, 
    User, 
    VileBot, 
    confirm, 
    fmtseconds,
    strip_flags
)

import re


TUPLE = ()
DICT = { }


class Moderation(Cog):
    def __init__(self, bot: VileBot) -> NoReturn:
        self.bot = bot
        self.hidden = False
        self.ignore_lockdown = { }
        self.tasks = {
            "unban_all": { },
            "role": { },
            "purge": { }
        }
        
    
    async def cog_load(self) -> NoReturn:
        """
        An asynchronous setup function for the Cog
        """

        self.do_scheduled_actions.start()
        
        
    async def cog_unload(self) -> NoReturn:
        """
        The opposite of cog_load
        """

        self.do_scheduled_actions.cancel()
        
        
        
    async def cog_check(self: "Moderation", ctx: Context) -> bool:
        """
        A check for every Moderation command
        """
        
        if ctx.me.guild_permissions.administrator is False:
            raise BotMissingPermissions(("administrator",))
            
        return True
    

    async def find_stickers(
        self: "Moderation", 
        channel: TextChannel, 
        limit: int = 100
    ) -> AsyncIterator[StickerItem]:
        """
        Search channel history for stickers
        """

        async for message in channel.history(limit=limit or 100):
            if message.stickers:
                for sticker in message.stickers:
                    yield sticker

        
    async def log_history(
        self: "Moderation", 
        guild_id: int, 
        moderator_id: int, 
        member_id: int, 
        type: str, 
        reason: str = "No reason provided"
    ) -> NoReturn:
        """
        Log a moderation action
        """
        
        case_id = await self.bot.db.fetchval(
            "SELECT MAX(case_id) FROM moderation_history WHERE guild_id = %s;",
            guild_id
        ) or 0
        
        # I couldn't make AUTO_INCREMENT work
        # even when the same exact table structure worked for a friend
        
        with suppress(IntegrityError):
            await self.bot.db.execute(
                "INSERT INTO moderation_history (guild_id, moderator_id, member_id, type, reason, created_on, case_id) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                guild_id, moderator_id, member_id, type, reason, Date.now(), case_id+1
            )
            
    
    async def notify(
        self: "Moderation", 
        member: Member,
        title: str,
        message: str,
        guild: Member,
        moderator: Member,
        reason: str = "No reason provided"
    ):
        """
        Notify the member of a Moderation action
        """
        
        embed = (
            Embed(
                color=self.bot.color,
                title=title,
                description=f"> {message} {guild.name}",
                timestamp=Date.now()
            )
            .set_author(
                name=guild.name,
                icon_url=guild.icon
            )
            .add_field(
                name="Moderator",
                value=str(moderator)
            )
            .add_field(
                name="Reason",
                value=reason
            )
            .set_thumbnail(
                url=self.bot.user.display_avatar
            )
            .set_footer(
                text="Contact a staff member if you wish to dispute this punishment"
            )
        )
        
        return await member.send(embed=embed)
            
    
    @tasks.loop(seconds=10)        
    async def do_scheduled_actions(self):
        """
        Do scheduled actions
        """
        
        await self.bot.wait_until_ready()
        
        for guild_id, user_id, unban_on in await self.bot.db.execute("SELECT guild_id, user_id, unban_on FROM temporary_bans;"):
            await sleep(1e-3)
            
            if Date.now() < unban_on:
                return

            if not (guild := self.bot.get_guild(guild_id)):
                return
                
            if guild.me.guild_permissions.ban_members is False:
                return

            async for entry in guild.bans():
                await sleep(1e-3)

                if entry.user.id == user_id:
                    await guild.unban(
                        entry.user, 
                        reason=f"{self.bot.user.name.title()} Moderation: Temporary ban has been lifted"
                    )
                    
                    await self.bot.db.execute(
                        "DELETE FROM temporary_bans WHERE guild_id = %s AND user_id = %s;",
                        guild_id, user_id
                    )

                    break

            

        async def lift_punishment(punishment: str) -> NoReturn:
            for guild_id, user_id, punishment_expiration in await self.bot.db.execute(f"SELECT * FROM {'jailed' if punishment == 'jail' else 'muted'}_user;"):
                await sleep(1e-3)
                
                if Date.now() < punishment_expiration:
                    return

                if not (guild := self.bot.get_guild(guild_id)):
                    return

                if not (member := guild.get_member(user_id)):
                    return

                if guild.me.guild_permissions.administrator is False:
                    return

                if not (
                    punishment_role_id := await self.bot.db.fetchval(
                        f"SELECT {'jail' if punishment == 'jail' else 'mute'}_role_id FROM guild_settings WHERE guild_id = %s;", 
                        guild_id
                )):
                    return

                if not (punishment_role := guild.get_role(punishment_role_id)):
                    return

                if punishment_role not in member.roles:
                    return

                await member.remove_roles(
                    punishment_role,
                    reason=f"{self.bot.user.name.title()} Moderation: {punishment.capitalize()} has been lifted"
                )

                taken_roles = await self.bot.db.fetch(
                    "SELECT role_id FROM taken_roles WHERE guild_id = %s AND user_id = %s;",
                    guild_id, user_id
                )

                await self.bot.db.execute(
                    f"""
                    DELETE FROM {'jailed' if punishment == 'jail' else 'muted'}_user WHERE guild_id = %s AND user_id = %s;
                    DELETE FROM taken_roles WHERE guild_id = %s AND user_id = %s;
                    """,
                    guild_id, user_id,
                    guild_id, user_id
                )

                await member.add_roles(
                    *(guild.get_role(role_id) for role_id in taken_roles if guild.get_role(role_id) and guild.get_role(role_id).is_assignable()),
                    reason=f"{self.bot.user.name.title()} Moderation: Restoring roles taken due to {punishment}",
                    atomic=False
                )

        gather(*(
            lift_punishment(punishment)
            for punishment in ("jail", "mute")
        ))
                           
                        
    @Cog.listener()
    async def on_audit_log_entry_create(self: "Moderation", entry: AuditLogEntry):
        """
        An event listener for Audit Logs
        """
        
        guild = entry.guild
        user = entry.user
        target = entry.target
        reason = entry.reason
        action = entry.action

        self.bot.cache.sadd(f"auditlogs{guild.id}", entry)
        
        if _user := re.findall(rf"{self.bot.user.name.title()} Moderation \[(.+)\]", reason or ""):
            if user.id == self.bot.user.id:
                user = utils.find(lambda u: str(u) == _user, self.bot.users) or user
                
        if action == AuditLogAction.ban:
            self.bot.cache.ratelimited(f"rl:bans{guild.id}", 15, 300)
            
            await self.log_history(
                guild_id=guild.id, 
                moderator_id=user.id, 
                member_id=target.id, 
                type="Ban", 
                reason=reason or "No reason provided"
            )
            
        if action == AuditLogAction.kick:
            self.bot.cache.ratelimited(f"rl:kicks{guild.id}", 15, 300)
            
            await self.log_history(
                guild_id=guild.id, 
                moderator_id=user.id, 
                member_id=target.id, 
                type="Kick", 
                reason=reason or "No reason provided"
            )
            
        if action == AuditLogAction.unban:
            if target.id in self.bot.cache.smembers(f"data:hard_banned:{guild.id}"):
                return await guild.ban(
                    user=target,
                    reason=f"{self.bot.user.name.title()} Moderation: User is hard banned"
                )
                
            await self.log_history(
                guild_id=guild.id, 
                moderator_id=user.id, 
                member_id=target.id, 
                type="Unban", 
                reason=reason or "No reason provided"
            )
            
            
    @Command(
        name="tempban",
        aliases=("temporaryban",),
        usage="<member> <time d/h/m/s> [reason]",
        example="@mewa 7d Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def tempban(
        self: "Moderation", 
        ctx: Context, 
        member: Member,
        timespan: Timespan, 
        *, 
        reason: str = "No reason provided"
    ):
        """
        Temporarily ban the mentioned member
        """
        
        if self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            raise CommandError("This resource is being **rate limited**.")
        
        await Member().can_moderate(ctx, member, "ban")

        if member.premium_since:
            raise CommandError("I couldn't ban this member; they're boosting the server.")
        
        if timespan.seconds < 1 or timespan.seconds > 2.419e6:
            raise CommandError("Please provide a **valid** timespan between 1 second and 4 weeks.")
        
        bot_message = await ctx.error(f"Are you sure you want to **temporarily ban** this member?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
            
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            await ctx.guild.ban(
                member,
                delete_message_days=0,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )

            await self.bot.db.execute(
                "INSERT INTO temporary_bans (guild_id, user_id, unban_on) VALUES (%s, %s, %s);",
                ctx.guild.id, member.id, Date.now()
            )
            
            if isinstance(member, _Member):
                if ctx.parameters.get("silent") is not True:
                    self.bot.loop.create_task(self.notify(
                        member,
                        title="Temporarily Banned",
                        message="You have been temporarily banned from",
                        guild=ctx.guild,
                        moderator=ctx.author,
                        reason=reason
                    ))
                
            return await ctx.success(f"Successfully **banned** {member.mention} temporarily for `{fmtseconds(timespan.seconds)}`.")
            
        
    @Command(
        name="warn",
        usage="<member> [reason]",
        example="@mewa Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @has_permissions(manage_messages=True)
    async def warn(
        self: "Moderation",
        ctx: Context,
        member: Member,
        *,
        reason: str = "No reason provided"
    ):
        """
        Warn the mentioned member
        """
        
        await Member().can_moderate(ctx, member, "warn")
            
        bot_message = await ctx.error(f"Are you sure you want to **warn** this member?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
            
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            await self.log_history(
                ctx.guild.id, 
                ctx.author.id, 
                member.id, 
                "Warn", 
                reason
            )
            
            message_sent = False
            if ctx.parameters.get("silent") is not True:
                with suppress(HTTPException):
                    await self.notify(
                        member,
                        title="Warned",
                        message="You have been warned in",
                        guild=ctx.guild,
                        moderator=ctx.author,
                        reason=reason
                    )
                    message_sent = True
                
            return await ctx.send(f"{member.mention}, you have been warned for doing something stupid which broke the rules{f', specifically {reason}.' if reason != 'No reason provided' else '.'} {'You can find more information about this warning in your private messages.' if message_sent else ''}")
            
        
    @Command(
        name="kick",
        aliases=("k",),
        usage="<member> [reason]",
        example="@mewa Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick(
        self: "Moderation", 
        ctx: Context, 
        member: Member,
        *, 
        reason: str = "No reason provided"
    ):
        """
        Kick the mentioned member
        """
        
        if self.bot.cache.ratelimited(f"rl:kicks{ctx.guild.id}", 15, 300):
            raise CommandError("This resource is being **rate limited**.")
        
        await Member().can_moderate(ctx, member, "kick")
            
        bot_message = await ctx.error(f"Are you sure you want to **kick** this member?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
            
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            await ctx.guild.kick(
                member,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            
            if ctx.parameters.get("silent") == False:
                self.bot.loop.create_task(self.notify(
                    member,
                    title="Kicked",
                    message="You have been kicked from",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
                
            return await ctx.success(f"Successfully **kicked** {member.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
        
        
    @Command(
        name="cleanup",
        aliases=("botclear", "bc",),
        usage="[amount]",
        example="50"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def cleanup(self: "Moderation", ctx: Context, amount: int = 100):
        """
        Clean up bots messages in a channel
        """
        
        if amount > 100 or amount < 1:
            raise CommandError("Please provide a **valid** amount between 1 and 100.")
            
        deleted_messages = await ctx.channel.purge(
            limit=amount,
            check=lambda m: m.author.bot or m.content.startswith(ctx.prefix)
        )

        return await ctx.success(
            f"Successfully **cleaned up** `{len(deleted_messages)}` messages from bots.",
            delete_after=5
        )
        
        
    @Group(
        name="thread",
        aliases=("forum",),
        usage="<sub command>",
        example="lock",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_threads=True)
    @has_permissions(manage_threads=True)
    async def thread(self: "Moderation", ctx: Context):
        """
        Commands to manage threads
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
    
    @thread.command(
        name="lock",
        usage="[thread] [reason]",
        example="#helpguys Issue resolved"
    )
    @bot_has_permissions(manage_threads=True)
    @has_permissions(manage_threads=True)
    async def thread_lock(self: "Moderation", ctx: Context, thread: Optional[Thread] = None, *, reason: str = "No reason provided"):
        """
        Lock a thread
        """
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.locked is True:
            raise CommandError("That thread channel **is already** locked.")
            
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        await thread.edit(
            locked=True,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
        )

        return await ctx.success(f"Successfully **locked** {thread.mention}.")
    
    
    @thread.command(
        name="unlock",
        usage="[thread] [reason]",
        example="#helpguys Issue not resolved"
    )
    @bot_has_permissions(manage_threads=True)
    @has_permissions(manage_threads=True)
    async def thread_unlock(self: "Moderation", ctx: Context, thread: Optional[Thread] = None, *, reason: str = "No reason provided"):
        """
        Unlock a thread
        """
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.locked is False:
            raise CommandError("That thread channel **is not** locked.")
            
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        await thread.edit(
            locked=False,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
        )

        return await ctx.success(f"Successfully **unlocked** {thread.mention}.")
        
        
    @thread.command(
        name="archive",
        usage="[thread] [reason]",
        example="#helpguys Issue resolved"
    )
    @bot_has_permissions(manage_threads=True)
    @has_permissions(manage_threads=True)
    async def thread_archive(self: "Moderation", ctx: Context, thread: Optional[Thread] = None, *, reason: str = "No reason provided"):
        """
        Archive a thread
        """
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.archived is True:
            raise CommandError("That thread channel **is already** archived.")
            
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        await thread.edit(
            archived=True,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
        )

        return await ctx.success(f"Successfully **archived** {thread.mention}.")
    
    
    @thread.command(
        name="unarchive",
        usage="[thread] [reason]",
        example="#helpguys Issue resolved"
    )
    @bot_has_permissions(manage_threads=True)
    @has_permissions(manage_threads=True)
    async def thread_unarchive(self: "Moderation", ctx: Context, thread: Optional[Thread] = None, *, reason: str = "No reason provided"):
        """
        Unarchive a thread
        """
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.archived is False:
            raise CommandError("That thread channel **is not** archived.")
            
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        await thread.edit(
            archived=False,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
        )
        
        return await ctx.success(f"Successfully **unarchived** {thread.mention}.")
    
    
    @thread.command(
        name="pin",
        usage="[thread]",
        example="#helpguys"
    )
    @bot_has_permissions(manage_threads=True)
    @has_permissions(manage_threads=True)
    async def thread_pin(self: "Moderation", ctx: Context, thread: Optional[Thread] = None):
        """
        Pin a thread
        """
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.pinned is True:
            raise CommandError("That thread channel **is already** pinned.")
            
        await thread.edit(pinned=True)
        return await ctx.success(f"Successfully **pinned** {thread.mention}.")
    
    
    @thread.command(
        name="unpin",
        usage="[thread]",
        example="#helpguys"
    )
    @bot_has_permissions(manage_threads=True)
    @has_permissions(manage_threads=True)
    async def thread_unpin(self: "Moderation", ctx: Context, thread: Optional[Thread] = None):
        """
        Unpin a thread
        """
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.pinned is False:
            raise CommandError("That thread channel **is not** pinned.")
            
        await thread.edit(pinned=False)
        return await ctx.success(f"Successfully **unpinned** {thread.mention}.")
    
    
    @Group(
        name="lockdown",
        aliases=("lock",),
        usage="[channel] [reason]",
        example="#chat ...",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def lockdown(self: "Moderation", ctx: Context, channel: Optional[TextChannel] = None, *, reason: str = "No reason provided"):
        """
        Lockdown a channel
        """
        
        channel = channel or ctx.channel
        
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        if channel.permissions_for(ctx.guild.default_role).send_messages is False:
            raise CommandError("That channel is **already locked**.")
        
        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=PermissionOverwrite(send_messages=False),
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
        )
        
        return await ctx.success(f"Successfully **locked** {channel.mention}.")
    
    
    @lockdown.command(
        name="all",
        usage="[reason]",
        example="..."
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def lockdown_all(self: "Moderation", ctx: Context, *, reason: str = "No reason provided"):
        """
        Lock every channel
        """
        
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        async def lock_channel(channel: TextChannel):
            if channel.permissions_for(ctx.guild.default_role).send_messages is False:
                if ctx.guild.id not in self.ignore_lockdown:
                    self.ignore_lockdown[ctx.guild.id] = [ ]
                    
                self.ignore_lockdown[ctx.guild.id].append(channel.id)
                return
                
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=PermissionOverwrite(send_messages=False),
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            
        await gather(*(
            lock_channel(channel)
            for channel in ctx.guild.text_channels
        ))
        
        return await ctx.success(f"Successfully **locked** every channel.")
        
        
    @lockdown.group(
        name="remove",
        aliases=("lift",),
        usage="[channel] [reason]",
        example="#chat ...",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def lockdown_remove(self: "Moderation", ctx: Context, channel: Optional[TextChannel] = None, *, reason: str = "No reason provided"):
        """
        Unlock a channel
        """
        
        channel = channel or ctx.channel
        
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        if channel.permissions_for(ctx.guild.default_role).send_messages is True:
            raise CommandError("That channel is **already unlocked**.")
            
        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=PermissionOverwrite(send_messages=True),
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
        )
        
        return await ctx.success(f"Successfully **unlocked** {channel.mention}.")
        
        
    @lockdown_remove.command(
        name="all",
        usage="[reason]",
        example="..."
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def lockdown_remove_all(self: "Moderation", ctx: Context, *, reason: str = "No reason provided"):
        """
        Unlock every channel
        """
        
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        unlocked = await gather(*(
            channel.set_permissions(
                ctx.guild.default_role,
                overwrite=PermissionOverwrite(send_messages=True),
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            for channel in ctx.guild.text_channels
            if channel.id not in self.ignore_lockdown.get(ctx.guild.id, TUPLE)
            and channel.permissions_for(ctx.guild.default_role).send_messages is False
        ))
        
        return await ctx.success(f"Successfully **unlocked** `{len(unlocked)}` channels.")
        
    
    @Group(
        name="unlock",
        usage="[channel] [reason]",
        example="#chat ...",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def unlock(self: "Moderation", ctx: Context, channel: Optional[TextChannel] = None, *, reason: str = "No reason provided"):
        """
        Unlock a channel
        """
        
        channel = channel or ctx.channel
        
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        if channel.permissions_for(ctx.guild.default_role).send_messages is True:
            raise CommandError("That channel is **already unlocked**.")
            
        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=PermissionOverwrite(send_messages=True),
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
        )
        
        return await ctx.success(f"Successfully **unlocked** {channel.mention}.")
        
        
    @unlock.command(
        name="all",
        usage="[reason]",
        example="..."
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def unlock_all(self: "Moderation", ctx: Context, *, reason: str = "No reason provided"):
        """
        Unlock every channel
        """
        
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")

        unlocked = await gather(*(
            channel.set_permissions(
                ctx.guild.default_role,
                overwrite=PermissionOverwrite(send_messages=True),
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            for channel in ctx.guild.text_channels
            if channel.id not in self.ignore_lockdown.get(ctx.guild.id, TUPLE)
            and channel.permissions_for(ctx.guild.default_role).send_messages is False
        ))
        
        return await ctx.success(f"Successfully **unlocked** `{len(unlocked)}` channels.")
        
        
    @Command(
        name="moveall",
        aliases=("ma",),
        usage="<channel>",
        example="#Main Voice"
    )
    
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def moveall(self: "Moderation", ctx: Context, channel: VoiceChannel, *, reason: str = "No reason provided"):
        """
        Move all members in your current channel to another channel
        """
        
        if ctx.author.voice is None:
            raise CommandError("You must be connected to a voice channel.")
            
        current_channel = ctx.author.voice.channel
        if len(current_channel.members) < 2:
            raise CommandError("There aren't any other members in this channel.")
        
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
            
        moved = await gather(*(
            member.move_to(
                channel,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            for member in current_channel.members
            if member.id != ctx.author.id
        ))
                
        return await ctx.success(f"Successfully **moved** `{len(moved)}` members to {channel.mention}.")
        
    
    @Command(
        name="stripstaff",
        usage="<member>",
        example="@mewa"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def stripstaff(self: "Moderation", ctx: Context, *, member: Member):
        """
        Strips all staff roles from the mentioned user
        """
        
        await Member().can_moderate(ctx, member, "strip")
            
        await member.remove_roles(
            *(role for role in member.roles if role.is_assignable() and ctx.is_dangerous(role)),
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Stripped staff roles from member",
            atomic=False
        )
        
        return await ctx.success(f"Successfully **stripped** {member.mention} of their staff roles.")
    
    
    @Command(
        name="setup"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(administrator=True)
    @has_permissions(manage_roles=True)
    async def setup(self: "Moderation", ctx: Context):
        """
        Start the setup process for the moderation system
        """
        
        mute_role_id = jail_role_id = jail_channel_id = 0
        if data := await self.bot.db.fetchrow("SELECT mute_role_id, jail_role_id, jail_channel_id FROM guild_settings WHERE guild_id = %s;", ctx.guild.id):
            mute_role_id, jail_role_id, jail_channel_id = data
            
        if ctx.guild.get_role(mute_role_id) is None:
            mute_role = utils.get(ctx.guild.roles, name=f"Muted ({self.bot.user.name.title()})") or await ctx.guild.create_role(
                name=f"Muted ({self.bot.user.name.title()})",
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Setting up moderation system"
            )

            mute_role_id = mute_role.id
        
        if ctx.guild.get_role(jail_role_id) is None:
            jail_role = utils.get(ctx.guild.roles, name=f"Jailed ({self.bot.user.name.title()})") or await ctx.guild.create_role(
                name=f"Jailed ({self.bot.user.name.title()})",
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Setting up moderation system"
            )

            jail_role_id = jail_role.id
            
        if ctx.guild.get_channel(jail_channel_id) is None:
            jail_channel = utils.get(ctx.guild.text_channels, name="jailed") or await ctx.guild.create_text_channel(
                name="jailed",
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Setting up moderation system"
            )

            await jail_channel.edit(overwrites={
                ctx.guild.me: PermissionOverwrite(read_messages=True),
                ctx.guild.default_role: PermissionOverwrite(read_messages=False),
                ctx.guild.get_role(jail_role_id): PermissionOverwrite(read_messages=True, send_messages=True)
            })

            jail_channel_id = jail_channel.id

        await gather(*chain.from_iterable((
            (
                channel.set_permissions(
                    ctx.guild.get_role(mute_role_id),
                    overwrite=PermissionOverwrite(send_messages=False)
                ),
                channel.set_permissions(
                    ctx.guild.get_role(jail_role_id),
                    overwrite=PermissionOverwrite(view_channel=False)
                )
            )
            for channel in ctx.guild.channels
            if channel.permissions_for(ctx.guild.get_role(mute_role_id)).send_messages is True
            or (channel.permissions_for(ctx.guild.get_role(jail_role_id)).read_messages is True and channel.id != jail_channel_id)
        )))

        await self.bot.db.execute(
            "INSERT INTO guild_settings (guild_id, mute_role_id, jail_role_id, jail_channel_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE mute_role_id = VALUES(mute_role_id), jail_role_id = VALUES(jail_role_id), jail_channel_id = VALUES(jail_channel_id);",
            ctx.guild.id, mute_role_id, jail_role_id, jail_channel_id
        )
        
        return await ctx.success("Successfully **setup** the moderation system.")
        
        
    @Command(
        name="jail",
        aliases=("j",),
        usage="<member> [time d/h/m/s] [reason]",
        example="@mewa 10m Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(administrator=True)
    @has_permissions(manage_messages=True)
    async def jail(self: "Moderation", ctx: Context, member: Member, timespan: Optional[Timespan] = None, *, reason: str = "No reason provided"):
        """
        Jail the mentioned member
        """
        
        if member.id in await self.bot.db.fetch("SELECT user_id FROM jailed_user WHERE guild_id = %s;", ctx.guild.id):
            raise CommandError("That member is **already** jailed.")
        
        await Member().can_moderate(ctx, member, "jail")
            
        jail_role_id = jail_channel_id = 0
        if data := await self.bot.db.fetchrow("SELECT jail_role_id, jail_channel_id FROM guild_settings WHERE guild_id = %s;", ctx.guild.id):
            jail_role_id, jail_channel_id = data
            
        if ctx.guild.get_role(jail_role_id) is None or ctx.guild.get_channel(jail_channel_id) is None:
            raise CommandError("The **moderation system** is not set up.")
            
        jail_role = ctx.guild.get_role(jail_role_id)
        jail_channel = ctx.guild.get_channel(jail_channel_id)
            
        bot_message = await ctx.error(f"Are you sure you want to **jail** this member?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
            
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            roles = member.roles.copy()

            await member.remove_roles(
                *(role for role in roles if role.is_assignable()),
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Member jailed",
                atomic=False
            )

            await gather(*(
                self.bot.db.execute("INSERT INTO taken_roles (guild_id, user_id, role_id) VALUES (%s, %s, %s);", ctx.guild.id, member.id, role.id)
                for role in roles
                if role.is_assignable()
            ))

            await member.add_roles(
                jail_role,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            
            await self.bot.db.execute(
                "INSERT INTO jailed_user (guild_id, user_id, unjail_on) VALUES (%s, %s, %s);",
                ctx.guild.id, member.id, Date.now()+timedelta(seconds=(timespan.seconds if timespan else 2419200))
            )
            
            message_sent = False
            if ctx.parameters.get("silent") is not True:
                with suppress(HTTPException):
                    await self.notify(
                        member,
                        title="Jailed",
                        message="You have been jailed in",
                        guild=ctx.guild,
                        moderator=ctx.author,
                        reason=reason
                    )
                    message_sent = True
                
            await self.log_history(
                ctx.guild.id, 
                ctx.author.id, 
                member.id, 
                "Jail", 
                reason
            )
            
            await jail_channel.send(f"{member.mention}, you have been jailed by {ctx.author.mention} for doing something stupid which broke the rules{f', specifically {reason}.' if reason != 'No reason provided' else '.'} {'You can find more information about this warning in your private messages.' if message_sent else ''}")
            return await ctx.success(f"Successfully **jailed** {member.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
            
        
    @Command(
        name="unjail",
        aliases=("uj",),
        usage="<member>",
        example="@mewa",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(administrator=True)
    @has_permissions(manage_messages=True)
    async def unjail(self: "Moderation", ctx: Context, member: Member):
        """
        Unjail the mentioned member
        """
        
        if member.id not in await self.bot.db.fetch("SELECT user_id FROM jailed_user WHERE guild_id = %s;", ctx.guild.id):
            raise CommandError("That member **isn't** jailed.")
            
        jail_role_id = await self.bot.db.fetchval(
            "SELECT jail_role_id FROM guild_settings WHERE guild_id = %s;", 
            ctx.guild.id
        )
        
        if jail_role := ctx.guild.get_role(jail_role_id):
            if jail_role in member.roles:
                await member.remove_roles(
                    jail_role,
                    reason=f"{self.bot.user.name.title()} Moderation: Member has been unjailed"
                )
        
        taken_roles = await self.bot.db.fetch(
            "SELECT role_id FROM taken_roles WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, member.id
        )

        await self.bot.db.execute(
            """
            DELETE FROM jailed_user WHERE guild_id = %s AND user_id = %s;
            DELETE FROM taken_roles WHERE guild_id = %s AND user_id = %s;
            """,
            ctx.guild.id, member.id,
            ctx.guild.id, member.id
        )

        await member.add_roles(
            *(ctx.guild.get_role(role_id) for role_id in taken_roles if ctx.guild.get_role(role_id) and ctx.guild.get_role(role_id).is_assignable()),
            reason=f"{self.bot.user.name.title()} Moderation: Restoring roles taken due to jail",
            atomic=False
        )

        if ctx.parameters.get("silent") is not True:
            self.bot.loop.create_task(self.notify(
                member,
                title="Unjailed",
                message="You have been unjailed in",
                guild=ctx.guild,
                moderator=ctx.author,
                reason="No reason provided"
            ))
        
        return await ctx.success(f"Successfully **unjailed** {member.mention}.")
        
        
    @Command(
        name="jailed",
        aliases=("jailedlist",)
    )
    @has_permissions(manage_messages=True)
    async def jailed(self: "Moderation", ctx: Context):
        """
        View every jailed member
        """
        
        jailed_members = await self.bot.db.fetch(
            "SELECT user_id FROM jailed_user WHERE guild_id = %s;",
            ctx.guild.id
        )
        if not jailed_members:
            raise CommandError("There aren't any jailed members.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Jailed Members in '{ctx.guild.name}'"
        )
        for user_id in jailed_members:
            if member := ctx.guild.get_member(user_id):
                rows.append(f"{member.mention} {member} (`{member.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="moderationhistory",
        aliases=("mh", "modhistory",),
        usage="[member]",
        example="@mewa",
        invoke_without_command=True
    )
    @has_permissions(manage_messages=True)
    async def moderationhistory(self: "Moderation", ctx: Context, member: Optional[Member] = Author):
        """
        View moderation history for a staff member
        """
        
        history = await self.bot.db.execute(
            "SELECT case_id, type, member_id, reason FROM moderation_history WHERE guild_id = %s AND moderator_id = %s ORDER BY case_id DESC;",
            ctx.guild.id, member.id
        )
        if not history:
            raise CommandError("There is no previously recorded moderation history for that staff member.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Moderation History for '{member}'"
        )
        for case_id, type, member_id, reason in history:
            if _member := self.bot.get_user(member_id):
                rows.append(f"**Case #{case_id}**\n{self.bot.reply} **Type:** {type}\n{self.bot.reply} **Member:** {_member} (`{_member.id}`)\n{self.bot.reply} **Reason:** {reason}")
                
        return await ctx.paginate((embed, rows), show_index=False)
        
        
    @Group(
        name="history",
        usage="[member]",
        example="@mewa",
        invoke_without_command=True
    )
    @has_permissions(manage_messages=True)
    async def history(self: "Moderation", ctx: Context, member: Optional[Member] = Author):
        """
        View a list of every punishment recorded
        """
        
        history = await self.bot.db.execute(
            "SELECT case_id, type, moderator_id, reason FROM moderation_history WHERE guild_id = %s AND member_id = %s ORDER BY case_id DESC;",
            ctx.guild.id, member.id
        )
        if not history:
            raise CommandError("There is no previously recorded punishment history for that member.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Punishment History for {member}"
        )
        for case_id, type, moderator_id, reason in history:
            if moderator := self.bot.get_user(moderator_id):
                rows.append(f"**Case #{case_id}**\n{self.bot.reply} **Type:** {type}\n{self.bot.reply} **Moderator:** {moderator} (`{moderator.id}`)\n{self.bot.reply} **Reason:** {reason}")
                
        return await ctx.paginate((embed, rows), show_index=False)
        
        
    @history.group(
        name="remove",
        usage="<member> [case ID]",
        example="@mewa 1528",
        invoke_without_command=True
    )
    @has_permissions(manage_messages=True)
    async def history_remove(self: "Moderation", ctx: Context, member: Member, case_id: int):
        """
        Remove a punishment from a member
        """
        
        history = await self.bot.db.fetchrow(
            "SELECT * FROM moderation_history WHERE guild_id = %s AND member_id = %s AND case_id = %s;",
            ctx.guild.id, member.id, case_id
        )
        if not history:
            raise CommandError("Please provide a **valid** case ID belonging to that member.")
            
        await self.bot.db.execute(
            "DELETE FROM moderation_history WHERE guild_id = %s AND member_id = %s AND case_id = %s;",
            ctx.guild.id, member.id, case_id
        )
        
        return await ctx.success(f"Successfully **removed** that punishment.")
        
        
    @history_remove.command(
        name="all",
        usage="<member>",
        example="@mewa",
        invoke_without_command=True
    )
    @has_permissions(manage_messages=True)
    async def history_remove_all(self: "Moderation", ctx: Context, member: Member):
        """
        Remove all punishments from a member
        """
        
        history = await self.bot.db.fetchrow(
            "SELECT * FROM moderation_history WHERE guild_id = %s AND member_id = %s LIMIT 1;",
            ctx.guild.id, member.id
        )
        if not history:
            raise CommandError("There is no previously recorded punishment history for that member.")
            
        await self.bot.db.execute(
            "DELETE FROM moderation_history WHERE guild_id = %s AND member_id = %s;",
            ctx.guild.id, member.id
        )
        
        return await ctx.success(f"Successfully **removed** every punishment.")
        
    
    @Command(
        name="reason",
        usage="[case ID] <reason>",
        example="1528 ..."
    )
    @has_permissions(manage_messages=True)
    async def reason(self: "Moderation", ctx: Context, case_id: Optional[int] = None, *, reason: str):
        """
        Update the reason on a case log
        """
        
        if len(reason) > 64:
            raise CommandError("Please provide a **valid** reason under 64 characters.")
        
        case_id = case_id or await self.bot.db.fetchval(
            "SELECT MAX(case_id) FROM moderation_history WHERE guild_id = %s AND moderator_id = %s;",
            ctx.guild.id, ctx.author.id
        ) or 0
        if not await self.bot.db.fetchrow("SELECT * FROM moderation_history WHERE guild_id = %s AND moderator_id = %s AND case_id = %s;", ctx.guild.id, ctx.author.id, case_id):
            raise CommandError("Please provide a **valid** case ID.")
            
        await self.bot.db.execute(
            "UPDATE moderation_history SET reason = %s WHERE case_id = %s;",
            reason, case_id
        )
        
        return await ctx.success("Successfully **updated** the reason for that case log.")
        
        
    @Command(
        name="timeout",
        aliases=("tm",),
        usage="<member> [time d/h/m/s] [reason]",
        example="@mewa 10m Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(moderate_members=True)
    @has_permissions(moderate_members=True)
    async def timeout(
        self: "Moderation", 
        ctx: Context, 
        member: Member,
        timespan: Optional[Timespan] = None,
        *,
        reason: str = "No reason provided"
    ):
        """
        Timeout the mentioned member
        """
        
        await Member().can_moderate(ctx, member, "timeout")
            
        if timespan:
            if timespan.seconds < 1 or timespan.seconds > 2.419e6:
                raise CommandError("Please provide a **valid** timespan between 1 second and 4 weeks.")
            
        bot_message = await ctx.error(f"Are you sure you want to **timeout** this member for `{fmtseconds(timespan.seconds if timespan else 2419200)}`?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
            
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            await member.timeout(
                Date.now().astimezone() + timedelta(seconds=(timespan.seconds if timespan else 2419200)),
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            
            if isinstance(member, _Member):
                if ctx.parameters.get("silent") == False:
                    self.bot.loop.create_task(self.notify(
                        member,
                        title="Timed Out",
                        message="You have been timed out in",
                        guild=ctx.guild,
                        moderator=ctx.author,
                        reason=reason
                    ))
                    
            await self.log_history(
                ctx.guild.id, 
                ctx.author.id, 
                member.id, 
                "Timeout", 
                reason
            )
                
            return await ctx.success(f"Successfully **timed out** {member.mention} for `{fmtseconds(timespan.seconds if timespan else 2419200)}`.")
            
        
    @Group(
        name="untimeout",
        aliases=("utm",),
        usage="<member>",
        example="@mewa",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        },
        invoke_without_command=True
    )
    @bot_has_permissions(moderate_members=True)
    @has_permissions(moderate_members=True)
    async def untimeout(self: "Moderation", ctx: Context, member: Member):
        """
        Untimeout the mentioned member
        """
            
        if member.timed_out_until is None:
            raise CommandError("That member **isn't** timed out.")

        await member.timeout(
            None,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )
        
        if isinstance(member, _Member):
            if ctx.parameters.get("silent") == False:
                self.bot.loop.create_task(self.notify(
                    member,
                    title="Timed Out",
                    message="Your timeout was revoked in",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason="N/A"
                ))
                
        await self.log_history(
            ctx.guild.id, 
            ctx.author.id, 
            member.id, 
            "Untimeout", 
            "No reason provided"
        )
            
        return await ctx.success(f"Successfully **revoked** {member.mention}'s timeout.")
        
    
    @untimeout.command(
        name="all"
    )
    @bot_has_permissions(moderate_members=True)
    @has_permissions(moderate_members=True)
    async def untimeout_all(self: "Moderation", ctx: Context):
        """
        Untimeout every timed out member
        """
        
        timed_out = tuple(member for member in ctx.guild.members if member.timed_out_until is not None and (ctx.guild.roles.index(member.top_role) < ctx.guild.roles.index(ctx.me.top_role) if member.top_role else True))
            
        await gather(*(
            member.timeout(None)
            for member in timed_out
        ))
        
        return await ctx.success(f"Successfully **revoked** `{len(timed_out)}` timeouts.")
        
        
    @Command(
        name="mute",
        aliases=("m",),
        usage="<member> [time d/h/m/s] [reason]",
        example="@mewa 10m Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(administrator=True)
    @has_permissions(manage_messages=True)
    async def mute(
        self: "Moderation", 
        ctx: Context, 
        member: Member, 
        timespan: Optional[Timespan] = None, 
        *, 
        reason: str = "No reason provided"
    ):
        """
        Mute the mentioned member
        """
        
        if member.id in await self.bot.db.fetch(
            "SELECT user_id FROM muted_user WHERE guild_id = %s;", 
            ctx.guild.id
        ):
            raise CommandError("That member is **already** muted.")

        if timespan:
            if timespan.seconds < 1 or timespan.seconds > 2.419e6:
                raise CommandError("Please provide a **valid** timespan between 1 second and 4 weeks.")
            
        mute_role_id = 0

        if data := await self.bot.db.fetchval(
            "SELECT mute_role_id FROM guild_settings WHERE guild_id = %s;", 
            ctx.guild.id
        ):
            mute_role_id = data
            
        if ctx.guild.get_role(mute_role_id) is None:
            raise CommandError("The **moderation system** is not set up.")
            
        mute_role = ctx.guild.get_role(mute_role_id)
            
        await Member().can_moderate(ctx, member, "mute")

        bot_message = await ctx.error(f"Are you sure you want to *mute** this member for `{fmtseconds(timespan.seconds if timespan else 2419200)}`?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
            
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            roles = member.roles.copy()

            await member.remove_roles(
                *(role for role in roles if role.is_assignable()),
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Member muted",
                atomic=False
            )

            await gather(*(
                self.bot.db.execute(
                    "INSERT INTO taken_roles (guild_id, user_id, role_id) VALUES (%s, %s, %s);", 
                    ctx.guild.id, member.id, role.id
                )
                for role in roles
                if role.is_assignable()
            ))

            await member.add_roles(
                mute_role,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            
            await self.bot.db.execute(
                "INSERT INTO muted_user (guild_id, user_id, unmute_on) VALUES (%s, %s, %s);",
                ctx.guild.id, member.id, Date.now()+timedelta(seconds=(timespan.seconds if timespan else 2419200))
            )
            
            message_sent = False
            if ctx.parameters.get("silent") is not True:
                self.bot.loop.create_task(self.notify(
                    member,
                    title="Muted",
                    message="You have been muted in",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
                
            await self.log_history(
                ctx.guild.id, 
                ctx.author.id, 
                member.id, 
                "Mute", 
                reason
            )
            
            return await ctx.success(f"Successfully **muted** {member.mention} for `{fmtseconds(timespan.seconds if timespan else 2419200)}`.")
            
        
    @Group(
        name="unmute",
        aliases=("um",),
        usage="<member>",
        example="@mewa",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        },
        invoke_without_command=True
    )
    @bot_has_permissions(administrator=True)
    @has_permissions(manage_messages=True)
    async def unmute(self: "Moderation", ctx: Context, member: Member):
        """
        Unmute the mentioned member
        """
        
        if member.id not in await self.bot.db.fetch("SELECT user_id FROM muted_user WHERE guild_id = %s;", ctx.guild.id):
            raise CommandError("That member **isn't** muted.")
            
        mute_role_id = await self.bot.db.fetchval(
            "SELECT mute_role_id FROM guild_settings WHERE guild_id = %s;", 
            ctx.guild.id
        )

        if mute_role := ctx.guild.get_role(mute_role_id):
            if mute_role in member.roles:
                await member.remove_roles(
                    mute_role,
                    reason=f"{self.bot.user.name.title()} Moderation: Member has been unmuted"
                )
        
        taken_roles = await self.bot.db.fetch(
            "SELECT role_id FROM taken_roles WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, member.id
        )

        await self.bot.db.execute(
            """
            DELETE FROM muted_user WHERE guild_id = %s AND user_id = %s;
            DELETE FROM taken_roles WHERE guild_id = %s AND user_id = %s;
            """,
            ctx.guild.id, member.id,
            ctx.guild.id, member.id
        )
        
        await member.add_roles(
            *(ctx.guild.get_role(role_id) for role_id in taken_roles if ctx.guild.get_role(role_id) and ctx.guild.get_role(role_id).is_assignable()),
            reason=f"{self.bot.user.name.title()} Moderation: Restoring roles taken due to mute",
            atomic=False
        )

        if ctx.parameters.get("silent") is not True:
            self.bot.loop.create_task(self.notify(
                member,
                title="Unmuted",
                message="You have been unmuted in",
                guild=ctx.guild,
                moderator=ctx.author,
                reason="No reason provided"
            ))
            
        await self.log_history(
            ctx.guild.id, 
            ctx.author.id, 
            member.id, 
            "Unmute", 
            "N/A"
        )
        
        return await ctx.success(f"Successfully **unmuted** {member.mention}.")
        
        
    @unmute.command(
        name="all"
    )
    @bot_has_permissions(moderate_members=True)
    @has_permissions(moderate_members=True)
    async def unmute_all(self: "Moderation", ctx: Context):
        """
        Unmute every muted member
        """
        
        muted = await self.bot.db.fetch(
            "SELECT user_id FROM muted_user WHERE guild_id = %s;",
            ctx.guild.id
        )
            
        await gather(*(
            self.bot.db.execute(
                "DELETE FROM muted_user WHERE guild_id = %s AND user_id = %s;",
                ctx.guild.id, member.id
            )
            for member in ctx.guild.members
            if member.id in muted
        ))
        
        return await ctx.success(f"Successfully **unmuted** `{len(muted)}` members.")
        
        
    @Command(
        name="muted",
        aliases=("mutedlist",)
    )
    @has_permissions(manage_messages=True)
    async def muted(self: "Moderation", ctx: Context):
        """
        View every muted member
        """
        
        muted_members = await self.bot.db.fetch(
            "SELECT user_id FROM muted_user WHERE guild_id = %s;",
            ctx.guild.id
        )
        if not muted_members:
            raise CommandError("There aren't any muted members.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Muted Members in '{ctx.guild.name}'"
        )
        for user_id in muted_members:
            if member := ctx.guild.get_member(user_id):
                rows.append(f"{member.mention} {member} (`{member.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @Command(
        name="timedout",
        aliases=("timedoutlist",)
    )
    @has_permissions(manage_messages=True)
    async def timedout(self: "Moderation", ctx: Context):
        """
        View every timed out member
        """
        
        timed_out_members = tuple(m.id for m in ctx.guild.members if m.timed_out_until)
        if not timed_out_members:
            raise CommandError("There aren't any timed out members.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Timed Out Members in '{ctx.guild.name}'"
        )

        for user_id in timed_out_members:
            if member := ctx.guild.get_member(user_id):
                rows.append(f"{member.mention} {member} (`{member.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @Command(
        name="imute",
        aliases=("imagemute",),
        usage="<member> [reason]",
        example="@mewa Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_messages=True)
    async def imute(
        self: "Moderation", 
        ctx: Context, 
        member: Member,
        *, 
        reason: str = "No reason provided"
    ):
        """
        Image mute the mentioned member
        """
        
        await Member().can_moderate(ctx, member, "image mute")
            
        bot_message = await ctx.error(f"Are you sure you want to **image mute** this member?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
            
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            await gather(*(
                channel.set_permissions(
                    member,
                    overwrite=PermissionOverwrite(attach_files=False, embed_links=False)
                )
                for channel in ctx.guild.text_channels
                if channel.permissions_for(member).attach_files is True
                or channel.permissions_for(member).embed_links is True
            ))
            
            if ctx.parameters.get("silent") == False:
                self.bot.loop.create_task(self.notify(
                    member,
                    title="Image Muted",
                    message="You have been image muted in",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
                
            await self.log_history(
                ctx.guild.id, 
                ctx.author.id, 
                member.id, 
                "Image Mute", 
                reason
            )
                
            return await ctx.success(f"Successfully **image muted** {member.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
            
        
    @Command(
        name="iunmute",
        aliases=("imageunmute",),
        usage="<member>",
        example="@mewa"
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_messages=True)
    async def iunmute(self: "Moderation", ctx: Context, member: Member):
        """
        Revoke the mentioned member's image mute
        """
            
        await gather(*(
            channel.set_permissions(
                member,
                overwrite=None
            )
            for channel in ctx.guild.text_channels
            if channel.permissions_for(member).attach_files is False
            or channel.permissions_for(member).embed_links is False
        ))
            
        await self.log_history(
            ctx.guild.id, 
            ctx.author.id, 
            member.id, 
            "Image Unmute", 
            "N/A"
        )
            
        return await ctx.success(f"Successfully **revoked** {member.mention}'s image mute.")
        
        
    @Command(
        name="rmute",
        aliases=("reactionmute",),
        usage="<member> [reason]",
        example="@mewa Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_messages=True)
    async def rmute(
        self: "Moderation", 
        ctx: Context, 
        member: Member,
        *, 
        reason: str = "No reason provided"
    ):
        """
        Reaction mute the mentioned member
        """
        
        await Member().can_moderate(ctx, member, "reaction mute")
            
        bot_message = await ctx.error(f"Are you sure you want to **reaction mute** this member?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
                
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            await gather(*(
                channel.set_permissions(
                    member,
                    overwrite=PermissionOverwrite(attach_files=False, embed_links=False)
                )
                for channel in ctx.guild.text_channels
                if channel.permissions_for(member).attach_files is True
                or channel.permissions_for(member).embed_links is True
            ))
            
            if ctx.parameters.get("silent") == False:
                self.bot.loop.create_task(self.notify(
                    member,
                    title="Reaction Muted",
                    message="You have been reaction muted in",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
                
            await self.log_history(
                ctx.guild.id, 
                ctx.author.id, 
                member.id, 
                "Reaction Mute", 
                reason
            )
                
            return await ctx.success(f"Successfully **reaction muted** {member.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
            
        
    @Command(
        name="runmute",
        aliases=("reactionunmute",),
        usage="<member>",
        example="@mewa"
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_messages=True)
    async def runmute(self: "Moderation", ctx: Context, member: Member):
        """
        Revoke the mentioned member's reaction mute
        """
            
        await gather(*(
            channel.set_permissions(
                member,
                overwrite=None
            )
            for channel in ctx.guild.text_channels
            if channel.permissions_for(member).add_reactions is False
        ))
            
        await self.log_history(
            ctx.guild.id, 
            ctx.author.id, 
            member.id, 
            "Reaction Unmute", 
            "N/A"
        )
            
        return await ctx.success(f"Successfully **revoked** {member.mention}'s reaction mute.")
        
        
    @Group(
        name="notes",
        usage="[member]",
        example="@mewa",
        invoke_without_command=True
    )
    @has_permissions(manage_messages=True)
    async def notes(
        self: "Moderation", 
        ctx: Context, 
        *, 
        member: Optional[Member] = Author
    ):
        """
        View a member's notes
        """
        
        notes = await self.bot.db.execute(
            "SELECT note_id, note FROM notes WHERE guild_id = %s AND user_id = %s ORDER BY note_id DESC;",
            ctx.guild.id, member.id
        )
        if not notes:
            raise CommandError("There are no notes for that member.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Notes for '{member}'"
        )
        for note_id, note in notes:
            rows.append(f"**Note #{note_id}**\n{note}")
                
        return await ctx.paginate((embed, rows), show_index=False)
        
    
    @notes.command(
        name="add",
        usage="<member> <note>",
        example="@mewa very very dumb"
    )
    @has_permissions(manage_messages=True)
    async def notes_add(
        self: "Moderation", 
        ctx: Context, 
        member: Member, 
        *, 
        note: str
    ):
        """
        Add a note to a member
        """
        
        if note in await self.bot.db.fetch("SELECT note FROM notes WHERE guild_id = %s AND user_id = %s;", ctx.guild.id, member.id):
            raise CommandError("That is **already** a note for that member.")
            
        if len(note) > 64:
            raise CommandError("Please provide a **valid** note under 64 characters.")
            
        note_id = await self.bot.db.fetchval(
            "SELECT MAX(note_id) FROM notes WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, member.id
        ) or 0
        
        await self.bot.db.execute(
            "INSERT INTO notes (guild_id, user_id, note, note_id) VALUES (%s, %s, %s, %s);",
            ctx.guild.id, member.id, note, note_id+1
        )
        
        return await ctx.success(f"Successfully **added** that note to {member.mention}.")
        
        
    @notes.command(
        name="remove",
        aliases=("delete",),
        usage="<member> <note ID>",
        example="@mewa 2"
    )
    @has_permissions(manage_messages=True)
    async def notes_remove(
        self: "Moderation", 
        ctx: Context, 
        member: Member, 
        note_id: int
    ):
        """
        Remove a note from a member
        """
        
        if note_id not in await self.bot.db.fetch("SELECT note_id FROM notes WHERE guild_id = %s AND user_id = %s;", ctx.guild.id, member.id):
            raise CommandError("Please provide a **valid** note ID for that member.")
        
        await self.bot.db.execute(
            "DELETE FROM notes WHERE guild_id = %s AND user_id = %s AND note_id = %s;",
            ctx.guild.id, member.id, note_id
        )
        
        return await ctx.success(f"Successfully **removed** that note from {member.mention}.")
        
    
    @notes.command(
        name="clear",
        aliases=("removeall",),
        usage="<member>",
        example="@mewa"
    )
    @has_permissions(manage_messages=True)
    async def notes_clear(self: "Moderation", ctx: Context, member: Member):
        """
        Remove every note from a member
        """
        
        if not await self.bot.db.fetchrow("SELECT note FROM notes WHERE guild_id = %s AND user_id = %s LIMIT 1;", ctx.guild.id, member.id):
            raise CommandError("That member doesn't have any notes.")
        
        await self.bot.db.execute(
            "DELETE FROM notes WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, member.id
        )
        
        return await ctx.success(f"Successfully **cleared** every note from {member.mention}.")
        
        
    @Command(
        name="hardban",
        usage="<member> [reason]",
        example="@mewa Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(administrator=True)
    async def hardban(
        self: "Moderation", 
        ctx: Context, 
        member: Member,
        *, 
        reason: str = "No reason provided"
    ):
        """
        Permanently ban the mentioned member
        """
        
        if self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            raise CommandError("This resource is being **rate limited**.")
        
        await Member().can_moderate(ctx, member, "hard ban")
        
        if member.premium_since:
            raise CommandError("I couldn't ban this member; they're boosting the server.")
            
        bot_message = await ctx.error(f"Are you sure you want to **hard ban** this member?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
            
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            await ctx.guild.ban(
                member,
                delete_message_days=0,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            await self.bot.db.execute(
                "INSERT INTO hard_banned (guild_id, user_id) VALUES (%s, %s);",
                ctx.guild.id, member.id
            )
            
            if ctx.parameters.get("silent") is not True:
                self.bot.loop.create_task(self.notify(
                    member,
                    title="Hard Banned",
                    message="You have been permanently banned from",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
                
            return await ctx.success(f"Successfully **banned** {member.mention} permanently for {'no reason' if reason == 'No reason provided' else reason}.")
            
        
    @Command(
        name="hardunban",
        usage="<member>",
        example="@mewa",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(administrator=True)
    async def hardunban(self: "Moderation", ctx: Context, user: User):
        """
        Revoke the mentioned user's hard ban
        """
            
        await ctx.guild.unban(
            user,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Hard ban has been revoked"
        )
        await self.bot.db.execute(
            "DELETE FROM hard_banned WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, user.id
        )
        
        if ctx.parameters.get("silent") is not True:
            self.bot.loop.create_task(self.notify(
                user,
                title="Unbanned",
                message="You have been unbanned from",
                guild=ctx.guild,
                moderator=ctx.author,
                reason="N/A"
            ))
            
        return await ctx.success(f"Successfully **unbanned** {user.mention}.")
        
        
    @Command(
        name="hardbanned",
        aliases=("hardbannedlist",)
    )
    @has_permissions(manage_messages=True)
    async def hardbanned(self: "Moderation", ctx: Context):
        """
        View every hardbanned user
        """

        if not (hard_banned_users := await self.bot.db.fetch(
            "SELECT user_id FROM hard_banned WHERE guild_id = %s;",
            ctx.guild.id
        )):
            raise CommandError("There aren't any hardbanned users.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Hard Banned Users in '{ctx.guild.name}'"
        )
        
        for user_id in hard_banned_users:
            if user := ctx.guild.get_member(user_id):
                rows.append(f"{user.mention} {user} (`{user.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @Command(
        name="deleteinvites",
        aliases=("clearinvites",)
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def clearinvites(self: "Moderation", ctx: Context):
        """
        Delete every invite in the server
        """
        
        if not (invites := await ctx.guild.invites()):
            raise CommandError("There aren't any invites in this server.")
            
        bot_message = await ctx.error(f"Are you sure you want to **delete** every invite?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            await gather(*(
                invite.delete() 
                for invite in invites
            ))

            return await ctx.success("Successfully **deleted** every invite in this server.")
            
        
    @Command(
        name="drag",
        aliases=("move",),
        usage="<members> <voice channel>",
        example="@cop#0001 @mewa #Main Voice"
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(move_members=True)
    async def drag(
        self: "Moderation",
        ctx: Context,
        members: Greedy[Member],
        *,
        channel: VoiceChannel
    ):
        """
        Drag member(s) to a voice channel
        """
        
        if not members:
            return await ctx.send_help(ctx.command.qualified_name)
            
        if ctx.author.voice is None:
            raise CommandError("You must be connected to a voice channel.")
            
        await gather(*(
            member.move_to(channel)
            for member in members
            if member.voice
        ))
        
        return await ctx.success(f"Successfully **dragged** those members to {channel.mention}.")
            
        
    @Group(
        name="unbanall",
        aliases=("massunban",),
        invoke_without_command=True
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(ban_members=True)
    @has_permissions(administrator=True)
    async def unbanall(self: "Moderation", ctx: Context):
        """
        Unban every banned user
        """
        
        if ctx.guild.id in self.tasks["unban_all"]:
            raise CommandError("There is already a running unban all task.")
        
        self.tasks["unban_all"][ctx.guild.id] = 1
        unbanned = 0
        
        async for ban in ctx.guild.bans(limit=1000):
            if self.tasks["unban_all"][ctx.guild.id] == 0:
                del self.tasks["unban_all"][ctx.guild.id]
                raise CommandError("This task was cancelled.")
                
            await ctx.guild.unban(
                ban.user,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Unbanning all users"
            )
            unbanned += 1
            
            await sleep(1.25)
            
        del self.tasks["unban_all"][ctx.guild.id]
        return await ctx.success(f"Successfully **unbanned** {unbanned:,} users.")
        
    
    @unbanall.command(
        name="cancel",
        aliases=("stop",)
    )
    @has_permissions(administrator=True)
    async def unbanall_cancel(self: "Moderation", ctx: Context):
        """
        Cancel a running unban all task
        """
        
        if ctx.guild.id not in self.tasks["unban_all"]:
            raise CommandError("There isn't a running unban all task.")
            
        self.tasks["unban_all"][ctx.guild.id] = 0
        raise CommandError("Successfully **cancelled** the running unban all task.")
        
        
    @Command(
        name="ban",
        aliases=("b",),
        usage="<member> [delete days 0/1/7] [reason]",
        example="@mewa Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban(
        self: "Moderation", 
        ctx: Context, 
        user: Union[ User, Member ],
        days: Optional[Literal[ 0, 1, 7 ]] = 0,
        *, 
        reason: str = "No reason provided"
    ):
        """
        Ban the mentioned member
        """
        
        if self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            raise CommandError("This resource is being **rate limited**.")
        
        if user_2 := ctx.guild.get_member(user.id):
            await Member().can_moderate(ctx, user_2, "ban")

            if user_2.premium_since:
                raise CommandError("I couldn't ban this member; they're boosting the server.")
            
        bot_message = await ctx.error(f"Are you sure you want to **ban** this user?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
                
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
            
            await ctx.guild.ban(
                user,
                delete_message_seconds=days*86400,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            
            if user_2:
                if ctx.parameters.get("silent") == False:
                    self.bot.loop.create_task(self.notify(
                        user_2,
                        title="Banned",
                        message="You have been banned from",
                        guild=ctx.guild,
                        moderator=ctx.author,
                        reason=reason
                    ))
                
            return await ctx.success(f"Successfully **banned** {user.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
    
              
    @Command(
        name="unban",
        aliases=("ub",),
        usage="<user>",
        example="@mewa",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban(self: "Moderation", ctx: Context, user: User):
        """
        Unban the mentioned user
        """
        
        if await self.bot.db.execute("SELECT * FROM hard_banned WHERE guild_id = %s AND user_id = %s;", ctx.guild.id, user.id):
            raise CommandError("That user is hard banned.")

        async for ban in ctx.guild.bans():
            if ban.user.id == user.id:
                await ctx.guild.unban(
                    user,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
                )
                
                break
                
        else:
            raise CommandError("That user isn't banned.")
        
        if ctx.parameters.get("silent") == False:
            self.bot.loop.create_task(self.notify(
                user,
                title="Unbanned",
                message="You have been unbanned from",
                guild=ctx.guild,
                moderator=ctx.author,
                reason="N/A"
            ))
            
        return await ctx.success(f"Successfully **unbanned** {user.mention}.")
        
        
    @Command(
        name="softban",
        aliases=("sb",),
        usage="<member> <delete days 0/1/7> [reason]",
        example="@mewa Breaking the rules",
        parameters={
            "silent": {
                "require_value": False,
                "description": "Don't DM the member",
                "aliases": [
                    "s"
                ]
            }
        }
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def softban(
        self: "Moderation", 
        ctx: Context, 
        member: Member,
        days: Optional[Literal[ 0, 1, 7 ]] = 0,
        *, 
        reason: str = "No reason provided"
    ):
        """
        Soft ban the mentioned member
        """
        
        if self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            raise CommandError("This resource is being **rate limited**.")
        
        await Member().can_moderate(ctx, member, "soft ban")
        
        if member.premium_since:
            raise CommandError("I couldn't softban this member; they're boosting the server.")
        
        bot_message = await ctx.error(f"Are you sure you want to **softban** this member?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:  
            if not (reason := strip_flags(reason, ctx)):
                reason = "No reason provided"
                
            if len(reason) > 64:
                raise CommandError("Please provide a **valid** reason under 64 characters.")
                
            await ctx.guild.ban(
                member,
                delete_message_seconds=days*86400,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: {reason}"
            )
            await ctx.guild.unban(
                member,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: User was soft banned"
            )
            
            if ctx.parameters.get("silent") == False:
                self.bot.loop.create_task(self.notify(
                    member,
                    title="Soft Banned",
                    message="You have been soft banned from",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
                
            return await ctx.success(f"Successfully **soft banned** {member.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
            
    
    @Command(
        name="banned",
        usage="<user>",
        example="@mewa"
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def banned(self: "Moderation", ctx: Context, *, user: User):
        """
        Check if a user is banned
        """
        
        async for ban in ctx.guild.bans():
            if ban.user.id == user.id:
                return await ctx.success(f"{user} (`{user.id}`) is banned.")
                
        raise CommandError(f"{user} (`{user.id}`) is not banned.")
        
        
    @Group(
        name="role",
        aliases=("r",),
        usage="<member> <roles>",
        example="@mewa @Staff @Moderator",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role(self: "Moderation", ctx: Context, member: Member, *roles: Role):
        """
        Update a member's roles
        """
        
        await Member().can_moderate(ctx, member, "role")
            
        if len(roles) > 10:
            raise CommandError("You can only add or remove 10 roles at a ")

        _added = tuple(
            role for role in roles 
            if role not in member.roles 
            and role.is_assignable()
            and ctx.author.top_role > role
        )

        _removed = tuple(
            role for role in roles 
            if role in member.roles 
            and role.is_assignable()
            and ctx.author.top_role > role
        )
        
        if not _added and not _removed:
            raise CommandError("I can't assign any of those roles, or your highest role is lower than the roles you're trying to give.")
        
        await member.add_roles(
            *_added,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )
        await member.remove_roles(
            *_removed,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )
                
        added = ", ".join((role.mention for role in _added))
        removed = ", ".join((role.mention for role in _removed))
        string = f"{f'added {added}'+(' and ' if _removed else '') if _added else ''}{f'removed {removed}' if _removed else ''}"
        
        del _added
        del _removed
            
        return await ctx.success(f"Successfully **updated** {member.mention}, {string}.")


    @role.group(
        name="add",
        usage="<sub command>",
        example="bots Bot",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_add(self: "Moderation", ctx: Context):
        """
        Add a role to all of an object (bots/humans/inrole/all)
        """

        return await ctx.send_help(ctx.command.qualified_name)


    @role_add.command(
        name="bots",
        usage="<role>",
        example="Bot"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_add_bots(self: "Moderation", ctx: Context, *, role: Role):
        """
        Add a role to all bots
        """
        
        
        if ctx.guild.id in self.tasks["role"]:
            raise CommandError("There is already a running mass role task.")

        if not role.is_assignable():
            raise CommandError("I can't assign that role.")
        
        if ctx.is_dangerous(role):
            raise CommandError("That role has **dangerous permissions**.")

        if not (members := tuple(
            member for member in ctx.guild.members 
            if member.bot 
            and role not in member.roles
        )):
            raise CommandError("There aren't any bots without that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("This task was canceled.")

            try:
                await member.add_roles(
                    role,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Mass role (bots)"
                )
                
                if members.index(member) != len(members)-1:
                    await sleep(1)
            
            except Exception:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **added** {role.mention} to every bot.")


    @role_add.command(
        name="humans",
        usage="<role>",
        example="Member"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_add_humans(self: "Moderation", ctx: Context, *, role: Role):
        """
        Add a role to all humans
        """
        
        
        if ctx.guild.id in self.tasks["role"]:
            raise CommandError("There is already a running mass role task.")

        if not role.is_assignable():
            raise CommandError("I can't assign that role.")
        
        if ctx.is_dangerous(role):
            raise CommandError("That role has **dangerous permissions**.")

        if not (members := tuple(
            member for member in ctx.guild.members 
            if member.bot is False 
            and role not in member.roles
        )):
            raise CommandError("There aren't any humans without that role.")
        
        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in ctx.guild.members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("This task was canceled.")

            try:
                await member.add_roles(
                    role,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Mass role (humans)"
                )

                if ctx.guild.members.index(member) != len(ctx.guild.members)-1:
                    await sleep(1)
            
            except Exception:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **added** {role.mention} to every human.")


    @role_add.command(
        name="all",
        usage="<role>",
        example="..."
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_add_all(self: "Moderation", ctx: Context, *, role: Role):
        """
        Add a role to every members
        """
        
        if ctx.guild.id in self.tasks["role"]:
            raise CommandError("There is already a running mass role task.")

        if not role.is_assignable():
            raise CommandError("I can't assign that role.")
        
        if ctx.is_dangerous(role):
            raise CommandError("That role has **dangerous permissions**.")

        if not (members := tuple(
            member for member in ctx.guild.members 
            if role not in member.roles
        )):
            raise CommandError("There aren't any members without that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("This task was canceled.")

            try:
                await member.add_roles(
                    role,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Mass role (all)"
                )

                if ctx.guild.members.index(member) != len(ctx.guild.members)-1:
                    await sleep(1)
            
            except Exception:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **added** {role.mention} to every member.")


    @role_add.command(
        name="has",
        aliases=("inrole",),
        usage="<has> <role>",
        example="Supporter VIP"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_add_has(self: "Moderation", ctx: Context, has: Role, *, role: Role):
        """
        Add a role to all members in a specific role
        """
        
        
        if ctx.guild.id in self.tasks["role"]:
            raise CommandError("There is already a running mass role task.")

        if not role.is_assignable():
            raise CommandError("I can't assign that role.")
        
        if ctx.is_dangerous(role):
            raise CommandError("That role has **dangerous permissions**.")

        if not (members := tuple(
            member for member in ctx.guild.members 
            if has in member.roles 
            and role not in member.roles
        )):
            raise CommandError("There aren't any members in the provided role, or there aren't any members without the role I'm supposed to give.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("This task was canceled.")

            try:
                await member.add_roles(
                    role,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Mass role (inrole)"
                )

                if members.index(member) != len(members)-1:
                    await sleep(1)
            
            except Exception:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **added** {role.mention} to every member with the role {has.mention}.")

    
    @role.group(
        name="remove",
        usage="<sub command>",
        example="bots Bot",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_remove(self: "Moderation", ctx: Context):
        """
        Remove a role from all of an object (bots/humans/inrole/all)
        """

        return await ctx.send_help(ctx.command.qualified_name)


    @role_remove.command(
        name="bots",
        usage="<role>",
        example="Bot"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_remove_bots(self: "Moderation", ctx: Context, *, role: Role):
        """
        Remove a role from all bots
        """
        
        
        if ctx.guild.id in self.tasks["role"]:
            raise CommandError("There is already a running mass role task.")

        if not role.is_assignable():
            raise CommandError("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if member.bot and role in member.roles)
        if not members:
            raise CommandError("There aren't any bots with that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("This task was canceled.")
            
            try:
                await member.remove_roles(
                    role,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Mass role (bots)"
                )

                if members.index(member) != len(members)-1:
                    await sleep(1)
            
            except Exception:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **removed** {role.mention} from every bot.")


    @role_remove.command(
        name="humans",
        usage="<role>",
        example="Member"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_remove_humans(self: "Moderation", ctx: Context, *, role: Role):
        """
        Remove a role from every human
        """
        
        
        if ctx.guild.id in self.tasks["role"]:
            raise CommandError("There is already a running mass role task.")

        if not role.is_assignable():
            raise CommandError("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if member.bot is False and role in member.roles)
        if not members:
            raise CommandError("There aren't any humans with that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("This task was canceled.")

            try:
                await member.remove_roles(
                    role,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Mass role remove (humans)"
                )

                if members.index(member) != len(members)-1:
                    await sleep(1)
            
            except Exception:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **removed** {role.mention} from every human.")


    @role_remove.command(
        name="all",
        usage="<role>",
        example="..."
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_remove_all(self: "Moderation", ctx: Context, *, role: Role):
        """
        Remove a role from every member
        """
        
        
        if ctx.guild.id in self.tasks["role"]:
            raise CommandError("There is already a running mass role task.")

        if not role.is_assignable():
            raise CommandError("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if role in member.roles)
        if not members:
            raise CommandError("There aren't any members with that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("This task was canceled.")

            try:
                await member.remove_roles(
                    role,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Mass role remove (all)"
                )

                if members.index(member) != len(members)-1:
                    await sleep(1)
            
            except Exception:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **removed** {role.mention} from every member.")


    @role_remove.command(
        name="has",
        aliases=("inrole",),
        usage="<has> <role>",
        example="Supporter VIP"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_roles=True)
    @has_permissions(administrator=True)
    async def role_remove_has(self: "Moderation", ctx: Context, has: Role, *, role: Role):
        """
        Remove a role from every member in a specific role
        """
        
        
        if ctx.guild.id in self.tasks["role"]:
            raise CommandError("There is already a running mass role task.")

        if not role.is_assignable():
            raise CommandError("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if has in member.roles and role in member.roles)
        if not members:
            raise CommandError("There aren't any members in the provided role, or there aren't any members with the role I'm supposed to remove.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("This task was canceled.")

            try:
                await member.remove_roles(
                    role,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Mass role remove (inrole)"
                )

                if members.index(member) != len(members)-1:
                    await sleep(1)
            
            except Exception:
                del self.tasks["role"][ctx.guild.id]
                raise CommandError("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **removed** {role.mention} from every member with the role {has.mention}.")


    @role.command(
        name="cancel",
        aliases=("stop",)
    )
    @has_permissions(administrator=True)
    async def role_cancel(self: "Moderation", ctx: Context):
        """
        Cancel a running mass role task
        """
        
        if ctx.guild.id not in self.tasks["role"]:
            raise CommandError("There isn't a running mass role task.")
            
        self.tasks["role"][ctx.guild.id] = 0
        raise CommandError("Successfully **cancelled** the running mass role task.")


    @role.command(
        name="create",
        aliases=("make",),
        usage="<color> <name>",
        example="#0000FF Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_create(self: "Moderation", ctx: Context, color: Color, *, name: str):
        """
        Create a role
        """

        if len(name) > 32:
            raise CommandError("Please provide a **valid** name under 32 characters.")

        role = await ctx.guild.create_role(
            name=name,
            color=color
        )
        
        return await ctx.success(f"Successfully **created** {role.mention}.")


    @role.command(
        name="delete",
        aliases=("del", "d",),
        usage="<role>",
        example="Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_delete(self: "Moderation", ctx: Context, *, role: Role):
        """
        Delete a role
        """

        bot_message = await ctx.error(f"Are you sure you want to **delete** {role.mention}?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:
            if role.is_assignable() is False:
                raise CommandError("I can't manage that role.")

            await role.delete(reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]")
            return await ctx.success(f"Successfully **deleted** {role.mention}.")


    @role.command(
        name="icon",
        aliases=("image",),
        usage="<image> <role>",
        example="... Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_icon(
        self: "Moderation", 
        ctx: Context, 
        source: Union[ Emoji, PartialEmoji, Attachment ], 
        *, 
        role: Role
    ):
        """
        Set a role's icon
        """

        if role.is_assignable() is False:
            raise CommandError("I can't manage that role.")

        if hasattr(source, "url"):
            source = source.url

        try:
            await role.edit(display_icon=await self.bot.proxied_session.read(source))

        except Forbidden:
            raise CommandError("I can't manage that role's display icon.")
            
        except Exception:
            if not ctx.message.attachments or source != ctx.message.attachments[0].url:
                if not await self.bot.is_owner(ctx.author):
                    if self.bot.cache.ratelimited(f"globalrl:suspicious_urls{source}", 3, 86400):
                        return await self.bot.blacklist(ctx.author.id, _type=1)
                    
            raise CommandError("Please provide a **valid** image.")

        return await ctx.success(f"Successfully **updated** that role's [**icon**]({source}).")


    @role.command(
        name="mentionable",
        aliases=("pingable",),
        usage="<role>",
        example="... Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_mentionable(self: "Moderation", ctx: Context, *, role: Role):
        """
        Toggle mentioning a role
        """

        if role.is_assignable() is False:
            raise CommandError("I can't manage that role.")

        await role.edit(mentionable=role.mentionable is False)
        return await ctx.success(f"Successfully **toggled** mentioning {role.mention}.")


    @role.command(
        name="topcolor",
        aliases=("highestcolor", "tc",),
        usage="<color> <member>",
        example="#0000FF Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_topcolor(self: "Moderation", ctx: Context, color: Color, *, member: Member = Author):
        """
        Change your highest role's color
        """

        if member.top_role is None:
            raise CommandError("That member does not have any roles.")

        if member.top_role.is_assignable() is False:
            raise CommandError("I can't manage that role.")

        await member.top_role.edit(color=color)
        return await ctx.success(f"Successfully **set** {member.mention}'s top role color to `#{hex(color)[2:]}`.")


    @role.command(
        name="color",
        aliases=("colour",),
        usage="<color> <role>",
        example="#0000FF Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_color(self: "Moderation", ctx: Context, color: Color, *, role: Role):
        """
        Change a role's color
        """

        if role.is_assignable() is False:
            raise CommandError("I can't manage that role.")

        await role.edit(color=color)
        return await ctx.success(f"Successfully **set** {role.mention}'s color to `#{hex(color.value)[2:]}`.")


    @role.command(
        name="hoist",
        aliases=("visible",),
        usage="<role>",
        example="... Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_hoist(self: "Moderation", ctx: Context, *, role: Role):
        """
        Toggle hoisting a role
        """

        if role.is_assignable() is False:
            raise CommandError("I can't manage that role.")

        await role.edit(hoist=role.hoist is False)
        return await ctx.success(f"Successfully **toggled** hoisting {role.mention}.")


    @role.command(
        name="name",
        aliases=("setname",),
        usage="<role> <name>",
        example="#0000FF Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_name(self: "Moderation", ctx: Context, role: Role, *, name: str):
        """
        Change a role's name
        """

        if len(name) > 32:
            raise CommandError("Please provide a **valid** name under 32 characters.")

        if role.is_assignable() is False:
            raise CommandError("I can't manage that role.")

        await role.edit(name=name)
        return await ctx.success(f"Successfully **set** {role.mention}'s name to `{name}`.")


    @role.command(
        name="restore",
        usage="<member>",
        example="@mewa"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_restore(self: "Moderation", ctx: Context, *, member: Member):
        """
        Restore a member's role
        """

        await Member().can_moderate(ctx, member, "role")

        if not (roles := self.bot.cache.smembers(f"restore{ctx.guild.id}-{member.id}")):
            raise CommandError("There are no roles to restore.")

        await member.add_roles(
            *(role for role in roles if role not in member.roles and role.is_assignable() and ctx.is_dangerous(role) is False),
            reason=f"{self.bot.user.name.title()} Moderation: Restoring member's roles",
            atomic=False
        )

        self.bot.cache.srem(
            f"restore{ctx.guild.id}-{member.id}", 
            *roles
        )

        return await ctx.success(f"Successfully **restored** {member.mention}'s roles.")


    @role.command(
        name="position",
        aliases=("pos",),
        usage="<position> <role>",
        example="1 Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_position(self: "Moderation", ctx: Context, position: int, *, role: Role):
        """
        Set a role's position
        """

        if role.is_assignable() is False:
            raise CommandError("I can't manage that role.")

        try:
            await role.edit(position=position)
        except ValueError:
            raise CommandError("Please provide a **valid** permission.")

        return await ctx.success(f"Successfully **set** {role.mention}'s position to {role.position}.")


    @role.command(
        name="permissions",
        aliases=("perms",),
        usage="<permissions> <role>",
        example="8 Lab Rat"
    )
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def role_permissions(self: "Moderation", ctx: Context, permissions: int, *, role: Role):
        """
        Update a role's permissions
        """

        if role.is_assignable() is False:
            raise CommandError("I can't manage that role.")

        if not any(map(lambda t: t[1], iter(Permissions(permissions)))):
            raise CommandError("Please provide a **valid** permission.")
        
        await role.edit(permissions=Permissions(permissions))
        return await ctx.success(f"Successfully **updated** {role.mention}'s permissions.")


    @Group(
        name="purge",
        aliases=("clear", "c",),
        usage="[member], <amount>",
        example="matches nigg.*? 100",
        invoke_without_command=True
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge(
        self: "Moderation", 
        ctx: Context, 
        member: Optional[Member],
        amount: int
    ):
        """
        Clear messages in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: ((member or m.author).id == m.author.id) if member else True,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages.",
            delete_after=3
        )


    @purge.command(
        name="matches",
        usage="<expression> <amount>",
        example="nigg.*? 100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_matches(self: "Moderation", ctx: Context, expression: str, amount: int):
        """
        Clear messages matching an expression in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: re.findall(expression.lower(), m.content.lower()),
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        except re.error:
            raise CommandError("Please provide a **valid** expression.")

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages matching the expression `{expression}`.",
            delete_after=3
        )


    @purge.command(
        name="humans",
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_humans(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages from humans in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: not m.author.bot,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages from humans.",
            delete_after=3
        )


    @purge.command(
        name="bots",
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_bots(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages from bots in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: m.author.bot,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages from bots.",
            delete_after=3
        )


    @purge.command(
        name="after",
        usage="<message>",
        example="1120872265786077364"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_after(self: "Moderation", ctx: Context, *, message: Message):
        """
        Clear messages sent after the specified message
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=None,
                after=message.created_at,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages.",
            delete_after=3
        )


    @purge.command(
        name="stickers",
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_stickers(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages with stickers in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: m.stickers,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with stickers.",
            delete_after=3
        )


    @purge.command(
        name="attachments",
        aliases=("images",),
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_attachments(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages with attachments in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: m.attachments,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with attachments.",
            delete_after=3
        )



    @purge.command(
        name="emojis",
        aliases=("emotes",),
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_emojis(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages with emojis in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")

        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: m.emojis,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with emojis.",
            delete_after=3
        )


    @purge.command(
        name="mentions",
        aliases=("pings",),
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_mentions(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages with mentions in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: m.mentions,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]
        
        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with mentions.",
            delete_after=3
        )


    # @purge.command(
    #     name="upto",
    #     aliases=("before",),
    #     usage="<message>",
    #     example="1120872265786077364"
    # )
    # @max_concurrency(1, BucketType.channel, wait=False)
    # @bot_has_permissions(manage_messages=True)
    # @has_permissions(manage_messages=True)
    # async def purge_upto(self: "Moderation", ctx: Context, *, message: Message):
    #     """
    #     Clear messages sent before the specified message
    #     """

    #     if ctx.guild.id in self.tasks["purge"]:
    #         raise CommandError("There is already a running purge task.")
        
    #     self.tasks["purge"][ctx.guild.id] = 1

    #     try:
    #         cleared_messages = await ctx.channel.purge(
    #             limit=None,
    #             before=message.created_at,
    #             reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
    #         )

    #     finally:
    #         del self.tasks["purge"][ctx.guild.id]

    #     return await ctx.success(
    #         f"Successfully **cleared** `{len(cleared_messages)}` messages.",
    #         delete_after=3
    #     )


    @purge.command(
        name="embeds",
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_embeds(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages with embeds in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: m.embeds,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with embeds.",
            delete_after=3
        )


    @purge.command(
        name="reactions",
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_reactions(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages with reactions in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: m.reactions,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with reactions.",
            delete_after=3
        )


    @purge.command(
        name="links",
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_links(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages with links in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: expressions.link.findall(m.content),
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]
        
        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with links.",
            delete_after=3
        )


    @purge.command(
        name="webhooks",
        aliases=("whook", "wh",),
        usage="<amount>",
        example="100"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_webhooks(self: "Moderation", ctx: Context, amount: int):
        """
        Clear messages with webhooks in bulk
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        if amount > 1000 or amount in (0, 1):
            raise CommandError("You can only clear between **1** and *1,000** messages.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: m.author.bot and m.author.discriminator == "0000" and not m.author.system,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with webhooks.",
            delete_after=3
        )


    @purge.command(
        name="between",
        usage="<start> <finish>",
        example="1120872265786077364"
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge_upto(
        self: "Moderation", 
        ctx: Context, 
        start: Message, 
        finish: Message
    ):
        """
        Clear messages between message (A) and message (B)
        """

        if ctx.guild.id in self.tasks["purge"]:
            raise CommandError("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1

        try:
            cleared_messages = await ctx.channel.purge(
                limit=None,
                before=finish.created_at,
                after=start.created_at,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )
        
        finally:
            del self.tasks["purge"][ctx.guild.id]

        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages.",
            delete_after=3
        )


    @Command(name="nuke")
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def nuke(self: "Moderation", ctx: Context):
        """
        Clone and delete the current channel
        """

        if ctx.channel in (ctx.guild.system_channel, ctx.guild.rules_channel):
            return await ctx.send_error("You cant **nuke** this channel.")

        bot_message = await ctx.error("Are you sure you want to **nuke** this channel?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:
            new_channel = await ctx.channel.clone(
                name=ctx.channel.name,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
            )

            await ctx.channel.delete(reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]")
            await new_channel.edit(position=ctx.channel.position)

            if ctx.channel.id in await self.bot.db.fetch("SELECT channel_id FROM welcome_settings WHERE guild_id = %s", ctx.guild.id):
                await self.bot.db.execute(
                    "UPDATE welcome_settings SET channel_id = %s WHERE guild_id = %s AND channel_id = %s",
                    new_channel.id, ctx.guild.id, ctx.channel.id
                )

            if ctx.channel.id in await self.bot.db.fetch("SELECT channel_id FROM leave_settings WHERE guild_id = %s", ctx.guild.id):
                await self.bot.db.execute(
                    "UPDATE leave_settings SET channel_id = %s WHERE guild_id = %s AND channel_id = %s",
                    new_channel.id, ctx.guild.id, ctx.channel.id
                )

            if ctx.channel.id in await self.bot.db.fetch("SELECT channel_id FROM boost_settings WHERE guild_id = %s", ctx.guild.id):
                await self.bot.db.execute(
                    "UPDATE boost_settings SET channel_id = %s WHERE guild_id = %s AND channel_id = %s",
                    new_channel.id, ctx.guild.id, ctx.channel.id
                )

            if ctx.channel.id in await self.bot.db.fetch("SELECT channel_id FROM unboost_settings WHERE guild_id = %s", ctx.guild.id):
                await self.bot.db.execute(
                    "UPDATE unboost_settings SET channel_id = %s WHERE guild_id = %s AND channel_id = %s",
                    new_channel.id, ctx.guild.id, ctx.channel.id
                )
                
            self.bot.cache.initialize_settings_cache()
            
            return await new_channel.send(
                embed=Embed(
                    color=self.bot.color,
                    description=f"{self.bot.done} {ctx.author.mention}**:** Successfully **nuked** #{ctx.channel.name}."
                )
            )


    @Command(
        name="talk",
        usage="[channel] [role]",
        example="#private VIP"
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def talk(
        self: "Moderation",
        ctx: Context,
        channel: Optional[TextChannel] = None,
        *,
        role: Optional[Role] = None
    ):
        """
        Toggle a channel to text for a role
        """

        channel = channel or ctx.channel
        role = role or ctx.guild.default_role

        overwrite = not channel.permissions_for(role).send_messages
        await channel.set_permissions(
            role,
            overwrite=PermissionOverwrite(send_messages=overwrite),
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )

        return await ctx.success(f"Successfully **{'enabled' if overwrite else 'disabled'}** text for {role.mention if role != ctx.guild.default_role else '@everyone'} in {channel.mention}.")


    @Command(
        name="hide",
        usage="[channel] [role]",
        example="#private VIP"
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def hide(
        self: "Moderation",
        ctx: Context,
        channel: Optional[TextChannel] = None,
        *,
        role: Optional[Role] = None
    ):
        """
        Toggle a channel to read messages for a role
        """

        channel = channel or ctx.channel
        role = role or ctx.guild.default_role

        overwrite = not channel.permissions_for(role).send_messages
        await channel.set_permissions(
            role,
            overwrite=PermissionOverwrite(view_channel=overwrite),
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )

        return await ctx.success(f"Successfully **{'enabled' if overwrite else 'disabled'}** reading messages for {role.mention if role != ctx.guild.default_role else '@everyone'} in {channel.mention}.")


    @Command(
        name="slowmode",
        usage="<time d/h/m/s>",
        example="5s"
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def slowmode(self: "Moderation", ctx: Context, timespan: Timespan):
        """
        Restricts members to sending one message per interval
        """

        if timespan.seconds < 0 or timespan.seconds > 216e2:
            raise CommandError("Please provide a **valid** timespan between 0 seconds and 6 hours.")

        await ctx.channel.edit(
            slowmode_delay=timespan.seconds,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )
        
        return await ctx.success(f"Successfully **set** the channel's **message interval** to `{fmtseconds(timespan.seconds)}`.")


    @Command(
        name="revokefiles",
        aliases=("rf",)
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def revokefiles(self: "Moderation", ctx: Context):
        """
        Removes/assigns the permission to attach files & embed links in the current channel
        """

        overwrite = any((
            not ctx.channel.permissions_for(ctx.guild.default_role).attach_files,
            not ctx.channel.permissions_for(ctx.guild.default_role).embed_links
        ))
        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=PermissionOverwrite(
                attach_files=overwrite,
                embed_links=overwrite
            ),
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )

        return await ctx.success(f"Successfully **{'assigned' if overwrite else 'revoked'}** attach files/embed links permissions for @everyone.")


    @Command(
        name="rename",
        aliases=("nickname", "nick"),
        usage="<member> <nickname>",
        example="@mewa skidward"
    )
    @bot_has_permissions(manage_nicknames=True)
    @has_permissions(manage_nicknames=True)
    async def rename(self: "Moderation", ctx: Context, member: Member, *, nickname: str):
        """
        Assigns the mentioned user a new nickname in the server
        """

        await Member().can_moderate(ctx, member, "rename")

        if len(nickname) < 2 or len(nickname) > 32:
            raise CommandError("Please provide a **valid** nickname between 2 and 32 characters.")

        await member.edit(
            nick=nickname,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )

        raise CommandError(f"Successfully **renamed** {member.mention} to `{nickname}`.")


    @Group(
        name="stickyrole",
        aliases=("sr", "sticky"),
        usage="<sub command>",
        example="add Loser",
        extras={
            "permissions": "Server Owner"
        },
        invoke_without_command=True
    )
    @is_guild_owner()
    async def stickyrole(self: "Moderation", ctx: Context):
        """
        Reapply a role on join
        """

        return await ctx.send_help(ctx.command.qualified_name)


    @stickyrole.command(
        name="add",
        usage="<role>",
        example="Loser",
        extras={
            "permissions": "Server Owner"
        }
    )
    @is_guild_owner()
    async def stickyrole_add(self: "Moderation", ctx: Context, *, role: Role):
        """
        Add a sticky role
        """

        if role in self.bot.cache.sticky_roles.get(ctx.guild.id, DICT):
            raise CommandError("That is **already** a sticky role.")

        await self.bot.db.execute(
            "INSERT INTO sticky_roles (guild_id, role_id) VALUES (%s, %s);",
            ctx.guild.id, role.id
        )
        
        if ctx.guild.id not in self.bot.cache.sticky_roles:
            self.bot.cache.sticky_roles[ctx.guild.id] = [ ]

        self.bot.cache.sticky_roles[ctx.guild.id].append(role.id)
        return await ctx.success(f"Successfully **added** {role.mention} as a **sticky role**.")


    @stickyrole.command(
        name="remove",
        usage="<role>",
        example="Loser",
        extras={
            "permissions": "Server Owner"
        }
    )
    @is_guild_owner()
    async def stickyrole_remove(self: "Moderation", ctx: Context, *, role: Role):
        """
        Remove a sticky role
        """

        if role not in self.bot.cache.sticky_roles.get(ctx.guild.id, DICT):
            raise CommandError("That is **not** a sticky role.")

        await self.bot.db.execute(
            "DELETE FROM sticky_roles WHERE guild_id = %s AND role_id = %s;",
            ctx.guild.id, role.id
        )

        self.bot.cache.sticky_roles[ctx.guild.id].remove(role.id)

        return await ctx.success(f"Successfully **removed** {role.mention} from the server's **sticky roles**.")


    @stickyrole.command(
        name="list",
        aliases=("view",),
        extras={
            "permissions": "Server Owner"
        }
    )
    @is_guild_owner()
    async def stickyrole_list(self: "Moderation", ctx: Context):
        """
        View every sticky role
        """
        
        if ctx.guild.id not in self.bot.cache.sticky_roles:
            raise CommandError("There are no **sticky roles** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Sticky Roles in '{ctx.guild.name}'"
        )
        
        for role_id in self.bot.cache.sticky_roles[ctx.guild.id]:
            if (role := ctx.guild.get_role(role_id)) is not None:
                rows.append(f"{role.mention}: **{role.name}** ( `{role.id}` )")
                
        return await ctx.paginate((embed, rows))
    

    @Group(
        name="raid",
        usage="<sub command>",
        example="ban 10m",
        invoke_without_command=True
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(administrator=True)
    async def raid(self: "Moderation", ctx: Context):
        """
        Remove members who joined within the specified timespan
        """

        return await ctx.send_help(ctx.command.qualified_name)
    
    
    @raid.command(
        name="ban",
        usage="<time d/h/m/s>",
        example="10m"
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(administrator=True)
    async def raid_ban(self: "Moderation", ctx: Context, timespan: Timespan):
        """
        Ban members who joined within the specified timespan
        """

        if self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            raise CommandError("This resource is being **rate limited**.")

        if timespan.seconds < 1 or timespan.seconds > 2.16e4:
            raise CommandError("Please provide a **valid** timespan between 1 second and 6 hours.")
        
        members = tuple(
            m 
            for m in ctx.guild.members 
            if not m.premium_since 
            and m.id != self.bot.user.id 
            and time()-m.joined_at.timestamp() < timespan.seconds
        )
        
        if not members:
            raise CommandError("There aren't any members to ban.")
        
        bot_message = await ctx.error(f"Are you sure you want to **ban** `{len(members)}` members?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:
            banned = await gather(*(
                m.ban(reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Raid mass-ban")
                for m in members
                if m.top_role.position < ctx.me.top_role.position
            ))

            return await ctx.success(f"Successfully **banned** `{len(banned)}` members.")
    
    
    @raid.command(
        name="kick",
        usage="<time d/h/m/s>",
        example="10m"
    )
    @bot_has_permissions(ban_members=True)
    @has_permissions(administrator=True)
    async def raid_kick(self: "Moderation", ctx: Context, timespan: Timespan):
        """
        Kick members who joined within the specified timespan
        """

        if self.bot.cache.ratelimited(f"rl:kicks{ctx.guild.id}", 15, 300):
            raise CommandError("This resource is being **rate limited**.")
        
        if timespan.seconds < 1 or timespan.seconds > 2.16e4:
            raise CommandError("Please provide a **valid** timespan between 1 second and 6 hours.")
        
        members = tuple(
            m 
            for m in ctx.guild.members 
            if not m.premium_since 
            and m.id != self.bot.user.id 
            and time()-m.joined_at.timestamp() < timespan.seconds
        )
        
        if not members:
            raise CommandError("There aren't any members to kick.")
        
        bot_message = await ctx.error(f"Are you sure you want to **kick** `{len(members)}` members?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:
            kicked = await gather(*(
                m.kick(reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Raid mass-kick")
                for m in members
                if m.top_role.position < ctx.me.top_role.position
            ))

            return await ctx.success(f"Successfully **kicked** `{len(kicked)}` members.")
    

    @Group(
        name="forcenickname",
        aliases=("forcenick", "fn"),
        usage="<member> <nickname>",
        example="@mewa loser",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_nicknames=True)
    @has_permissions(manage_nicknames=True)
    async def forcenickname(
        self: "Moderation",
        ctx: Context,
        member: Member,
        *,
        nickname: str
    ):
        """
        Force a member's nickname
        """

        bot_message = await ctx.error("Are you sure you want to **force** this member's nickname?", delete_after=30)
        confirmation = await confirm(ctx, bot_message)

        if confirmation is True:
            if len(nickname) < 2 or len(nickname) > 32:
                raise CommandError("Please provide a **valid** nickname between 2 and 32 characters.")
            
            self.bot.cache.set(
                f"fn{ctx.guild.id}-{member.id}", 
                nickname
            )

            await member.edit(
                nick=nickname,
                reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: Forced nickname"
            )

            return await ctx.success(f"Successfully **forced** {member.mention}'s nickname to `{nickname}`.")
        

    @forcenickname.command(
        name="remove",
        usage="<member>",
        example="@mewa"
    )
    @bot_has_permissions(manage_nicknames=True)
    @has_permissions(manage_nicknames=True)
    async def forcenickname_remove(self: "Moderation", ctx: Context, *, member: Member):
        """
        Remove a member's forced nickname
        """

        if self.bot.cache.get(f"fn{ctx.guild.id}-{member.id}") is None:
            raise CommandError("That member doesn't have a **forced nickname**.")
        
        self.bot.cache.delete(f"fn{ctx.guild.id}-{member.id}")
        await member.edit(
            nick=None,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]: No longer forcing member's nickname"
        )
        
        return await ctx.success(f"No longer **forcing** {member.mention}'s nickname.")
    

    @forcenickname.command(
        name="list",
        aliases=("view",),
        extras={
            "permissions": "Server Owner"
        }
    )
    @has_permissions(manage_nicknames=True)
    async def forcenickname_list(self: "Moderation", ctx: Context):
        """
        View every forced nickname
        """
        
        if not self.bot.cache.keys(pattern=f"fn{ctx.guild.id}-*"):
            raise CommandError("There are no **forced nicknames** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Forced Nicknames in '{ctx.guild.name}'"
        )
        for member_id in re.findall(f"fn{ctx.guild.id}-(\d+)", " ".join(self.bot.cache.keys(pattern=f"fn{ctx.guild.id}-*"))):
            if (member := ctx.guild.get_member(int(member_id))) is not None:
                rows.append(f"{member.mention}: `{self.bot.cache.get(f'fn{ctx.guild.id}-{member.id}')}`")
                
        return await ctx.paginate((embed, rows))
    

    @Command(
        name="topic",
        usage="<text>",
        example="Hang out with fellow members"
    )
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def topic(self: "Moderation", ctx: Context, *, text: Optional[str] = None):
        """
        Set the current channel's topic
        """

        if isinstance(text, str) and len(text) > 1024:
            raise CommandError("Please provide a **valid** topic under 1024 characters.")
        
        try:
            async with sleep(2):
                await ctx.channel.edit(
                    topic=text,
                    reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
                )
        
        except TimeoutError:
            raise CommandError("This resource is being **rate limited**.")

        return await ctx.success(f"Successfully **set** {ctx.channel.mention}'s topic.")
    

    @Command(name="naughty")
    @cooldown(2, 600, BucketType.channel)
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_channels=True)
    async def naughty(self: "Moderation", ctx: Context):
        """
        Toggle NSFW in the current channel for 30 seconds
        """

        if ctx.channel.nsfw:
            raise CommandError("This channel is already **NSFW**.")
        
        async def do_naughty():
            await sleep(30)
            await ctx.channel.edit(nsfw=False)

        await ctx.channel.edit(
            nsfw=True,
            reason=f"{self.bot.user.name.title()} Moderation [{ctx.author}]"
        )
        
        self.bot.loop.create_task(do_naughty())
        return await ctx.success(f"Successfully **toggled** NSFW in {ctx.channel.mention} for `30 seconds`.")
    

    @Group(
        name="restrictcommand",
        usage="<sub command>",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def restrictcommand(self: "Moderation", ctx: Context):
        """
        Only allows people with a certain role to use command
        """

        return await ctx.send_help(ctx.command.qualified_name)
    

    @restrictcommand.command(
        name="add",
        usage="<command> <role>",
        example="screenshot @Cool People"
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def restrictcommand_add(
        self: "Moderation", 
        ctx: Context, 
        command: str, 
        *, 
        role: Role
    ):
        """
        Allows the specified role exclusive permission to use a command
        """

        if not (command := self.bot.get_command(command)):
            raise CommandError("Please provide a **valid** command.")

        if role.id in self.bot.cache.restricted_commands.get(ctx.guild.id, DICT).get(command.qualified_name, TUPLE):
            raise CommandError(f"This command is **already restricted** to that role.")
        
        await self.bot.db.execute(
            "INSERT INTO restricted_command (guild_id, command_name, role_id) VALUES (%s, %s, %s);",
            ctx.guild.id, command.qualified_name, role.id
        )

        if ctx.guild.id not in self.bot.cache.restricted_commands:
            self.bot.cache.restricted_commands[ctx.guild.id] = { }

        if command.qualified_name not in self.bot.cache.restricted_commands[ctx.guild.id]:
            self.bot.cache.restricted_commands[ctx.guild.id][command.qualified_name] = [ ]
            
        self.bot.cache.restricted_commands[ctx.guild.id][command.qualified_name].append(role.id)
        return await ctx.success(f"Successfully **allowed** {role.mention} to use `{command.qualified_name}`.")
    

    @restrictcommand.command(
        name="remove",
        usage="<command> <role>",
        example="screenshot @Cool People"
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def restrictcommand_remove(
        self: "Moderation", 
        ctx: Context, 
        command: str, 
        *, 
        role: Role
    ):
        """
        Removes the specified roles exclusive permission to use a command
        """

        if not (command := self.bot.get_command(command)):
            raise CommandError("Please provide a **valid** command.")

        if role.id not in self.bot.cache.restricted_commands.get(ctx.guild.id, DICT).get(command.qualified_name, TUPLE):
            raise CommandError(f"This command is not restricted to that role.")
        
        await self.bot.db.execute(
            "DELETE FROM restricted_command WHERE guild_id = %s AND command_name = %s AND role_id = %s;",
            ctx.guild.id, command.qualified_name, role.id
        )
            
        self.bot.cache.restricted_commands[ctx.guild.id][command.qualified_name].remove(role.id)
        return await ctx.success(f"Successfully **removed** {role.mention}'s permission to use `{command.qualified_name}`.")
    

    @restrictcommand.command(name="reset")
    @has_permissions(manage_guild=True)
    async def pins_reset(self: "Moderation", ctx: Context):
        """
        Unrestricts every command
        """
        
        if ctx.guild.id not in self.bot.cache.restricted_commands:
            raise CommandError("There aren't any **restricted commands** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM restricted_command WHERE guild_id = %s;",
            ctx.guild.id
        )

        del self.bot.cache.restricted_commands[ctx.guild.id]
        return await ctx.success("Successfully **unrestricted** every command.")
    

    @restrictcommand.command(
        name="list",
        aliases=("view",)
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def restrictcommand_list(
        self: "Moderation",
        ctx: Context
    ):
        """
        List all restricted commands
        """
        
        if not (commands := self.bot.cache.restricted_commands.get(ctx.guild.id, DICT)):
            raise CommandError("There aren't any restricted commands in this server.")
        
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Restriced Commands in '{ctx.guild.name}'"
        )

        for command, roles in commands.items():
            if command := self.bot.get_command(command):
                roles = ", ".join((ctx.guild.get_role(role).mention for role in roles if ctx.guild.get_role(role)))
                rows.append(f"`{command.qualified_name}` **—** {roles}")
            
        return await ctx.paginate((embed, rows))
            

async def setup(bot: VileBot) -> NoReturn:
    """
    Add the Moderation cog to the bot.

    Parameters:
        bot (VileBot): An instance of the VileBot class.
    """

    await bot.add_cog(Moderation(bot))