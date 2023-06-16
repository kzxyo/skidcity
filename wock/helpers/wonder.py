import config
import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands.errors import *
from typing import Any


from helpers.patch.context import Context
from helpers.managers.network import ClientSession
from pathlib import Path
from asyncpg import Connection, Pool, create_pool
from pomice import Node
from orjson import dumps, loads



class Wonder(commands.AutoShardedBot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=self.get_prefix,
            strip_after_prefix=True,
            case_insensitive=True,
            help_command=commands.MinimalHelpCommand(),
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                users=True,
                roles=False,
                replied_user=False,
            ),
        )

        self.node: Node
        self.run()
        self.session: ClientSession
        self.db: Pool

    def run(self) -> None:
        super().run(
            token=config.token,
            reconnect=True,
        )

    async def on_ready(self) -> None:
        await self.load_extension("jishaku")
        for category in Path("cogs").iterdir():
            try:
                await self.load_extension(f"cogs.{category.stem}")
            except Exception as e:
                print(e)

        self.session = ClientSession()
        await self.create_pool()

    async def create_pool(self) -> None:
        async def init(connection: Connection) -> None:
            await connection.set_type_codec(
                "jsonb",
                schema="pg_catalog",
                format="text",
                encoder=dumps,
                decoder=loads,
            )

        self.db = await create_pool(
            "postgres://%s:%s@%s/%s"
            % (
                config.Database.user,
                config.Database.password,
                config.Database.host,
                config.Database.name,
            ),
            init=init,
        )

    async def get_context(self, origin: Message, *, cls=None) -> Context:
        return await super().get_context(
            origin,
            cls=cls or Context,
        )
    
    def check_message(self, message: Message) -> bool:
        if not self.is_ready() or message.author.bot or not message.guild:
            return False

        return True
    
    async def on_message(self, message: Message):
        if not self.check_message(message):
            return

        await self.process_commands(message)
    
    async def on_message_edit(self, before: Message, message: Message) -> None:
        if not self.check_message(message):
            return

        elif before.content == message.content or not message.content:
            return

        else:
            await self.process_commands(message)

    async def on_command_error(self, ctx: Context, error: CommandError) -> None:
        ignored = (
            CommandNotFound,
            CheckFailure,
            BadArgument,
            MissingRequiredArgument,
        )

        if isinstance(error, ignored):
            return
        
        else:
            await ctx.neutral(error)

    async def get_prefix(self, message: Message) -> Any:
        prefix = await self.db.fetchval(
            """
            SELECT prefix FROM config
            WHERE guild_id = $1
            """,
            message.guild.id,
        ) or ";"
                
        if prefix == "disabled":
            return commands.when_mentioned(self, message)

        return commands.when_mentioned_or(prefix)(self, message)