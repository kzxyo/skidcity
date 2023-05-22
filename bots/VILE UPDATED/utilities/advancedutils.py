import ast, asyncio, inspect, linecache, import_expression
from typing import Optional, Union, Awaitable, Any, AsyncGenerator, Callable, TypeVar, Dict, List, Iterable, Iterator, AsyncIterator, Generic, Tuple, Type

from jishaku.repl.walkers import KeywordTransformer


class Scope:
    def __init__(self,globals_: Optional[Dict[str, Any]] = None, locals_: Optional[Dict[str, Any]] = None):
        self.globals: Dict[str, Any] = globals_ or dict()
        self.locals: Dict[str, Any] = locals_ or dict()

    def clear_intersection(self, other_dict: Dict[str, Any]):

        for key, value in other_dict.items():
            if key in self.globals and self.globals[key] is value:
                del self.globals[key]
            if key in self.locals and self.locals[key] is value:
                del self.locals[key]

        return self

    def update(self, other: 'Scope'):

        self.globals.update(other.globals)
        self.locals.update(other.locals)
        return self

    def update_globals(self, other: Dict[str, Any]):

        self.globals.update(other)
        return self

    def update_locals(self, other: Dict[str, Any]):

        self.locals.update(other)
        return self


def get_parent_scope_from_var(name: str, global_ok: bool = False, skip_frames: int = 0) -> Optional[Scope]:

    stack = inspect.stack()
    try:
        for frame_info in stack[skip_frames + 1:]:
            frame = None

            try:
                frame = frame_info.frame

                if name in frame.f_locals or (global_ok and name in frame.f_globals):
                    return Scope(globals_=frame.f_globals, locals_=frame.f_locals)
            finally:
                del frame
    finally:
        del stack

    return None


def get_parent_var(name: str, global_ok: bool = False, default: Any = None, skip_frames: int = 0) -> Any:

    scope = get_parent_scope_from_var(name, global_ok=global_ok, skip_frames=skip_frames + 1)

    if scope is None:
        return default

    if name in scope.locals:
        return scope.locals.get(name, default)

    return scope.globals.get(name, default)


CORO_CODE = f"""
async def _repl_coroutine({{0}}):
    import asyncio
    from importlib import import_module as {import_expression.constants.IMPORTER}
    import aiohttp
    import discord
    from discord.ext import commands
    try:
        import jishaku
    except ImportError:
        jishaku = None 
    try:
        pass
    finally:
        _async_executor.scope.globals.update(locals())
"""


def wrap_code(code: str, args: str = '', auto_return: bool = True) -> ast.Module:

    user_code: ast.Module = import_expression.parse(code, mode='exec')
    mod: ast.Module = import_expression.parse(CORO_CODE.format(args), mode='exec')

    for node in ast.walk(mod):
        node.lineno = -100_000
        node.end_lineno = -100_000

    definition = mod.body[-1]
    assert isinstance(definition, ast.AsyncFunctionDef)

    try_block = definition.body[-1]
    assert isinstance(try_block, ast.Try)

    try_block.body.extend(user_code.body)

    ast.fix_missing_locations(mod)

    KeywordTransformer().generic_visit(try_block)

    if auto_return is False:
        return mod

    last_expr = try_block.body[-1]

    if not isinstance(last_expr, ast.Expr):
        return mod

    if not isinstance(last_expr.value, ast.Yield):
        yield_stmt = ast.Yield(last_expr.value)
        ast.copy_location(yield_stmt, last_expr)
        yield_expr = ast.Expr(yield_stmt)
        ast.copy_location(yield_expr, last_expr)

        try_block.body[-1] = yield_expr

    return mod


class AsyncCodeExecutor:
    def __init__(
        self,
        code: str,
        scope: Optional[Scope] = None,
        arg_dict: Optional[Dict[str, Any]] = None,
        convertables: Optional[Dict[str, str]] = None,
        loop: Optional[asyncio.BaseEventLoop] = None,
        auto_return: bool = True,
    ):
        self.args = [self]
        self.arg_names = ['_async_executor']

        if arg_dict:
            for key, value in arg_dict.items():
                self.arg_names.append(key)
                self.args.append(value)

        self.source = code

        try:
            self.code = wrap_code(code, args=', '.join(self.arg_names), auto_return=auto_return)
        except (SyntaxError, IndentationError) as first_error:
            if not convertables:
                raise

            try:
                for key, value in convertables.items():
                    code = code.replace(key, value)
                self.code = wrap_code(code, args=', '.join(self.arg_names))
            except (SyntaxError, IndentationError) as second_error:
                raise second_error from first_error

        self.scope = scope or Scope()
        self.loop = loop or asyncio.get_event_loop()
        self._function = None


    @property
    def function(self) -> Callable[..., Union[Awaitable[Any], AsyncGenerator[Any, Any]]]:

        if self._function is not None:
            return self._function

        exec(compile(self.code, '<repl>', 'exec'), self.scope.globals, self.scope.locals)
        self._function = self.scope.locals.get('_repl_coroutine') or self.scope.globals['_repl_coroutine']

        return self._function


    def create_linecache(self) -> List[str]:

        lines = [line + '\n' for line in self.source.splitlines()]

        linecache.cache['<repl>'] = (
            len(self.source),
            None,
            lines,
            '<repl>'
        )

        return lines


    def __aiter__(self) -> AsyncGenerator[Any, Any]:
        return self.traverse(self.function)


    async def traverse(
        self,
        func: Callable[..., Union[Awaitable[Any], AsyncGenerator[Any, Any]]]
    ) -> AsyncGenerator[Any, Any]:

        try:
            if inspect.isasyncgenfunction(func) is True:
                func_g: Callable[..., AsyncGenerator[Any, Any]] = func
                async for send, result in AsyncSender(func_g(*self.args)):
                    send((yield result))
            else:
                func_a: Callable[..., Awaitable[Any]] = func
                yield await func_a(*self.args)
        except:
            self.create_linecache()

            raise


import asyncio
import functools
import sys
import typing

T = TypeVar('T')
from typing_extensions import ParamSpec
if sys.version_info < (3, 10):
    P = ParamSpec('P')
else:
    P = ParamSpec('P')


def coroutine(sync_function: Callable[P, T]) -> Callable[P, Awaitable[T]]:

    @functools.wraps(sync_function)
    async def sync_wrapper(*args: P.args, **kwargs: P.kwargs):

        loop = asyncio.get_event_loop()
        internal_function = functools.partial(sync_function, *args, **kwargs)
        return await loop.run_in_executor(None, internal_function)

    return sync_wrapper


U = TypeVar('U')


class AsyncSender(Generic[T, U]):
    def __init__(self, iterator: AsyncGenerator[T, Optional[U]]):
        self.iterator = iterator
        self.send_value: U = None


    def __aiter__(self) -> AsyncGenerator[Tuple[Callable[[Optional[U]], None], T], None]:
        return self._internal(self.iterator.__aiter__())


    async def _internal(self,base: AsyncGenerator[T, Optional[U]]) -> AsyncGenerator[Tuple[Callable[[Optional[U]], None], T], None]:
        try:
            while True:
                value = await base.asend(self.send_value)
                self.send_value = None
                yield self.set_send_value, value
        except StopAsyncIteration:
            pass


    def set_send_value(self, value: Optional[U]):
        self.send_value = value


import collections, datetime, decimal, numbers, os, os.path, re, time


time_units = (dict(divider=1e-9, singular='nanosecond', plural='nanoseconds', abbreviations=['ns']),
              dict(divider=1e-6, singular='microsecond', plural='microseconds', abbreviations=['us']),
              dict(divider=1e-3, singular='millisecond', plural='milliseconds', abbreviations=['ms']),
              dict(divider=1, singular='second', plural='seconds', abbreviations=['s', 'sec', 'secs']),
              dict(divider=60, singular='minute', plural='minutes', abbreviations=['m', 'min', 'mins']),
              dict(divider=60 * 60, singular='hour', plural='hours', abbreviations=['h']),
              dict(divider=60 * 60 * 24, singular='day', plural='days', abbreviations=['d']),
              dict(divider=60 * 60 * 24 * 7, singular='week', plural='weeks', abbreviations=['w']),
              dict(divider=60 * 60 * 24 * 7 * 52, singular='year', plural='years', abbreviations=['y']))


def is_string(value):
    return isinstance(value, str)


def tokenize(text):
    tokenized_input = list()
    for token in re.split(r'(\d+(?:\.\d+)?)', text):
        token = token.strip()
        if re.match(r'\d+\.\d+', token):
            tokenized_input.append(float(token))
        elif token.isdigit():
            tokenized_input.append(int(token))
        elif token:
            tokenized_input.append(token)
    return tokenized_input


def parse_timespan(timespan):
    tokens = tokenize(timespan)
    if tokens and isinstance(tokens[0], numbers.Number):
        if len(tokens) == 1:
            return float(tokens[0])
        if len(tokens) == 2 and is_string(tokens[1]):
            normalized_unit = tokens[1].lower()
            for unit in time_units:
                if (normalized_unit == unit['singular'] or
                        normalized_unit == unit['plural'] or
                        normalized_unit in unit['abbreviations']):
                    return float(tokens[0]) * unit['divider']

    raise TypeError('Timespan is invalid')



import asyncio, subprocess, sys, traceback, typing, discord
from types import TracebackType

from discord.ext import commands

from jishaku.flags import Flags


async def send_traceback(
    destination: Union[discord.abc.Messageable, discord.Message],
    verbosity: int,
    etype: Type[BaseException],
    value: BaseException,
    trace: TracebackType
):

    traceback_content = "".join(traceback.format_exception(etype, value, trace, verbosity)).replace("``", "`\u200b`")

    paginator = commands.Paginator(prefix='```py')
    for line in traceback_content.split('\n'):
        paginator.add_line(line)

    message = None

    for page in paginator.pages:
        if isinstance(destination, discord.Message):
            message = await destination.reply(page)
        else:
            message = await destination.send(page)

    return message


T = TypeVar('T')

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
    P = ParamSpec('P')
else:
    P = ParamSpec('P')  # pylint: disable=no-member


async def do_after_sleep(delay: float, coro: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
    await asyncio.sleep(delay)
    return await coro(*args, **kwargs)


async def attempt_add_reaction(
    msg: discord.Message,
    reaction: Union[str, discord.Emoji]
) -> Optional[discord.Reaction]:
    try:
        return await msg.add_reaction(reaction)
    except discord.HTTPException:
        pass


class ReplResponseReactor:

    __slots__ = ('message', 'loop', 'handle', 'raised')

    def __init__(self, message: discord.Message, loop: Optional[asyncio.BaseEventLoop] = None):
        self.message = message
        self.loop = loop or asyncio.get_event_loop()
        self.handle = None
        self.raised = False

    async def __aenter__(self):
        self.handle = self.loop.create_task(
            do_after_sleep(
                2, attempt_add_reaction, 
                self.message, '<:v_next_page:1067034038386303016>'
            )
        )
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
            await attempt_add_reaction(self.message, '<:v_done:1067033981452828692>')
            return False

        self.raised = True

        if isinstance(exc_val, (SyntaxError, asyncio.TimeoutError, subprocess.TimeoutExpired)):
            destination = Flags.traceback_destination(self.message) or self.message.channel

            if destination != self.message.channel:
                await attempt_add_reaction(
                    self.message,
                    '<:v_warn:1067034029569888266>' if isinstance(exc_val, SyntaxError) else '<:v_warn:1067034029569888266>'
                )

            await send_traceback(
                self.message if destination == self.message.channel else destination,
                0, exc_type, exc_val, exc_tb
            )
        else:
            destination = Flags.traceback_destination(self.message) or self.message.author

            if destination != self.message.channel:
                await attempt_add_reaction(self.message, '<:v_warn:1067034029569888266>')

            await send_traceback(
                self.message if destination == self.message.channel else destination,
                8, exc_type, exc_val, exc_tb
            )

        return True


import asyncio
import os
import pathlib
import re
import subprocess
import sys
import time
import typing

T = typing.TypeVar('T')

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
    P = ParamSpec('P')
else:
    P = typing.ParamSpec('P')  # pylint: disable=no-member


SHELL = os.getenv('SHELL') or '/bin/bash'
WINDOWS = sys.platform == 'win32'


def background_reader(stream: typing.IO[bytes], loop: asyncio.AbstractEventLoop, callback: typing.Callable[[bytes], typing.Any]):
    for line in iter(stream.readline, b''):
        loop.call_soon_threadsafe(loop.create_task, callback(line))


class ShellReader:
    def __init__(self, code: str, timeout: int = 120, loop: typing.Optional[asyncio.AbstractEventLoop] = None, escape_ansi: bool = True):
        if WINDOWS:
            if pathlib.Path(r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe').exists():
                sequence = ['powershell', code]
                self.ps1 = 'PS >'
                self.highlight = 'powershell'

            else:
                sequence = ['cmd', '/c', code]
                self.ps1 = 'cmd >'
                self.highlight = 'cmd'

            self.escape_ansi = True

        else:
            sequence = [SHELL, '-c', code]
            self.ps1 = '$'
            self.highlight = 'ansi'
            self.escape_ansi = escape_ansi

        self.process = subprocess.Popen(sequence, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # pylint: disable=consider-using-with
        self.close_code = None

        self.loop = loop or asyncio.get_event_loop()
        self.timeout = timeout

        self.stdout_task = self.make_reader_task(self.process.stdout, self.stdout_handler) if self.process.stdout else None
        self.stderr_task = self.make_reader_task(self.process.stderr, self.stderr_handler) if self.process.stderr else None

        self.queue: asyncio.Queue[str] = asyncio.Queue(maxsize=250)


    @property
    def closed(self) -> bool:
        return (not self.stdout_task or self.stdout_task.done()) and (not self.stderr_task or self.stderr_task.done())


    async def executor_wrapper(self, func: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        return await self.loop.run_in_executor(None, func, *args, **kwargs)


    def make_reader_task(self, stream: typing.IO[bytes], callback: typing.Callable[[bytes], typing.Any]):
        return self.loop.create_task(self.executor_wrapper(background_reader, stream, self.loop, callback))


    ANSI_ESCAPE_CODE = re.compile(r'\x1b\[\??(\d*)(?:([ABCDEFGJKSThilmnsu])|;(\d+)([fH]))')


    def clean_bytes(self, line: bytes) -> str:
        
        text = line.decode('utf-8').replace('\r', '').strip('\n')

        def sub(group: typing.Match[str]):
            return group.group(0) if group.group(2) == 'm' and not self.escape_ansi else ''

        return self.ANSI_ESCAPE_CODE.sub(sub, text).replace("``", "`\u200b`").strip('\n')


    async def stdout_handler(self, line: bytes) -> None:
        await self.queue.put(self.clean_bytes(line))


    async def stderr_handler(self, line: bytes) -> None:
        await self.queue.put(self.clean_bytes(b'[stderr] ' + line))


    def __enter__(self):
        return self


    def __exit__(self, *_):
        self.process.kill()
        self.process.terminate()
        self.close_code = self.process.wait(timeout=0.5)


    def __aiter__(self):
        return self


    async def __anext__(self):
        
        last_output = time.perf_counter()

        while not self.closed or not self.queue.empty():
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1)

            except asyncio.TimeoutError as exception:
                if time.perf_counter() - last_output >= self.timeout:
                    raise exception

            else:
                last_output = time.perf_counter()
                return item

        raise StopAsyncIteration()