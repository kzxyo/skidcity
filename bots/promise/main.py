import discord, aiosqlite, os, asyncio, time, sys, random, aiohttp, datetime, json, logging, traceback
from datetime import datetime
from discord.ext import commands, tasks 
from discord.gateway import DiscordWebSocket
from pymongo import MongoClient

async def mobile(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": "Discord iOS",
                "$browser": "Discord iOS",
                "$device": "iOS",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
        },
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload["d"]["presence"] = {
            "status": state._status,
            "game": state._activity,
            "since": 0,
            "afk": True,
        }
        if state._intents is not None:
            payload["d"]["intents"] = state._intents.value
    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
discord.gateway.DiscordWebSocket.identify = mobile

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

with open("config.json") as f:
   config = json.load(f)
   token = config["token"]
   
class promise(commands.AutoShardedBot):
    def __init__(self, config):
        self.config = config
        self.cluster = MongoClient(config["mongo"])
        

        intents = discord.Intents.all()
        super().__init__(
            command_prefix=",",
            intents=intents,
            help_command=None,
            owner_ids=[990633882644791318],
            case_insensitive=True,        
            activity=discord.Activity(type=discord.ActivityType.competing))
        
    async def setup_hook(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension("cogs." + file[:-3])
                print(f"Loaded cog: {file[:-3]}")
        await self.load_extension("jishaku")
        print(f"Loaded cog: jishaku")
        
async def on_connect(self):
    setattr(bot, "db")
    await aiosqlite.connect("main.db")

    async def on_ready(self):
        print("Bot Back To Alive")

bot = promise(config)
bot.run(token)
