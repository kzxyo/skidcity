from statcord import StatcordClient
from discord.ext import commands
import os


class MyStatcordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = os.environ.get("STATCORD_TOKEN")
        self.statcord_client = StatcordClient(bot, self.token, self.custom_graph_1)

    def cog_unload(self):
        self.statcord_client.close()

    async def custom_graph_1(self):
        return 1 + 2 + 3


async def setup(bot):
	await bot.add_cog(MyStatcordCog(bot))
