import discord, os, aiohttp, typing, json, random
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
        self.av = "https://cdn.discordapp.com/attachments/1116443743831199814/1118245305352200332/Cherry_Blossoms.png"


    @commands.hybrid_command(aliases=["revavatar", "ra"])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def reverseavatar(
        self, ctx, *, user: typing.Union[discord.Member, discord.User] = None
    ):
        user = ctx.author if not user else user
        embed = discord.Embed(
            color=0x4c5264,
            title="Reverse Avatar",
            description=f"[results](https://images.google.com/searchbyimage?image_url={user.display_avatar}) for {user.mention}'s avatar.",
        )
        await ctx.reply(embed=embed)

    @commands.command(name = "opticalcharacterrecognition", description = "Return text off image",aliases=['ocr'], usage = "ocr [attachment]")
    @commands.cooldown(1, 8, commands.BucketType.guild)
    async def opticalcharacterrecognition(self, ctx, image: discord.Attachment):
        await ctx.typing()
        if isinstance(image, discord.Attachment):
            payload = {
                "url": image.url,
                "isOverlayRequired": False,
                "apikey": "K88991768788957",
                "language": "eng",
            }
            x = await self.bot.session.post(
                "https://api.ocr.space/parse/image", data=payload
            )

            x = await x.read()
            await ctx.reply(
                embed=discord.Embed(
                    color=0x4c5264,
                    description=json.loads(x.decode())["ParsedResults"][0][
                        "ParsedText"
                    ],
                )
            )

        elif isinstance(image, str):
            payload = {
                "url": __import__("yarl").URL(image),
                "isOverlayRequired": False,
                "apikey": "K88991768788957",
                "language": "eng",
            }
            x = await self.bot.session.post(
                "https://api.ocr.space/parse/image", data=payload
            )

            x = await x.read()
            await ctx.reply(
                embed=discord.Embed(
                    color=0x4c5264,
                    description=json.loads(x.decode())["ParsedResults"][0][
                        "ParsedText"
                    ],
                )
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.rival.rocks/media/ocr",
                    headers={"api-key": self.bot.rival_api},
                    params={"url": image},
                ) as resp:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=0x4c5264, description=eval(await resp.text())
                        )
                    )


    @commands.command(
        aliases=["removebg", "rbg", "removebackground", "transparentimg", "transimg"]
    )
    @commands.cooldown(1, 11, commands.BucketType.guild)
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


async def setup(bot):
    await bot.add_cog(image(bot))
