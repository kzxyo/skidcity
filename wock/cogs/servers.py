from typing import Literal
import asyncio

from discord.ext.commands import Cog, command, group, has_permissions
from discord import Message

from helpers.wonder import Wonder
from helpers.patch.context import Context

import config

class Servers(Cog, name = "Server"):
    def __init__(self, bot: Wonder):
        self.bot: Wonder = bot
    
    @group(
        name="prefix",
        invoke_without_command=True,
    )
    async def prefix(self, ctx: Context) -> Message:
        """
        View guild prefix
        """

        prefix = (
            await self.bot.db.fetchval(
                """
            SELECT prefix FROM config
            WHERE guild_id = $1
            """,
                ctx.guild.id,
            )
            or ";"
        )
        if prefix == "disabled":
            return await ctx.neutral(
                f"You don't have a **custom prefix** set for this guild, you can set one using `@{self.bot.user} prefix set (prefix)`"
            )

        return await ctx.neutral(f"Guild Prefix: `{prefix}`")

    @prefix.command(
        name="remove",
        aliases=[
            "delete",
            "del",
            "clear",
        ],
    )
    @has_permissions(administrator=True)
    async def prefix_remove(self, ctx: Context) -> Message:
        """
        Remove command prefix for guild
        """

        await self.bot.db.execute(
            """
            UPDATE config SET
                prefix = $2
            WHERE guild_id = $1
            """,
            ctx.guild.id,
            "disabled",
        )

        return await ctx.neutral(
            f"Removed your current guild's prefix, you can set one using `@{self.bot.user} prefix set (prefix)`"
        )

    @prefix.command(
        name="set",
        usage="(prefix)",
        example="!",
        aliases=["add"],
    )
    @has_permissions(administrator=True)
    async def prefix_set(self, ctx: Context, prefix: str) -> Message:
        """
        Set command prefix for guild
        """

        if len(prefix) > 12:
            return await ctx.neutral(
                "The prefix can not be longer than **12 characters**"
            )

        await self.bot.db.execute(
            """
            INSERT INTO config (
                guild_id,
                prefix
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET
                prefix = EXCLUDED.prefix;
            """,
            ctx.guild.id,
            prefix.lower(),
        )

        return await ctx.approve(
            f"{'Set' if prefix == ';' else 'Replaced'} your current guild's prefix to `{prefix.lower()}`"
        )

async def setup(bot: Wonder):
    await bot.add_cog(Servers(bot))