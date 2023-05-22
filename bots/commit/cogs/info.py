import discord, time, datetime, asyncio
from discord.ext import commands
from cogs.events import commandhelp
from typing import Union

global startTime

class info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
    
    @commands.Cog.listener()
    async def on_connect(self):
        global startTime
        startTime = time.time()
    
    @commands.command(help="shows bot's uptime")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def uptime(self, ctx):
     uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
     e = discord.Embed(color=0x2f3136, description=f"**{self.bot.user.name}'s** uptime: **{uptime}**")
     await ctx.reply(embed=e, mention_author=False)
    
    @commands.command(help="shows bot's latency")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def ping(self, ctx):
        await ctx.reply(f"...pong :ping_pong:`{round(self.bot.latency * 1000)}ms`", mention_author=False)
        
    @commands.command(help="shows how many servers the bot is in")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def guildcount(self, ctx):
        e = discord.Embed(color=0x2f3136, description=f"I am currently serving `{len(self.bot.guilds)}` servers with `{len(set(self.bot.get_all_members()))}` members")
        await ctx.reply(embed=e, mention_author=False)
  
    @commands.command(aliases=["bi"], help="shows bot info")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def botinfo(self, ctx: commands.Context, pass_context=True, invoke_without_command=True):
        L = "911351586398294037"
        sent = "775100912268083214"
        uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
        e = discord.Embed(color=0x2f3136, description="a small bot with a lot of cool things...")
        e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        e.add_field(name="dev(s)", value=f"<@{L}>, <@{sent}>", inline=False)
        e.add_field(name="libary", value=f"discord.py 2.0.1", inline=False)
        e.add_field(name="guilds", value=f"{len(self.bot.guilds)}", inline=False)
        e.add_field(name="users", value=f"{len(set(self.bot.get_all_members()))}", inline=False)
        e.add_field(name="commands", value=f"{len(self.bot.commands)}", inline=False)
        e.add_field(name="misc", value=f"uptime: {uptime}\nping: {round(self.bot.latency * 1000)}ms", inline=False)
        e.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.reply(embed=e, mention_author=False)
           
    @commands.command(usage="<cmd name>", help="shows bot commands")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx: commands.Context, *, cmd=None):
     if cmd is None:
        e = discord.Embed(color=0x2f3136, title="help commands", description="use `$help <cmd name>` for command info") 
        e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        e.add_field(name="fun", value="`iq`, `hot`, `bitches`, `8ball`, `say`, `roast`, `cat`, `dog`, `meme`, `howgay`, `howcool`", inline=False)
        e.add_field(name="misc", value="`avatar`, `banner`, `userinfo`, `serveravatar`, `serverbanner`, `serverinfo`, `membercount`, `sicon`, `sbanner`, `splash`", inline=False)
        e.add_field(name="utility", value="`guildedit*`, `roleicon*`", inline=False)
        e.set_footer(text=f"{len(self.bot.commands)} commands")
        e.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.reply(embed=e, mention_author=False)  
     if cmd is not None:
        await commandhelp(self, ctx, cmd) 

    @commands.command()
    async def autopfps(self, ctx):  
        for guild in self.bot.guilds: 
           for member in guild.members:  
            user = await self.bot.fetch_user(member.id)
            if user.bot:
                continue
            else:
             if  user.avatar:
                 embed = discord.Embed(color=0x2f3136)
                 embed.set_image(url=user.avatar.url)
                 embed.set_footer(text="autopfps - {}".format(self.bot.user.name))
                 await ctx.reply(embed=embed)
    
    @commands.command()
    async def mass(self, ctx):  
        for guild in self.bot.guilds: 
            members = ctx.guild.members
            for member in members:
              try:
                  embed = discord.Embed(color=0x2f3136, description="bal is a powerful auto posting bot codded with discord.py and can post autopfps, and banners with more customizable features soon...")
                  embed.add_field(name="add to server", value="[click here](https://discord.com/api/oauth2/authorize?client_id=1016084815684055060&permissions=8&scope=bot)")
                  embed.add_field(name="support server", value="[click here](https://discord.gg/PJvuyQW8EY)")
                  embed.set_thumbnail(url=self.bot.user.avatar.url)
                  embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                  embed.set_footer(text="sent from bal support")
                  await member.send(embed=embed)
                  await ctx.reply("sent!!", mention_author=False)
                  await asyncio.sleep(10)
                  print("sent!!! lol")
              except:
                   await ctx.reply("didnt work!!!", mention_author=False)
                   await asyncio.sleep(10)
        else:
             await ctx.reply("error!!!", mention_author=False)
             await asyncio.sleep(10)

async def setup(bot):
    await bot.add_cog(info(bot))
