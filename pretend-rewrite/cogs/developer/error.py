import discord
from discord.ext import commands

class error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="shown an error details",
        usage="error <error code>",
        aliases=["err"],
        hidden=True
    )
    @commands.is_owner()
    async def error(self, ctx, error_code: str):

        # CREATE TABLE IF NOT EXISTS errors (
        #     id TEXT NOT NULL UNIQUE,
        #     error TEXT NOT NULL,
        #     command TEXT NOT NULL,
        #     message_url TEXT NOT NULL,
        #     user_id BIGINT NOT NULL,
        #     time TIMESTAMP NOT NULL DEFAULT NOW()
        # );

        error = await self.bot.db.fetchrow("SELECT * FROM errors WHERE id = $1", error_code)

        if not error:
            return await ctx.reply("error not found")

        embed = discord.Embed(
            color=self.bot.color,
            title=f"error • {error['id']}"
        )
        embed.add_field(
            name="error",
            value=error['error'],
            inline=False
        )
        embed.add_field(
            name="command",
            value=error['command'],
            inline=False
        )
        embed.add_field(
            name="message url",
            value=error['message_url'],
            inline=True
        )
        embed.add_field(
            name="user id",
            value=error['user_id'],
            inline=True
        )
        embed.add_field(
            name="time",
            value=f"<t:{int(error['time'].timestamp())}:R> (<t:{int(error['time'].timestamp())}:F>)",
            inline=True
        )
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(error(bot))