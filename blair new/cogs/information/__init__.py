from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools import Blair


async def setup(bot: "Blair"):
    from .information import Information

    await bot.add_cog(Information(bot))
