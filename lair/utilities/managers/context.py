from __future__ import annotations

from asyncio import get_running_loop
import asyncio
from ctypes import Union
from io import BytesIO
from subprocess import TimeoutExpired
from types import TracebackType
from shazamio import Shazam
from typing import Any, Awaitable, Callable, Coroutine, Dict, Iterable, Iterator, Optional, Generator, Type, TypeVar, ParamSpec
import datetime
from aiohttp import ClientError
from discord import Embed, Message
from discord.ext.commands import Context
from discord import (
    Message,
    MessageReference,
    Reaction,
    Emoji,
    HTTPException
)
from discord.context_managers import Typing
from PIL import Image
import itertools
from jishaku.flags import Flags
from discord.utils import cached_property
from utilities.general import Confirm

from .. import config
from ..paginator import Paginator

BE = TypeVar('BE', bound=BaseException)
T = TypeVar('T')
P = ParamSpec('P')

def _typing_done_callback(fut: asyncio.Future) -> None:
    try:
        fut.exception()
    except (asyncio.CancelledError, Exception):
        pass

async def do_after_sleep(delay: float, coro: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
    await asyncio.sleep(delay)
    return await coro(*args, **kwargs)


async def attempt_add_reaction(
    msg: Message,
    reaction: Union[str, Emoji]
) -> Optional[Reaction]:
    try:
        return await msg.add_reaction(reaction)
    except HTTPException:
        pass

class Writing:
    __slots__ = ('message', 'loop', 'handle', 'raised', 'task')

    def __init__(self, message: Message, loop: Optional[asyncio.BaseEventLoop] = None):
        self.task = None
        self.message = message
        self.loop = loop or asyncio.get_event_loop()
        self.handle = None
        self.raised = False

    async def do_typing(self) -> None:
        while True:
            await asyncio.sleep(5)
            await self.message.channel._state.http.send_typing(self.message.channel.id)

    async def __aenter__(self):
        await self.message.channel._state.http.send_typing(self.message.channel.id)
        self.task: asyncio.Task[None] = self.loop.create_task(self.do_typing())
        self.task.add_done_callback(_typing_done_callback)
        self.handle = self.loop.create_task(do_after_sleep(2, attempt_add_reaction, self.message,
                                                           "🔃"))
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType
    ) -> bool:
        if self.handle:
            self.handle.cancel()

        if not exc_val:
            await attempt_add_reaction(self.message, config.Emoji.done)
            self.task.cancel()
            return False

        self.raised = True

        if isinstance(exc_val, (SyntaxError, asyncio.TimeoutError, TimeoutExpired)):
            destination = Flags.traceback_destination(self.message) or self.message.channel

            if destination != self.message.channel:
                await attempt_add_reaction(
                    self.message,
                    config.Emoji.warning if isinstance(exc_val, SyntaxError) else config.Emoji.loading
                )
                self.task.cancel()

            await self.message.channel.send(f"{self.message if destination == self.message.channel else destination}")
            self.task.cancel()
        else:
            destination = Flags.traceback_destination(self.message) or self.message.author

            if destination != self.message.channel:
                await attempt_add_reaction(self.message, config.Emoji.warning)
                self.task.cancel()

            await self.message.channel.send(f"{self.message if destination == self.message.channel else destination}")
            self.task.cancel()

        self.task.cancel()
        return True



class Context(Context):
    flags: Dict[str, Any] = {}


    async def sample(self, buffer: bytes) -> int:
        loop = get_running_loop()
        image = await loop.run_in_executor(None, lambda: Image.open(BytesIO(buffer)).convert("RGBA"))
        pixel = await loop.run_in_executor(None, lambda: image.resize((1, 1), resample=0).getpixel((0, 0)))
        hex_value = "%02x%02x%02x" % pixel[:3]
        result = int(hex_value, 16)
        return result


    async def dominant(self, url: str) -> int:
        cache_key = f"dominant:{url}"
        cached_result = await self.bot.cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            async with self.bot.session.get(url) as response:
                buffer = await response.read()
        except ClientError:
            return 0
        else:
            result = await self.sample(buffer)

            await self.bot.cache.set(cache_key, result)

            return result


    @staticmethod
    async def confirm(self, message: Message):
        view = Confirm(invoker=self.author)
        await message.edit(view=view)
        await view.wait()
        return view.value
        
    @cached_property
    def replied_reference(self) -> Union[Message, MessageReference]:
        reference = self.message.reference
        message = self.message

        if reference and isinstance(reference.resolved, Message):
            return reference.resolved.to_reference()

        return message

    async def song(self, source: Union[str, bytes]) -> Optional[Dict]:
        if isinstance(source, str):
            source = await self.bot.session.get(source)
            source = await source.read()
        song_data = await Shazam().recognize_song(source)
        return song_data.get('track')

    @cached_property
    def replied_message(self) -> Message:
        reference = self.message.reference
        message = self.message

        if reference and isinstance(reference.resolved, Message):
            return reference.resolved

        return message
    
    async def main(self, content: str, emoji: str = None, **kwargs) -> Message:
        themec = await self.bot.db.fetchdict('SELECT embeds, color FROM theme WHERE guild_id = $1', self.guild.id)
        themec = themec[0] if themec else {}
        color = themec.get('color') if themec.get('color') else config.Color.main
        desc = f"> {self.author.mention}, {content}"

        if not themec:
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)

        if themec.get('embeds'):
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)
        else:
            return await self.reply(content=desc, **kwargs)

    async def done(self, content: str, emoji: str = config.Emoji.done, **kwargs) -> Message:
        themec = await self.bot.db.fetchdict('SELECT embeds, color FROM theme WHERE guild_id = $1', self.guild.id)
        themec = themec[0] if themec else {}
        color = themec.get('color') if themec.get('color') else config.Color.done
        desc = f"> {self.author.mention}, {content}"
        
        if not themec:
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)

        if themec.get('embeds'):
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)
        else:
            return await self.reply(content=desc, **kwargs)

    async def error(self, content: str, emoji: str = config.Emoji.error, **kwargs) -> Message:
        themec = await self.bot.db.fetchdict('SELECT embeds, color FROM theme WHERE guild_id = $1', self.guild.id)
        themec = themec[0] if themec else {}
        color = themec.get('color') if themec.get('color') else config.Color.error
        desc = f"> {self.author.mention}, {content}"

        if not themec:
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)

        if themec.get('embeds'):
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)
        else:
            return await self.reply(content=desc, **kwargs)

    async def warn(self, content: str, emoji: str = config.Emoji.warning, **kwargs) -> Message:
        themec = await self.bot.db.fetchdict('SELECT embeds, color FROM theme WHERE guild_id = $1', self.guild.id)
        themec = themec[0] if themec else {}
        color = themec.get('color') if themec.get('color') else config.Color.warning
        desc = f"> {self.author.mention}, {content}"

        if not themec:
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)

        if themec.get('embeds'):
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)
        else:
            return await self.reply(content=desc, **kwargs)

    async def music(self, content: str, emoji: str = config.Emoji.music, **kwargs) -> Message:
        themec = await self.bot.db.fetchdict('SELECT embeds, color FROM theme WHERE guild_id = $1', self.guild.id)
        themec = themec[0] if themec else {}
        color = themec.get('color') if themec.get('color') else config.Color.music
        desc = f"> {self.author.mention}, {content}"

        if not themec:
            return await self.reply(embed=Embed(color=color, description=desc), **kwargs)

        if themec.get('embeds'):
            return await self.reply(
                embed=Embed(
                    color=color, description=desc
                ),
                **kwargs
            )
        else:
            return await self.reply(content=desc, **kwargs)

    def as_chunks(self, iterator: Iterable[Any], max_size: int) -> Iterator[Any]:
        iterator = iter(iterator)
        chunk = list(itertools.islice(iterator, max_size))
        
        while chunk:
            yield chunk
            chunk = list(itertools.islice(iterator, max_size))

    def should_paginate(self, _list: list) -> bool:
        return len(_list) > 1

    async def paginate(self, to_paginate: Union[Embed, list], per: int = 10) -> Optional[Message]:
        if isinstance(to_paginate, Embed):
            embed = to_paginate
            if not embed.description:
                return

            if not isinstance(embed.description, list):
                return

            if len(embed.description) == 0:
                return await self.error("No entries located.")

            embeds = list()
            num = 0
            rows = [
                f"`{index}` {row}"
                for index, row in enumerate(embed.description, start=1)
            ]

            for page in self.as_chunks(rows, 10):
                num += 1
                embeds.append(
                    Embed(
                        color=embed.color or config.Color.main,
                        title=embed.title,
                        description="\n".join(page),
                        timestamp=datetime.datetime.now(),
                    )
                    .set_footer(
                        text=f"Page {num}/{len(list(self.as_chunks(rows, 10)))}  ({len(rows)} entries)"
                    )
                    .set_author(name=self.author, icon_url=self.author.display_avatar)
                )

            if self.should_paginate(embeds) is False:
                return await self.reply(embed=embeds[0])

            interface = Paginator(
                self.bot, embeds, self, invoker=self.author.id, timeout=30
            )
            interface.default_pagination()
            return await interface.start()

        elif isinstance(to_paginate, list):
            embeds = to_paginate

            if len(embeds) == 0:
                return await self.error("No entries located.")

            if self.should_paginate(embeds) is False:
                return await self.reply(embed=embeds[0])

            interface = Paginator(
                self.bot, embeds, self, invoker=self.author.id, timeout=30
            )
            interface.default_pagination()
            return await interface.start()
