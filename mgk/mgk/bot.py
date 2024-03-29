import discord, jishaku, datetime, os, aiohttp, pymysql
from discord import Intents, Activity, ActivityType, AllowedMentions
from discord.ext import commands
from mgk.cfg import MGKCFG
from modules.database import fetchall, fetchone, execute, _db
from modules.context import context
from discord.ext.commands.bot import when_mentioned_or
from modules.http import get

class MGK(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=Intents.all(),
            help_command=None,
            owner_ids=MGKCFG.OWNERS,
            case_insensitive=True,
            strip_after_prefix=True,
            allowed_mentions=AllowedMentions(
                everyone=False,
                replied_user=False,
                users=True,
                roles=False
            ),
            #proxy = "http://brd.superproxy.io:22225",
            #proxy_auth = aiohttp.BasicAuth("brd-customer-hl_7bd3953d-zone-nexcord_discord", "w69dur1wn5hb"),
            shard_count = 1,
            # activity = Activity(type=ActivityType.watching, name=f"{len(self.commands)}{MGKCFG.ACTIVITY}"),
            **kwargs
        )
        self.uptime = datetime.datetime.now()
        
        self.http.get = get

        self.db = pymysql.connect(**_db)
        self.db.fetchall = fetchall
        self.db.fetchone = fetchone
        self.db.execute = execute
        
    async def get_prefix(self, message):
        p = MGKCFG.DEFAULT_PREFIX
        r = await self.db.fetchone("SELECT prefix FROM prefix WHERE guild = %s", (message.guild.id,))
        guild = str(r['prefix']) if r is not None else p
        r = await self.db.fetchone("SELECT prefix FROM selfprefix WHERE user = %s", (message.author.id,))
        user = str(r['prefix']) if r is not None else guild
        prefix = [user, guild]
        return when_mentioned_or(*prefix)(self, message)

    async def get_context(self, message, *, cls=context):
        return await super().get_context(message, cls=cls)

    async def cog(self, extension: str):
        try:
            await self.load_extension(extension)
            print(f"{extension} is loaded")
        except Exception as err:
            print(f"errror at {extension}: {err}")
            
    async def handler(self, handler: str):
        try:
            await self.load_extension(handler)
            print(f"{handler} working")
        except Exception as err:
            print(f"errror at {handler}: {err}")

    async def load(self):
        await self.load_extension("jishaku")
        os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        os.environ["JISHAKU_HIDE"] = "True"
        os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
        os.environ["JISHAKU_RETAIN"] = "True"
        owners = ", ".join([f"{self.get_user(id).name}#{self.get_user(id).discriminator}" for id in self.owner_ids])
        print(f"jishaku is loaded | {owners}")
        for i in ["cogs"]:
            for j in os.listdir(i):
                if "pycache" not in j:
                    await self.cog(f"{i}.{j[:-3]}")
        for i in ["handlers"]:
            for j in os.listdir(i):
                if "pycache" not in j:
                    await self.handler(f"{i}.{j[:-3]}")
                    
    @property
    def cmds(self):
        return sum(1 for command in self.walk_commands() if not command.parent or (command.parent and command.parent.cog_name != "Jishaku"))
