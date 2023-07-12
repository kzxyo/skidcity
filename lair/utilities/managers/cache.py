import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List
from redis.asyncio import StrictRedis as AsyncStrictRedis
from redis.asyncio.connection import BlockingConnectionPool
from redis.backoff import EqualJitterBackoff
from redis.retry import Retry


log = logging.getLogger(__name__)

class Cache:
    def __init__(self, bot):
        self.bot = bot
        self.cache: Dict[Any, Any] = {}
        self.expiry: Dict[Any, Any] = {}
        self.ratelimit: Dict[Any, Any] = {}
        self.loop = asyncio.get_event_loop()
        self.cached = False
        self.avatars = {}
        self.fakeperms = {}

    async def get(self, key: Any):
        if await self._check_ratelimit(key):
            raise Exception(f"Cache ratelimit exceeded for key: {key}")
        if key in self.cache:
            if self.expiry.get(key) is None or self.expiry.get(key) > datetime.now():
                return self.cache[key]
            else:
                await self.delete(key)
        return None

    async def set(self, key: Any, value: Any, expiry=None, append=False):
        if await self._check_ratelimit(key):
            raise Exception(f"Cache ratelimit exceeded for key: {key}")
        if key in self.cache and append:
            cache_val = self.cache[key]
            if isinstance(cache_val, (list, dict, set)):
                if isinstance(cache_val, list):
                    cache_val.append(value)
                elif isinstance(cache_val, dict):
                    if key in cache_val:
                        if isinstance(cache_val[key], list):
                            cache_val[key].append(value)
                        else:
                            cache_val[key] = [cache_val[key], value]
                    else:
                        cache_val[key] = value
                elif isinstance(cache_val, set):
                    cache_val.add(value)
            else:
                self.cache[key] = [cache_val, value]
        else:
            self.cache[key] = value

        if expiry:
            self.expiry[key] = expiry + datetime.now()
            self.loop.create_task(self._schedule_expiry(key, expiry))

    async def delete(self, key: Any):
        if key in self.cache:
            del self.cache[key]
            if key in self.expiry:
                del self.expiry[key]
                

    @property
    def keys(self) -> List[Any]:
        return self.cache.keys()

    async def _schedule_expiry(self, key: str, expiry: timedelta):
        await asyncio.sleep(expiry.total_seconds())
        await self.delete(key)
        log.info(f'Cache: expired key {key}')

    async def _check_ratelimit(self, key: str) -> bool:
        current_time: datetime = datetime.now()
        limit: int = 100
        interval: timedelta = timedelta(seconds=10)
        
        if key not in self.ratelimit:
            self.ratelimit[key] = {'requests': 1, 'start_time': current_time}
            return False
        
        limit_info: dict = self.ratelimit[key]
        if current_time - limit_info['start_time'] >= interval:
            limit_info['requests'] = 1
            limit_info['start_time'] = current_time
        else:
            limit_info['requests'] += 1
        
        return limit_info['requests'] > limit
                
    async def cache_prefixes(self) -> None:
        prefixes = await self.bot.db.fetch(
                """
                SELECT prefix, guild_id FROM guildprefix
                """
        )
        for prefix, guild_id in prefixes:
            await self.set(f"prefix:{guild_id}", prefix)

    async def _init(self) -> None:
        log.info('Initializing cache')
        await self.cache_prefixes()
        self.cached = True
    
    def __repr__(self) -> str:
        items = len(self.cache)
        return f"<Cache items={items} status={self.cached}>"

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