import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class memberEvents(commands.Cog):
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
    async def on_member_join(self, member):

        guild = member.guild
        user = member
        try:
            welcome = self.bot.db("welcome")[str(member.guild.id)]
            new = await utils.embed_replacement(member, welcome["message"])
            objects = await utils.to_object(new)
            async for channel in utils.aiter(welcome["channel"]):
                channel = member.guild.get_channel(channel)
                await channel.send(**objects)

        except:
            pass

        try:
            autorole = self.bot.db("autorole")[str(member.guild.id)]
            async for role in utils.aiter(autorole):
                r = member.guild.get_role(role)
                try:
                    await member.add_roles(r, reason="autorole")
                except:
                    pass
        except:
            pass


async def setup(bot):
    await bot.add_cog(memberEvents(bot))
