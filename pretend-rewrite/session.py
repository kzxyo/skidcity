import aiohttp 
from typing import Optional

class Http: 
 def __init__(self, headers: Optional[dict]=None): 
  self.headers = headers or {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }   

 async def get(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None): 
  """Make a get request and get the json""" 
  async with aiohttp.ClientSession(headers=headers or self.headers) as cs: 
   async with cs.get(url, params=params) as r: 
    return await r.json()

 async def get_text(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None):
   """Make a get request and get the text"""
   async with aiohttp.ClientSession(headers=headers or self.headers) as cs: 
    async with cs.get(url, params=params) as r: 
     return await r.text()  

 async def get_bytes(self, url: str, headers: Optional[dict]=None, params: Optional[dict]=None):
   """Make a get request and get the bytes object"""
   async with aiohttp.ClientSession(headers=headers or self.headers) as cs: 
    async with cs.get(url, params=params) as r: 
     return await r.read()  

# idk what yall need here       