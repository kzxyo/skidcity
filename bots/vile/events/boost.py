import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class boostEvents(commands.Cog):
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
    async def on_message(self, message):

        if not message.guild:
            return

        guild = message.guild
        user = message.author
        if message.type == discord.MessageType.premium_guild_subscription:
            try:
                boost = self.bot.db("boost")[str(message.guild.id)]
                channels = boost["channel"]
                new = await utils.embed_replacement(message.author, boost["message"])
                objects = await utils.to_object(new)
                async for channel in utils.aiter(channels):
                    await channel.send(**objects)
            except:
                traceback.print_exc()


async def setup(bot):
    await bot.add_cog(boostEvents(bot))
