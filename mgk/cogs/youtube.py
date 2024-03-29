import discord, pyyoutube, os, pathlib, youtube_dl
from discord.ext import commands
from pyyoutube import Api
from dotenv import load_dotenv
from modules.errors import Var

load_dotenv(dotenv_path=pathlib.Path("mgk/.ENV"))

class youtube(commands.Cog, description = "see youtube commands"):
    def __init__(self, bot):
        self.bot = bot
        self.api = Api(api_key=os.getenv("YTB"))
        
    @commands.command(extras={"Category": "Youtube"}, usage="youtube !channel name", help="view information about a youtube channel", aliases=["ytb", "yt"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def youtube(self, ctx, *, username: str=None):
        try:
            id = self.api.get_channel_info(for_username=username).items[0].id
            data = self.api.get_channel_info(channel_id=id).items[0].to_dict()
            e = discord.Embed(color=ctx.get_color(1), title=data['snippet']['title'], description=data['snippet']['description'], url=f"https://www.youtube.com/{data['snippet']['customUrl']}" if data['snippet']['customUrl'] is not None else f"https://www.youtube.com/channel/{data['id']}")
            e.set_thumbnail(url=data['snippet']['thumbnails']['default']['url'])
            await ctx.reply(embed=e)
        except:
            await ctx.error("i can't find this youtuber")
            
    @commands.command(extras={"Category": "Youtube"}, usage="ytdownload !video url", help="download a music from youtube")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ytdownload(self, ctx, url: str=None):
        if url is None:
            raise Var("url")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'./ytb/{ctx.guild.id}.%(ext)s',
            'noplaylist': True,
            'continue_dl': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', 
            },
                {'key': 'FFmpegMetadata'},
            ],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(song_url, download=True)
        
        
async def setup(bot):
    await bot.add_cog(youtube(bot))
