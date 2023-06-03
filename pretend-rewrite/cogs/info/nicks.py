import discord
from discord.ext import commands

class nicks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="shows the nicknames of the members",
        usage="nicks",
        aliases=["nick", "n", "ni", "nic"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nicks(self, ctx):
        embed = discord.Embed(
            color=self.bot.color,
            title=f"nicknames • shard: {ctx.guild.shard_id + 1}/{self.bot.shard_count}"
        )

        embed.add_field(
            name="general",
            value=f"**nicknames**: {ctx.guild.members.nick}",
            inline=False
        )

        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(nicks(bot))