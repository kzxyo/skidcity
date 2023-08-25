import os, orjson, socket, time, pyppeteer, pytz, textract, chardet, xxhash, hashlib, logging, humanize, difflib, random, tuuid, asyncio, traceback, colorgram, yarl, aiomysql, subprocess, discord, sys, aiofiles, arrow, inspect, re, emcache, aiohttp, unicodedata
from typing import Optional, Union, Literal, Iterable, Iterator, Any, Awaitable, Callable, Type, Dict, Tuple, List, IO, Match
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta
from discord.ext import commands
from PIL import Image
from shazamio import Shazam
from io import BytesIO, StringIO
from durations_nlp import Duration
from pathlib import Path
from typing_extensions import Self
from async_timeout import timeout as Timeout
from cryptography.fernet import Fernet
from redis.asyncio import Redis
logger = logging.getLogger(__name__)
from . import constants, regex, cache as cacheclasses
from .views import Confirm
from .paginator import Paginator
fernet = Fernet(os.environ.get("FERNET_KEY", ""))


TUPLE = ()
DICT = {}


class HelpCommand(commands.HelpCommand):
    def extra_params(self, command: Any) -> str:
        params = command.parameters
        ret = []
        if not params:
            return "None"
            
        for param, config in params.items():
            aliases = f"[{'|'.join(config['aliases'])}]" if config["aliases"] else ""
            ret.append(f"{param}{aliases} - {config.get('description', 'None')}")
                
        lines = "\n".join(ret)
        return f"```\n{lines}```"
        
        
    async def send_bot_help(self, mapping: Any) -> discord.Message:
        """Send the default command menu"""
        
        ctx = self.context
        cogs = tuple(
            cog for cog in ctx.bot.cogs.values()
            if cog.get_commands() and getattr(cog, "hidden", False) is False
            and cog.qualified_name not in ("Jishaku")
        )
        cog_count = len(cogs)
        embeds = []
        
        embeds.append(
            discord.Embed(color=ctx.bot.color)
            .set_author(name="Vile Command Menu", icon_url=ctx.bot.user.display_avatar)
            .set_thumbnail(url=ctx.bot.user.display_avatar)
            .add_field(
                name=f"{ctx.bot.dash} **Need to Know**",
                value=f"{ctx.bot.reply} [] = optional, <> = required\n{ctx.bot.reply} Important commands have slash versions",
            )
            .add_field(
                name=f"{ctx.bot.dash} **Links**",
                value=f"{ctx.bot.reply} [**Invite**]({ctx.bot.invite})   \u2022    [**Support**](https://discord.gg/KsfkG3BZ4h)   \u2022   [**Docs**](https://github.com/treyt3n/vile)",
                inline=False,
            )
            .set_footer(text=f"Page 1 / {cog_count+1} ({sum(1 for _ in ctx.bot.walk_commands())} commands)")
        )
        for index, cog in enumerate(cogs, start=2):
            embeds.append(
                discord.Embed(
                    color=ctx.bot.color,
                    title=f"Category: {cog.qualified_name}",
                    description=f"```\n{', '.join(tuple(cmd.name + ('*' if isinstance(cmd, commands.Group) else '') for cmd in cog.get_commands() if 'help' not in cmd.name))}\n\n```",
                )
                .set_author(
                    name="Vile Command Menu", 
                    icon_url=ctx.bot.user.display_avatar
                )
                .set_footer(text=f"Page {index} / {cog_count+1}  ({len(tuple(cmd for cmd in cog.walk_commands() if 'help' not in cmd.name))} commands)")
            )
        
        return await ctx.paginate(embeds)
        

    async def send_command_help(self, command: commands.Command) -> discord.Message:
        """Send the help menu for a command"""
        
        if not await self.context.bot.is_owner(self.context.author):
            if command.cog_name == "Jishaku" or getattr(command.cog, "hidden", False) is True:
                return await self.context.send(f"No command called \"{command.qualified_name}\" found.")
            
        ctx = self.context
        embed = (
            discord.Embed(
                color=ctx.bot.color, 
                title=f"Command: {command.qualified_name}",
                description=f"> {command.callback.__doc__}" if command.callback.__doc__ else None
            )
            .set_author(
                name="Vile Help Menu", 
                icon_url=ctx.bot.user.display_avatar
            )
            .add_field(
                name="<:v_slash:1067034025895665745> Parameters",
                value=", ".join(command.clean_params.keys()) or "None"
            )
            .add_field(
                name="<:v_checklist:1067033997386981408> Permissions",
                value=command.extras.get("permissions", command.permissions.replace("_", " ").title())
            )
            .add_field(
                name="<:v_plus:1112130842513383514> Extra Parameters",
                value=self.extra_params(command),
                inline=False
            )
            .add_field(
                name=f"{ctx.bot.dash} Usage",
                value=f"```\nSyntax: {ctx.prefix}{command.qualified_name} {command.usage or ''}\nExample: {ctx.prefix}{command.qualified_name} {command.example or ''}\n```",
                inline=False
            )
            .set_footer(text=f"Module: {command.cog_name}   \u2022   Aliases: {', '.join(command.aliases) or None}")
        )
        
        return await ctx.reply(embed=embed)


    async def send_group_help(self, group: commands.Group) -> discord.Message:
        """Send the help menu for a group command"""
        
        if group.cog_name == "Jishaku" or getattr(group.cog, "hidden", False) is True:
            return await self.context.send(f"No command called \"{group.qualified_name}\" found.")
        
        ctx = self.context
        _commands = list(group.walk_commands())
        embeds = []
        
        embeds.append(
            discord.Embed(
                color=ctx.bot.color, 
                title=f"Group Command: {group.qualified_name}",
                description=f"> {group.callback.__doc__}" if group.callback.__doc__ else None
            )
            .set_author(
                name="Vile Help Menu", 
                icon_url=ctx.bot.user.display_avatar
            )
            .add_field(
                name="<:v_slash:1067034025895665745> Parameters",
                value=", ".join(group.clean_params.keys()) or "None"
            )
            .add_field(
                name="<:v_checklist:1067033997386981408> Permissions",
                value=group.extras.get("permissions", group.permissions.replace("_", " ").title())
            )
            .add_field(
                name="<:v_plus:1112130842513383514> Extra Parameters",
                value=self.extra_params(group),
                inline=False
            )
            .add_field(
                name=f"{ctx.bot.dash} Usage",
                value=f"```\nSyntax: {ctx.prefix}{group.qualified_name} {group.usage or ''}\nExample: {ctx.prefix}{group.qualified_name} {group.example or ''}\n```",
                inline=False
            )
            .set_footer(text=f"Page 1 / {len(_commands)+1}   \u2022   Module: {group.cog_name}   \u2022   Aliases: {', '.join(group.aliases) or None}")
        )
        
        for index, command in enumerate(_commands, start=2):
            embeds.append(
                discord.Embed(
                    color=ctx.bot.color, 
                    title=f"{'Group ' if isinstance(command, commands.Group) else ''}Command: {command.qualified_name}",
                    description=f"> {command.callback.__doc__}" if command.callback.__doc__ else None
                )
                .set_author(
                    name="Vile Help Menu", 
                    icon_url=ctx.bot.user.display_avatar
                )
                .add_field(
                    name="<:v_slash:1067034025895665745> Parameters",
                    value=", ".join(command.clean_params.keys()) or "None"
                )
                .add_field(
                    name="<:v_checklist:1067033997386981408> Permissions",
                    value=command.extras.get("permissions", command.permissions.replace("_", " ").title())
                )
                .add_field(
                    name="<:v_plus:1112130842513383514> Extra Parameters",
                    value=self.extra_params(command),
                    inline=False
                )
                .add_field(
                    name=f"{ctx.bot.dash} Usage",
                    value=f"```\nSyntax: {ctx.prefix}{command.qualified_name} {command.usage or ''}\nExample: {ctx.prefix}{command.qualified_name} {command.example or ''}\n```",
                    inline=False
                )
                .set_footer(text=f"Page {index} / {len(_commands)+1}   \u2022   Module: {command.cog_name}   \u2022   Aliases: {', '.join(command.aliases) or None}")
            )
            
        return await ctx.paginate(embeds)
        

    async def on_help_command_error(self, ctx: "Context", error: Any) -> None:
        raise Exception(traceback.format_exc())


def ordinal(number: int) -> str:
    """Format a number"""
    return "%d%s" % (number, "tsnrhtdd"[(number // 10 % 10 != 1) * (number % 10 < 4) * number % 10 :: 4])
    
    
def fmtseconds(seconds: Union[int, float], unit: str = "microseconds") -> str:
    """Format time using seconds"""
    return humanize.naturaldelta(timedelta(seconds=seconds), minimum_unit=unit)


def source(obj: object) -> str:
    """Get the source code of an object"""
    return inspect.getsource(obj)
    
    
def encrypt(key: Any) -> str:
    """Encrypt an object using Fernet"""
    return fernet.encrypt(str(key).encode()).decode()
    

def decrypt(key: Any) -> str:
    """Decrypt an object using Fernet"""
    return fernet.decrypt(str(key).encode()).decode()
    
    
def hash(key: Union[str, bytes, memoryview]) -> str:
    """Hash text or bytes using xxhash"""
    return xxhash.xxh3_64_hexdigest(key)
    
    
class ParameterParser:
    def __init__(self, context: "Context", parameters: dict) -> None:
        self.context = context
        self.parameters = parameters
        
        
    def get_args(self, text: str, args: list, pattern: re.Pattern) -> dict:
        """Get the parameter values"""
        
        ret = {arg: "" for arg in args}
        ret.update({k: v for k, v in pattern.findall(text)})
        return ret
        
    
    def get_params_and_aliases(self, d: dict) -> list:
        ret = []
        for parameter, config in d.items():
            ret.append(parameter)
            if config.get("aliases"):
                for alias in config.get("aliases"):
                    ret.append(alias)
        
        return ret
        
        
    async def parse(self) -> None:
        """Parse the paramaters"""
        
        ret = {parameter: None for parameter in self.parameters}
        all_params = self.get_params_and_aliases(self.parameters)
        parsed = self.get_args(
            self.context.message.content, 
            all_params,
            regex.parameter_parser(all_params)
        )

        for parameter, config in self.parameters.items():
            
            if config.get("require_value", True) is False:
                for p in (parameter, *config.get("aliases", TUPLE)):
                    if f"-{p}" in set(self.context.message.content.split()):
                        ret[parameter] = True
                        break
                    
            else:
                converter = config.get("converter", str)
                for p in (parameter, *config.get("aliases", TUPLE)):
                    if parsed.get(p):
                        if isinstance(parsed.get(p), int) and config.get("minimum") and config.get("maximum"):
                            if not parsed.get(p) >= config.get("minimum") <= config.get("maximum"):
                                await self.context.error(f"Value for parameter **{parameter}** does not comply with the size limits")
                                raise Exception(f"Value for parameter **{parameter}** does not comply with the size limits")
                        
                        try:
                            if isinstance(converter, commands.Converter):
                                ret[parameter] = await converter().convert(self.context, parsed.get(p).strip())
                                break
                                 
                            if converter == str:
                                ret[parameter] = converter(parsed.get(p))
                                break
                                
                            if converter == int:
                                ret[parameter] = converter(parsed.get(p).strip())
                                break

                        except Exception:
                            await self.context.error(f"Failed to convert value for parameter **{parameter}**")
                            raise Exception(f"Failed to convert value for parameter **{parameter}**")
                        
        return ret


class Browser:
    def __init__(
        self, 
        executable_path: str, 
        args: list,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        self.executable_path = executable_path
        self.args = args
        self._browser = None
        self.username = username
        self.password = password


    def __repr__(self) -> str:
        return f"<Browser closed={self.closed}>"


    @property
    def browser(self) -> Optional[pyppeteer.browser.Browser]:
        return self._browser


    @property
    def closed(self) -> bool:
        return not self._browser._connection._connected


    async def __aenter__(self) -> Self:
        self._browser = await pyppeteer.launch({
            "executablePath": self.executable_path,
            "args": self.args
        })
        page = next(iter(await self._browser.pages()))
        await page.setViewport({
            "width": 1920, 
            "height": 1080
        })

        return self


    async def __aexit__(self, *_) -> None:
        if self._browser is not None:
            await self._browser.close()

        
    async def pages(self) -> List[pyppeteer.page.Page]:
        """Get a list of the currently open pages"""
        return await self._browser.pages()


    async def page(self) -> pyppeteer.page.Page:
        """Get the main page"""
        return next(iter(await self._browser.pages()))


    async def goto(self, url: str, new_page: bool = False) -> pyppeteer.page.Page:
        """Go to a web page"""
        
        page = next(iter(await self._browser.pages())) if new_page is False else await self._browser.newPage()

        if tuple(page.viewport.values()) != (1980, 1080):
            await page.setViewport({
                "width": 1920, 
                "height": 1080
            })

        if self.username and self.password:
            ### This is discouraged as the proxy connector is not asynchronous ###
            await page.authenticate({
                "username": self.username, 
                "password": self.password
            })

        if page.url != url and page.url != f"{url}/":
            await page.goto(url, {"waitUntil": "networkidle0"})

        return page


    async def screenshot(self, url: str) -> BytesIO:
        """Screenshot a web page"""

        async def _get_screenshot() -> bytes:
            page = await self.goto(url, new_page=True)
            ret = await page.screenshot()
            await page.close()
            return ret

        if "?" not in url:
            if cached_value := await CACHE.get(f"screenshot-{url}"):
                return BytesIO(cached_value)

            ret = await _get_screenshot()
            await CACHE.set(f"screenshot-{url}", ret, expiration=3600)
            return BytesIO(ret)
    
        return BytesIO(await _get_screenshot())


class SendHelp(Exception):
    pass
        
        
def strip_flags(text: str, ctx: "Context") -> str:
    """Strip flags from a string"""
    
    def _filter():
        ret = {}
        for k, d in ctx.command.parameters.items():
            ret[k] = ctx.parameters.get(k)
            for alias in d.get("aliases", TUPLE):
                ret[alias] = ctx.parameters.get(k)
                
        return ret
    
    flag_dict = _filter()
    return multi_replace(text, {
        **{f" --{key} {value}": "" for key, value in flag_dict.items() if value},
        **{f" -{key}": "" for key in flag_dict},
        **{f"--{key} {value}": "" for key, value in flag_dict.items() if value},
        **{f"-{key}": "" for key in flag_dict}
    })
    
    
async def embed_replacement(params: str, member: discord.Member, guild: discord.Guild, moderator: Optional[discord.Member] = None) -> str:
    """Replace variables in an embed script"""
    
    member = member or random.choice(guild.members)
    return multi_replace(params, {
        "{moderator}": str(moderator),
        "{user}": str(member),
        "{user.mention}": member.mention,
        "{user.name}": member.name,
        "{user.avatar}": member.display_avatar.url,
        "{user.color}": f"#{hex(await dominant_color(member.display_avatar.url)).replace('0x', '')}",
        "{user.joined_at}": discord.utils.format_dt(member.joined_at, style="R"),
        "{user.created_at}": discord.utils.format_dt(member.created_at, style="R"),
        "{user.discriminator}": member.discriminator,
        "{guild.name}": guild.name,
        "{guild.count}": str(guild.member_count),
        "{guild.count.format}": ordinal(guild.member_count),
        "{guild.id}": str(guild.id),
        "{guild.created_at}": discord.utils.format_dt(guild.created_at, style="R"),
        "{guild.boost_count}": str(guild.premium_subscription_count),
        "{guild.boost_count.format}": ordinal(guild.premium_subscription_count),
        "{guild.booster_count}": str(len(guild.premium_subscribers)),
        "{guild.booster_count.format}": ordinal(len(guild.premium_subscribers)),
        "{guild.boost_tier}": str(guild.premium_tier),
        "{guild.icon}": guild.icon.url if guild.icon else ""
    })
    
    
async def pagination_replacement(params: str, guild: discord.Guild, current_page: int, total_pages: int) -> str:
    """Replace variables in a pagination embed script"""
    return multi_replace(params, {
        "{page.current}": str(current_page),
        "{page.total}": str(total_pages),
        "{guild.name}": guild.name,
        "{guild.count}": str(guild.member_count),
        "{guild.count.format}": ordinal(guild.member_count),
        "{guild.id}": str(guild.id),
        "{guild.created_at}": discord.utils.format_dt(guild.created_at, style="R"),
        "{guild.boost_count}": str(guild.premium_subscription_count),
        "{guild.boost_count.format}": ordinal(guild.premium_subscription_count),
        "{guild.booster_count}": str(len(guild.premium_subscribers)),
        "{guild.booster_count.format}": ordinal(len(guild.premium_subscribers)),
        "{guild.boost_tier}": str(guild.premium_tier),
        "{guild.icon}": guild.icon.url if guild.icon else ""
    })
        
        
class HTTP:
    def __init__(self, headers: Optional[dict] = None, proxy: bool = False) -> None:
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        }
        self.proxied = proxy
        self.proxy = lambda: random.choice(os.environ.get("PROXIES").split("||")) if proxy else None
        self.get = self.json
        self.range = (
            "209.133.206.226", 
            "209.133.206.227", 
            "209.133.206.228", 
            #"209.133.206.229", 
            #"209.133.206.230"
        )

        
    def session(self, headers: Optional[dict] = None) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            headers=headers,
            connector=aiohttp.TCPConnector(
                family=socket.AF_INET,
                resolver=aiohttp.AsyncResolver(),
                limit=0,
                local_addr=(random.choice(self.range), 0) if self.proxied is False else None
            ),
            json_serialize=orjson.dumps
        )
        
        
    async def post_json(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, ssl: Optional[bool] = None) -> dict:
        """Send a POST request and get the JSON response"""
        
        async with self.session(headers=headers or self.headers) as session:
            async with session.post(url, data=data, params=params, proxy=self.proxy(), ssl=ssl) as response:
                return await response.json()


    async def post_text(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, ssl: Optional[bool] = None) -> str:
        """Send a POST request and get the HTML response"""
        
        async with self.session(headers=headers or self.headers) as session:
            async with session.post(url, data=data, params=params, ssl=ssl) as response:
                return await response.text()


    async def post_bytes(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, ssl: Optional[bool] = None) -> bytes:
        """Send a POST request and get the response in bytes"""
        
        async with self.session(headers=headers or self.headers) as session: 
            async with session.post(url, data=data, params=params, ssl=ssl) as response:
                return await response.read()


    async def _dl(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, ssl: Optional[bool] = False) -> bytes:
        
        total_size = 0
        data = b""

        async with self.session(headers=headers or self.headers) as session:
            async with session.get(url, params=params, ssl=ssl) as response:
                while True:
                    chunk = await response.content.read(4*1024)
                    data += chunk
                    total_size += len(chunk)

                    if not chunk:
                        break

                    if total_size > 500_000_000:
                        return None

                return data


    async def text(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, ssl: Optional[bool] = False) -> str:
        """Send a GET request and get the HTML response"""
        
        data = await self._dl(url, headers, params, ssl)
        if data:
            return data.decode("utf-8")
            
        return data


    async def json(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, ssl: Optional[bool] = False) -> dict:
        """Send a GET request and get the JSON response"""
        
        data = await self._dl(url, headers, params, ssl)
        if data:
            return orjson.loads(data)

        return data


    async def read(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, ssl: Optional[bool] = False) -> bytes:
        """Send a GET request and get the response in bytes"""
        return await self._dl(url, headers, params, ssl)
        
        
class MariaDB:
    def __init__(self) -> None:
        self.pool = None

    
    async def __aenter__(self):
        if self.pool is None:
            await self.initialize_pool()
            
        return self

    
    async def __aexit__(self, *_) -> None:
        return await self.cleanup()


    async def wait_for_pool(self) -> None:
        """Wait for the Pool to be initialized"""
        
        async with Timeout(10):
            while self.pool is None:
                logger.info("Pool not initialized yet, waiting...")


    async def initialize_pool(self) -> None:
        """Create the Pool"""
        
        self.pool = await aiomysql.create_pool(
            db="vilebot",
            host="localhost",
            port=3306,
            user="root",
            password="Glory9191",
            maxsize=10, 
            autocommit=True, 
            echo=False
        )


    async def cleanup(self) -> None:
        """Close the Pool"""

        self.pool.close()
        await self.pool.wait_closed()


    async def execute(self, statement: str, *params: Any, one_row: bool = False, one_value: bool = False, as_list: bool = False) -> Any:
        """Return all entries for the specified query"""
        
        await self.wait_for_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(statement, params)
                data = await cursor.fetchall()

        if data:
            if one_value:
                return data[0][0]

            if one_row:
                return data[0]

            if as_list:
                return tuple(row[0] for row in data)

            return data

        return ()


    async def fetchrow(self, statement: str, *params: Any) -> Tuple:
        """Return a single row"""
        return await self.execute(statement, *params, one_row=True)
    

    async def fetchval(self, statement: str, *params: Any) -> Any:
        """Return a single entry"""
        return await self.execute(statement, *params, one_value=True)


    async def fetch(self, statement: str, *params: Any) -> Tuple:
        """Return a Tuple of entries"""
        return await self.execute(statement, *params, as_list=True)


class VileCache:
    def __init__(self, bot: Optional["VileBot"] = None) -> None:
        self.bot = bot
        self._dict = {}
        self._rl = {}
        self._delete = {}
        self._futures = {}

        self.blacklisted = {}
        self.errors = {}
        self.custom_prefix = {}
        self.guild_prefix = {}
        self.lastfm_vote = {}
        self.donator = {}
        self.starboard = {}
        self.starboard_blacklist = {}
        self.starboard_message = {}
        self.welcome_settings = {}
        self.boost_settings = {}
        self.unboost_settings = {}
        self.booster_role = {}
        self.booster_award = {}
        self.booster_base = {}
        self.leave_settings = {}
        self.sticky_message_settings = {}
        self.aliases = {}
        self.filter = {}
        self.filter_whitelist = {}
        self.filter_event = {}
        self.filter_snipe = {}
        self.autoresponder = {}
        self.autoresponder_event = {}
        self.autoreact = {}
        self.autoreact_event = {}
        self.disabled_module = {}
        self.disabled_command = {}
        self.ignore = {}
        self.pins = {}
        self.webhooks = {}
        self.fake_permissions = {}
        self.pagination = {}
        self.pagination_pages = {}
        self.sticky_roles = {}
            

    async def do_expiration(self, key: str, expiration: int) -> None:
        """Start the expiration process for a key"""
        
        await asyncio.sleep(expiration)
        if key in self._dict: 
            del self._dict[key]
            

    async def set(self, key: Any, value: Any, expiration: Optional[int] = None) -> int:
        """Set a value to a key, with an optional expiration in seconds"""
        
        self._dict[key] = value
        if expiration is not None:
            if key in self._futures:
                self._futures[key].cancel()
            
            self._futures[key] = asyncio.ensure_future(self.do_expiration(key, expiration))
        
        return 1


    async def sadd(self, key: Any, *values: Any) -> int:
        """Add values to a set"""

        if key not in self._dict:
            self._dict[key] = set()

        assert isinstance(self._dict[key], set), "The provided key is already in the cache as another type."

        to_add = set()
        for value in values:
            if value not in self._dict[key]:
                to_add.add(value)

        for value in to_add:
            self._dict[key].add(value)

        return len(to_add)

    
    async def smembers(self, key: Any) -> set:
        """Get the members of a set"""

        assert isinstance(self._dict.get(key, set()), set), "That key belongs to another type."
        return tuple(self._dict.get(key, set()))


    async def scard(self, key: Any) -> int:
        """Get the number of members in a set"""

        assert isinstance(self._dict.get(key), set), "There is no such set in this cache, or that belongs to another type."
        return len(self._dict[key])


    async def srem(self, key: Any, *members: Any) -> int:
        """Remove members from a set"""

        assert isinstance(self._dict.get(key), set), "There is no such set in this cache, or that belongs to another type."

        to_delete = set()
        for member in members:
            if member in self._dict[key]:
                to_delete.add(member)

        for member in to_delete:
            self._dict[key].remove(member)

        if not self._dict[key]:
            del self._dict[key]

        return len(to_delete)


    async def delete(self, *keys: Any) -> int:
        """Delete the provided key"""
        
        ret = 0
        for key in keys:
            if key in self._dict:
                await asyncio.sleep(0.001)
                del self._dict[key]
                ret += 1
                
        return ret


    async def get(self, key: Any) -> Any:
        """Get the value for a key"""
        return self._dict.get(key, None)
        

    async def keys(self, pattern: Optional[str] = None) -> list:
        """Return a list of the dictionary's keys"""
        
        if pattern:
            return list(filter(lambda k: pattern.rstrip("*") in k, self._dict.keys()))
            
        return list(self._dict.keys())


    def is_ratelimited(self, key: Any) -> bool:
        """Check if a key is ratelimited"""
        
        _type, k = key.split(":")
        key = f"{_type}:{hash(k)}"
        if key in self._dict:
            if self._dict[key] >= self._rl[key]: 
                return True
                
        return False
        

    def time_remaining(self, key: Any) -> int:
        """Check the remaining time for a ratelimit"""
        
        _type, k = key.split(":")
        key = f"{_type}:{hash(k)}"
        if key in self._dict and key in self._delete:
            if not self._dict[key] >= self._rl[key]:
                return 0
                
            return (self._delete[key]["last"] + self._delete[key]["bucket"]) - datetime.now().timestamp()
        
        else:
            return 0
            

    async def ratelimited(self, key: str, amount: int, bucket: int) -> int:
        """Check if a key is ratelimited"""
        
        _type, k = key.split(":") if len(key.split(":")) == 2 else ("undefined", key)
        key = f"{_type}:{hash(k)}"
        if key not in self._dict:
            self._dict[key] = 1
            self._rl[key] = amount
            
            if key not in self._delete:
                self._delete[key] = {
                    "bucket": bucket,
                    "last": datetime.now().timestamp()
                }
            
            return 0
            
        try:
            if self._delete[key]["last"] + bucket <= datetime.now().timestamp():
                del self._dict[key]
                self._delete[key]["last"] = datetime.now().timestamp()
                self._dict[key] = 0
                    
            self._dict[key] += 1
            if self._dict[key] > self._rl[key]:
                return round((bucket - (datetime.now().timestamp() - self._delete[key]["last"])), 3)
                
            return 0
                    
        except Exception:
            return await self.ratelimited(key, amount, bucket)
        
    
    async def cache_blacklists(self) -> None:
        objectt = await self.bot.db.execute("SELECT object_id, reason FROM blacklisted_object;")
        starboardblacklist = await self.bot.db.execute("SELECT guild_id, channel_id FROM starboard_blacklist;")
        
        for object_id, reason in objectt:
            self.blacklisted[object_id] = reason
            
        for guild_id, channel_id in starboardblacklist:
            if guild_id not in self.starboard_blacklist:
                self.starboard_blacklist[guild_id] = []
                
            self.starboard_blacklist[guild_id].append(channel_id)
            
        
    async def cache_user_data(self) -> None:
        customprefix = await self.bot.db.execute("SELECT user_id, prefix FROM custom_prefix;")
        guildprefix = await self.bot.db.execute("SELECT guild_id, prefix FROM guild_prefix;")
        lastfmvote = await self.bot.db.execute("SELECT user_id, is_enabled, upvote_emoji, downvote_emoji FROM lastfm_vote_setting;")
        donator = await self.bot.db.execute("SELECT user_id, donation_tier, total_donated, donating_since FROM donator;")
        
        
        for user_id, prefix in customprefix:
            self.custom_prefix[user_id] = prefix
            
        for guild_id, prefix in guildprefix:
            self.guild_prefix[guild_id] = prefix
            
        for user_id, is_enabled, upvote_emoji, downvote_emoji in lastfmvote:
            self.lastfm_vote[user_id] = {
                "is_enabled": is_enabled,
                "upvote_emoji": upvote_emoji,
                "downvote_emoji": downvote_emoji
            }
            
        for user_id, donation_tier, total_donated, donating_since in donator:
            self.donator[user_id] = {
                "donation_tier": donation_tier,
                "total_donated": total_donated,
                "donating_since": donating_since
            }
            
    
    async def cache_settings(self) -> None:
        welcome_settings = await self.bot.db.execute("SELECT guild_id, channel_id, is_enabled, message FROM welcome_settings;")
        boost_settings = await self.bot.db.execute("SELECT guild_id, channel_id, is_enabled, message FROM boost_settings;")
        unboost_settings = await self.bot.db.execute("SELECT guild_id, channel_id, is_enabled, message FROM unboost_settings;")
        booster_award = await self.bot.db.execute("SELECT guild_id, role_id FROM booster_role_award;")
        booster_base = await self.bot.db.execute("SELECT guild_id, role_id FROM booster_role_base;")
        booster_role = await self.bot.db.execute("SELECT guild_id, user_id, role_id FROM booster_role;")
        leave_settings = await self.bot.db.execute("SELECT guild_id, channel_id, is_enabled, message FROM leave_settings;")
        sticky_message_settings = await self.bot.db.execute("SELECT guild_id, channel_id, is_enabled, message FROM sticky_message_settings;")
        aliases = await self.bot.db.execute("SELECT guild_id, command_name, alias FROM aliases;")
        _filter = await self.bot.db.execute("SELECT guild_id, keyword FROM filter;")
        filter_whitelist = await self.bot.db.execute("SELECT guild_id, user_id FROM filter_whitelist;")
        filter_event = await self.bot.db.execute("SELECT guild_id, event, is_enabled, threshold FROM filter_event;")
        filter_snipe = await self.bot.db.execute("SELECT guild_id, invites, links, images, words from filter_snipe;")
        autoresponder = await self.bot.db.execute("SELECT guild_id, keyword, response, created_by FROM autoresponder;")
        autoresponder_event = await self.bot.db.execute("SELECT guild_id, event, response FROM autoresponder_event;")
        autoreact = await self.bot.db.execute("SELECT guild_id, keyword, reaction FROM autoreact;")
        autoreact_event = await self.bot.db.execute("SELECT guild_id, event, reaction FROM autoreact_event;")
        disabled_feature = await self.bot.db.execute("SELECT guild_id, name, type FROM disabled_feature;")
        ignore = await self.bot.db.execute("SELECT guild_id, object_id, type FROM ignore_object;")
        pins = await self.bot.db.execute("SELECT guild_id, channel_id, is_enabled FROM pin_archive;")
        webhooks = await self.bot.db.execute("SELECT guild_id, identifier, webhook_url, channel_id FROM webhooks;")
        fake_permissions = await self.bot.db.execute("SELECT guild_id, role_id, permission FROM fake_permissions;")
        pagination = await self.bot.db.execute("SELECT guild_id, message_id, current_page FROM pagination;")
        pagination_pages = await self.bot.db.execute("SELECT guild_id, message_id, page, page_number FROM pagination_pages;")
        sticky_roles = await self.bot.db.execute("SELECT guild_id, role_id FROM sticky_roles;")

        for guild_id, channel_id, is_enabled, message in welcome_settings:
            if guild_id not in self.welcome_settings:
                self.welcome_settings[guild_id] = {}
                
            self.welcome_settings[guild_id][channel_id] = {
                "is_enabled": is_enabled,
                "message": message
            }
            
        for guild_id, channel_id, is_enabled, message in boost_settings:
            if guild_id not in self.boost_settings:
                self.boost_settings[guild_id] = {}
                
            self.boost_settings[guild_id][channel_id] = {
                "is_enabled": is_enabled,
                "message": message
            }
            
        for guild_id, channel_id, is_enabled, message in unboost_settings:
            if guild_id not in self.unboost_settings:
                self.unboost_settings[guild_id] = {}
                
            self.unboost_settings[guild_id][channel_id] = {
                "is_enabled": is_enabled,
                "message": message
            }
            
        for guild_id, role_id in booster_award:
            self.booster_award[guild_id] = role_id
            
        for guild_id, role_id in booster_base:
            self.booster_base[guild_id] = role_id
            
        for guild_id, user_id, role_id in booster_role:
            if guild_id not in self.booster_role:
                self.booster_role[guild_id] = {}
                
            self.booster_role[guild_id][user_id] = role_id
            
        for guild_id, channel_id, is_enabled, message in leave_settings:
            if guild_id not in self.leave_settings:
                self.leave_settings[guild_id] = {}
                
            self.leave_settings[guild_id][channel_id] = {
                "is_enabled": is_enabled,
                "message": message
            }
            
        for guild_id, channel_id, is_enabled, message in sticky_message_settings:
            if guild_id not in self.sticky_message_settings:
                self.sticky_message_settings[guild_id] = {}
                
            self.sticky_message_settings[guild_id][channel_id] = {
                "is_enabled": is_enabled,
                "message": message
            }
            
        for guild_id, command_name, alias in aliases:
            if guild_id not in self.aliases:
                self.aliases[guild_id] = {}
                
            if command_name not in self.aliases[guild_id]:
                self.aliases[guild_id][command_name] = []
                
            self.aliases[guild_id][command_name].append(alias)
            
        for guild_id, keyword in _filter:
            if guild_id not in self.filter:
                self.filter[guild_id] = []
                
            self.filter[guild_id].append(keyword)
            
        for guild_id, user_id in filter_whitelist:
            if guild_id not in self.filter_whitelist:
                self.filter_whitelist[guild_id] = []
                
            self.filter_whitelist[guild_id].append(user_id)
            
        for guild_id, event, is_enabled, threshold in filter_event:
            if guild_id not in self.filter_event:
                self.filter_event[guild_id] = {}
            
            self.filter_event[guild_id][event] = {
                "is_enabled": is_enabled,
                "threshold": threshold
            }
            
        for guild_id, invites, links, images, words in filter_snipe:
            self.filter_snipe[guild_id] = {
                "invites": invites,
                "links": links,
                "images": images,
                "words": words
            }
            
        for guild_id, keyword, response, created_by in autoresponder:
            if guild_id not in self.autoresponder:
                self.autoresponder[guild_id] = {}
                
            self.autoresponder[guild_id][keyword] = {
                "response": response,
                "created_by": created_by
            }
            
        for guild_id, event, response in autoresponder_event:
            if guild_id not in self.autoresponder_event:
                self.autoresponder_event[guild_id] = {}
            
            self.autoresponder_event[guild_id][event] = response
            
            
        for guild_id, keyword, reaction in autoreact:
            if guild_id not in self.autoreact:
                self.autoreact[guild_id] = {}
                
            if keyword not in self.autoreact[guild_id]:
                self.autoreact[guild_id][keyword] = []
                
            self.autoreact[guild_id][keyword].append(reaction)
            
        for guild_id, event, reaction in autoreact_event:
            if guild_id not in self.autoreact_event:
                self.autoreact_event[guild_id] = {}
                
            if event not in self.autoreact_event[guild_id]:
                self.autoreact_event[guild_id][event] = []
            
            self.autoreact_event[guild_id][event].append(reaction)
            
        for guild_id, name, _type in disabled_feature:
            if guild_id not in self.disabled_module:
                self.disabled_module[guild_id] = []
                
            if guild_id not in self.disabled_command:
                self.disabled_command[guild_id] = []
                
            if _type == "module":
                self.disabled_module[guild_id].append(name)
                
            elif _type == "command":
                self.disabled_command[guild_id].append(name)
                
        for guild_id, object_id, _ in ignore:
            if guild_id not in self.ignore:
                self.ignore[guild_id] = []
                
            self.ignore[guild_id].append(object_id)
            
        for guild_id, channel_id, is_enabled in pins:
            self.pins[guild_id] = {
                "channel_id": channel_id,
                "is_enabled": is_enabled
            }
            
        for guild_id, identifier, webhook_url, channel_id in webhooks:
            if guild_id not in self.webhooks:
                self.webhooks[guild_id] = {}
                
            self.webhooks[guild_id][identifier] = {
                "webhook_url": webhook_url,
                "channel_id": channel_id
            }
            
        for guild_id, role_id, permission in fake_permissions:
            if guild_id not in self.fake_permissions:
                self.fake_permissions[guild_id] = {}
            
            if role_id not in self.fake_permissions[guild_id]:
                self.fake_permissions[guild_id][role_id] = []
                
            self.fake_permissions[guild_id][role_id].append(permission)
            
        for guild_id, message_id, current_page in pagination:
            if guild_id not in self.pagination:
                self.pagination[guild_id] = {}
                
            self.pagination[guild_id][message_id] = current_page
            
        for guild_id, message_id, page, page_number in pagination_pages:
            if guild_id not in self.pagination_pages:
                self.pagination_pages[guild_id] = {}
                
            if message_id not in self.pagination_pages[guild_id]:
                self.pagination_pages[guild_id][message_id] = []
                
            self.pagination_pages[guild_id][message_id].append((page, page_number))

        for guild_id, role_id in sticky_roles:
            if guild_id not in self.sticky_roles:
                self.sticky_roles[guild_id] = []

            self.sticky_roles[guild_id].append(role_id)


    async def initialize_settings_cache(self) -> None:
        """Start the caching process"""
        
        self.__init__(self.bot)
        await self.cache_blacklists()
        await self.cache_user_data()
        await self.cache_settings()
        
        
        
class RSUCache:
    def __init__(self, bot: Optional["VileBot"] = None) -> None:
        self.bot = bot
        self._dict = {}
        self._rl = {}
        self._delete = {}
        self._futures = {}

        self.blacklisted = cacheclasses.Blacklists({}, bot.db)
        self.errors = {}
        self.custom_prefix = cacheclasses.CustomPrefix({}, bot.db)
        self.guild_prefix = cacheclasses.GuildPrefix({}, bot.db)
        self.lastfm_vote = cacheclasses.LastfmVote({}, bot.db)
        self.donator = cacheclasses.Donator({}, bot.db)
        self.starboard = None
        self.starboard_blacklist = {}
        self.starboard_message = None
        self.welcome_settings = cacheclasses.WelcomeSettings({}, bot.db)
        self.boost_settings = cacheclasses.BoostSettings({}, bot.db)
        self.unboost_settings = cacheclasses.UnboostSettings({}, bot.db)
        self.booster_role = cacheclasses.BoosterRole({}, bot.db)
        self.booster_award = cacheclasses.BoosterRoleAward({}, bot.db)
        self.booster_base = cacheclasses.BoosterRoleBase({}, bot.db)
        self.leave_settings = cacheclasses.LeaveSettings({}, bot.db)
        self.sticky_message_settings = cacheclasses.StickyMessageSettings({}, bot.db)
        self.aliases = cacheclasses.Aliases({}, bot.db)
        self.filter = cacheclasses.Filter({}, bot.db)
        self.filter_whitelist = cacheclasses.FilterWhitelist({}, bot.db)
        self.filter_event = cacheclasses.FilterEvent({}, bot.db)
        self.filter_snipe = cacheclasses.FilterSnipe({}, bot.db)
        self.autoresponder = cacheclasses.Autoresponder({}, bot.db)
        self.autoresponder_event = cacheclasses.AutoresponderEvent({}, bot.db)
        self.autoreact = cacheclasses.Autoreact({}, bot.db)
        self.autoreact_event = cacheclasses.AutoreactEvent({}, bot.db)
        self.disabled_module = cacheclasses.DisabledModule({}, bot.db)
        self.disabled_command = cacheclasses.DisabledCommand({}, bot.db)
        self.ignore = cacheclasses.Ignore({}, bot.db)
        self.pins = cacheclasses.Pins({}, bot.db)
        self.webhooks = cacheclasses.Webhooks({}, bot.db)
        self.fake_permissions = cacheclasses.FakePermissions({}, bot.db)
        self.pagination = cacheclasses.Pagination({}, bot.db)
        self.pagination_pages = cacheclasses.PaginationPages({}, bot.db)
        self.sticky_roles = cacheclasses.StickyRoles({}, bot.db)
            

    async def do_expiration(self, key: str, expiration: int) -> None:
        """Start the expiration process for a key"""
        
        await asyncio.sleep(expiration)
        if key in self._dict: 
            del self._dict[key]
            

    async def set(self, key: Any, value: Any, expiration: Optional[int] = None) -> int:
        """Set a value to a key, with an optional expiration in seconds"""
        
        self._dict[key] = value
        if expiration is not None:
            if key in self._futures:
                self._futures[key].cancel()
            
            self._futures[key] = asyncio.ensure_future(self.do_expiration(key, expiration))
        
        return 1


    async def sadd(self, key: Any, *values: Any) -> int:
        """Add values to a set"""

        if key not in self._dict:
            self._dict[key] = set()

        assert isinstance(self._dict[key], set), "The provided key is already in the cache as another type."

        to_add = set()
        for value in values:
            if value not in self._dict[key]:
                to_add.add(value)

        for value in to_add:
            self._dict[key].add(value)

        return len(to_add)

    
    async def smembers(self, key: Any) -> set:
        """Get the members of a set"""

        assert isinstance(self._dict.get(key, set()), set), "That key belongs to another type."
        return tuple(self._dict.get(key, set()))


    async def scard(self, key: Any) -> int:
        """Get the number of members in a set"""

        assert isinstance(self._dict.get(key), set), "There is no such set in this cache, or that belongs to another type."
        return len(self._dict[key])


    async def srem(self, key: Any, *members: Any) -> int:
        """Remove members from a set"""

        assert isinstance(self._dict.get(key), set), "There is no such set in this cache, or that belongs to another type."

        to_delete = set()
        for member in members:
            if member in self._dict[key]:
                to_delete.add(member)

        for member in to_delete:
            self._dict[key].remove(member)

        if not self._dict[key]:
            del self._dict[key]

        return len(to_delete)


    async def delete(self, *keys: Any) -> int:
        """Delete the provided key"""
        
        ret = 0
        for key in keys:
            if key in self._dict:
                await asyncio.sleep(0.001)
                del self._dict[key]
                ret += 1
                
        return ret


    async def get(self, key: Any) -> Any:
        """Get the value for a key"""
        return self._dict.get(key, None)
        

    async def keys(self, pattern: Optional[str] = None) -> list:
        """Return a list of the dictionary's keys"""
        
        if pattern:
            return list(filter(lambda k: pattern.rstrip("*") in k, self._dict.keys()))
            
        return list(self._dict.keys())


    def is_ratelimited(self, key: Any) -> bool:
        """Check if a key is ratelimited"""
        
        _type, k = key.split(":")
        key = f"{_type}:{hash(k)}"
        if key in self._dict:
            if self._dict[key] >= self._rl[key]: 
                return True
                
        return False
        

    def time_remaining(self, key: Any) -> int:
        """Check the remaining time for a ratelimit"""
        
        _type, k = key.split(":")
        key = f"{_type}:{hash(k)}"
        if key in self._dict and key in self._delete:
            if not self._dict[key] >= self._rl[key]:
                return 0
                
            return (self._delete[key]["last"] + self._delete[key]["bucket"]) - datetime.now().timestamp()
        
        else:
            return 0
            

    async def ratelimited(self, key: str, amount: int, bucket: int) -> int:
        """Check if a key is ratelimited"""
        
        _type, k = key.split(":") if len(key.split(":")) == 2 else ("undefined", key)
        key = f"{_type}:{hash(k)}"
        if key not in self._dict:
            self._dict[key] = 1
            self._rl[key] = amount
            
            if key not in self._delete:
                self._delete[key] = {
                    "bucket": bucket,
                    "last": datetime.now().timestamp()
                }
            
            return 0
            
        try:
            if self._delete[key]["last"] + bucket <= datetime.now().timestamp():
                del self._dict[key]
                self._delete[key]["last"] = datetime.now().timestamp()
                self._dict[key] = 0
                    
            self._dict[key] += 1
            if self._dict[key] > self._rl[key]:
                return round((bucket - (datetime.now().timestamp() - self._delete[key]["last"])), 3)
                
            return 0
                    
        except Exception:
            return await self.ratelimited(key, amount, bucket)
        
        
        
async def confirm(ctx: "Context", message: discord.Message) -> bool:
    """Attach confirmation buttons to a message"""
    
    view = Confirm(message=message, invoker=ctx.author)
    await message.edit(view=view)
    await view.wait()
    return view.value
        
        
class Context(commands.Context):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parameters = {}
        
        
    async def success(self, message: str, member: Optional[discord.Member] = None, content: Optional[str] = None, delete_after: Optional[int] = None) -> discord.Message:
        """Send a success notification"""
        return await self.respond(message, content=content, emoji=self.bot.done, color=self.bot.color, member=member, delete_after=delete_after)
        
        
    async def error(self, message: str, member: Optional[discord.Member] = None, content: Optional[str] = None, delete_after: Optional[int] = None) -> discord.Message:
        """Send an error notification"""
        return await self.respond(message, content=content, emoji=self.bot.warn, color=self.bot.color, member=member, delete_after=delete_after)
        
    
    async def respond(self, message: str, emoji: str = "", color: int = constants.colors.main, content: Optional[str] = None, member: Optional[discord.Member] = None, delete_after: Optional[int] = None) -> discord.Message:
        
        if await self.bot.cache.ratelimited(f"rl:ms{self.guild.id}", 3, 5):
            return
            
        try:
            return await self.reply(
                content=content,
                embed=discord.Embed(
                    color=color,
                    description=f"{emoji} {(member or self.author).mention}**:** {message}"
                )
            )
        except Exception:
            return await self.send(
                content=content,
                embed=discord.Embed(
                    color=color,
                    description=f"{emoji} {(member or self.author).mention}**:** {message}"
                )
            )
        
        
    async def paginate(self, to_paginate: Union[tuple, list], show_index: bool = True) -> Optional[discord.Message]:
        """Paginate embeds or rows"""
        
        if isinstance(to_paginate, tuple):
            embed, rows = to_paginate

            if not isinstance(rows, list):
                return

            if len(rows) == 0:
                return await self.error("No entries found!")
            
            embeds = []
            embed.description = StringIO()
            rows = tuple(
                f"{f'`{index}` ' if show_index else ''}{row}"
                for index, row in enumerate(rows, start=1)
            )
            count = 0
            
            for row in rows:
                if count < 10:
                    embed.description.write(f"\n{row}")
                    count += 1
                    
                else:
                    count = 0
                    embed.description = embed.description.getvalue()
                    embeds.append(embed)
                    embed = embed.copy()
                    embed.description = StringIO()
                    embed.description.write(row)
                    count += 1
                
            if count > 0 and count <= 10:
                embeds.append(embed)
                
            for index, embed in enumerate(embeds, start=1):
                if isinstance(embed.description, StringIO):
                    embed.description = embed.description.getvalue()

                embed.set_footer(text=f"Page {index} / {len(embeds)}  ({len(rows)} entries)")
                embed.set_author(name=self.author, icon_url=self.author.display_avatar)

            if self.should_paginate(embeds) is False:
                return await self.reply(embed=embeds[0])

            interface = Paginator(self.bot, embeds, self, invoker=self.author.id)
            return await interface.start()

        elif isinstance(to_paginate, list):
            
            embeds = to_paginate
            if len(embeds) == 0:
                return await self.error("No entries found!")
                

            if self.should_paginate(embeds) is False:
                return await self.reply(embed=embeds[0])

            interface = Paginator(self.bot, embeds, self, invoker=self.author.id)
            return await interface.start()
            
            
        
    def find_role(self, name: str) -> Optional[discord.Role]:
        """Query for a role"""
        
        roles = tuple(r.name.lower() for r in self.guild.roles)
        closest = difflib.get_close_matches(name.lower(), roles, n=3, cutoff=0.5)
        if closest:
            for r in self.guild.roles:
                if r.name.lower() == closest[0].lower():
                    return r
        
        return None


    async def can_moderate(self, user: Union[discord.Member, discord.User], action: str = 'moderate') -> Optional[discord.Message]:
        """Check if the author can moderate the provided user"""
        
        if user == self.author:
            return await self.error(f"You can't **{action}** yourself")
        
        if isinstance(user, discord.Member) and (user.top_role.position >= self.author.top_role.position and self.author.id != self.guild.owner_id) or user.id == self.guild.owner_id:
            return await self.error(f"You can't **{action}** that {'member' if isinstance(user, discord.Member) else 'user'}")
            
        if self.bot.get_user(user.id) == self.bot.get_user(self.bot.user.id):
            return await self.error(f"You can't **{action}** that {'member' if isinstance(user, discord.Member) else 'user'}")
            
        if isinstance(user, discord.Member) and (user.top_role.position >= self.guild.me.top_role.position and self.author.id != self.guild.owner_id):
            return await self.error(f"I can't **{action}** that {'member' if isinstance(user, discord.Member) else 'user'}")

        return None


    def should_paginate(self, _list: list) -> bool:
        """Check if a list needs to be paginated"""
        return len(_list) > 1


    def is_dangerous(self, role: discord.Role) -> bool:
        """Check if a role is dangerous"""
        
        permissions = role.permissions
        return any((
            permissions.kick_members, permissions.ban_members,
            permissions.administrator, permissions.manage_channels,
            permissions.manage_guild,
            permissions.manage_roles, permissions.manage_webhooks,
            permissions.manage_emojis_and_stickers, permissions.manage_threads,
            permissions.mention_everyone
        ))


    def is_boosting(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if a user is boosting a mutual server (mostly inaccurate)"""
        
        for guild in user.mutual_guilds:
            if guild.get_member(user.id).premium_since is not None:
                return True

        return False


    async def await_response(self) -> Optional[str]:
        """Wait wait for a response from the author and return it"""
        
        try:
            message = await self.bot.wait_for(
                "message", 
                check=lambda m: m.author.id == self.author.id and m.channel.id == self.channel.id, 
                timeout=30
            )
            
        except asyncio.TimeoutError:
            return None
        
        else:
            return message.content
            
            
class VileBot(commands.AutoShardedBot):
    def __init__(self, cluster_id: int, cluster_ids: tuple) -> None:
        super().__init__(
            owner_ids=(
                1109861649910874274,
                461914901624127489,
                267267329807745024,
            ),
            anti_cloudflare_ban=True,
            help_command=HelpCommand(),
            command_prefix=lambda _bot, message: _bot.cache.custom_prefix.get(message.author.id) or _bot.cache.guild_prefix.get(message.guild.id) or commands.when_mentioned_or(",,")(_bot, message),
            case_insensitive=True,
            strip_after_prefix=True,
            allowed_mentions=discord.AllowedMentions(
                users=True, 
                roles=False, 
                replied_user=False, 
                everyone=False
            ),
            max_messages=500,
            activity=discord.Streaming(
                name="in discord.gg/vilebot",
                url="https://twitch.tv/directory"
            ),
            chunk_guilds_at_startup=False,
            shard_count=2,
            shard_ids=(0, 1),
            intents=discord.Intents(
        		guilds=True,
        		members=True,
        		bans=True,
        		emojis=True,
        		integrations=True,
        		webhooks=True,
        		invites=True,
        		voice_states=True,
        		presences=False,
        		messages=True,
        		reactions=True,
        		typing=True,
        		message_content=True,
        	)
        )
        self.cluster = cluster_id
        self.clusters = cluster_ids
        self.color = constants.colors.main
        self.done = constants.emojis.done
        self.fail = constants.emojis.fail
        self.warn = constants.emojis.warn
        self.dash = constants.emojis.dash
        self.reply = constants.emojis.reply
        self.version = "3.8.1"
        self.db = MariaDB()
        self.cache = VileCache(self)
        self.config = {
            "emojis": constants.emojis,
            "colors": constants.colors,
            "api": constants.api
        }
        self.blacklist_types = {
            0: "Unknown reason",
            1: "Abusing or exploiting Vile bot",
            2: "Violating the Discord ToS",
            3: "Violating our Terms or Privacy Policy",
            4: "Copying Vile's services or features",
            5: "Channel blacklisted by server administrators",
            6: "Guild blacklisted by the bot team",
            7: "Role blacklisted by server administrators"
        }
        self.before_invoke(self.before_commands)
        self.check(self.command_check)
        
        
    async def setup_hook(self) -> None:
        logger.info("Setting things up...")
        self.session = HTTP(proxy=False)
        self.proxied_session = HTTP(proxy=True)
        await self.db.initialize_pool()
        self.loop.create_task(self.cache.initialize_settings_cache())
        
        
    async def get_context(self, origin: Union[discord.Interaction, discord.Message], cls: Any = Context) -> "Context":
        return await super().get_context(origin, cls=cls)
        
        
    @property
    def user_count(self) -> int:
        return sum(g.member_count for g in self.guilds)
        
    
    @property
    def guild_count(self) -> int:
        return len(self.guilds)
        
    
    @staticmethod
    async def before_commands(ctx: "Context") -> None:
        """A function that runs before commands are executed"""
        
        if not ctx.guild.chunked:
            await ctx.guild.chunk(cache=True)

        if hasattr(ctx.command, "parameters"):
            ctx.parameters = await ParameterParser(ctx, ctx.command.parameters).parse()     
        
        await ctx.typing()

            
    @staticmethod
    async def command_check(ctx: "Context") -> bool:
        """A check that runs before commands are executed"""
        
        if await ctx.bot.is_owner(ctx.author):
            return True
        
        # blacklisted object
        if any((
            ctx.author.id in ctx.bot.cache.blacklisted,
            ctx.channel.id in ctx.bot.cache.blacklisted,
            ctx.guild.id in ctx.bot.cache.blacklisted
        )):
            return False
            
        # cooldown
        if retry_after := await ctx.bot.cache.ratelimited(f"rl:user_commands{ctx.author.id}", 2, 4):
            if await ctx.bot.cache.ratelimited(f"globalrl:user_commands{ctx.author.id}", 30, 60):
                return False
                    
            if await ctx.bot.cache.ratelimited(f"banrl:user_commands{ctx.author.id}", 5, 8):
                await ctx.bot.blacklist(ctx.author.id, type=1)
                return False
                
            raise commands.CommandOnCooldown(
                None, 
                retry_after, 
                None
            )

        # disabled feature
        if (ctx.command.root_parent or ctx.command).qualified_name in ctx.bot.cache.disabled_command.get(ctx.guild.id, TUPLE):
            await ctx.error("That command has been **disabled** by **server administrators**.")
            return False
            
        if (ctx.command.cog_name or "").lower() in ctx.bot.cache.disabled_module.get(ctx.guild.id, TUPLE):
            await ctx.error("That module has been **disabled** by **server administrators**.")
            return False
            
        # ignored object
        if any((
            ctx.author.id in ctx.bot.cache.ignore.get(ctx.guild.id, TUPLE), 
            ctx.channel.id in ctx.bot.cache.ignore.get(ctx.guild.id, TUPLE), 
            any(role.id in ctx.bot.cache.ignore.get(ctx.guild.id, TUPLE) for role in ctx.author.roles)
        )) and ctx.author.guild_permissions.administrator is False:
            return False
            
        return True
        
        
    async def load_extensions(self) -> None:
        """Load the bot extensions"""
        folders = ("cogs", "web")
        await self.load_extension("jishaku")
        for folder in folders:
            for file in Path(folder).glob("*.py"):
                try:
                    await self.load_extension(f"{folder}.{file.name[:-3]}")
                    logger.info(f"Successfully loaded {folder}/{file.name}")
                    
                except Exception:
                    logger.error(f"Failed to load {folder}/{file.name}")
        
        
    async def blacklist(self, id: int, type: int = 0) -> int:
        """Blacklist the provided ID"""
        
        if type not in self.blacklist_types:
            raise ValueError("Please provide a valid type between 0 and 7.")
            
        if id in self.cache.blacklisted:
            return 0
            
        await self.db.execute(
            "INSERT INTO blacklisted_object (object_id, reason) VALUES (%s, %s);",
            id, self.blacklist_types[type]
        )
        self.cache.blacklisted[id] = self.blacklist_types[type]
        
        if (user := self.get_user(id)) and self.get_user(id).mutual_guilds:
            asyncio.ensure_future(user.send(embed=discord.Embed(
                color=self.color,
                description=f"{self.warn} {user.mention}**:** You were **blacklisted** for violating our Terms of Service or Privacy Policy.\n{self.reply} **Exact Reason:** {self.blacklist_types[type]}"
            ).set_footer(text="The Vile Team")
            ))
            
        return 1
        
        
    async def unblacklist(self, id: int) -> int:
        """Unblacklist the provided ID"""
        
        if id not in self.cache.blacklisted:
            return 0
            
        await self.db.execute(
            "DELETE FROM blacklisted_object WHERE object_id = %s;",
            id
        )
        del self.cache.blacklisted[id]
        
        if (user := self.get_user(id)) and self.get_user(id).mutual_guilds:
            asyncio.ensure_future(user.send(embed=discord.Embed(
                color=self.color,
                description=f"{self.warn} {user.mention}**:** You were **unblacklisted** and can now continue using Vile bot."
            ).set_footer(text="The Vile Team")
            ))
            
        return 1
        
    
    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (Application ID: {self.user.id})")
        await self.load_extensions()
        self.invite = discord.utils.oauth_url(
            self.user.id, 
            permissions=discord.Permissions(8)
        )
        
    
    async def on_shard_connect(self, shard_id: int):
        shard = self.shards[shard_id]._parent
        shard.uptime = datetime.now()
        shard.cluster_id = self.cluster
        
        
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
            
        await self.wait_until_ready()    
        block_command_execution = False
        context = await self.get_context(message)
        
        def check():
            return all([
                message.author.id != message.guild.owner_id,
                message.author.guild_permissions.administrator is False,
                (message.author.top_role.position <= message.guild.me.top_role.position) if message.author.top_role else True,
                not any((message.author.id in self.cache.filter_whitelist.get(message.guild.id, TUPLE), message.channel.id in self.cache.filter_whitelist.get(message.guild.id, TUPLE), any(role.id in self.cache.filter_whitelist.get(message.guild.id, TUPLE) for role in message.author.roles))),
                message.author.id != message.guild.me.id
            ])
            
        if message.guild.id in self.cache.filter and block_command_execution is False:
            if check():
                async def do_filter():
                    content = "".join(c for c in message.content if c.isalnum() or c.isspace())
                    for keyword in self.cache.filter[message.guild.id]:
                        if keyword in content: # or chardet.detect(content.encode("utf-8"))["language"] is None:
                            asyncio.gather(*[
                                message.author.timeout(datetime.now().astimezone() + timedelta(seconds=5)),
                                context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my chat filter", member=message.guild.me),
                                message.delete()
                            ])
                            block_command_execution = True
                            await asyncio.sleep(0.001)
                        
                asyncio.ensure_future(do_filter())
                
        if "spoilers" in self.cache.filter_event.get(message.guild.id, DICT) and self.cache.filter_event[message.guild.id]["spoilers"]["is_enabled"] == True and block_command_execution is False:
            if message.content.count("||") >= (self.cache.filter_event[message.guild.id]["spoilers"]["threshold"] * 2):
                if check():
                    asyncio.gather(*[
                        message.author.timeout(datetime.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my spoiler filter", member=message.guild.me),
                        message.delete()
                    ])
                    block_command_execution = True
                    
        if "links" in self.cache.filter_event.get(message.guild.id, DICT) and self.cache.filter_event[message.guild.id]["links"]["is_enabled"] == True and block_command_execution is False:
            if check():
                if "http" in message.content or "www" in message.content:
                    asyncio.gather(*[
                        message.author.timeout(datetime.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my link filter", member=message.guild.me),
                        message.delete()
                    ])
                    block_command_execution = True
                    
        if "spam" in self.cache.filter_event.get(message.guild.id, DICT) and self.cache.filter_event[message.guild.id]["spam"]["is_enabled"] == True and block_command_execution is False:
            if check():
                if await self.cache.ratelimited(f"rl:message_spam{message.author.id}-{message.guild.id}", self.cache.filter_event[message.guild.id]["spam"]["threshold"], 5):
                    asyncio.gather(*[
                        message.author.timeout(datetime.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my spam filter", member=message.guild.me)
                    ])
                    await message.channel.purge(limit=10, check=lambda m: m.author.id == message.author.id)
                    block_command_execution = True
                    
        if "emojis" in self.cache.filter_event.get(message.guild.id, DICT) and self.cache.filter_event[message.guild.id]["emojis"]["is_enabled"] == True and block_command_execution is False:
            if len(find_emojis(message.content)) >= (self.cache.filter_event[message.guild.id]["emojis"]["threshold"]):
                if check():
                    asyncio.gather(*[
                        message.author.timeout(datetime.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my emoji filter", member=message.guild.me),
                        message.delete()
                    ])
                    block_command_execution = True
                    
        if "invites" in self.cache.filter_event.get(message.guild.id, DICT) and self.cache.filter_event[message.guild.id]["invites"]["is_enabled"] == True and block_command_execution is False:
            if find_invites(message.content):
                if check():
                    asyncio.gather(*[
                        message.author.timeout(datetime.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my invite filter", member=message.guild.me),
                        message.delete()
                    ])
                    block_command_execution = True
                    
        if "caps" in self.cache.filter_event.get(message.guild.id, DICT) and self.cache.filter_event[message.guild.id]["caps"]["is_enabled"] == True and block_command_execution is False:
            if len(tuple(c for c in message.content if c.isupper())) >= (self.cache.filter_event[message.guild.id]["caps"]["threshold"]):
                if check():
                    asyncio.gather(*[
                        message.author.timeout(datetime.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my cap filter", member=message.guild.me),
                        message.delete()
                    ])
                    block_command_execution = True
                    
        if "massmention" in self.cache.filter_event.get(message.guild.id, DICT) and self.cache.filter_event[message.guild.id]["massmention"]["is_enabled"] == True and block_command_execution is False:
            if len(message.mentions) >= (self.cache.filter_event[message.guild.id]["massmention"]["threshold"]):
                if check():
                    asyncio.gather(*[
                        message.author.timeout(datetime.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my mention filter", member=message.guild.me),
                        message.delete()
                    ])
                    block_command_execution = True
                    
        if block_command_execution is True:
            return
            
        if str(self.user.id) in regex.user_mention.findall(message.content):
            prefix = self.command_prefix(self, message)
            asyncio.ensure_future(context.respond(
                f"[**Vile's**](https://discord.gg/KsfkG3BZ4h) prefix is `{prefix[-1] if isinstance(prefix, list) else prefix}`",
                emoji="<:v_slash:1067034025895665745>"
            ))
            
        if context.valid is False:
            if message.guild.id in self.cache.autoresponder:
                async def do_autoresponder():
                    if await self.cache.ratelimited(f"rl:autoresponder{message.guild.id}", 5, 30):
                        return
                    for keyword, _dict in self.cache.autoresponder[message.guild.id].items():
                        if keyword in message.content:
                            script = ParsedEmbed(
                                EmbedScriptValidator(),
                                    _dict["response"]
                            )
                            asyncio.ensure_future(script.send(
                                context,
                                bot=self,
                                guild=message.guild,
                                channel=message.channel,
                                user=message.author
                            ))
                            await asyncio.sleep(0.001)
                    
                asyncio.ensure_future(do_autoresponder())
                
            if message.guild.id in self.cache.autoresponder_event:
                async def do_autoresponder_event(type: str):
                    if await self.cache.ratelimited(f"rl:autoresponder{message.guild.id}", 5, 30):
                        return
                    script = ParsedEmbed(
                        EmbedScriptValidator(),
                        self.cache.autoresponder_event[message.guild.id][type]
                    )
                    asyncio.ensure_future(script.send(
                        context,
                        bot=self,
                        guild=message.guild,
                        channel=message.channel,
                        user=message.author
                    ))
                            
                if "images" in self.cache.autoresponder_event[message.guild.id] and message.attachments:
                    asyncio.ensure_future(do_autoresponder_event("images"))
                
                if "spoilers" in self.cache.autoresponder_event[message.guild.id] and (message.content.count("||") > 2):
                    asyncio.ensure_future(do_autoresponder_event("spoilers"))
                    
                if "emojis" in self.cache.autoresponder_event[message.guild.id] and find_emojis(message.content):
                    asyncio.ensure_future(do_autoresponder_event("emojis"))
        
                if "stickers" in self.cache.autoresponder_event[message.guild.id] and message.stickers:
                    asyncio.ensure_future(do_autorespondet_event("stickers"))
            
            if message.guild.id in self.cache.autoreact:
                async def do_autoreact():
                    if await self.cache.ratelimited(f"rl:autoreact{message.guild.id}", 5, 30):
                        return
                    for keyword, reactions in self.cache.autoreact[message.guild.id].items():
                        if keyword in message.content:
                            asyncio.gather(*(message.add_reaction(reaction) for reaction in reactions))
                            await asyncio.sleep(0.001)
                    
                asyncio.ensure_future(do_autoreact())
                
            if message.guild.id in self.cache.autoreact_event:
                async def do_autoreact_event(type: str):
                    if await self.cache.ratelimited(f"rl:autoreact{message.guild.id}", 5, 30):
                        return
                    reactions = self.cache.autoreact_event[message.guild.id][type]
                    asyncio.gather(*(message.add_reaction(reaction) for reaction in reactions))
                    
                if "images" in self.cache.autoreact_event[message.guild.id] and message.attachments:
                    asyncio.ensure_future(do_autoreact_event("images"))
                
                if "spoilers" in self.cache.autoreact_event[message.guild.id] and (message.content.count("||") > 2):
                    asyncio.ensure_future(do_autoreact_event("spoilers"))
                    
                if "emojis" in self.cache.autoreact_event[message.guild.id] and find_emojis(message.content):
                    asyncio.ensure_future(do_autoreact_event("emojis"))
        
                if "stickers" in self.cache.autoreact_event[message.guild.id] and message.stickers:
                    asyncio.ensure_future(do_autoreact_event("stickers"))
        
        await self.process_commands(message)
        
        
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        await self.wait_until_ready()
        if after.guild is None or after.author.bot:
            return
            
        if before.content != after.content:
            await self.process_commands(after)
            
        if before.pinned is False and after.pinned is True:
            if config := self.cache.pins.get(after.guild.id, DICT):
                if config["is_enabled"] == True and (channel := after.guild.get_channel(config["channel_id"])):
                    embed = discord.Embed(
                        color=after.author.color, 
                        description=after.content + (("\n" + "\n".join(attachment.url for attachment in after.attachments)) if after.attachments else ""),
                        timestamp=after.created_at
                    )
                    embed.set_author(name=after.author, icon_url=after.author.display_avatar)
                    embed.set_footer(text=f"Pin archived from #{channel.name}")
                    if after.attachments:
                        embed.set_image(url=after.attachments[0].url)
                        
                    try:
                        await channel.send(
                            embed=embed,
                                view=discord.ui.View().add_item(
                                    discord.ui.Button(
                                        label="Jump to Message",
                                        style=discord.ButtonStyle.link,
                                        url=after.jump_url
                                )
                            )
                        )
                        await after.unpin()
                    except Exception:
                        pass
            
        
    async def on_user_update(self, before: discord.User, after: discord.User):
        await self.wait_until_ready()
        if str(before) != str(after):
            await self.db.execute(
                "INSERT INTO name_history (user_id, name, updated_on) VALUES (%s, %s, %s);",
                before.id, encrypt(str(before)), datetime.now()
            )
            
            
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        await self.wait_until_ready()
        if after.guild.premium_subscriber_role not in before.roles and after.guild.premium_subscriber_role in after.roles:
            self.dispatch("boost", after)
            
        elif after.guild.premium_subscriber_role in before.roles and after.guild.premium_subscriber_role not in after.roles:
            self.dispatch("unboost", after)
            
        elif before.nick != after.nick:
            if after.guild.id in self.cache.filter:
                if after.nick in self.cache.filter[after.guild.id]:
                    await after.edit(nick=None)
            
    
    async def on_member_join(self, member: discord.Member):
        await self.wait_until_ready()
        
        if member.id in await self.db.fetch("SELECT user_id FROM hard_banned WHERE guild_id = %s;", member.guild.id):
            return await member.ban(reason="Vile Moderation: User is hard banned")
                
        if member.guild.id in self.cache.welcome_settings:
            if await self.cache.ratelimited(f"rl:welcome_message{message.guild.id}", 5, 60):
                return
                
            for channel_id in self.cache.welcome_settings[member.guild.id]:
                if (channel := self.get_channel(channel_id)) is not None:
                    if channel.permissions_for(member.guild.me).send_messages is True:
                        await asyncio.sleep(0.001)
                        settings = self.cache.welcome_settings[member.guild.id][channel_id]
                        if settings["is_enabled"] == False:
                            continue
                            
                        script = ParsedEmbed(
                            EmbedScriptValidator(),
                            settings["message"]
                        )
                        await script.send(
                            channel,
                            bot=self,
                            guild=member.guild,
                            channel=channel,
                            user=member
                        )
                        
        if await self.db.fetchrow("SELECT * FROM muted_user WHERE guild_id = %s AND user_id = %s LIMIT 1;", member.guild.id, member.id):
            if mute_role_id := await self.db.fetchval("SELECT mute_role_id FROM guild_settings WHERE guild_id = %s;", member.guild.id):
                if mute_role := member.guild.get_role(mute_role_id):
                    await member.add_roles(
                        mute_role,
                        reason="Vile Moderation: Member is muted"
                    )
                    
        if await self.db.fetchrow("SELECT * FROM jailed_user WHERE guild_id = %s AND user_id = %s LIMIT 1;", member.guild.id, member.id):
            if jail_role_id := await self.db.fetchval("SELECT jail_role_id FROM guild_settings WHERE guild_id = %s;", member.guild.id):
                if jail_role := member.guild.get_role(jail_role_id):
                    await member.add_roles(
                        jail_role,
                        reason="Vile Moderation: Member is jailed"
                    )

        if member.id in await self.cache.smembers(f"srm{member.guild.id}"):
            await asyncio.gather(*(
                member.add_roles(
                    member.guild.get_role(role_id),
                    reason="Sticky role"
                )
                for role_id in self.cache.sticky_roles[member.guild.id]
                if member.guild.get_role(role_id)
            ))
                        
            
    async def on_member_remove(self, member: discord.Member):
        await self.wait_until_ready()

        if member.roles:
            await self.cache.sadd(f"restore{member.guild.id}-{member.id}", *member.roles)

        if member.guild.id in self.cache.sticky_roles:
            await self.cache.sadd(f"srm{member.guild.id}", member.id)

        if member.guild.id in self.cache.leave_settings:
            if await self.cache.ratelimited(f"rl:leave_message{message.guild.id}", 5, 60):
                return
                
            for channel_id in self.cache.leave_settings[member.guild.id]:
                if (channel := self.get_channel(channel_id)) is not None:
                    if channel.permissions_for(member.guild.me).send_messages is True:
                        await asyncio.sleep(0.001)
                        settings = self.cache.leave_settings[member.guild.id][channel_id]
                        if settings["is_enabled"] == False:
                            continue
                            
                        script = ParsedEmbed(
                            EmbedScriptValidator(),
                            settings["message"]
                        )
                        await script.send(
                            channel,
                            bot=self,
                            guild=member.guild,
                            channel=channel,
                            user=member
                        )
                        
                        
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.wait_until_ready()
        if payload.member is None or payload.member.bot:
            return
            
        if payload.member.guild.me.guild_permissions.administrator is False:
            return
            
        if payload.guild_id in self.cache.pagination and payload.guild_id in self.cache.pagination_pages:
            if payload.message_id in self.cache.pagination[payload.guild_id] and payload.message_id in self.cache.pagination_pages[payload.guild_id]:
                channel = self.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                
                if str(payload.emoji) == "<:v_left_page:1067034010624200714>":
                    await message.remove_reaction(payload.emoji, payload.member)
                    current_page = self.cache.pagination[payload.guild_id][message.id]
                    page_count = len(self.cache.pagination_pages[payload.guild_id][message.id])
                    
                    if current_page == 1:
                        return
                        
                    new_page, _ = next(filter(lambda page: page[1] == current_page-1, self.cache.pagination_pages[payload.guild_id][message.id]), None)
                    if new_page is None:
                        return
                        
                    await self.db.execute(
                        "UPDATE pagination SET current_page = %s WHERE message_id = %s;", 
                        current_page-1, message.id
                    )
                    self.cache.pagination[payload.guild_id][message.id] = current_page-1
                    
                    validator = EmbedScriptValidator()
                    data = await validator.to_embed(await pagination_replacement(
                        new_page, 
                        payload.member.guild, 
                        current_page-1, 
                        page_count
                    ))
                    del data["files"]
                    await message.edit(**data)
                    
    
                if str(payload.emoji) == "<:v_right_page:1067034017108607076>":
                    await message.remove_reaction(payload.emoji, payload.member)
                    current_page = self.cache.pagination[payload.guild_id][message.id]
                    page_count = len(self.cache.pagination_pages[payload.guild_id][message.id])
                    
                    if current_page == page_count:
                        return
                        
                    new_page, _ = next(filter(lambda page: page[1] == current_page+1, self.cache.pagination_pages[payload.guild_id][message.id]), None)
                    if new_page is None:
                        return
                        
                    await self.db.execute(
                        "UPDATE pagination SET current_page = %s WHERE message_id = %s;", 
                        current_page+1, message.id
                    )
                    self.cache.pagination[payload.guild_id][message.id] = current_page+1
                        
                    validator = EmbedScriptValidator()
                    data = await validator.to_embed(await pagination_replacement(
                        new_page, 
                        payload.member.guild, 
                        current_page+1, 
                        page_count
                    ))
                    del data["files"]
                    await message.edit(**data)
                    
            
    async def on_command(self, ctx: "Context"):
        await self.db.execute(
            "INSERT INTO command_usage (user_id, command_name, uses) VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE uses = uses+1;",
            ctx.author.id, ctx.command.qualified_name
        )
        
    
    async def on_command_error(self, ctx: "Context", error: Any):
        await self.wait_until_ready()
        
        if type(error) in (
            commands.NotOwner, 
            commands.CheckFailure,
            AssertionError
        ):
            return
            
        if isinstance(error, commands.CommandNotFound):
            if ctx.guild.id in self.cache.aliases:
                for command, aliases in self.cache.aliases[ctx.guild.id].items():
                    for alias in aliases:
                        if alias.lower() in ctx.message.content.lower():
                            ctx.message.content = ctx.message.content.replace(alias, command)
                            context = await self.get_context(ctx.message)
                            try:
                                await self.invoke(context)
                            except Exception:
                                pass
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            permission = error.missing_permissions[0].lower().replace("_", " ").title()
            return await ctx.error(f"I'm missing the **{permission}** permission.")

        if isinstance(error, commands.MissingPermissions):
            permission = error.missing_permissions[0].lower().replace("_", " ").title()
            return await ctx.error(f"You're missing the **{permission}** permission.")

        if isinstance(error, commands.CommandOnCooldown):
            if await self.cache.ratelimited(f"rl:cooldown_message{ctx.author.id}", 1, error.retry_after):
                return
            
            return await ctx.error(
                    f"You're on a [**cooldown**](https://discord.com/developers/docs/topics/rate-limits) & cannot use `{ctx.invoked_with}` for **{fmtseconds(error.retry_after)}**.",
                    delete_after=error.retry_after
                )

        if isinstance(error, commands.MemberNotFound):
            return await ctx.error("Please provide a **valid** member.")

        if isinstance(error, commands.UserNotFound):
            return await ctx.error("Please provide a **valid** user.")

        if isinstance(error, commands.ChannelNotFound):
            return await ctx.error("Please provide a **valid** channel.")

        if isinstance(error, commands.RoleNotFound):
            return await ctx.error("Please provide a **valid** role.")

        if isinstance(error, commands.EmojiNotFound):
            return await ctx.error("Please provide a **valid** emoji.")

        if isinstance(error, commands.GuildNotFound):
            return await ctx.error("Please provide a **valid** guild.")

        if isinstance(error, commands.BadInviteArgument):
            return await ctx.error("Please provide a **valid** invite.")

        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, SendHelp):
            return await ctx.send_help(ctx.command.qualified_name)

        if isinstance(error, commands.BadArgument):
            return await ctx.error(
                multi_replace(
                    error.args[0].lower(), {
                        '"': "**", 
                        "int": "number", 
                        "str": "text"
                    }
                )[:-1].capitalize(), 
                delete_after=10
            )

        if isinstance(error, commands.BadUnionArgument):
            return await ctx.error(
                multi_replace(
                    error.args[0].lower(), {
                        '"': "**", 
                        "into": "into a", 
                        "member": "**member**", 
                        "user": "**user**"
                    }
                )[:-1].capitalize(),
                delete_after=10
            )
            
        if isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.error(f"This command can only be ran {error.number} time{'s' if error.number > 1 else ''} concurrently {'globally' if error.per.name == 'default' else f'per {error.per.name}'}.")

        error_code = tuuid.tuuid()
        self.cache.errors[error_code] = {
            "guild": ctx.guild,
            "command": ctx.command,
            "user": ctx.author,
            "error": error
        }
            
        return await ctx.error(f"**{ctx.command.qualified_name}** raised an unexpected error ([**{error_code}**](https://discord.gg/vilebot))")
            
            
class TempFile:
    def __init__(
        self, 
        input: bytes = b"", 
        directory: str = "/tmp", 
        extension: str = "txt", 
        return_type: Literal["path", "filename", "object", "file", "buffer"] = "path"
    ) -> None:
        self.input = input
        self.directory = directory
        self.extension = extension
        self.path = ""
        self.file = None
        self.return_type = return_type


    async def create(self) -> Any:
        """Create a temporary file"""
        
        self.path = f"{self.directory}/{tuuid.tuuid()}.{self.extension}"
        file = await aiofiles.open(self.path, mode="wb+")
        await file.write(self.input)
        self.file = file
        return file


    async def delete(self) -> None:
        """Delete the temporary file we created"""
        if self.file.closed is False:
            await self.file.close()
        return os.remove(self.path)
        
        
    async def __aenter__(self) -> Any:
        """Create a temporary file"""
        
        self.path = f"{self.directory}/{tuuid.tuuid()}.{self.extension}"
        async with aiofiles.open(self.path, mode="wb+") as file:
            await file.write(self.input)
            self.file = file
            
        return self.output()
        
        
    async def __aexit__(self, *_) -> None:
        """Delete the temporary file we created"""
        if self.file.closed is False:
            await self.file.close()
        return os.remove(self.path)
        
        
    def output(self) -> str:
        """Return the file's path, the File object or the buffer"""
        
        assert self.return_type in (
            "path", "filename", 
            "object", "file", 
            "buffer"
        ), "Invalid return type."
        
        if self.return_type in ("path", "filename"):
            return self.path
        
        if self.return_type in ("object", "file"):
            return self.file
            
        if self.return_type == "buffer":
            return self.buffer
        
        
    def __repr__(self) -> str:
        return self.path
    
    
    __str__ = __repr__
    
    
def multi_replace(text: str, to_replace: Dict[str, str], once: bool = False) -> str:
    """Replace multiple keywords in a string"""
    
    for r1, r2 in to_replace.items():
        if r1 in text:
            if once:
                text = text.replace(str(r1), str(r2), 1)
            else:
                text = text.replace(str(r1), str(r2))
            
    return text


def get_parts(code: str):
    """Get the parts needed to parse an embed script"""
    params = code.replace('{embed}', '')
    return tuple(p[1:][:-1] for p in params.split('$v'))
    

class ParsedEmbed:
    def __init__(self, validator, code: str) -> None:
        self.validator = validator
        self.code = code
        
    
    async def send(self, destination: Any, bot: "VileBot", guild: discord.Guild, channel: discord.TextChannel, user: discord.Member, moderator: Optional[discord.Member] = None, extras: Optional[dict] = None, context: Optional["Context"] = None, strip_text_of_flags: bool = False) -> Optional[discord.Message]:
        """Send the embed"""
        
        code = self.code
        if context and strip_text_of_flags is True:
            code = strip_flags(code, context.parameters)
            
        data = await self.validator.to_embed(code=await embed_replacement(
            code,
            member=user,
            guild=guild,
            moderator=moderator
        ))
        if isinstance(destination, discord.Webhook):
            del data["delete_after"]
            
        if extras and isinstance(extras, dict):
            data |= extras
            
        try:
            return await destination.send(**data)
        except Exception:
            await channel.send(traceback.format_exc())
            if isinstance(destination, Context):
                await destination.error("The embed script syntaxing you provided **is incorrect**.")
                

class EmbedScriptValidator(commands.Converter):
    async def convert(self, ctx: "Context", argument: str) -> ParsedEmbed:
        """Check if the syntaxing is valid and return the parsed embed"""
        
        embed_dict = await self.to_embed(argument)
        if embed_dict is None:
            return await ctx.error("The embed script syntaxing you provided **is incorrect**.")
            
        return ParsedEmbed(self, argument)
        

    async def to_embed(self, code: str) -> Optional[dict]:
        """Return the JSON of a parsed embed"""
        
        embed = {}
        files = []
        fields = []
        content = None
        timestamp = None
        delete = None
        view = discord.ui.View()

        for part in get_parts(code):
            
            if part.startswith("content:"):
                content = part[len("content:"):]

            elif part.startswith("url:"):
                embed["url"] = part[len("url:"):]

            elif part.startswith("title:"):
                embed["title"] = part[len("title:"):]

            elif part.startswith("delete:"):
                if part[len("delete:"):].strip().isdigit():
                    delete = int(part[len("delete:"):].strip())

            elif part.startswith("description:"):
                embed["description"] = part[len("description:"):]

            elif part.startswith("footer:"):
                embed["footer"] = {"text": part[len("footer:"):]}

            elif part.startswith("color:"):
                try:
                    embed["color"] = int(part[len("color:"):].strip().strip("#"), 16)
                except Exception:
                    pass

            elif part.startswith("image:"):
                embed["image"] = {"url": part[len("image:"):]}

            elif part.startswith("thumbnail:"):
                embed["thumbnail"] = {"url": part[len("thumbnail:"):]}

            elif part.startswith('attach:'):
                files.append(
                    discord.File(
                        BytesIO(await HTTP(proxy=True).read(part[len("attach:"):].strip())), 
                        yarl.URL(part[len("attach:"):].strip()).name
                    )
                )

            elif part.startswith("author:"):
                part = part[len("author:"):].split(" && ")
                icon_url = None
                url = None

                embed["author"] = {"name": part and part[0]}
                for part in part[1:]:
                    if part.startswith("icon:"):
                        part = part[len("icon:"):]
                        icon_url = part.strip()
                    
                    elif p.startswith("url:"):
                        part = part[len("url:"):]
                        url = part.strip
                        

                if icon_url:
                    embed["author"]["icon_url"] = icon_url
                
                if url:
                    embed["author"]["url"] = url

            elif part.startswith("field:"):
                part = part[len("field:"):].split(" && ")
                value = None
                inline = "true"
                
                name = part and part[0]
                for part in part[1:]:
                    if part.startswith("value:"):
                        value = part[len("value:"):]
                    
                    elif p.startswith("inline:"):
                        inline = part[len("inline:"):].strip()
            
                if isinstance(inline, str):
                    if inline == "true":
                        inline = True

                    elif inline == "false":
                        inline = False

                fields.append({"name": name, "value": value, "inline": inline})

            elif part.startswith("footer:"):
                part = part[len("footer:"):].split(" && ")
                text = None
                icon_url = None
                for part in part[1:]:
                    if part.startswith("icon:"):
                        icon_url = part[len("icon:"):].strip()
                
                embed["footer"] = {"text": part and part[0]}
                if icon_url:
                    embed["footer"]["icon_url"] = icon_url

            elif part.startswith("label:"):
                part = part[len("label:"):].split(' && ')
                label = "no label"
                url = None
                for part in part[1:]:
                    if part.startswith("link:"):
                        url = part[len("link:"):].strip()
                    
                label = part and part[0]
                view.add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link, 
                        label=label, 
                        url=url
                    )
                )
            
            elif part.startswith("image:"):
                part = part[len("image:"):]
                embed["image"] = {'url': part}
            
            elif part.startswith("timestamp:"):
                part = part[len("timestamp:"):].strip()
                if part == "true":
                    timestamp = True
                
        if not embed:
            embed = None
                
        else:
            embed["fields"] = fields
            embed = discord.Embed.from_dict(embed)

        if not code.count("{") and not code.count("}"):
            content = code
        
        if timestamp:
            embed.timestamp = datetime.now(pytz.timezone("America/New_York"))

        embed_dict = {"content": content, "embed": embed, "files": files, "view": view, "delete_after": delete}
        if not embed_dict["content"] and not embed_dict["embed"] and not embed_dict["files"] and not len(embed_dict["view"].children):
            return None
            
        return embed_dict
        
        
INCREMENT_SCRIPT = b"""
    local current
    current = tonumber(redis.call("incrby", KEYS[1], ARGV[2]))
    if current == tonumber(ARGV[2]) then
        redis.call("expire", KEYS[1], ARGV[1])
    end
    return current
"""
INCREMENT_SCRIPT_HASH = hashlib.sha256(INCREMENT_SCRIPT).hexdigest()


class VileRedis(Redis):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        
    async def __aenter__(self) -> Self:
        return await self.init()
        
        
    async def __aexit__(self, *_: Any) -> None:
        return await self.close()
        
        
    @classmethod
    async def init(cls, host: str = "localhost", port: int = 6379) -> Self:
        return cls(
            host=host,
            port=port,
            decode_responses=False
        )
        
        
    async def cache(self, key: Union[str, bytes, memoryview], value: Optional[Union[str, bytes, memoryview]] = None, namespace: Optional[str] = None, ex: int = 3600) -> str:
        """Cache or retrieved the cached value for a key"""
        
        key = f"{namespace}:{hash(key)}" if namespace else hash(key)
        if (cached_value := await self.get(key.encode())) is not None:
            return cached_value
            
        if value is None:
            return None
            
        await self.set(key.encode(), value, ex=ex)
        return value
    
    
    async def ratelimited(self, resource_ident: str, request_limit: int, timespan: int = 60, increment: int = 1) -> bool:
        
        ratelimit_key = f"rl:{xxhash.xxh3_64_hexdigest(resource_ident)}"
        try:
            current_usage = await self.evalsha(INCREMENT_SCRIPT_HASH, 1, ratelimit_key, timespan, increment)
        except Exception:
            current_usage = await self.eval(INCREMENT_SCRIPT, 1, ratelimit_key, timespan, increment)
        
        if int(current_usage) > request_limit:
            return True
            
        return False
        
        
class RoleConverter(commands.RoleConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[discord.Role]:    
        try:
            return await super().convert(ctx, argument)
        except commands.RoleNotFound:
            if (role := ctx.find_role(argument)) is not None:
                return role
            raise commands.RoleNotFound(argument)
        
        
class EmojiConverter(commands.EmojiConverter):
    async def convert(self, ctx: "Context", argument: str) -> Union[discord.Emoji, str]:    
        try:
            return await super().convert(ctx, argument)
        except commands.EmojiNotFound:
            try:
                unicodedata.name(argument)
            except Exception:
                raise commands.EmojiNotFound(argument)
            else:
                return argument
                
                
class MessageConverter(commands.MessageConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[discord.Message]:    
        
        if len(list(filter(lambda r: f"invalid_id{ctx.guild.id}" in r, ctx.bot.cache._rl))) >= 15:
            return await ctx.error("This resource is being rate limited.")
            
        if argument.isdigit():
            id = int(argument)
            if ctx.bot.cache.is_ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}"):
                raise commands.MessageNotFound(argument)
                
            if len(argument) not in (16, 17, 18, 19, 20):
                await ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise commands.MessageNotFound(argument)
                
            try:
                return await super().convert(ctx, argument)
            except Exception:
                await ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise commands.MessageNotFound(argument)
                
        return await super().convert(ctx, argument)
        
        
class MemberConverter(commands.MemberConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[discord.Member]:    
        
        if len(list(filter(lambda r: f"invalid_id{ctx.guild.id}" in r, ctx.bot.cache._rl))) >= 15:
            return await ctx.error("This resource is being rate limited.")
            
        if argument.isdigit():
            id = int(argument)
            if ctx.bot.cache.is_ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}"):
                raise commands.MemberNotFound(argument)
                
            if len(argument) not in (16, 17, 18, 19, 20):
                await ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise commands.MemberNotFound(argument)
                
            try:
                return await super().convert(ctx, argument)
            except Exception:
                await ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise commands.MemberNotFound(argument)
                
        return await super().convert(ctx, argument)
        
    
class UserConverter(commands.UserConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[discord.User]:    
        
        if len(list(filter(lambda r: f"invalid_id{ctx.guild.id}" in r, ctx.bot.cache._rl))) >= 15:
            return await ctx.error("This resource is being rate limited.")
            
        if argument.isdigit():
            id = int(argument)
            if ctx.bot.cache.is_ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}"):
                raise commands.UserNotFound(argument)
                
            if len(argument) not in (16, 17, 18, 19, 20):
                await ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise commands.UserNotFound(argument)
                
            try:
                return await super().convert(ctx, argument)
            except Exception:
                await ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise commands.UserNotFound(argument)
                
        return await super().convert(ctx, argument)
        
        
class Timespan(commands.Converter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[Duration]:
        ret = Duration(argument)
        if not ret.seconds and argument not in ("0", "0 seconds", "0s", "0h", "0w", "0m", "0 hours", "0 weeks"," 0 months", "0 hours"):
            raise SendHelp()
            
        return ret

        
async def spotify_token() -> str:
    
    if cached_value := await CACHE.get("spotifytoken"):
        return cached_value
        
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://accounts.spotify.com/api/token", 
            data={
                "grant_type": "client_credentials"
            },
            auth=aiohttp.BasicAuth(
                "48eae30513e74f779e65a1e5d37d2421", 
                "3a5ccde745494af6911887f391ced0a5"
            )
        ) as resp:
            data = await resp.json()
            spotify_token = data["access_token"]
            await CACHE.set("spotifytoken", spotify_token, expiration=3600)
            return spotify_token
        
        
async def dominant_color(source: Union[discord.Asset, str, bytes], proxy: bool = False) -> int:
    """Extract the most dominant color of an image"""
    
    if isinstance(source, discord.Asset):
        source = source.url
    
    if isinstance(source, bytes):
        if (color := await CACHE.get(f"imagecolor{hash(source)}")) is not None:
            return 
            
        resp = source
        
    else:
        resp = await HTTP(proxy=proxy).read(source)
    
    image_hash = hash(resp)
    img = Image.open(BytesIO(resp))
    img.thumbnail((32, 32))
    
    if (color := await CACHE.get(f"imagecolor{image_hash}")) is not None:
        return color
        
    colors = colorgram.extract(img, 1)
    color = discord.Color.from_rgb(*colors[0].rgb).value
    await CACHE.set(f"inagecolor{image_hash}", color)
    
    return color
            
            
def find_emojis(text: str) -> list:
    """Find every emoji in a message"""
    return regex.custom_emoji.findall(text) + regex.unicode_emoji.findall(text)
    
    
def find_invites(text: str) -> list:
    """Find every invite in a message"""
    return regex.discord_invite.findall(text)
    
    
class AttachmentConverter(commands.Converter):
    async def convert(self, ctx: "Context", argument: Optional[str] = None) -> Optional[str]:
        
        if links := regex.link.findall(argument):
            return links[0]
        
        if not argument:
            async for message in ctx.channel.history(limit=50):
                if message.attachments:
                    return message.attachments[0].url
                    
        await ctx.send_help(ctx.command.qualified_name)
        raise SendHelp()

    
class HexConverter(commands.Converter):
    async def convert(self, ctx: "Context", argument: Optional[str] = None) -> Optional[str]:
        
        try:
            hex(int(argument))
            return int(argument)
        except:
            try:
                return int(argument.strip("#"), 16)
            except:
                pass

        raise SendHelp()
        

async def screenshot(url: str) -> BytesIO:
    """Screenshot a web page"""
    
    async def _screenshot():
        browser = await pyppeteer.launch({
            "executablePath": "/usr/bin/google-chrome",
            "args": [
                "--ignore-certificate-errors",
                "--disable-extensions",
                "--proxy-server=http://p.webshare.io:80/"
                "--no-sandbox",
                "--headless"
            ]
        })

        page = await browser.newPage()
        await page.setViewport({"width": 1920, "height": 1080})
        await page.authenticate({"username": "yjxaasab-rotate", "password": "n6hhdcqoywub"})
        await page.goto(url, {"waitUntil": "networkidle0"})
    
        ret = await page.screenshot()
        await browser.close()
        return ret
        
    if "?" not in url:
        if (cached_value := await CACHE.get(f"screenshot-{url}")) is not None:
            return BytesIO(cached_value)
            
        ret = await _screenshot()
        await CACHE.set(f"screenshot-{url}", ret, expiration=3600)
        return BytesIO(ret)
    
    return BytesIO(await _screenshot())
            
            
async def eval_bash(script: str, decode: bool = False) -> Optional[str]:
    """Evaluate a bash script and return the output"""
    
    process = await asyncio.create_subprocess_shell(
        script,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    result, err = await process.communicate()
    
    if err:
        raise Exception(err.decode("utf-8").replace("\n", "\n"))
        
    ret = result.decode() if decode else result
    return ret
    
    
async def eval_javascript(script: str) -> Optional[str]:
    """Evaluate JavaScript and return the output"""
    
    async with TempFile(script.encode(), extension="js") as file:
        return await eval_bash(f"node {file}", decode=True)
        
        
async def eval_lolcode(script: str) -> Optional[str]:
    """Evaluate a LolCode script and return the output"""
    
    async with TempFile(script.encode(), extension="lol") as file:
        return await eval_bash(f"lci {file}", decode=True)
        
        
async def eval_rust(script: str) -> Optional[str]:
    """Evaluate a Rust script and return the output"""
    
    async with TempFile(script.encode(), input_type="bytes", extension="rs") as file:
        await eval_bash(f"rustc {file}")
        other_file = file.split("/")[-1][:-3]
        ret = await eval_bash(f"./{other_file}", decode=True)
        os.remove(f"./{other_file}")
        return ret


def has_permissions(**perms: bool) -> Any:

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    async def predicate(ctx: "Context") -> Optional[bool]:
        
        author_roles = list(map(lambda r: r.id, ctx.author.roles))
        fake_permissions = []
        
        if ctx.bot.cache.fake_permissions.get(ctx.guild.id):
            fake_permissions = tuple(
                list(p)[0] for p in list(map(
                    lambda r: ctx.bot.cache.fake_permissions[ctx.guild.id][r], 
                    (r for r in ctx.bot.cache.fake_permissions[ctx.guild.id] if r in author_roles if ctx.bot.cache.fake_permissions[ctx.guild.id][r])
                ))
            )

        for perm, _ in perms.items():
            if (getattr(ctx.author.guild_permissions, perm) is True) or (perm in set(fake_permissions)):
                return True

        raise commands.MissingPermissions([perm])

    return commands.check(predicate)
    
    
def is_guild_owner() -> Any:
    async def predicate(ctx: "Context") -> bool:
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.error("You're missing the **Server Owner** permission.")
            return False
            
        return True
        
    return commands.check(predicate)
    
    
class DataProcessing:
    def __init__(self) -> None:
        self.API_KEY = constants.api.apininjas
        self.BASE_URL = "https://api.api-ninjas.com/v1"
        
    async def _request(self, method: str, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None) -> dict:
        """Make a request to the provided endpoint"""
        
        if method == "GET":
            method = HTTP(proxy=False).get(
                f"{self.BASE_URL}/{endpoint}", 
                params=params, 
                headers={
                    "X-Api-Key": self.API_KEY
                }
            )
        
        elif method == "POST":
            method = HTTP(proxy=False).post_json(
                f"{self.BASE_URL}/{endpoint}", 
                data=data,
                params=params,
                headers={
                    "X-Api-Key": self.API_KEY
                }
            )
            
        return await method
        
        
    async def image_to_text(self, source: Union[str, bytes]) -> Optional[str]:
        """Extract text from an image"""
        
        if isinstance(source, str):
            source = await HTTP(proxy=True).read(source)

        if cached_text := await CACHE.get(f"ocr-{hash(source)}"):
            return cached_text
        
        data = await self._request(
            "POST", 
            "imagetotext",
            data={
                "image": source
            }
        )
        if not data or isinstance(data, dict):
            return None
        
        ret = []
        previous_y2 = None

        for entry in data:
            text = entry["text"]
            bounding_box = entry["bounding_box"]
            current_y1 = bounding_box["y1"]
            
            if previous_y2 is not None and current_y1 > previous_y2:
                ret.append("\n")

            ret.append(text.strip())
            previous_y2 = bounding_box["y2"]

        if isinstance(source, bytes):
            await CACHE.set(f"ocr-{hash(source)}", " ".join(ret))
            
        return " ".join(ret)
        

    async def timezone(self, city: str) -> Optional[str]:
        """Get the timezone of the provided city"""
        
        if city in pytz.all_timezones:
            return city

        if cached_timezone := await CACHE.get(f"timezone-{city}"):
            return cached_timezone
            
        data = await self._request(
            "GET", 
            "timezone",
            params={
                "city": city
            }
        )

        if data.get("error"):
            return None
        
        await CACHE.set(f"timezone-{city}", data["timezone"])
        return data["timezone"]
        
        
    async def weather(self, city: str) -> Optional[dict]:
        """Get the weather data of the provided city"""

        if cached_weather := await CACHE.get(f"weather-{city}"):
            return cached_weather
            
        data = await self._request(
            "GET", 
            "weather",
            params={
                "city": city
            }
        )

        if data.get("error"):
            return None
        
        await CACHE.set(f"weather-{city}", data["timezone"], expiration=3600)
        return data
        
        
image_to_text = DataProcessing().image_to_text
timezone = DataProcessing().timezone
weather = DataProcessing().weather
    
        
class RivalAPI:
    def __init__(self) -> None:
        self.API_KEY = os.environ.get("RIVAL_API_KEY")


async def identify_song(source: Union[str, bytes]) -> Optional[dict]:
    """Identify a song from an audio or video file"""
    
    if isinstance(source, str):
        source = await HTTP(proxy=True).read(source)
        
    data = await Shazam().recognize_song(source)
    return data.get("track")
    
    
def background_reader(stream: IO[bytes], loop: AbstractEventLoop, callback: Callable[[bytes], Any]) -> None:
    for line in iter(stream.readline, bytes):
        loop.call_soon_threadsafe(loop.create_task, callback(line))


class ShellReader:
    def __init__(
        self,
        code: str,
        timeout: int = 120,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        escape_ansi: bool = True
    ) -> None:
        
        self.escape_ansi = escape_ansi
        self.process = subprocess.Popen(["/bin/bash", "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.close_code = None
        self.loop = loop or asyncio.get_event_loop()
        self.timeout = timeout
        self.stdout_task = self.make_reader_task(self.process.stdout, self.output_handler) if self.process.stdout else None
        self.stderr_task = self.make_reader_task(self.process.stderr, self.output_handler) if self.process.stderr else None
        self.queue = asyncio.Queue(maxsize=250)


    @property
    def closed(self) -> bool:
        return (not self.stdout_task or self.stdout_task.done()) and (not self.stderr_task or self.stderr_task.done())


    async def executor_wrapper(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        return await self.loop.run_in_executor(None, func, *args, **kwargs)


    def make_reader_task(self, stream: IO[bytes], callback: Callable[[bytes], Any]):
        return self.loop.create_task(self.executor_wrapper(background_reader, stream, self.loop, callback))


    ANSI_ESCAPE_CODE = re.compile(r"\x1b\[\??(\d*)(?:([ABCDEFGJKSThilmnsu])|;(\d+)([fH]))")


    def clean_bytes(self, line: bytes) -> str:
        text = line.decode("utf-8").replace("\r", "").strip("\n")
        
        def sub(group: Match[str]):
            return group.group(0) if group.group(2) == "m" and not self.escape_ansi else ""

        return self.ANSI_ESCAPE_CODE.sub(sub, text).replace("``", "`\u200b`").strip("\n")


    async def output_handler(self, line: bytes) -> None:
        await self.queue.put(self.clean_bytes(line))
        
        
    def __enter__(self) -> Self:
        return self
        

    def __exit__(self, *_) -> None:
        self.process.kill()
        self.process.terminate()
        self.close_code = self.process.wait(timeout=0.5)

    
    def __aiter__(self) -> Self:
        return self
        

    async def __anext__(self) -> Optional[str]:
        last_output = time.perf_counter()
        while not self.closed or not self.queue.empty():
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1)
            
            except asyncio.TimeoutError as exception:
                if time.perf_counter() - last_output >= self.timeout:
                    raise exception
            
            else:
                last_output = time.perf_counter()
                
                if not item:
                    raise StopAsyncIteration()
                    
                return item

        raise StopAsyncIteration()
