import discord, asyncio, itertools, re, time
from typing import Union, Optional, Literal
from datetime import datetime, timedelta
from utilities import vile
from discord.ext import commands, tasks

TUPLE = ()
DICT = {}


class Moderation(commands.Cog):
    def __init__(self, bot: "VileBot") -> None:
        self.bot = bot
        self.ignore_lockdown = {}
        self.tasks = {
            "unban_all": {},
            "role": {},
            "purge": {}
        }
        
    
    async def cog_load(self) -> None:
        """An asynchronous setup function for the Cog"""
        self.do_scheduled_actions.start()
        
        
    async def cog_unload(self) -> None:
        """The opposite of cog_load"""
        self.do_scheduled_actions.cancel()
        
        
        
    async def cog_check(self, ctx) -> bool:
        """A check for every Moderation command"""
        
        if ctx.me.guild_permissions.administrator is False:
            raise commands.BotMissingPermissions(("administrator",))
            
        return True
        
        
    async def log_history(
        self, 
        guild_id: int, 
        moderator_id: int, 
        member_id: int, 
        type: str, 
        reason: str = "No reason provided"
    ) -> None:
        """Log a moderation action"""
        
        case_id = await self.bot.db.fetchval(
            "SELECT MAX(case_id) FROM moderation_history WHERE guild_id = %s;",
            guild_id
        ) or 0
        
        # I couldn't make AUTO_INCREMENT work
        # even when the same exact table structure worked for a friend
        
        try:
            await self.bot.db.execute(
                "INSERT INTO moderation_history (guild_id, moderator_id, member_id, type, reason, created_on, case_id) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                guild_id, moderator_id, member_id, type, reason, datetime.now(), case_id+1
            )
        except Exception:
            # Duplicate entry
            return
            
    
    async def notify(
        self, 
        member: discord.Member,
        title: str,
        message: str,
        guild: discord.Member,
        moderator: discord.Member,
        reason: str = "No reason provided"
    ):
        """Notify the member of a Moderation action"""
        
        embed = (
            discord.Embed(
                color=self.bot.color,
                title=title,
                description=f"> {message} {guild.name}",
                timestamp=datetime.now()
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
        try:
            return await member.send(embed=embed)
        except Exception:
            # User's DMs are disabled
            return
            
    
    @tasks.loop(seconds=10)        
    async def do_scheduled_actions(self):
        """Do scheduled actions"""
        
        for guild_id, user_id, unban_on in await self.bot.db.execute("SELECT guild_id, user_id, unban_on FROM temporary_bans;"):
            if datetime.now() > unban_on:
                if guild := self.bot.get_guild(guild_id):
                    if guild.me.guild_permissions.ban_members:
                        async for entry in guild.bans():
                            if entry.user.id == user_id:
                                await guild.unban(entry.user, reason="Vile Moderation: Temporary ban has been lifted")
                                await self.bot.db.execute(
                                    "DELETE FROM temporary_bans WHERE guild_id = %s AND user_id = %s;",
                                    guild_id, user_id
                                )
                                break
                        await asyncio.sleep(0.001)
                        
        for guild_id, user_id, unjail_on in await self.bot.db.execute("SELECT guild_id, user_id, unjail_on FROM jailed_user;"):
            if datetime.now() > unjail_on:
                if guild := self.bot.get_guild(guild_id):
                    if member := guild.get_member(user_id):
                        if guild.me.guild_permissions.administrator:
                            if jail_role_id := await self.bot.db.fetchval("SELECT jail_role_id FROM guild_settings WHERE guild_id = %s;", guild_id):
                                if jail_role := guild.get_role(jail_role_id):
                                    if jail_role in member.roles:
                                        await member.remove_roles(
                                            jail_role,
                                            reason="Vile Moderation: Jail has been lifted"
                                        )
                                        taken_roles = await self.bot.db.fetch(
                                            "SELECT role_id FROM taken_roles WHERE guild_id = %s AND user_id = %s;",
                                            guild_id, user_id
                                        )
                                        await self.bot.db.execute(
                                            """
                                            DELETE FROM jailed_user WHERE guild_id = %s AND user_id = %s;
                                            DELETE FROM taken_roles WHERE guild_id = %s AND user_id = %s;
                                            """,
                                            guild_id, user_id,
                                            guild_id, user_id
                                        )
                                        await member.add_roles(
                                            *(guild.get_role(role_id) for role_id in taken_roles if guild.get_role(role_id) and guild.get_role(role_id).is_assignable()),
                                            reason="Vile Moderation: Restoring roles taken due to jail",
                                            atomic=False
                                        )
                                        
        for guild_id, user_id, unmute_on in await self.bot.db.execute("SELECT guild_id, user_id, unmute_on FROM muted_user;"):
            if datetime.now() > unmute_on:
                if guild := self.bot.get_guild(guild_id):
                    if member := guild.get_member(user_id):
                        if guild.me.guild_permissions.administrator:
                            if mute_role_id := await self.bot.db.fetchval("SELECT mute_role_id FROM guild_settings WHERE guild_id = %s;", guild_id):
                                if mute_role := guild.get_role(mute_role_id):
                                    if mute_role in member.roles:
                                        await member.remove_roles(
                                            mute_role,
                                            reason="Vile Moderation: Mute has been lifted"
                                        )
                                        taken_roles = await self.bot.db.fetch(
                                            "SELECT role_id FROM taken_roles WHERE guild_id = %s AND user_id = %s;",
                                            guild_id, user_id
                                        )
                                        await self.bot.db.execute(
                                            """
                                            DELETE FROM muted_user WHERE guild_id = %s AND user_id = %s;
                                            DELETE FROM taken_roles WHERE guild_id = %s AND user_id = %s;
                                            """,
                                            guild_id, user_id,
                                            guild_id, user_id
                                        )
                                        await member.add_roles(
                                            *(guild.get_role(role_id) for role_id in taken_roles if guild.get_role(role_id) and guild.get_role(role_id).is_assignable()),
                                            reason="Vile Moderation: Restoring roles taken due to mute",
                                            atomic=False
                                        )
                           
                        
    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        """An event listener for Audit Logs"""
        
        guild = entry.guild
        user = entry.user
        target = entry.target
        reason = entry.reason
        action = entry.action

        await self.bot.cache.sadd(f"auditlogs{guild.id}", entry)
        
        if _user := re.findall(r"Vile Moderation \[(.+)\]", reason or ""):
            if user.id == self.bot.user.id:
                user = discord.utils.find(lambda u: str(u) == _user, self.bot.users) or user
                
        if action == discord.AuditLogAction.ban:
            await self.bot.cache.ratelimited(f"rl:bans{guild.id}", 15, 300)
            await self.log_history(
                guild.id, 
                user.id, 
                target.id, 
                "Ban", 
                reason or "No reason provided"
            )
            
        if action == discord.AuditLogAction.kick:
            await self.bot.cache.ratelimited(f"rl:kicks{guild.id}", 15, 300)
            await self.log_history(
                guild.id, 
                user.id, 
                target.id, 
                "Kick", 
                reason or "No reason provided"
            )
            
        if action == discord.AuditLogAction.unban:
            await self.log_history(
                guild.id, 
                user.id, 
                target.id, 
                "Unban", 
                reason or "No reason provided"
            )
            
            if target.id in await self.bot.db.fetch("SELECT user_id FROM hard_banned WHERE guild_id = %s;", guild.id):
                await guild.ban(
                    target,
                    reason="Vile Moderation: User is hard banned"
                )
            
            
    @commands.command(
        name="tempban",
        aliases=("temporaryban",),
        usage="<member> <time d/h/m/s> [reason]",
        example="@cop#0666 7d Breaking the rules",
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
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def tempban(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter,
        timespan: vile.Timespan, 
        *, 
        reason: str = "No reason provided"
    ):
        """Temporarily ban the mentioned member"""
        
        if await self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            return await ctx.error("This resource is being **rate limited**.")
        
        if await ctx.can_moderate(member, "ban") is not None:
            return
            
        if timespan.seconds < 1 or timespan.seconds > 2.419e+6:
            return await ctx.error("Please provide a **valid** timespan between 1 second and 4 weeks.")
        
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await ctx.guild.ban(
            member,
            delete_message_days=0,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        await self.bot.db.execute(
            "INSERT INTO temporary_bans (guild_id, user_id, unban_on) VALUES (%s, %s, %s);",
            ctx.guild.id, member.id, datetime.now()
        )
        
        if isinstance(member, discord.Member):
            if ctx.parameters.get("silent") is not True:
                asyncio.ensure_future(self.notify(
                    member,
                    title="Temporarily Banned",
                    message="You have been temporarily banned from",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
            
        return await ctx.success(f"Successfully **banned** {member.mention} temporarily for `{vile.fmtseconds(timespan.seconds)}`.")
        
        
    @commands.command(
        name="warn",
        usage="<member> [reason]",
        example="@cop#0666 Breaking the rules",
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
    @commands.has_permissions(manage_messages=True)
    async def warn(
        self,
        ctx: vile.Context,
        member: vile.MemberConverter,
        *,
        reason: str = "No reason provided"
    ):
        """Warn the mentioned member"""
        
        if await ctx.can_moderate(member, "warn") is not None:
            return
            
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await self.log_history(
            ctx.guild.id, 
            ctx.author.id, 
            member.id, 
            "Warn", 
            reason
        )
        
        message_sent = False
        if ctx.parameters.get("silent") is not True:
            try:
                await self.notify(
                    member,
                    title="Warned",
                    message="You have been warned in",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                )
                message_sent = True
            except Exception:
                message_sent = False
            
        return await ctx.send(f"{member.mention}, you have been warned for doing something stupid which broke the rules{f', specifically {reason}.' if reason != 'No reason provided' else '.'} {'You can find more information about this warning in your private messages.' if message_sent else ''}")
        
        
    @commands.command(
        name="kick",
        aliases=("k",),
        usage="<member> [reason]",
        example="@cop#0666 Breaking the rules",
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
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter,
        *, 
        reason: str = "No reason provided"
    ):
        """Kick the mentioned member"""
        
        if await self.bot.cache.ratelimited(f"rl:kicks{ctx.guild.id}", 15, 300):
            return await ctx.error("This resource is being **rate limited**.")
        
        if await ctx.can_moderate(member, "kick") is not None:
            return
            
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await ctx.guild.kick(
            member,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        
        if ctx.parameters.get("silent") == False:
            asyncio.ensure_future(self.notify(
                member,
                title="Kicked",
                message="You have been kicked from",
                guild=ctx.guild,
                moderator=ctx.author,
                reason=reason
            ))
            
        return await ctx.success(f"Successfully **kicked** {member.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
        
        
    @commands.command(
        name="cleanup",
        aliases=("botclear", "bc",),
        usage="[amount]",
        example="50"
    )
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx: vile.Context, amount: int = 100):
        """Clean up bots messages in a channel"""
        
        if amount > 100 or amount < 1:
            return await ctx.error("Please provide a **valid** amount between 1 and 100.")
            
        deleted_messages = await ctx.channel.purge(
            limit=amount,
            check=lambda m: m.author.bot or m.content.startswith(ctx.prefix)
        )
        return await ctx.success(
            f"Successfully **cleaned up** `{len(deleted_messages)}` messages from bots.",
            delete_after=5
        )
        
        
    @commands.group(
        name="thread",
        aliases=("forum",),
        usage="<sub command>",
        example="lock",
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_threads=True)
    @commands.has_permissions(manage_threads=True)
    async def thread(self, ctx: vile.Context):
        """Commands to manage threads"""
        return await ctx.send_help(ctx.command.qualified_name)
        
    
    @thread.command(
        name="lock",
        usage="[thread] [reason]",
        example="#helpguys Issue resolved"
    )
    @commands.bot_has_permissions(manage_threads=True)
    @commands.has_permissions(manage_threads=True)
    async def thread_lock(self, ctx: vile.Context, thread: Optional[discord.Thread] = None, *, reason: str = "No reason provided"):
        """Lock a thread"""
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, discord.Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.locked is True:
            return await ctx.error("That thread channel **is already** locked.")
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await thread.edit(
            locked=True,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        return await ctx.success(f"Successfully **locked** {thread.mention}.")
    
    
    @thread.command(
        name="unlock",
        usage="[thread] [reason]",
        example="#helpguys Issue not resolved"
    )
    @commands.bot_has_permissions(manage_threads=True)
    @commands.has_permissions(manage_threads=True)
    async def thread_unlock(self, ctx: vile.Context, thread: Optional[discord.Thread] = None, *, reason: str = "No reason provided"):
        """Unlock a thread"""
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, discord.Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.locked is False:
            return await ctx.error("That thread channel **is not** locked.")
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await thread.edit(
            locked=False,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        return await ctx.success(f"Successfully **unlocked** {thread.mention}.")
        
        
    @thread.command(
        name="archive",
        usage="[thread] [reason]",
        example="#helpguys Issue resolved"
    )
    @commands.bot_has_permissions(manage_threads=True)
    @commands.has_permissions(manage_threads=True)
    async def thread_archive(self, ctx: vile.Context, thread: Optional[discord.Thread] = None, *, reason: str = "No reason provided"):
        """Archive a thread"""
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, discord.Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.archived is True:
            return await ctx.error("That thread channel **is already** archived.")
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await thread.edit(
            archived=True,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        return await ctx.success(f"Successfully **archived** {thread.mention}.")
    
    
    @thread.command(
        name="unarchive",
        usage="[thread] [reason]",
        example="#helpguys Issue resolved"
    )
    @commands.bot_has_permissions(manage_threads=True)
    @commands.has_permissions(manage_threads=True)
    async def thread_unarchive(self, ctx: vile.Context, thread: Optional[discord.Thread] = None, *, reason: str = "No reason provided"):
        """Unarchive a thread"""
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, discord.Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.archived is False:
            return await ctx.error("That thread channel **is not** archived.")
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await thread.edit(
            archived=False,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        return await ctx.success(f"Successfully **unarchived** {thread.mention}.")
    
    
    @thread.command(
        name="pin",
        usage="[thread]",
        example="#helpguys"
    )
    @commands.bot_has_permissions(manage_threads=True)
    @commands.has_permissions(manage_threads=True)
    async def thread_pin(self, ctx: vile.Context, thread: Optional[discord.Thread] = None):
        """Pin a thread"""
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, discord.Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.pinned is True:
            return await ctx.error("That thread channel **is already** pinned.")
            
        await thread.edit(pinned=True)
        return await ctx.success(f"Successfully **pinned** {thread.mention}.")
    
    
    @thread.command(
        name="unpin",
        usage="[thread]",
        example="#helpguys"
    )
    @commands.bot_has_permissions(manage_threads=True)
    @commands.has_permissions(manage_threads=True)
    async def thread_unpin(self, ctx: vile.Context, thread: Optional[discord.Thread] = None):
        """Unpin a thread"""
        
        if thread is None:
            thread = ctx.channel
            if not isinstance(thread, discord.Thread):
                return await ctx.send_help(ctx.command.qualified_name)
                
        if thread.pinned is False:
            return await ctx.error("That thread channel **is not** pinned.")
            
        await thread.edit(pinned=False)
        return await ctx.success(f"Successfully **unpinned** {thread.mention}.")
    
    
    @commands.group(
        name="lockdown",
        aliases=("lock",),
        usage="[channel] [reason]",
        example="#chat ...",
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx: vile.Context, channel: Optional[discord.TextChannel] = None, *, reason: str = "No reason provided"):
        """Lockdown a channel"""
        
        channel = channel or ctx.channel
        
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        if channel.permissions_for(ctx.guild.default_role).send_messages is False:
            return await ctx.error("That channel is **already locked**.")
        
        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=discord.PermissionOverwrite(send_messages=False),
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        
        return await ctx.success(f"Successfully **locked** {channel.mention}.")
    
    
    @lockdown.command(
        name="all",
        usage="[reason]",
        example="..."
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def lockdown_all(self, ctx: vile.Context, *, reason: str = "No reason provided"):
        """Lock every channel"""
        
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        async def lock_channel(channel: discord.TextChannel):
            if channel.permissions_for(ctx.guild.default_role).send_messages is False:
                if ctx.guild.id not in self.ignore_lockdown:
                    self.ignore_lockdown[ctx.guild.id] = []
                    
                self.ignore_lockdown[ctx.guild.id].append(channel.id)
                return
                
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=discord.PermissionOverwrite(send_messages=False),
                reason=f"Vile Moderation [{ctx.author}]: {reason}"
            )
            
        await asyncio.gather(*(
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
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def lockdown_remove(self, ctx: vile.Context, channel: Optional[discord.TextChannel] = None, *, reason: str = "No reason provided"):
        """Unlock a channel"""
        
        channel = channel or ctx.channel
        
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        if channel.permissions_for(ctx.guild.default_role).send_messages is True:
            return await ctx.error("That channel is **already unlocked**.")
            
        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=discord.PermissionOverwrite(send_messages=True),
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        
        return await ctx.success(f"Successfully **unlocked** {channel.mention}.")
        
        
    @lockdown_remove.command(
        name="all",
        usage="[reason]",
        example="..."
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def lockdown_remove_all(self, ctx: vile.Context, *, reason: str = "No reason provided"):
        """Unlock every channel"""
        
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        unlocked = await asyncio.gather(*(
            channel.set_permissions(
                ctx.guild.default_role,
                overwrite=discord.PermissionOverwrite(send_messages=True),
                reason=f"Vile Moderation [{ctx.author}]: {reason}"
            )
            for channel in ctx.guild.text_channels
            if channel.id not in self.ignore_lockdown.get(ctx.guild.id, TUPLE)
            and channel.permissions_for(ctx.guild.default_role).send_messages is False
        ))
        
        return await ctx.success(f"Successfully **unlocked** `{len(unlocked)}` channels.")
        
    
    @commands.group(
        name="unlock",
        usage="[channel] [reason]",
        example="#chat ...",
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: vile.Context, channel: Optional[discord.TextChannel] = None, *, reason: str = "No reason provided"):
        """Unlock a channel"""
        
        channel = channel or ctx.channel
        
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        if channel.permissions_for(ctx.guild.default_role).send_messages is True:
            return await ctx.error("That channel is **already unlocked**.")
            
        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=discord.PermissionOverwrite(send_messages=True),
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        
        return await ctx.success(f"Successfully **unlocked** {channel.mention}.")
        
        
    @unlock.command(
        name="all",
        usage="[reason]",
        example="..."
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def unlock_all(self, ctx: vile.Context, *, reason: str = "No reason provided"):
        """Unlock every channel"""
        
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")

        unlocked = await asyncio.gather(*(
            channel.set_permissions(
                ctx.guild.default_role,
                overwrite=discord.PermissionOverwrite(send_messages=True),
                reason=f"Vile Moderation [{ctx.author}]: {reason}"
            )
            for channel in ctx.guild.text_channels
            if channel.id not in self.ignore_lockdown.get(ctx.guild.id, TUPLE)
            and channel.permissions_for(ctx.guild.default_role).send_messages is False
        ))
        
        return await ctx.success(f"Successfully **unlocked** `{len(unlocked)}` channels.")
        
        
    @commands.command(
        name="moveall",
        aliases=("ma",),
        usage="<channel>",
        example="#Main Voice"
    )
    
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def moveall(self, ctx: vile.Context, channel: discord.VoiceChannel, *, reason: str = "No reason provided"):
        """Move all members in your current channel to another channel"""
        
        if ctx.author.voice is None:
            return await ctx.error("You must be connected to a voice channel.")
            
        current_channel = ctx.author.voice.channel
        if len(current_channel.members) < 2:
            return await ctx.error("There aren't any other members in this channel.")
        
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        moved = await asyncio.gather(*(
            member.move_to(
                channel,
                reason=f"Vile Moderation [{ctx.author}]: {reason}"
            )
            for member in current_channel.members
            if member.id != ctx.author.id
        ))
                
        return await ctx.success(f"Successfully **moved** `{len(moved)}` members to {channel.mention}.")
        
    
    @commands.command(
        name="stripstaff",
        usage="<member>",
        example="@cop#0666"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def stripstaff(self, ctx: vile.Context, *, member: vile.MemberConverter):
        """Strips all staff roles from the mentioned user"""
        
        if await ctx.can_moderate(member, "strip") is not None:
            return
            
        await member.remove_roles(
            *(role for role in ctx.author.roles if role.is_assignable() and list(filter(lambda p: p[1], (role.permissions & discord.Permissions.elevated())))),
            reason=f"Vile Moderation [{ctx.author}]: Stripped staff roles from member",
            atomic=False
        )
        
        return await ctx.success(f"Successfully **stripped** {member.mention} of their staff roles.")
    
    
    @commands.command(
        name="setup"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(manage_roles=True)
    async def setup(self, ctx: vile.Context):
        """Start the setup process for the moderation system"""
        
        mute_role_id = jail_role_id = jail_channel_id = 0
        if data := await self.bot.db.fetchrow("SELECT mute_role_id, jail_role_id, jail_channel_id FROM guild_settings WHERE guild_id = %s;", ctx.guild.id):
            mute_role_id, jail_role_id, jail_channel_id = data
            
        if ctx.guild.get_role(mute_role_id) is None:
            mute_role = discord.utils.get(ctx.guild.roles, name="Muted (vile)") or await ctx.guild.create_role(
                name="Muted (vile)",
                reason=f"Vile Moderation [{ctx.author}]: Setting up moderation system"
            )
            mute_role_id = mute_role.id
        
        if ctx.guild.get_role(jail_role_id) is None:
            jail_role = discord.utils.get(ctx.guild.roles, name="Jailed (vile)") or await ctx.guild.create_role(
                name="Jailed (vile)",
                reason=f"Vile Moderation [{ctx.author}]: Setting up moderation system"
            )
            jail_role_id = jail_role.id
            
        if ctx.guild.get_channel(jail_channel_id) is None:
            jail_channel = discord.utils.get(ctx.guild.text_channels, name="jail") or await ctx.guild.create_text_channel(
                name="jail",
                reason=f"Vile Moderation [{ctx.author}]: Setting up moderation system"
            )
            if jail_channel.permissions_for(ctx.guild.default_role).read_messages is True or jail_channel.permissions_for(ctx.guild.get_role(jail_role_id)).read_messages is False:
                await jail_channel.edit(overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.get_role(jail_role_id): discord.PermissionOverwrite(read_messages=True)
                })
            jail_channel_id = jail_channel.id
            
        await asyncio.gather(*itertools.chain.from_iterable((
            (
                channel.set_permissions(
                    ctx.guild.get_role(mute_role_id),
                    overwrite=discord.PermissionOverwrite(send_messages=False)
                ),
                channel.set_permissions(
                    ctx.guild.get_role(jail_role_id),
                    overwrite=discord.PermissionOverwrite(read_messages=False)
                )
            )
            for channel in ctx.guild.text_channels
            if channel.permissions_for(ctx.guild.get_role(mute_role_id)).send_messages is True
            or channel.permissions_for(ctx.guild.get_role(jail_role_id)).read_messages is True
            and channel.id != jail_channel_id
        )))
            
        await self.bot.db.execute(
            "INSERT INTO guild_settings (guild_id, mute_role_id, jail_role_id, jail_channel_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE mute_role_id = VALUES(mute_role_id), jail_role_id = VALUES(jail_role_id), jail_channel_id = VALUES(jail_channel_id);",
            ctx.guild.id, mute_role_id, jail_role_id, jail_channel_id
        )
        
        return await ctx.success("Successfully **setup** the moderation system.")
        
        
    @commands.command(
        name="jail",
        aliases=("j",),
        usage="<member> [time d/h/m/s] [reason]",
        example="@cop#0666 10m Breaking the rules",
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
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(manage_messages=True)
    async def jail(self, ctx: vile.Context, member: vile.MemberConverter, timespan: Optional[vile.Timespan] = None, *, reason: str = "No reason provided"):
        """Jail the mentioned member"""
        
        if member.id in await self.bot.db.fetch("SELECT user_id FROM jailed_user WHERE guild_id = %s;", ctx.guild.id):
            return await ctx.error("That member is **already** jailed.")
            
        jail_role_id = jail_channel_id = 0
        if data := await self.bot.db.fetchrow("SELECT jail_role_id, jail_channel_id FROM guild_settings WHERE guild_id = %s;", ctx.guild.id):
            jail_role_id, jail_channel_id = data
            
        if ctx.guild.get_role(jail_role_id) is None or ctx.guild.get_channel(jail_channel_id) is None:
            return await ctx.error("The **moderation system** is not set up.")
            
        jail_role = ctx.guild.get_role(jail_role_id)
        jail_channel = ctx.guild.get_channel(jail_channel_id)
            
        if await ctx.can_moderate(member, "jail") is not None:
            return

        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        roles = member.roles.copy()
        await member.remove_roles(
            *(role for role in roles if role.is_assignable()),
            reason=f"Vile Moderation [{ctx.author}]: Member jailed",
            atomic=False
        )
        await asyncio.gather(*(
            self.bot.db.execute("INSERT INTO taken_roles (guild_id, user_id, role_id) VALUES (%s, %s, %s);", ctx.guild.id, member.id, role.id)
            for role in roles
            if role.is_assignable()
        ))
        await member.add_roles(
            jail_role,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        
        await self.bot.db.execute(
            "INSERT INTO jailed_user (guild_id, user_id, unjail_on) VALUES (%s, %s, %s);",
            ctx.guild.id, member.id, datetime.now()+timedelta(seconds=(timespan.seconds if timespan else 2419200))
        )
        
        message_sent = False
        if ctx.parameters.get("silent") is not True:
            try:
                await self.notify(
                    member,
                    title="Jailed",
                    message="You have been jailed in",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                )
                message_sent = True
            except Exception:
                message_sent = False
            
        await self.log_history(
            ctx.guild.id, 
            ctx.author.id, 
            member.id, 
            "Jail", 
            reason
        )
        
        await jail_channel.send(f"{member.mention}, you have been jailed by {ctx.author.mention} for doing something stupid which broke the rules{f', specifically {reason}.' if reason != 'No reason provided' else '.'} {'You can find more information about this warning in your private messages.' if message_sent else ''}")
        return await ctx.success(f"Successfully **jailed** {member.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
        
        
    @commands.command(
        name="unjail",
        aliases=("uj",),
        usage="<member>",
        example="@cop#0666",
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
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(manage_messages=True)
    async def unjail(self, ctx: vile.Context, member: vile.MemberConverter):
        """Unjail the mentioned member"""
        
        if member.id not in await self.bot.db.fetch("SELECT user_id FROM jailed_user WHERE guild_id = %s;", ctx.guild.id):
            return await ctx.error("That member **isn't** jailed.")
            
        jail_role_id = await self.bot.db.fetchval("SELECT jail_role_id FROM guild_settings WHERE guild_id = %s;", ctx.guild.id)
        if jail_role := ctx.guild.get_role(jail_role_id):
            if jail_role in member.roles:
                await member.remove_roles(
                    jail_role,
                    reason="Vile Moderation: Member has been unjailed"
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
            reason="Vile Moderation: Restoring roles taken due to jail",
            atomic=False
        )

        if ctx.parameters.get("silent") is not True:
            asyncio.ensure_future(self.notify(
                member,
                title="Unjailed",
                message="You have been unjailed in",
                guild=ctx.guild,
                moderator=ctx.author,
                reason="No reason provided"
            ))
        
        return await ctx.success(f"Successfully **unjailed** {member.mention}.")
        
        
    @commands.command(
        name="jailed",
        aliases=("jailedlist",)
    )
    @commands.has_permissions(manage_messages=True)
    async def jailed(self, ctx: vile.Context):
        """View every jailed member"""
        
        jailed_members = await self.bot.db.fetch(
            "SELECT user_id FROM jailed_user WHERE guild_id = %s;",
            ctx.guild.id
        )
        if not jailed_members:
            return await ctx.error("There aren't any jailed members.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Jailed Member in {ctx.guild.name}"
        )
        for user_id in jailed_members:
            if member := ctx.guild.get_member(user_id):
                rows.append(f"{member.mention} {member} (`{member.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="moderationhistory",
        aliases=("mh", "modhistory",),
        usage="[member]",
        example="@cop#0666",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_messages=True)
    async def moderationhistory(self, ctx: vile.Context, member: Optional[vile.MemberConverter] = commands.Author):
        """View moderation history for a staff member"""
        
        history = await self.bot.db.execute(
            "SELECT case_id, type, member_id, reason FROM moderation_history WHERE guild_id = %s AND moderator_id = %s ORDER BY case_id DESC;",
            ctx.guild.id, member.id
        )
        if not history:
            return await ctx.error("There is no previously recorded moderation history for that staff member.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Moderation History for {member}"
        )
        for case_id, type, member_id, reason in history:
            if _member := self.bot.get_user(member_id):
                rows.append(f"**Case #{case_id}**\n{self.bot.reply} **Type:** {type}\n{self.bot.reply} **Member:** {_member} (`{_member.id}`)\n{self.bot.reply} **Reason:** {reason}")
                
        return await ctx.paginate((embed, rows), False)
        
        
    @commands.group(
        name="history",
        usage="[member]",
        example="@cop#0666",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_messages=True)
    async def history(self, ctx: vile.Context, member: Optional[vile.MemberConverter] = commands.Author):
        """View a list of every punishment recorded"""
        
        history = await self.bot.db.execute(
            "SELECT case_id, type, moderator_id, reason FROM moderation_history WHERE guild_id = %s AND member_id = %s ORDER BY case_id DESC;",
            ctx.guild.id, member.id
        )
        if not history:
            return await ctx.error("There is no previously recorded punishment history for that member.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Punishment History for {member}"
        )
        for case_id, type, moderator_id, reason in history:
            if moderator := self.bot.get_user(moderator_id):
                rows.append(f"**Case #{case_id}**\n{self.bot.reply} **Type:** {type}\n{self.bot.reply} **Moderator:** {moderator} (`{moderator.id}`)\n{self.bot.reply} **Reason:** {reason}")
                
        return await ctx.paginate((embed, rows), False)
        
        
    @history.group(
        name="remove",
        usage="<member> [case ID]",
        example="@cop#0666 1528",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_messages=True)
    async def history_remove(self, ctx: vile.Context, member: vile.MemberConverter, case_id: int):
        """Remove a punishment from a member"""
        
        history = await self.bot.db.fetchrow(
            "SELECT * FROM moderation_history WHERE guild_id = %s AND member_id = %s AND case_id = %s;",
            ctx.guild.id, member.id, case_id
        )
        if not history:
            return await ctx.error("Please provide a **valid** case ID belonging to that member.")
            
        await self.bot.db.execute(
            "DELETE FROM moderation_history WHERE guild_id = %s AND member_id = %s AND case_id = %s;",
            ctx.guild.id, member.id, case_id
        )
        
        return await ctx.success(f"Successfully **removed** that punishment.")
        
        
    @history_remove.command(
        name="all",
        usage="<member>",
        example="@cop#0666",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_messages=True)
    async def history_remove_all(self, ctx: vile.Context, member: vile.MemberConverter):
        """Remove all punishments from a member"""
        
        history = await self.bot.db.fetchrow(
            "SELECT * FROM moderation_history WHERE guild_id = %s AND member_id = %s LIMIT 1;",
            ctx.guild.id, member.id
        )
        if not history:
            return await ctx.error("There is no previously recorded punishment history for that member.")
            
        await self.bot.db.execute(
            "DELETE FROM moderation_history WHERE guild_id = %s AND member_id = %s;",
            ctx.guild.id, member.id
        )
        
        return await ctx.success(f"Successfully **removed** every punishment.")
        
    
    @commands.command(
        name="reason",
        usage="[case ID] <reason>",
        example="1528 ..."
    )
    @commands.has_permissions(manage_messages=True)
    async def reason(self, ctx: vile.Context, case_id: Optional[int] = None, *, reason: str):
        """Update the reason on a case log"""
        
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
        
        case_id = case_id or await self.bot.db.fetchval(
            "SELECT MAX(case_id) FROM moderation_history WHERE guild_id = %s AND moderator_id = %s;",
            ctx.guild.id, ctx.author.id
        ) or 0
        if not await self.bot.db.fetchrow("SELECT * FROM moderation_history WHERE guild_id = %s AND moderator_id = %s AND case_id = %s;", ctx.guild.id, ctx.author.id, case_id):
            return await ctx.error("Please provide a **valid** case ID.")
            
        await self.bot.db.execute(
            "UPDATE moderation_history SET reason = %s WHERE case_id = %s;",
            reason, case_id
        )
        
        return await ctx.success("Successfully **updated** the reason for that case log.")
        
        
    @commands.command(
        name="timeout",
        aliases=("tm",),
        usage="<member> [time d/h/m/s] [reason]",
        example="@cop#0666 10m Breaking the rules",
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
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def timeout(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter,
        timespan: Optional[vile.Timespan] = None,
        *,
        reason: str = "No reason provided"
    ):
        """Timeout the mentioned member"""
        
        if await ctx.can_moderate(member, "timeout") is not None:
            return

        if timespan.seconds < 1 or timespan.seconds > 2.419e+6:
            return await ctx.error("Please provide a **valid** timespan between 1 second and 4 weeks.")
            
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await member.timeout(
            datetime.now().astimezone() + timedelta(seconds=(timespan.seconds if timespan else 3600)),
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        
        if isinstance(member, discord.Member):
            if ctx.parameters.get("silent") == False:
                asyncio.ensure_future(self.notify(
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
            
        return await ctx.success(f"Successfully **timed out** {member.mention} for `{vile.fmtseconds(timespan.seconds if timespan else 3600)}`.")
        
        
    @commands.group(
        name="untimeout",
        aliases=("utm",),
        usage="<member>",
        example="@cop#0666",
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
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx: vile.Context, member: vile.MemberConverter):
        """Untimeout the mentioned member"""
        
        if await ctx.can_moderate(member, "untimeout") is not None:
            return
            
        if member.timed_out_until is None:
            return await ctx.error("That member **isn't** timed out.")

        await member.timeout(
            None,
            reason=f"Vile Moderation [{ctx.author}]"
        )
        
        if isinstance(member, discord.Member):
            if ctx.parameters.get("silent") == False:
                asyncio.ensure_future(self.notify(
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
            reason
        )
            
        return await ctx.success(f"Successfully **revoked** {member.mention}'s timeout.")
        
    
    @untimeout.command(
        name="all"
    )
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def untimeout_all(self, ctx: vile.Context):
        """Untimeout every timed out member"""
        
        timed_out = tuple(member for member in ctx.guild.members if member.timed_out_until is not None and (ctx.guild.roles.index(member.top_role) < ctx.guild.roles.index(ctx.me.top_role) if member.top_role else True))
            
        await asyncio.gather(*(
            member.timeout(None)
            for member in timed_out
        ))
        
        return await ctx.success(f"Successfully **revoked** `{len(timed_out)}` timeouts.")
        
        
    @commands.command(
        name="mute",
        aliases=("m",),
        usage="<member> [time d/h/m/s] [reason]",
        example="@cop#0666 10m Breaking the rules",
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
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(manage_messages=True)
    async def mute(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter, 
        timespan: Optional[vile.Timespan] = None, 
        *, 
        reason: str = "No reason provided"
    ):
        """Mute the mentioned member"""
        
        if member.id in await self.bot.db.fetch("SELECT user_id FROM muted_user WHERE guild_id = %s;", ctx.guild.id):
            return await ctx.error("That member is **already** muted.")

        if timespan.seconds < 1 or timespan.seconds > 2.419e+6:
            return await ctx.error("Please provide a **valid** timespan between 1 second and 4 weeks.")
            
        mute_role_id = 0
        if data := await self.bot.db.fetchval("SELECT mute_role_id FROM guild_settings WHERE guild_id = %s;", ctx.guild.id):
            mute_role_id = data
            
        if ctx.guild.get_role(mute_role_id) is None:
            return await ctx.error("The **moderation system** is not set up.")
            
        mute_role = ctx.guild.get_role(mute_role_id)
            
        if await ctx.can_moderate(member, "mute") is not None:
            return

        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        roles = member.roles.copy()
        await member.remove_roles(
            *(role for role in roles if role.is_assignable()),
            reason=f"Vile Moderation [{ctx.author}]: Member muted",
            atomic=False
        )
        await asyncio.gather(*(
            self.bot.db.execute("INSERT INTO taken_roles (guild_id, user_id, role_id) VALUES (%s, %s, %s);", ctx.guild.id, member.id, role.id)
            for role in roles
            if role.is_assignable()
        ))
        await member.add_roles(
            mute_role,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        
        await self.bot.db.execute(
            "INSERT INTO muted_user (guild_id, user_id, unmute_on) VALUES (%s, %s, %s);",
            ctx.guild.id, member.id, datetime.now()+timedelta(seconds=(timespan.seconds if timespan else 2419200))
        )
        
        message_sent = False
        if ctx.parameters.get("silent") is not True:
            asyncio.ensure_future(self.notify(
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
        
        return await ctx.success(f"Successfully **muted** {member.mention} for `{vile.fmtseconds(timespan.seconds if timespan else 2419200)}`.")
        
        
    @commands.group(
        name="unmute",
        aliases=("um",),
        usage="<member>",
        example="@cop#0666",
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
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx: vile.Context, member: vile.MemberConverter):
        """Unmute the mentioned member"""
        
        if member.id not in await self.bot.db.fetch("SELECT user_id FROM muted_user WHERE guild_id = %s;", ctx.guild.id):
            return await ctx.error("That member **isn't** muted.")
            
        mute_role_id = await self.bot.db.fetchval("SELECT mute_role_id FROM guild_settings WHERE guild_id = %s;", ctx.guild.id)
        if mute_role := ctx.guild.get_role(mute_role_id):
            if mute_role in member.roles:
                await member.remove_roles(
                    mute_role,
                    reason="Vile Moderation: Member has been unmuted"
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
            reason="Vile Moderation: Restoring roles taken due to mute",
            atomic=False
        )

        if ctx.parameters.get("silent") is not True:
            asyncio.ensure_future(self.notify(
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
            reason
        )
        
        return await ctx.success(f"Successfully **unmuted** {member.mention}.")
        
        
    @unmute.command(
        name="all"
    )
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def unmute_all(self, ctx: vile.Context):
        """Unmute every muted member"""
        
        muted = await self.bot.db.fetch(
            "SELECT user_id FROM muted_user WHERE guild_id = %s;",
            ctx.guild.id
        )
            
        await asyncio.gather(*[
            self.bot.db.execute(
                "DELETE FROM muted_user WHERE guild_id = %s AND user_id = %s;",
                ctx.guild.id, member.id
            )
            for member in ctx.guild.members
            if member.id in muted
        ])
        
        return await ctx.success(f"Successfully **unmuted** `{len(muted)}` members.")
        
        
    @commands.command(
        name="muted",
        aliases=("mutedlist",)
    )
    @commands.has_permissions(manage_messages=True)
    async def muted(self, ctx: vile.Context):
        """View every muted member"""
        
        muted_members = await self.bot.db.fetch(
            "SELECT user_id FROM muted_user WHERE guild_id = %s;",
            ctx.guild.id
        )
        if not muted_members:
            return await ctx.error("There aren't any muted members.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Muted Members in {ctx.guild.name}"
        )
        for user_id in muted_members:
            if member := ctx.guild.get_member(user_id):
                rows.append(f"{member.mention} {member} (`{member.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.command(
        name="timedout",
        aliases=("timedoutlist",)
    )
    @commands.has_permissions(manage_messages=True)
    async def timedout(self, ctx: vile.Context):
        """View every timed out member"""
        
        timed_out_members = tuple(m for m in ctx.guild.members if m.timed_out_until)
        if not timed_out_members:
            return await ctx.error("There aren't any timed out members.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Timed Out Members in {ctx.guild.name}"
        )
        for user_id in timed_out_members:
            if member := ctx.guild.get_member(user_id):
                rows.append(f"{member.mention} {member} (`{member.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.command(
        name="imute",
        aliases=("imagemute",),
        usage="<member> [reason]",
        example="@cop#0666 Breaking the rules",
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
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_messages=True)
    async def imute(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter,
        *, 
        reason: str = "No reason provided"
    ):
        """Image mute the mentioned member"""
        
        if await ctx.can_moderate(member, "image mute") is not None:
            return
            
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await asyncio.gather(*(
            channel.set_permissions(
                member,
                overwrite=discord.PermissionOverwrite(attach_files=False, embed_links=False)
            )
            for channel in ctx.guild.text_channels
            if channel.permissions_for(member).attach_files is True
            or channel.permissions_for(member).embed_links is True
        ))
        
        if ctx.parameters.get("silent") == False:
            asyncio.ensure_future(self.notify(
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
        
        
    @commands.command(
        name="iunmute",
        aliases=("imageunmute",),
        usage="<member>",
        example="@cop#0666"
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_messages=True)
    async def iunmute(self, ctx: vile.Context, member: vile.MemberConverter):
        """Revoke the mentioned member's image mute"""
            
        await asyncio.gather(*(
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
        
        
    @commands.command(
        name="rmute",
        aliases=("reactionmute",),
        usage="<member> [reason]",
        example="@cop#0666 Breaking the rules",
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
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_messages=True)
    async def rmute(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter,
        *, 
        reason: str = "No reason provided"
    ):
        """Reaction mute the mentioned member"""
        
        if await ctx.can_moderate(member, "reaction mute") is not None:
            return
            
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await asyncio.gather(*(
            channel.set_permissions(
                member,
                overwrite=discord.PermissionOverwrite(attach_files=False, embed_links=False)
            )
            for channel in ctx.guild.text_channels
            if channel.permissions_for(member).attach_files is True
            or channel.permissions_for(member).embed_links is True
        ))
        
        if ctx.parameters.get("silent") == False:
            asyncio.ensure_future(self.notify(
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
        
        
    @commands.command(
        name="runmute",
        aliases=("reactionunmute",),
        usage="<member>",
        example="@cop#0666"
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_messages=True)
    async def runmute(self, ctx: vile.Context, member: vile.MemberConverter):
        """Revoke the mentioned member's reaction mute"""
            
        await asyncio.gather(*(
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
        
        
    @commands.group(
        name="notes",
        usage="[member]",
        example="@cop#0666",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_messages=True)
    async def notes(
        self, 
        ctx: vile.Context, 
        *, 
        member: Optional[vile.MemberConverter] = commands.Author
    ):
        """View a member's notes"""
        
        notes = await self.bot.db.execute(
            "SELECT note_id, note FROM notes WHERE guild_id = %s AND user_id = %s ORDER BY note_id DESC;",
            ctx.guild.id, member.id
        )
        if not notes:
            return await ctx.error("There are no notes for that member.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Notes for {member}"
        )
        for note_id, note in notes:
            rows.append(f"**Note #{note_id}**\n{note}")
                
        return await ctx.paginate((embed, rows), False)
        
    
    @notes.command(
        name="add",
        usage="<member> <note>",
        example="@cop#0666 very very dumb"
    )
    @commands.has_permissions(manage_messages=True)
    async def notes_add(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter, 
        *, 
        note: str
    ):
        """Add a note to a member"""
        
        if note in await self.bot.db.fetch("SELECT note FROM notes WHERE guild_id = %s AND user_id = %s;", ctx.guild.id, member.id):
            return await ctx.error("That is **already** a note for that member.")
            
        if len(note) > 64:
            return await ctx.error("Please provide a **valid** note under 64 characters.")
            
        note_id = await self.bot.db.fetchval(
            "SELECT MAX(note_id) FROM notes WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, member.id
        ) or 0
        
        await self.bot.db.execute(
            "INSERT INTO notes (guild_id, user_id, note, note_id) VALUES (%s, %s, %s, %s);",
            ctx.guild.id, member.id, note, note_id+1
        )
        
        return await ctx.error(f"Successfully **added** that note to {member.mention}.")
        
        
    @notes.command(
        name="remove",
        aliases=("delete",),
        usage="<member> <note ID>",
        example="@cop#0666 2"
    )
    @commands.has_permissions(manage_messages=True)
    async def notes_remove(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter, 
        note_id: int
    ):
        """Remove a note from a member"""
        
        if note_id not in await self.bot.db.fetch("SELECT note_id FROM notes WHERE guild_id = %s AND user_id = %s;", ctx.guild.id, member.id):
            return await ctx.error("Please provide a **valid** note ID for that member.")
        
        await self.bot.db.execute(
            "DELETE FROM notes WHERE guild_id = %s AND user_id = %s AND note_id = %s;",
            ctx.guild.id, member.id, note_id
        )
        
        return await ctx.error(f"Successfully **removed** that note from {member.mention}.")
        
    
    @notes.command(
        name="clear",
        aliases=("removeall",),
        usage="<member>",
        example="@cop#0666"
    )
    @commands.has_permissions(manage_messages=True)
    async def notes_clear(self, ctx: vile.Context, member: vile.MemberConverter):
        """Remove every note from a member"""
        
        if not await self.bot.db.fetchrow("SELECT note FROM notes WHERE guild_id = %s AND user_id = %s LIMIT 1;", ctx.guild.id, member.id):
            return await ctx.error("That member doesn't have any notes.")
        
        await self.bot.db.execute(
            "DELETE FROM notes WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, member.id
        )
        
        return await ctx.error(f"Successfully **cleared** every note from {member.mention}.")
        
        
    @commands.command(
        name="hardban",
        usage="<member> [reason]",
        example="@cop#0666 Breaking the rules",
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
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(administrator=True)
    async def hardban(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter,
        *, 
        reason: str = "No reason provided"
    ):
        """Permanently ban the mentioned member"""
        
        if await self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            return await ctx.error("This resource is being **rate limited**.")
        
        if await ctx.can_moderate(member, "hard ban") is not None:
            return
            
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await ctx.guild.ban(
            member,
            delete_message_days=0,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        await self.bot.db.execute(
            "INSERT INTO hard_banned (guild_id, user_id) VALUES (%s, %s);",
            ctx.guild.id, member.id
        )
        
        if ctx.parameters.get("silent") is not True:
            asyncio.ensure_future(self.notify(
                member,
                title="Hard Banned",
                message="You have been permanently banned from",
                guild=ctx.guild,
                moderator=ctx.author,
                reason=reason
            ))
            
        return await ctx.success(f"Successfully **banned** {member.mention} permanently for {'no reason' if reason == 'No reason provided' else reason}.")
        
        
    @commands.command(
        name="hardunban",
        usage="<member>",
        example="@cop#0666",
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
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(administrator=True)
    async def hardunban(self, ctx: vile.Context, user: vile.UserConverter):
        """Revoke the mentioned user's hard ban"""
            
        await ctx.guild.unban(
            user,
            reason=f"Vile Moderation [{ctx.author}]: Hard ban has been revoked"
        )
        await self.bot.db.execute(
            "DELETE FROM hard_banned WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, member.id
        )
        
        if ctx.parameters.get("silent") is not True:
            asyncio.ensure_future(self.notify(
                member,
                title="Unbanned",
                message="You have been unbanned from",
                guild=ctx.guild,
                moderator=ctx.author,
                reason="N/A"
            ))
            
        return await ctx.success(f"Successfully **unbanned** {member.mention}.")
        
        
    @commands.command(
        name="hardbanned",
        aliases=("hardbannedlist",)
    )
    @commands.has_permissions(manage_messages=True)
    async def hardbanned(self, ctx: vile.Context):
        """View every hard banned user"""
        
        hard_banned_users = await self.bot.db.fetch(
            "SELECT user_id FROM hard_banned WHERE guild_id = %s;",
            ctx.guild.id
        )
        if not hard_banned_users:
            return await ctx.error("There aren't any hard banned users.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Hard Banned Users in {ctx.guild.name}"
        )
        for user_id in hard_banned_users:
            if user := ctx.guild.get_member(user_id):
                rows.append(f"{user.mention} {user} (`{user.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.command(
        name="deleteinvites",
        aliases=("clearinvites",)
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def clearinvites(self, ctx: vile.Context):
        """Delete every invite in the server"""
        
        invites = await ctx.guild.invites()
        if not invites:
            return await ctx.error("There aren't any invites in this server.")
            
        await asyncio.gather(*(invite.delete() for invite in invites))
        return await ctx.success("Successfully **deleted** every invite in this server.")
        
        
    @commands.command(
        name="drag",
        aliases=("move",),
        usage="<members> <voice channel>",
        example="@cop#0001 @cop#0666 #Main Voice"
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(move_members=True)
    async def drag(
        self,
        ctx: vile.Context,
        members: commands.Greedy[vile.MemberConverter],
        *,
        channel: discord.VoiceChannel
    ):
        """Drag member(s) to a voice channel"""
        
        if not members:
            return await ctx.send_help(ctx.command.qualified_name)
            
        if ctx.author.voice is None:
            return await ctx.error("You must be connected to a voice channel.")
            
        await asyncio.gather(*(
            member.move_to(channel)
            for member in members
            if member.voice
        ))
        
        return await ctx.success(f"Successfully **dragged** those members to {channel.mention}.")
            
        
    @commands.group(
        name="unbanall",
        aliases=("massunban",),
        invoke_without_command=True
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(administrator=True)
    async def unbanall(self, ctx: vile.Context):
        """Unban every banned user"""
        
        if ctx.guild.id in self.tasks["unban_all"]:
            return await ctx.error("There is already a running unban all task.")
        
        self.tasks["unban_all"][ctx.guild.id] = 1
        unbanned = 0
        
        async for ban in ctx.guild.bans(limit=1000):
            if self.tasks["unban_all"][ctx.guild.id] == 0:
                del self.tasks["unban_all"][ctx.guild.id]
                return await ctx.error("This task was cancelled.")
                
            await ctx.guild.unban(
                ban.user,
                reason="Vile Moderation [{ctx.author}]: Unbanning all users"
            )
            unbanned += 1
            
            await asyncio.sleep(1.25)
            
        del self.tasks["unban_all"][ctx.guild.id]
        return await ctx.success(f"Successfully **unbanned** {unbanned:,} users.")
        
    
    @unbanall.command(
        name="cancel",
        aliases=("stop",)
    )
    @commands.has_permissions(administrator=True)
    async def unbanall_cancel(self, ctx: vile.Context):
        """Cancel a running unban all task"""
        
        if ctx.guild.id not in self.tasks["unban_all"]:
            return await ctx.error("There isn't a running unban all task.")
            
        self.tasks["unban_all"][ctx.guild.id] = 0
        return await ctx.error("Successfully **cancelled** the running unban all task.")
        
        
    @commands.command(
        name="ban",
        aliases=("b",),
        usage="<member> [delete days 0/1/7] [reason]",
        example="@cop#0666 Breaking the rules",
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
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, 
        ctx: vile.Context, 
        user: Union[vile.UserConverter, vile.MemberConverter],
        days: Optional[Literal[0, 1, 7]] = 0,
        *, 
        reason: str = "No reason provided"
    ):
        """Ban the mentioned member"""
        
        if await self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            return await ctx.error("This resource is being **rate limited**.")
        
        if isinstance(user, discord.Member) and await ctx.can_moderate(user, "ban") is not None:
            return
            
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await ctx.guild.ban(
            user,
            delete_message_seconds=days*86400,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        
        if isinstance(user, discord.Member):
            if ctx.parameters.get("silent") == False:
                asyncio.ensure_future(self.notify(
                    user,
                    title="Banned",
                    message="You have been banned from",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
            
        return await ctx.success(f"Successfully **banned** {user.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
  
              
    @commands.command(
        name="unban",
        aliases=("ub",),
        usage="<user>",
        example="@cop#0666",
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
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: vile.Context, user: vile.UserConverter):
        """Unban the mentioned user"""
        
        if await self.bot.db.execute("SELECT * FROM hard_banned WHERE guild_id = %s AND user_id = %s;", ctx.guild.id, user.id):
            return await ctx.error("That user is hard banned.")

        async for ban in ctx.guild.bans():
            if ban.user.id == user.id:
                await ctx.guild.unban(
                    user,
                    reason=f"Vile Moderation [{ctx.author}]"
                )
                break
                
        else:
            return await ctx.error("That user isn't banned.")
        
        if ctx.parameters.get("silent") == False:
            asyncio.ensure_future(self.notify(
                user,
                title="Unbanned",
                message="You have been unbanned from",
                guild=ctx.guild,
                moderator=ctx.author,
                reason="N/A"
            ))
            
        return await ctx.success(f"Successfully **unbanned** {user.mention}.")
        
        
    @commands.command(
        name="softban",
        aliases=("sb",),
        usage="<member> <delete days 0/1/7> [reason]",
        example="@cop#0666 Breaking the rules",
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
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def softban(
        self, 
        ctx: vile.Context, 
        member: vile.MemberConverter,
        days: Optional[Literal[0, 1, 7]] = 0,
        *, 
        reason: str = "No reason provided"
    ):
        """Soft ban the mentioned member"""
        
        if await self.bot.cache.ratelimited(f"rl:bans{ctx.guild.id}", 15, 300):
            return await ctx.error("This resource is being **rate limited**.")
        
        if await ctx.can_moderate(member, "soft ban") is not None:
            return
            
        reason = vile.strip_flags(reason, ctx)
        if not reason:
            reason = "No reason provided"
            
        if len(reason) > 64:
            return await ctx.error("Please provide a **valid** reason under 64 characters.")
            
        await ctx.guild.ban(
            member,
            delete_message_seconds=days*86400,
            reason=f"Vile Moderation [{ctx.author}]: {reason}"
        )
        await ctx.guild.unban(
            member,
            reason=f"Vile Moderation [{ctx.author}]: User was soft banned"
        )
        
        if isinstance(user, discord.Member):
            if ctx.parameters.get("silent") == False:
                asyncio.ensure_future(self.notify(
                    member,
                    title="Soft Banned",
                    message="You have been soft banned from",
                    guild=ctx.guild,
                    moderator=ctx.author,
                    reason=reason
                ))
            
        return await ctx.success(f"Successfully **soft banned** {member.mention} for {'no reason' if reason == 'No reason provided' else reason}.")
        
    
    @commands.command(
        name="banned",
        usage="<user>",
        example="@cop#0666"
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def banned(self, ctx: vile.Context, *, user: vile.UserConverter):
        """Check if a user is banned"""
        
        async for ban in ctx.guild.bans():
            if ban.user.id == user.id:
                return await ctx.success(f"{user} (`{user.id}`) is banned.")
                
        return await ctx.error(f"{user} (`{user.id}`) is not banned.")
        
        
    @commands.group(
        name="role",
        aliases=("r",),
        usage="<member> <roles>",
        example="@cop#0666 @Staff @Moderator",
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx: vile.Context, member: vile.MemberConverter, *roles: vile.RoleConverter):
        """Update a member's roles"""
        
        if await ctx.can_moderate(member, "role") is not None:
            return
            
        if len(roles) > 10:
            return await ctx.error("You can only add or remove 10 roles at a time.")

        _added = tuple(role for role in roles if role not in member.roles and role.is_assignable())
        _removed = tuple(role for role in roles if role in member.roles and role.is_assignable())
        
        if not _added and not _removed:
            return await ctx.error("I can't assign any of those roles.")
        
        await member.add_roles(
            *_added,
            reason=f"Vile Moderation [{ctx.author}]"
        )
        await member.remove_roles(
            *_removed,
            reason=f"Vile Moderation [{ctx.author}]"
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
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_add(self, ctx: vile.Context):
        """Add a role to all of an object (bots/humans/inrole/all)"""
        return await ctx.send_help(ctx.command.qualified_name)


    @role_add.command(
        name="bots",
        usage="<role>",
        example="Bot"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_add_bots(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Add a role to all bots"""
        
        
        if ctx.guild.id in self.tasks["role"]:
            return await ctx.error("There is already a running mass role task.")

        if not role.is_assignable():
            return await ctx.error("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if member.bot and role not in member.roles)
        if not members:
            return await ctx.error("There aren't any bots without that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                return await ctx.error("This task was canceled.")

            try:
                await member.add_roles(
                    role,
                    reason=f"Vile Moderation [{ctx.author}]: Mass role (bots)"
                )
                if members.index(member) != len(members)-1:
                    await asyncio.sleep(1)
            
            except discord.Forbidden:
                return await ctx.error("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **added** {role.mention} to all bots.")


    @role_add.command(
        name="humans",
        usage="<role>",
        example="Member"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_add_humans(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Add a role to all humans"""
        
        
        if ctx.guild.id in self.tasks["role"]:
            return await ctx.error("There is already a running mass role task.")

        if not role.is_assignable():
            return await ctx.error("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if member.bot is False and role not in member.roles)
        if not members:
            return await ctx.error("There aren't any humans without that role.")
        
        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in ctx.guild.members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                return await ctx.error("This task was canceled.")

            try:
                await member.add_roles(
                    role,
                    reason=f"Vile Moderation [{ctx.author}]: Mass role (humans)"
                )
                if ctx.guild.members.index(member) != len(ctx.guild.members)-1:
                    await asyncio.sleep(1)
            
            except discord.Forbidden:
                return await ctx.error("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **added** {role.mention} to all humans.")


    @role_add.command(
        name="all",
        usage="<role>",
        example="..."
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_add_all(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Add a role to all members"""
        
        
        if ctx.guild.id in self.tasks["role"]:
            return await ctx.error("There is already a running mass role task.")

        if not role.is_assignable():
            return await ctx.error("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if role not in member.roles)
        if not members:
            return await ctx.error("There aren't any members without that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                return await ctx.error("This task was canceled.")

            try:
                await member.add_roles(
                    role,
                    reason=f"Vile Moderation [{ctx.author}]: Mass role (all)"
                )
                if ctx.guild.members.index(member) != len(ctx.guild.members)-1:
                    await asyncio.sleep(1)
            
            except discord.Forbidden:
                return await ctx.error("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **added** {role.mention} to all members.")


    @role_add.command(
        name="has",
        aliases=("inrole",),
        usage="<has> <role>",
        example="Supporter VIP"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_add_has(self, ctx: vile.Context, has: vile.RoleConverter, *, role: vile.RoleConverter):
        """Add a role to all members in a specific role"""
        
        
        if ctx.guild.id in self.tasks["role"]:
            return await ctx.error("There is already a running mass role task.")

        if not role.is_assignable():
            return await ctx.error("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if has in member.roles and role not in member.roles)
        if not members:
            return await ctx.error("There aren't any members in the provided role, or there aren't any members without the role I'm supposed to give.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                return await ctx.error("This task was canceled.")

            try:
                await member.add_roles(
                    role,
                    reason=f"Vile Moderation [{ctx.author}]: Mass role (inrole)"
                )
                if members.index(member) != len(members)-1:
                    await asyncio.sleep(1)
            
            except discord.Forbidden:
                return await ctx.error("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **added** {role.mention} to all members.")

    
    @role.group(
        name="remove",
        usage="<sub command>",
        example="bots Bot",
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_remove(self, ctx: vile.Context):
        """Remove a role from all of an object (bots/humans/inrole/all)"""
        return await ctx.send_help(ctx.command.qualified_name)


    @role_remove.command(
        name="bots",
        usage="<role>",
        example="Bot"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_remove_bots(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Remove a role from all bots"""
        
        
        if ctx.guild.id in self.tasks["role"]:
            return await ctx.error("There is already a running mass role task.")

        if not role.is_assignable():
            return await ctx.error("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if member.bot and role in member.roles)
        if not members:
            return await ctx.error("There aren't any bots with that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                return await ctx.error("This task was canceled.")
            try:
                await member.remove_roles(
                    role,
                    reason=f"Vile Moderation [{ctx.author}]: Mass role (bots)"
                )
                if members.index(member) != len(members)-1:
                    await asyncio.sleep(1)
            
            except discord.Forbidden:
                return await ctx.error("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **removed** {role.mention} from all bots.")


    @role_remove.command(
        name="humans",
        usage="<role>",
        example="Member"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_remove_humans(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Remove a role from all humans"""
        
        
        if ctx.guild.id in self.tasks["role"]:
            return await ctx.error("There is already a running mass role task.")

        if not role.is_assignable():
            return await ctx.error("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if member.bot is False and role in member.roles)
        if not members:
            return await ctx.error("There aren't any humans with that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                return await ctx.error("This task was canceled.")

            try:
                await member.remove_roles(
                    role,
                    reason=f"Vile Moderation [{ctx.author}]: Mass role remove (humans)"
                )
                if members.index(member) != len(members)-1:
                    await asyncio.sleep(1)
            
            except discord.Forbidden:
                return await ctx.error("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **removed** {role.mention} from all humans.")


    @role_remove.command(
        name="all",
        usage="<role>",
        example="..."
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_remove_all(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Remove a role from all members"""
        
        
        if ctx.guild.id in self.tasks["role"]:
            return await ctx.error("There is already a running mass role task.")

        if not role.is_assignable():
            return await ctx.error("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if role in member.roles)
        if not members:
            return await ctx.error("There aren't any members with that role.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                return await ctx.error("This task was canceled.")

            try:
                await member.remove_roles(
                    role,
                    reason=f"Vile Moderation [{ctx.author}]: Mass role remove (all)"
                )
                if members.index(member) != len(members)-1:
                    await asyncio.sleep(1)
            
            except discord.Forbidden:
                return await ctx.error("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **removed** {role.mention} from all members.")


    @role_remove.command(
        name="has",
        aliases=("inrole",),
        usage="<has> <role>",
        example="Supporter VIP"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def role_remove_has(self, ctx: vile.Context, has: vile.RoleConverter, *, role: vile.RoleConverter):
        """Remove a role from all members in a specific role"""
        
        
        if ctx.guild.id in self.tasks["role"]:
            return await ctx.error("There is already a running mass role task.")

        if not role.is_assignable():
            return await ctx.error("I can't assign that role.")

        members = tuple(member for member in ctx.guild.members if has in member.roles and role in member.roles)
        if not members:
            return await ctx.error("There aren't any members in the provided role, or there aren't any members with the role I'm supposed to remove.")

        self.tasks["role"][ctx.guild.id] = 1
        roled = 0

        for member in members:
            if self.tasks["role"][ctx.guild.id] == 0:
                del self.tasks["role"][ctx.guild.id]
                return await ctx.error("This task was canceled.")

            try:
                await member.remove_roles(
                    role,
                    reason=f"Vile Moderation [{ctx.author}]: Mass role remove (inrole)"
                )
                if members.index(member) != len(members)-1:
                    await asyncio.sleep(1)
            
            except discord.Forbidden:
                return await ctx.error("I no longer have the permissions to complete this task.")

        del self.tasks["role"][ctx.guild.id]
        return await ctx.success(f"Successfully **removed** {role.mention} from all members.")


    @role.command(
        name="cancel",
        aliases=("stop",)
    )
    @commands.has_permissions(administrator=True)
    async def role_cancel(self, ctx: vile.Context):
        """Cancel a running mass role task"""
        
        if ctx.guild.id not in self.tasks["role"]:
            return await ctx.error("There isn't a running mass role task.")
            
        self.tasks["role"][ctx.guild.id] = 0
        return await ctx.error("Successfully **cancelled** the running mass role task.")


    @role.command(
        name="create",
        aliases=("make",),
        usage="<color> <name>",
        example="#0000FF Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_create(self, ctx: vile.Context, color: vile.HexConverter, *, name: str) -> None:
        """Create a role"""

        if len(name) > 32:
            return await ctx.error("Please provide a **valid** name under 32 characters.")

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
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_create(self, ctx: vile.Context, *, role: vile.RoleConverter) -> None:
        """Delete a role"""

        if role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        await role.delete(reason=f"Vile Moderation [{ctx.author}]")
        return await ctx.success(f"Successfully **deleted** {role.mention}.")


    @role.command(
        name="icon",
        aliases=("image",),
        usage="<image> <role>",
        example="... Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_icon(
        self, 
        ctx: vile.Context, 
        source: Union[discord.Emoji, discord.PartialEmoji, vile.AttachmentConverter], 
        *, 
        role: vile.RoleConverter
    ):
        """Set a role's icon"""

        if role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        if hasattr(source, "url"):
            source = source.url

        try:
            image_bytes = await self.bot.proxied_session.read(source)
            await role.edit(display_icon=image_bytes)

        except discord.Forbidden:
            return await ctx.error("I can't manage that role's display icon.")
            
        except Exception:
            if not ctx.message.attachments or source != ctx.message.attachments[0].url:
                if not await self.bot.is_owner(ctx.author):
                    if await self.bot.cache.ratelimited(f"globalrl:suspicious_urls{source}", 3, 86400):
                        return await self.bot.blacklist(ctx.author.id, type=1)
                    
            return await ctx.error("Please provide a **valid** image.")

        return await ctx.success(f"Successfully **updated** that role's [**icon**]({source}).")


    @role.command(
        name="mentionable",
        aliases=("pingable",),
        usage="<role>",
        example="... Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_mentionable(self, ctx: vile.Context, *, role: vile.RoleConverter) -> None:
        """Toggle mentioning a role"""

        if role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        await role.edit(mentionable=role.mentionable is False)
        return await ctx.success(f"Successfully **toggled** mentioning {role.mention}.")


    @role.command(
        name="topcolor",
        aliases=("highestcolor", "tc",),
        usage="<color> <member>",
        example="#0000FF Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_topcolor(self, ctx: vile.Context, color: vile.HexConverter, *, member: vile.MemberConverter = commands.Author) -> None:
        """Change your highest role's color"""

        if member.top_role is None:
            return await ctx.error("That member does not have any roles.")

        if member.top_role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        await member.top_role.edit(color=color)
        return await ctx.success(f"Successfully **set** {member.mention}'s top role color to `#{hex(color)[2:]}`.")


    @role.command(
        name="color",
        aliases=("colour",),
        usage="<color> <role>",
        example="#0000FF Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_color(self, ctx: vile.Context, color: vile.HexConverter, *, role: vile.RoleConverter) -> None:
        """Change a role's color"""

        if role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        await role.edit(color=color)
        return await ctx.success(f"Successfully **set** {role.mention}'s color to `#{hex(color)[2:]}`.")


    @role.command(
        name="hoist",
        aliases=("visible",),
        usage="<role>",
        example="... Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_hoist(self, ctx: vile.Context, *, role: vile.RoleConverter) -> None:
        """Toggle hoisting a role"""

        if role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        await role.edit(hoist=role.hoist is False)
        return await ctx.success(f"Successfully **toggled** hoisting {role.mention}.")


    @role.command(
        name="name",
        aliases=("setname",),
        usage="<role> <name>",
        example="#0000FF Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_name(self, ctx: vile.Context, role: vile.RoleConverter, *, name: str) -> None:
        """Change a role's name"""

        if len(name) > 32:
            return await ctx.error("Please provide a **valid** name under 32 characters.")

        if role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        await role.edit(name=name)
        return await ctx.success(f"Successfully **set** {role.mention}'s name to `{name}`.")


    @role.command(
        name="restore",
        usage="<member>",
        example="@cop#0666"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_restore(self, ctx: vile.Context, *, member: vile.MemberConverter) -> None:
        """Restore a member's role"""

        if await ctx.can_moderate(member, "role") is not None:
            return

        roles = await self.bot.cache.smembers(f"restore{ctx.guild.id}-{member.id}")
        if not roles:
            return await ctx.error("There are no roles to restore.")

        await member.add_roles(
            *(role for role in roles if role not in member.roles and role.is_assignable()),
            reason="Vile Moderation: Restoring member's roles",
            atomic=False
        )
        await self.bot.cache.srem(f"restore{ctx.guild.id}-{member.id}", *roles)

        return await ctx.success(f"Successfully **restored** {member.mention}'s roles.")


    @role.command(
        name="position",
        aliases=("pos",),
        usage="<position> <role>",
        example="1 Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_position(self, ctx: vile.Context, position: int, *, role: vile.RoleConverter) -> None:
        """Set a role's position"""

        if role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        try:
            await role.edit(position=position)
        except ValueError:
            return await ctx.error("Please provide a **valid** permission.")

        return await ctx.success(f"Successfully **set** {role.mention}'s position to {role.position}.")


    @role.command(
        name="permissions",
        aliases=("perms",),
        usage="<permissions> <role>",
        example="8 Lab Rat"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role_permissions(self, ctx: vile.Context, permissions: int, *, role: vile.RoleConverter) -> None:
        """Update a role's permissions"""

        if role.is_assignable() is False:
            return await ctx.error("I can't manage that role.")

        if not any(map(lambda t: t[1], iter(discord.Permissions(permissions)))):
            return await ctx.error("Please provide a **valid** permission.")
        
        await role.edit(permissions=discord.Permissions(permissions))
        return await ctx.success(f"Successfully **updated** {role.mention}'s permissions.")


    @commands.group(
        name="purge",
        aliases=("clear", "c",),
        usage="[member], <amount>",
        example="matches nigg.*? 100",
        invoke_without_command=True
    )
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(
        self, 
        ctx: vile.Context, 
        member: Optional[vile.MemberConverter],
        amount: int
    ):
        """Clear messages in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: (member or m.author).id == m.author.id,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_matches(self, ctx: vile.Context, expression: str, amount: int):
        """Clear messages matching an expression in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        try:
            cleared_messages = await ctx.channel.purge(
                limit=amount+1,
                check=lambda m: re.findall(expression.lower(), m.content.lower()),
                reason=f"Vile Moderation [{ctx.author}]"
            )

        except re.error:
            del self.tasks["purge"][ctx.guild.id]
            return await ctx.error("Please provide a **valid** expression.")

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_humans(self, ctx: vile.Context, amount: int):
        """Clear messages from humans in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: not m.author.bot,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_bots(self, ctx: vile.Context, amount: int):
        """Clear messages from bots in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: m.author.bot,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_after(self, ctx: vile.Context, *, message: vile.MessageConverter):
        """Clear messages sent after the specified message"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        cleared_messages = await ctx.channel.purge(
            limit=None,
            after=message.created_at,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_stickers(self, ctx: vile.Context, amount: int):
        """Clear messages with stickers in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: m.stickers,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_attachments(self, ctx: vile.Context, amount: int):
        """Clear messages with attachments in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: m.attachments,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_emojis(self, ctx: vile.Context, amount: int):
        """Clear messages with emojis in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: m.emojis,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_mentions(self, ctx: vile.Context, amount: int):
        """Clear messages with mentions in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: m.mentions,
            reason=f"Vile Moderation [{ctx.author}]"
        )

        del self.tasks["purge"][ctx.guild.id]
        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages with mentions.",
            delete_after=3
        )


    @purge.command(
        name="upto",
        aliases=("before",),
        usage="<message>",
        example="1120872265786077364"
    )
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_upto(self, ctx: vile.Context, *, message: vile.MessageConverter):
        """Clear messages sent before the specified message"""

        return await ctx.error("This resource is ")
        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        cleared_messages = await ctx.channel.purge(
            limit=None,
            before=message.created_at,
            reason=f"Vile Moderation [{ctx.author}]"
        )

        del self.tasks["purge"][ctx.guild.id]
        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages.",
            delete_after=3
        )


    @purge.command(
        name="embeds",
        usage="<amount>",
        example="100"
    )
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_embeds(self, ctx: vile.Context, amount: int):
        """Clear messages with embeds in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: m.embeds,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_reactions(self, ctx: vile.Context, amount: int):
        """Clear messages with reactions in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: m.reactions,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_links(self, ctx: vile.Context, amount: int):
        """Clear messages with links in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: regex.link.findall(m.content),
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_webhooks(self, ctx: vile.Context, amount: int):
        """Clear messages with webhooks in bulk"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        if amount > 1000 or amount in (0, 1):
            return await ctx.error("You can only clear between **1** and *1,000** messages.")

        cleared_messages = await ctx.channel.purge(
            limit=amount+1,
            check=lambda m: m.author.bot and m.author.discriminator == "0000" and not m.author.system,
            reason=f"Vile Moderation [{ctx.author}]"
        )

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
    @commands.max_concurrency(1, commands.BucketType.channel, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_upto(
        self, 
        ctx: vile.Context, 
        start: vile.MessageConverter, 
        finish: vile.MessageConverter
    ):
        """Clear messages between message (A) and message (B)"""

        if ctx.guild.id in self.tasks["purge"]:
            return await ctx.error("There is already a running purge task.")
        
        self.tasks["purge"][ctx.guild.id] = 1
        cleared_messages = await ctx.channel.purge(
            limit=None,
            before=finish.created_at,
            after=start.created_at,
            reason=f"Vile Moderation [{ctx.author}]"
        )

        del self.tasks["purge"][ctx.guild.id]
        return await ctx.success(
            f"Successfully **cleared** `{len(cleared_messages)}` messages.",
            delete_after=3
        )


    @commands.command(
        name="recentjoins",
        aliases=("rj", "newusers")
    )
    async def recentjoins(self, ctx: vile.Context):
        """View recently joined members"""

        recent_joins = sorted(
            (m for m in ctx.guild.members if time.time() - m.joined_at.timestamp() < 86400),
            key=lambda m: m.joined_at,
            reverse=True
        )
        
        if not recent_joins:
            return await ctx.error("There aren't any **recent** joins.")

        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Recent Joins in {ctx.guild.name}"
        )
        for member in recent_joins:
            rows.append(f"{member.mention}: **{member}** ( {discord.utils.format_dt(member.joined_at, style='R')} )")

        return await ctx.paginate((embed, rows))


    @commands.command(
        name="nuke"
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx: vile.Context):
        """Clone and delete the current channel"""

        if ctx.channel in (ctx.guild.system_channel, ctx.guild.rules_channel):
            return await ctx.send_error("You cant **nuke** this channel.")

        bot_message = await ctx.error("Are you sure you want to **nuke** this channel?")
        conf = await vile.confirm(ctx, bot_message)

        if conf is True:
            new_channel = await ctx.channel.clone(
                name=ctx.channel.name,
                reason=f"Vile Moderation [{ctx.author}]"
            )

            await ctx.channel.delete(reason=f"Vile Moderation [{ctx.author}]")
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
                
            await self.bot.cache.initialize_settings_cache()
            return await new_channel.send(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.done} {ctx.author.mention}**:** Successfully **nuked** #{ctx.channel.name}."
                )
            )


    @commands.command(
        name="talk",
        usage="[channel] [role]",
        example="#private VIP"
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def talk(
        self,
        ctx: vile.Context,
        channel: Optional[discord.TextChannel] = None,
        *,
        role: Optional[vile.RoleConverter] = None
    ):
        """Toggle a channel to text for a role"""

        channel = channel or ctx.channel
        role = role or ctx.guild.default_role

        overwrite = not channel.permissions_for(role).send_messages
        await channel.set_permissions(
            role,
            overwrite=discord.PermissionOverwrite(send_messages=overwrite),
            reason=f"Vile Moderation [{ctx.author}]"
        )

        return await ctx.success(f"Successfully **{'enabled' if overwrite else 'disabled'}** text for {role.mention if role != ctx.guild.default_role else '@everyone'} in {channel.mention}.")


    @commands.command(
        name="hide",
        usage="[channel] [role]",
        example="#private VIP"
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def hide(
        self,
        ctx: vile.Context,
        channel: Optional[discord.TextChannel] = None,
        *,
        role: Optional[vile.RoleConverter] = None
    ):
        """Toggle a channel to read messages for a role"""

        channel = channel or ctx.channel
        role = role or ctx.guild.default_role

        overwrite = not channel.permissions_for(role).send_messages
        await channel.set_permissions(
            role,
            overwrite=discord.PermissionOverwrite(view_channel=overwrite),
            reason=f"Vile Moderation [{ctx.author}]"
        )

        return await ctx.success(f"Successfully **{'enabled' if overwrite else 'disabled'}** reading messages for {role.mention if role != ctx.guild.default_role else '@everyone'} in {channel.mention}.")


    @commands.command(
        name="slowmode",
        usage="<time d/h/m/s>",
        example="5s"
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: vile.Context, timespan: vile.Timespan):
        """Restricts members to sending one message per interval"""

        if timespan.seconds < 0 or timespan.seconds > 216e+2:
            return await ctx.error("Please provide a **valid** timespan between 0 seconds and 6 hours.")

        await ctx.channel.edit(
            slowmode_delay=timespan.seconds,
            reason=f"Vile Moderation [{ctx.author}]"
        )
        
        return await ctx.success(f"Successfully **set** the channel's **message interval** to `{vile.fmtseconds(timespan.seconds)}`.")


    @commands.command(
        name="revokefiles",
        aliases=("rf",)
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def revokefiles(self, ctx: vile.Context):
        """Removes/assigns the permission to attach files & embed links in the current channel"""

        overwrite = any((
            not channel.permissions_for(role).attach_files,
            not channel.permissions_for(role).embed_links
        ))
        await channel.set_permissions(
            role,
            overwrite=discord.PermissionOverwrite(
                attach_files=overwrite,
                embed_links=overwrite
            ),
            reason=f"Vile Moderation [{ctx.author}]"
        )

        return await ctx.success(f"Successfully **{'assigned' if overwrite else 'revoked'}** attach files/embed links permissions for @everyone.")


    @commands.command(
        name="rename",
        aliases=("nickname", "nick"),
        usage="<member> <nickname>",
        example="@cop#0666 skidward"
    )
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    async def rename(self, ctx: vile.Context, member: vile.MemberConverter, *, nickname: str):
        """Assigns the mentioned user a new nickname in the server"""

        if await ctx.can_moderate(member, "rename") is not None:
            return

        if len(nickname) < 2 or len(nickname) > 32:
            return await ctx.error("Please provide a **valid** nickname between 2 and 32 characters.")

        await member.edit(
            nick=nickname,
            reason=f"Vile Moderation [{ctx.author}]"
        )

        return await ctx.error(f"Successfully **renamed** {member.mention} to `{nickname}`.")


    @commands.group(
        name="stickyrole",
        aliases=("sr", "sticky"),
        usage="<sub command>",
        example="add Loser",
        extras={
            "permissions": "Server Owner"
        },
        invoke_without_command=True
    )
    @commands.is_guild_owner()
    async def stickyrole(self, ctx: vile.Context):
        """Reapply a role on join"""
        return await ctx.send_help(ctx.command.qualified_name)


    @stickyrole.command(
        name="add",
        usage="<role>",
        example="Loser",
        extras={
            "permissions": "Server Owner"
        }
    )
    @commands.is_guild_owner()
    async def stickyrole_add(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Add a sticky role"""

        if role in self.bot.cache.sticky_roles.get(ctx.guild.id, DICT):
            return await ctx.error("That is **already** a sticky role.")

        await self.bot.db.execute(
            "INSERT INTO sticky_roles (guild_id, role_id) VALUES (%s, %s);",
            ctx.guild.id, role.id
        )
        
        if ctx.guild.id not in self.bot.cache.sticky_roles:
            self.bot.cache.sticky_roles[ctx.guild.id] = []

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
    @commands.is_guild_owner()
    async def stickyrole_remove(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Remove a sticky role"""

        if role not in self.bot.cache.sticky_roles.get(ctx.guild.id, DICT):
            return await ctx.error("That is **not** a sticky role.")

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
    @commands.is_guild_owner()
    async def stickyrole_list(self, ctx: vile.Context):
        """View every sticky role"""
        
        if not self.bot.cache.sticky_roles.get(ctx.guild.id, DICT):
            return await ctx.error("There are no **sticky roles** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Sticky Roles in {ctx.guild.name}"
        )
        for role_id in self.bot.cache.sticky_roles[ctx.guild.id]:
            if (role := ctx.guild.get_role(role_id)) is not None:
                rows.append(f"{role.mention}: **{role.name}** ( `{role.id}` )")
                
        return await ctx.paginate((embed, rows))

    
async def setup(bot: "VileBot") -> None:
    await bot.add_cog(Moderation(bot))