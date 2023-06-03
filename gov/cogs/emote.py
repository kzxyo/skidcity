from platform import python_version, python_version_tuple
import discord, requests, os, datetime, psutil, time, button_paginator as pg
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
import requests
from utility import Emotes, Colours

start_time = time.time()

class emote(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command(aliases=['add', 'addemoji', 'stealemoji', 'addemote', 'stealemote'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_emojis=True)    
    async def steal(self, ctx, emoji: discord.PartialEmoji = None, *, emojiname = None):
        if ctx.author.guild_permissions.manage_emojis == True:
            if emoji == None:
                permissions = discord.Embed(description=f"**{Emotes.warningemote} {ctx.author.mention}: You've not mentioned an emoji.**", color=Colours.standard)
                await ctx.send(embed=permissions)
                return
            if emojiname == None:
                r = requests.get(emoji.url, allow_redirects=True)
                emojiname = emoji.name
            else:
                text = emojiname.replace(" ", "_")
                r = requests.get(emoji.url, allow_redirects=True)
            if emoji.animated == True:
                open("emoji.gif", "wb").write(r.content)
                with open("emoji.gif", "rb") as f:
                    emote = await ctx.guild.create_custom_emoji(name=emoji.name, image=f.read())
                os.remove("emoji.gif")
            else:
                open("emoji.png", "wb").write(r.content)
                with open("emoji.png", "rb") as f:
                    emote = await ctx.guild.create_custom_emoji(name=emoji.name, image=f.read())
                os.remove("emoji.png")    
        emoji = discord.Embed(description=f"**{ctx.author.mention}: Added {emote} as ` {emojiname} `**", color=Colours.standard)
        await ctx.send(embed=emoji)
        
        
    @commands.command(aliases=['large', 'el'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def enlarge(self, ctx, emoji: discord.PartialEmoji = None):
        if emoji == None:
            embed = discord.Embed(description=f"**{Emotes.warningemote} {ctx.author.mention}: This command requires a custom emoji.** `,enlarge [emote]`", colour=Colours.warning)
            await ctx.reply(embed=embed)
            return
        embed = discord.Embed(colour=Colours.standard)
        embed.set_author(name=emoji.name)
        embed.set_image(url=emoji.url)
        await ctx.reply(embed=embed)
        

async def setup(bot) -> None:
    await bot.add_cog(emote(bot))