from __future__ import annotations

import asyncio
from asyncio import as_completed, Semaphore
from asyncio.futures import isfuture
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from itertools import chain
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import asyncstdlib as a
from discord.utils import maybe_coroutine

_T = TypeVar("_T")
_S = TypeVar("_S")


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


class AsyncFilter(AsyncIterator[_T], Awaitable[List[_T]]):  # pylint: disable=duplicate-bases
    """Class returned by `async_filter`. See that function for details.

    We don't recommend instantiating this class directly.
    """

    def __init__(self, func: Callable[[_T], Union[bool, Awaitable[bool]]], iterable: Union[AsyncIterable[_T], Iterable[_T]]) -> None:
        self.__func: Callable[[_T], Union[bool, Awaitable[bool]]] = func
        self.__iterable: Union[AsyncIterable[_T], Iterable[_T]] = iterable

        # We assign the generator strategy based on the arguments' types
        if isinstance(iterable, AsyncIterable):
            if asyncio.iscoroutinefunction(func):
                self.__generator_instance = self.__async_generator_async_pred()
            else:
                self.__generator_instance = self.__async_generator_sync_pred()
        elif asyncio.iscoroutinefunction(func):
            self.__generator_instance = self.__sync_generator_async_pred()
        else:
            raise TypeError("Must be either an async predicate, an async iterable, or both.")

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

    def __aiter__(self):
        return self

    def __await__(self):
        # Simply return the generator filled into a list
        return self.__flatten().__await__()

    def __anext__(self) -> Awaitable[_T]:
        # This will use the generator strategy set in __init__
        return self.__generator_instance.__anext__()


def async_filter(func: Callable[[_T], Union[bool, Awaitable[bool]]], iterable: Union[AsyncIterable[_T], Iterable[_T]]) -> AsyncFilter[_T]:
    """Filter an (optionally async) iterable with an (optionally async) predicate.

    At least one of the arguments must be async.

    Parameters
    ----------
    func : Callable[[T], Union[bool, Awaitable[bool]]]
        A function or coroutine function which takes one item of ``iterable``
        as an argument, and returns ``True`` or ``False``.
    iterable : Union[AsyncIterable[_T], Iterable[_T]]
        An iterable or async iterable which is to be filtered.

    Raises
    ------
    TypeError
        If neither of the arguments are async.

    Returns
    -------
    AsyncFilter[T]
        An object which can either be awaited to yield a list of the filtered
        items, or can also act as an async iterator to yield items one by one.

    """
    return AsyncFilter(func, iterable)


async def async_enumerate(async_iterable: AsyncIterable[_T], start: int = 0) -> AsyncIterator[Tuple[int, _T]]:
    """Async iterable version of `enumerate`.

    Parameters
    ----------
    async_iterable : AsyncIterable[T]
        The iterable to enumerate.
    start : int
        The index to start from. Defaults to 0.

    Returns
    -------
    AsyncIterator[Tuple[int, T]]
        An async iterator of tuples in the form of ``(index, item)``.

    """
    async for item in async_iterable:
        yield start, item
        start += 1


async def _sem_wrapper(sem, task):
    async with sem:
        return await task


def bounded_gather_iter(*coros_or_futures, limit: int = 4, semaphore: Optional[Semaphore] = None) -> Iterator[Awaitable[Any]]:
    """
    An iterator that returns tasks as they are ready, but limits the
    number of tasks running at a time.

    Parameters
    ----------
    *coros_or_futures
        The awaitables to run in a bounded concurrent fashion.
    limit : Optional[`int`]
        The maximum number of concurrent tasks. Used when no ``semaphore``
        is passed.
    semaphore : Optional[:class:`asyncio.Semaphore`]
        The semaphore to use for bounding tasks. If `None`, create one
        using ``loop`` and ``limit``.

    Raises
    ------
    TypeError
        When invalid parameters are passed
    """
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


class AsyncIter(AsyncIterator[_T], Awaitable[List[_T]]):  # pylint: disable=duplicate-bases
    def __init__(self, iterable: Iterable[_T], delay: Union[float, int] = 0, steps: int = 0, circuit_breaker=None) -> None:
        # sourcery skip: assign-if-exp
        self._delay = delay
        if iterable == True:
            self._iterator = True
        else:
            self._iterator = a.any_iter(iterable)
        self._i = -1
        self._circuit_breaker = circuit_breaker
        self._steps = steps
        self._map = None

    def __aiter__(self):
        return self

    async def __anext__(self) -> _T:  # sourcery skip: assign-if-exp
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
        """Returns a list of the iterable.

        Examples
        --------
        >>> iterator = AsyncIter(range(5))
        >>> await iterator
        [0, 1, 2, 3, 4]

        """
        return self.flatten().__await__()

    async def next(self, default: Any = ...) -> _T:
        """Returns a next entry of the iterable.
        Examples
        --------
        >>> iterator = AsyncIter(range(5))
        >>> await iterator.next()
        0
        >>> await iterator.next()
        1

        """
        try:
            value = await self.__anext__()
        except StopAsyncIteration:
            if default is ...:
                raise
            value = default
        return value

    async def flatten(self) -> List[_T]:
        """Returns a list of the iterable.
        >>> iterator = AsyncIter(range(5))
        >>> await iterator.flatten()
        [0, 1, 2, 3, 4]

        """
        return [item async for item in self]

    def filter(self, function: Callable[[_T], Union[bool, Awaitable[bool]]]) -> AsyncFilter[_T]:
        """Filter the iterable with an (optionally async) predicate.

        Parameters
        ----------
        function: Callable[[T], Union[bool, Awaitable[bool]]]
            A function or coroutine function which takes one item of ``iterable``
            as an argument, and returns ``True`` or ``False``.

        Examples
        --------
        >>> def predicate(value):
        ...     return value <= 5
        >>> iterator = AsyncIter([1, 10, 5, 100])
        >>> async for i in iterator.filter(predicate):
        ...     print(i)
        1
        5
        """
        return async_filter(function, self)

    def enumerate(self, start: int = 0) -> AsyncIterator[Tuple[int, _T]]:
        """Async iterable version of `enumerate`."""
        return async_enumerate(self, start)

    async def without_duplicates(self) -> AsyncIterator[_T]:
        """
        Iterates while omitting duplicated entries.
        """
        _temp = set()
        async for item in self:
            if item not in _temp:
                yield item
                _temp.add(item)
        del _temp

    async def find(self, predicate: Callable[[_T], Union[bool, Awaitable[bool]]], default: Optional[Any] = None) -> AsyncIterator[_T]:
        """Calls ``predicate`` over items in iterable and return first value to match.

        Parameters
        ----------
        predicate: Union[Callable, Coroutine]
            A function that returns a boolean-like result. The predicate provided can be a coroutine.
        default: Optional[Any]
            The value to return if there are no matches.

        Raises
        ------
        TypeError
            When ``predicate`` is not a callable.

        Examples
        --------
        >>> from redbot.core.utils import AsyncIter
        >>> await AsyncIter(range(3)).find(lambda x: x == 1)
        1
        """
        while True:
            try:
                elem = await self.__anext__()
            except StopAsyncIteration:
                return default
            ret = await maybe_coroutine(predicate, elem)
            if ret:
                return elem

    def map(self, func: Callable[[_T], Union[_S, Awaitable[_S]]]):
        """Set the mapping callable for this instance of `AsyncIter`."""
        if not callable(func):
            raise TypeError("Mapping must be a callable.")
        self._map = a.sync(func)
        return self


# Benchmarked to be the fastest method.
def deduplicate_iterables(*iterables):
    """
    Returns a list of all unique items in ``iterables``, in the order they
    were first encountered.
    """
    # dict insertion order is guaranteed to be preserved in 3.6+
    return list(dict.fromkeys(chain.from_iterable(iterables)))
