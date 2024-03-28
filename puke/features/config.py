from puke import Puke
from puke.managers import Context

from discord.ext.commands import Cog, command

from tools.checks import Perms as utils


class Config(Cog):

    def __init__(self, bot):
        self.bot: Puke = bot

    @command(
        name="prefix",
        invoke_without_command=True,
    )
    @utils.get_perms("manage_guild")
    async def prefix(
        self: "Config",
        ctx: Context, 
        prefix: str
    ): 
        """
        Edit your guilds prefix
        """     
        if len(prefix) > 3: 
            return await ctx.warn("Uh oh! The prefix is too long")
        
        await self.bot.db.execute(
            """
            INSERT INTO prefixes (
                guild_id,
                prefix
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET prefix = $2
            """,
            ctx.guild.id, 
            prefix
        )

        return await ctx.approve(f"guild prefix changed to `{prefix}`".capitalize())

async def setup(bot):
    await bot.add_cog(Config(bot))