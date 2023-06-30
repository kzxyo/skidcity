async def setup(bot) -> None:
    from .developer import Developer

    await bot.add_cog(Developer(bot))
