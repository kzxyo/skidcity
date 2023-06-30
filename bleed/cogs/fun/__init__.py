async def setup(bot) -> None:
    from .fun import Fun

    await bot.add_cog(Fun(bot))
