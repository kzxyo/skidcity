from asyncio import AbstractEventLoop
from asyncio import TimeoutError as AsyncTimeoutError
from async_timeout import timeout as Timeout

from asyncio import (
    create_subprocess_shell, 
    ensure_future, 
    gather,
    get_event_loop, 
    Lock,
    Semaphore,
    sleep,
    wait_for
)

from typing import (
    Any, 
    Callable,
    Dict, 
    Sequence, 
    List, 
    Literal, 
    Optional,
    Tuple, 
    Union
)

from base64 import b64encode, b64decode
from cashews import Cache
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from datetime import datetime as Date, timedelta
from difflib import get_close_matches
from functools import partial
from hashlib import sha256
from inspect import currentframe
from io import BytesIO, StringIO
from logging import getLogger
from os import environ, remove, sep, getcwd
from os.path import normpath
from pathlib import Path, PosixPath
from pydub import AudioSegment
from random import choice, randrange, shuffle
from re import Pattern
from socket import AF_INET
from subprocess import PIPE


from aiohttp import (
    AsyncResolver, 
    BasicAuth, 
    ClientConnectorError, 
    ContentTypeError, 
    ClientSession, 
    TCPConnector
)

from aiohttp.web_exceptions import HTTPError
from aiohttp import ClientResponseError

from aiomysql import (
    create_pool,
    Pool
)

from cryptography.fernet import Fernet

from discord import (
    Activity,
    ActivityType,
    AllowedMentions, 
    Asset, 
    ButtonStyle, 
    Color as BaseColor, 
    Embed, 
    Emoji as BaseEmoji, 
    File, 
    Forbidden, 
    Guild, 
    GuildSticker, 
    Intents, 
    Interaction, 
    Member as BaseMember, 
    Message as BaseMessage, 
    NotFound, 
    Permissions, 
    Role,
    TextChannel, 
    User as BaseUser, 
    VoiceChannel,
    Webhook
)

from discord.abc import GuildChannel
from discord.errors import HTTPException

from discord.ext.commands import (
    Bot, #AutoShardedBot,
    BadArgument, 
    BadBoolArgument, 
    BadInviteArgument, 
    BadUnionArgument,
    BotMissingPermissions, 
    ChannelNotFound,
    CheckFailure, 
    Command, 
    CommandError, 
    CommandInvokeError,
    CommandNotFound,
    CommandOnCooldown, 
    Context, 
    Converter,
    EmojiConverter as _EmojiConverter,
    EmojiNotFound, 
    Group, 
    GuildNotFound,
    GuildStickerConverter, 
    GuildStickerNotFound,
    HelpCommand as BaseHelpCommand, 
    MaxConcurrencyReached,
    MemberConverter as _MemberConverter,
    MemberNotFound,
    MessageConverter as _MessageConverter,
    MessageNotFound, 
    MissingPermissions,
    MissingRequiredArgument, 
    NotOwner,
    RoleConverter as _RoleConverter,
    RoleNotFound,
    UserConverter as _UserConverter,
    UserNotFound, 
    check, 
    when_mentioned_or
)

from bs4 import BeautifulSoup
from copy import copy
from discord.ui import Button, View
from discord.utils import format_dt, oauth_url, cached_property
from durations_nlp import Duration
from http import HTTPStatus
from humanize import naturaldelta
from matplotlib.colors import cnames
from munch import Munch
from PIL import Image, ImageDraw
from pydantic import BaseModel
from pyppeteer import launch
from pyppeteer.browser import Browser as BaseBrowser
from pyppeteer.page import Page
from pytz import all_timezones, timezone as Timezone
from redis.asyncio import Redis
from sys import getsizeof, stdout, exc_info
from traceback import format_exc, print_exc
from typing_extensions import Self, NoReturn
from watchfiles import Change, awatch
from xxhash import xxh3_64_hexdigest as hash
from yarl import URL

from loguru import logger
from utilities import expressions, literals, models
from utilities.paginator import Paginator, FieldPaginator, text_creator
from utilities.views import Confirmation

import arrow
import colorgram
import imghdr
import itertools
import jishaku
import langcodes
import orjson
import traceback
import tuuid
import unicodedata
import urllib
import re

fernet = Fernet(literals.keys.fernet)

TUPLE = ()
DICT = { }
GLOBAL = Munch()

(Cache := Cache()).setup("redis://")


class BetterList(list):
    def first(self: "BetterList") -> Any:
        return self[0]

    
    def first(self: "BetterList") -> Any:
        return self[0]

    
    def shuffle(self: "BetterList") -> "BetterList":
        shuffle(self)
        return self


    def random(self: "BetterList") -> Any:
        return choice(self)


class HelpCommand(BaseHelpCommand):
    def extra_params(self: "HelpCommand", command: Command) -> str:
        if not command.parameters:
            return "None"
        
        lines = "\n".join((
            f"{'--' if config.get('require_value', True) else '-'}{parameter}[{'|'.join(config.get('aliases', TUPLE))}] - {config.get('description', 'None')}"
            for parameter, config in command.parameters.items()
        ))

        return f"```\n{lines}```"
        
        
    async def send_bot_help(self: "HelpCommand", mapping: Any) -> Optional[BaseMessage]:
        """
        Send the default command menu
        """
        
        ctx = self.context

        cogs = sorted(
            (
                cog for cog in ctx.bot.cogs.values()
                if cog.get_commands() and not getattr(cog, "hidden", False)
            ), 
            key=lambda cog: cog.qualified_name
        )

        cog_count = len(cogs)

        embeds = [(
            Embed(color=ctx.bot.color)
            .set_author(
                name=f"{ctx.bot.user.name.title()} Command Menu", 
                icon_url=ctx.bot.user.display_avatar
            )
            .add_field(
                name=f"{ctx.bot.dash} Need to Know",
                value=f"> [ ] = optional, <> = required\n> Important commands have slash versions",
            )
            .add_field(
                name=f"{ctx.bot.dash} Directory",
                value=f"> [**Invite**]({ctx.bot.invite}) \u2022 [**Support**](https://discord.gg/KsfkG3BZ4h) \u2022 [**Web**](https://github.com/treyt3n/vile)\n> [**Donate**](https://cash.app/$vilebot) \u2022 [**Business**](https://discord.com/users/1109861649910874274) \u2022 [**Other**](https://vileb.org)",
                inline=False,
            )
            .set_thumbnail(url=ctx.bot.user.display_avatar)
            .set_footer(text=f"Page 1 / {cog_count+1} ({sum(1 for _ in ctx.bot.walk_commands())} commands)")
        )]

        embeds.extend(
            (
                Embed(
                    color=ctx.bot.color,
                    title=f"Category: {cog.qualified_name}",
                    description=f"```{', '.join(cmd.name + ('*' if isinstance(cmd, Group) else '') for cmd in cog.get_commands())}```",
                )
                .set_author(
                    name=f"{ctx.bot.user.name.title()} Command Menu", 
                    icon_url=ctx.bot.user.display_avatar
                )
                .set_footer(text=f"Page {index} / {cog_count+1}  ({sum(1 for _ in cog.walk_commands())} commands)")
            )
            for index, cog in enumerate(cogs, start=2)
        )
        
        return await ctx.paginate(embeds)
        

    async def send_command_help(self: "HelpCommand", command: Command) -> Optional[BaseMessage]:
        """
        Send the help menu for a command
        """
            
        ctx = self.context

        embed = (
            Embed(
                color=ctx.bot.color, 
                title=f"Command: {command.qualified_name}",
                description=f"> {command.callback.__doc__.strip() if command.name != 'help' else 'Show this interface'}" if command.callback.__doc__ else None
            )
            .set_author(
                name=f"{ctx.bot.user.name.title()} Help Menu", 
                icon_url=ctx.bot.user.display_avatar
            )
            .add_field(
                name="<:v_slash:1067034025895665745> Parameters",
                value=", ".join(key.strip("_") for key in command.clean_params.keys()) or "None"
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
                value=f"```ruby\nSyntax: {ctx.prefix}{command.qualified_name} {command.usage or ''}\nExample: {ctx.prefix}{command.qualified_name} {command.example or ''}\n```" if command.usage or command.example else "```No syntax has been set for this command.```",
                inline=False
            )
            .set_footer(text=f"Module: {command.cog_name}   \u2022   Aliases: {', '.join(command.aliases) or 'None'}")
        )
        
        return await ctx.reply(embed=embed)


    async def send_group_help(self: "HelpCommand", group: Group) -> Optional[BaseMessage]:
        """
        Send the help menu for a group command
        """
        
        ctx = self.context
        _commands = sorted(
            group.walk_commands(),
            key=lambda command: command.qualified_name
        )
        
        embeds = [(
            Embed(
                color=ctx.bot.color, 
                title=f"Group Command: {group.qualified_name}",
                description=f"> {group.callback.__doc__.strip()}" if group.callback.__doc__ else None
            )
            .set_author(
                name=f"{ctx.bot.user.name.title()} Help Menu", 
                icon_url=ctx.bot.user.display_avatar
            )
            .add_field(
                name="<:v_slash:1067034025895665745> Parameters",
                value=", ".join(key.strip("_") for key in group.clean_params.keys()) or "None"
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
                value=f"```ruby\nSyntax: {ctx.prefix}{group.qualified_name} {group.usage or ''}\nExample: {ctx.prefix}{group.qualified_name} {group.example or ''}\n```" if group.usage or group.example else "```No syntax has been set for this command.```",
                inline=False
            )
            .set_footer(text=f"Page 1 / {len(_commands)+1}   \u2022   Module: {group.cog_name}   \u2022   Aliases: {', '.join(group.aliases) or None}")
        )]
        
        embeds.extend(
            (
                Embed(
                    color=ctx.bot.color, 
                    title=f"{'Group ' if isinstance(command, Group) else ''}Command: {command.qualified_name}",
                    description=f"> {command.callback.__doc__.strip()}" if command.callback.__doc__ else None
                )
                .set_author(
                    name=f"{ctx.bot.user.name.title()} Help Menu", 
                    icon_url=ctx.bot.user.display_avatar
                )
                .add_field(
                    name="<:v_slash:1067034025895665745> Parameters",
                    value=", ".join(key.strip("_") for key in command.clean_params.keys()) or "None"
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
                    value=f"```ruby\nSyntax: {ctx.prefix}{command.qualified_name} {command.usage or ''}\nExample: {ctx.prefix}{command.qualified_name} {command.example or ''}\n```" if command.usage or command.example else "```No syntax has been set for this command.```",
                    inline=False
                )
                .set_footer(text=f"Page {index} / {len(_commands)+1}   \u2022   Module: {command.cog_name}   \u2022   Aliases: {', '.join(command.aliases) or None}")
            )
            for index, command in enumerate(_commands, start=2)
        )
            
        return await ctx.paginate(embeds)
        

    async def on_help_command_error(self: "HelpCommand", _: None, error: Exception) -> NoReturn:
        raise


def ordinal(number: int) -> str:
    """
    Format a number
    """
    
    return "%d%s" % (
        number, 
        "tsnrhtdd"[(number // 10 % 10 != 1) * (number % 10 < 4) * number % 10 :: 4]
    )
    
    
def fmtseconds(seconds: Union[ int, float ], unit: str = "microseconds") -> str:
    """
    Format time using seconds
    """

    return naturaldelta(
        timedelta(seconds=seconds), 
        minimum_unit=unit
    )
    
    
def encrypt(key: Any) -> str:
    """
    Encrypt an object using Fernet
    """
    
    return fernet.encrypt(str(key).encode()).decode()
    

def decrypt(key: Any) -> str:
    """
    Decrypt an object using Fernet
    """
    
    return fernet.decrypt(str(key).encode()).decode()
    
    
class ParameterParser:
    def __init__(self: "ParameterParser", ctx: "Context") -> NoReturn:
        self.context = ctx


    def get(
        self: "ParameterParser", 
        parameter: str, 
        **kwargs: Dict[ str, Any ]
    ) -> Any:

        sliced = self.context.message.content.split()

        for parameter in (parameter, *kwargs.get("aliases", TUPLE)):
            if kwargs.get("require_value", True) is False:
                if f"-{parameter}" not in sliced:
                    return kwargs.get("default", None)

                return True

            try:
                index = sliced.index(f"--{parameter}")
            
            except ValueError:
                return kwargs.get("default", None)
            
            result = [ ]
            for word in sliced[index+1:]:
                if word.startswith("-"):
                    break
                
                result.append(word)

            if not (result := " ".join(result).replace("\\n", "\n").strip()):
                return kwargs.get("default", None)
            
            if choices := kwargs.get("choices"):
                choice = tuple(
                    choice 
                    for choice in choices 
                    if choice.lower() == result.lower()
                )
                
                if not choice:
                    raise CommandError(f"Invalid choice for parameter `{parameter}`.")

                result = choice[0]

            if converter := kwargs.get("converter"):
                if hasattr(converter, "convert"):
                    result = self.context.bot.loop.create_task(converter().convert(self.ctx, result))
                
                else:
                    try:
                        result = converter(result)
                    
                    except Exception:
                        raise CommandError(f"Invalid value for parameter `{parameter}`.")

            if isinstance(result, int):
                if result < kwargs.get("minimum", 1):
                    raise CommandError(f"The **minimum input** for parameter `{parameter}` is `{kwargs.get('minimum', 1)}`")
                
                if result > kwargs.get("maximum", 100):
                    raise CommandError(f"The **maximum input** for parameter `{parameter}` is `{kwargs.get('maximum', 100)}`")

            return result

        return kwargs.get("default", None)



class SendHelp(Exception):
    pass
        
        
def strip_flags(text: str, ctx: "Context") -> str:
    """
    Strip flags from a string
    """
    
    def _filter():
        ret = { }
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
    
    
async def pagination_replacement(params: str, guild: Guild, current_page: int, total_pages: int) -> str:
    """
    Replace variables in a pagination embed script.
    """

    return multi_replace(params, {
        "{page.current}": str(current_page),
        "{page.total}": str(total_pages),
        "{guild.name}": guild.name,
        "{guild.count}": str(guild.member_count),
        "{guild.count.format}": ordinal(guild.member_count),
        "{guild.id}": str(guild.id),
        "{guild.created_at}": format_dt(guild.created_at, style="R"),
        "{guild.boost_count}": str(guild.premium_subscription_count),
        "{guild.boost_count.format}": ordinal(guild.premium_subscription_count),
        "{guild.booster_count}": str(len(guild.premium_subscribers)),
        "{guild.booster_count.format}": ordinal(len(guild.premium_subscribers)),
        "{guild.boost_tier}": str(guild.premium_tier),
        "{guild.icon}": guild.icon.url if guild.icon else ""
    })


def find_emojis(text: str) -> List[str]:
    """
    Find emojis in the given text.

    Parameters:
        text (str): The text to search for emojis.

    Returns:
        List[str]: A list of emojis found in the text.
    """

    return expressions.custom_emoji.findall(text) + expressions.unicode_emoji.findall(text)
    
    
def find_invites(text: str) -> List[str]:
    """
	Finds all Discord invite links in the given text.

	Parameters:
	    text (str): A string representing the text to search for invite links.

	Return:
	    List[str]: A list of Discord invite links found in the text.
	"""

    return expressions.discord_invite.findall(text)
        
        
class HTTPClient:
    def __init__(
        self: "HTTPClient", 
        headers: Optional[dict] = None, 
        proxy: bool = False
    ) -> NoReturn:
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        }
        
        self.proxied = proxy
        self.proxy = lambda: choice(literals.keys.proxies.split("||")) if proxy else None
        self.cloudflare_proxy = "https://proxy.vileb.org"

        
    def session(self: "HTTPClient", headers: Optional[dict] = None) -> ClientSession:
        return ClientSession(
            headers=headers,
            connector=TCPConnector(
                family=AF_INET,
                resolver=AsyncResolver(),
                limit=0,
                local_addr=None
            ),
            json_serialize=orjson.dumps
        )
        
        
    async def post_json(
        self: "HTTPClient", 
        url: str, 
        data: Optional[Any] = None,
        json: Optional[Dict] = None,
        headers: Optional[dict] = None, 
        params: Optional[dict] = None, 
        allow_redirects: bool = False, 
        ssl: Optional[bool] = None, 
        raise_for_status: bool = True,
        command_error: bool = True
    ) -> dict:
        """
        Send a POST request and get the JSON response.
        """
        
        async with self.session(headers=headers or self.headers) as session:
            async with session.post(
                url=url, 
                data=data, 
                proxy=self.proxy(), 
                params=params, 
                allow_redirects=allow_redirects, 
                ssl=ssl
            ) as response:
                
                if raise_for_status:
                    try:
                        response.raise_for_status()
                        
                    except HTTPError:
                        if command_error is True:
                            with suppress(Exception):
                                raise CommandError(f"The **API** returned [`{response.status} {HTTPStatus(response.status).phrase}`](https://http.cat/{response.status}).")
                    
                return await response.json()


    async def post_text(
        self: "HTTPClient", 
        url: str, 
        data: Optional[Any] = None, 
        json: Optional[Dict] = None,
        headers: Optional[dict] = None, 
        params: Optional[dict] = None, 
        allow_redirects: bool = False, 
        ssl: Optional[bool] = None, 
        raise_for_status: bool = True,
        command_error: bool = True
    ) -> str:
        """
        Send a POST request and get the HTML response.
        """
        
        async with self.session(headers=headers or self.headers) as session:
            async with session.post(
                url=url, 
                data=data, 
                proxy=self.proxy(), 
                params=params, 
                allow_redirects=allow_redirects, 
                ssl=ssl
            ) as response:
                if raise_for_status:
                    try:
                        response.raise_for_status()
                        
                    except HTTPError:
                        if command_error is True:
                            with suppress(Exception):
                                raise CommandError(f"The **API** returned [`{response.status} {HTTPStatus(response.status).phrase}`](https://http.cat/{response.status}).")
                    
                return await response.text()


    async def post_bytes(
        self: "HTTPClient", 
        url: str, 
        data: Optional[Any] = None, 
        json: Optional[Dict] = None,
        headers: Optional[dict] = None, 
        params: Optional[dict] = None, 
        allow_redirects: bool = False, 
        ssl: Optional[bool] = None, 
        raise_for_status: bool = True,
        command_error: bool = True
    ) -> bytes:
        """
        Send a POST request and get the response in bytes.
        """
        
        async with self.session(headers=headers or self.headers) as session: 
            async with session.post(
                url=url, 
                data=data, 
                proxy=self.proxy(), 
                params=params, 
                allow_redirects=allow_redirects, 
                ssl=ssl
            ) as response:
                if raise_for_status:
                    try:
                        response.raise_for_status()
                        
                    except HTTPError:
                        if command_error is True:
                            with suppress(Exception):
                                raise CommandError(f"The **API** returned [`{response.status} {HTTPStatus(response.status).phrase}`](https://http.cat/{response.status}).")
                    
                return await response.read()
            

    async def _dl(
        self: "HTTPClient", 
        url: str, 
        headers: Optional[dict] = None, 
        params: Optional[dict] = None, 
        allow_redirects: bool = False, 
        ssl: Optional[bool] = False, 
        cloudflare: bool = False, 
        timeout: Union[ float, int ] = float("inf"), 
        raise_for_status: bool = True,
        command_error: bool = True,
        filesize_limit: int = 1e8
    ) -> bytes:
        
        total_size = 0
        data = BytesIO()

        async with Timeout(timeout):
            async with self.session(headers=headers or self.headers) as session:
                async with session.get(
                    url=f"{self.cloudflare_proxy}?url={url}" if cloudflare else url, 
                    proxy=self.proxy(), 
                    params=params, 
                    allow_redirects=allow_redirects, 
                    ssl=ssl
                ) as response:

                    if raise_for_status:
                        try:
                            response.raise_for_status()
                            
                        except HTTPError:
                            if command_error is True:
                                with suppress(Exception):
                                    raise CommandError(f"The **API** returned [`{response.status} {HTTPStatus(response.status).phrase}`](https://http.cat/{response.status}).")
                        
                    if int(response.headers.get("Content-Length", 0)) > filesize_limit:
                        if command_error is True:
                            raise CommandError("This download exceeded the filesize limit.")
                            
                        return
                        
                    while True:
                        await sleep(1e-3)

                        data.write(chunk := await response.content.read(4096))
                        total_size += len(chunk)

                        if not chunk:
                            break

                        if total_size > 1e8:
                            del data
                            raise CommandError("This download exceeded my 100 Mb limit.")

                    return data.getvalue()


    async def text(
        self: "HTTPClient", 
        url: str, 
        headers: Optional[dict] = None, 
        params: Optional[dict] = None, 
        allow_redirects: bool = False, 
        ssl: Optional[bool] = False, 
        cloudflare: bool = False,
        timeout: Union[ float, int ] = float("inf"), 
        raise_for_status: bool = True,
        command_error: bool = True,
        filesize_limit: int = 1e8
    ) -> str:
        """
        Send a GET request and get the HTML response.
        """
        
        data = await self._dl(
            url, 
            headers, 
            params, 
            allow_redirects, 
            ssl, 
            cloudflare,
            timeout,
            raise_for_status,
            command_error,
            filesize_limit
        )
        
        if data:
            return data.decode("utf-8")
            
        return data


    async def json(
        self: "HTTPClient", 
        url: str, 
        headers: Optional[dict] = None, 
        params: Optional[dict] = None, 
        allow_redirects: bool = False, 
        ssl: Optional[bool] = False, 
        cloudflare: bool = False,
        timeout: Union[ float, int ] = float("inf"),
        raise_for_status: bool = True,
        command_error: bool = True,
        filesize_limit: int = 1e8
    ) -> str:
        """
        Send a GET request and get the JSON response.
        """
        
        data = await self._dl(
            url, 
            headers, 
            params, 
            allow_redirects, 
            ssl, 
            cloudflare,
            timeout,
            raise_for_status,
            command_error,
            filesize_limit
        )
        
        if data:
            return orjson.loads(data)

        return data
        
    
    get = json


    async def read(
        self: "HTTPClient", 
        url: str, 
        headers: Optional[dict] = None, 
        params: Optional[dict] = None, 
        allow_redirects: bool = False, 
        ssl: Optional[bool] = False, 
        cloudflare: bool = False,
        raise_for_status: bool = True,
        timeout: Union[ float, int ] = float("inf"),
        command_error: bool = True,
        filesize_limit: int = 1e8
    ) -> str:
        """
        Send a GET request and get the response in bytes.
        """
        
        return await self._dl(
            url, 
            headers, 
            params, 
            allow_redirects, 
            ssl, 
            cloudflare,
            timeout,
            raise_for_status,
            command_error,
            filesize_limit
        )
        
        
class MariaDB:
    def __init__(self: "MariaDB") -> NoReturn:
        self.pool = None

    
    async def __aenter__(self: "MariaDB"):
        if self.pool is None:
            await self.initialize_pool()
            
        return self

    
    async def __aexit__(self: "MariaDB", *_) -> NoReturn:
        return await self.close()


    async def wait_for_pool(self: "MariaDB") -> NoReturn:
        """
        Wait for the Pool to be initialized.
        """
        
        async with Timeout(10):
            while self.pool is None:
                logger.warning("Pool not initialized yet, waiting...")


    async def initialize(self: "MariaDB") -> NoReturn:
        """
        Create the MariaDB pool.
        """
        
        logger.info("Initializing MariaDB pool..")
 
        self.pool = await create_pool(
            db="vilebot",
            host="localhost",
            port=3306,
            user="vileuser",  # Update with your new user
            password="your_password",  # Update with your new password
            maxsize=10, 
            autocommit=True, 
            echo=False
        )
 
        logger.info("Initialized MariaDB pool @ 127.0.0.1:3306")


    async def close(self: "MariaDB") -> NoReturn:
        """
        Close the Pool
        """

        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

        return True


    async def execute(
        self: "MariaDB", 
        query: str, 
        *params: Any, 
        one_row: bool = False, 
        one_value: bool = False, 
        as_list: bool = False
    ) -> Any:
        """
        Return all entries for the specified query.
        """
        
        await self.wait_for_pool()
        
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, params)
                data = await cursor.fetchall()

        if data:
            
            if one_value:
                return data[0][0]

            if one_row:
                return data[0]

            if as_list:
                return tuple(row[0] for row in data)

            return data

        return ( )


    async def fetchrow(
        self: "MariaDB", 
        statement: str, 
        *params: Any
    ) -> Tuple:
        """
        Return a single row.
        """
        
        return await self.execute(
            statement, 
            *params, 
            one_row=True
        )
    

    async def fetchval(
        self: "MariaDB", 
        statement: str, 
        *params: Any
    ) -> Any:
        """
        Return a single entry.
        """
        
        return await self.execute(
            statement, 
            *params, 
            one_value=True
        )


    async def fetch(
        self: "MariaDB", 
        statement: str, 
        *params: Any
    ) -> Tuple:
        """
        Return a Tuple of entries.
        """
        
        return await self.execute(
            statement, 
            *params, 
            as_list=True
        )


class VileCache:
    def __init__(self, bot: Optional["VileBot"] = None) -> NoReturn:
        self.bot = bot
        
        self._dict = { }
        self._rl = { }
        self._locks = { }
        self._semaphores = { }
        self._delete = { }
        self._futures = { }

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #

        self.blacklisted = { }
        self.errors = { }
        self.custom_prefix = { }
        self.guild_prefix = { }
        self.lastfm_vote = { }
        self.donator = { }
        self.starboard = { }
        self.starboard_blacklist = { }
        self.starboard_message = { }
        self.welcome_settings = { }
        self.boost_settings = { }
        self.unboost_settings = { }
        self.booster_role = { }
        self.booster_award = { }
        self.booster_base = { }
        self.leave_settings = { }
        self.sticky_message_settings = { }
        self.aliases = { }
        self.filter = { }
        self.filter_whitelist = { }
        self.filter_event = { }
        self.filter_snipe = { }
        self.autoresponder = { }
        self.autoresponder_event = { }
        self.autoreact = { }
        self.autoreact_event = { }
        self.disabled_module = { }
        self.disabled_command = { }
        self.ignore = { }
        self.pins = { }
        self.restricted_commands = { }
        self.webhooks = { }
        self.fake_permissions = { }
        self.pagination = { }
        self.pagination_pages = { }
        self.sticky_roles = { }
            

    async def do_expiration(self, key: str, expiration: int) -> NoReturn:
        """
        Removes an item from the dictionary after a specified expiration time.

        Parameters:
            key (str): The key of the item to be removed.
            expiration (int): The time in seconds after which the item should be removed.
        """
        
        await sleep(expiration)

        if key in self._dict: 
            del self._dict[key]


    def lock(self, key: Any) -> int:
        """
        Returns the `asyncio.Lock` associated with a key.
        
        Parameters:
            key (Any): The key to check for.
            
        Returns:
            Lock: The corresponding `asyncio.Lock` if found, otherwise returns a new `asyncio.Lock` object.
        """
        
        if key in self._locks:
            return self._locks[key]
        
        self._locks[key] = Lock()
        return self._locks[key]


    def semaphore(self, key: Any, amount: int) -> int:
        """
        Returns the `asyncio.Semaphore` associated with a key.
        
        Parameters:
            key (Any): The key to check for.
            
        Returns:
            Semaphore: The corresponding `asyncio.Semaphore` if found, otherwise returns a new `asyncio.Semaphore` object.
        """
        
        if key in self._semaphores:
            return self._semaphores[key]
        
        self._semaphores[key] = Semaphore(amount)
        return self._semaphores[key]
            

    def set(self, key: Any, value: Any, expiration: Optional[int] = None) -> int:
        """
        Set the value of the given key in the dictionary.

        Parameters:
            key (Any): The key to set the value for.
            value (Any): The value to set.
            expiration (Optional[int], optional): The expiration time in seconds. Defaults to None.

        Returns:
            int: The number of items in the dictionary after setting the value.
        """
        
        self._dict[key] = value
        
        if expiration is not None:
            if key in self._futures:
                self._futures[key].cancel()
            
            self._futures[key] = self.bot.loop.create_task(self.do_expiration(
                key, 
                expiration
            ))
        
        return 1


    def sadd(self, key: Any, *values: Any) -> int:
        """
        Add one or more values to a set stored under a given key.
        
        Parameters:
            key (Any): The key under which the set is stored.
            *values (Any): The values to add to the set.
            
        Returns:
            int: The number of values that were successfully added to the set.
            
        Raises:
            AssertionError: If the provided key is already in the cache as another type.
        """

        if key not in self._dict:
            self._dict[key] = set()

        assert isinstance(self._dict[key], set), \
            "The provided key is already in the cache as another type."

        to_add = set()
        
        for value in values:
            if value not in self._dict[key]:
                to_add.add(value)
                continue

        for value in to_add:
            self._dict[key].add(value)
                
        return len(to_add)

    
    def smembers(self, key: Any) -> set:
        """
        Return a set of values associated with the given key.
        
        Parameters:
            key (Any): The key to retrieve the values for.
            
        Returns:
            set: A set of values associated with the key.
            
        Raises:
            AssertionError: If the key belongs to a different type.
        """

        assert isinstance(self._dict.get(key, set()), set), \
            "That key belongs to another type."
        
        return tuple(self._dict.get(key, set()))


    def scard(self, key: Any) -> int:
        """
        Retrieve the cardinality of a set in the cache.

        Parameters:
            key (Any): The key associated with the set.

        Returns:
            int: The number of elements in the set.

        Raises:
            AssertionError: If the set does not exist in the cache or if it belongs to another type.
        """

        assert isinstance(self._dict.get(key), set), \
            "There is no such set in this cache, or that belongs to another type."
        
        return len(self._dict[key])


    def srem(self, key: Any, *members: Any) -> int:
        """
        Remove the specified members from the set stored at key. 
        If a member does not exist in the set, it is ignored.
        
        Parameters:
            key (Any): The key of the set in the cache.
            *members (Any): The members to remove from the set.
            
        Returns:
            int: The number of members that were successfully removed from the set.
            
        Raises:
            AssertionError: If the value associated with key is not a set.
        """

        assert isinstance(self._dict.get(key), set), \
            "There is no such set in this cache, or that belongs to another type."

        try:
            return len(tuple(
                self._dict[key].remove(member)
                for member in members
                if member in self._dict[key]
            ))

        finally:
            if not self._dict[key]:
                del self._dict[key]


    def delete(self, *keys: Any, pattern: Optional[str] = None) -> int:
        """
    	Delete one or more keys from the dictionary.

        Parameters:
            *keys (Any): The keys to be deleted.
            pattern (Optional[str], optional): A pattern to filter the keys by. Defaults to None.

        Returns:
            int: The number of keys deleted.
    	"""

        if not keys and pattern is not None:
            keys = tuple(filter(
                lambda k: pattern.rstrip("*") in k, 
                self._dict.keys()
            ))
                
        return len(tuple(
            self._dict.pop(key) 
            for key in keys 
            if key in self._dict
        ))


    def get(self, key: Any, fallback: Any = None) -> Any:
        """
        Get the value associated with the given key from the dictionary.

        Parameters:
            key (Any): The key to search for in the dictionary.

        Returns:
            Any: The value associated with the given key. Returns None if the key is not found.
        """

        return self._dict.get(key, fallback)
        

    def keys(self, pattern: Optional[str] = None) -> Tuple[Any]:
        """
        Retrieves all keys from the dictionary that match the given pattern.

        Parameters:
            pattern (Optional[str]): A string pattern to match keys against. Defaults to None.

        Returns:
            Tuple[Any]: A tuple containing all the keys that match the pattern.
        """
        
        if pattern:
            return tuple(filter(
                lambda k: pattern.rstrip("*") in k, 
                self._dict.keys()
            ))
            
        return tuple(self._dict.keys())


    def is_ratelimited(self, key: Any) -> bool:
        """
        Check if the given key is rate limited.

        Parameters:
            key (Any): The key to check for rate limiting.

        Returns:
            bool: True if the key is rate limited, False otherwise.
        """
        
        if key in self._dict:
            if self._dict[key] >= self._rl[key]: 
                return True
                
        return False
        

    def time_remaining(self, key: Any) -> int:
        """
        Calculates the time remaining for the given key in the cache.
        
        Parameters:
            key (Any): The key to check the remaining time for.
        
        Returns:
            int: The time remaining in seconds. Returns 0 if the key does not exist in the cache.
        """
        
        if key in self._dict and key in self._delete:
            if not self._dict[key] >= self._rl[key]:
                return 0
                
            return (self._delete[key]["last"] + self._delete[key]["bucket"]) - Date.now().timestamp()
        
        else:
            return 0
            

    def ratelimited(self, key: str, amount: int, bucket: int) -> int:
        """
        Check if a key is rate limited and return the remaining time until the next request is allowed.

        Parameters:
            key (str): The key to check for rate limiting.
            amount (int): The maximum number of requests allowed within the rate limit window.
            bucket (int): The duration of the rate limit window in seconds.

        Returns:
            int: The remaining time in seconds until the next request is allowed. Returns 0 if the key is not rate limited.
        """
        
        current_time = Date.now().timestamp()

        if key not in self._dict:
            self._dict[key] = 1
            self._rl[key] = amount
            
            if key not in self._delete:
                self._delete[key] = {
                    "bucket": bucket,
                    "last": current_time
                }
            
            return 0
            
        try:
            if self._delete[key]["last"] + bucket <= current_time:
                self._dict[key] = 0
                self._delete[key]["last"] = current_time
                    
            self._dict[key] += 1

            if self._dict[key] > self._rl[key]:
                return round((bucket - (current_time - self._delete[key]["last"])), 3)
                
            return 0
                    
        except Exception:
            return self.ratelimited(key, amount, bucket)
        
    
    async def cache_blacklists(self) -> NoReturn:
        """
        Cache blacklisted objects from the database.
        """

        _object = await self.bot.db.execute("SELECT object_id, reason FROM blacklisted_object;")
        starboard_blacklist = await self.bot.db.execute("SELECT guild_id, channel_id FROM starboard_blacklist;")
        
        for object_id, reason in _object:
            self.blacklisted[object_id] = reason
            
        for guild_id, channel_id in starboard_blacklist:
            if guild_id not in self.starboard_blacklist:
                self.starboard_blacklist[guild_id] = [ ]
                
            self.starboard_blacklist[guild_id].append(channel_id)
            
        
    async def cache_user_data(self) -> NoReturn:
        """
        Cache user data from the database.
        """

        custom_prefix = await self.bot.db.execute("SELECT user_id, prefix FROM custom_prefix;")
        guild_prefix = await self.bot.db.execute("SELECT guild_id, prefix FROM guild_prefix;")
        lastfm_vote = await self.bot.db.execute("SELECT user_id, is_enabled, upvote_emoji, downvote_emoji FROM lastfm_vote_setting;")
        donator = await self.bot.db.execute("SELECT user_id, donation_tier, total_donated, donating_since FROM donator;")
        
        for user_id, prefix in custom_prefix:
            self.custom_prefix[user_id] = prefix
            
        for guild_id, prefix in guild_prefix:
            self.guild_prefix[guild_id] = prefix
            
        for user_id, is_enabled, upvote_emoji, downvote_emoji in lastfm_vote:
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
            
    
    async def cache_settings(self) -> NoReturn:
        """
        Caches settings from the database.
        """

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
        moderation_confirmations = await self.bot.db.execute("SELECT guild_id, is_enabled FROM moderation_confirmations;")
        autoresponder = await self.bot.db.execute("SELECT guild_id, keyword, response, created_by FROM autoresponder;")
        autoresponder_event = await self.bot.db.execute("SELECT guild_id, event, response FROM autoresponder_event;")
        autoreact = await self.bot.db.execute("SELECT guild_id, keyword, reaction FROM autoreact;")
        autoreact_event = await self.bot.db.execute("SELECT guild_id, event, reaction FROM autoreact_event;")
        disabled_feature = await self.bot.db.execute("SELECT guild_id, name, type FROM disabled_feature;")
        ignore = await self.bot.db.execute("SELECT guild_id, object_id, type FROM ignore_object;")
        pins = await self.bot.db.execute("SELECT guild_id, channel_id, is_enabled FROM pin_archive;")
        webhooks = await self.bot.db.execute("SELECT guild_id, identifier, webhook_url, channel_id FROM webhooks;")
        fake_permissions = await self.bot.db.execute("SELECT guild_id, role_id, permission FROM fake_permissions;")
        hard_banned = await self.bot.db.execute("SELECT guild_id, user_id FROM hard_banned;")
        soft_muted = await self.bot.db.execute("SELECT guild_id, user_id FROM soft_muted;")
        pagination = await self.bot.db.execute("SELECT guild_id, message_id, current_page FROM pagination;")
        pagination_pages = await self.bot.db.execute("SELECT guild_id, message_id, page, page_number FROM pagination_pages;")
        #sticky_roles = await self.bot.db.execute("SELECT guild_id, role_id FROM sticky_roles;")
        restricted_commands = await self.bot.db.execute("SELECT guild_id, command_name, role_id FROM restricted_command")
        afk = await self.bot.db.execute("SELECT guild_id, user_id, status, left_at FROM afk;")
        
        for guild_id, channel_id, is_enabled, message in welcome_settings:
            if guild_id not in self.welcome_settings:
                self.welcome_settings[guild_id] = { }
                
            self.welcome_settings[guild_id][channel_id] = {
                "is_enabled": is_enabled,
                "message": message
            }
            
        for guild_id, channel_id, is_enabled, message in boost_settings:
            if guild_id not in self.boost_settings:
                self.boost_settings[guild_id] = { }
                
            self.boost_settings[guild_id][channel_id] = {
                "is_enabled": is_enabled,
                "message": message
            }
            
        for guild_id, channel_id, is_enabled, message in unboost_settings:
            if guild_id not in self.unboost_settings:
                self.unboost_settings[guild_id] = { }
                
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
                self.booster_role[guild_id] = { }
                
            self.booster_role[guild_id][user_id] = role_id
            
        for guild_id, channel_id, is_enabled, message in leave_settings:
            if guild_id not in self.leave_settings:
                self.leave_settings[guild_id] = { }
                
            self.leave_settings[guild_id][channel_id] = {
                "is_enabled": is_enabled,
                "message": message
            }
            
        for guild_id, channel_id, is_enabled, message in sticky_message_settings:
            self.set(
                f"data:sticky_message_settings:{guild_id}:{channel_id}", Munch(
                    is_enabled=is_enabled,
                    message=message
                )
            )

        for guild_id, command_name, alias in aliases:
            self.sadd(
                f"data:aliases:{guild_id}:{command_name}",
                alias
            )
            
        for guild_id, keyword in _filter:
            self.sadd(
                f"data:filter:{guild_id}",
                keyword
            )
            
        for guild_id, user_id in filter_whitelist:
            self.sadd(
                f"data:filter_whitelist:{guild_id}",
                user_id
            )
            
        for guild_id, event, is_enabled, threshold in filter_event:
            self.set(
                f"data:filter_event:{guild_id}:{event}", Munch(
                    is_enabled=is_enabled,
                    threshold=threshold
                )
            )
            
        for guild_id, invites, links, images, words in filter_snipe:
            self.set(
                f"data:filter_snipe:{guild_id}", Munch(
                    invites=invites,
                    links=links,
                    images= images,
                    words=words
                )
            )
            
        for guild_id, is_enabled in moderation_confirmations:
            self.set(
                f"data:moderation_confirmations:{guild_id}",
                is_enabled
            )
            
        for guild_id, keyword, response, created_by in autoresponder:
            self.set(
                f"data:autoresponder:{guild_id}:{keyword}", Munch(
                    response=response,
                    created_by=created_by
                )
            )
            
        for guild_id, event, response in autoresponder_event:
            self.set(
                f"data:autoresponder_event:{guild_id}:{event}",
                response
            )
            
            
        for guild_id, keyword, reaction in autoreact:
            self.sadd(
                f"data:autoreaction:{guild_id}:{keyword}",
                reaction
            )
            
        for guild_id, event, reaction in autoreact_event:
            self.sadd(
                f"data:autoreaction_event:{guild_id}:{event}",
                reaction
            )
            
        for guild_id, name, _type in disabled_feature:
            self.sadd(
                f"data:disabled_feature:{guild_id}", orjson.dumps(dict(
                    name=name,
                    type=_type
                )
            ))
                
        for guild_id, object_id, _ in ignore:
            self.sadd(f"data:ignore:{guild_id}", object_id)
            
        for guild_id, channel_id, is_enabled in pins:
            self.set(
                f"data:pins:{guild_id}", Munch(
                    channel_id=channel_id,
                    is_enabled=is_enabled
                )
            )
            
        for guild_id, identifier, webhook_url, channel_id in webhooks:
            self.set(
                f"data:webhooks:{guild_id}:{identifier}", Munch(
                    webhook_url=webhook_url,
                    channel_id=channel_id
                )
            )
            
        for guild_id, user_id, status, left_at in afk:
            self.set(
                f"data:afk:{guild_id}:{user_id}", Munch(
                    status=status,
                    left_at=left_at
                )
            )
            
        for guild_id, role_id, permission in fake_permissions:
            self.bot.cache.sadd(f"data:fake_permissions:{guild_id}:{role_id}", permission)

        for guild_id, user_id in hard_banned:
            self.bot.cache.sadd(f"data:hard_banned:{guild_id}", user_id)

        for guild_id, user_id in soft_muted:
            self.bot.cache.sadd(f"data:soft_muted:{guild_id}", user_id)
            
        for guild_id, message_id, current_page in pagination:
            if guild_id not in self.pagination:
                self.pagination[guild_id] = { }
                
            self.pagination[guild_id][message_id] = current_page
            
        for guild_id, message_id, page, page_number in pagination_pages:
            if guild_id not in self.pagination_pages:
                self.pagination_pages[guild_id] = { }
                
            if message_id not in self.pagination_pages[guild_id]:
                self.pagination_pages[guild_id][message_id] = [ ]
                
            self.pagination_pages[guild_id][message_id].append((page, page_number))

        # for guild_id, role_id in sticky_roles:
        #     if guild_id not in self.sticky_roles:
        #         self.sticky_roles[guild_id] = [ ]

        #     self.sticky_roles[guild_id].append(role_id)

        for guild_id, command_name, role_id in restricted_commands:
            if guild_id not in self.restricted_commands:
                self.restricted_commands[guild_id] = { }

            if command_name not in self.restricted_commands[guild_id]:
                self.restricted_commands[guild_id][command_name] = [ ]

            self.restricted_commands[guild_id][command_name].append(role_id)


    async def initialize(self) -> NoReturn:
        """
        Initializes the settings cache.
        
        This function initializes the settings cache by performing the following steps:
            Calls the __init__ method of the class, passing the bot instance as an argument.
            Calls the cache_blacklists method to cache blacklists.
            Calls the cache_user_data method to cache user data.
            Calls the cache_settings method to cache settings.
        """
        
        self.__init__(self.bot)
        
        logger.info("Commencing cache..")

        await gather(
            self.cache_blacklists(),
            self.cache_user_data(),
            self.cache_settings()
        )

        logger.success("Caching complete.")
        
        
async def confirm(ctx: "Context", message: BaseMessage) -> bool:
    """
    Sends a confirmation message.

    parameters:
        ctx (Context): The context object representing the current execution context.
        message (BaseMessage): The message to be confirmed.

    Returns:
        bool: The value of the confirmation.
    """
    
    await message.edit(view=(view := Confirmation(
        message=message, 
        invoker=ctx.author
    )))

    await view.wait()
    return view.value

        
class Context(Context):
    def __init__(self, **kwargs) -> NoReturn:
        super().__init__(**kwargs)
        self.__parameter_parser = ParameterParser(self)
        self.response = None


    @cached_property
    def parameters(self) -> Dict[ str, Any ]:
        """
        Returns a dictionary of parameters for the current command.

        Returns:
            Dict[str, Any]: A dictionary of parameters.
        """

        return {
            name: self.__parameter_parser.get(name, **config) 
            for name, config in self.command.parameters.items()
        }


    @property
    def default_embed(self) -> Embed:
        """
        Returns the default embed for the object.

        Returns:
            Embed: The default embed.
        """
        
        return Embed(color=self.bot.color).set_author(
            name=self.author, 
            icon_url=self.author.display_avatar
        )
        
        
    async def success(
        self, 
        message: str,
        member: Optional[BaseMember] = None, 
        content: Optional[str] = None, 
        delete_after: Optional[int] = None
    ) -> BaseMessage:
        """
        Sends a successful response.

        Parameters:
            message (str): The message to be sent.
            member (Optional[BaseMember], optional): The member to whom the message will be sent. Defaults to None.
            content (Optional[str], optional): The content of the message. Defaults to None.
            delete_after (Optional[int], optional): The time in seconds after which the message will be deleted. Defaults to None.

        Returns:
            BaseMessage: A BaseMessage object representing a successful response.
        """
        
        return await self.respond(
            message, 
            content=content, 
            emoji=self.bot.done, 
            color=self.bot.color, 
            member=member, 
            delete_after=delete_after
        ) 
        
        
    async def error(
        self, 
        message: str,
        member: Optional[BaseMember] = None, 
        content: Optional[str] = None, 
        delete_after: int = 15
    ) -> BaseMessage:
        """
        Sends an error message.

        Parameters:
            message (str): The error message to send.
            member (Optional[BaseMember], optional): The member to send the error message to. Defaults to None.
            content (Optional[str], optional): The content of the error message. Defaults to None.
            delete_after (int, optional): The time in seconds after which the error message should be deleted. Defaults to 15.

        Returns:
            BaseMessage: The sent error message.
        """
        
        return await self.respond(
            message, 
            content=content, 
            emoji=self.bot.warn, 
            color=self.bot.color, 
            member=member, 
            delete_after=delete_after
        )
        
    
    async def respond(
        self, 
        message: str, 
        emoji: str = "", 
        color: int = literals.colors.main, 
        content: Optional[str] = None, 
        member: Optional[BaseMember] = None, 
        delete_after: Optional[int] = None
    ) -> BaseMessage:
        """
        Sends a response message with the specified content, embed, and other optional parameters.

        Parameters:
            message (str): The message to be sent.
            emoji (str, optional): The emoji to be included in the message. Defaults to "".
            color (int, optional): The color of the embed. Defaults to literals.colors.main.
            content (str, optional): The content of the message. Defaults to None.
            member (BaseMember, optional): The member to mention in the message. Defaults to None.
            delete_after (int, optional): The time in seconds after which the message should be deleted. Defaults to None.

        Returns:
            BaseMessage: The sent message.

        Raises:
            Exception: If an error occurs while sending the message.
        """
            
        try:
            return await self.reply(
                content=content,
                delete_after=delete_after,
                embed=Embed(
                    color=color,
                    description=f"{emoji} {(member or self.author).mention}**:** {message}"
                )
            )
        
        except Exception:
            return await self.send(
                content=content,
                delete_after=delete_after,
                embed=Embed(
                    color=color,
                    description=f"{emoji} {(member or self.author).mention}**:** {message}"
                )
            )
        

    async def send(self: "Context", *args: List[Any], **kwargs: Dict[ str, Any ]) -> Optional[BaseMessage]:
        """
        Overwrites the original Context.send.

        Parameters:
            *args (List[Any]): The arguments to pass to the underlying send method.
            **kwargs (Dict[str, Any]): The keyword arguments to pass to the underlying send method.

        Returns:
            Optional[BaseMessage]: The response from the underlying send method, or None if the function is rate limited.
        """
        
        if kwargs.pop("cooldown", True) and self.bot.cache.ratelimited(f"rl:message_send{self.channel.id}", 2, 4):
            return

        if (sem := self.bot.cache.semaphore(f"message_send:{self.channel.id}", 2)).locked():
            return
        
        async with sem:
            self.response = await super().send(*args, **kwargs)
            return self.response
        
        
    async def paginate(
        self: "Context", 
        entries: Union[ Tuple[ Embed, List[str] ], List[Embed], str ], 
        embed: Optional[Embed] = None,
        patch: Optional[BaseMessage] = None,
        per_page: int = 10,
        max_size: int = 1980,
        show_index: bool = True,
        execute: Optional[Tuple[Callable]] = None
    ) -> Optional[BaseMessage]:
        """
        Paginates a list of entries and sends them as embeds.

        Parameters:
            entries (Union[Tuple[Embed, List[str]], List[Embed], str]): The entries to paginate. Can be a tuple of an embed and a list of strings, a list of embeds, or a single string.
            embed (Optional[Embed], optional): The base embed to use. Defaults to None.
            patch (Optional[BaseMessage], optional): The message to patch. Defaults to None.
            per_page (int, optional): The number of entries to display per page. Defaults to 10.
            max_size (int, optional): The maximum size of the description field in the embed. Defaults to 1980.
            show_index (bool, optional): Whether to display an index number before each entry. Defaults to True.

        Returns:
            Optional[BaseMessage]: The patched message or None.

        Raises:
            TypeError: If the rows parameter is not a list.
        """
        
        if isinstance(entries, tuple):
            embed, rows = entries

            if not isinstance(rows, list):
                raise TypeError

            if len(rows) == 0:
                return await self.error("No entries found!")
            
            count = 0
            embeds = [ ]
            embed.description = StringIO()

            rows = tuple(
                f"{f'`{index}` ' if show_index else ''}{row}"
                for index, row in enumerate(rows, start=1)
            )
            
            for row in rows:
                await sleep(1e-3)

                if count < per_page:
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

            if len(embeds) == 1:
                func = patch.edit if patch is not None else self.reply
                return await func(embed=embeds[0])

            return await Paginator(
                self.bot, 
                embeds, 
                self, 
                patch=patch, 
                invoker=self.author.id,
                execute=execute
            ).start()

        elif isinstance(entries, list):
            embeds = entries
            
            if len(embeds) == 0:
                return await self.error("I couldn't find any entries.")
            
            if isinstance(embeds[0], str):
                return await self.paginate((self.default_embed, embeds))

            if len(embeds) == 1:
                return await self.reply(embed=embeds[0])

            return await Paginator(
                self.bot, 
                embeds, 
                self, 
                patch=patch, 
                invoker=self.author.id,
                execute=execute
            ).start()
        
        elif isinstance(entries, str):
            embed = embed or self.default_embed
            return await self.paginate(
                (
                    self.default_embed, 
                    list(text_creator(entries, max_size))
                ),
                per_page=1,
                show_index=False
            )
        

    async def paginate_fields(
        self: "Context", 
        embed: Embed, 
        fields: List[Dict[ str, Any ]], 
        footer: Optional[Dict[ str, Any ]] = None,
        patch: Optional[BaseMessage] = None,
        per_page: int = 10,
    ) -> Optional[BaseMessage]:
        """
        Paginates a list of fields in an embed.

        Parameters:
            embed (Embed): The embed to paginate the fields for.
            fields (List[Dict[str, Any]]): The list of fields to paginate.
            footer (Optional[Dict[str, Any]]): The footer to add to the embed. Defaults to None.
            patch (Optional[BaseMessage]): The message to patch. Defaults to None.
            per_page (int): The number of fields to display per page. Defaults to 10.

        Returns:
            Optional[BaseMessage]: The message object of the paginated embed, or None if there are no fields.
        """
            
        if len(fields) == 0:
             return await self.error("I couldn't find any fields.")

        if len(fields) <= per_page:
            embed._fields = fields
            return await self.reply(embed=embed)

        return await FieldPaginator(
            self.bot, 
            self, 
            embed, 
            fields, 
            footer,
            per_page=per_page,
            patch=patch, 
            invoker=self.author.id
        ).start()


    def is_dangerous(self, role: Role) -> bool:
        """
        Determines if the given role is dangerous based on its permissions.

        Parameters:
            role (Role): The role to check for danger.

        Returns:
            bool: True if the role is dangerous, False otherwise.
        """
        
        permissions = role.permissions
        intersected = permissions & Permissions.elevated()

        return any((v for _, v in intersected))


    def is_boosting(self, user: Union[ BaseMember, BaseUser ]) -> bool:
        """
        Check if a user is boosting any mutual guild.

        Parameters:
            user (Union[BaseMember, BaseUser]): The user to check if they are boosting any mutual guild.

        Returns:
            bool: True if the user is boosting at least one mutual guild, False otherwise.
        """
        
        for guild in user.mutual_guilds:
            if guild.get_member(user.id).premium_since is not None:
                return True

        return False


    async def await_response(self) -> Optional[str]:
        """
        Waits for a response from the user.

        Returns:
            Optional[str]: The content of the user's response, or None if no response is received within 30 seconds.
        """
        
        try:
            message = await self.bot.wait_for(
                "message", 
                check=lambda m: m.author.id == self.author.id and m.channel.id == self.channel.id, 
                timeout=30
            )
            
        except AsyncTimeoutError:
            return

        return message.content
            

class VileBot(Bot):
    def __init__(
        self: "VileBot", 
        command_prefix: str,
        activity: Optional[Activity] = None,
    ) -> NoReturn:
        super().__init__(
            owner_ids=(
                971464344749629512,
                971464344749629512,
            ),
            anti_cloudflare_ban=True,
            s_proxy="https://proxy.vileb.org",
            auto_update=False,
            help_command=HelpCommand(),
            command_prefix=lambda _bot, message: (
                _bot.cache.custom_prefix.get(message.author.id) 
                or _bot.cache.guild_prefix.get(message.guild.id) 
                or when_mentioned_or(command_prefix)(_bot, message)
            ),
            case_insensitive=True,
            strip_after_prefix=True,
            max_messages=500,
            activity=activity,
            chunk_guilds_at_startup=False,
            # shard_count=1,
            # shard_ids=(0,),
            allowed_mentions=AllowedMentions(
                users=True, 
                roles=False, 
                replied_user=False, 
                everyone=False
            ),
            intents=Intents(
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

        self.global_prefix = command_prefix
        self.version = "3.8.1"

        self.color = literals.colors.main
        self.done = literals.emojis.done
        self.fail = literals.emojis.fail
        self.warn = literals.emojis.warn
        self.dash = literals.emojis.dash
        self.reply = literals.emojis.reply
        self.config = Munch(
            emojis=literals.emojis,
            colors=literals.colors,
            api=literals.api
        )

        self.blacklist_types = {
            0: "Unknown reason",
            1: "Abusing or exploiting the bot",
            2: "Violating the Discord ToS",
            3: "Violating our Terms or Privacy Policy",
            4: "Copying our services or features",
            5: "Channel blacklisted by server administrators",
            6: "Guild blacklisted by the bot team",
            7: "Role blacklisted by server administrators"
        }

        self.before_invoke(self.before_commands)
        self.check(self.command_check)
        
        
    async def setup_hook(self: "VileBot") -> NoReturn:
        """
        Initializes the necessary components and sets up the environment for the application.
        
        This function performs the following tasks:
            Initializes the database connection by creating an instance of the MariaDB class.
            Initializes the cache system by creating an instance of the VileCache class.
            Sets up the logger to log messages with a specific format and colorize the output.
            Initializes the configuration object with predefined values for emojis, colors, and API settings.
            Sets the proxy and iterate_local_addresses properties of the HTTP client.
            Creates instances of the HTTPClient class for making HTTP requests with and without proxy.
            Initializes the database connection asynchronously.
            Sets the global variable "DATABASE" to the initialized database instance.
            Creates a background task to initialize the cache system asynchronously.
        """

        self.db = MariaDB()
        self.redis = VileRedis()
        self.cache = VileCache(self)
        self.data_processing = DataProcessing()
        self.logger = logger
        
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.run_async = partial(self.loop.run_in_executor, self.executor)
        
        self.logger.remove()
        self.logger.add(
            stdout,
            colorize=True,
            level="INFO",
            format="<cyan>[</cyan><blue>{time:YYYY-MM-DD HH:MM:SS}</blue><cyan>]</cyan> (<magenta>vile:{function}</magenta>) <yellow>@</yellow> <fg #BBAAEE>{message}</fg #BBAAEE>",
        )

        self.http.s_proxy = "https://proxy.vileb.org"
        self.http.iterate_local_addresses = False
        
        self.session = HTTPClient(proxy=False)
        self.proxied_session = HTTPClient(proxy=True)

        try:
            await self.db.initialize()
            GLOBAL["DATABASE"] = self.db

        except Exception:
            logger.warning("Shutting down; MariaDB pool failed to initialize.")
            await self.close()
            raise

        try:
            await self.redis.initialize()
            GLOBAL["REDIS"] = self.redis

        except Exception:
            logger.warning("Shutting down; Redis client failed to initialize.")
            await self.close()
            raise
        
        try:
            await self.cache.initialize()
            GLOBAL.CACHE = self.cache

        except Exception:
            logger.warning("Shutting down; cache failed to initialize.")
            await self.close()
            raise

        await self.redis.set(
            b"backend_key",
            hash(tuuid.tuuid())
        )
        
        
    async def get_context(
        self: "VileBot", 
        origin: Union[ Interaction, BaseMessage ], 
        cls: "Context" = Context
    ) -> "Context":
        """
        Retrieve the context for a given origin object.

        Parameters:
            origin (Union[Interaction, BaseMessage]): The origin object from which to retrieve the context.
            cls (Type[Context], optional): The class to use for creating the context object. Defaults to Context.

        Returns:
            Context: The context object for the given origin.
        """

        return await super().get_context(origin, cls=cls)
        
        
    async def close(self: "VileBot") -> NoReturn:
        """
        Closes the database connection and the cache system.
        """
        
        await self.db.close()
        await super().close()


    async def report_exception(
        self: "VileBot",
        ctx: Context,
        code: str,
        exception: Munch
    ) -> NoReturn:
        """
        Reports an exception.

        Parameters:
            self (VileBot): The VileBot instance.
            ctx (Context): The context where the exception occurred.
            code (str): The error code.
            exception (Munch): The exception that was raised.
        """
        await self.wait_until_ready()

        return await self.get_channel(1256851790985560145).send(embed=(
            Embed(
                title=f"Error: '{code}' - {ctx.command.qualified_name}",
                color=self.color,
                description=f"**User:** {ctx.author} ({ctx.author.id})\n**Server:** {ctx.guild.name} ({ctx.guild.id})\n**Channel:** {ctx.channel.name} ({ctx.channel.id})\n**Timestamp:** {format_dt(tuuid.decode(code), style='f')}\n```{traceback.format_exception(exception)}```"
            )
            .set_author(
                name="Error",
                icon_url=self.user.display_avatar.url
            )
        ))
    
    
    def __lshift__(self: "VileBot", other: Union[ str, Dict[ str, Any ] ]) -> Callable:
        """
        Perform a left shift operation on the object and return the result.

        Parameters:
            other (Union[str, Dict[str, Any]]): The object to perform the left shift operation with.

        Returns:
            Callable: A callable object representing the result of the left shift operation.
        """
        
        locals = currentframe().f_back.f_locals
        context = (
            locals.get("ctx") 
            or locals.get("context") 
            or getattr(locals.get("self"), "context", None)
        )
        
        if context is None:
            raise Exception
        
        if not isinstance(other, dict):
            return context.send(other)
        
        if isinstance(other, dict):
            return context.send(**other)
        

    __matmul__ = __lshift__
        
        
    @property
    def guilds(self: "VileBot") -> Tuple[Guild]:
        """
        Returns a tuple of all the guilds that the bot is currently connected to.

        Returns:
            Tuple[Guild]: A tuple of Guild objects.
        """
        
        return tuple(self._connection._guilds.values())
    

    @property
    def members(self: "VileBot") -> Tuple[BaseMember]:
        """
        Returns a tuple of all the members of the class.
        
        Returns:
            Tuple[BaseMember]: A tuple of BaseMember objects.
        """
        
        return tuple(self.get_all_members())


    @property
    def channels(self: "VileBot") -> Tuple[GuildChannel]:
        """
        Returns a tuple of all the guild channels.

        Returns:
            Tuple[GuildChannel]: A tuple of GuildChannel objects.
        """

        return tuple(self.get_all_channels())


    @property
    def text_channels(self: "VileBot") -> Tuple[TextChannel]:
        """
        Returns all text channels in the class instance.

        Returns:
            Tuple[TextChannel]: A tuple of TextChannel objects.
        """
        
        return tuple(
            filter(
                lambda channel: isinstance(channel, TextChannel),
                self.get_all_channels()
            )
        )


    @property
    def voice_channels(self: "VileBot") -> Tuple[VoiceChannel]:
        """
        Returns a tuple of all voice channels in the guild.

        Returns:
            Tuple[VoiceChannel]: A tuple of VoiceChannel objects representing all voice channels in the guild.
        """

        return tuple(
            filter(
                lambda channel: isinstance(channel, VoiceChannel),
                self.get_all_channels()
            )
        )
    

    @property
    def database_pool(self: "VileBot") -> Optional[Pool]:
        """
        Returns the database connection pool.

        Returns:
            Optional[Pool]: The database connection pool or None if there is no pool.
        """

        return self.db.pool
        
    
    @staticmethod
    async def before_commands(ctx: "Context") -> NoReturn:
        """
        A static method that is called before executing any commands.
        
        Parameters:
            ctx (Context): The context object representing the current execution context.
        """
        
        if ctx.author.bot:
            return
            
        if ctx.guild and ctx.guild.chunked is False:
            await ctx.guild.chunk(cache=True)
        
        if not ctx.bot.cache.ratelimited(f"rl:typing:{ctx.channel.id}", 3, 10):
            await ctx.typing()

            
    @staticmethod
    async def command_check(ctx: "Context") -> bool:
        """
        Check if the command is allowed to be executed.

        Parameters:
            ctx (Context): The context object representing the current execution context.

        Returns:
            bool: True if the command is allowed to be executed, False otherwise.
        """

        await ctx.bot.wait_until_ready()
        
        if await ctx.bot.is_owner(ctx.author):
            return True
        
        ### Blacklisted Object ###

        if any((
            ctx.author.id in ctx.bot.cache.blacklisted,
            ctx.channel.id in ctx.bot.cache.blacklisted,
            ctx.guild.id in ctx.bot.cache.blacklisted if ctx.guild else False
        )):
            return False
            
        ### Cooldown ###

        if retry_after := ctx.bot.cache.ratelimited(f"rl:user_commands:{ctx.author.id}", 2, 4):
            if ctx.bot.cache.ratelimited(f"globalrl:user_commands", 30, 60):
                return False
                    
            if ctx.bot.cache.ratelimited(f"banrl:user_commands:{ctx.author.id}", 5, 8):
                await ctx.bot.blacklist(ctx.author.id, _type=1)
                return False
                
            raise CommandOnCooldown(
                None, retry_after, None
            )
        
        if ctx.guild is None:
            return True
            
        ### Disabled Feature ###

        disabled_features = tuple(
            orjson.loads(feature)["name"]
            for feature in ctx.bot.cache.smembers(f"data:disabled_feature:{ctx.guild.id}")
        )

        if ctx.command.qualified_name in disabled_features:
            await ctx.error(f"The '{(ctx.command.root_parent or ctx.command).qualified_name}' command has been **disabled** by **server administrators**.")
            return False
            
        if (ctx.command.cog_name or "").lower() in disabled_features:
            await ctx.error(f"The '{ctx.command.cog_name}' module has been **disabled** by **server administrators**.")
            return False
            
        ### Ignored Object ###

        if ignored := ctx.bot.cache.smembers(f"data:ignore:{ctx.guild.id}"):
            if any((
                ctx.author.id in ignored, 
                ctx.channel.id in ignored, 
                any(role.id in ignored for role in ctx.author.roles)
            )) and ctx.author.guild_permissions.administrator is False:
                return False
        
        ### Restricted Command ###

        if ctx.command.qualified_name in (restricted := ctx.bot.cache.restricted_commands.get(ctx.guild.id, DICT)):
            if not any(ctx.author.get_role(role_id) for role_id in restricted[ctx.command.qualified_name]):
                await ctx.error("This command is restricted to certain roles.")
                return False
            
        return True
        
        
    async def load_extensions(self: "VileBot") -> NoReturn:
        """
        Load extensions for the bot.
        This function loads the "jishaku" extension and starts a Watcher to monitor changes in the "cogs" directory.
        """
        
        logger.info("Loading extensions...")
        
        jishaku.Flags.RETAIN = True
        jishaku.Flags.NO_DM_TRACEBACK = True
        jishaku.Flags.FORCE_PAGINATOR = True
        jishaku.Flags.NO_UNDERSCORE = True
        jishaku.Flags.HIDE = True
        
        await self.load_extension("jishaku")
        logger.info("Loaded extension: jishaku")
        
        # Load the cogs
        cogs = [
            "cogs.moderation",
            "cogs.developer",
            "cogs.servers"
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded extension: {cog}")
            except Exception as e:
                logger.error(f"Failed to load extension {cog}: {e}")
        
        self.loop.create_task(Watcher(
            bot=self,
            path="cogs",
            loop=self.loop,
            preload=True
        ).start())
        logger.info("Started Watcher for 'cogs' directory")
        
        
    async def blacklist(
        self: "VileBot", 
        id: int, 
        _type: int = 0
    ) -> int:
        """
        Adds an object to the blacklist.

        Parameters:
            id (int): The ID of the object to be blacklisted.
            _type (int, optional): The type of the object. Defaults to 0.

        Returns:
            int: Returns 0 if the object is already blacklisted, otherwise returns 1.
        """

        
        assert _type in self.blacklist_types, \
            "Please provide a valid type between 0 and 7."
            
        assert id not in self.cache.blacklisted, \
            "That object is already blacklisted."
            
        await self.db.execute(
            "INSERT INTO blacklisted_object (object_id, reason) VALUES (%s, %s);",
            id, self.blacklist_types[_type]
        )
        
        self.cache.blacklisted[id] = self.blacklist_types[_type]
        
        if (user := self.get_user(id)) and self.get_user(id).mutual_guilds:
            self.loop.create_task(user.send(
                embed = (
                    Embed(
                        color=self.color,
                        title="Blacklisted",
                        description=f"> You have been blacklisted from {self.user.name.title()}",
                        timestamp=Date.now()
                    )
                    .set_author(
                        name=f"{self.user.name.title()} Trust & Safety",
                        icon_url=self.user.display_avatar
                    )
                    .add_field(
                        name="Moderator",
                        value=str(self.user)
                    )
                    .add_field(
                        name="Reason",
                        value=self.blacklist_types[_type]
                    )
                    .set_thumbnail(
                        url=self.user.display_avatar
                    )
                    .set_footer(
                        text="Contact a developer if you wish to dispute this punishment"
                    )
                )
            ))
            
        return 1
        
        
    async def unblacklist(self: "VileBot", id: int) -> int:
        """
        Remove an object from the blacklist.

        Parameters:
            id (int): The ID of the object to be unblacklisted.

        Returns:
            int: 0 if the object was not blacklisted, 1 if the user was successfully unblacklisted.
        """
        
        assert id in self.cache.blacklisted, \
            "That object is not blacklisted."
            
        await self.db.execute(
            "DELETE FROM blacklisted_object WHERE object_id = %s;",
            id
        )

        del self.cache.blacklisted[id]

        if (user := self.get_user(id)) and self.get_user(id).mutual_guilds:
            self.loop.create_task(user.send(
                embed = (
                    Embed(
                        color=self.color,
                        title="Unblacklisted",
                        description=f"> You have been unblacklisted from {self.user.name.title()}",
                        timestamp=Date.now()
                    )
                    .set_author(
                        name=f"{self.user.name.title()} Trust & Safety",
                        icon_url=self.user.display_avatar
                    )
                    .add_field(
                        name="Moderator",
                        value=str(self.user)
                    )
                    .add_field(
                        name="Reason",
                        value="N/A"
                    )
                    .set_thumbnail(
                        url=self.user.display_avatar
                    )
                    .set_footer(
                        text="This action was performed by an owner"
                    )
                )
            ))
            
        return 1
        
    
    async def on_ready(self: "VileBot"):
        """
        Event handler that is called when the bot is ready to start responding to events.

        This function performs several tasks when the bot is ready:
            Logs the bot's login information.
            Sets aliases for the "help" command.
            Loads all extensions.
            Generates an OAuth invite URL for the bot.
            Launches a headless browser if specified.
        """

        logger.info(f"Logged in as {self.user} (Application ID: {self.user.id})")
        
        help_command = self.get_command("help")
        help_command.aliases = ("commands", "h")

        for alias in help_command.aliases:
            self.all_commands[alias] = help_command

        for i in (m := range(int(2e6))):
            self._connection._users[i] = self.user

        fake_guild = copy(self.guilds[0])
        fake_guild.id = 1
        fake_guild.owner_id = self.user.id
        fake_guild._member_count = int(2e6)
        fake_guild._members = {i: self.user for i in range(1,6)}
        self._connection._guilds[1] = fake_guild

        await self.load_extensions()

        self.invite = oauth_url(
            self.user.id, 
            permissions=Permissions(8)
        )
            
        await self.redis.set(
            b"guild_count",
            len(self.guilds)
        )

        await self.redis.set(
            b"user_count",
            sum(g.member_count for g in self.guilds)
        )

        async def chunk_guild(guild: Guild):
            await sleep(1.5)
            
            if guild.chunked is False:
                await guild.chunk(cache=True)

        for guild in sorted(
            self.guilds,
            key=lambda g: g.member_count,
            reverse=True
        ):
            if guild.id != 1 and guild.chunked is False:
                await sleep(1e-3)
                await self.loop.create_task(chunk_guild(guild))
        
    
    async def on_shard_connect(self: "VileBot", shard_id: int):
        """
        Set the connection status for a specific shard.

        Parameters:
            shard_id (int): The ID of the shard to set the connection status for.
        """
        
        shard = self.shards[shard_id]._parent
        shard.uptime = Date.now()
        # shard.cluster_id = self.cluster
        
        
    async def on_message(self: "VileBot", message: BaseMessage):
        """
        Handle the event of a message being sent.

        Parameters:
            message (BaseMessage): The message that was sent.
        """

        await self.wait_until_ready()  
        
        if message.author.bot:
            return
        
        if message.guild is None:
            if not await self.is_owner(message.author):
                return
                
            return await self.process_commands(message) 
             
        block_command_execution = False
        context = await self.get_context(message)
        
        await self.redis.lpush(f"data:messages:{message.guild.id}:{message.channel.id}:{message.author.id}", message.content)
        await self.redis.hset(f"data:last_seen:{message.author.id}", message.guild.id, Date.now().timestamp())
        
        def check():
            return all((
                message.author.id != message.guild.owner_id,
                message.author.guild_permissions.administrator is False,
                (message.author.top_role.position <= message.guild.me.top_role.position) if message.author.top_role else True,
                not any((message.author.id in self.cache.smembers(f"data:filter_whitelist:{message.guild.id}"), message.channel.id in self.cache.smembers(f"data:filter_whitelist:{message.guild.id}"), any(role.id in self.cache.smembers(f"data:filter_whitelist:{message.guild.id}") for role in message.author.roles))),
                message.author.id != message.guild.me.id
            ))
            
        # -- Filtered words -- #
        
        if self.cache.get(f"data:filter:{message.guild.id}") and block_command_execution is False:
            if check():
                async def do_filter():
                    content = "".join(
                        c 
                        for c in message.content 
                        if c.isalnum() or c.isspace()
                    )
                    
                    for keyword in self.cache.smembers(f"data:filter:{message.guild.id}"):
                        await sleep(1e-3)
                        
                        if keyword in content:
                            gather(*[
                                message.author.timeout(Date.now().astimezone() + timedelta(seconds=5)),
                                context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my chat filter.", member=message.guild.me),
                                message.delete()
                            ])
                            
                            block_command_execution = True
                            break
                        
                self.loop.create_task(do_filter())
            
        # -- Filtered events -- #
        
        filter_events = tuple(
            record.split(":")[::-1][0]
            for record in self.cache.keys(pattern=f"data:filter_event:{message.guild.id}:*")
        )
        
        # -- Filter spoilers -- #
        
        if "spoilers" in filter_events and self.cache.get(f"data:filter_event:{message.guild.id}:spoilers").is_enabled == True and block_command_execution is False:
            if message.content.count("||") >= (self.cache.get(f"data:filter_event:{message.guild.id}:spoilers").threshold * 2):
                if check():
                    gather(*[
                        message.author.timeout(Date.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my spoiler filter.", member=message.guild.me),
                        message.delete()
                    ])

                    block_command_execution = True
                    
        # -- Filter links -- #
        
        if "links" in filter_events and self.cache.get(f"data:filter_event:{message.guild.id}:links").is_enabled == True and block_command_execution is False:
            if check():
                if "http" in message.content or "www" in message.content:
                    gather(*[
                        message.author.timeout(Date.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my link filter.", member=message.guild.me),
                        message.delete()
                    ])

                    block_command_execution = True
         
        # -- Filter spam -- #
        
        if "spam" in filter_events and self.cache.get(f"data:filter_event:{message.guild.id}:spam").is_enabled == True and block_command_execution is False:
            if check():
                if self.cache.ratelimited(f"rl:message_spam{message.author.id}-{message.guild.id}", self.cache.get(f"data:filter_event:{message.guild.id}:spam").threshold, 5):
                    gather(*[
                        message.author.timeout(Date.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my spam filter.", member=message.guild.me)
                    ])

                    await message.channel.purge(
                        limit=10,
                        check=lambda m: m.author.id == message.author.id
                    )

                    block_command_execution = True
            
        # -- Filter emojis -- #
        
        if "emojis" in filter_events and self.cache.get(f"data:filter_event:{message.guild.id}:emojis").is_enabled == True and block_command_execution is False:
            if len(find_emojis(message.content)) >= (self.cache.get(f"data:filter_event:{message.guild.id}:emojis").threshold):
                if check():
                    gather(*[
                        message.author.timeout(Date.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my emoji filter.", member=message.guild.me),
                        message.delete()
                    ])

                    block_command_execution = True
                    
        # -- Filter invites -- #
        
        if "invites" in filter_events and self.cache.get(f"data:filter_event:{message.guild.id}:invites").is_enabled == True and block_command_execution is False:
            if find_invites(message.content):
                if check():
                    gather(*[
                        message.author.timeout(Date.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my invite filter.", member=message.guild.me),
                        message.delete()
                    ])

                    block_command_execution = True
                    
        # -- Filter caps -- #
        
        if "caps" in filter_events and self.cache.get(f"data:filter_event:{message.guild.id}:caps").is_enabled == True and block_command_execution is False:
            if len(tuple(c for c in message.content if c.isupper())) >= (self.cache.get(f"data:filter_event:{message.guild.id}:caps").threshold):
                if check():
                    gather(*[
                        message.author.timeout(Date.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my cap filter.", member=message.guild.me),
                        message.delete()
                    ])

                    block_command_execution = True
                    
        # -- Filter massmention -- #
        
        if "massmention" in filter_events and self.cache.get(f"data:filter_event:{message.guild.id}:massmention").is_enabled == True and block_command_execution is False:
            if len(message.mentions) >= (self.cache.get(f"data:filter_event:{message.guild.id}:massmention").threshold):
                if check():
                    gather(*[
                        message.author.timeout(Date.now().astimezone() + timedelta(seconds=5)),
                        context.success(f"{message.author} (`{message.author.id}`) has been **timed out** for `5 seconds`.\n{self.reply} **Reason:** muted by my mention filter.", member=message.guild.me),
                        message.delete()
                    ])

                    block_command_execution = True
                    
        if block_command_execution is True:
            return
            
        # -- Mention reply -- #
        
        if self.user in message.mentions:
            self.loop.create_task(context.respond(
                f"[**{self.user.name.title()}'s**](https://discord.gg/KsfkG3BZ4h) global prefix is `{self.global_prefix}`, this server's prefix is {'not set' if message.guild.id not in self.cache.guild_prefix else f'`{self.cache.guild_prefix[message.guild.id]}`'} and your custom prefix is {'not set' if message.author.id not in self.cache.custom_prefix else f'`{self.cache.custom_prefix[message.author.id]}`'}.",
                emoji="<:v_slash:1067034025895665745>"
            ))
            
        # -- Autoresponder words -- #
        
        if context.valid is False and self.cache.keys(pattern=f"data:autoresponder:{message.guild.id}:*"):
            async def do_autoresponder():
                if self.cache.ratelimited(f"rl:autoresponder{message.guild.id}", 5, 30):
                    return
                
                for keyword in tuple(
                    record.split(":")[::-1][0]
                    for record in self.cache.keys(pattern=f"data:autoresponder:{message.guild.id}:*")
                ):
                    await sleep(1e-3)
                    
                    if keyword in message.content:
                        data = self.cache.get(f"data:autoresponder:{message.guild.id}:{keyword}")
                        
                        async with self.cache.lock(f"autoresponder:{message.guild.id}"):
                            return await EmbedScript(data.response).send(
                                context,
                                guild=message.guild,
                                user=message.author
                            )
                
            self.loop.create_task(do_autoresponder())
            
        # -- Autoresponder events -- #
        
        if self.cache.keys(pattern=f"data:autoresponder_event:{message.guild.id}:*"):
            async def do_autoresponder_event(_type: str):
                if self.cache.ratelimited(f"rl:autoresponder:{message.guild.id}", 5, 30):
                    return
                
                data = self.cache.get(f"data:autoresponder_event:{message.guild.id}:{_type}")
                
                async with self.cache.lock(f"autoresponder:{message.guild.id}"):
                    return EmbedScript(data.response).send(
                        context,
                        guild=message.guild,
                        user=message.author
                    )

            autoresponder_events = tuple(
                record.split(":")[::-1][0]
                for record in self.cache.keys(pattern=f"data:autoresponder_event:{message.guild.id}:*")
            )
                        
            if "images" in autoresponder_events and any(tuple(
                attachment.content_type.startswith(("image/", "video/"))
                for attachment in message.attachments
            )):
                self.loop.create_task(do_autoresponder_event("images"))
            
            if "spoilers" in autoresponder_events and (message.content.count("||") > 2):
                self.loop.create_task(do_autoresponder_event("spoilers"))
                
            if "emojis" in autoresponder_events and find_emojis(message.content):
                self.loop.create_task(do_autoresponder_event("emojis"))
    
            if "stickers" in autoresponder_events and message.stickers:
                self.loop.create_task(do_autoresponder_event("stickers"))
            
        # -- Autoreaction words -- #
        
        if self.cache.keys(pattern=f"data:autoreaction:{message.guild.id}:*"):
            async def do_autoreaction():
                """
                Performs an autoreact action based on keywords and reactions.
                
                Returns:
                    If the function is rate-limited, the function returns immediately.
                    If any of the keywords in the message content match the autoreact keywords, it adds the corresponding reactions to the message.
                """
                
                if self.cache.ratelimited(f"rl:autoreaction:{message.guild.id}", 5, 30):
                    return
                
                for keyword in tuple(
                    record.split(":")[::-1][0]
                    for record in self.cache.keys(pattern=f"data:autoreaction:{message.guild.id}:*")
                ):
                    await sleep(1e-3)
                    
                    if keyword in message.content:
                        async with self.cache.lock(f"autoreaction:{message.guild.id}"):
                            return gather(*(
                                message.add_reaction(b64decode(reaction.encode()).decode() if len(tuple(reaction)) > 1 else reaction)
                                for reaction in self.cache.smembers(f"data:autoreaction:{message.guild.id}:{keyword}")[:20]
                            ))
                
            self.loop.create_task(do_autoreaction())
            
        # -- Autoreaction events -- #
        
        if self.cache.keys(pattern=f"data:autoreaction_event:{message.guild.id}:*"):
            async def do_autoreact_event(_type: str):
                if self.cache.ratelimited(f"rl:autoreaction:{message.guild.id}", 5, 30):
                    return

                async with self.cache.lock(f"autoreaction:{message.guild.id}"):
                    gather(*(
                        message.add_reaction(b64decode(reaction.encode()).decode() if len(tuple(reaction)) < 1 else reaction)
                        for reaction in self.cache.smembers(f"data:autoreaction_event:{message.guild.id}:{_type}")[:20]
                    ))
            
            autoreaction_events = tuple(
                record.split(":")[::-1][0]
                for record in self.cache.keys(pattern=f"data:autoreaction_event:{message.guild.id}:*")
            )
            
            if "images" in autoreaction_events and message.attachments:
                self.loop.create_task(do_autoreact_event("images"))
            
            if "spoilers" in autoreaction_events and (message.content.count("||") > 2):
                self.loop.create_task(do_autoreact_event("spoilers"))
                
            if "emojis" in autoreaction_events and find_emojis(message.content):
                self.loop.create_task(do_autoreact_event("emojis"))
    
            if "stickers" in autoreaction_events and message.stickers:
                self.loop.create_task(do_autoreact_event("stickers"))

        # -- Color reposting -- #
                
        async def do_color_reposting():
            async with self.cache.semaphore(f"color_reposting:{message.guild.id}", 2):
                if message.content == "##":
                    return await context.invoke(
                        self.get_command("color"),
                        sources=TUPLE
                    )
                
                colors = [ ]

                for word in message.content.split():
                    await sleep(1e-3)

                    with suppress(Exception):
                        if not word.startswith("#"):
                            return
                        
                        colors.append(await Color().convert(..., word))
                    
                if not colors:
                    return
                
                return await context.invoke(
                    self.get_command("color"),
                    sources=colors
                )
        
        self.loop.create_task(do_color_reposting())
        
        # -- Media Reposting -- #
        
        async def do_youtube_reposting():
            async with self.cache.semaphore(f"media_reposting:{message.guild.id}", 2):
                if (links := expressions.youtube_url.findall(message.content)) and message.content.lower().startswith(f"{self.user.name.lower()} "):
                    await message.delete()
                    
                    if not (data := await self.data_processing.fetch_youtube_post(links[0])).url:
                        return
                    
                    return await context.send(
                        file=File(
                            fp=BytesIO(await (await self.session.session().get(data.url)).read()),
                            filename="Vile YouTube.mp4"
                        ),
                        embed=(
                            Embed(
                                color=self.color,
                                description=data.description
                            )
                            .set_author(
                                name=f"@{data.author.name} - {data.title} | {fmtseconds(data.duration)} long",
                                icon_url="https://cdn.discordapp.com/emojis/1214858039065190403.png",
                                url=data.original_url,
                            )
                            .set_footer(text=f"💬 {data.comment_count:,} ({data.view_count:,} views)"
                            )
                        )
                    )
                    
        self.loop.create_task(do_youtube_reposting())
        
        async def do_instagram_reposting():
            async with self.cache.semaphore(f"media_reposting:{message.guild.id}", 2):
                if (links := expressions.instagram_url.findall(message.content)) and message.content.lower().startswith(f"{self.user.name.lower()} "):
                    await message.delete()
                    
                    data = await self.data_processing.fetch_instagram_post(links[0])
                    item = data.items[0]
                    
                    if not item.video_versions:
                        return
                    
                    return await context.send(
                        file=File(
                            fp=BytesIO(await (await self.session.session().get(item.video_versions[0].url)).read()),
                            filename="Vile Instagram.mp4"
                        ),
                        embed=(
                            Embed(
                                color=self.color,
                                description=item.caption.text
                            )
                            .set_author(
                                name=f"@{item.owner.full_name}",
                                icon_url="https://cdn.discordapp.com/emojis/1214909204780027964.png",
                                url=item.video_versions[0].url,
                            )
                            .set_footer(text=f"💬 {item.comment_count:,} | 👍 {item.like_count:,} (N views)"
                            )
                        )
                    )
                    
        self.loop.create_task(do_instagram_reposting())

        # -- Voice Message Transcription -- #
        
        async def do_transcription():
            async with self.cache.semaphore(f"transcription:{message.guild.id}", 2):
                if message.attachments and message.attachments[0].filename.endswith(".ogg"):
                    return await context.reply(
                        await self.data_processing.transcribe(
                            message.attachments[0].url,
                            format="ogg"
                        )
                    )

        self.loop.create_task(do_transcription())
        
        # -- AFK module -- #
        
        async def do_afk():
            if self.cache.ratelimited(f"rl:afk:{message.channel.id}", 2, 5):
                return
                
            embeds = [ ]
            
            if record := self.cache.get(f"data:afk:{message.guild.id}:{message.author.id}"):
                _, last_at = record.values() 
                self.cache.delete(f"data:afk:{message.guild.id}:{message.author.id}")
                
                return await context.respond(
                    f"Welcome back {message.author.mention}, you were last seen {arrow.get(last_at).humanize()}.",
                    color=BaseColor.dark_embed(), emoji="<a:vile_afk:1002923032844718102>"
                )
            
            for member in message.mentions:
                if record := self.cache.get(f"data:afk:{message.guild.id}:{member.id}"):
                    status, last_at = record.values()

                    embeds.append(
                        Embed(
                            color=BaseColor.dark_embed(), 
                            description=f"> **Reason:** {status}"
                        )
                        .set_author(
                            name=f"{member} is currently afk",
                            icon_url=member.display_avatar,
                        )
                        .set_footer(text=f"Last seen {arrow.get(last_at).humanize()}")
                    )
                
            if embeds:
                return await message.reply(embeds=embeds[:10])
        
        if not context.command or context.command.qualified_name != "afk":
            self.loop.create_task(do_afk())
        
        await self.process_commands(message)
        
        
    async def on_message_delete(self: "VileBot", message: BaseMessage):
        """
        Handle the event of a message being deleted.

        Parameters:
            message (BaseMessage): The message that was deleted.
        """
        
        await self.wait_until_ready()
        
        # -- Ignore DMs and bots -- #
        
        if message.guild is None or message.author.bot:
            return
        
        # -- Log deleted message -- #
        
        self.cache.sadd(
            f"snipes:delete:{message.guild.id}:{message.channel.id}",
            (message, Date.now(Timezone("America/New_York")))
        )
    
        
    async def on_message_edit(
        self: "VileBot", 
        before: BaseMessage, 
        after: BaseMessage
    ):
        """
        Handle the event of a message being edited.

        Parameters:
            before (BaseMessage): The message before being edited.
            after (BaseMessage): The message after being edited.
        """

        await self.wait_until_ready()
        
        # -- Ignore DMs and bots -- #
        
        if after.guild is None or after.author.bot:
            return
        
        # -- Log edited message -- #
        
        self.cache.sadd(
            f"snipes:edit:{after.guild.id}:{after.channel.id}",
            (before, Date.now(Timezone("America/New_York")))
        )
        
        # -- Process commands -- #
        
        if before.content != after.content:
            await self.process_commands(after)
            
        # -- Archive pins -- #
        
        if not (before.pinned is False and after.pinned is True):
            return

        if not (config := self.cache.get(f"data:pins:{after.guild.id}")):
            return

        if config.is_enabled == False or not (channel := after.guild.get_channel(config.channel_id)):
            return

        embed = Embed(
            color=after.author.color, 
            description=after.content + (("\n" + "\n".join(attachment.url for attachment in after.attachments)) if after.attachments else ""),
            timestamp=after.created_at
        )

        embed.set_author(name=after.author, icon_url=after.author.display_avatar)
        embed.set_footer(text=f"Pin archived from #{channel.name}")
        
        if after.attachments:
            embed.set_image(url=after.attachments[0].url)
            
        with suppress(HTTPException):
            await channel.send(
                embed=embed,
                view=View().add_item(
                    Button(
                        label="Jump to Message",
                        style=ButtonStyle.link,
                        url=after.jump_url
                    )
                )
            )

            await after.unpin()
    
        
    async def on_user_update(
        self: "VileBot", 
        before: BaseUser, 
        after: BaseUser
    ):
        """
        Handles user updates.

        Parameters:
            before (BaseUser): The user object before the update.
            after (BaseUser): The user object after the update.
        """

        await self.wait_until_ready()
        
        # -- Avatar History -- #
        if before.display_avatar.url != after.display_avatar.url:
            try:
                avatar = await before.avatar.to_file()
            
            except Exception:
                avatar = await after.avatar.to_file()
            
            finally:
                message = await self.get_channel(1256851790985560145).send(file=avatar)
                await self.redis.lpush(f"data:avatars:{after.id}", message.attachments[0].url)
        
        # -- Name history -- #
        if before.name != after.name:
            await self.redis.lpush(f"data:usernames:{after.id}", before.name)
            await self.db.execute(
                "INSERT INTO name_history (user_id, name, updated_on) VALUES (%s, %s, %s);",
                before.id, encrypt(str(before)), Date.now()
            )
            
            
    async def on_member_update(
        self: "VileBot", 
        before: BaseMember, 
        after: BaseMember
    ):
        """
        Handle member updates in the guild.

        Parameters:
            before (BaseMember): The member object before the update.
            after (BaseMember): The member object after the update.
        """

        await self.wait_until_ready()
        
        if before.nick != after.nick:
            await self.redis.sadd(f"data:nicknames:{after.guild.id}:{after.id}", before.nick)
        
        # -- Boost related events -- #
        
        if after.guild.premium_subscriber_role not in before.roles and after.guild.premium_subscriber_role in after.roles:
            self.dispatch("member_boost", after)
            
        elif after.guild.premium_subscriber_role in before.roles and after.guild.premium_subscriber_role not in after.roles:
            self.dispatch("member_unboost", after)
            
        # -- Force nickname -- #
        
        elif before.nick != after.nick:
            forced = False
            
            if after.guild.me.guild_permissions.manage_nicknames is True:
                if forced_nickname := self.cache.get(f"fn{after.guild.id}-{after.id}"):
                    if after.nick != forced_nickname:
                        slept = False

                        if time_remaining := self.cache.ratelimited(f"rl:fn{after.guild.id}", 3, 10):
                            await sleep(time_remaining)
                            slept = True

                        if slept is False:
                            await sleep(1.5)

                        if after.nick != forced_nickname:
                            await after.edit(
                                nick=forced_nickname,
                                reason=f"{self.user.name.title()} Moderation: Forced nickname"
                            )

                            forced = True
            
            # -- Filter nicknames -- #
            
            if forced is False and self.cache.get(f"fn{after.guild.id}-{after.id}") is None:
                if after.top_role.position < after.guild.me.top_role.position and after.id != after.guild.owner_id:
                    filter_events = tuple(
                        record.split(":")[::-1][0]
                        for record in self.cache.keys(pattern=f"data:filter_event:{after.guild.id}:*")
                    )
                    
                    if "nicknames" in filter_events and self.cache.get(f"data:filter_event:{after.guild.id}:nicknames").is_enabled == True:
                        if after.guild.id in self.bot.cache.keys(pattern=f"data:filter:*"):
                            if after.nick in self.bot.cache.smembers(f"data:filter:{after.guild.id}"):
                                await after.edit(
                                    nick=None,
                                    reason=f"{self.user.name.title()} Moderation: Nickname contains a filtered word"
                                )
            
    
    async def on_member_join(self: "VileBot", member: BaseMember):
        """
        Handles the event when a member joins the server.

        Parameters:
            member (BaseMember): The member who joined the server.
        """

        await self.wait_until_ready()
        
        await self.redis.srem(f"data:guilds:leaves:{member.id}", member.guild.id)
        await self.redis.sadd(f"data:guilds:{member.id}", member.guild.id)
        
        # -- Hard ban -- #
        
        if member.id in await self.db.fetch(
            "SELECT user_id FROM hard_banned WHERE guild_id = %s;", 
            member.guild.id
        ):
            return await member.ban(reason=f"{self.user.name.title()} Moderation: User is hard banned")
                
        # -- Welcome message -- #
        
        if member.guild.id in self.cache.welcome_settings:
            if self.cache.ratelimited(f"rl:welcome_message{member.guild.id}", 5, 30):
                return
            
            for channel_id in self.cache.welcome_settings[member.guild.id]:
                if (channel := self.get_channel(channel_id)) is not None and channel.permissions_for(member.guild.me).send_messages is True:
                    if self.cache.welcome_settings[member.guild.id][channel_id]["is_enabled"] == True:
                        self.loop.create_task(EmbedScript(self.cache.welcome_settings[member.guild.id][channel_id]["message"]).send(
                            channel,
                            guild=member.guild,
                            user=member
                        ))
                        
        # -- Mute bypassing -- #
        
        if await self.db.fetchrow("SELECT * FROM muted_user WHERE guild_id = %s AND user_id = %s LIMIT 1;", member.guild.id, member.id):
            if mute_role_id := await self.db.fetchval("SELECT mute_role_id FROM guild_settings WHERE guild_id = %s;", member.guild.id):
                if mute_role := member.guild.get_role(mute_role_id):
                    await member.add_roles(
                        mute_role,
                        reason=f"{self.user.name.title()} Moderation: Member is muted"
                    )
                    
        # -- Jail bypassing -- #
        
        if await self.db.fetchrow("SELECT * FROM jailed_user WHERE guild_id = %s AND user_id = %s LIMIT 1;", member.guild.id, member.id):
            if jail_role_id := await self.db.fetchval("SELECT jail_role_id FROM guild_settings WHERE guild_id = %s;", member.guild.id):
                if jail_role := member.guild.get_role(jail_role_id):
                    await member.add_roles(
                        jail_role,
                        reason=f"{self.user.name.title()} Moderation: Member is jailed"
                    )
        
        # -- Sticky roles -- #
        
        # if member.id in self.cache.smembers(f"srm{member.guild.id}"):
        #     await gather(*(
        #         member.add_roles(
        #             member.guild.get_role(role_id),
        #             reason="Sticky role"
        #         )
        #         for role_id in self.cache.sticky_roles[member.guild.id]
        #         if member.guild.get_role(role_id)
        #     ))
                        
            
    async def on_member_remove(self: "VileBot", member: BaseMember):
        """
        Handle the event when a member leaves the server.

        Parameters:
            member (BaseMember): The member who left the server.
        """
        
        await self.wait_until_ready()
        
        await self.redis.srem(f"data:guilds:{member.id}", member.guild.id)
        await self.redis.sadd(f"data:guilds:leaves:{member.id}", member.guild.id)

        # -- Add restore roles -- #
        
        if member.roles:
            self.cache.sadd(
                f"restore-{member.guild.id}-{member.id}", 
                *member.roles
            )
        
        # -- Add sticky roles -- #
        
        if member.guild.id in self.cache.sticky_roles:
            self.cache.sadd(
                f"sticky_roles-{member.guild.id}-{member.id}", 
                *(role for role in member.roles if role.id in self.cache.sticky_roles[member.guild.id])
            )
        
        # -- Leave message -- #
        
        if member.guild.id in self.cache.leave_settings:
            if self.cache.ratelimited(f"rl:leave_message{member.guild.id}", 5, 30):
                return

            for channel_id in self.cache.leave_settings[member.guild.id]:
                if (channel := self.get_channel(channel_id)) is not None and channel.permissions_for(member.guild.me).send_messages is True:
                    if self.cache.leave_settings[member.guild.id][channel_id]["is_enabled"] == True:
                        self.loop.create_task(EmbedScript(self.cache.leave_settings[member.guild.id][channel_id]["message"]).send(
                            channel,
                            guild=member.guild,
                            user=member
                        ))
                        
                        
    # async def on_raw_reaction_add(self: "VileBot", payload: RawReactionActionEvent):
    #     """
    #     An event handler that is triggered when a raw reaction is added to a message.
        
    #     Parameters:
    #         payload (RawReactionActionEvent): The payload containing information about the reaction event.
    #     """

    #     await self.wait_until_ready()

    #     if (
    #         payload.member is None 
    #         or payload.member.bot 
    #         or payload.member.guild.me.guild_permissions.administrator is False
    #     ):
    #         return
            
    #     if payload.guild_id in self.cache.pagination and payload.guild_id in self.cache.pagination_pages:
    #         if (
    #             payload.message_id in self.cache.pagination[payload.guild_id]
    #             and payload.message_id in self.cache.pagination_pages[payload.guild_id]
    #         ):
    #             channel = self.get_channel(payload.channel_id)
    #             message = await channel.fetch_message(payload.message_id)
                
    #             if str(payload.emoji) == "<:v_left_page:1067034010624200714>":
    #                 await message.remove_reaction(
    #                     payload.emoji, 
    #                     payload.member
    #                 )
                    
    #                 current_page = self.cache.pagination[payload.guild_id][message.id]
    #                 page_count = len(self.cache.pagination_pages[payload.guild_id][message.id])
                    
    #                 if current_page == 1:
    #                     return
                        
    #                 new_page, *_ = next(
    #                     filter(
    #                         lambda page: page[1] == current_page-1, 
    #                         self.cache.pagination_pages[payload.guild_id][message.id]
    #                     ), 
    #                     (None,)
    #                 )

    #                 if not new_page[0]:
    #                     return
                        
    #                 await self.db.execute(
    #                     "UPDATE pagination SET current_page = %s WHERE message_id = %s;", 
    #                     current_page-1, message.id
    #                 )
                    
    #                 self.cache.pagination[payload.guild_id][message.id] = current_page-1
                    
    #                 script = EmbedScript(await pagination_replacement(
    #                     new_page, 
    #                     payload.member.guild, 
    #                     current_page-1, 
    #                     page_count
    #                 ))

    #                 await script.parse()
    #                 del script.objects["files"]
    #                 await message.edit(**script.objects)
                

    #             if str(payload.emoji) == "<:v_right_page:1067034017108607076>":
    #                 await message.remove_reaction(payload.emoji, payload.member)
    #                 current_page = self.cache.pagination[payload.guild_id][message.id]
    #                 page_count = len(self.cache.pagination_pages[payload.guild_id][message.id])
                    
    #                 if current_page == page_count:
    #                     return
                        
    #                 new_page, *_ = next(
    #                     filter(
    #                         lambda page: page[1] == current_page+1, 
    #                         self.cache.pagination_pages[payload.guild_id][message.id]
    #                     ), 
    #                     (None,)
    #                 )

    #                 if not new_page[0]:
    #                     return
                        
    #                 await self.db.execute(
    #                     "UPDATE pagination SET current_page = %s WHERE message_id = %s;", 
    #                     current_page+1, message.id
    #                 )

    #                 self.cache.pagination[payload.guild_id][message.id] = current_page+1
                        
    #                 script = EmbedScript(await pagination_replacement(
    #                     new_page, 
    #                     payload.member.guild, 
    #                     current_page-1, 
    #                     page_count
    #                 ))

    #                 await script.parse()
    #                 del script.objects["files"]
    #                 await message.edit(**script.objects)
                    
            
    async def on_command(self: "VileBot", ctx: "Context"):
        """
        Handles a command event.

        Parameters:
            ctx (Context): The context object representing the command event.
        """

        self.logger.warning(f"{ctx.author} ({ctx.author.id}) in ({ctx.guild} - {ctx.guild.id}): {ctx.message.content}")
        
        # -- Increment command usage -- #
        
        await self.db.execute(
            "INSERT INTO command_usage (user_id, command_name, uses) VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE uses = uses+1;",
            ctx.author.id, ctx.command.qualified_name
        )
        
    
    async def on_command_error(self, ctx: "Context", error: Any):
        """
        Handle errors that occur during command execution.

        Parameters:
            ctx (Context): The context in which the conversion is being performed.
            error (Any): The error that occurred during command execution.
        """

        await self.wait_until_ready()
        self.logger.warning(f"{ctx.author} ({ctx.invoked_with} - {type(error).__name__}): {error}")
        
        # -- Ignore unhandled errors -- #
        
        if isinstance(error, (
            NotOwner,
            AssertionError
        )):
            return
            
        # -- Check for command aliases -- #
        
        if isinstance(error, CommandNotFound):
            if self.cache.keys(pattern=f"data:aliases:{ctx.guild.id}:*"):
                commands = tuple(
                    record.split(":")[::-1][0]
                    for record in self.cache.keys(pattern=f"data:aliases:{ctx.guild.id}:*")
                )

                for command in commands:
                    await sleep(1e-3)

                    for alias in self.cache.smembers(f"data:aliases:{ctx.guild.id}:{command}"):
                        await sleep(1e-3)
                        
                        if ctx.message.content.lower().startswith(ctx.prefix+alias.lower()):
                            ctx.message.content = ctx.message.content.replace(alias, command)
                            
                            with suppress(Exception):
                                return await self.invoke(await self.get_context(ctx.message))

                return

            return
        
        # -- Handle lack of privileges -- #
        
        if isinstance(error, BotMissingPermissions):
            permission = error.missing_permissions[0].lower().replace("_", " ").title()
            return await ctx.error(f"I'm missing the **{permission}** permission.")

        if isinstance(error, MissingPermissions):
            permission = error.missing_permissions[0].lower().replace("_", " ").title()
            return await ctx.error(f"You're missing the **{permission}** permission.")

        # -- Handle command cooldown -- #
        
        if isinstance(error, CommandOnCooldown):
            if self.cache.ratelimited(f"rl:cooldown_message{ctx.author.id}", 1, error.retry_after):
                return
            
            return await ctx.error(
                f"You're on a [**cooldown**](https://discord.com/developers/docs/topics/rate-limits) & cannot use `{ctx.invoked_with}` for **{fmtseconds(error.retry_after)}**.",
                delete_after=error.retry_after
            )

        # -- Handle object not found -- #
        
        if isinstance(error, MemberNotFound):
            return await ctx.error("I couldn't find that member.")

        if isinstance(error, UserNotFound):
            return await ctx.error("I couldn't find that user.")

        if isinstance(error, ChannelNotFound):
            return await ctx.error("I couldn't find that channel.")

        if isinstance(error, RoleNotFound):
            return await ctx.error("I couldn't find that role.")

        if isinstance(error, EmojiNotFound):
            return await ctx.error("I couldn't find that emoji.")
        
        if isinstance(error, GuildStickerNotFound):
            return await ctx.error("I couldn't find that sticker.")

        if isinstance(error, GuildNotFound):
            return await ctx.error("I couldn't find that guild.")

        if isinstance(error, BadInviteArgument):
            return await ctx.error("I couldn't find that invite.")
        
        if isinstance(error, BadBoolArgument):
            return await ctx.error("Please provide a **valid** true/false value.")

        if isinstance(error, (MissingRequiredArgument, SendHelp)):
            return await ctx.send_help(ctx.command.qualified_name)
        
        # -- Handle malformed arguments -- #
        
        if isinstance(error, BadArgument):
            return await ctx.error(
                multi_replace(
                    error.args[0].lower(), {
                        '"': "**", 
                        "int": "number", 
                        "str": "text"
                    }
                )[:-1].capitalize().replace(
                    "Converting to ", 
                    "Converting to a "
                ).replace(
                    "for parameter ",
                    "for the parameter "
                ) + "."
            )

        if isinstance(error, BadUnionArgument):
            return await ctx.error(
                multi_replace(
                    error.args[0].lower(), {
                        "could not convert": "i couldn't convert the parameter",
                        '"': "**", 
                        "into": "into a", 
                        "member": "**member**", 
                        "user": "**user**", 
                        "guild": "**server**", 
                        "invite": "**server invite**"
                    }
                )[:-1].capitalize() + "."
            )
        
        # -- Handle concurrency -- #
        
        if isinstance(error, MaxConcurrencyReached):
            return await ctx.error(f"This command can only be ran {error.number} time{'s' if error.number > 1 else ''} concurrently {'globally' if error.per.name == 'default' else f'per {error.per.name}'}.")
        
        # -- Handle API errors -- #
        
        if isinstance(error, HTTPException):
            if "Invalid Form Body" in error.text:
                if "Cannot send an empty message" in error.text:
                    return await ctx.error(f"The message I'm trying to send doesn't contain any content.")
                
                if "Must be 4000 or fewer in length." in error.text:
                    return await ctx.error(f"The message I'm trying to send is **too long**.")
                
                return await ctx.error(f"The message I'm trying to send is **malformed**.\n```{error.text}```")
            
        if isinstance(error, CommandInvokeError):
            if isinstance(error.original, ClientConnectorError):
                return await ctx.error("The **API** is currently unavailable.")

            if isinstance(error.original, ContentTypeError):
                return await ctx.error(f"The **API** returned a malformed response*.")
            
        if isinstance(error, NotFound):
            return await ctx.error(f"I couldn't find that {error.text.split()[::-1][0].lower()}.")
            
        if isinstance(error, Forbidden):
            return await ctx.error("I'm missing the required permissions to do that.")
        
        # -- Handle custom errors -- #

        if isinstance(error, CheckFailure):
            return
        
        if isinstance(error, CommandError):
            ret = str(error).replace("Command raised an exception: ", "")
            
            if ret[0].islower():
                ret[0] = ret[0].upper()

            if ret[-1] != ".":
                ret += "."

            return await ctx.error(
                ret,
                delete_after=None
            )
        
        # -- Send unhandled error code -- #
        
        self.cache.set(f"exceptions:{(error_code := tuuid.tuuid())}", Munch({
            "ctx": ctx,
            "error": error
        }))

        self.bot.loop.create_task(self.report_exception(
            code=error_code,
            ctx=ctx,
            exception=self.cache.get(f"exceptions:{error_code}")
        ))
            
        return await ctx.error(f"Something went wrong while executing this command ([**{error_code}**](https://discord.gg/KsfkG3BZ4h))")
    
    
def multi_replace(text: str, to_replace: Dict[ str, str ], once: bool = False) -> str:
    """
    Replaces multiple occurrences of substrings in a given text.

    Parameters:
        text (str): The original text in which the replacements will be made.
        to_replace (Dict[str, str]): A dictionary containing the substrings to replace
            as keys and their corresponding replacement strings as values.
        once (bool, optional): If set to True, only the first occurrence of each
            substring will be replaced. Defaults to False.

    Returns:
        str: The modified text after performing the replacements.
    """
    
    for r1, r2 in to_replace.items():
        if r1 in text:
            if once:
                text = text.replace(str(r1), str(r2), 1)
            else:
                text = text.replace(str(r1), str(r2))
            
    return text


async def resolve_variables(script: str, models: List[BaseModel]) -> str:
    """
    Resolves variables in a script by replacing placeholders with actual values.
    
    Parameters:
        script (str): The script containing placeholders to be replaced.
        **kwargs (Dict[str, Any]): Additional keyword arguments that contain the values of the variables to be replaced.
        
    Returns:
        str: The script with the placeholders replaced by actual values.
    """
    
    for model in models:
        await sleep(1e-3)

        script = script.replace(
            "{" + model.__repr_name__().replace("EUser", "User").lower() + "}",
            str(model)
        )

        for key, value in model.dict().items():
            await sleep(1e-3)
            
            script = script.replace(
                "{" + f"{model.__repr_name__().replace('EUser', 'User').lower()}.{key}" + "}", 
                str(value)
            )
  
    return script
        
 
class EmbedScript:
    def __init__(
        self: "EmbedScript", 
        script: str,
        models: Optional[List[BaseModel]] = None
    ) -> NoReturn:
        self.script = script.replace(r"\n", "\n")
        self.argument_delimeter = "&&"
        self.data_processing = DataProcessing()
        self.models = models or [ ]
        
        self.objects = {
            "content": None,
            "embeds": [ ],
            "files": [ ],
            "view": View(),
            "delete_after": None
        }
        
        
    def _validate_url(self: "EmbedScript", index: int, name: str, value: str) -> NoReturn:
        """
        Validates the URL for a given embed tag in an embed script.

        Parameters:
            index (int): The index of the embed tag.
            name (str): The name of the embed tag.
            value (str): The value of the embed tag.
        """

        if len(split := value.strip().split()) > 1:
            raise CommandError(f"The **{name}** tag in embed `{index}` expected one whole word, got {len(split)}.")
                    
        if not expressions.link.match(value.strip()):
            raise CommandError(f"The value for the **{name}** tag in embed `{index}` couldn't be validated.")
        
        
    def _validate_image(self: "EmbedScript", index: int, name: str, value: str) -> NoReturn:
        """
        Validates an image URL for a specific embed tag.

        Parameters:
            index (int): The index of the embed tag.
            name (str): The name of the embed tag.
            value (str): The value of the embed tag.

        Raises:
            CommandError: If the value for the embed tag couldn't be validated.
        """

        self._validate_url(index, name, value)
        if not (mime := URL(value).suffix) or mime not in (
            ".jpeg", 
            ".png", 
            ".gif", 
            ".jpg", 
            ".mp4", 
            ".mov", 
            ".wmv", 
            ".webm", 
            ".mp3", 
            ".mpeg"
        ):
            raise CommandError(f"The value for the **{name}** tag in embed `{index}` couldn't be validated.")
        

    def get_tags(self: "EmbedScript", script: str) -> List[Tuple[str]]:
        """
        Retrieves the tags from the given script.

        Parameters:
            script (str): The script from which to retrieve the tags.

        Returns:
            List[Tuple[str]]: A list of tuples containing the tags found in the script.
        """

        return expressions.tag.findall(script)

    def add_file(self: "EmbedScript", source: bytes, filename: str) -> NoReturn:
        """
        Adds a file to the embed script.

        Parameters:
            source (BytesIO): The source of the file.
            filename (str): The name of the file.
        """

        self.objects["files"].append(File(
            BytesIO(source), 
            filename
        ))
    

    def resolve_methods(self: "EmbedScript", script: str) -> str:
        """
        Resolve the methods in the script and replace them with their corresponding values.

        Parameters:
            script (str): The script to be processed.

        Returns:
            str: The processed script with the methods resolved.
        """

        for method in ("upper", "lower", "title", "len", "http", "quote"):
            script = multi_replace(script, {
                f"{method}({v})": (
                    v.upper() if method == "upper" 
                    else v.lower() if method == "lower" 
                    else v.title() if method == "title" 
                    else (int(v.strip()) if v.strip().isnumeric() else len(v)) if method == "len"
                    else urllib.parse.quote(v.strip(), safe="")
                )
                for v in re.findall(rf"{method}\((.*?)\)", script) 
            })

        for name, value in self.get_tags(script): 
            if name == "upper":
                script = script.replace(
                    f"{{{name}: {value}}}", 
                    value.strip().upper()
                )

            elif name == "lower":
                script = script.replace(
                    f"{{{name}: {value}}}", 
                    value.strip().lower()
                )

            elif name == "title":
                script = script.replace(
                    f"{{{name}: {value}}}", 
                    value.strip().title()
                )

            elif name == "len":
                script = script.replace(
                    f"{{{name}: {value}}}", 
                    int(value.strip())
                    if value.strip().isnumeric()
                    else len(value.strip())
                )

            elif name == "strip":
                if len(sliced := value.strip().split(self.argument_delimeter)) != 2: 
                    continue
                
                text, removal = (item.strip() for item in sliced)
                script = script.replace(
                    f"{{{name}: {value}}}", 
                    text.replace(removal, "")
                )

            elif name in ("random", "choose", "choice"):
                if len(sliced := value.strip().split(self.argument_delimeter)) < 2: 
                    continue

                script = script.replace(
                    f"{{{name}: {value}}}", 
                    choice(tuple(c.strip() for c in sliced))
                )

            elif name in ("if", "%"):
                if len(sliced := value.strip().split(self.argument_delimeter)) < 3: 
                    continue

                condition, value_if_true, value_if_false = (item.strip() for item in sliced)

                if "==" in condition:
                    condition = condition.split("==")
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if condition[0].lower().strip() == condition[1].lower().strip() 
                        else value_if_false
                    )

                elif "!=" in condition:
                    condition = condition.split("!=")
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if condition[0].lower().strip() != condition[1].lower().strip() 
                        else value_if_false
                    )
                    
                elif "<>" in condition:
                    condition = condition.split("<>")
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if condition[0].lower().strip() != condition[1].lower().strip() 
                        else value_if_false
                    )

                elif "<=" in condition:
                    condition = condition.split("<=")

                    if not condition[0].strip().isnumeric() or not condition[1].strip().isnumeric():
                        continue

                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if int(condition[0].strip()) <= int(condition[1].strip()) 
                        else value_if_false
                    )

                elif ">=" in condition:
                    condition = condition.split(">=")

                    if not condition[0].strip().isnumeric() or not condition[1].strip().isnumeric():
                        continue

                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if int(condition[0].strip()) >= int(condition[1].strip()) 
                        else value_if_false
                    )

                elif "<" in condition:
                    condition = condition.split("<")

                    if not condition[0].strip().isnumeric() or not condition[1].strip().isnumeric():
                        continue
                    
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if int(condition[0].strip()) < int(condition[1].strip()) 
                        else value_if_false
                    )

                elif ">" in condition:
                    condition = condition.split(">")

                    if not condition[0].strip().isnumeric() or not condition[1].strip().isnumeric():
                        continue

                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if int(condition[0].strip()) > int(condition[1].strip()) 
                        else value_if_false
                    )

                elif "startswith" in condition:
                    condition = condition.split("startswith")
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if condition[0].lower().strip().startswith(condition[1].lower().strip()) 
                        else value_if_false
                    )

                elif "endswith" in condition:
                    condition = condition.split("endswith")
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if condition[0].lower().strip().endswith(condition[1].lower().strip()) 
                        else value_if_false
                    )

                elif "contains" in condition:
                    condition = condition.split("contains")
                    to_check = condition[0].lower().strip()
                    
                    if condition[0].strip().startswith("[") and condition[0].strip().endswith("]"):
                        if condition[0].strip().count(",") > 25:
                            continue
                            
                        if (condition[0].strip().count("[") > 1) or (condition[0].strip().count("]") > 1):
                            continue
                            
                        with suppress(Exception):
                            to_check = map(str, orjson.loads(condition[0].lower().strip()))

                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if condition[1].lower().strip() in to_check
                        else value_if_false
                    )

                elif "excludes" in condition:
                    condition = condition.split("excludes")
                    to_check = condition[0].lower().strip()
                    
                    if condition[0].strip().startswith("[") and condition[0].strip().endswith("]"):
                        if condition[0].strip().count(",") > 25:
                            continue
                            
                        if (condition[0].strip().count("[") > 1) or (condition[0].strip().count("]") > 1):
                            continue
                            
                        with suppress(Exception):
                            to_check = map(str, orjson.loads(condition[0].lower().strip()))
                    
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if condition[1].lower().strip() not in to_check
                        else value_if_false
                    )
                    
                elif "hasany" in condition:
                    condition = condition.split("hasany")
                    to_check = condition[0].lower().strip()
                    
                    if condition[0].strip().startswith("[") is False or condition[0].strip().endswith("]") is False:
                        return
                        
                    if condition[1].strip().startswith("[") is False or condition[1].strip().endswith("]") is False:
                        return
                    
                    if condition[0].strip().count(",") > 25:
                        continue
                            
                    if (condition[0].strip().count("[") > 1) or (condition[0].strip().count("]") > 1):
                        continue
                        
                    if condition[1].strip().count(",") > 25:
                        continue
                            
                    if (condition[1].strip().count("[") > 1) or (condition[1].strip().count("]") > 1):
                        continue
                            
                    try:
                        array_one = tuple(map(str, orjson.loads(condition[0].lower().strip())))
                        array_two = tuple(map(str, orjson.loads(condition[1].lower().strip())))
                        
                    except Exception:
                        continue
                        
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if any(item in array_one for item in array_two)
                        else value_if_false
                    )

                else:
                    script = script.replace(
                        f"{{{name}: {value}}}", 
                        value_if_true 
                        if condition in ("true", "1") 
                        else value_if_false
                    )

        return script

    
    async def parse(self: "EmbedScript", context: Optional[Context] = None) -> Optional[Dict[ str, Any ]]:
        """
        Parse the script and extract tags to create embeds for the message.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the embed data, or None if no tags were found.

        Raises:
            CommandError: If there are more than 10 embeds in the message.
            CommandError: If one of the tags in an embed is malformed.
            CommandError: If a tag in an embed is missing a value.
            CommandError: If the content tag exceeds the 2,000 character limit.
            CommandError: If the title tag in an embed exceeds the 256 character limit.
            CommandError: If the URL or URI tag in an embed is invalid.
            CommandError: If the description tag in an embed exceeds the 4,096 character limit.
            CommandError: If the color or colour tag in an embed is invalid.
            CommandError: If the footer tag in an embed exceeds the 2,048 character limit.
            CommandError: If the footer tag in an embed has more than 2 arguments.
            CommandError: If the image tag in an embed is invalid.
            CommandError: If the thumbnail tag in an embed is invalid.
            CommandError: If there are more than 10 files in the message.
            CommandError: If an attachment in an embed is too large.
            CommandError: If the author tag in an embed exceeds the 256 character limit.
            CommandError: If the author tag in an embed has more than 2 arguments.
            CommandError: If the field tag in an embed has more than 3 arguments.
            CommandError: If the field tag in an embed has a malformed name.
            CommandError: If the field tag in an embed has a malformed value.
            CommandError: If the field tag in an embed has a malformed inline value.
            CommandError: If the field tag in an embed has a name that exceeds the 256 character limit.
            CommandError: If the field tag in an embed has a value that exceeds the 256 character limit.
            CommandError: If the field tag in an embed does not have a valid inline value.
            CommandError: If the label tag in an embed does not have exactly 2 arguments.
            CommandError: If the label tag in an embed has a malformed name.
            CommandError: If the label tag in an embed has a malformed value.
            CommandError: If the label tag in an embed has a value that cannot be validated as a URL.
            CommandError: If the timestamp tag in an embed cannot be added because no other form body was found.
            CommandError: If the timestamp tag in an embed is not a valid unix timestamp or one of ('current', 'today', 'now').
            CommandError: If the timestamp tag in an embed cannot be converted to a valid unix timestamp.
        """
        
        for index, script in enumerate(self.script.split("{embed}"), start=1):
            if not (tags := self.get_tags(script)):
                continue

            if len(self.objects["embeds"]) == 10:
                 raise CommandError("Cannot add more embeds to the message.")

            self.objects["embeds"].append(embed := Embed())
            for name, value in tags:
                name = name.strip()
                value = self.resolve_methods(value.strip())
                
                if not name:
                    raise CommandError(f"One of the tags in embed `{index}` is malformed.")
                
                if not value:
                    raise CommandError(f"The **{name}** tag in embed `{index}` is missing a value.")
                
                if name in ("content", "message"):
                    if len(value) > 1980:
                        raise CommandError(f"The **content** tag exceeds the 2,000 character limit.")
                    
                    self.objects["content"] = value
 
                elif name == "title":
                    if len(value) > 256:
                        raise CommandError(f"The **title** tag in embed `{index}` exceeds the 256 character limit.")
                    
                    embed.title = value
 
                elif name in ("url", "uri"):
                    self._validate_url(index, name, value)
                    embed.url = value
  
                elif name in ("description", "desc"):
                    if len(value) >  4076:
                        raise CommandError(f"The **description** tag in embed `{index}` exceeds the 4,096 character limit.")
                    
                    embed.description = value
                    
                    
                elif name in ("color", "colour"):
                    if value == "dominant":
                        if not self.objects["files"] and not embed.image:
                            raise CommandError(f"The color 'dominant' was used in embed `{index}`, but no embed image was found.")

                        value = await dominant_color(
                            self.objects["files"][0].fp.read() 
                            if self.objects["files"] 
                            else embed.image.url
                        )
                    
                    else:
                        value = await Color().convert(..., value)
                    
                    embed.color = value
                    
                elif name == "footer":
                    if len(value) > 2028:
                        raise CommandError(f"The **footer** tag in embed `{index}` exceeds the 2,048 character limit.")
                    
                    if len(sliced := value.split(self.argument_delimeter)) > 2:
                        raise CommandError(f"The **footer** tag in embed `{index}` expected 2 or less arguments, got {len(sliced)}.")
                    
                    if len(sliced) == 1:
                        embed.set_footer(text=value)
                    
                    else:
                        text, icon_url = sliced
                        self._validate_image(index, name, icon_url)
                        
                        embed.set_footer(
                            text=text,
                            icon_url=icon_url
                        )
 
                elif name in ("image", "img"):
                    self._validate_image(index, name, value)
                    embed.set_image(url=value)
                    
                elif name == "thumbnail":
                    self._validate_image(index, name, value)
                    embed.set_thumbnail(url=value)
                    
                elif name in ("attach", "file"):
                    self._validate_url(index, name, value)
                    
                    if len(self.objects["files"]) == 10:
                        raise CommandError("Cannot add more files to the message.")
                        
                    with suppress(ClientResponseError):
                        explicit_report = await self.data_processing.determine_explicit(value)

                        if explicit_report.nudity or explicit_report.gore:
                            raise CommandError(f"The attachment `{len(self.objects['files'])+1}` contains explicit content.")
                    
                    filename = URL(value).name
                    url_hash = hash(value)

                    if not (cached_value := GLOBAL.CACHE.get(f"embed_attachment:{url_hash}")):
                        try:
                            downloaded_file = await HTTPClient(proxy=True).read(
                                value, 
                                filesize_limit=context and context.guild.filesize_limit or 2.62144e7
                            )
                        
                        except CommandError as error:
                            if "filesize" in str(error):
                                raise CommandError(f"The attachment `{len(self.objects['files'])+1}` is too large.")
                            
                            raise
                        
                        GLOBAL.CACHE.set(
                            f"embed_attachment:{url_hash}", 
                            downloaded_file,
                        )

                        self.add_file(downloaded_file, filename)

                    else:
                        self.add_file(cached_value, filename)
 
                elif name == "author":
                    if len(value) > 256:
                        raise CommandError(f"The **author** tag in embed `{index}` exceeds the 256 character limit.")
                    
                    if len(sliced := value.split(self.argument_delimeter)) > 2:
                        raise CommandError(f"The **author** tag in embed `{index}` expected 2 or less arguments, got {len(sliced)}.")
                    
                    if len(sliced) == 1:
                        embed.set_author(name=value)
                    
                    else:
                        name, icon_url = sliced
                        self._validate_image(index, name, icon_url)
                        
                        embed.set_author(
                            name=name,
                            icon_url=icon_url
                        )
                        
                elif name == "field":
                    if len(embed.fields) == 10:
                        raise CommandError(f"Cannot add more fields to embed `{index}`.")
                    
                    if len(sliced := value.split(self.argument_delimeter)) > 3:
                        raise CommandError(f"The **field** tag in embed `{index}` expected 2 or less arguments, got {len(sliced)}.")
                    
                    name, value, *other = sliced
                    name = name.strip()
                    value = value.strip()
                    inline = "true"
                    
                    for item in other:
                        inline = item.strip()
                        break
                        
                    if not name:
                        raise CommandError(f"The **field** tag in embed `{index}` has a malformed name.")
                
                    if not value:
                        raise CommandError(f"The **field** tag in embed `{index}` has a malformed value.")
                
                    if not inline:
                        raise CommandError(f"The **field** tag in embed `{index}` has a malformed inline value.")
                    
                    if len(name) > 256:
                        raise CommandError(f"The **field** tag in embed `{index}` has a name that exceeds the 256 character limit.")
                    
                    if len(value) > 1024:
                        raise CommandError(f"The **field** tag in embed `{index}` has a value that exceeds the 256 character limit.")
                    
                    if inline not in ("true", "false"):
                        raise CommandError(f"The **field** tag in embed `{index}` must have an inline value of either 'true' or 'false'.")
                    
                    embed.add_field(
                        name=name,
                        value=value,
                        inline=(inline == "true" and True or False)
                    )
                        
                elif name == "label":
                    if len(sliced := value.split(self.argument_delimeter)) != 2:
                        raise CommandError(f"The **label** tag in embed `{index}` expected 2 arguments, got {len(sliced)}.")
                    
                    label, link = sliced
                    label = label.strip()
                    link = link.strip()
                    
                    if not label:
                        raise CommandError(f"The **label** tag in embed `{index}` has a malformed name.")
                
                    if not link:
                        raise CommandError(f"The **label** tag in embed `{index}` has a malformed value.")
                
                    # if not URL(link).suffix:
                    #     raise CommandError(f"The **label** tag in embed `{index}` couldn't be validated.")
                    
                    if len(link) > 256:
                        raise CommandError(f"The **field** tag in embed `{index}` has a name that exceeds the 256 character limit.")
                    
                    self._validate_url(index, name, link)
                    
                    self.objects["view"].add_item(
                        Button(
                            style=ButtonStyle.link,
                            label=label,
                            url=link
                        )
                    )
            
                elif name == "timestamp":
                    if not embed.title and not embed.description and not embed.image.url and not embed.fields and not embed.thumbnail.url:
                        raise CommandError(f"Couldn't add a timestamp to embed `{index}`; no other form body was found.")
                    
                    if value.lower() in ("current", "today", "now"):
                        embed.timestamp = Date.now(Timezone("America/New_York"))
                
                    else:
                        try:
                            embed.timestamp = Date.fromtimestamp(int(value))

                        except TypeError:
                            raise CommandError(f"The **timestamp** tag in embed `{index}` must be a unix timestamp, or in ('current', 'today', 'now').")
                        
                        except OverflowError:
                            raise CommandError(f"The **timestamp** tag in embed `{index}` couldn't be converted to a valid unix timestamp..")
    
        if not self.get_tags(self.script):
            self.objects["content"] = self.resolve_methods(self.script.strip())
            
        for embed in self.objects["embeds"]:
            if not embed:
                self.objects["embeds"].remove(embed)
                del embed
        
    
    async def send(
        self: "EmbedScript", 
        destination: Union[ Context, TextChannel ], 
        **kwargs: Dict[ str, Any ]
    ) -> Optional[BaseMessage]:
        """
        Sends a message to the specified destination.

        Parameters:
            destination (Union[Context, TextChannel]): The destination where the message will be sent.
            **kwargs (Dict[str, Any]): Additional keyword arguments for the destination.

        Returns:
            Optional[BaseMessage]: The message that was sent, or None if the message failed to send.

        Raises:
            CommandError: If something unexpected happened while parsing the script.
        """
        
        used_models = self.models
        
        if moderator_data := kwargs.get("moderator"):
            used_models.append(models.Moderator(
                id=moderator_data.id,
                mention=moderator_data.mention,
                name=moderator_data.name,
                avatar=moderator_data.display_avatar.url,
                color=f"#{hex(await dominant_color(moderator_data.display_avatar.url))[2:]}",
                joined_at=format_dt(moderator_data.joined_at, style="R"),
                created_at=format_dt(moderator_data.created_at, style="R")
            ))
            
        if user_data := kwargs.get("user"):
            used_models.append(models.EUser(
                id=user_data.id,
                mention=user_data.mention,
                name=user_data.name,
                avatar=user_data.display_avatar.url,
                color=f"#{hex(await dominant_color(user_data.display_avatar.url))[2:]}",
                joined_at=format_dt(user_data.joined_at, style="R"),
                created_at=format_dt(user_data.created_at, style="R")
            ))
            
        if guild_data := kwargs.get("guild"):
            used_models.append(models.Guild(
                id=guild_data.id,
                name=guild_data.name,
                count=str(guild_data.member_count),
                count_formatted=ordinal(guild_data.member_count),
                boost_count=str(guild_data.premium_subscription_count),
                boost_count_formatted=ordinal(guild_data.premium_subscription_count),
                booster_count=str(len(guild_data.premium_subscribers)),
                booster_count_formatted=ordinal(len(guild_data.premium_subscribers)),
                boost_tier=str(guild_data.premium_tier),
                icon=guild_data.icon and guild_data.icon.url or "",
                created_at=format_dt(guild_data.created_at, style="R")
            ))

        self.script = await resolve_variables(
            self.script,
            models=used_models
        )

        await self.parse(context := kwargs.get("context"))

        if context and kwargs.get("strip_text_of_flags", False) is True:
            script = strip_flags(self.script, context)
 
        if isinstance(destination, Webhook):
            del self.objects["delete_after"]
            
        if (extras := kwargs.get("extras")) and isinstance(extras, dict):
            self.objects |= extras
            
        try:
            return await destination.send(**self.objects)
        
        except Exception:
            raise CommandError("Something unexpected happened while parsing your script.")
        
        
INCREMENT_SCRIPT_HASH = sha256(INCREMENT_SCRIPT := b"""
    local current
    current = tonumber(redis.call("incrby", KEYS[1], ARGV[2]))
    if current == tonumber(ARGV[2]) then
        redis.call("expire", KEYS[1], ARGV[1])
    end
    return current
""").hexdigest()


class VileRedis(Redis):
    def __init__(
        self: "VileRedis", 
        *args: Tuple[ Any ], 
        **kwargs: Dict[ str, Any ]
    ) -> NoReturn:
        super().__init__(*args, **kwargs)
        
        
    async def __aenter__(self: "VileRedis") -> Self:
        """
        Asynchronous context manager enter method.

        Returns:
            Self: A new instance of the class.
        """

        return await self.inititalize()
        
        
    async def __aexit__(self: "VileRedis", *_: None) -> NoReturn:
        """
        Asynchronous context manager exit method.

        Parameters:
            _ (Any):  Unused argument list.
        """

        await self.close()
        
        
    @classmethod
    async def inititalize(
        cls: "VileRedis", 
        host: str = "localhost", 
        port: int = 6379
    ) -> Self:
        """
        Initializes a new instance of the class.

        Parameters:
            host (str, optional): The host of the Redis server. Defaults to "localhost".
            port (int, optional): The port of the Redis server. Defaults to 6379.

        Returns:
            Self: A new instance of the class.
        """

        return cls(
            host=host,
            port=port,
            decode_responses=False
        )
    
    
    async def ratelimited(
        self, 
        resource_identifcation: str, 
        request_limit: int, 
        timespan: int = 60, 
        increment: int = 1
    ) -> bool:
        """
        Check if the resource identified by `resource_ident` has reached the rate limit.

        Parameters:
            resource_ident (str): The identifier of the resource.
            request_limit (int): The maximum number of requests allowed within `timespan`.
            timespan (int, optional): The time span in seconds for which the rate limit is enforced. Defaults to 60.
            increment (int, optional): The amount by which the rate limit counter is incremented. Defaults to 1.

        Returns:
            bool: True if the resource has reached the rate limit, False otherwise.
        """
        
        ratelimit_key = f"rl:{hash(resource_identifcation)}"
        
        try:
            current_usage = await self.evalsha(
                INCREMENT_SCRIPT_HASH, 
                1, 
                ratelimit_key, 
                timespan, 
                increment
            )
        
        except Exception:
            current_usage = await self.eval(
                INCREMENT_SCRIPT, 
                1, 
                ratelimit_key, 
                timespan, 
                increment
            )
        
        if int(current_usage) > request_limit:
            return True
            
        return False
        
        
class Role(_RoleConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[Role]:    
        """
        Converts the given argument into a Role object.
        
        Parameters:
            ctx (Context): The context in which the conversion is being performed.
            argument (str): The argument to be converted.
            
        Returns:
            Optional[Role]: The converted Role object, or None if the conversion fails.
        
        Raises:
            RoleNotFound: If the argument couldn't be converted.
        """
        
        try:
            return await super().convert(
                ctx, 
                argument
            )
        
        except RoleNotFound:
            closest = get_close_matches(
                argument.lower(), 
                (
                    r.name.lower() 
                    for r in ctx.guild.roles
                ), 
                n=1, 
                cutoff=0.5
            )
            
            if closest:
                for r in ctx.guild.roles:
                    if r.name.lower() == closest[0].lower():
                        return r
            
            raise RoleNotFound(argument)
                
                
class Message(_MessageConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[BaseMessage]:    
        """
        Converts the given argument to a BaseMessage object.

        Parameters:
            ctx (Context): The context in which the conversion is being performed.
            argument (str): The argument to be converted.

        Returns:
            Optional[BaseMessage]: Returns a BaseMessage object if the conversion is successful, otherwise returns None.
        
        Raises:
            MessageNotfound: If the argument couldn't be converted.
        """
        
        if len(tuple(filter(
            lambda r: f"invalid_id{ctx.guild.id}" in r, 
            ctx.bot.cache._rl
        ))) >= 15:
            raise CommandError("This resource is being rate limited.")
            
        if argument.isnumeric():
            id = int(argument)
            if ctx.bot.cache.is_ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}"):
                raise MessageNotFound(argument)
                
            if len(argument) not in (16, 17, 18, 19, 20):
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise MessageNotFound(argument)
                
            try:
                return await super().convert(
                    ctx, 
                    argument
                )
            
            except MessageNotFound:
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise
                
        return await super().convert(
            ctx, 
            argument
        )
    

class Sticker(GuildStickerConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[GuildSticker]:    
        """
        Convert the given argument to a GuildSticker object.

        Parameters:
            ctx (Context): The context of the command.
            argument (str): The argument to be converted.

        Returns:
            Optional[GuildSticker]: The converted GuildSticker object, or None if not found.
        
        Raises:
            GuildStickerNotfound: If the argument couldn't be converted.
        """
        
        if len(tuple(filter(
            lambda r: f"invalid_id{ctx.guild.id}" in r, 
            ctx.bot.cache._rl
        ))) >= 15:
            raise CommandError("This resource is being rate limited.")
            
        if argument.isnumeric():
            id = int(argument)
            if ctx.bot.cache.is_ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}"):
                raise GuildStickerNotFound(argument)
                
            if len(argument) not in (16, 17, 18, 19, 20):
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise GuildStickerNotFound(argument)
                
            try:
                return await super().convert(
                    ctx, 
                    argument
                )
            
            except GuildStickerNotFound:
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise
                
        return await super().convert(
            ctx, 
            argument
        )
    

class Emoji(_EmojiConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[BaseEmoji]:    
        """
        Converts the argument into a BaseEmoj object.
        
        Parameters:
            ctx (Context): The context in which the moderation action is being performed.
            argument (str): A string representing the argument to be converted.
        
        Returns:
            BaseEmoji: The emoji if the conversion is successful, None otherwise.
        
        Raises:
            EmojiNotfound: If the argument couldn't be converted.
        """
        
        if len(tuple(filter(
            lambda r: f"invalid_id{ctx.guild.id}" in r, 
            ctx.bot.cache._rl
        ))) >= 15:
            raise CommandError("This resource is being rate limited.")
            
        if argument.isnumeric():
            id = int(argument)
            if ctx.bot.cache.is_ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}"):
                raise EmojiNotFound(argument)
                
            if len(argument) not in (16, 17, 18, 19, 20):
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise EmojiNotFound(argument)
                
            try:
                return await super().convert(
                    ctx, 
                    argument
                )
            
            except EmojiNotFound:
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise
                
        try:
            return await super().convert(
                ctx, 
                argument
            )
        
        except EmojiNotFound:
            try:
                unicodedata.name(argument)
            
            except Exception:
                raise EmojiNotFound(argument)
            
            return argument
        
        
class Member(_MemberConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[BaseMember]:    
        """
        Convert the argument to a BaseMember object.

        Parameters:
            ctx (Context): The context in which the moderation action is being performed.
            argument (str): The string argument to be converted.

        Returns:
            Optional[BaseMember]: The converted BaseMember object, or None if the conversion fails.

        Raises:
            MemberNotfound: If the argument couldn't be converted.
        """

        if len(tuple(filter(
            lambda r: f"invalid_id{ctx.guild.id}" in r, 
            ctx.bot.cache._rl
        ))) >= 15:
            raise CommandError("This resource is being rate limited.")
            
        if argument.isnumeric():
            id = int(argument)
            if ctx.bot.cache.is_ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}"):
                raise MemberNotFound(argument)
                
            if len(argument) not in (16, 17, 18, 19, 20):
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise MemberNotFound(argument)
                
            try:
                return ctx.guild.get_member(id) or await ctx.guild.fetch_member(id)
            
            except MemberNotFound:
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise
                
        return await super().convert(
            ctx, 
            argument
        )
    

    async def can_moderate(self, ctx: "Context", member: BaseMember, action: str = "moderate") -> Optional[BaseMessage]:
        """
        Check if the given member can perform a moderation action.

        Parameters:
            ctx (Context): The context in which the moderation action is being performed.
            member (BaseMember): The member being checked for moderation permissions.
            action (str, optional): The moderation action being performed. Defaults to "moderate".

        Returns:
            Optional[BaseMessage]: Returns None if the member is allowed to perform the moderation action.
        
        Raises:
            CommandError: If the member is trying to moderate themselves or another member who has higher permissions.
            CommandError: If the member is trying to moderate the guild owner.
            CommandError: If the member is trying to moderate the bot itself.
            CommandError: If the bot does not have sufficient permissions to moderate the member.
        """
        
        if member.id == ctx.author.id:
            raise CommandError(f"You can't **{action}** yourself.")
        
        if (member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id) or member.id == ctx.guild.owner_id:
            raise CommandError(f"You can't **{action}** that member.")
            
        if member.id == ctx.bot.user.id:
            raise CommandError(f"You can't **{action}** me.")
            
        if (member.top_role >= ctx.guild.me.top_role and ctx.author.id != ctx.guild.owner_id):
            raise CommandError(f"I can't **{action}** that member.")
        
        return True
    

class User(_UserConverter):
    async def convert(self, ctx: "Context", argument: str) -> Optional[BaseUser]:    
        """
        Convert the given argument to a User object.

        Parameters:
            ctx (Context):  The context object representing the current execution context
            argument (str): The argument to convert.

        Returns:
            Optional[BaseUser]: The converted User object, or None if the argument is not valid.
        
        Raises:
            UserNotfound: If the argument couldn't be converted.
        """
        
        if len(tuple(filter(
            lambda r: f"invalid_id{ctx.guild.id}" in r, 
            ctx.bot.cache._rl
        ))) >= 15:
            raise CommandError("This resource is being rate limited.")
            
        if argument.isnumeric():
            id = int(argument)
            if ctx.bot.cache.is_ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}"):
                raise UserNotFound(argument)
                
            if len(argument) not in (16, 17, 18, 19, 20):
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise UserNotFound(argument)
                
            try:
                return ctx.bot.get_user(id) or await ctx.bot.fetch_user(id)
            
            except UserNotFound:
                ctx.bot.cache.ratelimited(f"rl:invalid_id{ctx.guild.id}-{id}", 1, 86400)
                raise
                
        return await super().convert(
            ctx, 
            argument
        )
        
        
class Timespan(Converter):
    async def convert(self, _: None, argument: str) -> Optional[Duration]:
        """
        Convert the given argument to a Duration object.
        
        Parameters:
            _ (Context): The unused context object representing the current execution context.
            argument (str): The string argument to be converted.
            
        Returns:
            Optional[Duration]: The converted Duration object, or None if the argument is invalid.
            
        Raises:
            SendHelp: If the argument is invalid and not equal to "0", "0 seconds", "0s", "0h", "0w", "0m", "0 hours", "0 weeks", or "0 months".
        """

        if not (ret := Duration(argument)).seconds and argument not in ("0", "0 seconds", "0s", "0h", "0w", "0m", "0 hours", "0 weeks"," 0 months", "0 hours"):
            raise SendHelp()
            
        return ret
    

class Color(Converter):
    async def convert(self, _: None, argument: str) -> Optional[Union[ str, BaseColor ]]:
        """
        Convert the given argument to a color value.
        
        Parameters:
            _ (Context): The unusued context object representing the current execution context.
            argument (str): The argument to be converted.
        
        Returns:
            Optional[Union[str, BaseColor]]: The converted color value, or None if the argument couldn't be converted.
        
        Raises:
            CommandError: If the argument couldn't be converted.
        """

        if argument.lower() in ("random", "rand", "r"):
            return BaseColor.random()
        
        if argument.lower() in ("invisible", "invis"):
            return BaseColor.dark_embed()
        
        if argument.lower() in ("blurple", "blurp"):
            return BaseColor.blurple()
        
        if argument.lower() in ("black", "negro"):
            return BaseColor.from_str("#000001")

        try:
            color = BaseColor.from_str(argument)
        
        except ValueError:
            if argument not in cnames:
                raise CommandError("I couldn't find that color")
            
            color = BaseColor.from_str(cnames[argument])
        
        return color
    

class MinecraftUser(Converter):
    async def convert(self: "MinecraftUser", ctx: "Context", argument: str) -> Optional[str]:
        """
        Convert the argument into a minecraft user object.
        
        Parameters:
            ctx (Context): The context object representing the current execution context.
            argument (str): The argument to be converted.
        
        Returns:
            Optional[str]: The player object if the conversion was successful, otherwise None.
        """
        
        if len(argument.split()) > 1:
            raise CommandError("Please provide a **valid** minecraft user.")
        
        data = await ctx.bot.session.get(
            f"https://playerdb.co/api/player/minecraft/{argument}",
            raise_for_status=False
        )

        if not data["data"]:
            raise CommandError("I couldn't find that minecraft user.")
        
        player = data["data"]["player"]
        player["body"] = f"https://crafthead.net/armor/body/{player['id']}"
        del player["meta"]

        return Munch(player)

        
async def spotify_token() -> str:
    """
    Retrieves the Spotify access token.

    Returns:
        str: The access token for Spotify.
    """
    
    if cached_value := GLOBAL.CACHE.get("spotifytoken"):
        return cached_value
        
    async with HTTPClient().session() as session:
        async with session.post(
            "https://accounts.spotify.com/api/token", 
            data={
                "grant_type": "client_credentials"
            },
            auth=BasicAuth(*literals.keys.spotify.split("-"))
        ) as resp:
            data = await resp.json()
            spotify_token = data["access_token"]
            
            GLOBAL.CACHE.set(
                "spotifytoken", 
                spotify_token, 
                expiration=3600
            )
            
            return spotify_token
        
        
async def dominant_color(source: Union[ Asset, str, bytes ], proxy: bool = False) -> int:
    """
    Calculates the dominant color of an image from the given source.

    Parameters:
        source: Union[Asset, str, bytes]: The image source. It can be an Asset object, a URL string, or a bytes object.
        proxy: bool (default=False): Whether to use a proxy for the HTTP request.

    Returns:
        int: The 16-bit RGB value of the image represented.
    """
    
    async def get_color(source: Union[ Asset, str, bytes ], proxy: bool = False) -> int:
        if isinstance(source, Asset):
            source = source.url

            if (color := GLOBAL.CACHE.get(f"imagecolor-{hash(source)}")) is not None:
                return color
        
        if isinstance(source, bytes):
            if (color := GLOBAL.CACHE.get(f"imagecolor-{hash(source)}")) is not None:
               return color
                
            resp = source
            
        else:
            try:
                resp = await HTTPClient(proxy=proxy).read(source)
            
            except Exception:
                return 0 
        
        def prep_image():
            image_hash = hash(resp)
            img = Image.open(BytesIO(resp))
            img.thumbnail((100, 100))
            
            if (color := GLOBAL.CACHE.get(f"imagecolor-{image_hash}")) is not None:
                return color
                
            colors = colorgram.extract(img, 1)
            color = BaseColor.from_rgb(*colors[0].rgb).value
            GLOBAL.CACHE.set(f"imagecolor-{image_hash}", color, expiration=600 if isinstance(source, bytes) else None)

            return color
        
        return await GLOBAL.BOT.run_async(prep_image)
    
    return await wait_for(get_color(source=source, proxy=proxy), timeout=10)
    
    
class Attachment(Converter):
    async def convert(self, ctx: "Context", argument: str, fail: bool = True) -> Optional[str]:
        """
        Convert the given argument to a link if it matches the link pattern.
        
        Parameters:
            ctx (Context): The context object representing the current execution context.
            argument (str): The argument to be converted.
            fail (bool, optional): Whether to raise an exception if the conversion fails. Defaults to True.
            
        Returns:
            Optional[str]: The converted link if the argument matches the link pattern, None otherwise.
        
        Raises:
            AssertionError: If fail is True and no link is found.
        """

        if match := expressions.link.match(argument):
            return match.group()

        if fail is True:
            with suppress(Exception):
                await ctx.send_help(ctx.command.qualified_name)

            assert False


    @staticmethod
    async def search(ctx: "Context", fail: bool = True) -> Optional[str]:
        """
        Retrieves the URL of the first attachment in the last 50 messages in the given context's channel.
        
        Parameters:
            ctx (Context): The context object representing the current execution context.
            fail (bool, optional): Specifies whether an error should be raised if no attachment is found. Defaults to True.
            
        Returns:
            Optional[str]: The URL of the first attachment found, or None if no attachment is found.
        
        Raises:
            AssertionError: If fail is True and no link is found.
        """

        async for message in ctx.channel.history(limit=50):
             if message.attachments:
                return message.attachments[0].url
                    
        if fail is True:
            with suppress(Exception):
                await ctx.send_help(ctx.command.qualified_name)

            assert False
    
            
async def eval_bash(script: str, decode: bool = False) -> Optional[str]:
    """
	Evaluates a bash script and returns the result.

	Parameters:
	    script (str): The bash script to be evaluated.
	    decode (bool, optional): Whether to decode the result using utf-8. Defaults to False.

	Returns:
	    Optional[str]: The result of the bash script evaluation. If decode is True, the result is decoded using utf-8.
	"""

    process = await create_subprocess_shell(
        script,
        stdout=PIPE,
        stderr=PIPE
    )

    result, err = await process.communicate()

    if err:
        raise Exception(err.decode("utf-8"))
        
    return result.decode() if decode else result


def has_permissions(**perms: bool) -> Any:
    """
	Checks if the user has the required permissions.

	Parameters:
		**perms (bool): The required permissions as keyword arguments.

	Returns:
		Any: Returns the result of the predicate function.

	Raises:
		TypeError: If any of the permissions provided are invalid.
		MissingPermissions: If the user does not have the required permissions.
	"""

    invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    async def predicate(ctx: "Context") -> Optional[bool]:
        """
        Check if the user has the necessary permissions to execute the command.

        Parameters:
            ctx (Context): The context object representing the current execution context.

        Returns:
            Optional[bool]: Returns True if the user has the necessary permissions, otherwise returns None.

        Raises:
            MissingPermissions: If the user is missing any of the required permissions.
        """
        
        if ctx.author.guild_permissions.administrator:
            return True
        
        author_roles = tuple(map(lambda r: r.id, ctx.author.roles))
        fake_permissions = ()
        
        if ctx.bot.cache.keys(pattern=f"data:fake_permissions:{ctx.guild.id}:*"):
            fake_permissions = tuple(
                itertools.chain.from_iterable(map(
                    lambda r: ctx.bot.cache.smembers(f"data:fake_permissions:{ctx.guild.id}:{r}"), 
                    (r for r in tuple(int(record.split(":")[-1]) for record in ctx.bot.cache.keys(pattern=f"data:fake_permissions:{ctx.guild.id}:*")) if r in author_roles if ctx.bot.cache.smembers(f"data:fake_permissions:{ctx.guild.id}:{r}"))
                ))
            )

        for perm, _ in perms.items():
            if (getattr(ctx.author.guild_permissions, perm) is True) or (perm in set(fake_permissions)):
                return True

        raise MissingPermissions((perm,))

    return check(predicate)
    
    
def is_guild_owner() -> Any:
    """
    Checks if the author is the owner of the guild.

    Returns:
        check: A command check.
    """
    
    async def predicate(ctx: "Context") -> bool:
        """
        Check if the author is the owner of the guild.

        Parameters:
            ctx (Context): The context object representing the current execution context.

        Returns:
            bool: True if the author is the guild owner, False otherwise.
        """
        
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.error("You're missing the **Server Owner** permission.")
            return False
            
        return True
        
    return check(predicate)


def guild_has_vanity() -> Any:
    """
    Checks if the guild has a vanity invite.

    Returns:
        check: A command check.
    """

    async def predicate(ctx: Context) -> bool:
        """
        Check if the guild has a vanity URL code.
        
        Parameters:
            ctx (Context): The context object representing the current execution context.
        
        Returns:
            bool: True if the context has a vanity URL code, False otherwise.
        """
        
        if ctx.guild.vanity_url_code is None:
            await ctx.error("This server doesn't have a **vanity invite**.")
            return False
            
        return True
        
    return check(predicate)


async def embed_send(self) -> Optional[BaseMessage]:
    """
    Sends an embed using the local context variable.

    Returns:
        Optional[BaseMessage]: The message that was sent, or None if sending failed.

    Raises:
        Exception: If there is no context.
    """
    
    locals = currentframe().f_back.f_locals
    context = (
        locals.get("ctx") 
        or locals.get("context") 
        or getattr(locals.get("self"), "context", None)
    )
    
    if context is None:
        raise Exception
    
    return await context.send(embed=self)


class FileProcessing:
    def __init__(self: "FileProcessing") -> NoReturn:
        return


    def get_bytes_per_second(
        self: "FileProcessing", 
        source: bytes,
        format: str
    ) -> int:
        """
        Calculate the number of bytes per second in an audio file.

        Parameters:
            source (bytes): The audio file in bytes.

        Returns:
            int: The number of bytes per second in the audio file.
        """

        duration = AudioSegment.from_file(
            BytesIO(source),
            format=format
        )
        
        return int(len(source) // duration.duration_seconds)
        

    def chunk(
        self: "FileProcessing", 
        source: bytes, 
        chunk_size: int
    ):
        """
        Splits the source into chunks of size chunk_size and sends them as a tuple.

        Parameters:
            source (bytes): The audio file in bytes.
            chunk_size (int): The size of each chunk in bytes.

        Returns:
            list: A list of the chunks.
        """

        return tuple(
            source[i*chunk_size:(i+1)*chunk_size]
            for i in range(int((len(source) + chunk_size - 1) // chunk_size))
        )
    
    
class DataProcessing:
    def __init__(self: "DataProcessing") -> NoReturn:
        self.APININJAS_API_KEY = literals.api.apininjas
        self.pipelines = Munch()
        
        self.__session = HTTPClient(proxy=False)
        self.__proxied_session = HTTPClient(proxy=True)

        self.rival = APIWrapper(
            name="Rival",
            default_url="https://api.rival.rocks",
            headers={
                "api-key": literals.api.rival
            }
        )

        
    async def __request(
        self: "DataProcessing", 
        method: str, endpoint: str, 
        params: Optional[dict] = None, 
        data: Optional[dict] = None
    ) -> dict:
        """
        Sends an HTTP request to the API-Ninjas API.

        Parameters:
            method (str): The HTTP method to use for the request. Can be "GET" or "POST".
            endpoint (str): The endpoint to send the request to.
            params (dict, optional): The parameters to include in the request URL. Defaults to None.
            data (dict, optional): The data to include in the request body. Defaults to None.

        Returns:
            dict: The response from the server.
        """
        
        if method == "GET":
            method = self.__session.get(
                f"https://api.api-ninjas.com/v1/{endpoint}", 
                params=params, 
                headers={
                    "X-Api-Key": self.APININJAS_API_KEY
                },
                command_error=False
            )
        
        elif method == "POST":
            method = self.__session.post_json(
                f"https://api.api-ninjas.com/v1/{endpoint}", 
                data=data,
                params=params,
                headers={
                    "X-Api-Key": self.APININJAS_API_KEY
                },
                command_error=False
            )
            
        return await method
        
        
    async def detect_text(self: "DataProcessing", source: Union[ str, bytes ]) -> Optional[str]:
        """
        Detects text in the given source image and returns it as a string.
        
        Parameters:
            source (Union[str, bytes]): The source image to detect text from. It can be either a file path or image data in bytes.
        
        Returns:
            Optional[str]: The detected text as a string, or None if no text is detected.
        """
        
        if isinstance(source, str):
            source = await self.__proxied_session.read(source)

        if cached_text := GLOBAL.CACHE.get(f"ocr-{hash(source)}"):
            return cached_text
        
        data = await self.__request(
            "POST", 
            "imagetotext",
            data={
                "image": source
            }
        )

        if not data or isinstance(data, dict):
            return
        
        ret = [ ]
        previous_y2 = None

        for entry in data:
            await sleep(0.01)
            text = entry["text"]
            bounding_box = entry["bounding_box"]
            current_y1 = bounding_box["y1"]
            
            if previous_y2 is not None and current_y1 > previous_y2:
                ret.append("\n")

            ret.append(text.strip())
            previous_y2 = bounding_box["y2"]

        GLOBAL.CACHE.set(
            f"ocr-{hash(source)}", 
            ret := " ".join(ret)
        )
            
        return ret
        

    async def timezone(self: "DataProcessing", city: str) -> Optional[str]:
        """
        Retrieve the timezone for a given city.

        Parameters:
            city (str): The name of the city.

        Returns:
            Optional[str]: The timezone of the city, or None if not found.
        
        Raises:
            CommandError: If there is an internal server error in the API.
        """
        
        if city in all_timezones:
            return city

        if cached_timezone := GLOBAL.CACHE.get(f"timezone-{city}"):
            return cached_timezone
            
        data = await self.__request(
            "GET", 
            "timezone",
            params={
                "city": city
            }
        )

        if data.get("error"):
            return
        
        if data.get("message") == "Internal server error":
            raise CommandError(f"The **API** returned [`500 {HTTPStatus(500).phrase}`](https://http.cat/500).")
        
        GLOBAL.CACHE.set(
            f"timezone-{city}", 
            data["timezone"]
        )

        return data["timezone"]
        
        
    async def weather(self: "DataProcessing", city: str) -> Optional[dict]:
        """
        Retrieves the weather for a given city.
        
        Parameters:
            city: The name of the city for which to retrieve the weather.
            
        Returns:
            Optional[dict]: A dictionary containing the weather information for the given city, or None.
        
        Raises:
            CommandError: If there is an internal server error in the API.
        
        """

        if cached_weather := GLOBAL.CACHE.get(f"weather-{city}"):
            return cached_weather
            
        data = await self.__request(
            "GET", 
            "weather",
            params={
                "city": city
            }
        )

        if data.get("error"):
            return
        
        if data.get("message") == "Internal server error":
            raise CommandError(f"The **API** returned [`500 {HTTPStatus(500).phrase}`](https://http.cat/500).")
        
        for field in (
            "temp", "feels_like",
            "min_temp", "max_temp"
        ):
            data[field] = dict(
                fahrenheit=(data[field] * 1.8) + 32,
                celsius=data[field]
            )
        
        GLOBAL.CACHE.set(
            f"weather-{city}", 
            data := models.Weather(**data),
            expiration=3600
        )

        return data
    

    async def definition(self: "DataProcessing", word: str) -> Dict[ str, Any ]:
        """
        Retrieves the definition of a word from a dictionary API.

    	Parameters:
    	    word (str): The word for which the definition is needed.

    	Returns:
    	    Dict[str, Any]: A dictionary containing the definition of the word.
    	
        Raises:
            CommandError: If there is an internal server error in the API.
        """

        if cached_definition := GLOBAL.CACHE.get(f"definition-{word}"):
            return cached_definition
        
        data = await self.__request(
            "GET",
            "dictionary",
            params={
                "word": word
            }
        )

        if data.get("message") == "Internal server error":
            raise CommandError(f"The **API** returned [`500 {HTTPStatus(500).phrase}`](https://http.cat/500).")
        
        GLOBAL.CACHE.set(
            f"definition-{word}", 
            data := models.Definition(**data)
        )

        return data
    

    async def urban_definition(self: "DataProcessing", term: str) -> Dict[ str, Any ]:
        """
        Retrieves the definition of a given term from the Urban Dictionary API.
        
        Parameters:
            term (str): The term to look up in the Urban Dictionary.
            
        Returns:
            Dict[str, Any]: A dictionary containing the definition of the term and other related information.
        
        Raises:
            CommandError: If there is an internal server error in the API.
        """
        
        if cached_definition := GLOBAL.CACHE.get(f"urban_definition-{term}"):
            return cached_definition
        
        data = await self.__session.get(
            "https://api.urbandictionary.com/v0/define",
            params={
                "term": term
            }
        )

        if data.get("message") == "Internal server error":
            raise CommandError(f"The **API** returned [`500 {HTTPStatus(500).phrase}`](https://http.cat/500).")

        GLOBAL.CACHE.set(
            f"urban_definition-{term}", 
            data := tuple(models.UrbanDefinition(**record) for record in data["list"])
        )

        return data
    

    async def detect_objects(self: "DataProcessing", source: Union[ str, bytes ]) -> Counter:
        """
        Detects objects in an image and returns a Counter object containing the labels of the detected objects.

        Parameters:
            source (Union[str, bytes]): The source of the image to be processed. It can be either a string representing the path to the image file or the image data in bytes.

        Returns:
            Counter: A Counter object containing the labels of the detected objects along with their frequencies.

        Raises:
            CommandError: If the image resolution is larger than 2000x2000 or if there is an internal server error in the API.
        """
        
        if isinstance(source, str):
            source = await self.__proxied_session.read(source)

        if cached_text := GLOBAL.CACHE.get(f"objects-{hash(source)}"):
            return cached_text
        
        data = await self.__request(
            "POST", 
            "objectdetection",
            data={
                "image": source
            }
        )

        if not data:
            return
        
        if isinstance(data, dict) and data.get("error") == "Images must be smaller than 2000x2000.":
            raise CommandError("The image resolution must be smaller than 2000x2000.")
        
        if isinstance(data, dict) and data.get("message") == "Internal server error":
            raise CommandError(f"The **API** returned [`500 {HTTPStatus(500).phrase}`](https://http.cat/500).")

        ret = Counter((
            item["label"] 
            for item in data 
            if float(item["confidence"]) >= 0.5
        ))

        GLOBAL.CACHE.set(
            f"objects-{hash(source)}", 
            ret
        )
            
        return ret
    

    async def inflation(
        self: "DataProcessing", 
        _type: Literal[ "CPI", "HICP" ] = "CPI", 
        country: str = ""
    ) -> List[Dict[ str, Any ]]:
        """
        Retrieves the inflation data for a specific country.
        
        Parameters:
            _type (Literal["CPI", "HICP"], optional): The type of inflation data to retrieve. Defaults to "CPI".
            country (str, optional): The country for which to retrieve the inflation data. Defaults to "".
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the inflation data.
        """

        if cached_data := GLOBAL.CACHE.get(f"inflation-{country}"):
            return cached_data
        
        data = await self.__request(
            "GET",
            "inflation",
            params={
                "type": _type,
                "country": country
            }
        )

        if not data:
            return None
        
        if data.get("message") == "Internal server error":
            raise CommandError(f"The **API** returned [`500 {HTTPStatus(500).phrase}`](https://http.cat/500).")

        GLOBAL.CACHE.set(
            f"inflation-{country}", 
            data[0]
        )

        return data[0]
    

    async def text_sentiment(self: "DataProcessing", text: str) -> Dict[ str, Any ]:
        """
        Retrieve the sentiment analysis of a given text.
        
        Parameters:
            text (str): The text to be analyzed.
        
        Returns:
            Dict[str, Any]: A dictionary containing the sentiment analysis results.
        """

        if cached_data := GLOBAL.CACHE.get(f"sentiment-{text}"):
            return cached_data
        
        data = await self.__request(
            "GET",
            "sentiment",
            params={
                "text": text
            }
        )

        GLOBAL.CACHE.set(
            f"sentiment-{text}", 
            data := models.Sentiment(**data)
        )

        return data
    
    
    async def text_similarity(
        self: "DataProcessing", 
        text1: str, 
        text2: str
    ) -> Optional[Dict[ str, Any ]]:
        """
        Calculate the similarity between two texts.

        Parameters:
            text1 (str): The first text.
            text2 (str): The second text.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the similarity data, 
                or `None` if the API returns an internal server error.

        Raises:
            CommandError: If the API returns an internal server error.
        """

        if cached_data := GLOBAL.CACHE.get(f"similarity-{text1}-{text2}"):
            return cached_data
        
        data = await self.__request(
            "POST",
            "textsimilarity",
            data={
                "text_1": text1,
                "text_2": text2
            }
        )

        if data.get("message") == "Internal server error":
            raise CommandError(f"The **API** returned [`500 {HTTPStatus(500).phrase}`](https://http.cat/500).")

        GLOBAL.CACHE.set(
            f"similarity-{text1}-{text2}", 
            data
        )

        return data
    

    async def google_images(
        self: "DataProcessing", 
        query: str, 
        safe: bool = False
    ) -> Munch:
        """
        Performs a Google image search with the given query and returns a list of search results.

        Parameters:
            query (str): The search query for Google images.
            safe (bool): A flag to indicate whether to filter out explicit content or not.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing information about Google images.
        """

        return await self.__session.post_json(
            "https://vile.bot/api/browser/images",
            data=query,
            params={
                "colors": "true"
            }
        )
    

    async def google_search(
        self: "DataProcessing", 
        query: str, 
        safe: bool = False
    ) -> List[Dict[ str, Any ]]:
        """
        Performs a Google search with the given query and returns a list of search results.

        Parameters:
            query (str): The query string to search for.
            safe (bool): Indicates whether to enable safe search or not.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the search results. Each dictionary contains
                information about the title, URL, and other details of a search result.
        """
        
        return await self.__session.post_json(
            "https://vile.bot/api/browser/search",
            data=query
        )

            
            
    async def caption(self: "DataProcessing", source: Union[ str, bytes ]) -> str:
        """
        Describes what's happening in an image.
        
        Parameters:
            source (Union[str, bytes]): The source of the image to be described. It can be either a string or bytes.
            
        Returns:
            str: A string containing the image description.
        """
        
        if isinstance(source, str):
            source = await self.__proxied_session.read(source)

        if cached_data := GLOBAL.CACHE.get(f"caption-{hash(source)}"):
            return cached_data
        
        data = await self.__session.post_json(
            url="https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large",
            data=source,
            headers={
                "Authorization": f"Bearer {literals.api.huggingface}"
            }
        )

        GLOBAL.CACHE.set(
            f"caption-{hash(source)}", 
            data[0]["generated_text"]
        )

        return data[0]["generated_text"]


    async def transcribe(
        self: "DataProcessing", 
        source: Union[ str, bytes ],
        format: str
    ) -> str:
        """
        Transcribes audio into text.
        
        Parameters:
            source (Union[str, bytes]): The source of the audio to be transcribed. It can be either a string or bytes.
            format (str): The format of the audio.
            
        Returns:
            str: A string containing the transcribed text.
        """
        
        if isinstance(source, str):
            source = await self.__proxied_session.read(source)

        if cached_data := GLOBAL.CACHE.get(f"transcription-{hash(source)}"):
            return cached_data

        with open(f"/root/.cache/vilebot/transcription{(tid := tuuid.tuuid())}.{format}", "wb") as file:
            file.write(source)
            
            data = await (await self.rival.request(
                "GET", "/media/transcribe",
                params={
                    "url": f"https://vile.bot/cache/transcription{tid}.{format}"
                }
            )).json()

            GLOBAL.CACHE.set(
                f"transcription-{hash(source)}", 
                data["text"]
            )

            return data["text"]


    async def prompt(
        self: "DataProcessing", 
        prompt: str,
        expert: str = "",
        large: bool = False
    ) -> str:
        """
        Generates text based on the given prompt.

        Parameters:
            prompt (str): The prompt to generate text from.

        Returns:
            str: The generated content.
        """
    
        return await self.__session.post_text(
            "https://vile.bot/api/prompt",
            data=prompt,
            params={
                "expert": "" if not expert else expert
            }
        )
            
    
    async def determine_explicit(
        self: "DataProcessing",
        source: Union[ str, bytes ],
        threshold: float = 0.6
    ) -> Munch:
        """
        Determines if the image is explicit.

        Parameters:
            source (Union[str, bytes]): The source of the image to be checked. It can be either a string or bytes.
            threshold (float, optional): The threshold for determining if the image is explicit. Defaults to 0.6.

        Returns:
            bool: Whether the image is explicit or not.
        """

        if isinstance(source, str):
            source = await self.__proxied_session.read(source)

        if cached_value := GLOBAL.CACHE.get(f"explicit-{hash(source)}"):
            return cached_value

        data = await self.__session.post_json(
            "https://api.sightengine.com/1.0/check.json", 
            data={
                "media": BytesIO(source),
                "models": "nudity-2.0,gore",
                "api_user": "1006949843",
                "api_secret": literals.api.sightengine
            }
        )

        ret = Munch({
            "nudity": data["nudity"]["sexual_activity"] > threshold,
            "gore": data["gore"]["prob"] > threshold
        })

        GLOBAL.CACHE.set(
            f"explicit-{hash(source)}", 
            ret
        )

        return ret


    async def translate_text(
        self: "DataProcessing",
        text: str,
        source_language: str = "auto",
        target_language: str = "english"
    ) -> str:
        """
        Translate text to another language.

        Parameters:
            text (str): The text to translate.
            target_language (str): The target language of the translation.

        Returns:
            str: The translated text.
        """

        data = await self.__session.post_text(
            "https://www.google.com/async/translate",
            data = {
                "async": f"translate,sl:{langcodes.find(source_language).language if source_language != 'auto' else source_language},tl:{langcodes.find(target_language).language},st:{text},id:{-randrange(9e10)},qc:true,ac:true,_id:tw-async-translate,_pms:s,_fmt:pc"
            }
        )

        return BeautifulSoup(data, "html.parser").find("span", attrs={"id": "tw-answ-target-text"}).text


    async def wolfram(self: "DataProcessing", input: str) -> Dict[ str, Any ]:
        """
        Performs WolframAlpha query.

        Parameters:
            input (str): The query to perform.

        Returns:
            Dict[str, Any]: The result of the query.
        """

        return await self.__session.get(
            "http://api.wolframalpha.com/v2/query",
            params={
                "appid": literals.api.wolfram,
                "input": input,
                "output": "json",
                "units": "metric"
            }
        )
    

    async def address_info(self: "DataProcessing", address: str) -> Dict[ str, Any ]:
        """
        Gets information about an address.

        Parameters:
            address (str): The address to get information about.

        Returns:
            Dict[str, Any]: The information about the address.
        """

        try:
            data = await self.__proxied_session.get(
                f"https://api.ipregistry.co/{address}?hostname=true&key=sb69ksjcajfs4c",
                headers={
                    "Origin": "https://ipregistry.co"
                }
            )

        except Exception:
            raise Exception("The IP address is a bogon IP. No data for this IP address.")
        
        if data.get("code") == "RESERVED_IP_ADDRESS":
            raise Exception("The IP address is a bogon IP. No data for this IP address.")
        
        if data.get("code") == "INVALID_IP_ADDRESS":
            raise Exception("You entered a value that does not appear to be a valid IP address.")
        
        assert not data.get("message"), \
            "Failed to retrieve information on that address."
        
        return models.GeoIP(**data)
    
    
    async def fetch_youtube_post(self: "DataProcessing", url: str) -> Dict[ str, Any ]:
        """
        Fetch information about a YouTube post using its URL.

        Parameters:
            url (str): The URL of the YouTube post.
            
        Returns:
            Dict[str, Any]: A dictionary containing information about the YouTube post.
        """
        
        cache_key = f"youtube_embedding:{hash(url)}"
        
        if cached_data := GLOBAL.CACHE.get(cache_key):
            return cached_data

        async with await GLOBAL.BOT.rival.request(
            method="GET", 
            endpoint="/youtube", 
            params={
                "url": url 
        }) as response:
            GLOBAL.CACHE.set(
                cache_key,
                ret := models.YouTubePost(**await response.json()),
                expiration=21600
            )
            
            return ret
        
        
    async def fetch_instagram_post(self: "DataProcessing", url: str) -> Dict[ str, Any ]:
        """
        Fetch information about an Instagram post using its URL.

        Parameters:
            url (str): The URL of the Instagram post.
            
        Returns:
            Dict[str, Any]: A dictionary containing information about the Instagram post.
        """
        
        if "stories" in url:
            raise CommandError(f"Instagram Embedding doesn't support stories.")
        
        cache_key = f"instagram_embedding:{hash(url)}"
        
        if cached_data := GLOBAL.CACHE.get(cache_key):
            return cached_data
        
        async with await GLOBAL.BOT.rival.request(
            method="GET", 
            endpoint="/instagram/media", 
            params={
                "url": url 
        }) as response:
            GLOBAL.CACHE.set(
                cache_key,
                ret := models.InstagramMedia(**await response.json()),
                expiration=21600
            )
            
            return ret


class Watcher:
    def __init__(
        self: "Watcher",
        bot: VileBot,
        path: str = "cogs",
        loop: AbstractEventLoop = None,
        preload: bool = False
    ) -> NoReturn:
        self.bot = bot
        self.path = path
        self.loop = loop or get_event_loop()
        self.preload = preload


    def get_dotted_cog_path(self: "Watcher", file: Union[ PosixPath, str ]) -> str:
        """
        Get the dotted cog path for a given file.

        Parameters:
            file (Union[PosixPath, str]): The file path to get the dotted cog path for.

        Returns:
            str: The dotted cog path of the file.
        """

        if isinstance(file, str):
            file = Path(file.replace(f"{getcwd()}/", ""))
            
        return ".".join(file.parts)[:-3]


    async def _start(self: "Watcher") -> NoReturn:
        """
        Starts the Watcher.

        This function continuously checks if the specified directory exists. If it does, it
        asynchronously watches for changes in the directory using the `awatch` function.
        For each change detected, it determines the type of change and the path of the
        changed file. It then performs the appropriate action based on the change type.
        """

        while self.directory_exists():
            try:
                async for changes in awatch(Path.cwd() / self.path):
                    self.validate_directory()
                    reverse_ordered_changes = sorted(changes, reverse=True)

                    for change in reverse_ordered_changes:
                        change_type, change_path = change
                        cog = self.get_dotted_cog_path(change_path)

                        if change_type == Change.deleted:
                            if cog in self.bot.extensions:
                                await self.unload(cog)

                        elif change_type == Change.added:
                            if cog not in self.bot.extensions:
                                await self.load(cog)

                        elif change_type == Change.modified and change_type not in (Change.added, Change.deleted):
                            if cog in self.bot.extensions:
                                await self.reload(cog)

                            else:
                                await self.load(cog)

            except (FileNotFoundError, RuntimeError):
                continue

            else:
                await sleep(1)

        else:
            await self.start()


    def directory_exists(self: "Watcher") -> bool:
        """
        Check if the directory specified by the `path` attribute exists.

        Returns:
            bool: True if the directory exists, False otherwise.
        """

        return Path(Path.cwd() / self.path).exists()


    def validate_directory(self: "Watcher") -> NoReturn:
        """
        Validate the directory.
        This function checks if the directory exists and raises a FileNotFoundError if it does not.
        """

        if self.directory_exists() is None:
            raise FileNotFoundError


    async def start(self: "Watcher"):
        """
        Starts the watcher and begins monitoring for file changes.
        """

        self.validate_directory()

        if self.preload:
            await self._preload()

        logger.info(f"Watching for file changes in {Path.cwd() / self.path}.")
        self.loop.create_task(self._start())


    async def load(self: "Watcher", cog: str):
        """
        Loads the specified cog.

        Parameters:
            cog (str): The name of the cog to load.
        """

        with suppress(Exception):
            await self.bot.load_extension(cog)


    async def unload(self: "Watcher", cog: str):
        """
        Unloads the specified cog.

        Parameters:
            cog (str): The name of the cog to unload.
        """

        with suppress(Exception):
            await self.bot.unload_extension(cog)


    async def reload(self: "Watcher", cog: str) -> NoReturn:
        """
        Reloads the specified cog.

        Parameters:
            cog (str): The name of the cog to reload.
        """

        with suppress(Exception):
            await self.bot.reload_extension(cog)


    async def _preload(self: "Watcher") -> NoReturn:
        """
        Preloads all the cogs found in the specified path.
        """
        
        for file in Path(self.path).rglob("*.py"):
            cog = self.get_dotted_cog_path(file)
            await self.load(cog)
            logger.info(f"Preloaded cog: {cog}")


class ImageGenerator:
    def single_color(
        self: "ImageGenerator", 
        width: int = 500, 
        height: int = 500, 
        color: Union[ BaseColor, Tuple[int] ] = ( 0, 0, 0 )
    ) -> BytesIO:
        """
        Generates an image with a single color.

        Parameters:
            width (int, optional): The width of the image. Defaults to 500.
            height (int, optional): The height of the image. Defaults to 500.
            color (Union[BaseColor, Tuple[int]], optional): The color of the image.
                Can be a BaseColor object or a tuple of RGB values. Defaults to (0, 0, 0).

        Returns:
            BytesIO: The generated image as a BytesIO object.
        """

        image = Image.new(
            "RGBA", 
            (width, height), 
            (color.to_rgb() if isinstance(color, BaseColor) else color)
        )

        image.save(
            buffer := BytesIO(), 
            format="PNG"
        )

        buffer.seek(0)
        return buffer
    

    def multiple_colors(
        self: "ImageGenerator", 
        width: int = 500, 
        height: int = 500, 
        colors: Sequence[Union[ BaseColor, Tuple[int] ]] = ( ( 0, 0, 0 ), ( 255, 255, 255 ) )
    ) -> BytesIO:
        """
        Generate an image with multiple colors.

        Parameters:
            width (int, optional): The width of the image in pixels. Defaults to 500.
            height (int, optional): The height of the image in pixels. Defaults to 500.
            colors (List[Union[BaseColor, Tuple[int]]], optional): A list of colors to fill the image with. Each color can be specified as a BaseColor or as a tuple of RGB values. Defaults to [(0, 0, 0), (255, 255, 255)].

        Returns:
            BytesIO: The image data as a BytesIO object.
        """

        image = Image.new(
            "RGBA", 
            (width, height), 
        )

        draw = ImageDraw.Draw(image)
        color_width = width // len(colors)
        
        for i, color in enumerate(colors):
            x1, x2 = i * color_width, (i + 1) * color_width
            draw.rectangle(
                (x1, 0, x2, height), 
                fill=color
            )
            
        image.save(
            buffer := BytesIO(), 
            format="PNG"
        )

        buffer.seek(0)
        return buffer
    

class TikTok:
    class Feed(object):
        def __init__(self: "TikTok.Feed", results: BetterList["TikTok.Result"]) -> NoReturn:
            assert isinstance(results, BetterList), \
                "Argument 'results' must be a BetterList."
                
            self.__results = results


        @property
        def results(self: "TikTok.Feed") -> BetterList:
            return self.__results


    class Result(object):
        def __init__(self, data: dict) -> NoReturn:
            assert isinstance(data, dict), \
                "Argument 'data' must be a dictionary."
                
            self.__data = Munch(data)


        def __repr__(self: "TikTok.Result") -> str:
            return f"<TikTok.Result data={self.data}>"


        @property
        def data(self: "TikTok.Result") -> Munch:
            return self.__data

        
        def __getattr__(self: "TikTok.Result", name: str) -> Any:
            if name == "data":
                return self.data

            return self.data[name]


    def __init__(self: "TikTok") -> NoReturn:
        self.__BASE_URL = "https://api-h2.tiktokv.com"
        self.__session = HTTPClient(proxy=False)
        self.__proxied_session = HTTPClient(proxy=True)
    

    async def __request(
        self: "TikTok", 
        method: str, 
        endpoint: str, 
        params: Optional[dict] = None, 
    ) -> dict:
        """
        Sends an HTTP request to the TikTok API.

        Parameters:
            method (str): The HTTP method to use for the request. Can be "GET" or "POST".
            endpoint (str): The endpoint to send the request to.
            params (dict, optional): The parameters to include in the request URL. Defaults to None.

        Returns:
            dict: The response from the server.
        """

        if method == "GET":
            method = self.__session.get(
                f"{self.__BASE_URL}/{endpoint}/", 
                params=params,
                command_error=False
            )

        elif method == "POST":
            method = self.__session.post(
                f"{self.__BASE_URL}/{endpoint}/", 
                params=params,
                command_error=False
            )

        async with Timeout(15):
            return await method
        
        
    async def __format_data(
        self: "TikTok", 
        data: dict,
        amount: int = 1
    ) -> dict:
    
        assert "aweme_list" in data, \
            "Couldn't find any results."
            
        response = [ ]
        
        for result in data["aweme_list"][:amount]:
            await sleep(1e-3)
            
            video = result["video"]
            author = result["author"]
            music = result["music"]
        
            statistics = result["statistics"]
            statistics["aweme_id"] = int(statistics["aweme_id"])
            statistics["like_count"] = statistics.pop("digg_count")

            response.append(TikTok.Result({
                "type": "slide" if result.get("image_post_info") else "video",
                "url": video["play_addr"]["url_list"][0],
                "urls": video["play_addr"]["url_list"],
                "description": result["desc"],
                "username": author["unique_id"],
                "nickname": author["nickname"],
                "avatar": author["avatar_medium"]["url_list"][1],
                "statistics": Munch(statistics),
                "music": Munch(
                    title=music.get("title"),
                    author=music.get("author"),
                    album=music.get("album"),
                    duration=music.get("duration")
                )
            }))
            
        return amount == 1 and response[0] or response
    

    async def generate_embed(
        self: "TikTok",
        bot: Optional[VileBot],
        data: "TikTok.Result"
    ) -> Embed:
        """
        Generate an embed object based on the provided data.

        Parameters:
            self (TikTok): The TikTok instance.
            bot (Optional[VileBot]): An optional VileBot instance.
            data (dict): The data to generate the embed from.

        Returns:
            Embed: The generated embed object.
        """

        return (
            Embed(
                color=bot.color if bot else BaseColor.dark_embed(),
                description=data.description
            )
            .set_author(
                name=f"@{data.username} | {fmtseconds(data.music.duration)} long",
                icon_url="https://cdn.discordapp.com/emojis/1017812426164551762.png?size=4096",
                url=data.url,
            )
            .set_footer(text=f"💬 {data.statistics.comment_count:,} \
                | 👍 {data.statistics.like_count:,} \
                | 🔗 {data.statistics.share_count:,} ({data.statistics.play_count:,} views) \
                \n🎵 {data.music.title} (by {data.music.author})"
            )
        )



    async def feed(self: "TikTok", amount: int = 1) -> dict:
        """
        Returns the "For You" page of the TikTok website.
        
        Parameters:
            amount (int): The amount of posts to return. Defaults to 1.
        
        Returns:
            dict: The response from the server.
        """

        results = await self.__format_data(await self.__request(
            "GET", 
            "aweme/v1/feed"
        ), amount=amount)

        if isinstance(results, list):
            return TikTok.Feed(
                results=BetterList((
                    result
                    for result in results
                ))
            )

        return TikTok.Feed(results=BetterList((results,)))
    

    async def fetch_video(
        self: "TikTok", 
        id: Optional[int] = None,
        url: Optional[str] = None
    ) -> dict:
        """
        Fetches a TikTok video by its ID or URL.

        Parameters:
            id (int, optional): The ID of the video. Defaults to None.
            url (str, optional): The URL of the video. Defaults to None.

        Returns:
            dict: The response from the server.
        """
        
        assert id or url, \
            "You must provide either an ID or a URL."
        
        if id:
            data = await self.__request(
                "GET", 
                f"aweme/v1/feed",
                params={"aweme_id": id}
            )

        elif url:
            async with self.__session.session() as session:
                async with session.get(url, proxy=self.__proxied_session.proxy(), allow_redirects=True) as response:
                    url = str(response.url)

            assert (ids := expressions.tiktok_aweme_id.findall(url)), \
                "Please provide a valid TikTok URL."
                
            data = await self.__request(
                "GET", 
                f"aweme/v1/feed",
                params={"aweme_id": ids[0]}
            )
            
        if not tuple(r for r in data["aweme_list"] if r["aweme_id"] == ids[0]):
            raise CommandError("Couldn't fetch that video; TikTok is pasted.")
            
        return await self.__format_data(data)
        
        
class APIWrapper:
    def __init__(
        self: "APIWrapper",
        name: str,
        default_url: str,
        headers: Optional[Dict[ str, Any ]] = None
    ) -> NoReturn:
        self.name = name
        self.default_url = default_url
        self.headers = headers or { }
        
        self.__session = HTTPClient(proxy=False)
        
        
    def __repr__(self: "APIWrapper") -> str:
        return f"""<APIWrapper name={self.name!r} url={self.default_url!r}>"""
        
    
    async def request(
        self: "APIWrapper", 
        method: str,
        endpoint: str,
        **kwargs: Dict[ str, Any ]
    ) -> dict:
        """
        Sends an HTTP request to the API.

        Parameters:
            method (str): The HTTP method to use for the request. Can be "GET" or "POST".
            endpoint (str): The endpoint to send the request to.
            kwargs (dict, optional): The request information.
        
        Returns:
            dict: The response from the server.
        """
        
        async with self.__session.session() as session:
            return await session.request(
                method=method,
                url=self.default_url+endpoint,
                headers=self.headers or kwargs.get("headers", DICT),
                **(kwargs or { })
            )
            
