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


def get_parts(params):
    params=params.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]

async def to_object(params):

    x={}
    fields=[]
    content=None
    view=discord.ui.View()

    for part in get_parts(params):
        
        if part.startswith('content:'):
            content=part[len('content:'):]
          
        if part.startswith('title:'):
            x['title']=part[len('title:'):]
        
        if part.startswith('description:'):
            x['description']=part[len('description:'):]

        if part.startswith('footer:'):
            x['footer']=part[len('footer:'):]

        if part.startswith('color:'):
            try:
                x['color']=int(part[len('color:'):].strip('#').strip(), 16)
            except:
                x['color']=0x2f3136

        if part.startswith('image:'):
            x['image']={'url': part[len('description:'):]}

        if part.startswith('thumbnail:'):
            x['thumbnail']={'url': part[len('thumbnail:'):]}
        
        if part.startswith('author:'):
            z=part[len('author:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            try:
                url=z[2] if z[2] else None
            except:
                url=None

            x['author']={'name': name}
            if icon_url:
                x['author']['icon_url']=icon_url
            if url:
                x['author']['url']=url

        if part.startswith('field:'):
            z=part[len('field:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                value=z[1] if z[1] else None
            except:
                value=None
            try:
                inline=z[2] if z[2] else True
            except:
                inline=True

            if isinstance(inline, str):
                if inline == 'true':
                    inline=True

                elif inline == 'false':
                    inline=False

            fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z=part[len('footer:'):].split(' && ')
            try:
                text=z[0] if z[0] else None
            except:
                text=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            x['footer']={'text': text}
            if icon_url:
                x['footer']['icon_url']=icon_url
                
        if part.startswith('button:'):
            z=part[len('button:'):].split(' && ')
            try:
                label=z[0] if z[0] else None
            except:
                label='no label'
            try:
                url=z[1] if z[1] else None
            except:
                url='https://none.none'
            try:
                emoji=z[2] if z[2] else None
            except:
                emoji=None
                
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=label, url=url, emoji=emoji))
            
    if not x: embed=None
    else:
        x['fields']=fields
        embed=discord.Embed.from_dict(x)
    return content, embed, view


async def embed_replacement(user, params):

    if '{user}' in params:
        params=params.replace('{user}', user)
    if '{user.mention}' in params:
        params=params.replace('{user.mention}', user.mention)
    if '{user.name}' in params:
        params=params.replace('{user.name}', user.name)
    if '{user.avatar}' in params:
        params=params.replace('{user.avatar}', user.display_avatar.url)
    if '{user.joined_at}' in params:
        params=params.replace('{user.joined_at}', discord.utils.format_dt(user.joined_at, style='R'))
    if '{user.created_at}' in params:
        params=params.replace('{user.created_at}', discord.utils.format_dt(user.created_at, style='R'))
    if '{user.discriminator}' in params:
        params=params.replace('{user.discriminator}', user.discriminator)
    if '{guild.name}' in params:
        params=params.replace('{guild.name}', user.guild.name)
    if '{guild.count}' in params:
        params=params.replace('{guild.count}', str(user.guild.member_count))
    if '{guild.count.format}' in params:
        params=params.replace('{guild.count.format}', ordinal(len(user.guild.members)))
    if '{guild.id}' in params:
        params=params.replace('{guild.id}', user.guild.id)
    if '{guild.created_at}' in params:
        params=params.replace('{guild.created_at}', discord.utils.format_dt(user.guild.created_at, style='R'))
    if '{guild.boost_count}' in params:
        params=params.replace('{guild.boost_count}', str(user.guild.premium_subscription_count))
    if '{guild.booster_count}' in params:
        params=params.replace('{guild.booster_count}', str(len(user.guild.premium_subscribers)))
    if '{guild.boost_count.format}' in params:
        params=params.replace('{guild.boost_count.format}', ordinal(str(len(user.guild.premium_subscriber_count))))
    if '{guild.booster_count.format}' in params:
        params=params.replace('{guild.booster_count.format}', ordinal(str(len(user.guild.premium_subscriber_count))))
    if '{guild.boost_tier}' in params:
        params=params.replace('{guild.boost_tier}', str(user.guild.premium_tier))
    if '{guild.icon}' in params:
        if user.guild.icon:
            params=params.replace('{guild.icon}', user.guild.icon.url)
        else:
            params=params.replace('{guild.icon}', '')
    return params

class autoresponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS autoresponderconfiglol (trigger TEXT, response TEXT, guild INTEGER)")
        await self.bot.db.commit()
    
    @commands.group(aliases = ['ar'])
    async def autoresponder(self, ctx):
        if ctx.invoked_subcommand is None:
            dev = self.bot.get_user(565627105552105507)
            return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")
            
    @autoresponder.command()
    @commands.has_permissions(manage_guild = True)
    async def add(self, ctx, trigger, *, reaction):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO autoresponderconfiglol VALUES (?, ?, ?)", (trigger, reaction, ctx.guild.id,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: Successfully created an **autoresponse** for `{trigger}`""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @autoresponder.command()
    @commands.has_permissions(manage_guild = True)
    async def clear(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autoresponderconfiglol WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: Successfully deleted **all** triggers""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @autoresponder.command(aliases = ['remove'])
    @commands.has_permissions(manage_guild = True)
    async def delete(self, ctx, *, msg):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autoresponderconfiglol WHERE guild = ? AND trigger LIKE ?", (ctx.guild.id, msg,))
            embed = discord.Embed(description = f"""<:success:1034500520926253146> {ctx.author.mention}: Successfully deleted the **autoresponse** for `{msg}`""", color = 0x2F3136)
            await ctx.reply(embed=embed)
            await self.bot.db.commit()
        except Exception as e:
            print(e)


    @autoresponder.command(aliases = ['list'])
    @commands.has_permissions(manage_guild = True)
    async def show(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT response, trigger FROM autoresponderconfiglol WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        trigger = table[1]
                        response = table[0]
                        num += 1
                        auto += f"\n`{num}` {trigger} — {response}"
                    embed = discord.Embed(description = auto, color = 0xccd7f7)
                    embed.set_author(name = "List of autoresponses", icon_url = ctx.message.author.display_avatar)
                    await ctx.reply(embed=embed)
                else:
                    embed = discord.Embed(description = f"<:warn:1028222512888291348> {ctx.message.author.mention}: No auto responder triggers have been set up", color = 0xccd7f7)
                    await ctx.reply(embed=embed)
        except Exception as e:
            print(e)


    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT response, trigger FROM autoresponderconfiglol WHERE guild = ?", (message.guild.id,))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            response = table[0]
                            trigger = table[1]
                            if message.author.bot:
                                pass
                            else:
                                if trigger.lower() in message.content.lower():
                                    x = await to_object(await embed_replacement(message.author, response))
                                    await message.channel.send(content=x[0], embed=x[1], view=x[2])

async def setup(bot):
    await bot.add_cog(autoresponder(bot))