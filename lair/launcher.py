import os
import discord
from multiprocessing import Process
from utilities import config
from utilities.lair import Lair
import uvloop
from worker.worker2 import Workers
import logging
from xxhash import xxh64_hexdigest
from discord.gateway import DiscordWebSocket
uvloop.install()
active = []

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
discord.utils.setup_logging()

bot = Lair()
if __name__ == "__main__":
    bot.run(config.tokens[0], reconnect=True, root_logger=False)