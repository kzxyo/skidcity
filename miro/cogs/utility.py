from code import interact
from email.mime import image
from inspect import trace
from re import L
import discord, datetime, math, typing, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import paginator as pg
from modules import utils
from typing import Optional, Union
from discord import Embed, File, TextChannel, Member, User, Role 
from discord.ui import Button, View
from discord.ext.commands import Context

async def paginator(self, ctx, pages):
        if len(pages) == 1:
            await ctx.send(embed=pages[0])
            return

        def check(interaction):
            if interaction.user.id != ctx.author.id:
                return False

        class PaginatorView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.bot = ctx.bot
                self.current = 0

            @discord.ui.button(style=discord.ButtonStyle.gray, label="<")
            async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
                if check(interaction) is False:
                    return interaction.response.defer()
                if self.current == 0 or self.current < 0:
                    await interaction.response.defer()
                    return
                try:
                    self.current -= 1
                    await interaction.response.edit_message(embed=pages[self.current])
                except:
                    await interaction.response.defer()

            @discord.ui.button(label=">", style=discord.ButtonStyle.gray)
            async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                if check(interaction) is False:
                    return interaction.response.defer()
                if self.current == len(pages) - 1:
                    await interaction.response.defer()
                    return
                self.current += 1
                try:
                    await interaction.response.edit_message(embed=pages[self.current])
                except:
                    await interaction.response.defer()

            @discord.ui.button(label="x", style=discord.ButtonStyle.red)
            async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
                if check(interaction) is False:
                    return interaction.response.defer()
                await interaction.response.edit_message(content=":thumbsup_tone2: Stopped interaction", embed=None, view=None)
                self.stop()
                
        paginator = PaginatorView()
        await ctx.send(embed=pages[0], view=paginator)
        await paginator.wait()


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

def human_format(number):
    if number > 999: return humanize.naturalsize(number, False, True) 
    return number 

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

    @commands.command(
        name="banner",
        aliases=["userbanner"],
        description="get the mentioned user's banner",
        usage="banner [user]",
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
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
                    label="webp",
                    url=str(user.banner.replace(format="webp")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="png",
                    url=str(user.banner.replace(format="png")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="jpg",
                    url=str(user.banner.replace(format="jpg")),
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="gif",
                    url=str(user.banner.replace(format="gif")),
                )
            )
        except:
            view = None

        return await ctx.reply(embed=embed, view=view)


    @commands.command(
        name="serverinfo",
        usage="serverinfo <server>",
        example="/mirobot",
        aliases=["sinfo", "guildinfo", "ginfo", "si", "gi"],
    )
    async def serverinfo(
        self,
        ctx,
        *,
        server: discord.Guild | discord.Invite = None,
    ):

        if isinstance(server, discord.Invite):
            _invite = server
            server = server.guild
            if not self.bot.get_guild(server.id):
                return await self.bot.get_command("inviteinfo")(ctx, server=_invite)

        server = self.bot.get_guild(server.id) if server else ctx.guild

        embed = discord.Embed(
            description=(discord.utils.format_dt(server.created_at, "f") + " (" + discord.utils.format_dt(server.created_at, "R") + ")")
        )
        embed.set_author(
            name=f"{server} ({server.id})",
            icon_url=server.icon,
        )
        embed.set_image(url=server.banner.with_size(1024).url if server.banner else None)

        embed.add_field(
            name="Information",
            value=(
                f">>> **Owner:** {server.owner or server.owner_id}"
                + f"\n**Shard ID:** {server.shard_id}"
                + f"\n**Verification:** {server.verification_level.name.title()}"
                + f"\n**Notifications:** {'Mentions' if server.default_notifications == discord.NotificationLevel.only_mentions else 'All Messages'}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Statistics",
            value=(
                f">>> **Members:** {server.member_count:,}"
                + f"\n**Text Channels:** {len(server.text_channels):,}"
                + f"\n**Voice Channels:** {len(server.voice_channels):,}"
                + f"\n**Nitro Boosts:** {server.premium_subscription_count:,} (`Level {server.premium_tier}`)"
            ),
            inline=True,
        )

        if server == ctx.guild and (roles := list(reversed(server.roles[1:]))):
            embed.add_field(
                name=f"Roles ({len(roles)})",
                value=">>> " + ", ".join([role.mention for role in roles[:7]]) + (f" (+{(len(roles) - 7)})" if len(roles) > 7 else ""),
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.group(
        name="guild",
        aliases=["server"],
        description="get info about the current or provided server",
        usage="serverinfo (invite)",
        invoke_without_command=True,
    )
    async def guild(self, ctx, guild: Optional[discord.Invite] = None):
        return await ctx.invoke(self.bot.get_command("serverinfo"), guild=guild)

    @commands.cooldown(1, 3, commands.BucketType.guild)
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

    @commands.command(
        name="servericon",
        description="View the icon of a server",
        usage="servericon <guild>",
        aliases=["icon", "guildicon", "sicon", "gicon"],
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def servericon(self, ctx, *, guild: discord.Guild = None):
        ctx.typing()
        guild = ctx.guild if guild is None else guild
        e = discord.Embed(
            title=f"{guild.name}'s server icon", url=guild.icon.url, color=0x4c5264
        )
        e.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        e.set_image(url=guild.icon.url)
        await ctx.send(embed=e)



    @commands.command(name = "nuke", description = "Remakes the channel with same permissions",aliases=['remake'], usage = "nuke")
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 12, commands.BucketType.guild)
    async def nuke(self, ctx):
        channel_info = [ctx.channel.category, ctx.channel.position]
        await ctx.channel.clone()
        await ctx.channel.delete()
        embed = discord.Embed(
            description=f"{self.done} channel nuked by **{ctx.author}**", color=0x4c5264
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/769749773401849896/776951922295963648/giphy-downsized-large.gif"
        )
        new_channel = channel_info[0].text_channels[-1]
        await new_channel.edit(position=channel_info[1])
        await new_channel.send(embed=embed)

    @guild.command(name="bots", aliases=["botlist"])
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
                        color=0x4c5264,
                        description=" ".join(page),
                        title=f"Bot list",
                        timestamp=datetime.now(),
                    ).set_footer(
                        text=f"{pagenum}/{len(pages)} ({num} entries)",
                        icon_url=None,
                    )
                )
            from modules import paginator as pg
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()

        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **emojis** in the guild",
                )
            )

    @commands.hybrid_command(name = "botclear", description = "Delete all bot messages",aliases=['bc', 'cleanup'], usage = "botclear")
    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def botclear(self, ctx):
        await ctx.typing()
        await ctx.channel.purge(limit=100, check=lambda m: m.author.bot)
        await ctx.send(":thumbsup:")

    @commands.command(
        name="joinposition",
        aliases=["joinpos"],
        description="view your join position",
        usage="joinposition [member]",
    )
    async def joinposition(self, ctx, member: discord.Member = commands.Author):
        join_position = utils.ordinal(
            sorted(ctx.guild.members, key=lambda m: m.joined_at).index(member) + 1
        )
        return await ctx.reply(f"{member.name} is the **{join_position}** member")


    @commands.hybrid_command(name = "afk", description = "Go afk with a reason",aliases=['dnd'], usage = "afk (reason)")
    @commands.cooldown(1, 4, commands.BucketType.guild)
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

    @commands.hybrid_command(name = "boosters", description = "Return all server boosters",aliases=['boosts', 'boostcount'], usage = "boostcount")
    @commands.cooldown(1, 4, commands.BucketType.guild)
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
                        color=0x4c5264,
                        description=" ".join(page),
                        title=f"booster list",
                        timestamp=datetime.now(),
                    ).set_footer(
                        text=f"{pagenum}/{len(pages)} ({num} entries)",
                        icon_url=None,
                    )
                )
            from modules import paginator as pg
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()

        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** there are no **boosters** in the guild",
                )
            )


    @commands.hybrid_command(name = "firstmessage", description = "View first message of channel",aliases=['firstmsg'], usage = "firstmsg")
    @commands.cooldown(1, 4, commands.BucketType.guild)
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




    @commands.hybrid_command(name = "discordstatus", description = "View discord status/game",aliases=['ds'], usage = "discordstatus [user]")
    async def discordstatus(self, ctx, user: discord.Member = None):

        user = ctx.author if not user else user
        status = "none" if not user.activity.name else user.activity.name
        e = discord.Embed(color=0x4c5264, description=status)
        e.set_author(name=f"{user.name}'s status", icon_url=user.avatar)
        await ctx.reply(embed=e)

    @commands.hybrid_command(name = "invites", description = "Show all invites a user has",aliases=['invs'], usage = "invites [user]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def invites(self, ctx, user: discord.Member = None):
        user = ctx.author if not user else user
        totalInvites = 0
        async for i in utils.aiter(await ctx.guild.invites()):
            if i.inviter == user:
                totalInvites += i.uses
        await ctx.reply(
            embed=discord.Embed(
                color=0x4c5264,
                description=f"{self.done} {ctx.author.mention}: **{user.name}** has **{totalInvites}** invite{'s' if totalInvites != 1 else ''}",
            )
        )

    @commands.hybrid_command(name = "messages", description = "Show total messages of a user",aliases=['msgs', 'activity'], usage = "messages [user]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def messages(self, ctx, *, user: discord.Member = None):
        user = ctx.author if not user else user
        db = utils.read_json("messages")
        try:
            msgs = db[str(ctx.guild.id)][str(user.id)]
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("main"),
                    description=f"{self.done} {ctx.author.mention}**: {user.name}** has sent {msgs} message{'s' if msgs != 1 else ''}",
                )
            )
        except:
            await ctx.reply(
                embed=discord.Embed(
                    color=utils.color("main"),
                    description=f"{self.done} {ctx.author.mention}**: {user.name}** has sent 0 message{'s' if 0 != 1 else ''}",
                )
            )

    @commands.hybrid_command(name = "colorrole", description = "Make a role a color",aliases=['cr'], usage = "cr [color]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.member, wait=False)
    async def colorrole(self, ctx, hexx=None):
        if not hexx:
            e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
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
                value=f"{self.reply} syntax: ;colorrole <hex>\n{self.reply} example: ;colorrole 636890",
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

    @commands.hybrid_command(aliases=["dcuser"])
    @commands.cooldown(1, 4, commands.BucketType.guild)
    @commands.bot_has_permissions(move_members=True)
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
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.bot_has_permissions(move_members=True)
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

    @commands.command(name = "enlarge", description = "Enlarges a emoji",aliases=['e'], usage = "enlarge [emoji]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def enlarge(
        self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji] = None
    ):
        cc = discord.Embed(color=0x4c5264, timestamp=datetime.now())
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
            value=f"{self.reply} syntax: ;enlarge <emoji>\n{self.reply} example: ;enlarge :50DollaLemonade:",
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

    @commands.command(name = "weather", description = "View weather in country/location",aliases=['temptature'], usage = "weather [location]")
    @commands.cooldown(1, 6, commands.BucketType.guild)
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


    @commands.hybrid_group(invoke_without_command=False)
    @utils.perms("manage_emojis")
    async def emoji(self, ctx):
        ...

    @emoji.command(name="dump")
    @commands.cooldown(1, 4, commands.BucketType.guild)
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


    @commands.command(name = "vanitycheck", description = "Check if a vanity is available",aliases=['van'], usage = "vanity [vanity name]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def vanitycheck(self, ctx, a: str):
        await ctx.typing()
        x = await self.bot.session.get(f"https://discord.com/api/v10/invites/{a}")
        if x.status == 200:
            return await ctx.reply(f"{self.fail} vanity **{a}** is taken :thumbsdown:")
        elif x.status == 404:
            return await ctx.reply(f"{self.done} vanity **{a}** is available or termed")

    @commands.command(
        name="auditlogs",
        aliases=["alogs"],
        description="view the recent audit logs",
        usage=";auditlogs [index]",
    )
    @commands.cooldown(1, 4, commands.BucketType.guild)
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

        embed = discord.Embed(color=0x4c5264, timestamp=datetime.now())
        embed.set_footer(text="audit logs", icon_url=None)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        embed.title = action
        embed.description = f"{self.bot.reply} **moderator:** {mod}\n{self.bot.reply} **reason:** {reason}\n{self.bot.reply} **target:** {target}\n{self.bot.reply} **recorded:** {created} ago"

        return await ctx.reply(embed=embed)


    @commands.command(name = "mods", description = "View all guild mods", aliases=['moderators'], usage = "mods")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def mods(self, ctx):
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "<:OnlineStatus:1107307724506661026>"},
            "idle": {"users": [], "emoji": "<:idle:1107307740927377409>"},
            "dnd": {"users": [], "emoji": "<:dnd:1110552530766802944>"},
            "offline": {"users": [], "emoji": "<:OfflineStatus:1107307726947745863>"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"
        await ctx.send(embed=Embed(
           title="All Discord Moderators Online",
           description=f">>> {message}"
        ))


    @commands.command(
        description="lookup a user by username",
        usage="lookup <username>",
        aliases=["lu", "userlook"],
    )
    async def lookup(self, ctx: commands.Context, *, username: str):
        users = []
        for user in self.bot.users:
            if username.lower() in user.name.lower():
                users.append(user)

        if not users:
            return await ctx.reply("no users found")

        pages = []
        for i in range(0, len(users), 10):
            embed = discord.Embed(
                color=self.bot.color,
                title=f"users • {len(users)}"
            )
            page = ""
            for user in users[i:i+10]:
                page += f"{user.name} ({user.id})\n"
            embed.description = page
            pages.append(embed)

        await self.bot.paginator(ctx, pages)


    @commands.command(
        description="shows application info",
        usage="appinfo <botid>",
        aliases=["ai", "app", "a", "app-info"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def appinfo(self, ctx, id: int):
        try:
            response = await self.bot.session.get(f"https://discord.com/api/applications/{id}/rpc")
            res = await response.json()
        except:
            return await ctx.reply("Invalid application id")

        avatar = f"https://cdn.discordapp.com/avatars/{res['id']}/{res['icon']}.png?size=1024"

        embed = discord.Embed(color=self.bot.color, title=res["name"], description=res["description"] or "No description for this application found")
        embed.add_field(
            name="general",
            value=f"**id**: {res['id']}\n**name**: {res['name']}\n**bot public**: {res['bot_public']}\n**bot require code grant**: {res['bot_require_code_grant']}",
        )
        embed.set_thumbnail(url=avatar)

        return await ctx.reply(embed=embed)


    @commands.command(
        name='bans',
        usage= "bans",
        aliases=["banlist"],
        description="show a list of the server's banned members",
        extras={'permissions': 'ban members'}
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def bans(self, ctx: Context):

        if not [b async for b in ctx.guild.bans(limit=1)]:
            return await ctx.send_error(f"there aren't any **bans** in {ctx.guild.name}")
            
        embed = discord.Embed(color=self.bot.color, title=f'Bans in {ctx.guild.name}', description='')  # Initialize as an empty string
        async for ban in ctx.guild.bans(limit=500):
            embed.description += f'{ban.user.mention}: **{ban.user}** ( `{ban.user.id}` )\n'  # Concatenate the string

        paginator = pg.Paginator(self.bot, [embed], ctx, invoker=None, timeout=30)  # Pass embed as a list
        paginator.add_button("prev", emoji="<:left:1107307769582850079>")
        paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
        paginator.add_button("next", emoji="<:right:1107307767041105920>")
        paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
        await paginator.start()






async def setup(bot):
    await bot.add_cog(utility(bot))
