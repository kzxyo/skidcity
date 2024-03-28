import discord_ios, datetime

from asyncpg import create_pool
from puke.patches import interaction

from puke.setup import logging
from puke.managers import Context, Help
from config import owner_ids, token

from datetime import timedelta, datetime

from discord.ext import commands

from discord.ext.commands import (
    AutoShardedBot,
    CooldownMapping, 
    BucketType,
    CommandOnCooldown, 
    CommandError,
    CheckFailure,
    CommandError,
    CommandNotFound,
    CommandOnCooldown,
    DisabledCommand,
    NotOwner,
    UserInputError,
    MissingRequiredArgument,
    MissingPermissions,
    when_mentioned_or
)
from discord import Intents, AllowedMentions, Message, Guild

from pathlib import Path
from discord.utils import utcnow
from datetime import datetime
from typing import Any
log = logging.getLogger(__name__)

class Puke(AutoShardedBot):
    def __init__(self: "Puke"):
        super().__init__(
            auto_update=False,
            intents=Intents.all(),
            help_command=Help(),
            command_prefix=self.get_prefix,
            case_insensitive=True,
            owner_ids=owner_ids,
            allowed_mentions=AllowedMentions(
                replied_user=False,
                everyone=False,
                roles=False,
                users=True,
            ),
        )
        self.uptime: datetime = utcnow()
        self.cooldown = CooldownMapping.from_cooldown(3, 5, BucketType.member)
        self.run(
            token,
            log_handler=None,
        )

    @property
    def members(self):
        return list(self.get_all_members())

    @property
    def channels(self):
        return list(self.get_all_channels())

    @property
    def commandss(self):
        return set(self.walk_commands())

    async def setup_hook(self: "Puke"):
        self.db = await create_pool(
            port="5432", 
            database="postgres", 
            user="postgres.bkomearzauonpbczyphz", 
            host="aws-0-us-west-1.pooler.supabase.com",
            password="L:jU77xLHwUjM5!"
        )
        await self.load_extension("jishaku")

        for file in Path("features").rglob("*.py"):
            await self.load_extension(f"{'.'.join(file.parts[:-1])}.{file.stem}")

    async def get_context(self: "Puke", message: Message, *, cls=Context) -> Context:
        return await super().get_context(message, cls=cls)
    
    async def get_prefix(self, message: Message) -> Any:
        prefix = (
            await self.db.fetchval(
                """
            SELECT prefix FROM prefixes
            WHERE guild_id = $1
            """,
                message.guild.id,
            )
            or ';'
        )

        return when_mentioned_or(prefix)(self, message)
    
    async def process_commands(self: "Puke", message: Message):
        if not message.guild: 
            return
        
        ctx = await self.get_context(message)
        bucket = self.cooldown.get_bucket(ctx.message)

        if retry_after := bucket.update_rate_limit():
            raise CommandOnCooldown(
                bucket, 
                retry_after,
                BucketType.member
            )
        
        return await super().process_commands(message)


    async def on_message(self, message: Message) -> Message:
        if not message.guild or not self.is_ready():
            return
        
        if message.content == f"<@{message.guild.me.id}>" or message.content == f"<@!{message.guild.me.id}>":
            prefix = (
                await self.db.fetchval(
                    """
                SELECT prefix FROM prefixes
                WHERE guild_id = $1
                """,
                    message.guild.id,
                )
                or ';'
            )
                
            return await message.reply(f"Prefix: `{prefix}`")
        
        await self.process_commands(message)

    async def on_command_error(self: "Puke", ctx: Context, exception: CommandError):\

        if type(exception) in (
            NotOwner,
            CheckFailure,
            UserInputError,
            DisabledCommand,
            CommandNotFound,
            CommandOnCooldown
        ): 
            return
                
        elif isinstance(exception, commands.MissingPermissions): 
            return await ctx.warn(f"you're missing the **{exception.missing_permissions[0]}** permissions")
        
        elif isinstance(exception, MissingRequiredArgument):
                return await ctx.send_help(ctx.command)
        
        elif isinstance(exception, commands.BotMissingPermissions): 
            return await ctx.warn(f"im missing the **{exception.missing_permissions[0]}** permissions")
            
        else:
            print(exception)

    async def on_guild_join(self: "Puke", guild: Guild):
        channel = await self.fetch_channel(1203799826903465984)
        await channel.send(f"Joined {guild} ({guild.id}) owned by {guild.owner}")

    async def on_guild_remove(self: "Puke", guild: Guild):
        channel = await self.fetch_channel(1203799849535807528)
        await channel.send(f"Left {guild} ({guild.id}) owned by {guild.owner}")
