import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class reactionEvents(commands.Cog):
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
    async def on_raw_reaction_add(self, payload):

        try:
            db = utils.read_json("reactionrole")
            x = db[str(payload.member.guild.id)]
            async for z in utils.aiter(x):
                if payload.message_id == z["msg"]:
                    member = payload.member
                    guild = member.guild
                    if (
                        payload.emoji.name
                        == discord.utils.get(guild.emojis, id=z["emoji"]).name
                    ):
                        await member.add_roles(
                            discord.utils.get(guild.roles, id=z["role"]),
                            reason=f"reaction role: triggered by {member}",
                        )
        except:
            # traceback.print_exc()
            pass

        if payload.message_id == 1001017957301882930:
            member = payload.member
            guild = member.guild
            if payload.emoji.name == "0_hrt":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="waste"),
                    reason=f"verification: triggered by {member}",
                )

        if payload.message_id == 1004334585544445992:
            member = payload.member
            guild = member.guild
            if payload.emoji == "💎":
                await member.add_roles(
                    discord.utils.get(guild.roles, id=1003744482962968590),
                    reason=f"verification: triggered by {member}",
                )

        if payload.message_id == 1001023002965708850:
            member = payload.member
            guild = member.guild
            if payload.emoji.name == "0_headphone":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="18+"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "0_key2":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="<18"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "0_bf":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="male"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "0_heart4":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="female"),
                    reason=f"reaction role: triggered by {member}",
                )

        if payload.message_id == 1001026355745525891:
            member = payload.member
            guild = member.guild
            if payload.emoji.name == "0_pink":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="pi"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "💜":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="pu"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "🧡":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="o"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "💚":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="g"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "💙":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="b"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "♥":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="r"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "💛":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="y"),
                    reason=f"reaction role: triggered by {member}",
                )

        if payload.message_id == 1001027615349551104:
            member = payload.member
            guild = member.guild
            if payload.emoji.name == "0_heart4":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="pm"),
                    reason=f"reaction role: triggered by {member}",
                )

        if payload.message_id == 1001028437420560384:
            member = payload.member
            guild = member.guild
            if payload.emoji.name == "0_kirby":
                await member.add_roles(
                    discord.utils.get(guild.roles, name="upld"),
                    reason=f"reaction role: triggered by {member}",
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        try:
            db = utils.read_json("reactionrole")
            x = db[str(payload.guild_id)]
            async for z in utils.aiter(x):
                if payload.message_id == z["msg"]:
                    guild = await self.bot.fetch_guild(payload.guild_id)
                    member = await guild.fetch_member(payload.user_id)
                    if (
                        payload.emoji.name
                        == discord.utils.get(guild.emojis, id=z["emoji"]).name
                    ):
                        await member.remove_roles(
                            discord.utils.get(guild.roles, id=z["role"]),
                            reason=f"reaction role: triggered by {member}",
                        )
        except:
            # traceback.print_exc()
            pass

        if payload.message_id == 1001017957301882930:
            guild = await self.bot.fetch_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            if payload.emoji.name == "0_hrt":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="waste"),
                    reason=f"verification: triggered by {member}",
                )

        if payload.message_id == 1004334585544445992:
            guild = await self.bot.fetch_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            if payload.emoji == "💎":
                await member.remove_roles(
                    discord.utils.get(guild.roles, id=1003744482962968590),
                    reason=f"verification: triggered by {member}",
                )

        if payload.message_id == 1001023002965708850:
            guild = await self.bot.fetch_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            if payload.emoji.name == "0_headphone":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="18+"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "0_key2":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="<18"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "0_bf":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="male"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "0_heart4":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="female"),
                    reason=f"reaction role: triggered by {member}",
                )

        if payload.message_id == 1001026355745525891:
            guild = await self.bot.fetch_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            if payload.emoji.name == "0_pink":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="pi"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "💜":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="pu"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "🧡":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="o"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "💚":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="g"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "💙":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="b"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "♥":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="r"),
                    reason=f"reaction role: triggered by {member}",
                )
            elif payload.emoji.name == "💛":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="y"),
                    reason=f"reaction role: triggered by {member}",
                )

        if payload.message_id == 1001027615349551104:
            guild = await self.bot.fetch_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            if payload.emoji.name == "0_heart4":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="pm"),
                    reason=f"reaction role: triggered by {member}",
                )

        if payload.message_id == 1001028437420560384:
            guild = await self.bot.fetch_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            if payload.emoji.name == "0_kirby":
                await member.remove_roles(
                    discord.utils.get(guild.roles, name="upld"),
                    reason=f"reaction role: triggered by {member}",
                )


async def setup(bot):
    await bot.add_cog(reactionEvents(bot))
