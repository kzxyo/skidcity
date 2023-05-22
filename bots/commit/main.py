import discord, os, datetime, aiohttp, asyncio, random, aiohttp, aiosqlite 
from discord.ext import commands, tasks  

class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=",", intents=discord.Intents.all(), help_command=None, owner_id=911351586398294037)  
  
    async def on_ready(self):
        await self.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="/commit"))
        print("---------------------")
        print("{} is online".format(bot.user))
        print("---------------------")
        

    async def setup_hook(self) -> None:
      for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await self.load_extension("cogs." + file[:-3])
      
      await self.load_extension("jishaku") 

bot = Bot()
bot.run("MTAxNTM0OTYwNzM1OTg1MjU4NQ.Gz8SfL.xkSRmE7z7OgShE0UHwqeUhyrl9sopuhssAq5co")                 
