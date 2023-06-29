import io
import os
import re
import zlib

from typing import Generator

from discord.abc import Messageable
from discord.ext import commands

from helpers import fuzzy


RTFM_PAGE_TYPES = {
    "discord.py": "https://discordpy.readthedocs.io/en/latest",
    "python": "https://docs.python.org/3",
}


class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer: bytes):
        self.stream = io.BytesIO(buffer)

    def readline(self) -> str:
        return self.stream.readline().decode("utf-8")

    def skipline(self) -> None:
        self.stream.readline()

    def read_compressed_chunks(self) -> Generator[bytes, None, None]:
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self) -> Generator[str, None, None]:
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


def parse_object_inv(stream: SphinxObjectFileReader, url: str) -> dict[str, str]:
    # key: URL
    # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
    result: dict[str, str] = {}

    # first line is version info
    inv_version = stream.readline().rstrip()

    if inv_version != "# Sphinx inventory version 2":
        raise RuntimeError("Invalid objects.inv file version.")

    # next line is "# Project: <name>"
    # then after that is "# Version: <version>"
    projname = stream.readline().rstrip()[11:]
    version = stream.readline().rstrip()[11:]

    # next line says if it's a zlib header
    line = stream.readline()
    if "zlib" not in line:
        raise RuntimeError("Invalid objects.inv file, not z-lib compatible.")

    # This code mostly comes from the Sphinx repository.
    entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
    for line in stream.read_compressed_lines():
        match = entry_regex.match(line.rstrip())
        if not match:
            continue

        name, directive, prio, location, dispname = match.groups()
        domain, _, subdirective = directive.partition(":")
        if directive == "py:module" and name in result:
            # From the Sphinx Repository:
            # due to a bug in 1.1 and below,
            # two inventory entries are created
            # for Python modules, and the first
            # one is correct
            continue

        # Most documentation pages have a label
        if directive == "std:doc":
            subdirective = "label"

        if location.endswith("$"):
            location = location[:-1] + name

        key = name if dispname == "-" else dispname
        prefix = f"{subdirective}:" if domain == "std" else ""

        if projname == "discord.py":
            key = key.replace("discord.ext.commands.", "").replace("discord.", "")

        result[f"{prefix}{key}"] = os.path.join(url, location)

    return result


async def build_rtfm_lookup_table(ctx: commands.Context):
    cache: dict[str, dict[str, str]] = {}
    for key, page in RTFM_PAGE_TYPES.items():
        cache[key] = {}
        async with ctx.bot.session.get(page + "/objects.inv") as response:
            if response.status != 200:
                raise RuntimeError("Cannot build rtfm lookup table, try again later.")

            stream = SphinxObjectFileReader(await response.read())
            cache[key] = parse_object_inv(stream, page)

    await ctx.bot.redis.set("rtfm_table", cache, ex=60 * 60 * 26)


async def search(ctx: commands.Context, key: str, obj: str):
    if key == "discord.py":
        obj = re.sub(r"^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)", r"\1", obj)
        for name in dir(Messageable):
            if name[0] == "_":
                continue
            if obj.lower() == name:
                obj = f"abc.Messageable.{name}"
                break

    cache = await ctx.bot.redis.get("rtfm_table")
    if cache is None:
        await build_rtfm_lookup_table(ctx)
        cache = await ctx.bot.redis.get("rtfm_table")

    if key in cache:
        cache = list(cache[key].items())
        matches = fuzzy.finder(obj, cache, key=lambda t: t[0])[:8]
        return matches or None

    return None
