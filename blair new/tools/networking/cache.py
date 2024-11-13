from __future__ import annotations

import asyncio
import enum
import time
from functools import wraps
from typing import Any, Callable, Coroutine, Generic, MutableMapping, Protocol, TypeVar

from lru import LRU

R = TypeVar("R")


# Can't use ParamSpec due to https://github.com/python/typing/discussions/946
class CacheProtocol(Protocol[R]):
    cache: MutableMapping[str, asyncio.Task[R]]

    def __call__(self, *args: Any, **kwds: Any) -> asyncio.Task[R]: ...

    def get_key(self, *args: Any, **kwargs: Any) -> str: ...

    def invalidate(self, *args: Any, **kwargs: Any) -> bool: ...

    def invalidate_containing(self, key: int | str) -> None: ...

    def get_stats(self) -> tuple[int, int]: ...


class ExpiringCache(dict, Generic[R]):
    def __init__(self, seconds: float) -> None:
        self.__ttl: float = seconds
        super().__init__()

    def __verify_cache_integrity(self) -> None:
        # Have to do this in two steps...
        current_time = time.monotonic()
        to_remove = [
            k for (k, (_, t)) in self.items() if current_time > (t + self.__ttl)
        ]
        for k in to_remove:
            del self[k]

    def __contains__(self, key: str) -> bool:
        self.__verify_cache_integrity()
        return super().__contains__(key)

    def __getitem__(self, key: str) -> tuple[R, float]:
        self.__verify_cache_integrity()
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: R) -> None:
        super().__setitem__(key, (value, time.monotonic()))


class Strategy(enum.Enum):
    lru = 1
    raw = 2
    timed = 3


def cache(
    maxsize: int = 128,
    strategy: Strategy = Strategy.lru,
    ignore_kwargs: bool = False,
) -> Callable[[Callable[..., Coroutine[Any, Any, R]]], CacheProtocol[R]]:
    def decorator(func: Callable[..., Coroutine[Any, Any, R]]) -> CacheProtocol[R]:
        if strategy is Strategy.lru:
            _internal_cache = LRU(maxsize)
            _stats = _internal_cache.get_stats  # type: ignore
        elif strategy is Strategy.raw:
            _internal_cache = {}

            def _stats():
                return 0, 0

        elif strategy is Strategy.timed:
            _internal_cache = ExpiringCache(maxsize)

            def _stats():
                return 0, 0

        def _make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
            # this is a bit of a cluster fuck
            # we do care what 'self' parameter is when we __repr__ it
            def _true_repr(o: object) -> str:
                if o.__class__.__repr__ is object.__repr__:
                    return f"{o.__class__.__name__}"

                return str(o.id) if hasattr(o, "id") else repr(o)  # type: ignore

            key = [f"{func.__module__}.{func.__name__}"]
            key.extend(_true_repr(o) for o in args)
            if not ignore_kwargs:
                for k, v in kwargs.items():
                    if k in ["connection", "pool"]:
                        continue

                    key.append(_true_repr(k))
                    key.append(_true_repr(v))

            return ":".join(key)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _make_key(args, kwargs)
            try:
                task = _internal_cache[key]
            except KeyError:
                _internal_cache[key] = task = asyncio.create_task(func(*args, **kwargs))
                return task
            else:
                return task

        def _invalidate(*args: Any, **kwargs: Any) -> bool:
            try:
                del _internal_cache[_make_key(args, kwargs)]
            except KeyError:
                return False
            else:
                return True

        def _invalidate_containing(key: str | int) -> None:
            if isinstance(key, int):
                key = str(key)

            to_remove = [k for k in _internal_cache.keys() if key in k]

            for k in to_remove:
                try:
                    del _internal_cache[k]
                except KeyError:
                    continue

        wrapper.cache = _internal_cache  # type: ignore
        wrapper.get_key = lambda *args, **kwargs: _make_key(args, kwargs)  # type: ignore
        wrapper.invalidate = _invalidate  # type: ignore
        wrapper.get_stats = _stats  # type: ignore
        wrapper.invalidate_containing = _invalidate_containing  # type: ignore
        return wrapper  # type: ignore

    return decorator
