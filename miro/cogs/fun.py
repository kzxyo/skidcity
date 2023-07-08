import discord, os, asyncio,  random, aiohttp, requests, io, random, time
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from gtts import gTTS
from modules import utils
from typing import Optional, Union
from discord.ui import Button, View
from io import BytesIO
from discord.ext.commands import Context


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #
        self.done = utils.emoji("done")
        self.fail = utils.emoji("fail")
        self.warn = utils.emoji("warn")
        self.reply = utils.emoji("reply")
        self.dash = utils.emoji("dash")
        #
        self.success = utils.color("done")
        self.error = utils.color("fail")
        self.warning = utils.color("warn")
        #
        self.av = "https://cdn.discordapp.com/attachments/1107734070659653652/1116445181974167632/download_2.jpg"


    @commands.hybrid_command(name = "eject", description = "Eject specified user",aliases=['imposter'], usage = "eject [user]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def eject(self, ctx, user: discord.Member = None):
        user = ctx.author if not user else user

        impostor = ["true", "false"]

        crewmate = [
            "black",
            "blue",
            "brown",
            "cyan",
            "darkgreen",
            "lime",
            "orange",
            "pink",
            "purple",
            "red",
            "white",
            "yellow",
        ]

        await ctx.reply(
            f"https://vacefron.nl/api/ejected?name={user.name}&impostor={random.choice(impostor)}&crewmate={random.choice(crewmate)}"
        )

    @commands.hybrid_command(name = "tts", description = "Make text to tts",aliases=['texttoospeech'], usage = "tts [text]")
    @commands.cooldown(1, 7, commands.BucketType.guild)
    async def tts(self, ctx, lang, *, text: str):
        tts = gTTS(text, lang=lang)
        filename = f"{text}.mp3"
        tts.save(filename)
        await ctx.send(file=discord.File(fp=filename, filename=filename))
        if os.path.exists(filename):
            os.remove(filename)

    @commands.hybrid_command(name = "uselessfact", description = "Return uselessfact",aliases=['uf', 'fact'], usage = "uselessfact")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def uselessfact(self, ctx):
        data = await self.bot.session.get(
            f"https://uselessfacts.jsph.pl/random.json?language=en"
        )
        data = await data.json()
        await ctx.reply(data["text"])

    @commands.hybrid_command(name = "emojify", description = "Make text to emojis",aliases=['emojitext'], usage = "emojitext [text]")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def emojify(self, ctx, *, text=None):
        if not text:
            return await ctx.reply("?")
        emojis = []
        for char in text.lower().replace(" ", "  "):
            if char.isdigit():
                number2emoji = {
                    "1": "one",
                    "2": "two",
                    "3": "three",
                    "4": "four",
                    "5": "five",
                    "6": "six",
                    "7": "seven",
                    "8": "eight",
                    "9": "nine",
                    "0": "zero",
                }

                emojis.append(f":{number2emoji[char]}:")

            elif char.isalpha():
                emojis.append(f":regional_indicator_{char}:")
            else:
                emojis.append(char)

        await ctx.reply(" ".join(emojis))

    @commands.hybrid_command(name = "morse", description = "Make text to morse code", aliases=['morsing'], usage = "morse [text]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def morse(self, ctx, *, text: str):
        to_morse = {
            "a": ".-",
            "b": "-...",
            "c": "-.-.",
            "d": "-..",
            "e": ".",
            "f": "..-.",
            "g": "--.",
            "h": "....",
            "i": "..",
            "j": ".---",
            "k": "-.-",
            "l": ".-..",
            "m": "--",
            "n": "-.",
            "o": "---",
            "p": ".--.",
            "q": "--.-",
            "r": ".-.",
            "s": "...",
            "t": "-",
            "u": "..-",
            "v": "...-",
            "w": ".--",
            "x": "-..-",
            "y": "-.--",
            "z": "--..",
            "1": ".----",
            "2": "..---",
            "3": "...--",
            "4": "....-",
            "5": ".....",
            "6": "-....",
            "7": "--...",
            "8": "---..",
            "9": "----.",
            "0": "-----",
        }

        cipher = ""
        for letter in text:
            if letter.isalpha() or letter.isdigit():
                cipher += to_morse[letter.lower()] + " "
            else:
                cipher += letter
        await ctx.reply(cipher)

    @commands.command(name = "spotifyuser", description = "Return user spotify activity", aliases=['spotuser'], usage = "spotifyuser [user]")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def spotifyuser(self, ctx, user: discord.Member = None):
        await ctx.typing()
        user = ctx.author if not user else user
        spotify_result = next(
            (
                activity
                for activity in user.activities
                if isinstance(activity, discord.Spotify)
            ),
            None,
        )

        if spotify_result is None:
            return await ctx.send(
                embed=discord.Embed(
                    color=0x4c5264,
                    description=f'{self.fail} {ctx.author.mention}**:** make sure to enable: " *display spotify as your status* " in user settings',
                )
            )

        api = f"https://api.jeyy.xyz/discord/spotify?title={spotify_result.title}&cover_url={spotify_result.album_cover_url}&duration_seconds={spotify_result.duration.seconds}&start_timestamp={spotify_result.created_at.timestamp()}&artists={', '.join(spotify_result.artists).replace(',', '%2C').replace(' ', '%20')}"
        api = await utils.file(api, "spotify.png")

        embed = discord.Embed(color=utils.color("main"))
        embed.description = f"**Spotify Now Playing**\n\n{self.reply} **Track**: *[{spotify_result.title}](https://open.spotify.com/track/{spotify_result.track_id})*\n{self.reply} **Artist:** *[{spotify_result.artist}](https://open.spotify.com/artist/undefined)*"
        embed.set_author(name=user, icon_url=user.avatar)
        embed.set_thumbnail(url=spotify_result.album_cover_url)
        embed.set_image(url="attachment://spotify.png")
        msg = await ctx.reply(embed=embed, file=api)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.command()
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def quote(self, ctx, message: discord.Message = None):
        if not message and ctx.message.reference:
            message = ctx.message.reference.resolved

        x = discord.Embed(color=0x4c5264)
        z = "\u200b"
        x.description = f"{z if not message.content else message.content}"
        x.set_author(name=message.author, icon_url=message.author.display_avatar)
        if message.attachments:
            x.set_image(url=message.attachments[0].proxy_url)
        embeds = []
        embeds.append(x)
        [embeds.append(e) async for e in utils.aiter(message.embeds)]
        await ctx.reply(embeds=embeds, view=discord.ui.View().from_message(message))


    @commands.command(name = "kiss", description = "Kiss specified user",aliases=['smooch'], usage = "kiss [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def kiss(self, ctx, *, member: discord.Member = None):
        if member == None:
            embed = discord.Embed(
                color=0x4c5264, description=f"> ```syntax: kiss [member]```"
            )
            await ctx.reply(embed=embed, mention_author=False)
            return
        response = requests.get("http://api.nekos.fun:8080/api/kiss")
        data = response.json()
        embed = discord.Embed(
            color=0x4c5264,
            description=f"> Aww how cute! __{ctx.author.mention}__ kissed __{member.mention}__",
        )
        embed.set_image(url=data["image"])
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "cuddle", description = "Cuddle's specified user",aliases=['hug'], usage = "cuddle [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def cuddle(self, ctx, *, member: discord.Member = None):
        if member == None:
            embed = discord.Embed(
                color=0x4c5264, description=f"> ```syntax: cuddle [member]```"
            )
            await ctx.reply(embed=embed, mention_author=False)
            return
        response = requests.get("http://api.nekos.fun:8080/api/cuddle")
        data = response.json()
        embed = discord.Embed(
            color=0x4c5264,
            description=f"> *Aww how cute! __{ctx.author.mention}__ cuddled __{member.mention}__*",
        )
        embed.set_image(url=data["image"])
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "pat", description = "Pat's specified user",aliases=['tap'], usage = "pat [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def pat(self, ctx, *, member: discord.Member = None):
        if member == None:
            embed = discord.Embed(
                color=0x4c5264, description=f"> ```syntax: pat [member]```"
            )
            await ctx.reply(embed=embed, mention_author=False)
            return
        response = requests.get("http://api.nekos.fun:8080/api/pat")
        data = response.json()
        embed = discord.Embed(
            color=0x4c5264,
            description=f"> *Aww how cute! __{ctx.author.mention}__ pat __{member.mention}__*",
        )
        embed.set_image(url=data["image"])
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "slap", description = "Slap's specified user",aliases=['hit'], usage = "slap [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def slap(self, ctx, *, member: discord.Member = None):
        if member == None:
            embed = discord.Embed(
                color=0x4c5264, description=f"> ```syntax: slap [member]```"
            )
            await ctx.reply(embed=embed, mention_author=False)
            return
        response = requests.get("http://api.nekos.fun:8080/api/slap")
        data = response.json()
        embed = discord.Embed(
            color=0x4c5264,
            description=f"> *__{ctx.author.mention}__ slapped __{member.mention}__*",
        )
        embed.set_image(url=data["image"])
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "laugh", description = "Makes you laugh",aliases=['chuckle'], usage = "laugh")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def laugh(self, ctx):
        response = requests.get("http://api.nekos.fun:8080/api/laugh")
        data = response.json()
        embed = discord.Embed(
            color=0x4c5264, description=f"> *__{ctx.author.mention}__ laughs*"
        )
        embed.set_image(url=data["image"])
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "cry", description = "Makes you cry",aliases=['sob'], usage = "cry")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def cry(self, ctx):
        response = requests.get("http://api.nekos.fun:8080/api/cry")
        data = response.json()
        embed = discord.Embed(
            color=0x4c5264, description=f"> *__{ctx.author.mention}__ cries*"
        )
        embed.set_image(url=data["image"])
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "hack", description = "Hack's specified user",aliases=['haxxor'], usage = "hack [user]")
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
            emb = discord.Embed(color=0x4c5264, description="You cannot hack yourself.")
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

    @commands.command(name = "_simp", description = "Simp's specified user",aliases=['simp', 'simprate'], usage = "simprate [user]")
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
            color=0x4c5264,
        )
        await ctx.send(embed=embed)

    @commands.command(help="b-baka!!!", description="roleplay", aliases=["idiot"])
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def baka(self, ctx, user: discord.Member = None):
        r = requests.get("http://api.nekos.fun:8080/api/baka")
        res = r.json()
        em = discord.Embed(color=0x4c5264)
        em.set_image(url=res["image"])
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(name = "_8ball", description = "Ask miro a question",aliases=['8ball', 'question', 'ask'], usage = "8ball [question]")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def _8ball(self, ctx, *, question):
        if question == None:
            embed = discord.Embed(description="**Specify a question**", color=0x4c5264)
            await ctx.send(embed=embed)
        else:
            responses = [
                "it is certain",
                "Yes",
                "No",
                "Ask again later.",
                "As I see it, yes",
                "Signs point to yes",
                "Hell naw",
                "You may rely on it,",
                "Most likely",
                "better not tell you now",
                "Of course not",
                "Is that even a question?",
                "Negative",
                "Definetly not",
                "100% yes",
            ]
            embed = discord.Embed(
                title=f"",
                description=f":8ball: | {random.choice(responses)}, `{ctx.author.name}`",
                color=0x4c5264,
            )
            await ctx.send(embed=embed)

    @commands.command(name = "pp", description = "See pp size for specified user",aliases=['ppsize'], usage = "pp [user]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def pp(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
            size = random.randint(1, 50)
            ppsize = ""
            for _i in range(size):
                ppsize += "="
                embed = discord.Embed(
                    title=f"{user}'s pp size",
                    description=f"8{ppsize}D",
                    colour=0x4c5264,
                )
            await ctx.send(embed=embed)

    @commands.command(name = "reverse",  description = "Reverses text", usage = "reverse <text>", aliases=["reversetext"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def reverse(self, ctx,*,msg):
                msg = list(msg)
                msg.reverse()
                embed = discord.Embed(description = "".join(msg), timestamp=ctx.message.created_at, colour=0x4c5264)
                embed.set_author(name = ctx.message.author, icon_url = ctx.message.author.avatar)
                await ctx.reply(embed=embed)


    @commands.command(
        help="senpai notice meeeee!", usage="[member]", description="poke someone", aliases=["push"]
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
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

    @commands.command(help="tickle someone", usage="[member]", description="tickle someone", aliases=["stroke"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
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

    @commands.command(
        help="feed someone?....", usage="[member]", description="feed someone?", aliases=["snuckle"]
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
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

    @commands.command(
        help=f"returns the urban dictionary meaning of the word",
        description="returns the urban dictionary meaning of the word",
        usage="urban [word]",
        aliases=["ud"],
    )
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def urban(self, ctx, *, word):
        if word is None:
            e = discord.Embed(description="> please provide a word")
            await ctx.send(embed=e)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.urbandictionary.com/v0/define?term={word}"
                ) as resp:
                    data = await resp.json()
            if not data["list"]:
                await ctx.send(f"No results found for {word}.")
                return
            definition = data["list"][0]["definition"]
            example = data["list"][0]["example"]
            embed = discord.Embed(title=f"Urban Dictionary: {word}", color=0x7289DA)
            embed.add_field(name="Definition", value=definition, inline=False)
            embed.add_field(name="Example", value=example, inline=False)
            embed.set_thumbnail(
                url="https://imgs.search.brave.com/CrwNIBGq0wryzQTxOpFlsZTHvf7jCqcXU7Di-qqkU60/rs:fit:512:512:1/g:ce/aHR0cHM6Ly9zbGFj/ay1maWxlczIuczMt/dXMtd2VzdC0yLmFt/YXpvbmF3cy5jb20v/YXZhdGFycy8yMDE4/LTAxLTExLzI5NzM4/NzcwNjI0NV84NTg5/OWE0NDIxNmNlMTYw/NGM5M181MTIuanBn"
            )
            await ctx.send(embed=embed)

    @commands.command(name = "cum", description = "Make miro cum",aliases=['jerkoff'], usage = "cum")
    @commands.cooldown(1, 4, commands.BucketType.guild)
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

    @commands.command(name = "createembed", description = "Make miro create a embed",aliases=['ce'], usage = "createembed")
    @commands.cooldown(1, 12, commands.BucketType.guild)
    @commands.bot_has_permissions(administrator=True)
    @utils.perms("administrator")
    async def createembed(self, ctx):
        def check_author(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Ask for embed title
        await ctx.send("Enter the embed title:")
        title_msg = await self.bot.wait_for('message', check=check_author)
        title = title_msg.content

        # Ask for embed description
        await ctx.send("Enter the embed description:")
        description_msg = await self.bot.wait_for('message', check=check_author)
        description = description_msg.content

        # Ask if embed should have an author
        await ctx.send("Should the embed have an author? (yes/no)")
        author_choice_msg = await self.bot.wait_for('message', check=check_author)
        author_choice = author_choice_msg.content.lower()

        author_name = None
        author_icon_url = None

        if author_choice == "yes":
            await ctx.send("Enter the author name:")
            author_name_msg = await self.bot.wait_for('message', check=check_author)
            author_name = author_name_msg.content

            await ctx.send("Enter the author icon URL (optional):")
            author_icon_url_msg = await self.bot.wait_for('message', check=check_author)
            if author_icon_url_msg.content:
                author_icon_url = author_icon_url_msg.content

        # Ask if embed should have a footer
        await ctx.send("Should the embed have a footer? (yes/no)")
        footer_choice_msg = await self.bot.wait_for('message', check=check_author)
        footer_choice = footer_choice_msg.content.lower()

        footer_text = None
        footer_icon_url = None

        if footer_choice == "yes":
            await ctx.send("Enter the footer text:")
            footer_text_msg = await self.bot.wait_for('message', check=check_author)
            footer_text = footer_text_msg.content

            await ctx.send("Enter the footer icon URL (optional):")
            footer_icon_url_msg = await self.bot.wait_for('message', check=check_author)
            if footer_icon_url_msg.content:
                footer_icon_url = footer_icon_url_msg.content

        # Ask if embed should have a button
        await ctx.send("Should the embed have a button? (yes/no)")
        button_choice_msg = await self.bot.wait_for('message', check=check_author)
        button_choice = button_choice_msg.content.lower()

        button_label = None
        button_url = None

        if button_choice == "yes":
            await ctx.send("Enter the button label:")
            button_label_msg = await self.bot.wait_for('message', check=check_author)
            button_label = button_label_msg.content

            await ctx.send("Enter the button URL:")
            button_url_msg = await self.bot.wait_for('message', check=check_author)
            button_url = button_url_msg.content

        # Ask if embed should have a thumbnail
        await ctx.send("Should the embed have a thumbnail? (yes/no)")
        thumbnail_choice_msg = await self.bot.wait_for('message', check=check_author)
        thumbnail_choice = thumbnail_choice_msg.content.lower()

        thumbnail_url = None

        if thumbnail_choice == "yes":
            await ctx.send("Enter the thumbnail URL:")
            thumbnail_url_msg = await self.bot.wait_for('message', check=check_author)
            thumbnail_url = thumbnail_url_msg.content

        # Ask if embed should have an image
        await ctx.send("Should the embed have an image? (yes/no)")
        image_choice_msg = await self.bot.wait_for('message', check=check_author)
        image_choice = image_choice_msg.content.lower()

        image_url = None

        if image_choice == "yes":
            await ctx.send("Enter the image URL:")
            image_url_msg = await self.bot.wait_for('message', check=check_author)
            image_url = image_url_msg.content

        # Create the embed
        embed = discord.Embed(title=title, description=description, color=0x4c5264)

        if author_name:
            embed.set_author(name=author_name, icon_url=author_icon_url)

        if footer_text:
            embed.set_footer(text=footer_text, icon_url=footer_icon_url)

        if button_label and button_url:
            embed.add_field(name="Links", value=f"[{button_label}]({button_url})", inline=False)

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        if image_url:
            embed.set_image(url=image_url)

        # Send the embed
        await ctx.send(embed=embed)

    @commands.command(name="roll", usage="roll (sides)", description="Rolls a dice using miro", aliases=["dice"])
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def roll(self, ctx, sides: int = 6):
        """Roll a dice"""

        await ctx.reply(f"Rolling a **{sides}-sided** dice..")
        await asyncio.sleep(1)

        await ctx.reply(f"The dice landed on **🎲 {random.randint(1, sides)}**")



    @commands.command(
        name="scrapbook",
        usage="scrap (text)",
        example="miro so sexy",
        aliases=["scrap"],
        descripotion="Make a Scrap book with given text",
    )
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def scrapbook(self, ctx, *, text: str):

        if len(text) > 20:
            return await ctx.reply("Your text can't be longer than **20 characters**")

        async with ctx.typing():
            response = await self.bot.session.get(
                "https://api.jeyy.xyz/image/scrapbook",
                params=dict(text=text),
            )
            if response.status != 200:
                return await ctx.reply("Couldn't **scrapbook** text - Try again later!")

            image = await response.read()
            buffer = io.BytesIO(image)
            await ctx.reply(
                file=discord.File(
                    buffer,
                    filename=f"MiroScrapbook{(text)}.gif",
                )
            )




async def setup(bot):
    await bot.add_cog(fun(bot))
