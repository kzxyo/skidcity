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

class autorole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS autorole (role INTEGER, guild INTEGER)")
        await self.bot.db.commit()
    
    @commands.group(aliases = ['arl'])
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            dev = self.bot.get_user(565627105552105507)
            return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")

    @autorole.command()
    @commands.has_permissions(manage_guild = True)
    async def add(self, ctx, *, role: discord.Role):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO autorole VALUES (?, ?)", (role.id, ctx.guild.id,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: Now assigning {role.mention} to new members""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @autorole.command()
    @commands.has_permissions(manage_guild = True)
    async def clear(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autorole WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: No longer assigning any role to new members""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @autorole.command(aliases = ['list'])
    @commands.has_permissions(manage_guild = True)
    async def show(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT role FROM autorole WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        response = table[0]
                        role = ctx.guild.get_role(response)
                        num += 1
                        auto += f"\n`{num}` {role.mention}"
                    embed = discord.Embed(description = auto, color = 0x2f3136)
                    embed.set_author(name = "list of automatically assigned roles", icon_url = ctx.message.author.display_avatar)
                    await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @autorole.command(aliases = ['remove'])
    @commands.has_permissions(manage_guild = True)
    async def delete(self, ctx, *, msg: discord.Role):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autorole WHERE guild = ? AND role LIKE ?", (ctx.guild.id, msg.id,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: No longer assigning {msg.mention} to new members""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
 

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT role FROM autorole WHERE guild = ?", (member.guild.id,))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            trigger = table[0]
                            role = member.guild.get_role(trigger)
                            if role in member.roles:
                                pass
                            else:
                                await member.add_roles(role)
                    else:
                        pass


async def setup(bot):
    await bot.add_cog(autorole(bot))