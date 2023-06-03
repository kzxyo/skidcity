import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class userEvents(commands.Cog):
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
        #
        self.av = "https://cdn.discordapp.com/attachments/989422588340084757/1008195005317402664/vile.png"

    @commands.Cog.listener()
    async def on_user_update(self, before, after):

        datacheck = self.bot.db("nodata")
        if datacheck.get(str(after.id)):
            if datacheck.get(str(after.id)).get("data") == False:
                return

        db = utils.read_json("names")
        if before.name != after.name:

            try:
                db[str(before.id)]["names"].append(
                    f"{before.name}#{before.discriminator} • <t:{int(datetime.now().timestamp())}:R>"
                )
                utils.write_json(db, "names")
            except:
                db[str(before.id)] = {"names": []}
                db[str(before.id)]["names"].append(
                    f"{before.name}#{before.discriminator} • <t:{int(datetime.now().timestamp())}:R>"
                )
                utils.write_json(db, "names")
                pass

            try:
                db = utils.read_json("tags")
                if (
                    before.discriminator != after.discriminator
                    and before.discriminator == "0001"
                ):
                    db["tt"][
                        f"{before.name}#{before.discriminator}"
                    ] = datetime.now().timestamp()
                    utils.write_json(db, "tags")
            except:
                pass

        if before.display_avatar != after.display_avatar:

            try:
                ch = self.bot.get_channel(1021868675394969660)
                msg = await ch.send(
                    file=await before.display_avatar.to_file(
                        filename=f"avatar.{'png' if not before.display_avatar.is_animated() else 'gif'}"
                    )
                )
                db = self.bot.db("avatarhistory")
                try:
                    db.get(str(before.id)).append(msg.attachments[0].proxy_url)
                    self.bot.db.put(db, "avatarhistory")
                except:
                    db[str(before.id)] = []
                    db.get(str(before.id)).append(msg.attachments[0].proxy_url)
                    self.bot.db.put(db, "avatarhistory")
            except:
                pass


async def setup(bot):
    await bot.add_cog(userEvents(bot))
