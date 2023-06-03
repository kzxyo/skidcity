import os
import re
import ast
import io
import json
import random
import urllib
import discord
import inspect
import base64
import asyncio
import aiohttp
import datetime
import requests
import giphy_client
import aiosqlite
import button_paginator as pg

from io import BytesIO
from discord import ui
from pyfiglet import Figlet
from asyncio import sleep
from urllib.request import urlopen
from discord.ext import commands
from discord.ext import tasks
from discord.ui import Button, View
from giphy_client.rest import ApiException

class tiktok(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
            r = []
            num = 0
            first_word = message.content.split(' ')
            if first_word[0].lower() == f"wonder":
                if 'tiktok.com' in message.content:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'}
                        async with aiohttp.ClientSession() as session:
                            async with message.channel.typing():
                                async with session.get(first_word[1], headers = headers) as resp:
                                    x = str(resp.url)
                                    z = x.split('?')[0].split('/')[::-1][0]
                                async with session.get(url=f"https://dev.wock.cloud/tiktok/post/{z}", headers= {'Authorization': 'ARTIST:jpbpU3GaYBvCw9wIjloSKjrq7fJjLJEg'}) as response:
                                    try:
                                        data = await response.json()
                                        if data.get('images'):
                                                for image in data.get('images'):
                                                    num += 1
                                                    r.append(discord.Embed(color=discord.Color.random(), title = data['information']['caption'], url = data['share_url']).set_footer(text = f"Page {num}/{len(data.get('images'))} | {data['information']['likes']} 👍 | {data['information']['comments']} 💬 | {data['information']['views']} 👀 ({data['information']['shares']} 🔗)", icon_url = "https://cdn.discordapp.com/attachments/663058789582372891/1046539354983628820/image.png").set_author(name = f"{data['author']['nickname']} (@{data['author']['unique_id']})", icon_url = data['author']['avatar_url']).set_image(url=image))
                                                paginator = pg.Paginator(self.bot, r, message.channel, invoker=message.author.id)
                                                paginator.add_button('prev')
                                                paginator.add_button('next')
                                                await paginator.start()
                                        if data.get('video'):
                                            async with session.get(url=data.get('video')) as res:
                                                object = io.BytesIO(await res.read())
                                                embed = discord.Embed(color = discord.Color.random(), description = f"**[{data['information']['caption']}]({data['share_url']})**")
                                                embed.set_author(name = f"{data['author']['nickname']} (@{data['author']['unique_id']})", icon_url = data['author']['avatar_url'])
                                                embed.set_footer(text = f"{int(data['information']['likes']):,} 👍 | {int(data['information']['comments']):,} 💬 | {int(data['information']['views']):,} 👀 ({int(data['information']['shares']):,} 🔗) — {message.author.name}#{message.author.discriminator}", icon_url = "https://cdn.discordapp.com/attachments/663058789582372891/1046539354983628820/image.png")
                                                await message.channel.send(file=discord.File(object, filename = "wonder.mp4"), embed=embed)
                                    except Exception as e:
                                        await message.channel.send(f"Something pooped - {e}")
async def setup(bot):
    await bot.add_cog(tiktok(bot))