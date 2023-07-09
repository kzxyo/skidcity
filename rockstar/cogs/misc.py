import discord, aiohttp, button_paginator as pg, datetime, time
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote
from discord.ui import Button, Select, View

start = time.time()


class misc(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
# Latency Command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        e = discord.Embed(color=hex.normal, description=f"Latency: **`{round(self.bot.latency * 1000)}ms`**")
        await ctx.reply(embed=e, mention_author=False)
        
# Invite Command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        embed = discord.Embed(colour=hex.normal, description=f"[**Invite Rockstar**](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar) 
        await ctx.reply(embed=embed)
        
# Quickpoll Command

    @commands.command(aliases=['poll'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def quickpoll(self, ctx, *, text = None):
        if text == None:
            embed = discord.Embed(colour=hex.normal, description=f"**{emote.warning} {ctx.author.mention}: Usage: ,quickpoll [question]**")
            await ctx.send(embed=embed)
            return
        p = discord.Embed(description=f"{text}", color=hex.normal)
        p.set_author(name=f"{ctx.author.display_name}#{ctx.author.discriminator}'s poll", icon_url=f"{ctx.author.avatar}", url=f"https://discord.com/users/{ctx.author.id}")
        p = await ctx.send(embed=p)
        await p.add_reaction(f"👍")
        await p.add_reaction(f"👎")
        
# Credits Command

    @commands.command(aliases=['founded'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def credits(self, ctx):
        embed = discord.Embed(colour=hex.normal, description=f"**Developer: [indent#0001](https://discord.com/users/983815296760549426)**\n**Owners: [dp#0001](https://discord.com/users/723776809312845824), [rot#0001](https://discord.com/users/1003027555747635353)**")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar)
        support = Button(label="Support", url=f"https://discord.gg/CM8cGEGy")
        invite = Button(label="Invite", url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands")
        view = View()
        view.add_item(support)
        view.add_item(invite)
        await ctx.reply(embed=embed, view=view)
        
    @commands.command(aliases=['userl', 'users'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userlist(self, ctx: commands.Context):
            page=0
            count=1
            length=0
            mes = ""
            number = []
            messages = []
            for member in ctx.guild.members:
              mes = f"{mes}`{count}` {member.mention} - `{member.id}`\n"
              count+=1
              length+=1
              if length == 15:
               messages.append(mes)
               number.append(discord.Embed(color=hex.normal, title=f"members in {ctx.guild.name} ({len(ctx.guild.members)})", description=messages[page]))
               page+=1
               mes = ""
               length=0
            messages.append(mes)
            number.append(discord.Embed(color=hex.normal, title=f"members in {ctx.guild.name} [{len(ctx.guild.members)}]", description=messages[page]))
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
            paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
            paginator.add_button('next', emoji="<:right:1018156484170883154>")
            await paginator.start()
            
    @commands.command(aliases=['botl', 'bots'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botlist(self, ctx: commands.Context):
            page=0
            count=1
            length=0
            mes = ""
            number = []
            messages = []
            for member in [member for member in ctx.guild.members if member.bot]:
              mes = f"{mes}`{count}` {member.mention} - `{member.id}`\n"
              count+=1
              length+=1
              if length == 15:
               messages.append(mes)
               number.append(discord.Embed(color=hex.normal, title=f"bots in {ctx.guild.name} ({len([m for m in ctx.guild.members if m.bot])})", description=messages[page]))
               page+=1
               mes = ""
               length=0
            messages.append(mes)
            number.append(discord.Embed(color=hex.normal, title=f"bots in {ctx.guild.name} ({len([m for m in ctx.guild.members if m.bot])})", description=messages[page]))
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
            paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
            paginator.add_button('next', emoji="<:right:1018156484170883154>")
            await paginator.start()
        
async def setup(bot) -> None:
    await bot.add_cog(misc(bot))