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

class color(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def color(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = f"""<:info:1031966439055315036> {ctx.author.mention}: View the commands at **https://wonderbot.club/commands**""",color = 0x6CCCE6)
            return await ctx.send(embed=embed)

    @color.command()
    @commands.has_permissions(manage_guild = True)
    async def hoist(self, ctx, status):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT status FROM hoist WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchone()
                if data:
                    nigga = data[0]
                    if status == "on":
                        if nigga == "off":
                            await cursor.execute("UPDATE hoist SET status = ? WHERE guild = ?", ('off', ctx.guild.id,))
                            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: I will no longer **hoist** color roles")
                            return await ctx.reply(embed=embed)
                        elif nigga == "on":
                            embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: **Hoisting** color roles is **already enabled**", color = 0x2f3136)
                            return await ctx.reply(embed=embed)
                    elif status == "off":
                        if nigga == "on":
                            await cursor.execute("UPDATE hoist SET status = ? WHERE guild = ?", ('on', ctx.guild.id,))
                            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: I will now **hoist** color roles")
                            return await ctx.reply(embed=embed)
                        elif nigga == "off":
                            embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: **Hoisting** color roles is **already disabled**", color = 0x2f3136)
                            return await ctx.reply(embed=embed)
                else:
                    if status == "on":
                            await cursor.execute("INSERT INTO hoist VALUES (?, ?)", ('on', ctx.guild.id,))
                            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: I will now **hoist** color roles")
                            return await ctx.reply(embed=embed)
                    elif status == "off":
                            await cursor.execute("INSERT INTO hoist VALUES (?, ?)", ('off', ctx.guild.id,))
                            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: I will no longer **hoist** color roles")
                            return await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.reply(e)


    @color.command()
    async def me(self, ctx, color = None):
        try:
                role = await ctx.guild.create_role(name=f"{ctx.author.name}'s color", color = int(color, 16))
                if color == "none":
                    await role.delete()
                    embed = discord.Embed(color = 0x2f3136, description = f"🎨 {ctx.author.mention}: Your **color role** has been **deleted**")
                    await ctx.reply(embed=embed)
                else:
                    async with self.bot.db.cursor() as cursor:
                        await cursor.execute("SELECT status FROM hoist WHERE guild = ?", (ctx.guild.id,))
                        data = await cursor.fetchone()
                        if data:
                            status = data[0]
                            if status == "on":
                                await role.edit(position=ctx.author.top_role.position)
                            elif status == "off":
                                pass
                        else:
                            pass
                        await ctx.author.add_roles(role)
                        embed = discord.Embed(color = 0x2f3136, description = f"🎨 {ctx.author.mention}: Cool, your **color role** is now set to `{role.color}`")
                        await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.reply(e)
            

async def setup(bot):
    await bot.add_cog(color(bot))