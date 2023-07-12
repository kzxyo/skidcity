from aiohttp import BasicAuth
from selfcord import Client, Message, User, CaptchaHandler, Guild
from multiprocessing import Process, Pool
import redis.asyncio as redis
import winerp
import asyncio
import sys
import contextlib
import orjson
import json
from twocaptcha import TwoCaptcha
import logging
from loguru import logger
from typing import Any, Coroutine, Dict, List, Optional, Union
import re
from redis.asyncio import StrictRedis as AsyncStrictRedis
from redis.asyncio.connection import BlockingConnectionPool
from redis.backoff import EqualJitterBackoff
from redis.retry import Retry
from capmonster_python import HCaptchaTask
from xxhash import xxh64_hexdigest
worker_tokens = ['MTIwMjc4OTQ1MDQzMDU0NTky.G8rj3Z.Rdfhw1JIfQ_FlP8fPmf1plUirNBc_poRLJFxxo', "MTA5Mzk1NjUyMTMzMjgzODQ1Mw.Gg3Cal.zdu_duZ6fcZFDSs1uL8a4Ds7YL5v28pQ38Qt7E"]
logging.getLogger("selfcord").setLevel(logging.CRITICAL)
logging.getLogger("selfcord.http").setLevel(logging.CRITICAL)
logging.getLogger("selfcord.client").setLevel(logging.CRITICAL)
logging.getLogger("selfcord.gateway").setLevel(logging.CRITICAL)
logging.getLogger("pomice").setLevel(logging.CRITICAL)
logging.getLogger("aiohttp.access").setLevel(logging.CRITICAL)
proxy = "http://root:wise@144.172.67.168:31280"

class Handler(CaptchaHandler):
    def __init__(self, bot: Client):
        self.bot = bot
        self.config = {"apiKey": "e67a7b85f7eebe93ff051f5fc4a19006"}

    def two_captcha(self, data: dict, proxy: str, proxy_auth: BasicAuth) -> str:
        solver = TwoCaptcha("e67a7b85f7eebe93ff051f5fc4a19006")
        result = solver.hcaptcha(
            sitekey=data.get('captcha_sitekey'),
            url='https://discord.com/channels/@me',
            data=data.get("captcha_rqdata")
        )
        return result['code']

    async def fetch_token(self, data: Dict[str, Any], proxy: str | None, proxy_auth: BasicAuth | None) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.two_captcha, data, proxy, proxy_auth)


class Redis(AsyncStrictRedis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock: asyncio.Lock = asyncio.Lock()

    def __repr__(self):
        return f"<Redis lock={self._lock.locked()}>"

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
    ):
        return await cls(
            connection_pool=BlockingConnectionPool.from_url(
                "redis://default:lair@127.0.0.1:6379/0",
                decode_responses=True,
                timeout=1,
                max_connections=7000,
                retry=Retry(backoff=EqualJitterBackoff(3, 1), retries=100),
            )
        )

class IPC(winerp.Client):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(
            local_name=name,
            port=6000,
            reconnect=True
        )

class Worker(Client):
    def __init__(self, tokens: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, captcha_handler=Handler(self))
        self.redis = None
        self.logger = logger
        self.logger.remove()
        self.logger.add(
            sys.stdout,
            colorize=True,
            format=(
                "<cyan>[</cyan><blue>{time:YYYY-MM-DD HH:MM:SS}</blue><cyan>]</cyan> (<magenta>worker:{function}</magenta>) <yellow>@</yellow> <fg"
                " #BBAAEE>{message}</fg #BBAAEE>"
            ),
        )
        self.worker = xxh64_hexdigest(tokens)
        self.ipc = IPC(f"worker:{self.worker}")
        self.run(tokens)

    async def on_guild_update(self, before: Guild, after: Guild):
        print(before.vanity_url_code if before.vanity_url_code else print(before))
        if before.vanity_url_code != after.vanity_url_code:
            if after.vanity_url_code:
                print(f'Before: {before.vanity_url_code} After: {after.vanity_url_code}')

    async def setup_hook(self) -> Coroutine[Any, Any, None]:
        self.redis: Redis = await Redis.from_url()
        await self.loop.create_task(self.ipc.start())
        
    async def on_user_update(self, before, after):
        if before.display_avatar != after.display_avatar:
            channel = self.get_channel(1126445318825848832)
            if before.display_avatar:
                image = await before.avatar.read()
                file = await before.display_avatar.to_file(filename=f'{before.id}.{"png" if not before.display_avatar.is_animated() else "gif"}')
                message = await channel.send(file=file)

    def find_invites(self, userbio):
        pattern = r'/(?P<invite>[^\s/]+)'
        invites = re.findall(pattern, userbio)
        return invites

    async def on_ready(self) -> None:
        print('ready')
        print(self.user)
        for guild in self.guilds:
            if not guild.chunked:
                await guild.chunk(cache=True)

    async def on_message(self, message: Message) -> None:
        if not message.guild:
            return

        if message.author.id == 1093956521332838453:
            if message.content.startswith('discord.gg'):
                await self.accept_invite(message.content)
        await self.redis.publish(
            f"worker1:{message.channel.id}",
            orjson.dumps(
                {
                    "content": message.content,
                    "embed": [e.to_dict() for e in message.embeds],
                    "images": [
                        {
                            "url": a.url,
                            "file": a.filename
                        }
                        for a in message.attachments
                    ]
                }
            ),
        )
run = []
if __name__ == "__main__":
    try:
        for token in worker_tokens:
            process = Process(target=Worker, args=(token,))
            run.append(process)
            process.start()
    except:
        pass
    finally:
        for process in run:
            process.join()
            process.terminate()
            process.close()