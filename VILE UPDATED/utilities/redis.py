import asyncio, contextlib, time, humanize, orjson, tuuid
from typing_extensions import Self
from datetime import timedelta
from typing import Dict, Optional, Union, Any
from hashlib import sha1
from async_timeout import timeout as Timeout
from redis.asyncio import Redis
from redis.asyncio.connection import BlockingConnectionPool
from redis.asyncio.lock import Lock
from redis.backoff import EqualJitterBackoff
from redis.exceptions import LockError, NoScriptError
from redis.retry import Retry
from redis.commands.json import JSON


def fmtseconds(seconds: Union[int, float], unit='microseconds') -> str:
    return humanize.naturaldelta(timedelta(seconds=seconds), minimum_unit=unit)


class ORJSONDecoder:
    def __init__(self, **kwargs) -> None:
        self.options = kwargs

    def decode(self, obj) -> dict:
        return orjson.loads(obj)


class ORJSONEncoder:
    def __init__(self, **kwargs):
        self.options = kwargs
    
    def encode(self, obj):
        return orjson.dumps(obj).decode('utf-8')


INCREMENT_SCRIPT = b'''
    local current
    current = tonumber(redis.call('incrby', KEYS[1], ARGV[2]))
    if current == tonumber(ARGV[2]) then
        redis.call('expire', KEYS[1], ARGV[1])
    end
    return current
'''
INCREMENT_SCRIPT_HASH = sha1(INCREMENT_SCRIPT).hexdigest()


class VileLock(Lock):
    def __init__(
        self,
        redis: Redis,
        name: Union[str, bytes, memoryview],
        max_lock_ttl: float = 30.0,
        extension_time: float = 0.5,
        sleep: float = 0.2,
        blocking: bool = True,
        blocking_timeout: float = None,
        thread_local: bool = False
    ) -> None:
        super().__init__(redis, name, max_lock_ttl, sleep, blocking, blocking_timeout, thread_local)
        self.extension_time = extension_time
        self.extend_task: Optional[asyncio.Task] = None
        self._held = False


    def __repr__(self) -> str:
        return f'{self.__class__.__name__} <Held in CtxManager: {self._held!r}>'


    async def extending_task(self) -> None:
        while True:
            await asyncio.sleep(self.extension_time)
            await self.reacquire()


    async def __aexit__(self, *_: Any) -> None:
        if self.extend_task:
            self.extend_task.cancel()
            with contextlib.supress(asyncio.CancelledError):
                await self.extend_task
            self.extend_task = None

        await self.release()
        self._held = False


    async def __aenter__(self) -> Optional[Self]:
        if await self.acquire():
            self._held = True
            if self.extension_time:
                self.extend_task = asyncio.create_task(self.extending_task())

            return self

        raise LockError('Unable to acquire lock within the time specificed')


class VileRedis(Redis):
    def __init__(self, *a, **ka) -> None:
        super().__init__(*a, **ka)
        self._locks_created: Dict[Union[str, bytes, memoryview], VileLock] = {}
        self._namespace = tuuid.tuuid()
        self.rl_prefix = 'rl:'


    def json(self) -> JSON:
        return super().json(ORJSONEncoder(), ORJSONDecoder())


    @property
    def held_locks(self) -> list:
        return [{name: lock} for name, lock in self._locks_created.items() if lock.locked()]


    @property
    def locks(self) -> dict:
        return self._locks_created


    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self._namespace} <{self.connection_pool!r}>>'


    async def jsonset(self, key: Any, data: dict, **ka) -> Any:
        return await self.json().set(key, '.', data, **ka)


    async def jsonget(self, key: Any) -> Any:
        return await self.json().get(key)


    async def jsondelete(self, key: Any) -> Any:
        return await self.json.delete(key)


    async def get(self, key: Any) -> Any:
        return await super().get(key)


    @classmethod
    async def from_url(cls) -> Self:
        return await cls(
            host='localhost', 
            port=6379,
            decode_responses=True, 
            #connection_pool=BlockingConnectionPool(
                #timeout=120, 
                #max_connections=7000, 
                #retry=Retry(
                    #backoff=EqualJitterBackoff(3, 1), 
                    #retries=100
                #)
            #)
        )
