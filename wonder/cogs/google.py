import os
import re
import ast
import json
import random
import urllib
import discord
import inspect
import asyncio
import aiohttp
import datetime
import requests
import giphy_client
import button_paginator as pg
import aiosqlite


from io import BytesIO
from bs4 import BeautifulSoup
from asyncio import sleep
from discord.ext import commands, tasks
from discord.ui import Button, View
from giphy_client.rest import ApiException


class google(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['g', 'gsearch', 'googlesearch'])
    async def google(self, ctx, *, query: str=None):
        if query == None:
            return await ctx.reply("what do you wanna search for")
        embeds = []
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://dev.wock.cloud/google/search', params={'query': query, 'safe': 'True'}) as resp:
                    x = await resp.json()
                    for i in range(len(x['results'])):
                        try:
                            embeds.append(
                                discord.Embed(
                                    color = 0x2f3136,
                                    description = f"> [{x['results'][int(i)]['description']}]({x['results'][int(i)]['url']})",
                                    title = x['results'][int(i)]['title'],).set_footer(
                                        text = f"Page {int(i) + 1}/{len(x['results'])} of google search results",
                                        icon_url = "https://cdn.discordapp.com/attachments/663058789582372891/1048952152355242034/google-logo-png-webinar-optimizing-for-success-google-business-webinar-13.png"
                                    ).set_author(
                                        name = ctx.author.name,
                                        icon_url = ctx.author.display_avatar
                                    ))
                        except:
                            pass
                    paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
                    paginator.add_button('prev')
                    paginator.add_button('delete')
                    paginator.add_button('next')
                    paginator.add_button('goto')
                    await paginator.start()

    @commands.command(aliases = ['img'])
    async def image(self, ctx, *, query: str=None):
        if query == None:
            return await ctx.reply("what do you wanna search for")
        embeds = []
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://dev.wock.cloud/google/search', params={'query': query, 'images': 'True', 'safe': 'True'}) as resp:
                    x = await resp.json()
                    for i in range(len(x['results'])):
                        try:
                            embeds.append(
                                discord.Embed(
                                    color = 0x2f3136,
                                    description = f"> [{x['results'][int(i)]['description']}]({x['results'][int(i) + 1]['url']})",
                                    title = x['results'][int(i)]['title'],).set_footer(
                                        text = f"Page {int(i) + 1}/{len(x['results'])} of google search results",
                                        icon_url = "https://cdn.discordapp.com/attachments/663058789582372891/1048952152355242034/google-logo-png-webinar-optimizing-for-success-google-business-webinar-13.png"
                                    ).set_author(
                                        name = ctx.author.name,
                                        icon_url = ctx.author.display_avatar
                                    ).set_image(url = x['results'][int(i) + 1]['image']))
                        except:
                            pass
                    paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
                    paginator.add_button('prev')
                    paginator.add_button('delete')
                    paginator.add_button('next')
                    paginator.add_button('goto')
                    await paginator.start()
async def setup(bot):
    await bot.add_cog(google(bot))
