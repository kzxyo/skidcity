import discord
from discord.ext import commands

class nodata(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS nodata (user INTEGER)")
        await self.bot.db.commit()

async def setup(bot):
    await bot.add_cog(nodata(bot))