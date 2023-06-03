import discord, os, datetime, discord_ios, jishaku, random, json, nacl, traceback, asyncio, sys, textwrap ; from datetime import datetime, timezone, timedelta ; from discord.ext import tasks, commands ; from discord.gateway import DiscordWebSocket
from modules import extensions


class Bot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = 0xB1AAD8
        self.done = "<:v_done:1010717995099758634>"
        self.fail = "<:v_warn:1010718010828390400>"
        self.reply = "<:vile_reply:997487959093825646>"
        self.dash = "<:vile_dash:998014671107928105>"

bot = Bot(
    command_prefix=',,', 
    intents=discord.Intents.all(), 
    help_command=None, 
    activity=discord.Activity(
        type=discord.ActivityType.competing,
        name='discord.gg/heist', 
    ), 
    strip_after_prefix=True, 
    allowed_mentions=discord.AllowedMentions(
        everyone=False, 
        replied_user=False, 
        users=True, 
        roles=True
    )
)

@bot.event
async def on_ready():
    print('ready')
    await extensions.load(bot)

bot.run('MTAxNTI5NzA5NDcwNzMxNDY4OA.GKwHkV.bSx4Cu273Zz9X8BUFTm0HZtL7-x2ixZPUWN3fY')