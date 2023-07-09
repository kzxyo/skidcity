import discord, aiohttp, button_paginator as pg, json
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote

class prefix(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def selfprefix(self, ctx, prefix = "."):
        with open('selfprefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(ctx.author.id)] = prefix
        with open('selfprefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=2)
        if prefix == ".":
            changed = discord.Embed(description=f"**I've changed your self prefix back to Default.**", colour=hex.normal)
            await ctx.reply(embed=changed)
            return
        changed = discord.Embed(description=f"**I've changed your self prefix to: `{prefix}`**", colour=hex.normal)
        await ctx.reply(embed=changed)
        
        
    @commands.Cog.listener()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def on_message(self, message: discord.Message, sp = None):
        if message.content == f"<@{self.bot.user.id}>":
            with open('selfprefixes.json', 'r') as f:
                data = json.load(f)
                if str(message.author.id) in data:
                    sp = data[str(message.author.id)]
                if sp == None:
                    embed = discord.Embed(description=f"**Rockstar's Default Prefix:** `.`", colour=hex.normal)
                    await message.reply(embed=embed)
                    return
            embed = discord.Embed(description=f"**Selfprefix:** `{sp}`", colour=hex.normal)
            await message.reply(embed=embed)
            
            
    @commands.command(aliases=['commandprefix'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def prefix(self, message: discord.Message, sp = None):
            with open('selfprefixes.json', 'r') as f:
                data = json.load(f)
                if str(message.author.id) in data:
                    sp = data[str(message.author.id)]
                if sp == None:
                    embed = discord.Embed(description=f"**Rockstar's Default Prefix:** `.`", colour=hex.normal)
                    await message.reply(embed=embed)
                if sp == ".":
                    embed = discord.Embed(description=f"**Rockstar's Default Prefix:** `.`", colour=hex.normal)
                    await message.reply(embed=embed)
                    return
            embed = discord.Embed(description=f"**Selfprefix:** `{sp}`", colour=hex.normal)
            await message.reply(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(prefix(bot))