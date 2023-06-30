from io import BytesIO
from mimetypes import guess_type
from typing import Literal, Optional

import discord

from discord.ext.commands import (
    BadArgument,
    CommandError,
    Converter,
    MemberConverter,
    RoleConverter,
)

from helpers import regex
from helpers.managers import Context
from helpers.models.basic import Attachment
from helpers.utilities import get_color, human_join
from helpers.variables import regions


class File(Converter):
    def __init__(self, *acceptable_types: Literal["image", "video", "audio"]):
        self.acceptable_types = acceptable_types

    async def run_before(self, ctx: Context) -> Optional[BytesIO]:
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]

        elif ctx.replied_message and ctx.replied_message.attachments:
            attachment = ctx.replied_message.attachments[0]

        else:
            return

        if attachment.content_type.startswith(self.acceptable_types):
            return Attachment(
                buffer=await attachment.read(),
                extension=attachment.content_type.split("/")[1],
                url=attachment.url,
            )

    async def convert(self, ctx: Context, argument: str) -> BytesIO:
        buffer: BytesIO = None
        extension: str = None
        try:
            argument = await (
                await MemberConverter().convert(ctx, argument)
            ).display_avatar.url
        except:
            pass

        if not (match := guess_type(argument)[0]) and match.startswith(
            self.acceptable_types
        ):
            raise CommandError(
                "Please provide a valid "
                + human_join([f"`{type}`" for type in self.acceptable_types])
                + " file"
            )

        try:
            response = await ctx.bot.session.get(argument)
            buffer = BytesIO(await response.read())
            extension = guess_type(argument)[0].split("/")[1]
        except:
            raise CommandError("Please provide a valid **URL**")

        if not response.content_type.startswith(self.acceptable_types):
            raise CommandError(
                "Please provide a valid "
                + human_join([f"`{type}`" for type in self.acceptable_types])
                + " file"
            )

        if not buffer:
            raise CommandError(
                "Please provide a valid "
                + human_join([f"`{type}`" for type in self.acceptable_types])
                + " file"
            )

        return Attachment(buffer=buffer, extension=extension, url=argument)


class Status(Converter):
    async def convert(self, ctx: Context, argument: str) -> bool:
        if argument.lower() in (
            "enable",
            "true",
            "yes",
            "on",
        ):
            return True

        elif argument.lower() in (
            "disable",
            "false",
            "none",
            "null",
            "off",
            "no",
        ):
            return False

        else:
            raise CommandError("Please specify **yes** or **no**")


class Percentage(Converter):
    async def convert(self, ctx: Context, argument: str) -> int:
        if argument.isdigit():
            argument = int(argument)

        elif match := regex.PERCENTAGE.match(argument):
            argument = int(match.group(1))

        else:
            argument = 0

        if argument < 0 or argument > 100:
            raise CommandError("Please **specify** a valid percentage")

        return argument


class Bitrate(Converter):
    async def convert(self, ctx: Context, argument: str) -> int:
        if argument.isdigit():
            argument = int(argument)

        elif match := regex.BITRATE.match(argument):
            argument = int(match.group(1))

        else:
            argument = 0

        if argument < 8:
            raise CommandError("**Bitrate** cannot be less than `8 kbps`!")

        elif argument > int(ctx.guild.bitrate_limit / 1000):
            raise CommandError(
                f"`{argument} kbps` cannot be **greater** than `{int(ctx.guild.bitrate_limit / 1000)} kbps`!"
            )

        return argument


class Region(Converter):
    async def convert(self, ctx: Context, argument: str) -> int:
        argument = argument.lower().replace(" ", "-")
        if not argument in regions:
            raise CommandError(
                "**Voice region** must be one of "
                + human_join([f"`{region}`" for region in regions])
            )

        return argument


class Position(Converter):
    async def convert(self, ctx: Context, argument: str) -> int:
        argument = argument.lower()
        player = ctx.voice_client
        ms: int = 0

        if ctx.invoked_with == "ff" and not argument.startswith("+"):
            argument = f"+{argument}"

        elif ctx.invoked_with == "rw" and not argument.startswith("-"):
            argument = f"-{argument}"

        if match := regex.Position.HH_MM_SS.fullmatch(argument):
            ms += (
                int(match.group("h")) * 3600000
                + int(match.group("m")) * 60000
                + int(match.group("s")) * 1000
            )

        elif match := regex.Position.MM_SS.fullmatch(argument):
            ms += int(match.group("m")) * 60000 + int(match.group("s")) * 1000

        elif (match := regex.Position.OFFSET.fullmatch(argument)) and player:
            ms += player.position + int(match.group("s")) * 1000

        elif match := regex.Position.HUMAN.fullmatch(argument):
            if m := match.group("m"):
                if match.group("s") and argument.endswith("m"):
                    raise CommandError(f"Position `{argument}` is not valid")

                ms += int(m) * 60000

            elif s := match.group("s"):
                if argument.endswith("m"):
                    ms += int(s) * 60000
                else:
                    ms += int(s) * 1000

        else:
            raise CommandError(f"Position `{argument}` is not valid")

        return ms


class Color(Converter):
    async def convert(self, ctx: Context, argument: str) -> discord.Color:
        if argument.lower() == "random":
            return discord.Color.random()

        try:
            return (await MemberConverter().convert(ctx, argument)).color
        except (CommandError, BadArgument):
            pass

        try:
            return (await RoleConverter().convert(ctx, argument)).color
        except (CommandError, BadArgument):
            pass

        if not (color := get_color(argument)):
            raise CommandError(f"**#{argument}** is an invalid hex code")

        return color
