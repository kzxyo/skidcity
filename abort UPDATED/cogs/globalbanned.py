import discord
from discord.ext import commands, tasks

class globalbanned(commands.Cog):
    def init(self, bot):
        self.bot = bot
        self.blacklisted = [1114402138760687616]

    @tasks.loop(seconds=2)
    async def check_blacklist(self):
          for guild in self.bot.guilds:
            for member in guild.members:
                if member.id in self.blacklisted: 
                    await guild.ban(member, reason="Globally Banned User.")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.check_blacklist.start()

async def setup(bot):
    await bot.add_cog(globalbanned(bot))