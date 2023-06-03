import asyncio
import sys,tweepy

import discord
from discord.ext import commands, tasks
from tweepy import StreamRule, Tweet
from tweepy.asynchronous import AsyncClient, AsyncStreamingClient

from modules import log
from modules import queries
from modules.twitter_renderer import TwitterRenderer

import logging
logger = logging.getLogger(__name__)

def from_creator(status):
    if hasattr(status, 'retweeted_status'):
        return False
    elif status.in_reply_to_status_id != None:
        return False
    elif status.in_reply_to_screen_name != None:
        return False
    elif status.in_reply_to_user_id != None:
        return False
    else:
        return True

def reply(status):
    if status.in_reply_to_user_id == None:
        return True
    else:
        return False

class RunForeverClient(AsyncStreamingClient):
    def __init__(self, bot, **kwargs):
        self.bot=bot
        self.twitter_renderer = TwitterRenderer(self.bot)
        super().__init__(**kwargs)

    def run_forever(self) -> asyncio.Task:
        async def task():
            while True:
                await self.filter(tweet_fields=["author_id"])
                if sys.exc_info()[0] == KeyboardInterrupt:
                    break

        return asyncio.create_task(task())

    async def on_tweet(self, tweet: Tweet) -> None:
        if reply(tweet):
            pass
        else:
            return
        if tweet.in_reply_to_user_id != None:
            return
        asyncio.ensure_future(self.send_to_channels(tweet))

    async def send_to_channels(self, tweet: Tweet):
        channel_ids = await queries.get_channels(self.bot.db, tweet.author_id)
        if not channel_ids:
            logger.warning(f"No channel ids found for user id {tweet.author_id} {tweet}")
            return

        channels = [self.bot.get_channel(c) for c in channel_ids]
        if not channels:
            logger.warning(f"Could not find channel ids within bot context for tweet {tweet}")
            return

        await self.twitter_renderer.send_tweet(tweet.id, channels)


class asyncstreamer(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        auth = tweepy.OAuthHandler("4R8BAE5oIi2PbmoVdSfAP7fQC", "caDyyTyOahyTTRjT59ZCYxBEbprOltC3HrtxhxOO9Ouv3m5VMR")
        auth.set_access_token("4259600601-RUI8J2afi16LCTgfPsRJ8jFtR5PDgxEc8s3oRnc", "nTWXjuMhnF3vFVLdgvbaMrvjkvQ4qfMAyBhCBzhM9Ax2v")
        self.twt = tweepy.API(auth)

    async def cog_load(self):
        self.api = AsyncClient(
            bearer_token="AAAAAAAAAAAAAAAAAAAAAHbRggEAAAAA%2BCuuSYLDtOOxpKmmYEgY96MF8KE%3DxgCBX8fwb0QXv8qMbOTFARy7oZirRb8QFaW3KO4wz4TDF3VxMP",
            wait_on_rate_limit=True,
        )
        self.stream = RunForeverClient(
            self.bot,
            bearer_token="AAAAAAAAAAAAAAAAAAAAAHbRggEAAAAA%2BCuuSYLDtOOxpKmmYEgY96MF8KE%3DxgCBX8fwb0QXv8qMbOTFARy7oZirRb8QFaW3KO4wz4TDF3VxMP",
        )
        self.stream.run_forever()
        self.refresh_loop.start()
        #self.nsfw_loop.start()

    @staticmethod
    def rule_builder(users: list[str]) -> list[StreamRule]:
        if len(users) == 0:
            return []

        suffix = "-is:retweet"
        rules = []
        rule_value = "from:" + str(users[0])
        for user in users[1:]:
            addition = " OR from:" + str(user)
            if len(rule_value + addition + suffix) <= 510:
                rule_value += addition
            else:
                rules.append(f"({rule_value}) {suffix}")
                rule_value = "from:" + str(user)
        if rule_value:
            rules.append(f"({rule_value}) {suffix}")

        return [StreamRule(value) for value in rules]

    def deconstruct_rules(self, rules: list[StreamRule]) -> list[str]:
        suffix = " -is:retweet"
        usernames = []
        for rule in rules:
            value = rule.value.removesuffix(suffix).strip("()")
            usernames += [x.split(":")[1] for x in value.split(" OR ")]
        return usernames

    async def cog_unload(self):
        self.stream.disconnect()
        #self.nsfw_loop.cancel()
        self.refresh_loop.cancel()

    @tasks.loop(minutes=1)
    async def refresh_loop(self):
        try:
            await self.check_for_filter_changes()
        except Exception as e:
            logger.error("Unhandled exception in refresh loop")
            logger.error(e)
            raise e

    @refresh_loop.before_loop
    async def before_refresh_loop(self):
        await self.bot.wait_until_ready()
        logger.info("Starting streamer refresh loop")

    @commands.command(name="twitterporn")
    async def twitterporn(self, ctx, index=1):
        ls=await self.bot.loop.run_in_executor(None, lambda: self.twt.home_timeline(limit=1))
        for t in ls:
            await TwitterRenderer.embed_tweet(t.id, ctx.channel)

    # @tasks.loop(minutes=15)
    # async def nsfw_loop(self):
    #     db=await self.bot.db.execute("""SELECT guild_id,channel_id FROM porn""")
    #     for guild_id,channel_id in db:
    #         g=self.bot.get_guild(int(guild_id))
    #         c=g.get_channel(int(channel_id))
    #         if c.is_nsfw():
    #             st=await self.bot.loop.run_in_executor(None, lambda: self.twt.home_timeline(limit=1))
    #             for t in st:
    #                 await TwitterRenderer.embed_tweet(t.id, c)
    #     logger.info("Posting NSFW Content To Channels")

    # @nsfw_loop.before_loop
    # async def before(self):
    #     await self.bot.wait_until_ready()
    #     logger.info("Starting NSFW Loop")

    async def replace_rules(self, current_rules: list[StreamRule], new_rules: list[StreamRule]):
        if current_rules:
            await self.stream.delete_rules([r.id for r in current_rules])
        if new_rules:
            await self.stream.add_rules(new_rules)
            logger.info(f"Added new ruleset {new_rules}")

    async def check_for_filter_changes(self):
        current_rules = await self.stream.get_rules()
        current_rules = current_rules.data or []
        followed_users = await queries.get_all_users(self.bot.db)
        current_users = self.deconstruct_rules(current_rules)
        if set(followed_users) != set(current_users):
            new_rules = self.rule_builder(followed_users)
            await self.replace_rules(current_rules, new_rules)


async def setup(bot):
    await bot.add_cog(asyncstreamer(bot))