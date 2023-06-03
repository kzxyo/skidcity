import os
import sys
import re
import ast
import json
import random
import urllib
import discord
import inspect
import asyncio
import aiohttp
import datetime
import requests
import giphy_client

from io import BytesIO
from asyncio import sleep
from discord.ext import commands, tasks
from discord.ui import Button, View
from giphy_client.rest import ApiException

def restart_bot(): 
    os.execv(sys.executable, ['python'] + sys.argv)

class owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def guildlist(self, ctx):
        try:
            x = ""
            for guild in self.bot.guilds:
                x += f"{guild.name} - {guild.id}\n"
            embed = discord.Embed(description = x, color = 0x2F3136)
            embed.set_author(name = f"All guilds I'm in")
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command()
    @commands.is_owner()
    async def leaveserver(self, ctx, guild: discord.Guild = None):
        if guild is None:
            return await ctx.reply("provid a guild")
        try:
            guild = guild
            await guild.leave()
            await ctx.reply(f"done")
        except Exception as e:
            await ctx.reply(e)

    @commands.command(aliases=['link'])
    @commands.is_owner() 
    async def guildinvite(self, ctx, *, guild: discord.Guild = None):
        try:
            if guild == None:
                guild = ctx.guild
            else:
                guild = self.bot.get_guild(guild.id)
            link = await random.choice(guild.text_channels).create_invite(max_age=0, max_uses=0)
            await ctx.reply(f'**invite:** {link}')
        except Exception as e:
            print(e)

    @commands.command(aliases = ['reboot'])
    @commands.is_owner()
    async def restart(self, ctx):
        embed = discord.Embed(description = "<a:loading:1008825897798869055> **Restarting bot**", color = 0xFCFCFC)
        await ctx.reply(embed=embed)
        restart_bot()



    @commands.command(aliases = ['auth'])
    @commands.is_owner()
    async def authorize(self, ctx, guild: discord.Guild = None):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT guild FROM authorized WHERE guild = ?", (guild.id,))
                data = await cursor.fetchall()
                if data:
                        await cursor.execute("DELETE FROM authorized WHERE guild = ?", (guild.id,))
                        return await ctx.reply(f"`{guild.id}` is no longer authorized")
                else:
                    await cursor.execute("INSERT INTO authorized VALUES (?)", (guild.id,))
                    return await ctx.reply(f"`{guild.id}` is now authorized")
        except Exception as e:
            print(e)

    @commands.command(aliases = ['authed'])
    @commands.is_owner()
    async def authorized(self, ctx):
        try:
            guilds = ""
            num = 0
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT guild FROM authorized")
                data = await cursor.fetchall()
                if data:
                    for table in data:
                        num += 1
                        x = self.bot.get_guild(table[0])
                        guilds += f"`{num}` {x.name} - {x.id}\n"
            embed = discord.Embed(color = 0x2F3136, description = guilds)
            embed.set_author(name = f"authorized servers", icon_url = self.bot.user.avatar)
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)
    
async def setup(bot):
    await bot.add_cog(owner(bot))