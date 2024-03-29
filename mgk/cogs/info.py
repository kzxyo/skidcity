import discord, psutil, platform, datetime, humanize
from discord.ext import commands
from mgk.cfg import E
from modules.func import member

class info(commands.Cog, description = "see information commands"):
    def __init__(self, bot):
        self.bot = bot
   
    @commands.command(extras={"Category": "Info"}, usage="ping", help="View bot latency", aliases=["latency", "ms"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):
        await ctx.embed(description=f"latency: `{round(self.bot.latency * 1000)}`**ms** on **{ctx.guild.shard_id}** shard")
        
    @commands.command(extras={"Category": "Info"}, usage="botinfo", help="View information about bot", aliases=["bi", "info"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def botinfo(self, ctx):
        cogs = []
        for c in self.bot.cogs:
            if c not in ["help", "dev", "events", "Jishaku", "ready", "guild"]:
                cogs.append(c)
        embed = discord.Embed(description=f"**{self.bot.user.name}** is a bot with {len(cogs)} categories ``(use {ctx.prefix}help to see categories/commands)``. **{self.bot.user.name}** run **{len(self.bot.guilds)}** guilds and **{sum(len(guild.members) for guild in self.bot.guilds)}** users. Discord.py version is **{discord.__version__}** and py version **{platform.python_version()}**. Bot use **MariaDB 10.11.3**. Host is 🔥 and cpu percent is **{psutil.cpu_percent()}**, memory percent is **{psutil.virtual_memory().percent}**", color=ctx.get_color(1))
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)
        
    @commands.command(extras={"Category": "Info"}, usage="uptime", help="View how long the bot is online")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def uptime(self, ctx):
        current = datetime.datetime.utcnow()
        uptime = current - self.bot.uptime
        await ctx.embed(description=f"I'm alive! **{humanize.precisedelta(uptime)}**")
        
    @commands.command(extras={"Category": "Info"}, usage="invite *bot", help="Get link to invite this bot or a bot", aliases=["inv"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def invite(self, ctx, bot: discord.User=None):
        if bot:
            if bot.bot == False:
                return await ctx.error("you provide a user")
            else:
                button = discord.ui.Button(emoji=E.invite, style=discord.ButtonStyle.url, url=f"https://discord.com/api/oauth2/authorize?client_id={bot.id}&permissions=8&scope=bot%20applications.commands")
                view = discord.ui.View()
                view.add_item(button)
                return await ctx.reply(f"broo you want to invite **{bot.name}**, instead of **{self.bot.user.name}**", view=view)
        else:
            button = discord.ui.Button(emoji=E.invite, style=discord.ButtonStyle.url, url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands")
            view = discord.ui.View()
            view.add_item(button)
            await ctx.reply(embed=discord.Embed(description=f"press on button 2 invite **{self.bot.user.name}**", color=ctx.get_color(1)), view=view)
            
       
async def setup(bot):
    await bot.add_cog(info(bot))
