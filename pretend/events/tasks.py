from discord.ext import tasks, commands
import discord, asyncio, random, datetime
from cogs.donor import checktag
from handlers.pfps import PFPS

async def get_genre(category): 
  if category == "male_pfps": return random.choice(PFPS.male)
  elif category == "female_pfps": return random.choice(PFPS.female)
  elif category == "anime_pfps": return random.choice(PFPS.anime)
  elif category == "male_gifs": return random.choice(PFPS.male_gif)
  elif category == "female_gifs": return random.choice(PFPS.female_gif)
  elif category == "anime_gifs": return random.choice(PFPS.anime_gif)
  elif category == "banners": return random.choice(PFPS.banner)

@tasks.loop(minutes=13)
async def discrim_update(bot: commands.AutoShardedBot): 
  results = await bot.db.fetch("SELECT role_id FROM discrim") 
  for result in results: 
   guild = bot.get_guild(int(result['guild_id']))
   if guild: 
    role = guild.get_role(int(result['role_id']))
    if not role: 
      await bot.db.execute('DELETE FROM discrim WHERE guild_id = $1', guild.id)
      continue 
    for member in role.members: 
     if member.discriminator != "0001": 
      try: await member.remove_roles(role, reason="member doesn't have a good 0001 discriminator name anymore")   
      except: continue 
    for member in [m for m in guild.members if m.discriminator == "0001"]:
     if checktag(member.name) is True: 
      try: await member.add_roles(role, reason="member has a good 0001 discriminator name") 
      except: continue   

@tasks.loop(minutes=10)
async def counter_update(bot: commands.AutoShardedBot): 
  results = await bot.db.fetch("SELECT * FROM counters")
  for result in results: 
   channel = bot.get_channel(int(result["channel_id"]))
   if channel: 
    guild = channel.guild 
    module = result["module"]
    if module == "members": target = str(guild.member_count)
    elif module == "humans": target = str(len([m for m in guild.members if not m.bot]))
    elif module == "bots": target = str(len([m for m in guild.members if m.bot])) 
    elif module == "boosters": target = str(len(guild.premium_subscribers))
    elif module == "voice": target = str(sum(len(c.members) for c in guild.voice_channels))     
    name = result["channel_name"].replace("{target}", target)
    await channel.edit(name=name, reason="updating counter")         

@tasks.loop(hours=6)
async def delete(bot):
   lis = ["snipe", "reactionsnipe", "editsnipe"]
   for l in lis: await bot.db.execute(f"DELETE FROM {l}")  

@tasks.loop(minutes=2)
async def autopfp(bot: commands.AutoShardedBot): 
  results = await bot.db.fetch("SELECT * FROM autopfp")
  embed = discord.Embed(color=bot.color, title="pfps source", url="https://pinterest.com/antipfps").set_author(name="follow the pinterest", icon_url="https://images-ext-1.discordapp.net/external/patbltTGq126PE_DJ-ZVbxORqhW8cipRzo95lYr6FaE/%3Fsize%3D240%26quality%3Dlossless/https/cdn.discordapp.com/emojis/1026647994390552666.webp")
  for result in results: 
   print("working")
   if result['genre'] == "random": links = await get_genre(random.choice(["anime_pfps", "anime_gifs", "male_pfps", "male_gifs", "female_pfps", "female_gifs"]))
   if result['genre'] == "banner": links = await get_genre("banners")
   else: links = await get_genre(f"{result['genre']}_{result['type']}s")
   embed.set_image(url=links)
   embed.timestamp = datetime.datetime.now()
   channel_id = result['channel_id']
   channel = bot.get_channel(channel_id)
   if channel: 
     print("channel found")
     await channel.send(embed=embed)
     await asyncio.sleep(30)   
             
class Tasks(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot 

    @commands.Cog.listener()
    async def on_ready(self): 
      await self.bot.wait_until_ready()
      counter_update.start(self.bot)
      delete.start(self.bot)       
      autopfp.start(self.bot)
      discrim_update.start(self.bot)

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Tasks(bot))                 