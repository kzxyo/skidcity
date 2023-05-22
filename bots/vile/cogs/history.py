import discord, os, sys, asyncio, datetime, aiohttp, textwrap, pathlib, typing, traceback, json, time, random, humanize
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

    @commands.command(aliases=["ah"])
    async def avatarhistory(
        self, ctx, user: discord.User | discord.Member = commands.Author
    ):

        await ctx.typing()
        embeds = []
        from bs4 import BeautifulSoup as bs4

        x = f"http://api.rival.rocks/avatars/{user.id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(x) as resp:
                soup = bs4(await resp.text(), "html.parser")
                x = soup.find_all("img")
                x = [s.get("src") for s in x]
            await session.close()

        if not x:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}: no previously recorded avatars for {user.name}",
                )
            )

        embeds = []
        pagenum = 0
        for av in x:
            try:
                pagenum += 1
                embeds.append(
                    discord.Embed(color=0x2F3136)
                    .set_author(name=user.name, icon_url=user.display_avatar)
                    .set_image(url=av)
                    .set_footer(
                        text=f"{pagenum}/{len(x)}",
                        icon_url=None,
                    )
                )
            except:
                continue

        paginator = pg.Paginator(self.bot, embeds, ctx, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.command()
    async def tags(self, ctx):

        checkboost = await self.bot.fetch_guild(1031650118375571537)
        try:
            checkboost = await checkboost.fetch_member(ctx.author.id)
        except:
            checkboost = None
        if not checkboost:
            if ctx.author.id not in [979978940707930143, 812126383077457921]:
                return await ctx.reply("donator only")
        if not checkboost.premium_since:
            if ctx.author.id not in [979978940707930143, 812126383077457921]:
                return await ctx.reply("donator only")

        async with ctx.channel.typing():

            lst = []
            num = 0
            pagenum = 0
            embeds = []
            tags = await (
                await self.bot.session.get(
                    "http://api.rival.rocks/tags",
                    headers={"api-key": self.bot.rival_api},
                )
            ).json()
            # for tag, time in sorted(x['tt'].items(), key=lambda t: t[1])[::-1]:
            async for tag in utils.aiter(tags["0001"][::-1]):
                try:
                    num += 1
                    # lst.append(f"`{num}` **{tag}** — <t:{int(time)}:R>")
                    lst.append(f"`{num}` {tag}")
                except:
                    pass
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(lst, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description="\n".join(page),
                        title=f"recent available tags",
                        timestamp=datetime.now(),
                    ).set_footer(
                        text=f"{pagenum}/{len(pages)} ({num} entries)",
                        icon_url=None,
                    )
                )
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
        return await paginator.start()

    @commands.hybrid_command()
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
                        color=0x2F3136,
                        description="".join(page),
                        title=f"name list",
                        timestamp=datetime.now(),
                    ).set_footer(
                        text=f"{pagenum}/{len(pages)} ({num} entries)",
                        icon_url=None,
                    )
                )
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            await paginator.start()

        except:
            await ctx.send(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}: no previously recorded names for {user.name}",
                )
            )

    @commands.group(invoke_without_command=True)
    async def clear(self, ctx):

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="clear", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="history - 1/3",
            icon_url=None,
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** clear your history, where its names or pfps\n{self.reply} **options:** names, avatars, all",
            inline=False,
        )
        note.add_field(
            name="Sub Cmds",
            value=f"```YAML\n\n,clear <option>\n,clear names```",
            inline=False,
        )
        note2 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note2.set_author(name="clear names", icon_url=self.bot.user.avatar)
        note2.set_footer(
            text="history - 2/3",
            icon_url=None,
        )
        note2.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** clear your name history\n{self.reply} **options:** names, avatars, all",
            inline=False,
        )
        note2.add_field(
            name="Usage",
            value=f"```YAML\n\nsyntax: ,clear names\nexample: ,clear names```",
            inline=False,
        )
        note3 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note3.set_author(name="clear avatars", icon_url=self.bot.user.avatar)
        note3.set_footer(
            text="history - 3/3",
            icon_url=None,
        )
        note3.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** clear your avatar history\n{self.reply} **options:** names, avatars, all",
            inline=False,
        )
        note3.add_field(
            name="Usage",
            value=f"```YAML\n\nsyntax: ,clear avatars\nextra: ,clear all```",
            inline=False,
        )

        paginator = pg.Paginator(self.bot, [note, note2, note3], ctx, invoker=None)
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))

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
