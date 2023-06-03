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

class autoreact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS autoreact (trigger TEXT, emoji TEXT, guild INTEGER)")
        await self.bot.db.commit()
    
    @commands.group(aliases = ['art'])
    async def autoreact(self, ctx):
        if ctx.invoked_subcommand is None:
            dev = self.bot.get_user(565627105552105507)
            return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")

    @autoreact.command()
    @commands.has_permissions(manage_guild = True)
    async def add(self, ctx, trigger, reaction):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO autoreact VALUES (?, ?, ?)", (trigger, reaction, ctx.guild.id,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: Successfully created an **autoreaction** for `{trigger}`""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @autoreact.command(aliases = ['remove'])
    @commands.has_permissions(manage_guild = True)
    async def delete(self, ctx, *, msg):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autoreact WHERE guild = ? AND trigger LIKE ?", (ctx.guild.id, msg,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: Successfully deleted the **autoreaction** for `{msg}`""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @autoreact.command(aliases = ['list'])
    @commands.has_permissions(manage_guild = True)
    async def show(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT emoji, trigger FROM autoreact WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        trigger = table[1]
                        emoji = table[0]
                        num += 1
                        auto += f"\n`{num}` {trigger}: {emoji}"
                    embed = discord.Embed(description = auto, color = 0x2F3136)
                    embed.set_author(name = "list of auto reactions", icon_url = ctx.message.author.display_avatar)
                    await ctx.reply(embed=embed)
                else:
                    embed = discord.Embed(description = f"<:warn:1012642863701565481> {ctx.message.author.mention}: No auto reaction triggers have been set up", color = 0xFFD33C)
                    await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @autoreact.command()
    @commands.has_permissions(manage_guild = True)
    async def clear(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autoreact WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: Successfully deleted **all** triggers""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)


    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT emoji, trigger FROM autoreact WHERE guild = ?", (message.guild.id,))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            trigger = table[1]
                            emoji = table[0]
                            if message.author.bot:
                                pass
                            else:
                                if trigger.lower() in message.content.lower():
                                    await message.add_reaction(emoji)   


async def setup(bot):
    await bot.add_cog(autoreact(bot))