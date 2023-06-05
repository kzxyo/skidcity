import discord, aiosqlite, os, asyncio, time, sys, random, aiohttp, datetime
from datetime import datetime
from discord.ext import commands, tasks 
from discord.gateway import DiscordWebSocket
from utils.classes import Emojis
from cogs.tickets import closeticket, ticketb
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
                '$browser': 'Discord iOS',
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
       if not message.guild: return ","
       selfprefix = "," 
       guildprefix = ","
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
            guildprefix = ","    

       return guildprefix

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
      embed = discord.Embed(color=Colors.default, title=f"<a:whiteloading:1103721417322790952> **restarted**", description=f"> {online} abort is back online")
      embed.set_footer(text="connected to discord API as: abort#1897")    
      await message.send(embed=embed)


@tasks.loop(minutes=5)
async def stats():
  gays = self.bot.get_channel(1113394814201905174) 
  online = "<:icons_goodping:1106138130081386527>"
  embed1 = discord.Embed(color=0x2B2D31, description=f":arrows_clockwise: loading informations")
  embed = discord.Embed(color=0x495063, description=f"{online} haunt is running `{round(bot.latency * 1000)}ms`, serving `{len(bot.guilds)}` servers with `{len(set(bot.get_all_members()))}` members")
  embed.set_footer(text="next update in 5 minutes")
  msg = await gays.send(embed=embed1)
  await msg.edit(embed=embed)

@tasks.loop()
async def statuses():
      await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.competing, name=f"discord.gg/htc", url='https://www.twitch.tv/com'))



intents = discord.Intents.all()
intents.presences = True

class Client(commands.AutoShardedBot):
  def __init__(self):
    super().__init__(
        command_prefix=getprefix,
        intents=intents,
        help_command=None, 
        case_insensitive=True,
        allowed_mentions=discord.AllowedMentions.none(),
        strip_after_prefix=True,  
        owner_ids=[1077729793400897576, 509244475126841365, 1107903478451408936, 371224177186963460]
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
bot.run("MTA3NTc5NzIyMTQ2NDg3MTAxMg.GKYJua.9ifCZ4n6tCZbPnIQ8d7JkP-8AiSFdFjkSMEn2U", reconnect=True)