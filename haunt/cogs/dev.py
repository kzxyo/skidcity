import discord; import time
from discord.ext import commands
from discord.ext.commands import has_permissions
from utils.classes import Colors
from cogs.events import commandhelp, noperms, blacklist, sendmsg

class Developers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      
    @commands.command(name="gban")
    @commands.cooldown(1, 6, commands.BucketType.user)
    @blacklist()
    async def global_ban(self,ctx,member: discord.Member):
      if ctx.message.author.id == 112635397481213952:
        reason = "Abort | Globally Banned."
        time.sleep(2)
        await member.ban(reason=reason)
        for guild in self.bot.guilds:
          await ctx.guild.ban(member)
          time.sleep(3)
        await ctx.send('👍🏾', mention_author=False)
      else:
        await ctx.send('youre not the **developer** of this bot.')

async def setup(bot):
    await bot.add_cog(Developers(bot))