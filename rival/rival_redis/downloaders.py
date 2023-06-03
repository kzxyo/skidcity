from typing import Optional

import httpx
from xxhash import xxh3_64_hexdigest

from .redis import blocking_redis

USER_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"}


def make_download_key(url):
    return f"url_download:{xxh3_64_hexdigest(url)}"


sync_redis = blocking_redis  # cos idk which name i like better


def blocking_download_cached(url) -> Optional[bytes]:
    key = make_download_key(url)
    with blocking_redis() as redis:
        data = redis.get(key)
        if not data:
            with httpx.Client(http2=2, headers=USER_HEADERS, follow_redirects=True) as hx:
                r = hx.get(url)
                r.raise_for_status()
                data = r.content
                redis.set(key, data, ex=604800)

    return data


async def download_cached(url: str, session_x: httpx.AsyncClient) -> Optional[bytes]:
    from rival import get_redis

    _redis = get_redis()
    key = make_download_key(url)
    data = await _redis.get(key)
    if not data:
        r = await session_x.get(url, headers=USER_HEADERS, follow_redirects=True)
        r.raise_for_status()
        data = r.content
        await _redis.set(key, data, ex=604800)

    return data
