import discord
import requests
import platform
import animec
import asyncio
import datetime
import humanize
import random
from googleapiclient.discovery import build
from urllib.parse import quote
from typing import Union
from discord.ui import Button, View
from discord.ext import commands

now = datetime.datetime.now()
my_system = platform.uname()


def human_format(number):
    if number > 999:
        return humanize.naturalsize(number, False, True)
    return number


class TikTokLinkBUtton(discord.ui.Button):
    def __init__(self, username: str, custom_emoji: Union[discord.Emoji, str] = None):
        self.username = username
        super().__init__(
            style=discord.ButtonStyle.link,
            label=None,
            url=f"https://www.tiktok.com/@{self.username}?lang=en",
            emoji=custom_emoji,
        )


class YoutubeButton(discord.ui.Button):
    def __init__(
        self, channel_name: str, custom_emoji: Union[discord.Emoji, str] = None
    ):
        self.channel_name = channel_name
        super().__init__(
            style=discord.ButtonStyle.link,
            label=None,
            url=f"https://www.youtube.com/channel/{quote(self.channel_name)}",
            emoji=custom_emoji,
        )


class socials(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube = build(
            "youtube", "v3", developerKey="AIzaSyCSSiHIlwCYEE17VCV5Ig4SdvVsvngafdA"
        )

    @commands.command(
        name="youtube",
        description="Show info about youtube profile",
        aliases=["yt", "tube", "you"],
        usage="youtube [user]",
    )
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def youtube(self, ctx, *, username):
        search_request = self.youtube.search().list(
            part="id", q=username, type="channel"
        )
        search_response = search_request.execute()
        if not search_response["items"]:
            embed = discord.Embed(
                title="<:icons_Wrong:1135642272092926054> Error",
                description=f"> *`Could not find a youtube channel with the uername {username}`*",
                color=0x4C5264,
            )
            await ctx.send(embed=embed)
            return
        channel_id = search_response["items"][0]["id"]["channelId"]
        channel_request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics", id=channel_id
        )
        channel_response = channel_request.execute()
        channel = channel_response["items"][0]
        title = channel["snippet"]["title"]
        description = channel["snippet"]["description"]
        subs = int(channel["statistics"]["subscriberCount"])
        videos = int(channel["statistics"]["videoCount"])
        views = int(channel["statistics"]["viewCount"])
        thumbnail_url = channel["snippet"]["thumbnails"]["high"]["url"]
        country = channel["snippet"].get("country", "Unknown")
        created_at = channel["snippet"]["publishedAt"]
        embed = discord.Embed(
            title=f"<:youtube:1136548217891332207> {title}", color=0x4C5264
        )
        user = ctx.author
        embed.set_author(name=str(user.name), icon_url=user.display_avatar.url)
        embed.add_field(name="Description", value=f">>> *{description}*")
        embed.add_field(name="Subscribers", value=f"> `{subs:,}`", inline=False)
        embed.add_field(name="Videos", value=f">>> `{videos:,}`", inline=False)
        embed.add_field(name="Views", value=f">>> `{views:,}`", inline=False)
        embed.add_field(name="Country", value=f">>> `{country}`", inline=False)
        embed.add_field(
            name="Channel Created At", value=f">>> `{created_at}`", inline=False
        )
        embed.set_thumbnail(url=thumbnail_url)

        button = YoutubeButton(
            channel_id, custom_emoji="<:youtube:1136548217891332207>"
        )
        view = discord.ui.View()
        view.add_item(button)

        await ctx.send(embed=embed, view=view)

    @commands.command(
        name="tiktok",
        description="Show info about tiktok profile",
        aliases=["tic", "tik", "tok", "toc", "tt"],
        usage="tiktok [user]",
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def fetch_tiktok_profile(self, ctx, username):
        url = f"https://www.tiktok.com/@{username}?lang=en"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title="<:icons_Wrong:1135642272092926054> Error",
                description=f">>> ***{e}***",
                color=0x4C5264,
            )
            await ctx.send(embed=embed)
            return

        html = response.text
        try:
            nickname = html.split('nickname":"')[1].split('"')[0]
            followers = html.split('followerCount":')[1].split(",")[0]
            following = html.split('followingCount":')[1].split(",")[0]
            likes = html.split('heartCount":')[1].split(",")[0]
            videos = html.split('videoCount":')[1].split(",")[0]
            bio = html.split('desc":"')[1].split('"')[0]
            profile_pic_url = html.split('og:image" content="')[1].split('"')[0]
        except IndexError as e:
            embed = discord.Embed(
                title="<:icons_Wrong:1135642272092926054> Error",
                description=f">>> ***{e}***",
                color=0x4C5264,
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"<:tiktok:1136548331280150628> {nickname}'s TikTok Stats",
            color=0x4C5264,
        )

        embed.set_thumbnail(url=profile_pic_url)

        embed.add_field(
            name="<:11_blackuser:1136548435282108537> Username",
            value=f"> *@{username}*",
            inline=False,
        )
        embed.add_field(
            name="<a:red:1136548505717067776> Posts",
            value=f"> `{videos}`",
            inline=False,
        )
        embed.add_field(
            name="<:icons_like:1136548580178538596> Likes",
            value=f"> `{likes}`",
            inline=False,
        )
        embed.add_field(
            name="<:icons_friends:1136548734201765918> Followers",
            value=f"> `{followers}`",
            inline=False,
        )
        embed.add_field(
            name="<:icons_friends:1136548734201765918> Following",
            value=f"> `{following}`",
            inline=False,
        )
        embed.add_field(
            name="<:icons_richpresence:1136548877126873149> Bio",
            value=f"> *{bio}*",
            inline=False,
        )

        button = TikTokLinkBUtton(
            username, custom_emoji="<:tiktok:1114291908659908719>"
        )
        view = discord.ui.View()
        view.add_item(button)

        await ctx.send(embed=embed, view=view)

    @commands.command(
        description="Shows information on an anime",
        usage="anime <name>",
        aliases=["ani"],
    )
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def anime(self, ctx, *, query):
        try:
            embed = discord.Embed(
                description=f"Fetching anime information", colour=0x4C5264
            )
            message = await ctx.reply(embed=embed)
            anime = animec.Anime(query)
        except:
            embed = discord.Embed(description="No results found")
            await ctx.reply(embed=embed)

        try:
            title = (
                str(anime.title_english)
                if str(anime.title_english)
                else str(anime.title_japanese)
            )
            embed = discord.Embed(
                title="Anime search results",
                url=anime.url,
                description=f"""**{str(anime.title_english)}**
**Description:** {anime.description[:500]}...""",
                colour=0x4C5264,
            )
            embed.add_field(
                name="General",
                value=f"""**Genres:** {str(anime.genres)}
**Aired:** {str(anime.aired)}
**Broadcast:** {str(anime.broadcast)}
**Popularity:** {str(anime.popularity)}""",
            )
            embed.add_field(
                name="Overview",
                value=f"""**Episodes:** {str(anime.episodes)}
**NSFW:** {str(anime.is_nsfw())}
**Status:** {str(anime.status)}""",
            )
            embed.add_field(
                name="Scores",
                value=f"""**Favorites:** {str(anime.favorites)}
**Rating:** {str(anime.rating)}
**Rank:** {str(anime.ranked)}""",
            )
            embed.set_thumbnail(url=anime.poster)
            embed.set_author(
                name=ctx.message.author.name, icon_url=ctx.message.author.avatar
            )
            await message.delete()
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(
        case_insensitive=True,
        aliases=["remind", "remindme", "remind_me"],
        description="Schedules a reminder to help you remind something",
        usage="reminder <something> <time>",
    )
    async def reminder(self, ctx, time, *, reminder):
        try:
            user = ctx.message.author
            embed = discord.Embed(colour=0x4C5264)

            seconds = 0
            if reminder is None:
                embed.description = f"{ctx.message.author.mention}: Specify something to be reminded about"
            if time.lower().endswith("d"):
                seconds += int(time[:-1]) * 60 * 60 * 24
                counter = f"{seconds // 60 // 60 // 24} days"
            if time.lower().endswith("h"):
                seconds += int(time[:-1]) * 60 * 60
                counter = f"{seconds // 60 // 60} hours"
            elif time.lower().endswith("m"):
                seconds += int(time[:-1]) * 60
                counter = f"{seconds // 60} minutes"
            elif time.lower().endswith("s"):
                seconds += int(time[:-1])
                counter = f"{seconds} seconds"
            if seconds == 0:
                embed.description = (
                    f"{ctx.message.author.mention}: Specify a proper duration"
                )
            elif seconds < 5:
                embed.description = (
                    f"{ctx.message.author.mention}: Minimum duration is 5 seconds"
                )
            elif seconds > 7776000:
                embed.description = (
                    f"{ctx.message.author.mention}: Maximum duration is 90 days"
                )
            else:
                embed = discord.Embed(
                    description=f"{ctx.message.author.mention}:<:icons_Correct:1136549254513561642> I will remind you about `{reminder}` in {counter}",
                    color=0x4C5264,
                )
                await ctx.reply(embed=embed)
                await asyncio.sleep(seconds)
                await ctx.reply(f"{ctx.message.author.mention}, {reminder}")
                return
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(
        description="Shows the latest anime news",
        usage="aninews",
        aliases=["animenews"],
    )
    async def aninews(self, ctx, amount: int = 4):
        try:
            embed = discord.Embed(description=f"Fetching anime news", colour=0x4C5264)
            message = await ctx.reply(embed=embed)
            await asyncio.sleep(1)
            news = animec.Aninews(amount)
            links = news.links
            titles = news.titles
            descriptions = news.description

            embed = discord.Embed(
                title="Latest Anime News",
                timestamp=datetime.datetime.utcnow(),
                colour=0x4C5264,
            )
            embed.set_thumbnail(url=news.images[0])

            for i in range(amount):
                embed.add_field(
                    name=f"{i+1}) {titles[i]}",
                    value=f"{descriptions[i][:200]}...\n[Read more]({links[i]})",
                    inline=False,
                )
            await message.delete()
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(socials(bot))
