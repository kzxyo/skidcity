import discord, aiosqlite, os, asyncio, time, sys, random, aiohttp, datetime, jishaku
from datetime import datetime
from discord.ext import commands, tasks 
from discord.gateway import DiscordWebSocket
from cogs.voicemaster import vmbuttons
from images.pfps import PFPS

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
       if not message.guild: return "."
       selfprefix = "." 
       guildprefix = "."
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
            guildprefix = "."    

       return guildprefix, selfprefix  

@tasks.loop(seconds=12)
async def female(): 
    links = random.choice(PFPS.females)
    embeds = []
    embed = discord.Embed(color=0x2f3136, description="[our pinterest](https://www.pinterest.com/antipfps/)", timestamp=datetime.datetime.now())
    embed.set_image(url=links)
    embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
    embed.set_footer(text="powered by {}".format(bot.user.name))
    embeds.append(embed)
    async with bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM female")
      results = await cursor.fetchall()
      for result in results:
        channel_id = result[1]
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embed=embed)
          await asyncio.sleep(12)
        except:
            pass

@tasks.loop(seconds=12)
async def male():
    links = random.choice(PFPS.males)
    embeds = []
    embed = discord.Embed(color=0x2f3136, description="[our pinterest](https://www.pinterest.com/antipfps/)", timestamp=datetime.datetime.now())
    embed.set_image(url=links)
    embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
    embed.set_footer(text="powered by {}".format(bot.user.name))
    embeds.append(embed)
    async with bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM male")
      results = await cursor.fetchall()
      for result in results:
        channel_id = result[1]
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embed=embed)
          await asyncio.sleep(12)
        except:
            pass

@tasks.loop(seconds=12)
async def anime():
    links = random.choice(PFPS.animes)
    embeds = []
    embed = discord.Embed(color=0x2f3136, description="[our pinterest](https://www.pinterest.com/antipfps/)", timestamp=datetime.datetime.now())
    embed.set_image(url=links)
    embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
    embed.set_footer(text="powered by {}".format(bot.user.name))
    embeds.append(embed)
    async with bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM anime")
      results = await cursor.fetchall()
      for result in results:
        channel_id = result[1]
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embed=embed)
          await asyncio.sleep(12)
        except:
            pass

@tasks.loop(seconds=12) 
async def ricon():  
    for guild in bot.guilds: 
       for member in guild.members:  
        if member.bot:
            continue
        else:
         if member.avatar:
          async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM random")
            results = await cursor.fetchall()
            for result in results:
             channel_id = result[1]
             user = await bot.fetch_user(member.id)
             embed = discord.Embed(color=0x2f3136, description="[our pinterest](https://www.pinterest.com/antipfps/)", timestamp=datetime.datetime.now())
             embed.set_image(url=user.avatar.url)
             embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
             embed.set_footer(text="powered by {}".format(bot.user.name))
             try:
              channel = bot.get_channel(channel_id)
              await channel.send(embed=embed)
              await asyncio.sleep(12)
             except:
                pass

@tasks.loop(seconds=12)
async def banner():  
    links = random.choice(PFPS.banners)
    embeds = []
    embed = discord.Embed(color=0x2f3136, description="[our pinterest](https://www.pinterest.com/antipfps/)", timestamp=datetime.datetime.now())
    embed.set_image(url=links)
    embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
    embed.set_footer(text="powered by {}".format(bot.user.name))
    embeds.append(embed)
    async with bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM banner")
      results = await cursor.fetchall()
      for result in results:
        channel_id = result[1]
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embed=embed)
          await asyncio.sleep(12)
        except:
            pass

@tasks.loop(seconds=12)
async def fgif():  
    links = random.choice(PFPS.female_gifs)
    embeds = []
    embed = discord.Embed(color=0x2f3136, description="[our pinterest](https://www.pinterest.com/antipfps/)", timestamp=datetime.datetime.now())
    embed.set_image(url=links)
    embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
    embed.set_footer(text="powered by {}".format(bot.user.name))
    embeds.append(embed)
    async with bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM fgifs")
      results = await cursor.fetchall()
      for result in results:
        channel_id = result[1]
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embed=embed)
          await asyncio.sleep(12)
        except:
            pass

@tasks.loop(seconds=12)
async def mgif():  
    links = random.choice(PFPS.male_gifs)
    embeds = []
    embed = discord.Embed(color=0x2f3136, description="[our pinterest](https://www.pinterest.com/antipfps/)", timestamp=datetime.datetime.now())
    embed.set_image(url=links)
    embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
    embed.set_footer(text="powered by {}".format(bot.user.name))
    embeds.append(embed)
    async with bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM mgifs")
      results = await cursor.fetchall()
      for result in results:
        channel_id = result[1]
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embed=embed)
          await asyncio.sleep(12)
        except:
            pass

@tasks.loop(seconds=12)
async def agif():  
    links = random.choice(PFPS.anime_gifs)
    embeds = []
    embed = discord.Embed(color=0x2f3136, description="[our pinterest](https://www.pinterest.com/antipfps/)", timestamp=datetime.datetime.now())
    embed.set_image(url=links)
    embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
    embed.set_footer(text="powered by {}".format(bot.user.name))
    embeds.append(embed)
    async with bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM agifs")
      results = await cursor.fetchall()
      for result in results:
        channel_id = result[1]
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embed=embed)
          await asyncio.sleep(12)
        except:
            pass

@tasks.loop(minutes=1) 
async def automeme():    
 for j in range(50):
  async with bot.db.cursor() as cursor:
   await cursor.execute("SELECT * FROM automeme")
   results = await cursor.fetchall()
   for result in results:
    channel_id = result[1]
    async with aiohttp.ClientSession() as cs:
       async with cs.get('https://api.popcat.xyz/meme') as response3: 
        data3 = await response3.json()

        image = data3["image"]
        title = data3["title"]
        url = data3["url"]
        upvotes = data3["upvotes"]
        comments = data3["comments"]
        embed3 = discord.Embed(color=0x2f3136)
        embed3.set_image(url=image)
        e = discord.Embed(color=0x2f3136, description=f"[{title}]({url})")
        e.set_footer(text=f"❤️ {upvotes}  💬 {comments}")
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embeds=[embed3, e])
          await asyncio.sleep(60)
        except:
                continue

@tasks.loop(minutes=1) 
async def autonsfw():    
 for i in range(50):
  pics = ["hentai", "4k", "pussy", "boobs"]
  async with bot.db.cursor() as cursor:
   await cursor.execute("SELECT * FROM autonsfw")
   results = await cursor.fetchall()
   for result in results:
    channel_id = result[1]
    async with aiohttp.ClientSession() as cs:
      async with cs.get(f"http://api.nekos.fun:8080/api/{random.choice(pics)}") as r: 
       res = await r.json()
       embed2 = discord.Embed(color=0x2f3136)
       embed2.set_image(url=res['image'])
       try:
        channel = bot.get_channel(channel_id)
        await channel.send(embed=embed2)
        await asyncio.sleep(10)  
       except:
            continue


@tasks.loop(minutes=5)
async def stats():
  online = "<:online:1046291787007934537>"
  embed = discord.Embed(color=0x2f3136, description=f"{online} millions is running `{round(bot.latency * 1000)}ms`, serving `{len(bot.guilds)}` servers with `{len(set(bot.get_all_members()))}` members")
  embed.set_footer(text="next update in 5 minutes")
  stat_log = bot.get_channel(1047678747182112798)
  await stat_log.send(embed=embed)

class Client(commands.AutoShardedBot):
  def __init__(self):
    super().__init__(
        command_prefix=getprefix,
        intents=discord.Intents.all(),
        help_command=None, 
        case_insensitive=True,
        allowed_mentions=discord.AllowedMentions.none(),
        strip_after_prefix=True,  
        owner_ids=[1025634319483535423, 999254575188025376]
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
    female.start()
    male.start()
    anime.start()
    ricon.start()
    banner.start()
    fgif.start()
    mgif.start()
    agif.start()
    automeme.start()
    autonsfw.start()
    stats.start()
    print(f"logged in as {bot.user}")
bot = Client()
bot.run("MTAzMzgyMDE1MzgxMDUzNDQ2MQ.GrNfvS.sc6u8fP7c-DjZI3_Mko-5RReT-VdWO5-cPy3qU", reconnect=True)
