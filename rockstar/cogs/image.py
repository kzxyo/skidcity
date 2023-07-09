import discord, aiohttp, button_paginator as pg
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote

class image(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
# Drake Meme

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def drake(self, ctx, d1: str = " ", d2: str = ""):
        if d1 == " ":
            em = discord.Embed(color=hex.warning, description=f"**{emote.warning} {ctx.author.mention}: You must type something...")
            await ctx.reply(embed=em, mention_author=False)
            return
        if d2 == "":
            em = discord.Embed(color=hex.warning, description=f'**{emote.warning} {ctx.author.mention} not just `"{d1}"`, make a space after it and type more!**')
            await ctx.reply(embed=em, mention_author=False)
            return
        await ctx.channel.typing()
        embed = discord.Embed(colour=hex.normal)
        embed.set_image(url=f'https://api.memegen.link/images/drake/{d1.replace(" ", "%20")}/{d2.replace(" ", "%20")}.png')
        await ctx.reply(embed=embed)
        
# https://api.memegen.link/images/captain/look_at_me/i_am_the_captain_now.png

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def captain(self, ctx, *, topsentence = " "):
        if topsentence is None:
            embed = discord.Embed(colour=hex.warning, description=f"**{emote.warning} {ctx.author.mention}: You must type something...**")
            await ctx.reply(embed=embed, mention_author=False)
            return
        await ctx.channel.typing()
        embed = discord.Embed(colour=hex.normal)
        embed.set_image(url=f'https://api.memegen.link/images/captain/{topsentence.replace(" ", "_")}.png')
        await ctx.send(embed=embed)
        
async def setup(bot) -> None:
    await bot.add_cog(image(bot))