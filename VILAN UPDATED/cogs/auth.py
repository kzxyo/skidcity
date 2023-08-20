import discord
from discord.ext import commands

owners = [994896336040239114, 1107903478451408936]

class Auth(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    
    
async def setup(bot):
    await bot.add_cog(Auth(bot))