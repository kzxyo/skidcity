import discord_ios
import discord, aiosqlite, json, aiohttp, random, asyncio, datetime
from discord.ext import commands, tasks
from discord import Embed
import os
from cogs.utils.list import PFPS
from cogs.utils import maria
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

async def getprefix(bot, message):
       if not message.guild: return ",,"
       selfprefix = ",," 
       guildprefix = ",,"
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
            guildprefix = ",,"    

       return guildprefix, selfprefix

config = json.load(open("db/config.json", encoding="UTF-8"))

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
class crime(commands.AutoShardedBot):
  def __init__(self):
    super().__init__(
        command_prefix=getprefix,
        intents=discord.Intents.all(),
        help_command=None,
        case_insensitive=True,
        allowed_mentions=discord.AllowedMentions.none(),
        strip_after_prefix=True,
        owner_ids=[950183066805092372, 932378206537916466]
    ) 

      
  async def on_connect(self): 
    setattr(bot, "db", await aiosqlite.connect("db/main.db"))
    print("Attempting to connect to Discord's API")
    await self.load_extension("jishaku")
    for file in os.listdir("./cogs"): 
      if file.endswith(".py"):
        try: 
            await self.load_extension("cogs." + file[:-3])
            print("loaded extension {}".format(file[:-3])) 
        except Exception as e: 
           print("unable to load extension {} - {}".format(file[:-3], e))
    female.start()
    male.start()
    anime.start()
    ricon.start()
    banner.start()
    fgif.start()
    mgif.start()
    agif.start()

bot = crime()
bot.run(str(config["token"]))