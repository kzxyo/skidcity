from discord import Embed, Message
from discord.ext.commands import Cog, command
from discord.utils import format_dt

from helpers.bleed import Bleed
from helpers.managers import Context


class Developer(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot

    async def cog_check(self, ctx: Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @command(
        name="traceback",
        usage="(error code)",
        example="YEZ4nIN3POZKM",
        aliases=["trace"],
    )
    async def traceback(self, ctx: Context, error_code: str = None) -> Message:
        """
        View an error traceback
        """

        if not error_code:
            error = await self.bot.db.fetchrow(
                "SELECT * FROM traceback ORDER BY id DESC LIMIT 1"
            )
        else:
            error = await self.bot.db.fetchrow(
                "SELECT * FROM traceback WHERE lower(error_code) = $1",
                error_code.lower(),
            )
            if not error:
                return await ctx.warn(
                    "No **error code** was found matching the argument provided"
                )

        embed = Embed(
            title=f"Error #{error['id']} - {error['command']}",
            description=(
                f"**User:** {self.bot.get_user(error['user_id']) or 'Unknown User'} (`{error['user_id']}`)\n"
                f"**Guild:** {self.bot.get_guild(error['guild_id']) or 'Unknown Server'} (`{error['guild_id']}`)\n"
                f"**Channel:** {self.bot.get_channel(error['channel_id']) or 'Unknown Channel'} (`{error['channel_id']}`)\n"
                f"**Timestamp:** {format_dt(error['date'])}\n"
                f"**Error:** `{error['error_code']}`\n"
                f"```\n{error['error_message']}```"
            ),
        )

        return await ctx.send(embed=embed)

    @command(
        name="me",
        usage="<amount>",
        example="150",
        aliases=["m"],
    )
    async def me(self, ctx: Context, amount: int = 100) -> None:
        """
        Clear your own messages
        """

        await ctx.message.delete()
        await ctx.channel.purge(limit=amount, check=lambda m: m.author == ctx.author)
