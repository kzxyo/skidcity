import discord, random
from discord.ext import commands
from discord.ui import View, Button

class info(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot        

   @commands.hybrid_command(description="check how long the bot has been online for", help="info")
   async def uptime(self, ctx: commands.Context):
     e = discord.Embed(color=self.bot.color, description=f"⏰ **{self.bot.user.name}'s** uptime: **{self.bot.ext.uptime}**")
     await ctx.reply(embed=e)

   @commands.hybrid_command(help="info", description="shows bot information", aliases=["about", "info", "bi"]) 
   async def botinfo(self, ctx: commands.Context):
    embed = discord.Embed(color=self.bot.color, title="stats", description=f">>> • ping `{self.bot.ping}`\n• uptime `{(self.bot.ext.uptime.split(','))[0]}`\n• version `{discord.__version__}`\n• commands `{len(set(self.bot.walk_commands()))}`\n• guilds `{len(self.bot.guilds)}`\n• premium guilds `{len([g['guild_id'] for g in await self.bot.db.fetch('SELECT * FROM authorize') if self.bot.get_guild(int(g['guild_id']))])}`\n• members `{sum(g.member_count for g in self.bot.guilds):,}`")   
    await ctx.reply(embed=embed)
    
   @commands.hybrid_command(description="check bot connection", help="info")
   async def ping(self, ctx):
    await ctx.reply(f"....pong 🏓 `{self.bot.ping}ms`")
   
   @commands.hybrid_command(description="show credits to contributors of the bot", help="info")
   async def credits(self, ctx: commands.Context): 
     embed = discord.Embed(color=self.bot.color, description=f">>> **{self.bot.get_user(self.bot.owner_ids[0])}** - main developer of the bot\n**{self.bot.get_user(self.bot.owner_ids[1])}** - bot showcaser & website developer\n**{self.bot.get_user(928364018870136902)}** - created the bot's emojis\n**{self.bot.get_user(352190010998390796)}** - helped with many features that use rival's api\n**{self.bot.get_user(211999419036336131)}** - helped growing the bot\n**{self.bot.get_user(288748368497344513)}** - day one").set_author(icon_url=self.bot.user.display_avatar, name="contributors of pretend")
     await ctx.reply(embed=embed)

   @commands.hybrid_command(description="invite the bot", help="info", aliases=["support", "inv"])
   async def invite(self, ctx):
    avatar_url = self.bot.user.avatar.url
    embed = discord.Embed(color=self.bot.color, description="Add the bot in your server!")
    embed.set_author(name=self.bot.user.name, icon_url=f"{avatar_url}")
    button1 = Button(label="invite", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands")
    button2 = Button(label="support", url="https://discord.gg/4D5zzsYcUx")
    view = View()
    view.add_item(button1)
    view.add_item(button2)
    await ctx.reply(embed=embed, view=view)

async def setup(bot) -> None:
    await bot.add_cog(info(bot))      
