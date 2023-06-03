import discord
from discord.ext import commands
import asyncio
from utils.paginator import Paginator
import typing

color = 0x2b2d31

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
                                   
async def setup(bot):
    await bot.add_cog(Music(bot))
