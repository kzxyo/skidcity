import discord 
from discord.ext import commands 
from tools.utils import EmbedBuilder
from tools.checks import Perms

class Greet(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
  
  @commands.Cog.listener()
  async def on_message(self, message: discord.Message): 
    if "MessageType.premium_guild" in str(message.type):
     res = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", message.guild.id)
     if res: 
      channel = message.guild.get_channel(res['channel_id'])
      if channel is None: return 
      try: 
       x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(message.author, res['mes']))
       await channel.send(content=x[0],embed=x[1], view=x[2])
      except: await channel.send(EmbedBuilder.embed_replacement(message.author, res['mes'])) 
    
  @commands.Cog.listener()
  async def on_member_update(self, before: discord.Member, after: discord.Member): 
   if not before.guild.premium_subscriber_role in before.roles and after.guild.premium_subscriber_role in after.roles: 
    if not before.guild.system_channel: 
     res = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", before.guild.id)
     if res: 
      channel = before.guild.get_channel(res['channel_id'])
      if channel is None: return 
      try: 
       x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(before, res['mes']))
       await channel.send(content=x[0],embed=x[1], view=x[2])
      except: await channel.send(EmbedBuilder.embed_replacement(before, res['mes'])) 

  @commands.Cog.listener()
  async def on_member_remove(self, member: discord.Member): 
   res = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", member.guild.id)
   if res: 
    channel = member.guild.get_channel(res['channel_id'])
    if channel is None: return 
    try: 
       x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, res['mes']))
       await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(member, res['mes'])) 

  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member): 
   res = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", member.guild.id)
   if res: 
    channel = member.guild.get_channel(res['channel_id'])
    if channel is None: return 
    try: 
       x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, res['mes']))
       await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(member, res['mes'])) 
  
  @commands.group(invoke_without_command=True)
  async def boost(self, ctx): 
   await ctx.create_pages()

  @boost.command(name="variables", help="config", description="return the variables for the boost message")
  async def boost_variables(self, ctx: commands.Context): 
    await ctx.invoke(self.bot.get_command('embed variables'))

  @boost.command(name="config", help="config", description="returns stats of the boost message")
  async def boost_config(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", ctx.guild.id)
   if not res: return await ctx.send_warning("Boost is not **configured**")
   channel = f'#{ctx.guild.get_channel(res["channel_id"]).name}' if ctx.guild.get_channel(res['channel_id']) else "none"
   e = res['mes'] or "none"
   embed = discord.Embed(color=self.bot.color, title=f"channel {channel}", description=f"```{e}```")
   await ctx.reply(embed=embed)     
  
  @boost.command(name="message", help="config", description="configure the boost message", brief="manage guild", usage="[message]")
  @Perms.get_perms("manage_guild")
  async def boost_message(self, ctx: commands.Context, *, code: str):    
    check = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", ctx.guild.id)
    if check: await self.bot.db.execute("UPDATE boost SET mes = $1 WHERE guild_id = $2", code, ctx.guild.id)
    else: await self.bot.db.execute("INSERT INTO boost VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
    return await ctx.send_success(f"Configured boost message as `{code}`")

  @boost.command(name="channel", help="config", description="configure the boost channel", brief="manage guild", usage="[channel]")  
  @Perms.get_perms("manage_guild")
  async def boost_channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None): 
   if channel is None: 
    check = await self.bot.db.fetchrow("SELECT channel_id FROM boost WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.send_warning("Boost **channel** is not configured") 
    await self.bot.db.execute("UPDATE boost SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
    return await ctx.send_success("Removed the boost **channel**")
   else: 
     check = await self.bot.db.fetchrow("SELECT channel_id FROM boost WHERE guild_id = $1", ctx.guild.id)
     if check: await self.bot.db.execute("UPDATE boost SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
     else: await self.bot.db.execute("INSERT INTO boost VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
     await ctx.send_success("Configured boost **channel** to {}".format(channel.mention))

  @boost.command(name="delete", help="config", description="delete the boost module", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def boost_delete(self, ctx: commands.Context): 
   check = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", ctx.guild.id) 
   if not check: return await ctx.send_warning("Boost module is not configured") 
   await self.bot.db.execute("DELETE FROM boost WHERE guild_id = $1", ctx.guild.id)
   await ctx.send_success("Boost module is now **disabled**")
  
  @boost.command(name="test", help="config", description="test boost module", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def boost_test(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", ctx.guild.id)
   if res: 
    channel = ctx.guild.get_channel(res['channel_id'])
    if channel is None: return await ctx.send_error("Channel **not** found")
    try: 
     x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, res['mes']))
     await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(ctx.author, res['mes'])) 
    await ctx.send_success("Sent the **boost** message to {}".format(channel.mention))

  @commands.group(invoke_without_command=True)
  async def leave(self, ctx): 
   await ctx.create_pages()

  @leave.command(name="variables", help="config", description="return the variables for the leave message")
  async def leave_variables(self, ctx: commands.Context): 
    await ctx.invoke(self.bot.get_command('embed variables'))

  @leave.command(name="config", help="config", description="returns stats of the leave message")
  async def leave_config(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
   if not res: return await ctx.send_warning("Leave is not **configured**")
   channel = f'#{ctx.guild.get_channel(res["channel_id"]).name}' if ctx.guild.get_channel(res['channel_id']) else "none"
   e = res['mes'] or "none"
   embed = discord.Embed(color=self.bot.color, title=f"channel {channel}", description=f"```{e}```")
   await ctx.reply(embed=embed)     
  
  @leave.command(name="message", help="config", description="configure the leave message", brief="manage guild", usage="[message]")
  @Perms.get_perms("manage_guild")
  async def leave_message(self, ctx: commands.Context, *, code: str):  
    check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
    if check: await self.bot.db.execute("UPDATE leave SET mes = $1 WHERE guild_id = $2", code, ctx.guild.id)
    else: await self.bot.db.execute("INSERT INTO leave VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
    return await ctx.send_success(f"Configured leave message as `{code}`")

  @leave.command(name="channel", help="config", description="configure the leave channel", brief="manage guild", usage="[channel]")  
  @Perms.get_perms("manage_guild")
  async def leave_channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None): 
   if channel is None: 
    check = await self.bot.db.fetchrow("SELECT channel_id FROM leave WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.send_warning("Leave **channel** is not configured") 
    await self.bot.db.execute("UPDATE leave SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
    return await ctx.send_success("Removed the leave **channel**")
   else: 
     check = await self.bot.db.fetchrow("SELECT channel_id FROM leave WHERE guild_id = $1", ctx.guild.id)
     if check: await self.bot.db.execute("UPDATE leave SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
     else: await self.bot.db.execute("INSERT INTO leave VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
     await ctx.send_success("Configured leave **channel** to {}".format(channel.mention))

  @leave.command(name="delete", help="config", description="delete the leave module", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def leave_delete(self, ctx: commands.Context): 
   check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id) 
   if not check: return await ctx.send_warning("Leave module is not configured") 
   await self.bot.db.execute("DELETE FROM leave WHERE guild_id = $1", ctx.guild.id)
   await ctx.send_success("Leave module is now **disabled**")
  
  @leave.command(name="test", help="config", description="test leave module", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def leave_test(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
   if res: 
    channel = ctx.guild.get_channel(res['channel_id'])
    if channel is None: return await ctx.send_error("Channel **not** found")
    try: 
     x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, res['mes']))
     await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(ctx.author, res['mes'])) 
    await ctx.send_success("Sent the **leave** message to {}".format(channel.mention))

  @commands.group(aliases=["welc"], invoke_without_command=True)
  async def welcome(self, ctx): 
   await ctx.create_pages()

  @welcome.command(name="variables", help="config", description="return the variables for the welcome message")
  async def welcome_variables(self, ctx: commands.Context): 
    await ctx.invoke(self.bot.get_command('embed variables'))

  @welcome.command(name="config", help="config", description="returns stats of the welcome message")
  async def welcome_config(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
   if not res: return await ctx.send_warning("Welcome is not **configured**")
   channel = f'#{ctx.guild.get_channel(res["channel_id"]).name}' if ctx.guild.get_channel(res['channel_id']) else "none"
   e = res['mes'] or "none"
   embed = discord.Embed(color=self.bot.color, title=f"channel {channel}", description=f"```{e}```")
   await ctx.reply(embed=embed)     
  
  @welcome.command(name="message", help="config", description="configure the welcome message", brief="manage guild", usage="[message]")
  @Perms.get_perms("manage_guild")
  async def welcome_message(self, ctx: commands.Context, *, code: str):   
    check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
    if check: await self.bot.db.execute("UPDATE welcome SET mes = $1 WHERE guild_id = $2", code, ctx.guild.id)
    else: await self.bot.db.execute("INSERT INTO welcome VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
    return await ctx.send_success(f"Configured welcome message as `{code}`")

  @welcome.command(name="channel", help="config", description="configure the welcome channel", brief="manage guild", usage="[channel]")  
  @Perms.get_perms("manage_guild")
  async def welcome_channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None): 
   if channel is None: 
    check = await self.bot.db.fetchrow("SELECT channel_id FROM welcome WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.send_warning("Welcome **channel** is not configured") 
    await self.bot.db.execute("UPDATE welcome SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
    return await ctx.send_success("Removed the welcome **channel**")
   else: 
     check = await self.bot.db.fetchrow("SELECT channel_id FROM welcome WHERE guild_id = $1", ctx.guild.id)
     if check: await self.bot.db.execute("UPDATE welcome SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
     else: await self.bot.db.execute("INSERT INTO welcome VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
     await ctx.send_success("Configured welcome **channel** to {}".format(channel.mention))

  @welcome.command(name="delete", help="config", description="delete the welcome module", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def welcome_delete(self, ctx: commands.Context): 
   check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id) 
   if not check: return await ctx.send_warning("Welcome module is not configured") 
   await self.bot.db.execute("DELETE FROM welcome WHERE guild_id = $1", ctx.guild.id)
   await ctx.send_success("Welcome module is now **disabled**")
  
  @welcome.command(name="test", help="config", description="test welcome module", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def welcome_test(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
   if res: 
    channel = ctx.guild.get_channel(res['channel_id'])
    if channel is None: return await ctx.send_error("Channel **not** found")
    try: 
     x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, res['mes']))
     await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(ctx.author, res['mes'])) 
    await ctx.send_success("Sent the **welcome** message to {}".format(channel.mention))
   
async def setup(bot: commands.Bot): 
  await bot.add_cog(Greet(bot))        