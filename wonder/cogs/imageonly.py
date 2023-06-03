import os
import re
import ast
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

from io import BytesIO
from discord import ui
from pyfiglet import Figlet
from asyncio import sleep
from urllib.request import urlopen
from discord.ext import commands
from discord.ext import tasks
from discord.ui import Button, View
from giphy_client.rest import ApiException

class imageonly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS imageonly (channel INTEGER, guild INTEGER)")
        await self.bot.db.commit()
    
    @commands.group(aliases = ['io'])
    async def imageonly(self, ctx):
        if ctx.invoked_subcommand is None:
            dev = self.bot.get_user(565627105552105507)
            return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")

    @imageonly.command()
    @commands.has_permissions(manage_guild = True)
    async def add(self, ctx, *, channel: discord.TextChannel):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO imageonly VALUES (?, ?)", (channel.id, ctx.guild.id,))
            await ctx.reply("👍")
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @imageonly.command()
    @commands.has_permissions(manage_guild = True)
    async def clear(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM imageonly WHERE guild = ?", (ctx.guild.id,))
            await ctx.reply("👍")
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @imageonly.command(aliases = ['list'])
    @commands.has_permissions(manage_guild = True)
    async def show(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT channel FROM imageonly WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        response = table[0]
                        channel = self.bot.get_channel(response)
                        num += 1
                        auto += f"\n`{num}` {channel.mention}"
                    embed = discord.Embed(description = auto, color = 0x2f3136)
                    embed.set_author(name = "list of image-only channels", icon_url = ctx.message.author.display_avatar)
                    await ctx.reply(embed=embed)
        except Exception as e:
            print(e)
 

    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT channel FROM imageonly WHERE guild = ?", (message.guild.id,))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            trigger = table[0]
                            channel = self.bot.get_channel(trigger)
                            if message.author.bot:
                                pass
                            else:
                                if message.channel.id == channel.id:
                                    if message.attachments:
                                        pass
                                    else:
                                        await message.delete()


async def setup(bot):
    await bot.add_cog(imageonly(bot))