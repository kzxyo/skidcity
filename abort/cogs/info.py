import discord, time, platform 
from discord.ext import commands 
from cogs.events import seconds_to_dhms, blacklist, commandhelp
from utils.classes import Colors, Emojis

my_system = platform.uname()

class info(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot 
    
    @commands.command(help="check the bot's latency", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def ping(self, ctx: commands.Context): 
      await ctx.reply("...pong :ping_pong: `{}ms`".format(round(self.bot.latency * 1000)))  

    @commands.command(help="check the bot's uptime", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def uptime(self, ctx: commands.Context):  
     uptime = int(time.time() - self.bot.uptime)
     e = discord.Embed(color=Colors.default, description=f":alarm_clock: **{self.bot.user.name}'s** uptime: **{seconds_to_dhms(uptime)}**")
     await ctx.reply(embed=e, mention_author=False) 

    @commands.command(help="check bot's statistics", aliases=["about", "bi", "info"], description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def botinfo(self, ctx: commands.Context): 
        await ctx.send(f"> Suck My Dick.", mention_author=False)  
    
    @commands.command(help="invite the bot in your server", aliases=["inv"], description="info")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def invite(self, ctx):
        embed = discord.Embed(color=Colors.default, description="invite **abort** in your server")
        button = discord.ui.Button(label="invite", style=discord.ButtonStyle.url, url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all()))
        button2 = discord.ui.Button(label="support", style=discord.ButtonStyle.url, url="https://discord.gg/abort")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @commands.command(help="check bot's commands", aliases=["h"], usage="<command name>", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def help(self, ctx: commands.Context, *, command=None):
        await ctx.send(f"https://tear.lol/commands, server @ https://tear.lol/discord", mention_author=False)  

async def setup(bot):
    await bot.add_cog(info(bot))   