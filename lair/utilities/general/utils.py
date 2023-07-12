from __future__ import annotations
import asyncio
from functools import partial, wraps
from io import BytesIO
import imagehash
import random
from PIL import Image
import string

from typing import Any, Iterable, Optional, Sequence


class plural:
    def __init__(self, value: int):
        self.value: int = value

    def __format__(self, format_spec: str) -> str:
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


class TabularData:
    def __init__(self):
        self._widths: list[int] = []
        self._columns: list[str] = []
        self._rows: list[list[str]] = []

    def set_columns(self, columns: list[str]):
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row: Iterable[Any]) -> None:
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 2
            if width > self._widths[index]:
                self._widths[index] = width

    def add_rows(self, rows: Iterable[Iterable[Any]]) -> None:
        for row in rows:
            self.add_row(row)

    def render(self) -> str:
        sep = "+".join("-" * w for w in self._widths)
        sep = f"+{sep}+"

        to_draw = [sep]

        def get_entry(d):
            elem = "|".join(f"{e:^{self._widths[i]}}" for i, e in enumerate(d))
            return f"|{elem}|"

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return "\n".join(to_draw)

def unique_id(lenght: int = 6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=lenght))

def async_executor():
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            task = partial(func, *args, **kwargs)
            return asyncio.get_event_loop().run_in_executor(None, task)

        return inner

    return outer

@async_executor()
def image_hash(image: BytesIO):
    if isinstance(image, bytes):
        image = BytesIO(image)

    result = str(imagehash.average_hash(image=Image.open(image), hash_size=8))
    if result == "0000000000000000":
        return unique_id(16)
    else:
        return result