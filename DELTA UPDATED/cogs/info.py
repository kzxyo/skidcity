import discord, random
from discord.ext import commands
from discord.ui import View, Button

class info(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot        
 

   @commands.hybrid_command(help="info", description="shows bot information", aliases=["about", "info", "bi"]) 
   async def botinfo(self, ctx: commands.Context):
    voice_channels = 0
    text_channels = 0
    category_channels = 0
    for guild in self.bot.guilds:
       voice_channels += len(guild.voice_channels)
       text_channels += len(guild.text_channels)
       category_channels += len(guild.categories)
    embed = discord.Embed(color=self.bot.color, title="info", description=f"ping `{self.bot.ping}`\nversion `{discord.__version__}`\ncommands `{len(set(self.bot.walk_commands()))}`")
    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
    embed.add_field(name="stats", value=f"guilds `{len(self.bot.guilds)}`\ndonor guilds `{len([g['guild_id'] for g in await self.bot.db.fetch('SELECT * FROM authorize') if self.bot.get_guild(int(g['guild_id']))])}`\nmembers `{sum(g.member_count for g in self.bot.guilds):,}`\nchannels `{text_channels}`")  
    embed.set_thumbnail(url=self.bot.user.display_avatar.url)
    await ctx.reply(embed=embed)
    
   @commands.hybrid_command(description="check bot connection", help="info")
   async def ping(self, ctx):
    await ctx.reply(f"takes `{self.bot.ping}ms` to ping delta support...")

   @commands.hybrid_command(description="invite the bot", help="info", aliases=["support", "inv"])
   async def invite(self, ctx):
    avatar_url = self.bot.user.avatar.url
    embed = discord.Embed(color=self.bot.color, description="Add the bot in your server!")
    embed.set_author(name=self.bot.user.name, icon_url=f"{avatar_url}")
    button1 = Button(label="invite", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands")
    button2 = Button(label="support", url="https://discord.gg/QpKVpXABxx")
    view = View()
    view.add_item(button1)
    view.add_item(button2)
    await ctx.reply(embed=embed, view=view)

async def setup(bot) -> None:
    await bot.add_cog(info(bot))      
