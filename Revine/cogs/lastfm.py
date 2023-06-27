# This source code is 100% original, any contents will be credited in revine's credits command. Created by fsb#1337 & report#0001

import discord, datetime, time, asyncio, random, requests, os
from discord.ext import commands
from typing import Union
from discord.ui import View, Button
from classes import Emotes, Colors, API_Keys

start_time = time.time()

async def get(session: object, url: object) -> object:
    async with session.get(url) as response:
        return await response.text()


class lastfm(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot



async def setup(bot) -> None:
    await bot.add_cog(lastfm(bot))