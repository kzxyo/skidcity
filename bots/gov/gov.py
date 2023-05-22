
# Gov is owned by asf#1337. Any contents in gov are fully created by asf#1337.

import discord, random, asyncio, psutil, datetime, os, jishaku, json, sys, aiohttp
from discord.ext import commands
from discord.gateway import DiscordWebSocket, _log
from discord.ext.commands import Bot

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
        token = configData["token"]

class gov(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=(self_prefix),intents=intents.all(),help_command=None,case_insensitive=True,owner_ids=[enter your account id])

    async def setup_hook(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension("cogs." + file[:-3])
                print(f"Loaded cog: {file[:-3]}")

        await self.load_extension("jishaku")

def self_prefix(bot, ctx):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    if str(ctx.author.id) not in prefixes:
        prefixes[str(ctx.author.id)] = ','
    return prefixes[str(ctx.author.id)]

async def identify(self):
    payload = {
        'op': self.IDENTIFY,
        'd': {
            'token': self.token,
            'properties': {
                '$os': sys.platform,
                '$browser': 'Discord Android',
                '$device': 'Discord Android',
                '$referrer': '',
                '$referring_domain': ''
            },
            'compress': True,
            'large_threshold': 250,
            'v': 3
        }
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload['d']['presence'] = {
            'status': state._status,
            'game': state._activity,
            'since': 0,
            'afk': False
        }

    if state._intents is not None:
        payload['d']['intents'] = state._intents.value

    await self.call_hooks('before_identify', self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
    _log.info('Shard ID %s has sent the IDENTIFY payload.', self.shard_id)

DiscordWebSocket.identify = identify

bot = gov()
bot.run(token)