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

class afk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS afk1 (user INTEGER, guild INTEGER, reason TEXT, time INTEGER)")
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT reason, time FROM afk1 WHERE user = ? AND guild = ?", (message.author.id, message.guild.id,))
            data = await cursor.fetchone()
            if data:
                embed = discord.Embed(color = 0x2f3136, description = f"👋 {message.author.mention}: Welcome back, you were last seen <t:{int(data[1])}:R>")
                await message.reply(embed=embed, delete_after=5) 
                await cursor.execute("DELETE FROM afk1 WHERE user = ? AND guild = ?", (message.author.id, message.guild.id,))
            if message.mentions:
                for mention in message.mentions:
                    await cursor.execute("SELECT reason, time FROM afk1 WHERE user = ? AND guild = ?", (mention.id, message.guild.id,))
                    data2 = await cursor.fetchone()
                    if data2 and mention.id != message.author.id:
                        embed = discord.Embed(color = 0x2f3136, description = f"💤 {message.author.mention}: {mention.mention} is currently AFK: `{data2[0]}` - <t:{int(data2[1])}:R>")
                        await message.channel.send(embed=embed, delete_after=5)
        await self.bot.db.commit()

    @commands.command()
    async def afk(self, ctx, *, reason = None):
        if reason == None:
            reason = "AFK"
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT reason, time FROM afk1 WHERE user = ? AND guild = ?", (ctx.author.id, ctx.guild.id,))
            data = await cursor.fetchone()
            if data:
                if data[0] == reason:
                    return await ctx.reply("you're already afk with that reason")
                await cursor.execute("UPDATE afk1 SET reason = ? AND time = ? WHERE user = ? AND guild = ?", (reason, ctx.author.id, ctx.guild.id, int(datetime.datetime.now().timestamp()),))
            else:
                await cursor.execute("INSERT INTO afk1 (user, guild, reason, time) VALUES (?, ?, ?, ?)", (ctx.author.id, ctx.guild.id, reason, int(datetime.datetime.now().timestamp()),))
                embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: You're now **AFK:** `{reason}`")
                await ctx.reply(embed=embed)
        await self.bot.db.commit()


async def setup(bot):
    await bot.add_cog(afk(bot))