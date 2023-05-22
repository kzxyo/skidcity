import inspect, discord, math, psutil, aiohttp, requests, random, pytz, shutil, os, humanize, traceback, yarl, re, asyncio, time, colorgram, contextlib, orjson, tuuid, difflib, subprocess, sys, openai, tiktoken, json, aiomysql, logging
from PIL import Image
from discord.ext import commands
from io import BytesIO
from datetime import datetime, timedelta
from .context import Context
from .paginator import Paginator, text_creator
from pytube import YouTube
from . import DL as http, config
from .advancedutils import coroutine
from wordcloud import WordCloud
from multiprocessing import Process
from gtts import gTTS
from bs4 import BeautifulSoup
from typing import Iterator, AsyncIterator, Any, Optional, Union, Callable, Iterable, AsyncIterable, List, Dict, Awaitable, Type, NamedTuple, Generator, TypeVar, Tuple
from yt_dlp import YoutubeDL
from typing_extensions import Self
from datetime import timedelta
import asyncstdlib as a
from discord.utils import maybe_coroutine
from asyncio import as_completed, Semaphore
from asyncio.futures import isfuture
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from itertools import chain


_T = TypeVar("_T")
_S = TypeVar("_S")


class nullcontext(AbstractContextManager, AbstractAsyncContextManager):
    def __init__(self, enter_result: Any = None) -> None:
        self.enter_result = enter_result

    def __enter__(self) -> Any:
        return self.enter_result

    def __exit__(self, *excinfo) -> None:
        return

    async def __aenter__(self) -> Any:
        return self.enter_result

    async def __aexit__(self, *excinfo) -> None:
        return


class AsyncFilter(AsyncIterator[_T], Awaitable[List[_T]]):
    def __init__(self, func: Callable[[_T], Union[bool, Awaitable[bool]]], iterable: Union[AsyncIterable[_T], Iterable[_T]]) -> None:
        self.__func: Callable[[_T], Union[bool, Awaitable[bool]]] = func
        self.__iterable: Union[AsyncIterable[_T], Iterable[_T]] = iterable

        if isinstance(iterable, AsyncIterable):
            if asyncio.iscoroutinefunction(func):
                self.__generator_instance = self.__async_generator_async_pred()
            else:
                self.__generator_instance = self.__async_generator_sync_pred()

        elif asyncio.iscoroutinefunction(func):
            self.__generator_instance = self.__sync_generator_async_pred()
        else:
            raise TypeError('Must be either an async predicate, an async iterable, or both')


    async def __sync_generator_async_pred(self) -> AsyncIterator[_T]:
        for item in self.__iterable:
            if await self.__func(item):
                yield item


    async def __async_generator_sync_pred(self) -> AsyncIterator[_T]:
        async for item in self.__iterable:
            if self.__func(item):
                yield item


    async def __async_generator_async_pred(self) -> AsyncIterator[_T]:
        async for item in self.__iterable:
            if await self.__func(item):
                yield item


    async def __flatten(self) -> List[_T]:
        return [item async for item in self]


    def __aiter__(self) -> Self:
        return self


    def __await__(self) :
        return self.__flatten().__await__()
        

    def __anext__(self) -> Awaitable[_T]:
        return self.__generator_instance.__anext__()


def async_filter(func: Callable[[_T], Union[bool, Awaitable[bool]]], iterable: Union[AsyncIterable[_T], Iterable[_T]]) -> AsyncFilter[_T]:
    return AsyncFilter(func, iterable)


async def async_enumerate(async_iterable: AsyncIterable[_T], start: int = 0) -> AsyncIterator[Tuple[int, _T]]:
    async for item in async_iterable:
        yield start, item
        start += 1


async def _sem_wrapper(sem, task):
    async with sem:
        return await task


def bounded_gather_iter(*coros_or_futures, limit: int = 4, semaphore: Optional[Semaphore] = None) -> Iterator[Awaitable[Any]]:

    loop = asyncio.get_running_loop()

    if semaphore is None:
        if not isinstance(limit, int) or limit <= 0:
            raise TypeError("limit must be an int > 0")
        semaphore = Semaphore(limit)
    pending = []
    for cof in coros_or_futures:
        if isfuture(cof) and cof._loop is not loop:
            raise ValueError("futures are tied to different event loops")
        cof = _sem_wrapper(semaphore, cof)
        pending.append(cof)

    return as_completed(pending)


class AsyncIter(AsyncIterator[_T], Awaitable[List[_T]]):
    def __init__(self, iterable: Iterable[_T], delay: Union[float, int] = 0, steps: int = 0, circuit_breaker=None) -> None:
        self._delay = delay

        if iterable == True:
            self._iterator = True
        else:
            self._iterator = a.any_iter(iterable)

        self._i = -1
        self._circuit_breaker = circuit_breaker
        self._steps = steps
        self._map = None


    def __aiter__(self) -> Self:
        return self


    async def __anext__(self) -> _T:
        
        if self._circuit_breaker:
            raise StopAsyncIteration

        if self._iterator == True:
            item = True

        else:
            item = await a.anext(self._iterator)

        if self._delay != -1 and self._i == self._steps:
            await asyncio.sleep(self._delay)
            self._i = 0

        self._i += 1

        if self._map:
            item = await self._map(item)

        return item


    def __await__(self) -> Generator[Any, None, List[_T]]:
        return self.flatten().__await__()


    async def next(self, default: Any = ...) -> _T:

        try:
            value = await self.__anext__()
        except StopAsyncIteration:
            if default is ...:
                raise
            value = default
        return value


    async def flatten(self) -> List[_T]:
        return [item async for item in self]


    def filter(self, function: Callable[[_T], Union[bool, Awaitable[bool]]]) -> AsyncFilter[_T]:
        return async_filter(function, self)


    def enumerate(self, start: int = 0) -> AsyncIterator[Tuple[int, _T]]:
        return async_enumerate(self, start)


    async def without_duplicates(self) -> AsyncIterator[_T]:

        _temp = set()

        async for item in self:
            if item not in _temp:
                yield item
                _temp.add(item)

        del _temp


    async def find(self, predicate: Callable[[_T], Union[bool, Awaitable[bool]]], default: Optional[Any] = None) -> AsyncIterator[_T]:
        
        while True:
            try:
                elem = await self.__anext__()
            except StopAsyncIteration:
                return default

            ret = await maybe_coroutine(predicate, elem)
            if ret:
                return elem


    def map(self, func: Callable[[_T], Union[_S, Awaitable[_S]]]) -> None:
        
        if not callable(func):
            raise TypeError('Mapping must be a callable')

        self._map = a.sync(func)
        return


class aiter(AsyncIter):
    def __init__(self, iterable: Iterable[_T], circuit_breaker=None, delay: Union[float, int] = 0.05, steps: int = 1) -> None:
        super().__init__(iterable, delay, steps, circuit_breaker=circuit_breaker)


def source(obj: object) -> str:
    return inspect.getsource(obj)


def determine_prefix(bot: 'Vile', message: discord.Message) -> str:
    customprefix = bot.cache.customprefixes.get(message.author.id)
    if customprefix:
        return customprefix

    guildprefix = bot.cache.guildprefixes.get(message.guild.id)
    if guildprefix:
        return guildprefix

    return commands.when_mentioned_or(bot.prefix)(bot, message)


def find(iterable: Iterator[Any], /, key: Callable[[Any], bool]) -> Optional[Any]:
    for item in iterable:
        if key(item):
            return item
    return None


def filter(iterable: Iterator[Any], /, key: Callable[[Any], bool] = bool) -> Iterator[Any]:
    for item in iterable:
        if key(item):
            yield item


def as_chunks(iterator: Iterable[Any], max_size: int) -> Iterator[Any]:
    ret = list()
    n = 0
    for item in iterator:
        ret.append(item)
        n += 1
        if n == max_size:
            yield ret
            ret = list()
            n = 0
    if ret:
        yield ret


async def handle_result(ctx: Context, result: Any) -> Optional[discord.Message]:
    
    if isinstance(result, discord.Message):
        pass
    
    if isinstance(result, discord.File):
        return await ctx.send(file=result)

    if isinstance(result, discord.Embed):
        return await ctx.send(embed=result)
        
    if isinstance(result, discord.Button):
        return await ctx.send(view=discord.ui.View().add_item(result))

    if not isinstance(result, str):
        result = repr(result)

    if len(result) <= 2000:
        if result.strip() == '':
            result = "\u200b"

        if ctx.bot.http.token:
            result = result.replace(ctx.bot.http.token, '[token]')

        return await ctx.send(
            result,
            allowed_mentions=discord.AllowedMentions.none()
        )
        
    paginator = text_creator(result, 1980, prefix='```py\n', suffix='```')

    interface = Paginator(ctx.bot, paginator, ctx, invoker=ctx.author.id, timeout=30)
    interface.default_pagination(True)
    return await interface.start()


async def send_success(ctx: Context, message: str, delete_after: Optional[int] = None) -> discord.Message:

    return await ctx.reply(
        embed=discord.Embed(
            color=ctx.bot.color,
            description=f'{ctx.bot.done} {ctx.author.mention}**:** {message}'
        ),
        delete_after=delete_after
    )


async def send_error(ctx: Context, message: str, delete_after: Optional[int] = None) -> discord.Message:

    return await ctx.reply(
        embed=discord.Embed(
            color=ctx.bot.color,
            description=f'{ctx.bot.fail} {ctx.author.mention}**:** {message}'
        ),
        delete_after=delete_after
    )


async def send_help(ctx: Context) -> discord.Message:
    
    command=ctx.command
    bot = ctx.bot
    done = bot.done
    fail = bot.fail
    warn = bot.fail
    reply = bot.reply
    dash = bot.dash
    success = bot.color
    error = bot.color
    warning = bot.color
    nl='\n'

    if not hasattr(command, 'commands'):
        cmd=command
        name=f'{cmd.full_parent_name} {cmd.name}'
        desc=cmd.description or 'none'
        aliases=', '.join(cmd.aliases) or 'none'
        syntax=cmd.brief or 'none'
        example=cmd.help or 'none'
        
        embed=discord.Embed(
            color=bot.color, 
            timestamp=datetime.now()
        )
        embed.set_author(
            name=name,
            icon_url=ctx.bot.user.display_avatar
        )
        embed.add_field(
            name=f'{dash} Info',
            value=f'{reply} **description:** {desc}{nl+f"{reply} **aliases:** {aliases}" if aliases else ""}',
            inline=False
        )
        embed.add_field(
            name=f'{dash} Usage',
            value=f'{reply} **syntax:** {syntax}\n{reply} **example:** {example}',
            inline=False
        )
        embed.set_footer(
            text=cmd.cog_name
        )
        return await ctx.reply(embed=embed)
        
    if hasattr(command, 'commands'):
        embeds=list()
        aliases=', '.join(command.aliases)
        num=1
        embed=discord.Embed(
            color=bot.color, 
            timestamp=datetime.now()
        )
        embed.set_author(
            name=ctx.command.name,
            icon_url=ctx.bot.user.display_avatar
        )
        embed.add_field(
            name=f'{dash} Info',
            value=f'{reply} **description:** {command.description or "none"}{nl+f"{reply} **aliases:** {aliases}" if aliases else ""}',
            inline=False
        )
        embed.add_field(
            name=f'{dash} Usage',
            value=f'{reply} **syntax:** {command.brief or "none"}\n{reply} **example:** {command.help or "none"}',
            inline=True
        )
        embed.set_footer(
            text=f'{num}/{len(set(ctx.command.walk_commands()))+1}'
        )
        embeds.append(embed)
        
        for command in set(command.walk_commands()):
            num+=1
            aliases=', '.join(getattr(command, 'aliases', list()))
            embed=discord.Embed(color=bot.color, timestamp=datetime.now())
            embed.set_author(
                name=f'{command.full_parent_name} {getattr(command, "name", None) or "none"}',
                icon_url=bot.user.display_avatar
            )
            embed.add_field(
                name=f'{dash} Info',
                value=f'{reply} **description:** {getattr(command, "description", None) or "none"}{nl+f"{reply} **aliases:** {aliases}" if aliases else ""}',
                inline=False
            )
            embed.add_field(
                name=f'{dash} Usage',
                value=f'{reply} **syntax:** {getattr(command, "brief", None) or "none"}\n{reply} **example:** {getattr(command, "help", None) or "none"}',
                inline=True
            )
            embed.set_footer(
                text=f'{num}/{len(set(ctx.command.walk_commands()))+1}'
            )
            embeds.append(embed)
            
        interface = Paginator(bot, embeds, ctx, timeout=30, invoker=ctx.author.id)
        interface.default_pagination()
            
        return await interface.start()


def size(size_in_bytes: int) -> str:
    units = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')
    power = int(math.log(max(abs(size_in_bytes), 1), 1024))

    return multi_replace(
        f'{size_in_bytes / (1024 ** power):.2f}{units[power]}', 
        {'KiB': 'KB', 'MiB': 'MB', 'GiB': 'GB', 'TiB': 'TB', 'PiB': 'PB', 'ZiB': 'ZB', 'YiB': 'YB'}
    )


def multi_replace(text: str, to_replace: dict, once: bool = False) -> str:
    for r1, r2 in to_replace.items():
        if once:
            text=text.replace(str(r1), str(r2), 1)
        else:
            text=text.replace(str(r1), str(r2))
    return text


class obj(object):
    def __init__(self, *args, **kwargs):
        for arg in args:
            self.__dict__.update(arg)

        self.__dict__.update(kwargs)

    def __getitem__(self, name):
        return self.__dict__.get(name, None)

    def __setitem__(self, name, val):
        return self.__dict__.__setitem__(name, val)

    def __delitem__(self, name):
        if self.__dict__.has_key(name):
            del self.__dict__[name]

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __setattr__(self, name, val):
        return self.__setitem__(name, val)

    def __delattr__(self, name):
        return self.__delitem__(name)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __repr__(self):
        return self.__dict__.__repr__()

    def __str__(self):
        return self.__dict__.__str__()


def ordinal(number: int) -> str:
    return '%d%s' % (number, 'tsnrhtdd'[(number // 10 % 10 != 1) * (number % 10 < 4) * number % 10 :: 4])


async def google_images(query: str, safe: bool = False) -> list:
        
    params = {
        'api_key': random.choice([
            '34d7e5bcb2a7cf7648bf6291b2fef6864110fc3d3e230975957fc8320c96ac1d', 
            '73ba8e01b960793afa064bdda00da0fd1f2dec95742f4360efc0fb09c4b6a592', 
            'fec4630d07602a39337dda740b6879f90de865135bd771782b5339bc2202bdcc',
            '3bd395020ed338a2edbee26473c5260ca4c05347dac3e29fc1197c688bbac95d'
        ]),
        'engine': 'google',
        'q': query,
        'location': 'United States',
        'google_domain': 'google.com',
        'gl': 'us',
        'hl': 'en',
        'tbm': 'isch',
        'ijn': '1',
    }

    if safe is True:
        params['safe'] = 'active'

    data = await http.get('https://serpapi.com/search', params=params)
    return [
        {'url': result['original'], 'title': result['title'], 'source': result['source']}
        for result in data['images_results']
    ]


async def google_search(query: str) -> list:
        
    params = {
        'api_key': random.choice([
            '34d7e5bcb2a7cf7648bf6291b2fef6864110fc3d3e230975957fc8320c96ac1d', 
            '73ba8e01b960793afa064bdda00da0fd1f2dec95742f4360efc0fb09c4b6a592', 
            'fec4630d07602a39337dda740b6879f90de865135bd771782b5339bc2202bdcc',
            '3bd395020ed338a2edbee26473c5260ca4c05347dac3e29fc1197c688bbac95d'
        ]),
        'engine': 'google',
        'q': query,
        'location': 'United States',
        'google_domain': 'google.com'
    }


    data = await http.get('https://serpapi.com/search', params=params)
    return [
        {'url': result['link'], 'title': result['title'], 'description': result['snippet']}
        for result in data['organic_results']
    ]


def get_parts(code: str):
    
    params = code.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]


async def to_object(code: str):
    
    embed = {}
    fields = []
    content = None
    timestamp = None
    files = []
    delete=None
    view = discord.ui.View()

    for part in get_parts(code):

        if part.startswith('content:'):
            content = part[len('content:'):]

        if part.startswith('url:'):
            embed['url'] = part[len('url:'):]

        if part.startswith('title:'):
            embed['title'] = part[len('title:'):]

        if part.startswith('delete:'):
            if part[len('delete:'):].strip().isdigit():
                delete=int(part[len('delete:'):].strip())

        if part.startswith('description:'):
            embed['description'] = part[len('description:'):]

        if part.startswith('footer:'):
            embed['footer'] = part[len('footer:'):]

        if part.startswith('color:'):
            try:
                embed['color'] = int(part[len('color:'):].strip().strip('#'), 16)
            except:
                embed['color'] = 0x2f3136

        if part.startswith('image:'):
            embed['image'] = {'url': part[len('description:'):]}

        if part.startswith("thumbnail:"):
            embed['thumbnail'] = {'url': part[len('thumbnail:'):]}

        if part.startswith('attach:'):
            files.append(
                discord.File(
                    BytesIO(await http.read(part[len('attach:'):].replace(' ', ''), proxy=True)), yarl.URL(part[len('attach:') :].replace(' ', '')).name)
            )

        if part.startswith('author:'):
            z = part[len('author:'):].split(' && ')
            icon_url = None
            url = None
            for p in z[1:]:
                if p.startswith('icon:'):
                    p = p[len('icon:') :]
                    icon_url = p.replace(' ', '')
                elif p.startswith('url:'):
                    p = p[len('url:'):]
                    url = p.replace(' ', '')
            try:
                name = z[0] if z[0] else None
            except:
                name = None

            embed['author'] = {'name': name}
            if icon_url:
                embed['author']['icon_url'] = icon_url
            if url:
                embed['author']['url'] = url

        if part.startswith('field:'):
            z = part[len('field:'):].split(' && ')
            value = None
            inline='true'
            for p in z[1:]:
                if p.startswith('value:'):
                    p = p[len('value:'):]
                    value = p
                elif p.startswith('inline:'):
                    p = p[len('inline:'):]
                    inline = p.replace(' ', '')
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            
            if isinstance(inline, str):
                if inline == 'true':
                    inline = True

                elif inline == 'false':
                    inline = False

            fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z = part[len('footer:'):].split(' && ')
            text = None
            icon_url = None
            for p in z[1:]:
                if p.startswith('icon:'):
                    p = p[len('icon:'):]
                    icon_url = p.replace(' ', '')
            try:
                text = z[0] if z[0] else None
            except:
                pass
                
            embed['footer'] = {'text': text}
            if icon_url:
                embed['footer']['icon_url'] = icon_url

        if part.startswith('label:'):
            z = part[len('label:'):].split(' && ')
            label = 'no label'
            url = None
            for p in z[1:]:
                if p.startswith('link:'):
                    p = p[len('link:'):]
                    url = p.replace(' ', '')
                    
            try:
                label = z[0] if z[0] else None
            except:
                pass
                

            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link, 
                    label=label, 
                    url=url
                )
            )
            
        if part.startswith('image:'):
            z = part[len('image:'):]
            embed['image'] = {'url': z}
            
        if part.startswith('timestamp:'):
            z = part[len('timestamp:'):].replace(' ', '')
            if z == 'true':
                timestamp = True
                
    if not embed:
        embed = None
    else:
        embed['fields'] = fields
        embed = discord.Embed.from_dict(embed)

    if not code.count('{') and not code.count('}'):
        content = code
        
    if timestamp:
        embed.timestamp = datetime.now(pytz.timezone('America/New_York'))

    return {'content': content, 'embed': embed, 'files': files, 'view': view, 'delete_after': delete}


async def embed_replacement(user, params):

    if '{user}' in params:
        params = params.replace('{user}', user)
    if '{user.mention}' in params:
        params = params.replace('{user.mention}', user.mention)
    if '{user.name}' in params:
        params = params.replace('{user.name}', user.name)
    if '{user.avatar}' in params:
        params = params.replace('{user.avatar}', user.display_avatar.url)
    if '{user.color}' in params:
        params = params.replace('{user.color}', f"#{hex(await dominant_color(user.display_avatar.url)).replace('0x', '')}")
    if '{user.joined_at}' in params:
        params = params.replace(
            '{user.joined_at}', discord.utils.format_dt(user.joined_at, style='R')
        )
    if '{user.created_at}' in params:
        params = params.replace(
            '{user.created_at}', discord.utils.format_dt(user.created_at, style='R')
        )
    if '{user.discriminator}' in params:
        params = params.replace('{user.discriminator}', user.discriminator)
    if '{guild.name}' in params:
        params = params.replace('{guild.name}', user.guild.name)
    if '{guild.count}' in params:
        params = params.replace('{guild.count}', str(user.guild.member_count))
    if '{guild.count.format}' in params:
        params = params.replace(
            '{guild.count.format}', ordinal(len(user.guild.members))
        )
    if '{guild.id}' in params:
        params = params.replace('{guild.id}', user.guild.id)
    if '{guild.created_at}' in params:
        params = params.replace(
            '{guild.created_at}',
            discord.utils.format_dt(user.guild.created_at, style='R'),
        )
    if '{guild.boost_count}' in params:
        params = params.replace(
            '{guild.boost_count}', str(user.guild.premium_subscription_count)
        )
    if '{guild.booster_count}' in params:
        params = params.replace(
            '{guild.booster_count}', str(len(user.guild.premium_subscribers))
        )
    if '{guild.boost_count.format}' in params:
        params = params.replace(
            '{guild.boost_count.format}',
            ordinal(str(len(user.guild.premium_subscriber_count))),
        )
    if '{guild.booster_count.format}' in params:
        params = params.replace(
            '{guild.booster_count.format}',
            ordinal(str(len(user.guild.premium_subscriber_count))),
        )
    if '{guild.boost_tier}' in params:
        params = params.replace('{guild.boost_tier}', str(user.guild.premium_tier))
    if '{guild.icon}' in params:
        if user.guild.icon:
            params = params.replace('{guild.icon}', user.guild.icon.url)
        else:
            params = params.replace('{guild.icon}', '')
    return params


def determine_filter(bot: 'Vile', message: discord.Message) -> bool:

    if bot.cache.chatfilter.get(message.guild.id) is None:
        return False

    msg = message.content
    for word in bot.cache.chatfilter[message.guild.id]:
        for char in message.content:
            if not char.isdigit() and not char.isalpha():
                msg = msg.replace(char, '')
                            
        if word in msg.replace('\n', ' ').split():
            return True

        else:
            if word.endswith('*'):
                word = word.strip('*')
                for w in msg.replace('\n', ' ').split():
                    if word in w:
                        return True

    return False


def get_xp(level: int) -> int:
    return math.ceil(math.pow((level - 1) / (0.05 * (1 + math.sqrt(5))), 2))


def get_level(xp: int) -> int:
    return math.floor(0.05 * (1 + math.sqrt(5)) * math.sqrt(xp)) + 1


def xp_to_next_level(level: int) -> int:
    return get_xp(level + 1) - get_xp(level)


def xp_from_message(message: discord.Message) -> int:
    words = message.content.split()
    eligible_words = 0
    for x in words:
        if len(x) > 1:
            eligible_words += 1
    xp = eligible_words + (10 * len(message.attachments))
    if xp == 0:
        xp = 1

    return min(xp, 50)


def moment(time: datetime, accuracy: int = 1, separator: str = ', ') -> str:

    time = datetime.now().timestamp() - time.timestamp()
    m, s = divmod(time, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    y, d = divmod(d, 365)

    components = []
    if y > 0:
        components.append(f"{int(y)} year" + ("s" if y != 1 else ""))
    if d > 0:
        components.append(f"{int(d)} day" + ("s" if d != 1 else ""))
    if h > 0:
        components.append(f"{int(h)} hour" + ("s" if h != 1 else ""))
    if m > 0:
        components.append(f"{int(m)} minute" + ("s" if m != 1 else ""))
    if s > 0:
        components.append(f"{int(s)} second" + ("s" if s != 1 else ""))

    return ", ".join(components[:accuracy])


def intword(num: int) -> str:
    return humanize.intword(num).replace('.0', '')
    

async def get_youtube(destination: Union[Context, discord.Message], bot: 'Vile', link: str) -> Optional[discord.Message]:

    try:
        video_data = YouTube(link)

        duration = multi_replace(
            moment((datetime.now() - timedelta(seconds=video_data.length)), 2),
            {' minutes': 'm', ' seconds': 's'}
        )
        url = (await asyncio.to_thread(lambda: video_data.streams.get_highest_resolution())).url
        download = await file(url, f'{bot.user.name} youtube.mp4')
        
        embed = discord.Embed(
            color=bot.color,
            description=video_data.description
        )
        embed.set_author(
            name=f'@{video_data.author} | {duration} long',
            icon_url='https://cdn.discordapp.com/emojis/1056868832981045279.png?size=4096',
            url=url
        )
        embed.set_footer(text=f'{intword(video_data.views)} views')

        return await destination.reply(
            embed=embed,
            file=download
        )
    except Exception as e:
        return traceback.format_exc()


async def file(url: str, filename: str = 'unknown.png'):
    return discord.File(BytesIO(await http.read(url)), filename=filename)


async def create_wordcloud(text: Union[str, List[discord.Message]], limit: int = 5_000_000) -> BytesIO:

    if isinstance(text, list):
        text = ' '.join(text)

    wc = WordCloud(mode='RGBA', max_words=limit, background_color=None, height=400, width=700)
    await asyncio.to_thread(lambda: wc.generate(text))
    wc.to_file(filename='wordcloud.png')

    ret = BytesIO(open('wordcloud.png', 'rb').read())

    if os.path.exists('wordcloud.png'):
        os.remove('wordcloud.png')

    return ret


@coroutine
def text_to_speech(language: str, text: str) -> BytesIO:

    ret = list(gTTS(text, lang=language).stream())
    return BytesIO(ret[0])


async def get_tiktok_data(url: str) -> dict:

    str_id = re.findall('https://www.tiktok.com/@.*?/video/(\d+)', url)
    if str_id:
        str_id = str_id[0]
    else:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html, application/xhtl+xml, application/xml; q=0.9, image/avif, image/webp, */*; q=0.8'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                url = str(resp.url)
                str_id = re.findall('https://www.tiktok.com/@.*?/video/(\d+)', url)
                if str_id:
                    str_id = str_id[0]
    
    seconds = time.time()
    uuid = os.urandom(8).hex()
    openudid = uuid

    js = await http.get('https://api-h2.tiktokv.com/aweme/v1/feed/', params={'aweme_id': str_id})
    video = js['aweme_list'][0]['video']
    l = list()

    if js['aweme_list'][0].get('image_post_info') is not None:
        for i in js['aweme_list'][0]['image_post_info']:
            l.append(i['display_image']['url_list'][0])
        image_urls = l
        is_video = False
    else:
        is_video = True
        image_urls = video['play_addr']['url_list'][0]
    
    stats = js['aweme_list'][0]['statistics']
    stats['like_count'] = stats.pop('digg_count')
    author = js['aweme_list'][0]['author']
    avatar = author['avatar_medium']['url_list'][1]
    username = author['unique_id']
    nickname = author['nickname']
    music = js['aweme_list'][0]['music']
    desc = js['aweme_list'][0]['desc']
    
    data = {
        'is_video': is_video,
        'urls': image_urls,
        'desc': desc,
        'username': username,
        'nickname': nickname,
        'avatar': avatar,
        'stats': stats,
        'url': url
    }

    if music:
        ss = dict()
        title = music.get('title')
        music_author = music.get('author')
        album = music.get('album')
        duration = music.get('duration')
        if title:
            ss['title'] = title
        if music_author:
            ss['author'] = music_author
        if album:
            ss['album'] = album
        if duration:
            ss['duration'] = duration
        if ss:
            data['music'] = ss
    
    return data


async def get_tiktok(destination: Union[Context, discord.Message], bot: 'Vile', link: str) -> Optional[discord.Message]:

    try:
        cached_data = await bot.redis.get(f'tiktok:{link}')
        
        if cached_data is None:
            video_data = await get_tiktok_data(link)
            await bot.redis.set(f'tiktok:{link}', orjson.dumps(video_data), ex=86400)
            
        else:
            video_data = orjson.loads(cached_data)

        duration = multi_replace(
            moment((datetime.now() - timedelta(seconds=video_data['music']['duration'])), 2),
            {' minutes': 'm', ' seconds': 's'}
        )

        embed = discord.Embed(
            color=bot.color,
            description=video_data['desc']
        )
        embed.set_author(
            name=f"@{video_data['username']} | {duration} long",
            icon_url='https://cdn.discordapp.com/emojis/1017812426164551762.png?size=4096',
            url=video_data['urls'],
        )
        embed.set_footer(text=f"💬 {video_data['stats']['comment_count']:,} | 👍 {video_data['stats']['like_count']:,} | 🔗 {video_data['stats']['share_count']:,} ({video_data['stats']['play_count']:,} views)\n🎵 {video_data['music']['title']} (by {video_data['music']['author']})")
        
        return await destination.reply(
            embed=embed,
            file=await file(video_data['urls'], f'{bot.user.name} tiktok.mp4')
        )
    except:
        return None


async def get_video_data(url: str) -> dict:
    
    with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as dl:
        return await asyncio.to_thread(lambda: dl.extract_info(url, download=False))


async def get_twitter(destination: Union[Context, discord.Message], bot: 'Vile', link: str) -> Optional[discord.Message]:

    try:
        cached_data = await bot.redis.get(f'twitter:{link}')
        
        if cached_data is None:
            video_data = await get_video_data(link)
            await bot.redis.set(f'twitter:{link}', orjson.dumps(video_data), ex=86400)
            
        else:
            video_data = orjson.loads(cached_data)

        embed = discord.Embed(
            color=bot.color,
            description=video_data['description']
        )
        embed.set_author(
            name=f"@{video_data['uploader']}",
            icon_url='https://cdn.discordapp.com/emojis/1088888839034130522.png?size=4096',
            url=video_data['url'],
        )
        embed.set_footer(text=f"💬 {video_data['comment_count']:,} | 👍 {video_data['like_count']:,} | 🔗 {video_data['repost_count']:,}")
        
        return await destination.reply(
            embed=embed,
            file=await file(video_data['url'], f'{bot.user.name} twitter.mp4')
        )
    except:
        return None


async def get_soundcloud(destination: Union[Context, discord.Message], bot: 'Vile', link: str) -> Optional[discord.Message]:

    try:
        cached_data = await bot.redis.get(f'soundcloud:{link}')
        
        if cached_data is None:
            video_data = await get_video_data(link)
            await bot.redis.set(f'soundcloud:{link}', orjson.dumps(video_data), ex=86400)
            
        else:
            video_data = orjson.loads(cached_data)
        
        duration = multi_replace(
            moment((datetime.now() - timedelta(seconds=video_data['duration'])), 2),
            {' minutes': 'm', ' seconds': 's'}
        )

        embed = discord.Embed(
            color=bot.color,
            description=video_data['description']
        )
        embed.set_author(
            name=f"@{video_data['uploader']} | {duration} long",
            icon_url='https://cdn.discordapp.com/emojis/1088900684998520953.png?size=4096',
            url=video_data['url'],
        )
        embed.set_footer(text=f"💬 {video_data['comment_count']:,} | 👍 {video_data['like_count']:,} | 🔗 {video_data['repost_count']:,} ({video_data['view_count']:,} views)")
        
        return await destination.reply(
            embed=embed,
            file=await file(video_data['url'], f'{bot.user.name} soundcloud.mp3')
        )
    except:
        return traceback.format_exc()


async def get_medal(destination: Union[Context, discord.Message], bot: 'Vile', link: str) -> Optional[discord.Message]:

    try:
        cached_data = await bot.redis.get(f'medal:{link}')
        
        if cached_data is None:
            video_data = await get_video_data(link)
            await bot.redis.set(f'medal:{link}', orjson.dumps(video_data), ex=86400)
            
        else:
            video_data = orjson.loads(cached_data)
            
        embed = discord.Embed(
            color=bot.color,
            description=video_data['description']
        )
        embed.set_author(
            name=f"@{video_data['uploader']}",
            icon_url='https://cdn.discordapp.com/emojis/1088950069035802694.png?size=4096',
            url=video_data['url'],
        )
        embed.set_footer(text=f"💬 {video_data['comment_count']:,} | 👍 {video_data['like_count']:,} ({intword(video_data['view_count'])} views)")
        
        return await destination.reply(
            embed=embed,
            file=await file(video_data['url'], f'{bot.user.name} medal.mp4')
        )
    except:
        return None


def fmtseconds(seconds: Union[int, float], unit='microseconds') -> str:
    return humanize.naturaldelta(timedelta(seconds=seconds), minimum_unit=unit)


async def get_invites(message: discord.Message):

    ret = list()
    for word in message.content.split():
        if '.gg/' in word or '/invite/' in word:
            ret.append(await message._state.fetch_invite(code))

    return ret


async def pack(ctx: Context, user: discord.Member, limit: int = 5) -> None:

    url = f"https://discord.com/api/v10/channels/{ctx.channel.id}/messages"

    packs = [
        "why you still talkin to me nig you smell like expired sea food dust dumb ass nig you hideous as shit you dont know how to run because you got inverted kneecaps dumb ass nig you got that shit as an inherited trait from yo grandmother yo dumb ass nig you got mad at her and started slamming a hammer on the back of her knee to fix that shit hoping it would magically fix yours you dumb ass nig",
        "Shut up nig yo bus driver got sick of you smoking ciggaretes at the back of the school-bus so he recorded you with a Black and White Vintage Camera and got you expelled from school nig you dumb as shit",
        "nope nig that's why yo ass ran away from home and got into an altercation with Team Rocket from Pokemon boy them nigs got to throwing pokeballs at yo ass unleashing all the legendary pokemon just to kill you nig;Sike nig yo dumb ass traded yo Samsung Galaxy Note10 for a Pillow Pet because you always lonely at night nig fuck is you talkin bout",
        "This nigga ugly as shit you fat ass boy you been getting flamed by two donkeys when you walk to the store and one of them smacked you in the forehead fuckboy and then you go to come in with uh ???? and smacked you in the bootycheeks fuckboy you dirty as shit boy everytime you go to school nigga you get bullied by 10 white kids that say you gay behind the bus fuckboy suck my dick nigga unknown as shit nigga named nud you been getting hit by two frozen packs when you walk into the store fuckboy suck my dick unknown ass nigga named nud nigga you my son nigga hold on, ay creedo you can flame this nigga for me? Yeah im in this bitch fuck is you saying nigga my nigga.",
        "thats cool in all my nigga but you're ass is build like my grandma with you're no neck body built bath and body works double or nothing for a barbie girl doll that built like ken stupid ass my nigga. You brush your teeth with the cum from your dad's left cock that was in your mom and aunt's asshole. and your calling me a fuckboy? NIGGA YOURE BUILT LIKE AN ENDERMAN WITH HEIGHT SWAPPED TO WIDTH YOUR ASS CHEEKS LOOK LIKE 2 JIGGLYPUFFS RUBBING AGAINST EACH OTHER FOR \"BREEDING\" TO MAKE A BUZZWOLE EGG. You hack pokemon but you cant hack a new dad my nigga you thought your dad died in minecraft and didnt respawn yet.",
        "I kno ass aint talkin boy you look like a discombobulated toe nail nigga whenever you take a bath your jerk off then the next you smell like ass nasty nigga fuck is you saying nigga you got smacked with a gold fish in the grocery store and smacked the gold fish with fish food nasty bitch boy you ugly as shit fuck is you saying FAT BOY ugly bitch my nigga i caught yo ass slap boxing yo granny with an apple fuck is you saying my nigga when you get horny you jerk off to donkeys fuck is you saying ugly bitch",
        "lil bitchass nigga i know you aint talking to me with that greasy ass mcdonalds french fries lubricated fingers nigga you are dirty as shit you are the cousin of the dirtiest man in the entire fucking word nigga you disgusting as shit nigga your nickname be the human repellant cause no bitches want to be near you dirtyass nigga shut the fuck up with any excuses i know u aint talking to me with that nastyass neckbeard lil redhead headass boy",
    ]
    random.shuffle(packs)

    def pp():
        requests.post(
            url, 
            data={'content': f'{random.choice(packs)} {user.mention}'},
            headers={'Authorization': f"Bot {config.authorization.vile_token}"}
        )

    for i in range(limit):
        Process(target=pp).start()


async def getwhi(query: str) -> AsyncIterator[str]:

    url = f"https://weheartit.com/search/entries?query={query.replace(' ', '+')}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=config.proxy.webshare) as resp:
            soup = BeautifulSoup(await resp.text(), features='html.parser')
            divs = str(soup.find_all('div', class_='entry grid-item'))
            soup2 = BeautifulSoup(divs, features='html.parser')
            badge = soup2.find_all(class_='entry-badge')
            images = soup2.find_all('img')
            links = list()
            for image in images:
                if 'data.whicdn.com/images/' in str(image):
                    yield image['src']


async def getwhiuser(query: str) -> AsyncIterator[str]:

    url = f"https://weheartit.com/{query.replace(' ', '+')}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=config.proxy.webshare) as resp:
            soup = BeautifulSoup(await resp.text(), features='html.parser')
            divs = str(soup.find_all('div', class_='entry grid-item'))
            soup2 = BeautifulSoup(divs, features='html.parser')
            badge = soup2.find_all(class_='entry-badge')
            images = soup2.find_all('img')
            links = list()
            for image in images:
                if 'data.whicdn.com/images/' in str(image):
                    yield image['src']


def get_args(text: str, args: list) -> dict:
    
    strings = text.split('--')
    ret = {arg: '' for arg in args}

    for string in strings:
        for arg in args:
            if string.startswith(arg):
                ret[arg] = string[len(arg):]

    return ret 


def rgb_to_hex(rgb):
    r, g, b = rgb
    balls = lambda x: max(0, min(x, 255))

    return '{0:02x}{1:02x}{2:02x}'.format(balls(r), balls(g), balls(b))


async def dominant_color(url: Union[discord.Asset, str]) -> int:
    
    if isinstance(url, discord.Asset):
        url = url.url
    
    resp = await http.read(url)
    img = Image.open(BytesIO(resp))
    
    colors = await asyncio.to_thread(lambda: colorgram.extract(img, 1))

    return discord.Color.from_rgb(*list(colors[0].rgb)).value


async def youtube_search(query: str) -> Optional[str]:

     html = await http.text('https://youtube.com/results', params={'search_query': query})
     matches = re.findall(r'\/watch\?v=\w+', html)

     if matches:
         return f'https://youtube.com{matches[0]}'

     return None


async def get_commits(author: str = 'treyt3n', repository: str = 'vilebot') -> Dict:
    return await http.get(
        f'https://api.github.com/repos/{author}/{repository}/commits',
        headers={
            'Authorization': 'Bearer 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'
        }
    )


class TWI:
    def __init__(self, items: List[Any], loop: bool = False) -> None:
        self.items = items
        self.loop = loop
        self.index = 0


    def first(self) -> Optional[Any]:
        self.index = 0
        return self.items[self.index]


    def previous(self) -> Optional[Any]:
        if self.index == 0:
            if self.loop:
                self.index = len(self.items)
            else:
                return None

        self.index -= 1
        return self.items[self.index]


    def next(self) -> Optional[Any]:
        if self.index == len(self.items) - 1:
            if self.loop:
                self.index = -1
            else:
                return None
                
        self.index += 1
        return self.items[self.index]


    def last(self) -> Optional[Any]:
        self.index = len(self.items) - 1
        return self.items[self.index]


    def current(self) -> Any:
        return self.items[self.index]


async def reaction_buttons(ctx: 'Context', message: discord.Message, functions: Dict[str, Callable], timeout: int = 30) -> None:

    for emojiname in functions:
        try:
            await message.add_reaction(emojiname)
        except:
            return

    while True:
        try:
            payload = await ctx.bot.wait_for(
                'raw_reaction_add', 
                timeout=timeout, 
                check=lambda payload: payload.message_id == message.id and str(payload.emoji) in functions and payload.member != ctx.bot.user and payload.member == ctx.author
            )
        except asyncio.TimeoutError:
            break

        else:
            try:
                exits = await functions[str(payload.emoji)]()
            except:
                return await ctx.reply(traceback.format_exc())

            try:
                await message.remove_reaction(payload.emoji, payload.member)
            except:
                pass

    for emojiname in functions:
        try:
            await message.clear_reactions()
        except:
            pass


async def remove_background(
    img_url: str,
    size: str = 'regular',
    type: str = 'auto',
    type_level: str = 'none',
    format: str ='auto',
    roi: str ='0 0 100% 100%',
    crop: str = None,
    scale: str = 'original',
    position: str = 'original',
    channels: str = 'rgba',
    shadow: bool = False,
    semitransparency: bool = True,
    bg: str = None,
    bg_type: str = None,
    new_file_name: str = 'transparent.png'
) -> BytesIO:

    if size not in ['auto', 'preview', 'small', 'regular', 'medium', 'hd', 'full', '4k']:
        raise ValueError("size argument wrong")

    if type not in ['auto', 'person', 'product', 'animal', 'car', 'car_interior', 'car_part', 'transportation', 'graphics', 'other',]:
        raise ValueError('type argument wrong')

    if type_level not in ['none', 'latest', '1', '2']:
        raise ValueError('type_level argument wrong')

    if format not in ['jpg', 'zip', 'png', 'auto']:
        raise ValueError('format argument wrong')

    if channels not in ['rgba', 'alpha']:
        raise ValueError('channels argument wrong')

    files = {}

    data = {
        'image_url': img_url,
        'size': size,
        'type': type,
        'type_level': type_level,
        'format': format,
        'roi': roi,
        'crop': 'true' if crop else 'false',
        'crop_margin': '',#crop,
        'scale': scale,
        'position': position,
        'channels': channels,
        'add_shadow': 'true' if shadow else 'false',
        'semitransparency': 'true' if semitransparency else 'false',
    }

    if bg_type == 'path':
        files['bg_image_file'] = open(bg, 'rb')
    elif bg_type == 'color':
        data['bg_color'] = bg
    elif bg_type == 'url':
        data['bg_image_url'] = bg

    response = await http.async_post_bytes(
        'https://api.remove.bg/v1.0/removebg', 
        data=data, 
        headers={'X-Api-Key': random.choice(['52tiT5sgHQxoVBoQhvXPPaEy', 'stFyKj4GTUY3CUPFYKWmt57V', 'nFXg4MpkATXYVHcJM5J9hq1L'])}
    )

    return BytesIO(response)


class _MissingSentinel:
    __slots__ = ()

    def __eq__(self, other) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self):
        return '...'


MISSING = _MissingSentinel()


async def get_user(user_id: int) -> dict:

    ret = dict()
    data = await http.get(f'https://japi.rest/discord/v1/user/{user_id}')

    if data.get('error'):
        ret['code'] = 10013
        ret['message'] = 'Unknown User'
        return ret

    data.pop('cached')
    data.pop('cache_expiry')
    data.pop('presence')

    ret.update(data['data'])
    ret['badges'] = ret.pop('public_flags_array')
    if isinstance(data['connections'], dict):
        ret['connections'] = list()
    else:
        ret['connections'] = data['connections']

    return ret
