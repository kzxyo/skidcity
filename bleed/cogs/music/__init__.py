async def setup(bot) -> None:
    from .music import Music

    await bot.add_cog(Music(bot))
