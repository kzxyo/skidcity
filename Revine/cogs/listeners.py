# This source code is 100% original, any contents will be credited in revine's credits command. Created by fsb#1337 & report#0001

import discord, time, datetime, psutil
from discord.ext import commands
from typing import Union
from discord.ui import View, Button, Select
from classes import Colors, Emotes

class listeners(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Timed out for ` {round(error.retry_after, 2 )}s `", color=Colors.normal)
            await ctx.send(embed=cooldown)

    @commands.Cog.listener()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def on_message(self, message: discord.Message):
        if message.content == f"<@{self.bot.user.id}>":
            embed = discord.Embed(color=Colors.normal, description="Revine's current prefix is **` ; `**")
            await message.reply(embed=embed)
        elif message.content == "revine who created you":
            await message.reply("Well looking at the comments in my code, I think <@979054576546242651> and <@1069726264983818340> are the developers...")
        elif message.content == "whats revine":
            await message.reply(f"Revine is a multipurpose discord bot that features alot of the commands most bots have but... revine's developers listen to there community and add 80% of features requested.")

        
async def setup(bot) -> None:
    await bot.add_cog(listeners(bot))