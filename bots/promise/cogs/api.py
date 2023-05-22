import discord, time, datetime, psutil, requests
from discord.ext import commands
from discord.ui import View, Button, Select
from core.utils.classes import Colors

session = requests.Session()

global start

class api(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    

    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lizard(self, ctx):
     url = f"https://nekos.life/api/v2/img/lizard"
     resp = session.get(url)
     js = resp.json()
     embed=discord.Embed(color=Colors.green)
     embed.set_image(url=js['url'])
     await ctx.reply(embed=embed)
    
    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def goose(self, ctx):
     url = f"https://nekos.life/api/v2/img/goose"
     resp = session.get(url)
     js = resp.json()
     embed=discord.Embed(color=Colors.green)
     embed.set_image(url=js['url'])
     await ctx.reply(embed=embed)
        
    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cat(self, ctx):
     url = f"https://nekos.life/api/v2/img/meow"
     resp = session.get(url)
     js = resp.json()
     embed=discord.Embed(color=Colors.green)
     embed.set_image(url=js['url'])
     await ctx.reply(embed=embed)
        
    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dog(self, ctx):
     url = f"https://nekos.life/api/v2/img/woof"
     resp = session.get(url)
     js = resp.json()
     embed=discord.Embed(color=Colors.green)
     embed.set_image(url=js['url'])
     await ctx.reply(embed=embed)
        
    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nekopat(self, ctx):
     url = f"https://nekos.life/api/v2/img/pat"
     resp = session.get(url)
     js = resp.json()
     embed=discord.Embed(color=Colors.green)
     embed.set_image(url=js['url'])
     await ctx.reply(embed=embed)
        
    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nekofox(self, ctx):
     url = f"https://nekos.life/api/v2/img/fox_girl"
     resp = session.get(url)
     js = resp.json()
     embed=discord.Embed(color=Colors.green)
     embed.set_image(url=js['url'])
     await ctx.reply(embed=embed)
        
    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nekoimg(self, ctx):
     url = f"https://nekos.life/api/v2/img/neko"
     resp = session.get(url)
     js = resp.json()
     embed=discord.Embed(color=Colors.green)
     embed.set_image(url=js['url'])
     await ctx.reply(embed=embed)
        
    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nekogif(self, ctx):
     url = f"https://nekos.life/api/v2/img/ngif"
     resp = session.get(url)
     js = resp.json()
     embed=discord.Embed(color=Colors.green)
     embed.set_image(url=js['url'])
     await ctx.reply(embed=embed)
        
async def setup(bot):
    await bot.add_cog(api(bot))