import json, discord, typing
from discord import TextChannel, ChannelType, Embed, Role, SelectOption, Interaction, PartialEmoji, PermissionOverwrite
from discord.ext.commands import Cog, Context, group, command, Bot as AB
from discord.ui import Select, View, Button 
from typing import Union
from utils.utils import InvokeClass, EmbedScript
from discord.ext import commands
from patches.permissions import Permissions

poj_cache = {}

class config(Cog):
    def __init__(self, bot: AB):
        self.bot = bot 
        self.perms = ["administrator", "manage_guild", "manage_roles", "manage_channels", "manage_messages", "manage_nicknames", "manage_expressions", "ban_members", "kick_members", "moderate_members"]
    
    @Permissions.has_permission(manage_messages=True)
    @command(name="createembed", aliases=['ce'], description="create embed", usage="[code]", brief="manage messages")
    async def createembed(self, ctx: Context,  *, code: EmbedScript):
     await ctx.send(**code)

    @group(invoke_without_command=True)
    async def embed(self, ctx): 
     await ctx.create_pages() 
  
    @embed.command(description="shows variables for the embed")
    async def variables(self, ctx: Context): 
     
     embed = Embed(color=self.bot.color, description="to view variables visit https://evict.cc/variables")
     await ctx.reply(embed=embed)

    @Permissions.has_permission(manage_messages=True)
    @embed.command(description="create an embed", usage="[code]")
    async def create(self, ctx: Context, *, name: EmbedScript): 
     return await ctx.send(**name)

    @group(invoke_without_command=True)
    async def mediaonly(self, ctx: Context):
     await ctx.create_pages()

    @mediaonly.command(name="add", description="delete messages that are not images", usage="[channel]", brief="manage_guild")
    @commands.has_permissions(manage_guild=True)
    async def mediaonly_add(self, ctx: Context, *, channel: TextChannel):
        
        check = await self.bot.db.fetchrow("SELECT * FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is not None: return await ctx.warning(f"The channel {channel.mention} is **already** added as a mediaonly channel.")
        
        elif check is None: 
          await self.bot.db.execute("INSERT INTO mediaonly VALUES ($1,$2)", ctx.guild.id, channel.id)
          return await ctx.success(f"I have **added** {channel.mention} as a **mediaonly** channel.")

    @mediaonly.command(name="remove", description="unset media only", usage="[channel]", brief="manage_guild") 
    @commands.has_permissions(manage_guild=True)
    async def mediaonly_remove(self, ctx: Context, *, channel: TextChannel=None):
     if channel is not None: 
      check = await self.bot.db.fetchrow("SELECT * FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
      if check is None: return await ctx.warning(f"The channel {channel.mention} is not added as a **mediaonly** channel.") 
      
      await self.bot.db.execute("DELETE FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
      return await ctx.success(f"The channel {channel.mention} isn't a **mediaonly** channel anymore.")

     res = await self.bot.db.fetch("SELECT * FROM mediaonly WHERE guild_id = $1", ctx.guild.id) 
     
     if res is None: return await ctx.warning("There is no **mediaonly** channel in this server.")
     await self.bot.db.execute("DELETE FROM mediaonly WHERE guild_id = $1", ctx.guild.id)
     return await ctx.success("I have removed **all** channels from mediaonly.") 

    @mediaonly.command(name="list", description="return a list of mediaonly channels", help="config")
    async def mediaonly_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          
          mes = ""
          number = []
          messages = []
          results = await self.bot.db.fetch("SELECT * FROM mediaonly WHERE guild_id = {}".format(ctx.guild.id))
          
          if len(results) == 0: return await ctx.reply("There are **no** mediaonly channels set.")
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
          
          if len(number) > 1: return await ctx.paginate(number) 
          
          return await ctx.send(embed=number[0])
    
    @commands.group(invoke_without_command=True, aliases=["poj"])
    async def pingonjoin(self, ctx): 
      await ctx.create_pages()

    @pingonjoin.command(name="add", description="ping new members when they join your server", usage="[channel]", brief="manage_guild")
    @commands.has_permissions(manage_guild=True)
    async def poj_add(self, ctx: Context, *, channel: TextChannel): 
        
        check = await self.bot.db.fetchrow("SELECT * FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is not None: return await ctx.warning(f"The channel {channel.mention} is **already** added as a ping on join channel.")
        
        elif check is None: await self.bot.db.execute("INSERT INTO pingonjoin VALUES ($1,$2)", channel.id, ctx.guild.id)
        return await ctx.success(f"I will now ping new members in {channel.mention}.")  
    
    @pingonjoin.command(name="remove", description="remove a pingonjoin channel", usage="<channel>", brief="manage_guild")
    @commands.has_permissions(manage_guild=True)
    async def poj_remove(self, ctx: Context, *, channel: TextChannel=None): 
      
      if channel is not None: 
        
        check = await self.bot.db.fetchrow("SELECT * FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is None: return await ctx.error(f"The channel {channel.mention} is **not** added as an pingonjoin channel.")
        
        elif check is not None: await self.bot.db.execute("DELETE FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        return await ctx.success(f"I will not ping new members in {channel.mention}.")

      check = await self.bot.db.fetch("SELECT * FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
      if check is None: return await ctx.error("There is no channel added.")
      
      elif check is not None:  await self.bot.db.execute("DELETE FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
      
      return await ctx.success("I will **not** ping new members in any channel.") 
          
    @pingonjoin.command(name="list", description="get a list of pingonjoin channels", help="config")
    async def poj_list(self, ctx: Context): 
          
          results = await self.bot.db.fetch("SELECT * FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
          
          if results is None: return await ctx.error("There are **no** pingonjoin channels.")
          
          poj_list = [{ctx.guild.get_channel(int(result['channel_id'])).mention if ctx.guild.get_channel(result['channel_id']) else result['channel_id']}
          for result in results]
          
          await ctx.paginate(poj_list)
    
    @commands.group(invoke_without_command=True)
    async def starboard(self, ctx): 
      await ctx.create_pages()

    @starboard.command(description="modify the starboard count", brief="manage guild", usage="[count]", aliases=["amount"])
    @commands.has_permissions(manage_guild=True)
    async def count(self, ctx: Context, count: int): 
      
      if count < 1: return await ctx.warning("The count can't be **less** than 1.")
      check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
      
      if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, count) VALUES ($1, $2)", ctx.guild.id, count)
      
      else: await self.bot.db.execute("UPDATE starboard SET count = $1 WHERE guild_id = $2", count, ctx.guild.id)
      await ctx.success(f"I have set the starboard **count** set to **{count}**.")  
    
    @starboard.command(name="channel", description="configure the starboard channel", brief="manage guild", usage="[channel]")
    @commands.has_permissions(manage_guild=True)
    async def starboard_channel(self, ctx: Context, *, channel: TextChannel): 
      
      check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, channel_id) VALUES ($1, $2)", ctx.guild.id, channel.id)
      
      else: await self.bot.db.execute("UPDATE starboard SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
      await ctx.success(f"I have set the starboard **channel** set to {channel.mention}.")

    @starboard.command(name="remove", description="remove starboard", brief="manage guild", aliases=["disable"])
    @commands.has_permissions(manage_guild=True)
    async def starboard_remove(self, ctx: Context): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.warning("This server does not have starboard **enabled**.") 
     
     await self.bot.db.execute("DELETE FROM starboard WHERE guild_id = $1", ctx.guild.id)
     await self.bot.db.execute("DELETE FROM starboardmes WHERE guild_id = $1", ctx.guild.id)
     
     await ctx.success("I have disabled starboard **succesfully**.")

    @starboard.command(description="check starboard stats", aliases=["settings", "status"])
    async def stats(self, ctx: Context): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.warning("This server does not have starboard **enabled**.") 
     
     embed = Embed(color=self.bot.color, title="starboard settings")
     
     if ctx.guild.get_channel(int(check["channel_id"])): embed.add_field(name="channel", value=ctx.guild.get_channel(int(check["channel_id"])).mention)
     if check["count"]: embed.add_field(name="amount", value=check["count"])
     if check["emoji_text"]: embed.add_field(name="emoji", value=check["emoji_text"])
     
     await ctx.reply(embed=embed)

    @starboard.command(name="emoji", description="configure the starboard emoji", brief="manage guild", usage="[emoji]")
    async def starboard_emoji(self, ctx: Context, emoji: Union[PartialEmoji, str]): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     emoji_id = emoji.id if isinstance(emoji, PartialEmoji) else ord(str(emoji)) 
     
     if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, emoji_id, emoji_text) VALUES ($1,$2,$3)", ctx.guild.id, emoji_id, str(emoji)) 
     
     else: 
      
      await self.bot.db.execute("UPDATE starboard SET emoji_id = $1 WHERE guild_id = $2", emoji_id, ctx.guild.id)
      await self.bot.db.execute("UPDATE starboard SET emoji_text = $1 WHERE guild_id = $2", str(emoji), ctx.guild.id) 
     
     await ctx.success(f"I have set the starboard **emoji** set to {emoji}.") 

    @commands.group(invoke_without_command=True)
    async def autorole(self, ctx): 
      await ctx.create_pages()

    @autorole.command(name="add", description="give a role to the new members that join the server", usage="[role]", brief="manage_guild")
    @commands.has_permissions(manage_guild=True)
    async def autorole_add(self, ctx: Context, *, role: Union[Role, str]): 
      
      if isinstance(role, str): 
        role = ctx.find_role( role)
        
        if role is None: 
          return await ctx.error(f"I couldn't find a role named **{ctx.message.clean_content[-len(ctx.clean_prefix)+11:]}**.")         
      
      if self.bot.ext.is_dangerous(role): 
        return await ctx.warning("I **cannot** assign roles with dangerous permissions as autorole.")
      
      check = await self.bot.db.fetchrow("SELECT * FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
      if check is not None: return await ctx.error(f"{role.mention} is already added as an autorole.")
      
      await self.bot.db.execute("INSERT INTO autorole VALUES ($1,$2)", role.id, ctx.guild.id)      
      return await ctx.success(f"I have **added** {role.mention} as an autorole.")
    
    @autorole.command(name="remove", description="remove a role from autoroles", usage="<role>", brief="manage_guild")
    @commands.has_permissions(manage_guild=True)
    async def autorole_remove(self, ctx: Context, *, role: Union[Role, str]=None): 
      if isinstance(role, str): 
        role = ctx.find_role( role)
        if role is None: return await ctx.error(f"I couldn't find a role named **{ctx.message.clean_content[-len(ctx.clean_prefix)+14:]}**.")         
      
      if role is not None:
        
        check = await self.bot.db.fetchrow("SELECT * FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
        if check is None: return await ctx.error(f"{role.mention} is not added")
        
        await self.bot.db.execute("DELETE FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
        return await ctx.success(f"I have **removed** {role.mention} from autorole.")

      check = await self.bot.db.fetch("SELECT * FROM autorole WHERE guild_id = {}".format(ctx.guild.id))
      if check is None: return await ctx.error("There are no autoroles set.")    
      
      await self.bot.db.execute("DELETE FROM autorole WHERE guild_id = {}".format(ctx.guild.id))
      return await ctx.success("I have **removed** all roles from autorole.")
    
    @autorole.command(name="list", description="list of autoroles", help="config")
    async def autorole_list(self, ctx: Context): 
          
          i=0
          k=1
          l=0
          
          mes = ""
          number = []
          messages = []
          results = await self.bot.db.fetch("SELECT * FROM autorole WHERE guild_id = {}".format(ctx.guild.id))
          
          if not results: return await ctx.warning("There are **no** autoroles set in this server.")
          
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
          
          return await ctx.paginate(number)

    @commands.group(invoke_without_command=True, description="manage custom punishment responses", help="config")
    async def invoke(self, ctx): 
     await ctx.create_pages()
  
    @invoke.command(name="variables", description="check invoke variables")
    async def embed_variables(self, ctx: Context): 
     await ctx.invoke(self.bot.get_command('embed variables'))
    
    @invoke.command(name="unban", description='add a custom unban message', brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke unban --embed test\nexample 2: -invoke unban {user.mention} unbanned {member.mention}")
    @commands.has_permissions(manage_guild=True)
    async def invoke_unban(self, ctx: Context, *, code: str):
      await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)

    @invoke.command(name="ban", description="add a custom ban command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke ban --embed test\nexample 2: -invoke ban {user.mention} banned {member.mention}")
    @commands.has_permissions(manage_guild=True)
    async def invoke_ban(self, ctx: Context, *, code: str):
      await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code) 

    @invoke.command(name="kick", description="add a custom kick command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke kick --embed test\nexample 2: -invoke kick {user.mention} kicked {member.mention}")
    @commands.has_permissions(manage_guild=True)
    async def invoke_kick(self, ctx: Context, *, code: str):
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)  

    @invoke.command(name="mute", description="add a custom mute command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke mute --embed test\nexample 2: -invoke mute {user.mention} muted {member.mention}")
    @commands.has_permissions(manage_guild=True)
    async def invoke_mute(self, ctx: Context, *, code: str):
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)    
  
    @invoke.command(name="unmute", description="add a custom unmute command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke unmute --embed test\nexample 2: -invoke unmute {user.mention} unmuted {member.mention}")
    @commands.has_permissions(manage_guild=True)
    async def invoke_unmute(self, ctx: Context, *, code: str):
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)
  
    @invoke.command(name="warn", description="add a custom warn command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke warn --embed test\nexample 2: -invoke warn {user.mention} warned {member.mention}")
    @commands.has_permissions(manage_guild=True)
    async def invoke_warn(self, ctx: Context, *, code: str):
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code)
    
    @invoke.command(name="jail", description="add a custom jail command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke jail --embed test\nexample 2: -invoke jail {user.mention} jailed {member.mention}")
    @commands.has_permissions(manage_guild=True)
    async def invoke_jail(self, ctx: Context, *, code: str): 
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code) 
    
    @invoke.command(name="unjail", description="add a custom unjail command", brief="manage guild", usage="[--embed embed name | message]\nexample 1: -invoke unjail --embed test\nexample 2: -invoke unjail {user.mention} unjailed {member.mention}")
    @commands.has_permissions(manage_guild=True)
    async def invoke_unjail(self, ctx: Context, *, code: str): 
     await InvokeClass.invoke_cmds(ctx, ctx.guild.me, code) 

    @commands.group(invoke_without_command=True)
    async def bumpreminder(self, ctx): 
     await ctx.create_pages() 
    
    @bumpreminder.command(name="add", description="reminder to bump your server via disboard", brief="manage guild")
    @commands.has_permissions(manage_guild=True)
    async def bumpreminder_add(self, ctx: Context):
       
       check = await self.bot.db.fetchrow("SELECT * FROM bumps WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None: return await ctx.warning("I **already** have bump reminder setup.")
       
       await self.bot.db.execute("INSERT INTO bumps VALUES ($1, $2)", ctx.guild.id, "true")
       return await ctx.success("I have **enabled** the bump reminder.")
    
    @bumpreminder.command(name="remove", description="remove bump reminder", brief="manage guild")
    @commands.has_permissions(manage_guild=True)
    async def bumpreminder_remove(self, ctx: Context):  
       
       check = await self.bot.db.fetchrow("SELECT * FROM bumps WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is None: return await ctx.warning("There is **no** bump reminder set.")
       
       await self.bot.db.execute("DELETE FROM bumps WHERE guild_id = {}".format(ctx.guild.id))
       return await ctx.success("I have **disabled** the bump reminder.")  
    
    @command(aliases=["disablecmd"], description="disable a command", brief='administrator', usage="[command name]")  
    @commands.has_permissions(administrator=True)       
    async def disablecommand(self, ctx: Context, *, cmd: str): 
     
     found_command = self.bot.get_command(cmd)
     if found_command is None: return await ctx.warning(f"Command **{cmd}** not found")
     if found_command.name in ["ping", "help", "uptime", "disablecommand", "disablecmd", "enablecommand", "enablecmd"]: return await ctx.warning("This command can't be disabled")
     
     check = await self.bot.db.fetchrow("SELECT * FROM disablecommand WHERE command = $1 AND guild_id = $2", found_command.name, ctx.guild.id)
     if check: return await ctx.error("This command is **already** disabled.")
     
     await self.bot.db.execute("INSERT INTO disablecommand VALUES ($1,$2)", ctx.guild.id, found_command.name)     
     await ctx.success(f"I have disabled the command **{found_command.name}**.")

    @commands.command(aliases=["enablecmd"], help="enable a command that was previously disabled in this server", brief='administrator', description="config", usage="[command name]")
    @commands.has_permissions(administrator=True)   
    async def enablecommand(self, ctx: Context, *, cmd: str): 
     
     found_command = self.bot.get_command(cmd)
     if found_command is None: return await ctx.warning(f"The command **{cmd}** was not found.")
     
     check = await self.bot.db.fetchrow("SELECT * FROM disablecommand WHERE command = $1 AND guild_id = $2", found_command.name, ctx.guild.id)
     if not check: return await ctx.error("This command is **not** disabled.")
     
     await self.bot.db.execute("DELETE FROM disablecommand WHERE guild_id = $1 AND command = $2", ctx.guild.id, found_command.name)     
     await ctx.success(f"I have **enabled** the command **{found_command.name}**.")

    @commands.group(invoke_without_command=True)
    async def confessions(self, ctx): 
      await ctx.create_pages()
    
    @confessions.command(name="mute", description="mute a member that send a specific confession", usage="[confession number]", brief="manage messages")
    @commands.has_permissions(manage_messages=True)   
    async def confessions_mute(self, ctx: Context, *, number: int): 
     
     check = await self.bot.db.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
     if check is None: return await ctx.warning("Confessions aren't **enabled** in this server.") 
     
     re = await self.bot.db.fetchrow("SELECT * FROM confess_members WHERE guild_id = $1 AND confession = $2", ctx.guild.id, number)
     if re is None: return await ctx.warning("I **couldn't** find that confession.")
     
     member_id = re['user_id']
     
     r = await self.bot.db.fetchrow("SELECT * FROM confess_mute WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member_id)
     if r: return await ctx.warning("This **member** is **already** confession muted")
     
     await self.bot.db.execute("INSERT INTO confess_mute VALUES ($1,$2)", ctx.guild.id, member_id)
     return await ctx.success(f"I have **muted** the author of confession #{number}.") 
    
    @confessions.command(name="unmute", description="unmute a member that send a specific confession", usage="[confession count | all (unmutes all members)]", brief="manage messages")
    @commands.has_permissions(manage_messages=True) 
    async def connfessions_unmute(self, ctx: Context, *, number: str): 
      
      check = await self.bot.db.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
      if check is None: return await ctx.warning("Confessions aren't **enabled** in this server")  
      
      if number == "all": 
       await self.bot.db.execute("DELETE FROM confess_mute WHERE guild_id = $1", ctx.guild.id)
       return await ctx.success("I have unmuted **everyone** in confession mute.") 
      
      num = int(number)
      re = await self.bot.db.fetchrow("SELECT * FROM confess_members WHERE guild_id = $1 AND confession = $2", ctx.guild.id, num)
      
      if re is None: return await ctx.warning("I **couldn't** find that confession.")
      member_id = re['user_id']
      
      r = await self.bot.db.fetchrow("SELECT * FROM confess_mute WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member_id)
      if not r: return await ctx.warning("This **member** is **not** confession muted.")
      
      await self.bot.db.execute("DELETE FROM confess_mute WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member_id)
      return await ctx.success(f"I have **unmuted** the author of confession #{number}.") 
    
    @confessions.command(name="add", description="set confession channel", usage="[channel]", brief="manage_guild")
    @commands.has_permissions(manage_guild=True)
    async def confessions_add(self, ctx: Context, *, channel: TextChannel): 
       
       check = await self.bot.db.fetchrow("SELECT * FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None: await self.bot.db.execute("UPDATE confess SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
       
       elif check is None: await self.bot.db.execute("INSERT INTO confess VALUES ($1,$2,$3)", ctx.guild.id, channel.id, 0)
       return await ctx.success(f"I have set the confessions channel to {channel.mention}.")
    
    @confessions.command(name="remove", description="remove confession channel", brief="manage_guild")
    @commands.has_permissions(manage_guild=True)
    async def confessions_remove(self, ctx: Context): 
       
       check = await self.bot.db.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is None: return await ctx.warning("Confessions aren't **enabled** in this server.")
       
       await self.bot.db.execute("DELETE FROM confess WHERE guild_id = {}".format(ctx.guild.id))
       await self.bot.db.execute("DELETE FROM confess_members WHERE guild_id = {}".format(ctx.guild.id))
       await self.bot.db.execute("DELETE FROM confess_mute WHERE guild_id = {}".format(ctx.guild.id))
       
       return await ctx.success("I have **disabled** confessions for this server.")
    
    @confessions.command(name="channel", description="get the confessions channel", help="config")
    async def confessions_channel(self, ctx: Context): 
       
       check = await self.bot.db.fetchrow("SELECT * FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None:
        
        channel = ctx.guild.get_channel(check['channel_id'])   
        embed = Embed(color=self.bot.color, description=f"confession channel: {channel.mention}\nconfessions sent: **{check['confession']}**")
        
        return await ctx.reply(embed=embed)
       return await ctx.warning("Confessions aren't **enabled** in this server.")
    
    @commands.command(description="changes the guild prefix", usage="[prefix]", brief="manage guild")
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx: Context, prefix: str):      
       
       if len(prefix) > 3: return await ctx.error("Uh oh! The prefix is too long")
       check = await self.bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = {}".format(ctx.guild.id)) 
       
       if check is not None: await self.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
       else: await self.bot.db.execute("INSERT INTO prefixes VALUES ($1, $2)", ctx.guild.id, prefix)
       
       return await ctx.success(f"I have **changed** your guild prefix changed to `{prefix}`.")

    @commands.command(description="set your own prefix", usage="[prefix]", help="config")
    async def selfprefix(self, ctx: Context, prefix: str):      
      
      if len(prefix) > 3 and prefix.lower() != "none": return await ctx.error("Uh oh! The prefix is too long")
      if prefix.lower() == "none": 
        
        check = await self.bot.db.fetchrow("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id)) 
        if check is not None:
          
          await self.bot.db.execute("DELETE FROM selfprefix WHERE user_id = {}".format(ctx.author.id))
          return await ctx.success("I have **removed** your self prefix.")
        
        elif check is None: return await ctx.error("You **don't** have a self prefix.")   
      else:    
        
        result = await self.bot.db.fetchrow("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id)) 
        if result is not None: await self.bot.db.execute("UPDATE selfprefix SET prefix = $1 WHERE user_id = $2", prefix, ctx.author.id)
        
        elif result is None: await self.bot.db.execute('INSERT INTO selfprefix VALUES ($1, $2)', ctx.author.id, prefix)
        return await ctx.success(f"I have **set** your self prefix to `{prefix}`.")
  
    @commands.group(invoke_without_command=True, aliases=["fakeperms"])
    async def fakepermissions(self, ctx):
      await ctx.create_pages()

    @fakepermissions.command(description="edit fake permissions for a role", usage="[role]", brief="server owner")
    @Permissions.server_owner()
    async def edit(self, ctx: Context, *, role: Union[Role, str]=None): 
     
     if isinstance(role, str): 
        
        role = ctx.find_role( role)
        if role is None: return await ctx.warning("This is not a valid role") 
     
     perms = ["administrator", "manage_guild", "manage_roles", "manage_channels", "manage_messages", "manage_nicknames", "manage_emojis", "ban_members", "kick_members", "moderate_members"]
     options = [SelectOption(label=perm.replace("_", " "), value=perm) for perm in perms]
     
     embed = Embed(color=self.bot.color, description="🔍 Which permissions would you like to add to {}?".format(role.mention))
     select = Select(placeholder="select permissions", max_values=10, options=options)

     async def select_callback(interaction: Interaction):
      
      if ctx.author != interaction.user: return await self.bot.ext.warning(interaction, "This is not your embed", ephemeral=True)
      data = json.dumps(select.values)
      check = await self.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE guild_id = $1 AND role_id = $2", interaction.guild.id, role.id)
      
      if not check: await self.bot.db.execute("INSERT INTO fake_permissions VALUES ($1,$2,$3)", interaction.guild.id, role.id, data)
      else: await self.bot.db.execute("UPDATE fake_permissions SET permissions = $1 WHERE guild_id = $2 AND role_id = $3", data, interaction.guild.id, role.id)      
      
      await interaction.response.edit_message(embed=Embed(color=self.bot.color, description=f"{self.bot.yes} {interaction.user.mention}: Added **{len(select.values)}** permission{'s' if len(select.values) > 1 else ''} to {role.mention}"), view=None)

     select.callback = select_callback 
     
     view = View()
     view.add_item(select)
     
     await ctx.reply(embed=embed, view=view)      

    @fakepermissions.command(description='Toggle Anti-Nuke', help="[Module]", usage="ban",  brief="Anti-Nuke Admin")
    @Permissions.server_owner()
    async def add(self, ctx: commands.Context, permissions: str, role: discord.Role):
      
      if permissions not in self.perms: return await ctx.warning('that is not a valid **fakepermission**.')
      if permissions in self.perms:
        
        check = await self.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE guild_id = $1 AND role_id = $2", ctx.guild.id, role.id)
      if not check: await self.bot.db.execute("INSERT INTO fake_permissions VALUES ($1,$2,$3)", ctx.guild.id, role.id, permissions)
      
      else: await self.bot.db.execute("UPDATE fake_permissions SET permissions = $1 WHERE guild_id = $2 AND role_id = $3", ["permissions"], ctx.guild.id, role.id)  
      await ctx.success('fakepermissions have been updated.')

    @fakepermissions.command(name="list", description="list the permissions of a specific role", usage="[role]")
    async def fakeperms_list(self, ctx: Context, *, role: Union[Role, str]): 
     if isinstance(role, str): 
        
        role = ctx.find_role(role)
        if role is None: return await ctx.warning("This is not a valid role") 
     
     check = await self.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE guild_id = $1 AND role_id = $2", ctx.guild.id, role.id)
     if check is None: return await ctx.error("This role has no fake permissions")
     permissions = json.loads(check['permissions'])
     
     embed = Embed(color=self.bot.color, title=f"@{role.name}'s fake permissions", description="\n".join([f"`{permissions.index(perm)+1}` {perm}" for perm in permissions]))
     embed.set_thumbnail(url=role.display_icon)
     
     return await ctx.reply(embed=embed)

    @fakepermissions.command(aliases=["perms"], description="list all the available permissions", help="config")
    async def permissions(self, ctx: Context): 
      
      perms = ["administrator", "manage_guild", "manage_roles", "manage_channels", "manage_messages", "manage_nicknames", "manage_emojis", "ban_members", "kick_members", "moderate_members"]
      
      embed = Embed(color=self.bot.color, description="\n".join([f"`{perms.index(perm)+1}` {perm}" for perm in perms])).set_author(icon_url=self.bot.user.display_avatar.url, name="fakepermissions perms list")
      await ctx.reply(embed=embed)  
    
    @command(description="react to a message using the bot", brief="manage messages", usage="[message id / message link] [emoji]")
    @commands.has_permissions(manage_messages=True) 
    async def react(self, ctx: Context, link: str, reaction: str):
     
     try: mes = await ctx.channel.fetch_message(int(link))
     except: mes = None
     
     if mes: 
      try:
       
       await mes.add_reaction(reaction)  
       
       view = View()
       view.add_item(Button(label="jump to message", url=mes.jump_url))
       
       return await ctx.reply(view=view)
      except: return await ctx.warning("I am unable to add the reaction to that message.") 
     
     message = await self.bot.ext.link_to_message(link)
     
     if not message: return await ctx.warning("No **message** found")
     if message.guild != ctx.guild: return await ctx.warning("This **message** is not from this server.")
     
     elif message.channel.type != ChannelType.text: return await ctx.error("I can only react in text channels.")
     
     try: 
      
      await message.add_reaction(reaction)
      
      v = View()
      v.add_item(Button(label="jump to message", url=message.jump_url))
      
      return await ctx.reply(view=v)  
     
     except: return await ctx.warning("I am unable to add the reaction to that message.") 
    
    @commands.group(invoke_without_command=True, name="counter", description="create stats counters for your server")
    async def counter(self, ctx): 
      await ctx.create_pages()
    
    @counter.command(name="types", description="check the counter types and channel types")
    async def counter_types(self, ctx: Context):
      embed = Embed(color=self.bot.color, description="to view counters visit https://evict.cc/counters")
      await ctx.reply(embed=embed)

    @counter.command(name="list", description="check a list of the active server counters")
    async def counter_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          
          mes = ""
          number = []
          messages = []
          
          results = await self.bot.db.fetch("SELECT * FROM counters WHERE guild_id = {}".format(ctx.guild.id))
          if not results: return await ctx.warning("There are **no** counters in this server.")
          
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
          
          return await ctx.paginate(number) 

    @counter.command(name="remove", description="remove a counter from the server", brief="manage guild", usage="[counter type]")
    @commands.has_permissions(manage_guild=True)
    async def counter_remove(self, ctx: Context, countertype: str): 
     
     if not countertype in ["members", "voice", "boosters", "humans", "bots"]: return await ctx.warning(f"**{countertype}** is not an **available** counter.") 
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, countertype)
     
     if not check: return await ctx.warning(f"There is no **{countertype}** counter in this server.")
     channel = ctx.guild.get_channel(int(check["channel_id"]))
     
     if channel: await channel.delete()
     
     await self.bot.db.execute("DELETE FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, countertype)
     return await ctx.success(f"I have removed the **{countertype}** counter.")
    
    @counter.group(invoke_without_command=True, name="add", description="add a counter to the server", brief="manage guild")
    async def counter_add(self, ctx): 
      await ctx.create_pages()

    @counter_add.command(name="members", description="add a counter for member count", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add members voice {target} Members")
    @commands.has_permissions(manage_guild=True)
    async def counter_add_members(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     
     if not channeltype in ["voice", "text", "stage"]: return await ctx.warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.warning("{target} variable is **missing** from the channel name.")
     
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.warning(f"The channel <#{check['channel_id']}> is already a **member** counter.")
     
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     
     reason="creating member counter"
     name = message.replace("{target}", str(ctx.guild.member_count))
     
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.success(f"I created the **member** counter -> {channel.mention}.")  

    @counter_add.command(name="humans", description="add a counter for humans", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add humans voice {target} humans")
    @commands.has_permissions(manage_guild=True)
    async def counter_add_humans(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     
     if not channeltype in ["voice", "text", "stage"]: return await ctx.warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.warning("The {target} variable is **missing** from the channel name.")
     
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.warning(f"The channel <#{check['channel_id']}> is already a **humans** counter.")
     
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     
     reason="creating human counter"
     name = message.replace("{target}", str(len([m for m in ctx.guild.members if not m.bot])))
     
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.success(f"I created the **humans** counter -> {channel.mention}.")  

    @counter_add.command(name="bots", description="add a counter for bots", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add bots voice {target} bots")
    @commands.has_permissions(manage_guild=True)
    async def counter_add_bots(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     
     if not channeltype in ["voice", "text", "stage"]: return await ctx.warning(f"**{channeltype}** is not a **valid** channel type.")     
     if not "{target}" in message: return await ctx.warning("The {target} variable is **missing** from the channel name.")
     
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.warning(f"The channel <#{check['channel_id']}> is already a **bots** counter.")
     
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     
     reason="creating bot counter"
     name = message.replace("{target}", str(len([m for m in ctx.guild.members if m.bot])))
     
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.success(f"I created the **bots** counter -> {channel.mention}.")  

    @counter_add.command(name="voice", description="add a counter for voice members", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add voice stage {target} in vc")         
    @commands.has_permissions(manage_guild=True)
    async def counter_add_voice(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     
     if not channeltype in ["voice", "text", "stage"]: return await ctx.warning(f"**{channeltype}** is not a **valid** channel type.")     
     if not "{target}" in message: return await ctx.warning("The {target} variable is **missing** from the channel name.")
     
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.warning(f"The channel <#{check['channel_id']}> is already a **voice** counter.")
     
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     
     reason="creating voice counter"
     name = message.replace("{target}", str(sum(len(c.members) for c in ctx.guild.voice_channels)))
     
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.success(f"I created the **voice** counter -> {channel.mention}.")  

    @counter_add.command(name="boosters", description="add a counter for boosters", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add boosters voice {target} boosters") 
    @commands.has_permissions(manage_guild=True)
    async def counter_add_boosters(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     
     if not channeltype in ["voice", "text", "stage"]: return await ctx.warning(f"**{channeltype}** is not a **valid** channel type.")     
     if not "{target}" in message: return await ctx.warning("{target} variable is **missing** from the channel name.")
     
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.warning(f"The channel <#{check['channel_id']}> is already a **booster** counter.")
     
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     
     reason="creating booster counter"
     name = message.replace("{target}", str(len(ctx.guild.premium_subscribers)))
     
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(send_messages=False)})
     
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.success(f"I created the **boosters** counter -> {channel.mention}.") 
    
    @commands.group(name="stickymessage", aliases=["stickymsg", "sticky"], invoke_without_command=True)
    async def stickymessage(self, ctx: commands.Context):
        return await ctx.create_pages()

    @stickymessage.command(name='add', description='add a sticky message', help="chat", brief="manage guild", aliases=['set'], usage="[channel] [message]")
    @Permissions.has_permission(manage_guild=True) 
    async def stickymessage_add(self, ctx, channel: typing.Optional[discord.TextChannel] = None, *, key: str):
        
        if channel is None:
          channel = ctx.channel
        
        if await ctx.bot.db.fetch("SELECT * FROM stickym WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id): return await ctx.warning(f"You already have a sticky message for {channel.mention}.")
        
        await ctx.bot.db.execute("INSERT INTO stickym VALUES ($1, $2, $3)", ctx.guild.id, channel.id, key)
        return await ctx.success(f'I have successfully **added** the sticky message.')

    @stickymessage.command(name="remove", brief="manage guild")
    @Permissions.has_permission(manage_guild=True)
    async def stickymessage_remove(self, ctx, channel: typing.Optional[discord.TextChannel] = None):
        
        if channel is None:
          channel = ctx.channel
        
        check = await self.bot.db.fetchrow("SELECT * FROM stickym WHERE channel_id = $1", channel.id)
        if not check:
            return await ctx.warning("There is no sticky message configured in this channel.")
        
        await self.bot.db.execute("DELETE FROM stickym WHERE channel_id = $1", channel.id)
        return await ctx.success(f"I **deleted** the sticky message from {channel.mention}.")

    @stickymessage.command(name="config", brief="manage guild", aliases=["list", "l"])
    @Permissions.has_permission(manage_guild=True)
    async def stickymessage_config(self, ctx: commands.context):
        
        results = await self.bot.db.fetch("SELECT * FROM stickym WHERE guild_id = $1", ctx.guild.id)
        if not results:
            return await ctx.warning("There is no sticky message configured in this server.")
        
        embeds = [
            Embed(color=self.bot.color, title=f"sticky messages", description=f"{ctx.guild.get_channel(result['channel_id'])} ```{result['key']}```",).set_footer(text=f"{results.index(result)+1}/{len(results)}")
            for result in results]
        
        await ctx.paginate(embeds)
        
    @commands.group(name="restrictcommand", aliases=["rc"], invoke_without_command=True)
    async def restrictcommand(self, ctx: commands.Context):
      return await ctx.create_pages()
    
    @restrictcommand.command(name="add", description="restrict a command to a role", brief="server owner", usage="[command] [role]")
    @Permissions.server_owner()
    async def restrictcommand_add(self, ctx: commands.Context, command: str, *, role: Role): 
      
      command = command.replace(".", "")
      _command = self.bot.get_command(command)
      
      if not _command: 
        return await ctx.warning(f"The command `{command}` does not exist.")
      
      if _command.name in ("help", "restrictcommand", "disablecmd", "enablecmd"):
        return await ctx.warning("I **cannot allow** you to restrict these commands.")
      
      if not await self.bot.db.fetchrow("SELECT * FROM restrictcommand WHERE guild_id = $1 AND command = $2 AND role_id = $3", ctx.guild.id, _command.qualified_name, role.id):
        await ctx.bot.db.execute("INSERT INTO restrictcommand VALUES ($1, $2, $3)", ctx.guild.id, command, role.id)
      
      else:
        return await ctx.warning(f"The command `{_command.qualified_name}` is **already** restricted to {role.mention}.")
      
      await ctx.success(f"I am now **allowing** members with {role.mention} to use `{_command.qualified_name}`.")
      
    @restrictcommand.command(name="delete", description="remove a command from being restricted.", brief="server owner")
    @Permissions.server_owner()
    async def restrictcommand_delete(self, ctx: commands.Context, command: str, role: Role):
      
      command = command.replace(".", "")
      _command = self.bot.get_command(command)
      
      if not _command: 
        return await ctx.warning(f"The command `{command}` does not exist.")
      
      if await self.bot.db.fetchrow("SELECT * FROM restrictcommand WHERE guild_id = $1 AND command = $2 AND role_id = $3", ctx.guild.id, _command.qualified_name, role.id):
        await self.bot.db.execute("""DELETE FROM restrictcommand WHERE guild_id = $1 AND command = $2 AND role_id = $3""", ctx.guild.id, _command.qualified_name, role.id)
      else: return await ctx.warning(f"`{_command.qualified_name}` is **not** restricted to {role.mention}")
    
      await ctx.success(f"I am **no longer** allowing members with {role.mention} to use `{_command.qualified_name}`.")
     
async def setup(bot): 
    await bot.add_cog(config(bot))