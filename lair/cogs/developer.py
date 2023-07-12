import datetime
import importlib
import time
import traceback
import importlib
import re
from typing import Any, Awaitable, Callable, Literal, Optional, List, Union
from utilities.lair import Rec
from discord import HTTPException, Member, Reaction, User
from discord.ext.commands import command, is_owner, group
from utilities.general import DurationConverter
from utilities.general.text import api_key_generator
from utilities.lair import Lair
from utilities.managers import Wrench, Context, Writing
from discord import Embed, Member, User, File
from utilities.general import plural, TabularData
from io import BytesIO


class Developer(Wrench):
    @staticmethod
    def cleanup_code(content: str) -> str:
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        return content.strip("` \n")

    @staticmethod
    async def send_sql_results(ctx: Context, records: List[Any]):
        headers = list(records[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in records)
        render = table.render()

        fmt = f"```\n{render}\n```"
        if len(fmt) > 2000:
            fp = BytesIO(fmt.encode("utf-8"))
            await ctx.send(
                "Result reached character limit.", file=File(fp, "results.txt")
            )
        else:
            await ctx.send(fmt)
    @command(name="ping", aliases=["pin"])
    async def ping(self, ctx: Context):
        return await ctx.send(round(self.bot.latency * 1000, 2))
    
    @command()
    @is_owner()
    async def pull(self, ctx: Context):
        await self.bot.shell("git pull")
        return await ctx.message.add_reaction("👍")
    
    @command(name="shell", aliases=["sh"])
    @is_owner()
    async def shell(self, ctx: Context, *, command: str):
        await self.bot.shell(command)
        return await ctx.message.add_reaction("👍")
    
    @command()
    @is_owner()
    async def userinfo(self, ctx: Context, user: Member | User | int):
        try:
            data = await self.bot.ipc.request("getprofile", source="selfbot", user_id=user.id)
            return await ctx.send(data)
        except HTTPException:
            print(data)

    @command()
    @is_owner()
    async def key(self, ctx: Context, option: Optional[Literal['add', 'remove']], user: Member | User, expiry: DurationConverter) -> Reaction:
        if option == "add":
            if not expiry:
                expiry = datetime.timedelta(days=1)
            api_key = api_key_generator(user.name)
            await self.bot.db.execute('INSERT INTO api_keys (user_id, api_key, expiry) VALUES ($1, $2, $3)', user.id, str(api_key), expiry)
            await user.send(f"Your API key is: `{api_key}`")
            return await ctx.message.add_reaction("👍")

        if option == "remove":
            await self.bot.db.execute('DELETE FROM api_keys WHERE user_id = $1', user.id)
            return await ctx.message.add_reaction("👍")

    @command(name="reload", brief="Reload a cog.")
    @is_owner()
    async def reload(self, ctx: Context, *cogs: str):
        reloaded = []
        for cog in cogs:
            match = re.match(r"^([#$!])\.(.+)$", cog)
            if match:
                if match.group(1) == "~":
                    await ctx.send(match)
                    for m in list(self.bot.extensions):
                        try:
                            await self.bot.reload_extension(m)
                            reloaded.append(m)
                        except Exception as error:
                            return await ctx.warn(error)
                if match.group(1) == "#":
                    await self.bot.reload_extension(f"cogs.{match.group(2)}")
                    reloaded.append(f'cogs.{match.group(2)}')
                if match.group(1) == "$":
                    await self.bot.reload_extension(f"events.{match.group(2)}")
                    reloaded.append(f'events.{match.group(2)}')
                    reloaded.append(match.group(2))
                if match.group(1) == "!":
                    importlib.reload(importlib.import_module(match.group(2)))
                    reloaded.append(match.group(2))
        if reloaded:
            return await ctx.done(
                f"Reloaded **{len(reloaded)}** {'module' if len(reloaded) <= 1 else 'modules'}: " + "\n".join(reloaded)
            )

    @group(invoke_without_command=True)
    @is_owner()
    async def sql(self, ctx: Context, *, query: str):
        async with Writing(ctx.message):
            query = self.cleanup_code(query)

            is_multistatement = query.count(";") > 1
            strategy: Callable[[str], Union[Awaitable[list[Rec]], Awaitable[str]]]
            if is_multistatement:
                strategy = self.bot.db.execute
            else:
                strategy = self.bot.db.fetch

            try:
                start = time.perf_counter()
                results = await strategy(query)
                dt = (time.perf_counter() - start) * 1000.0
            except Exception:
                return await ctx.warn(f"```py\n{traceback.format_exc()}\n```")

            rows = len(results)
            if isinstance(results, str) or rows == 0:
                return await ctx.send(f"`{dt:.2f}ms: {results}`")

            headers = list(results[0].keys())
            table = TabularData()
            table.set_columns(headers)
            table.add_rows(list(r.values()) for r in results)
            render = table.render()

            fmt = f"```\n{render}\n```\n*Returned {plural(rows):row} in {dt:.2f}ms*"
            if len(fmt) > 500:
                fp = BytesIO(fmt.encode("utf-8"))
                await ctx.send(file=File(fp, "lair.txt"))
            else:
                await ctx.send(fmt)

    @sql.command(name="schema", hidden=True)
    @is_owner()
    async def sql_schema(self, ctx: Context, *, table_name: str):
        async with Writing(ctx.message):
            query = """SELECT column_name, data_type, column_default, is_nullable
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE table_name = $1
                    """

            results: list[Rec] = await self.bot.db.fetch(query, table_name)

            if len(results) == 0:
                return await ctx.error("Could not find a table with that name")

            await self.send_sql_results(ctx, results)

    @sql.command(name="tables", hidden=True, aliases=["table"])
    @is_owner()
    async def sql_tables(self, ctx: Context):
        async with Writing(ctx.message):
            query = """SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema='public' AND table_type='BASE TABLE'
                    """

            results: list[Rec] = await self.bot.db.fetch(query)

            if len(results) == 0:
                return await ctx.error("Could not find any tables")

            await self.send_sql_results(ctx, results)



async def setup(bot: Lair):
    await bot.add_cog(Developer(bot=bot))
