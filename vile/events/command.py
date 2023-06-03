import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize, difflib
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils
from modules import logging


class DataBatchEntry(typing.TypedDict):
    guild: typing.Optional[int]
    channel: int
    author: int
    used: str
    prefix: str
    command: str
    failed: bool


class commandEvents(commands.Cog):
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
        #
        self._batch_lock = asyncio.Lock()
        self._data_batch: list[DataBatchEntry] = []

    @commands.Cog.listener()
    async def on_command(self, ctx):

        cache = utils.read_json("cache")
        cache["cmds"] += 1
        utils.write_json(cache, "cache")

        destination = (
            "Private Message" if not ctx.guild else f"#{ctx.channel} ({ctx.guild})"
        )
        channel = self.bot.get_channel(1039918538934190221)
        await channel.send(f"{ctx.author} in {destination}: **{ctx.message.content}**")
        # print(f"{command.author} | {command.command} | {command.guild.name}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound):
            x=[cmd.name.lower() for cmd in self.bot.commands]
            cmd=ctx.message.content.split()[0].strip('#')
            used=ctx.message.content.split()[0]
            
            z=difflib.get_close_matches(cmd, x)
            if z:
                p=ctx.prefix+z[0]
                embed=discord.Embed(color=self.bot.color)
                embed.description=f'{self.bot.fail} {ctx.author.mention}**:** {used} isnt a **valid** command, did you mean `{p}` instead?'
                
                await ctx.reply(embed=embed)

        if isinstance(error, commands.BotMissingPermissions):
            permissions = "\n".join(
                [x.lower() async for x in utils.aiter(error.missing_permissions)]
            )
            permissions = permissions.replace("_", " ")
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** i'm missing the **{permissions}** permission",
                )
            )

        elif isinstance(error, commands.MissingPermissions):
            permissions = "\n".join(
                [i.lower() async for i in utils.aiter(error.missing_permissions)]
            )
            permissions = permissions.replace("_", " ")
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** you're missing the **{permissions}** permission",
                )
            )

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("fail"),
                    description=f"{utils.emoji('fail')} {ctx.author.mention}**:** you're on a **[cooldown](https://discord.com/developers/docs/topics/rate-limits)** & cannot use `{ctx.invoked_with}` for another **{error.retry_after:.2f}** second(s)",
                ),
                delete_after=int(error.retry_after),
            )

        elif isinstance(error, commands.NotOwner):
            pass

        elif isinstance(error, commands.MemberNotFound):
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** please provide a **valid** member",
                )
            )

        elif isinstance(error, commands.UserNotFound):
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** please provide a **valid** user",
                )
            )

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** please provide a **valid** channel",
                )
            )

        elif isinstance(error, commands.RoleNotFound):
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** please provide a **valid** role",
                )
            )

        elif isinstance(error, commands.EmojiNotFound):
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** please provide a **valid** emoji",
                )
            )

        elif isinstance(error, commands.GuildNotFound):
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** please provide a **valid** guild",
                )
            )

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.BadInviteArgument):
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("warn"),
                    description=f"{utils.emoji('warn')} {ctx.author.mention}**:** please provide a **valid** invite",
                )
            )

        elif isinstance(error, commands.CheckFailure):
            try:
                if ctx.command.name in ctx.bot.db("disabled").get(str(ctx.guild.id)):
                    await ctx.reply(
                        embed=discord.Embed(
                            color=utils.color("warn"),
                            description=f"{utils.emoji('warn')} {ctx.author.mention}**:** that command is **disabled** in this guild",
                        )
                    )
            except:
                pass

        elif isinstance(error, commands.CommandInvokeError):
            pass

        elif isinstance(error, KeyError):

            embed = discord.Embed(
                color=utils.color("fail"),
                description=f"{utils.emoji('fail')} `undefined`",
            )
            await ctx.send(embed=embed)

        elif isinstance(error, TypeError):

            embed = discord.Embed(
                color=utils.color("fail"),
                description=f"{utils.emoji('fail')} `undefined`",
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                color=utils.color("fail"),
                description=f"{utils.emoji('fail')} `{type(error).__name__}: {str(error)}`",
            )
            await ctx.send(embed=embed)

        await self.register_command(ctx, "command.error")

    async def register_command(self, ctx, x):
        if ctx.command is None:
            return

        command = ctx.command.qualified_name
        message = ctx.message
        destination = None
        if ctx.guild is None:
            destination = "Private Message"
            guild_id = None
        else:
            destination = f"#{message.channel} ({message.guild})"
            guild_id = ctx.guild.id

        logging.info(f"{message.author} in {destination}: {message.content}", x)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        await self.register_command(ctx, "command.success")

        match ctx.command.name:
            case 'py':
                await ctx.reply('Promise { <pending> }')
            case 'eval':
                await ctx.reply('Promise { <pending> }')

async def setup(bot):
    await bot.add_cog(commandEvents(bot))
