from email import utils
import discord
import requests
import datetime
import button_paginator as pg
import random
import asyncio
import json
from discord.ui import Button, View
import time
from discord.ext import commands
from sqlalchemy import FetchedValue
from uwuipy import uwuipy
from datetime import datetime
from cogs.utilevents import blacklist
import os
import matplotlib.pyplot as plt
from io import BytesIO
from wordcloud import WordCloud
import calendar
from datetime import datetime
from .utils.util import Emojis

with open("db/config.json") as f:
    data = json.load(f)
    mongo = data["mongo"]


class fun(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(aliases=["8ball", "ask"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def question(self, ctx, *, question):
        responses = [
            "It is certain",
            "Without a doubt",
            "You may rely on it",
            "Yes definitely",
            "It is decidedly so",
            "As I see it, yes",
            "Most likely",
            "Yes",
            "Outlook good",
            "Signs point to yes",
            "Reply hazy, try again",
            "Better not tell you now",
            "Ask again later",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "Outlook not so good",
            "My sources say no",
            "Very doubtful",
            "My reply is no",
        ]
        embed = discord.Embed(
            color=0xF7F9F8,
            description=f"question: {question}\nanswer: {random.choice(responses)}",
        )
        embed.set_footer(text=f"requested by {ctx.author}")
        await ctx.reply(embed=embed)

    @commands.command()
    @blacklist()
    async def three(self, ctx):
        await ctx.reply("HOORAY! 303 CMDS Merlin and Hurt up next")

    async def cam(self, ctx):
        e = discord.Embed(description="XANO OWNS CAM", color=0xF7F9F8)
        e.set_image(
            url="https://media.discordapp.net/attachments/1082003523060912138/1084619540501110805/image.png"
        )
        e.set_footer(text="made 3/12/23 / 7:30PM")
        await ctx.send(embed=e)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, commands.BucketType.default)
    @blacklist()
    async def pack(self, ctx, user: discord.Member = commands.Author):
        if user == ctx.author:
            embed = discord.Embed(
                color=0xF7F9F8,
                description="**You fr wanna pack yourself??**",
                timestamp=datetime.now(),
            )
            embed.set_footer(
                text="dont do it my boy",
                icon_url=None,
            )
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

            return await ctx.reply(embed=embed)
        else:
            cc = [
                "why you still talkin to me nig you smell like expired sea food dust dumb ass nig you hideous as shit you dont know how to run because you got inverted kneecaps dumb ass nig you got that shit as an inherited trait from yo grandmother yo dumb ass nig you got mad at her and started slamming a hammer on the back of her knee to fix that shit hoping it would magically fix yours you dumb ass nig",
                "Shut up nig yo bus driver got sick of you smoking ciggaretes at the back of the school-bus so he recorded you with a Black and White Vintage Camera and got you expelled from school nig you dumb as shit",
                "nope nig that's why yo ass ran away from home and got into an altercation with Team Rocket from Pokemon boy them nigs got to throwing pokeballs at yo ass unleashing all the legendary pokemon just to kill you nig;Sike nig yo dumb ass traded yo Samsung Galaxy Note10 for a Pillow Pet because you always lonely at night nig fuck is you talkin bout",
                "This nigga ugly as shit you fat ass boy you been getting flamed by two donkeys when you walk to the store and one of them smacked you in the forehead fuckboy and then you go to come in with uh ???? and smacked you in the bootycheeks fuckboy you dirty as shit boy everytime you go to school nigga you get bullied by 10 white kids that say you gay behind the bus fuckboy suck my dick nigga unknown as shit nigga named nud you been getting hit by two frozen packs when you walk into the store fuckboy suck my dick unknown ass nigga named nud nigga you my son nigga hold on, ay creedo you can flame this nigga for me? Yeah im in this bitch fuck is you saying nigga my nigga.",
                "thats cool in all my nigga but you're ass is build like my grandma with you're no neck body built bath and body works double or nothing for a barbie girl doll that built like ken stupid ass my nigga. You brush your teeth with the cum from your dad's left cock that was in your mom and aunt's asshole. and your calling me a fuckboy? NIGGA YOURE BUILT LIKE AN ENDERMAN WITH HEIGHT SWAPPED TO WIDTH YOUR ASS CHEEKS LOOK LIKE 2 JIGGLYPUFFS RUBBING AGAINST EACH OTHER FOR \"BREEDING\" TO MAKE A BUZZWOLE EGG. You hack pokemon but you cant hack a new dad my nigga you thought your dad died in minecraft and didnt respawn yet.",
                "I kno ass aint talkin boy you look like a discombobulated toe nail nigga whenever you take a bath your jerk off then the next you smell like ass nasty nigga fuck is you saying nigga you got smacked with a gold fish in the grocery store and smacked the gold fish with fish food nasty bitch boy you ugly as shit fuck is you saying FAT BOY ugly bitch my nigga i caught yo ass slap boxing yo granny with an apple fuck is you saying my nigga when you get horny you jerk off to donkeys fuck is you saying ugly bitch",
                "lil bitchass nigga i know you aint talking to me with that greasy ass mcdonalds french fries lubricated fingers nigga you are dirty as shit you are the cousin of the dirtiest man in the entire fucking word nigga you disgusting as shit nigga your nickname be the human repellant cause no bitches want to be near you dirtyass nigga shut the fuck up with any excuses i know u aint talking to me with that nastyass neckbeard lil redhead headass boy",
            ]
            random.shuffle(cc)
            embed = discord.Embed(
                color=0xF7F9F8,
                description=f"**{ctx.author}**: {random.choice(cc)}",
                timestamp=datetime.now(),
            )
            embed.set_footer(text=f"{user} just got violated", icon_url=None)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
            await ctx.reply(embed=embed)

    @commands.command(name="cum", aliases=["jerkoff", "ejaculate", "orgasm"])
    @blacklist()
    async def cum(self, ctx):
        message = await ctx.send(
            """'
                :ok_hand:            :smile:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8=:punch:=D 
                :trumpet:      :eggplant:"""
        )
        await asyncio.sleep(0.5)
        await message.edit(
            content="""     :ok_hand:            :smiley:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D 
                :trumpet:      :eggplant:  
        """
        )
        await asyncio.sleep(0.5)
        await message.edit(
            content="""     :ok_hand:            :grimacing:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8=:punch:=D 
                :trumpet:      :eggplant:  
        """
        )
        await asyncio.sleep(0.5)
        await message.edit(
            content="""     :ok_hand:            :persevere:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D 
                :trumpet:      :eggplant:   
        """
        )
        await asyncio.sleep(0.5)
        await message.edit(
            content="""     :ok_hand:            :confounded:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8=:punch:=D 
                :trumpet:      :eggplant: 
        """
        )
        await asyncio.sleep(0.5)
        await message.edit(
            content="""     :ok_hand:            :tired_face:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D 
                :trumpet:      :eggplant:    
                """
        )
        await asyncio.sleep(0.5)
        await message.edit(
            content="""     :ok_hand:            :weary:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8=:punch:= D:sweat_drops:
                :trumpet:      :eggplant:        
        """
        )
        await asyncio.sleep(0.5)
        await message.edit(
            content="""     :ok_hand:            :dizzy_face:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D :sweat_drops:
                :trumpet:      :eggplant:                 :sweat_drops:
        """
        )
        await asyncio.sleep(0.5)
        await message.edit(
            content="""     :ok_hand:            :drooling_face:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D :sweat_drops:
                :trumpet:      :eggplant:                 :sweat_drops:
        """
        )

    @commands.command(
        help="cuddle with someone", usage="[member]", description="roleplay"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def cuddle(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`cuddle <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/cuddle")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*aww how cute! {ctx.author.mention} is cuddling with {user.mention}*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="slap someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def slap(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`slap <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/slap")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*{ctx.author.mention} slapped {user.mention}*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="pat someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def pat(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`pat <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/pat")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*aww how cute! {ctx.author.mention} pat {user.mention}*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="hug someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def hug(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`hug <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/hug")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*aww how cute! {ctx.author.mention} hugged {user.mention}*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="kiss someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def kiss(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`kiss <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/kiss")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*aww how cute! {ctx.author.mention} kissed {user.mention}*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(
        help="feed someone?....", usage="[member]", description="roleplay"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def feed(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`feed <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/feed")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*aww how cute! {ctx.author.mention} is feeding {user.mention}*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="tickle someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def tickle(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`tickle <user>`")
            await ctx.send(embed=embed)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/tickle")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*aw! look at the flirts! {ctx.author.mention} is tickling {user.mention}*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="cry", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def cry(self, ctx, user: discord.Member = None):
        r = requests.get("http://api.nekos.fun:8080/api/cry")
        res = r.json()
        em = discord.Embed(
            color=0xF7F9F8, description=f"*aww! {ctx.author.mention} is crying"
        )
        em.set_image(url=res["image"])
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="funny", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def laugh(self, ctx, user: discord.Member = None):
        r = requests.get("http://api.nekos.fun:8080/api/laugh")
        res = r.json()
        em = discord.Embed(color=0xF7F9F8)
        em.set_image(url=res["image"])
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(
        help="senpai notice meeeee!", usage="[member]", description="roleplay"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def poke(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(color=0xF7F9F8, title="`poke <user>`")
            await ctx.send(embed=embed)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/poke")
            res = r.json()
            em = discord.Embed(
                color=0xF7F9F8,
                description=f"*aw how cute! {ctx.author.mention} is poking {user.mention}!*",
            )
            em.set_image(url=res["image"])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="b-baka!!!", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def baka(self, ctx, user: discord.Member = None):
        r = requests.get("http://api.nekos.fun:8080/api/baka")
        res = r.json()
        em = discord.Embed(color=0xF7F9F8)
        em.set_image(url=res["image"])
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(
        name="rate",
        description="get a rating of a member",
        brief="member",
        usage="```Syntax: ,rate <member>\nExample: ,rate @aiohttp```",
    )
    async def rate(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.message.author

        embed = discord.Embed(
            description=f"> {user.mention} is a **{random.randint(1, 10)}/10**",
            color=0x2B2D31,
        )
        await ctx.send(embed=embed)

    @commands.command(help="roast anyone")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def roast(self, ctx):
        roast_list = [
            "at least my mom pretends to love me",
            "Bards will chant parables of your legendary stupidity for centuries, You",
            "Don't play hard to get when you are hard to want",
            "Don't you worry your pretty little head about it. The operative word being little. Not pretty.",
            "Get a damn life you uncultured cranberry fucknut.",
            "God wasted a good asshole when he put teeth in your mouth",
            "Goddamn did your parents dodge a bullet when they abandoned you.",
            "I bet your dick is an innie and your belly button an outtie.",
            "I can't even call you Fucking Ugly, because Nature has already beaten me to it.",
            "I cant wait to forget you.",
            "I curse the vagina that farted you out.",
            "I don't have the time, or the crayons to explain this to you.",
            "I FART IN YOUR GENERAL DIRECTION",
            "I fucking hate the way you laugh.",
            "I hope you win the lottery and lose your ticket.",
            "I once smelled a dog fart that had more cunning, personality, and charm than you.",
            "I shouldn't roast you, I can't imagine the pain you go through with that face!",
            "I want to call you a douche, but that would be unfair and unrealistic. Douches are often found near vaginas.",
            "I wonder if you'd be able to speak more clearly if your parents were second cousins instead of first.",
            "I would call you a cunt, but you lack the warmth or the depth.",
            "I would challenge you to a battle of wits, but it seems you come unarmed",
            "I would rather be friends with Ajit Pai than you.",
            "I'd love to stay and chat but I'd rather have type-2 diabetes",
            "I'm just surprised you haven't yet retired from being a butt pirate.",
            "I'm not mad. I'm just... disappointed.",
            "I've never met someone who's at once so thoughtless, selfish, and uncaring of other people's interests, while also having such lame and boring interests of his own. You don't have friends, because you shouldn't.",
            "Im betting your keyboard is filthy as fuck now from all that Cheeto-dust finger typing, you goddamn weaboo shut in. ",
            "If 'unenthusiastic handjob' had a face, your profile picture would be it.",
            "If there was a single intelligent thought in your head it would have died from loneliness.",
            "If you were a potato you'd be a stupid potato.",
            "If you were an inanimate object, you'd be a participation trophy.",
            "If you where any stupider we'd have to water you",
            "If you're dad wasn't so much of a pussy, he'd have come out of the closet before he had you.",
            "It's a joke, not a dick. You don't have to take it so hard.",
            "Jesus Christ it looks like your face was on fire and someone tried to put it out with an ice pick",
            "May the fleas of ten thousand camels live happily upon your buttocks",
            "Maybe if you eat all that makeup you will be beautiful on the inside.",
            "Mr. Rogers would be disappointed in you.",
            "Next time, don't take a laxative before you type because you just took a steaming stinking dump right on the page. Now wipe that shit up and don't fuck it up like your life.",
            "Not even your dog loves you. He's just faking it.",
            "Once upon a time, Santa Clause was asked what he thought of your mom, your sister and your grandma, and thus his catchphrase was born.",
            "People don't even pity you.",
            "People like you are the reason God doesn't talk to us anymore",
            "Take my lowest priority and put yourself beneath it.",
            "The IQ test only goes down to zero but you make a really compelling case for negative numbers",
            "the only thing you're fucking is natural selection",
            "There are two ugly people in this chat, and you're both of them.",
            "There will never be enough middle fingers in this world for You",
            "They don't make a short enough bus in the Continental United States for a person like you.",
            "Those aren't acne scars, those are marks from the hanger.",
            "Twelve must be difficult for you. I dont mean BEING twelve, I mean that being your IQ.",
            "We all dislike you, but not quite enough that we bother to think about you.",
            "Were you born a cunt, or is it something you have to recommit yourself to every morning?",
            "What's the difference between three dicks and a joke? You can't take a joke.",
            "When you die, people will struggle to think of nice things to say about you.",
            "Where'd ya get those pants? The toilet store?",
            "Why do you sound like you suck too many cocks?",
            "Why dont you crawl back to whatever micro-organism cesspool you came from, and try not to breath any of our oxygen on the way there",
            "WHY SHOULD I LISTEN TO YOU ARE SO FAT THAT YOU CAN'T POO OR PEE YOU STINK LYRE YOU HAVE A CRUSH ON POO",
            "You are a pizza burn on the roof of the world's mouth.",
            "You are a stupid.",
            "You are dumber than a block of wood and not nearly as useful",
            "You are like the end piece of bread in a loaf, everyone touches you but no one wants you",
            "You have a face made for radio",
            "You have more dick in your personality than you do in your pants",
            "You have the face of a bulldog licking piss off a stinging nettle.",
            "You know they say 90 percent of dust is dead human skin? That's what you are to me.",
            "You know, one of the many, many things that confuses me about you is that you remain unmurdered.",
            "You look like your father would be disappointed in you. If he stayed.",
            "You losing your virginity is like a summer squash growing in the middle of winter. Never happening.",
            "You may think people like being around you- but remember this: there is a difference between being liked and being tolerated.",
            "You might want to get a colonoscopy for all that butthurt",
            "You need to go up to your daddy, get on your knees and apologize to each and every brother and sister that didn't make it to your mother's egg before you",
            "You should put a condom on your head, because if you're going to act like a dick you better dress like one too.",
            "You stuck up, half-witted, scruffy looking nerf herder!",
            "You were birthed out your mothers ass because her cunt was too busy.",
            "You're an example of why animals eat their young.",
            "You're impossible to underestimate",
            "You're kinda like Rapunzel except instead of letting down your hair you let down everyone in your life",
            "You're like a penny on the floor of a public restroom - filthy, untouchable and practically worthless.",
            "You're like a square blade, all edge and no point.",
            "You're looking well for a man twice your age! Any word on the aneurism?",
            "You're not pretty enough to be this dumb",
            "You're objectively unattractive.",
            "You're so dense, light bends around you.",
            "You're so salty you would sink in the Dead Sea",
            "You're so stupid you couldn't pour piss out of a boot if the directions were written on the heel",
            "You're such a pussy that fucking you wouldnt be gay.",
            "You're ugly when you cry.",
            "Your birth certificate is an apology letter from the abortion clinic.",
            "Your memes are trash.",
            "Your mother may have told you that you could be anything you wanted, but a douchebag wasn't what she meant.",
            "Your mother was a hamster, and your father reeks of elderberries!",
            "Your penis is smaller than the payment a homeless orphan in Mongolia received for stitching my shoes.",
        ]
        embed = discord.Embed(
            color=0xF7F9F8, description=f"{random.choice(roast_list)}"
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="cat")
    async def cat_picture(self, ctx):
        CAT_API_URL = "https://api.thecatapi.com/v1/images/search"
        response = requests.get(CAT_API_URL)

        if response.status_code == 200:
            data = response.json()
            if data:
                cat_image_url = data[0]["url"]
                embed = discord.Embed(
                    title="Heres your cat picture <a:022catjam:1135482785533009951>",
                    color=0x2B2D31,
                )
                embed.set_image(url=cat_image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(
                    "Sorry, I couldn't find a cat picture at the moment. Meow!"
                )
        else:
            await ctx.send("Sorry, I couldn't fetch a cat picture at the moment. Meow!")

    @commands.command(name="dog")
    async def dog_picture(self, ctx):
        DOG_API_URL = "https://dog.ceo/api/breeds/image/random"
        response = requests.get(DOG_API_URL)

        if response.status_code == 200:
            data = response.json()
            if data and data["status"] == "success":
                dog_image_url = data["message"]
                embed = discord.Embed(
                    title="Heres's your dog photo <a:dogbarks:1135493740224581732>",
                    color=0x2B2D31,
                )
                embed.set_image(url=dog_image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(
                    "Sorry, I couldn't find a dog picture at the moment. Woof!"
                )
        else:
            await ctx.send("Sorry, I couldn't fetch a dog picture at the moment. Woof!")

    @commands.command()
    async def roblox(self, ctx, username):
        try:
            users_json = requests.get(
                f"https://www.roblox.com/search/users/results?keyword={username}&maxRows=1&startIndex=0"
            )
            users = json.loads(users_json.text)

            if "UserSearchResults" not in users or not users["UserSearchResults"]:
                await ctx.send("User not found.")
                return

            user_id = users["UserSearchResults"][0]["UserId"]

            profile_json = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
            profile = json.loads(profile_json.text)

            if (
                "displayName" not in profile
                or "created" not in profile
                or "description" not in profile
            ):
                await ctx.send("An error occurred while fetching user data.")
                return

            display_name = profile["displayName"]
            created_date = profile["created"]
            description = profile["description"]

            thumbnail_json = requests.get(
                f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=100x100&format=Png&isCircular=false"
            )
            thumbnail = json.loads(thumbnail_json.text)

            if "data" not in thumbnail or not thumbnail["data"]:
                await ctx.send("An error occurred while fetching user data.")
                return

            thumbnail_url = thumbnail["data"][0]["imageUrl"]

            followers_json = requests.get(
                f"https://friends.roblox.com/v1/users/{user_id}/followers/count"
            )
            followers_count = json.loads(followers_json.text)["count"]

            badges_json = requests.get(
                f"https://badges.roblox.com/v1/users/{user_id}/badges"
            )
            badges_data = json.loads(badges_json.text)
            badges_count = len(badges_data["data"])
            badges_names = [badge["name"] for badge in badges_data["data"]]

            embed = discord.Embed(
                title=f"{username}",
                url=f"https://www.roblox.com/users/{user_id}/profile",
                color=0x2B2D31,
            )

            embed.add_field(name="ID", value=f"{user_id}", inline=True)
            embed.add_field(name="Display Name", value=f"{display_name}", inline=True)
            embed.add_field(
                name="Created", value=f"``{created_date[:10]}``", inline=True
            )  # Truncate the date to just show the month, day, and year in bold.
            embed.add_field(name="Description", value=f"{description}", inline=True)
            embed.add_field(name="Followers", value=f"{followers_count}", inline=True)
            embed.add_field(
                name=f"Badges ({badges_count})",
                value=", ".join(badges_names) if badges_names else "None",
                inline=True,
            )
            embed.set_thumbnail(url=f"{thumbnail_url}")

            # Set the footer to the user ID
            embed.set_footer(text=f"User ID: {user_id}")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"An error occurred while fetching user data: {e}")

    @commands.command(aliases=["wc"])
    async def wordcloud(self, ctx: commands.Context, limit: int = None):
        if limit is None or limit > 100:
            limit = 100

        async with ctx.typing():
            text = [
                message.content async for message in ctx.channel.history(limit=limit)
            ]
            if not text:
                await ctx.send("No messages found to generate the wordcloud.")
                return

            wc = WordCloud(mode="RGBA", background_color=None, height=400, width=700)
            wc.generate(" ".join(text))

            image_buffer = BytesIO()
            wc.to_image().save(image_buffer, format="PNG")
            image_buffer.seek(0)

            file = discord.File(
                fp=image_buffer, filename=f"{ctx.author.id}_wordcloud.png"
            )
            await ctx.send(file=file)

        image_buffer.close()

        try:
            os.remove(f"{ctx.author.id}_wordcloud.png")
        except FileNotFoundError:
            pass

    @commands.command(
        name="hack",
        description="Hack's specified user",
        aliases=["haxxor"],
        usage="hack [user]",
    )
    @commands.cooldown(1, 7, commands.BucketType.guild)
    async def hack(self, ctx, *, member: discord.Member):
        responses = [
            f"{member.name}@fatgmail.com",
            f"{member.name}@hotmom.com",
            f"{member.name}@gaylord.com",
            f"{member.name}@gaymail.com" f"{member.name}@hentaimaster.com",
            f"{member.name}@femboymaster.com",
        ]

        password = [
            f"gaymailxoxo",
            f"{member.name}isgayxo",
            f"imabitch",
            f"bigdick{member.name}",
        ]
        websites = [
            f"fatbitchesfightingoverfood.com",
            f"ilovehentai.com",
            f"femboyporn.com",
            f"stopchangingyournameproxyorsinful.com",
            f"https://www.pornhub.com/home/search/gay",
            f"bigfreecocks.com",
            f"howtomakeyourpplarger.com",
        ]
        ipad = [f"135.791.113", f"123.456.789", f"987.654.321", f"696.969.6969"]
        msgs = [
            f"Why is my dick so little?",
            f"How do I tell my friends I'm gay",
            f"I'm stuck inside the washing machine",
            f"Claqz is so sexy bro",
            f"Send nudes",
            "I'm gay",
            "how to delete history",
            "how to be a femboy",
            "femboy porn",
        ]
        messags = [
            f"Gay",
            f"Cock",
            f"Fuck",
            f"ilydaddyClaqz",
            f"Claqz",
            f"fatbitchesfightingoverfood",
            "Fap",
            "OOP",
            "femboy pics",
        ]
        if member == ctx.message.author:
            emb = discord.Embed(color=0x4C5264, description="You cannot hack yourself.")
            emb.set_author(
                name="Error : Author",
                icon_url="https://www.freeiconspng.com/uploads/error-icon-4.png",
            )
            await ctx.send(embed=emb)
            return

        if member == member.id:
            member = member
        message = await ctx.send(f"Hacking {member.name}")
        await asyncio.sleep(3)
        await message.edit(content=f"Finding {member.name}'s Discord Info..")
        asyncio.sleep(3)
        await message.edit(content=f"Cracking {member.name}'s Login Info..")
        await asyncio.sleep(2)
        await message.edit(content=f"Information now leaking..")
        await asyncio.sleep(2)
        await message.edit(
            content=f"Email:`{random.choice(responses)}`\n Password: `{random.choice(password)}`"
        )
        await asyncio.sleep(2)
        await message.edit(content=f"Finding {member.name}'s Most Recent Websites..")
        await asyncio.sleep(2)
        await message.edit(content=f"{random.choice(websites)}")
        await asyncio.sleep(2)
        await message.edit(content=f"Searching for {member.name}'s IP Address..")
        await asyncio.sleep(2)
        await message.edit(content=f"Found {member.name}'s IP Address")
        await asyncio.sleep(2)
        await message.edit(content=f"IP Address: `{random.choice(ipad)}`")
        await asyncio.sleep(3)
        await message.edit(content="Finding most used word..")
        await asyncio.sleep(2)
        await message.edit(content=f"Found {member.name}'s Most Common Word")
        await asyncio.sleep(2)
        await message.edit(content=f"Most common words: `{random.choice(msgs)}`")
        await asyncio.sleep(3)
        await message.edit(content="Finding most recent word..")
        await asyncio.sleep(2)
        await message.edit(content=f"Found {member.name}'s Most Recent Word")
        await asyncio.sleep(2)
        await message.edit(content=f"Most recent word: `{random.choice(messags)}`")
        await asyncio.sleep(2)
        await message.edit(
            content=f"Selling {member.name}'s Fortnite Account in the Dark Web"
        )
        await asyncio.sleep(2)
        await message.edit(content=f"Hacked {member.mention}")

    @commands.command(
        name="_simp",
        description="Simp's specified user",
        aliases=["simp", "simprate"],
        usage="simprate [user]",
    )
    @commands.cooldown(1, 6, commands.BucketType.guild)
    async def _simp(self, ctx, *, member: discord.Member = None):
        member = ctx.author if not member else member
        responses = [
            "Your 75% a simp.",
            "Your 100% a simp.",
            "You’re 5% simp.",
            "You’re 15% simp.",
            "You’re 25% simp.",
            "You're 85% simp.",
            "You’re 95% a simp.",
            "MF UR MAD SIMP 💀.",
            "You’re 100% simp.",
            "Your 90% simp.",
            "You’re 80% simp.",
            "You’re 70% simp.",
            "You’re 69% simp.",
            "You’re 60% simp.",
            "You’re 50% simp.",
            "You’re 40% simp..",
            "You’re 30% simp.",
            "You’re 20% simp.",
            "You’re 10% simp.",
            "You’re not a simp.",
        ]
        embed = discord.Embed(
            title=f"{member.name}'s simprate:",
            description=f"{random.choice(responses)}",
            color=0x4C5264,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="github",
        description="Shows information on a Github user",
        usage="$github <username>",
    )
    async def github(self, ctx, username: str):
        try:
            git_api = f"https://api.github.com/users/{username}"
            async with ctx.typing():
                user_data = await FetchedValue(git_api)
                embed = discord.Embed(
                    title=f"{username}",
                    description=f"{user_data['bio']}",
                    colour=0x2F3136,
                )
                embed.add_field(
                    name="**Overview**",
                    value=f"""**Public repos:** {user_data['public_repos']}
**Public gists:** {user_data['public_gists']}""",
                )
                embed.add_field(
                    name="**Dates**",
                    value=f"""**Created at:** {user_data['created_at'][:10]}
**Updated at:** {user_data['updated_at'][:10]}""",
                    inline=False,
                )
                embed.add_field(
                    name="**Statistics**",
                    value=f"""**Followers:** {user_data['followers']}
**Following:** {user_data['following']}""",
                    inline=False,
                )
                embed.set_thumbnail(url=user_data["avatar_url"])
                embed.set_author(
                    name=ctx.message.author.name,
                    icon_url=ctx.message.author.display_avatar,
                )
                embed.url = f"https://github.com/{username}"
                embed.set_footer(
                    text="Github",
                    icon_url="https://cdn.discordapp.com/emojis/998324589832716298.webp?size=4096&quality=lossless",
                )
                await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command()
    async def marry(self, ctx, *, member: discord.Member = None):
        if member == None:
            emb = discord.Embed(
                color=0x2F3136, title="**marry**", description="> __marry an user__"
            )
            emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            emb.add_field(name="**category**", value="> __roleplay__")
            emb.add_field(name="**permissions**", value="> __any__")
            emb.add_field(name="**usage**", value="> ```marry [user]```", inline=False)
            emb.add_field(name="**aliases**", value="> __none__")
            await ctx.reply(embed=emb, mention_author=False)
            return
        elif member == ctx.author:
            embe = discord.Embed(
                color=0x2F3136,
                description=f"> {ctx.author.mention} you can't __marry yourself__",
            )
            await ctx.reply(embed=embe, mention_author=False)
            return
        elif member.bot:
            em = discord.Embed(
                color=0x2F3136,
                description=f"> {ctx.author.mention} robots can't __consent marriage__",
            )
            await ctx.reply(embed=em, mention_author=False)
            return
        else:
            collection = self.db["marry"]
            ts = calendar.timegm(time.gmtime())
            meri = collection.find_one({"_id": member.id})
            if meri is not None:
                await ctx.reply(
                    "> uh oh! this user is __already married!__", mention_author=False
                )
                return
            else:
                mer = collection.find_one({"soulmate": member.id})
                if mer is not None:
                    await ctx.reply(
                        "> uh oh! this user is __already married!__",
                        mention_author=False,
                    )
                    return

            check = collection.find_one({"_id": ctx.author.id})
            if check is not None:
                emb = discord.Embed(
                    color=discord.Color.yellow(),
                    description=f"> {ctx.author.mention} you are already __married.__ don't try to **cheat!**",
                )
                await ctx.reply(embed=emb, mention_author=False)
                return
            else:
                check2 = collection.find_one({"soulmate": ctx.author.id})
                if check2 is not None:
                    emb = discord.Embed(
                        color=discord.Color.yellow(),
                        description=f"> {ctx.author.mention} you are already __married.__ don't try to **cheat!**",
                    )
                    await ctx.reply(embed=emb, mention_author=False)
                    return
                else:
                    button1 = Button(label="accept", style=discord.ButtonStyle.green)
                    button2 = Button(label="refuse", style=discord.ButtonStyle.red)
                    embed = discord.Embed(
                        color=0x2F3136,
                        description=f"> {ctx.author.mention} wants to __marry you.__ do you accept?",
                    )

                    async def button1_callback(interaction):
                        if interaction.user == ctx.author:
                            await interaction.response.send_message(
                                "> you can't accept your own __marriage__",
                                ephemeral=True,
                            )
                        elif interaction.user != member:
                            await interaction.response.send_message(
                                "> you can't accept **this**", ephemeral=True
                            )
                        else:
                            insert = {
                                "_id": ctx.author.id,
                                "soulmate": member.id,
                                "time": f"{ts}",
                            }
                            collection.insert_one(insert)
                            embe = discord.Embed(
                                color=0x2F3136,
                                description=f"> {ctx.author.mention} got __married__ with **{member.mention}**",
                            )
                            await interaction.response.edit_message(
                                content=None, embed=embe, view=None
                            )

                    button1.callback = button1_callback

                    async def button2_callback(interaction):
                        if interaction.user == ctx.author:
                            await interaction.response.send_message(
                                "> you can't accept your own __marriage__",
                                ephemeral=True,
                            )
                        elif interaction.user != member:
                            await interaction.response.send_message(
                                "> you can't __accept__ this", ephemeral=True
                            )
                        else:
                            embe = discord.Embed(
                                color=0x2F3136,
                                description=f"> {ctx.author.mention} i'm sorry, but __{member.mention}__ is probably not the right person for you",
                            )
                            await interaction.response.edit_message(
                                content=None, embed=embe, view=None
                            )

                    button2.callback = button2_callback

                    marry = View()
                    marry.add_item(button1)
                    marry.add_item(button2)
                    await ctx.send(f"{member.mention}", embed=embed, view=marry)

    @commands.command()
    async def lyrics(self, ctx, *, song: str = None):
        if not song:
            e = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            e.set_footer(
                text="fun",
                icon_url=None,
            )
            e.set_author(name="lyrics", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{ctx.bot.command_prefix} Info",
                value=f"{ctx.bot.command_prefix} **description:** get the lyrics of a song",
                inline=False,
            )
            e.add_field(
                name=f"{ctx.bot.command_prefix} Usage",
                value=f"{ctx.bot.command_prefix} syntax: ,lyrics <song name>\n{ctx.bot.command_prefix} example: ,lyrics new drank",
                inline=False,
            )
            return await ctx.reply(embed=e)

        with open("path/to/your/emojis.json", "r") as file:
            emojis = json.load(file)

        data = await self.bot.session.get(
            f'https://api.popcat.xyz/lyrics?song={song.replace(" ", "+")}'
        )
        data = await data.json()
        embed = discord.Embed(color=discord.Color.gold())
        embed.set_footer(
            text=data["artist"],
            icon_url=emojis["dash"],
        )
        embed.set_author(name=data["title"], icon_url=data["image"])
        embed.description = data["lyrics"]
        embed.set_image(url=data["image"])
        embed.set_thumbnail(url=data["image"])
        await ctx.reply(embed=embed)

    @commands.command()
    async def quote(self, ctx, message: discord.Message = None):
        if not message and ctx.message.reference:
            message = ctx.message.reference.resolved

        x = discord.Embed(color=0x2F3136)
        z = "\u200b"
        x.description = f"{z if not message.content else message.content}"
        x.set_author(name=message.author, icon_url=message.author.display_avatar)
        if message.attachments:
            x.set_image(url=message.attachments[0].proxy_url)
        embeds = []
        embeds.append(x)
        [embeds.append(e) async for e in utils.aiter(message.embeds)]
        await ctx.reply(embeds=embeds, view=discord.ui.View().from_message(message))


async def setup(bot):
    await bot.add_cog(fun(bot))
