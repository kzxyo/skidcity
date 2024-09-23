import discord, asyncpg, typing, time, os, discord_ios, pomice, asyncio, json

from typing import List
from humanfriendly import format_timespan

from discord.ext import commands

from bot.helpers import StartUp
from bot.helpers import EvictContext, HelpCommand
from bot.ext import Client
from bot.database import create_db
from bot.headers import Session
from bot.dynamicrolebutton import DynamicRoleButton

from cogs.voicemaster import vmbuttons
from cogs.ticket import CreateTicket, DeleteTicket
from cogs.giveaway import GiveawayView

from rivalapi.rivalapi import RivalAPI
from redis.asyncio import StrictRedis as AsyncStrictRedis
from redis.asyncio.connection import BlockingConnectionPool
from redis.backoff import EqualJitterBackoff
from redis.retry import Retry

class Redis(AsyncStrictRedis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock: asyncio.Lock = asyncio.Lock()

    def __repr__(self):
        return f"<bot.bot.Redis lock={self._lock}>"

    async def keys(self, pattern: str = "*"):
        async with self._lock:
            return await super().keys(pattern)

    async def get(self, key: str):
        async with self._lock:
            data = await super().get(key)

            if data:
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            return data

    async def set(self, key: str, value: any, **kwargs):
        async with self._lock:
            if type(value) in (dict, list, tuple):
                value = json.dumps(value)

            return await super().set(key, value, **kwargs)

    async def delete(self, *keys: str):
        async with self._lock:
            return await super().delete(*keys)

    async def ladd(self, key: str, *values: str, **kwargs):
        values = list(values)
        for index, value in enumerate(values):
            if type(value) in (dict, list, tuple):
                values[index] = json.dumps(value)

        async with self._lock:
            result = await super().sadd(key, *values)
            if kwargs.get("ex"):
                await super().expire(key, kwargs.get("ex"))

            return result

    async def lget(self, key: str):
        async with self._lock:
            _values = await super().smembers(key)

        values = list()
        for value in _values:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass

            values.append(value)

        return values

    async def get_lock(self, key: str):
        return await self._lock()

    @classmethod
    async def from_url(
        cls,
    ):  # URL: redis://default:f6sYIi6qucgqHsHJIKeLOsqRv9Oj9BAG@redis-11641.c282.east-us-mz.azure.redns.redis-cloud.com:11641"
        return await cls(
            connection_pool=BlockingConnectionPool.from_url(
                "redis://default:f6sYIi6qucgqHsHJIKeLOsqRv9Oj9BAG@redis-11641.c282.east-us-mz.azure.redns.redis-cloud.com:11641",
                decode_responses=True,
                timeout=1,
                max_connections=7000,
                retry=Retry(backoff=EqualJitterBackoff(3, 1), retries=100),
            )
        )

class Evict(commands.AutoShardedBot):
  def __init__(self, db: asyncpg.Pool=None):
        super().__init__(command_prefix=EvictContext.getprefix, allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True, replied_user=False), intents=discord.Intents.all(), 
                         owner_ids=[214753146512080907, 598125772754124823], shard_count=1,
                         help_command=HelpCommand(), strip_after_prefix=True, activity=discord.CustomActivity(name="🔗 evict.cc"))
        
        self.db = db
        
        self.color = 0xCCCCFF
        self.error_color= 0xFFFFED
        self.yes = "<:approve:1263726951613464627>"
        self.no = "<:deny:1269374707484852265>"
        self.warning = "<:warn:1263727178802004021>"
        self.left = "<:left:1263727060078035066>"
        self.right = "<:right:1263727130370637995>"
        self.goto = "<:filter:1263727034798968893>"
        self.pomice = pomice.NodePool()
        
        self.ext = Client(self)
        
        self.m_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.member)
        self.c_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.channel)
        self.m_cd2=commands.CooldownMapping.from_cooldown(1,10,commands.BucketType.member)
        self.global_cd = commands.CooldownMapping.from_cooldown(2, 3, commands.BucketType.member)
        
        self.uptime = time.time()
        self.session = Session()
        
        self.evict_api = os.environ.get("evict_api")
        self.rival_api = os.environ.get("rival_api")
        self.proxy_url = os.environ.get("proxy_url")
        self.rival = RivalAPI(self.rival_api)
        
        self.commands_url = os.environ.get("commands_url")
        self.support_server = os.environ.get("support_server")
        
  async def create_db_pool(self):
        self.db = await asyncpg.create_pool(port="5432", database="evict", user="postgres", host="localhost", password="admin")
        
  async def on_ready(self) -> None:
        print("I'm online!")
        await self.cogs["Music"].start_nodes()
        
  async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
      if isinstance(error, commands.CommandNotFound): return 
      if isinstance(error, commands.NotOwner): pass
      if isinstance(error, commands.CheckFailure): 
        if isinstance(error, commands.MissingPermissions): return await ctx.warning(f"This command requires **{error.missing_permissions[0]}** permission")
      elif isinstance(error, commands.CommandOnCooldown):
        if ctx.command.name != "hit": return await ctx.reply(embed=discord.Embed(color=0xE1C16E, description=f"⌛ {ctx.author.mention}: You are on cooldown. Try again in {format_timespan(error.retry_after)}"), mention_author=False)    
      if isinstance(error, commands.MissingRequiredArgument): return await ctx.cmdhelp()
      if isinstance(error, commands.EmojiNotFound): return await ctx.warning(f"Unable to convert {error.argument} into an **emoji**")
      if isinstance(error, commands.MemberNotFound): return await ctx.warning(f"Unable to find member **{error.argument}**")
      if isinstance(error, commands.UserNotFound): return await ctx.warning(f"Unable to find user **{error.argument}**")
      if isinstance(error, commands.RoleNotFound): return await ctx.warning(f"Couldn't find role **{error.argument}**")
      if isinstance(error, commands.ChannelNotFound): return await ctx.warning(f"Couldn't find channel **{error.argument}**")
      if isinstance(error, commands.ThreadNotFound): return await ctx.warning(f"I was unable to find the thread **{error.argument}**")
      if isinstance(error, commands.UserConverter): return await ctx.warning(f"Couldn't convert that into an **user** ")
      if isinstance(error, commands.MemberConverter): return await ctx.warning("Couldn't convert that into a **member**")
      if isinstance(error, commands.BadArgument): return await ctx.warning(error.args[0])
      if isinstance(error, commands.BotMissingPermissions): return await ctx.warning(f"I do not have enough **permissions** to execute this command")
      if isinstance(error, commands.CommandInvokeError): return await ctx.warning(error.original)
      if isinstance(error, discord.HTTPException): return await ctx.warning("Unable to execute this command")
      if isinstance(error, commands.NoPrivateMessage): return await ctx.warning(f"This command cannot be used in private messages.")
      if isinstance(error, commands.UserInputError): return await ctx.send_help(ctx.command.qualified_name)
      if isinstance(error, discord.NotFound): return await ctx.warning(f"**Not found** - the **ID** is invalid")
      if isinstance(error, commands.MemberNotFound): return await ctx.warning(f"I was unable to find a member with the name: **{error.argument}**")
      if isinstance(error, commands.GuildNotFound): return await ctx.warning(f"I was unable to find that **server** or the **ID** is invalid")
      if isinstance(error, commands.BadInviteArgument): return await ctx.warning(f"Invalid **invite code** given")
        
  async def channel_ratelimit(self,message:discord.Message) -> typing.Optional[int]:
      cd=self.c_cd
      bucket=cd.get_bucket(message)
      return bucket.update_rate_limit()

  async def on_message_edit(self, before, after):
        if before.content != after.content: await self.process_commands(after)

  async def prefixes(self, message: discord.Message) -> List[str]: 
     prefixes = []
     for l in set(p for p in await self.command_prefix(self, message)): prefixes.append(l)
     return prefixes

  async def member_ratelimit(self,message:discord.Message) -> typing.Optional[int]:
        cd=self.m_cd
        bucket=cd.get_bucket(message)
        return bucket.update_rate_limit()
      
  async def on_message(self, message: discord.Message): 
      
        channel_rl=await self.channel_ratelimit(message)
        member_rl=await self.member_ratelimit(message)
      
        if channel_rl == True:
          return
      
        if member_rl == True:
          return
      
        if message.content == "<@{}>".format(self.user.id): return await message.reply(content="prefixes: " + " ".join(f"`{g}`" for g in await self.prefixes(message)))
        await self.process_commands(message) 
    
  async def setup_hook(self):
        
        self.add_view(vmbuttons())
        self.add_dynamic_items(DynamicRoleButton)
        self.add_view(CreateTicket())
        self.add_view(DeleteTicket())
        self.add_view(GiveawayView())
        
        await self.load_extension('jishaku')
        await self.create_db_pool()
        self.redis: Redis = await Redis.from_url()
        
        await StartUp.loadcogs(self)
       
        await create_db(self)

  async def get_context(self, message: discord.Message, cls=EvictContext) -> EvictContext:
      return await super().get_context(message, cls=cls)