async def setup(bot) -> None:
    from .information import Information

    await bot.add_cog(Information(bot))
