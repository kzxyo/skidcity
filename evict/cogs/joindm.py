import discord, datetime 
from discord.ext import commands
from utils.utils import EmbedBuilder 
from patches.permissions import Permissions

messages = {}
max_messages = 15 
cooldown = 3*60

class joindm(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
  
  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member): 
    check = await self.bot.db.fetchrow("SELECT * FROM joindm WHERE guild_id = $1", member.guild.id) 
    if check: 
      if not messages.get(str(member.guild.id)): messages[str(member.guild.id)] = []  
      messages[str(member.guild.id)].append(datetime.datetime.now())
      expired = [msg for msg in messages[str(member.guild.id)] if (datetime.datetime.now() - msg).total_seconds() > cooldown]
      for msg_time in expired: messages[str(member.guild.id)].remove(msg_time)
      if len(messages[str(member.guild.id)]) > max_messages: return 
      mes = check['message']
      view = discord.ui.View()
      view.add_item(discord.ui.Button(label=f"sent from {member.guild.name}", disabled=True))
      x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, mes))
      if x[0] and x[1]:
       x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, mes))
       try: await member.send(content=x[0], embed=x[1], view=view) 
       except: pass  
      else:
        try: await member.send(content=EmbedBuilder.embed_replacement(member, check['message'])  , view=view)
        except: pass 

  @commands.group(invoke_without_command=True, description="manage dm's on member join")
  async def joindm(self, ctx): 
    return await ctx.create_pages()
  
  @joindm.command(name="add", description="add a message that will be sent to any new member that will join the server", brief="manage guild", usage="[message | --embed embed name]")
  @Permissions.has_permission(manage_guild=True) 
  async def joindm_add(self, ctx: commands.Context, *, message: str): 
   check = await self.bot.db.fetchrow("SELECT * FROM joindm WHERE guild_id = $1", ctx.guild.id)
   if check: await self.bot.db.execute("UPDATE joindm SET message = $1 WHERE guild_id = $2", message, ctx.guild.id)
   else: await self.bot.db.execute("INSERT INTO joindm VALUES ($1,$2)", ctx.guild.id, message)
   await ctx.success(f"Configured **joindm** message to\n```{message}```")    
  
  @joindm.command(name="remove", description="remove the joindm message", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def joindm_remove(self, ctx: commands.Context):
    check = await self.bot.db.fetchrow("SELECT * FROM joindm WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.warning("Joindm not enabled")
    await self.bot.db.execute("DELETE FROM joindm WHERE guild_id = $1", ctx.guild.id)
    return await ctx.success('Deleted joindm')
  
  @joindm.command(name="test", description="test the joindm message", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def joindm_test(self, ctx: commands.Context): 
    check = await self.bot.db.fetchrow("SELECT message FROM joindm WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.warning("Joindm not enabled")
    member = ctx.author
    mes = check[0]
    view = discord.ui.View()    
    view.add_item(discord.ui.Button(label=f"sent from {member.guild.name}", disabled=True))
    x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, mes))
    if x[0] and x[1]:
      try: await member.send(content=x[0], embed=x[1], view=view) 
      except: pass  
    else:
      try: await member.send(EmbedBuilder.embed_replacement(ctx.author, mes), view=view)
      except: pass 
    return await ctx.success( "Check dm's if you received one")

async def setup(bot: commands.Bot) -> None: 
  await bot.add_cog(joindm(bot))   