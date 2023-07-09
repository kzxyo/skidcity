import discord, aiohttp, button_paginator as pg
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote

class role(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
# Add Role Command
        
    @commands.command(aliases=['rolei', 'rinfo', 'aboutrole', 'ri'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roleinfo(self, ctx, *, role: discord.Role = None):
        if role is None:
            errorembed = discord.Embed(colour=hex.normal, description=f"{emote.warning} {ctx.author.mention}**: You need to mention a role.**")
            await ctx.reply(embed=errorembed)
        else:
            roleembed = discord.Embed(title=f"{role.name}", colour=role.colour, description=f'{role.mention}\n**Role ID:** `{role.id}`\n**Role Created:** <t:{int(role.created_at.timestamp())}:R>\n**Mentionable?:** `{role.mentionable}`')
            roleembed.set_thumbnail(url=role.display_icon)
            await ctx.reply(embed=roleembed)
        
        
async def setup(bot) -> None:
    await bot.add_cog(role(bot))