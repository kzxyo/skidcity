import discord, os, sys, asyncio, gtts, datetime, textwrap, pathlib, traceback, json, typing, time, random, aiohttp, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from gtts import gTTS
from modules import utils
from wordcloud import WordCloud

NUM_TO_STORE = 1000
snipe_limit = NUM_TO_STORE
snipes = {}
deleted_msgs = {}
reaction = {}
restore = {}
edited_msgs = {}
emsgat = {}

sc = {}
si = {}
sav = {}
sa = {}
st = {}

esa = {}
esav = {}
esbefore = {}
esafter = {}
est = {}


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
        self.av = "https://cdn.discordapp.com/attachments/989422588340084757/1008195005317402664/vile.png"

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):

        datacheck = self.bot.db("nodata")
        if datacheck.get(str(message.author.id)):
            if datacheck.get(str(message.author.id)).get("data") == False:
                return

        ch_id = message.channel.id
        try:
            if not message.author.bot:
                sc[message.channel.id] = message.content
                try:
                    si[message.channel.id] = message.attachments[0]
                except:
                    pass
                sa[message.channel.id] = message.author
                sav[message.channel.id] = message.author.avatar
                st[message.channel.id] = datetime.now()
                if message.content:
                    if ch_id not in deleted_msgs:
                        deleted_msgs[ch_id] = []

                    deleted_msgs[ch_id].append(message)
                else:
                    if ch_id not in deleted_msgs:
                        deleted_msgs[ch_id] = []
                    deleted_msgs[ch_id].append(message)

                if len(deleted_msgs[ch_id]) > snipe_limit:
                    deleted_msgs[ch_id].pop(0)

                modlog = utils.read_json("modlog")

            try:
                if modlog[str(message.guild.id)] != None:

                    embed = discord.Embed(
                        description=f"msg by {message.author.mention} deleted in <#{message.channel.id}>\nmsg deleted <t:{round(st[message.channel.id].timestamp())}:R>",
                        timestamp=datetime.now(),
                    )
                    embed.set_author(
                        name=sa[message.channel.id], icon_url=sav[message.channel.id]
                    )
                    embed.add_field(
                        name="msg content",
                        value=f"***{sa[message.channel.id]}***: {sc[message.channel.id]}",
                    )
                    try:
                        embed.set_image(url=si[message.channel.id].proxy_url)
                    except:
                        pass
                    embed.set_footer(
                        text=f"user ID: {sa[message.channel.id].id}",
                        icon_url=None,
                    )
                    await self.bot.get_channel(modlog[str(message.guild.id)]).send(
                        embed=embed
                    )

                else:

                    pass

            except:
                pass
        except:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        try:

            datacheck = self.bot.db("nodata")
            if datacheck.get(str(after.author.id)):
                if datacheck.get(str(after.author.id)).get("data") == False:
                    return
            ch_id = before.channel.id

            if not before.author.bot:
                channel = before.channel
                esbefore[ch_id] = before.content
                esafter[ch_id] = after.content
                esa[ch_id] = before.author
                esav[ch_id] = before.author.avatar
                est[ch_id] = datetime.now()
                if before.content and after.content:
                    if ch_id not in edited_msgs:
                        edited_msgs[ch_id] = []
                    edited_msgs[ch_id].append((before, after))
                    emsgat[ch_id] = datetime.now()
                else:
                    if ch_id not in edited_msgs:
                        edited_msgs[ch_id] = []
                    edited_msgs[ch_id].append((before, after))
                    emsgat[ch_id] = datetime.now()
                try:
                    if len(edited_msgs[ch_id]) > snipe_limit:
                        edited_msgs[ch_id].pop(0)
                except:
                    pass

                modlog = utils.read_json("modlog")

            try:
                if modlog[str(before.guild.id)] != None:

                    try:
                        embed = discord.Embed(
                            description=f"msg by {before.author.mention} edited in <#{before.channel.id}>\nmsg edited <t:{round(est[before.channel.id].timestamp())}:R>",
                            timestamp=datetime.now(),
                        )
                        embed.set_author(
                            name=esa[before.channel.id],
                            icon_url=esav[before.channel.id],
                        )
                        embed.add_field(
                            name="before edit",
                            value=f"**{esa[before.channel.id]}**: {esbefore[before.channel.id]}",
                        )
                        embed.add_field(
                            name="after edit",
                            value=f"**{esa[before.channel.id]}**: {esafter[before.channel.id]}",
                            inline=False,
                        )
                        embed.set_footer(
                            text=f"user ID: {esa[before.channel.id].id}",
                            icon_url=None,
                        )
                        await self.bot.get_channel(modlog[str(before.guild.id)]).send(
                            embed=embed
                        )

                    except Exception as e:
                        print(e)
            except:
                pass

            try:
                if not after.author.bot:
                    if after.author.guild_permissions.administrator != False:
                        db = utils.read_json("chatfilter")
                        words = after.content.lower().replace("\n", " ").split(" ")
                        async for word in utils.aiter(words):
                            if word in db[str(after.guild.id)]:
                                await after.reply(
                                    embed=discord.Embed(
                                        color=utils.color("fail"),
                                        description=f"{utils.emoji('fail')} {after.author.mention} watch your mouth, that word is **filtered** in this guild",
                                    )
                                )
                                try:
                                    await after.delete()
                                except:
                                    pass
            except:
                pass
        except Exception as e:
            pass

        try:
            await self.bot.process_commands(after)
        except:
            pass

    @commands.hybrid_command(name="snipe", aliases=["s"])
    async def snipe(self, ctx: commands.Context, limit: int = 1):

        if limit > snipe_limit:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** current **snipe limit** is {snipe_limit}",
                )
            )
        try:
            msgs: list[discord.Message] = deleted_msgs[ctx.channel.id][::-1]  # [:limit]
            embeds = []
            num = 0
            async for msg in utils.aiter(msgs):
                num += 1
                cf = 0
                try:
                    chatfilter = utils.read_json("chatfilter")[str(ctx.guild.id)]
                    words = msg.content.split(" ")
                    async for word in utils.aiter(words):
                        if word in chatfilter:
                            cf += 1
                except:
                    pass
                # if cf != 0: return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.fail} {ctx.author.mention}**:** you can't snipe filtered messages"))
                snipe_embed = (
                    discord.Embed(color=ctx.author.color)
                    .set_author(name=msg.author, icon_url=msg.author.display_avatar)
                    .set_footer(
                        text=f"deleted {utils.moment(msg.created_at)} ago | {num}/{len(deleted_msgs[ctx.channel.id])}",
                        icon_url=None,
                    )
                )
                if cf != 0:
                    snipe_embed.description = "CENSORED MESSAGE"
                else:
                    if msg.content:
                        snipe_embed.description = msg.content
                    if msg.attachments:
                        snipe_embed.set_image(url=msg.attachments[0].proxy_url)
                embeds.append(snipe_embed)

            from modules import paginator as pg

            paginator = pg.Paginator(self.bot, embeds, ctx, timeout=30, invoker=None)
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            await paginator.start()

        except KeyError:
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** no recently **deleted** msgs",
                )
            )

    @commands.hybrid_command(name="editsnipe", aliases=["es"])
    async def editsnipe(self, ctx: commands.Context, limit: int = 1):

        if limit > snipe_limit:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** current **snipe limit** is {snipe_limit}",
                )
            )
        try:
            msgs = edited_msgs[ctx.channel.id][::-1]  # [:limit]
            embeds = []
            num = 0
            async for msg in utils.aiter(msgs):
                num += 1
                cf = 0
                try:
                    chatfilter = utils.read_json("chatfilter")[str(ctx.guild.id)]
                    words = msg.content.split(" ")
                    async for word in utils.aiter(words):
                        if word in chatfilter:
                            cf += 1
                except:
                    pass
                editsnipe_embed = (
                    discord.Embed(color=ctx.author.color)
                    .set_author(
                        name=msg[0].author, icon_url=msg[0].author.display_avatar
                    )
                    .set_footer(
                        text=f"edited {utils.moment(emsgat[ctx.channel.id])} {'ago' if 'ago' not in utils.moment(emsgat[ctx.channel.id]) else ''} | {num}/{len(edited_msgs[ctx.channel.id])}",
                        icon_url=None,
                    )
                )
                if cf != 0:
                    editsnipe_embed.description = "CENSORED MESSAGE"
                else:
                    if msg[0].content:
                        editsnipe_embed.description = msg[0].content
                    if msg[0].attachments:
                        editsnipe_embed.set_image(url=msg[0].attachments[0].proxy_url)
                embeds.append(editsnipe_embed)

            from modules import paginator as pg

            paginator = pg.Paginator(self.bot, embeds, ctx, timeout=30, invoker=None)
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            await paginator.start()

            # await ctx.reply(embed=editsnipe_embed)

        except KeyError:
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** no recently **edited** msgs",
                )
            )

    @commands.hybrid_command()
    async def kiss(self, ctx, user: discord.Member = None):

        if not user:

            embed = discord.Embed(
                color=utils.color("main"),
                description="**You fr wanna kiss yourself??**",
                timestamp=datetime.now(),
            )
            embed.set_footer(
                text="you must be lonely",
                icon_url=None,
            )
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            return await ctx.send(embed=embed)

        elif user == ctx.author:
            return await ctx.reply("here, have a kiss :heart:")

        else:

            embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            embed.description = f"***{ctx.author.name} kissed {user.name}***"
            embed.set_image(
                url=f'https://purrbot.site/img/sfw/kiss/gif/kiss_{random.choice(["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "016"])}.gif'
            )
            embed.set_author(
                name=f"{ctx.author if user == None else user}",
                icon_url=f"{ctx.author.avatar if user == None else user.avatar}",
            )
            await ctx.reply(embed=embed)

    @commands.hybrid_command()
    async def hug(self, ctx, user: discord.Member = None):

        if not user:

            embed = discord.Embed(
                color=utils.color("main"),
                description="**You fr wanna hug yourself??**",
                timestamp=datetime.now(),
            )
            embed.set_footer(
                text="you must be lonely",
                icon_url=None,
            )
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            return await ctx.send(embed=embed)

        elif user == ctx.author:
            return await ctx.reply("here, have a hug :heart:")

        else:

            embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            embed.description = f"***{ctx.author.name} kissed {user.name}***"
            embed.set_image(
                url=f'https://purrbot.site/img/sfw/hug/gif/hug_{random.choice(["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "016"])}.gif'
            )
            embed.set_author(
                name=f"{ctx.author if user == None else user}",
                icon_url=f"{ctx.author.avatar if user == None else user.avatar}",
            )
            await ctx.reply(embed=embed)

    @commands.hybrid_command()
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

    @commands.hybrid_command()
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def pack(self, ctx, user: discord.Member = commands.Author):

        if user == ctx.author:
            embed = discord.Embed(
                color=utils.color("main"),
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
            # embed = discord.Embed(color=utils.color('main'), description=f"{ctx.author}: {random.choice(cc)}", timestamp=datetime.now())
            # embed.set_footer(text=f"{user} just got violated", icon_url=None)
            # embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
            # await ctx.reply(embed=embed)
            random.shuffle(cc)
            await utils.pack(ctx, cc, user)

    @commands.hybrid_command(aliases=["chatdump", "chatdumper"])
    async def dumpchat(self, ctx, amount_of_messages: int = 50):

        try:
            if amount_of_messages > 100:
                await ctx.reply("slow down tf")
            elif amount_of_messages == 0:
                await ctx.reply("bro what")
            else:
                try:
                    with open(f"./chat_history.txt", "w", encoding="utf-8") as f:

                        lines = []
                        async for message in ctx.channel.history(
                            limit=amount_of_messages
                        ):

                            if len(message.content) > 1:
                                if message.content not in lines:
                                    lines.append(
                                        f"[{datetime.now().strftime('%H:%M:%S')}] {message.author}: {message.content}\n"
                                    )

                            try:
                                async for attachment in utils.aiter(
                                    message.attachments
                                ):
                                    if attachment.proxy_url not in lines:
                                        lines.append(
                                            f"[{datetime.now().strftime('%H:%M:%S')}] {message.author}: {attachment.proxy_url}\n"
                                        )
                            except Exception:
                                print("something went wrong, here is some info:")
                                traceback.print_exc()
                                pass

                            try:
                                async for embed in utils.aiter(message.embeds):
                                    embed_dict = embed.to_dict()
                                    if embed_dict not in lines:
                                        lines.append(
                                            f"[{datetime.now().strftime('%H:%M:%S')}] {message.author}: {embed_dict}\n"
                                        )
                            except Exception as e:
                                pass

                            f.writelines("\n".join(list(set(lines))))
                except Exception as e:
                    traceback.print_exc()

                await ctx.send(
                    "generated chat dump", file=discord.File(f"./chat_history.txt")
                )

                os.remove("./chat_history.txt")
        except:
            pass

    @commands.hybrid_command(aliases=["fakeidentity"])
    async def fakedata(self, ctx, locale: str = "en"):

        try:
            request = await self.bot.session.get(
                f"https://randomuser.me/api/?format=json"
            )
            response = await request.json()
            data = response["results"][0]
            gender = data["gender"]
            name = f"{data['name']['first']} {data['name']['last']}"
            street = f"{data['location']['street']['number']} {data['location']['street']['name']}"
            city = data["location"]["city"]
            state = data["location"]["state"]
            country = data["location"]["country"]
            postcode = data["location"]["postcode"]
            phone = data["phone"]
            email = data["email"]
            embed = discord.Embed(color=utils.color("main"), timestamp=datetime.now())
            embed.add_field(name=f"Name", value=f"{name}", inline=True)
            embed.add_field(name=f"Gender", value=f"{gender}", inline=True)
            embed.add_field(name=f"Street", value=f"{street}", inline=True)
            embed.add_field(name=f"Zipcode", value=f"{postcode}", inline=True)
            embed.add_field(name=f"City", value=f"{city}", inline=True)
            embed.add_field(name=f"State", value=f"{state}", inline=True)
            embed.add_field(name=f"Country", value=f"{country}", inline=True)
            embed.add_field(name=f"Phone", value=f"{phone}", inline=True)
            embed.add_field(name=f"E-Mail", value=f"{email}", inline=True)
            embed.set_thumbnail(url=f"{data['picture']['large']}")
            embed.set_author(
                name="fake identity", icon_url=self.bot.user.display_avatar
            )
            embed.set_footer(
                text="vile",
                icon_url=None,
            )
            await ctx.reply(embed=embed)

        except:
            pass

    @commands.hybrid_command(aliases=["randomcolor"])
    async def randomhex(self, ctx):

        hexxx = await (
            await self.bot.session.get("https://api.popcat.xyz/randomcolor")
        ).json()
        hexxx = hexxx["hex"]
        data = await self.bot.session.get(
            f'https://api.alexflipnote.dev/colour/{hexxx.strip("#")}'
        )
        data = await data.json()

        shades = (
            str(
                [data["shade"][0], data["shade"][1], data["shade"][2], data["shade"][3]]
            )
            .replace("[", "")
            .replace("'", "")
            .replace("]", "")
        )
        hexx = data["hex"]
        rgb = data["rgb"]
        name = data["name"]
        image = data["image"]
        grad = data["image_gradient"]
        brightness = data["brightness"]
        embed = discord.Embed(color=eval(f"0x{hexxx}"))
        embed.set_author(name=name, icon_url=image)
        embed.set_thumbnail(url=image)
        embed.set_image(url=grad)
        embed.add_field(name="RGB", value=rgb)
        embed.add_field(name="Hex", value=hexx)
        embed.add_field(name="Brightness", value=brightness)
        embed.add_field(name="Shades", value=f"```YAML\n\n{shades}```")

        await ctx.reply(embed=embed)

    @commands.hybrid_command()
    async def lyrics(self, ctx, *, song: str = None):

        if not song:

            e = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            e.set_footer(
                text="fun",
                icon_url=None,
            )
            e.set_author(name="lyrics", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** get the lyrics of a song",
                inline=False,
            )
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ,lyrics <song name>\n{self.reply} example: ,lyrics new drank",
                inline=False,
            )
            return await ctx.reply(embed=e)

        data = await self.bot.session.get(
            f'https://api.popcat.xyz/lyrics?song={song.replace(" ", "+")}'
        )
        data = await data.json()
        embed = discord.Embed(color=utils.color("main"))
        embed.set_footer(
            text=data["artist"],
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        embed.set_author(name=data["title"], icon_url=data["image"])
        embed.description = data["lyrics"]
        embed.set_image(url=data["image"])
        embed.set_thumbnail(url=data["image"])
        await ctx.reply(embed=embed)

    @commands.hybrid_command()
    async def tts(self, ctx, lang, *, text: str):

        tts = gTTS(text, lang=lang)
        filename = f"{text}.mp3"
        tts.save(filename)
        await ctx.send(file=discord.File(fp=filename, filename=filename))
        if os.path.exists(filename):
            os.remove(filename)

    @commands.hybrid_command(aliases=["uf", "fact"])
    async def uselessfact(self, ctx):

        data = await self.bot.session.get(
            f"https://uselessfacts.jsph.pl/random.json?language=en"
        )
        data = await data.json()
        await ctx.reply(data["text"])

    @commands.hybrid_command()
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

    @commands.hybrid_command()
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

    @commands.command()
    async def spotify(self, ctx, user: discord.Member = None):

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
                    color=0xED4245,
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

    @commands.hybrid_command(aliases=["wc"])
    @commands.max_concurrency(1, commands.BucketType.default, wait=True)
    async def wordcloud(self, ctx, limit: int = 100):

        if limit > 1000:
            return await ctx.reply("nigga no")
        await ctx.typing()
        text = [message.content async for message in ctx.channel.history(limit=limit)]
        wc = WordCloud(mode="RGBA", background_color=None, height=400, width=700)
        wc.generate(" ".join(text))
        wc.to_file(filename=f"{ctx.author.id}.png")

        await ctx.send(file=discord.File(f"{ctx.author.id}.png"))
        os.remove(f"{ctx.author.id}.png")

    @commands.command()
    async def uwu(self, ctx):

        if ctx.message.reference:
            message = ctx.message.reference.resolved
        else:
            message = [msg async for msg in ctx.channel.history(limit=2)][1]

        from utils.converter import send_uwu

        await ctx.reply(send_uwu(message.content))

    @commands.command(
        name='roleplay',
        aliases=['rp'],
        syntax=',roleplay (action) (user)',
        example=',roleplay hug glory'
    )
    async def roleplay(self, ctx, action: typing.Literal['hug', 'cuddle', 'tickle', 'kiss', 'feed', 'pat', 'slap'], user: typing.Optional[discord.Member]=None):
            
        verb: str
        user='undefined' if not user else user.mention
            
        match action:
            case 'hug':
                verb='hugs'
            case 'cuddle':
                verb='cuddles'
            case 'tickle':
                verb='tickles'
            case 'kiss':
                verb='kisses'
            case 'feed':
                verb='feeds'
            case 'pat':
                verb='pats'
            case 'slap':
                verb='slaps'
                
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://nekos.best/api/v2/{action}') as resp:
                response=utils.obj((await resp.json())['results'][0])
            await session.close()
            
        img=response.url
        embed=discord.Embed(color=self.bot.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.set_image(url=img)
        embed.description=f'{ctx.author.mention} kisses {user}'
        
        return await ctx.reply(embed=embed)
        

async def setup(bot):

    await bot.add_cog(fun(bot))
