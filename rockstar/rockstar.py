import discord, json, psutil, aiohttp, os, jishaku, sys
from discord.ext import commands
from discord.ext.commands import Bot

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
        token = configData["token"]
        
class rockstar(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=(self_prefix),
            intents=intents.all(),
            help_command=None,
            case_insensitive=True,
            activity=discord.Activity(type=discord.ActivityType.watching, name="mention for prefix"),
            owner_ids=[983815296760549426]
        )
        
    async def setup_hook(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension("cogs." + file[:-3])
                print(f'Loaded cog: {file[:-3]}')
        await self.load_extension("jishaku")
            
def self_prefix(bot, ctx):
    with open('selfprefixes.json', 'r') as f:
        selfprefixes = json.load(f)
    if str(ctx.author.id) not in selfprefixes:
        selfprefixes[str(ctx.author.id)] = '.'
    return selfprefixes[str(ctx.author.id)]


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

bot = rockstar()
bot.run(token)