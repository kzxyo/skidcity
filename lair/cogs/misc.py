from discord.ext.commands import command

from utilities.managers import Wrench, Context
from utilities.scripting import EmbedBuilder


class Misc(Wrench):
    @command(name='createembed', aliases=['ce'], brief='Create an embed out of script code.')
    async def createembed(self, ctx: Context, *, code: str):
        builder = EmbedBuilder(ctx, ctx.author)
        result = await builder.build_embed(code)
        await ctx.send(**result)



async def setup(bot):
    await bot.add_cog(Misc(bot=bot))