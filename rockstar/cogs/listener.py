import discord, aiohttp, button_paginator as pg
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote

class listener(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
# Cooldown Listener

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = discord.Embed(description=f"{emote.warning} {ctx.author.mention}: Command on Cooldown for ` {round(error.retry_after, 2 )}s `", color=hex.warning)
            await ctx.send(embed=cooldown)
            
# On Ready Listener

    @commands.Cog.listener()
    async def on_ready(self):
        online = "<:online:1087666742064590868>"
        log = self.bot.get_channel(1087667080775598170)
        embed = discord.Embed(colour=hex.normal, description=f"{online} Rockstar is now back online.")
        await log.send(embed=embed)
        
# On Server Join Listener

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log = self.bot.get_channel(1088222959434469436)
        embed = discord.Embed(colour=hex.normal, description=f"{emote.tick} Rockstar was added to: `{guild.name}` with `{len(guild.members)}` total users.")
        await log.send(embed=embed)
        
async def setup(bot) -> None:
    await bot.add_cog(listener(bot))