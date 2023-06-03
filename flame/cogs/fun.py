import http
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

from io import BytesIO
from asyncio import sleep
from discord.ext import commands, tasks
from discord.ui import Button, View
from giphy_client.rest import ApiException



class manipulation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ses = bot.aiohttp_session
        self.dag_token = os.getenv("DAGPI")
        self.deep_ai = os.getenv("DEEP_AI")
        self.radi_api = os.getenv("RADI_API")
emails = ["bigjohnny", "pizzaboy123", "baljeetsingh", "kennedycunningham1873", "georgewilliamthe7th", "papalovecows"]
passwords = ["qwerty123", "adhuawgdad", "abcdefg", "yomommaxdhaha", "pablogamerboyxx"]
randomWord = ["yes", "fat", "ugly", "ok", "dude", "bro", "no", "LOL", "LMAO", "LMFAO", "gang", "Chef Keith Sosa"]



start_time = time.time()

def format_date(dt:datetime.datetime):
    if dt is None:
        return 'N/A'
    return f'<t:{int(dt.timestamp())}>'

class fun(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.launch_time = datetime.datetime.utcnow()

#------------------------------------------------------------------------8BALL------------------------------------------------------------------------#

    @commands.command(aliases=['8ball', '8b'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def question(self, ctx, *, question):

        responses = ["definitely", "maybe","yes", "no", "as i see it, yes", "factual", "as i see it, no", "idk", "Ok", "Due to your nationality being Bosnian, I cannot answer the question you just asked me.", "🤓", "Fk dem culturally component nkkas onb they is not gng blud 💯🙅‍♂️🤦🏽"]
        embed = discord.Embed(color = 0xffffff)
        embed.add_field(name = "Question", value = f"{question}")
        embed.add_field(name = "Answer", value = f"{random.choice(responses)}")
        await ctx.reply(embed=embed)


#------------------------------------------------------------------------BIBLE VERSE------------------------------------------------------------------------#
    @commands.command(help="returns a random bible verse", description="fun")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def bible(self, ctx): 
     async with aiohttp.ClientSession() as cs:
      async with cs.get("https://labs.bible.org/api/?passage=random&type=json") as r:
       byte = await r.read()
       data = str(byte, 'utf-8')
       data = data.replace("[", "").replace("]", "")
       bible = json.loads(data) 
       embed = discord.Embed(color=Colors.default, description=bible["text"]).set_author(name="{} {}:{}".format(bible["bookname"], bible["chapter"], bible["verse"]), icon_url="https://imgs.search.brave.com/gQ1kfK0nmHlQe2XrFIoLH9vtFloO3HRTDaCwY5oc0Ow/rs:fit:1200:960:1/g:ce/aHR0cDovL3d3dy5w/dWJsaWNkb21haW5w/aWN0dXJlcy5uZXQv/cGljdHVyZXMvMTAw/MDAvdmVsa2EvNzU3/LTEyMzI5MDY0MTlC/MkdwLmpwZw") 
       await ctx.reply(embed=embed, mention_author=False)

#------------------------------------------------------------------------GAY------------------------------------------------------------------------#

    @commands.command(name = "gayrate", description = "shows how gay you are",aliases = ['gr', 'gay'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def gayrate(self, ctx):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You are {random.randrange(101)}% gay {member.mention}")

#------------------------------------------------------------------------COOL------------------------------------------------------------------------#

    @commands.command(aliases = ['cr', 'cool'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coolrate(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You are {random.randrange(101)}% cool {member.mention}")

#------------------------------------------------------------------------PPSIZE------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pp(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"Your pp is {random.randrange(11)} inches {member.mention}")

#------------------------------------------------------------------------CUTE------------------------------------------------------------------------#

    @commands.command(aliases = ['cute'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cuterate(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You are {random.randrange(101)}% cute {member.mention}")

#------------------------------------------------------------------------PUNCH------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def punch(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} punches themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} punches {member.mention}")

#------------------------------------------------------------------------KISS------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kiss(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} kisses themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} kisses {member.mention}")

#------------------------------------------------------------------------LICK------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lick(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} licks themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} licks {member.mention}")

#------------------------------------------------------------------------HUG------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hug(self, ctx, member: discord.Member):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} hugs themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} hugs {member.mention}")

#------------------------------------------------------------------------BITE------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bite(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} bites themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} bites {member.mention}")

#------------------------------------------------------------------------PET------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pat(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} pats themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} pats {member.mention}")

#------------------------------------------------------------------------BITCHES------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bitches(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"you get {random.randrange(21)} bitches {member.mention}")

#------------------------------------------------------------------------HORNY------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def horny(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You are {random.randrange(101)}% horny {member.mention}")

#------------------------------------------------------------------------TICKLE------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def tickle(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} tickle themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} tickle {member.mention}")

#------------------------------------------------------------------------WEIGHT------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fatrate(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You weigh {random.randrange(301)} kg {member.mention}")

#------------------------------------------------------------------------IQ------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def iq(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You have an IQ of {random.randrange(200)} {member.mention}")

#------------------------------------------------------------------------EMOJIFY------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def emojify(self, ctx, *,text):
        emojis = []
        for s in text:
            if s.isdecimal():
                num2emo = {'0':'zero','1':'one','2':'two','3':'three','4':'four','5':'five','6':'six','7':'seven','8':'eight','9':'nine'}
                emojis.append(f':{num2emo.get(s)}:')
            elif s.isalpha():
                emojis.append(f':regional_indicator_{s}:')
            else:
                emojis.append(s)
        await ctx.reply(''.join(emojis))

#------------------------------------------------------------------------COINFLIP------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coinflip(self, ctx):
        choices = ['heads', 'tails']
        rancoin = random.choice(choices)
        await ctx.reply(rancoin)

#------------------------------------------------------------------------SUS------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sus(self, ctx):
        if member == None:
            member = ctx.author

        await ctx.reply(f"You are {random.randrange(101)}% sus 😳 {member.mention}")


#------------------------------------------------------------------------FUCK------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fuck(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
            return await ctx.reply(f"mention someone to fuck them loser")


        await ctx.reply(f"**{ctx.author.name}** fucks **{member.name}** 🍆🍑")

#------------------------------------------------------------------------HACK------------------------------------------------------------------------#

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hack(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
            return await ctx.reply(f"mention a user to hack them")


        message = await ctx.reply(f"hacking {member.mention}")
        await asyncio.sleep(1)

        await message.edit(content = f"finding user's ip address")
        await asyncio.sleep(3)

        await message.edit(content = f"ip address found: 127.0.0.1:8000")
        await asyncio.sleep(3)

        await message.edit(content = f"finding discord login (bypassed 2fa)")
        await asyncio.sleep(3)

        await message.edit(content = f"found: email: `{random.choice(emails)}@gmail.com` password: `{random.choice(passwords)}`")
        await asyncio.sleep(3)

        await message.edit(content = f"finding most common word")
        await asyncio.sleep(3)

        await message.edit(content = f"most common word: {random.choice(randomWord)}")
        await asyncio.sleep(3)

        await message.edit(content = f"stealing user's nitro and payment methods")
        await asyncio.sleep(3)

        await message.edit(content = f"selling user's data on the very spooky dark web")
        await asyncio.sleep(3)

        await message.edit(content = f"reporting user's account for breaking tos")
        await asyncio.sleep(3)

        await message.edit(content = f"finished hacking {member.mention} 😈")
        
#------------------------------------------------------------------------USERNAME------------------------------------------------------------------------#

    @commands.command(name="username")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator = True)
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

#------------------------------------------------------------------------AVATARCHANGE------------------------------------------------------------------------#

    @commands.command(name="avatarchange")
    @commands.has_permissions(administrator = True)
    async def change_avatar(self, ctx, url: str = None):
        """ Change avatar. """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            await ctx.send("You need to either provide an image URL or upload one with the command")

async def setup(bot):
    await bot.add_cog(fun(bot))