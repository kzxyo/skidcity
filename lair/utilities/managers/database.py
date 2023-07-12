import orjson
import asyncpg
from utilities import config
from discord.ext.commands import CommandError

class Database:
    def __init__(self):
        self.config = config
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
                config.Database.user,
                config.Database.password,
                config.Database.name,
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

    async def fetchdict(self, query: str, *args):
        result = await self.pool.fetch(query, *args)
        return [dict(row) for row in result]