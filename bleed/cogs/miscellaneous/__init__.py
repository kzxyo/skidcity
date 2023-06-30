async def setup(bot) -> None:
    from .miscellaneous import Miscellaneous

    await bot.add_cog(Miscellaneous(bot))
