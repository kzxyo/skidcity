import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class guildEvents(commands.Cog):
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
    async def on_guild_join(self, guild):

        try:
            x = self.bot.get_channel(1002618168897970197)
            await x.send(
                f"joined **{guild.name}**, owned by **{guild.owner}**, **{guild.member_count}** members"
            )
        except:
            pass
        blacklisted = utils.read_json("blacklisted")
        if guild.id in blacklisted["servers"]:
            return await guild.leave()

        mc = len(guild.members)
        if mc < 10:
            try:
                async for logs in guild.audit_logs(
                    limit=1,
                    after=datetime.now() - timedelta(seconds=3),
                    action=discord.AuditLogAction.bot_add,
                ):
                    toDM = logs.user
                await toDM.send(
                    f"you can't add vile to a server with less than 20 members"
                )
            except:
                pass
            if guild.id != 593071828369408011:
                await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        try:
            async for table in utils.aiter(os.listdir("db")):
                try:
                    db = utils.read_json(table[:-5])
                    db.pop(str(guild.id))
                except:
                    continue
        except:
            pass


async def setup(bot):
    await bot.add_cog(guildEvents(bot))
