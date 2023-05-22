import os
import re
import ast
import json
import time
import random
import urllib
import discord
import inspect
import asyncio
import aiohttp
import datetime
import requests
import giphy_client
import button_paginator as pg
from PIL import Image, ImageFilter
from urllib.request import Request, urlopen

from io import BytesIO
from asyncio import sleep
from discord.ext import commands, tasks
from discord.ui import Button, View
from giphy_client.rest import ApiException

def is_server_owner(ctx):
    return ctx.message.author.id == ctx.guild.owner.id

class antinuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS antinukewhitelisted (user INTEGER, guild INTEGER)")
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
      with open('whitelisted.json') as f:
        whitelisted = json.load(f)
      async for i in channel.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.channel_create):
          if str(i.user.id) in whitelisted[str(channel.guild.id)]:
            return
          

          await channel.guild.kick(i.user, reason="Anti-Nuke: Creating Channels")
          await i.target.delete(reason=f"wonder antinuke")
          await i.target.delete(reason=f"wonder antinuke")
          return
        
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
      with open('whitelisted.json') as f:
        whitelisted = json.load(f)
      async for i in channel.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.channel_delete):
          if str(i.user.id) in whitelisted[str(channel.guild.id)]:
            return
          await channel.guild.kick(i.user, reason="wonder antinuke")
          return

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
      with open('whitelisted.json') as f:
        whitelisted = json.load(f)
      async for i in guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.ban):
      
          if str(i.user.id) in whitelisted[str(guild.id)]:
            return
    
          await guild.ban(i.user, reason="wonder antinuke")
          await guild.kick(i.user, reason="wonder antinuke")
          return

    @commands.Cog.listener()
    async def on_member_remove(self, member):
      with open('whitelisted.json') as f:
        whitelisted = json.load(f)
      async for i in member.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.kick):
      
          if str(i.user.id) in whitelisted[str(i.guild.id)]:
            return
          if i.target.id == member.id:
             await i.user.kick()
             return

    @commands.Cog.listener()
    async def on_member_join(self, member):
      with open('whitelisted.json') as f:
        whitelisted = json.load(f)
      async for i in member.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.bot_add):
      
          if str(i.user.id) in whitelisted[str(member.guild.id)]:
            return
          
          if member.bot:
             await member.ban(reason="wonder antinuke")
             await i.user.kick(reason="wonder antinuke")
             return


    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
      with open('whitelisted.json') as f:
        whitelisted = json.load(f)
      async for i in role.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.role_create):
        if i.user.bot:
            return
      
        if str(i.user.id) in whitelisted[str(role.guild.id)]:
            return
    
        await role.guild.kick(i.user, reason="wonder antinuke")
        await i.target.delete()
        return
        
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
      with open('whitelisted.json') as f:
        whitelisted = json.load(f)
      async for i in role.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.role_delete):
          if i.user.bot:
              return
      
          if str(i.user.id) in whitelisted[str(role.guild.id)]:
              return
    
          await role.guild.kick(i.user, reason="wonder antinuke")
          await i.target.clone()
          return

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
      with open('whitelisted.json') as f:
        whitelisted = json.load(f)
      async for i in after.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.role_update):
      
          if str(i.user.id) in whitelisted[str(after.guild.id)]:
            return

          if not before.permissions.ban_members and after.permissions.ban_members:
                await after.guild.kick(i.user, reason=f"wonder antinuke")
          permissions = after.permissions
          permissions.update(ban_members=False)
          await after.edit(permissions=permissions)

          if not before.permissions.administrator and after.permissions.administrator:
                await after.guild.kick(i.user, reason=f"wonder antinuke")
          permissions = after.permissions
          permissions.update(administrator=False)
          await after.edit(permissions=permissions)

          if not before.permissions.kick_members and after.permissions.kick_members:
                await after.guild.kick(i.user, reason=f"wonder antinuke")
          permissions = after.permissions
          permissions.update(kick_members=False)
          await after.edit(permissions=permissions)

          if not before.permissions.manage_channels and after.permissions.manage_channels:
                await after.guild.kick(i.user, reason=f"wonder antinuke")
          permissions = after.permissions
          permissions.update(manage_guild=False)
          await after.edit(permissions=permissions)
          return


    @commands.command(aliases = ['wld'], hidden=True)
    async def whitelisted(self, ctx):
        icon = ''
        embed = discord.Embed(description="")
        embed.set_author(name = f"Whitelisted users in {ctx.guild.name}", icon_url = ctx.guild.icon.url)

        with open ('whitelisted.json', 'r') as i:
                whitelisted = json.load(i)
        try:
            for u in whitelisted[str(ctx.guild.id)]:
              embed.description += f"<@{u}>\n"
            await ctx.reply(embed = embed)
        except KeyError:
            await ctx.reply("no whitelisted users in this server")
            

    @commands.command(aliases = ['wl'], hidden=True)
    @commands.check(is_server_owner)
    async def whitelist(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.reply("specify a user to whitelist")
            return
        with open ('whitelisted.json', 'r') as f:
            whitelisted = json.load(f)


        if str(ctx.guild.id) not in whitelisted:
            whitelisted[str(ctx.guild.id)] = []
        else:
            if str(user.id) not in whitelisted[str(ctx.guild.id)]:
                whitelisted[str(ctx.guild.id)].append(str(user.id))
            else:
                await ctx.reply(f"{user.mention} is already whitelisted")
                return



        with open ('whitelisted.json', 'w') as f: 
            json.dump(whitelisted, f, indent=4)
        
        await ctx.reply(f"{user.mention} has been whitelisted")
    @whitelist.error
    async def whitelist_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("only the server owner can use this command")

    @commands.command(aliases = ['uwl'], hidden=True)
    @commands.check(is_server_owner)
    async def unwhitelist(self, ctx, user: discord.User = None):
        if user is None:
            await ctx.reply("specify a user to unwhitelist")
            return
        with open ('whitelisted.json', 'r') as f:
            whitelisted = json.load(f)
        try:
            if str(user.id) in whitelisted[str(ctx.guild.id)]:
                whitelisted[str(ctx.guild.id)].remove(str(user.id))
            
                with open ('whitelisted.json', 'w') as f: 
                    json.dump(whitelisted, f, indent=4)
            
            await ctx.reply(f"{user.mention} has been unwhitelisted")
        except KeyError:
            await ctx.reply(f"{user.mention} is not whitelisted")
    @unwhitelist.error
    async def unwhitelist_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("only the server owner can use this command")
async def setup(bot):
    await bot.add_cog(antinuke(bot))