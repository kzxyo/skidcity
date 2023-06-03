import discord, os, sys, asyncio, googletrans, datetime, math, textwrap, pathlib, typing, traceback, json, time, random, humanize, inspect
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import paginator as pg, utils


class skullboard(commands.Cog):
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
        self.sentmessages = {}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        try:
            if payload.emoji.name == "\N{SKULL}":

                if self.bot.db("skull").get(str(payload.guild_id)):

                    guild = self.bot.db("skull")[str(payload.guild_id)]

                    if guild.get("channel"):

                        channel = self.bot.get_channel(guild["channel"])
                        print(channel)
                        message = await (
                            self.bot.get_channel(payload.channel_id)
                        ).fetch_message(payload.message_id)
                        print(message)

                        reaction = [
                            reaction
                            for reaction in message.reactions
                            if reaction.emoji == "💀"
                        ]
                        if reaction:
                            reaction = reaction[0]
                        else:
                            return

                        embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
                        view = discord.ui.View().add_item(
                            discord.ui.Button(
                                style=discord.ButtonStyle.link,
                                label="message",
                                url=message.jump_url,
                            )
                        )

                        if not self.sentmessages.get(channel.id):

                            self.sentmessages[channel.id] = {}

                        if self.sentmessages.get(channel.id):

                            if self.sentmessages[channel.id].get(message.id):

                                bot_message = await channel.fetch_message(
                                    self.sentmessages[channel.id][message.id]
                                )

                                embed = bot_message.embeds[0]
                                embed.set_footer(
                                    text=f"{reaction.count} 💀 #{message.channel.name}"
                                )

                                return await bot_message.edit(embed=embed)

                        embed.set_author(
                            name=str(message.author),
                            icon_url=message.author.display_avatar,
                        )
                        embed.description = message.content

                        if message.attachments:

                            embed.set_image(url=message.attachments[0].proxy_url)

                        embed.set_footer(
                            text=f"{reaction.count} 💀 #{message.channel.name}"
                        )

                        msg = await channel.send(embed=embed, view=view)
                        self.sentmessages[channel.id][message.id] = msg.id
        except:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        try:
            if payload.emoji.name == "\N{SKULL}":

                if self.bot.db("skull").get(str(payload.guild_id)):

                    guild = self.bot.db("skull")[str(payload.guild_id)]

                    if guild.get("channel"):

                        channel = self.bot.get_channel(guild["channel"])
                        message = await (
                            self.bot.get_channel(payload.channel_id)
                        ).fetch_message(payload.message_id)

                        reaction = [
                            reaction
                            for reaction in message.reactions
                            if reaction.emoji == "💀"
                        ]
                        if reaction:
                            reaction = reaction[0]
                        else:
                            return

                        embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
                        view = discord.ui.View().add_item(
                            discord.ui.Button(
                                style=discord.ButtonStyle.link,
                                label="message",
                                url=message.jump_url,
                            )
                        )

                        if not self.sentmessages.get(channel.id):

                            self.sentmessages[channel.id] = {}

                        if self.sentmessages.get(channel.id):

                            if self.sentmessages[channel.id].get(message.id):

                                bot_message = await channel.fetch_message(
                                    self.sentmessages[channel.id][message.id]
                                )

                                embed = bot_message.embeds[0]
                                embed.set_footer(
                                    text=f"{reaction.count} 💀 #{message.channel.name}"
                                )

                                return await bot_message.edit(embed=embed)

        except:
            pass

    @commands.hybrid_group(name="skullboard", aliases=["skull"])
    @utils.perms("manage_guild")
    async def skullboard(self, ctx):

        ex = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        ex.set_author(name="skullboard", icon_url=self.bot.user.display_avatar)
        ex.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up the guild's skull board\n{self.reply} **aliases:** skull\n{self.reply} **functions:** on, off",
        )
        ex.add_field(
            name=f"{self.dash} Sub Cmds",
            value="```\n,skullboard channel - set the skullboard channel```",
            inline=False,
        )
        ex.set_footer(
            text=f"skull",
            icon_url=None,
        )
        await ctx.reply(embed=ex)

    @skullboard.command(name="channel")
    @utils.perms("manage_guild")
    async def skullboard_channel(self, ctx, channel: discord.TextChannel):

        if not self.bot.db("skull").get(str(ctx.guild.id)):
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** skullboard is **disabled** for this guild",
                )
            )

        db = self.bot.db("skull")
        guild = str(ctx.guild.id)
        db[guild]["channel"] = channel.id
        self.bot.db.put(db, "skull")
        await ctx.reply(":thumbsup:")

    @skullboard.command(name="on")
    @utils.perms("manage_guild")
    async def skullboard_on(
        self, ctx, channel: typing.Optional[discord.TextChannel] = None
    ):

        if self.bot.db("skull").get(str(ctx.guild.id)):
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** skullboard is already **enabled** for this guild",
                )
            )

        db = self.bot.db("skull")
        db[str(ctx.guild.id)] = {"channel": channel}
        self.bot.db.put(db, "skull")
        await ctx.reply(":thumbsup:")

    @skullboard.command(name="off")
    @utils.perms("manage_guild")
    async def skullboard_off(self, ctx):

        if not self.bot.db("skull").get(str(ctx.guild.id)):
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** skullboard is already **disabled** for this guild",
                )
            )

        db = self.bot.db("skull")
        db.pop(str(ctx.guild.id))
        self.bot.db.put(db, "skull")
        await ctx.reply(":thumbsup:")


async def setup(bot):
    await bot.add_cog(skullboard(bot))
