import discord, asyncio
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.command(description="check bot's latency", help="info")
    async def ping(self, ctx):
      return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"🛰 {ctx.author.mention}: latency `{self.bot.ping}ms`"))
    
    @commands.command(description="check for how long the bot has been running", help="info")
    async def uptime(self, ctx):
      return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"⏰ **{self.bot.user.name}** is running for **{self.bot.ext.uptime}**"))
    
    @commands.command(description="check informations about the bot", help="info", aliases=["bi", "about", "info"])
    async def botinfo(self, ctx):
      embed = discord.Embed(color=self.bot.color, title="vilan", description=f"Developed & Maintained by **{self.bot.get_user(994896336040239114).global_name}**").add_field(name="stats", value=f"• guilds: `{len(self.bot.guilds)}`\n• uptime: `{(self.bot.ext.uptime.split(','))[0]}`\n• commands: `{len(set(self.bot.walk_commands()))}`\n• ping: `{self.bot.ping}ms`\n• library: `disdick {discord.__version__}`\n• members: `{sum(g.member_count for g in self.bot.guilds):,}`").set_thumbnail(url=self.bot.user.avatar.url).set_author(name=ctx.author.global_name if ctx.author.global_name else ctx.author.name, icon_url=ctx.author.display_avatar.url)
      await ctx.reply(embed=embed)
    
    @commands.command(description="invite the bot in your server", help="info", aliases=["inv", "support"])
    async def invite(self, ctx):
      embed = discord.Embed(color=self.bot.color, description="invite the bot in your server!").set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
      view = discord.ui.View()
      view.add_item(discord.ui.Button(label="invite", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"))
      view.add_item(discord.ui.Button(label="support", url="https://discord.gg/kQcYeuDjvN"))
      await ctx.reply(embed=embed, view=view)
    
async def setup(bot):
    await bot.add_cog(Info(bot))