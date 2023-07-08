import discord, datetime, aiohttp
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import paginator as pg
from modules import utils


class history(commands.Cog):
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

    @commands.hybrid_command(aliases=["usernames"])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def names(self, ctx, user: discord.User | discord.Member = None):
        try:
            await ctx.typing()
            user = ctx.author if not user else user
            db = utils.read_json("names")[str(user.id)]
            ret = []
            num = 0
            pagenum = 0
            embeds = []
            names = db["names"]
            async for name in utils.aiter(names[::-1]):
                num += 1
                ret.append(f"`{num}` {name}\n")
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
            async for page in utils.aiter(pages):
                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x4c5264,
                        description="".join(page),
                        title=f"name list",
                        timestamp=datetime.now(),
                    ).set_footer(
                        text=f"{pagenum}/{len(pages)} ({num} entries)",
                        icon_url=None,
                    )
                )
            paginator = pg.Paginator(self.bot, embeds, ctx, timeout=30, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()

        except:
            await ctx.send(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}: no previously recorded names for {user.name}",
                )
            )

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def clear(self, ctx):
        note = discord.Embed(color=0x4c5264, timestamp=datetime.now())
        note.set_author(name="clear", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="history - 1/3",
            icon_url=None,
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** clear your history, where its names or pfps\n{self.reply} **options:** names, all",
            inline=False,
        )
        note.add_field(
            name="Sub Cmds",
            value=f"```YAML\n\n;clear <option>\n;clear names```",
            inline=False,
        )
        note2 = discord.Embed(color=0x4c5264, timestamp=datetime.now())
        note2.set_author(name="clear names", icon_url=self.bot.user.avatar)
        note2.set_footer(
            text="history - 2/3",
            icon_url=None,
        )
        note2.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** clear your name history\n{self.reply} **options:** names, all",
            inline=False,
        )
        note2.add_field(
            name="Usage",
            value=f"```YAML\n\nsyntax: lclear names\nexample: ;clear names```",
            inline=False,
        )
        paginator = pg.Paginator(self.bot, [note, note2], ctx, timeout=30, invoker=ctx.author.id)
        paginator.add_button("prev", emoji="<:left:1107307769582850079>")
        paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
        paginator.add_button("next", emoji="<:right:1107307767041105920>")
        paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
        await paginator.start()

    @clear.command(name="names")
    async def clear_names(self, ctx):
        db = self.bot.db("names")
        if not db.get(str(ctx.author.id)):
            return await ctx.send(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}: no previously recorded names for {ctx.author.name}",
                )
            )

        db.get(str(ctx.author.id))["names"] = []
        self.bot.db.put(db, "names")
        await ctx.reply(":thumbsup:")

    @clear.command(name="avatars")
    async def clear_avatars(self, ctx):
        db = self.bot.db("avatarhistory")
        if not db.get(str(ctx.author.id)):
            return await ctx.send(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}: no previously recorded avatars for {ctx.author.name}",
                )
            )

        db[str(ctx.author.id)] = []
        self.bot.db.put(db, "avatarhistory")
        await ctx.reply(":thumbsup:")

    @clear.command(name="all")
    async def clear_all(self, ctx):
        await ctx.typing()
        db = self.bot.db("names")
        if db.get(str(ctx.author.id)):
            db.get(str(ctx.author.id))["names"] = []
            self.bot.db.put(db, "names")

        db = self.bot.db("avatarhistory")
        if db.get(str(ctx.author.id)):
            db[str(ctx.author.id)] = []
            self.bot.db.put(db, "avatarhistory")

        await ctx.reply(":thumbsup:")

    @commands.hybrid_group(aliases=["data"], invoke_without_command=False)
    async def nodata(self, ctx):
        ...

    @nodata.command(name="true")
    async def nodata_true(self, ctx):
        x = self.bot.db("nodata")
        x[str(ctx.author.id)] = {}
        x[str(ctx.author.id)]["data"] = False
        self.bot.db.put(x, "nodata")
        await ctx.reply(":thumbsup:")


async def setup(bot):
    await bot.add_cog(history(bot))
