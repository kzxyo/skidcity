import discord, aiohttp,button_paginator as pg
from discord.ext import commands
from discord import app_commands
from typing import Union
from io import BytesIO
from classes import hex, emote

class sql(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @app_commands.command(description="this command is a test")
    async def test(self, ctx: discord.Interaction):
        await ctx.response.send_message("test")
        
async def setup(bot) -> None:
    await bot.add_cog(sql(bot))