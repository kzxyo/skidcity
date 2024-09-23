import datetime, discord

from discord.ext import commands

from patches.modules import AntiNukeModule, AntiNukeUser
from patches.permissions import Permissions

from utils.emojis import Emojis

def has_admin():
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.author.id in ctx.bot.owner_ids or ctx.author.id == ctx.guild.owner.id: return True
        admin = await ctx.bot.db.fetchrow("SELECT * FROM antinuke_admins WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
        if not admin: return await ctx.success("You do not have **anti-nuke admin**")
        return True
    
    return commands.check(predicate)

def is_enabled():
    async def predicate(ctx: commands.Context) -> bool:
        module = await ctx.bot.db.fetchrow("SELECT * FROM antinuke WHERE guild_id = $1", ctx.guild.id)
        if not module:
            return await ctx.success("AntiNuke is not **enabled** in this server. Use `antinuke enable` to **enable** it.")
        return True
    
    return commands.check(predicate)

class antinuke(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.modules = ["Ban", "Kick", "Bot", "Roles", "Vanity", "Webhook", "Channels", "Permissions"]
        self.actions = {}
        
    @has_admin()
    @commands.group(invoke_without_command=True, description='Anti-Nuke Commands', help="<subcommand>", usage="settings",  brief="Anti-Nuke Admin", aliases=['an'])
    @Permissions.has_permission(administrator=True)
    async def antinuke(self, ctx: commands.Context):
        await ctx.create_pages()
        
    @has_admin()
    @is_enabled()    
    @antinuke.command(description='Anti-Nuke Settings', help="", usage="",  brief="Anti-Nuke Admin", aliases=['config'])
    @Permissions.has_permission(administrator=True)
    async def settings(self, ctx: commands.Context):
        
        embed = discord.Embed(title=f"Anti-Nuke Settings - {ctx.guild.name}", color=self.bot.color)
        embed.set_footer(icon_url=ctx.me.avatar.url, text=f"If you have any questions, please join our support server: {self.bot.support_server}")
        embed.add_field(name="Support", value=f"**[Support Server]({self.bot.support_server})**", inline=True)
        
        if ctx.guild.icon: embed.set_thumbnail(url=ctx.guild.icon.url)
        
        for name in self.modules:
            module = await AntiNukeModule.from_database(self.bot.db, ctx.guild.id, name)
            embed.add_field(name=f"**{name}**: {Emojis.OFF if not module or not module.toggled else Emojis.ON}", value=f"‎ ‎ ﹒Action: `{module.punishment if module is not None else 'None'}`\n‎ ‎ ﹒Threshold: `{module.threshold if module is not None else 'None'}`", inline=True)
    
        return await ctx.send(embed=embed)
    
    @has_admin()
    @is_enabled()
    @antinuke.command(description='Add an Anti-Nuke Whitelisted Member', help="[User]", usage="@Sam", brief="Anti-Nuke Admin", aliases=['wl'])
    @Permissions.has_permission(administrator=True)
    async def whitelist(self, ctx: commands.Context, user: discord.User):
        
        whitelist = await ctx.bot.db.fetchrow("SELECT * FROM antinuke_whitelist WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, user.id)
        if whitelist: 
            
            await ctx.bot.db.execute("DELETE FROM antinuke_whitelist WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, user.id)
            return await ctx.success(f"**{user.name}** has been **unwhitelisted** in this server.")
        
        await ctx.bot.db.execute("INSERT INTO antinuke_whitelist VALUES ($1, $2)", ctx.guild.id, user.id)
        
        return await ctx.success(f"**{user.name}** has been **whitelisted** in this server.")
    
    @has_admin()
    @is_enabled()
    @antinuke.command(description='Add an Anti-Nuke Admin', help="[User]", usage="@Sam", brief="Anti-Nuke Admin")
    @Permissions.has_permission(administrator=True)
    async def admin(self, ctx: commands.Context, user: discord.User):
        
        admin = await ctx.bot.db.fetchrow("SELECT * FROM antinuke_admins WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, user.id)
        if admin: 
            
            await ctx.bot.db.execute("DELETE FROM antinuke_admins WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, user.id)
            return await ctx.success(f"**{user.name}** has been **removed** from the **Anti-Nuke Admin** list in this server.")
        
        await ctx.bot.db.execute("INSERT INTO antinuke_admins VALUES ($1, $2)", ctx.guild.id, user.id)
        
        return await ctx.success(f"**{user.name}** has been **added** to the **Anti-Nuke Admin** list in this server.")
    
    @has_admin()
    @antinuke.command(description='List Anti-Nuke Whitelisted Members', help="", usage="",  brief="Anti-Nuke Admin")
    @Permissions.has_permission(administrator=True)
    async def whitelisted(self, ctx: commands.Context):
        
        whitelisted = await ctx.bot.db.fetch("SELECT * FROM antinuke_whitelist WHERE guild_id = $1", ctx.guild.id)
        if not whitelisted: return await ctx.success("No users are **whitelisted** in this server.")
        
        embed = discord.Embed(title=f"Anti-Nuke Whitelisted Members - {ctx.guild.name}", color=self.bot.color)
        embed.set_footer(icon_url=ctx.me.avatar.url, text=f"If you have any questions, please join our support server: {self.bot.support_server}")
        
        embed.add_field(name="Support", value=f"**[Support Server]({self.bot.support_server})**", inline=True)
        
        if ctx.guild.icon: embed.set_thumbnail(url=ctx.guild.icon.url)
        
        embed.description = '\n'.join([f"{ctx.guild.get_member(user['user_id']).name} ({user['user_id']})" for user in whitelisted])
        
        return await ctx.send(embed=embed)
    
    @has_admin()
    @is_enabled()
    @antinuke.command(description='List Anti-Nuke Admin', help="", usage="",  brief="Anti-Nuke Admin")
    @Permissions.has_permission(administrator=True)
    async def admins(self, ctx: commands.Context):
        
        admins = await ctx.bot.db.fetch("SELECT * FROM antinuke_admins WHERE guild_id = $1", ctx.guild.id)
        if not admins: return await ctx.success("No users are **Anti-Nuke Admins** in this server.")
        
        embed = discord.Embed(title=f"Anti-Nuke Admins - {ctx.guild.name}", color=self.bot.color)
        embed.set_footer(icon_url=ctx.me.avatar.url, text=f"If you have any questions, please join our support server: {self.bot.support_server}")
        embed.add_field(name="Support", value=f"**[Support Server]({self.bot.support_server})**", inline=True)
        
        if ctx.guild.icon: embed.set_thumbnail(url=ctx.guild.icon.url)
        
        embed.description = '\n'.join([f"{ctx.guild.get_member(user['user_id']).name} ({user['user_id']})" for user in admins])
        
        return await ctx.send(embed=embed)
    
    @has_admin()
    @is_enabled()
    @antinuke.command(description='Enable Anti-Nuke', help="", usage="",  brief="Anti-Nuke Admin")
    @Permissions.has_permission(administrator=True)
    async def enable(self, ctx: commands.Context):
        enabled = await ctx.bot.db.fetchrow("SELECT * FROM antinuke WHERE guild_id = $1", ctx.guild.id)
        if enabled: return await ctx.success("AntiNuke is already **enabled** in this server.")
        
        await ctx.bot.db.execute("INSERT INTO antinuke VALUES ($1)", ctx.guild.id)
        
        modules = await ctx.bot.db.fetch("SELECT * FROM antinuke_modules WHERE guild_id = $1", ctx.guild.id)
        
        if not modules:
            for name in self.modules:
                
                await ctx.bot.db.execute("INSERT INTO antinuke_modules VALUES ($1, $2, $3, $4, $5)", ctx.guild.id, name, 'Ban', 1, False)
        
        return await ctx.success("Anti-Nuke has been **enabled** in this server.")
    
    @has_admin()
    @is_enabled()
    @antinuke.command(description='Disable Anti-Nuke', help="", usage="",  brief="Anti-Nuke Admin")
    @Permissions.has_permission(administrator=True)
    async def disable(self, ctx: commands.Context):
        await ctx.bot.db.execute("DELETE FROM antinuke WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success("Anti-Nuke has been **disabled** in this server.")
        
    @has_admin()
    @is_enabled()
    @antinuke.command(description='Toggle Anti-Nuke', help="[Module]", usage="ban",  brief="Anti-Nuke Admin")
    @Permissions.has_permission(administrator=True)
    async def toggle(self, ctx: commands.Context, module: str):
        if module.capitalize() not in self.modules: return await ctx.success(f"The module `{module}` is not a valid **Anti-Nuke module**.")
        
        an_module = await AntiNukeModule.from_database(self.bot.db, ctx.guild.id, module.capitalize())
        an_module.toggled = not an_module.toggled
        
        await an_module.update(self.bot.db, ctx.guild.id)
        
        return await ctx.success(f"Anti-Nuke module `{module}` has been **{'Enabled' if an_module.toggled else 'Disabled'}**.")
        
    @has_admin()
    @is_enabled()
    @antinuke.command(description='Anti-Nuke Module Threshold', help="[Module] [Threshold]", usage="ban 1",  brief="Anti-Admin")
    @Permissions.has_permission(administrator=True)
    async def threshold(self, ctx: commands.Context, module: str, threshold: int):
        if module.capitalize() not in self.modules: return await ctx.success(f"The module `{module}` is not a valid **Anti-Nuke module**.")
        
        an_module = await AntiNukeModule.from_database(self.bot.db, ctx.guild.id, module.capitalize())
        an_module.threshold = threshold
        
        await an_module.update(self.bot.db, ctx.guild.id)
        
        return await ctx.success(f"Anti-Nuke module `{module}` threshold has been set to `{threshold}`.")
    
    @has_admin()
    @is_enabled()
    @antinuke.command(description='Anti-Nuke Module Action', help="[Module] [Action]", usage="ban kick",  brief="Anti-Admin", aliases=['punishment'])
    @Permissions.has_permission(administrator=True)
    async def action(self, ctx: commands.Context, module: str, action: str):
        
        if module.capitalize() not in self.modules: return await ctx.success(f"The module `{module}` is not a valid **Anti-Nuke module**.")
        if action.lower() not in ['ban', 'warn', 'kick' ,'strip']: return await ctx.success(f"The action `{action}` is not a valid action. Use `ban`, `warn`, `kick` or 'strip'.")
        
        an_module = await AntiNukeModule.from_database(self.bot.db, ctx.guild.id, module.capitalize())
        an_module.punishment = action
        
        await an_module.update(self.bot.db, ctx.guild.id)
        
        return await ctx.success(f"Anti-Nuke module `{module}` action has been set to `{action}`.")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        
        if not member.bot: return
        
        module = await AntiNukeModule.from_database(self.bot.db, member.guild.id, 'Bot')
        if not module or not module.toggled: return
        
        admin = await self.bot.db.fetchrow("SELECT * FROM antinuke_admins WHERE guild_id = $1 AND user_id = $2", member.guild.id, member.id)
        
        whitelisted = await self.bot.db.fetchrow("SELECT * FROM antinuke_whitelist WHERE guild_id = $1 AND user_id = $2", member.guild.id, member.id)
        if whitelisted or admin: return
        
        return await member.ban(reason=f"{self.bot.user.name} Anti-Nuke: Protection (Anti-Bot)")
        
    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        if entry.user is None: return
        if entry.user.id == entry.guild.me.id: return
        if entry.action == discord.AuditLogAction.channel_create or entry.action == discord.AuditLogAction.ban or entry.action == discord.AuditLogAction.unban:
            module = await AntiNukeModule.from_database(self.bot.db, entry.guild.id, 'Ban')
            if not module or not module.toggled: return
            
            return await self.take_action(entry.guild.id, entry.user.id, entry.guild.owner.id, module)
        if entry.action == discord.AuditLogAction.channel_delete or entry.action == discord.AuditLogAction.channel_update or entry.action == discord.AuditLogAction.channel_create:
            module = await AntiNukeModule.from_database(self.bot.db, entry.guild.id, 'Channels')
            if not module or not module.toggled: return
            
            return await self.take_action(entry.guild.id, entry.user.id, entry.guild.owner.id, module)
        
        if entry.action == discord.AuditLogAction.kick:
            module = await AntiNukeModule.from_database(self.bot.db, entry.guild.id, 'Kick')
            if not module or not module.toggled: return
            
            return await self.take_action(entry.guild.id, entry.user.id, entry.guild.owner.id, module)
        
        if entry.action == discord.AuditLogAction.role_delete or entry.action == discord.AuditLogAction.role_create:
            module = await AntiNukeModule.from_database(self.bot.db, entry.guild.id, 'Roles')
            if not module or not module.toggled: return
            
            return await self.take_action(entry.guild.id, entry.user.id, entry.guild.owner.id, module)
        
        if entry.action == discord.AuditLogAction.member_role_update:
            
            module = await AntiNukeModule.from_database(self.bot.db, entry.guild.id, 'Permissions')
            if not module or not module.toggled: return
            
            admin = await self.bot.db.fetchrow("SELECT * FROM antinuke_admins WHERE guild_id = $1 AND user_id = $2", entry.guild.id, entry.user.id)
            whitelisted = await self.bot.db.fetchrow("SELECT * FROM antinuke_whitelist WHERE guild_id = $1 AND user_id = $2", entry.guild.id, entry.user.id)
                    
            if admin or whitelisted or entry.user.id == entry.guild.owner.id: return
            
            for role in entry.after.roles:
                if role not in entry.before.roles and role.permissions.administrator:
                    
                    await self.take_action(entry.guild.id, entry.user.id, entry.guild.owner.id, module)
                    return await entry.target.remove_roles(role)
        
        if entry.action == discord.AuditLogAction.webhook_create or entry.action == discord.AuditLogAction.webhook_delete:
            
            module = await AntiNukeModule.from_database(self.bot.db, entry.guild.id, 'Webhook')
            if not module or not module.toggled: return
            
            return await self.take_action(entry.guild.id, entry.user.id, entry.guild.owner.id, module)
        
    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        if before.vanity_url_code != after.vanity_url_code:
            
            user = None
            async for entry in before.audit_logs(limit=1, action=discord.AuditLogAction.guild_update): user = entry.user
            
            module = await AntiNukeModule.from_database(self.bot.db, after.id, 'Vanity')
            if not module or not module.toggled: return
            
            return await self.take_action(after.id, user.id, after.owner.id, module)
         
    async def take_action(self, guild_id: int, user_id: int, owner_id: int, module: AntiNukeModule):
        admin = await self.bot.db.fetchrow("SELECT * FROM antinuke_admins WHERE guild_id = $1 AND user_id = $2", guild_id, user_id)
        whitelisted = await self.bot.db.fetchrow("SELECT * FROM antinuke_whitelist WHERE guild_id = $1 AND user_id = $2", guild_id, user_id)
        
        if whitelisted is not None or admin is not None: return
        if user_id == self.bot.user.id or user_id == owner_id: return
        if guild_id not in self.actions: self.actions[guild_id] = [AntiNukeUser(module.module, user_id, datetime.datetime.now(), 1)]
        
        found = False
        for action in self.actions[guild_id]:
            if action.user_id == user_id and action.module == module.module:
                found = True
                if (datetime.datetime.now() - action.last_action).total_seconds() > 60: 
                    
                    try: self.remove_action(guild_id, user_id, module.module)
                    except: return
                    
                    action.amount = 1
                    self.actions[guild_id].append(AntiNukeUser(module.module, user_id, datetime.datetime.now(), 1))
                    
                if action.amount >= module.threshold: 
                    
                    self.remove_action(guild_id, guild_id, module.module)
                    
                    try: await self.send_action(guild_id, user_id, module)
                    
                    except: return
                    break
                
                action.amount += 1
                
                self.remove_action(guild_id, user_id, module.module)
                self.actions[guild_id].append(AntiNukeUser(module.module, user_id, datetime.datetime.now(), action.amount))
                break
            
        if not found: return self.actions[guild_id].append(AntiNukeUser(module.module, user_id, datetime.datetime.now(), 1))
    
    async def send_action(self, guild_id: int, user_id: int, module: AntiNukeModule):
        user = await self.bot.fetch_user(user_id)
        
        if module.punishment.lower() == 'ban': await self.bot.get_guild(guild_id).ban(user=user, reason=f"{self.bot.user.name} Anti-Nuke: Protection {module.module} (Anti-{module.module})")
        if module.punishment.lower() == 'kick': await self.bot.get_guild(guild_id).kick(user=user, reason=f"{self.bot.user.name} Anti-Nuke: Protection {module.module} (Anti-{module.module})")
        if module.punishment.lower() == 'warn': await user.send(f"{self.bot.user.name} Anti-Nuke: Protection {module.module} (Anti-Bot)\n**You have been warned**, further actions will result in a punishment decided by relevant staff.")
        if module.punishment.lower() == 'strip': await self.bot.get_guild(guild_id).get_member(user_id).remove_roles(*[role for role in self.bot.get_guild(guild_id).get_member(user_id).roles 
                                                            if any([role.permissions.administrator, role.permissions.manage_channels, role.permissions.manage_roles, role.permissions.manage_webhooks, role.permissions.mention_everyone, role.permissions.manage_expressions, role.permissions.moderate_members, role.permissions.manage_messages, role.permissions.manage_guild, role.permissions.ban_members, role.permissions.kick_members, role.permissions.mute_members, role.permissions.manage_webhooks])])
        
        self.remove_action(guild_id, user_id, module.module) # Cleaining up cache
        
        log_embed = discord.Embed(title=f"Anti-Nuke: {module.module}", description=f"Action taken by {self.bot.user.name}", color=self.bot.color, timestamp=datetime.datetime.now())
        
        log_embed.add_field(name="User", value=f"<@{user_id}>", inline=True)
        log_embed.add_field(name="Action", value=module.punishment, inline=True)
        log_embed.set_footer(text=f"{self.bot.user.name} Anti-Nuke", icon_url=self.bot.user.avatar.url)
        
        log = await self.bot.db.fetchval("SELECT channel_id FROM mod_logs WHERE guild_id = $1", guild_id)
        if not log: return
        
        channel = self.bot.get_channel(log)
        
        if not channel: return
        
        try: await channel.send(embed=log_embed)
        except: return
    
    def remove_action(self, guild_id: int, user_id: int, module: str):
        for pos, action in enumerate(self.actions[guild_id]):
            if action.user_id == user_id and action.module == module:
                del self.actions[guild_id][pos]
                return True
                     
async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(antinuke(bot))