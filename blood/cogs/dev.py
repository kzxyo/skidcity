import discord
from discord.ext import commands
import os

class reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="N/A", usage="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        cmds = 0
        for file in os.listdir(f"./cogs"):
                if file.endswith(".py"):
                    cmds += 1
                    await self.bot.reload_extension(f"cogs.{file[:-3]}")
        embed = discord.Embed(color=self.bot.color, description=f"Reloaded all cogs with {cmds} commands")
        await ctx.reply(embed=embed)
            

async def setup(bot):
    await bot.add_cog(reload(bot))