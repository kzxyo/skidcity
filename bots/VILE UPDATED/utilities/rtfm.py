import os, discord, re, zlib
from io import BytesIO
from typing import Generator, Dict, List, Tuple, Iterable, Optional, Callable, Union
from . import DL as http
from .context import Context


RTFM_PAGE_TYPES = {
    'stable': 'https://discordpy.readthedocs.io/en/stable',
    'latest': 'https://discordpy.readthedocs.io/en/latest',
    'python': 'https://docs.python.org/3'
}


class SphinxObjectFileReader:
    BUFSIZE = 16 * 1024


    def __init__(self, buffer: bytes):
        self.stream = BytesIO(buffer)


    def readline(self) -> str:
        return self.stream.readline().decode('utf-8')


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
        
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')

            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1 :]
                pos = buf.find(b'\n')


def finder(text: str, collection: Iterable[str], key: Optional[Callable[[str], str]] = None) -> Union[List[Tuple[int, int, str]], List[str]]:
    
    suggestions = list()
    text = text
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)

    for item in collection:
        to_search = key(item) if key else str(item)
        r = regex.search(to_search)

        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(_tuple: Tuple[int, int, str]) -> Tuple[int, int, str]:
        if key:
            return _tuple[0], _tuple[1], key(_tuple[2])
        return _tuple

    return [z for _, _, z in sorted(suggestions, key=sort_key)]


class RTFM:
    def __init__(self):
        self._rtfm_cache = dict()


    def parse_object_inv(self, stream: SphinxObjectFileReader, url: str) -> Dict[str, str]:

        result = dict()

        inv_version = stream.readline().rstrip()
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]
        line = stream.readline()
        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')

        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())

            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')

            if directive == 'py:module' and name in result:
                continue

            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result


    async def build_rtfm_lookup_table(self) -> None:

        cache = dict()

        for key, page in RTFM_PAGE_TYPES.items():
            cache[key] = dict()
            resp = await http.read(page + '/objects.inv')

            stream = SphinxObjectFileReader(resp)
            cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache


    async def do_rtfm(self, ctx: Context, key: str, obj: str):

        if not self._rtfm_cache:
            async with ctx.handle_response():
                await self.build_rtfm_lookup_table()

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            q = obj.lower()

            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue

                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())
        matches = finder(obj, cache, key=lambda t: t[0])[:60]

        embed = discord.Embed(color=ctx.bot.color, title=f'RTFM: {obj}', description=list())
        if len(matches) == 0:
            return await ctx.send_error("couldn't find anything matching that query")

        for key, url in matches:
            embed.description.append(f'[`{key}`]({url})')

        return await ctx.paginate(embed)