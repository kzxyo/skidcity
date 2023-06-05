import discord
from discord.ext import commands
from cogs.events import sendmsg
from utils.classes import Colors, Emojis

class auth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases = ["auth"])
    async def authorize(self, ctx, *, gid: int=None): 
     if not ctx.author.id in self.bot.owner_ids: return
     if gid is None: return await ctx.send(embed=discord.Embed(color=Colors.default, description="specify guild id"))
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM authorize WHERE guild_id = {}".format(gid)) 
      check = await cursor.fetchone()
      if check is not None: return await sendmsg(self, ctx, None, discord.Embed(color=Colors.yellow, description=f"**{gid}** is already authorized"), None, None, None)
      await cursor.execute(f"INSERT INTO authorize VALUES ({gid})")
      await self.bot.db.commit()
      await sendmsg(self, ctx, None, discord.Embed(color=Colors.default, description=f"authorized **{gid}**"), None, None, None)
    
    @commands.command(aliases = ["unauth"])
    async def unauthorize(self, ctx, gid: int=None): 
     if not ctx.author.id in self.bot.owner_ids: return
     if gid is None: return
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM authorize WHERE guild_id = {}".format(gid)) 
      check = await cursor.fetchone()
      if check is None: return await sendmsg(self, ctx, None, discord.Embed(color=Colors.yellow, description=f"**{gid}** is not authorized"), None, None, None)
      await cursor.execute("DELETE FROM authorize WHERE guild_id = {}".format(gid))
      await self.bot.db.commit()
      await sendmsg(self, ctx, None, discord.Embed(color=Colors.default, description=f"removed authorization from **{gid}**"), None, None, None)
    
async def setup(bot):
    await bot.add_cog(auth(bot))