from logging import getLogger
from typing_extensions import NoReturn
from warnings import filterwarnings
from dotenv import load_dotenv
load_dotenv(verbose=True)

from discord import Activity, ActivityType

from utilities.vile import (
    GLOBAL, 
    VileBot, 
    embed_send, 
    guild_has_vanity,
    has_permissions, 
    is_guild_owner
)

import aiohttp
import asyncio
import datetime
import discord
import uvloop

logger = getLogger(__name__)
discord.utils.setup_logging()

aiohttp.resolver.aiodns_default = True
aiohttp.resolver._DefaultType = aiohttp.resolver.AsyncResolver
aiohttp.resolver.DefaultResolver = aiohttp.resolver.AsyncResolver
aiohttp.connector.DefaultResolver = aiohttp.resolver.AsyncResolver

discord.Embed.send = embed_send
discord.ext.commands.has_permissions = has_permissions
discord.ext.commands.is_guild_owner = is_guild_owner
discord.ext.commands.guild_has_vanity = guild_has_vanity

uvloop.install()

filterwarnings(
    "ignore", 
    category=RuntimeWarning
)


async def run() -> NoReturn:
    async with VileBot(
        command_prefix=",",
        activity=Activity(
            type=ActivityType.streaming,
            name="no",
            url="https://twitch.tv/directory"
        )
    ) as bot:
        GLOBAL.BOT = bot

        try:
            await bot.start(
                token=bot.config.api.discord, 
                reconnect=False
            )

        finally:
            if hasattr(bot, "browser") and bot.browser.closed is False:
                await bot.browser.__aexit__()

            if not bot.is_closed():
                await bot.close()
                
            bot.logger.info("Application shut down.")
           

if __name__ == "__main__":
    asyncio.run(run())
