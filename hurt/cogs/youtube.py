import os
import discord
import asyncio
import requests
import uuid
import json
from discord.ext import commands
from pytube import YouTube


class yt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube_data_api_key = "AIzaSyB0xagOTb78tqWR-2hmUD1STMufjdFBACY"
        self.download_lock = asyncio.Lock()
        self.downloading_videos = set()

        self.db_folder = os.path.join(os.getcwd(), "db")
        self.guilds_file = os.path.join(self.db_folder, "guilds.json")
        self.guilds_data = {}
        if os.path.exists(self.guilds_file):
            with open(self.guilds_file, "r") as f:
                self.guilds_data = json.load(f)

    @commands.command(aliases=["d"])
    async def download(self, ctx, url):
        try:
            if url in self.downloading_videos:
                embed = discord.Embed(
                    description="**Sorry command loop, video already being downloaded** <:icons_Wrong:1135642272092926054>",
                    color=discord.Color.red(),
                )
                status_message = await ctx.send(embed=embed)
                await asyncio.sleep(3)
                await status_message.delete()
                return

            async with self.download_lock:
                self.downloading_videos.add(url)

                video = YouTube(url)
                video_stream = video.streams.filter(
                    file_extension="mp4", progressive=True
                ).first()

                embed = discord.Embed(
                    description="**Ok video downloading Currently**  <:icons_Download:1136897800903331942>",
                    color=discord.Color.yellow(),
                )
                status_message = await ctx.send(embed=embed)

                guild_folder = os.path.join(os.getcwd(), "vids", str(ctx.guild.id))
                os.makedirs(guild_folder, exist_ok=True)

                random_filename = str(uuid.uuid4()) + ".mp4"
                custom_filepath = os.path.join(guild_folder, random_filename)

                video_stream.download(
                    output_path=guild_folder, filename=random_filename
                )

                video_id = video.video_id
                stats = self.get_video_stats(video_id)

                message_content = (
                    f"**Video downloaded successfully** <:lean_wock:1136754041569955880>\n"
                    f"**Video Title:** {video.title}\n"
                    f"**Artist:** {self.get_video_artist(video.description)}\n"
                    f"**Views:** {stats.get('views', 'N/A')}\n"
                    f"**Likes:** {stats.get('likes', 'N/A')}\n"
                    f"**Dislikes:** {stats.get('dislikes', 'N/A')}\n"
                    f"**Comments:** {stats.get('comments', 'N/A')}"
                )

                await ctx.send(file=discord.File(custom_filepath))

                embed = discord.Embed(
                    description=message_content, color=discord.Color.purple()
                )
                await ctx.send(embed=embed)

                if ctx.author.voice and ctx.author.voice.channel:
                    voice_channel = ctx.author.voice.channel
                    voice_client = await voice_channel.connect()

                    audio_source = discord.FFmpegPCMAudio(custom_filepath)
                    voice_client.play(
                        discord.PCMVolumeTransformer(audio_source, volume=0.5)
                    )

                self.guilds_data[str(ctx.guild.id)] = guild_folder

                with open(self.guilds_file, "w") as f:
                    json.dump(self.guilds_data, f)

                await status_message.delete()

                self.downloading_videos.remove(url)

        except Exception as e:
            self.downloading_videos.remove(url)
            await ctx.send(f"Error: {e}")

    def get_video_stats(self, video_id):
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "key": self.youtube_data_api_key,
            "part": "statistics",
            "id": video_id,
        }

        response = requests.get(url, params=params, verify=True, timeout=10)
        data = response.json()

        if "items" not in data or len(data["items"]) == 0:
            return {}

        statistics = data["items"][0]["statistics"]

        stats = {
            "views": statistics.get("viewCount", 0),
            "likes": statistics.get("likeCount", 0),
            "dislikes": statistics.get("dislikeCount", 0),
            "comments": statistics.get("commentCount", 0),
        }

        return stats

    def get_video_artist(self, description):
        return "Unknown"


async def setup(bot):
    await bot.add_cog(yt(bot))
