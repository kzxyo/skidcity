import discord, jishaku, aiosqlite, os
from discord.ext import commands

class blood(commands.AutoShardedBot):
  def __init__(self):
    super().__init__(
        command_prefix=";",
        intents=discord.Intents.all(),
        help_command=None, 
        case_insensitive=True,
        allowed_mentions=discord.AllowedMentions.none(),
        strip_after_prefix=True,  
        owner_ids=[1114446438601064500 , 1087087109283782737],
        activity=discord.Activity(
               type=discord.ActivityType.playing, name="Booting Up.."
            ),
            status=discord.Status.idle,
    ) 
    self.color = 0x1C1A1B

  async def on_connect(self): 
    setattr(bot, "db", await aiosqlite.connect("blood.db"))
    print("CONNECTED TO AIOSQLITE BASE")
    await self.load_extension("jishaku")
    for file in os.listdir("./cogs"): 
      if file.endswith(".py"):
        try: 
            await self.load_extension("cogs." + file[:-3])
            print("I LOAD THE COG{}".format(file[:-3])) 
        except Exception as e: 
           print("I CANT LOAD THE COG {} - {}".format(file[:-3], e))


  async def on_ready(self):
    print(f"I LOG IN INTO : {bot.user}")

bot = blood()
bot.run("MTA3OTQ1MzA4MDE5MTUxMjU3Ng.G2wjqF.BeMa4cY8LWaDn2z0_IPD_OirPkQFM0Sv1jxf7o")