from structure import Blare
from structure.managers import Context

from discord import Message, Embed, Role, Member, User, ButtonStyle
from discord.ui import View, Button
from discord.utils import format_dt
from discord.ext.commands import Cog, command, Author

from psutil import Process
from jishaku.math import natural_size

class Developer(Cog):
    def __init__(self, bot: Blare):
        self.bot: Blare = bot
        
    async def cog_check(self: "Developer", ctx: Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @command(
        name="reload",
        aliases=["rl"],
    )
    async def reload(
        self: "Developer", 
        ctx: Context
    ) -> Message:
        """
        Reload a feature.
        """

        reloaded = list()

        for feature in list(self.bot.extensions):
            if feature == "modules.network":
                continue

            try:
                await self.bot.reload_extension(feature)
            except Exception as e:
                return await ctx.send(f"```py\n{e}\n```")
            reloaded.append(feature)

        return await ctx.send("👍")
    
async def setup(bot: Blare) -> None:
    await bot.add_cog(Developer(bot))
