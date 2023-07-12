import asyncio
import logging
import datetime
import socket
import sys
import subprocess
from multiprocessing import Process
from typing import Any, Coroutine, Optional, Type

import aiohttp.connector
import orjson
import redis.asyncio as redis
import uvloop
from asyncpg import Connection, Pool, create_pool, Record
from discord import AllowedMentions, AuditLogEntry, Intents, Message, Interaction, Attachment
from discord.ext import tasks
from discord.ext.commands import (AutoShardedBot, CheckFailure, CommandError,
                                  CommandNotFound, DisabledCommand, NotOwner,
                                  UserInputError, when_mentioned_or, Context as ct)
from discord.message import Message
from discord.utils import utcnow
from pomice import Node
from winerp import Client

from cogs.music import Music
from utilities.managers import Cache, Help, Redis, Database, ClientSes
from utilities.webserver.main import WebServer
logger = logging.getLogger(__name__)

from . import config
from .managers import Context


aiohttp.resolver.aiodns_default = True
aiohttp.resolver._DefaultType = aiohttp.resolver.AsyncResolver
aiohttp.resolver.DefaultResolver = aiohttp.resolver.AsyncResolver
aiohttp.connector.DefaultResolver = aiohttp.resolver.AsyncResolver
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class Rec(Record):
    def __getattr__(self, name: str) -> Any:
        if name in self.keys():
            return self[name]
        return super().__getattr__(name)


class Lair(AutoShardedBot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            command_prefix=self.get_prefix,
            shard_count=1,
            case_insensitive=True,
            intents=Intents.all(),
            allowed_mentions=AllowedMentions(
                everyone=False,
                users=True,
                roles=False,
                replied_user=False,
            ),
            auto_update=False,
            owner_ids=config.owner_ids,
            help_command=Help(command_attrs={"aliases": ["h"]})
        )

        self.session: ClientSes
        self.uptime: datetime = utcnow()
        self.db: Pool
        self.node: Node
        self.web = WebServer(self)
        self.ipc = Client(local_name="lair", port=6000)
        self.cache = Cache(self)

    async def shell(self, command: str) -> str:
        process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
        stdout, _ = await process.communicate()
        return stdout.decode()

    async def on_ready(self) -> None:
        self.loop.create_task(Music(self).lavalink())

    async def setup_hook(self) -> Coroutine[Any, Any, None]:
        logger.info('Bot process initialized')
        self.db: Database = await Database().connect()
        await self.cache._init()
        self.loop.create_task(self.ipc.start())
        await config.Start.load(self)
        self.redis: Redis = await Redis().from_url()
        await self.load_extension("jishaku")
        self.session = ClientSes()
        self.uptime
        self.invalidate_api_keys.start()
        return await super().setup_hook()

    async def close(self):
        await self.db.close()
        await self.session.close()
        await self.redis.close()
        await super().close()


    @tasks.loop(hours=1)
    async def invalidate_api_keys(self):
        keys = await self.db.fetch('SELECT user_id, expiry FROM api_keys')
        current_datetime = datetime.datetime.now()

        for user_id, expiry in keys:
            if not expiry:
                continue
            if expiry < current_datetime:
                await self.db.execute('DELETE FROM api_keys WHERE user_id = $1', user_id)
                logger.info(f"Invalidated {user_id}'s api key.")


    async def get_prefix(self, message: Message, strict: bool = False) -> Any:
        prefix = await self.cache.get(f'prefix:{message.guild.id}')
        if not prefix:
            prefix = ","

        if strict:
            return prefix
        
        else:
            return when_mentioned_or(prefix)(self, message)
        
    async def get_context(
        self, message: Message | Interaction, /, *, cls: type[ct[AutoShardedBot]] | None = None
    ) -> Context:
        return await super().get_context(message, cls=cls or Context)

    async def on_message_edit(self, before: Message | None, after: Message | None):
        if not self.is_ready() or before.author.bot or not before.guild:
            return

        elif before.content == after.content or not after.content:
            return

        else:
            await self.process_commands(after)

    async def on_command_error(self, ctx: Context, error: Exception) -> Message:
        bleh = (
            CommandNotFound,
            NotOwner,
            CheckFailure,
            DisabledCommand,
            UserInputError,
        )

        if type(error) in bleh:
            logger.error(error)

        elif isinstance(error, CommandError):
            return await ctx.warn(error)
        
    def __repr__(self) -> str:
        tasks = len(asyncio.all_tasks())
        count = sum(1 for guild in self.guilds if not guild.chunked)
        return f"<Lair active_tasks={tasks} unchunked_guilds={count}>"
    
    async def on_audit_log_entry_create(self, entry: AuditLogEntry) -> None:
        if not self.is_ready():
            return
        
        event_name = "AuditLogEntry." + entry.action.name
        await self.cache.set(event_name, entry, append=True)

    async def on_message(self, message: Message) -> Message:
        if not message.guild or not self.is_ready():
            return
        
        if message.content == f"<@{message.guild.me.id}>" or message.content == f"<@!{message.guild.me.id}>":
            prefix = await self.get_prefix(message, strict=True)
            return await message.reply(f'My prefix for this guild is **{prefix}**')
        
        await self.process_commands(message)