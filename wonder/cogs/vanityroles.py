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

class vanityroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS vanityroles2 (vanity TEXT, role INTEGER, message TEXT, channel INTEGER, guild INTEGER)")
        await self.bot.db.commit()
    
    @commands.group(aliases = ['vr'])
    async def vanityroles(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = f"<:reply:1006282469928079360> **Description:** Reward users for advertising your server in their status",color = 0x62688F)
            embed.add_field(name = "<:reply:1006282469928079360> **Sub commands**", value = f"""```$vanityroles role <role_name/id>
$vanityroles channel <text>
$vanityroles vanity <text>```""", inline = False)
            embed.add_field(name = "<:reply:1006282469928079360> **Example**", value = f"""```$vanityroles role rep
$vanityroles channel #rep-logs
$vanityroles vanity /cool ```""", inline = False)
            embed.set_thumbnail(url = self.bot.user.avatar)
            embed.set_author(name = "Vanity roles", icon_url = self.bot.user.avatar)
            return await ctx.reply(embed=embed)

    @vanityroles.command()
    @commands.has_permissions(manage_guild = True)
    async def vanity(self, ctx, *, vanity):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT vanity FROM vanityroles2 WHERE guild = ?", (ctx.guild.id,))
                starData = await cursor.fetchone()
                if starData:
                    starData = starData[0]
                    if starData == vanity:
                        embed = discord.Embed(description = f"{ctx.message.author.mention}: **{vanity}** is already set", color = 0x2F3136)
                        return await ctx.reply(embed=embed)
                    await cursor.execute("UPDATE vanityroles2 SET vanity = ? WHERE guild = ?", (vanity, ctx.guild.id,))
                    embed = discord.Embed(description = f"{ctx.message.author.mention}: **{vanity}** has been set as the trigger vanity", color = 0xA8EA7B)
                    await ctx.reply(embed=embed)
                else:
                    await cursor.execute("INSERT INTO vanityroles2 VALUES (?, ?, ?, ?, ?)", (vanity, 0, 0, 0, ctx.guild.id,))
                    embed = discord.Embed(description = f"{ctx.message.author.mention}: **{vanity}** has been set as the trigger vanity", color = 0xA8EA7B)
                    await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @vanityroles.command()
    @commands.has_permissions(manage_guild = True)
    async def message(self, ctx, *, message):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT message FROM vanityroles2 WHERE guild = ?", (ctx.guild.id,))
                starData = await cursor.fetchone()
                if starData:
                    starData = starData[0]
                    if starData == message:
                        embed = discord.Embed(description = f"{ctx.message.author.mention}: **{message}** is already set", color = 0x2F3136)
                        return await ctx.reply(embed=embed)
                    await cursor.execute("UPDATE vanityroles2 SET message = ? WHERE guild = ?", (message, ctx.guild.id,))
                    embed = discord.Embed(description = f"{ctx.message.author.mention}: **{message}** has been set as the vanityroles message", color = 0xA8EA7B)
                    await ctx.reply(embed=embed)
                else:
                    await cursor.execute("INSERT INTO vanityroles2 VALUES (?, ?, ?, ?, ?)", (0, 0, message, 0, ctx.guild.id,))
                    embed = discord.Embed(description = f"{ctx.message.author.mention}: **{message}** has been set as the vanityroles message", color = 0xA8EA7B)
                    await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @vanityroles.command()
    @commands.has_permissions(manage_guild = True)
    async def channel(self, ctx, channel: discord.TextChannel):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT channel FROM vanityroles2 WHERE guild = ?", (ctx.guild.id,))
                starData = await cursor.fetchone()
                if starData:
                    starData = starData[0]
                    if starData == channel.id:
                        embed = discord.Embed(description = f"{ctx.message.author.mention}: **{channel.mention}** is already set", color = 0x2F3136)
                        return await ctx.reply(embed=embed)
                    await cursor.execute("UPDATE vanityroles2 SET channel = ? WHERE guild = ?", (channel.id, ctx.guild.id,))
                    embed = discord.Embed(description = f"{ctx.message.author.mention}: **{channel.mention}** has been set as the vanityroles channel", color = 0xA8EA7B)
                    await ctx.reply(embed=embed)
                else:
                    await cursor.execute("INSERT INTO vanityroles2 VALUES (?, ?, ?, ?, ?)", (0, 0, 0, channel.id, ctx.guild.id,))
                    embed = discord.Embed(description = f"{ctx.message.author.mention}: **{channel.mention}** has been set as the vanityroles channel", color = 0xA8EA7B)
                    await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @vanityroles.command()
    @commands.has_permissions(manage_guild = True)
    async def role(self, ctx, *, role: discord.Role):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT role FROM vanityroles2 WHERE guild = ?", (ctx.guild.id,))
                starData = await cursor.fetchone()
                if starData:
                    starData = starData[0]
                    if starData == role.id:
                        embed = discord.Embed(description = f"{ctx.message.author.mention}: **{role.mention}** is already set as the vanityroles reward role", color = 0x2F3136)
                        return await ctx.reply(embed=embed)
                    await cursor.execute("UPDATE vanityroles2 SET role = ? WHERE guild = ?", (role.id, ctx.guild.id,))
                    embed = discord.Embed(description = f"{ctx.message.author.mention}: **{role.mention}** has been set as the vanityroles reward role", color = 0xA8EA7B)
                    await ctx.reply(embed=embed)
                else:
                    await cursor.execute("INSERT INTO vanityroles2 VALUES (?, ?, ?, ?)", (0, 0, 0, role.id, ctx.guild.id,))
                    embed = discord.Embed(description = f"{ctx.message.author.mention}: **{role.mention}** has been set as the vanityroles reward role", color = 0xA8EA7B)
                    await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)



    @tasks.loop(seconds = 2)
    async def statusCheck(self, member):
        async with self.bot.db.cursor() as cursor:
            try:
                await cursor.execute("SELECT vanity, role, message, channel FROM vanityroles2 WHERE guild = ?", (member.guild.id,))
                starData = await cursor.fetchone()
                if starData:
                    status_keyword = starData[0]
                    guild = member.guild
                    role = discord.utils.get(guild.roles, id=starData[1])
                    channel = self.bot.get_channel(starData[3])

                    for member in guild.members:
                        if status_keyword in str(member.activity) and not role in member.roles:
                            try: 
                                await member.add_roles(role)
                                embed = discord.Embed(
                                    color=0x2F3136,
                                    description=starData[2],
                                    timestamp=ctx.message.created_at)   

                                embed.set_author(name=member, icon_url=member.avatar)   
                                await channel.send(embed=embed) 
                            except Exception as f:
                                print(f)
                        elif status_keyword not in str(member.activity) and role in member.roles:
                            try:
                                await member.remove_roles(role)
                            except Exception as e:
                                print(e)
            except Exception as f:
                await ctx.send(f)


async def setup(bot):
    await bot.add_cog(vanityroles(bot))