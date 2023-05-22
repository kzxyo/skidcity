from code import interact
from email.mime import image
from inspect import trace
from re import L
import discord, os, sys, asyncio, googletrans, datetime, math, textwrap, pathlib, typing, traceback, json, time, random, humanize, inspect
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import paginator as pg
from modules import utils
from typing import Optional


def get_xp(level):
    return math.ceil(math.pow((level - 1) / (0.05 * (1 + math.sqrt(5))), 2))


def get_level(xp):
    return math.floor(0.05 * (1 + math.sqrt(5)) * math.sqrt(xp)) + 1


def xp_to_next_level(level):
    return get_xp(level + 1) - get_xp(level)


def xp_from_message(message: discord.Message):
    words = message.content.split(" ")
    eligible_words = 0
    for x in words:
        if len(x) > 1:
            eligible_words += 1
    xp = eligible_words + (10 * len(message.attachments))
    if xp == 0:
        xp = 1

    return min(xp, 50)


class utility(commands.Cog):
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
        self.trans = googletrans.Translator()

    @commands.command(
        name="banner",
        aliases=["userbanner"],
        description="get the mentioned user's banner",
        brief=",banner [user]",
        help=",banner glory",
    )
    async def userbanner(
        self, ctx, user: Optional[discord.User | discord.Member] = commands.Author
    ):

        user = await self.bot.fetch_user(user.id)

        embed = discord.Embed(color=self.bot.color, title=f"{user.name}'s banner")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        if not user.banner:
            banner = f"https://singlecolorimage.com/get/{str('18191c' if not user.accent_color else user.accent_color).strip('#').replace('None', 'null')}/400x150"
        else:
            banner = user.banner.url

        embed.url = banner
        embed.set_image(url=banner)

        try:
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="w",
                    url=str(user.banner.replace(format="webp")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="p",
                    url=str(user.banner.replace(format="png")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="j",
                    url=str(user.banner.replace(format="jpg")),
                )
            )
        except:
            view = None

        return await ctx.reply(embed=embed, view=view)

    @commands.command(
        name="avatar",
        aliases=["av", "useravatar"],
        description="get the mentioned user's avatar",
        brief=",avatar [user]",
        help=",avatar glory",
    )
    async def useravatar(
        self, ctx, user: Optional[discord.User | discord.Member] = commands.Author
    ):

        embed = discord.Embed(color=await utils.domcolor(user.display_avatar.url), title=f"{user.name}'s avatar")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.url = user.display_avatar.url
        embed.set_image(url=user.display_avatar)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="w",
                url=str(user.display_avatar.replace(format="webp")),
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="p",
                url=str(user.display_avatar.replace(format="png")),
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="j",
                url=str(user.display_avatar.replace(format="jpg")),
            )
        )

        return await ctx.reply(embed=embed, view=view)

    @commands.group(
        name="guild",
        aliases=["server"],
        description="get info about the current or provided server",
        brief=",serverinfo (invite)",
        help=",serverinfo heist",
        invoke_without_command=True,
    )
    async def guild(self, ctx, guild: Optional[discord.Invite] = None):

        return await ctx.invoke(self.bot.get_command("serverinfo"), guild=guild)

    @guild.command(name="banner", description=f"get the guild's banner, if it has one")
    async def guild_banner(self, ctx, guild: Optional[discord.Invite] = None):

        guild = ctx.guild if not guild else guild.guild

        embed = discord.Embed(
            color=self.bot.color, title=f"{guild.name}'s guild banner"
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        if not guild.banner:
            banner = "https://singleutils.colorimage.com/get/18191c/400x150"
        else:
            banner = guild.banner

        embed.url = banner.url
        embed.set_image(url=banner)

        try:
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="w",
                    url=str(banner.replace(format="webp")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="p",
                    url=str(banner.replace(format="png")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="j",
                    url=str(banner.replace(format="jpg")),
                )
            )
        except:
            view = None

        return await ctx.reply(embed=embed, view=view)

    @guild.command(name="icon", description="get the guild's icon, if it has one")
    async def guildicon(self, ctx, guild: Optional[discord.Invite] = None):

        guild = ctx.guild if not guild else guild.guild

        embed = discord.Embed(color=self.bot.color, title=f"{guild.name}'s server icon")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        if not guild.icon:
            icon = "https://singleutils.colorimage.com/get/18191c/200x200"
        else:
            icon = guild.icon

        embed.url = icon.url
        embed.set_image(url=icon)

        try:
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="w",
                    url=str(icon.replace(format="webp")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="p",
                    url=str(icon.replace(format="png")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="j",
                    url=str(icon.replace(format="jpg")),
                )
            )
        except:
            view = None

        return await ctx.reply(embed=embed, view=view)

    @guild.command(name="splash", description=f"get the guild's splash, if it has one")
    async def guildsplash(self, ctx, guild: Optional[discord.Invite] = None):

        guild = ctx.guild if not guild else guild.guild

        embed = discord.Embed(
            color=self.bot.color, title=f"{guild.name}'s server splash"
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)

        if not guild.splash:
            splash = "https://singleutils.colorimage.com/get/18191c/400x50"
        else:
            splash = guild.splash

        embed.url = splash.url
        embed.set_image(url=splash)

        try:
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="w",
                    url=str(splash.replace(format="webp")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="p",
                    url=str(splash.replace(format="png")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="j",
                    url=str(splash.replace(format="jpg")),
                )
            )
        except:
            view = None

        return await ctx.reply(embed=embed, view=view)

    @commands.group(name="set", invoke_without_command=False)
    @commands.bot_has_permissions(manage_guild=True)
    @utils.perms("manage_guild")
    async def _set(self, ctx):
        ...

    @_set.command(
        name="icon",
        description="set the guild's icon",
        brief=",set icon [link or attachment]",
    )
    async def set_icon(self, ctx, link: str = None):

        if not ctx.message.attachments and not link:
            return await ctx.send("tf do u want the icon to be :joy:")
        if not link:
            if ctx.message.attachments:
                link = ctx.message.attachments[0].proxy_url

        await ctx.guild.edit(icon=await utils.file(link))
        return await ctx.send(":thumbsup:")

    @_set.command(
        name="banner",
        description="set the guild's banner",
        brief=",set banner [link or attachment]",
    )
    @commands.bot_has_permissions(manage_guild=True)
    @utils.perms("manage_guild")
    async def set_banner(self, ctx, link: str = None):

        if not ctx.message.attachments and not link:
            return await ctx.send("tf do u want the banner to be :joy:")
        if not link:
            if ctx.message.attachments:
                link = ctx.message.attachments[0].proxy_url

        await ctx.guild.edit(banner=await utils.file(link))
        return await ctx.send(":thumbsup:")

    @_set.command(
        name="splash",
        description="set the guild's splash",
        brief=",set splash [link or attachment]",
    )
    @commands.bot_has_permissions(manage_guild=True)
    @utils.perms("manage_guild")
    async def set_splash(self, ctx, link: Optional[str] = None):

        if not ctx.message.attachments and not link:
            return await ctx.send("tf do u want the splash to be :joy:")
        if not link:
            if ctx.message.attachments:
                link = ctx.message.attachments[0].proxy_url

        await ctx.guild.edit(splash=await utils.file(link))
        return await ctx.send(":thumbsup:")

    @commands.command(
        name="steal",
        aliases=["emadd", "addemoji"],
        description="steal emojis from other guilds",
        brief=",steal <emoji> [name]",
        help=",steal :50DollaLemonade: jitTrippin",
    )
    @utils.perms("manage_emojis")
    async def steal(
        self, ctx, emoji: Optional[discord.Emoji | discord.PartialEmoji] = None
    ):

        cc = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        cc.set_footer(
            text=ctx.command.cog_name,
            icon_url=None,
        )
        cc.set_author(name=ctx.command.name, icon_url=self.bot.user.display_avatar)
        cc.add_field(
            name=f"{self.bot.dash} Info",
            value=f"{self.bot.eply} **description:** {ctx.command.description}\n{self.bot.reply} **aliases:** {', '.join(ctx.command.aliases)}",
            inline=False,
        )
        cc.add_field(
            name=f"{self.bot.dash} Usage",
            value=f"{self.bot.reply} syntax: {ctx.command.brief}\n{self.bot.reply} example: {ctx.command.help}",
            inline=False,
        )

        if not emojis:
            return await ctx.reply(embed=cc)

    @commands.command(
        name="bans", aliases=["banlist"], description="get a list of banned members"
    )
    @commands.bot_has_permissions(ban_members=True)
    @utils.perms("ban_members")
    async def bans(self, ctx):

        if not ctx.guild.bans():
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.fail} {ctx.author.mention}**:** there are no **bans** in the guild",
                )
            )

        ret = []
        num = 0
        pagenum = 0
        embeds = []
        async for entry in ctx.guild.bans():
            num += 1
            ret.append(
                f"**`{num}`** **{entry.user.name}**#{entry.user.discriminator} ( `{entry.user.id}` ) for: {'no reason' if not entry.reason else entry.reason}\n"
            )

        pages = [p for p in discord.utils.as_chunks(ret, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x2F3136,
                    description=" ".join(page),
                    title=f"ban list",
                    timestamp=datetime.now(),
                )
                .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                .set_footer(
                    text=f"{pagenum}/{len(pages)} ({num} entries)",
                    icon_url=None,
                )
            )

        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        return await paginator.start()

    @commands.hybrid_command(aliases=["emojilist"])
    #
    async def emojis(self, ctx):

        try:
            ret = []
            num = 0
            pagenum = 0
            embeds = []
            async for emoji in utils.aiter(ctx.guild.emojis):
                num += 1
                ret.append(
                    f"**`{num}`** {emoji}: **{emoji.name} [`{emoji.id}`]({emoji.url})**\n"
                )
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=" ".join(page),
                        title=f"emoji list",
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
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **emojis** in the guild",
                )
            )

    @guild.command(name="bans", aliases=["banlist"])
    @commands.bot_has_permissions(ban_members=True)
    @utils.perms("ban_members")
    async def guild_bans(self, ctx):

        try:
            ret = []
            num = 0
            pagenum = 0
            embeds = []
            async for entry in ctx.guild.bans():
                num += 1
                ret.append(
                    f"**`{num}`** **{entry.user.name}**#{entry.user.discriminator} ( `{entry.user.id}` ) for: {'no reason' if not entry.reason else entry.reason}\n"
                )

            pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=" ".join(page),
                        title=f"ban list",
                        timestamp=datetime.now(),
                    )
                    .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                    .set_footer(
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
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **bans** in the guild",
                )
            )

    @guild.command(name="emojis", aliases=["emojilist"])
    async def guild_emojis(self, ctx):

        try:
            ret = []
            num = 0
            pagenum = 0
            embeds = []
            async for emoji in utils.aiter(ctx.guild.emojis):
                num += 1
                ret.append(
                    f"**`{num}`** {emoji}: **{emoji.name} [`{emoji.id}`]({emoji.url})**\n"
                )
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=" ".join(page),
                        title=f"emoji list",
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
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **emojis** in the guild",
                )
            )

    @commands.hybrid_command()
    #
    @commands.bot_has_permissions(administrator=True)
    @utils.perms("administrator")
    async def nuke(self, ctx):

        invoker = ctx.author.id
        channel = ctx.channel

        class disabledbuttons(discord.ui.View):
            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=True,
                emoji=utils.read_json("emojis")["done"],
            )
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(
                    name=interaction.channel.name,
                    reason=f"original channel nuked by {invoker}",
                )
                ch = await interaction.guild.fetch_channel(ch.id)
                await ch.send(f"<@{invoker}>: channel has been nuked successfully")

            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=True,
                emoji=utils.read_json("emojis")["fail"],
            )
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                await interaction.response.edit_message(
                    content="are you sure you want to nuke this channel?", view=None
                )
                await interaction.channel.send(
                    f"<@{interaction.user.id}>: channel nuke has been cancelled"
                )

        class buttons(discord.ui.View):
            @discord.ui.button(
                style=discord.ButtonStyle.grey, emoji=utils.read_json("emojis")["done"]
            )
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(
                    name=interaction.channel.name,
                    reason=f"original channel nuked by {invoker}",
                )
                ch = await interaction.guild.fetch_channel(ch.id)
                await ch.send(f"<@{invoker}>**:** channel has been nuked successfully")

            @discord.ui.button(
                style=discord.ButtonStyle.grey, emoji=utils.read_json("emojis")["fail"]
            )
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                await interaction.response.edit_message(
                    content="are you sure you want to nuke this channel?",
                    view=disabledbuttons(),
                )
                await interaction.message.reply(
                    f"<@{interaction.user.id}>**:** channel nuke has been cancelled"
                )

        await ctx.reply("are you sure you want to nuke this channel?", view=buttons())
        # try:
        # from modules import confirmation
        # msg = await ctx.reply('are you sure you want to nuke this channel?')#, view=buttons())
        # ret = await confirmation.confirm(self=self, ctx=ctx, msg=msg)
        # if ret == True:
        # ch = await ctx.channel.clone(name=ctx.channel.name, reason=f"original channel nuked by {invoker}")
        # ch = await ctx.guild.fetch_channel(ch.id)
        # await ctx.channel.delete()
        # await ch.send(f"<@{invoker}>**:** channel has been nuked successfully")
        # elif ret == False:
        # return await msg.reply(f'<@{invoker}>**:** channel nuke has been cancelled')
        # except Exception as e: await ctx.reply(e)

    @commands.hybrid_command(aliases=["ir"])
    async def inrole(self, ctx, *, role: discord.Role = None):

        if not role:
            em = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            em.set_footer(
                text="information",
                icon_url=None,
            )
            em.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** view members in a role\n{self.reply} **aliases:** inrole, ir",
            )
            em.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ,inrole <role>\n{self.reply} example: ,inrole bots",
                inline=False,
            )
            em.set_author(name="inrole", icon_url=self.bot.user.avatar)
            await ctx.reply(embed=em)

        else:
            try:
                ret = []
                num = 0
                pagenum = 0
                embeds = []
                async for m in utils.aiter(role.member):
                    num += 1
                    ret.append(f"`{num}` {m.mention}: **{m}** ( `{m.id}` )\n")
                pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
                async for page in utils.aiter(pages):

                    pagenum += 1
                    embeds.append(
                        discord.Embed(
                            color=0x2F3136,
                            description=" ".join(page),
                            title=f"inrole {role.name}",
                            timestamp=datetime.now(),
                        ).set_footer(
                            text=f"{pagenum}/{len(pages)} ({num} entries)",
                            icon_url=None,
                        )
                    )
                paginator = pg.Paginator(
                    self.bot, embeds, ctx, invoker=None, timeout=30
                )
                paginator.add_button("prev", emoji=utils.emoji("prevpage"))
                paginator.add_button("goto", emoji=utils.emoji("choosepage"))
                paginator.add_button("next", emoji=utils.emoji("nextpage"))
                await paginator.start()

            except:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}**:** there are no **emojis** in the guild",
                    )
                )

    @commands.hybrid_command(aliases=["botlist"])
    #
    async def bots(self, ctx):

        try:
            ret = []
            num = 0
            pagenum = 0
            embeds = []
            async for m in utils.aiter(ctx.guild.members):
                if m.bot:
                    num += 1
                    ret.append(f"`{num}` {m.mention}: **{m}** ( `{m.id}` )\n")
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=" ".join(page),
                        title=f"bot list",
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
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **emojis** in the guild",
                )
            )

    @commands.hybrid_command(aliases=["rolelist"])
    #
    async def roles(self, ctx):

        try:
            rows = []
            num = 0
            pagenum = 0
            embeds = []
            async for r in utils.aiter(ctx.guild.roles[::-1]):
                num += 1
                rows.append(f"`{num}` {r.mention} ( `{r.id}` )\n")
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(rows, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=" ".join(page),
                        title=f"role list",
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
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **roles** in the guild",
                )
            )

    @guild.command(name="inrole", aliases=["ir"])
    async def guild_inrole(self, ctx, *, role: discord.Role = None):

        if not role:
            em = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            em.set_footer(
                text="information",
                icon_url=None,
            )
            em.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** view members in a role\n{self.reply} **aliases:** inrole, ir",
            )
            em.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ,inrole <role>\n{self.reply} example: ,inrole bots",
                inline=False,
            )
            em.set_author(name="inrole", icon_url=self.bot.user.avatar)
            await ctx.reply(embed=em)

        else:
            try:
                ret = []
                num = 0
                pagenum = 0
                embeds = []
                async for m in utils.aiter(role.members):
                    num += 1
                    ret.append(f"`{num}` {m.mention}: **{m}** ( `{m.id}` )\n")
                pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
                async for page in utils.aiter(pages):

                    pagenum += 1
                    embeds.append(
                        discord.Embed(
                            color=0x2F3136,
                            description=" ".join(page),
                            title=f"inrole {role.name}",
                            timestamp=datetime.now(),
                        ).set_footer(
                            text=f"{pagenum}/{len(pages)} ({num} entries)",
                            icon_url=None,
                        )
                    )
                paginator = pg.Paginator(
                    self.bot, embeds, ctx, invoker=None, timeout=30
                )
                paginator.add_button("prev", emoji=utils.emoji("prevpage"))
                paginator.add_button("goto", emoji=utils.emoji("choosepage"))
                paginator.add_button("next", emoji=utils.emoji("nextpage"))
                await paginator.start()

            except:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{self.warn} {ctx.author.mention}**:** there are no **emojis** in the guild",
                    )
                )

    @guild.command(name="bots", aliases=["botlist"])
    async def guild_bots(self, ctx):

        try:
            ret = []
            num = 0
            pagenum = 0
            embeds = []
            async for m in utils.aiter(ctx.guild.members):
                if m.bot:
                    num += 1
                    ret.append(f"`{num}` {m.mention}: **{m}** ( `{m.id}` )\n")
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=" ".join(page),
                        title=f"bot list",
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
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **emojis** in the guild",
                )
            )

    @guild.command(name="roles", aliases=["rolelist"])
    async def guild_roles(self, ctx):

        try:
            ret = []
            num = 0
            pagenum = 0
            embeds = []
            async for r in utils.aiter(ctx.guild.roles[::-1]):
                num += 1
                ret.append(f"`{num}` {r.mention} ( `{r.id}` )\n")
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=" ".join(page),
                        title=f"role list",
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
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **roles** in the guild",
                )
            )

    @commands.hybrid_command(aliases=["bc", "cleanup"])
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def botclear(self, ctx):

        await ctx.typing()
        await ctx.channel.purge(limit=100, check=lambda m: m.author.bot)
        await ctx.send(":thumbsup:")

    @commands.hybrid_command()
    async def hex(self, ctx, hexxx=None):

        if hexxx == None:

            e = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            e.set_footer(
                text="utility",
                icon_url=None,
            )
            e.set_author(name="hex", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** get more information on a provided base hex code",
                inline=False,
            )
            e.add_field(
                name=f"{self.dash} Usage",
                value=f"{self.reply} syntax: ,hex <hexcode>\n{self.reply} example: ,hex 0000FF or ,hex #0000FF",
                inline=False,
            )
            await ctx.reply(embed=e)

        else:

            hexxx = hexxx.replace("#", "")
            data = await self.bot.session.get(
                f"https://api.alexflipnote.dev/colour/{hexxx}"
            )
            data = await data.json()

            shades = (
                str(
                    [
                        data["shade"][0],
                        data["shade"][1],
                        data["shade"][2],
                        data["shade"][3],
                    ]
                )
                .replace("[", "")
                .replace("'", "")
                .replace("]", "")
            )
            hexx = data["hex"]
            rgb = data["rgb"]
            name = data["name"]
            image = data["image"]
            grad = data["image_gradient"]
            brightness = data["brightness"]
            embed = discord.Embed(color=eval(f"0x{hexxx}"))
            embed.set_author(name=name, icon_url=image)
            embed.set_thumbnail(url=image)
            embed.set_image(url=grad)
            embed.add_field(name="RGB", value=rgb)
            embed.add_field(name="Hex", value=hexx)
            embed.add_field(name="Brightness", value=brightness)
            embed.add_field(name="Shades", value=f"```YAML\n\n{shades}```")

            await ctx.reply(embed=embed)

    @commands.hybrid_command(aliases=["img", "gimage"])
    async def image(self, ctx, *, query: str = None):

        if not query:
            em = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            em.set_footer(
                text="utility",
                icon_url=None,
            )
            em.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** get google image results\n{self.reply} **aliases:** img, gimage",
            )
            em.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ,image <search query>\n{self.reply} example: ,image lucki",
                inline=False,
            )
            em.set_author(name="image", icon_url=self.bot.user.avatar)
            return await ctx.reply(embed=em)

        safe = "off"
        try:
            safedb = self.bot.db("safesearch")
            if safedb[str(ctx.guild.id)]["state"] == "on":
                safe = "active"
        except:
            pass

        params = {
            "api_key": "3bd395020ed338a2edbee26473c5260ca4c05347dac3e29fc1197c688bbac95d",
            "engine": "google",
            "q": query,
            "location": "United States",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "tbm": "isch",
            "ijn": "1",
        }

        if safe == "active":
            params["safe"] = "active"

        try:
            async with ctx.channel.typing():
                search = await self.bot.session.get(
                    "https://serpapi.com/search", params=params
                )
                results = await search.json()
                num = 0
                embeds = []
                async for result in utils.aiter(results["images_results"]):
                    num += 1
                    embeds.append(
                        discord.Embed(
                            color=utils.color("main"),
                            title=f"results for {query}",
                            url=result["original"],
                            timestamp=datetime.now(),
                        )
                        .set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                        .set_image(url=result["original"])
                        .set_footer(
                            text=f"{num}/100",
                            icon_url=None,
                        )
                    )
                paginator = pg.Paginator(
                    self.bot, embeds, ctx, timeout=30, invoker=None
                )
                paginator.add_button("prev", emoji=utils.emoji("prevpage"))
                paginator.add_button("goto", emoji=utils.emoji("choosepage"))
                paginator.add_button("next", emoji=utils.emoji("nextpage"))
            await paginator.start()
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** safe search is **enabled** for this guild",
                )
            )

    @commands.hybrid_command()
    #
    async def afk(self, ctx, *, status="AFK"):

        db = utils.read_json("afk")
        ls = datetime.now().timestamp()
        db[str(ctx.author.id)] = {"guild": [], "status": status, "lastseen": ls}
        db[str(ctx.author.id)]["guild"].append(ctx.guild.id)
        utils.write_json(db, "afk")
        db = utils.read_json("afk")[str(ctx.author.id)]
        embed = discord.Embed(
            color=self.success,
            description=f'{self.done} {ctx.author.mention}**:** you\'re now afk with the status **{db["status"]}**',
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command()
    #
    async def boosters(self, ctx):

        try:
            ret = []
            num = 0
            pagenum = 0
            embeds = []
            async for s in utils.aiter(ctx.guild.premium_subscribers):
                num += 1
                ret.append(f"`{num}` {s.mention} ( `{s.id}` )\n")
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=" ".join(page),
                        title=f"booster list",
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
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **boosters** in the guild",
                )
            )

    @commands.hybrid_command(aliases=["fnshop"])
    #
    async def fortniteshop(self, ctx):

        await ctx.typing()
        e1 = discord.Embed(
            color=self.success,
            description=f"{self.done} {ctx.author.mention}**:** fortnite shop as of `{datetime.now().strftime('%m-%d-%Y').replace('0', '').replace('-', '/').replace('222', '2022')}`",
        )
        await ctx.reply(
            embed=e1,
            file=await utils.file(
                f"https://bot.fnbr.co/shop-image/fnbr-shop-{datetime.now().strftime('%d-%m-%Y').replace('0', '').replace('222', '2022')}.png?1653143336437",
                fn="fortniteshop.png",
            ),
        )

    @commands.hybrid_command(aliases=["firstmsg"])
    #
    async def firstmessage(self, ctx):

        async for message in ctx.channel.history(limit=1, oldest_first=True):

            await ctx.reply(
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label="first message",
                        url=message.jump_url,
                    )
                )
            )

    @commands.hybrid_command()
    #
    async def status(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        status = "none" if not user.activity.name else user.activity.name

        e = discord.Embed(color=0x2F3136, description=status)
        e.set_author(name=f"{user.name}'s status", icon_url=user.avatar)

        await ctx.reply(embed=e)

    @commands.hybrid_command()
    async def boosts(self, ctx):
        await ctx.reply(
            embed=discord.Embed(
                color=0x2F3136,
                description=f"{self.done} {ctx.author.mention}: **{ctx.guild.name}** has **{ctx.guild.premium_subscription_count}** boost{'s' if ctx.guild.premium_subscription_count != 1 else ''}",
            )
        )

    @commands.hybrid_command(aliases=["invs"])
    #
    async def invites(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        totalInvites = 0
        async for i in utils.aiter(await ctx.guild.invites()):
            if i.inviter == user:
                totalInvites += i.uses
        await ctx.reply(
            embed=discord.Embed(
                color=0x2F3136,
                description=f"{self.done} {ctx.author.mention}: **{user.name}** has **{totalInvites}** invite{'s' if totalInvites != 1 else ''}",
            )
        )

    @commands.hybrid_command(aliases=["msgs", "activity"])
    async def messages(self, ctx, *, user: discord.Member = None):

        user = ctx.author if not user else user
        db = utils.read_json("messages")
        try:
            msgs = db[str(ctx.guild.id)][str(user.id)]
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("main"),
                    description=f"{ctx.author.mention}**: {user.name}** has sent {msgs} message{'s' if msgs != 1 else ''}",
                )
            )
        except:
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("main"),
                    description=f"{ctx.author.mention}**: {user.name}** has sent 0 message{'s' if 0 != 1 else ''}",
                )
            )

    @commands.hybrid_command(aliases=["cr"])
    @commands.bot_has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.member, wait=False)
    async def colorrole(self, ctx, hexx=None):

        if not hexx:
            e = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            e.set_footer(
                text="utility",
                icon_url=None,
            )
            e.set_author(name="colorrole", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** create/update your personal color role\n{self.reply} **aliases:** colorrole, cr",
                inline=False,
            )
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ,colorrole <hex>\n{self.reply} example: ,colorrole 636890",
                inline=False,
            )
            return await ctx.reply(embed=e)

        success = False
        try:
            r = discord.utils.get(ctx.guild.roles, name=f"color-{ctx.author.id}")
            try:
                await r.edit(color=eval(f"0x{hexx}"))
                success = True
            except:
                try:
                    await r.delete()
                    role = await ctx.guild.create_role(
                        name=f"color-{ctx.author.id}", color=eval(f"0x{hexx}")
                    )
                    await ctx.author.add_roles(role, reason="color role")
                    success = True
                except:
                    role = await ctx.guild.create_role(
                        name=f"color-{ctx.author.id}", color=eval(f"0x{hexx}")
                    )
                    await ctx.author.add_roles(role, reason="color role")
                    success = True

        except:
            pass

        if success == False:
            ret = ":thumbsdown:"
        elif success == True:
            ret = ":thumbsup:"
        await ctx.reply(ret)

    @commands.hybrid_command(aliases=["ma"])
    # @commands.bot_has_permissions(move_members=True)
    @utils.perms("manage_messages")
    async def moveall(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        async for m in utils.aiter(ctx.guild.members):
            if m.voice.channel:
                await m.edit(voice_channel=user.voice.channel)

        await ctx.reply(":thumbsup:")

    @commands.hybrid_command(aliases=["dcall"])
    # @commands.bot_has_permissions(move_members=True)
    @utils.perms("manage_messages")
    async def disconnectall(self, ctx):

        async for m in utils.aiter(ctx.guild.members):
            if m.voice.channel:
                await m.edit(voice_channel=None)

        await ctx.reply(":thumbsup:")

    @commands.hybrid_command(aliases=["dcuser"])
    # @commands.bot_has_permissions(move_members=True)
    @utils.perms("manage_messages")
    async def disconnectuser(self, ctx, user: discord.Member = None):

        if not user:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** username",
                )
            )

        await user.edit(voice_channel=None)
        await ctx.reply(":thumbsup:")

    @commands.hybrid_command()
    # @commands.bot_has_permissions(move_members=True)
    @utils.perms("manage_messages")
    async def move(
        self, ctx, user: discord.Member = None, channel: discord.VoiceChannel = None
    ):

        if not user:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** username",
                )
            )
        if not channel:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** voice channel",
                )
            )

        await user.edit(voice_channel=channel)
        await ctx.reply(":thumbsup:")

    @commands.command(aliases=["e"])
    async def enlarge(
        self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji] = None
    ):

        cc = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        cc.set_footer(
            text="utility",
            icon_url=None,
        )
        cc.set_author(name="enlarge", icon_url=self.bot.user.avatar)
        cc.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** enlarge an emoji\n{self.reply} **aliases:** e",
            inline=False,
        )
        cc.add_field(
            name=f"{self.dash} Usage",
            value=f"{self.reply} syntax: ,enlarge <emoji>\n{self.reply} example: ,enlarge :50DollaLemonade:",
            inline=False,
        )

        if not emoji:
            return await ctx.reply(embed=cc)

        ret = emoji.url
        em = discord.Embed(color=utils.color("main"))
        em.title = emoji.name
        em.url = ret
        em.set_image(url=ret)
        v = discord.ui.View()
        v.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link, url=str(ret), label="download"
            )
        )
        await ctx.reply(embed=em, view=v)

    @commands.hybrid_command(aliases=["ce"])
    async def createembed(self, ctx, *, code: str=None):

        if not code:
            return await ctx.reply('https://rival.rocks/embedbuilder')        
        objects = await utils.to_object(await utils.embed_replacement(ctx.author, code))
        await ctx.send(**objects)

    @commands.command()
    async def actives(self, ctx):

        async with ctx.channel.typing():
            x = self.bot.db("messages")
            lst = []
            num = 0
            pagenum = 0
            embeds = []
            async for u, msgs in utils.aiter(
                sorted(x.get(str(ctx.guild.id)).items(), key=lambda x: x[1])[::-1]
            ):
                try:
                    num += 1
                    lst.append(
                        f"`{num}` **{await ctx.guild.fetch_member(u)}** — **{msgs:,}**"
                    )
                except:
                    pass
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(lst, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description="\n".join(page),
                        timestamp=datetime.now(),
                    )
                    .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                    .set_thumbnail(url=ctx.guild.icon)
                    .set_footer(
                        text=f"{pagenum}/{len(pages)} ({num} entries)",
                        icon_url=None,
                    )
                )
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

        # await ctx.reply(embed=discord.Embed(color=utils.color('main'), description='\n'.join(lst)).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon).set_thumbnail(url=ctx.guild.icon))

    @commands.command()
    async def rank(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        async with ctx.channel.typing():
            y = self.bot.db("levels")
            lst = []
            num = 0
            # experience=x.get(str(ctx.guild.id)).get(str(user.id))['experience']#rank=sorted(x.get(str(ctx.guild.id)).items(), key=lambda x: .index(str(ctx.author.id))+1['level'])[::-1].index(str(user.id))+1

            x = {}
            async for u, p in utils.aiter(
                self.bot.db("levels").get(str(ctx.guild.id)).items()
            ):
                try:
                    z: dict = p
                    x[u] = z
                except:
                    pass
            x.pop("message")
            x.pop("state")
            x = sorted(x.items(), key=lambda p: p[1]["level"])[::-1]
            z = sorted(x, key=lambda u: u[0] == str(user.id))[::-1][0]
            p = x.index(z)
            rank = p + 1

            level = y.get(str(ctx.guild.id)).get(str(user.id))["level"]

        await ctx.reply(
            embed=discord.Embed(
                color=utils.color("main"),
                description=f"**rank:** `{rank:,}`\n**level:** `{level:,}`\n**experience needed:** `{xp_to_next_level(level):,}`",
            )
            .set_author(name=user.name, icon_url=user.display_avatar)
            .set_thumbnail(url=ctx.guild.icon)
        )

    @commands.group(fallback="levels", aliases=["lb"], invoke_without_command=True)
    async def leaderboard(self, ctx):
        pass

    @leaderboard.command(name="levels", aliases=["lvls"])
    async def lb_levels(self, ctx):

        async with ctx.channel.typing():
            x = {}
            async for u, p in utils.aiter(
                self.bot.db("levels").get(str(ctx.guild.id)).items()
            ):
                if u not in ["message", "state"]:
                    z: dict = p
                    x[u] = z
                x = sorted(x.items(), key=lambda p: p[1]["level"])[::-1]
            lst = []
            num = 0
            pagenum = 0
            embeds = []
            async for u in utils.aiter(x):
                try:
                    num += 1
                    lst.append(
                        f"`{num}` **{await ctx.guild.fetch_member(int(u[0]))}** — **{u[1]['level']}**"
                    )
                except:
                    pass
                pages = [p async for p in utils.aiter(discord.utils.as_chunks(lst, 10))]
                async for page in utils.aiter(pages):

                    pagenum += 1
                    embeds.append(
                        discord.Embed(color=0x2F3136, description="\n".join(page))
                        .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                        .set_thumbnail(url=ctx.guild.icon)
                        .set_footer(
                            text=f"{pagenum}/{len(pages)} ({num} entries)",
                            icon_url=None,
                        )
                    )
                paginator = pg.Paginator(
                    self.bot, embeds, ctx, invoker=None, timeout=30
                )
                paginator.add_button("prev", emoji=utils.emoji("prevpage"))
                paginator.add_button("goto", emoji=utils.emoji("choosepage"))
                paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

        # await ctx.reply(embed=discord.Embed(color=utils.color('main'), description='\n'.join(lst)).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon).set_thumbnail(url=ctx.guild.icon))

    @leaderboard.command(name="messages", aliases=["msgs"])
    async def lb_messages(self, ctx):

        async with ctx.channel.typing():
            x = self.bot.db("messages")
            lst = []
            num = 0
            pagenum = 0
            embeds = []
            async for u, msgs in utils.aiter(
                sorted(x.get(str(ctx.guild.id)).items(), key=lambda x: x[1])[::-1]
            ):
                try:
                    num += 1
                    lst.append(
                        f"`{num}` **{await ctx.guild.fetch_member(u)}** — **{msgs:,}**"
                    )
                except:
                    pass
            pages = [p async for p in utils.aiter(discord.utils.as_chunks(lst, 10))]
            async for page in utils.aiter(pages):

                pagenum += 1
                embeds.append(
                    discord.Embed(color=0x2F3136, description="\n".join(page))
                    .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                    .set_thumbnail(url=ctx.guild.icon)
                    .set_footer(
                        text=f"{pagenum}/{len(pages)} ({num} entries)",
                        icon_url=None,
                    )
                )
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("goto", emoji=utils.emoji("choosepage"))
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

        # await ctx.reply(embed=discord.Embed(color=utils.color('main'), description='\n'.join(lst)).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon).set_thumbnail(url=ctx.guild.icon))

    @commands.command()
    async def weather(self, ctx, *, location: str):
        location = location.replace(" ", "+")
        req = await (
            await self.bot.session.get(
                f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?unitGroup=metric&key=4G437RNSM6FDH6EFGXCJ5VX5Q&contentType=json"
            )
        ).json()
        title = req["resolvedAddress"]
        description = req["days"][0]["description"]
        feelslike = int(req["days"][0]["feelslike"]) * 1.8 + 32
        temperature = int(req["days"][0]["temp"]) * 1.8 + 32
        embed = discord.Embed(color=utils.color("main"))
        embed.description = description
        embed.title = title
        embed.add_field(name="Temperature", value=f"{temperature} °F")
        embed.add_field(name="Feels Like", value=f"{feelslike} °F", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.set_thumbnail(url=ctx.author.display_avatar)
        await ctx.reply(embed=embed)

        # await ctx.reply(embed=discord.Embed(color=utils.color('main'), title='recent available tags', description='\n'.join(lst)))

    @commands.command()
    async def testec(self, ctx, chnnl: discord.TextChannel):

        embed = discord.Embed()

        class embedCreator(discord.ui.View):
            def __init__(
                self, embed: discord.Embed, channel: discord.TextChannel, bot, ctx=ctx
            ):
                self.embed = embed
                self.channel = channel
                self.author: str = None
                self.description: str = None
                self.footer: str = None
                self.author_icon: str = None
                self.thumbnail: str = None
                self.image: str = None
                self.bot = bot
                self.ctx = ctx
                super().__init__(timeout=180)

            @discord.ui.button(label="send", style=discord.ButtonStyle.green)
            async def setup_send(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != self.ctx.author.id:
                    return

                try:
                    self.embed.set_author(name=self.author, icon_url=self.author_icon)
                except:
                    pass
                try:
                    self.embed.description = self.description
                except:
                    pass
                try:
                    self.embed.set_footer(text=self.footer)
                except:
                    pass
                try:
                    self.embed.set_thumbnail(url=self.thumbnail)
                except:
                    pass
                try:
                    self.embed.set_image(url=self.image)
                except:
                    pass
                try:
                    if self.timestamp:
                        self.embed.timestamp = datetime.now()
                except:
                    pass

                try:
                    await self.channel.send(embed=self.embed)
                except:
                    return await interaction.response.send_message(
                        traceback.format_exc()
                    )

            @discord.ui.button(label="author", style=discord.ButtonStyle.grey)
            async def setup_author(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != self.ctx.author.id:
                    return

                await interaction.response.send_message("what should the author be?")
                # await interaction.response.defer()
                message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user
                    and m.channel == interaction.channel,
                    timeout=30,
                )
                self.author = None if not message.content else message.content
                await message.add_reactions("👍")

            @discord.ui.button(label="description", style=discord.ButtonStyle.grey)
            async def setup_description(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != self.ctx.author.id:
                    return

                await interaction.response.send_message(
                    "what should the description be?"
                )
                # await interaction.response.defer()
                message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user
                    and m.channel == interaction.channel,
                    timeout=30,
                )
                self.description = None if not message.content else message.content
                await message.add_reactions("👍")

            @discord.ui.button(label="footer", style=discord.ButtonStyle.grey)
            async def setup_footer(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != self.ctx.author.id:
                    return

                await interaction.response.send_message("what should the footer be?")
                # await interaction.response.defer()
                message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user
                    and m.channel == interaction.channel,
                    timeout=30,
                )
                self.footer = None if not message.content else message.content
                await message.add_reactions("👍")

            @discord.ui.button(label="author icon", style=discord.ButtonStyle.grey)
            async def setup_author_icon(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != self.ctx.author.id:
                    return

                await interaction.response.send_message(
                    "what should the author icon be?"
                )
                # await interaction.response.defer()
                message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user
                    and m.channel == interaction.channel,
                    timeout=30,
                )
                self.author_icon = None if not message.content else message.content
                await message.add_reactions("👍")

            @discord.ui.button(label="thumbnail", style=discord.ButtonStyle.grey)
            async def setup_thumbnail(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != self.ctx.author.id:
                    return

                await interaction.response.send_message("what should the thumbnail be?")
                # await interaction.response.defer()
                message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user
                    and m.channel == interaction.channel,
                    timeout=30,
                )
                self.thumbnail = None if not message.content else message.content
                await message.add_reactions("👍")

            @discord.ui.button(label="image", style=discord.ButtonStyle.grey)
            async def setup_image(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != self.ctx.author.id:
                    return

                await interaction.response.send_message("what should the image be?")
                # await interaction.response.defer()
                message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user
                    and m.channel == interaction.channel,
                    timeout=30,
                )
                self.image = None if not message.content else message.content
                await message.add_reactions("👍")

        await ctx.reply(view=embedCreator(embed=embed, channel=chnnl, bot=self.bot))

    @commands.command(aliases=["aboutme"])
    async def bio(self, ctx, *, user: discord.User | discord.Member = commands.Author):

        await ctx.typing()
        embed = discord.Embed(color=utils.color("main"))
        embed.set_footer(icon_url=None)
        embed.description = f"{'none' if ((await self.bot.get_user_data(user))['bio']) == '' else ((await self.bot.get_user_data(user))['bio'])}"
        embed.set_author(name=user, icon_url=user.display_avatar)
        await ctx.reply(embed=embed)

    @commands.hybrid_group(invoke_without_command=False)
    @utils.perms("manage_emojis")
    async def emoji(self, ctx):
        ...

    @emoji.command(name="dump")
    @utils.perms("manage_emojis")
    async def emoji_dump(self, ctx, guild: discord.Guild):

        async with ctx.channel.typing():
            async for emoji in utils.aiter(guild.emojis):
                try:
                    await ctx.guild.create_custom_emoji(
                        name=emoji.name, image=await emoji.read()
                    )
                except:
                    continue

        await ctx.reply(":thumbsup:")

    @commands.command(aliases=["copy"])
    async def copyembed(self, ctx, message: discord.Message = None):

        await ctx.typing()
        if not message and ctx.message.reference:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        if not message.author.bot:
            return await ctx.reply("the message must belong to a bot :thumbsdown:")
        if not message.embeds:
            return await ctx.reply("that message has no embeds :thumbsdown:")

        embed = discord.Embed(color=0x2F3136)
        embed.description = f"```{json.dumps(message.embeds[0].to_dict(), indent=4)}```"
        await ctx.reply(embed=embed)

    @commands.command()
    async def vanity(self, ctx, a: str):

        await ctx.typing()
        x = await self.bot.session.get(f"https://discord.com/api/v10/invites/{a}")
        if x.status == 200:
            return await ctx.reply(f"vanity **{a}** is taken :thumbsdown:")
        elif x.status == 404:
            return await ctx.reply(f"vanity **{a}** is available")

    @commands.command(aliases=["ud"])
    async def urban(self, ctx, *, word):

        await ctx.typing()
        api = "http://api.urbandictionary.com/v0/define"
        ret = await self.bot.session.get(api, params={"term": word})
        ret = await ret.json()
        embeds = []
        num = 0
        if len(word) > 50:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** please **provide** a word under 50 chars",
                )
            )
        noresultembed = discord.Embed(
            color=utils.color("main"),
            description=f"{self.error} {ctx.author.mention}**:** no results found for **`{word}`**",
        )
        if len(ret["list"]) == 0:
            return await ctx.reply(embed=noresultembed)

        async for i in utils.aiter(ret["list"][:3]):
            num += 1
            embed = discord.Embed(color=utils.color("main")).set_author(
                name=word, icon_url=self.bot.user.display_avatar
            )
            if i["example"]:
                embed.add_field(
                    name=f"{self.dash} Definition",
                    value=f"{i['definition'].replace('[', '**').replace(']', '**')}",
                    inline=False,
                )
                embed.add_field(
                    name=f"{self.dash} Examples",
                    value=f"{i['example'].replace('[', '**').replace(']', '**')}",
                )
                embed.set_footer(
                    text=f'{num}/3 ; 👍 {i["thumbs_up"]} 👎 {i["thumbs_down"]}',
                    icon_url=None,
                )
            embeds.append(embed)

        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None, timeout=30)
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        await paginator.start()

    @commands.command()
    async def translate(
        self,
        ctx,
        *,
        message: typing.Annotated[typing.Optional[str], commands.clean_content] = None,
    ):

        loop = self.bot.loop
        if not message:
            ref = ctx.message.reference
            if ref and isinstance(ref.resolved, discord.Message):
                message = ref.resolved.content
            else:
                return

        ret = self.trans.translate(message)

        embed = discord.Embed(color=utils.color("main"))
        src = googletrans.LANGUAGES.get(ret.src, "(auto-detected)").title()
        dest = googletrans.LANGUAGES.get(ret.dest, "Unknown").title()
        embed.add_field(name=f"{self.dash} from {src}", value=ret.origin, inline=False)
        embed.add_field(name=f"{self.dash} to {dest}", value=ret.text, inline=False)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["geolookup", "lookup", "geo"])
    async def iplookup(self, ctx, *, ipaddr: str = None):

        if not ipaddr:

            lookupEmbed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            lookupEmbed.set_footer(text=f"utility")
            lookupEmbed.set_author(
                name=f"iplookup", icon_url=self.bot.user.display_avatar
            )
            lookupEmbed.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** get more information on a provided ip address\n{self.reply} **aliases:** iplookup, lookup, geolookup, geo",
                inline=False,
            )
            lookupEmbed.add_field(
                name=f"{self.dash} Usage",
                value=f"{self.reply} **syntax:** ,iplookup <ip address>\n{self.reply} **example:** ,iplookup 12.34.567.890",
            )

            await ctx.reply(embed=lookupEmbed)

        else:

            await ctx.message.add_reaction("<a:vile_loading:1003252144377446510>")

            geo = await self.bot.session.get(
                f"https://extreme-ip-lookup.com/json/{ipaddr}?key=H3X2LfhHgIB7Ab7wcWgb"
            )
            r = await geo.json()

            embed = discord.Embed(color=0x636890, timestamp=datetime.now())
            embed.add_field(name="IP", value=r["query"])
            embed.add_field(name="IP Type", value=r["ipType"])
            embed.add_field(name="Country", value=r["country"])
            embed.add_field(name="City", value=r["city"])
            embed.add_field(name="Continent", value=r["continent"])
            embed.add_field(name="Internet Service Provider", value=r["isp"])
            embed.add_field(name="IP Name", value=r["ipName"])
            embed.add_field(name="Latitude", value=r["lat"])
            embed.add_field(name="Longitude", value=r["lon"])
            embed.add_field(name="Organization", value=r["org"])
            embed.add_field(name="Region", value=r["region"])
            embed.add_field(name="Status", value=r["status"])
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            embed.set_footer(text=ipaddr)

            await ctx.message.clear_reaction("<a:vile_loading:1003252144377446510>")
            await ctx.reply(embed=embed)

    @commands.command(
        name="auditlogs",
        aliases=["logs"],
        description="view the recent audit logs",
        brief=",auditlogs [index]",
        help=",auditlogs 2",
    )
    @commands.bot_has_permissions(view_audit_log=True)
    @utils.perms("view_audit_log")
    async def auditlogs(self, ctx, index: int = 1):

        if index > 100:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.fail} {ctx.author.mention}**:** please provide an index **under** 100",
                )
            )
        log = [log async for log in ctx.guild.audit_logs(limit=index)][index - 1]
        reason = "N/A" if not log.reason else log.reason
        mod = str(log.user)
        action = str(log.action).split(".")[1].replace("_", " ").title()
        try:
            category = str(log.category).split(".")[1]
        except:
            category = "N/A"
        try:
            target = log.target.name
        except:
            target = "N/A"
        created = utils.moment(log.created_at)

        embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        embed.set_footer(text="audit logs", icon_url=None)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        embed.title = action
        embed.description = f"{self.bot.reply} **moderator:** {mod}\n{self.bot.reply} **reason:** {reason}\n{self.bot.reply} **target:** {target}\n{self.bot.reply} **recorded:** {created} ago"

        return await ctx.reply(embed=embed)

    @commands.command(
        name='stickers',
        description='get the stickers of a message',
        syntax=',stickers [message]',
        example=',stickers ...'
    )
    async def stickers(self, ctx, message: discord.Message=None):
        
        if not message:
            if ctx.message.reference:
                message=ctx.message.reference.resolved
            else:
                message=[msg async for msg in ctx.channel.history(limit=2, oldest_first=True)][0]
                
        if not message.stickers:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.fail} {ctx.author.mention}**:** could not find any **stickers**'
                )
            )
            
        embed=discord.Embed(color=0x2f3136)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.set_image(url=message.stickers[0].url)
        
        return await ctx.reply(embed=embed)

    @commands.command(
        name='translate',
        aliases=['tr'],
        description='translate text to a language of your choice',
        syntax=',translate (language) (text)',
        example=',translate english hola doy dora'
    )
    async def translate(self, ctx, lang: str, *, text: str):
        
        try:
            from deep_translator import GoogleTranslator
        
            trans=GoogleTranslator(
                source='auto',
                target=lang
            )
            
            return await ctx.reply(trans.translate(text=text))
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.fail} {ctx.author.mention}**:** failed to **translate** the provided text'
                )
            )                

    @commands.command(
        name='copyembed',
        aliases=['embedcode'],
        description='get the code of an embed',
        syntax=',copyembed (message)',
        example=',copyembed 1047076267838676992'
    )
    async def copyembed(self, ctx, message: typing.Optional[discord.Message]=None):
        
        if not message:
            if not ctx.message.reference:
                return
            message=ctx.message.reference.resolved
            
        if not message.embeds:
            return
        
        embed=message.embeds[0]
        code='{embed}'
        if embed.description:
            code+='{description: '+embed.description+'}'
            
        if embed.title:
            code+='$v{title: '+embed.title+'}'
            
        if embed.footer:
            x=''
            if embed.footer.text:
                x+=embed.footer.text
            if embed.footer.icon_url:
                x+=f' && icon: {embed.footer.icon_url}'
            code+='$v{footer: '+x+'}'
            
        if embed.thumbnail:
            code+='$v{thumbnail: '+embed.thumbnail.url+'}'
            
        if embed.image:
            code+='$v{image: '+embed.image.url+'}'
            
        if embed.fields:
            for field in embed.fields:
                x=''
                n=field.name
                v=field.value
                i=field.inline
                x+=f'{n} && value: {v} && inline: {"true" if i else "false"}'
                code+='$v{field: '+x+'}'
                
        if embed.author:
            x=''
            n=embed.author.name
            i=embed.author.icon_url
            u=embed.author.url
            x+=n
            if i:
                x+=f' && icon: {i}'
            if u: 
                x+=f' && url: {u}'
            code+='$v{author: '+x+'}'
                
        if embed.timestamp:
            code+='$v{timestamp: true}'
            
        if message.components:
            comp=message.components[0]
            if isinstance(comp, discord.ActionRow):
                for button in comp.children:
                    if button.style == discord.ButtonStyle.link:
                        x=''
                        l=button.label
                        u=button.url
                        x+=f'{l} && link: {u}'
                        code+='$v{label: '+x+'}'
                        
        if embed.color:
            if embed.color.value == 0:
                code+='$v{color: #000000}'
            else:
                c=hex(embed.color.value).replace('0x', '')
                code+='$v{color: #'+c+'}'
                
        code+='$v'
        return await ctx.reply(code)

async def setup(bot):

    await bot.add_cog(utility(bot))
