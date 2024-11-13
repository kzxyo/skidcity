from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools import Blair


async def setup(bot: "Blair"):
    from .mod import Mod

    await bot.add_cog(Mod(bot))
