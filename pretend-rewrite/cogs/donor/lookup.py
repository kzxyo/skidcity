import discord
from discord.ext import commands
from utils.isDonor import isDonor

class lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="lookup a user by username",
        usage="lookup <username>",
        aliases=["lu", "search"],
    )
    @isDonor()
    async def lookup(self, ctx: commands.Context, *, username: str):
        users = []
        for user in self.bot.users:
            if username.lower() in user.name.lower():
                users.append(user)

        if not users:
            return await ctx.reply("no users found")

        pages = []
        for i in range(0, len(users), 10):
            embed = discord.Embed(
                color=self.bot.color,
                title=f"users • {len(users)}"
            )
            page = ""
            for user in users[i:i+10]:
                page += f"{user.name} ({user.id})\n"
            embed.description = page
            pages.append(embed)

        await self.bot.paginator(ctx, pages)


async def setup(bot):
    await bot.add_cog(lookup(bot))