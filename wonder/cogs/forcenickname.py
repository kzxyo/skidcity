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

class forcenickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.group(aliases = ['fn'])
    async def forcenickname(self, ctx):
        if ctx.invoked_subcommand is None:
            dev = self.bot.get_user(565627105552105507)
            return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")

    @forcenickname.command()
    @commands.has_permissions(manage_guild = True)
    async def add(self, ctx,  member: discord.Member, *, nick):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT user, nickname FROM forcenick WHERE guild = ? AND user = ?", (ctx.guild.id, member.id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute("UPDATE forcenick SET nickname = ? WHERE user = ?", (nick, member.id,))
                else:
                    await cursor.execute("INSERT INTO forcenick VALUES (?, ?, ?)", (member.id, nick, ctx.guild.id,))
            await member.edit(nick=nick)
            await ctx.reply("👍")
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @forcenickname.command()
    @commands.has_permissions(manage_guild = True)
    async def clear(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM forcenick WHERE guild = ?", (ctx.guild.id,))
            await ctx.reply("👍")
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @forcenickname.command(aliases = ['remove'])
    @commands.has_permissions(manage_guild = True)
    async def delete(self, ctx, *, msg):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM forcenick WHERE guild = ? AND user LIKE ?", (ctx.guild.id, msg,))
            await ctx.reply("👍")
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @forcenickname.command(aliases = ['list'])
    @commands.has_permissions(manage_guild = True)
    async def show(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT user, nickname FROM forcenick WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        response = table[0]
                        nick = table[1]
                        num += 1
                        await self.bot.get_user(response)
                        auto += f"\n`{num}` {response.mention} — `{nick}`"
                    embed = discord.Embed(description = auto, color = 0x2F3136)
                    embed.set_author(name = "forcenickname", icon_url = ctx.message.author.display_avatar)
                    await ctx.reply(embed=embed)
                else:
                    embed = discord.Embed(description = f"<:warn:1012642863701565481> {ctx.message.author.mention}: No member ", color = 0xFFD33C)
                    await ctx.reply(embed=embed)
        except Exception as e:
            print(e)


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
            async with self.bot.db.cursor() as cursor:
                        await cursor.execute("SELECT nickname FROM forcenick WHERE guild = ? AND user = ?", (before.guild.id, before.id,))
                        data = await cursor.fetchone()
                        if data:
                            nick = data[0]
                            user = [1]
                            if after.nick != nick:
                                await before.edit(nick=nick)
                        

async def setup(bot):
    await bot.add_cog(forcenickname(bot))