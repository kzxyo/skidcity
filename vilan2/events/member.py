import discord
from discord.ext import commands

class Member(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
      if before.avatar == after.avatar: return
      else:
        check = await self.bot.db.fetchrow("SELECT * FROM avh WHERE user_id = $1", before.id)
        newcount = int(check['count'])+1
        if not check: await self.bot.db.execute("INSERT INTO avh VALUES ($1,$2)", before.id, 0)
        else: await self.bot.db.execute("UPDATE avh SET count = $1 WHERE user_id = $2", newcount, before.id)
    
async def setup(bot):
    await bot.add_cog(Member(bot))