from mgk.bot import MGK

bot = MGK()

import os, pathlib, discord
from dotenv import load_dotenv
from mgk.cfg import MGKCFG, E, CLR

@bot.event
async def on_ready():
    await MGK.load(bot)
    await bot.change_presence(activity=discord.CustomActivity(name=f"{bot.cmds}{MGKCFG.ACTIVITY}"))
    ch = bot.get_channel(1147914717365534831)
    await ch.send(embed=discord.Embed(description=f"{E.smile} - **I revived lol**", color=CLR.green))
    
load_dotenv(dotenv_path=pathlib.Path("mgk/.ENV"))
bot.run(os.getenv("TOKEN"))
