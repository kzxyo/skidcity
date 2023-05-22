import discord, os, aiohttp, typing, random
from discord.ext import tasks, commands
from .modules import utils
import button_paginator as pg
from cogs.utilevents import blacklist
class img(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="compare two things with the drake meme")
    @blacklist()
    async def drake(self, ctx, msg1, msg2):
        embed = discord.Embed(
             title="Drake meme", color=0xf7f9f8)
        embed.set_image(url=f"https://api.popcat.xyz/drake?text1={msg1}&text2={msg2}")
        await ctx.reply(embed=embed, mention_author=False)
    @commands.command()
    @blacklist()
    async def fry(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/fry/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    @blacklist()
    async def bihw(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/bihw/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    @blacklist()
    async def cheems(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/cheems/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)


    @commands.command()
    @blacklist()
    async def mb(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/mb/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    @blacklist()
    async def mordor(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/mordor/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(img(bot))