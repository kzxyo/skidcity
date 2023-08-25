import discord
from discord.ext import commands
from utilities import vile


class Alley(commands.Cog):
    def __init__(self, bot: "VileBot") -> None:
        self.bot = bot

    
    @commands.command(
        name="alley"
    )
    async def alley(self, ctx: vile.Context):
        """Alley!"""
        return await ctx.send(file=discord.File("king-bob.gif"))


async def setup(bot: "VileBot") -> None:
    await bot.add_cog(Alley(bot))