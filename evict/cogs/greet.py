import discord 
from discord.ext import commands 
import discord
from utils.utils import EmbedBuilder
from patches.permissions import Permissions

class greet(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
  
  @commands.group(invoke_without_command=True)
  async def boost(self, ctx): 
   await ctx.create_pages()

  @boost.command(name="variables", description="return the variables for the boost message")
  @Permissions.has_permission(manage_guild=True) 
  async def boost_variables(self, ctx: commands.Context): 
    await ctx.invoke(self.bot.get_command('embed variables'))

  @boost.command(name="config", description="returns stats of the boost message")
  @Permissions.has_permission(manage_guild=True) 
  async def boost_config(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", ctx.guild.id)
   if not res: return await ctx.warning("Boost is not **configured**")
   channel = f'#{ctx.guild.get_channel(res["channel_id"]).name}' if ctx.guild.get_channel(res['channel_id']) else "none"
   e = res['mes'] or "none"
   embed = discord.Embed(color=self.bot.color, title=f"channel {channel}", description=f"```{e}```")
   await ctx.reply(embed=embed)     
  
  @boost.command(name="message", description="configure the boost message", brief="manage guild", usage="[message]")
  @Permissions.has_permission(manage_guild=True) 
  async def boost_message(self, ctx: commands.Context, *, code: str):    
    check = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", ctx.guild.id)
    if check: await self.bot.db.execute("UPDATE boost SET mes = $1 WHERE guild_id = $2", code, ctx.guild.id)
    else: await self.bot.db.execute("INSERT INTO boost VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
    return await ctx.success(f"Configured boost message as `{code}`")

  @boost.command(name="channel", description="configure the boost channel", brief="manage guild", usage="[channel]")  
  @Permissions.has_permission(manage_guild=True) 
  async def boost_channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None): 
   if channel is None: 
    check = await self.bot.db.fetchrow("SELECT channel_id FROM boost WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.warning("Boost **channel** is not configured") 
    await self.bot.db.execute("UPDATE boost SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
    return await ctx.success("Removed the boost **channel**")
   else: 
     check = await self.bot.db.fetchrow("SELECT channel_id FROM boost WHERE guild_id = $1", ctx.guild.id)
     if check: await self.bot.db.execute("UPDATE boost SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
     else: await self.bot.db.execute("INSERT INTO boost VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
     await ctx.success("Configured boost **channel** to {}".format(channel.mention))

  @boost.command(name="delete", description="delete the boost module", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def boost_delete(self, ctx: commands.Context): 
   check = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", ctx.guild.id) 
   if not check: return await ctx.warning("Boost module is not configured") 
   await self.bot.db.execute("DELETE FROM boost WHERE guild_id = $1", ctx.guild.id)
   await ctx.success("Boost module is now **disabled**")
  
  @boost.command(name="test", description="test boost module", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def boost_test(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", ctx.guild.id)
   if res: 
    channel = ctx.guild.get_channel(res['channel_id'])
    if channel is None: return await ctx.error("Channel **not** found")
    try: 
     x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, res['mes']))
     await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(ctx.author, res['mes'])) 
    await ctx.success("Sent the **boost** message to {}".format(channel.mention))

  @commands.group(invoke_without_command=True)
  async def leave(self, ctx): 
   await ctx.create_pages()

  @leave.command(name="variables", description="return the variables for the leave message")
  async def leave_variables(self, ctx: commands.Context): 
    await ctx.invoke(self.bot.get_command('embed variables'))

  @leave.command(name="config", description="returns stats of the leave message")
  async def leave_config(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
   if not res: return await ctx.warning("Leave is not **configured**")
   channel = f'#{ctx.guild.get_channel(res["channel_id"]).name}' if ctx.guild.get_channel(res['channel_id']) else "none"
   e = res['mes'] or "none"
   embed = discord.Embed(color=self.bot.color, title=f"channel {channel}", description=f"```{e}```")
   await ctx.reply(embed=embed)     
  
  @leave.command(name="message", description="configure the leave message", brief="manage guild", usage="[message]")
  @Permissions.has_permission(manage_guild=True) 
  async def leave_message(self, ctx: commands.Context, *, code: str):  
    check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
    if check: await self.bot.db.execute("UPDATE leave SET mes = $1 WHERE guild_id = $2", code, ctx.guild.id)
    else: await self.bot.db.execute("INSERT INTO leave VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
    return await ctx.success(f"Configured leave message as `{code}`")

  @leave.command(name="channel", description="configure the leave channel", brief="manage guild", usage="[channel]")  
  @Permissions.has_permission(manage_guild=True) 
  async def leave_channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None): 
   if channel is None: 
    check = await self.bot.db.fetchrow("SELECT channel_id FROM leave WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.warning("Leave **channel** is not configured") 
    await self.bot.db.execute("UPDATE leave SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
    return await ctx.success("Removed the leave **channel**")
   else: 
     check = await self.bot.db.fetchrow("SELECT channel_id FROM leave WHERE guild_id = $1", ctx.guild.id)
     if check: await self.bot.db.execute("UPDATE leave SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
     else: await self.bot.db.execute("INSERT INTO leave VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
     await ctx.success("Configured leave **channel** to {}".format(channel.mention))

  @leave.command(name="delete", description="delete the leave module", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def leave_delete(self, ctx: commands.Context): 
   check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id) 
   if not check: return await ctx.warning("Leave module is not configured") 
   await self.bot.db.execute("DELETE FROM leave WHERE guild_id = $1", ctx.guild.id)
   await ctx.success("Leave module is now **disabled**")
  
  @leave.command(name="test", description="test leave module", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def leave_test(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
   if res: 
    channel = ctx.guild.get_channel(res['channel_id'])
    if channel is None: return await ctx.error("Channel **not** found")
    try: 
     x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, res['mes']))
     await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(ctx.author, res['mes'])) 
    await ctx.success("Sent the **leave** message to {}".format(channel.mention))

  @commands.group(aliases=["welc"], invoke_without_command=True)
  async def welcome(self, ctx): 
   await ctx.create_pages()

  @welcome.command(name="variables", description="return the variables for the welcome message")
  async def welcome_variables(self, ctx: commands.Context): 
    await ctx.invoke(self.bot.get_command('embed variables'))

  @welcome.command(name="config", description="returns stats of the welcome message")
  async def welcome_config(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
   if not res: return await ctx.warning("Welcome is not **configured**")
   channel = f'#{ctx.guild.get_channel(res["channel_id"]).name}' if ctx.guild.get_channel(res['channel_id']) else "none"
   e = res['mes'] or "none"
   embed = discord.Embed(color=self.bot.color, title=f"channel {channel}", description=f"```{e}```")
   await ctx.reply(embed=embed)     
  
  @welcome.command(name="message", description="configure the welcome message", brief="manage guild", usage="[message]")
  @Permissions.has_permission(manage_guild=True) 
  async def welcome_message(self, ctx: commands.Context, *, code: str):   
    check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
    if check: await self.bot.db.execute("UPDATE welcome SET mes = $1 WHERE guild_id = $2", code, ctx.guild.id)
    else: await self.bot.db.execute("INSERT INTO welcome VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
    return await ctx.success(f"Configured welcome message as `{code}`")

  @welcome.command(name="channel", description="configure the welcome channel", brief="manage guild", usage="[channel]")  
  @Permissions.has_permission(manage_guild=True) 
  async def welcome_channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None): 
   if channel is None: 
    check = await self.bot.db.fetchrow("SELECT channel_id FROM welcome WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.warning("Welcome **channel** is not configured") 
    await self.bot.db.execute("UPDATE welcome SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
    return await ctx.success("Removed the welcome **channel**")
   else: 
     check = await self.bot.db.fetchrow("SELECT channel_id FROM welcome WHERE guild_id = $1", ctx.guild.id)
     if check: await self.bot.db.execute("UPDATE welcome SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
     else: await self.bot.db.execute("INSERT INTO welcome VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
     await ctx.success("Configured welcome **channel** to {}".format(channel.mention))

  @welcome.command(name="delete", description="delete the welcome module", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def welcome_delete(self, ctx: commands.Context): 
   check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id) 
   if not check: return await ctx.warning("Welcome module is not configured") 
   await self.bot.db.execute("DELETE FROM welcome WHERE guild_id = $1", ctx.guild.id)
   await ctx.success("Welcome module is now **disabled**")
  
  @welcome.command(name="test", description="test welcome module", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def welcome_test(self, ctx: commands.Context): 
   res = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
   if res: 
    channel = ctx.guild.get_channel(res['channel_id'])
    if channel is None: return await ctx.error("Channel **not** found")
    try: 
     x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, res['mes']))
     await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(ctx.author, res['mes'])) 
    await ctx.success("Sent the **welcome** message to {}".format(channel.mention))

  @commands.group(invoke_without_command=True)
  async def hellohook(self, ctx): 
    await ctx.create_pages()
 
  @hellohook.command(name="message", description="configure the hellohook message", brief="manage guild", usage="[message]")
  @Permissions.has_permission(manage_guild=True) 
  async def hellohook_message(self, ctx: commands.Context, *, code: str):   
    check = await self.bot.db.fetchrow("SELECT * FROM hellohook WHERE guild_id = $1", ctx.guild.id)
    if check: await self.bot.db.execute("UPDATE hellohook SET mes = $1 WHERE guild_id = $2", code, ctx.guild.id)
    else: await self.bot.db.execute("INSERT INTO hellohook VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
    return await ctx.success(f"Configured hellohook message as `{code}`")

  @hellohook.command(name="webhook", description="configure the hellohook webhook", brief="manage guild", usage="[url]")  
  @Permissions.has_permission(manage_guild=True) 
  async def hellohook_url(self, ctx: commands.Context, *, link): 
     check = await self.bot.db.fetchrow("SELECT * FROM hellohook WHERE guild_id = $1 AND webhook_link = $2", ctx.guild.id, link)
     if check: await self.bot.db.execute("UPDATE hellohook SET guild_id = $1 WHERE webhook_link = $2", ctx.guild.id, link)
     else: await self.bot.db.execute("INSERT INTO hellohook VALUES ($1,$2)", ctx.guild.id, link)
     await ctx.success("Configured welcome **webhook**.")

  @hellohook.command(name="delete", description="delete the hellohook welcome", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def hellohook_delete(self, ctx: commands.Context): 
   check = await self.bot.db.fetchrow("SELECT * FROM hellohook WHERE guild_id = $1", ctx.guild.id) 
   if not check: return await ctx.warning("Welcome module is not configured") 
   await self.bot.db.execute("DELETE FROM hellohook WHERE guild_id = $1", ctx.guild.id)
   await ctx.success("Hellohook module is now **disabled**")

async def setup(bot: commands.Bot): 
  await bot.add_cog(greet(bot))        