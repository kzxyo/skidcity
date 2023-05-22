import discord, requests, json, aiohttp, random, asyncio
from discord import app_commands
from discord import Member
from discord.ext import commands
from utils.classes import colors, emojis
from cogs.events import commandhelp, blacklist


class roleplay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(help="cuddle with someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def cuddle(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=colors.default, title="`syntax: cuddle <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/cuddle")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*aww how cute! {ctx.author.mention} is cuddling with {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)
          
    @commands.command(help="slap someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def slap(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=colors.default, title="`syntax: slap <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/slap")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*{ctx.author.mention} slapped {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="pat someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def pat(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=colors.default, title="`syntax: pat <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/pat")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*aww how cute! {ctx.author.mention} pat {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="hug someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def hug(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=colors.default, title="`syntax: hug <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/hug")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*aww how cute! {ctx.author.mention} hugged {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="kiss someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def kiss(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=colors.default, title="`syntax: kiss <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/kiss")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*aww how cute! {ctx.author.mention} kissed {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="feed someone?....", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def feed(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=colors.default, title="`syntax: feed <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/feed")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*aww how cute! {ctx.author.mention} is feeding {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="tickle someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def tickle(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=colors.default, title="`syntax: tickle <user>`")
            await ctx.send(embed=embed)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/tickle")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*aw! look at the flirts! {ctx.author.mention} is tickling {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="cry", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def cry(self, ctx, user: discord.Member=None):
            r = requests.get("http://api.nekos.fun:8080/api/cry")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*aww! {ctx.author.mention} is crying")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="funny", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def laugh(self, ctx, user: discord.Member=None):
            r = requests.get("http://api.nekos.fun:8080/api/laugh")
            res = r.json()
            em = discord.Embed(color=colors.default)
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="senpai notice meeeee!", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def poke(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=colors.default, title="`syntax: poke <user>`")
            await ctx.send(embed=embed)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/poke")
            res = r.json()
            em = discord.Embed(color=colors.default, description=f"*aw how cute! {ctx.author.mention} is poking {user.mention}!*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="b-baka!!!", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def baka(self, ctx, user: discord.Member=None):
            r = requests.get("http://api.nekos.fun:8080/api/baka")
            res = r.json()
            em = discord.Embed(color=colors.default)
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)
  
async def setup(bot):
    await bot.add_cog(roleplay(bot))