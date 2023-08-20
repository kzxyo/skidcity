import discord, traceback, datetime, json
from discord.ext import commands
from tools.utils.checks import Perms, Messages
from typing import Union
from tools.utils.utils import EmbedScript, Invoke

poj_cache = {}

class Config(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
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
    
    @commands.group(invoke_without_command=True)
    async def guildedit(self, ctx):
        await ctx.create_pages()
    
    @guildedit.command(name="name", description="edit the server's name", help="config", usage="[name]")
    @Perms.get_perms("manage_guild")
    async def guildedit_name(self, ctx: commands.Context, *, name: str=None):
        await ctx.guild.edit(name=name)
        return await ctx.send_success("Changed server's name to **{}**".format(name))
    
    @guildedit.command(name="description", description="edit the server's description", help="config", usage="[description]")
    @Perms.get_perms("manage_guild")
    async def guildedit_description(self, ctx: commands.Context, *, desc: str=None):
        await ctx.guild.edit(description=desc)
        return await ctx.send_success("Changed server's description to **{}**".format(desc))
    
    @guildedit.command(name="icon", description="edit the server's icon", help="config", usage="[attachment]")
    @Perms.get_perms("manage_guild")
    async def guildedit_icon(self, ctx: commands.Context, *, url: str=None):
        if not url: url = discord.Attachment
        icon = await self.bot.session.read(url)
        await ctx.guild.edit(icon=icon)
        await ctx.send_success("Changed server icon")
    
    @guildedit.command(name="banner", description="edit the server's banner", help="config", usage="[attachment]")
    @Perms.get_perms("manage_guild")
    async def guildedit_banner(self, ctx: commands.Context):
        banner = await self.bot.session.read(ctx.message.attachments[0].url)
        await ctx.guild.edit(banner=banner)
        await ctx.send_success("Changed server banner")
    
    @guildedit.command(name="splash", description="edit the server's splash", help="config", usage="[attachment]")
    @Perms.get_perms("manage_guild")
    async def guildedit_splash(self, ctx: commands.Context):
        splash = await self.bot.session.read(ctx.message.attachments[0].url)
        await ctx.guild.edit(splash=splash)
        await ctx.send_success("Changed server splash")
    
    @commands.command(description="create an embed using the embed parser", help="config", usage="[code]", aliases=["ce"])
    async def createembed(self, ctx: commands.Context, *, code: EmbedScript):
     await ctx.send(**code)
    
    @commands.group(invoke_without_command=True)
    async def embed(self, ctx): 
     await ctx.create_pages() 
  
    @embed.command(help="config", description="shows variables for the embed")
    async def variables(self, ctx: commands.Context): 
     embed1 = discord.Embed(color=self.bot.color, title="user variables")
     embed1.description = """
     {user} - returns user full name
{user.name} - returns user's username
{user.mention} - mentions user
{user.joined_at} returns the relative date the user joined the server
{user.created_at} returns the relative time the user created the account
    """

     embed2 = discord.Embed(color=self.bot.color, title="guild variables")
     embed2.description = """
     {guild.name} - returns the server's name
{guild.count} - returns the server's member count
{guild.icon} - returns the server's icon
{guild.id} - returns the server's id 
{guild.boost_count} - returns the number of server's boosts
{guild.booster_count} - returns the number of boosters
{guild.boost_tier} - returns the server's boost level
   """
     
     embed3 = discord.Embed(color=self.bot.color, title="invoke message variables")
     embed3.description = """
     {member} - returns member's name and discriminator
{member.name} - returns member's name
{member.mention} - returns member mention
{member.id} - return member's id
{member.avatar} - returns member's avatar
{reason} - returns action reason, if any
    """
     
     embed4 = discord.Embed(color=self.bot.color, title="last.fm variables")
     embed4.description = """
    {scrobbles} - returns all song play count
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
{useravatar} - returns user's profile picture
    """
     
     await ctx.paginator([embed1, embed2, embed3, embed4])
    
    @commands.group(invoke_without_command=True)
    async def autopfp(self, ctx):
      await ctx.create_pages()
    
    @autopfp.command(name="add", description="add the autopfp module", help="config", usage="[channel] [genre] [type]") 
    @Perms.get_perms("manage_guild")  
    async def autopfp_add(self, ctx: commands.Context, channel: discord.TextChannel, genre: str, typ: str=None):
     try:
      if genre in ["anime", "male", "female"]:
        if typ in ["pfp", "gif"]:
          check = await self.bot.db.fetchrow("SELECT * FROM autopfp WHERE guild_id = $1 AND genre = $2 AND type = $3", ctx.guild.id, genre, typ)
          if check: return await ctx.send_warning(f"A **channel** for **{genre}** **{typ}s** is already configured")
          await self.bot.db.execute("INSERT INTO autopfp VALUES ($1,$2,$3,$4)", ctx.guild.id, channel.id, genre, typ)
          return await ctx.send_success(f"Configured **{genre}** **{typ}s** to {channel.mention}")
        else: return await ctx.send_warning("The **type** you passed is **invalid**. Types must be one of the following: pfp, gif")
      elif genre in ["random", "banner"]: 
          check = await self.bot.db.fetchrow("SELECT * FROM autopfp WHERE channel_id = $1 AND guild_id = $2 AND genre = $3", channel.id, ctx.guild.id, genre) 
          if check is not None: return await ctx.send_warning(f"A channel for {genre} is already **configured**")
          await self.bot.db.execute("INSERT INTO autopfp VALUES ($1,$2,$3,$4)", ctx.guild.id, channel.id, genre, typ)
          return await ctx.send_success(f"Configured {genre} pictures to {channel.mention}")      
      else: return await ctx.send_error("The **genre** passed is **invalid**. Genres must be one of the following: male, female, anime, banner, random")
     except: traceback.print_exc()
    
    @autopfp.command(name="remove", description="remove the autopfp module", help="config", usage="[genre] [type]")
    @Perms.get_perms("manage_guild")
    async def autopfp_remove(self, ctx: commands.Context, genre: str, typ: str="none"):
       try:  
        check = await self.bot.db.fetchrow("SELECT * FROM autopfp WHERE guild_id = $1 AND genre = $2 AND type = $3", ctx.guild.id, genre, typ)                
        if check is None: return await ctx.send_warning(f"No autopfp channel found for **{genre} {typ if typ != 'none' else ''}**")
        await self.bot.db.execute("DELETE FROM autopfp WHERE guild_id = $1 AND genre = $2 AND type = $3", ctx.guild.id, genre, typ)   
        await ctx.send_success(f"Removed **{genre} {typ if typ != 'none' else ''}** posting")
       except: traceback.print_exc()
    
    @commands.group(invoke_without_command=True, aliases=["poj"])
    async def pingonjoin(self, ctx): 
      await ctx.create_pages()

    @pingonjoin.command(name="add", description="ping new members when they join your server", help="config", usage="[channel]")
    @Perms.get_perms("manage_guild")
    async def poj_add(self, ctx: commands.Context, *, channel: discord.TextChannel): 
        check = await self.bot.db.fetchrow("SELECT * FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check: return await ctx.send_warning(f"{channel.mention} is already added")
        elif not check: await self.bot.db.execute("INSERT INTO pingonjoin VALUES ($1,$2)", channel.id, ctx.guild.id)
        return await ctx.send_success(f"I will ping new members in {channel.mention}")  
    
    @pingonjoin.command(name="remove", description="remove a pingonjoin channel", help="config", usage="<channel>")
    @Perms.get_perms("manage_guild")
    async def poj_remove(self, ctx: commands.Context, *, channel: discord.TextChannel):  
        check = await self.bot.db.fetchrow("SELECT * FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if not check: return await ctx.send_error(f"{channel.mention} is not added")
        elif check: await self.bot.db.execute("DELETE FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        return await ctx.send_success(f"I will not ping new members in {channel.mention}")
    
    @pingonjoin.command(name="list", description="get a list of pingonjoin channels", help="config")
    async def poj_list(self, ctx: commands.Context): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.db.fetch("SELECT * FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
          if not results: return await ctx.send_error("There are no pingonjoin channels")
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
    
    @commands.group(invoke_without_command=True)
    async def starboard(self, ctx):
        await ctx.create_pages()
    
    @starboard.command(help="config", description="set the starboard count", usage="[count]", aliases=["amount"])
    @Perms.get_perms("manage_guild")
    async def count(self, ctx: commands.Context, count: int): 
      if count < 1: return await ctx.send_warning("Count cannot be **less** than 1")
      check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, count) VALUES ($1, $2)", ctx.guild.id, count)
      else: await self.bot.db.execute("UPDATE starboard SET count = $1 WHERE guild_id = $2", count, ctx.guild.id)
      await ctx.send_success(f"Starboard **count** set to **{count}**")  
    
    @starboard.command(name="channel", help="config", description="configure the starboard channel", usage="[channel]")
    @Perms.get_perms("manage_guild")
    async def starboard_channel(self, ctx: commands.Context, *, channel: discord.TextChannel): 
      check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, channel_id) VALUES ($1, $2)", ctx.guild.id, channel.id)
      else: await self.bot.db.execute("UPDATE starboard SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
      await ctx.send_success(f"Starboard **channel** set to {channel.mention}")

    @starboard.command(name="emoji", help="config", description="configure the starboard emoji", usage="[emoji]")
    @Perms.get_perms("manage_guild")
    async def starboard_emoji(self, ctx: commands.Context, emoji: Union[discord.PartialEmoji, str]): 
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     emoji_id = emoji.id if isinstance(emoji, discord.PartialEmoji) else ord(str(emoji)) 
     if check is None: await self.bot.db.execute("INSERT INTO starboard (guild_id, emoji_id, emoji_text) VALUES ($1,$2,$3)", ctx.guild.id, emoji_id, str(emoji)) 
     else: 
      await self.bot.db.execute("UPDATE starboard SET emoji_id = $1 WHERE guild_id = $2", emoji_id, ctx.guild.id)
      await self.bot.db.execute("UPDATE starboard SET emoji_text = $1 WHERE guild_id = $2", str(emoji), ctx.guild.id) 
     await ctx.send_success(f"Starboard **emoji** set to {emoji}") 

    @starboard.command(name="remove", help="config", description="remove starboard", aliases=["disable"])
    @Perms.get_perms("manage_guild")
    async def starboard_remove(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.send_warning("Starboard is not **configured**") 
     await self.bot.db.execute("DELETE FROM starboard WHERE guild_id = $1", ctx.guild.id)
     await self.bot.db.execute("DELETE FROM starboardmes WHERE guild_id = $1", ctx.guild.id)
     await ctx.send_success("Starboard has been **disabled**")

    starboard.command(help="config", description="check starboard stats", aliases=["settings", "status"])
    async def stats(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.send_warning("Starboard is not **configured**") 
     embed = discord.Embed(color=self.bot.color, title="starboard settings")
     if ctx.guild.get_channel(int(check["channel_id"])): embed.add_field(name="channel", value=ctx.guild.get_channel(int(check["channel_id"])).mention)
     if check["count"]: embed.add_field(name="amount", value=check["count"])
     if check["emoji_text"]: embed.add_field(name="emoji", value=check["emoji_text"])
     await ctx.reply(embed=embed)
    
    @commands.group(invoke_without_command=True)
    async def autorole(self, ctx): 
      await ctx.create_pages()

    @autorole.command(name="add", description="give a role to new users that joins your server", help="config", usage="[role]")
    @Perms.get_perms("manage_guild")
    async def autorole_add(self, ctx: commands.Context, *, role: Union[discord.Role, str]): 
      if isinstance(role, str): 
        role = ctx.find_role( role)
        if role is None: return await ctx.send_error(f"No role named **{ctx.message.clean_content[-len(ctx.clean_prefix)+15:]}** found")         
      check = await self.bot.db.fetchrow("SELECT * FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
      if check is not None: return await ctx.send_error(f"{role.mention} is already added")
      await self.bot.db.execute("INSERT INTO autorole VALUES ($1,$2)", role.id, ctx.guild.id)      
      return await ctx.send_success(f"Added {role.mention} as autorole")
    
    @autorole.command(name="remove", description="remove a role from autorole", help="config", usage="[role]")
    @Perms.get_perms("manage_guild")
    async def autorole_remove(self, ctx: commands.Context, *, role: Union[discord.Role, str]=None): 
      if isinstance(role, str): 
        role = ctx.find_role( role)
        if role is None: return await ctx.send_error(f"No role named **{ctx.message.clean_content[-len(ctx.clean_prefix)+18:]}** found")         
      if role is not None:
        check = await self.bot.db.fetchrow("SELECT * FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
        if check is None: return await ctx.send_error(f"{role.mention} is not added")
        await self.bot.db.execute("DELETE FROM autorole WHERE guild_id = {} AND role_id = {}".format(ctx.guild.id, role.id))
        return await ctx.send_success(f"Removed {role.mention} from autorole")
    
    @commands.group(invoke_without_command=True)
    async def confessions(self, ctx):
      await ctx.create_pages()
    
    @confessions.command(name="add", description="set confessions channel", help="config", usage="[channel]")
    @Perms.get_perms("manage_guild")
    async def confessions_add(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
       check = await self.bot.db.fetchrow("SELECT * FROM confess WHERE guild_id = $1", ctx.guild.id)
       if check: await self.bot.db.execute("UPDATE confess SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
       else: await self.bot.db.execute("INSERT INTO confess VALUES ($1,$2,$3)", ctx.guild.id, channel.id, 0)
       return await ctx.send_success(f"Confessions channel set to {channel.mention}")
    
    @confessions.command(name="remove", description="remove confessions channel", help="config")
    @Perms.get_perms("manage_guild")
    async def confessions_remove(self, ctx: commands.Context):
       check = await self.bot.db.fetchrow("SELECT * FROM confess WHERE guild_id = $1", ctx.guild.id)
       if not check: return await ctx.send_warning("Confessions are **not** enabled in this server")
       await self.bot.db.execute("DELETE FROM confess WHERE guild_id = $1", ctx.guild.id)
       await self.bot.db.execute("DELETE FROM confess_members WHERE guild_id = $1", ctx.guild.id)
       return await ctx.send_success("Disabled confessions")
    
    @confessions.command(name="channel", description="check confessions channel", help="config")
    async def confessions_channel(self, ctx: commands.Context):
       check = await self.bot.db.fetchrow("SELECT * FROM confess WHERE guild_id = $1", ctx.guild.id)
       if check:
        channel = ctx.guild.get_channel(check["channel_id"])
        embed = discord.Embed(color=self.bot.color, title="confessions settings", description=f"**confession channel:** {channel.mention}")
        return await ctx.reply(embed=embed)
       return await ctx.send_warning("Confessions are **not** enabled in this server")
    
    @commands.command(aliases=["disablecmd"], description="disable a command", help="config", usage="[command name]")  
    @Perms.get_perms("administrator")   
    async def disablecommand(self, ctx: commands.Context, *, cmd: str): 
     command = self.bot.get_command(cmd)
     if not command: return await ctx.send_warning(f"Command **{cmd}** not found")
     if command.name in ["ping", "help", "uptime", "disablecommand", "disablecmd", "enablecommand", "enablecmd"]: return await ctx.send_warning("This command can't be disabled")
     check = await self.bot.db.fetchrow("SELECT * FROM disablecommand WHERE command = $1 AND guild_id = $2", command.name, ctx.guild.id)
     if check: return await ctx.send_error("This command is **already** disabled")
     await self.bot.db.execute("INSERT INTO disablecommand VALUES ($1,$2)", ctx.guild.id, command.name)     
     await ctx.send_success(f"Disabled command **{command.name}**")

    @commands.command(aliases=["enablecmd"], help="enable a command that was previously disabled in this server", description="config", usage="[command name]")
    @Perms.get_perms("administrator")
    async def enablecommand(self, ctx: commands.Context, *, cmd: str): 
     command = self.bot.get_command(cmd)
     if not command: return await ctx.send_warning(f"Command **{cmd}** not found")
     check = await self.bot.db.fetchrow("SELECT * FROM disablecommand WHERE command = $1 AND guild_id = $2", command.name, ctx.guild.id)
     if not check: return await ctx.send_error("This command is **not** disabled")
     await self.bot.db.execute("DELETE FROM disablecommand WHERE guild_id = $1 AND command = $2", ctx.guild.id, command.name)     
     await ctx.send_success(f"Enabled command **{command.name}**")
    
    @commands.command(description="set a server prefix", help="config", usage="[prefix]")
    @Perms.get_perms("manage_guild")
    async def prefix(self, ctx: commands.Context, *, prefix: str):
        if len(prefix) > 3: return await ctx.send_error("Uh! The prefix is too long")
        check = await self.bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", ctx.guild.id) 
        if check: await self.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
        else: await self.bot.db.execute("INSERT INTO prefixes VALUES ($1, $2)", ctx.guild.id, prefix)
        return await ctx.send_success(f"Guild prefix set to `{prefix}`")
    
    @commands.command(description="set your own prefix", usage="[prefix]", help="config")
    async def selfprefix(self, ctx: commands.Context, prefix: str):      
      if len(prefix) > 3 and prefix.lower() != "none": return await ctx.send_error("Uh! The prefix is too long")
      if prefix.lower() == "none": 
        check = await self.bot.db.fetchrow("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id)) 
        if check is not None:
          await self.bot.db.execute("DELETE FROM selfprefix WHERE user_id = {}".format(ctx.author.id))
          return await ctx.send_success("Your self prefix has been removed")
        elif check is None: return await ctx.send_error("you don't have a self prefix".capitalize())   
      else:    
        result = await self.bot.db.fetchrow("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id)) 
        if result is not None: await self.bot.db.execute("UPDATE selfprefix SET prefix = $1 WHERE user_id = $2", prefix, ctx.author.id)
        elif result is None: await self.bot.db.execute('INSERT INTO selfprefix VALUES ($1, $2)', ctx.author.id, prefix)
        return await ctx.send_success(f"self prefix set to `{prefix}`".capitalize())
    
    @commands.group(invoke_without_command=True, description="manage custom punishment responses", help="config")
    async def invoke(self, ctx): 
     await ctx.create_pages()
  
    @invoke.command(name="variables", description="see invoke variables", help="config")
    async def embed_variables(self, ctx: commands.Context): 
     await ctx.invoke(self.bot.get_command('embed variables'))
    
    @invoke.command(name="unban", help="config", description='add a custom unban message', usage="[message / embed")
    @Perms.get_perms("manage_guild")
    async def invoke_unban(self, ctx: commands.Context, *, code: str):
      await Invoke.invoke_cmds(ctx, ctx.guild.me, code)
    
    @invoke.command(name="ban", help="config", description="add a custom ban message", usage="[message / embed]")
    @Perms.get_perms("manage_guild")
    async def invoke_ban(self, ctx: commands.Context, *, code: str):
      await Invoke.invoke_cmds(ctx, ctx.guild.me, code) 

    @invoke.command(name="kick", help="config", description="add a custom kick message", usage="[message / embed]")
    @Perms.get_perms("manage_guild")
    async def invoke_kick(self, ctx: commands.Context, *, code: str):
     await Invoke.invoke_cmds(ctx, ctx.guild.me, code)  
    
    @invoke.command(name="mute", help="config", description="add a custom mute command", brief="manage guild", usage="[message / embed]")
    @Perms.get_perms("manage_guild")
    async def invoke_mute(self, ctx: commands.Context, *, code: str):
     await Invoke.invoke_cmds(ctx, ctx.guild.me, code)    
  
    @invoke.command(name="unmute", help="config", description="add a custom unmute command", brief="manage guild", usage="[message / embed]")
    @Perms.get_perms("manage_guild")
    async def invoke_unmute(self, ctx: commands.Context, *, code: str):
     await Invoke.invoke_cmds(ctx, ctx.guild.me, code)
    
    @invoke.command(name="jail", help="config", description="add a custom jail command", brief="manage guild", usage="[message / embed]")
    @Perms.get_perms("manage_guild")
    async def invoke_jail(self, ctx: commands.Context, *, code: str): 
     await Invoke.invoke_cmds(ctx, ctx.guild.me, code) 
    
    @invoke.command(name="unjail", help="config", description="add a custom unjail command", brief="manage guild", usage="[message / embed]")
    @Perms.get_perms("manage_guild")
    async def invoke_unjail(self, ctx: commands.Context, *, code: str): 
     await Invoke.invoke_cmds(ctx, ctx.guild.me, code) 
    
    @commands.group(invoke_without_command=True, name="counter", help="config", description="create stats counters for your server")
    async def counter(self, ctx): 
      await ctx.create_pages()
    
    @counter.command(name="types", description="check the counter types and channel types", help="config")
    async def counter_types(self, ctx: commands.Context):
      embed1 = discord.Embed(color=self.bot.color, title="counter types")
      embed2 = discord.Embed(color=self.bot.color, title="channel types")
      embed1.description = """members - all members from the server (including bots)
      humans - all members from the server (excluding bots)
      bots - all bots from the server
      """
      embed2.description = """voice - creates a counter as voice channel
      text - creates a counter as text channel
      """
      await ctx.paginator([embed1, embed2])
    
    @counter.command(name="remove", help="config", description="remove a counter from the server", brief="manage guild", usage="[counter type]")
    @Perms.get_perms("manage_guild")
    async def counter_remove(self, ctx: commands.Context, typ: str): 
     if not typ in ["members", "humans", "bots"]: return await ctx.send_warning(f"**{typ}** is not an **available** counter") 
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, typ)
     if not check: return await ctx.send_warning(f"There is no **{typ}** counter in this server")
     channel = ctx.guild.get_channel(int(check["channel_id"]))
     if channel: await channel.delete()
     await self.bot.db.execute("DELETE FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, typ)
     return await ctx.send_success(f"Removed **{typ}** counter")
    
    @counter.command(name="list", help="config", description="check a list of the active server counters")
    async def counter_list(self, ctx: commands.Context): 
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
               number.append(discord.Embed(color=self.bot.color, title=f"server counters ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
          messages.append(mes)
          number.append(discord.Embed(color=self.bot.color, title=f"server counters ({len(results)})", description=messages[i]))
          return await ctx.paginator(number) 
    
    @counter.group(invoke_without_command=True, name="add", help="config", description="add a counter to the server", brief="manage guild")
    async def counter_add(self, ctx): 
      await ctx.create_pages()

    @counter_add.command(name="members", help="config", description="add a counter for member count", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add members voice {target} Members")
    @Perms.get_perms("manage_guild")
    async def counter_add_members(self, ctx: commands.Context, typ: str, *, message: str="{target}"): 
     if not typ in ["voice", "text"]: return await ctx.send_warning(f"**{typ}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send_warning("`{target}` is **missing** from the channel name")
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send_warning(f"<#{check['channel_id']}> is already a **member** counter")
     overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)}
     reason="creating member counter"
     name = message.replace("{target}", str(ctx.guild.member_count))
     if typ == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)})
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, typ, channel.id, message, ctx.command.name)
     await ctx.send_success(f"Created **member** counter to {channel.mention}")  
    
    @counter_add.command(name="humans", help="config", description="add a counter for humans", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add humans voice {target} humans")
    @Perms.get_perms("manage_guild")
    async def counter_add_humans(self, ctx: commands.Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text"]: return await ctx.send_warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send_warning("`{target}` is **missing** from the channel name")
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send_warning(f"<#{check['channel_id']}> is already a **humans** counter")
     overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)}
     reason="creating human counter"
     name = message.replace("{target}", str(len([m for m in ctx.guild.members if not m.bot])))
     if channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)})
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send_success(f"Created **humans** counter to {channel.mention}")  
    
    @counter_add.command(name="bots", help="config", description="add a counter for humans", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add bots voice {target} humans")
    @Perms.get_perms("manage_guild")
    async def counter_add_bots(self, ctx: commands.Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text"]: return await ctx.send_warning(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send_warning("`{target}` is **missing** from the channel name")
     check = await self.bot.db.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send_warning(f"<#{check['channel_id']}> is already a **bots** counter")
     overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)}
     reason="creating bot counter"
     name = message.replace("{target}", str(len([m for m in ctx.guild.members if m.bot])))
     if channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)})
     await self.bot.db.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send_success(f"Created **bots** counter to {channel.mention}") 
    
    @commands.group(invoke_without_command=True, aliases=["fakeperms"])
    async def fakepermissions(self, ctx):
      await ctx.create_pages()
    
    @fakepermissions.command(description="edit fake permissions for a role", help="config", usage="[role]", brief="server owner")
    @Perms.server_owner()
    async def edit(self, ctx: commands.Context, *, role: Union[discord.Role, str]): 
     if isinstance(role, str): 
        role = ctx.find_role( role)
        if role is None: return await ctx.send_warning("This is not a valid role") 
      
     perms = ["administrator", "manage_guild", "manage_roles", "manage_channels", "manage_messages", "manage_nicknames", "manage_emojis", "ban_members", "kick_members", "moderate_members"]
     options = [discord.SelectOption(label=perm.replace("_", " "), value=perm) for perm in perms]
     embed = discord.Embed(color=self.bot.color, description="What perms should i add to {}?".format(role.mention))
     select = discord.ui.Select(placeholder="select permissions", options=options)
     
     async def select_callback(interaction: discord.Interaction):
      if ctx.author != interaction.user: return await self.bot.ext.send_warning(interaction, "This is not your embed", ephemeral=True)
      data = json.dumps(select.values)
      check = await self.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE guild_id = $1 AND role_id = $2", interaction.guild.id, role.id)
      if not check: await self.bot.db.execute("INSERT INTO fake_permissions VALUES ($1,$2,$3)", interaction.guild.id, role.id, data)
      else: await self.bot.db.execute("UPDATE fake_permissions SET permissions = $1 WHERE guild_id = $2 AND role_id = $3", data, interaction.guild.id, role.id)     
      await interaction.response.edit_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {interaction.user.mention}: Added **{len(select.values)}** permission{'s' if len(select.values) > 1 else ''} to {role.mention}"), view=None)

     select.callback = select_callback 
     view = discord.ui.View()
     view.add_item(select)
     await ctx.reply(embed=embed, view=view)
    
    @fakepermissions.command(name="list", description="list the permissions of a specific role", help="config", usage="[role]")
    async def fakeperms_list(self, ctx: commands.Context, *, role: Union[discord.Role, str]): 
     if isinstance(role, str): 
        role = ctx.find_role(role)
        if role is None: return await ctx.send_warning("This is not a valid role") 
     
     check = await self.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE guild_id = $1 AND role_id = $2", ctx.guild.id, role.id)
     if check is None: return await ctx.send_error("This role has no fake permissions")
     permissions = json.loads(check['permissions'])
     embed = discord.Embed(color=self.bot.color, title=f"@{role.name}'s fake permissions", description="\n".join([f"`{permissions.index(perm)+1}` {perm}" for perm in permissions]))
     embed.set_thumbnail(url=role.display_icon)
     return await ctx.reply(embed=embed)
    
    @fakepermissions.command(aliases=["perms"], description="list all the available permissions", help="config")
    async def permissions(self, ctx: commands.Context): 
      perms = ["administrator", "manage_guild", "manage_roles", "manage_channels", "manage_messages", "manage_nicknames", "manage_emojis", "ban_members", "kick_members", "moderate_members"]
      embed = discord.Embed(color=self.bot.color, description="\n".join([f"`{perms.index(perm)+1}` {perm}" for perm in perms])).set_author(icon_url=self.bot.user.display_avatar.url, name="avaible fakepermissions perms list")
      await ctx.reply(embed=embed)  
    
async def setup(bot):
    await bot.add_cog(Config(bot))