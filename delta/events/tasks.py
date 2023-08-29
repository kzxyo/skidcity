from discord.ext import tasks, commands
import discord, asyncio, random, datetime
from cogs.donor import checktag
from handlers.pfps import PFPS

@tasks.loop(minutes=5)
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


class Tasks(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot 

    @commands.Cog.listener()
    async def on_ready(self): 
      await self.bot.wait_until_ready()
      counter_update.start(self.bot)
      delete.start(self.bot)       
      

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Tasks(bot))                 