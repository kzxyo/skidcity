import discord, time, platform, psutil, asyncio
from discord.ext import commands 
from cogs.events import uptime, blacklist, commandhelp
from utils.classes import Colors, Emojis

my_system = platform.uname()

class info(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot 
    
    @commands.command(help="check the bot's latency", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def ping(self, ctx: commands.Context): 
       mes = await ctx.reply(f"websocket: **{round(self.bot.latency * 1000)}ms**")
       await asyncio.sleep(0.2)
       await mes.edit(content=f"{mes.content} ({round((time.time() - int(mes.created_at.timestamp())) * 100)})") 
  
    @commands.command(description="check for how long was the bot running for")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def uptime(self, ctx: commands.Context): 
     uptime = int(time.time() - self.bot.uptime)
     await ctx.reply(embed=discord.Embed(color=Colors.default, description=f"{self.bot.user.name} has been running for **{' '.join(self.bot.uptime)}**"))

    @commands.command(help="check bot's statistics", aliases=["about", "bi", "info"], description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def botinfo(self, ctx: commands.Context):
        channels = []
        for guild in self.bot.guilds:
          for channel in guild.text_channels:
             channels.append(channel)

        embed = discord.Embed(color=Colors.default, description=f'**bot information**').set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name="about", value=f'> <:Reply:1067710251148791860> created by [ece](https://discord.com/users/1077729793400897576)', inline=False)
        embed.add_field(name="developers", value=f'> <:Reply:1067710251148791860> devs: [ece](https://discord.com/users/1077729793400897576), [mayors](https://discord.com/users/509244475126841365), & [pretend](https://discord.com/users/1107903478451408936)', inline=False)
        embed.add_field(name="stats", value=f'> <:Reply:1067710251148791860> servers: ``{len(self.bot.guilds)}`` \n> <:Reply:1067710251148791860> users: ``{len(self.bot.users):,}`` \n> <:Reply:1067710251148791860> channels: ``{len(channels):,}`` \n> <:Reply:1067710251148791860> commands: ``{len(self.bot.commands)}``', inline=False)
        embed.add_field(name="versions", value=f'> <:Reply:1067710251148791860> py: ``3.8.2`` \n> <:Reply:1067710251148791860> discord.py ``2.0.1``', inline=False)
        embed.add_field(name="usage", value=f'> <:Reply:1067710251148791860> ping: ``{round(self.bot.latency * 1000)}ms`` \n> <:Reply:1067710251148791860> ram: ``{psutil.virtual_memory().percent}%`` \n> <:Reply:1067710251148791860> cpu: ``{psutil.cpu_percent()}%``', inline=False)
        embed.set_footer(text="abort/v13.8.0")
        mes = await ctx.send(embed=embed)
 
    @commands.command(description="show credits to contributors of the bot", aliases=["c", "creds"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def credits(self, ctx: commands.Context):
       embed = discord.Embed(color=Colors.default, description=f">>> **{self.bot.get_user(self.bot.owner_ids[0])}** - main developer of the bot\n**{self.bot.get_user(994896336040239114)}** - bot showcaser & website developer\n**{self.bot.get_user(432110614341746689)}** - created the bot's emojis\n**{self.bot.get_user(1107903478451408936)}** - helped growing the bot\n**{self.bot.get_user(530079572893368330)}** - day one").set_author(icon_url=self.bot.user.display_avatar, name="contributors of abort")
       await ctx.send(embed=embed)

    @commands.command(help="invite the bot in your server", aliases=["inv"], description="info")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def invite(self, ctx):
        button = discord.ui.Button(label="invite", style=discord.ButtonStyle.url, url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all()))
        button2 = discord.ui.Button(label="support", style=discord.ButtonStyle.url, url="https://discord.gg/abort")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        await ctx.reply(view=view, mention_author=False)

    @commands.command(help="check bot's commands", aliases=["h"], usage="<command name>", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def help(self, ctx: commands.Context, *, command=None):
       await ctx.reply(f"<https://tear.lol/commands>, server @ <https://tear.lol/commands>")

    @commands.command(help="donate", usage="<command name>", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def donate(self, ctx: commands.Context): 
       embed = discord.Embed(color=Colors.default, description="**cashapp:** $nycsluts")
       embed.set_footer(text="abort/v13.8.0")
       await ctx.send(embed=embed)
 

async def setup(bot):
    await bot.add_cog(info(bot))   