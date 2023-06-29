import asyncio
import contextlib
import importlib
import io
import json
import logging
import os
import random
import sys

from copy import copy
from datetime import datetime, timedelta
from multiprocessing import Process
from pathlib import Path
from typing import Dict

import aiohttp
import asyncpg
import discord
import websockets

from cashews import cache
from discord import channel as DiscordChannel
from discord import embeds as DiscordEmbeds
from discord import message as DiscordMessage
from discord.ext import commands, ipc
from discord.ext.ipc.objects import ClientPayload
from discord.ext.ipc.server import Server
from loguru import logger
from redis.asyncio import StrictRedis as AsyncStrictRedis
from redis.asyncio.connection import BlockingConnectionPool
from redis.backoff import EqualJitterBackoff
from redis.retry import Retry

from helpers import checks, functions, humanize, regex, tagscript, tuuid, views
from helpers.paginator import Paginator


try:
    config = json.loads(open("config.json", "r").read())
except FileNotFoundError:
    config = json.loads(open("../config.json", "r").read())
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
logging.getLogger("discord").setLevel(logging.CRITICAL)
logging.getLogger("discord.http").setLevel(logging.CRITICAL)
logging.getLogger("discord.client").setLevel(logging.CRITICAL)
logging.getLogger("discord.gateway").setLevel(logging.CRITICAL)
logging.getLogger("discord.ext.ipc.server").setLevel(logging.CRITICAL)
logging.getLogger("pomice").setLevel(logging.CRITICAL)
cache.setup("mem://")


class wockSuper(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            help_command=None,
            strip_after_prefix=True,
            case_insensitive=True,
            max_messages=1000,
            command_attrs=dict(hidden=True),
            intents=discord.Intents(
                guilds=True,
                members=True,
                messages=True,
                message_content=True,
                presences=True,
                bans=True,
                emojis_and_stickers=True,
                reactions=True,
                voice_states=True,
            ),
            activity=discord.Activity(type=discord.ActivityType.competing, name="discord.gg/wock"),
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=False),
            owner_ids=config.get("owners"),
        )
        self.config = config
        self.domain = config.get("domain")
        self.logger = logger
        self.logger.remove()
        self.logger.add(
            sys.stdout,
            colorize=True,
            format=(
                "<cyan>[</cyan><blue>{time:YYYY-MM-DD HH:MM:SS}</blue><cyan>]</cyan> (<magenta>wock:{function}</magenta>) <yellow>@</yellow> <fg"
                " #BBAAEE>{message}</fg #BBAAEE>"
            ),
        )
        self.ipc = ipc.Server(
            self,
            secret_key="M8XV07GPjmMKA",
            standard_port=3218,
            do_multicast=False,
        )
        self.buckets: dict = dict(
            guild_commands=dict(
                lock=asyncio.Lock(),
                cooldown=commands.CooldownMapping.from_cooldown(
                    12,
                    2.5,
                    commands.BucketType.guild,
                ),
                blocked=set(),
            ),
            response_triggers=commands.CooldownMapping.from_cooldown(
                1,
                2.5,
                commands.BucketType.member,
            ),
            reaction_triggers=commands.CooldownMapping.from_cooldown(
                1,
                2.5,
                commands.BucketType.member,
            ),
            message_reposting=commands.CooldownMapping.from_cooldown(
                3,
                30,
                commands.BucketType.user,
            ),
            tiktok_reposting=commands.CooldownMapping.from_cooldown(
                3,
                30,
                commands.BucketType.user,
            ),
            twitter_reposting=commands.CooldownMapping.from_cooldown(
                15,
                360,
                commands.BucketType.user,
            ),
            instagram_reposting=commands.CooldownMapping.from_cooldown(
                15,
                360,
                commands.BucketType.user,
            ),
            youtube_reposting=commands.CooldownMapping.from_cooldown(
                5,
                60,
                commands.BucketType.user,
            ),
            highlights=commands.CooldownMapping.from_cooldown(
                1,
                60,
                commands.BucketType.member,
            ),
            video_repairs=commands.CooldownMapping.from_cooldown(
                1,
                60,
                commands.BucketType.member,
            ),
        )

    def __repr__(self):
        pid = os.getpid()
        active_tasks = len(asyncio.all_tasks())
        unchunked_guilds = len([guild for guild in self.guilds if not guild.chunked])
        return f"<wock PID={pid} tasks={active_tasks} unchuked={unchunked_guilds}>"

    def run(self, *args, **kwargs):
        self.tasks = list()
        proc = Process(
            name=("wock:main" + functions.unique_id(16)),
            target=super().run,
            kwargs=kwargs,
        )
        proc.start()
        self.logger.info(f"Starting wock")

    async def setup_hook(self):
        self.check(self.command_cooldown)
        await self.load_extension("jishaku")

        self.session: aiohttp.ClientSession = self.http._HTTPClient__session
        self.db: Database = await Database(self.config).connect()
        self.redis: Redis = await Redis.from_url()
        # self.dask: Client = await Client(
        #     asynchronous=True,
        #     dashboard_address="100.121.252.74:133787",
        # )
        # self.socket = WebSocket(self, "wss://dev.wock.cloud/socket-OYGNn43REKA8p")
        # await self.socket.connect()
        await self.ipc.start()

    async def on_ready(self):
        for file in Path("cogs").glob("**/*.py"):
            *tree, _ = file.parts
            module = ".".join(tree)
            try:
                await self.load_extension(f"{module}.{file.stem}")
            except Exception as error:
                self.logger.exception(error)
            else:
                cog_name = [name for name, cog in self.cogs.items() if cog.__module__ == f"{module}.{file.stem}"][0]
                self.logger.success(f"Loaded {cog_name}")

        self.logger.success(f"Logged in as {self.user} ({self.user.id})")

    async def on_guild_join(self, guild: discord.Guild):
        if not guild.chunked:
            await guild.chunk(cache=True)

        if not await self.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1", guild.id):
            with contextlib.suppress(discord.Forbidden):
                await guild.leave()
                self.logger.info(f"Payment not found for guild {guild} ({guild.id})")
        else:
            self.logger.info(f"Joined guild {guild} ({guild.id})")

    async def on_guild_remove(self, guild: discord.Guild):
        self.logger.info(f"Left guild {guild} ({guild.id})")

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

    async def get_context(self, message: discord.Message, *, cls=None):
        return await super().get_context(message, cls=cls or Context)

    async def get_prefix(self, message: discord.Message, mention: bool = True):
        if self.user.id == self.config.get("wock_id"):
            if message.guild:
                prefix = await self.db.fetchval("SELECT prefix FROM config WHERE guild_id = $1", message.guild.id) or self.config.get("prefix")

            if not mention:
                return prefix
            else:
                return commands.when_mentioned_or(prefix)(self, message)
        else:
            return commands.when_mentioned(self, message)

    def get_command(self, command: str, module: str = None):
        if command := super().get_command(command):
            if not command.cog_name:
                return command
            if command.cog_name.lower() in ("jishaku", "developer") or command.hidden:
                return None
            if module and command.cog_name.lower() != module.lower():
                return None
            return command

        return None

    def walk_commands(self):
        for command in super().walk_commands():
            if command.cog_name.lower() in ("jishaku", "developer") or command.hidden:
                continue
            yield command

    @staticmethod
    async def command_cooldown(ctx: commands.Context):
        if ctx.author.id == ctx.guild.owner_id:
            return True

        blocked = ctx.bot.buckets["guild_commands"]["blocked"]
        if not ctx.bot.get_guild(ctx.guild.id) or ctx.guild.id in blocked:
            return False

        bucket = ctx.bot.buckets["guild_commands"]["cooldown"].get_bucket(ctx.message)
        if retry_after := bucket.update_rate_limit():
            blocked.add(ctx.guild.id)
            lock = ctx.bot.buckets["guild_commands"]["lock"]
            async with lock:
                rx = ctx.bot.get_user(1004836998151950358)
                await rx.send(f"le wock is being flooded in {ctx.guild} (`{ctx.guild.id}`) owned by {ctx.guild.owner} (`{ctx.guild.owner_id}`)..")
                return False

        return True

    async def on_command(self, ctx: commands.Context):
        self.logger.info(
            f"{ctx.author} ({ctx.author.id}): {ctx.command.qualified_name} in {ctx.guild} ({ctx.guild.id}) #{ctx.channel} ({ctx.channel.id})"
        )
        await self.db.execute(
            "INSERT INTO metrics.commands (guild_id, channel_id, user_id, command, timestamp) VALUES($1, $2, $3, $4, $5)",
            ctx.guild.id,
            ctx.channel.id,
            ctx.author.id,
            ctx.command.qualified_name,
            ctx.message.created_at,
        )

    async def on_message(self, message: discord.Message):
        if not self.is_ready() or not message.guild or message.author.bot:
            return

        if message.guild.system_channel_flags.premium_subscriptions:
            if message.type in (
                discord.MessageType.premium_guild_subscription,
                discord.MessageType.premium_guild_tier_1,
                discord.MessageType.premium_guild_tier_2,
                discord.MessageType.premium_guild_tier_3,
            ):
                self.dispatch("member_boost", message.author)

        if message.content == f"<@{self.user.id}>":
            with contextlib.suppress(discord.HTTPException):
                prefix = await self.get_prefix(message, mention=False)
                await message.reply(f"hi :3 (prefix is `{prefix}`)")

        ctx = await self.get_context(message)

        if str(message.content).lower().startswith(f"{self.user.name} "):
            if match := regex.URL.match(message.content.split(" ", 1)[1]):
                with contextlib.suppress(discord.HTTPException):
                    await message.delete()

                self.dispatch("message_repost", ctx, match.group())

        if not ctx.command:
            self.dispatch("user_message", ctx, message)
        self.dispatch("user_activity", message.channel, message.author)
        await self.process_commands(message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not self.is_ready() or not before.guild or before.author.bot:
            return

        if before.content == after.content or not after.content:
            return

        self.dispatch("user_activity", after.channel, after.author)
        await self.process_commands(after)

    async def on_typing(self, channel: discord.abc.Messageable, user: discord.User, when: datetime):
        if not self.is_ready() or not channel.guild or user.bot:
            return

        self.dispatch("user_activity", channel, user)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if not self.is_ready() or not reaction.message.guild or user.bot:
            return

        self.dispatch("user_activity", reaction.message.channel, user)

    # async def on_message_delete(self, message: discord.Message):
    #     if not self.is_ready() or not message.guild or message.author.bot:
    #         return

    #     await super().on_message_delete(message)
    #
    # This is pointless since discord.py helpers are retards & you have to monkey patch the event entirely..

    async def on_member_join(self, member: discord.Member):
        if not self.is_ready() or not member.guild:
            return

        if not member.pending:
            self.dispatch("member_agree", member)

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not self.is_ready() or not after.guild:
            return

        if before.pending and not after.pending:
            self.dispatch("member_agree", after)

        if booster_role := after.guild.premium_subscriber_role:
            if booster_role in before.roles and not booster_role in after.roles:
                self.dispatch("member_unboost", before)

            if system_flags := after.guild.system_channel_flags:
                if system_flags.premium_subscriptions:
                    return

            if not booster_role in before.roles and booster_role in after.roles:
                self.dispatch("member_boost", after)

    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        if not self.is_ready() or not entry.guild:
            return

        event = "audit_log_entry_" + entry.action.name.lower()
        self.dispatch(event, entry)

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if not self.is_ready() or member.bot:
            return

        if not before.channel and after.channel:
            self.dispatch("member_voice_join", member, after.channel)
        elif before.channel and not after.channel:
            self.dispatch("member_voice_leave", member, before.channel)
        elif before.channel and after.channel and before.channel != after.channel:
            self.dispatch("member_voice_move", member, before.channel, after.channel)

    async def on_error(self, event: str, *args, **kwargs):
        if event.startswith("on_command"):
            return

        error = sys.exc_info()
        if len(args) != 0 and isinstance(args[0], Context):
            ctx = args[0]
            if "Payload Too Large" in str(error[1]):
                return await ctx.warn("The **video** is too large to be sent")

        if event == "on_member_remove" and "top_role" in str(error[1]):  # wock kicked
            return

        self.logger.info(f"{event}: ({error[0].__name__}): {error[1]} | {args}")
        self.logger.exception(error)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        self.logger.warning(f"{ctx.author} ({ctx.invoked_with}-{type(error).__name__}): {error}")
        if type(error) in (
            commands.NotOwner,
            commands.CheckFailure,
            commands.DisabledCommand,
            commands.UserInputError,
        ):
            return
        elif isinstance(error, commands.CommandNotFound):
            command = await self.db.fetchval(
                "SELECT command FROM aliases WHERE guild_id = $1 AND alias = $2",
                ctx.guild.id,
                ctx.invoked_with.lower(),
            )
            if command := self.get_command(command):
                self.err = ctx
                message = copy(ctx.message)
                message.content = message.content.replace(ctx.invoked_with, command.qualified_name)
                await self.process_commands(message)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help()
        elif isinstance(error, commands.MissingPermissions):
            await ctx.warn(f"You're **missing** the `{', '.join(error.missing_permissions)}` permission")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.warn(f"I'm **missing** the `{', '.join(error.missing_permissions)}` permission")
        elif isinstance(error, commands.GuildNotFound):
            await ctx.warn(f"I wasn't able to find that **guild**")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.warn(f"I wasn't able to find that **channel**")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.warn(f"I wasn't able to find that **role**")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.warn(f"I wasn't able to find that **member**")
        elif isinstance(error, commands.UserNotFound):
            await ctx.warn(f"I wasn't able to find that **user**")
        elif isinstance(error, commands.EmojiNotFound):
            await ctx.warn(f"I wasn't able to find that **emoji**")
        elif isinstance(error, commands.BadUnionArgument):
            parameter = error.param.name
            converters = list()
            for converter in error.converters:
                if name := getattr(converter, "__name__", None):
                    if name == "Literal":
                        converters.extend([f"`{literal}`" for literal in converter.__args__])
                    else:
                        converters.append(f"`{name}`")
            if len(converters) > 2:
                fmt = "{}, or {}".format(", ".join(converters[:-1]), converters[-1])
            else:
                fmt = " or ".join(converters)
            await ctx.warn(f"Couldn't convert **{parameter}** into {fmt}")
        elif isinstance(error, commands.BadLiteralArgument):
            parameter = error.param.name
            literals = [f"`{literal}`" for literal in error.literals]
            if len(literals) > 2:
                fmt = "{}, or {}".format(", ".join(literals[:-1]), literals[-1])
            else:
                fmt = " or ".join(literals)
            await ctx.warn(f"Parameter **{parameter}** must be {fmt}")
        elif isinstance(error, commands.BadArgument):
            await ctx.warn(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.warn(
                f"This command is on cooldown for **{error.retry_after:.2f} seconds**",
                delete_after=(error.retry_after if error.retry_after < 5 else 5),
            )
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.warn(
                f"This command can only be used {functions.plural(error.number, bold=True):time} per **{error.per.name}** concurrently",
                delete_after=5,
            )
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.HTTPException) or isinstance(error.original, discord.NotFound):
                if "Invalid Form Body" in error.original.text:
                    # TODO: Use regex to get the malformed embed schemes
                    parts = "\n".join(
                        [
                            part.split(".", 3)[2] + ":" + part.split(".", 3)[3].split(":", 1)[1].split(".", 1)[0]
                            for part in error.original.text.split("\n")
                            if "." in part
                        ]
                    )
                    if not parts:
                        parts = error.original.text
                    await ctx.warn(f"Your **script** is malformed\n```{parts}\n```")
                elif "Cannot send an empty message" in error.original.text:
                    await ctx.warn(f"Your **script** doesn't contain any **content**")
                elif "Must be 4000 or fewer in length." in error.original.text:
                    await ctx.warn(f"Your **script** content is too **long**")
                return
            elif isinstance(error.original, discord.Forbidden):
                await ctx.warn("I don't have **permission** to do that")
            elif isinstance(error.original, aiohttp.ClientConnectorError):
                await ctx.warn("The **API** is currently **unavailable**")
            elif isinstance(error.original, aiohttp.ContentTypeError):
                await ctx.warn(f"The **API** returned a **malformed response**")
            else:
                unique_id = tuuid.random()
                await self.db.execute(
                    "INSERT INTO traceback (id, command, guild_id, channel_id, user_id, traceback, timestamp) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    unique_id,
                    ctx.command.qualified_name,
                    ctx.guild.id,
                    ctx.channel.id,
                    ctx.author.id,
                    error.args[0],
                    discord.utils.utcnow(),
                )
                await ctx.warn(
                    f"An unknown error occurred while running **{ctx.command.qualified_name}**\n> Please report error `{unique_id}` in the "
                    " [**Discord Server**](https://discord.gg/wock)"
                )
        elif isinstance(error, commands.CommandError):
            await ctx.warn(error)
        else:
            await ctx.warn("An unknown error occurred. Please try again later")

    @Server.route(
        name="shard",
    )
    async def shard_status(self, payload: ClientPayload) -> Dict:
        return {"shard": {"guilds": f"{len(self.guilds):,}", "users": f"{len(self.users):,}", "latency": f"{(self.latency * 1000):.2f}ms"}}

    @Server.route(
        name="shard_commands",
    )
    async def shard_commands(self, payload: ClientPayload) -> Dict:
        return {
            "shard": {
                "cogs": [
                    {
                        "name": cog.qualified_name,
                        "count": len(set(cog.walk_commands())),
                        "commands": [
                            {
                                "name": command.qualified_name,
                                "aliases": command.aliases,
                                "description": command.short_doc,
                                "args": list(command.params),
                                "usage": command.usage,
                                "example": command.example,
                            }
                            for command in cog.walk_commands()
                            if not command.hidden
                        ],
                    }
                    for name, cog in sorted(self.cogs.items(), key=lambda cog: cog[0].lower())
                    if not name.lower() in ("jishaku", "developer")
                ]
            }
        }

    @Server.route(
        name="commands",
    )
    async def ipc_commands(self, payload: ClientPayload) -> Dict:
        output = "Support @ https://wock.cloud\nDefault Prefix: , | () = Required, <> = Optional\n\n"

        for name, cog in sorted(self.cogs.items(), key=lambda cog: cog[0].lower()):
            if name.lower() in ("jishaku", "developer"):
                continue

            _commands = list()
            for command in cog.walk_commands():
                if command.hidden:
                    continue

                usage = " " + command.usage if command.usage else ""
                aliases = "[" + "|".join(command.aliases) + "]" if command.aliases else ""
                if isinstance(command, commands.Group) and not command.root_parent:
                    _commands.append(f"|    ├── {command.name}{aliases}: {command.short_doc or 'No description'}")
                elif not isinstance(command, commands.Group) and command.root_parent:
                    _commands.append(f"|    |   ├── {command.qualified_name}{aliases}{usage}: {command.short_doc or 'No description'}")
                elif isinstance(command, commands.Group) and command.root_parent:
                    _commands.append(f"|    |   ├── {command.qualified_name}{aliases}: {command.short_doc or 'No description'}")
                else:
                    _commands.append(f"|    ├── {command.qualified_name}{aliases}{usage}: {command.short_doc or 'No description'}")

            if _commands:
                output += f"┌── {name}\n" + "\n".join(_commands) + "\n"

        return {
            "bot": {
                "name": self.user.name,
                "avatar": self.user.display_avatar.url,
            },
            "commands": output,
        }

    @Server.route(
        name="avatars",
    )
    async def ipc_avatars(self, payload: ClientPayload) -> Dict:
        if not regex.DISCORD_ID.match(str(payload.user_id)):
            return {"error": "Invalid user ID"}

        avatars = await self.db.fetch("SELECT avatar FROM metrics.avatars WHERE user_id = $1 ORDER BY timestamp DESC", int(payload.user_id))
        if not avatars:
            return {"error": "User has no avatar history"}

        output = {
            "user_id": int(payload.user_id),
            "avatars": [avatar["avatar"] for avatar in avatars],
        }
        if user := self.get_user(int(payload.user_id)):
            output["user"] = {"name": user.name, "avatar": user.display_avatar.url}
        else:
            output["user"] = {"name": "Unknown User", "avatar": self.user.display_avatar.url}

        return output

    @Server.route(
        name="dispatch",
    )
    async def ipc_dispatch(self, payload: ClientPayload) -> Dict:
        self.dispatch(
            payload.event,
            payload.post,
        )

    @Server.route(
        name="music",
    )
    async def ipc_music(self, payload: ClientPayload) -> Dict:
        data = payload.info

        channel = self.get_channel(data["channel_id"])
        player = self.node.get_player(channel.guild.id)

        self.dispatch(
            "music_panel_request",
            player,
            data,
        )

    @Server.route(
        name="webhook",
    )
    async def ipc_webhook(self, payload: ClientPayload) -> Dict:
        info = payload.info
        channel = discord.utils.get(self.get_guild(1004857168761204746).text_channels, name="github")
        if payload.event == "github":
            embed = discord.Embed(
                description=(
                    f"[`{info['repository']['name']}`]({info['repository']['url']}) - {info['author']['name']}\n"
                    + "\n".join(f"> [`{commit['id'][:7]}`]({commit['url']}) {functions.shorten(commit['message'], 39)}" for commit in info["commits"])
                ),
            )
            if info["repository"]["name"] == "rxnk/wock":
                await functions.run_shell("git pull")
                for commit in info["commits"]:
                    if commit["message"].startswith("Bump version"):
                        return

                    for file in commit["files"]["added"]:
                        root, ext = os.path.splitext(file)
                        if root.startswith("cogs/") and ext == ".py":
                            extension = root.split("/", 1)[1]
                            if self.extensions.get(f"cogs.{extension}"):
                                with contextlib.suppress(Exception):
                                    await self.reload_extension(f"cogs.{extension}")
                                    self.logger.info(f"Reloaded cogs.{extension} ({commit['id'][:7]})")
                            else:
                                with contextlib.suppress(Exception):
                                    await self.load_extension(f"cogs.{extension}")
                                    self.logger.info(f"Loaded cogs.{extension} ({commit['id'][:7]})")
                        elif root.startswith("helpers/"):
                            with contextlib.suppress(Exception):
                                module = importlib.import_module(root.replace("/", "."))
                                importlib.reload(module)
                                self.logger.info(f"Reloaded {root} ({commit['id'][:7]})")
                    for file in commit["files"]["removed"]:
                        root, ext = os.path.splitext(file)
                        if root.startswith("cogs/") and ext == ".py":
                            extension = root.split("/", 1)[1]
                            if self.extensions.get(f"cogs.{extension}"):
                                with contextlib.suppress(Exception):
                                    await self.unload_extension(f"cogs.{extension}")
                                    self.logger.info(f"Unloaded cogs.{extension} ({commit['id'][:7]})")
                    for file in commit["files"]["modified"]:
                        root, ext = os.path.splitext(file)
                        if root.startswith("cogs/") and ext == ".py":
                            extension = root.split("/", 1)[1]
                            if self.extensions.get(f"cogs.{extension}"):
                                with contextlib.suppress(Exception):
                                    await self.reload_extension(f"cogs.{extension}")
                                    self.logger.info(f"Reloaded cogs.{extension} ({commit['id'][:7]})")
                        elif root.startswith("helpers/"):
                            with contextlib.suppress(Exception):
                                module = importlib.import_module(root.replace("/", "."))
                                importlib.reload(module)
                                self.logger.info(f"Reloaded {root} ({commit['id'][:7]})")

        await channel.send(embed=embed)


class Message:
    def __init__(self: discord.Message):
        super().__init__()

    async def edit(self, *args, **kwargs):
        kwargs["attachments"] = kwargs.get("attachments", [])

        if embed := kwargs.get("embed"):
            if not embed.color:
                embed.color = functions.config_color("main")
            if embed.title:
                embed.title = functions.shorten(embed.title, 256)
            if embed.description:
                embed.description = functions.shorten(embed.description, 4096)
            if hasattr(embed, "_attachments") and embed._attachments:
                for attachment in embed._attachments:
                    if isinstance(attachment, discord.File):
                        kwargs["attachments"].append(discord.File(copy(attachment.fp), filename=attachment.filename))
                    elif isinstance(attachment, tuple):
                        response = await self._state._get_client().session.get(attachment[0])
                        if response.status == 200:
                            kwargs["attachments"].append(discord.File(io.BytesIO(await response.read()), filename=attachment[1]))

                # embed._attachments = []

        elif embeds := kwargs.get("embeds"):
            for embed in embeds:
                if not embed.color:
                    embed.color = functions.config_color("main")
                if embed.title:
                    embed.title = functions.shorten(embed.title, 256)
                if embed.description:
                    embed.description = functions.shorten(embed.description, 4096)
                if hasattr(embed, "_attachments") and embed._attachments:
                    for attachment in embed._attachments:
                        if isinstance(attachment, discord.File):
                            kwargs["attachments"].append(discord.File(copy(attachment.fp), filename=attachment.filename))
                        elif isinstance(attachment, tuple):
                            response = await self._state._get_client().session.get(attachment[0])
                            if response.status == 200:
                                kwargs["attachments"].append(discord.File(io.BytesIO(await response.read()), filename=attachment[1]))

                    # embed._attachments = []

        if content := (args[0] if args else kwargs.get("content")):
            content = str(content)
            if len(content) > 4000:
                kwargs["content"] = f"Response too large to send (`{len(content)}/4000`)"
                kwargs["attachments"].append(
                    discord.File(
                        io.StringIO(content),
                        filename=f"wockResult.txt",
                    )
                )
                if args:
                    args = args[1:]

        # Run the original edit function with the new payload super() doesn't work since we don't subclass it properly
        return await super(discord.message.Message, self).edit(*args, **kwargs)

    @property
    def emojis(self):
        if not self.content:
            return []

        return list(match[2] for match in regex.DISCORD_EMOJI.findall(self.content))

    async def invites(self):
        if not self.content:
            return

        for match in regex.DISCORD_INVITE.findall(self.content):
            try:
                invite = await self._state._get_client().fetch_invite(match)
            except discord.NotFound:
                continue
            else:
                yield invite

    def __repr__(self):
        return f"<helpers.wock.Message id={self.id} user={self.author.id}>"


DiscordMessage.Message.edit = Message.edit
DiscordMessage.Message.emojis = Message.emojis
DiscordMessage.Message.invites = Message.invites
DiscordMessage.Message.__repr__ = Message.__repr__


class Embed(DiscordEmbeds.Embed):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_attachment(self, attachment: discord.File) -> DiscordEmbeds.Embed:
        if hasattr(self, "_attachments"):
            if attachment not in self._attachments:
                self._attachments.append(attachment)

        return self

    def __repr__(self):
        return f"<helpers.wock.Embed title={self.title!r} description={self.description!r}>"


DiscordEmbeds.Embed.add_attachment = Embed.add_attachment
DiscordEmbeds.Embed.__repr__ = Embed.__repr__


class TextChannelPatch:
    def __init__(self: discord.TextChannel):
        super().__init__()

    @cache(ttl="25m", key="{self.guild.id}:{self.id}", prefix="reskin:channel")
    async def reskin(self):
        bot = self._state._get_client()
        reskin = await bot.db.fetch_config(self.guild.id, "reskin") or {}
        if reskin.get("status") and (reskin.get("username") or reskin.get("avatar_url")):
            if webhook_id := reskin["webhooks"].get(str(self.id)):
                webhook = await self.reskin_webhook(webhook_id)
                if not webhook:
                    del reskin["webhooks"][str(self.id)]
                    await bot.db.update_config(self.guild.id, "reskin", reskin)
                else:
                    return {
                        "username": reskin.get("username") or bot.user.name,
                        "avatar_url": reskin.get("avatar_url") or bot.user.display_avatar.url,
                        "webhook": webhook,
                    }

        return {}

    @cache(ttl="25m", key="{self.id}:{webhook_id}", prefix="reskin:webhook")
    async def reskin_webhook(self, webhook_id: int):
        bot = self._state._get_client()
        try:
            webhook = await bot.fetch_webhook(webhook_id)
        except:
            return None
        else:
            return webhook

    async def send(self, *args, **kwargs):
        kwargs["files"] = kwargs.get("files") or []
        if file := kwargs.pop("file", None):
            kwargs["files"].append(file)

        if embed := kwargs.get("embed"):
            if not embed.color:
                embed.color = functions.config_color("main")
            if embed.title:
                embed.title = functions.shorten(embed.title, 256)
            if embed.description:
                embed.description = functions.shorten(embed.description, 4096)
            if hasattr(embed, "_attachments") and embed._attachments:
                for attachment in embed._attachments:
                    if isinstance(attachment, discord.File):
                        kwargs["files"].append(discord.File(copy(attachment.fp), filename=attachment.filename))
                    elif isinstance(attachment, tuple):
                        response = await self._state._get_client().session.get(attachment[0])
                        if response.status == 200:
                            kwargs["files"].append(discord.File(io.BytesIO(await response.read()), filename=attachment[1]))

        elif embeds := kwargs.get("embeds"):
            for embed in embeds:
                if not embed.color:
                    embed.color = functions.config_color("main")
                if embed.title:
                    embed.title = functions.shorten(embed.title, 256)
                if embed.description:
                    embed.description = functions.shorten(embed.description, 4096)
                if hasattr(embed, "_attachments") and embed._attachments:
                    for attachment in embed._attachments:
                        if isinstance(attachment, discord.File):
                            kwargs["files"].append(discord.File(copy(attachment.fp), filename=attachment.filename))
                        elif isinstance(attachment, tuple):
                            response = await self._state._get_client().session.get(attachment[0])
                            if response.status == 200:
                                kwargs["files"].append(discord.File(io.BytesIO(await response.read()), filename=attachment[1]))

        if content := (args[0] if args else kwargs.get("content")):
            content = str(content)
            if len(content) > 4000:
                kwargs["content"] = f"Response too large to send (`{len(content)}/4000`)"
                kwargs["files"].append(
                    discord.File(
                        io.StringIO(content),
                        filename=f"wockResult.txt",
                    )
                )
                if args:
                    args = args[1:]

        if reskin := await self.reskin():
            webhook = reskin["webhook"]
            kwargs["username"] = reskin["username"]
            kwargs["avatar_url"] = reskin["avatar_url"]
            kwargs["wait"] = True

            delete_after = kwargs.pop("delete_after", None)
            kwargs.pop("stickers", None)
            kwargs.pop("reference", None)

            message = await webhook.send(*args, **kwargs)
            if delete_after:
                await message.delete(delay=delete_after)

            return message

        return await discord.abc.Messageable.send(self, *args, **kwargs)


DiscordChannel.TextChannel.reskin = TextChannelPatch.reskin
DiscordChannel.TextChannel.reskin_webhook = TextChannelPatch.reskin_webhook
DiscordChannel.TextChannel.send = TextChannelPatch.send


def _typing_done_callback(fut: asyncio.Future) -> None:
    # just retrieve any exception and call it a day
    try:
        fut.exception()
    except (asyncio.CancelledError, Exception):
        pass


class Typing:
    def __init__(self, ctx: commands.Context) -> None:
        self.loop: asyncio.AbstractEventLoop = ctx._state.loop
        self.messageable: discord.Message = ctx.message
        self.command: commands.Command = ctx.command
        self.bot: wockSuper = ctx.bot
        self.guild: discord.Guild = ctx.guild
        self.author: discord.Member = ctx.author
        self.channel: discord.TextChannel = ctx.channel

    async def is_reskin(self) -> bool:
        try:
            await checks.donator().predicate(self)
        except:
            pass
        else:
            configuration = await self.bot.db.fetch_config(self.guild.id, "reskin") or {}
            if configuration.get("status"):
                if configuration["webhooks"].get(str(self.channel.id)):
                    reskin = await self.bot.db.fetchrow("SELECT username, avatar_url FROM reskin WHERE user_id = $1", self.author.id)
                    if reskin and (reskin["username"] or reskin["avatar_url"]):
                        return True

        return False

    async def wrapped_typer(self) -> None:
        # if await self.is_reskin():
        #     with contextlib.suppress(discord.HTTPException):
        #         await self.messageable.add_reaction(self.bot.config["styles"]["load"].get("emoji"))
        #         return

        await self.channel._state.http.send_typing(self.channel.id)

    def __await__(self):
        return self.wrapped_typer().__await__()

    async def do_typing(self) -> None:
        typing = self.channel._state.http.send_typing

        while True:
            await asyncio.sleep(5)
            await typing(self.channel.id)

    async def __aenter__(self) -> None:
        if await self.is_reskin():
            if self.command and not self.command.cog_name == "Last.fm Integration":
                with contextlib.suppress(discord.HTTPException):
                    await self.messageable.add_reaction(self.bot.config["styles"]["load"].get("emoji"))
            return

        await self.channel._state.http.send_typing(self.channel.id)
        self.task: asyncio.Task[None] = self.loop.create_task(self.do_typing())
        self.task.add_done_callback(_typing_done_callback)

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        if hasattr(self, "task"):
            self.task.cancel()

        if await self.is_reskin():
            if self.command and not self.command.cog_name == "Last.fm Integration":
                with contextlib.suppress(discord.HTTPException):
                    await functions.ensure_future(self.messageable.remove_reaction(self.bot.config["styles"]["load"].get("emoji"), self.bot.user))
            return


class Context(commands.Context):
    sent_message = None

    @discord.utils.cached_property
    def parameters(self):
        data = {}
        if command := self.command:
            if parameters := command.parameters:
                for name, parameter in parameters.items():
                    data[name] = ParameterSlicer(self).get(parameter=name, **parameter)

        return data

    @discord.utils.cached_property
    def replied_message(self):
        reference = self.message.reference
        if reference and isinstance(reference.resolved, discord.Message):
            return reference.resolved

        return None

    @cache(ttl="1m", key="{self.message.id}", prefix="reskin")
    async def reskin(self):
        try:
            await checks.donator().predicate(self)
        except:
            pass
        else:
            configuration = await self.bot.db.fetch_config(self.guild.id, "reskin") or {}
            if configuration.get("status"):
                if webhook_id := configuration["webhooks"].get(str(self.channel.id)):
                    reskin = await self.bot.db.fetchrow("SELECT username, avatar_url, colors, emojis FROM reskin WHERE user_id = $1", self.author.id)
                    if reskin and (reskin.get("username") or reskin.get("avatar_url")):
                        webhook = await self.channel.reskin_webhook(webhook_id)
                        if not webhook:
                            del configuration["webhooks"][str(self.channel.id)]
                            await self.bot.db.update_config(self.guild.id, "reskin", configuration)
                        else:
                            return {
                                "username": reskin.get("username") or self.bot.user.name,
                                "avatar_url": reskin.get("avatar_url") or self.bot.user.display_avatar.url,
                                "colors": reskin.get("colors", {}),
                                "emojis": reskin.get("emojis", {}),
                                "webhook": webhook,
                            }

        return {}

    async def send(self, *args, **kwargs):
        reskin = await self.reskin()
        kwargs["files"] = kwargs.get("files") or []
        if file := kwargs.pop("file", None):
            kwargs["files"].append(file)

        if embed := kwargs.get("embed"):
            if not embed.color:
                embed.color = reskin.get("colors", {}).get("main") or functions.config_color("main")
            if embed.title and not embed.author and not self.command.qualified_name in ("nowplaying", "createembed"):
                embed.set_author(
                    name=self.author.display_name,
                    icon_url=self.author.display_avatar,
                )
            if embed.title:
                embed.title = functions.shorten(embed.title, 256)
            if embed.description:
                embed.description = functions.shorten(embed.description, 4096)
            for field in embed.fields:
                embed.set_field_at(
                    index=embed.fields.index(field),
                    name=field.name,
                    value=field.value[:1024],
                    inline=field.inline,
                )
            if hasattr(embed, "_attachments") and embed._attachments:
                for attachment in embed._attachments:
                    if isinstance(attachment, discord.File):
                        kwargs["files"].append(discord.File(copy(attachment.fp), filename=attachment.filename))
                    elif isinstance(attachment, tuple):
                        response = await self.bot.session.get(attachment[0])
                        if response.status == 200:
                            kwargs["files"].append(discord.File(io.BytesIO(await response.read()), filename=attachment[1]))

                # embed._attachments = []

        if embeds := kwargs.get("embeds"):
            for embed in embeds:
                if not embed.color:
                    embed.color = reskin.get("colors", {}).get("main") or functions.config_color("main")
                if embed.title and not embed.author and not self.command.qualified_name in ("nowplaying", "createembed"):
                    embed.set_author(
                        name=self.author.display_name,
                        icon_url=self.author.display_avatar,
                    )
                if embed.title:
                    embed.title = functions.shorten(embed.title, 256)
                if embed.description:
                    embed.description = functions.shorten(embed.description, 4096)
                for field in embed.fields:
                    embed.set_field_at(
                        index=embed.fields.index(field),
                        name=field.name,
                        value=field.value[:1024],
                        inline=field.inline,
                    )
                if hasattr(embed, "_attachments") and embed._attachments:
                    for attachment in embed._attachments:
                        if isinstance(attachment, discord.File):
                            kwargs["files"].append(discord.File(copy(attachment.fp), filename=attachment.filename))
                        elif isinstance(attachment, tuple):
                            response = await self._state._get_client().session.get(attachment[0])
                            if response.status == 200:
                                kwargs["files"].append(discord.File(io.BytesIO(await response.read()), filename=attachment[1]))

                    # embed._attachments = []

        if content := (args[0] if args else kwargs.get("content")):
            content = str(content)
            if len(content) > 4000:
                kwargs["content"] = f"Response too large to send (`{len(content)}/4000`)"
                kwargs["files"].append(
                    discord.File(
                        io.StringIO(content),
                        filename=f"wockResult.txt",
                    )
                )
                if args:
                    args = args[1:]

        # Override the send function with a webhook for reskin..
        if reskin:
            webhook = reskin["webhook"]
            kwargs["username"] = reskin["username"]
            kwargs["avatar_url"] = reskin["avatar_url"]
            kwargs["wait"] = True

            delete_after = kwargs.pop("delete_after", None)
            kwargs.pop("stickers", None)
            kwargs.pop("reference", None)
            kwargs.pop("followup", None)

            try:
                message = await webhook.send(*args, **kwargs)
            except discord.NotFound:
                reskin = await self.bot.db.fetch_config(self.guild.id, "reskin") or {}
                del reskin["webhooks"][str(self.channel.id)]
                await self.bot.db.update_config(self.guild.id, "reskin", reskin)
                await cache.delete_many(f"reskin:channel:{self.channel.id}", f"reskin:webhook:{self.channel.id}")
            except discord.HTTPException as error:
                raise error
            else:
                if delete_after:
                    await message.delete(delay=delete_after)

                return message

        return await super().send(*args, **kwargs)

        # if not self.command.qualified_name.startswith("jishaku"):
        #     if not self.sent_message:
        #         self.sent_message = await super().send(*args, **kwargs)
        #     else:
        #         await self.sent_message.edit(*args, **kwargs)
        # else:
        #     return await super().send(*args, **kwargs)

        # return self.sent_message

    async def reply(self, *args, **kwargs):
        kwargs["reference"] = self.message
        try:
            return await self.send(*args, **kwargs)
        except discord.HTTPException as error:
            if error.code == 50035:
                kwargs.pop("reference", None)
                return await self.send(*args, **kwargs)

    def typing(self) -> Typing:
        return Typing(self)

    async def check(self):
        return await self.send(content="👍🏾")

    async def react_check(self):
        return await self.message.add_reaction("✅")

    async def deny(self):
        return await self.send(content="👎🏾")

    async def react_deny(self):
        return await self.message.add_reaction("❌")

    async def prompt(self, message: str, **kwargs):
        view = views.ConfirmView(self)
        message = await self.warn(message, view=view, **kwargs)

        await view.wait()
        with contextlib.suppress(discord.HTTPException):
            await message.delete()

        if view.value is False:
            raise commands.UserInputError("Prompt was denied.")
        return view.value

    async def neutral(self, message: str, **kwargs):
        message = str(message)
        reskin = await self.reskin()
        color = reskin.get("colors", {}).get("main") or kwargs.pop("color", functions.config_color("main"))
        emoji = reskin.get("emojis", {}).get("main") or ""
        sign = "> " if not "\n>" in message or (self.command.qualified_name if self.command else "") in ("lastfm mode", "copyembed") else ""

        kwargs.pop("color", None)
        kwargs.pop("emoji", None)

        embed = discord.Embed(
            color=color,
            description=f"{sign}{emoji} {message}",
        )
        if kwargs.pop("reply", True):
            return await self.reply(embed=embed, **kwargs)
        else:
            return await self.send(embed=embed, **kwargs)

    async def approve(self, message: str, **kwargs):
        message = str(message)
        reskin = await self.reskin()
        color = reskin.get("colors", {}).get("approve") or kwargs.pop("color", functions.config_color("approve"))
        emoji = reskin.get("emojis", {}).get("approve") or ""
        sign = "> " if not "\n>" in message or (self.command.qualified_name if self.command else "") in ("lastfm mode", "copyembed") else ""

        kwargs.pop("color", None)
        kwargs.pop("emoji", None)

        embed = discord.Embed(
            color=color,
            description=f"{sign}{emoji} {message}",
        )
        if previous_load := getattr(self, "previous_load", None):
            cancel_load = kwargs.pop("cancel_load", False)
            result = await previous_load.edit(embed=embed, **kwargs)
            if cancel_load:
                delattr(self, "previous_load")
            return result
        else:
            return await self.reply(embed=embed, **kwargs)

    async def warn(self, message: str, **kwargs):
        message = str(message)
        reskin = await self.reskin()
        color = reskin.get("colors", {}).get("warn") or kwargs.pop("color", functions.config_color("warn"))
        emoji = reskin.get("emojis", {}).get("warn") or ""
        sign = "> " if not "\n>" in message or (self.command.qualified_name if self.command else "") in ("lastfm mode", "copyembed") else ""

        kwargs.pop("color", None)
        kwargs.pop("emoji", None)

        embed = discord.Embed(
            color=color,
            description=f"{sign}{emoji} {message}",
        )
        if previous_load := getattr(self, "previous_load", None):
            cancel_load = kwargs.pop("cancel_load", False)
            result = await previous_load.edit(embed=embed, **kwargs)
            if cancel_load:
                delattr(self, "previous_load")
            return result
        else:
            return await self.reply(embed=embed, **kwargs)

    async def search(self, message: str, **kwargs):
        message = str(message)
        reskin = await self.reskin()
        color = reskin.get("colors", {}).get("search") or kwargs.pop("color", functions.config_color("search"))
        emoji = reskin.get("emojis", {}).get("search") or ""
        sign = "> " if not "\n>" in message or (self.command.qualified_name if self.command else "") in ("lastfm mode", "copyembed") else ""

        kwargs.pop("color", None)
        kwargs.pop("emoji", None)

        embed = discord.Embed(
            color=color,
            description=f"{sign}{emoji} {message}",
        )
        return await self.reply(embed=embed, **kwargs)

    async def load(self, message: str, **kwargs):
        message = str(message)
        reskin = await self.reskin()
        color = reskin.get("colors", {}).get("load") or kwargs.pop("color", functions.config_color("load"))
        emoji = reskin.get("emojis", {}).get("load") or ""
        sign = "> " if not "\n>" in message or (self.command.qualified_name if self.command else "") in ("lastfm mode", "copyembed") else ""

        kwargs.pop("color", None)
        kwargs.pop("emoji", None)

        embed = discord.Embed(
            color=color,
            description=f"{sign}{emoji} {message}",
        )
        if not getattr(self, "previous_load", None):
            message = await self.reply(embed=embed, **kwargs)
            setattr(self, "previous_load", message)
            return self.previous_load
        else:
            await self.previous_load.edit(embed=embed, **kwargs)
            return self.previous_load

    async def paginate(self, entries: list[discord.Embed], **kwargs):
        if not entries:
            return await self.warn(f"No entries found for **{self.command.qualified_name}**")

        embed = None
        _total_entries = 0
        _max_entries: int = kwargs.pop("max_entries", 10)
        if isinstance(entries, discord.Embed):
            embed = entries
        elif isinstance(entries, list) and len(entries) == 1:
            embed = entries[0]
        if embed:
            if isinstance(embed.description, list):
                entries = list()
                _entries = list()
                _total_entries = len(embed.description)
                _counter: bool = kwargs.pop("counter", True)
                counter: int = 0
                for entry in embed.description:
                    if _counter:
                        counter += 1
                        _entries.append(f"`{counter}` {entry}")
                    else:
                        _entries.append(str(entry))
                    if len(_entries) == _max_entries:
                        _embed = embed.copy()
                        _embed.description = "\n".join(_entries)
                        entries.append(_embed)
                        _entries.clear()
                if _entries:
                    _embed = embed.copy()
                    _embed.description = "\n".join(_entries)
                    entries.append(_embed)
                elif len(entries) == 0:
                    return await self.warn(f"No entries found for **{self.command.qualified_name}**")
            else:
                _field = None
                for field in embed.fields:
                    if len(field.value) > 1024:
                        _field = (
                            field.name,
                            field.value.split("\n"),
                            field.inline,
                            embed.fields.index(field),
                        )
                if _field:
                    entries = list()
                    _temp = list()
                    for entry in _field[1]:
                        _temp.append(entry)
                        if len(_temp) == _max_entries:
                            _embed = discord.Embed(
                                color=embed.color,
                                title=embed.title,
                                description=embed.description,
                                url=embed.url,
                                timestamp=embed.timestamp,
                            )
                            if embed.author:
                                _embed.set_author(
                                    name=embed.author.name,
                                    url=embed.author.url,
                                    icon_url=embed.author.icon_url,
                                )
                            if embed.thumbnail:
                                _embed.set_thumbnail(url=embed.thumbnail.url)
                            if embed.image:
                                _embed.set_image(url=embed.image.url)
                            if embed.footer:
                                _embed.set_footer(
                                    text=embed.footer.text,
                                    icon_url=embed.footer.icon_url,
                                )
                            for field in embed.fields:
                                if field.name != _field[0]:
                                    _embed.add_field(
                                        name=field.name,
                                        value=field.value,
                                        inline=field.inline,
                                    )
                            _embed.add_field(
                                name=_field[0],
                                value="\n".join(_temp),
                                inline=_field[2],
                            )
                            entries.append(_embed)
                            _temp.clear()
                    if _temp:
                        _embed = discord.Embed(
                            color=embed.color,
                            title=embed.title,
                            description=embed.description,
                            url=embed.url,
                            timestamp=embed.timestamp,
                        )
                        if embed.author:
                            _embed.set_author(
                                name=embed.author.name,
                                url=embed.author.url,
                                icon_url=embed.author.icon_url,
                            )
                        if embed.thumbnail:
                            _embed.set_thumbnail(url=embed.thumbnail.url)
                        if embed.image:
                            _embed.set_image(url=embed.image.url)
                        if embed.footer:
                            _embed.set_footer(
                                text=embed.footer.text,
                                icon_url=embed.footer.icon_url,
                            )
                        for field in embed.fields:
                            if field.name != _field[0]:
                                _embed.add_field(
                                    name=field.name,
                                    value=field.value,
                                    inline=field.inline,
                                )
                        _embed.add_field(
                            name=_field[0],
                            value="\n".join(_temp),
                            inline=_field[2],
                        )
                        entries.append(_embed)

        if isinstance(entries, discord.Embed):
            entries = [entries]
        _entries = list()
        footer_override = kwargs.pop("footer_override", True)
        for entry in entries:
            if not entry.color:
                reskin = await self.reskin()
                color = reskin.get("colors", {}).get("main") or functions.config_color("main")
                entry.color = color
            if entry.title and not entry.author:
                entry.set_author(
                    name=self.author.display_name,
                    icon_url=self.author.display_avatar,
                )
            if entry.description:
                entry.description = entry.description[:4096]
            for field in entry.fields:
                entry.set_field_at(
                    index=entry.fields.index(field),
                    name=field.name,
                    value=field.value[:1024],
                    inline=field.inline,
                )
            if footer_override:
                if entry.footer:
                    entry.set_footer(
                        text=f"{entry.footer.text} ∙ Page {len(_entries) + 1} of {len(entries)}"
                        if entry.footer.text
                        else f"Page {len(_entries) + 1} of {len(entries)}",
                        icon_url=entry.footer.icon_url,
                    )
                else:
                    entry.set_footer(
                        text=f"Page {len(_entries) + 1} of {len(entries)}",
                    )
                if _total_entries:
                    entry.set_footer(
                        text=f"{entry.footer.text} ({functions.plural(_total_entries):entry|entries})",
                        icon_url=entry.footer.icon_url,
                    )
            _entries.append(entry)

        if len(_entries) == 1:
            return await self.send(embed=_entries[0], **kwargs)
        return await Paginator(self, _entries).execute()

    async def send_help(self):
        embed = discord.Embed(
            description=(
                f"{self.command.short_doc or ''}\n>>> ```bf\nSyntax: {self.prefix}{self.command.qualified_name} {self.command.usage or ''}\nExample:"
                f" {self.prefix}{self.command.qualified_name} {self.command.example or ''}\n```"
            ),
        )
        embed.set_author(name=self.command.cog_name or "No category", icon_url=self.bot.user.display_avatar, url=f"https://docs.wock.cloud")

        await self.send(embed=embed)

    def __repr__(self):
        return f"<helpers.wock.Context guild={self.guild.id} channel={self.channel.id} user={self.author.id}>"


class EmbedScript:
    def __init__(self, script: str):
        self.script: str = script
        self._script: str = script
        self._type: str = "text"
        self.parser: tagscript.Parser = tagscript.Parser()
        self.embed_parser: tagscript.FunctionParser = tagscript.Parser()
        self.objects: dict = dict(content=None, embed=discord.Embed(), embeds=list())

    async def resolve_variables(self, **kwargs):
        """Format the variables inside the script"""

        if guild := kwargs.get("guild"):
            self.script = (
                self.script.replace("{guild}", str(guild))
                .replace("{guild.id}", str(guild.id))
                .replace("{guild.name}", str(guild.name))
                .replace(
                    "{guild.icon}",
                    str(guild.icon or "https://cdn.discordapp.com/embed/avatars/1.png"),
                )
                .replace("{guild.banner}", str(guild.banner or "No banner"))
                .replace("{guild.splash}", str(guild.splash or "No splash"))
                .replace(
                    "{guild.discovery_splash}",
                    str(guild.discovery_splash or "No discovery splash"),
                )
                .replace("{guild.owner}", str(guild.owner))
                .replace("{guild.owner_id}", str(guild.owner_id))
                .replace("{guild.count}", str(humanize.comma(len(guild.members))))
                .replace("{guild.members}", str(humanize.comma(len(guild.members))))
                .replace("{len(guild.members)}", str(humanize.comma(len(guild.members))))
                .replace("{guild.channels}", str(humanize.comma(len(guild.channels))))
                .replace("{guild.channel_count}", str(humanize.comma(len(guild.channels))))
                .replace(
                    "{guild.category_channels}",
                    str(humanize.comma(len(guild.categories))),
                )
                .replace(
                    "{guild.category_channel_count}",
                    str(humanize.comma(len(guild.categories))),
                )
                .replace(
                    "{guild.text_channels}",
                    str(humanize.comma(len(guild.text_channels))),
                )
                .replace(
                    "{guild.text_channel_count}",
                    str(humanize.comma(len(guild.text_channels))),
                )
                .replace(
                    "{guild.voice_channels}",
                    str(humanize.comma(len(guild.voice_channels))),
                )
                .replace(
                    "{guild.voice_channel_count}",
                    str(humanize.comma(len(guild.voice_channels))),
                )
                .replace("{guild.roles}", str(humanize.comma(len(guild.roles))))
                .replace("{guild.role_count}", str(humanize.comma(len(guild.roles))))
                .replace("{guild.emojis}", str(humanize.comma(len(guild.emojis))))
                .replace("{guild.emoji_count}", str(humanize.comma(len(guild.emojis))))
                .replace(
                    "{guild.created_at}",
                    str(guild.created_at.strftime("%m/%d/%Y, %I:%M %p")),
                )
                .replace("{unix(guild.created_at)}", str(guild.created_at.timestamp()))
            )
        if channel := kwargs.get("channel"):
            if isinstance(channel, discord.TextChannel):
                self.script = (
                    self.script.replace("{channel}", str(channel))
                    .replace("{channel.id}", str(channel.id))
                    .replace("{channel.mention}", str(channel.mention))
                    .replace("{channel.name}", str(channel.name))
                    .replace("{channel.topic}", str(channel.topic))
                    .replace("{channel.created_at}", str(channel.created_at))
                    .replace(
                        "{channel.created_at}",
                        str(channel.created_at.strftime("%m/%d/%Y, %I:%M %p")),
                    )
                    .replace(
                        "{unix(channel.created_at)}",
                        str(int(channel.created_at.timestamp())),
                    )
                )
        if role := kwargs.get("role"):
            self.script = (
                self.script.replace("{role}", str(role))
                .replace("{role.id}", str(role.id))
                .replace("{role.mention}", str(role.mention))
                .replace("{role.name}", str(role.name))
                .replace("{role.color}", str(role.color))
                .replace("{role.created_at}", str(role.created_at))
                .replace(
                    "{role.created_at}",
                    str(role.created_at.strftime("%m/%d/%Y, %I:%M %p")),
                )
                .replace("{unix(role.created_at)}", str(int(role.created_at.timestamp())))
            )
        if roles := kwargs.get("roles"):
            self.script = self.script.replace("{roles}", " ".join([str(role) for role in roles]))
        if user := kwargs.get("user"):
            self.script = self.script.replace("{member", "{user")
            self.script = (
                self.script.replace("{user}", str(user))
                .replace("{user.id}", str(user.id))
                .replace("{user.mention}", str(user.mention))
                .replace("{user.name}", str(user.name))
                .replace("{user.tag}", str(user.discriminator))
                .replace("{user.bot}", "Yes" if user.bot else "No")
                .replace("{user.color}", str(user.color))
                .replace("{user.avatar}", str(user.display_avatar))
                .replace("{user.nickname}", str(user.display_name))
                .replace("{user.nick}", str(user.display_name))
                .replace(
                    "{user.created_at}",
                    str(user.created_at.strftime("%m/%d/%Y, %I:%M %p")),
                )
                .replace("{unix(user.created_at)}", str(int(user.created_at.timestamp())))
            )
            if isinstance(user, discord.Member):
                self.script = (
                    self.script.replace(
                        "{user.joined_at}",
                        str(user.joined_at.strftime("%m/%d/%Y, %I:%M %p")),
                    )
                    .replace("{unix(user.joined_at)}", str(int(user.joined_at.timestamp())))
                    .replace("{user.join_position}", str(user.join_position))
                    .replace(
                        "{suffix(user.join_position)}",
                        str(humanize.ordinal(user.join_position)),
                    )
                    .replace("{user.boost}", "Yes" if user.premium_since else "No")
                    .replace(
                        "{user.boosted_at}",
                        str(user.premium_since.strftime("%m/%d/%Y, %I:%M %p")) if user.premium_since else "Never",
                    )
                    .replace(
                        "{unix(user.boosted_at)}",
                        str(int(user.premium_since.timestamp())) if user.premium_since else "Never",
                    )
                    .replace(
                        "{user.boost_since}",
                        str(user.premium_since.strftime("%m/%d/%Y, %I:%M %p")) if user.premium_since else "Never",
                    )
                    .replace(
                        "{unix(user.boost_since)}",
                        str(int(user.premium_since.timestamp())) if user.premium_since else "Never",
                    )
                )
        if moderator := kwargs.get("moderator"):
            self.script = (
                self.script.replace("{moderator}", str(moderator))
                .replace("{moderator.id}", str(moderator.id))
                .replace("{moderator.mention}", str(moderator.mention))
                .replace("{moderator.name}", str(moderator.name))
                .replace("{moderator.tag}", str(moderator.discriminator))
                .replace("{moderator.bot}", "Yes" if moderator.bot else "No")
                .replace("{moderator.color}", str(moderator.color))
                .replace("{moderator.avatar}", str(moderator.display_avatar))
                .replace("{moderator.nickname}", str(moderator.display_name))
                .replace("{moderator.nick}", str(moderator.display_name))
                .replace(
                    "{moderator.created_at}",
                    str(moderator.created_at.strftime("%m/%d/%Y, %I:%M %p")),
                )
                .replace(
                    "{unix(moderator.created_at)}",
                    str(int(moderator.created_at.timestamp())),
                )
            )
            if isinstance(moderator, discord.Member):
                self.script = (
                    self.script.replace(
                        "{moderator.joined_at}",
                        str(moderator.joined_at.strftime("%m/%d/%Y, %I:%M %p")),
                    )
                    .replace(
                        "{unix(moderator.joined_at)}",
                        str(int(moderator.joined_at.timestamp())),
                    )
                    .replace("{moderator.join_position}", str(moderator.join_position))
                    .replace(
                        "{suffix(moderator.join_position)}",
                        str(humanize.ordinal(moderator.join_position)),
                    )
                    .replace("{moderator.boost}", "Yes" if moderator.premium_since else "No")
                    .replace(
                        "{moderator.boosted_at}",
                        str(moderator.premium_since.strftime("%m/%d/%Y, %I:%M %p")) if moderator.premium_since else "Never",
                    )
                    .replace(
                        "{unix(moderator.boosted_at)}",
                        str(int(moderator.premium_since.timestamp())) if moderator.premium_since else "Never",
                    )
                    .replace(
                        "{moderator.boost_since}",
                        str(moderator.premium_since.strftime("%m/%d/%Y, %I:%M %p")) if moderator.premium_since else "Never",
                    )
                    .replace(
                        "{unix(moderator.boost_since)}",
                        str(int(moderator.premium_since.timestamp())) if moderator.premium_since else "Never",
                    )
                )
        if case_id := kwargs.get("case_id"):
            self.script = self.script.replace("{case.id}", str(case_id)).replace("{case}", str(case_id)).replace("{case_id}", str(case_id))
        if reason := kwargs.get("reason"):
            self.script = self.script.replace("{reason}", str(reason))
        if duration := kwargs.get("duration"):
            self.script = self.script.replace("{duration}", str(duration))
        if image := kwargs.get("image"):
            self.script = self.script.replace("{image}", str(image))
        if option := kwargs.get("option"):
            self.script = self.script.replace("{option}", str(option))
        if text := kwargs.get("text"):
            self.script = self.script.replace("{text}", str(text))
        if emoji := kwargs.get("emoji"):
            self.script = (
                self.script.replace("{emoji}", str(emoji))
                .replace("{emoji.id}", str(emoji.id))
                .replace("{emoji.name}", str(emoji.name))
                .replace("{emoji.animated}", "Yes" if emoji.animated else "No")
                .replace("{emoji.url}", str(emoji.url))
            )
        if emojis := kwargs.get("emojis"):
            self.script = self.script.replace("{emojis}", str(emojis))
        if sticker := kwargs.get("sticker"):
            self.script = (
                self.script.replace("{sticker}", str(sticker))
                .replace("{sticker.id}", str(sticker.id))
                .replace("{sticker.name}", str(sticker.name))
                .replace("{sticker.animated}", "Yes" if sticker.animated else "No")
                .replace("{sticker.url}", str(sticker.url))
            )
        if color := kwargs.get("color"):
            self.script = self.script.replace("{color}", str(color)).replace("{colour}", str(color))
        if name := kwargs.get("name"):
            self.script = self.script.replace("{name}", str(name))
        if "hoist" in kwargs:
            hoist = kwargs.get("hoist")
            self.script = self.script.replace("{hoisted}", "Yes" if hoist else "No")
            self.script = self.script.replace("{hoist}", "Yes" if hoist else "No")
        if "mentionable" in kwargs:
            mentionable = kwargs.get("mentionable")
            self.script = self.script.replace("{mentionable}", "Yes" if mentionable else "No")
        if lastfm := kwargs.get("lastfm"):
            self.script = (
                self.script.replace("{lastfm}", lastfm["user"]["username"])
                .replace("{lastfm.name}", lastfm["user"]["username"])
                .replace("{lastfm.url}", lastfm["user"]["url"])
                .replace("{lastfm.avatar}", lastfm["user"]["avatar"] or "")
                .replace(
                    "{lastfm.plays}",
                    humanize.comma(lastfm["user"]["library"]["scrobbles"]),
                )
                .replace(
                    "{lastfm.scrobbles}",
                    humanize.comma(lastfm["user"]["library"]["scrobbles"]),
                )
                .replace(
                    "{lastfm.library}",
                    humanize.comma(lastfm["user"]["library"]["scrobbles"]),
                )
                .replace(
                    "{lastfm.library.artists}",
                    humanize.comma(lastfm["user"]["library"]["artists"]),
                )
                .replace(
                    "{lastfm.library.albums}",
                    humanize.comma(lastfm["user"]["library"]["albums"]),
                )
                .replace(
                    "{lastfm.library.tracks}",
                    humanize.comma(lastfm["user"]["library"]["tracks"]),
                )
                .replace("{artist}", discord.utils.escape_markdown(lastfm["artist"]["name"]))
                .replace("{artist.name}", discord.utils.escape_markdown(lastfm["artist"]["name"]))
                .replace("{artist.url}", lastfm["artist"]["url"])
                .replace("{artist.image}", lastfm["artist"]["image"] or "")
                .replace("{artist.plays}", humanize.comma(lastfm["artist"]["plays"]))
                .replace(
                    "{artist.spotify.url}",
                    lastfm["spotify"]["artist"] if lastfm.get("spotify") else lastfm["url"],
                )
                .replace(
                    "{artist.spotify_url}",
                    lastfm["spotify"]["artist"] if lastfm.get("spotify") else lastfm["url"],
                )
                .replace("{album}", discord.utils.escape_markdown(lastfm["album"]["name"]) if lastfm.get("album") else "")
                .replace("{album.name}", discord.utils.escape_markdown(lastfm["album"]["name"]) if lastfm.get("album") else "")
                .replace("{album.url}", lastfm["album"]["url"] if lastfm.get("album") else "")
                .replace(
                    "{album.image}",
                    (lastfm["album"]["image"] or "") if lastfm.get("album") else "",
                )
                .replace(
                    "{album.cover}",
                    (lastfm["album"]["image"] or "") if lastfm.get("album") else "",
                )
                .replace(
                    "{album.plays}",
                    humanize.comma(lastfm["album"]["plays"]) if lastfm.get("album") else "",
                )
                .replace("{track}", discord.utils.escape_markdown(lastfm["name"]))
                .replace("{track.name}", discord.utils.escape_markdown(lastfm["name"]))
                .replace("{track.url}", lastfm["url"])
                .replace("{track.image}", lastfm["image"]["url"] if lastfm["image"] else "")
                .replace("{track.cover}", lastfm["image"]["url"] if lastfm["image"] else "")
                .replace(
                    "{track.color}",
                    lastfm["image"]["palette"] if lastfm["image"] else "",
                )
                .replace(
                    "{track.palette}",
                    lastfm["image"]["palette"] if lastfm["image"] else "",
                )
                .replace(
                    "{track.spotify.url}",
                    lastfm["spotify"]["track"] if lastfm.get("spotify") else lastfm["url"],
                )
                .replace(
                    "{track.spotify_url}",
                    lastfm["spotify"]["track"] if lastfm.get("spotify") else lastfm["url"],
                )
                .replace(
                    "{track.duration}",
                    lastfm["spotify"]["duration"] if lastfm.get("spotify") else "02:37",
                )
                .replace("{track.plays}", humanize.comma(lastfm["plays"]))
                .replace("{lower(artist)}", discord.utils.escape_markdown(lastfm["artist"]["name"].lower()))
                .replace("{lower(artist.name)}", discord.utils.escape_markdown(lastfm["artist"]["name"].lower()))
                .replace(
                    "{lower(album)}",
                    discord.utils.escape_markdown(lastfm["album"]["name"].lower()) if lastfm.get("album") else "",
                )
                .replace(
                    "{lower(album.name)}",
                    discord.utils.escape_markdown(lastfm["album"]["name"].lower()) if lastfm.get("album") else "",
                )
                .replace("{lower(track)}", discord.utils.escape_markdown(lastfm["name"].lower()))
                .replace("{lower(track.name)}", discord.utils.escape_markdown(lastfm["name"].lower()))
                .replace("{upper(artist)}", discord.utils.escape_markdown(lastfm["artist"]["name"].upper()))
                .replace("{upper(artist.name)}", discord.utils.escape_markdown(lastfm["artist"]["name"].upper()))
                .replace(
                    "{upper(album)}",
                    discord.utils.escape_markdown(lastfm["album"]["name"].upper()) if lastfm.get("album") else "",
                )
                .replace(
                    "{upper(album.name)}",
                    discord.utils.escape_markdown(lastfm["album"]["name"].upper()) if lastfm.get("album") else "",
                )
                .replace("{upper(track)}", discord.utils.escape_markdown(lastfm["name"].upper()))
                .replace("{upper(track.name)}", discord.utils.escape_markdown(lastfm["name"].upper()))
                .replace("{title(artist)}", discord.utils.escape_markdown(lastfm["artist"]["name"].title()))
                .replace("{title(artist.name)}", discord.utils.escape_markdown(lastfm["artist"]["name"].title()))
                .replace(
                    "{title(album)}",
                    discord.utils.escape_markdown(lastfm["album"]["name"].title()) if lastfm.get("album") else "",
                )
                .replace(
                    "{title(album.name)}",
                    discord.utils.escape_markdown(lastfm["album"]["name"].title()) if lastfm.get("album") else "",
                )
                .replace("{title(track)}", discord.utils.escape_markdown(lastfm["name"].title()))
                .replace("{title(track.name)}", discord.utils.escape_markdown(lastfm["name"].title()))
            )
            if lastfm["artist"].get("crown"):
                self.script = self.script.replace("{artist.crown}", "👑")
            else:
                self.script = self.script.replace("`{artist.crown}`", "").replace("{artist.crown}", "")
        if youtube := kwargs.get("youtube"):
            self.script = (
                self.script.replace("{youtube}", youtube["title"])
                .replace("{youtube.title}", youtube["title"])
                .replace("{youtube.url}", youtube["url"])
                .replace("{youtube.id}", youtube["id"])
                # .replace("{youtube.thumbnail}", youtube["thumbnail"])
                .replace("{youtube.channel}", youtube["channel"]["name"])
                .replace("{youtube.channel.name}", youtube["channel"]["name"])
                .replace("{youtube.channel.url}", youtube["channel"]["url"])
                .replace("{youtube.channel.id}", youtube["channel"]["id"])
            )

        return self.script

    async def resolve_objects(self, **kwargs):
        """Attempt to resolve the objects in the script"""

        # Initialize the parser methods

        if not self.parser.tags:

            @self.parser.method(
                name="lower",
                usage="(value)",
                aliases=["lowercase", "lowercase"],
            )
            async def lower(_: None, value: str):
                """Convert the value to lowercase"""

                return value.lower()

            @self.parser.method(
                name="upper",
                usage="(value)",
                aliases=["uppercase", "uppercase"],
            )
            async def upper(_: None, value: str):
                """Convert the value to uppercase"""

                return value.upper()

            @self.parser.method(
                name="quote",
                usage="(value)",
                aliases=["http"],
            )
            async def quote(_: None, value: str):
                """Format the value for a URL"""

                return functions.format_uri(value)

            @self.parser.method(
                name="len",
                usage="(value)",
                aliases=["length", "size", "count"],
            )
            async def length(_: None, value: str):
                """Get the length of the value"""

                if ", " in value:
                    return len(value.split(", "))
                elif "," in value:
                    value = value.replace(",", "")
                    if value.isnumeric():
                        return int(value)
                return len(value)

            @self.parser.method(
                name="strip",
                usage="(text) (removal)",
                aliases=["remove"],
            )
            async def _strip(_: None, text: str, removal: str):
                """Remove a value from text"""

                return text.replace(removal, "")

            @self.parser.method(
                name="random",
                usage="(items)",
                aliases=["choose", "choice"],
            )
            async def _random(_: None, *items):
                """Chooses a random item"""

                return random.choice(items)

            @self.parser.method(
                name="if",
                usage="(condition) (value if true) (value if false)",
                aliases=["%"],
            )
            async def if_statement(_: None, condition, output, err=""):
                """If the condition is true, return the output, else return the error"""

                condition, output, err = str(condition), str(output), str(err)
                if output.startswith("{") and not output.endswith("}"):
                    output += "}"
                if err.startswith("{") and not err.endswith("}"):
                    err += "}"

                if "==" in condition:
                    condition = condition.split("==")
                    if condition[0].lower().strip() == condition[1].lower().strip():
                        return output
                    else:
                        return err
                elif "!=" in condition:
                    condition = condition.split("!=")
                    if condition[0].lower().strip() != condition[1].lower().strip():
                        return output
                    else:
                        return err
                elif ">=" in condition:
                    condition = condition.split(">=")
                    if "," in condition[0]:
                        condition[0] = condition[0].replace(",", "")
                    if "," in condition[1]:
                        condition[1] = condition[1].replace(",", "")
                    if int(condition[0].strip()) >= int(condition[1].strip()):
                        return output
                    else:
                        return err
                elif "<=" in condition:
                    condition = condition.split("<=")
                    if "," in condition[0]:
                        condition[0] = condition[0].replace(",", "")
                    if "," in condition[1]:
                        condition[1] = condition[1].replace(",", "")
                    if int(condition[0].strip()) <= int(condition[1].strip()):
                        return output
                    else:
                        return err
                elif ">" in condition:
                    condition = condition.split(">")
                    if "," in condition[0]:
                        condition[0] = condition[0].replace(",", "")
                    if "," in condition[1]:
                        condition[1] = condition[1].replace(",", "")
                    if int(condition[0].strip()) > int(condition[1].strip()):
                        return output
                    else:
                        return err
                elif "<" in condition:
                    condition = condition.split("<")
                    if "," in condition[0]:
                        condition[0] = condition[0].replace(",", "")
                    if "," in condition[1]:
                        condition[1] = condition[1].replace(",", "")
                    if int(condition[0].strip()) < int(condition[1]).strip():
                        return output
                    else:
                        return err
                else:
                    if not condition.lower().strip() in (
                        "null",
                        "no",
                        "false",
                        "none",
                        "",
                    ):
                        return output
                    else:
                        return err

            @self.parser.method(
                name="message",
                usage="(value)",
                aliases=["content", "msg"],
            )
            async def message(_: None, value: str):
                """Set the message content"""

                self.objects["content"] = value

            @self.embed_parser.method(
                name="color",
                usage="(value)",
                aliases=["colour", "c"],
            )
            async def embed_color(_: None, value: str):
                """Set the color of the embed"""

                self.objects["embed"].color = functions.get_color(value)

            @self.embed_parser.method(
                name="author",
                usage="(name) <icon url> <url>",
                aliases=["a"],
            )
            async def embed_author(_: None, name: str, icon_url: str = None, url: str = None):
                """Set the author of the embed"""

                if str(icon_url).lower() in (
                    "off",
                    "no",
                    "none",
                    "null",
                    "false",
                    "disable",
                ):
                    icon_url = None
                elif match := regex.URL.match(str(icon_url)) and not regex.IMAGE_URL.match(str(icon_url)):
                    icon_url = None
                    url = match.group()

                self.objects["embed"].set_author(name=name, icon_url=icon_url, url=url)

            @self.embed_parser.method(
                name="url",
                usage="(value)",
                aliases=["uri", "u"],
            )
            async def embed_url(_: None, value: str):
                """Set the url of the embed"""

                self.objects["embed"].url = value

            @self.embed_parser.method(name="title", usage="(value)", aliases=["t"])
            async def embed_title(_: None, value: str):
                """Set the title of the embed"""

                self.objects["embed"].title = value

            @self.embed_parser.method(name="description", usage="(value)", aliases=["desc", "d"])
            async def embed_description(_: None, value: str):
                """Set the description of the embed"""

                self.objects["embed"].description = value

            @self.embed_parser.method(name="field", usage="(name) (value) <inline>", aliases=["f"])
            async def embed_field(_: None, name: str, value: str, inline: bool = True):
                """Add a field to the embed"""

                self.objects["embed"].add_field(name=name, value=value, inline=inline)

            @self.embed_parser.method(
                name="thumbnail",
                usage="(url)",
                aliases=["thumb", "t"],
            )
            async def embed_thumbnail(_: None, url: str = None):
                """Set the thumbnail of the embed"""

                self.objects["embed"].set_thumbnail(url=url)

            @self.embed_parser.method(
                name="image",
                usage="(url)",
                aliases=["img", "i"],
            )
            async def embed_image(_: None, url: str = None):
                """Set the image of the embed"""

                self.objects["embed"].set_image(url=url)

            @self.embed_parser.method(
                name="footer",
                usage="(text) <icon url>",
                aliases=["f"],
            )
            async def embed_footer(_: None, text: str, icon_url: str = None):
                """Set the footer of the embed"""

                self.objects["embed"].set_footer(text=text, icon_url=icon_url)

            @self.embed_parser.method(
                name="timestamp",
                usage="(value)",
                aliases=["t"],
            )
            async def embed_timestamp(_: None, value: str = "now"):
                """Set the timestamp of the embed"""

                if value.lower() in ("now", "current", "today", "now"):
                    self.objects["embed"].timestamp = discord.utils.utcnow()
                else:
                    self.objects["embed"].timestamp = functions.get_timestamp(value)

    async def compile(self, **kwargs):
        """Attempt to compile the script into an object"""

        await self.resolve_variables(**kwargs)
        await self.resolve_objects(**kwargs)
        try:
            self.script = await self.parser.parse(self.script)
            for script in self.script.split("{embed}"):
                if script := script.strip():
                    self.objects["embed"] = discord.Embed()
                    await self.embed_parser.parse(script)
                    # if result := str(result).strip():
                    #     self.objects["content"] = result
                    if embed := self.objects.pop("embed", None):
                        self.objects["embeds"].append(embed)
            self.objects.pop("embed", None)
        except Exception as error:
            if kwargs.get("validate"):
                if type(error) == TypeError:
                    function = [tag for tag in self.embed_parser.tags if tag.callback.__name__ == error.args[0].split("(")[0]][0].name
                    parameters = str(error).split("'")[1].split(", ")
                    raise commands.CommandError(f"The **{function}** method requires the `{parameters[0]}` parameter")
                else:
                    raise error

        validation = any(self.objects.values())
        if not validation:
            self.objects["content"] = self.script
        if kwargs.get("validate"):
            if self.objects.get("embeds"):
                self._type = "embed"
            self.objects: dict = dict(content=None, embeds=list(), stickers=list())
            self.script = self._script
        return validation

    async def send(self, bound: discord.TextChannel, **kwargs):
        """Attempt to send the embed to the channel"""

        # Attempt to compile the script
        compiled = await self.compile(**kwargs)
        if not compiled:
            if not self.script:
                self.objects["content"] = self.script
        if embed := self.objects.pop("embed", None):
            self.objects["embeds"].append(embed)

        if delete_after := kwargs.get("delete_after"):
            self.objects["delete_after"] = delete_after
        if allowed_mentions := kwargs.get("allowed_mentions"):
            self.objects["allowed_mentions"] = allowed_mentions
        if reference := kwargs.get("reference"):
            self.objects["reference"] = reference
        if isinstance(bound, discord.Webhook) and (ephemeral := kwargs.get("ephemeral")):
            self.objects["ephemeral"] = ephemeral

        return await getattr(bound, ("send" if not isinstance(bound, discord.Message) else "edit"))(
            **self.objects,
        )

    def replace(self, key: str, value: str):
        """Replace a key word in the script"""

        self.script = self.script.replace(key, value)
        return self

    def strip(self):
        """Strip the script"""

        self.script = self.script.strip()
        return self

    def type(self, suffix: bool = True, bold: bool = True):
        """Return the script type"""

        if self._type == "embed":
            return "embed" if not suffix else "an **embed message**" if bold else "an embed"
        else:
            return "text" if not suffix else "a **text message**" if bold else "a text"

    def __str__(self):
        return self.script

    def __repr__(self):
        return f"<helpers.wock.EmbedScript length={len(self.script)}>"


class EmbedScriptValidator(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        script = EmbedScript(str(argument))
        await script.compile(validate=True)
        return script


class Color(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)

        if ctx.command.qualified_name in ("lastfm color"):
            if argument.lower() in ("dominant", "dom"):
                return "dominant"
            elif argument.lower() in ("remove", "reset", "clear", "default", "none"):
                return "remove"

        if argument.lower() in ("random", "rand", "r"):
            return discord.Color.random()
        elif argument.lower() in ("invisible", "invis"):
            return discord.Color.from_str("#2F3136")

        if color := functions.get_color(argument):
            return color
        else:
            raise commands.CommandError(f"Color **{argument}** not found")


class SynthEngine(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        voices = dict(
            male="en_au_002",
            ghostface="en_us_ghostface",
            chewbacca="en_us_chewbacca",
            stormtrooper="en_us_stormtrooper",
            stitch="en_us_stitch",
            narrator="en_male_narration",
            peaceful="en_female_emotional",
            glorious="en_female_ht_f08_glorious",
            chipmunk="en_male_m2_xhxs_m03_silly",
            chipmunks="en_male_m2_xhxs_m03_silly",
        )
        if voice := voices.get(argument.lower()):
            return voice
        else:
            raise commands.CommandError(f"Synth engine **{argument}** not found")


class Language(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        if language := functions.get_language(argument):
            return language
        else:
            raise commands.CommandError(f"Language **{argument}** not found")


class ChartSize(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        if not "x" in argument:
            raise commands.CommandError("Collage size **incorrectly formatted** - example: `6x6`")
        if not len(argument.split("x")) == 2:
            raise commands.CommandError("Collage size **incorrectly formatted** - example: `6x6`")
        row, col = argument.split("x")
        if not row.isdigit() or not col.isdigit():
            raise commands.CommandError("Collage size **incorrectly formatted** - example: `6x6`")
        if (int(row) + int(col)) < 2:
            raise commands.CommandError("Collage size **too small**\n> Minimum size is `1x1`")
        elif (int(row) + int(col)) > 20:
            raise commands.CommandError("Collage size **too large**\n> Maximum size is `10x10`")

        return row + "x" + col


class YouTubeChannel(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument).split("--", 1)[0].strip()
        if match := regex.YOUTUBE_CHANNEL_URL.match(argument):
            if "@" in match.group():
                argument = f"@{match.group('id')}"
            else:
                argument = match.group()
        else:
            argument = f"@{argument}"
        argument = argument.strip()

        async with ctx.typing():
            response = await ctx.bot.session.get(
                "https://dev.wock.cloud/youtube/search",
                params=dict(query=argument, channel="1"),
                headers=dict(
                    Authorization=ctx.bot.config["api"].get("wock"),
                ),
            )
            data = await response.json()

            if not data.get("results"):
                raise commands.CommandError(f"Channel **{argument}** not found")

        return data["results"][0]


class Location(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        async with ctx.typing():
            response = await ctx.bot.session.get(
                "https://api.weatherapi.com/v1/timezone.json",
                params=dict(key=config["api"].get("weather"), q=argument),
            )

            if response.status == 200:
                data = await response.json()
                return data.get("location")
            else:
                raise commands.CommandError(f"Location **{argument}** not found")


class State(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        if argument.lower() in ("on", "yes", "true", "enable"):
            return True
        elif argument.lower() in ("off", "no", "none", "null", "false", "disable"):
            return False
        else:
            raise commands.CommandError("Please **specify** a valid state - `on` or `off`")


class Percentage(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        if argument.isdigit():
            argument = int(argument)
        elif match := regex.PERCENTAGE.match(argument):
            argument = int(match.group("percentage"))
        else:
            argument = 0

        if argument < 0 or argument > 100:
            raise commands.CommandError("Please **specify** a valid percentage")

        return argument


class Bitrate(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        if argument.isdigit():
            argument = int(argument)
        elif match := regex.BITRATE.match(argument):
            argument = int(match.group("bitrate"))
        else:
            argument = 0

        if argument < 0:
            raise commands.CommandError("Please **specify** a valid bitrate")
        elif argument > int(ctx.guild.bitrate_limit / 1000):
            raise commands.CommandError(f"Bitrate `{argument}kbps` is too high for this server")

        return argument


class Region(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        regions = {
            "automatic": "automatic",
            "auto": "automatic",
            "brazil": "brazil",
            "hongkong": "hongkong",
            "india": "india",
            "japan": "japan",
            "russia": "russia",
            "singapore": "singapore",
            "southafrica": "southafrica",
            "southkorea": "southkorea",
            "sydney": "sydney",
            "america": "us-central",
            "usa": "us-central",
            "us": "us-central",
            "americaeast": "us-east",
            "usaeast": "us-east",
            "useast": "us-east",
            "americawest": "us-west",
            "usawest": "us-west",
            "uswest": "us-west",
            "americasouth": "us-south",
            "usasouth": "us-south",
            "ussouth": "us-south",
            "na": "us-central",
            "nae": "us-east",
            "naw": "us-west",
            "nas": "us-south",
        }
        if region := regions.get((argument.lower().replace(" ", ""))):
            return region if region != "automatic" else None
        else:
            raise commands.CommandError(f"Region **{argument}** not found")


class Time:
    def __init__(self, seconds: int):
        self.seconds: int = seconds
        self.minutes: int = (self.seconds % 3600) // 60
        self.hours: int = (self.seconds % 86400) // 3600
        self.days: int = self.seconds // 86400
        self.weeks: int = self.days // 7
        self.delta: timedelta = timedelta(seconds=self.seconds)

    def __str__(self):
        return humanize.time(self.delta)


class TimeConverter(commands.Converter):
    def _convert(self, argument: str):
        argument = str(argument)
        units = dict(
            s=1,
            m=60,
            h=3600,
            d=86400,
            w=604800,
        )
        if matches := regex.TIME.findall(argument):
            seconds = 0
            for time, unit in matches:
                try:
                    seconds += units[unit] * int(time)
                except KeyError:
                    raise commands.CommandError(f"Invalid time unit `{unit}`")

            return seconds

    async def convert(self, ctx: Context, argument: str):
        if seconds := self._convert(argument):
            return Time(seconds)
        else:
            raise commands.CommandError("Please **specify** a valid time - `1h 30m`")


class Emoji:
    def __init__(self, name: str, url: str, **kwargs):
        self.name: str = name
        self.url: str = url
        self.id: int = int(kwargs.get("id", 0))
        self.animated: bool = kwargs.get("animated", False)

    async def read(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                return await response.read()

    def __str__(self):
        if self.id:
            return f"<{'a' if self.animated else ''}:{self.name}:{self.id}>"
        else:
            return self.name

    def __repr__(self):
        return f"<helpers.wock.Emoji name={self.name!r} url={self.url!r}>"


class EmojiFinder(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        if match := regex.DISCORD_EMOJI.match(argument):
            return Emoji(
                match.group("name"),
                "https://cdn.discordapp.com/emojis/" + match.group("id") + (".gif" if match.group("animated") else ".png"),
                id=int(match.group("id")),
                animated=bool(match.group("animated")),
            )
        else:
            characters = list()
            for character in argument:
                characters.append(str(hex(ord(character)))[2:])
            if len(characters) == 2:
                if "fe0f" in characters:
                    characters.remove("fe0f")
            if "20e3" in characters:
                characters.remove("20e3")

            hexcode = "-".join(characters)
            url = "https://cdn.notsobot.com/twemoji/512x512/" + hexcode + ".png"
            response = await ctx.bot.session.get(url)
            if response.status == 200:
                return Emoji(argument, url)

        raise commands.EmojiNotFound(argument)


class StickerFinder(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        try:
            message = await commands.MessageConverter().convert(ctx, argument)
        except commands.MessageNotFound:
            pass
        else:
            if message.stickers:
                sticker = await message.stickers[0].fetch()
                if isinstance(sticker, discord.StandardSticker):
                    raise commands.CommandError("Sticker **must** be a nitro sticker")
                return sticker
            else:
                raise commands.CommandError(f"[**Message**]({message.jump_url}) doesn't contain a sticker")

        sticker = discord.utils.get(ctx.guild.stickers, name=argument)
        if not sticker:
            raise commands.CommandError("That **sticker** doesn't exist in this server")
        return sticker

    async def search(ctx: Context):
        if ctx.message.stickers:
            sticker = await ctx.message.stickers[0].fetch()
        elif ctx.replied_message:
            if ctx.replied_message.stickers:
                sticker = await ctx.replied_message.stickers[0].fetch()
            else:
                raise commands.CommandError(f"[**Message**]({ctx.replied_message.jump_url}) doesn't contain a sticker")
        else:
            raise commands.CommandError("Please **specify** a sticker")

        if isinstance(sticker, discord.StandardSticker):
            raise commands.CommandError("Sticker **must** be a nitro sticker")
        return sticker


class ImageFinder(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        try:
            member = await Member().convert(ctx, argument)
            if member:
                return member.display_avatar.url
        except:
            pass

        if match := regex.DISCORD_ATTACHMENT.match(argument):
            if not match.group("mime") in ("png", "jpg", "jpeg", "webp", "gif"):
                raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
            return match.group()
        elif match := regex.IMAGE_URL.match(argument):
            return "https://proxy.wock.cloud?url=" + match.group()
        else:
            raise commands.CommandError(f"Couldn't find an **image**")

    async def search(ctx: Context, history: bool = True):
        if message := ctx.replied_message:
            for attachment in message.attachments:
                if attachment.content_type.split("/", 1)[1] in (
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                    "gif",
                ):
                    return attachment.url
            for embed in message.embeds:
                if image := embed.image:
                    if match := regex.DISCORD_ATTACHMENT.match(image.url):
                        if not match.group("mime") in (
                            "png",
                            "jpg",
                            "jpeg",
                            "webp",
                            "gif",
                        ):
                            raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
                        return match.group()
                    elif match := regex.IMAGE_URL.match(image.url):
                        return "https://proxy.wock.cloud?url=" + match.group()
                elif thumbnail := embed.thumbnail:
                    if match := regex.DISCORD_ATTACHMENT.match(thumbnail.url):
                        if not match.group("mime") in (
                            "png",
                            "jpg",
                            "jpeg",
                            "webp",
                            "gif",
                        ):
                            raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
                        return match.group()
                    elif match := regex.IMAGE_URL.match(thumbnail.url):
                        return "https://proxy.wock.cloud?url=" + match.group()

        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if attachment.content_type.split("/", 1)[1] in (
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                    "gif",
                ):
                    return attachment.url

        if history:
            async for message in ctx.channel.history(limit=50):
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.content_type.split("/", 1)[1] in (
                            "png",
                            "jpg",
                            "jpeg",
                            "webp",
                            "gif",
                        ):
                            return attachment.url
                if message.embeds:
                    for embed in message.embeds:
                        if image := embed.image:
                            if match := regex.DISCORD_ATTACHMENT.match(image.url):
                                if not match.group("mime") in (
                                    "png",
                                    "jpg",
                                    "jpeg",
                                    "webp",
                                    "gif",
                                ):
                                    raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
                                return match.group()
                            elif match := regex.IMAGE_URL.match(image.url):
                                return "https://proxy.wock.cloud?url=" + match.group()
                        elif thumbnail := embed.thumbnail:
                            if match := regex.DISCORD_ATTACHMENT.match(thumbnail.url):
                                if not match.group("mime") in (
                                    "png",
                                    "jpg",
                                    "jpeg",
                                    "webp",
                                    "gif",
                                ):
                                    raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
                                return match.group()
                            elif match := regex.IMAGE_URL.match(thumbnail.url):
                                return "https://proxy.wock.cloud?url=" + match.group()

        raise commands.CommandError("Please **provide** an image")


class ImageFinderStrict(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        # try:
        #     member = await Member().convert(ctx, argument)
        #     if member and not member.display_avatar.is_animated():
        #         return member.display_avatar.url
        # except:
        #     pass

        if match := regex.DISCORD_ATTACHMENT.match(argument):
            if not match.group("mime") in ("png", "jpg", "jpeg", "webp"):
                raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
            return match.group()
        elif match := regex.IMAGE_URL.match(argument):
            if match.group("mime") == "gif":
                raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
            return "https://proxy.wock.cloud?url=" + match.group()
        else:
            raise commands.CommandError(f"Couldn't find an **image**")

    async def search(ctx: Context, history: bool = True):
        if message := ctx.replied_message:
            for attachment in message.attachments:
                if attachment.content_type.split("/", 1)[1] in (
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                ):
                    return attachment.url
            for embed in message.embeds:
                if image := embed.image:
                    if match := regex.DISCORD_ATTACHMENT.match(image.url):
                        if not match.group("mime") in (
                            "png",
                            "jpg",
                            "jpeg",
                            "webp",
                        ):
                            raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
                        return match.group()
                    elif match := regex.IMAGE_URL.match(image.url):
                        if match.group("mime") == "gif":
                            continue
                        return "https://proxy.wock.cloud?url=" + match.group()
                elif thumbnail := embed.thumbnail:
                    if match := regex.DISCORD_ATTACHMENT.match(thumbnail.url):
                        if not match.group("mime") in (
                            "png",
                            "jpg",
                            "jpeg",
                            "webp",
                        ):
                            raise commands.CommandError(f"Invalid image format: **{match.group('mime')}**")
                        return match.group()
                    elif match := regex.IMAGE_URL.match(thumbnail.url):
                        if match.group("mime") == "gif":
                            continue
                        return "https://proxy.wock.cloud?url=" + match.group()

        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if attachment.content_type.split("/", 1)[1] in (
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                ):
                    return attachment.url

        if history:
            async for message in ctx.channel.history(limit=50):
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.content_type.split("/", 1)[1] in (
                            "png",
                            "jpg",
                            "jpeg",
                            "webp",
                        ):
                            return attachment.url
                if message.embeds:
                    for embed in message.embeds:
                        if image := embed.image:
                            if match := regex.DISCORD_ATTACHMENT.match(image.url):
                                if not match.group("mime") in (
                                    "png",
                                    "jpg",
                                    "jpeg",
                                    "webp",
                                ):
                                    continue
                                return match.group()
                            elif match := regex.IMAGE_URL.match(image.url):
                                if match.group("mime") == "gif":
                                    continue
                                return "https://proxy.wock.cloud?url=" + match.group()
                        elif thumbnail := embed.thumbnail:
                            if match := regex.DISCORD_ATTACHMENT.match(thumbnail.url):
                                if not match.group("mime") in (
                                    "png",
                                    "jpg",
                                    "jpeg",
                                    "webp",
                                ):
                                    continue
                                return match.group()
                            elif match := regex.IMAGE_URL.match(thumbnail.url):
                                if match.group("mime") == "gif":
                                    continue
                                return "https://proxy.wock.cloud?url=" + match.group()

        raise commands.CommandError("Please **provide** an image")


class MediaFinder(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)
        try:
            member = await Member().convert(ctx, argument)
            if member:
                return member.display_avatar.url
        except:
            pass

        if match := regex.DISCORD_ATTACHMENT.match(argument):
            if not match.group("mime") in ("mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "mov", "webm", "quicktime"):
                raise commands.CommandError(f"Invalid media format: **{match.group('mime')}**")
            return match.group()
        elif match := regex.MEDIA_URL.match(argument):
            return "https://proxy.wock.cloud?url=" + match.group()
        else:
            raise commands.CommandError(f"Couldn't find any **media**")

    async def search(ctx: Context, history: bool = True):
        if message := ctx.replied_message:
            for attachment in message.attachments:
                if attachment.content_type.split("/", 1)[1] in (
                    "mp3",
                    "mp4",
                    "mpeg",
                    "mpga",
                    "m4a",
                    "wav",
                    "mov",
                    "webp",
                    "quicktime",
                ):
                    return attachment.url

        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if attachment.content_type.split("/", 1)[1] in (
                    "mp3",
                    "mp4",
                    "mpeg",
                    "mpga",
                    "m4a",
                    "wav",
                    "mov",
                    "webp",
                    "quicktime",
                ):
                    return attachment.url

        if history:
            async for message in ctx.channel.history(limit=50):
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.content_type.split("/", 1)[1] in (
                            "mp3",
                            "mp4",
                            "mpeg",
                            "mpga",
                            "m4a",
                            "wav",
                            "mov",
                            "webp",
                        ):
                            return attachment.url

        raise commands.CommandError("Please **provide** a media file")


def DiscriminatorValidator(argument: str):
    argument = str(argument)
    if match := regex.DISCORD_DISCRIMINATOR.match(argument):
        if match != "0000":
            return match.group()

    raise commands.CommandError(f"Invalid discriminator: `{argument}`")


class Command(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        argument = str(argument)

        if command := ctx.bot.get_command(argument):
            return command
        else:
            raise commands.CommandError(f"Command `{argument}` doesn't exist")


class MemberStrict(commands.MemberConverter):
    async def convert(self, ctx: Context, argument: str):
        member = None
        argument = str(argument)
        if match := regex.DISCORD_ID.match(argument):
            member = ctx.guild.get_member(int(match.group(1)))
        elif match := regex.DISCORD_USER_MENTION.match(argument):
            member = ctx.guild.get_member(int(match.group(1)))

        if not member:
            raise commands.MemberNotFound(argument)
        return member


class Member(commands.MemberConverter):
    async def convert(self, ctx: Context, argument: str):
        member = None
        argument = str(argument)
        if match := regex.DISCORD_ID.match(argument):
            member = ctx.guild.get_member(int(match.group(1)))
        elif match := regex.DISCORD_USER_MENTION.match(argument):
            member = ctx.guild.get_member(int(match.group(1)))
        else:
            member = (
                discord.utils.find(
                    lambda m: m.name.lower() == argument.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in m.name.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.name.lower().startswith(argument.lower()),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.display_name.lower() == argument.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in m.display_name.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.display_name.lower().startswith(argument.lower()),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: str(m).lower() == argument.lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in str(m).lower(),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: str(m).lower().startswith(argument.lower()),
                    sorted(
                        ctx.channel.members,
                        key=lambda m: int(m.discriminator if not isinstance(m, discord.ThreadMember) else 0),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.name.lower() == argument.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in m.name.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.name.lower().startswith(argument.lower()),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.display_name.lower() == argument.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in m.display_name.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: m.display_name.lower().startswith(argument.lower()),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: str(m).lower() == argument.lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: argument.lower() in str(m).lower(),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
                or discord.utils.find(
                    lambda m: str(m).lower().startswith(argument.lower()),
                    sorted(
                        ctx.guild.members,
                        key=lambda m: int(m.discriminator),
                        reverse=False,
                    ),
                )
            )
        if not member:
            raise commands.MemberNotFound(argument)
        return member

    async def hierarchy(self, ctx: Context, user: discord.Member, author: bool = False):
        if isinstance(user, discord.User):
            return True
        elif ctx.guild.me.top_role <= user.top_role:
            raise commands.CommandError(f"I'm unable to **{ctx.command.qualified_name}** {user.mention}")
        elif ctx.author.id == user.id and not author:
            raise commands.CommandError(f"You're unable to **{ctx.command.qualified_name}** yourself")
        elif ctx.author.id == user.id and author:
            return True
        elif ctx.author.id == ctx.guild.owner_id:
            return True
        elif user.id == ctx.guild.owner_id:
            raise commands.CommandError(f"You're unable to **{ctx.command.qualified_name}** the **server owner**")
        elif ctx.author.top_role.is_default():
            raise commands.CommandError(
                f"You're unable to **{ctx.command.qualified_name}** {user.mention} because your **highest role** is {ctx.guild.default_role.mention}"
            )
        elif ctx.author.top_role == user.top_role:
            raise commands.CommandError(
                f"You're unable to **{ctx.command.qualified_name}** {user.mention} because they have the **same role** as you"
            )
        elif ctx.author.top_role < user.top_role:
            raise commands.CommandError(
                f"You're unable to **{ctx.command.qualified_name}** {user.mention} because they have a **higher role** than you"
            )
        else:
            return True


class User(commands.UserConverter):
    async def convert(self, ctx: Context, argument: str):
        user = None
        argument = str(argument)
        if match := regex.DISCORD_ID.match(argument):
            user = ctx.bot.get_user(int(match.group(1)))
            if not user:
                user = await ctx.bot.fetch_user(int(match.group(1)))
        elif match := regex.DISCORD_USER_MENTION.match(argument):
            user = ctx.bot.get_user(int(match.group(1)))
            if not user:
                user = await ctx.bot.fetch_user(int(match.group(1)))
        else:
            user = (
                discord.utils.find(lambda u: u.name.lower() == argument.lower(), ctx.bot.users)
                or discord.utils.find(lambda u: argument.lower() in u.name.lower(), ctx.bot.users)
                or discord.utils.find(
                    lambda u: u.name.lower().startswith(argument.lower()),
                    ctx.bot.users,
                )
                or discord.utils.find(lambda u: str(u).lower() == argument.lower(), ctx.bot.users)
                or discord.utils.find(lambda u: argument.lower() in str(u).lower(), ctx.bot.users)
                or discord.utils.find(
                    lambda u: str(u).lower().startswith(argument.lower()),
                    ctx.bot.users,
                )
            )
        if not user:
            raise commands.UserNotFound(argument)
        return user


class Role(commands.RoleConverter):
    async def convert(self, ctx: Context, argument: str):
        role = None
        argument = str(argument)
        if match := regex.DISCORD_ID.match(argument):
            role = ctx.guild.get_role(int(match.group(1)))
        elif match := regex.DISCORD_ROLE_MENTION.match(argument):
            role = ctx.guild.get_role(int(match.group(1)))
        else:
            role = (
                discord.utils.find(lambda r: r.name.lower() == argument.lower(), ctx.guild.roles)
                or discord.utils.find(lambda r: argument.lower() in r.name.lower(), ctx.guild.roles)
                or discord.utils.find(
                    lambda r: r.name.lower().startswith(argument.lower()),
                    ctx.guild.roles,
                )
            )
        if not role or role.is_default():
            raise commands.RoleNotFound(argument)
        return role

    async def manageable(self, ctx: Context, role: discord.Role, booster: bool = False):
        if role.managed and not booster:
            raise commands.CommandError(f"You're unable to manage {role.mention}")
        elif not role.is_assignable() and not booster:
            raise commands.CommandError(f"I'm unable to manage {role.mention}")
        elif role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
            raise commands.CommandError(f"You're unable to manage {role.mention}")

        return True

    async def dangerous(self, ctx: Context, role: discord.Role, _: str = "manage"):
        if (
            permissions := list(
                filter(
                    lambda permission: getattr(role.permissions, permission),
                    DANGEROUS_PERMISSIONS,
                )
            )
        ) and not ctx.author.id == ctx.guild.owner_id:
            raise commands.CommandError(f"You're unable to {_} {role.mention} because it has the `{permissions[0]}` permission")

        return False


class Roles(commands.RoleConverter):
    async def convert(self, ctx: Context, argument: str):
        roles = []
        argument = str(argument)
        for role in argument.split(","):
            try:
                role = await Role().convert(ctx, role.strip())
                if role not in roles:
                    roles.append(role)
            except commands.RoleNotFound:
                continue

        if not roles:
            raise commands.RoleNotFound(argument)
        return roles

    async def manageable(self, ctx: Context, roles: list[discord.Role], booster: bool = False):
        for role in roles:
            await Role().manageable(ctx, role, booster)

        return True

    async def dangerous(self, ctx: Context, roles: list[discord.Role], _: str = "manage"):
        for role in roles:
            await Role().dangerous(ctx, role, _)

        return False


class WebSocket:
    def __init__(self, bot: wockSuper, url: str):
        self.bot: wockSuper = bot
        self.url: str = url

    async def ping_task(self):
        while True:
            await self.emit({"type": "PING", "data": {"ping": "pong"}})
            try:
                await asyncio.wait_for(self.receive(), timeout=3)
            except:
                pass
            await asyncio.sleep(5)

    async def connect(self):
        self.websocket = await websockets.connect(self.url)
        self.bot.loop.create_task(self.ping_task())
        return self

    async def _attempt(self, func, *args):
        try:
            return await func(*args)
        except:
            self.bot.socket = await self.connect()
            await asyncio.sleep(1)
            return await func(*args)

    async def emit(self, data: dict):
        await self._attempt(self.websocket.send, json.dumps(data))

    async def receive(self):
        return json.loads(await self._attempt(self.websocket.recv))


class Database:
    def __init__(self, config: Dict):
        self.config = config
        self.pool = None

    def __repr__(self):
        return f"<helpers.wock.Database host=127.0.0.1 user=rx database=wock>"

    def _encode_jsonb(*values):
        return json.dumps(values[1])

    def _decode_jsonb(*values):
        return json.loads(values[1])

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
                config["database"]["user"],
                config["database"]["password"],
                config["database"]["database"],
            ),
            init=self._init,
        )
        await self.create_tables()
        return self

    async def close(self):
        await self.pool.close()

    async def create_tables(self):
        try:
            with open("schema.sql", "r") as f:
                return await self.pool.execute(f.read())
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
                        raise commands.CommandError("Invalid **select** argument")

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
                    raise commands.CommandError("Invalid **select** argument")

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

    async def create_table(self, table: str, columns: list):
        return await self.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})")

    async def drop_table(self, table: str):
        return await self.execute(f"DROP TABLE IF EXISTS {table}")

    async def fetch_config(self, guild_id: int, key: str):
        return await self.fetchval(f"SELECT {key} FROM config WHERE guild_id = $1", guild_id)

    async def update_config(self, guild_id: int, key: str, value: str):
        await self.execute(
            f"INSERT INTO config (guild_id, {key}) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET {key} = $2",
            guild_id,
            value,
        )
        return await self.fetchrow(f"SELECT * FROM config WHERE guild_id = $1", guild_id)


class Redis(AsyncStrictRedis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock: asyncio.Lock = asyncio.Lock()

    def __repr__(self):
        return f"<helpers.wock.Redis lock={self._lock}>"

    async def keys(self, pattern: str = "*"):
        async with self._lock:
            return await super().keys(pattern)

    async def get(self, key: str):
        async with self._lock:
            data = await super().get(key)

            if data:
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            return data

    async def set(self, key: str, value: any, **kwargs):
        async with self._lock:
            if type(value) in (dict, list, tuple):
                value = json.dumps(value)

            return await super().set(key, value, **kwargs)

    async def delete(self, *keys: str):
        async with self._lock:
            return await super().delete(*keys)

    async def ladd(self, key: str, *values: str, **kwargs):
        values = list(values)
        for index, value in enumerate(values):
            if type(value) in (dict, list, tuple):
                values[index] = json.dumps(value)

        async with self._lock:
            result = await super().sadd(key, *values)
            if kwargs.get("ex"):
                await super().expire(key, kwargs.get("ex"))

            return result

    async def lget(self, key: str):
        async with self._lock:
            _values = await super().smembers(key)

        values = list()
        for value in _values:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass

            values.append(value)

        return values

    async def get_lock(self, key: str):
        return await self._lock()

    @classmethod
    async def from_url(
        cls,
    ):  # URL: redis://default:VpOlWDrcAAjw2Vd5wTULlt0IIbZRdEcj@redis-16382.c61.us-east-1-3.ec2.cloud.redislabs.com:16382"
        return await cls(
            connection_pool=BlockingConnectionPool.from_url(
                "redis://default:VpOlWDrcAAjw2Vd5wTULlt0IIbZRdEcj@redis-16382.c61.us-east-1-3.ec2.cloud.redislabs.com:16382",
                decode_responses=True,
                timeout=1,
                max_connections=7000,
                retry=Retry(backoff=EqualJitterBackoff(3, 1), retries=100),
            )
        )


class ParameterSlicer:
    def __init__(self, ctx: Context, slicer: str = "--"):
        self.ctx: Context = ctx
        self.slicer: str = slicer
        self.short_slicer: str = slicer[0]

    def get(self, parameter: str, **kwargs):
        parameters = [parameter]
        parameters.extend(kwargs.get("aliases", []))

        for parameter in parameters:
            target: str = f"{self.slicer}{parameter}"
            target_short: str = f"{self.short_slicer}{parameter}"
            sliced: list = self.ctx.message.content.replace("—", "--").replace("\n", "\\n").split()

            if not target in sliced and not target_short in sliced:
                continue

            if not kwargs.get("require_value", True):
                return True

            try:
                index: int = sliced.index(target)
            except ValueError:
                index: int = sliced.index(target_short)
            result: list = list()
            for word in sliced[index + 1 :]:
                if word.startswith(self.short_slicer):
                    break
                result.append(word)

            result = " ".join(result).replace("\\n", "\n").strip()
            if result:
                if choices := kwargs.get("choices"):
                    choice = [choice for choice in choices if choice.lower() == result.lower()]
                    if not choice:
                        raise commands.CommandError(f"Invalid choice for parameter **{parameter}**")

                    result = choice[0]
            else:
                return kwargs.get("default", None)

            if converter := kwargs.get("converter"):
                if getattr(converter, "convert", None):
                    result = self.ctx.bot.loop.create_task(converter().convert(self.ctx, result))
                else:
                    try:
                        result = converter(result)
                    except:
                        raise commands.CommandError(f"Invalid value for parameter **{parameter}**")

            if isinstance(result, int):
                if result < kwargs.get("minimum", 1):
                    raise commands.CommandError(f"The **minimum** input for parameter **{parameter}** is `{kwargs.get('minimum', 1)}`")
                if result > kwargs.get("maximum", 100):
                    raise commands.CommandError(f"The **maximum** input for parameter **{parameter}** is `{kwargs.get('maximum', 100)}`")

            return result

        return kwargs.get("default", None)

    def __contains__(self, parameter: str):
        return self.get(parameter, False) is not None

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


async def identify(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": "Discord iOS",
                "$browser": "Discord iOS",
                "$device": "iOS",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
        },
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload["d"]["presence"] = {
            "status": state._status,
            "game": state._activity,
            "since": 0,
            "afk": False,
        }

    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value

    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)


from discord.gateway import DiscordWebSocket


DiscordWebSocket.identify = identify

DANGEROUS_PERMISSIONS = [
    "administrator",
    "kick_members",
    "ban_members",
    "manage_guild",
    "manage_roles",
    "manage_channels",
    "manage_emojis",
    "manage_webhooks",
    "manage_nicknames",
    "mention_everyone",
]


from discord.ext.commands import core


class PatchCore:
    def __init__(self):
        super().__init__()

    async def permissions(self):
        _permissions = list()

        if self.checks:
            for check in self.checks:
                if "has_permissions" in str(check):
                    return await check(0)

        return _permissions

    async def invoke(self, ctx: Context, /) -> None:
        await self.prepare(ctx)

        if hasattr(ctx, "parameters") and (parameters := ctx.parameters):
            for parameter, value in parameters.items():
                if kwargs := list(ctx.kwargs.keys()):
                    kwarg = kwargs[-1]
                    for parameter in (
                        parameter,
                        *ctx.command.parameters.get(parameter).get("aliases", []),
                    ):
                        if type(ctx.kwargs.get(kwarg)) in (str, EmbedScript):
                            ctx.kwargs.update(
                                {
                                    kwarg: (
                                        ctx.kwargs.get(kwarg)
                                        .replace("—", "--")
                                        .replace(f"--{parameter} {value}", "")
                                        .replace(f"--{parameter}", "")
                                        .replace(f"-{parameter}", "")
                                        .strip()
                                    )
                                    or (ctx.command.params.get(kwarg).default if isinstance(ctx.command.params.get(kwarg).default, str) else None)
                                }
                            )

        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None
        injected = core.hooked_wrapped_callback(self, ctx, self.callback)  # type: ignore
        await injected(*ctx.args, **ctx.kwargs)  # type: ignore


core.Command.invoke = PatchCore.invoke
core.Command.permissions = PatchCore.permissions

from discord import interactions


class PatchInteraction:
    def __init__(self):
        super().__init__()

    async def neutral(self, message: str, **kwargs):
        embed = discord.Embed(
            color=kwargs.pop("color", functions.config_color("main")),
            description=f"{kwargs.pop('emoji', None) or ''} {message}",
        )
        if kwargs.pop("followup", True):
            return await self.followup.send(embed=embed, ephemeral=True, **kwargs)
        else:
            return await self.response.send_message(embed=embed, ephemeral=True, **kwargs)

    async def approve(self, message: str, **kwargs):
        config["styles"]["approve"].get("emoji")
        embed = discord.Embed(
            color=functions.config_color("approve"),
            description=f"{kwargs.pop('emoji', None) or ''} {message}",
        )
        if kwargs.pop("followup", True):
            return await self.followup.send(embed=embed, ephemeral=True, **kwargs)
        else:
            return await self.response.send_message(embed=embed, ephemeral=True, **kwargs)

    async def warn(self, message: str, **kwargs):
        config["styles"]["warn"].get("emoji")
        embed = discord.Embed(
            color=functions.config_color("warn"),
            description=f"{kwargs.pop('emoji', None) or ''} {message}",
        )
        if kwargs.pop("followup", True):
            return await self.followup.send(embed=embed, ephemeral=True, **kwargs)
        else:
            return await self.response.send_message(embed=embed, ephemeral=True, **kwargs)


interactions.Interaction.neutral = PatchInteraction.neutral
interactions.Interaction.approve = PatchInteraction.approve
interactions.Interaction.warn = PatchInteraction.warn
