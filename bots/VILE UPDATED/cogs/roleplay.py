import discord, typing, time, arrow, psutil, copy, aiohttp, random, asyncio, yarl
from datetime import datetime
from typing import Optional, Union
from io import BytesIO
from utilities import utils
from utilities.baseclass import Vile
from utilities.context import Context
from discord.ext import commands


class Roleplay(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.command(
        name='hug',
        description='hug the mentioned user',
        brief='hug <user>',
        help='hug @glory#0007'
    )
    async def hug(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error('you must be lonely..')

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/hug')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} hugged {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='cuddle',
        description='cuddle the mentioned user',
        brief='cuddle <user>',
        help='cuddle @glory#0007'
    )
    async def cuddle(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error('you must be lonely..')

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/cuddle')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} cuddled {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='tickle',
        description='tickle the mentioned user',
        brief='tickle <user>',
        help='tickle @glory#0007'
    )
    async def tickle(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error('you must be lonely..')

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/tickle')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} tickled {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='kiss',
        description='kiss the mentioned user',
        brief='kiss <user>',
        help='kiss @glory#0007'
    )
    async def kiss(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error('you must be lonely..')

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/kiss')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} kissed {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='feed',
        description='feed the mentioned user',
        brief='feed <user>',
        help='feed @glory#0007'
    )
    async def feed(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error('you must be lonely..')

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/feed')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} fed {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='pat',
        description='pat the mentioned user',
        brief='pat <user>',
        help='pat @glory#0007'
    )
    async def pat(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error('you must be lonely..')

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/pat')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} pat {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='slap',
        description='slap the mentioned user',
        brief='slap <user>',
        help='slap @glory#0007'
    )
    async def slap(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error("don't slap yourself :frowning:")

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/slap')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} slapped {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='wave',
        description='wave at the mentioned user',
        brief='wave <user>',
        help='wave @glory#0007'
    )
    async def wave(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error('you must be lonely..')

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/wave')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} waved at {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='bite',
        description='bite the mentioned user',
        brief='bite <user>',
        help='bite @glory#0007'
    )
    async def bite(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error("don't bite yourself :frowning:")

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/bite')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} bit {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='wink',
        description='wink at the mentioned user',
        brief='wink <user>',
        help='wink @glory#0007'
    )
    async def wave(self, ctx: Context, user: Union[discord.Member, discord.User]):

        if user == ctx.author:
            return await ctx.send_error('you must be lonely..')

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/wink')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} winked at {user.mention}')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


    @commands.command(
        name='cry',
        description="start crying because you're a miserable loser",
    )
    async def cry(self, ctx: Context):

        async with ctx.handle_response():

            data = await self.bot.session.get('https://nekos.best/api/v2/cry')

            embed = discord.Embed(color=self.bot.color, description=f'{ctx.author.mention} started crying...')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=f"attachment://{yarl.URL(data['results'][0]['url']).name}")

            return await ctx.reply(
                embed=embed, 
                file=await utils.file(data['results'][0]['url'], yarl.URL(data['results'][0]['url']).name)
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Roleplay(bot))