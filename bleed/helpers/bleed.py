import json

from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

import discord

from aiohttp.client_exceptions import (
    ClientConnectorError,
    ClientResponseError,
    ContentTypeError,
)
from asyncpg import Connection, Pool, create_pool
from discord import AuditLogEntry, Embed, Guild, HTTPException, Message
from discord.ext import commands
from discord.ext.commands import Command, Group
from discord.utils import utcnow
from pomice import Node

import config

from helpers.converters import Member, User
from helpers.managers import ClientSession, Context
from helpers.tuuid import tuuid
from helpers.utilities import human_join, plural


class Bleed(commands.AutoShardedBot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=self.get_prefix,
            help_command=None,
            strip_after_prefix=True,
            case_insensitive=True,
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                users=True,
                roles=False,
                replied_user=False,
            ),
            activity=discord.Activity(
                type=config.Status.type,
                name=config.Status.name,
            ),
            owner_ids=config.owner_ids,
        )
        self.ready: bool = False
        self.uptime: datetime = utcnow()
        self.session: ClientSession
        self.node: Node
        self.db: Pool
        self.run()

    @property
    def members(self):
        return list(self.get_all_members())

    @property
    def channels(self):
        return list(self.get_all_channels())

    @property
    def text_channels(self):
        return list(
            filter(
                lambda channel: isinstance(channel, discord.TextChannel),
                self.get_all_channels(),
            )
        )

    @property
    def voice_channels(self):
        return list(
            filter(
                lambda channel: isinstance(channel, discord.VoiceChannel),
                self.get_all_channels(),
            )
        )

    def run(self) -> None:
        super().run(
            token=config.token,
            reconnect=True,
        )

    async def on_ready(self) -> None:
        if not self.ready:
            self.ready = True
        else:
            return

        self.uptime
        self.session = ClientSession()
        await self.create_pool()
        await self.load_extension("jishaku")
        for category in Path("cogs").iterdir():
            if not category.is_dir():
                continue
            elif not (category / "__init__.py").is_file():
                continue
            else:
                await self.load_extension(".".join(category.parts))

    async def create_pool(self) -> None:
        def encode_jsonb(value):
            return json.dumps(value)

        def decode_jsonb(value):
            return json.loads(value)

        async def init(connection: Connection) -> None:
            await connection.set_type_codec(
                "jsonb",
                schema="pg_catalog",
                format="text",
                encoder=encode_jsonb,
                decoder=decode_jsonb,
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

        with open("helpers/schema/tables.sql", "r") as f:
            await self.db.execute(f.read())

    async def get_prefix(self, message: Message) -> Any:
        prefix = (
            await self.db.fetchval(
                """
            SELECT prefix FROM config
            WHERE guild_id = $1
            """,
                message.guild.id,
            )
            or config.prefix
        )
        if prefix == "disabled":
            return commands.when_mentioned(self, message)

        return commands.when_mentioned_or(prefix)(self, message)

    async def get_context(self, origin: Message, *, cls=None) -> Context:
        return await super().get_context(
            origin,
            cls=cls or Context,
        )

    def check_message(self, message: Message) -> bool:
        if not self.is_ready() or message.author.bot or not message.guild:
            return False

        return True

    def get_command(self, *args, **kwargs) -> Optional[Command]:
        if command := super().get_command(*args, **kwargs):
            if (
                (cog := command.cog_name)
                and cog.lower() in ("jishaku", "developer")
                or command.hidden
            ):
                return None

        return command

    def walk_commands(self) -> Union[Command, Group]:
        for command in super().walk_commands():
            if (
                (cog := command.cog_name)
                and cog.lower() in ("jishaku", "developer")
                or command.hidden
            ):
                continue

            yield command

    async def on_command_error(self, ctx: Context, error: Exception) -> Message:
        ignored = (
            commands.CommandNotFound,
            commands.NotOwner,
            commands.CheckFailure,
            commands.DisabledCommand,
            commands.UserInputError,
        )
        if type(error) in ignored:
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help()

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.warn(
                f"You're **missing** {plural(error.missing_permissions, number=False):permission}: "
                + ", ".join(
                    [f"`{permission}`" for permission in error.missing_permissions]
                )
            )

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.neutral(
                f"Please wait **{error.retry_after:.2f} seconds** before using this command again",
                color=config.Color.cooldown,
                emoji=config.Emoji.cooldown,
                delete_after=10,
            )

        elif isinstance(error, commands.MaxConcurrencyReached):
            pass

        elif isinstance(error, commands.BadArgument):
            return await ctx.warn(error)

        elif isinstance(error, commands.BadUnionArgument):
            if error.converters == (Member, User):
                return await ctx.warn(
                    "I was unable to find that **member** or the **ID** is invalid"
                )

            elif error.converters == (discord.Guild, discord.Invite):
                return await ctx.warn("Invalid **invite code** given")

            else:
                return await ctx.warn(
                    f"Could not convert **{error.param.name}** into "
                    + human_join(
                        [f"`{converter.__name__}`" for converter in error.converters]
                    )
                )

        elif isinstance(error, commands.MemberNotFound):
            return await ctx.warn(
                "I was unable to find that **member** or the **ID** is invalid"
            )

        elif isinstance(error, commands.UserNotFound):
            return await ctx.warn(
                "I was unable to find that **user** or the **ID** is invalid"
            )

        elif isinstance(error, commands.RoleNotFound):
            return await ctx.warn(
                f"I was unable to find a role with the name: **{error.argument}**"
            )

        elif isinstance(error, commands.ChannelNotFound):
            return await ctx.warn(
                f"I was unable to find a channel with the name: **{error.argument}**"
            )

        elif isinstance(error, commands.GuildNotFound):
            if error.argument.isdigit():
                return await ctx.warn(
                    f"I do not **share a server** with the ID `{error.argument}`"
                )
            else:
                return await ctx.warn(
                    f"I do not **share a server** with the name `{error.argument}`"
                )

        elif isinstance(error, commands.BadInviteArgument):
            return await ctx.warn("Invalid **invite code** given")

        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, HTTPException):
                if error.original.code == 50035:
                    return await ctx.warn(
                        "**Invalid code**" f"```\n{error.original}```"
                    )

                elif error.original.code == 50013:
                    return await ctx.warn("I'm missing necessary **permissions**!")

                elif error.original.code == 60003:
                    return await ctx.warn(
                        f"**{self.application.owner}** doesn't have **2FA** enabled!"
                    )

            elif isinstance(error.original, ClientConnectorError):
                return await ctx.warn("**API** no longer exists")

            elif isinstance(error.original, ClientResponseError):
                if error.original.status == 522:
                    return await ctx.warn(
                        "**Timed out** while requesting data - probably the API's fault"
                    )
                else:
                    return await ctx.warn(
                        f"**API** returned a `{error.original.status}` - try again later"
                    )

            elif isinstance(error.original, ContentTypeError):
                return await ctx.warn(
                    "**API** returned an error for that request - try again later"
                )

        if "*" in str(error) or "`" in str(error):
            return await ctx.warn(str(error))

        else:
            error_code = tuuid()
            await self.db.execute(
                """
                INSERT INTO traceback (
                    command,
                    error_code,
                    error_message,
                    guild_id,
                    channel_id,
                    user_id
                ) VALUES ($1, $2, $3, $4, $5, $6)
                """,
                ctx.command.qualified_name,
                error_code,
                str(error),
                ctx.guild.id,
                ctx.channel.id,
                ctx.author.id,
            )
            return await ctx.warn(
                f"Error occurred while performing command **{ctx.command.qualified_name}**. Use this error code `{error_code}` to report to the"
                f" developers in the [support server]({config.support_server})"
            )

    async def on_guild_join(self, guild: Guild) -> None:
        if channel := discord.utils.find(
            lambda c: c.permissions_for(guild.me).embed_links, guild.text_channels
        ):
            embed = Embed(
                color=config.Color.bleed,
                title="Getting started with bleed",
                description=(
                    "Hey! Thanks for your interest in **bleed bot**. "
                    "The following will provide you with some tips on how to get started with your server!"
                ),
            )
            embed.set_thumbnail(url=self.user.display_avatar)

            embed.add_field(
                name="**Prefix 🤖**",
                value=(
                    "The most important thing is my prefix. "
                    f"It is set to `{config.prefix}` by default for this server and it is also customizable, "
                    "so if you don't like this prefix, you can always change it with `prefix set` command!"
                ),
                inline=False,
            )
            embed.add_field(
                name="**Moderation System 🛡️**",
                value=(
                    "If you would like to use moderation commands, such as `jail`, `ban`, `kick` and so much more... "
                    "please run the `setme` command to quickly set up the moderation system."
                ),
                inline=False,
            )
            embed.add_field(
                name="**Documentation and Help 📚**",
                value=(
                    "You can always visit our [documentation](https://docs.bleed.bot) "
                    "and view the list of commands that are available [here](https://bleed.bot/help)"
                    " - and if that isn't enough, feel free to join our [Support Server](https://discord.gg/7QHPCxU) for extra assistance!"
                ),
            )

            await channel.send(embed=embed)

    async def on_message(self, message: Message) -> None:
        if not self.check_message(message):
            return
        else:
            await self.process_commands(message)

        if (
            message.guild.system_channel_flags.premium_subscriptions
            and message.type
            in (
                discord.MessageType.premium_guild_subscription,
                discord.MessageType.premium_guild_tier_1,
                discord.MessageType.premium_guild_tier_2,
                discord.MessageType.premium_guild_tier_3,
            )
        ):
            self.dispatch(
                "member_boost",
                message.author,
            )

    async def on_message_edit(self, before: Message, message: Message) -> None:
        if not self.check_message(message):
            return

        elif before.content == message.content or not message.content:
            return

        else:
            await self.process_commands(message)

    async def on_member_join(self, member: discord.Member) -> None:
        if not member.pending:
            self.dispatch(
                "member_agree",
                member,
            )

    async def on_member_remove(self, member: discord.Member) -> None:
        if member.premium_since:
            self.dispatch(
                "member_unboost",
                member,
            )

    async def on_member_update(
        self, before: discord.Member, member: discord.Member
    ) -> None:
        if before.pending and not member.pending:
            self.dispatch(
                "member_agree",
                member,
            )

        if booster_role := member.guild.premium_subscriber_role:
            if (booster_role in before.roles) and not (booster_role in member.roles):
                self.dispatch(
                    "member_unboost",
                    before,
                )

            elif (
                system_flags := member.guild.system_channel_flags
            ) and system_flags.premium_subscriptions:
                return

            elif not (booster_role in before.roles) and (booster_role in member.roles):
                self.dispatch(
                    "member_boost",
                    member,
                )

    async def on_audit_log_entry_create(self, entry: AuditLogEntry) -> None:
        if not self.is_ready() or not entry.guild:
            return

        event = "audit_log_entry_" + entry.action.name
        self.dispatch(
            event,
            entry,
        )
