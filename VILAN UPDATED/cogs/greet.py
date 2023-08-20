import discord
from discord.ext import commands
from tools.utils.checks import Perms
from tools.utils.utils import EmbedBuilder

class greet(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member): 
     check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", member.guild.id)
     if check: 
      channel = member.guild.get_channel(check['channel_id'])
      if channel is None: return 
      try: 
         x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, check['message']))
         await channel.send(content=x[0],embed=x[1], view=x[2])
      except: await channel.send(EmbedBuilder.embed_replacement(member, check['message'])) 
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member): 
     check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", member.guild.id)
     if check: 
      channel = member.guild.get_channel(check['channel_id'])
      if channel is None: return 
      try: 
         x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, check['message']))
         await channel.send(content=x[0],embed=x[1], view=x[2])
      except: await channel.send(EmbedBuilder.embed_replacement(member, check['message'])) 
    
    @commands.group(invoke_without_command=True)
    async def leave(self, ctx): 
     await ctx.create_pages()

    @leave.command(name="variables", help="config", description="return the variables for the leave message")
    async def leave_variables(self, ctx: commands.Context): 
      await ctx.invoke(self.bot.get_command('embed variables'))
     
    @leave.command(name="config", help="config", description="returns stats of the leave message")
    async def leave_config(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
     if not check: return await ctx.send_warning("Welcome is **not** configured")
     channel = f'#{ctx.guild.get_channel(check["channel_id"]).name}' if ctx.guild.get_channel(check['channel_id']) else "none"
     e = check['mes'] or "none"
     embed = discord.Embed(color=self.bot.color, title=f"channel {channel}", description=f"```{e}```")
     await ctx.reply(embed=embed)     
    
    @leave.command(name="channel", description="configure the leave channel", help="config", usage="[channel]")
    @Perms.get_perms("manage_guild")
    async def leave_channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
      check = await self.bot.db.fetchrow("SELECT channel_id FROM leave WHERE guild_id = $1", ctx.guild.id)
      if check: await self.bot.db.execute("UPDATE leave SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
      else: await self.bot.db.execute("INSERT INTO leave VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
      return await ctx.send_success(f"Leave channel set to {channel.mention}")
    
    @leave.command(name="message", help="config", description="configure the leave message", usage="[message]")
    @Perms.get_perms("manage_guild")
    async def leave_message(self, ctx: commands.Context, *, code: str):
      check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
      if check: await self.bot.db.execute("UPDATE leave SET message = $1 WHERE guild_id = $2", code, ctx.guild.id)
      else: await self.bot.db.execute("INSERT INTO leave VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
      return await ctx.send_success(f"Leave message configured as\n```{code}```")
    
    @leave.command(name="delete", help="config", description="delete the leave module")
    @Perms.get_perms("manage_guild")
    async def leave_delete(self, ctx: commands.Context):
      check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
      if not check: return await ctx.send_warning("Leave is **not** configured")
      else: await self.bot.db.execute("DELETE FROM leave WHERE guild_id = $1", ctx.guild.id)
      return await ctx.send_success("Leave has been **deleted**")
    
    @leave.command(name="test", help="config", description="test the leave module")
    @Perms.get_perms("manage_guild")
    async def leave_test(self, ctx):
      check = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", ctx.guild.id)
      if check:
        channel = ctx.guild.get_channel(check["channel_id"])
        if not channel: return await ctx.send_warning("channel **not** found")
        self.bot.dispatch("member_remove", ctx.author)
        return await ctx.send_success("Leave message sent to {}".format(channel.mention))
    
    @commands.group(aliases=["welc"], invoke_without_command=True)
    async def welcome(self, ctx): 
     await ctx.create_pages()

    @welcome.command(name="variables", help="config", description="return the variables for the welcome message")
    async def welcome_variables(self, ctx: commands.Context): 
      await ctx.invoke(self.bot.get_command('embed variables'))
     
    @welcome.command(name="config", help="config", description="returns stats of the welcome message")
    async def welcome_config(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
     if not check: return await ctx.send_warning("Welcome is **not** configured")
     channel = f'#{ctx.guild.get_channel(check["channel_id"]).name}' if ctx.guild.get_channel(check['channel_id']) else "none"
     e = check['mes'] or "none"
     embed = discord.Embed(color=self.bot.color, title=f"channel {channel}", description=f"```{e}```")
     await ctx.reply(embed=embed)     
    
    @welcome.command(name="channel", description="configure the welcome channel", help="config", usage="[channel]")
    @Perms.get_perms("manage_guild")
    async def welcome_channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
      check = await self.bot.db.fetchrow("SELECT channel_id FROM welcome WHERE guild_id = $1", ctx.guild.id)
      if check: await self.bot.db.execute("UPDATE welcome SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
      else: await self.bot.db.execute("INSERT INTO welcome VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
      return await ctx.send_success(f"Welcome channel set to {channel.mention}")
    
    @welcome.command(name="message", help="config", description="configure the welcome message", usage="[message]")
    @Perms.get_perms("manage_guild")
    async def welcome_message(self, ctx: commands.Context, *, code: str):
      check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
      if check: await self.bot.db.execute("UPDATE welcome SET message = $1 WHERE guild_id = $2", code, ctx.guild.id)
      else: await self.bot.db.execute("INSERT INTO welcome VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
      return await ctx.send_success(f"Welcome message configured as\n```{code}```")
    
    @welcome.command(name="delete", help="config", description="delete the welcome module")
    @Perms.get_perms("manage_guild")
    async def welcome_delete(self, ctx: commands.Context):
      check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
      if not check: return await ctx.send_warning("Welcome is **not** configured")
      else: await self.bot.db.execute("DELETE FROM welcome WHERE guild_id = $1", ctx.guild.id)
      return await ctx.send_success("Welcome has been **deleted**")
    
    @welcome.command(name="test", help="config", description="test welcome module")
    @Perms.get_perms("manage_guild")
    async def welcome_test(self, ctx):
      check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
      if check:
        channel = ctx.guild.get_channel(check["channel_id"])
        if not channel: return await ctx.send_warning("channel **not** found")
        self.bot.dispatch("member_join", ctx.author)
        return await ctx.send_success("Welcome message sent to {}".format(channel.mention))
    
async def setup(bot):
    await bot.add_cog(greet(bot))