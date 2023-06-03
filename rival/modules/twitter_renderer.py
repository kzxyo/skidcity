import io
import re

import arrow, datetime
import discord
from modules.asynciterations import aiter
from modules import log
from modules import queries

import logging
logger = logging.getLogger(__name__)


class TwitterRenderer:
    def __init__(self, bot):
        self.bot = bot

    async def tweet_cdn_data(self, tweet_id: int) -> dict:
        URL = "https://cdn.syndication.twimg.com/tweet?id={}"
        async with self.bot.session.get(URL.format(tweet_id)) as response:
            response.raise_for_status()
            return await response.json()

    async def embed_tweet(self, tweet_id: int, channel:discord.TextChannel) -> None:
        """Format and send a tweet to given discord channels"""
        tweet = await self.tweet_cdn_data(tweet_id)
        timestamp = arrow.get(tweet["created_at"])
        screen_name = tweet["user"]["screen_name"]
        av=tweet['user']['profile_image_url_https']
        tweet_link = f"https://twitter.com/{screen_name}/status/{tweet_id}"

        if int(tweet["id_str"]) != tweet_id:
            logger.warning(f"Got id {tweet['id_str']}, Possible retweet {tweet_link}")
        caption=" "


        files_per_max_size = {}
        
        content = discord.Embed(description="", color=int("1ca1f1", 16), timestamp=datetime.datetime.now()).set_author(name=screen_name, icon_url=av).set_footer(icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
        try:
            parent_id = tweet["in_reply_to_status_id_str"]
            parent_screen_name = tweet["in_reply_to_screen_name"]
            parent_link = f"https://twitter.com/{parent_screen_name}/status/{parent_id}"
            content.description += f"> [*in reply to @{parent_screen_name}*]({parent_link})\n"

            return

        except KeyError:
            pass

        if not tweet_config["media_only"]:
            tweet_text = self.replace_links(tweet)
            if tweet_text:
                content.description += tweet_text + "\n"

        content.description += f"[View on Twitter]({tweet_link})"

            # discord normally has 8MB file size limit, but it can be increased in some guilds
            # try to send the best version in each guild without unnecessary downloading
        max_filesize = getattr(channel.guild, "filesize_limit", 8388608)
        if files_per_max_size.get(max_filesize):
            files, too_big_files = files_per_max_size[max_filesize]
        else:
            files, too_big_files = await self.extract_files(tweet, max_filesize)
            files_per_max_size[max_filesize] = (files, too_big_files)

        if not files and not too_big_files and tweet_config["media_only"]:
            return

        caption += "\n" + "\n".join(too_big_files)
        await channel.send(files=files, embed=content)

    async def send_tweet(self, tweet_id: int, channels: list[discord.TextChannel]) -> None:
        """Format and send a tweet to given discord channels"""
        logger.info(f"sending {tweet_id} into {', '.join(f'#{c}' for c in channels)}")
        tweet = await self.tweet_cdn_data(tweet_id)
        timestamp = arrow.get(tweet["created_at"])
        screen_name = tweet["user"]["screen_name"]
        av=tweet['user']['profile_image_url_https']
        tweet_link = f"https://twitter.com/{screen_name}/status/{tweet_id}"

        if int(tweet["id_str"]) != tweet_id:
            logger.warning(f"Got id {tweet['id_str']}, Possible retweet {tweet_link}")
        caption=" "


        files_per_max_size = {}
        async for channel in aiter(channels):
            tweet_config = await queries.tweet_config(
                self.bot.db, channel, tweet["user"]["id_str"]
            )
            content = discord.Embed(description="", color=int("1ca1f1", 16), timestamp=datetime.datetime.now()).set_author(name=screen_name, icon_url=av).set_footer(icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
            try:
                parent_id = tweet["in_reply_to_status_id_str"]
                parent_screen_name = tweet["in_reply_to_screen_name"]
                parent_link = f"https://twitter.com/{parent_screen_name}/status/{parent_id}"
                content.description += f"> [*in reply to @{parent_screen_name}*]({parent_link})\n"

                return

            except KeyError:
                pass

            if not tweet_config["media_only"]:
                tweet_text = self.replace_links(tweet)
                if tweet_text:
                    content.description += tweet_text + "\n"

            content.description += f"[View on Twitter]({tweet_link})"

            # discord normally has 8MB file size limit, but it can be increased in some guilds
            # try to send the best version in each guild without unnecessary downloading
            max_filesize = getattr(channel.guild, "filesize_limit", 8388608)
            if files_per_max_size.get(max_filesize):
                files, too_big_files = files_per_max_size[max_filesize]
            else:
                files, too_big_files = await self.extract_files(tweet, max_filesize)
                files_per_max_size[max_filesize] = (files, too_big_files)

            if not files and not too_big_files and tweet_config["media_only"]:
                return

            caption += "\n" + "\n".join(too_big_files)
            await channel.send(files=files, embed=content)

    @staticmethod
    def replace_links(tweet: dict) -> str:
        indices = []
        for url in tweet["entities"]["urls"]:
            indices.append((*url["indices"], url["expanded_url"]))

        try:
            for url in tweet["entities"]["media"]:
                indices.append((*url["indices"], ""))
        except KeyError:
            pass

        if indices:
            s = tweet["text"]
            res = []
            i = 0
            for start, end, replacement in indices:
                res.append(s[i:start] + replacement)
                i = end
            res.append(s[end:])
            tweet_text = "".join(res)
        else:
            tweet_text = tweet["text"]

        return tweet_text.strip()

    @staticmethod
    def sort_videos(video: dict) -> int:
        width, height = re.findall(r"[/](\d*)x(\d*)[/]", video["src"])[0]
        res = int(width) * int(height)
        return res

    async def extract_files(
        self, tweet: dict, max_filesize: int
    ) -> tuple[list[discord.File], list[str]]:
        media_urls = []
        files = []
        too_big_files = []
        if tweet.get("video"):
            videos = list(filter(lambda x: x["type"] == "video/mp4", tweet["video"]["variants"]))
            if len(videos) > 1:
                best_src = sorted(videos, key=self.sort_videos)[-1]["src"]
            else:
                best_src = videos[0]["src"]
            media_urls.append(("mp4", best_src))

        for photo in tweet.get("photos", []):
            base, extension = photo["url"].rsplit(".", 1)
            media_urls.append(("jpg", base + "?format=" + extension + "&name=orig"))

        for n, (extension, media_url) in enumerate(media_urls, start=1):
            timestamp = arrow.get(tweet["created_at"])
            screen_name = tweet["user"]["screen_name"]
            filename = (
                f"{timestamp.format('YYMMDD')}-@{screen_name}-{tweet['id_str']}-{n}.{extension}"
            )
            async with self.bot.session.get(media_url) as response:
                if int(response.headers.get("content-length", max_filesize)) > max_filesize:
                    too_big_files.append(media_url)
                else:
                    buffer = io.BytesIO(await response.read())
                    files.append(discord.File(fp=buffer, filename=filename))

        return files, too_big_files