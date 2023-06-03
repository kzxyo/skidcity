import discord, json, button_paginator as pg
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
from utility import Emotes, Colours

class role(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, user: discord.Member = None, role: discord.Role = None):
        if role == None:
            e = discord.Embed(description=f"{Emotes.warningemote} {ctx.author.mention}: You have not mentioned a role.")
            await ctx.reply(embed=e)
            return
        if user == None:
            e = discord.Embed(description=f"{Emotes.warningemote} {ctx.author.mention}: You have not mentioned a user.")
            await ctx.reply(embed=e)
            return
        await user.add_roles(role)
        e = discord.Embed(description=f"{ctx.author.mention} gave {user.mention} the {role.mention}")
        await ctx.send(embed=e)
        
    @role.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.reply(f"I could not find the role that you provided.")
            
    @role.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"You do not have the required permissions.")
            
async def setup(bot) -> None:
    await bot.add_cog(role(bot))