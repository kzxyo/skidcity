import aiohttp, orjson
from . import config
from typing import Optional
PROXY = config.proxy.webshare


async def async_post_json(url, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> dict:
    async with aiohttp.ClientSession(headers=headers, json_serialize=orjson.dumps) as session:
        async with session.post(url, data=data, params=params, proxy=(PROXY if proxy else None), ssl=ssl) as response:
            return await response.json()


async def async_post_text(url, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> str:
    async with aiohttp.ClientSession(headers=headers, json_serialize=orjson.dumps) as session:
        async with session.post(url, data=data, params=params, proxy=(PROXY if proxy else None), ssl=ssl) as response:
            res = await response.text()


async def async_post_bytes(url, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None)-> bytes:
    async with aiohttp.ClientSession(headers=headers, json_serialize=orjson.dumps) as session: 
        async with session.post(url, data=data, params=params, proxy=(PROXY if proxy else None), ssl=ssl) as response:
            return await response.read()


async def async_dl(url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> bytes:

    total_size = 0
    data = b''

    async with aiohttp.ClientSession(headers=headers, json_serialize=orjson.dumps) as session:
        async with session.get(url, params=params, proxy=(PROXY if proxy else None), ssl=ssl) as response:
            while True:
                chunk = await response.content.read(4*1024)
                data += chunk
                total_size += len(chunk)

                if not chunk:
                    break

                if total_size > 500_000_000:
                    return None

    return data


async def async_text(url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> str:
    data = await async_dl(url, headers, params, proxy, ssl)
    
    if data:
        return data.decode('utf-8')
    return data


async def async_json(url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> dict:
    data = await async_dl(url, headers, params, proxy, ssl)
    
    if data:
        return orjson.loads(data)

    return data


async def async_read(url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> bytes:
    return await async_dl(url, headers, params, proxy, ssl)


get = async_json
text = async_text
read = async_read
post = async_post_json
