import discord, aiosqlite, os, asyncio, time, sys, random, aiohttp, datetime
from datetime import datetime
from discord.ext import commands, tasks 
from discord.gateway import DiscordWebSocket
from utils.classes import Emojis
from cogs.tickets import closeticket, ticketb
from tools.utils import PaginatorView
from typing import List
from backend.classes import Emojis
from cogs.voicemaster import vmbuttons
import typing

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

async def identify(self):
    payload = {
        'op': self.IDENTIFY,
        'd': {
            'token': self.token,
            'properties': {
                '$os': sys.platform,
                '$browser': 'website',
                '$device': 'Discord iOS',
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

DiscordWebSocket.identify = identify

async def getprefix(bot, message):
       if not message.guild: return ";"
       selfprefix = ";" 
       guildprefix = ";"
       async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM selfprefix WHERE user_id = {}".format(message.author.id)) 
        check = await cursor.fetchone()
        if check is not None:
         selfprefix = check[0]
        await cursor.execute("SELECT prefix, * FROM prefixes WHERE guild_id = {}".format(message.guild.id)) 
        res = await cursor.fetchone()
        if res is not None: 
            guildprefix = res[0]
        elif res is None:
            guildprefix = ";"    

       return guildprefix, selfprefix  

def get_status(name: str): 
   if name == "competing": return discord.ActivityType.competing
   elif name == "streaming": return discord.ActivityType.streaming
   elif name == "playing": return discord.ActivityType.playing 
   elif name == "watching": return discord.ActivityType.watching
   elif name == "listening": return discord.ActivityType.listening

@tasks.loop(seconds=16)
async def status(): 
   list = [";help"]
   activities = ["competing"]
   for a in activities:
    for l in list: 
     await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=get_status(a), name=l, url="https://twitch.tv/lol"))
     await asyncio.sleep(20) 

@tasks.loop(minutes=5)
async def stats():
  online = "<:online:1046291787007934537>"
  embed = discord.Embed(color=0x495063, description=f"{online} abort is running `{round(bot.latency * 1000)}ms`, serving `{len(bot.guilds)}` servers with `{len(set(bot.get_all_members()))}` members")
  embed.set_footer(text="next update in 5 minutes")
  stat_log = bot.get_channel(1107120847036092467)
  await stat_log.send(embed=embed)

intents = discord.Intents.all()
intents.presences = True

class Client(commands.AutoShardedBot):
  def __init__(self):
    super().__init__(
        command_prefix=getprefix,
        intents=intents,
        help_command=None, 
        case_insensitive=True,
        allowed_mentions=discord.AllowedMentions.all(),
        strip_after_prefix=True,  
        owner_ids=[1107903478451408936]
    ) 
    self.uptime = time.time()

  async def on_connect(self): 
    setattr(bot, "db", await aiosqlite.connect("main.db"))
    print("Attempting to connect to Discord's API")
    await self.load_extension("jishaku")
    self.add_view(closeticket())
    self.add_view(ticketb())
    for file in os.listdir("./cogs"): 
      if file.endswith(".py"):
        try: 
            await self.load_extension("cogs." + file[:-3])
            print("loaded extension {}".format(file[:-3])) 
        except Exception as e: 
           print("unable to load extension {} - {}".format(file[:-3], e))
  
  async def on_ready(self):
    self.add_view(vmbuttons())
    status.start()
    stats.start()
    print(f"logged in as {bot.user}")
bot = Client()
bot.run("have no idea what goes here lol", reconnect=True)