async def setup(bot) -> None:
    from .antinuke import Antinuke

    await bot.add_cog(Antinuke(bot))
