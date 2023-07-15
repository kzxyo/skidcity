import discord
from discord.ext import commands
import os

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        help="returns the bot ping",
        usage="ping",
        aliases=["pong", "latency", "ms", "lat"]
    )
    async def ping(self, ctx):
        embed = discord.Embed(color=self.bot.color, description=f"*pings a hot women*: {round(self.bot.latency * 1000)}ms")
        msg = await ctx.reply(embed=embed)
                         

async def setup(bot):
    await bot.add_cog(help(bot))