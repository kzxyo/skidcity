import json
import logging
import os
import sys

from multiprocessing import Process

import discord

from aiohttp import ClientSession
from discord.ext.commands import Bot, when_mentioned_or
from loguru import logger


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
logging.getLogger("discord").setLevel(logging.CRITICAL)
logging.getLogger("discord.http").setLevel(logging.CRITICAL)
logging.getLogger("discord.client").setLevel(logging.CRITICAL)
logging.getLogger("discord.gateway").setLevel(logging.CRITICAL)
logging.getLogger("discord.ext.ipc.server").setLevel(logging.CRITICAL)


class Cluster(Bot):
    def __init__(self):
        super().__init__(
            command_prefix=when_mentioned_or("---"),
            strip_after_prefix=True,
            case_insensitive=True,
            max_messages=10,
            command_attrs=dict(hidden=True),
            intents=discord.Intents(
                guilds=True,
                members=True,
                messages=True,
                message_content=True,
                voice_states=True,
            ),
            activity=discord.Activity(type=discord.ActivityType.competing, name="discord.gg/wock"),
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=False),
            owner_ids=[1004836998151950358],
        )
        self.logger = logger
        self.logger.remove()
        self.logger.add(
            sys.stdout,
            colorize=True,
            format=(
                "<cyan>[</cyan><blue>{time:YYYY-MM-DD HH:MM:SS}</blue><cyan>]</cyan> (<magenta>cluster:{function}</magenta>) <yellow>@</yellow> <fg"
                " #BBAAEE>{message}</fg #BBAAEE>"
            ),
        )

    async def on_ready(self):
        self.logger.success(f"Logged in as {self.user} ({self.user.id})")

    async def setup_hook(self):
        await self.load_extension("jishaku")
        # await self.load_extension("cogs.developer")

        self.session: ClientSession = self.http._HTTPClient__session

    async def on_command(self, ctx):
        self.logger.info(f"{ctx.author} ({ctx.author.id}) ran command {ctx.command}")


if __name__ == "__main__":
    try:
        config = json.loads(open("config.json", "r").read())
    except FileNotFoundError:
        config = json.loads(open("../config.json", "r").read())

    tasks = list()
    for token in config.get("music_tokens"):
        tasks.append(
            Process(
                name=("wock:cluster" + str(len(tasks))),
                target=Cluster().run,
                args=(token,),
            )
        )

    for process in tasks:
        process.start()
