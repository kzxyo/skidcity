import discord, os, pytube
from discord.ext import commands
#from modules.youtube import Downloader
from modules.errors import *

class utility(commands.Cog, description = "see utility commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(extras={"Category": "Utility"}, usage="translate !language !text", help="Translate a word or a text", aliases=["tr"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def translate(self, ctx, lang: str=None, *, text: str=None):
        if lang is None or text is None:
            raise Var("lang or text")
        src = ctx.translate(to_lang=lang, arg=text)
        await ctx.reply(embed=discord.Embed(color=ctx.get_color(1), title=f"Translated from **{src[1].title()}** to **{lang.title()}**", description=f"- {src[0]}"))
        
    #@commands.command(extras={"Category": "Utility"}, usage="ytdownload !youtube link", help="Donwload a video from youtube")
    #@commands.cooldown(1, 10, commands.BucketType.user)
    async def ytdownload(self, ctx, link: str):
        downloader = Downloader("ip", "name", "pass") # YOUR PROXY
        pytube.request.default_downloader = downloader
        try:
            yt = pytube.YouTube(link)
            stream = yt.streams.get_highest_resolution()
            stream.download(filename="youtube.mp4")
            await ctx.reply(file=discord.File("youtube.mp4"))
            path = os.path.abspath("youtube.mp4")
            os.remove(path)
        except Exception as e:
            await ctx.error(e)
            
    @commands.command(extras={"Category": "Utility"}, usage="stackoverflow !id", help="Get an Stack Overflow user with id")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stackoverflow(self, ctx, id: int=None):
        if id is None:
            raise Var("id")
        await ctx.typing()
        data = await self.bot.http.get(f"https://api.stackexchange.com/2.3/users/{id}?order=desc&sort=reputation&site=stackoverflow")
        try:
            username= data['items'][0]['display_name']
            url = data['items'][0]['link']
        except:
            username = 'Unknown'
            url = None
        embed = discord.Embed(title=username, url=url)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(utility(bot))
