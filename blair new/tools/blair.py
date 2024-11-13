from discord.utils import utcnow
from discord import (
    AllowedMentions,
    Message,
    Guild,
    HTTPException,
    AuditLogEntry,
    Intents,
    Status,
)
from discord_http import Client  # type: ignore
from discord.ext.commands import AutoShardedBot, CommandError, when_mentioned_or
from discord.ext.commands import (
    Flag,
    NotOwner,
    CheckFailure,
    UserInputError,
    DisabledCommand,
    CommandNotFound,
    CommandOnCooldown,
    MemberNotFound,
    UserNotFound,
    RoleNotFound,
    ChannelNotFound,
    MissingPermissions,
    RangeError,
    BadInviteArgument,
    BadFlagArgument,
    BadColourArgument,
    MissingRequiredAttachment,
    MissingRequiredArgument,
    MissingRequiredFlag,
    BadLiteralArgument,
)

from aiohttp.client_exceptions import (
    ClientConnectorError,
    ClientResponseError,
    ContentTypeError,
)

from pathlib import Path
from datetime import datetime
from cashews import cache
from tornado.ioloop import IOLoop
from traceback import format_exception
from xxhash import xxh128_hexdigest

from typing import TYPE_CHECKING, Dict, List, Optional, cast

import config
from tools.discord import logging, HelpCommand, Context, Error, codeblock
from tools.networking import ClientSession, connect, Redis

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)


class Blair(AutoShardedBot):
    def __init__(self: "Blair", *args, **kwargs) -> None:
        super().__init__(
            command_prefix=self.get_prefix,
            allowed_mentions=AllowedMentions(
                everyone=False,
                roles=False,
                replied_user=False,
                users=True,
            ),
            help_command=HelpCommand(),
            intents=Intents.all(),
            case_insensitive=True,
            status=Status.dnd,
            owner_ids=config.OWNER_IDS,
            shard_count=3,
            *args,
            **kwargs,
        )
        self.cache = cache
        self.traceback: Dict[str, Dict] = {}
        self.ioloop: IOLoop
        self.blacklist: List[int] = []
        self.session: ClientSession
        self.uptime: datetime

        self.run(
            config.TOKEN,
            log_handler=None,
        )

    @property
    def command_count(self: "Blair") -> int:
        return len(set(self.walk_commands()))

    async def get_prefix(self: "Blair", message: Message) -> List[str]:
        prefix = [config.PREFIX]
        if message.guild:
            prefix = (
                cast(
                    Optional[List[str]],
                    await self.db.fetchval(
                        """
                        SELECT prefixes
                        FROM settings
                        WHERE guild_id = $1
                        """,
                        message.guild.id,
                    ),
                )
                or prefix
            )

        return when_mentioned_or(*prefix)(self, message)

    async def setup_hook(self: "Blair") -> None:
        self.session = ClientSession()
        self.ioloop = IOLoop.current()
        self.db = await connect()
        self.redis = await Redis.from_url()

        await self.load_extension("jishaku")

        for feature in Path("cogs").iterdir():
            if not feature.is_dir():
                continue

            elif not (feature / "__init__.py").is_file():
                continue

            await self.load_extension(".".join(feature.parts))

        """
        client = Client(
            token=config.TOKEN,
            application_id=config.APPLICATION_ID,
            public_key=config.PUBLIC_KEY,
            sync=False
        )

        client.start()
        """

    async def on_ready(self: "Blair") -> None:
        log.info(
            f"Connected to client ({self.user.name} / {self.user.id}) with {self.command_count} commands!"
        )

        self.uptime = utcnow()

    async def on_guild_join(self: "Blair", guild: Guild) -> None:
        log.info(f"Joined {guild} owned by {guild.owner} ({guild.owner.id})!")

        return await self.get_channel(1290752716187897927).send(
            f"Joined `{guild}` owned by {guild.owner} / {guild.owner.id}"
        )

    async def process_commands(self: "Blair", message: Message) -> None:
        if not message.guild:
            return

        elif message.author.id in self.blacklist:
            return

        return await super().process_commands(message)

    async def on_message_edit(self: "Blair", before: Message, after: Message) -> None:
        if before.content == after.content:
            return

        await self.on_message(after)

    async def get_context(self: "Blair", message: Message, *, cls=Context) -> Context:
        return await super().get_context(message, cls=cls)

    async def on_command(self: "Blair", ctx: Context) -> None:
        log.info(
            f"{ctx.author} ({ctx.author.id}) performed {ctx.command} / {ctx.guild} ({ctx.guild.id})!"
        )

    async def on_command_error(
        self: "Blair", ctx: Context, exception: CommandError
    ) -> Optional[Message]:
        exception = getattr(exception, "original", exception)
        if type(exception) in (
            NotOwner,
            CheckFailure,
            UserInputError,
            DisabledCommand,
            CommandNotFound,
        ):
            return

        if isinstance(exception, CommandOnCooldown):
            return self.ioloop.add_callback(
                ctx.message.add_reaction,
                "⏰",
            )

        elif isinstance(
            exception,
            (
                UserNotFound,
                MemberNotFound,
                ChannelNotFound,
                RoleNotFound,
            ),
        ):
            return await ctx.respond("I couldn't locate the `provided entity`!")

        elif isinstance(exception, MissingPermissions):
            return await ctx.respond(
                f"You don't have the required permissions to run `{ctx.command}`!"
            )

        elif isinstance(exception, RangeError):
            return await ctx.respond(
                f"The value must be between `{exception.minimum}` and `{exception.maximum}`, you provided `{exception.value}`!"
            )

        elif isinstance(exception, BadInviteArgument):
            return await ctx.respond("The `provided invite` wasn't found!")

        elif isinstance(exception, BadFlagArgument):
            flag: Flag = exception.flag
            argument: str = exception.argument

            return await ctx.respond(
                f"I couldn't convert `{flag}` with input `{argument}`!"
                + (f"\n> {flag.description}" if flag.description else "")
            )

        elif isinstance(exception, BadColourArgument):
            color: str = exception.argument

            return await ctx.respond(
                f"Color `{color}` is not a valid color!"
                + (
                    "\n> Please ensure it starts with a `#`."
                    if not color.startswith("#") and len(color) == 6
                    else ""
                )
            )

        elif isinstance(exception, MissingRequiredAttachment):
            return await ctx.respond("You need to provide an `attachment`!")

        elif isinstance(
            exception,
            (MissingRequiredArgument, MissingRequiredFlag, BadLiteralArgument),
        ):
            return await ctx.send_help(ctx.command)

        elif isinstance(exception, Error):
            return await ctx.respond(exception.message)

        elif isinstance(exception, HTTPException):
            code: int = exception.code

            if code == 50045:
                return await ctx.respond("The `provided asset` is too large for use!")

            elif code == 50013:
                return await ctx.respond(
                    "I am missing the required `permissions`!"
                    + (
                        "\n> Please ensure I have **Administrator** permissions and retry."
                    )
                )

            elif code == 60003 and self.application:
                return await ctx.respond(
                    f"`{self.application.owner}` doesn't have **2FA** enabled!"
                )

            elif code == 50035:
                return await ctx.respond(
                    "I was unable to send the message!"
                    + (f"\n>>> {codeblock(exception.text)}")
                )

            elif isinstance(exception, ClientConnectorError):
                return await ctx.respond("The `API` timed out during the request!")

            elif isinstance(exception, ClientResponseError):
                return await ctx.respond(
                    f"The third party `API` returned a `{exception.status}`"
                    + (
                        f" [*`{exception.message}`*](https://http.cat/{exception.status})"
                        if exception.message
                        else "!"
                    )
                )

            elif isinstance(exception, ContentTypeError):
                return await ctx.respond(
                    "The `API` returned malformed content, try again later!"
                )

            error_code = xxh128_hexdigest(
                f"{ctx.channel.id}:{ctx.message.id}",
                seed=1337,
            )

            self.traceback[error_code] = {
                "traceback": format_exception(exception),
                "command": ctx.command,
                "user": ctx.author,
                "guild": ctx.guild,
                "channel": ctx.channel,
                "timestamp": ctx.message.created_at,
            }

            return await ctx.respond(
                f"Something went wrong while executing `{ctx.command}`!"
                f"\n> Please report [`{error_code}`]({config.SUPPORT})."
            )

    async def on_audit_log_entry_create(self, entry: AuditLogEntry) -> None:
        if not self.is_ready():
            return

        event = f"audit_log_entry_{entry.action.name}"
        self.dispatch(event, entry)
