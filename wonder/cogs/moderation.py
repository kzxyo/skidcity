import os
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


class moderation(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["nick", "changenick"])
    @commands.has_permissions(manage_nicknames = True)
    async def changenickname(self, ctx, member: discord.Member, nick):
        try:
            await member.edit(nick=nick)
            await ctx.reply(f"👍")
        except Exception as e:
            print(e)


    @commands.command(aliases = ['c', 'clear'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, num: int, user: discord.Member = None):
        if user:
            check_func = lambda msg: msg.author == user and not msg.pinned
        else:
            check_func = lambda msg: not msg.pinned
        await ctx.message.delete()
        await ctx.channel.purge(limit=num, check=check_func)

    @commands.command(aliases = ['bc', 'botclear'])
    @commands.has_permissions(manage_messages=True)
    async def botpurge(self, ctx, num: int):
        await ctx.message.delete()
        await ctx.channel.purge(limit=num, check=lambda msg: msg.author.bot)
    
    @commands.command(name = "kick",  description = "kicks a member from the guild")
    @commands.has_permissions(kick_members = True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick(self, ctx, member: discord.Member = None, *, reason = None):
        if member == None:
            member = ctx.author
            return await ctx.reply("who i smoke")


        if member == ctx.author:
            return await ctx.reply("you cant kick yourself")

        if member.top_role.position == ctx.me.top_role.position:
                return await ctx.reply("i cant ban that user")

        elif member.top_role.position > ctx.me.top_role.position:
                return await ctx.reply("i cant ban that user")

        elif member.top_role.position == ctx.author.top_role.position:
                return await ctx.reply("you cant ban that user")
                
        elif member.top_role.position > ctx.author.top_role.position:
                return await ctx.reply("you cant ban that user")
        else:
            await member.kick(reason=reason)
            await ctx.reply(f"👍")

    @commands.command(name = "ban",  description = "Bans a user from the guild", aliases = ['yeet', 'smoke'], usage = "$ban <user>")
    @commands.has_permissions(ban_members = True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ban(self, ctx, user: discord.Member = None, *, reason = None):
        if user == None:
            return await ctx.reply("who i smoke")

        if user == ctx.author:
            return await ctx.reply("you cant ban yourself")

        if user.top_role.position == ctx.me.top_role.position:
                return await ctx.reply("i cant ban that user")

        elif user.top_role.position > ctx.me.top_role.position:
                return await ctx.reply("i cant ban that user")

        elif user.top_role.position == ctx.author.top_role.position:
                return await ctx.reply("you cant ban that user")
                
        elif user.top_role.position > ctx.author.top_role.position:
                return await ctx.reply("you cant ban that user")
        else:
            await user.ban(reason=reason)
            await ctx.reply(f"👍")


    @commands.command(name = "unban",  description = "unbans a member from the guild")
    @commands.has_permissions(ban_members = True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unban(self, ctx, *, user: discord.User = None):
        if user == None:
            user = ctx.author
            return await ctx.reply("who i smoke")


        user = await self.bot.fetch_user(user.id)
        try:
            await ctx.guild.unban(user)
        
            await ctx.reply(f"👍")
        except Exception as f:
            await ctx.reply(f)
            pass


    @commands.command(aliases = ['role'])
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def addrole(self, ctx, member : discord.Member, role : discord.Role):
        try:

            if role.position == ctx.author.top_role.position:
                return await ctx.reply("you cant give that role")
                
            elif role.position > ctx.author.top_role.position:
                return await ctx.reply("you cant give that role")
            else:
                if role in member.roles:
                    await member.remove_roles(role)
                    await ctx.reply(f"👍")

                else:
                    await member.add_roles(role)
                    await ctx.reply(f"👍")
        except Exception as e:
            print(e)


    @commands.command()
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.reply(f"slowmode set to {seconds}")
        
    
async def setup(bot):
    await bot.add_cog(moderation(bot))