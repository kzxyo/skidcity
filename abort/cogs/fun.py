import discord
from discord.ext import commands
from uwuipy import uwuipy
from utils.classes import Colors, Emojis

class fun(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 

    @commands.command(description="fun")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def uwu(self, ctx, *, message):
      if message == None:
            embed = discord.Embed(description=f"{Emojis.warning} {ctx.author.mention} what do you want me to uwuify?", color = Colors.default)
            await ctx.reply(embed=embed, mention_author=False)
      else:
            uwu = uwuipy()
            uwu_message = uwu.uwuify(message)
            await ctx.reply(uwu_message, mention_author=False)

async def setup(bot):
    await bot.add_cog(fun(bot))