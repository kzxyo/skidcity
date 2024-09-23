from discord.ext.commands import Context
from discord.ext import commands
from patches.classes  import Mod
import aiohttp, discord, typing
from patches.permissions import Permissions, GoodRole, PositionConverter
from typing import Union

class edit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @Permissions.has_permission(manage_guild=True)
    @commands.group(aliases=["guildedit"], invoke_without_command=True)
    async def gedit(self, ctx: Context):
       return await ctx.create_pages()
    
    @Mod.is_mod_configured()
    @Permissions.has_permission(manage_guild=True)
    @gedit.command(name="banner", description="change the server banner", usage="[image/link]")
    async def ge_banner(self, ctx: commands.Context, url: str=None):

      if len(ctx.message.attachments) > 0:
            data = await ctx.message.attachments[0].read()
        
      elif url is not None:
            if url.startswith("<") and url.endswith(">"):
                url = url[1:-1]

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as r:
                        data = await r.read()
                except aiohttp.InvalidURL:
                    return await ctx.warning('That url is **invalid**.')
                except aiohttp.ClientError:
                    return await ctx.warning('Something went wrong when trying to get the image.')
      else:
            await ctx.guild.edit(banner=None)
            await ctx.success('I have **cleared** the server banner.')
            return
      try:
            async with ctx.typing():
                await ctx.guild.edit(banner=data, reason=f'server banner updated by {ctx.author}')
      except ValueError:
            await ctx.warning('JPG/PNG format only.')
      else:
            await ctx.success(f'I have **updated** the server banner to [**image**]({url}).')
    
    @Mod.is_mod_configured()
    @Permissions.has_permission(manage_guild=True)
    @gedit.command(name="icon", description="change the server icon", usage="[image/link]")
    async def ge_icon(self, ctx, url: str=None):
        
        if len(ctx.message.attachments) > 0:
            data = await ctx.message.attachments[0].read()
        elif url is not None:
            if url.startswith("<") and url.endswith(">"):
                url = url[1:-1]

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as r:
                        data = await r.read()
                except aiohttp.InvalidURL:
                    return await ctx.warning('That link is invalid.')
                except aiohttp.ClientError:
                    return await ctx.warning('Something went wrong when trying to get the image.')
        else:
            await ctx.guild.edit(icon=None, reason=f'server icon updated by {ctx.author}')
            await ctx.success('I have **cleared** the server icon.')
            return

        try:
            async with ctx.typing():
                await ctx.guild.edit(icon=data, reason=f'server icon updated by {ctx.author}')
        except ValueError:
            await ctx.warning('JPG/PNG format only.')
        else:
            await ctx.success(f'I have **updated** the server icon to [**image**]({url}).')

    @Mod.is_mod_configured()
    @Permissions.has_permission(manage_guild=True)
    @gedit.command(name="splash", description="change the server splash", usage="[image/link]")
    async def ge_splash(self, ctx, url: str=None):
        
        if len(ctx.message.attachments) > 0:
            data = await ctx.message.attachments[0].read()
        elif url is not None:
            if url.startswith("<") and url.endswith(">"):
                url = url[1:-1]

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as r:
                        data = await r.read()
                except aiohttp.InvalidURL:
                    return await ctx.warning('That link is invalid.')
                except aiohttp.ClientError:
                    return await ctx.warning('Something went wrong when trying to get the image.')
        else:
            await ctx.guild.edit(splash=None, reason=f'server splash updated by {ctx.author}')
            await ctx.success('I have **removed** the server invite splash.')
            return

        try:
            async with ctx.typing():
                await ctx.guild.edit(splash=data, reason=f'server splash updated by {ctx.author}')
        except ValueError:
            await ctx.warning('JPG/PNG format only.')
        else:
            await ctx.success(f'I have **updated** the server invite splash to [**image**]({url}).')

    @Mod.is_mod_configured()
    @Permissions.has_permission(manage_guild=True)
    @gedit.command(name="cover", description="change the server discovery banner", usage="[image/link]")
    async def ge_cover(self, ctx, url: str=None): 
        
      if len(ctx.message.attachments) > 0:
            data = await ctx.message.attachments[0].read()
      elif url is not None:
            if url.startswith("<") and url.endswith(">"):
                url = url[1:-1]

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as r:
                        data = await r.read()
                except aiohttp.InvalidURL:
                    return await ctx.warning('that link is invalid.')
                except aiohttp.ClientError:
                    return await ctx.warning('something went wrong when trying to get the image.')
      else:
            await ctx.guild.edit(discovery_splash=None, reason=f'server discovery banner updated by {ctx.author}')
            await ctx.success('server discovery banner has been removed.')
            return

      try:
            async with ctx.typing():
                await ctx.guild.edit(discovery_splash=data, reason=f'server discovery banner updated by {ctx.author}')
      except ValueError:
            await ctx.warning('JPG/PNG format only.')
      else:
            await ctx.success('server discovery cover has been updated.')

    @Mod.is_mod_configured()
    @Permissions.has_permission(manage_guild=True)
    @gedit.command(name="name", description="change the server name", usage="[name]")
    async def ge_name(self, ctx, *, name: str) -> None:
       async with ctx.typing():
          await ctx.guild.edit(name=name, reason=f'server name updated by {ctx.author}')
          await ctx.success('I have **updated** the server name.')

    @Mod.is_mod_configured()
    @Permissions.has_permission(manage_guild=True)
    @gedit.command(name="description", description="change the server description", usage="[description]")
    async def ge_description(self, ctx, *, description: typing.Optional[str] = None) -> None:
       async with ctx.typing():
          await ctx.guild.edit(description=description, reason=f'server description updated by {ctx.author}')
          await ctx.success('I have **updated** the server description.')

    @Mod.is_mod_configured()
    @Permissions.has_permission(manage_guild=True)
    @gedit.command(name="invites", description="toggle invites", usage="[true / false]")
    async def invites(self, ctx, *, invites_disabled: bool) -> None:
       async with ctx.typing():
          await ctx.guild.edit(invites_disabled=invites_disabled, reason=f'server invite settings updated by {ctx.author}')
          await ctx.success(f'I have **updated** the server invites setting to {invites_disabled}.')

    @Mod.is_mod_configured()
    @Permissions.has_permission(manage_guild=True)
    @gedit.command(name="discovery", description="toggle discovery", usage="[true / false]")
    async def ge_discovery(self, ctx, *, discoverable: bool) -> None:
       async with ctx.typing():
          await ctx.guild.edit(discoverable=discoverable, reason=f'server discovery settings updated by {ctx.author}')
          await ctx.success(f'I have **updated** the server discovery settings to {discoverable}.')

    @commands.group(name="channeledit", aliases=["cedit"], invoke_without_command=True)
    async def cedit(self, ctx): 
        return await ctx.create_pages() 

    @Mod.is_mod_configured()
    @cedit.command(name='create', description="create a channel", usage="[name]", brief="manage channels")
    @Permissions.has_permission(manage_roles=True) 
    async def ce_create(self, ctx: commands.Context, *, name: str): 
        channel = await ctx.guild.create_text_channel(name=name, reason=f"created by {ctx.author}")
        return await ctx.success(f"I have **created** the channel {channel.mention}.")

    @Mod.is_mod_configured()
    @cedit.command(name='name', description='rename a text channel', brief="manage channels", usage="[channel] [name]")
    @Permissions.has_permission(manage_channels=True)
    async def ce_rename(self, ctx, channel: typing.Optional[discord.TextChannel] = None, *, name: str) -> None:
        if channel is None:
            channel = ctx.channel
        await channel.edit(name=name, reason=f"renamed by {ctx.author}")
        await ctx.success(f'I have **renamed** {channel.mention} to **{name}**.')

    @Mod.is_mod_configured()
    @cedit.command(name='nsfw', description='toggle whether or not a channel is nsfw', brief="manage channels", usage="[channel] [true / false]")
    @Permissions.has_permission(manage_channels=True)
    async def ce_nsfw(self, ctx, channel: typing.Optional[discord.TextChannel] = None, *, nsfw: bool):
        if channel is None:
          channel = ctx.channel
        await channel.edit(nsfw=nsfw, reason=f"nsfw status changed by {ctx.author}")
        await ctx.success(f"I have **updated** {channel.mention}'s nsfw settings to {nsfw}.")

    @Mod.is_mod_configured()
    @cedit.command(name='category', description='change a text channels category', brief="manage channels", usage="[channel] [category]")
    @Permissions.has_permission(manage_channels=True)
    async def ce_category(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel], category: discord.CategoryChannel):
        await channel.edit(category=category, reason=f"channel category changed by {ctx.author}")
        await ctx.success(f'I have **updated** the category for {channel.mention} to {category.mention}.')

    @Mod.is_mod_configured()
    @cedit.command(name='delete', description='delete a channel', brief="manage channels", usage="[channel]")
    @Permissions.has_permission(manage_channels=True)
    async def ce_delete(self, ctx, channel: typing.Optional[discord.TextChannel] = None):
        if channel is None:
         channel = ctx.channel
        await channel.delete(reason=f'channel deleted by {ctx.author}')
        await ctx.success(f'I have **deleted** the channel {channel.name}.')

    @Mod.is_mod_configured()
    @cedit.command(name='sync', description='sync the permissions to the text channel from the category', brief="manage channels", usage="[channel] [true / false]")
    @Permissions.has_permission(manage_channels=True)
    async def ce_sync(self, ctx, channel: typing.Optional[discord.TextChannel], sync_permissions: bool):
        if channel is None:
         channel = ctx.channel
        await channel.edit(sync_permissions=sync_permissions, reason=f"{ctx.author} has modifed {channel}.")
        await ctx.success(f'I have **updated** the sync permissions for {channel.mention} to `{sync_permissions}`.')

    @Mod.is_mod_configured()
    @cedit.command(name='clone', description='clone a text channel', brief="manage channels", usage="[channel] [name]")
    @Permissions.has_permission(manage_channels=True)
    async def ce_clone(self, ctx, channel: typing.Optional[discord.TextChannel] = None, *, name: str) -> None:
        if channel is None:
            channel = ctx.channel
        await channel.clone(name=name, reason=f"cloned by {ctx.author}")
        await ctx.success(f'I have **cloned** {channel.mention}.')

    @Mod.is_mod_configured()
    @cedit.command(name="topic", description="change the channel topic", usage="[channel] [topic]")
    @Permissions.has_permission(manage_channels=True)
    async def ce_topic(self, ctx, channel: typing.Optional[discord.TextChannel] = None, *, topic: str) -> None:
        
        if channel is None:
            channel = ctx.channel
        
        if topic == None: 
            await channel.edit(topic=None)
            return await ctx.success("I have **cleared** the channel topic.")
        
        await channel.edit(topic=topic, reason=f'server description updated by {ctx.author}')
        await ctx.success(f'I have **updated** {channel.mention} topic to {topic}.')

    @Mod.is_mod_configured()
    @cedit.command(name='lock', description="lock a channel", usage="<channel>", brief="manage channels")
    @Permissions.has_permission(manage_channels=True) 
    async def ce_lock(self, ctx, channel: typing.Optional[discord.TextChannel] = None):
        if channel is None:
            channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        return await ctx.success(f"Locked {channel.mention}")
    
    @Mod.is_mod_configured()
    @cedit.command(name='viewlock', description="viewlock a channel", usage="<channel>", brief="manage channels")
    @Permissions.has_permission(manage_channels=True) 
    async def ce_viewlock(self, ctx, channel: typing.Optional[discord.TextChannel] = None):
        if channel is None:
            channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        return await ctx.success(f"Viewlocked {channel.mention}")
    
    @Mod.is_mod_configured()
    @cedit.command(name='unviewlock', description="unviewlock a channel", usage="<channel>", brief="manage channels")
    @Permissions.has_permission(manage_channels=True) 
    async def ce_unviewlock(self, ctx, channel: typing.Optional[discord.TextChannel] = None):
        if channel is None:
            channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        return await ctx.success(f"Unviewlocked {channel.mention}")
    
    @Mod.is_mod_configured()
    @cedit.command(name='unlock', description="unlock a channel", usage="<channel>", brief="manage channels")
    @Permissions.has_permission(manage_channels=True) 
    async def ce_lock(self, ctx, channel: typing.Optional[discord.TextChannel] = None):
        if channel is None:
            channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        return await ctx.success(f"Unlocked {channel.mention}")

    @commands.group(aliases=["roleedit"], invoke_without_command=True)
    async def redit(self, ctx: commands.Context):
       return await ctx.create_pages()
   
    @Mod.is_mod_configured()
    @redit.command(name='hoist', description="make a role visible separately.. or not", brief="manage roles", usage="[role] [bool <true or false>]")
    @Permissions.has_permission(manage_roles=True) 
    async def re_hoist(self, ctx: commands.Context, role: GoodRole, state: str): 
     if not state.lower() in ["true", "false"]: return await ctx.error( f"**{state}** can be only **true** or **false**")
     await role.edit(hoist=bool(state.lower() == "true"))
     return await ctx.success(f"{f'The role is now hoisted' if role.hoist is True else 'The role is not hoisted anymore'}")

    @Mod.is_mod_configured()
    @redit.command(name='position', aliases=["pos"], description="change a role's position", usage="[role] [base role]", brief="manage roles")
    @Permissions.has_permission(manage_roles=True) 
    async def re_position(self, ctx: commands.Context, role: GoodRole, position: GoodRole):
     await role.edit(position=position.position)
     return await ctx.success(f"Role position changed to `{position.position}`")

    @Mod.is_mod_configured()
    @redit.command(name='icon', description="change a role's icon", brief="manage roles", usage="[role] <emoji>")
    @Permissions.has_permission(manage_roles=True) 
    async def re_icon(self, ctx: commands.Context, role: GoodRole, emoji: Union[discord.PartialEmoji, str]=None):
      if emoji == None: await role.edit(display_icon=None)
      await ctx.success("role icon has been **cleared**.")
      if isinstance(emoji, discord.PartialEmoji): 
       by = await emoji.read()
       await role.edit(display_icon=by)      
      elif isinstance(emoji, str): await role.edit(display_icon=str(emoji))
      return await ctx.success("Changed role icon")
  
    @Mod.is_mod_configured()
    @redit.command(name='name', brief="manage roles", description="change a role's name", usage="[role] [name]")
    @Permissions.has_permission(manage_roles=True) 
    async def re_name(self, ctx: commands.Context, role: GoodRole, *, name: str): 
     await role.edit(name=name, reason=f"role edited by {ctx.author}")
     return await ctx.success(f"Edited the role's name in **{name}**")

    @Mod.is_mod_configured()
    @redit.command(name='color', description="change a role's color", usage="[role] [color]")
    @Permissions.has_permission(manage_roles=True) 
    async def re_color(self, ctx: commands.Context, role: GoodRole, *, color: str):  
        try: 
            color = color.replace("#", "")
            await role.edit(color=int(color, 16), reason=f"role edited by {ctx.author}")
            return await ctx.reply(embed=discord.Embed(color=role.color, description=f"{self.bot.yes} {ctx.author.mention}: Changed role's color"))
        except: return await ctx.error( "Unable to change the role's color")  

    @commands.group(aliases=["threadedit"], invoke_without_command=True)
    async def tedit(self, ctx: commands.Context):
      return await ctx.create_pages()
    
    @Mod.is_mod_configured()
    @tedit.command(name='create', description='create a thread', brief="manage channels", usage="[channel] [message]")
    @Permissions.has_permission(manage_threads=True)
    async def te_create(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel] = None, message: typing.Optional[commands.MessageConverter] = None, *, name: str) -> None:
        if channel is None:
            channel = ctx.channel
            thread = await channel.create_thread(name=name, message=message, reason=f"{ctx.author} created a thread.")
            await thread.add_user(ctx.author)
            await ctx.success(f'{name} has been created.')

    @Mod.is_mod_configured()
    @tedit.command(name='name', description='rename a thread', brief="manage channels", usage="[thread] [name]")
    @Permissions.has_permission(manage_threads=True)
    async def te_name(self, ctx: commands.Context, thread: typing.Optional[discord.Thread], name: str) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
        await thread.edit(name=name, reason=f"{ctx.author} renamed the thread.")
        await ctx.success(f'{name} has been renamed.')

    @Mod.is_mod_configured()
    @tedit.command(name='archive', description='archive a thread', brief="manage channels", usage="[thread] [name]")
    @Permissions.has_permission(manage_threads=True)
    async def te_archive(self, ctx: commands.Context, thread: typing.Optional[discord.Thread], archived: bool = None) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
        await thread.edit(archived=archived, reason=f"{ctx.author} archived the thread.")
        await ctx.success(f'{thread.mention} has been archived.')
        
    @Mod.is_mod_configured()
    @tedit.command(name='bump', description='keep a thread from auto archiving', brief="manage channels", usage="[thread]")
    @Permissions.has_permission(manage_threads=True)
    async def te_bump(self, ctx: commands.Context, thread: typing.Optional[discord.Thread]) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
        check = await self.bot.db.fetchrow("SELECT * FROM threadbumper WHERE thread_id = $1", thread.id)
        if check: return await ctx.warning(f"{thread.mention} is **already** in threadbumoer.") 
        await ctx.success(f'{thread.mention} has been added to thread bumper.')
        await self.bot.db.execute("INSERT INTO threadbumper VALUES ($1, $2)", ctx.guild.id, thread.id)
        
    @Mod.is_mod_configured()
    @tedit.command(name='unbump', description='remove a thread from auto archiving', brief="manage channels", usage="[thread]")
    @Permissions.has_permission(manage_threads=True)
    async def te_unbump(self, ctx: commands.Context, thread: typing.Optional[discord.Thread]) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
        await ctx.success(f'{thread.mention} has been removed from thread bumper.')
        await self.bot.db.execute(f"DELETE FROM threadbumper WHERE guild_id = {ctx.guild.id} AND thread_id = {thread.id}")

    @Mod.is_mod_configured()
    @tedit.command(name='pin', description='pin the thread to the top', brief="manage channels", usage="[thread] [true / false]")
    @Permissions.has_permission(manage_threads=True)
    async def te_pin(self, ctx: commands.Context, thread: typing.Optional[discord.Thread], pinned: bool = None) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
        await thread.edit(pinned=pinned, reason=f"{ctx.author} pinned the thread.")
        await ctx.success(f'#{thread.mention} has been pinned.')

    @Mod.is_mod_configured()
    @tedit.command(name='invite', description='make the thread invitable', brief="manage channels", usage="[thread] [true / false]")
    @Permissions.has_permission(manage_threads=True)
    async def te_invite(self, ctx: commands.Context, thread: typing.Optional[discord.Thread], invitable: bool = None) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
        await thread.edit(invitable=invitable, reason=f"{ctx.author} made the thread invitable.")
        await ctx.success(f'#{thread.mention} has been updated.')

    @Mod.is_mod_configured()
    @tedit.command(name='time', description='change the auto archive time', brief="manage channels", usage="[thread] [60 1440 4320 10080]")
    @Permissions.has_permission(manage_threads=True)
    async def te_time(self, ctx: commands.Context, thread: typing.Optional[discord.Thread], time: typing.Literal["60", "1440", "4320", "10080"],) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
        await thread.edit(auto_archive_duration=time, reason=f"{ctx.author} changed the auto archive time.")
        await ctx.success(f'changed the auto archive time for {thread.mention}.')

    @Mod.is_mod_configured()
    @tedit.command(name='adduser', description='add a user to a thread', brief="manage channels", usage="[thread] [member]")
    @Permissions.has_permission(manage_threads=True)
    async def te_adduser(self, ctx: commands.Context, thread: typing.Optional[discord.Thread], member: discord.Member) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
            if discord.utils.get(await thread.fetch_members(), id=member.id) is not None:
                await ctx.warning(f'that user is already in the thread.')
                await thread.add_user(member)
        await ctx.success(f'added {member} to the thread.')

    @Mod.is_mod_configured()
    @tedit.command(name='removeuser', description='remove a user from the thread', brief="manage channels", usage="[thread] [member]")
    @Permissions.has_permission(manage_threads=True)
    async def te_removeuser(self, ctx: commands.Context, thread: typing.Optional[discord.Thread], member: discord.Member) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
            if discord.utils.get(await thread.fetch_members(), id=member.id) is not None:
                await ctx.warning(f'that user is not in the thread.')
                await thread.remove_user(member)
        await ctx.success(f'removed **{member}** from the thread.')

    @Mod.is_mod_configured()
    @tedit.command(name='delete', description='delete a thread', brief="manage channels", usage="[thread]")
    @Permissions.has_permission(manage_threads=True)
    async def te_delete(self, ctx: commands.Context, thread: typing.Optional[discord.Thread], invitable: bool = None) -> None:
        if thread is None:
            if isinstance(ctx.channel, discord.Thread):
                thread = ctx.channel
        await thread.delete()
        await ctx.success(f'{thread.mention} has been deleted.')

    @commands.group(aliases=["vcedit"], invoke_without_command=True)
    async def vedit(self, ctx: commands.Context):
      return await ctx.create_pages()
    
    @Mod.is_mod_configured()
    @vedit.command(name='create', description='create a voice channel', brief="manage channels", usage="[category] [name]")
    @Permissions.has_permission(manage_channels=True)
    async def ve_create(self, ctx: commands.Context, category: typing.Optional[discord.CategoryChannel] = None, *, name:str):
        await ctx.guild.create_voice_channel(name=name, category=category, reason=f"{ctx.author} has created the voice channel.",)
        await ctx.success(f'{name} has been created.')

    @Mod.is_mod_configured()
    @vedit.command(name='name', description='rename a voice channel', brief="manage channels", usage="[voice channel] [name]")
    @Permissions.has_permission(manage_channels=True)
    async def ve_name(self, ctx: commands.Context, channel: discord.VoiceChannel, name: str):
        await channel.edit(name=name, reason=f"{ctx.author} has renamed the voice channel.",)
        await ctx.success(f'{channel.mention} has been renamed.')

    @Mod.is_mod_configured()
    @vedit.command(name='nsfw', description='make a voice channel nsfw', brief="manage channels", usage="[voice channel] [true / false]")
    @Permissions.has_permission(manage_channels=True)
    async def ve_nsfw(self, ctx: commands.Context, channel: discord.VoiceChannel, nsfw: bool = None):
        if nsfw is None:
            nsfw = not channel.nsfw
        await channel.edit(nsfw=nsfw, reason=f"{ctx.author} has modifed {channel}.",)
        await ctx.success(f'{channel.mention} has been modified.')

    @Mod.is_mod_configured()
    @vedit.command(name='user', description='edit the user limit for a voice channel', brief="manage channels", usage="[voicelimit] [1-99]")
    @Permissions.has_permission(manage_channels=True)
    async def ve_userlimit(self, ctx: commands.Context, channel: discord.VoiceChannel, user_limit: int):
        if user_limit < 0 or user_limit > 99:
            return await ctx.warning(f'user limit must be between 1 and 99.')
        await channel.edit(user_limit=user_limit, reason=f"{ctx.author} has modifed {channel}.")
        await ctx.success(f'user limit for {channel.mention} has been set to {user_limit}.')

    @Mod.is_mod_configured()
    @vedit.command(name='position', description='change the position of a voice channel', brief="manage channels", usage="[channel] [position]")
    @Permissions.has_permission(manage_channels=True)
    async def ve_position(self, ctx: commands.Context, channel: discord.VoiceChannel, *, position: PositionConverter):
        await channel.edit(position=position, reason=f"{ctx.author} has modifed {channel}.")
        await ctx.success(f'position for {channel.mention} has been changed.')

    @Mod.is_mod_configured()
    @vedit.command(name='sync', description='sync the permissions to the voice channel from the category', brief="manage channels", usage="[channel] [true / false]")
    @Permissions.has_permission(manage_channels=True)
    async def ve_sync(self, ctx: commands.Context, channel: discord.VoiceChannel, sync_permissions: bool = None):
        await channel.edit(sync_permissions=sync_permissions, reason=f"{ctx.author} has modifed {channel}.")
        await ctx.success(f'permissions for {channel.mention} have been synced.')

    @Mod.is_mod_configured()
    @vedit.command(name='category', description='change the category for a voice channel', brief="manage channels", usage="[category] [channel]")
    @Permissions.has_permission(manage_channels=True)
    async def ve_category(self, ctx: commands.Context, channel: discord.VoiceChannel, category: discord.CategoryChannel,):
        await channel.edit(category=category, reason=f"{ctx.author} has modifed {channel}.")
        await ctx.success(f'the category for {channel.mention} has been changed.')

    @Mod.is_mod_configured()
    @vedit.command(name='delete', description='delete a voice channel', brief="manage channels", usage="[channel]")
    @Permissions.has_permission(manage_channels=True)
    async def ve_delete(self, ctx, channel: discord.VoiceChannel) -> None:
            if channel is None:
              channel = ctx.channel
            await channel.delete(reason=f'channel deleted by {ctx.author}')
            await ctx.success(f'{channel.mention} has been deleted.')
            
    @commands.group(aliases=["autopurge"], invoke_without_command=True)
    async def delete(self, ctx: commands.Context):
      return await ctx.create_pages()
    
    @delete.command(description="set a channel to have messages automatically deleted in.", usage="[channel] [time]", brief="manage guild")
    @Permissions.has_permission(manage_guild=True)
    async def enable(self, ctx: commands.Context, channel: discord.TextChannel, wait):
        if wait != "0":
            ttype = None
            wait = wait.lower()
            wt = wait[:-1]
            og = wait[:-1]
            if not wt.isdigit(): return await ctx.warning("Invalid amount of time. There is a non-number in your `wait` argument, not including the time type.")
            wt = int(wt)
            if wait.endswith("s"):
                ttype = "second"
            elif wait.endswith("m"):
                ttype = "minute"
                wt *= 60
            elif wait.endswith("h"):
                ttype = "hour"
                wt *= 3600
            elif wait.endswith("d"):
                ttype = "day"
                wt *= 86400
            elif wait.endswith("w"):
                ttype = "week"
                wt *= 604800
            if not ttype: return await ctx.warning("Invalid time unit. Please use S, M, H, D or W.")
        else:
            wt = 0
        if wt < 5 and wt != 0:
            return await ctx.warning("Wait times must be greater than or equal to 5 seconds.")
        if not channel.permissions_for(ctx.guild.me).manage_messages:
            return await ctx.warning("I do not have permission to delete messages in that channel.")
        await self.conf.channel(channel).wait.set(str(wt))
        if wt:
            await ctx.success(f"Messages in {channel.mention} will now be deleted after {og} {ttype}{'s' if og != '1' else ''}.")
        else:
            await ctx.success("Messages will not be auto-deleted after a specific amount of time.")

async def setup(bot):
    await bot.add_cog(edit(bot))