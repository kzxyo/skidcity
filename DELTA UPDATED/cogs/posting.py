import discord, json, random, aiohttp, datetime, requests, io
from discord.ext import commands
from datetime import timedelta, timezone
from datetime import datetime

session = requests.Session()

async def for_you():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://undefined.rip/api/1.0/tiktok/EN") as feed_request:
                res = await feed_request.json()
        videos = []
        for vid in res:
            formatted_video_data = await video_data_formatter(vid)
            videos.append(formatted_video_data)
        return videos
    except json.JSONDecodeError as e:
        print(e)

    
async def video_data_formatter(video_data):
    data = {"download_urls": {}, "author": {}, "stats": {}, "music": {}}
    data["created_at_timestamp"] = video_data["create_time"]
    data["created_at"] = str(datetime.fromtimestamp(video_data["create_time"]))
    data["video_url"] = f'https://tiktok.com/@{video_data["author"]["unique_id"]}/video/{video_data["aweme_id"]}'
    data["video_id"] = video_data["aweme_id"]
    data["download_urls"]["no_watermark"] = video_data['video']['play_addr']['url_list'][0]
    data["download_urls"]["watermark"] = video_data["video"]["play_addr"]["url_list"][2]
    data["author"]["avatar_url"] = video_data["author"]["avatar_larger"]["url_list"][0].replace("webp", "jpeg")
    data["author"]["username"] = video_data["author"]["unique_id"]
    data["author"]["nickname"] = video_data["author"]["nickname"]
    data["author"]["sec_uid"] = video_data["author"]["sec_uid"]
    data["author"]["user_id"] = video_data["author"]["uid"]
    data["description"] = video_data["desc"]
    data["video_length"] = video_data["video"]["duration"]/1000
    data["stats"] = {
        "comment_count": video_data["statistics"]["comment_count"],
        "likes": video_data["statistics"]["digg_count"],
        "downloads": video_data["statistics"]["download_count"],
        "views": video_data["statistics"]["play_count"],
        "shares": video_data["statistics"]["share_count"],
    }
    data["music"] = {
        "music_id": video_data["music"]["mid"],
        "album": video_data["music"]["album"],
        "title": video_data["music"]["title"],
        "author": video_data["music"]["author"],
         "length": video_data["music"]["duration"] 
     }
    return data

class poster(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(description="shows a for you tiktok video", help="utility")
    async def fyp(self, ctx):
        async with ctx.typing():
            fyp_videos = await for_you()
            videos = []
            for video in fyp_videos:
                videos.append(video)
            data = random.choice(videos)
            download = data["download_urls"]["no_watermark"]
            async with aiohttp.ClientSession() as session:
                async with session.get(download) as r:
                    downloaded_data = await r.read()
            file = discord.File(io.BytesIO(downloaded_data), filename=f"{self.bot.user.name}.mp4")
            comments = "{:,}".format(data['stats']['comment_count'])
            likes = "{:,}".format(data['stats']['likes'])
            shares = "{:,}".format(data['stats']['shares'])
            await ctx.reply(embed=discord.Embed(title="FYP Tiktok Video", color=self.bot.color).set_footer(text=f"💬 {comments} | ❤️ {likes} | 🔗 {shares} | 👤 {ctx.author}", icon_url="https://media.discordapp.net/attachments/1136728813674430528/1143966118868963388/multi_coloured_star.png"),file=file, mention_author=False)
            return
        
    
async def setup(bot):
    await bot.add_cog(poster(bot))