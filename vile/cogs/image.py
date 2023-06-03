import discord, os, sys, asyncio, aiohttp, urllib, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class image(commands.Cog):
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

    @commands.command()
    async def drake(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/drake/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def fry(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/fry/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def bihw(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/bihw/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def cheems(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/cheems/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def fpw(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/fpw/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def mb(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/mb/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def mordor(self, ctx, text1: str = "", text2: str = ""):

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(
            url=f'https://api.memegen.link/images/mordor/{text1.replace(" ", "%20")}/{text2.replace(" ", "%20")}.png'
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def ps4(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        embed = discord.Embed(color=0x2F3136)
        request = (
            await (
                await self.bot.session.get(
                    f'https://reactselfbot.cc/api/generation.php?type=ps4&url={str(user.display_avatar).replace(".webp", ".png")}'
                )
            ).json()
        )["url"]
        embed.set_image(url=f"{request}")
        await ctx.reply(embed=embed)

    @commands.command()
    async def thanos(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        embed = discord.Embed(color=0x2F3136)
        request = await self.bot.session.get(
            f'https://reactselfbot.cc/api/generation.php?type=thanos&url={str(user.display_avatar).replace(".webp", ".png")}'
        )
        request = await request.json()
        request = request["url"]
        embed.set_image(url=f"{request}")
        await ctx.reply(embed=embed)

    @commands.command()
    async def moustache(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        embed = discord.Embed(color=0x2F3136)
        request = (
            await (
                await self.bot.session.get(
                    f'https://reactselfbot.cc/api/generation.php?type=moustache&url={str(user.display_avatar).replace(".webp", ".png")}'
                )
            ).json()
        )["url"]
        embed.set_image(url=f"{request}")
        await ctx.reply(embed=embed)

    @commands.command()
    async def glitch(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        embed = discord.Embed(color=0x2F3136)
        request = (
            await (
                await self.bot.session.get(
                    f'https://reactselfbot.cc/api/generation.php?type=glitch&url={str(user.display_avatar).replace(".webp", ".png")}'
                )
            ).json()
        )["url"]
        embed.set_image(url=f"{request}")
        await ctx.reply(embed=embed)

    @commands.command()
    async def dungeon(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        embed = discord.Embed(color=0x2F3136)
        request = (
            await (
                await self.bot.session.get(
                    f'https://reactselfbot.cc/api/generation.php?type=dungeon&url={str(user.display_avatar).replace(".webp", ".png")}'
                )
            ).json()
        )["url"]
        embed.set_image(url=f"{request}")
        await ctx.reply(embed=embed)

    @commands.command()
    async def challenger(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        embed = discord.Embed(color=0x2F3136)
        request = (
            await (
                await self.bot.session.get(
                    f'https://reactselfbot.cc/api/generation.php?type=challenger&url={str(user.display_avatar).replace(".webp", ".png")}'
                )
            ).json()
        )["url"]
        embed.set_image(url=f"{request}")
        await ctx.reply(embed=embed)

    @commands.command(name="3000years", aliases=["3kyears"])
    async def threethousand_years(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        embed = discord.Embed(color=0x2F3136)
        request = (
            await (
                await self.bot.session.get(
                    f'https://reactselfbot.cc/api/generation.php?type=3000years&url={str(user.display_avatar).replace(".webp", ".png")}'
                )
            ).json()
        )["url"]
        embed.set_image(url=f"{request}")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(aliases=["revavatar", "ra"])
    async def reverseavatar(
        self, ctx, *, user: typing.Union[discord.Member, discord.User] = None
    ):

        user = ctx.author if not user else user
        embed = discord.Embed(
            color=0x2F3136,
            title="Reverse Avatar",
            description=f"[results](https://images.google.com/searchbyimage?image_url={user.display_avatar}) for {user.mention}'s avatar.",
        )
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ocr"])
    async def opticalcharacterrecognition(self, ctx, image: discord.Attachment):

        await ctx.typing()
        if isinstance(image, discord.Attachment):

            #payload = {
            #    "url": image.url,
            #    "isOverlayRequired": False,
            #    "apikey": "K88991768788957",
            #    "language": "eng",
            #}
            #x = await self.bot.session.post(
            #    "https://api.ocr.space/parse/image", data=payload
            #)

            #x = await x.read()
            #await ctx.reply(
            #    embed=discord.Embed(
            #        color=0x2F3136,
            #        description=json.loads(x.decode())["ParsedResults"][0][
            #            "ParsedText"
            #        ],
            #    )
            #)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://api.rival.rocks/media/ocr',
                    headers={
                        'api-key': self.bot.rival_api
                    },
                    params={
                        'url': image.url
                    }
                ) as resp:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=0x2f3136,
                            description=eval(await resp.text())
                        )
                    )

        elif isinstance(image, str):

            #payload = {
            #    "url": __import__("yarl").URL(image),
            #    "isOverlayRequired": False,
            #    "apikey": "K88991768788957",
            #    "language": "eng",
            #}
            #x = await self.bot.session.post(
            #    "https://api.ocr.space/parse/image", data=payload
            #)

            #x = await x.read()
            #await ctx.reply(
            #    embed=discord.Embed(
            #        color=0x2F3136,
            #        description=json.loads(x.decode())["ParsedResults"][0][
            #            "ParsedText"
            #        ],
            #    )
            #)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://api.rival.rocks/media/ocr',
                    headers={
                        'api-key': self.bot.rival_api
                    },
                    params={
                        'url': image
                    }
                ) as resp:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=0x2f3136,
                            description=eval(await resp.text())
                        )
                    )

    @commands.hybrid_group(aliases=["pfps"], invoke_without_command=True)
    async def pfp(self, ctx):
        ...

    @pfp.command(name="boypfp")
    async def pfp_boypfp(self, ctx):

        await ctx.typing()
        embeds = []
        images = await utils.getwhi(
            random.choice(["boy pfps", "boy pfp", "boypfp", "boypfps"])
        )
        async for image in utils.aiter(images):
            embed = discord.Embed(color=0x2F3136)
            embed.set_image(url=image)
            embeds.append(embed)

        paginator = utils.paginator(self.bot, embeds, ctx, timeout=30, invoker=None)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @pfp.command(name="girlpfp")
    async def pfp_girlpfp(self, ctx):

        await ctx.typing()
        embeds = []
        images = await utils.getwhi(
            random.choice(["girl pfps", "girl pfp", "girlpfp", "girlpfps"])
        )
        async for image in utils.aiter(images):
            embed = discord.Embed(color=0x2F3136)
            embed.set_image(url=image)
            embeds.append(embed)

        paginator = utils.paginator(self.bot, embeds, ctx, timeout=30, invoker=None)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.command(aliases=["ss"])
    async def screenshot(self, ctx, *, link: str):

        if not link.startswith("https://") or not link.startswith("http://"):
            link = "https://" + link
        await ctx.typing()
        api = f"https://processor.screenshotson.click/screenshot?key=819d482a7a9f7efc&url={link}&width=3840&height=2160&fullPage=false&quality=70&loadEvent=domcontentloaded&fileType=png"
        import io

        x = await self.bot.session.get(api)
        x = await x.read()
        x = io.BytesIO(x)
        await ctx.reply(file=discord.File(x, filename="unknown.png"))

    @commands.command(
        aliases=["removebg", "rbg", "removebackground", "transparentimg", "transimg"]
    )
    @commands.max_concurrency(1, commands.BucketType.default, wait=True)
    async def transparent(self, ctx, url: str = None):

        import requests, logging

        if not url:
            if not ctx.message.attachments:
                return
            url = ctx.message.attachments[0].url

        API_ENDPOINT = "https://api.remove.bg/v1.0/removebg"

        class RemoveBg(object):
            def __init__(self, api_key):

                self.__api_key = api_key

            def _output_file(self, response, new_file_name):

                if response.status_code == requests.codes.ok:
                    with open(new_file_name, "wb") as removed_bg_file:
                        removed_bg_file.write(response.content)
                else:
                    error_reason = response.json()["errors"][0]["title"].lower()
                    logging.error(
                        "Unable to save %s due to %s", new_file_name, error_reason
                    )

            def _check_arguments(self, size, type, type_level, format, channels):
                """Check if arguments are valid."""
                if size not in [
                    "auto",
                    "preview",
                    "small",
                    "regular",
                    "medium",
                    "hd",
                    "full",
                    "4k",
                ]:
                    raise ValueError("size argument wrong")

                if type not in [
                    "auto",
                    "person",
                    "product",
                    "animal",
                    "car",
                    "car_interior",
                    "car_part",
                    "transportation",
                    "graphics",
                    "other",
                ]:
                    raise ValueError("type argument wrong")

                if type_level not in ["none", "latest", "1", "2"]:
                    raise ValueError("type_level argument wrong")

                if format not in ["jpg", "zip", "png", "auto"]:
                    raise ValueError("format argument wrong")

                if channels not in ["rgba", "alpha"]:
                    raise ValueError("channels argument wrong")

            def remove_background_from_img_url(
                self,
                img_url,
                size="regular",
                type="auto",
                type_level="none",
                format="auto",
                roi="0 0 100% 100%",
                crop=None,
                scale="original",
                position="original",
                channels="rgba",
                shadow=False,
                semitransparency=True,
                bg=None,
                bg_type=None,
                new_file_name="transparent.png",
            ):

                self._check_arguments(size, type, type_level, format, channels)

                files = {}

                data = {
                    "image_url": img_url,
                    "size": size,
                    "type": type,
                    "type_level": type_level,
                    "format": format,
                    "roi": roi,
                    "crop": "true" if crop else "false",
                    "crop_margin": crop,
                    "scale": scale,
                    "position": position,
                    "channels": channels,
                    "add_shadow": "true" if shadow else "false",
                    "semitransparency": "true" if semitransparency else "false",
                }

                if bg_type == "path":
                    files["bg_image_file"] = open(bg, "rb")
                elif bg_type == "color":
                    data["bg_color"] = bg
                elif bg_type == "url":
                    data["bg_image_url"] = bg

                response = requests.post(
                    API_ENDPOINT, data=data, headers={"X-Api-Key": self.__api_key}
                )
                response.raise_for_status()

                self._output_file(response, new_file_name)

        x = RemoveBg(api_key=random.choice(self.bot.removebg_api))
        x.remove_background_from_img_url(url)
        await ctx.reply(file=discord.File("transparent.png"))
        os.remove("transparent.png")

    @commands.hybrid_command(aliases=["whi"])
    async def weheartit(self, ctx, *, query: str):

        await ctx.typing()
        x = await utils.getwhi(query)
        embeds = []
        num = 0
        async for image in utils.aiter(x):
            num += 1
            embeds.append(
                discord.Embed(description=f"results for {query}")
                .set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                .set_footer(text=f"{num}/{len(x)}")
                .set_image(url=image)
            )

            paginator = utils.paginator(self.bot, embeds, ctx, timeout=30, invoker=None)
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()


async def setup(bot):
    await bot.add_cog(image(bot))
