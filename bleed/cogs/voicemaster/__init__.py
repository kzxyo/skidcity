async def setup(bot) -> None:
    from .voicemaster import VoiceMaster

    await bot.add_cog(VoiceMaster(bot))
