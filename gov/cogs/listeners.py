from click import command
import discord, time, datetime, psutil, button_paginator as pg
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
from utility import Emotes, Colours

class listeners(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Timed out for ` {round(error.retry_after, 2 )}s `", color=Colours.standard)
            await ctx.send(embed=cooldown)
            
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            permissions = discord.Embed(description=f"**{Emotes.warningemote} {ctx.author.mention}: I've not got permissions to do that.**", color=Colours.standard)
            await ctx.send(embed=permissions)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.GuildNotFound):
            guildnotfound = discord.Embed(description=f"**{Emotes.warningemote} {ctx.author.mention}: I couldn't find that guild.**", color=Colours.standard)
            await ctx.send(embed=guildnotfound)
            
            
async def setup(bot) -> None:
    await bot.add_cog(listeners(bot))