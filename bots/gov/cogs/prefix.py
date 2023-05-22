from types import NoneType
import discord, json, button_paginator as pg
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
from utility import Emotes, Colours

class change(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def selfprefix(self, ctx, prefix = ","):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(ctx.author.id)] = prefix
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=2)
        if prefix == ",":
            changed = discord.Embed(description=f"**{Emotes.tickemote} I've changed your personal prefix back to Default.**", colour=Colours.standard)
            await ctx.reply(embed=changed)
            return
        changed = discord.Embed(description=f"**{Emotes.tickemote} I've changed your personal prefix to: `{prefix}`**", colour=Colours.standard)
        await ctx.reply(embed=changed)
        
        
    @commands.Cog.listener()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def on_message(self, message: discord.Message, sp = None):
        if message.content == f"<@{self.bot.user.id}>":
            with open('prefixes.json', 'r') as f:
                data = json.load(f)
                if str(message.author.id) in data:
                    sp = data[str(message.author.id)]
                if sp == None:
                    embed = discord.Embed(description=f"{Emotes.settingsemote} **Gov's Default Prefix:** `,`", colour=Colours.standard)
                    await message.reply(embed=embed)
                    return
            embed = discord.Embed(description=f"{Emotes.settingsemote} **Selfprefix:** `{sp}`", colour=Colours.standard)
            await message.reply(embed=embed)
            
            
    @commands.command(aliases=['commandprefix'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def prefix(self, message: discord.Message, sp = None):
            with open('prefixes.json', 'r') as f:
                data = json.load(f)
                if str(message.author.id) in data:
                    sp = data[str(message.author.id)]
                if sp == None:
                    embed = discord.Embed(description=f"{Emotes.settingsemote} **Gov's Default Prefix:** `,`", colour=Colours.standard)
                    await message.reply(embed=embed)
                if sp == ",":
                    embed = discord.Embed(description=f"{Emotes.settingsemote} **Gov's Default Prefix:** `,`", colour=Colours.standard)
                    await message.reply(embed=embed)
                    return
            embed = discord.Embed(description=f"{Emotes.settingsemote} **Selfprefix:** `{sp}`", colour=Colours.standard)
            await message.reply(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(change(bot))