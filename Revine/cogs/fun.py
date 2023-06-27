# This source code is 100% original, any contents will be credited in revine's credits command. Created by fsb#1337 & report#0001

import discord, datetime, time, asyncio, random, requests, os
from discord.ext import commands
from typing import Union
from discord.ui import View, Button
from classes import Emotes, Colors, API_Keys

start_time = time.time()

async def get(session: object, url: object) -> object:
    async with session.get(url) as response:
        return await response.text()


class fun(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

# --------------------------------------------------------------------------------------- Cat command

    @commands.command(aliases=["c"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cat(self, ctx):
        response = requests.get("https://aws.random.cat/meow")
        data = response.json()
        e = discord.Embed(color=Colors.normal)
        e.set_image(url=data["file"])
        e.set_footer(text="category: fun・revine ©️ 2023")
        await ctx.send(embed=e)
    
# --------------------------------------------------------------------------------------- Dog command

    @commands.command(aliases=["d"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dog(self, ctx):
        response = requests.get("https://random.dog/woof.json")
        data = response.json()
        d = discord.Embed(color=Colors.normal)
        d.set_image(url=data["url"])
        d.set_footer(text="category: fun・revine ©️ 2023")
        await ctx.send(embed=d)

# --------------------------------------------------------------------------------------- Duck command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def duck(self, ctx):
        response = requests.get("https://random-d.uk/api/v2/random")
        data = response.json()
        duck = discord.Embed(color=Colors.normal)
        duck.set_image(url=data["url"])
        duck.set_footer(text="category: fun・revine ©️ 2023")
        await ctx.send(embed=duck)

# --------------------------------------------------------------------------------------- Slap command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slap(self, ctx, *, member:discord.Member = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You must mention someone", color=Colors.normal)
            await ctx.reply(embed=embed)
            return
        response = requests.get("https://api.waifu.pics/sfw/slap")
        data = response.json()
        s = discord.Embed(description=f"{ctx.author.mention} slaps {member.mention}", color=Colors.normal)
        s.set_footer(text="category: fun・revine ©️ 2023")
        s.set_image(url=data["url"])
        await ctx.send(embed=s)

# --------------------------------------------------------------------------------------- Fun command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hug(self, ctx, member:discord.Member = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You must mention someone", color=Colors.normal)
            await ctx.reply(embed=embed)
            return
        response = requests.get("https://api.waifu.pics/sfw/hug")
        data = response.json()
        s = discord.Embed(description=f"{ctx.author.mention} hugs {member.mention}", color=Colors.normal)
        s.set_footer(text="category: fun・revine ©️ 2023")
        s.set_image(url=data["url"])
        await ctx.send(embed=s)

    # --------------------------------------------------------------------------------------- Kill command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kill(self, ctx, member:discord.Member = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You must mention someone", color=Colors.normal)
            await ctx.reply(embed=embed)
            return
        response = requests.get("https://api.waifu.pics/sfw/kill")
        data = response.json()
        s = discord.Embed(description=f"{ctx.author.mention} kills {member.mention}.", color=Colors.normal)
        s.set_footer(text="category: fun・revine ©️ 2023")
        s.set_image(url=data["url"])
        await ctx.send(embed=s)

# --------------------------------------------------------------------------------------- Cry command

    @commands.command(aliases=["cries"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cry(self, ctx):
        response = requests.get("https://api.waifu.pics/sfw/cry")
        data = response.json()
        c = discord.Embed(description=f"{ctx.author.mention} cries.", color=Colors.normal)
        c.set_footer(text="category: fun・revine ©️ 2023")
        c.set_image(url=data["url"])
        await ctx.send(embed=c)

# --------------------------------------------------------------------------------------- Smile command

    @commands.command(aliases=["smiles"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def smile(self, ctx):
        response = requests.get("https://api.waifu.pics/sfw/smile")
        data = response.json()
        c = discord.Embed(description=f"{ctx.author.mention} smiles.", color=Colors.normal)
        c.set_footer(text="category: fun・revine ©️ 2023")
        c.set_image(url=data["url"])
        await ctx.send(embed=c)

# --------------------------------------------------------------------------------------- Kiss command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kiss(self, ctx, member:discord.Member = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You must mention someone", color=Colors.normal)
            await ctx.reply(embed=embed)
            return
        response = requests.get("https://api.waifu.pics/sfw/kiss")
        data = response.json()
        kiss = discord.Embed(description=f"{ctx.author.mention} kissed {member.mention}.", color=Colors.normal)
        kiss.set_footer(text="category: fun・revine ©️ 2023")
        kiss.set_image(url=data["url"])
        await ctx.send(embed=kiss)


# --------------------------------------------------------------------------------------- 8ball command

    @commands.command(aliases=['8ball'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def eb(self, ctx, *, question = None):
        if question == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You must type a question", color=Colors.normal)
            await ctx.send(embed=embed)
            return
        responses = [
            "It is certain.","It is decidedly so.","Without a doubt.","Yes - definitely.","You may rely on it.","As I see it, yes.",
            "Most likely.","Outlook good.","Yes.","Signs point to yes.","Reply hazy, try again.","Ask again later.","Better not tell you now.",
            "Cannot predict now.","Concentrate and ask again.","Don't count on it.","My reply is no.","My sources say no.","Outlook not so good.","Very doubtful."]
        eb = discord.Embed(color=Colors.normal)
        eb.add_field(name="Question:", value=f"{question}")
        eb.add_field(name="Answer:", value=f"{random.choice(responses)}")
        eb.set_author(name=f"{ctx.author.display_name}#{ctx.author.discriminator}", icon_url=f"{ctx.author.avatar}", url=f"https://discord.com/users/{ctx.author.id}")
        eb.set_footer(text="category: fun・revine ©️ 2023")
        await ctx.send(embed=eb)

    # --------------------------------------------------------------------------------------- Dick command

    @commands.command(aliases=["dick"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dicksize(self, ctx, member:discord.Member = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You must mention someone", color=Colors.normal)
            await ctx.send(embed=embed)
            return
        responses = [
            "1","2","3","4","5","6","7","8","9","10",
            "11","12","13","14","15","16","17","18","19","20",
            "21","22","23","24","25","26","26","27","28","29","30"]
        eb = discord.Embed(description=f"{member.mention}: dicksize **{random.choice(responses)}** inches" ,color=Colors.normal)
        eb.set_author(name=f"{member.display_name}#{member.discriminator}", icon_url=f"{member.avatar}", url=f"https://discord.com/users/{member.id}")
        eb.set_footer(text="category: fun・revine ©️ 2023")
        await ctx.send(embed=eb)

    # --------------------------------------------------------------------------------------- Advice Command
    
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def advice(self, ctx):
        response = requests.get("https://luminabot.xyz/api/json/advice")
        data = response.json()
        advice = discord.Embed(description=f"**" + data["advice"] + "**", color=Colors.normal)
        advice.set_author(name="Revine's Advice", icon_url=f"{self.bot.user.avatar.url}", url="https://discord.gg/revine")
        advice.set_footer(text="category: fun・revine ©️ 2023")
        await ctx.send(embed=advice)

async def setup(bot) -> None:
    await bot.add_cog(fun(bot))