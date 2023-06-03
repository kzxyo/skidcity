import discord
from discord.ext import commands
import asyncpg
import os

class reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="N/A", usage="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        cmds = 0
        for category in os.listdir("./cogs"):
            for file in os.listdir(f"./cogs/{category}"):
                if file.endswith(".py"):
                    cmds += 1
                    await self.bot.reload_extension(f"cogs.{category}.{file[:-3]}")
        await ctx.reply(f'Reloaded **`{cmds}`** commands')

async def setup(bot):
    await bot.add_cog(reload(bot))