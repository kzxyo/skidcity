from __future__ import annotations

import os
import time
from collections.abc import Generator
from contextlib import contextmanager
from ctypes import Union
from datetime import timedelta
from typing import TypedDict

import humanize
import tuuid
from async_timeout import Timeout
from boltons.cacheutils import LRI
from loguru import logger as log

from redis import Redis as SyncRedis
from redis.asyncio import Redis as _Redis
from redis.asyncio.connection import BlockingConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import EqualJitterBackoff
from redis.commands.json import JSON
from redis.exceptions import NoScriptError, ResponseError

from .encoders import JSONPipeline
from .lock import RivalLock
from .lua_scripts import INCREMENT_SCRIPT, INCREMENT_SCRIPT_HASH

REDIS_URL = os.environ["REDIS_URL"]


def fmtseconds(seconds: Union[int, float], unit="microseconds") -> str:
    """String representation of the amount of time passed.

    Args:
        seconds (Union[int, float]): seconds from ts
        minimum_unit: str

    """

    return humanize.naturaldelta(timedelta(seconds=seconds), minimum_unit=unit)


class _RedisHolder(TypedDict):
    created: int
    client: "RivalRedis"


GLOBAL_REDIS: _RedisHolder = {}


@contextmanager
def blocking_redis() -> Generator[SyncRedis, None, None]:
    """Borrow a Sync redis instance. Must be used as a context manager!"""
    redis = SyncRedis.from_url(REDIS_URL)
    try:
        yield redis
    finally:
        redis.close()


class RivalRedis(_Redis):
    def __init__(self, *a, **ka):
        self.locks = LRI(3000)
        self.namespace = tuuid.tuuid()
        self.lock_prefix = "lock:"
        self.is_ratelimited = self.ratelimited
        self.json_instance: JSON = None
        super().__init__(*a, **ka)

    async def __aenter__(self) -> "RivalRedis":
        return await self.initialize()

    async def __aexit__(self, exc_type, exc_value, traceback):
        log.warning("Shutting down our Redis.")
        await self.close()

    def pipeline2(self, transaction=True, shard_hint=None):
        """Original Redis pipeline"""
        return super().pipeline(transaction=transaction, shard_hint=shard_hint)

    def pipeline(self, transaction=True, shard_hint=None):
        json = self.json()
        p = JSONPipeline(connection_pool=self.connection_pool, response_callbacks=json.MODULE_CALLBACKS, transaction=transaction, shard_hint=shard_hint)
        p._encode = json._encode
        p._decode = json._decode
        return p

    def __repr__(self):
        return f"{self.__class__.__name__} {self.namespace} <{self.connection_pool!r}>"

    async def jsonset(self, *a, **ka):
        return await self.json().set(*a, **ka)

    async def jsonget(self, *a, **ka):
        try:
            return await self.json().get(*a, **ka)
        except ResponseError:
            return None

    async def getstr(self, key):
        return (await self.get(key)).decode("UTF-8")

    @classmethod
    async def from_url(cls, url=REDIS_URL, retry="jitter", max_connections=7000, attempts=100, timeout=120, **ka):
        retry_form = Retry(backoff=EqualJitterBackoff(3, 1), retries=attempts)
        GLOBAL_REDIS["created"] = time.time()
        GLOBAL_REDIS["client"] = RivalRedis(connection_pool=BlockingConnectionPool.from_url(url=url, timeout=timeout, max_connections=max_connections, retry=retry_form, health_check_interval=10, **ka))
        log.warning(f"New Redis! {url}: timeout: {timeout} retry: {retry} attempts: {attempts} ")
        ping_time = 0

        redis = GLOBAL_REDIS["client"]
        async with Timeout(9):
            for _ in range(5):
                start = time.time()
                await redis.ping()
                ping_time += time.time() - start
        avg = ping_time / 5
        log.success(f"Connected. 5 pings latency: {fmtseconds(avg)}")

        return redis

    async def ratelimited(self, resource_ident: str, request_limit: int, timespan: int = 60, increment=1) -> bool:
        key = f"rl:{resource_ident}"
        try:
            current_usage = await self.evalsha(INCREMENT_SCRIPT_HASH, 1, key, timespan, increment)
        except NoScriptError:
            current_usage = await self.eval(INCREMENT_SCRIPT, 1, key, timespan, increment)
        return bool(int(current_usage) > request_limit)

    def get_lock(
        self,
        name: str,
        timeout: float = 60.0,
        sleep: float = 0.3,
        blocking: bool = True,
        blocking_timeout: float = None,
    ) -> RivalLock:
        name = f"mel_lock:{name}"
        return RivalLock(
            self,
            name,
            timeout=timeout,
            sleep=sleep,
            blocking=blocking,
            blocking_timeout=blocking_timeout,
        )
