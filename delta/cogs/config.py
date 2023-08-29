import json, traceback, datetime 
from discord import TextChannel, ChannelType, Embed, Role, Member,  Message, User, SelectOption, Interaction, PartialEmoji, PermissionOverwrite
from discord.ext.commands import Cog, Context, group, hybrid_command, hybrid_group, command, AutoShardedBot as AB
from discord.ui import Select, View, Button 
from typing import Union
from tools.checks import Perms as utils, Boosts
from tools.utils import EmbedBuilder, InvokeClass
from tools.utils import EmbedScript

poj_cache = {}

async def dm_cmds(ctx: Context, embed: str) -> Message:
  res = await ctx.bot.db.fetchrow("SELECT embed FROM dm WHERE guild_id = $1 AND command = $2", ctx.guild.id, ctx.command.name)
  if res:
   name = res['embed']    
   if embed == "none": 
    await ctx.bot.db.execute("DELETE FROM dm WHERE guild_id = $1 AND command = $2", ctx.guild.id, ctx.command.name)
    return await ctx.send_success(f"Deleted the **{ctx.command.name}** custom response")
   elif embed == "view": 
    em = Embed(color=ctx.bot.color, title=f"dm {ctx.command.name} message", description=f"```{name}```")
    return await ctx.reply(embed=em)
   elif embed == name: return await ctx.send_warning(f"This embed is already **configured** as the {ctx.command.name} custom dm")
   else:
      await ctx.bot.db.execute("UPDATE dm SET embed = $1 WHERE guild_id = $2 AND command = $3", embed, ctx.guild.id, ctx.command.name)
      return await ctx.send_success(f"Updated your custom **{ctx.command.name}** message to\n```{embed}```")
  else: 
   await ctx.bot.db.execute("INSERT INTO dm VALUES ($1,$2,$3)", ctx.guild.id, ctx.command.name, embed)
   return await ctx.send_success(f"Added your custom **{ctx.command.name}** direct message to\n```{embed}```")

class config(Cog):
    def __init__(self, bot: AB):
        self.bot = bot 
        
    @Cog.listener()
    async def on_member_join(self, member: Member):
        if member.bot: return   
        results = await self.bot.db.fetch("SELECT * FROM pingonjoin WHERE guild_id = $1", member.guild.id)
        members = [m for m in member.guild.members if (datetime.datetime.now() - m.joined_at.replace(tzinfo=None)).total_seconds() < 180]
        for result in results: 
         channel = member.guild.get_channel(int(result[0]))
         if channel: 
          if len(members) < 10: 
            try: await channel.send(member.mention, delete_after=6)
            except: continue    
          else:           
           if not poj_cache.get(str(channel.id)): poj_cache[str(channel.id)] = []
           poj_cache[str(channel.id)].append(f"{member.mention}")
           if len(poj_cache[str(channel.id)]) == 10: 
            try: 
             await channel.send(' '.join([m for m in poj_cache[str(channel.id)]]), delete_after=6) 
             poj_cache[str(channel.id)] = []
            except:
             poj_cache[str(channel.id)] = [] 
             continue 
    
    @Cog.listener()
    async def on_message(self, message: Message):
      if not message.guild: return
      if isinstance(message.author, User): return
      if message.author.guild_permissions.manage_guild: return 
      if message.author.bot: return 
      if message.attachments: return       
      check = await self.bot.db.fetchrow("SELECT * FROM mediaonly WHERE channel_id = $1", message.channel.id)
      if check: 
        try: await message.delete()
        except: pass 
    
    @command(name="createembed", aliases=['ce'], help="config", description="create embed", usage="[code]")
    async def createembed(self, ctx: Context,  *, code: EmbedScript):
     await ctx.send(**code)

    @group(invoke_without_command=True)
    async def embed(self, ctx): 
     await ctx.create_pages() 
  
    @embed.command(help="config", description="shows variables for the embed")
    async def variables(self, ctx: Context): 
     embed1 = Embed(color=self.bot.color, title="user related variables")
     embed1.description = """
    >>> {user} - returns user full name
{user.name} - returns user's username
{user.mention} - mentions user
{user.avatar} - return user's avatar
{user.joined_at} returns the relative date the user joined the server
{user.created_at} returns the relative time the user created the account
{user.discriminator} - returns the user's discriminator
    """

     embed2 = Embed(color=self.bot.color, title="guild related variables")
     embed2.description = """
    >>> {guild.name} - returns the server's name
 {guild.count} - returns the server's member count
 {guild.count.format} - returns the server's member count in ordinal format
 {guild.icon} - returns the server's icon
 {guild.id} - returns the server's id
 {guild.vanity} - returns the server's vanity, if any 
 {guild.created_at} - returns the relative time the server was created
 {guild.boost_count} - returns the number of server's boosts
 {guild.booster_count} - returns the number of boosters
 {guild.boost_count.format} - returns the number of boosts in ordinal format
 {guild.booster_count.format} - returns the number of boosters in ordinal format
 {guild.boost_tier} - returns the server's boost level
   """
    
     embed3 = Embed(color=self.bot.color, title="invoke command only variables")
     embed3.description = """
    >>> {member} - returns member's name and discriminator
    {member.name} - returns member's name
    {member.mention} - returns member mention
    {member.discriminator} - returns member's discriminator
    {member.id} - return member's id
    {member.avatar} - returns member's avatar
    {reason} - returns action reason, if any
    """
     
     embed4 = Embed(color=self.bot.color, title="last.fm variables")
     embed4.description = """
    >>> {scrobbles} - returns all song play count
    {trackplays} - returns the track total plays
    {artistplays} - returns the artist total plays
    {albumplays} - returns the album total plays
    {track} - returns the track name
    {trackurl} - returns the track url
    {trackimage} - returns the track image
    {artist} - returns the artist name
    {artisturl} - returns the artist profile url
    {album} - returns the album name 
    {albumurl} - returns the album url
    {username} - returns your username
    {useravatar} - returns user's profile picture"""
     
     embed6 = Embed(color=self.bot.color, title="vanity variables")
     embed6.description = """
     >>> {vanityrole.name} - returns the vanity role name\n{vanityrole.mention} - returns the mention of the vanity role\n{vanityrole.id} - returns the id of the vanity role\n{vanityrole.members} - returns the number of members who have the vanity role\n{vanityrole.members.format} - returns the number of members who have the vanity role in ordinal"""

     embed5 = Embed(color=self.bot.color, title="other variables")
     embed5.description = """
    >>> {invisible} - returns the invisible embed color
    {delete} - delete the trigger (for autoresponder)"""

     await ctx.paginator([embed1, embed2, embed3, embed4, embed6, embed5])

    @embed.command(help="config", description="create an embed", usage="[code]")
    async def create(self, ctx: Context, *, name: EmbedScript): 
     return await ctx.send(**name)
   
    

    @group(invoke_without_command=True)
    async def mediaonly(self, ctx: Context):
     await ctx.create_pages()

    @mediaonly.command(name="add", description="delete messages that are not images", help="config", usage="[channel]", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def mediaonly_add(self, ctx: Context, *, channel: TextChannel):
        check = await self.bot.db.fetchrow("SELECT * FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is not None: return await ctx.send_warning(f"{channel.mention} is already added")
        elif check is None: 
          await self.bot.db.execute("INSERT INTO mediaonly VALUES ($1,$2)", ctx.guild.id, channel.id)
          return await ctx.send_success(f"added {channel.mention} as a mediaonly channel")

    @mediaonly.command(name="remove", description="unset media only", help="config", usage="[channel]", brief="manage_guild") 
    @utils.get_perms("manage_guild")
    async def mediaonly_remove(self, ctx: Context, *, channel: TextChannel=None):
     if channel is not None: 
      check = await self.bot.db.fetchrow("SELECT * FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
      if check is None: return await ctx.send_warning(f"{channel.mention} is not added") 
      await self.bot.db.execute("DELETE FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
      return await ctx.send_success(f"{channel.mention} isn't a **mediaonly** channel anymore")

     res = await self.bot.db.fetch("SELECT * FROM mediaonly WHERE guild_id = $1", ctx.guild.id) 
     if res is None: return await ctx.send_warning("There is no **mediaonly** channel in this server")
     await self.bot.db.execute("DELETE FROM mediaonly WHERE guild_id = $1", ctx.guild.id)
     return await ctx.send_success("Removed all channels") 

    @mediaonly.command(name="list", description="return a list of mediaonly channels", help="config")
    async def mediaonly_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.db.fetch("SELECT * FROM mediaonly WHERE guild_id = {}".format(ctx.guild.id))
          if len(results) == 0: return await ctx.reply("there are no mediaonly channels")
          for result in results:
              mes = f"{mes}`{k}` <#{result['channel_id']}> ({result['channel_id']})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"mediaonly channels ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
          messages.append(mes)
          number.append(Embed(color=self.bot.color, title=f"mediaonly channels ({len(results)})", description=messages[i])) 
          if len(number) > 1: return await ctx.paginator(number) 
          return await ctx.send(embed=number[0])
    
    @hybrid_group(invoke_without_command=True, aliases=["poj"])
    async def pingonjoin(self, ctx): 
      await ctx.create_pages()

    @pingonjoin.command(name="add", description="ping new members when they join your server", help="config", usage="[channel]", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def poj_add(self, ctx: Context, *, channel: TextChannel): 
        check = await self.bot.db.fetchrow("SELECT * FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is not None: return await ctx.send_warning(f"{channel.mention} is already added")
        elif check is None: await self.bot.db.execute("INSERT INTO pingonjoin VALUES ($1,$2)", channel.id, ctx.guild.id)
        return await ctx.send_success(f"I will ping new members in {channel.mention}")  
    
    @pingonjoin.command(name="remove", description="remove a pingonjoin channel", help="config", usage="<channel>", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def poj_remove(self, ctx: Context, *, channel: TextChannel=None): 
      if channel is not None: 
        check = await self.bot.db.fetchrow("SELECT * FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is None: return await ctx.send_error(f"{channel.mention} is not added")
        elif check is not None: await self.bot.db.execute("DELETE FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        return await ctx.send_success(f"I will not ping new members in {channel.mention}")

      check = await self.bot.db.fetch("SELECT * FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
      if check is None: return await ctx.send_error("there is no channel added")
      elif check is not None:  await self.bot.db.execute("DELETE FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
      return await ctx.send_success("I will not ping new members in any channel") 
    
    @pingonjoin.command(name="list", description="get a list of pingonjoin channels", help="config")
    async def poj_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.db.fetch("SELECT * FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
          if results is None: return await ctx.send_error("there are no pingonjoin channels")
          for result in results:
              mes = f"{mes}`{k}` {ctx.guild.get_channel(int(result['channel_id'])).mention if ctx.guild.get_channel(result['channel_id']) else result['channel_id']}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"pingonjoin channels ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
          messages.append(mes)
          number.append(Embed(color=self.bot.color, title=f"pingonjoin channels ({len(results)})", description=messages[i]))
          await ctx.paginator(number)
    
    @group(invoke_without_command=True)
    async def starboard(self, ctx): 
      await ctx.create_pages()

    @starboard.command(help="config", description="modify the starboard count", brief="manage guild", usage="[count]", aliases=["amount"])
    @utils.get_perms("manage_guild")
    async def count(self, ctx: Context, count: int): 
      if count < 1: return await ctx.send_warning("Count can't be **less** than 1")
      check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, count) VALUES ($1, $2)", ctx.guild.id, count)
      else: await self.bot.db.execute("UPDATE starboard SET count = $1 WHERE guild_id = $2", count, ctx.guild.id)
      await ctx.send_success(f"Starboard **count** set to **{count}**")  
    
    @starboard.command(name="channel", help="config", description="configure the starboard channel", brief="manage guild", usage="[channel]")
    @utils.get_perms("manage_guild")
    async def starboard_channel(self, ctx: Context, *, channel: TextChannel): 
      check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, channel_id) VALUES ($1, $2)", ctx.guild.id, channel.id)
      else: await self.bot.db.execute("UPDATE starboard SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
      await ctx.send_success(f"Starboard **channel** set to {channel.mention}")

    @starboard.command(name="emoji", help="config", description="configure the starboard emoji", brief="manage guild", usage="[emoji]")
    @utils.get_perms("manage_guild")
    async def starboard_emoji(self, ctx: Context, emoji: Union[PartialEmoji, str]): 
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     emoji_id = emoji.id if isinstance(emoji, PartialEmoji) else ord(str(emoji)) 
     if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, emoji_id, emoji_text) VALUES ($1,$2,$3)", ctx.guild.id, emoji_id, str(emoji)) 
     else: 
      await self.bot.db.execute("UPDATE starboard SET emoji_id = $1 WHERE guild_id = $2", emoji_id, ctx.guild.id)
      await self.bot.db.execute("UPDATE starboard SET emoji_text = $1 WHERE guild_id = $2", str(emoji), ctx.guild.id) 
     await ctx.send_success(f"Starboard **emoji** set to {emoji}") 

    @starboard.command(name="remove", help="config", description="remove starboard", brief="manage guild", aliases=["disable"])
    @utils.get_perms("manage_guild")
    async def starboard_remove(self, ctx: Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.send_warning("Starboard is not **enabled**") 
     await self.bot.db.execute("DELETE FROM starboard WHERE guild_id = $1", ctx.guild.id)
     await self.bot.db.execute("DELETE FROM starboardmes WHERE guild_id = $1", ctx.guild.id)
     await ctx.send_success("Disabled starboard **succesfully**")

    @starboard.command(help="config", description="check starboard stats", aliases=["settings", "status"])
    async def stats(self, ctx: Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.send_warning("Starboard is not **enabled**") 
     embed = Embed(color=self.bot.color, title="starboard settings")
     if ctx.guild.get_channel(int(check["channel_id"])): embed.add_field(name="channel", value=ctx.guild.get_channel(int(check["channel_id"])).mention)
     if check["count"]: embed.add_field(name="amount", value=check["count"])
     if check["emoji_text"]: embed.add_field(name="emoji", value=check["emoji_text"])
     await ctx.reply(embed=embed)

    @group(invoke_without_command=True)
    async def autorole(self, ctx): 
      await ctx.create_pages()

    @autorole.command(name="add", description="give a role to the new members that join the server", help="config", usage="[role]", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def autorole_add(self, ctx: Context, *, role: Union[Role, str]): 
      if isinstance(role, str): 
        role = ctx.find_role( role)
        if role is None: return await ctx.send_error(f"Couldn't find a role named **{ctx.message.clean_content[-len(ctx.clean_prefix)+11:]}**")         
      
      if self.bot.is_dangerous(role): return await ctx.send_warning("This role can't be an autorole")
      check = await self.bot.db.fetchrow("SELECT * FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
      if check is not None: return await ctx.send_error(f"{role.mention} is already added")
      await self.bot.db.execute("INSERT INTO autorole VALUES ($1,$2)", role.id, ctx.guild.id)      
      return await ctx.send_success(f"Added {role.mention} as autorole")
    
    @autorole.command(name="remove", description="remove a role from autoroles", help="config", usage="<role>", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def autorole_remove(self, ctx: Context, *, role: Union[Role, str]=None): 
      if isinstance(role, str): 
        role = ctx.find_role( role)
        if role is None: return await ctx.send_error(f"Couldn't find a role named **{ctx.message.clean_content[-len(ctx.clean_prefix)+14:]}**")         
      if role is not None:
        check = await self.bot.db.fetchrow("SELECT * FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
        if check is None: return await ctx.send_error(f"{role.mention} is not added")
        await self.bot.db.execute("DELETE FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
        return await ctx.send_success(f"Removed {role.mention} from autorole")

      check = await self.bot.db.fetch("SELECT * FROM autorole WHERE guild_id = {}".format(ctx.guild.id))
      if check is None: return await ctx.send_error("there is no role added".capitalize())    
      await self.bot.db.execute("DELETE FROM autorole WHERE guild_id = {}".format(ctx.guild.id))
      return await ctx.send_success("Removed all roles from autorole")
    
    @autorole.command(name="list", description="list of autoroles", help="config")
    async def autorole_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.db.fetch("SELECT * FROM autorole WHERE guild_id = {}".format(ctx.guild.id))
          if not results: return await ctx.send_warning("There are no autoroles")
          for result in results:
              mes = f"{mes}`{k}` {ctx.guild.get_role(int(result[0])).mention if ctx.guild.get_role(int(result[0])) else result[0]}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"autoroles ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
          messages.append(mes)
          number.append(Embed(color=self.bot.color, title=f"autoroles ({len(results)})", description=messages[i]))
          return await ctx.paginator(number)
    
    @group(invoke_without_command=True, description="manage custom punishment dms", help="config")
    async def dm(self, ctx): 
      await ctx.create_pages()
    

    @group(invoke_without_command=True, description="manage custom punishment responses", help="config")
    async def invoke(self, ctx): 
     await ctx.create_pages()
  
    @invoke.command(name="variables", help="config", description="check invoke variables")
    async def embed_variables(self, ctx: Context): 
     await ctx.invoke(self.bot.get_command('embed variables'))
    
    @invoke.command(name="unban", help="config", description='add a custom unban message', brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke unban --embed test\nexample 2: -invoke unban {user.mention} unbanned {member.mention}")
    @utils.get_perms("manage_guild")
    async def invoke_unban(self, ctx: Context, *, code: str):
      await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)

    @invoke.command(name="ban", help="config", description="add a custom ban command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke ban --embed test\nexample 2: -invoke ban {user.mention} banned {member.mention}")
    @utils.get_perms("manage_guild")
    async def invoke_ban(self, ctx: Context, *, code: str):
      await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code) 

    @invoke.command(name="kick", help="config", description="add a custom kick command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke kick --embed test\nexample 2: -invoke kick {user.mention} kicked {member.mention}")
    @utils.get_perms("manage_guild")
    async def invoke_kick(self, ctx: Context, *, code: str):
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)  

    @invoke.command(name="mute", help="config", description="add a custom mute command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke mute --embed test\nexample 2: -invoke mute {user.mention} muted {member.mention}")
    @utils.get_perms("manage_guild")
    async def invoke_mute(self, ctx: Context, *, code: str):
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)    
  
    @invoke.command(name="unmute", help="config", description="add a custom unmute command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke unmute --embed test\nexample 2: -invoke unmute {user.mention} unmuted {member.mention}")
    @utils.get_perms("manage_guild")
    async def invoke_unmute(self, ctx: Context, *, code: str):
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)
  
    @invoke.command(name="warn", help="config", description="add a custom warn command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke warn --embed test\nexample 2: -invoke warn {user.mention} warned {member.mention}")
    @utils.get_perms("manage_guild")
    async def invoke_warn(self, ctx: Context, *, code: str):
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)
    
    @invoke.command(name="jail", help="config", description="add a custom jail command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke jail --embed test\nexample 2: -invoke jail {user.mention} jailed {member.mention}")
    @utils.get_perms("manage_guild")
    async def invoke_jail(self, ctx: Context, *, code: str): 
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code) 
    
    @invoke.command(name="unjail", help="config", description="add a custom unjail command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke unjail --embed test\nexample 2: -invoke unjail {user.mention} unjailed {member.mention}")
    @utils.get_perms("manage_guild")
    async def invoke_unjail(self, ctx: Context, *, code: str): 
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code) 

    @group(invoke_without_command=True)
    async def bumpreminder(self, ctx): 
     await ctx.create_pages() 
    
    @bumpreminder.command(name="add", help="config", description="reminder to bump your server via disboard", brief="manage guild")
    @utils.get_perms("manage_guild")
    async def bumpreminder_add(self, ctx: Context):
       check = await self.bot.db.fetchrow("SELECT * FROM bumps WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None: return await ctx.send_warning("bump reminder is already enabled".capitalize())
       await self.bot.db.execute("INSERT INTO bumps VALUES ($1, $2)", ctx.guild.id, "true")
       return await ctx.send_success("bump reminder is now enabled".capitalize())
    
    @bumpreminder.command(name="remove", help="config", description="remove bump reminder", brief="manage guild")
    @utils.get_perms("manage_guild")
    async def bumpreminder_remove(self, ctx: Context):  
       check = await self.bot.db.fetchrow("SELECT * FROM bumps WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is None: return await ctx.send_warning("bump reminder isn't enabled".capitalize())
       await self.bot.db.execute("DELETE FROM bumps WHERE guild_id = {}".format(ctx.guild.id))
       return await ctx.send_success("bump reminder is now disabled".capitalize())  
    
    @command(aliases=["disablecmd"], description="disable a command", help="config", usage="[command name]")  
    @utils.get_perms("administrator")          
    async def disablecommand(self, ctx: Context, *, cmd: str): 
     found_command = self.bot.get_command(cmd)
     if found_command is None: return await ctx.send_warning(f"Command **{cmd}** not found")
     if found_command.name in ["ping", "help", "uptime", "disablecommand", "disablecmd", "enablecommand", "enablecmd"]: return await ctx.send_warning("This command can't be disabled")
     check = await self.bot.db.fetchrow("SELECT * FROM disablecommand WHERE command = $1 AND guild_id = $2", found_command.name, ctx.guild.id)
     if check: return await ctx.send_error("This command is **already** disabled")
     await self.bot.db.execute("INSERT INTO disablecommand VALUES ($1,$2)", ctx.guild.id, found_command.name)     
     await ctx.send_success(f"Disabled command **{found_command.name}**")

    @command(aliases=["enablecmd"], help="enable a command that was previously disabled in this server", description="config", usage="[command name]")
    @utils.get_perms("administrator")
    async def enablecommand(self, ctx: Context, *, cmd: str): 
     found_command = self.bot.get_command(cmd)
     if found_command is None: return await ctx.send_warning(f"Command **{cmd}** not found")
     check = await self.bot.db.fetchrow("SELECT * FROM disablecommand WHERE command = $1 AND guild_id = $2", found_command.name, ctx.guild.id)
     if not check: return await ctx.send_error("This command is **not** disabled")
     await self.bot.db.execute("DELETE FROM disablecommand WHERE guild_id = $1 AND command = $2", ctx.guild.id, found_command.name)     
     await ctx.send_success(f"Enabled command **{found_command.name}**")

    @hybrid_command(description="changes the guild prefix", usage="[prefix]", help="config", brief="manage guild")
    @utils.get_perms("manage_guild")
    async def prefix(self, ctx: Context, prefix: str):      
       if len(prefix) > 3: return await ctx.send_error("Uh oh! The prefix is too long")
       check = await self.bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None: await self.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
       else: await self.bot.db.execute("INSERT INTO prefixes VALUES ($1, $2)", ctx.guild.id, prefix)
       return await ctx.send_success(f"guild prefix changed to `{prefix}`".capitalize())

    @hybrid_command(description="set your own prefix", usage="[prefix]", help="config")
    async def selfprefix(self, ctx: Context, prefix: str):      
      if len(prefix) > 3 and prefix.lower() != "none": return await ctx.send_error("Uh oh! The prefix is too long")
      if prefix.lower() == "none": 
        check = await self.bot.db.fetchrow("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id)) 
        if check is not None:
          await self.bot.db.execute("DELETE FROM selfprefix WHERE user_id = {}".format(ctx.author.id))
          return await ctx.send_success("Removed your self prefix")
        elif check is None: return await ctx.send_error("you don't have a self prefix".capitalize())   
      else:    
        result = await self.bot.db.fetchrow("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id)) 
        if result is not None: await self.bot.db.execute("UPDATE selfprefix SET prefix = $1 WHERE user_id = $2", prefix, ctx.author.id)
        elif result is None: await self.bot.db.execute('INSERT INTO selfprefix VALUES ($1, $2)', ctx.author.id, prefix)
        return await ctx.send_success(f"self prefix changed to `{prefix}`".capitalize())
  
    @group(invoke_without_command=True, aliases=["fakeperms"])
    async def fakepermissions(self, ctx):
      await ctx.create_pages()

    @fakepermissions.command(description="edit fake permissions for a role", help="config", usage="[role]", brief="server owner")
    @utils.server_owner()
    async def edit(self, ctx: Context, *, role: Union[Role, str]=None): 
     if isinstance(role, str): 
        role = ctx.find_role( role)
        if role is None: return await ctx.send_warning("This is not a valid role") 
     
     perms = ["administrator", "manage_guild", "manage_roles", "manage_channels", "manage_messages", "manage_nicknames", "manage_emojis", "ban_members", "kick_members", "moderate_members"]
     options = [SelectOption(label=perm.replace("_", " "), value=perm) for perm in perms]
     embed = Embed(color=self.bot.color, description="🔍 Which permissions would you like to add to {}?".format(role.mention))
     select = Select(placeholder="select permissions", max_values=10, options=options)

     async def select_callback(interaction: Interaction):
      if ctx.author != interaction.user: return await self.bot.ext.send_warning(interaction, "This is not your embed", ephemeral=True)
      data = json.dumps(select.values)
      check = await self.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE guild_id = $1 AND role_id = $2", interaction.guild.id, role.id)
      if not check: await self.bot.db.execute("INSERT INTO fake_permissions VALUES ($1,$2,$3)", interaction.guild.id, role.id, data)
      else: await self.bot.db.execute("UPDATE fake_permissions SET permissions = $1 WHERE guild_id = $2 AND role_id = $3", data, interaction.guild.id, role.id)      
      await interaction.response.edit_message(embed=Embed(color=self.bot.color, description=f"{self.bot.yes} {interaction.user.mention}: Added **{len(select.values)}** permission{'s' if len(select.values) > 1 else ''} to {role.mention}"), view=None)

     select.callback = select_callback 
     view = View()
     view.add_item(select)
     await ctx.reply(embed=embed, view=view)            

    @fakepermissions.command(name="list", description="list the permissions of a specific role", help="config", usage="[role]")
    async def fakeperms_list(self, ctx: Context, *, role: Union[Role, str]): 
     if isinstance(role, str): 
        role = ctx.find_role(role)
        if role is None: return await ctx.send_warning("This is not a valid role") 
     
     check = await self.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE guild_id = $1 AND role_id = $2", ctx.guild.id, role.id)
     if check is None: return await ctx.send_error("This role has no fake permissions")
     permissions = json.loads(check['permissions'])
     embed = Embed(color=self.bot.color, title=f"@{role.name}'s fake permissions", description="\n".join([f"`{permissions.index(perm)+1}` {perm}" for perm in permissions]))
     embed.set_thumbnail(url=role.display_icon)
     return await ctx.reply(embed=embed)

    @fakepermissions.command(aliases=["perms"], description="list all the available permissions", help="config")
    async def permissions(self, ctx: Context): 
      perms = ["administrator", "manage_guild", "manage_roles", "manage_channels", "manage_messages", "manage_nicknames", "manage_emojis", "ban_members", "kick_members", "moderate_members"]
      embed = Embed(color=self.bot.color, description="\n".join([f"`{perms.index(perm)+1}` {perm}" for perm in perms])).set_author(icon_url=self.bot.user.display_avatar.url, name="fakepermissions perms list")
      await ctx.reply(embed=embed)  
    
    @command(help="config", description="react to a message using the bot", brief="manage messages", usage="[message id / message link] [emoji]")
    @utils.get_perms("manage_messages")
    async def react(self, ctx: Context, link: str, reaction: str):
     try: mes = await ctx.channel.fetch_message(int(link))
     except: mes = None
     if mes: 
      try:
       await mes.add_reaction(reaction)  
       view = View()
       view.add_item(Button(label="jump to message", url=mes.jump_url))
       return await ctx.reply(view=view)
      except: return await ctx.send_warning("Unable to add the reaction to that message") 
     message = await self.bot.ext.link_to_message(link)
     if not message: return await ctx.send_warning("No **message** found")
     if message.guild != ctx.guild: return await ctx.send_warning("This **message** is not from this server")
     elif message.channel.type != ChannelType.text: return await ctx.send_error("I can only react in text channels")
     try: 
      await message.add_reaction(reaction)
      v = View()
      v.add_item(Button(label="jump to message", url=message.jump_url))
      return await ctx.reply(view=v)  
     except: return await ctx.send_warning("Unable to add the reaction to that message") 
    
    @group(invoke_without_command=True, name="counter", help="config", description="create stats counters for your server")
    async def counter(self, ctx): 
      await ctx.create_pages()
    
    @counter.command(name="types", description="check the counter types and channel types")
    async def counter_types(self, ctx: Context):
      embed1 = Embed(color=self.bot.color, title="counter types")
      embed2 = Embed(color=self.bot.color, title="channel types")
      embed1.description = """>>> members - all members from the server (including bots)
      humans - all members from the server (excluding bots)
      bots - all bots from the server
      boosters - all server boosters
      voice - all members in the server's voice channels
      """
      embed2.description = """>>> voice - creates voice channel
      stage - creates stage channel 
      text - createss text channel
      """
      await ctx.paginator([embed1, embed2])

    @counter.command(name="list", help="config", description="check a list of the active server counters")
    async def counter_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.db.fetch("SELECT * FROM counters WHERE guild_id = {}".format(ctx.guild.id))
          if not results: return await ctx.send_warning("There are no counters")
          for result in results:
              mes = f"{mes}`{k}` {result['module']} -> {ctx.guild.get_channel(int(result['channel_id'])).mention if ctx.guild.get_channel(int(result['channel_id'])) else result['channel_id']}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"server counters ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
          messages.append(mes)
          number.append(Embed(color=self.bot.color, title=f"server counters ({len(results)})", description=messages[i]))
          return await ctx.paginator(number) 

    @counter.command(name="remove", help="config", description="remove a counter from the server", brief="manage guild", usage="[counter type]")
    @utils.get_perms("manage_guild")
    async def counter_remove(self, ctx: Context, countertype: str): 
     if not countertype in ["members", "voice", "boosters", "humans", "bots"]: return await ctx.send_warning(f"**{countertype}** is not an **available** counter") 
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, countertype)
     if not check: return await ctx.send_warning(f"There is no **{countertype}** counter in this server")
     channel = ctx.guild.get_channel(int(check["channel_id"]))
     if channel: await channel.delete()
     await self.bot.db.execute("DELETE FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, countertype)
     return await ctx.send_success(f"Removed **{countertype}** counter")
    
    @counter.group(invoke_without_command=True, name="add", help="config", description="add a counter to the server", brief="manage guild")
    async def counter_add(self, ctx): 
      await ctx.create_pages()

    @counter_add.command(name="members", help="config", description="add a counter for member count", brief="manage guild", usage="[channel type] <channel name>\nexample: *counter add members voice {target} Members")
    @utils.get_perms("manage_guild")
    async def counter_add_members(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send_warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send_warning("{target} variable is **missing** from the channel name")
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send_warning(f"<#{check['channel_id']}> is already a **member** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating member counter"
     name = message.replace("{target}", str(ctx.guild.member_count))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send_success(f"Created **member** counter -> {channel.mention}")  

    @counter_add.command(name="humans", help="config", description="add a counter for humans", brief="manage guild", usage="[channel type] <channel name>\nexample: *counter add humans voice {target} humans")
    @utils.get_perms("manage_guild")
    async def counter_add_humans(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send_warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send_warning("{target} variable is **missing** from the channel name")
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send_warning(f"<#{check['channel_id']}> is already a **humans** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating human counter"
     name = message.replace("{target}", str(len([m for m in ctx.guild.members if not m.bot])))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send_success(f"Created **humans** counter -> {channel.mention}")  

    @counter_add.command(name="bots", help="config", description="add a counter for bots", brief="manage guild", usage="[channel type] <channel name>\nexample: *counter add bots voice {target} bots")
    @utils.get_perms("manage_guild")
    async def counter_add_bots(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send_warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send_warning("{target} variable is **missing** from the channel name")
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send_warning(f"<#{check['channel_id']}> is already a **bots** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating bot counter"
     name = message.replace("{target}", str(len([m for m in ctx.guild.members if m.bot])))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send_success(f"Created **bots** counter -> {channel.mention}")  

    @counter_add.command(name="voice", help="config", description="add a counter for voice members", brief="manage guild", usage="[channel type] <channel name>\nexample: *counter add voice stage {target} in vc")         
    @utils.get_perms("manage_guild")
    async def counter_add_voice(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send_warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send_warning("{target} variable is **missing** from the channel name")
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send_warning(f"<#{check['channel_id']}> is already a **voice** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating voice counter"
     name = message.replace("{target}", str(sum(len(c.members) for c in ctx.guild.voice_channels)))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send_success(f"Created **voice** counter -> {channel.mention}")  

    @counter_add.command(name="boosters", help="config", description="add a counter for boosters", brief="manage guild", usage="[channel type] <channel name>\nexample: *counter add boosters voice {target} boosters") 
    @utils.get_perms("manage_guild")
    async def counter_add_boosters(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send_warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send_warning("{target} variable is **missing** from the channel name")
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send_warning(f"<#{check['channel_id']}> is already a **booster** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating booster counter"
     name = message.replace("{target}", str(len(ctx.guild.premium_subscribers)))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send_success(f"Created **boosters** counter -> {channel.mention}")         

async def setup(bot): 
    await bot.add_cog(config(bot))        