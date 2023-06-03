
from discord.ext import commands
from math import log, floor
import discord, time, datetime, aiohttp, random, os, orjson
from typing import Union, Optional

class HTTP:
    def __init__(self, headers: Optional[dict] = None, proxy: bool = False) -> None:
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        }
        self.get = self.json
        if proxy:self.proxy = lambda: random.choice(os.environ.get("PROXIES", "").split("||"))
        else:self.proxy = lambda: None
               
    async def post_json(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> dict:
        """Send a POST request and get the JSON response"""
        
        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session:
            async with session.post(url, data=data, params=params, proxy=self.proxy(), ssl=ssl) as response:
                return await response.json()


    async def post_text(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> str:
        """Send a POST request and get the HTML response"""
        
        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session:
            async with session.post(url, data=data, params=params, proxy=self.proxy(), ssl=ssl) as response:
                res = await response.text()


    async def async_post_bytes(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> bytes:
        """Send a POST request and get the response in bytes"""
        
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
        """Send a GET request and get the HTML response"""
        
        data = await self._dl(url, headers, params, proxy, ssl)
        if data: return data.decode("utf-8")   
        return data

    async def json(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> dict:
        """Send a GET request and get the JSON response"""
        
        data = await self._dl(url, headers, params, proxy, ssl)
        if data: return orjson.loads(data)
        return data

    async def read(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> bytes:
        """Send a GET request and get the response in bytes"""
        return await self._dl(url, headers, params, proxy, ssl)

class Client(object): 
  def __init__(self, bot: commands.AutoShardedBot): 
    self.bot = bot 
  
  async def send_success(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message or None: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.user.mention}: {message}"), ephemeral=ephemeral)
  async def send_error(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message or None: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.user.mention}: {message}"), ephemeral=ephemeral)
  async def send_warning(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message or None: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.user.mention}: {message}"), ephemeral=ephemeral)
  
  async def link_to_message(self, link: str) -> discord.Message or None: 
   link = link.replace("https://discord.com/channels/", "")
   link = link.split("/")
   return await self.bot.get_guild(int(link[0])).get_channel(int(link[1])).fetch_message(int(link[2]))   

  def human_format(self, number) -> str:
    units = ['', 'K', 'M', 'G', 'T', 'P']
    if number < 1000:
      return number

    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])
  
  def relative_time(self, date):
    """Take a datetime and return its "age" as a string.
    The age can be in second, minute, hour, day, month or year. Only the
    biggest unit is considered, e.g. if it's 2 days and 3 hours, "2 days" will
    be returned.
    Make sure date is not in the future, or else it won't work.
    """

    def formatn(n, s):
        """Add "s" if it's plural"""

        if n == 1:
            return "1 %s" % s
        elif n > 1:
            return "%d %ss" % (n, s)

    def qnr(a, b):
        """Return quotient and remaining"""

        return a / b, a % b

    class FormatDelta:

        def __init__(self, dt):
            now = datetime.datetime.now()
            delta = now - dt
            self.day = delta.days
            self.second = delta.seconds
            self.year, self.day = qnr(self.day, 365)
            self.month, self.day = qnr(self.day, 30)
            self.hour, self.second = qnr(self.second, 3600)
            self.minute, self.second = qnr(self.second, 60)

        def format(self):
            for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                n = getattr(self, period)
                if n >= 1:
                    return '{0} ago'.format(formatn(n, period))
            return "just now"

    return FormatDelta(date).format()
    
  @property 
  def uptime(self) -> str:
    uptime = int(time.time() - self.bot.uptime)
    seconds_to_minute   = 60
    seconds_to_hour     = 60 * seconds_to_minute
    seconds_to_day      = 24 * seconds_to_hour

    days    =   uptime // seconds_to_day
    uptime    %=  seconds_to_day

    hours   =   uptime // seconds_to_hour
    uptime    %=  seconds_to_hour

    minutes =   uptime // seconds_to_minute
    uptime    %=  seconds_to_minute

    seconds = uptime
    if days > 0: return ("{} days, {} hours, {} minutes, {} seconds".format(days, hours, minutes, seconds))
    if hours > 0 and days == 0: return ("{} hours, {} minutes, {} seconds".format(hours, minutes, seconds))
    if minutes > 0 and hours == 0 and days == 0: return ("{} minutes, {} seconds".format(minutes, seconds))
    if minutes == 0 and hours == 0 and days == 0: return ("{} seconds".format(seconds))  