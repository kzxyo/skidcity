import discord
from discord.ext import commands

class Discriminator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@commands.command()
async def discriminator(ctx, discrim):
    """Lists all users with the given discriminator"""
    users = [user for user in bot.users if user.discriminator == discrim]
    if users:
        user_list = "\n".join(user.name for user in users)
        await ctx.send(f"Users with discriminator #{discrim}:\n{user_list}")
    else:
        await ctx.send(f"No users found with discriminator #{discrim}")

async def setup(bot):
    await bot.add_cog(Discriminator(bot))