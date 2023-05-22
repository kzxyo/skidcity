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

class chatfilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS chatfilter (trigger TEXT, guild INTEGER)")
        await self.bot.db.commit()
    
    @commands.group(aliases = ['cf'])
    async def chatfilter(self, ctx):
        if ctx.invoked_subcommand is None:
            dev = self.bot.get_user(565627105552105507)
            return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")

    @chatfilter.command()
    @commands.has_permissions(manage_guild = True)
    async def add(self, ctx, *, trigger):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO chatfilter VALUES (?, ?)", (trigger, ctx.guild.id,))
            embed = discord.Embed(description = f"Successfully added trigger `{trigger}` to the filter", color = 0xA8EA7B)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @chatfilter.command()
    @commands.has_permissions(manage_guild = True)
    async def clear(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM chatfilter WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"Successfully cleared blacklisted words", color = 0xA8EA7B)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @chatfilter.command(aliases = ['list'])
    @commands.has_permissions(manage_guild = True)
    async def show(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT trigger FROM chatfilter WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        response = table[0]
                        num += 1
                        auto += f"\n`{num}` {response}"
                    embed = discord.Embed(description = auto, color = 0x69919D)
                    embed.set_author(name = "list of blacklisted words", icon_url = ctx.message.author.display_avatar)
                    await ctx.reply(embed=embed)
        except Exception as e:
            print(e)
 

    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT trigger FROM chatfilter WHERE guild = ?", (message.guild.id,))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            trigger = table[0]
                            if message.author.bot:
                                pass
                            else:
                                if trigger.lower() in message.content.lower():
                                    await message.delete()
                                    embed = discord.Embed(description = f"<:warn:1012642863701565481> {ctx.message.author.mention}: That word is not allowed here")
                                    msg = await message.channel.send(embed=embed) 


async def setup(bot):
    await bot.add_cog(chatfilter(bot))