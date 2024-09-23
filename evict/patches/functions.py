import random, string, asyncio, imagehash as ih, discord, aiohttp, json
from io import BytesIO
from math import sqrt
from PIL import Image
from functools import partial, wraps
from xxhash import xxh64_hexdigest
from redis.asyncio import StrictRedis as AsyncStrictRedis
from redis.asyncio.connection import BlockingConnectionPool
from redis.backoff import EqualJitterBackoff
from redis.retry import Retry

class Redis(AsyncStrictRedis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock: asyncio.Lock = asyncio.Lock()

    def __repr__(self):
        return f"<helpers.patches.Redis lock={self._lock}>"

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

def hash(text: str):
    return xxh64_hexdigest(str(text))

def unique_id(lenght: int = 6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=lenght))

def async_executor():
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            task = partial(func, *args, **kwargs)
            return asyncio.get_event_loop().run_in_executor(None, task)

        return inner

    return outer

@async_executor()
def _collage_open(image: BytesIO):
    image = (
        Image.open(image)
        .convert("RGBA")
        .resize(
            (
                256,
                256,
            )
        )
    )
    return image


async def _collage_read(image: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image) as response:
            try:
                return await _collage_open(BytesIO(await response.read()))
            except:
                return None


async def _collage_paste(image: Image, x: int, y: int, background: Image):
    background.paste(
        image,
        (
            x * 256,
            y * 256,
        ),
    )


async def collage(images: list[str]):
    tasks = list()
    for image in images:
        tasks.append(_collage_read(image))

    images = [image for image in await asyncio.gather(*tasks) if image]
    if not images:
        return None

    rows = int(sqrt(len(images)))
    columns = (len(images) + rows - 1) // rows

    background = Image.new(
        "RGBA",
        (
            columns * 256,
            rows * 256,
        ),
    )
    tasks = list()
    for i, image in enumerate(images):
        tasks.append(_collage_paste(image, i % columns, i // columns, background))
    await asyncio.gather(*tasks)

    buffer = BytesIO()
    background.save(
        buffer,
        format="png",
    )
    buffer.seek(0)

    background.close()
    for image in images:
        image.close()

    return discord.File(
        buffer,
        filename="collage.png",
    )

@async_executor()
def image_hash(image: BytesIO):
    if isinstance(image, bytes):
        image = BytesIO(image)

    result = str(ih.average_hash(image=Image.open(image), hash_size=8))
    if result == "0000000000000000":
        return unique_id(16)
    else:
        return result
    
class plural:
    def __init__(self, value: int, bold: bool = False, code: bool = False):
        self.value: int = value
        self.bold: bool = bold
        self.code: bool = code

    def __format__(self, format_spec: str) -> str:
        v = self.value
        if isinstance(v, list):
            v = len(v)
        if self.bold:
            value = f"**{v:,}**"
        elif self.code:
            value = f"`{v:,}`"
        else:
            value = f"{v:,}"

        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"

        if abs(v) != 1:
            return f"{value} {plural}"

        return f"{value} {singular}"
    
class plural:
    def __init__(self, value: int, bold: bool = False, code: bool = False):
        self.value: int = value
        self.bold: bool = bold
        self.code: bool = code

    def __format__(self, format_spec: str) -> str:
        v = self.value
        if isinstance(v, list):
            v = len(v)
        if self.bold:
            value = f"**{v:,}**"
        elif self.code:
            value = f"`{v:,}`"
        else:
            value = f"{v:,}"

        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"

        if abs(v) != 1:
            return f"{value} {plural}"

        return f"{value} {singular}"