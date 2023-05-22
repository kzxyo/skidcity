import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import paginator as pg
from modules import utils
import math


class chat(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        #
        self.done = utils.emoji("done")
        self.fail = utils.emoji("fail")
        self.warn = utils.emoji("warn")
        self.reply = utils.emoji("reply")
        self.dash = utils.emoji("dash")
        #
        self.success = utils.color("done")
        self.error = utils.color("fail")
        self.warning = utils.color("warn")

    @commands.Cog.listener()
    async def on_message(self, message):

        try:
            db = self.bot.db("levels")
            author = message.author
            guild = message.guild
            if message.author.bot:
                return
            if db[str(guild.id)]["state"] == "on":
                try:
                    if not db.get(str(guild.id)).get(str(author.id)):
                        db.get(str(guild.id))[str(author.id)] = {}
                        db.get(str(guild.id))[str(author.id)]["experience"] = 0
                        db.get(str(guild.id))[str(author.id)]["level"] = 1
                        self.bot.db.put(db, "levels")
                except:
                    db.get(str(guild.id))[str(author.id)] = {}
                    db.get(str(guild.id))[str(author.id)]["experience"] = 0
                    db.get(str(guild.id))[str(author.id)]["level"] = 1
                    self.bot.db.put(db, "levels")

                db = self.bot.db("levels")
                db.get(str(guild.id)).get(str(author.id))[
                    "experience"
                ] += utils.xp_from_message(message)
                self.bot.db.put(db, "levels")
                db = self.bot.db("levels")
                exp = db.get(str(guild.id)).get(str(author.id))["experience"]
                lvl_start = db.get(str(guild.id)).get(str(author.id))["level"]
                lvl_end = utils.get_level(exp)

                if lvl_start == 100:
                    return
                if lvl_start < lvl_end:
                    db.get(str(guild.id)).get(str(author.id))["level"] = lvl_end
                    self.bot.db.put(db, "levels")
                    if db.get(str(guild.id))["message"] != None:
                        await message.reply(
                            db[str(guild.id)]["message"].format(
                                user=author,
                                level=db.get(str(guild.id)).get(str(author.id))[
                                    "level"
                                ],
                            )
                        )
        except:
            pass

        if message.content.startswith("vile ") or "tiktok.com/" in message.content:

            try:
                if "tiktok.com/" in message.content:
                    async with message.channel.typing():

                        link = [i for i in message.content.split() if 
'tiktok.com/' in i][0]
                        x = await self.bot.session.get(
                            f"https://api.rival.rocks/media/download", headers={'api-key': self.bot.rival_api}, params={"url": link}
                        )
                        video_data = await x.json()
                        duration = utils.moment(
                            (
                                datetime.now()
                                - timedelta(seconds=video_data["music"]["duration"])
                            ),
                            2,
                        )
                        embed = discord.Embed(color=utils.color("main"))
                        embed.description = f"{video_data['desc']}"
                        embed.set_author(
                            name=f"@{video_data['username']} | {duration.replace(' minutes', 'm').replace(' minute', 'm').replace(' seconds', 's').replace(' second', 's').replace(' and ', ' ')} long",
                            icon_url="https://cdn.discordapp.com/emojis/1017812426164551762.png?size=4096",
                            url=video_data["items"],
                        )
                        embed.set_footer(
                            text=f"💬 {video_data['stats']['comment_count']:,} | 👍 {video_data['stats']['digg_count']:,} | 🔗 {video_data['stats']['share_count']:,} ({video_data['stats']['play_count']:,} views)\n🎵 {video_data['music']['title']} (by {video_data['music']['author']})"
                        )
                    await message.reply(
                        file=await utils.file(video_data["items"], "viletiktok.mp4"),
                        embed=embed,
                    )
            except:
                pass

        # if message.content.startswith('vile '):
        #    if 'https://tiktok.com/' in message.content or 'https://www.tiktok.com/' in message.content:
        #        if '/video/' in message.content:
        #            async with message.channel.typing():
        #                x=message.content.strip('vile ')
        #                x=x.split('tiktok.com/')
        #                try:
        #                    x=x[1].split('?')[0]
        #                except:
        #                    x=x[1]
        #                ret=f'https://vm.dstn.to/{x}/video.mp4'
        #            await message.reply(ret)

        elif "instagram.com" in message.content and "/reel/" in message.content:
            async with message.channel.typing():
                from modules import instareel as instagram

                state, url, id = await instagram.check_url(message.content)
                await instagram.download(url, id)
            await message.reply(
                file=discord.File(fp=await instagram.binary(), filename="reel.mp4")
            )
            os.remove("reel.mp4")


async def setup(bot):
    await bot.add_cog(chat(bot))
