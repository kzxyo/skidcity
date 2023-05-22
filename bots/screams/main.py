import discord, aiosqlite, os, sys, random, aiohttp, asyncio, datetime
from discord.ext import commands, tasks
from discord.gateway import DiscordWebSocket
from cogs.tickets import closeticket, ticketb
from utils.pfps import PFPS
from utils.classes import colors

@tasks.loop(seconds=15)
async def female(): 
    links = random.choice(PFPS.females)
    embeds = []
    embed = discord.Embed(color=colors.default, description="[our pinterest](https://www.pinterest.com/)", timestamp=datetime.datetime.now())
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
          await asyncio.sleep(15)
        except:
            pass

@tasks.loop(seconds=15)
async def male():
    links = random.choice(PFPS.males)
    embeds = []
    embed = discord.Embed(color=colors.default, description="[our pinterest](https://www.pinterest.com/)", timestamp=datetime.datetime.now())
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
          await asyncio.sleep(15)
        except:
            pass

@tasks.loop(seconds=15)
async def anime():
    links = random.choice(PFPS.animes)
    embeds = []
    embed = discord.Embed(color=colors.default, description="[our pinterest](https://www.pinterest.com/)", timestamp=datetime.datetime.now())
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
          await asyncio.sleep(15)
        except:
            pass

@tasks.loop(seconds=15) 
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
             embed = discord.Embed(color=colors.default, description="[our pinterest](https://www.pinterest.com/)", timestamp=datetime.datetime.now())
             embed.set_image(url=user.avatar.url)
             embed.set_author(name="follow our pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
             embed.set_footer(text="powered by {}".format(bot.user.name))
             try:
              channel = bot.get_channel(channel_id)
              await channel.send(embed=embed)
              await asyncio.sleep(15)
             except:
                pass

@tasks.loop(seconds=15)
async def banner():  
    links = random.choice(PFPS.banners)
    embeds = []
    embed = discord.Embed(color=colors.default, description="[our pinterest](https://www.pinterest.com/)", timestamp=datetime.datetime.now())
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
          await asyncio.sleep(15)
        except:
            pass

@tasks.loop(seconds=15)
async def fgif():  
    links = random.choice(PFPS.female_gifs)
    embeds = []
    embed = discord.Embed(color=colors.default, description="[our pinterest](https://www.pinterest.com/)", timestamp=datetime.datetime.now())
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
          await asyncio.sleep(15)
        except:
            pass

@tasks.loop(seconds=15)
async def mgif():  
    links = random.choice(PFPS.male_gifs)
    embeds = []
    embed = discord.Embed(color=colors.default, description="[our pinterest](https://www.pinterest.com/)", timestamp=datetime.datetime.now())
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
          await asyncio.sleep(15)
        except:
            pass

@tasks.loop(seconds=15)
async def agif():  
    links = random.choice(PFPS.anime_gifs)
    embeds = []
    embed = discord.Embed(color=colors.default, description="[our pinterest](https://www.pinterest.com/)", timestamp=datetime.datetime.now())
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
          await asyncio.sleep(15)
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
        embed3 = discord.Embed(color=colors.default)
        embed3.set_image(url=image)
        e = discord.Embed(color=colors.default, description=f"[{title}]({url})")
        e.set_footer(text=f"❤️ {upvotes}  💬 {comments}")
        try:
          channel = bot.get_channel(channel_id)
          await channel.send(embeds=[embed3, e])
          await asyncio.sleep(15)
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
       embed2 = discord.Embed(color=colors.default)
       embed2.set_image(url=res['image'])
       try:
        channel = bot.get_channel(channel_id)
        await channel.send(embed=embed2)
        await asyncio.sleep(15)  
       except:
            continue


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), help_command=None,
                         owner_ids=[880267615694647327, 863641863076053032])

    async def on_connect(self):
        await db()

    async def on_ready(self):
        self.add_view(closeticket())
        self.add_view(ticketb())
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
        print("{} is online".format(bot.user))

    async def setup_hook(self) -> None:
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension("cogs." + file[:-3])
        await self.load_extension("jishaku")


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

bot = Bot()


async def db():
    setattr(bot, "db", await aiosqlite.connect("main.db"))
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS female (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS male (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS anime (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS banner (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS random (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS fgifs (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS mgifs (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS agifs (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS automeme (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS autonsfw (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS nodata (user INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS whitelisted (guild INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS stfu (user_id INTEGER, guild_id INTEGER);")
        await cursor.execute("CREATE TABLE IF NOT EXISTS skull (user_id INTEGER, guild_id INTEGER);")
        await cursor.execute("CREATE TABLE IF NOT EXISTS restore (guild_id INTEGER, user_id INTEGER, roles TEXT);")
    await bot.db.commit()


bot.run("MTA1ODk4NTgxNDU1NTYzNTczMg.GRSURA.knGvSapNeTrxLCHPu8UDNnDt-zfRIhE1fOqN8c")