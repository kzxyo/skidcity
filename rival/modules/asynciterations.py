from __future__ import annotations

import asyncio
import functools
from asyncio import Semaphore
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
    suppress,
)
from functools import wraps
from itertools import chain
from typing import AsyncIterator, Iterable, Union

import discord
from boltons.iterutils import chunked, chunked_iter
from discord.utils import maybe_coroutine
from loguru import logger as log

from .async_iter import _T, AsyncFilter, AsyncIter


class asuppress(suppress):
    def __init__(self, exceptions: type[BaseException] = (discord.HTTPException,)) -> None:
        super().__init__(*exceptions)


class aiter(AsyncIter):
    def __init__(self, iterable: Iterable[_T], circuit_breaker=None, delay: Union[float, int] = 0.05, steps: int = 1) -> None:
        super().__init__(iterable, delay, steps, circuit_breaker=circuit_breaker)


class aiterdict(AsyncIter):
    def __init__(self, iterable: Iterable[_T], circuit_breaker=None, delay: Union[float, int] = 0.05, steps: int = 1) -> None:
        super().__init__(iterable.items(), delay, steps, circuit_breaker=circuit_breaker)


class _aiterforever(aiter):
    def __init__(self, circuit_breaker, delay=0.05):
        super().__init__(True, circuit_breaker, delay=delay)


class AsyncContextDecorator(object):
    "A base class or mixin that enables async context managers to work as decorators."

    def _recreate_cm(self):
        """Return a recreated instance of self."""
        return self

    def __call__(self, func):
        @wraps(func)
        async def inner(*args, **kwds):
            async with self._recreate_cm():
                return await func(*args, **kwds)

        return inner


class nullcontext(AbstractContextManager, AbstractAsyncContextManager):
    """Context manager that does no additional processing.

    Used as a stand-in for a normal context manager, when a particular
    block of code is only sometimes used with a normal context manager:

    cm = optional_cm if condition else nullcontext()
    with cm:
        # Perform operation, using optional_cm if condition is True
    """

    def __init__(self, enter_result=None):
        self.enter_result = enter_result

    def __enter__(self):
        return self.enter_result

    def __exit__(self, *excinfo):
        pass

    async def __aenter__(self):
        return self.enter_result

    async def __aexit__(self, *excinfo):
        pass


@asynccontextmanager
async def taskguard(tasks):
    try:
        yield
    except:
        [t.cancel() for t in tasks]
        raise


async def _safe_aiter(async_iterator: AsyncIterator[_T]) -> AsyncIterator[_T]:
    async_iterator = async_iterator.__aiter__()
    while True:
        task = asyncio.create_task(async_iterator.__anext__())
        while not task.done():
            await asyncio.sleep(0.01)
        yield task.result()


def wait_safely(coro):
    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        task = asyncio.ensure_future(coro(*args, **kwargs))
        while not task.done():
            await asyncio.sleep(0.01)
        return task.result()

    return wrapper


async def aitergather(future_like, max_concurrent, chunksize=100, error_action="raise"):
    async def _await_bounded(coro, sem):
        async with sem:
            return await coro

    task_sem = Semaphore(max_concurrent) if max_concurrent else nullcontext()
    for chunk in chunked_iter(future_like, chunksize):
        import distributed

        tasks = []
        async with taskguard(tasks):
            for coro_or_future in chunk:
                if max_concurrent:
                    tasks.append(asyncio.ensure_future(_await_bounded(coro_or_future, task_sem)))
                else:
                    if isinstance(coro_or_future, (asyncio.Future, distributed.Future, asyncio.Task)):
                        tasks.append(coro_or_future)
                    else:
                        tasks.append(asyncio.ensure_future(_await_bounded(coro_or_future)))
            for f in asyncio.as_completed(tasks):
                try:
                    yield f
                except Exception as e:
                    if isinstance(e, (asyncio.CancelledError)):
                        raise
                    if error_action == "log":
                        log.exception(f"Task failure on {e} ")
                    else:
                        raise


async def aiterforever(circuit_breaker=False, loop_delay=30, task_delay=0.01, iterables=None):
    while True:
        await asyncio.sleep(1)
        yield 1

    # while True:
    #     if not iterables:
    #         iterables = range(100)
    #     async for x in aiter(iterables, circuit_breaker, task_delay):
    #         yield x
    #     await asyncio.sleep(loop_delay)
