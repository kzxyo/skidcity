import discord, button_paginator as pg, os, datetime, psutil, time, aiohttp
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
from platform import python_version, python_version_tuple

starttime = time.time()

class page(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
        
    class button(discord.ui.Button):
        def __init__(self):
            super().__init__(label='Hi', style=discord.ButtonStyle.danger)
  
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def test(self, ctx):
        embeds = pg.embed_creator("Very long text"*10000, 1995, prefix='```\n', suffix='\n```')
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
        paginator.default_pagination()
        await paginator.start()

async def setup(bot) -> None:
    await bot.add_cog(page(bot))        
