import discord
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter
from datetime import datetime, timedelta
now =datetime.now
from utils.classes import colors, emojis
from cogs.events import sendmsg

dev_list = [911351586398294037]

class own(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="owner")
    async def eval(self, ctx, *, argument: codeblock_converter):
      if not ctx.author.id in self.bot.owner_ids: return
      await ctx.invoke(self.bot.get_command('jishaku py'), argument=argument)

    @commands.command(description="owner")
    async def unauthorize(self, ctx, gid: int=None): 
     if not ctx.author.id in self.bot.owner_ids: return
     if gid is None: return
     guild = discord.utils.get(self.bot.guilds, id=gid)
     async with self.bot.db.cursor() as cursor: 
       await cursor.execute("SELECT * FROM whitelisted WHERE guild = {}".format(guild.id)) 
       check = await cursor.fetchone()
       if check is None: return await sendmsg(self, ctx, None, discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} {guild.name} is not whitelisted"), None, None, None)
       await cursor.execute("DELETE FROM whitelisted WHERE guild = {}".format(gid))
       await self.bot.db.commit()
       for x in self.bot.guilds:
        if x.id == gid:
          try:
            await x.leave()
          except:
            continue
          await sendmsg(self, ctx, None, discord.Embed(color=colors.default, description=f"{emojis.approve} {guild.name} can no longer use the bot"), None, None, None)

    @commands.command(description="owner")
    async def authorize(self, ctx, gid: int=None): 
     if not ctx.author.id in self.bot.owner_ids: return
     if gid is None: return
     async with self.bot.db.cursor() as cursor: 
       await cursor.execute("SELECT * FROM whitelisted WHERE guild = {}".format(gid)) 
       check = await cursor.fetchone()
       if check is not None: return await sendmsg(self, ctx, None, discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} {gid} is already whitelisted"), None, None, None)
       await cursor.execute(f"INSERT INTO whitelisted VALUES ({gid})")
       await self.bot.db.commit()
       await sendmsg(self, ctx, None, discord.Embed(color=colors.default, description=f"{emojis.approve} {gid} can now use the bot"), None, None, None)     

    @commands.command(aliases=['portal', 'getinv'])
    async def getinvite(self, ctx, gid: int=None):
        if not ctx.author.id in self.bot.owner_ids: return

        guild_msg = discord.utils.get(self.bot.guilds, id=gid)
        channel = guild_msg.text_channels[0]
        inv = await channel.create_invite(max_age=86400)
        await ctx.send(inv)

       
async def setup(bot):
    await bot.add_cog(own(bot))