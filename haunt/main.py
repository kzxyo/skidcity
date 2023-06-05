import discord, aiosqlite, os, asyncio, time, sys, random, aiohttp, datetime
from datetime import datetime
from discord.ext import commands, tasks 
from discord.gateway import DiscordWebSocket
from utils.classes import Emojis
from backend.classes import Emojis
from cogs.voicemaster import vmbuttons

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

def get_gay(name: str): 
   if name == "competing": return discord.ActivityType.competing
   elif name == "streaming": return discord.ActivityType.streaming
   elif name == "playing": return discord.ActivityType.playing 
   elif name == "watching": return discord.ActivityType.watching
   elif name == "listening": return discord.ActivityType.listening

@tasks.loop(minutes=5)
async def status(): 
   list = [";help"]
   activities = []
   for a in activities:
    for l in list: 
     await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=get_status(a), name=l, url="https://twitch.tv/lol"))
     await asyncio.sleep(20) 

@tasks.loop(minutes=5)
async def stats(self): 
      online = "<:icons_goodping:1106138130081386527>"
      message = self.bot.get_channel(1107561338143785041)
      embed = discord.Embed(color=Colors.default, title=f"<a:whiteloading:1103721417322790952> **restarted**", description=f"> {online} haunt is back online")
      embed.set_footer(text="connected to discord API as: haunt#8429")    
      await message.send(embed=embed)

@tasks.loop()
async def statuses():
      await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.competinzg, name=f"discord.gg/htc", url='https://www.twitch.tv/com'))


@tasks.loop(hours=763467634565634356346526348523476542376457236856732556)
async def on_ready(self): 
      online = "<:icons_goodping:1106138130081386527>"
      message = self.bot.get_channel(1107120847036092467)
      embed = discord.Embed(color=Colors.default, title=f"<a:whiteloading:1103721417322790952> **restarted**", description=f"> {online} haunt is back online")
      embed.set_footer(text="connected to discord API as: haunt#8429")    
      await message.send(embed=embed) 


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
        owner_ids=[509244475126841365, 112635397481213952, 530079572893368330]
    ) 
    self.uptime = time.time()

  async def on_connect(self): 
    setattr(bot, "db", await aiosqlite.connect("main.db"))
    print("Attempting to connect to Discord's API")
    await self.load_extension("jishaku")
    for file in os.listdir("./cogs"): 
      if file.endswith(".py"):
        try: 
            await self.load_extension("cogs." + file[:-3])
            print("loaded extension {}".format(file[:-3])) 
        except Exception as e: 
           print("unable to load extension {} - {}".format(file[:-3], e))
  
  async def on_ready(self):
    self.add_view(vmbuttons())
    statuses.start()
    stats.start()
    print(f"logged in as {bot.user}")
bot = Client()
bot.run("MTEwOTgxOTc5NzA5NDU0MzM2MA.GUJ8Xg.p8jICGZLK3mTja3Nf0BURt1MSYEKb_mzDFZz-k", reconnect=True)