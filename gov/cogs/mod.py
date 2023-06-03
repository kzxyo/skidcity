import discord, json, button_paginator as pg
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
from utility import Emotes, Colours

class mod(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member:discord.Member = None, *, reason = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warningemote}: Please mention a user.", color=Colours.warning)
            await ctx.send(embed=embed)
            return
        if reason == None:
            embed = discord.Embed(description=f"{Emotes.warningemote}: Please give a reason.", color=Colours.warning)
            await ctx.send(embed=embed)
            return
        await member.ban(reason = reason)
        embed = discord.Embed(description=f"banned {member.mention} **Reason: {reason}**", colour=Colours.standard)
        await ctx.send(embed=embed, mention_author=False)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warningemote} {ctx.author.mention}: You do not have permissions. `Manage Roles`", colour=Colours.standard)
            await ctx.send(embed=embed, mention_author=False)
            
async def setup(bot) -> None:
    await bot.add_cog(mod(bot))