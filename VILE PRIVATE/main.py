import uvloop, os, logging, aiohttp, discord, asyncio
logger = logging.getLogger(__name__)
discord.utils.setup_logging()
from dotenv import load_dotenv
load_dotenv(verbose=True)
from utilities.vile import VileBot, Browser, has_permissions, is_guild_owner
from utilities import vile

aiohttp.resolver.aiodns_default = True
aiohttp.resolver._DefaultType = aiohttp.resolver.AsyncResolver
aiohttp.resolver.DefaultResolver = aiohttp.resolver.AsyncResolver
aiohttp.connector.DefaultResolver = aiohttp.resolver.AsyncResolver

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"
discord.ext.commands.has_permissions = has_permissions
discord.ext.commands.is_guild_owner = is_guild_owner
uvloop.install()


async def run() -> None:
    async with VileBot(cluster_id=1, cluster_ids=(1,)) as bot:
        browser = vile.Browser(
            executable_path="/usr/bin/google-chrome",
            args=[
                "--ignore-certificate-errors",
                "--disable-extensions",
                "--no-sandbox",
                "--headless"
            ]
        )
        async with browser:
            bot.browser = browser
            vile.CACHE = bot.cache
            vile.BOT = bot
            vile.BROWSER = browser
            await bot.start(bot.config["api"].discord, reconnect=False)
    
    
if __name__ == "__main__":
    asyncio.run(run())
    