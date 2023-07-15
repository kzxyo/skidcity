import discord
from discord.ext import commands
import os
from cogs.events import blacklist, sendmsg, commandhelp

DISCORD_API_LINK = "https://discord.com/api/invite/"

class utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(help="Get the icon from vanity", description="utility", usage=" <vanity code>", aliases=["sic"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def sicon(self, ctx, *, link=None):
     if link == None:
      await commandhelp(self, ctx, ctx.command.name)
      return 

     invite_code = link
     async with aiohttp.ClientSession() as cs:
      async with cs.get(DISCORD_API_LINK + invite_code) as r:
       data = await r.json()

     try: 
      format = ""
      if "a_" in data["guild"]["icon"]:
        format = ".gif"
      else:
        format = ".png"
          
      embed = discord.Embed(color=self.bot.color, title=data["guild"]["name"] + "'s icon")
      embed.set_image(url="https://cdn.discordapp.com/icons/" + data["guild"]["id"] + "/" + data["guild"]["icon"] + f"{format}?size=1024")
      await sendmsg(self, ctx, None, embed, None, None, None)
     except:
      e = discord.Embed(color=self.bot.color, description=f"{ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** icon")
      await sendmsg(self, ctx, None, e, None, None, None)
                         

async def setup(bot):
    await bot.add_cog(utility(bot))