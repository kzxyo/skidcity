import discord, time, platform  
from discord import app_commands 
from discord.ext import commands
from cogs.events import commandhelp, seconds_to_dhms, blacklist
from utils.classes import Colors, Emojis

my_system = platform.uname()

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @app_commands.command(description="check the bot's latency")
    @blacklist()
    async def ping(self, ctx: discord.Interaction): 
      await ctx.response.send_message("...pong 🏓 `{}ms`".format(round(self.bot.latency * 1000)))  

    @app_commands.command(description="check the bot's uptime")
    @blacklist()
    async def uptime(self, ctx: discord.Interaction):  
     uptime = int(time.time() - self.bot.uptime)
     e = discord.Embed(color=Colors.green, description=f"⏰ **{self.bot.user.name}'s** uptime: **{seconds_to_dhms(uptime)}**")
     await ctx.response.send_message(embed=e) 

    @app_commands.command(description="check bot's statistics")
    @blacklist()
    async def botinfo(self, ctx: discord.Interaction): 
      lis = []  
      for i in self.bot.owner_ids:
        user = await self.bot.fetch_user(i) 
        lis.append(user.name + "#" + user.discriminator)
      embed = discord.Embed(color=Colors.default, title="botinfo").set_thumbnail(url=self.bot.user.display_avatar)
      embed.add_field(name=f"", value=f"`developers & owners`: `{' '.join(l for l in lis)}`\n`Server:` [here](https://discord.gg/abort)", inline=False)
      embed.add_field(name="Stats", value=f"`Users:` `{sum(g.member_count for g in self.bot.guilds)}`\n`Servers:` `{len(self.bot.guilds)}`", inline=False)
      embed.add_field(name="System:", value=f"`Latency:` `{round(self.bot.latency * 1000)}ms`\n`Language`: `Python`\n`System`: `{my_system.system}`", inline=False) 
      embed.set_footer(text="next in mind: help command.")   
      await ctx.response.send_message(embed=embed)
    
    @app_commands.command(description="invite the bot in your server")
    @blacklist()
    async def invite(self, ctx):
        embed = discord.Embed(color=Colors.default, description="invite **abort** in your server")
        button = discord.ui.Button(label="invite", style=discord.ButtonStyle.url, url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all()))
        button2 = discord.ui.Button(label="support", style=discord.ButtonStyle.url, url="https://discord.gg/abort")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        await ctx.response.send_message(embed=embed, view=view)

    @app_commands.command(description="check bot commands")
    @blacklist()
    async def help(self, ctx: discord.Interaction):
        embed = discord.Embed(color=Colors.default, description="veiw the commands ***[here](https://tear.lol/commands)***")
        embed.set_footer(text="working on website soon, dont worry, will be up soon!")  
        view = discord.ui.View()
        await ctx.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Slash(bot))        