import discord, aiohttp, button_paginator as pg
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote

class reaction(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
        
        
async def setup(bot) -> None:
    await bot.add_cog(reaction(bot))