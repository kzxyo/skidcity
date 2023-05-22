import discord, time, datetime, platform 
from discord.ext import commands
from cogs.events import commandhelp, noperms
from utils.classes import colors, emojis
from cogs.events import blacklist
from discord.ui import Button, View
from utils.embedparser import to_object

global startTime
my_system = platform.uname()

class utility(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
    

    @commands.command(help="build a custom embed", description="moderation")
    @commands.cooldown(1, 4, commands.BucketType.user)
    @blacklist()
    async def embed(self, ctx: commands.Context, *, code):
     if not ctx.author.guild_permissions.manage_guild: 
       await noperms(self, ctx, "manage_guild")
       return 
     await ctx.channel.typing()
     x = await to_object(code)
     await ctx.send(**x)

async def setup(bot):
    await bot.add_cog(utility(bot))
