from asyncio import Future
from asyncio import ensure_future as future
from asyncio import get_event_loop
from functools import partial, wraps


def async_executor():
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            task = partial(func, *args, **kwargs)
            return get_event_loop().run_in_executor(None, task)

        return inner

    return outer


async def ensure_future(coro, silent: bool = True) -> None:
    task: Future = future(coro)

    try:
        return await task
    except Exception:
        if not silent:
            raise
