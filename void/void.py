import json, os
from pathlib import Path
import discord
from discord.gateway import DiscordWebSocket
from utils.data import Bot
import logging
import datetime
from discord.ext import commands

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f'-----')

async def prefix(bot, message):
    prefixes = []
    data = await bot.db.fetchval('SELECT prefix FROM prefix WHERE guild_id = $1', message.guild.id)
    if data:
        prefixes.append(data)
    selfprefix = await bot.db.fetchval('SELECT prefix from selfprefix WHERE user_id = $1', message.author.id)
    if selfprefix:
        prefixes.append(selfprefix)
    return commands.when_mentioned_or(*(prefixes or [',']))(bot, message)

async def identify(self):
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
            "afk": False,
        }

    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value

    await self.call_hooks(
        "before_identify", self.shard_id, initial=self._initial_identify
    )
    await self.send_as_json(payload)


DiscordWebSocket.identify = identify

bot = Bot(
    intents=discord.Intents.all(),
    command_prefix=prefix,
    case_insensitive=True,
    owner_ids=[566434977093386258, 323118319144271872, 936602569042690150, 1096174712356339792]
)

bot.startup_time = datetime.datetime.utcnow()
config_file = json.load(open(cwd + '/config/config.json'))
bot.config_token = config_file['token']
bot.version = '0.0.1'
logging.basicConfig(level=logging.INFO)
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    print(f"-----\nLogged in as: {bot.user} : {bot.user.id}\n-----")

bot.run(bot.config_token, reconnect=True)
