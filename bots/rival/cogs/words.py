import aiohttp
import asyncio
import discord
import functools
import re
from io import BytesIO
import numpy as np
import os
from PIL import Image
from discord.ext import commands
from wordcloud import WordCloud as WCloud
from wordcloud import ImageColorGenerator

# Special thanks to co-author aikaterna for pressing onward
# with this cog when I had lost motivation!

URL_RE = re.compile(
    r"([\w+]+\:\/\/)?([\w\d-]+\.)*[\w-]+[\.\:]\w+([\/\?\=\&\#]?[\w-]+)*\/?", flags=re.I
)
# https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string


class words(commands.Cog):

    """Word Clouds"""

    def __init__(self, bot):
        self.bot = bot
        self.session = None

    @commands.guild_only()
    @commands.command(name="wordcloud", aliases=["wc"])
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def wordcloud(self, ctx, *argv):
        """Generate a wordcloud. Optional arguments are channel, user, and
        message limit (capped at 10,000)."""

        author = ctx.author
        channel = ctx.channel
        user = None
        limit = 5000

        # a bit clunky, see if Red has already implemented converters
        channel_converter = commands.TextChannelConverter()
        member_converter = commands.MemberConverter()

        for arg in argv:
            try:
                channel = await channel_converter.convert(ctx, arg)
                continue
            except discord.ext.commands.BadArgument:
                pass

            try:
                user = await member_converter.convert(ctx, arg)
                continue
            except discord.ext.commands.BadArgument:
                pass

            if arg.isdecimal() and int(arg) <= 10000:
                limit = int(arg)

        guild = channel.guild

        # Verify that wordcloud requester is not being a sneaky snek
        if not channel.permissions_for(author).read_messages or guild != ctx.guild:
            await ctx.send(":smirk:  Nice try.")
            return

        # Default settings
        mask = None
        coloring = None
        width = 600
        height = 400
        mode = "RGB"
        bg_color = "deepskyblue"
        if bg_color == "clear":
            mode += "A"
            bg_color = None
        max_words = 200
        if max_words == 0:
            max_words = 200
        excluded = []
        if not excluded:
            excluded = None

        mask_name = None

        kwargs = {
            "mask": mask,
            "color_func": coloring,
            "mode": mode,
            "font_path":"cogs/bebasneue-wordcloud.ttf",
            "background_color": "black",
            "max_words": max_words,
            "max_font_size": 50,
            "stopwords": excluded,
            "min_word_length": 3,
            "width": width,
            "height": height,
            "normalize_plurals": True
        }

        msg = "Generating wordcloud for **" + guild.name + "/" + channel.name
        if user is not None:
            msg += "/" + user.display_name
        msg += "** using the last {} messages. (this might take a while)".format(limit)

        msssss=await ctx.send(msg)

        text = ""
        try:
            async for message in channel.history(limit=limit):
                if not message.author.bot:
                    if user is None or user == message.author:
                        text += message.clean_content + " "
            text = URL_RE.sub("", text)
        except discord.errors.Forbidden:
            await ctx.send("Wordcloud creation failed. I can't see that channel!")
            return

        if not text or text.isspace():
            await ctx.send(
                "Wordcloud creation failed. I couldn't find "
                "any words. You may have entered a very small "
                "message limit, or I may not have permission "
                "to view message history in that channel."
            )
            return

        task = functools.partial(self.generate, text, **kwargs)
        task = self.bot.loop.run_in_executor(None, task)
        try:
            image = await asyncio.wait_for(task, timeout=45)
        except asyncio.TimeoutError:
            await ctx.send("Wordcloud creation timed out.")
            return
        msg = "Wordcloud for **" + guild.name + "/" + channel.name
        if user is not None:
            msg += "/" + user.display_name
        msg += "** using the last {} messages.".format(limit)
        await ctx.send(msg, file=discord.File(image))
        await msssss.delete()

    @staticmethod
    def generate(text, **kwargs):
        # Designed to be run in executor to avoid blocking
        wc = WCloud(**kwargs)
        wc.generate(text)
        file = BytesIO()
        file.name = "wordcloud.png"
        wc.to_file(file)
        file.seek(0)
        return file

async def setup(bot):
	await bot.add_cog(words(bot))