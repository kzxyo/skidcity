from typing import Optional
import aiohttp, humanize, orjson, random, os
from io import BytesIO

class Session:
  def __init__(self, headers: Optional[dict] = None, proxy: bool = False) -> None:
   
   self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
   self.get = self.json
   
   if proxy:self.proxy = lambda: random.choice(os.environ.get("PROXIES", "").split("||"))
   else:self.proxy = lambda: None
  
  async def post_json(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None, proxy: Optional[str]=None):

    async with aiohttp.ClientSession(headers=headers or self.headers) as cs: 
     async with cs.post(url, headers=headers, params=params, proxy=proxy) as r: 
       return await r.json()
     
  async def post_text(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> str:

        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session:
            async with session.post(url, data=data, params=params, proxy=self.proxy(), ssl=ssl) as response:
                return await response.text()
              
  async def async_post_bytes(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> bytes:

        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session: 
            async with session.post(url, data=data, params=params, proxy=self.proxy(), ssl=ssl) as response:
                return await response.read()
              
  async def _dl(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> bytes:
        
        total_size = 0
        data = b""

        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session:
            async with session.get(url, params=params, proxy=self.proxy(), ssl=ssl) as response:
                while True:
                    chunk = await response.content.read(4*1024)
                    data += chunk
                    total_size += len(chunk)
                    if not chunk: break
                    if total_size > 500_000_000: return None
                return data
              
  async def text(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> str:

        data = await self._dl(url, headers, params, proxy, ssl)
        if data: return data.decode("utf-8")   
        return data

  async def json(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> dict:
        
        data = await self._dl(url, headers, params, proxy, ssl)
        if data: return orjson.loads(data)
        return data

  async def read(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> bytes:
    
        return await self._dl(url, headers, params, proxy, ssl)
  
  async def get_json(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None, proxy: Optional[str]=None):
    
   async with aiohttp.ClientSession(headers=headers or self.headers) as cs: 
     async with cs.get(url, headers=headers, params=params, proxy=proxy) as r: 
       return await r.json()

  async def get_text(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None, proxy: Optional[str]=None): 

   async with aiohttp.ClientSession(headers=headers or self.headers) as cs: 
     async with cs.get(url, headers=headers, params=params, proxy=proxy) as r: 
       return await r.text()

  async def get_bytes(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None, proxy: Optional[str]=None):
    
    async with aiohttp.ClientSession(headers=headers or self.headers) as cs: 
      async with cs.get(url, headers=headers, params=params, proxy=proxy) as r: 
       return await r.read()  
      
  def human_format(self, number: int) -> str:
        if number > 999:
            return humanize.naturalsize(number, False, True)

        return number.__str__()
    
  async def getbyte(self, url: str) -> BytesIO:
      return BytesIO(await self.get_bytes(url))