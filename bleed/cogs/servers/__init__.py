async def setup(bot) -> None:
    from .servers import Servers

    await bot.add_cog(Servers(bot))
