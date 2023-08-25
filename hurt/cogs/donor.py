import sqlite3
import discord
from discord.ext import commands
import requests
import string
import random


def is_donor(user_id):
    conn = sqlite3.connect("donors.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM donors WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


class donor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chatgpt_api = "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"
        self.model_engine = "text-davinci-002"
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect("donors.db")
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS donors (user_id INTEGER PRIMARY KEY)"
        )
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_ready(self):
        self.create_tables()

    @commands.command()
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def exclusive_donor_command(self, ctx):
        await ctx.send(
            "This is an exclusive donor command. Thank you for your support!"
        )

    @commands.command()
    @commands.is_owner()
    async def adddonor(self, ctx, user: discord.User):
        conn = sqlite3.connect("donors.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO donors (user_id) VALUES (?)", (user.id,))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="",
            description=f"{user.name} has been added as a donor <:add:1139300178638164018>",
            color=0xB4B4D8,
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, user: discord.User):
        conn = sqlite3.connect("donors.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM donors WHERE user_id = ?", (user.id,))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="",
            description=f"{user.name} **has been removed from donors <:minus:1139475805420924928>**",
            color=0xB4B4D8,
        )
        await ctx.send(embed=embed)

    @commands.command(
        help="Give someone a blowjob", usage="[member]", description="Roleplay"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def bj(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xB4B4D8, title="`bj <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/bj")
            res = r.json()
            em = discord.Embed(
                color=0xB4B4D8,
                description=f"*{ctx.author.mention} Gets their soul snatched by {user.mention}*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(
        description="Purges an amount of messages sent by you",
        help="Donor",
        usage="[amount]",
    )
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def selfpurge(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            await ctx.send(
                "Please provide a positive integer for the amount of messages to purge."
            )
            return

        mes = []
        async for message in ctx.channel.history():
            if len(mes) == amount + 1:
                break
            if message.author == ctx.author:
                mes.append(message)

        await ctx.channel.delete_messages(mes)

        embed = discord.Embed(
            title="",
            description=f"<:icons_clean:1139494635794878464> **Successfully self purged** {len(mes)} **messages sent by** {ctx.author.mention}",
            color=0xB4B4D8,
        )
        await ctx.send(embed=embed)

    @selfpurge.error
    async def selfpurge_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("")
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="",
                description="<:cashappc:1139473859221921844> **This command is exclusive to donors. If you'd like to become a donor and access this command, please send a donation to our CashApp at** `$hurtbot`",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed)

    @commands.command(
        description="Generate and send a random strong password to your DMs",
        help="Donor",
    )
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def genratepassword(self, ctx):
        password_length = 16
        characters = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.choice(characters) for _ in range(password_length))

        try:
            embed = discord.Embed(
                title="",
                description=f"<:icons_locked:1135871065248247838> **Here's your random strong password. Make sure to save it**\n``{password}``",
                color=0xB4B4D8,
            )
            await ctx.author.send(embed=embed)

            embed_success = discord.Embed(
                description="<:approve:1139298421371568239> **please check your dms**",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed_success)
        except discord.Forbidden:
            embed_fail = discord.Embed(
                description="<:deny:1139298463658553364> **I'm unable to send you a message please make sure i'm not blocked or ur dms are off**",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed_fail)

    @genratepassword.error
    async def generate_password_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="",
                description="<:cashappc:1139473859221921844> **This command is exclusive to donors. If you'd like to become a donor and access this command, please send a donation to our CashApp at** `$hurtbot``",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed)

    @commands.command(help="hentai", usage="", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def hentai(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`hentai <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/hentai")
            res = r.json()
            em = discord.Embed(
                color=0xB4B4D8,
                description=f"*{ctx.author.mention} says __lets roleplay__ to {user.mention} *",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @hentai.error
    async def hentai_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="",
                description="<:deny:1139298463658553364> **This command is exclusive to donors If you'd like to become a donor and access this command, please send a donation to our CashApp at** ``$hurtbot``",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed)

    @bj.error
    async def bj_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="",
                description="<:cashappc:1139473859221921844> **This command is exclusive to donors. If you'd like to become a donor and access this command, please send a donation to our CashApp at** ``$hurtbot``",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed)

    @commands.command(help="cum on people", usage="", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def nut(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xB4B4D8, title="`cum <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/cum")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*{ctx.author.mention} nuts all over {user.mention} *",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @nut.error
    async def cum_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="",
                description="<:cashappc:1139473859221921844> **This command is exclusive to donors. If you'd like to become a donor and access this command, please send a donation to our CashApp at** ``$hurtbot``",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed)

    @commands.command(help="get lewd porn lol", usage="", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def lewd(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xB4B4D8, title="`lewd <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/lewd")
            res = r.json()
            em = discord.Embed(
                color=0xB4B4D8,
                description=f"*{ctx.author.mention} here's {user.mention} if they were lewd*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @lewd.error
    async def lewd_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="",
                description="<:cashappc:1139473859221921844> **This command is exclusive to donors. If you'd like to become a donor and access this command, please send a donation to our CashApp at** ``$hurtbot``",
                color=0xFFD700,
            )
            await ctx.send(embed=embed)

    @commands.command(help="get boobs", usage="", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def boobs(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xB4B4D8, title="`boobs <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/boobs")
            res = r.json()
            em = discord.Embed(
                color=0xB4B4D8,
                description=f"*{ctx.author.mention} loves {user.mention}'s boobs*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @boobs.error
    async def boobs_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="",
                description="<:cashappc:1139473859221921844> **This command is exclusive to donors. If you'd like to become a donor and access this command, please send a donation to our CashApp at** ``$hurtbot``",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed)

    @commands.command(help="get hd porn lol", usage="", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(lambda ctx: is_donor(ctx.author.id))
    async def hd(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xB4B4D8, title="`hd <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/4k")
            res = r.json()
            em = discord.Embed(
                color=0xB4B4D8, description=f"*{ctx.author.mention} here's your porn*"
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @hd.error
    async def hd_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="",
                description="<:cashappc:1139473859221921844> **This command is exclusive to donors. If you'd like to become a donor and access this command, please send a donation to our CashApp at** ``$hurtbot``",
                color=0xB4B4D8,
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(donor(bot))
