import asyncio, contextlib, time
from datetime import timedelta
from hashlib import sha1
from typing import Dict, Optional, Union

import humanize, orjson, tuuid
from async_timeout import timeout as Timeout
from loguru import logger as log
from xxhash import xxh3_64_hexdigest

from redis.asyncio import Redis
from redis.asyncio.connection import BlockingConnectionPool
from redis.asyncio.lock import Lock
from redis.backoff import EqualJitterBackoff
from redis.exceptions import LockError, NoScriptError
from redis.retry import Retry

REDIS_URL = "redis://localhost"


def fmtseconds(seconds: Union[int, float], unit="microseconds") -> str:
    """String representation of the amount of time passed.

    Args:
        seconds (Union[int, float]): seconds from ts
        minimum_unit: str

    """

    return humanize.naturaldelta(timedelta(seconds=seconds), minimum_unit=unit)


class ORJSONDecoder:
    def __init__(self, **kwargs):
        # eventually take into consideration when deserializing
        self.options = kwargs

    def decode(self, obj):
        return orjson.loads(obj)


class ORJSONEncoder:
    def __init__(self, **kwargs):
        # eventually take into consideration when serializing
        self.options = kwargs

    def encode(self, obj):
        # decode back to str, as orjson returns bytes
        return orjson.dumps(obj).decode("utf-8")


INCREMENT_SCRIPT = b"""
    local current
    current = tonumber(redis.call("incrby", KEYS[1], ARGV[2]))
    if current == tonumber(ARGV[2]) then
        redis.call("expire", KEYS[1], ARGV[1])
    end
    return current
"""

INCREMENT_SCRIPT_HASH = sha1(INCREMENT_SCRIPT).hexdigest()


class RivalLock(Lock):
    def __init__(
        self,
        redis: Redis,
        name: Union[str, bytes, memoryview],
        max_lock_ttl: float = 30.0,
        extension_time: float = 0.5,
        sleep: float = 0.2,
        blocking: bool = True,
        blocking_timeout: float = None,
        thread_local: bool = False,
    ) -> None:
        self.extension_time = extension_time
        self.extend_task: Optional[asyncio.Task] = None
        self._held = False

        super().__init__(redis, name, max_lock_ttl, sleep, blocking, blocking_timeout, thread_local)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} <Held in CtxManager: {self._held!r}>"

    async def extending_task(self):
        while True:
            await asyncio.sleep(self.extension_time)
            await self.reacquire()

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.extend_task:
            self.extend_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.extend_task
            self.extend_task = None

        await self.release()
        self._held = False

    async def __aenter__(self):
        if await self.acquire():
            self._held = True
            if self.extension_time:
                self.extend_task = asyncio.create_task(self.extending_task())
            return self
        raise LockError("Unable to acquire lock within the time specified")


class RivalRedis(Redis):
    def __init__(self, *a, **ka):
        self._locks_created: Dict[Union[str, bytes, memoryview], RivalLock] = {}
        self._namespace = tuuid.tuuid()
        self.rl_prefix = "rl:"
        self.is_ratelimited = self.ratelimited

        super().__init__(*a, **ka)

    def json(self):
        return super().json(ORJSONEncoder(), ORJSONDecoder())

    @property
    def held_locks(self):
        return [{name: lock} for name, lock in self._locks_created.items() if lock.locked()]

    @property
    def locks(self):
        return self._locks_created

    def __repr__(self):
        return f"{self.__class__.__name__} {self._namespace} <{self.connection_pool!r}>"

    async def jsonset(self, key, data: dict, **ka):
        return await self._json.set(key, ".", data, **ka)

    async def jsonget(self, key):
        return await self._json.get(key)

    async def getstr(self, key):
        return (await self.get(key)).decode("UTF-8")

    @classmethod
    async def from_url(cls, url=REDIS_URL, retry="jitter", attempts=100, timeout=120, **ka):
        retry_form = Retry(backoff=EqualJitterBackoff(3, 1), retries=attempts)
        cls = cls(connection_pool=BlockingConnectionPool.from_url(url, timeout=timeout, max_connections=7000, retry=retry_form, **ka))
        log.warning(f"New Redis! {url}: timeout: {timeout} retry: {retry} attempts: {attempts} ")

        ping_time = 0
        async with Timeout(9):
            for _ in range(5):
                start = time.time()
                await cls.ping()
                ping_time += time.time() - start
        avg = ping_time / 5

        log.success(f"Connected. 5 pings latency: {fmtseconds(avg)}")
        return cls

    def rl_key(self, ident) -> str:
        return f"{self.rl_prefix}{xxh3_64_hexdigest(ident)}"

    async def ratelimited(self, resource_ident: str, request_limit: int, timespan: int = 60, increment=1) -> bool:
        rlkey = f"{self.rl_prefix}{xxh3_64_hexdigest(resource_ident)}"
        try:
            current_usage = await self.evalsha(INCREMENT_SCRIPT_HASH, 1, rlkey, timespan, increment)
        except NoScriptError:
            current_usage = await self.eval(INCREMENT_SCRIPT, 1, rlkey, timespan, increment)
        if int(current_usage) > request_limit:
            return True
        return False

    def get_lock(self, name: Union[str, bytes, memoryview] = None, timeout: float = None, *a, **ka) -> RivalLock:
        name = f"lock:{xxh3_64_hexdigest(name)}"
        if name:
            if lock := self._locks_created.get(name):
                return lock
        else:
            name = f"{xxh3_64_hexdigest(tuuid.tuuid())}_l"
        self._locks_created[name] = RivalLock(redis=self, name=name, blocking_timeout=timeout, *a, **ka)
        self._locks_created[name]._namespace = self._namespace
        return self._locks_created[name]