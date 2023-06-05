import discord; import time
from discord.ext import commands
from discord.ext.commands import has_permissions
from utils.classes import Colors
from cogs.events import commandhelp, noperms, blacklist, sendmsg

class Firstmessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


@commands.command(usage="<channel>", aliases=['firstmsg'], description="get the first message from a certain channel")
@commands.cooldown(1, 6, commands.BucketType.user)
@blacklist()
async def firstmessage(self, ctx: commands.Context, *, channel: discord.TextChannel=None): 
   channel = channel or ctx.channel
   message = [m async for m in channel.history(oldest_first=True, limit=1)][0]
   embed = discord.Embed(color=self.bot.color, title=f"first message in {channel.name}", description=message.content, timestamp=message.created_at)
   embed.set_author(name=message.author, icon_url=message.author.display_avatar.url)
   view = discord.ui.View()
   view.add_item(discord.ui.Button(label="jump to message", url=message.jump_url))
   await ctx.reply(embed=embed, view=view)   


async def setup(bot):
    await bot.add_cog(Firstmessage(bot))