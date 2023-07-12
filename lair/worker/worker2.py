from typing import Coroutine
from discord.ext.commands import Bot, CommandError
from discord import Intents, User, Message
from loguru import logger
import sys
from xxhash import xxh64_hexdigest
import asyncpg
import discord
import contextlib
import time
from typing import Any
import orjson
import asyncio
from functools import partial, wraps
from io import BytesIO
import imagehash
import random
from PIL import Image
import string

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
owners = [1093956521332838453, 1105178083977334864]

class Database:
    def __init__(self):
        self.pool = None

    def __repr__(self):
        return f"<Database host=127.0.0.1>"

    def _encode_jsonb(*values):
        return orjson.dumps(values[1])

    def _decode_jsonb(*values):
        return orjson.loads(values[1])

    async def _init(self, conn):
        await conn.set_type_codec(
            "jsonb",
            encoder=self._encode_jsonb,
            decoder=self._decode_jsonb,
            schema="pg_catalog",
            format="text",
        )

    async def connect(self):
        self.pool: asyncpg.Pool = await asyncpg.create_pool(
            "postgres://%s:%s@127.0.0.1/%s"
            % (
                "postgres",
                "lair",
                "lair",
            ),
            init=self._init,
        )
        await self.create_tables()
        return self

    async def close(self):
        await self.pool.close()

    async def create_tables(self):
        try:
            with open("utilities/schema/tables.sql") as r:
                return await self.pool.execute(r.read())
        except FileNotFoundError:
            return

    async def execute(self, query: str, *args, **kwargs):
        args, _args = list(args), list(args).copy()
        if ";" in query and args:
            for _function in query.split(";"):
                if function := _function.strip():
                    await self.pool.execute(function, *args)
            return
        if query.startswith("DELETE") or query.startswith("UPDATE"):
            table = query.split(" ")[2] if query.startswith("DELETE") else query.split(" ")[1]
            select = None
            for index, argument in enumerate(args):
                if str(argument).lower().startswith("select:"):
                    args = list(filter(lambda arg: not str(arg).lower().startswith("select:"), args))
                    select: str = argument.split(":")[1]
                    if select.isdigit() and int(select) > 0:
                        select = (index, (int(select) - 1 or 0))
                        break
                    else:
                        raise CommandError("Provided invalid **select** argument.")

            if select:
                parameters = list()
                parameter = "*"
                if "WHERE" in query:
                    for index, parameter in enumerate(query.split("WHERE")[1].split("AND")):
                        if index == select[0]:
                            parameter = parameter.split("=")[0].strip()
                            continue

                        parameters.append(f"{parameter.split('=')[0].strip()} = ${len(parameters) + 1}")

                _query = (
                    "SELECT %s FROM %s WHERE %s" % (parameter, table, " AND ".join(parameters))
                    if parameters
                    else "SELECT %s FROM %s" % (parameter, table)
                )
                rows = await self.pool.fetch(_query, *args)
                try:
                    row = rows[select[1]]
                    args.insert(select[0], row[parameter])
                except IndexError:
                    raise CommandError("Provided invalid **select** argument.")

        if kwargs.get("raise_exceptions"):
            output = await self.pool.execute(query, *args)
            if output == "DELETE 0":
                raise asyncpg.exceptions.ForeignKeyViolationError("No rows were deleted")
            elif output == "UPDATE 0":
                raise asyncpg.exceptions.ForeignKeyViolationError("No rows were updated")
            elif output == "INSERT 0":
                raise asyncpg.exceptions.UniqueViolationError("No rows were inserted")
        else:
            output = await self.pool.execute(query, *args)

        if output.startswith("INSERT"):
            return int(output.split(" ")[-1].split(")")[0])
        return output

    async def executemany(self, query: str, *args):
        return await self.pool.executemany(query, *args)

    async def fetch(self, query: str, *args, **kwargs):
        return await self.pool.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        return await self.pool.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        return await self.pool.fetchval(query, *args)

    async def fetchall(self, query: str, *args):
        return await self.pool.fetch(query, *args)

    async def fetchiter(self, query: str, *args):
        output = await self.pool.fetch(query, *args)
        for row in output:
            yield row

class Workers(Bot):
    def __init__(self, token: str, *args, **kwargs):
        super().__init__(
            command_prefix=".",
            intents=Intents.all(),
            owner_ids=owners
        )
        self.logger = logger
        self.logger.remove()
        self.logger.add(
            sys.stdout,
            colorize=True,
            format=(
                "<cyan>[</cyan><blue>{time:YYYY-MM-DD HH:MM:SS}</blue><cyan>]</cyan> (<magenta>worker:{function}</magenta>) <yellow>@</yellow> <fg"
                " #BBAAEE>{message}</fg #BBAAEE>"
            ),
        )
        self.db = None
        self.last_logged_avatar = {}
        self.token = token
        self.run(token, reconnect=True)

    async def on_ready(self) -> None:
        self.logger.info(f"Started worker: {self.user.name} with {len(self.guilds)} guilds.")

    async def setup_hook(self) -> Coroutine[Any, Any, None]:
        self.db: Database = await Database().connect()
        await self.load_extension('jishaku')

    async def on_message(self, message: Message):
        if message.author.id not in owners:
            return

        await self.process_commands(message)

    async def on_user_update(self, before: User, after: User):
        if before.display_avatar != after.display_avatar:
            channel = self.get_channel(1126445318825848832)
            if before.display_avatar:
                image = await before.avatar.read()
                hash = await image_hash(image)
                file = await before.display_avatar.to_file(filename=f'{before.id}.{"png" if not before.display_avatar.is_animated() else "gif"}')
                tim = round(time.time())
                with contextlib.suppress(discord.HTTPException, discord.errors.NotFound):
                    message = await channel.send(file=file)
                await self.db.execute('INSERT INTO avatars (user_id, username, avatar, time, hash) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (user_id, hash) DO NOTHING', before.id, before.name, message.attachments[0].url, tim, hash)