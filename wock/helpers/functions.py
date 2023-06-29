import asyncio
import json
import random
import string
import subprocess
import urllib
import zlib

from datetime import datetime
from functools import partial, wraps
from io import BytesIO
from math import sqrt
from pathlib import Path

import aiohttp
import dateparser
import discord
import imagehash as ih

from discord.ext import commands
from PIL import Image
from wordcloud import STOPWORDS, WordCloud
from xxhash import xxh64_hexdigest

from helpers import tuuid
from helpers.wock import cache


# from plotly.io import pio


try:
    config = json.loads(open("config.json", "r").read())
except FileNotFoundError:
    config = json.loads(open("../config.json", "r").read())


def config_color(color: str):
    return discord.Color(int(config["styles"][color].get("color").replace("#", ""), 16))


def get_color(value: str):
    if value.lower() in ("random", "rand", "r"):
        return discord.Color.random()
    elif value.lower() in ("invisible", "invis"):
        return discord.Color.from_str("#2F3136")
    elif value.lower() in ("blurple", "blurp"):
        return discord.Color.blurple()
    elif value.lower() in ("black", "negro"):
        return discord.Color.from_str("#000001")

    value = COLORS.get(str(value).lower()) or value
    try:
        color = discord.Color(int(value.replace("#", ""), 16))
    except ValueError:
        return None

    if not color.value > 16777215:
        return color
    else:
        return None


def get_language(value: str):
    value = value.lower()
    if not value in LANGUAGES.keys():
        if not value in LANGUAGES.values():
            return None
        else:
            return value
    else:
        return LANGUAGES[value]


def get_timestamp(value: str):
    return dateparser.parse(str(value))


def unique_id(lenght: int = 6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=lenght))


def hash(text: str):
    return xxh64_hexdigest(str(text))


def link(text: str, link: str):
    return f"**[{text}]({link})**"


def format_duration(duration: int, ms: bool = True):
    if ms:
        seconds = int((duration / 1000) % 60)
        minutes = int((duration / (1000 * 60)) % 60)
        hours = int((duration / (1000 * 60 * 60)) % 24)
    else:
        seconds = int(duration % 60)
        minutes = int((duration / 60) % 60)
        hours = int((duration / (60 * 60)) % 24)

    if any((hours, minutes, seconds)):
        result = ""
        if hours:
            result += f"{hours:02d}:"
        result += f"{minutes:02d}:"
        result += f"{seconds:02d}"
        return result
    else:
        return "00:00"


def format_uri(text: str):
    return urllib.parse.quote(text, safe="")


def get_commit():
    file = Path(".git", "refs", "heads", "main")
    if file.exists():
        return file.read_text().strip()[:7]
    else:
        return "unknown"


def per_day(dt: datetime, uses: int):
    days = (discord.utils.utcnow() - dt).total_seconds() / 86400
    if days := int(days):
        return uses / days
    else:
        return uses


##
def async_executor():
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            task = partial(func, *args, **kwargs)
            return asyncio.get_event_loop().run_in_executor(None, task)

        return inner

    return outer


@async_executor()
def run_shell(command: str):
    return subprocess.run(command, shell=True, capture_output=True).stdout.decode()


@async_executor()
def image_hash(image: BytesIO):
    if isinstance(image, bytes):
        image = BytesIO(image)

    result = str(ih.average_hash(image=Image.open(image), hash_size=8))
    if result == "0000000000000000":
        return unique_id(16)
    else:
        return result


@async_executor()
def _extract_color(buffer: BytesIO):
    try:
        rgb = (Image.open(buffer).convert("RGBA").resize((1, 1), resample=0).getpixel((0, 0)))[:3]
        _hex = "%02x%02x%02x" % rgb
    except:
        return discord.Color.default()

    return discord.Color(int(_hex, 16))


async def extract_color(redis: any, url: str):
    key = f"palette:{xxh64_hexdigest(url)}"
    palette = await redis.get(key)
    if not palette:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                try:
                    buffer = BytesIO(await response.read())
                except:
                    return discord.Color.default()

        palette = await _extract_color(buffer)
        await redis.set(key, palette.value)

    return discord.Color(int(palette))


@async_executor()
def wordcloud(text: str):
    wordcloud = WordCloud(width=800, height=600, mode="RGBA", background_color=None, stopwords=set(STOPWORDS)).generate(text=text)

    arr = wordcloud.to_array()
    buffer = BytesIO()
    Image.fromarray(arr).save(buffer, format="png")
    buffer.seek(0)

    return discord.File(buffer, filename=f"{tuuid.random()}.png")


@async_executor()
def rotate(image: bytes, degrees: int = 90):
    if isinstance(image, bytes):
        image = BytesIO(image)

    with Image.open(image) as img:
        img = img.convert("RGBA").resize(
            (img.width * 2, img.height * 2),
        )

        img = img.rotate(
            angle=-degrees,
            expand=True,
        )

        buffer = BytesIO()
        img.save(
            buffer,
            format="png",
        )
        buffer.seek(0)

        img.close()
        return buffer


@async_executor()
def _collage_open(image: BytesIO):
    image = (
        Image.open(image)
        .convert("RGBA")
        .resize(
            (
                256,
                256,
            )
        )
    )
    return image


async def _collage_read(image: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image) as response:
            try:
                return await _collage_open(BytesIO(await response.read()))
            except:
                return None


async def _collage_paste(image: Image, x: int, y: int, background: Image):
    background.paste(
        image,
        (
            x * 256,
            y * 256,
        ),
    )


async def collage(images: list[str]):
    tasks = list()
    for image in images:
        tasks.append(_collage_read(image))

    images = [image for image in await asyncio.gather(*tasks) if image]
    if not images:
        return None

    rows = int(sqrt(len(images)))
    columns = (len(images) + rows - 1) // rows

    background = Image.new(
        "RGBA",
        (
            columns * 256,
            rows * 256,
        ),
    )
    tasks = list()
    for i, image in enumerate(images):
        tasks.append(_collage_paste(image, i % columns, i // columns, background))
    await asyncio.gather(*tasks)

    buffer = BytesIO()
    background.save(
        buffer,
        format="png",
    )
    buffer.seek(0)

    background.close()
    for image in images:
        image.close()

    return discord.File(
        buffer,
        filename="collage.png",
    )


async def ensure_future(coro: any, ignore_exceptions: bool = True):
    task: asyncio.Future = asyncio.ensure_future(coro)
    try:
        return await task
    except Exception as e:
        if not ignore_exceptions:
            raise e
        else:
            return None


async def configure_reskin(bot: commands.Bot, channel: discord.TextChannel, webhooks: dict):
    if not channel.permissions_for(channel.guild.me).manage_webhooks:
        return False

    if str(channel.id) in webhooks:  # We have to use str() because dicts are stupid
        try:
            await bot.fetch_webhook(webhooks[str(channel.id)])
        except:
            del webhooks[str(channel.id)]
            await cache.delete_many(f"reskin:channel:{channel.guild.id}:{channel.id}", f"reskin:webhook:{channel.id}")
        else:
            return True

    try:
        webhook = await asyncio.wait_for(
            channel.create_webhook(name="wock reskin"),
            timeout=5,
        )
    except:
        return False
    else:
        webhooks[str(channel.id)] = webhook.id
        try:
            await cache.delete(f"reskin:channel:{channel.guild.id}:{channel.id}")
            await cache.set(f"reskin:webhook:{channel.id}", webhook, expire="1h")
        except:
            pass
        return webhook


@async_executor()
def compress(buffer: bytes):
    return zlib.compress(buffer)


@async_executor()
def decompress(buffer: bytes):
    return zlib.decompress(buffer)


##


class plural:
    def __init__(self, value: int, bold: bool = False, code: bool = False):
        self.value: int = value
        self.bold: bool = bold
        self.code: bool = code

    def __format__(self, format_spec: str) -> str:
        v = self.value
        if isinstance(v, list):
            v = len(v)
        if self.bold:
            value = f"**{v:,}**"
        elif self.code:
            value = f"`{v:,}`"
        else:
            value = f"{v:,}"

        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"

        if abs(v) != 1:
            return f"{value} {plural}"

        return f"{value} {singular}"


def shorten(value: str, length: int = 20):
    if len(value) > length:
        value = value[: length - 2] + (".." if len(value) > length else "").strip()
    return value


# from io import BytesIO
# from imagetext_py import (EmojiOptions, FontDB, Paint, TextAlign, WrapStyle,
#                           Writer, text_size_multiline, text_wrap)
# import math, os
# from PIL import Image, ImageSequence

# font_path = os.path.join(os.getcwd(), "assets/fonts")
# FontDB.SetDefaultEmojiOptions(EmojiOptions(parse_discord_emojis=True))
# FontDB.LoadFromDir(font_path)

# @async_executor()
# def caption(
#     image: BytesIO, text: str, bypass_charlimit: bool = False
# ) -> BytesIO:

#     if isinstance(image, bytes):
#         image = BytesIO(image)

#     gif_char_limit = 1000
#     char_limit = 2000
#     frame_limit = 500
#     text_length = len(text)

#     if text_length > char_limit and not bypass_charlimit:
#         raise commands.CommandInvokeError(f"Text is too long (`{text_length}`/`{char_limit}`)")

#     font = FontDB.Query("futura-condensed-extra-bold arabic")

#     with Image.open(image) as img:
#         if hasattr(img, "n_frames"):
#             if img.n_frames > frame_limit:
#                 raise commands.CommandInvokeError(f"Too many frames (`{img.n_frames}`/`{frame_limit}`)")

#         aspect_ratio = img.height / img.width
#         size = (1024, int(1024 * aspect_ratio))

#         processed = []
#         durations = []

#         width, height = size
#         c_width = width * 0.85  # subjective design choice for borders
#         t_size = 130

#         wrapped_text = text_wrap(
#             text,
#             math.floor(c_width),
#             t_size,
#             font,
#             wrap_style=WrapStyle.Character,  # can change to make faster, just wont seperately wrap characters
#             draw_emojis=True,
#         )
#         _, t_height = text_size_multiline(
#             wrapped_text, t_size, font, draw_emojis=True
#         )
#         c_height = int(
#             t_height * 1.15
#         )  # objectively looks better /j (just adds borders)
#         min_height = int(height / 2.5)

#         if c_height < min_height:
#             c_height = min_height  # also just a subjective design choice

#         full_img_size = (
#             width,
#             height + c_height,
#         )  # combines height of the original image and the caption image height
#         caption_size = (width, c_height)

#         with Image.new("RGBA", caption_size, "white") as caption:
#             with Writer(caption) as writer:
#                 writer.draw_text_multiline(
#                     text=wrapped_text,
#                     x=width / 2,
#                     y=c_height / 2,  # get the center of the caption image
#                     ax=0.5,
#                     ay=0.5,  # define anchor points (middle)
#                     width=c_width,
#                     size=t_size,
#                     font=font,
#                     fill=Paint.Color((0, 0, 0, 255)),
#                     align=TextAlign.Center,
#                     draw_emojis=True,
#                 )

#             for frame in ImageSequence.Iterator(img):
#                 if text_length > gif_char_limit and not bypass_charlimit:
#                     break

#                 durations.append(frame.info.get("duration", 5))
#                 if frame.size != size:
#                     frame = frame.resize(size, resample=Image.LANCZOS)
#                 with Image.new(
#                     "RGBA", full_img_size, (255, 255, 255, 0)
#                 ) as full_img:
#                     full_img.paste(caption, (0, 0))
#                     full_img.paste(frame, (0, c_height))

#                     processed.append(full_img)

#             caption.close()

#             buffer = BytesIO()
#             processed[0].save(
#                 buffer,
#                 format="gif",
#                 save_all=True,
#                 append_images=[] if len(processed) == 1 else processed[1:],
#                 duration=durations,
#                 loop=0,
#                 disposal=2,
#                 comment="im gay",
#             )
#             buffer.seek(0)

#             is_animated = len(processed) > 1

#             for frame in processed:
#                 frame.close()

#             del processed
#             img.close()
#             return buffer, is_animated

# @async_executor()
# def uncaption(image: BytesIO) -> BytesIO:
#     if isinstance(image, bytes):
#         image = BytesIO(image)

#     with Image.open(image) as img:
#         width, height = img.size
#         aspect_ratio = height / width
#         size = (1024, int(1024 * aspect_ratio))
#         if img.size != size:
#             img = img.resize(size, resample=Image.LANCZOS)
#         img = img.crop((0, int(height / 2.5), width, height))
#         buffer = BytesIO()
#         img.save(buffer, format="png")
#         buffer.seek(0)
#         img.close()
#         return buffer


COLORS = {
    "aliceblue": "#f0f8ff",
    "antiquewhite": "#faebd7",
    "aqua": "#00ffff",
    "aquamarine": "#7fffd4",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    "bisque": "#ffe4c4",
    "black": "#000000",
    "blanchedalmond": "#ffebcd",
    "blue": "#0000ff",
    "blueviolet": "#8a2be2",
    "brown": "#a52a2a",
    "burlywood": "#deb887",
    "cadetblue": "#5f9ea0",
    "chartreuse": "#7fff00",
    "chocolate": "#d2691e",
    "coral": "#ff7f50",
    "cornflowerblue": "#6495ed",
    "cornsilk": "#fff8dc",
    "crimson": "#dc143c",
    "cyan": "#00ffff",
    "darkblue": "#00008b",
    "darkcyan": "#008b8b",
    "darkgoldenrod": "#b8860b",
    "darkgray": "#a9a9a9",
    "darkgrey": "#a9a9a9",
    "darkgreen": "#006400",
    "darkkhaki": "#bdb76b",
    "darkmagenta": "#8b008b",
    "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00",
    "darkorchid": "#9932cc",
    "darkred": "#8b0000",
    "darksalmon": "#e9967a",
    "darkseagreen": "#8fbc8f",
    "darkslateblue": "#483d8b",
    "darkslategray": "#2f4f4f",
    "darkslategrey": "#2f4f4f",
    "darkturquoise": "#00ced1",
    "darkviolet": "#9400d3",
    "deeppink": "#ff1493",
    "deepskyblue": "#00bfff",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1e90ff",
    "firebrick": "#b22222",
    "floralwhite": "#fffaf0",
    "forestgreen": "#228b22",
    "fuchsia": "#ff00ff",
    "gainsboro": "#dcdcdc",
    "ghostwhite": "#f8f8ff",
    "gold": "#ffd700",
    "goldenrod": "#daa520",
    "gray": "#808080",
    "grey": "#808080",
    "green": "#008000",
    "greenyellow": "#adff2f",
    "honeydew": "#f0fff0",
    "hotpink": "#ff69b4",
    "indianred": "#cd5c5c",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "lavenderblush": "#fff0f5",
    "lawngreen": "#7cfc00",
    "lemonchiffon": "#fffacd",
    "lightblue": "#add8e6",
    "lightcoral": "#f08080",
    "lightcyan": "#e0ffff",
    "lightgoldenrodyellow": "#fafad2",
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "lightgreen": "#90ee90",
    "lightpink": "#ffb6c1",
    "lightsalmon": "#ffa07a",
    "lightseagreen": "#20b2aa",
    "lightskyblue": "#87cefa",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#b0c4de",
    "lightyellow": "#ffffe0",
    "lime": "#00ff00",
    "limegreen": "#32cd32",
    "linen": "#faf0e6",
    "magenta": "#ff00ff",
    "maroon": "#800000",
    "mediumaquamarine": "#66cdaa",
    "mediumblue": "#0000cd",
    "mediumorchid": "#ba55d3",
    "mediumpurple": "#9370db",
    "mediumseagreen": "#3cb371",
    "mediumslateblue": "#7b68ee",
    "mediumspringgreen": "#00fa9a",
    "mediumturquoise": "#48d1cc",
    "mediumvioletred": "#c71585",
    "midnightblue": "#191970",
    "mintcream": "#f5fffa",
    "mistyrose": "#ffe4e1",
    "moccasin": "#ffe4b5",
    "navajowhite": "#ffdead",
    "navy": "#000080",
    "oldlace": "#fdf5e6",
    "olive": "#808000",
    "olivedrab": "#6b8e23",
    "orange": "#ffa500",
    "orangered": "#ff4500",
    "orchid": "#da70d6",
    "palegoldenrod": "#eee8aa",
    "palegreen": "#98fb98",
    "paleturquoise": "#afeeee",
    "palevioletred": "#db7093",
    "papayawhip": "#ffefd5",
    "peachpuff": "#ffdab9",
    "peru": "#cd853f",
    "pink": "#ffc0cb",
    "plum": "#dda0dd",
    "powderblue": "#b0e0e6",
    "purple": "#800080",
    "red": "#ff0000",
    "rosybrown": "#bc8f8f",
    "royalblue": "#4169e1",
    "saddlebrown": "#8b4513",
    "salmon": "#fa8072",
    "sandybrown": "#f4a460",
    "seagreen": "#2e8b57",
    "seashell": "#fff5ee",
    "sienna": "#a0522d",
    "silver": "#c0c0c0",
    "skyblue": "#87ceeb",
    "slateblue": "#6a5acd",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#fffafa",
    "springgreen": "#00ff7f",
    "steelblue": "#4682b4",
    "tan": "#d2b48c",
    "teal": "#008080",
    "thistle": "#d8bfd8",
    "tomato": "#ff6347",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "white": "#ffffff",
    "whitesmoke": "#f5f5f5",
    "yellow": "#ffff00",
    "yellowgreen": "#9acd32",
}

LANGUAGES = {
    "afrikaans": "af",
    "albanian": "sq",
    "amharic": "am",
    "arabic": "ar",
    "armenian": "hy",
    "azerbaijani": "az",
    "basque": "eu",
    "belarusian": "be",
    "bengali": "bn",
    "bosnian": "bs",
    "bulgarian": "bg",
    "catalan": "ca",
    "cebuano": "ceb",
    "chichewa": "ny",
    "chinese": "zh-cn",
    "chinese (simplified)": "zh-cn",
    "chinese (traditional)": "zh-tw",
    "corsican": "co",
    "croatian": "hr",
    "czech": "cs",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "esperanto": "eo",
    "estonian": "et",
    "filipino": "tl",
    "finnish": "fi",
    "french": "fr",
    "frisian": "fy",
    "galician": "gl",
    "georgian": "ka",
    "german": "de",
    "greek": "el",
    "gujarati": "gu",
    "haitian creole": "ht",
    "hausa": "ha",
    "hawaiian": "haw",
    "hebrew": "he",
    "hindi": "hi",
    "hmong": "hmn",
    "hungarian": "hu",
    "icelandic": "is",
    "igbo": "ig",
    "indonesian": "id",
    "irish": "ga",
    "italian": "it",
    "japanese": "ja",
    "javanese": "jw",
    "kannada": "kn",
    "kazakh": "kk",
    "khmer": "km",
    "korean": "ko",
    "kurdish (kurmanji)": "ku",
    "kyrgyz": "ky",
    "lao": "lo",
    "latin": "la",
    "latvian": "lv",
    "lithuanian": "lt",
    "luxembourgish": "lb",
    "macedonian": "mk",
    "malagasy": "mg",
    "malay": "ms",
    "malayalam": "ml",
    "maltese": "mt",
    "maori": "mi",
    "marathi": "mr",
    "mongolian": "mn",
    "myanmar (burmese)": "my",
    "nepali": "ne",
    "norwegian": "no",
    "odia": "or",
    "pashto": "ps",
    "persian": "fa",
    "polish": "pl",
    "portuguese": "pt",
    "punjabi": "pa",
    "romanian": "ro",
    "russian": "ru",
    "samoan": "sm",
    "scots gaelic": "gd",
    "serbian": "sr",
    "sesotho": "st",
    "shona": "sn",
    "sindhi": "sd",
    "sinhala": "si",
    "slovak": "sk",
    "slovenian": "sl",
    "somali": "so",
    "spanish": "es",
    "sundanese": "su",
    "swahili": "sw",
    "swedish": "sv",
    "tajik": "tg",
    "tamil": "ta",
    "telugu": "te",
    "thai": "th",
    "turkish": "tr",
    "ukrainian": "uk",
    "urdu": "ur",
    "uyghur": "ug",
    "uzbek": "uz",
    "vietnamese": "vi",
    "welsh": "cy",
    "xhosa": "xh",
    "yiddish": "yi",
    "yoruba": "yo",
    "zulu": "zu",
}
