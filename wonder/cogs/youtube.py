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
import timeago

from io import BytesIO
from discord import ui
from pyfiglet import Figlet
from asyncio import sleep
from urllib.request import urlopen
from discord.ext import commands
from discord.ext import tasks
from discord.ui import Button, View
from pytube import YouTube
from giphy_client.rest import ApiException

class youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
            first_word = message.content.split(' ')
            if first_word[0].lower() == f"wonder":
                if "youtube.com" in first_word[1]:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'}
                    async with aiohttp.ClientSession() as session:
                            async with session.get(first_word[1], headers = headers) as resp:
                                x = str(resp.url)
                            if YouTube(x).length < 300:
                                try:
                                    async with message.channel.typing():
                                        yt = YouTube(x).streams.get_highest_resolution().download("wonder.mp4")
                                        embed = discord.Embed(color=discord.Color.random(), description = f"**[{YouTube(x).title}]({YouTube(x).channel_url})**")
                                        embed.set_author(name = f"@{YouTube(x).author}", icon_url = YouTube(x).thumbnail_url)
                                        embed.set_footer(text=f"{int(YouTube(x).views):,} 👀| {YouTube(x).length}s ⏱️| {message.author.name}#{message.author.discriminator}", icon_url = "https://cdn.discordapp.com/emojis/1001641960324468788.png")
                                        await message.channel.send(file=discord.File(yt, filename="wonder.mp4"), embed=embed)
                                except Exception as e:
                                    await message.channel.send(f"Something pooped - {e}")
                            else:
                                await message.channel.send("I don't repost videos longer than 5 minutes...")
async def setup(bot):
    await bot.add_cog(youtube(bot))