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
import aiosqlite

from io import BytesIO
from discord import ui
from pyfiglet import Figlet
from asyncio import sleep
from urllib.request import urlopen
from discord.ext import commands
from discord.ext import tasks
from discord.ui import Button, View
from cogs.events import noperms, commandhelp, blacklist, sendmsg

class autoreact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS autoreact (trigger TEXT, emoji TEXT, guild_id INTEGER)")
        await self.bot.db.commit()
    
    @commands.group(help="set an autoreact for the server", description="utility", usage="[subcommand] [trigger] [emoji]", brief="autoreact add - add an autoreact\nautoreact remove - remove an autoreact\nautoreact list - see a list of autoreact", aliases = ['art'])
    async def autoreact(self, ctx):
        if ctx.invoked_subcommand is None:
            dev = self.bot.get_user(112635397481213952)
            return await ctx.reply(f"{ctx.author.mention}: view the commands for **autoreact** on the main help embed", mention_author=False)

    @autoreact.command(help="set an autoreact for the server", description="utility", usage="[subcommand] [trigger] [emoji]", brief="autoreact add - add an autoreact\autoreact remove - remove autoreact\autoreact list - see a list of autoreact")
    @commands.has_permissions(manage_guild = True)
    async def add(self, ctx, trigger, reaction):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO autoreact VALUES (?, ?, ?)", (trigger, reaction, ctx.guild.id,))
            embed = discord.Embed(description = f""" {ctx.author.mention}: Successfully created an **autoreaction** for `{trigger}`""", color = 0xd3d3d3)
            await ctx.reply(embed=embed, mention_author=False)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @blacklist()
    @autoreact.command(aliases = ['remove'])
    @commands.has_permissions(manage_guild = True)
    async def delete(self, ctx, *, msg):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autoreact WHERE guild_id = ? AND trigger LIKE ?", (ctx.guild.id, msg,))
            embed = discord.Embed(description = f""" {ctx.author.mention}: Successfully deleted the **autoreaction** for `{msg}`""", color = 0xd3d3d3)
            await ctx.reply(embed=embed, mention_author=False)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @blacklist()
    @autoreact.command(aliases = ['list'])
    @commands.has_permissions(manage_guild = True)
    async def show(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT emoji, trigger FROM autoreact WHERE guild_id = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        trigger = table[1]
                        emoji = table[0]
                        num += 1
                        auto += f"\n`{num}` {trigger}: {emoji}"
                    embed = discord.Embed(description = auto, color = 0xd3d3d3)
                    embed.set_author(name = "list of auto reactions", icon_url = ctx.message.author.display_avatar)
                    await ctx.reply(embed=embed, mention_author=False)
                else:
                    embed = discord.Embed(description = f" {ctx.message.author.mention}: No auto reaction triggers have been set up", color = 0xFFD33C)
                    await ctx.reply(embed=embed, mention_author=False)
        except Exception as e:
            print(e)
    @blacklist()
    @autoreact.command()
    @commands.has_permissions(manage_guild = True)
    async def clear(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autoreact WHERE guild_id = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f""" {ctx.author.mention}: Successfully deleted **all** triggers""", color = 0xd3d3d3)
            await ctx.reply(embed=embed, mention_author=False)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @blacklist()
    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT emoji, trigger FROM autoreact WHERE guild_id = ?", (message.guild.id,))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            trigger = table[1]
                            emoji = table[0]
                            if message.author.bot:
                                pass
                            else:
                                if trigger.lower() in message.content.lower():
                                    await asyncio.sleep(0.5)
                                    await message.add_reaction(emoji)   


async def setup(bot):
    await bot.add_cog(autoreact(bot))