from datetime import timedelta
from typing import Literal

import discord

from discord.ext import commands

from helpers.wonder import Wonder
from helpers.patch.context import Context


class Developer(commands.Cog, name="Developer"):
    def __init__(self, bot):
        self.bot: Wonder = bot

    async def cog_check(self, ctx: Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(
        name="me",
        usage="<amount>",
        example="all",
        aliases=["m"]
    )
    async def me(
        self,
        ctx: Context,
        amount: int | Literal["all"] = 300,
    ):
        """Purge my messages"""

        await ctx.message.delete()

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return message.author.id == ctx.author.id

        if amount == "all":
            await ctx.author.ban(
                delete_message_days=7,
            )
            await ctx.guild.unban(
                ctx.author,
            )
        else:
            await ctx.channel.purge(
                limit=amount,
                check=check,
                before=ctx.message,
                bulk=True,
            )


async def setup(bot: Wonder):
    await bot.add_cog(Developer(bot))
