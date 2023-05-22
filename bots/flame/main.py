import discord, asyncio, os, json, time 
import jishaku
import random
from discord.ext import commands, tasks

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

def prefix(client, message):
    with open("data\prefixes.json", "r") as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def run():
    try:
        await client.start("OTEyMzQ0MzQ5NDcwMjQ0OTc1.GITJTE.urbpcpo8b8sa903YO-kXlt5EeT9zquklE0ciG0", reconnect=True)
    except KeyboardInterrupt:
        await client.close()

@tasks.loop(seconds=10)
async def status():
    status = [",help"]  
    await client.change_presence(activity=discord.Streaming(name=random.choice(status), url="https://www.twitch.tv/ninja")) 

class Client(commands.Bot): 
    def __init__(self):
        super().__init__(
            intents=discord.Intents.all(),
            command_prefix=",",
            help_command=None,
            owner_id = 950183066805092372
        )
        self.uptime = time.time()

    async def on_connect(self):
        print("attempting to connect to discord API")
        await self.load_extension("jishaku")
        await load()

    async def on_ready(self):
        status.start()
        print('Bot is ready.') 
        
client = Client()
if __name__ == "__main__":
 loop = asyncio.get_event_loop()
 loop.run_until_complete(run())