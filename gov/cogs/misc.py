from click import command
import discord, time, datetime, psutil
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
from utility import Emotes, Colours

class misc(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        e = discord.Embed(description=f"{Emotes.pingemote1} **Current Latency:** `{round(self.bot.latency * 1000)}ms`")
        await ctx.reply(embed=e)
        
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, number = None):
        if number == None:
            embed = discord.Embed(description=f"{Emotes.warningemote} You haven't made a number input.", color=Colours.warning)
            await ctx.send(embed=embed)
            return
        number = int(number)
        await ctx.channel.purge(limit=number)
        clear = discord.Embed(description=f"{ctx.author.mention}: Cleared **{number}** Messages", color=Colours.standard)
        await ctx.send(embed=clear)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warningemote} {ctx.author.mention}: You do not have permissions. `Manage Roles`", colour=Colours.standard)
            await ctx.send(embed=embed, mention_author=False)
            
async def setup(bot) -> None:
    await bot.add_cog(misc(bot))