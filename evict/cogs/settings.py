import discord, datetime
from discord.ext import commands
from patches.permissions import Permissions
from reposter.reposter import Reposter
from bot.dynamicrolebutton import DynamicRoleButton

class settings(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.group(invoke_without_command=True, description='server settings', brief='manage guild', aliases=['config'])
    @Permissions.has_permission(manage_guild=True)
    async def settings(self, ctx: commands.Context):
        await ctx.create_pages()
    
    @settings.group(invoke_without_command=True, description='repost social media links as embeds', brief='manage server', aliases=['socialmedia'])
    @Permissions.has_permission(manage_guild=True)
    async def reposter(self, ctx: commands.Context):
        await ctx.create_pages()
        
    @reposter.command(description='enable reposter', brief='manage server', aliases=['true', 'on'])
    @Permissions.has_permission(manage_guild=True)
    async def enable(self, ctx: commands.Context):
        social = await ctx.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', ctx.guild.id)
        if social is not None and social['toggled']: return await ctx.warning('**Social Media** Reposting is already **enabled**.')
        await ctx.bot.db.execute("INSERT INTO settings_social VALUES ($1, $2, $3) ON CONFLICT (guild_id) DO UPDATE SET toggled = $2 WHERE settings_social.guild_id = $1", ctx.guild.id, True, 'evict')
        return await ctx.success('**social media** reposting is now enabled.')
    
    @reposter.command(description="disable reposter", brief='manage server', aliases=['false', 'off'])
    @Permissions.has_permission(manage_guild=True)
    async def disable(self, ctx: commands.Context):
        social = await ctx.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', ctx.guild.id)
        if not social or not social['toggled']: return await ctx.warning('**Social Media** Reposting is already **disabled**.')
        await ctx.bot.db.execute("INSERT INTO settings_social VALUES ($1, $2, $3) ON CONFLICT (guild_id) DO UPDATE SET toggled = $2 WHERE settings_social.guild_id = $1", ctx.guild.id, False, 'evict')
        return await ctx.success('**social media** reposting is now disabled.')
    
    @reposter.command(description="set reposter prefix (set to 'none' to have no prefix)", usage='[prefix]', brief='manage server', help='')
    @Permissions.has_permission(manage_guild=True)
    async def prefix(self, ctx: commands.Context, prefix: str=None):
        social = await ctx.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', ctx.guild.id)
        if not social: return await ctx.warning('Social Media Reposting is not enabled.')
        if not prefix: return await ctx.success(f'Current prefix: {social["prefix"]}')
        await ctx.bot.db.execute("UPDATE settings_social SET prefix = $2 WHERE guild_id = $1", ctx.guild.id, prefix)
        return await ctx.success(f'**social media** reposting prefix is now set to `{prefix}`.')
    
    @settings.group(invoke_without_command=True, description='server logs', brief='manage guild')
    @Permissions.has_permission(manage_guild=True)
    async def logs(self, ctx: commands.Context):
        await ctx.create_pages()
    
    @logs.command(description="toggle voice logging", brief="manage guild", usage="[toggle] <channel>")
    @Permissions.has_permission(manage_guild=True)
    async def voice(self, ctx: commands.Context, status: bool, channel: discord.TextChannel=None):
        voice = await self.bot.db.fetchrow("SELECT * FROM voice_logs WHERE guild_id = $1", ctx.guild.id)
        
        if status:
            if voice: return await ctx.warning('Voice logs are already enabled')
            if channel == None: channel = await ctx.guild.create_text_channel('voice-logs')
            await self.bot.db.execute("INSERT INTO voice_logs VALUES ($1, $2)", ctx.guild.id, channel.id)
            return await ctx.success('**voice channel** logs **enabled**')
        
        if not voice: return await ctx.warning('Voice logs are already disabled')
        await self.bot.db.execute("DELETE FROM voice_logs WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success('**voice channel** logs **disabled**')
        
    @logs.command(description="toggle message logging", brief="manage guild", usage="[toggle] <channel>")
    @Permissions.has_permission(manage_guild=True)
    async def message(self, ctx: commands.Context, status: bool, channel: discord.TextChannel=None):
        message = await self.bot.db.fetchrow("SELECT * FROM message_logs WHERE guild_id = $1", ctx.guild.id)
        if status:
            if message: return await ctx.warning('Message logs are already enabled')
            if channel == None: channel = await ctx.guild.create_text_channel('message-logs')
            await self.bot.db.execute("INSERT INTO message_logs VALUES ($1, $2)", ctx.guild.id, channel.id)
            return await ctx.success('**message** logs **enabled**')
        
        if not message: return await ctx.warning('Message logs are already disabled')
        await self.bot.db.execute("DELETE FROM message_logs WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success('**message** logs **disabled**')
    
    @logs.command(description="toggle member logging", brief="manage guild", usage="[toggle] <channel>")
    @Permissions.has_permission(manage_guild=True)
    async def member(self, ctx: commands.Context, status: bool, channel: discord.TextChannel=None):
        member = await self.bot.db.fetchrow("SELECT * FROM member_logs WHERE guild_id = $1", ctx.guild.id)
        if status:
            if member: return await ctx.warning('member logs are already **enabled**')
            if channel == None: channel = await ctx.guild.create_text_channel('member-logs')
            await self.bot.db.execute("INSERT INTO member_logs VALUES ($1, $2)", ctx.guild.id, channel.id)
            return await ctx.success('**member** logs **enabled**')
        
        if not member: return await ctx.warning('member logs are already disabled')
        await self.bot.db.execute("DELETE FROM member_logs WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success('**member** logs **disabled**')
        
    @logs.command(description="toggle role logging", brief="manage guild", usage="[toggle] <channel>")
    @Permissions.has_permission(manage_guild=True)
    async def role(self, ctx: commands.Context, status: bool, channel: discord.TextChannel=None):
        role = await self.bot.db.fetchrow("SELECT * FROM role_logs WHERE guild_id = $1", ctx.guild.id)
        if status:
            if role: return await ctx.warning('role logs are already **enabled**')
            if channel == None: channel = await ctx.guild.create_text_channel('role-logs')
            await self.bot.db.execute("INSERT INTO role_logs VALUES ($1, $2)", ctx.guild.id, channel.id)
            return await ctx.success('**role** logs **enabled**')
        
        if not role: return await ctx.warning('role logs are already disabled')
        await self.bot.db.execute("DELETE FROM role_logs WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success('**role** logs **disabled**')
        
    @logs.command(description="toggle server logging", brief="manage guild", usage="[toggle] <channel>")
    @Permissions.has_permission(manage_guild=True)
    async def server(self, ctx: commands.Context, status: bool, channel: discord.TextChannel=None):
        server = await self.bot.db.fetchrow("SELECT * FROM server_logs WHERE guild_id = $1", ctx.guild.id)
        if status:
            if server: return await ctx.warning('server logs are already enabled')
            if channel == None: channel = await ctx.guild.create_text_channel('server-logs')
            await self.bot.db.execute("INSERT INTO server_logs VALUES ($1, $2)", ctx.guild.id, channel.id)
            return await ctx.success('**server** logs **enabled**')

        if not server: return await ctx.warning('server logs are already disabled')
        await self.bot.db.execute("DELETE FROM server_logs WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success('**server** logs **disabled**')
        
    @logs.command(description="toggle channel logging", brief="manage guild", usage="[toggle] <channel>")
    @Permissions.has_permission(manage_guild=True)
    async def channel(self, ctx: commands.Context, status: bool, channel: discord.TextChannel=None):
        channelCheck = await self.bot.db.fetchrow("SELECT * FROM channel_logs WHERE guild_id = $1", ctx.guild.id)
        
        if status:
            if channelCheck: return await ctx.warning('Channel logs are already enabled')
            if channel == None: channel = await ctx.guild.create_text_channel('channel-logs')
            await self.bot.db.execute("INSERT INTO channel_logs VALUES ($1, $2)", ctx.guild.id, channel.id)
            return await ctx.success('**channel** logs **enabled**')
        
        if not channelCheck: return await ctx.warning('Channel logs are already disabled')
        await self.bot.db.execute("DELETE FROM channel_logs WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success('**channel** logs **disabled**')
    
    @settings.group(invoke_without_command=True, description='place role buttons on messages', brief='manage guild')
    @Permissions.has_permission(manage_roles=True)
    async def rolebutton(self, ctx: commands.Context):
        await ctx.create_pages()

    @rolebutton.command(name="add", description="add a role button", brief="manage roles", usage="[message] [emoji] [role]") 
    async def rolebutton_add(self, ctx: commands.Context, message: discord.Message, emoji: discord.Emoji, role: discord.Role):
        prefix = await self.bot.get_prefix(ctx.message)
        if message.author.id != self.bot.user.id: return await ctx.warning(f"I can only add role **buttons** to my own **messages**. You can create an **embed** using `{prefix}createembed (code)` and add the **button** there.")
        if self.bot.ext.is_dangerous(role): return await ctx.warning('I cant assign roles to users that have dangerous permissions.')
        if role.is_premium_subscriber(): return await ctx.warning('I cant assign integrated roles to users.')
        view = discord.ui.View()
        for component in message.components:
            if isinstance(component, discord.components.ActionRow):
                for button in component.children:
                    if button.custom_id == f"RB:{message.id}:{role.id}": return await ctx.warning(f"**role** {role.mention} is already **assigned** to this **message**.")
                    if button.custom_id.startswith("RB"): view.add_item(DynamicRoleButton(message_id=button.custom_id.split(':')[1], role_id=button.custom_id.split(':')[2], emoji=button.emoji))
                    else: view.add_item(discord.ui.Button(style=button.style, label=button.label, emoji=button.emoji, url=button.url, disabled=button.disabled))
        view.add_item(DynamicRoleButton(message_id=message.id, role_id=role.id, emoji=emoji))
        await message.edit(view=view)
        return await ctx.success(f"added **role** {role.mention} to [**message**]({message.jump_url})")
    
    @rolebutton.command(name="remove", description="remove a role button", brief="manage roles", usage="[message] [role]") 
    async def rolebutton_remove(self, ctx: commands.Context, message: discord.Message, role: discord.Role):
        prefix = await self.bot.get_prefix(ctx.message)
        if message.author.id != self.bot.user.id: return await ctx.warning(f"I can only remove role **buttons** to my own **messages**. You can create an **embed** using `{prefix}createembed (code)` and add the **button** there.")
        view = discord.ui.View()
        for component in message.components:
            if isinstance(component, discord.components.ActionRow):
                for button in component.children:
                    if button.custom_id == f"RB:{message.id}:{role.id}": continue
                    if button.custom_id.startswith("RB"): view.add_item(DynamicRoleButton(message_id=message.id, role_id=role.id, emoji=button.emoji))
                    else: view.add_item(discord.ui.Button(style=button.style, label=button.label, emoji=button.emoji, url=button.url, disabled=button.disabled))
        await message.edit(view=view)
        return await ctx.success(f"removed **role** {role.mention} from [**message**]({message.jump_url})")
                
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        voice_logs = await self.bot.db.fetchrow("SELECT * FROM voice_logs WHERE guild_id = $1", member.guild.id)
        if not voice_logs: return
        if before.channel != after.channel and before.channel != None and after.channel != None:
            
            channel = member.guild.get_channel(voice_logs['channel_id'])
            
            embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
            embed.set_author(name=f'{member.name}', icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
            embed.add_field(name='Switched Voice Channels', value=f'{member.mention}', inline=False)
            embed.add_field(name='IDs', value=f"> {member.mention} (``{member.id}``)\n > Before Channel: {before.channel.name} (``{before.channel.id}``)\n > After Channel: {after.channel.name} (``{after.channel.id}``)", inline=False)
            embed.set_footer(text=member.name, icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
        
        if before.channel != after.channel and before.channel == None:
            
            channel = member.guild.get_channel(voice_logs['channel_id'])
            
            embed = discord.Embed(color=self.bot.color, timestamp=datetime.datetime.now())
            embed.set_author(name=f'{member.name}', icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
            embed.add_field(name='Joined a Voice Channel', value=f'{member.mention}', inline=False)
            embed.add_field(name='IDs', value=f"> {member.mention} (``{member.id}``)\n > Channel: {after.channel.name} (``{after.channel.id}``)", inline=False)
            embed.set_footer(text=member.name, icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
        
        if before.channel != after.channel and after.channel == None:
            
            channel = member.guild.get_channel(voice_logs['channel_id'])
            
            embed = discord.Embed(color=self.bot.color, timestamp=datetime.datetime.now())
            embed.set_author(name=f'{member.name}', icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
            embed.add_field(name='Left a Voice Channel', value=f'{member.mention}', inline=False)
            embed.add_field(name='IDs', value=f"> {member.mention} (``{member.id}``)\n > Channel: {before.channel.name} (``{before.channel.id}``)", inline=False)
            embed.set_footer(text=member.name, icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot: return
        message_logs = await self.bot.db.fetchrow("SELECT * FROM message_logs WHERE guild_id = $1", message.guild.id)
        if not message_logs: return
        channel = message.guild.get_channel(message_logs['channel_id'])
        
        embed = discord.Embed(title="Message Deleted", timestamp=datetime.datetime.now(), color=self.bot.color)
        embed.set_author(name=f'{message.author.name}', icon_url=message.author.avatar.url if message.author.avatar is not None else message.author.default_avatar.url)
        embed.add_field(name='IDs', value=f" > Message: ``{message.id}``\n > {message.author.mention} (``{message.author.id}``)\n > {message.channel.mention} (``{message.channel.id}``)", inline=False)
        embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar is not None else message.author.default_avatar.url)
        embed.set_footer(text=message.author, icon_url=message.author.avatar.url if message.author.avatar is not None else message.author.default_avatar.url)
        
        if len(message.content) > 0: embed.description = f'{message.content}'
        
        if message.reference is not None:
            reference = await message.channel.fetch_message(message.reference.message_id)
            embed.add_field(name='Replying To', value=f'{reference.author.mention}: {reference.jump_url}', inline=False)

        if message.attachments is not None and len(message.attachments) > 0:
            embed.set_image(url=message.attachments[0].url)
            
        embed.set_footer(icon_url=message.author.avatar.url if message.author.avatar is not None else message.author.default_avatar.url)        
        
        try: await channel.send(embed=embed)
        except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        
        if before.author.bot or before.content == after.content: return
        message_logs = await self.bot.db.fetchrow("SELECT * FROM message_logs WHERE guild_id = $1", after.guild.id)
        
        if not message_logs: return
        
        channel = after.guild.get_channel(message_logs['channel_id'])
        
        embed = discord.Embed(title="Message Edited", timestamp=datetime.datetime.now(), color=self.bot.color)
        embed.set_author(name=f'{after.author.name}', icon_url=after.author.avatar.url if after.author.avatar is not None else after.author.default_avatar.url)
        embed.add_field(name='Before message:', value=f'{before.content}', inline=False)
        embed.add_field(name='After message:', value=f'[Click to see new message]({after.jump_url})', inline=False)
        embed.add_field(name='IDs', value=f" > Message: ``{after.id}``\n > {after.author.mention} (``{after.author.id}``)\n > {after.channel.mention} (``{after.channel.id}``)", inline=False)
        embed.set_thumbnail(url=after.author.avatar.url if after.author.avatar is not None else after.author.default_avatar.url)
        embed.set_footer(text=after.author, icon_url=after.author.avatar.url if after.author.avatar is not None else after.author.default_avatar.url)
        
        try: await channel.send(embed=embed)
        except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        
        member_logs = await self.bot.db.fetchrow("SELECT * FROM member_logs WHERE guild_id = $1", member.guild.id)
        if not member_logs: return
        
        channel = member.guild.get_channel(member_logs['channel_id'])
        
        embed = discord.Embed(description= f'{member.mention} has **joined the server.**', timestamp=datetime.datetime.now(), color=self.bot.color)
        embed.set_author(name=f'{member.name}', icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
        embed.add_field(name='Account Creation', value=f"<t:{int(member.created_at.timestamp())}:R>", inline=False)
        embed.add_field(name='IDs', value=f"> {member.mention} (``{member.id}``)", inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
        embed.set_footer(text=member.name, icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
        
        try: await channel.send(embed=embed)
        except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        member_logs = await self.bot.db.fetchrow("SELECT * FROM member_logs WHERE guild_id = $1", member.guild.id)
        if not member_logs: return
        
        channel = member.guild.get_channel(member_logs['channel_id'])
        
        embed = discord.Embed(description= f'{member.mention} has **left the server.**', timestamp=datetime.datetime.now(), color=self.bot.color)
        embed.set_author(name=f'{member.name}', icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
        embed.add_field(name='Joined', value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=False)
        embed.add_field(name='Roles', value=', '.join([role.mention for role in member.roles]), inline=False)
        embed.add_field(name='IDs', value=f"> {member.mention} (``{member.id}``)", inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
        embed.set_footer(text=member.name, icon_url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
        
        try: await channel.send(embed=embed)
        except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        member_logs = await self.bot.db.fetchrow("SELECT * FROM member_logs WHERE guild_id = $1", after.guild.id)
        if not member_logs: return
        
        if before.nick != after.nick:
            channel = after.guild.get_channel(member_logs['channel_id'])
            
            embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
            embed.set_author(name=f'{after.name}', icon_url=after.avatar.url if after.avatar is not None else after.default_avatar.url)
            embed.add_field(name='Member Updated', value=f'{after.mention}', inline=False)
            embed.add_field(name='Names', value=f'> Old Name: {before.nick}\n > New Name: {after.nick}')
            embed.add_field(name='IDs', value=f"> {after.mention} (``{after.id}``)", inline=False)
            embed.set_thumbnail(url=after.avatar.url if after.avatar is not None else after.default_avatar.url)
            embed.set_footer(text=after.name, icon_url=after.avatar.url if after.avatar is not None else after.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        
        role_logs = await self.bot.db.fetchrow("SELECT * FROM role_logs WHERE guild_id = $1", role.guild.id)
        if not role_logs: return
        
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create): 
            channel = role.guild.get_channel(role_logs['channel_id'])
            
            embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='Role Created', value=f'{role.name} | {role.mention}', inline=False)
            embed.add_field(name='IDs', value=f"> {role.mention} (``{role.id}``)\n > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        
        role_logs = await self.bot.db.fetchrow("SELECT * FROM role_logs WHERE guild_id = $1", role.guild.id)
        if not role_logs: return
        
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete): 
            channel = role.guild.get_channel(role_logs['channel_id'])
            
            embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='Role Deleted', value=f'{role.name}', inline=False)
            embed.add_field(name='IDs', value=f"> {role.name} (``{role.id}``)\n > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        if entry.action == discord.AuditLogAction.member_role_update:
            
            role_logs = await self.bot.db.fetchrow("SELECT * FROM role_logs WHERE guild_id = $1", entry.guild.id)
            roles_given = [role.name for role in entry.after.roles if role not in entry.before.roles]
            roles_removed = [role.name for role in entry.before.roles if role not in entry.after.roles]
            
            if not role_logs: return
            channel = entry.guild.get_channel(role_logs['channel_id'])
            
            embed = discord.Embed(description='**Member Updated**', color=self.bot.color, timestamp=datetime.datetime.now())
            embed.set_author(name=f'{entry.target}', icon_url=entry.target.avatar.url if entry.target.avatar is not None else entry.target.default_avatar.url)
            embed.add_field(name='IDs', value=f"> Perp:  {entry.user.mention} (``{entry.user.id}``)\n > Target: {entry.target.mention} (``{entry.target.id}``)", inline=False)
            
            if roles_given: embed.add_field(name=f'**Roles Given**:', value=f'{roles_given}')
            if roles_removed: embed.add_field(name=f'**Roles Removed**:', value=f'{roles_removed}')
            
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.target, icon_url=entry.target.avatar.url if entry.target.avatar is not None else entry.target.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
        
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        role_logs = await self.bot.db.fetchrow("SELECT * FROM role_logs WHERE guild_id = $1", after.guild.id)
        if not role_logs: return
        channel = after.guild.get_channel(role_logs['channel_id'])
        if before.name != after.name:
            async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update): 
                
                embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
                embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                embed.add_field(name='Role Updated', value=f'{after.mention}', inline=False)
                embed.add_field(name='Names', value=f'> Old Name: {before.name}\n > New Name: {after.name}')
                embed.add_field(name='IDs', value=f"> {after.mention} (``{after.id}``)\n > {entry.user.mention} (``{entry.user.id}``)", inline=False)
                embed.set_thumbnail(url=entry.user.avatar.url if entry.user.author.avatar is not None else entry.user.default_avatar.url)
                embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                
                try: await channel.send(embed=embed)
                except discord.Forbidden: return
                
    @commands.Cog.listener('on_guild_channel_create')
    async def jail(self, channel: discord.abc.GuildChannel):
        check = await self.bot.db.fetchrow("SELECT * FROM mod WHERE guild_id = {}".format(channel.guild.id))
        if check: await channel.set_permissions(channel.guild.get_role(int(check['role_id'])), view_channel=False, reason="overwriting permissions for jail role")
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, after: discord.abc.GuildChannel) -> None:
        
        channel_logs = await self.bot.db.fetchrow("SELECT * FROM channel_logs WHERE guild_id = $1", after.guild.id)
        if not channel_logs: return
        
        channel = after.guild.get_channel(channel_logs['channel_id'])
        
        async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            
            embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='Channel Created', value=f'{after.mention}', inline=False)
            embed.add_field(name='IDs', value=f"> {after.mention} (``{after.id}``)\n > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, after: discord.abc.GuildChannel) -> None:
        
        channel_logs = await self.bot.db.fetchrow("SELECT * FROM channel_logs WHERE guild_id = $1", after.guild.id)
        if not channel_logs: return
        
        channel = after.guild.get_channel(channel_logs['channel_id'])
        
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            
            embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='Channel Deleted', value=f'{after.name}', inline=False)
            embed.add_field(name='IDs', value=f"> {after.name} (``{after.id}``)\n > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
        
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel) -> None:
        
        channel_logs = await self.bot.db.fetchrow("SELECT * FROM channel_logs WHERE guild_id = $1", after.guild.id)
        if not channel_logs: return
        
        channel = after.guild.get_channel(channel_logs['channel_id'])
        
        if before.name != after.name:
            async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
                
                embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
                embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                embed.add_field(name='Channel Updated', value=f'{after.mention}', inline=False)
                embed.add_field(name='Names', value=f'> Old Name: {before.name}\n > New Name: {after.name}')
                embed.add_field(name='IDs', value=f"> {after.mention} (``{after.id}``)\n > {entry.user.mention} (``{entry.user.id}``)", inline=False)
                embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                
                try: await channel.send(embed=embed)
                except discord.Forbidden: return

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        
        channel_logs = await self.bot.db.fetchrow("SELECT * FROM server_logs WHERE guild_id = $1", after.id) 
        if not channel_logs: return
        
        channel = after.get_channel(channel_logs['channel_id'])
        if before.name != after.name:
            async for entry in after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
                
                embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
                embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                embed.add_field(name='Server Updated', value=f'{before.name}', inline=False)
                embed.add_field(name='Names', value=f'> Old Name: {before.name}\n > New Name: {after.name}')
                embed.add_field(name='IDs', value=f" > {entry.user.mention} (``{entry.user.id}``)", inline=False)
                embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                
                try: await channel.send(embed=embed)
                except discord.Forbidden: return
                       
    @commands.Cog.listener('on_audit_log_entry_create')
    async def webhook_delete(self, entry: discord.AuditLogEntry):
        
        if entry.action == discord.AuditLogAction.webhook_delete:
            
            server_logs = await self.bot.db.fetchrow("SELECT * FROM server_logs WHERE guild_id = $1", entry.guild.id) 
            if not server_logs: return
        
            channel = entry.guild.get_channel(server_logs['channel_id'])
                
            embed = discord.Embed(timestamp=datetime.datetime.now(), color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='Webhook Deleted', value=f'{entry.user.name}', inline=False)
            embed.add_field(name='IDs', value=f" > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
    
    @commands.Cog.listener('on_audit_log_entry_create')
    async def webhook_create(self, entry: discord.AuditLogEntry):
        
        if entry.action == discord.AuditLogAction.webhook_create:
            
            server_logs = await self.bot.db.fetchrow("SELECT * FROM server_logs WHERE guild_id = $1", entry.guild.id) 
            if not server_logs: return
        
            channel = entry.guild.get_channel(server_logs['channel_id'])

            embed = discord.Embed(timestamp=datetime.datetime.now(), title=f'Webhook Created', color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='IDs', value=f" > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                
            try: await channel.send(embed=embed)
            except discord.Forbidden: return

    @commands.Cog.listener('on_audit_log_entry_create')
    async def webhook_update(self, entry: discord.AuditLogEntry):
        
        if entry.action == discord.AuditLogAction.webhook_update:
            
            server_logs = await self.bot.db.fetchrow("SELECT * FROM server_logs WHERE guild_id = $1", entry.guild.id) 
            if not server_logs: return
        
            channel = entry.guild.get_channel(server_logs['channel_id'])
    
            embed = discord.Embed(timestamp=datetime.datetime.now(), title=f'Webhook Updated', color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='IDs', value=f" > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
            
    @commands.Cog.listener('on_audit_log_entry_create')
    async def emoji_create(self, entry: discord.AuditLogEntry):
        
        if entry.action == discord.AuditLogAction.emoji_create:
            
            server_logs = await self.bot.db.fetchrow("SELECT * FROM server_logs WHERE guild_id = $1", entry.guild.id) 
            if not server_logs: return
        
            channel = entry.guild.get_channel(server_logs['channel_id'])
            
            await self.bot.fetch_user(entry.target)
            
            embed = discord.Embed(timestamp=datetime.datetime.now(), title='Emoji Created', color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='IDs', value=f" > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
            
    @commands.Cog.listener('on_audit_log_entry_create')
    async def emoji_delete(self, entry: discord.AuditLogEntry):
        if entry.action == discord.AuditLogAction.emoji_delete:
            
            server_logs = await self.bot.db.fetchrow("SELECT * FROM server_logs WHERE guild_id = $1", entry.guild.id) 
            if not server_logs: return
        
            channel = entry.guild.get_channel(server_logs['channel_id'])
            
            embed = discord.Embed(timestamp=datetime.datetime.now(), title='Emoji Deleted', color=self.bot.color)
            embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.add_field(name='IDs', value=f" > {entry.user.mention} (``{entry.user.id}``)", inline=False)
            embed.set_thumbnail(url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
            embed.set_footer(text=entry.user, icon_url=entry.user.avatar.url if entry.user.avatar is not None else entry.user.default_avatar.url)
                
            try: await channel.send(embed=embed)
            except discord.Forbidden: return
            
    @commands.Cog.listener('on_message')
    async def on_message(self, message: discord.Message):
        if not message.guild: return
        if message.author.bot: return
        args = message.content.split(' ')
        social = await self.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', message.guild.id)
        
        if not social or not social['toggled']: return
        
        prefix = social['prefix']
        if prefix.lower() == 'none': return await Reposter().repost(self.bot, message, args[0])
        if args[0] == prefix and args[1] is not None: return await Reposter().repost(self.bot, message, args[1])
    
async def setup(bot):
    await bot.add_cog(settings(bot))