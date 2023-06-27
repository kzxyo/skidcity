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


class images(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

# --------------------------------------------------------------------------------------- Drake command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def drake(self, ctx, d1: str = " ", d2: str = ""):
        embed = discord.Embed(color=Colors.normal)
        embed.set_image(url=f'https://api.memegen.link/images/drake/{d1.replace(" ", "%20")}/{d2.replace(" ", "%20")}.png')
        await ctx.reply(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(images(bot))