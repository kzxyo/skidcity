async def setup(bot) -> None:
    from .lastfm import Lastfm

    await bot.add_cog(Lastfm(bot))
