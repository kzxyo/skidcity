import re
import discord, os, sys, asyncio, aiohttp, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class config(commands.Cog):
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

    @commands.hybrid_command(aliases=["prefix", "cp", "setprefix"])
    async def customprefix(self, ctx, stat: str = None, prefix=None):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="customprefix", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set up your own custom prefix for vile\n{self.reply} **aliases:** setprefix, prefix, cp\n{self.reply} **functions:** set, delete",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,prefix set\n,prefix delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="vile help menu", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set up your own custom prefix for vile\n{self.reply} **aliases:** setprefix, prefix, cp\n{self.reply} **functions:** set, delete",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,prefix set <prefix>\n{self.reply} **example:** ,prefix set glory",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="vile help menu", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set up your own custom prefix for vile\n{self.reply} **aliases:** setprefix, prefix, cp\n{self.reply} **functions:** set, delete",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,prefix delete\n{self.reply} **extra:** ping the bot to see your current prefix",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            if not stat:
                return await paginator.start()

            match stat:
                case 'set':
                    if not prefix:
                        return await ctx.reply(
                            embed=discord.Embed(
                                color=self.warning,
                                description=f"{utils.read_json('emojis')['warn']} please **provide** a prefix",
                            )
                        )

                    if len(prefix) > 10:
                        return await ctx.reply(
                            embed=discord.Embed(
                                color=self.warning,
                                description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please **provide** a prefix under 10 chars",
                            )
                        )

                    data = utils.read_json("prefixes")
                    data[str(ctx.author.id)] = {"prefix": prefix}
                    utils.write_json(data, "prefixes")

                    await ctx.reply(
                        embed=discord.Embed(
                            color=self.success,
                            description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}**:** your prefix has been set to **`{x['prefix']}`**",
                        )
                    )

                case 'delete':

                    data = utils.read_json("prefixes")
                    data.pop(str(ctx.author.id))
                    utils.write_json(data, "prefixes")

                    await ctx.reply(
                        embed=discord.Embed(
                            color=self.success,
                            description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}**:** your prefix has been deleted",
                        )
                    )
        except:
            pass

    @commands.hybrid_command(aliases=["gprefix", "gp", "setguildprefix"])
    @utils.perms("manage_guild")
    async def guildprefix(self, ctx, stat: str = None, prefix=None):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="guildprefix", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set up the guild's prefix\n{self.reply} **aliases:** setguildprefix, gprefix, gp\n{self.reply} **functions:** set, delete",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,guildprefix set\n,guildprefix delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="guildprefix", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set up the guild's prefix\n{self.reply} **aliases:** setguildprefix, gprefix, gp\n{self.reply} **functions:** set, delete",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,guildprefix set <prefix>\n{self.reply} **example:** ,guildprefix set glory",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="guildprefix", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set up the guild's prefix\n{self.reply} **aliases:** setguildprefix, gprefix, gp\n{self.reply} **functions:** set, delete",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,guildprefix delete\n{self.reply} **extra:** ping the bot to see your current prefix",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            if not stat:
                return await paginator.start()

            match stat:
                case 'set':
                    if not prefix:
                        return await ctx.reply(
                            embed=discord.Embed(
                                color=self.warning,
                                description=f"{utils.read_json('emojis')['warn']} please **provide** a prefix",
                            )
                        )

                    if len(prefix) > 5:
                        return await ctx.reply(
                            embed=discord.Embed(
                                color=self.warning,
                                description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please **provide** a prefix under 5 chars",
                            )
                        )

                    data = utils.read_json("guildprefixes")
                    data[str(ctx.guild.id)] = {"prefix": prefix}
                    utils.write_json(data, "guildprefixes")

                    await ctx.reply(
                        embed=discord.Embed(
                            color=self.success,
                            description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}**:** the prefix has been set to **`{x['prefix']}`**",
                        )
                    )

                case 'delete':

                    data = utils.read_json("guildprefixes")
                    data.pop(str(ctx.guild.id))
                    utils.write_json(data, "guildprefixes")

                    await ctx.reply(
                        embed=discord.Embed(
                            color=self.success,
                            description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}**:** your prefix has been deleted",
                        )
                    )
        except:
            pass

    @commands.hybrid_group(
        name="autoresponder",
        aliases=["autor", "ar", "autorespond"],
        invoke_without_command=True,
    )
    @utils.perms("manage_guild")
    async def autoresponder(self, ctx):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autoresponder", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,autoresponder add\n,autoresponder delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autoresponder add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,autoresponder add <trigger> <response>\n{self.reply} **example:** ,autoresponder add viile best bot",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autoresponder delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,autoresponder delete\n{self.reply} **extra:** ,autoresponder list",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            await paginator.start()
        except:
            pass

    @autoresponder.command(name="add")
    @utils.perms("manage_guild")
    async def autor_add(self, ctx, trigger: str = None, *, response: str = None):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autoresponder", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,autoresponder add\n,autoresponder delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autoresponder add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,autoresponder add <trigger> <response>\n{self.reply} **example:** ,autoresponder add viile best bot",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autoresponder delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,autoresponder delete\n{self.reply} **extra:** ,autoresponder list",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not trigger or not response:
                return await paginator.start()
            try:
                x = utils.read_json("autoresponder")
                x[str(ctx.guild.id)][str(trigger).lower()] = str(response)
                utils.write_json(x, "autoresponder")

            except:
                x = utils.read_json("autoresponder")
                x[str(ctx.guild.id)] = {}
                x[str(ctx.guild.id)][str(trigger).lower()] = str(response)
                utils.write_json(x, "autoresponder")

            embed = discord.Embed(color=self.success)
            embed.description = (
                f"{self.done} added an autoresponder **`{trigger}`** as: `{response}`"
            )
            await ctx.reply(embed=embed)
        except:
            pass

    @autoresponder.command(name="delete")
    @utils.perms("manage_guild")
    async def autor_delete(self, ctx, trigger: str = None):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autoresponder", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,autoresponder add\n,autoresponder delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autoresponder add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,autoresponder add <trigger> <response>\n{self.reply} **example:** ,autoresponder add vile best bot",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autoresponder delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto response\n{self.reply} **aliases:** autor, autorespond\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,autoresponder delete\n{self.reply} **extra:** ,autoresponder list",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not trigger:
                await paginator.start()
            db = utils.read_json("autoresponder")
            try:
                if not db[str(ctx.guild.id)].get(str(trigger).lower()):
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=self.error,
                            description=f"{self.fail} {ctx.author.mention}**:** no autoresponse with trigger `{trigger}` found",
                        )
                    )
                db[str(ctx.guild.id)].pop(str(trigger).lower())
                utils.write_json(db, "autoresponder")
            except:
                db[str(ctx.guild.id)] = {}
                utils.write_json(db, "autoresponder")
            # data = db[str(ctx.guild.id)]
            # db = data
            # if not db[str(trigger).lower()]: return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.fail} {ctx.author.mention}**:** no autoresponse with trigger `{trigger}` found"))
            # db.pop(str(trigger).lower())
            # utils.write_json(db, 'autoresponder')
            embed = discord.Embed(color=self.success)
            embed.description = f"{self.done} deleted the autoresponder **`{trigger}`**"
            await ctx.reply(embed=embed)
        except:
            pass

    @autoresponder.command(name="list")
    @utils.perms("manage_guild")
    async def autor_list(self, ctx):

        from modules import paginator as pg

        rows = []
        num = 0
        pagenum = 0
        embeds = []
        async for trigger, response in utils.aiter(
            utils.read_json("autoresponder")[str(ctx.guild.id)].items()
        ):
            num += 1
            rows.append(f"`{num}` **{trigger}**\n")
        pages = [p async for p in utils.aiter(discord.utils.as_chunks(rows, 10))]
        async for page in utils.aiter(pages):

            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x2F3136,
                    description=" ".join(page),
                    title=f"autoresponder list",
                    timestamp=datetime.now(),
                ).set_footer(
                    text=f"{pagenum}/{len(pages)} ({num} entries)",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
            )
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.hybrid_group(
        name="autoreact", aliases=["autoreaction"], invoke_without_command=True
    )
    @utils.perms("manage_guild")
    async def autoreact(self, ctx):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autoreaction", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,autoreaction add\n,autoreaction delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autoreaction add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,autoreaction add <trigger> <emoji>\n{self.reply} **example:** ,autoreaction add welc :f_welc:",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autoreaction delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"{self.reply} **syntax:** ,autoreaction delete\n{self.reply} **extra:** ,autoreaction list",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            await paginator.start()
        except:
            pass

    @autoreact.command(name="add")
    @utils.perms("manage_guild")
    async def autoreact_add(
        self, ctx, trigger: str = None, *, reaction: discord.Emoji = None
    ):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autoreaction", icon_url=self.bot.user.avatar)
            note.set_footer(text="config - 1/3")
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,autoreaction add\n,autoreaction delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autoreaction add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,autoreaction add <trigger> <emoji>\nExample: ,autoreaction add welc :f_welc:```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autoreaction delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,autoreaction delete\nExtra: ,autoreaction list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not trigger or not reaction:
                return await paginator.start()
            try:
                x = utils.read_json("autoreact")
                x[str(ctx.guild.id)][str(trigger).lower()].append(reaction.id)
                utils.write_json(x, "autoreact")

            except:
                x = utils.read_json("autoreact")
                try:
                    x[str(ctx.guild.id)][str(trigger).lower()] = []
                    x[str(ctx.guild.id)][str(trigger).lower()].append(reaction.id)
                    utils.write_json(x, "autoreact")
                except:
                    x[str(ctx.guild.id)] = {}
                    x[str(ctx.guild.id)][str(trigger).lower()] = []
                    x[str(ctx.guild.id)][str(trigger).lower()].append(reaction.id)
                    utils.write_json(x, "autoreact")

            embed = discord.Embed(color=self.success)
            embed.description = (
                f"{self.done} added an autoreaction **`{trigger}`** as {reaction}"
            )
            await ctx.reply(embed=embed)
        except:
            pass

    @autoreact.command(name="delete")
    @utils.perms("manage_guild")
    async def autoreact_delete(
        self, ctx, trigger: str = None, reaction: discord.Emoji = None
    ):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autoreaction", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,autoreaction add\n,autoreaction delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autoreaction add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,autoreaction add <trigger> <emoji>\nExample: ,autoreaction add welc :f_welc:```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autoreaction delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,autoreaction delete\nExtra: ,autoreaction list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not trigger or not reaction:
                await paginator.start()
            try:
                db = utils.read_json("autoreact")
                if not db[str(ctx.guild.id)][str(trigger).lower()]:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=self.error,
                            description=f"{self.fail} {ctx.author.mention}**:** no autoreaction with trigger `{trigger}` found",
                        )
                    )
                try:
                    db[str(ctx.guild.id)][str(trigger).lower()].remove(reaction.id)
                    utils.write_json(db, "autoreact")

                except:
                    x = utils.read_json("autoreact")
                    try:
                        x[str(ctx.guild.id)][str(trigger).lower()] = []
                        utils.write_json(x, "autoreact")
                    except:
                        x[str(ctx.guild.id)] = {}
                        x[str(ctx.guild.id)][str(trigger).lower()] = []
                        x[str(ctx.guild.id)][str(trigger).lower()].remove(reaction.id)
                        utils.write_json(x, "autoreact")

                data = db[str(ctx.guild.id)]
                db = data
                # if not db[str(trigger)]: return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.fail} {ctx.author.mention}**:** no autoreaction with trigger `{trigger}` found"))
            except:
                raise
            embed = discord.Embed(color=self.success)
            embed.description = f"{self.done} deleted autoreaction `{trigger}`"
            await ctx.reply(embed=embed)
        except:
            pass

    @autoreact.command(name="list")
    @utils.perms("manage_guild")
    async def autoreact_list(self, ctx):

        from modules import paginator as pg

        rows = []
        num = 0
        pagenum = 0
        embeds = []
        async for trigger in utils.aiter(
            utils.read_json("autoreact")[str(ctx.guild.id)].items()
        ):
            num += 1
            rows.append(f"`{num}` **{trigger[0]}**\n")
        pages = [p async for p in utils.aiter(discord.utils.as_chunks(rows, 10))]
        async for page in utils.aiter(pages):

            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x2F3136,
                    description=" ".join(page),
                    title=f"autoreaction list",
                    timestamp=datetime.now(),
                ).set_footer(
                    text=f"{pagenum}/{len(pages)} ({num} entries)",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
            )
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.hybrid_command(aliases=["sml", "modlogs"])
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def setmodlogs(self, ctx, channel: discord.TextChannel = None):

        if channel == None:

            e = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            e.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            e.set_author(name="setmodlogs", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set up the guild's mod-logs channel\n{self.reply} **aliases:** setmodlogs, sml, modlogs",
                inline=False,
            )
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ,setmodlogs <channel>\n{self.reply} example: ,setmodlogs #modlogs",
                inline=False,
            )
            await ctx.reply(embed=e)

        elif ctx.guild.get_channel(channel.id) != None:

            modlog = utils.read_json("modlog")

            modlog[str(ctx.guild.id)] = channel.id

            utils.write_json(modlog, "modlog")

            await ctx.reply(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}: **modlogs** channel binded to <#{channel.id}>",
                )
            )

            await self.bot.get_channel(modlog[str(ctx.guild.id)]).send(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}**:** all **modlog** actions will be logged in this channel",
                )
            )
        else:

            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please mention a **valid** logs channel",
                )
            )

    @commands.hybrid_command(aliases=["ic"])
    @utils.perms("manage_guild")
    async def ignorechannel(self, ctx, channel: discord.TextChannel = None):

        if not channel:

            e = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            e.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            e.set_author(name="ignorechannel", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** choose channels the bot wont respond in\n{self.reply} **aliases:** ignorechannel, ic",
                inline=False,
            )
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ,ignorechannel <channel>\n{self.reply} example: ,ignorechannel #msg",
                inline=False,
            )
            return await ctx.reply(embed=e)

        db = utils.read_json("ignorechannel")
        guild = str(ctx.guild.id)
        try:
            db[guild].append(channel.id)
            utils.write_json(db, "ignorechannel")
        except:
            db[guild] = []
            db[guild].append(channel.id)
            utils.write_json(db, "ignorechannel")

        await ctx.send(":thumbsup:")

    @commands.hybrid_command(aliases=["uic"])
    @utils.perms("manage_guild")
    async def unignorechannel(self, ctx, channel: discord.TextChannel = None):

        if not channel:

            e = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            e.set_footer(
                text="config",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            e.set_author(name="unignorechannel", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** undo the ignorechannel effect\n{self.reply} **aliases:** unignorechannel, uic",
                inline=False,
            )
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ,unignorechannel <channel>\n{self.reply} example: ,unignorechannel #msg",
                inline=False,
            )
            return await ctx.reply(embed=e)

        db = utils.read_json("ignorechannel")
        guild = str(ctx.guild.id)
        try:
            db[guild].remove(channel.id)
            utils.write_json(db, "ignorechannel")
        except:
            db[guild] = []
            db[guild].remove(channel.id)
            utils.write_json(db, "ignorechannel")

        await ctx.send(":thumbsup:")

    @commands.hybrid_command()
    @utils.perms("manage_guild")
    async def ignoredchannels(self, ctx):

        db = utils.read_json("ignorechannel")

        from modules import paginator as pg

        ret = []
        num = 0
        async for channel in utils.aiter(db[str(ctx.guild.id)]):
            ch = await ctx.guild.fetch_channel(channel)
            num += 1
            ret.append(f"`{num}` {ch.name}: {ch.mention} ( `{ch.id}` )\n")
            embed = discord.Embed(
                color=0x2F3136,
                description=" ".join(ret),
                title=f"ignored channels list",
                timestamp=datetime.now(),
            )
            embed.set_footer(text=f"1/1 ({num} entries)")
            fakeembed = discord.Embed(
                color=0x2F3136,
                description="undefined",
                title=f"ignored channels list",
                timestamp=datetime.now(),
            )
            fake1 = fakeembed.set_footer(
                text=f"2/1 ({num} entries)",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
        paginator = pg.Paginator(
            self.bot, [embed, fake1], ctx, timeout=30, invoker=None
        )
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("end", emoji=utils.read_json("emojis")["fail"])
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.hybrid_group(name="boost")
    @utils.perms("manage_guild")
    async def boost(self, ctx, *, msg: str = None):

        vars = "{user.tag} - the member's username#tag\n{user.mention} - mention the member\n{user.id} - the member's ID\n{user.avatar} - the member's avatar\n{guild.name} - the guild's name\n{guild.id} - the guild's ID"
        vars = f"```YAML\n{vars}```"
        if not msg:

            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="boost", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/5",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the boost module\n{self.reply} **sub commands:** toggle, message, channel, variables",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n,boost toggle\n,boost message\n,boost channel\n,boost variables```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="boost toggle", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/5",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** toggle the boost module\n{self.reply} **sub commands:** toggle, message, channel, variables",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,boost toggle \nExample: ,boost toggle```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="boost message", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/5",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set the boost message\n{self.reply} **sub commands:** toggle, message, channel, variables",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,autoreaction delete\nExtra: ,autoreaction list```",
                inline=False,
            )
            note4 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note4.set_author(name="boost channel", icon_url=self.bot.user.avatar)
            note4.set_footer(
                text="config - 4/5",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note4.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** set the boost channel\n{self.reply} **sub commands:** toggle, message, channel, variables",
                inline=False,
            )
            note4.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,boost channel (channel)\nExtra: ,boost channel #boosts```",
                inline=False,
            )
            note5 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note5.set_author(name="boost variables", icon_url=self.bot.user.avatar)
            note5.set_footer(
                text="config - 5/5",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note5.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete an auto reaction\n{self.reply} **sub commands:** toggle, message, channel, variables",
                inline=False,
            )
            note5.add_field(
                name="Variables",
                value=f"```YAML\n\nSyntax: ,autoreaction delete\nExtra: ,autoreaction list```",
                inline=False,
            )

            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

    @commands.hybrid_group(name="joindm", aliases=["jdm"], invoke_without_command=True)
    @utils.perms("manage_guild")
    async def joindm(self, ctx):

        return await ctx.send("currently disabled")
        from modules import paginator as pg

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="joindm", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="config - 1/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
            inline=False,
        )
        note.add_field(
            name="Sub Cmds",
            value=f"```YAML\n\n,joindm on\n,joindm off```",
            inline=False,
        )
        note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note2.set_author(name="joindm message", icon_url=self.bot.user.avatar)
        note2.set_footer(
            text="config - 2/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note2.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
            inline=False,
        )
        note2.add_field(
            name="Usage",
            value=f"```YAML\n\nSyntax: ,joindm message <message>\nExample: ,joindm message welc to the server```",
            inline=False,
        )
        note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note3.set_author(name="joindm variables", icon_url=self.bot.user.avatar)
        note3.set_footer(
            text="config - 3/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note3.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
            inline=False,
        )
        note3.add_field(
            name="Usage",
            value="```YAML\n\n{user.mention} - ping the user\n{user.name} - the name of the user\n{user.id} - the user's ID\n{guild.name} - the name of the guild\n{guild.icon} - the icon url of the guild\n{guild.id} - the guild's ID\n{guild.member_count} - the guild's member count\n{joinpos} - the user's join position```",
            inline=False,
        )
        paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))

        await paginator.start()

    @joindm.command(name="on")
    @utils.perms("manage_guild")
    async def joindm_on(self, ctx):

        return await ctx.send("currently disabled")
        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="joindm", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,joindm on\n,joindm off```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="joindm message", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,joindm message <message>\nExample: ,joindm message welc to the server```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="joindm variables", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value="```YAML\n\n{user.mention} - ping the user\n{user.name} - the name of the user\n{user.id} - the user's ID\n{guild.name} - the name of the guild\n{guild.icon} - the icon url of the guild\n{guild.id} - the guild's ID\n{guild.member_count} - the guild's member count\n{joinpos} - the user's join position```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            try:
                x = utils.read_json("joindm")
                x[str(ctx.guild.id)] = {
                    "state": "enabled",
                    "message": x[str(ctx.guild.id)]["message"],
                }
                utils.write_json(x, "joindm")

            except:
                x = utils.read_json("joindm")
                x[str(ctx.guild.id)] = {"state": "enabled", "message": ""}
                utils.write_json(x, "joindm")

            await ctx.reply(":thumbsup:")
        except:
            pass

    @joindm.command(name="off")
    @utils.perms("manage_guild")
    async def joindm_off(self, ctx):

        return await ctx.send("currently disabled")
        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="joindm", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,joindm on\n,joindm off```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="joindm message", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,joindm message <message>\nExample: ,joindm message welc to the server```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="joindm variables", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value="```YAML\n\n{user.mention} - ping the user\n{user.name} - the name of the user\n{user.id} - the user's ID\n{guild.name} - the name of the guild\n{guild.icon} - the icon url of the guild\n{guild.id} - the guild's ID\n{guild.member_count} - the guild's member count\n{joinpos} - the user's join position```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            try:
                x = utils.read_json("joindm")
                x[str(ctx.guild.id)] = {
                    "state": "disabled",
                    "message": x[str(ctx.guild.id)]["message"],
                }
                utils.write_json(x, "joindm")

            except:
                x = utils.read_json("joindm")
                x[str(ctx.guild.id)] = {"state": "disabled", "message": ""}
                utils.write_json(x, "joindm")

            await ctx.reply(":thumbsup:")
        except:
            pass

    @joindm.command(name="message", aliases=["msg"])
    @utils.perms("manage_guild")
    async def joindm_msg(self, ctx, *, msg: str = None):

        return await ctx.send("currently disabled")
        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="joindm", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,joindm on\n,joindm off```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="joindm message", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,joindm message <message>\nExample: ,joindm message welc to the server```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="joindm variables", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** manage the guild's joindm module\n{self.reply} **sub commands:** message, variables",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value="```YAML\n\n{user.mention} - ping the user\n{user.name} - the name of the user\n{user.id} - the user's ID\n{guild.name} - the name of the guild\n{guild.icon} - the icon url of the guild\n{guild.id} - the guild's ID\n{guild.member_count} - the guild's member count\n{joinpos} - the user's join position```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            if not msg:
                await paginator.start()

            try:
                x = utils.read_json("joindm")
                x[str(ctx.guild.id)] = {
                    "state": x[str(ctx.guild.id)]["state"],
                    "message": msg,
                }
                utils.write_json(x, "joindm")

            except:
                x = utils.read_json("joindm")
                x[str(ctx.guild.id)] = {"state": "disabled", "message": msg}
                utils.write_json(x, "joindm")

            await ctx.reply(":thumbsup:")
        except:
            pass

    @commands.hybrid_command(aliases=["banmsg"])
    @utils.perms("manage_guild")
    async def banmessage(self, ctx, *, msg: str = None):

        try:
            if not msg:

                from modules import paginator as pg

                lol = "{user.name} just got banned for {reason}"
                e = discord.Embed(color=0x2F3136, timestamp=datetime.now())
                e.set_footer(
                    text="config",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                e.set_author(name="banmessage", icon_url=self.bot.user.avatar)
                e.add_field(
                    name=f"{self.dash} Info",
                    value=f"{self.reply} **description:** set up the guild's mod-logs channel\n{self.reply} **aliases:** setmodlogs, sml, modlogs\n{self.reply} **extra:** setting itas 'none' removes the ban message",
                    inline=False,
                )
                e.add_field(
                    name=f"{self.dash} Usage",
                    value=f"{self.reply} syntax: ,banmessage <message>\n{self.reply} example: ,banmessage {lol}",
                    inline=False,
                )
                e2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
                e2.set_footer(
                    text="config",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                e2.set_author(
                    name="banmessage variables", icon_url=self.bot.user.avatar
                )
                e2.add_field(
                    name=f"{self.dash} Info",
                    value=f"{self.reply} **description:** set up the guild's mod-logs channel\n{self.reply} **aliases:** setmodlogs, sml, modlogs\n{self.reply} **extra:** setting itas 'none' removes the ban message",
                    inline=False,
                )
                e2.add_field(
                    name="Usage",
                    value="```YAML\n\n{user.mention} - ping the user\n{user.name} - the name of the user\n{user.id} - the user's ID\n{guild.name} - the name of the guild\n{guild.icon} - the icon url of the guild\n{guild.id} - the guild's ID\n{guild.member_count} - the guild's member count\n{mod.mention} - ping the moderator\n{mod.name} - the moderator's name\n{mod.id} - the moderator's ID\n{reason} - the reason for the ban```",
                    inline=False,
                )
                paginator = pg.Paginator(self.bot, [e, e2], ctx, invoker=None)
                paginator.add_button("first", emoji=utils.emoji("firstpage"))
                paginator.add_button("prev", emoji=utils.emoji("prevpage"))
                paginator.add_button("next", emoji=utils.emoji("nextpage"))
                paginator.add_button("last", emoji=utils.emoji("lastpage"))
                paginator.add_button("goto", emoji=utils.emoji("choosepage"))
                return await paginator.start()

            try:
                if msg != "none":
                    x = utils.read_json("banmessage")
                    x[str(ctx.guild.id)] = msg
                    utils.write_json(x, "banmessage")
                else:
                    try:
                        x = utils.read_json("banmessage")
                        x.pop(str(ctx.guild.id))
                        utils.write_json(x, "banmessage")
                    except:
                        pass
            except:
                pass

            await ctx.reply(":thumbsup:")
        except:
            pass

    @commands.hybrid_group(name="autorole", invoke_without_command=True)
    @utils.perms("manage_guild")
    async def autorole(self, ctx):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autorole", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name=f"{self.dash} Sub Cmds",
                value=f"```YAML\n\n,autorole add\n,autorole delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autorole add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,autorole add <role>\nExample: ,autorole add @members```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autorole delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,autorole delete\nExtra: ,autorole list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            await paginator.start()
        except:
            pass

    @autorole.command(name="add")
    @utils.perms("manage_guild")
    async def autorole_add(self, ctx, role: discord.Role = None):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autorole", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name=f"{self.dash} Sub Cmds",
                value=f"```YAML\n\n,autorole add\n,autorole delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autorole add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,autorole add <role>\nExample: ,autorole add @members```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autorole delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,autorole delete\nExtra: ,autorole list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not role:
                return await paginator.start()
            perms = [p[0] for p in role.permissions if p[1]]
            if (
                "manage_guild" in perms
                or "administrator" in perms
                or "manage_channels" in perms
                or "manage_roles" in perms
                or "manage_emojis" in perms
                or "manage_webhooks" in perms
                or "mention_everyone" in perms
                or "kick_members" in perms
                or "ban_members" in perms
            ):
                return await ctx.reply("nigga no")

            try:
                x = utils.read_json("autorole")
                x[str(ctx.guild.id)].append(role.id)
                utils.write_json(x, "autorole")

            except:
                x = utils.read_json("autorole")
                x[str(ctx.guild.id)] = []
                x[str(ctx.guild.id)].append(role.id)
                utils.write_json(x, "autorole")

            embed = discord.Embed(color=self.success)
            embed.description = (
                f"{self.done} successfully added autorole `{role.name}` "
            )
            await ctx.reply(embed=embed)
        except:
            pass

    @autorole.command(name="delete")
    @utils.perms("manage_guild")
    async def autorole_delete(self, ctx, role: discord.Role = None):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="autorole", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name=f"{self.dash} Sub Cmds",
                value=f"```YAML\n\n,autorole add\n,autorole delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="autorole add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,autorole add <role>\nExample: ,autorole add @members```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="autorole delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete an autorole\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,autorole delete\nExtra: ,autorole list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not role:
                await paginator.start()
            db = utils.read_json("autorole")
            try:
                db[str(ctx.guild.id)].remove(role.id)
                utils.write_json(db, "autorole")
                embed = discord.Embed(color=self.success)
                embed.description = (
                    f"{self.done} successfully deleted autorole `{role}`"
                )
                await ctx.reply(embed=embed)
            except:
                x = utils.read_json("autorole")
                x[str(ctx.guild.id)] = []
                utils.write_json(x, "autorole")
                embed = discord.Embed(color=self.success)
                embed.description = (
                    f"{self.done} successfully deleted autorole `{role}`"
                )
                await ctx.reply(embed=embed)
        except:
            pass

    @autorole.command(name="list")
    @utils.perms("manage_guild")
    async def autorole_list(self, ctx):

        from modules import paginator as pg

        rows = []
        num = 0
        pagenum = 0
        embeds = []
        async for b in utils.aiter(utils.read_json("autorole")[str(ctx.guild.id)]):
            num += 1
            b = ctx.guild.get_role(b)
            rows.append(f"`{num}` {b.mention}: **{b}** ( `{b.id}` )\n")
        pages = [p async for p in utils.aiter(discord.utils.as_chunks(rows, 10))]
        async for page in utils.aiter(pages):

            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x2F3136,
                    description=" ".join(page),
                    title=f"autorole list",
                    timestamp=datetime.now(),
                ).set_footer(
                    text=f"{pagenum}/{len(pages)} ({num} entries)",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
            )
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.hybrid_group(
        name="chatfilter", aliases=["cf", "filter"], invoke_without_command=True
    )
    @utils.perms("manage_guild")
    async def chatfilter(self, ctx):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="chatfilter", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name=f"{self.dash} Sub Cmds",
                value=f"```YAML\n\n,chatfilter add\n,chatfilter delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="chatfilter add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,chatfilter add <trigger>\nExample: ,chatfilter add nig ```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="chatfilter delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,chatfilter delete\nExtra: ,chatfilter list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            await paginator.start()
        except:
            pass

    @chatfilter.command(name="add")
    @utils.perms("manage_guild")
    async def chatfilter_add(self, ctx, trigger: str = None):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="chatfilter", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name=f"{self.dash} Sub Cmds",
                value=f"```YAML\n\n,chatfilter add\n,chatfilter delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="chatfilter add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,chatfilter add <trigger>\nExample: ,chatfilter add nig ```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="chatfilter delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,chatfilter delete\nExtra: ,chatfilter list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not trigger:
                return await paginator.start()
            try:
                x = utils.read_json("chatfilter")
                # if trigger in db[str(ctx.guild.id)]: return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.fail} {ctx.author.mention}**:** filter with trigger `{trigger}` already exists"))
                x[str(ctx.guild.id)].append(trigger)
                utils.write_json(x, "chatfilter")

            except:
                x = utils.read_json("chatfilter")
                x[str(ctx.guild.id)] = []
                x[str(ctx.guild.id)].append(trigger)
                utils.write_json(x, "chatfilter")

            embed = discord.Embed(color=self.success)
            embed.description = (
                f"{self.done} successfully added filter with trigger `{trigger}` "
            )
            await ctx.reply(embed=embed)
        except:
            pass

    @chatfilter.command(name="delete")
    @utils.perms("manage_guild")
    async def chatfilter_delete(self, ctx, trigger: str = None):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="chatfilter", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name=f"{self.dash} Sub Cmds",
                value=f"```YAML\n\n,chatfilter add\n,chatfilter delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="chatfilter add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,chatfilter add <trigger>\nExample: ,chatfilter add nig ```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="chatfilter delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a chat filter\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,chatfilter delete\nExtra: ,chatfilter list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not trigger:
                await paginator.start()
            try:
                db = utils.read_json("chatfilter")
                if trigger not in db[str(ctx.guild.id)]:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=self.error,
                            description=f"{self.fail} {ctx.author.mention}**:** no filter with trigger `{trigger}` found",
                        )
                    )
                try:
                    db[str(ctx.guild.id)].remove(trigger)
                    utils.write_json(db, "chatfilter")

                except:
                    db[str(ctx.guild.id)] = []
                    db[str(ctx.guild.id)].remove(trigger)
                    utils.write_json(db, "chatfilter")
                data = db[str(ctx.guild.id)]
                db = data
                # if not db[str(trigger)]: return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.fail} {ctx.author.mention}**:** no autoreaction with trigger `{trigger}` found"))
                embed = discord.Embed(color=self.success)
                embed.description = (
                    f"{self.done} successfully deleted filter with trigger `{trigger}`"
                )
                await ctx.reply(embed=embed)
            except:
                pass
        except:
            pass

    @chatfilter.command(name="list")
    @utils.perms("manage_guild")
    async def chatfilter_list(self, ctx):

        from modules import paginator as pg

        rows = []
        num = 0
        pagenum = 0
        embeds = []
        async for b in utils.aiter(utils.read_json("chatfilter")[str(ctx.guild.id)]):
            num += 1
            rows.append(f"`{num}` **{b}**\n")
        pages = [p async for p in utils.aiter(discord.utils.as_chunks(rows, 10))]
        async for page in utils.aiter(pages):

            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x2F3136,
                    description=" ".join(page),
                    title=f"chatfilter list",
                    timestamp=datetime.now(),
                ).set_footer(
                    text=f"{pagenum}/{len(pages)} ({num} entries)",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
            )
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.hybrid_group(
        name="welcome", aliases=["welc"], invoke_without_command=True
    )
    @utils.perms("manage_guild")
    async def welcome(self, ctx):

        ex = "{content:{user.mention} welcome}"
        note1 = discord.Embed(color=utils.color("main"), timestamp=datetime.now())
        note1.set_author(name=f"welcome", icon_url=self.bot.user.display_avatar)
        note1.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** manage the guild's welcome message\n{self.reply} **aliases:** welc\n{self.reply} **functions:** message, clear, test",
        )
        note1.add_field(
            name=f"{self.dash} Usage",
            value=f"{self.reply} **syntax:** ,welc message <code>\n{self.reply} **example:** ,welc message {ex}",
            inline=False,
        )
        note1.set_footer(
            text=f"config",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        await ctx.reply(embed=note1)

    @welcome.command(name="clear")
    @utils.perms("manage_guild")
    async def welcome_clear(self, ctx):

        try:
            db = utils.read_json("welcome")
            db.pop(str(ctx.guild.id))
            utils.write_json(db, "welcome")
        except:
            pass
        await ctx.reply(":thumbsup:")

    @welcome.command(name="channel")
    @utils.perms("manage_guild")
    async def welcome_channel(self, ctx, *, channel: discord.TextChannel):

        try:
            db = utils.read_json("welcome")
            if channel.id not in db[str(ctx.guild.id)]["channel"]:
                db[str(ctx.guild.id)]["channel"].append(channel.id)
            utils.write_json(db, "welcome")
        except:
            db = utils.read_json("welcome")
            msg = db.get(str(ctx.guild.id))
            if msg:
                msg = msg.get("message")
            db[str(ctx.guild.id)] = {"channel": [], "message": msg if msg else None}
            db[str(ctx.guild.id)]["channel"].append(channel.id)
            utils.write_json(db, "welcome")

        await ctx.send(":thumbsup:")

    @welcome.command(name="message", aliases=["msg"])
    @utils.perms("manage_guild")
    async def welcome_message(self, ctx, *, message: str = None):

        try:
            db = utils.read_json("welcome")
            db[str(ctx.guild.id)]["message"] = message
            utils.write_json(db, "welcome")
        except:
            db = utils.read_json("welcome")
            ch = db.get(str(ctx.guild.id))
            if ch:
                ch = ch.get("channel")
            db[str(ctx.guild.id)] = {"channel": ch if ch else None, "message": message}
            utils.write_json(db, "welcome")

        await ctx.send(":thumbsup:")

    @welcome.command(name="test")
    @utils.perms("manage_guild")
    async def welcome_test(self, ctx):

        try:
            self.bot.dispatch("member_join", ctx.author)
        except:
            pass
        await ctx.reply(":thumbsup:")

    @commands.hybrid_group(
        name="reactionrole", aliases=["rr"], invoke_without_command=True
    )
    @utils.perms("manage_guild")
    async def reactionrole(self, ctx):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="reactionrole", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,reactionrole add\n,reactionrole delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="reactionrole add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,reactionrole add <msg> <role> <emoji>\nExample: ,reactionrole add 1009122344725385346 @18+ :18:```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="reactionrole delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,reactionrole delete\nExtra: ,reactionrole list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            await paginator.start()
        except:
            pass

    @reactionrole.command(name="add")
    @utils.perms("manage_guild")
    async def reactionrole_add(
        self,
        ctx,
        msg: discord.Message = None,
        role: discord.Role = None,
        emoji: discord.Emoji = None,
    ):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="reactionrole", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,reactionrole add\n,reactionrole delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="reactionrole add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,reactionrole add <msg> <role> <emoji>\nExample: ,reactionrole add 1009122344725385346 @18+ :18:```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="reactionrole delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,reactionrole delete\nExtra: ,reactionrole list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not msg.id or not role.id or not emoji.id:
                await paginator.start()
            try:
                x = utils.read_json("reactionrole")
                x[str(ctx.guild.id)].append(
                    {"msg": msg.id, "role": role.id, "emoji": emoji.id}
                )
                utils.write_json(x, "reactionrole")

            except:
                x = utils.read_json("reactionrole")
                x[str(ctx.guild.id)] = []
                x[str(ctx.guild.id)].append(
                    {"msg": msg.id, "role": role.id, "emoji": emoji.id}
                )
                utils.write_json(x, "reactionrole")

            await msg.add_reaction(emoji)
            await ctx.reply(":thumbsup:")
        except:
            pass

    @reactionrole.command(name="delete")
    @utils.perms("manage_guild")
    async def reactionrole_delete(
        self, ctx, msg: discord.Message = None, role: discord.Role = None
    ):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="reactionrole", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name="Sub Cmds",
                value=f"```YAML\n\n,reactionrole add\n,reactionrole delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="reactionrole add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,reactionrole add <msg> <role> <emoji>\nExample: ,reactionrole add 1009122344725385346 @18+ :18:```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(name="reactionrole delete", icon_url=self.bot.user.avatar)
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create or delete a reaction role\n{self.reply} **aliases:** rr\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name="Usage",
                value=f"```YAML\n\nSyntax: ,reactionrole delete\nExtra: ,reactionrole list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            if not msg or not role:
                await paginator.start()
            db = utils.read_json("reactionrole")
            try:
                async for guild, reactionroles in utils.aiter(db.items()):
                    if guild == str(ctx.guild.id):
                        async for reactionrole in utils.aiter(reactionroles):
                            if (
                                reactionrole["msg"] == msg.id
                                and reactionrole["role"] == role.id
                            ):
                                db[guild].remove(reactionrole)
                utils.write_json(db, "reactionrole")
            except:
                db[str(ctx.guild.id)] = []
                utils.write_json(db, "reactionrole")
            # data = db[str(ctx.guild.id)]
            # db = data
            # if not db[str(trigger).lower()]: return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.fail} {ctx.author.mention}**:** no autoresponse with trigger `{trigger}` found"))
            # db.pop(str(trigger).lower())
            # utils.write_json(db, 'autoresponder')
            await ctx.reply(":thumbsup:")
        except:
            await ctx.reply(traceback.format_exc())

    @reactionrole.command(name="list")
    @utils.perms("manage_guild")
    async def reactionrole_list(self, ctx):

        from modules import paginator as pg

        ret = []
        num = 0
        # balls = str(utils.read_json('autoresponder')[str(ctx.guild.id)]).replace('{', '').replace('}', '').replace("'null': None", "").replace(', ', '\n').split(':')[1:]
        async for rr in utils.aiter(utils.read_json("reactionrole")[str(ctx.guild.id)]):
            num += 1
            ret.append(f"`{num}` **{rr['msg']}**")
            embed = discord.Embed(
                color=0x2F3136,
                description="\n".join(ret),
                title=f"reactionrole list",
                timestamp=datetime.now(),
            )
            embed.set_footer(text=f"1/1 ({num} entries)")
            fakeembed = discord.Embed(
                color=0x2F3136,
                description="undefined",
                title=f"reactionrole list",
                timestamp=datetime.now(),
            )
            fake1 = fakeembed.set_footer(
                text=f"2/1 ({num} entries)",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
        paginator = pg.Paginator(
            self.bot, [embed, fake1], ctx, timeout=30, invoker=None
        )
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("end", emoji=utils.read_json("emojis")["fail"])
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.group(
        name="fakepermissions",
        aliases=["fp", "fakepermission"],
        invoke_without_command=True,
    )
    @utils.perms("manage_guild")
    async def fakepermissions(self, ctx):

        try:
            from modules import paginator as pg

            note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note.set_author(name="fakepermissions", icon_url=self.bot.user.avatar)
            note.set_footer(
                text="config - 1/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note.add_field(
                name=f"{self.dash} Sub Cmds",
                value=f"```YAML\n\n,fakepermissions add\n,fakepermissions delete```",
                inline=False,
            )
            note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note2.set_author(name="fakepermissions add", icon_url=self.bot.user.avatar)
            note2.set_footer(
                text="config - 2/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note2.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note2.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,fakepermissions add <role> <permission>\nExample: ,fakepermissions add @mods ban_members```",
                inline=False,
            )
            note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            note3.set_author(
                name="fakepermissions delete", icon_url=self.bot.user.avatar
            )
            note3.set_footer(
                text="config - 3/3",
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            note3.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
                inline=False,
            )
            note3.add_field(
                name=f"{self.dash} Usage",
                value=f"```YAML\n\nSyntax: ,fakepermissions delete\nExtra: ,fakepermissions list```",
                inline=False,
            )
            paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
            paginator.add_button("first", emoji=utils.emoji("firstpage"))
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            paginator.add_button("last", emoji=utils.emoji("lastpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))

            await paginator.start()
        except:
            pass

    @fakepermissions.command(name="add")
    @utils.perms("manage_guild")
    async def fakepermissions_add(
        self, ctx, role: discord.Role = None, perm: str = None
    ):

        from modules import paginator as pg

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="fakepermissions", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="config - 1/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
            inline=False,
        )
        note.add_field(
            name=f"{self.dash} Sub Cmds",
            value=f"```YAML\n\n,fakepermissions add\n,fakepermissions delete```",
            inline=False,
        )
        note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note2.set_author(name="fakepermissions add", icon_url=self.bot.user.avatar)
        note2.set_footer(
            text="config - 2/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note2.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
            inline=False,
        )
        note2.add_field(
            name=f"{self.dash} Usage",
            value=f"```YAML\n\nSyntax: ,fakepermissions add <role> <permission>\nExample: ,fakepermissions add @mods ban_members```",
            inline=False,
        )
        note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note3.set_author(name="fakepermissions delete", icon_url=self.bot.user.avatar)
        note3.set_footer(
            text="config - 3/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note3.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
            inline=False,
        )
        note3.add_field(
            name=f"{self.dash} Usage",
            value=f"```YAML\n\nSyntax: ,fakepermissions delete\nExtra: ,fakepermissions list```",
            inline=False,
        )
        paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))

        if not role:
            return await paginator.start()
        if not perm:
            return await paginator.start()
        if perm not in [
            "add_reactions",
            "administrator",
            "attach_files",
            "ban_members",
            "change_nickname",
            "connect",
            "create_instant_invite",
            "create_private_threads",
            "create_public_threads",
            "deafen_members",
            "embed_links",
            "external_emojis",
            "external_stickers",
            "kick_members",
            "manage_channels",
            "manage_emojis",
            "manage_emojis_and_stickers",
            "manage_events",
            "manage_guild",
            "manage_messages",
            "manage_nicknames",
            "manage_permissions",
            "manage_roles",
            "manage_threads",
            "manage_webhooks",
            "mention_everyone",
            "moderate_members",
            "move_members",
            "mute_members",
            "priority_speaker",
            "read_message_history",
            "read_messages",
            "request_to_speak",
            "send_messages",
            "send_messages_in_threads",
            "send_tts_messages",
            "speak",
            "stream",
            "use_application_commands",
            "use_embedded_activities",
            "use_external_emojis",
            "use_external_stickers",
            "use_voice_activation",
            "value",
            "view_audit_log",
            "view_channel",
            "view_guild_insights",
        ]:
            return await ctx.reply("not a valid permission :thumbsdown:")

        try:
            x = utils.read_json("fakepermissions")
            x[str(ctx.guild.id)][str(role.id)].append(perm)
            utils.write_json(x, "fakepermissions")

        except:
            try:
                x = utils.read_json("fakepermissions")
                x[str(ctx.guild.id)][str(role.id)] = []
                x[str(ctx.guild.id)][str(role.id)].append(perm)
                utils.write_json(x, "fakepermissions")
            except:
                x = utils.read_json("fakepermissions")
                x[str(ctx.guild.id)] = {}
                utils.write_json(x, "fakepermissions")
                x = utils.read_json("fakepermissions")
                x[str(ctx.guild.id)][str(role.id)] = []
                x[str(ctx.guild.id)][str(role.id)].append(perm)
                utils.write_json(x, "fakepermissions")

        embed = discord.Embed(color=self.success)
        embed.description = f"{self.done} added fake perm to `{role.name}` "
        await ctx.reply(embed=embed)

    @fakepermissions.command(name="delete")
    @utils.perms("manage_guild")
    async def fakepermissions_delete(
        self, ctx, role: discord.Role = None, perm: str = None
    ):

        from modules import paginator as pg

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="fakepermissions", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="config - 1/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
            inline=False,
        )
        note.add_field(
            name=f"{self.dash} Sub Cmds",
            value=f"```YAML\n\n,fakepermissions add\n,fakepermissions delete```",
            inline=False,
        )
        note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note2.set_author(name="fakepermissions add", icon_url=self.bot.user.avatar)
        note2.set_footer(
            text="config - 2/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note2.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
            inline=False,
        )
        note2.add_field(
            name=f"{self.dash} Usage",
            value=f"```YAML\n\nSyntax: ,fakepermissions add <role> <permission>\nExample: ,fakepermissions add @mods ban_members```",
            inline=False,
        )
        note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note3.set_author(name="fakepermissions delete", icon_url=self.bot.user.avatar)
        note3.set_footer(
            text="config - 3/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note3.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up fake perms for the guild\n{self.reply} **sub commands:** add, delete, list",
            inline=False,
        )
        note3.add_field(
            name=f"{self.dash} Usage",
            value=f"```YAML\n\nSyntax: ,fakepermissions delete\nExtra: ,fakepermissions list```",
            inline=False,
        )
        paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))

        if not role:
            return await paginator.start()
        if not perm:
            return await paginator.start()
        if perm not in [
            "add_reactions",
            "administrator",
            "attach_files",
            "ban_members",
            "change_nickname",
            "connect",
            "create_instant_invite",
            "create_private_threads",
            "create_public_threads",
            "deafen_members",
            "embed_links",
            "external_emojis",
            "external_stickers",
            "kick_members",
            "manage_channels",
            "manage_emojis",
            "manage_emojis_and_stickers",
            "manage_events",
            "manage_guild",
            "manage_messages",
            "manage_nicknames",
            "manage_permissions",
            "manage_roles",
            "manage_threads",
            "manage_webhooks",
            "mention_everyone",
            "moderate_members",
            "move_members",
            "mute_members",
            "priority_speaker",
            "read_message_history",
            "read_messages",
            "request_to_speak",
            "send_messages",
            "send_messages_in_threads",
            "send_tts_messages",
            "speak",
            "stream",
            "use_application_commands",
            "use_embedded_activities",
            "use_external_emojis",
            "use_external_stickers",
            "use_voice_activation",
            "value",
            "view_audit_log",
            "view_channel",
            "view_guild_insights",
        ]:
            return await paginator.start()
        db = utils.read_json("fakepermissions")
        try:
            data = db[str(ctx.guild.id)]
        except:
            db[str(ctx.guild.id)] = {}
            utils.write_json(db, "fakepermissions")
        data = self.bot.db.get("fakepermissions").get(str(ctx.guild.id))
        db = data
        db[str(role.id)].remove(perm)
        utils.write_json(db, "fakepermissions")
        embed = discord.Embed(color=self.success)
        embed.description = f"{self.done} deleted fake perm from `{role.name}`"
        await ctx.reply(embed=embed)

    @fakepermissions.command(name="list")
    @utils.perms("manage_guild")
    async def fakepermissions_list(self, ctx):

        from modules import paginator as pg

        rows = []
        num = 0
        pagenum = 0
        embeds = []
        async for b in utils.aiter(
            utils.read_json("fakepermissions")[str(ctx.guild.id)]
        ):
            num += 1
            b = ctx.guild.get_role(int(b))
            rows.append(f"`{num}` {b.mention}: **{b}** ( `{b.id}` )\n")
        pages = [p async for p in utils.aiter(discord.utils.as_chunks(rows, 10))]
        async for page in utils.aiter(pages):

            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x2F3136,
                    description=" ".join(page),
                    title=f"fakepermission list",
                    timestamp=datetime.now(),
                ).set_footer(
                    text=f"{pagenum}/{len(pages)} ({num} entries)",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
            )
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            x = self.bot.db.get("pingonjoin")
            for channel in x.get(str(member.guild.id))["channels"]:
                z = await member.guild.fetch_channel(channel)
                await z.send(member.mention, delete_after=0.5)
        except:
            pass

    @commands.group(aliases=["poj"], invoke_without_command=True)
    @utils.perms("manage_guild")
    async def pingonjoin(self, ctx):

        from modules import paginator as pg

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="pingonjoin", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="config - 1/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up pingonjoin in the guild\n{self.reply} **sub commands:** channel, clear, list",
            inline=False,
        )
        note.add_field(
            name=f"{self.dash} Sub Cmds",
            value=f"```YAML\n\n,pingonjoin channel\n,pingonjoin clear```",
            inline=False,
        )
        note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note2.set_author(name="pingonjoin channel", icon_url=self.bot.user.avatar)
        note2.set_footer(
            text="config - 2/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note2.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up pingonjoin in the guild\n{self.reply} **sub commands:** channel, clear, list",
            inline=False,
        )
        note2.add_field(
            name=f"{self.dash} Usage",
            value=f"```YAML\n\nSyntax: ,pingonjoin channel <#channel>\nExample: ,pingonjoin channel #rules```",
            inline=False,
        )
        note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note3.set_author(name="pingonjoin clear", icon_url=self.bot.user.avatar)
        note3.set_footer(
            text="config - 3/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note3.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up pingonjoin in the guild\n{self.reply} **sub commands:** channel, clear, list",
            inline=False,
        )
        note3.add_field(
            name=f"{self.dash} Usage",
            value=f"```YAML\n\nSyntax: ,pingonjoin clear\nExtra: ,pingonjoin list```",
            inline=False,
        )
        paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        return await paginator.start()

    @pingonjoin.command(name="channel")
    @utils.perms("manage_guild")
    async def pingonjoin_channel(self, ctx, *, channel: discord.TextChannel):

        x = self.bot.db.get("pingonjoin")
        try:
            x.get(str(ctx.guild.id))["channels"].append(channel.id)
            self.bot.db.put(x, "pingonjoin")
        except:
            x[str(ctx.guild.id)] = {"channels": []}
            self.bot.db.put(x, "pingonjoin")
            x = self.bot.db.get("pingonjoin")
            x.get(str(ctx.guild.id))["channels"].append(channel.id)
            self.bot.db.put(x, "pingonjoin")
        await ctx.reply(":thumbsup:")

    @pingonjoin.command(name="clear")
    @utils.perms("manage_guild")
    async def pingonjoin_clear(self, ctx):

        x = self.bot.db.get("pingonjoin")
        try:
            x.pop(str(ctx.guild.id))
            self.bot.db.put(x, "pingonjoin")
        except:
            pass
        await ctx.reply(":thumbsup:")

    @pingonjoin.command(name="list")
    @utils.perms("manage_guild")
    async def pingonjoin_list(self, ctx):

        from modules import paginator as pg

        rows = []
        num = 0
        pagenum = 0
        embeds = []
        async for b in utils.aiter(
            utils.read_json("pingonjoin")[str(ctx.guild.id)]["channels"]
        ):
            num += 1
            b = ctx.guild.get_channel(int(b))
            rows.append(f"`{num}` {b.mention}: **{b}** ( `{b.id}` )\n")
        pages = [p async for p in utils.aiter(discord.utils.as_chunks(rows, 10))]
        async for page in utils.aiter(pages):

            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x2F3136,
                    description=" ".join(page),
                    title=f"pingonjoin list",
                    timestamp=datetime.now(),
                ).set_footer(
                    text=f"{pagenum}/{len(pages)} ({num} entries)",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
            )
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.group(aliases=["levels", "lvl", "lvls"], invoke_without_command=True)
    @utils.perms("manage_guild")
    async def level(self, ctx):

        from modules import paginator as pg

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="level", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="config - 1/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** manage the level system for the guild\n{self.reply} **sub commands:** channel, message, on, off",
            inline=False,
        )
        note.add_field(
            name=f"{self.dash} Sub Cmds",
            value=f"```YAML\n\n,level message\n,level on/off```",
            inline=False,
        )
        note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note2.set_author(name="level message", icon_url=self.bot.user.avatar)
        note2.set_footer(
            text="config - 2/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note2.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** manage the level system for the guild\n{self.reply} **sub commands:** channel, message, on, off",
            inline=False,
        )
        note2.add_field(
            name=f"{self.dash} Usage",
            value="```YAML\n\nSyntax: ,level message\nExample: ,level {user.mention} you're now lvl {level}```",
            inline=False,
        )
        note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note3.set_author(name="level on/off", icon_url=self.bot.user.avatar)
        note3.set_footer(
            text="config - 3/3",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note3.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** manage the level system for the guild\n{self.reply} **sub commands:** channel, message, on, off",
            inline=False,
        )
        note3.add_field(
            name=f"{self.dash} Usage",
            value=f"```YAML\n\nSyntax: ,level <on/off>\nExtra: ,level on```",
            inline=False,
        )
        paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        return await paginator.start()

    @level.command(name="message")
    @utils.perms("manage_guild")
    async def level_message(self, ctx, *, message: str):

        if message == "none":
            message = None
        try:
            x = self.bot.db("levels")
            x[str(ctx.guild.id)]["message"] = message
            self.bot.db.put(x, "levels")
        except:
            x = self.bot.db("levels")
            x[str(ctx.guild.id)] = {"message": None, "state": "off"}
            x[str(ctx.guild.id)]["message"] = message
            self.bot.db.put(x, "levels")

        await ctx.reply(":thumbsup:")

    @level.command(name="on")
    @utils.perms("manage_guild")
    async def level_on(self, ctx):

        try:
            x = self.bot.db("levels")
            x[str(ctx.guild.id)]["state"] = "on"
            self.bot.db.put(x, "levels")
        except:
            x = self.bot.db("levels")
            x[str(ctx.guild.id)] = {"message": None, "state": "on"}
            self.bot.db.put(x, "levels")

        await ctx.reply(":thumbsup:")

    @level.command(name="off")
    @utils.perms("manage_guild")
    async def level_off(self, ctx):

        try:
            x = self.bot.db("levels")
            x[str(ctx.guild.id)]["state"] = "off"
            self.bot.db.put(x, "levels")
        except:
            x = self.bot.db("levels")
            x[str(ctx.guild.id)] = {"message": None, "state": "off"}
            self.bot.db.put(x, "levels")

        await ctx.reply(":thumbsup:")

    @commands.group(aliases=["antiinv"], invoke_without_command=True)
    @utils.perms("manage_guild")
    async def antiinvite(self, ctx):

        from modules import paginator as pg

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="antiinvite", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="config - 1/2",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** manage the anti invite for the guild\n{self.reply} **sub commands:** on, off",
            inline=False,
        )
        note.add_field(
            name=f"{self.dash} Sub Cmds",
            value=f"```YAML\n\n,antiinvite on/off```",
            inline=False,
        )
        note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note2.set_author(name="antiinvite on/off", icon_url=self.bot.user.avatar)
        note2.set_footer(
            text="config - 2/2",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note2.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** manage the anti invite for the guild\n{self.reply} **sub commands:** on, off",
            inline=False,
        )
        note2.add_field(
            name=f"{self.dash} Usage",
            value=f"```YAML\n\nSyntax: ,antiinvite <on/off>\nExtra: ,antiinvite on```",
            inline=False,
        )
        paginator = pg.Paginator(self.bot, [note, note2], ctx, invoker=None)
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        return await paginator.start()

    @antiinvite.command(name="on")
    @utils.perms("manage_guild")
    async def antiinvite_on(self, ctx):

        try:
            x = self.bot.db("antiinvite")
            x[str(ctx.guild.id)]["state"] = "on"
            self.bot.db.put(x, "antiinvite")
        except:
            x = self.bot.db("antiinvite")
            x[str(ctx.guild.id)] = {"state": "on"}
            self.bot.db.put(x, "antiinvite")

        await ctx.reply(":thumbsup:")

    @antiinvite.command(name="off")
    @utils.perms("manage_guild")
    async def antiinvite_off(self, ctx):

        try:
            x = self.bot.db("antiinvite")
            x[str(ctx.guild.id)]["state"] = "off"
            self.bot.db.put(x, "antiinvite")
        except:
            x = self.bot.db("antiinvite")
            x[str(ctx.guild.id)] = {"state": "off"}
            self.bot.db.put(x, "antiinvite")

        await ctx.reply(":thumbsup:")

    @commands.command(aliases=["dis"])
    @utils.perms("manage_guild")
    async def disable(self, ctx, *, command: str):

        if not self.bot.get_command(command):
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** please provide a **valid** command",
                )
            )
        db = self.bot.db("disabled")
        try:
            db.get(str(ctx.guild.id)).append(self.bot.get_command(command).name)
            self.bot.db.put(db, "disabled")
        except:
            db[str(ctx.guild.id)] = []
            db.get(str(ctx.guild.id)).append(self.bot.get_command(command).name)
            self.bot.db.put(db, "disabled")
        await ctx.reply(":thumbsup:")

    @commands.command(aliases=["en"])
    @utils.perms("manage_guild")
    async def enable(self, ctx, *, command: str):

        if not self.bot.get_command(command):
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** please provide a **valid** command",
                )
            )
        db = self.bot.db("disabled")
        try:
            db.get(str(ctx.guild.id)).remove(self.bot.get_command(command).name)
            self.bot.db.put(db, "disabled")
        except:
            try:
                db[str(ctx.guild.id)] = []
                db.get(str(ctx.guild.id)).remove(self.bot.get_command(command).name)
                self.bot.db.put(db, "disabled")
            except:
                pass
        await ctx.reply(":thumbsup:")

    @commands.hybrid_group(aliases=["setting"])
    @utils.perms("manage_guild")
    async def settings(self, ctx):
        ...

    @settings.command(name="safesearch", aliases=["ss", "gs"])
    async def settings_safesearch(self, ctx, state: typing.Literal["on", "off"]):

        try:
            db = self.bot.db("safesearch")
            try:
                db[str(ctx.guild.id)]["state"] = state
                self.bot.db.put(db, "safesearch")
            except:
                db[str(ctx.guild.id)] = {}
                db[str(ctx.guild.id)]["state"] = state
                self.bot.db.put(db, "safesearch")
            await ctx.reply(":thumbsup:")
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** please provide a **valid** state",
                )
            )

    @settings.command(name="disable", aliases=["dis"])
    @utils.perms("manage_guild")
    async def settings_disable(self, ctx, *, command: str):

        if not self.bot.get_command(command):
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** please provide a **valid** command",
                )
            )
        db = self.bot.db("disabled")
        try:
            db.get(str(ctx.guild.id)).append(self.bot.get_command(command).name)
            self.bot.db.put(db, "disabled")
        except:
            db[str(ctx.guild.id)] = []
            db.get(str(ctx.guild.id)).append(self.bot.get_command(command).name)
            self.bot.db.put(db, "disabled")
        await ctx.reply(":thumbsup:")

    @settings.command(name="enable", aliases=["en"])
    @utils.perms("manage_guild")
    async def settings_enable(self, ctx, *, command: str):

        if not self.bot.get_command(command):
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** please provide a **valid** command",
                )
            )
        db = self.bot.db("disabled")
        try:
            db.get(str(ctx.guild.id)).remove(self.bot.get_command(command).name)
            self.bot.db.put(db, "disabled")
        except:
            try:
                db[str(ctx.guild.id)] = []
                db.get(str(ctx.guild.id)).remove(self.bot.get_command(command).name)
                self.bot.db.put(db, "disabled")
            except:
                pass
        await ctx.reply(":thumbsup:")

    @settings.command(name="antiinvite-on")
    @utils.perms("manage_guild")
    async def settings_antiinvite_on(self, ctx):

        try:
            x = self.bot.db("antiinvite")
            x[str(ctx.guild.id)]["state"] = "on"
            self.bot.db.put(x, "antiinvite")
        except:
            x = self.bot.db("antiinvite")
            x[str(ctx.guild.id)] = {"state": "on"}
            self.bot.db.put(x, "antiinvite")

        await ctx.reply(":thumbsup:")

    @settings.command(name="antiinvite-off")
    @utils.perms("manage_guild")
    async def settings_antiinvite_off(self, ctx):

        try:
            x = self.bot.db("antiinvite")
            x[str(ctx.guild.id)]["state"] = "off"
            self.bot.db.put(x, "antiinvite")
        except:
            x = self.bot.db("antiinvite")
            x[str(ctx.guild.id)] = {"state": "off"}
            self.bot.db.put(x, "antiinvite")

        await ctx.reply(":thumbsup:")

    @commands.hybrid_group(name="boost", invoke_without_command=True)
    @utils.perms("manage_guild")
    async def boost(self, ctx):

        ex = "{content:{user.mention} ty}"
        note1 = discord.Embed(color=utils.color("main"), timestamp=datetime.now())
        note1.set_author(name=f"boost", icon_url=self.bot.user.display_avatar)
        note1.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** manage the guild's boost message",
        )
        note1.add_field(
            name=f"{self.dash} Usage",
            value=f"{self.reply} **syntax:** ,boost message <code>\n{self.reply} **example:** ,boost message {ex}",
            inline=False,
        )
        note1.set_footer(
            text=f"config",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        await ctx.reply(embed=note1)

    @boost.command(name="clear")
    @utils.perms("manage_guild")
    async def boost_clear(self, ctx):

        try:
            db = utils.read_json("boost")
            db.pop(str(ctx.guild.id))
            utils.write_json(db, "boost")
        except:
            pass
        await ctx.reply(":thumbsup:")

    @boost.command(name="channel")
    @utils.perms("manage_guild")
    async def boost_channel(self, ctx, *, channel: discord.TextChannel):

        try:
            db = utils.read_json("boost")
            if channel.id not in db[str(ctx.guild.id)]["channel"]:
                db[str(ctx.guild.id)]["channel"].append(channel.id)
            utils.write_json(db, "boost")
        except:
            db = utils.read_json("boost")
            message = db.get(str(ctx.guild.id))
            if msg:
                msg = msg.get("message")
            db[str(ctx.guild.id)] = {
                "channel": [],
                "message": message if message else None,
            }
            db[str(ctx.guild.id)]["channel"].append(channel.id)
            utils.write_json(db, "boost")
        await ctx.send(":thumbsup:")

    @boost.command(name="message", aliases=["msg"])
    @utils.perms("manage_guild")
    async def boost_message(self, ctx, *, message: str = None):

        try:
            db = utils.read_json("boost")
            db[str(ctx.guild.id)]["message"] = message
            utils.write_json(db, "boost")
        except:
            db = utils.read_json("boost")
            channel = db.get(str(ctx.guild.id))
            if channel:
                channel = channel.get("channel")
            db[str(ctx.guild.id)] = {
                "channel": channel if channel else [],
                "message": message,
            }

            utils.write_json(db, "boost")
        await ctx.send(":thumbsup:")

    @boost.command(name="test")
    @utils.perms("manage_guild")
    async def boost_test(self, ctx):

        import copy

        msg = copy.copy(ctx.message)
        msg.type = discord.MessageType.premium_guild_subscription
        msg.content = ctx.message.content.strip(ctx.prefix)
        self.bot.dispatch("message", msg)
        return await ctx.reply(":thumbsup:")


async def setup(bot):
    await bot.add_cog(config(bot))
