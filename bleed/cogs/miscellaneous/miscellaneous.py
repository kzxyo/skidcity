import colorsys

from datetime import datetime
from random import choice
from typing import List

import discord

from discord import Embed, Guild, Invite, Message
from discord.ext.commands import Cog, command, group, has_permissions
from discord.ui import Button, View
from discord.utils import format_dt
from yarl import URL

import config

from helpers import services
from helpers.bleed import Bleed
from helpers.converters import Color, Member, Role, TagScript, User
from helpers.managers import Context, cache
from helpers.utilities import hidden, human_timedelta, plural, shorten


class Miscellaneous(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot

    @Cog.listener("on_message")
    async def check_afk(self, message: Message) -> None:
        if (ctx := await self.bot.get_context(message)) and ctx.command:
            return

        elif author_afk_since := await self.bot.db.fetchval(
            """
            DELETE FROM afk
            WHERE user_id = $1
            RETURNING date
            """,
            message.author.id,
        ):
            await message.neutral(
                f"Welcome back, you were away for **{human_timedelta(author_afk_since, suffix=False)}**",
                emoji=config.Emoji.wave,
                reference=message,
            )

        elif len(message.mentions) == 1 and (user := message.mentions[0]):
            if user_afk := await self.bot.db.fetchrow(
                """
                SELECT status, date FROM afk
                WHERE user_id = $1
                """,
                user.id,
            ):
                await message.channel.neutral(
                    f"{user.mention} is AFK: **{user_afk['status']}** - {human_timedelta(user_afk['date'], suffix=False)}",
                    emoji="💤",
                    reference=message,
                )

    @Cog.listener("on_member_unboost")
    async def store_boost(self, member: Member) -> None:
        await self.bot.db.execute(
            """
            INSERT INTO boosters_lost (
                guild_id,
                user_id,
                started_at
            ) VALUES($1, $2, $3)
            ON CONFLICT (guild_id, user_id)
            DO UPDATE SET
                started_at = EXCLUDED.started_at,
                expired_at = NOW()
            """,
            member.guild.id,
            member.id,
            member.premium_since,
        )

    @command(
        name="check",
    )
    async def check(self, ctx: Context) -> Message:
        """
        Responds with an insulting message unless the bot isn't alive
        """

        return await ctx.send("What bitch?")

    @command(
        name="randomhex",
    )
    async def randomhex(self, ctx: Context) -> Message:
        """
        Generate a random hex (color)
        """

        return await self.bot.get_command("color")(ctx, "random")

    @command(
        name="color",
        usage="(hex, random, member, or role color)",
        example="#c2e746",
        aliases=[
            "colour",
        ],
    )
    async def color(self, ctx: Context, hex: Color = discord.Color(0)):
        """
        Show a hex codes color in a embed
        """

        embed = Embed(color=hex)
        embed.set_author(name=f"Showing hex code: {hex}")
        embed.set_thumbnail(
            url=(
                "https://place-hold.it/250x219/"
                + str(hex).replace("#", "")
                + "/?text=%20"
            )
        )

        embed.add_field(
            name="RGB Value",
            # 194, 231, 70
            value=", ".join(str(value) for value in hex.to_rgb()),
            inline=True,
        )
        embed.add_field(
            name="HSL Value",
            value=", ".join(
                f"{int(value * (360 if index == 0 else 100))}%"
                for index, value in enumerate(
                    colorsys.rgb_to_hls(*[x / 255.0 for x in hex.to_rgb()])
                )
            ),
            inline=True,
        )

        return await ctx.send(embed=embed)

    @command(
        name="wouldyourather",
        usage="<choice1> <choice2>",
        example="kiss a dog, kiss a cat",
        aliases=[
            "wyr",
        ],
    )
    async def wouldyourather(self, ctx: Context, *, choices: str = None) -> Message:
        """
        Would you rather?
        """

        if not choices or not (choices := choices.split(", ", 2)):
            data = await self.bot.session.request(
                "GET",
                "https://wouldurather.io/",
            )
            choices = [
                (
                    data.find(
                        "div",
                        {
                            "id": "box1",
                        },
                    ).text.replace("\n", "")
                ),
                (
                    data.find(
                        "div",
                        {
                            "id": "box2",
                        },
                    ).text.replace("\n", "")
                ),
            ]

        message = await ctx.send(
            f"**Would You Rather:**\n🅰️ {choices[0]}\n**OR**\n🅱️ {choices[1]}"
        )
        for reaction in ("🅰️", "🅱️"):
            await message.add_reaction(reaction)

        return message

    @command(
        name="choose",
        usage="(choices)",
        example="yes, no",
    )
    async def choose(self, ctx: Context, *, choices: str) -> Message:
        """
        Give me choices and I will pick for you
        """

        if not (choices := choices.split(", ")):
            return await ctx.warn(
                "Not **enough choices** to pick from - use a comma to separate"
            )

        return await ctx.neutral(
            f"I choose `{choice(choices)}",
            emoji="🤔",
        )

    @command(
        name="afk",
        usage="<status>",
        example="sleeping...(slart)",
    )
    async def afk(self, ctx: Context, *, status: str = "AFK") -> Message:
        """
        Set an AFK status for when you are mentioned
        """

        status = shorten(status, 100)
        await self.bot.db.execute(
            """
            INSERT INTO afk (
                user_id,
                status
            ) VALUES ($1, $2)
            ON CONFLICT (user_id)
            DO NOTHING;
            """,
            ctx.author.id,
            status,
        )

        await ctx.approve(f"You're now AFK with the status: **{status}**")

    @command(
        name="osu",
        usage="(username) <game>",
        example="skeleton 1",
    )
    async def osu(self, ctx: Context, username: str, game: int = 0) -> Message:
        """
        Retrieve simple OSU! profile information
        """

        data = await self.bot.session.request(
            "GET",
            "https://osu.ppy.sh/api/get_user",
            params={
                "k": config.Authorization.osu,
                "u": username,
                "m": min(game, 3),
            },
        )
        if not data:
            return await ctx.warn(f"No **osu! account** found for **{username}**")

        data = data[0]

        embed = Embed(
            url=f"https://osu.ppy.sh/u/{data.user_id}",
            title=(
                "Game: "
                + {
                    0: "Standard",
                    1: "Taiko",
                    2: "CtB",
                    3: "osu!mania",
                }[min(game, 3)]
            ),
            description=(
                "**Joined:** "
                + (
                    format_dt(
                        datetime.strptime(
                            data.join_date,
                            "%Y-%m-%d %H:%M:%S",
                        ),
                        style="D",
                    )
                    + " ("
                    + format_dt(
                        datetime.strptime(
                            data.join_date,
                            "%Y-%m-%d %H:%M:%S",
                        ),
                        style="R",
                    )
                    + ")"
                )
            ),
        )
        embed.set_author(
            name=data.username,
            icon_url=f"https://osu.ppy.sh/images/flags/{data.country}.png",
        )
        embed.set_thumbnail(url=f"https://a.ppy.sh/{data.user_id}")

        embed.add_field(
            name="PP",
            value=f"{int(float(data.pp_raw)):,}",
            inline=True,
        )
        embed.add_field(
            name="Rank",
            value=f"#{int(data.pp_rank):,} ({data.country}: {int(data.pp_country_rank):,})",
            inline=True,
        )
        embed.add_field(
            name="Level",
            value=f"{int(float(data.level)):,}",
            inline=True,
        )
        embed.add_field(
            name="Accuracy",
            value=f"{float(data.accuracy):.2f}%",
            inline=True,
        )
        embed.add_field(
            name="Score",
            value=f"{int(float(data.total_score)):,}",
            inline=True,
        )
        embed.add_field(
            name="Ranks",
            value=(
                f"SS: {int(data.count_rank_ss):,} | "
                f"S: {int(data.count_rank_s):,} | "
                f"A: {int(data.count_rank_a):,}"
            ),
            inline=True,
        )

        embed.set_footer(
            text="osu!",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/e/e3/Osulogo.png",
        )

        return await ctx.send(embed=embed)

    @command(
        name="wikihow",
        usage="(query)",
        example="How to get a girlfriend",
        aliases=[
            "wiki",
            "whow",
            "how",
        ],
    )
    async def wikihow(self, ctx: Context, *, query: str) -> Message:
        """
        How to...?
        """

        async with ctx.typing():
            data = await self.bot.session.request(
                "GET",
                "https://notsobot.com/api/search/wikihow",
                params={"query": query},
            )
            if not data:
                return await ctx.warn(f"No results were found for **{query}**")

            item = data[0]

            soup = await self.bot.session.request(
                "GET",
                item.url,
            )

        return await ctx.send(
            embed=Embed(
                url=item.url,
                title=item.title,
                description=(
                    f"{item.title}\n"
                    + "\n".join(
                        [
                            f"{index + 1} - {step.text}"
                            for index, step in enumerate(
                                soup.findAll("b", class_="whb")[:15]
                            )
                        ]
                    )
                    + (
                        f"\n... Too much to show, more available information @ {item.url}"
                        if len(soup.findAll("b", class_="whb")) > 15
                        else ""
                    )
                ),
            ).set_footer(
                text="Information from WikiHow",
                icon_url="https://lh3.googleusercontent.com/PRyVT9EUZs5elFJfMugM-cRUQM9rzegZiLdheMh-4Oc_ehFmG5lQN6vuFxOx_AN7r50",
            )
        )

    @command(
        name="urbandictionary",
        usage="(word)",
        example="Slatt",
        aliases=[
            "urban",
            "ud",
        ],
    )
    async def urbandictionary(self, ctx: Context, *, word: str) -> Message:
        """
        Gets the definition of a word/slang from Urban Dictionary
        """

        data = await self.bot.session.request(
            "GET",
            "https://api.urbandictionary.com/v0/define",
            params={
                "term": word,
            },
        )
        if not data.list:
            return await ctx.search(f"No results were found for **{word}**")

        return await ctx.paginate(
            [
                Embed(
                    url=item.permalink,
                    title=item.word,
                    description=item.definition,
                )
                .add_field(
                    name="Example",
                    value=item.example,
                    inline=False,
                )
                .add_field(
                    name="Votes",
                    value=f"👍 `{item.thumbs_up:,} / {item.thumbs_down:,}` 👎",
                    inline=False,
                )
                .set_footer(
                    icon_url="https://cdn.notsobot.com/brands/urban-dictionary.png",
                )
                for item in data.list
            ],
            of_text="Urban Dictionary Results",
        )

    @command(
        name="roleinfo",
        usage="<role>",
        example="Friends",
        aliases=[
            "rinfo",
            "ri",
        ],
    )
    async def roleinfo(self, ctx: Context, *, role: Role = None) -> Message:
        """
        View information about a role
        """

        role = role or ctx.author.top_role

        embed = Embed(
            color=role.color,
            title=role.name,
        )
        if isinstance(role.display_icon, discord.Asset):
            embed.set_thumbnail(url=role.display_icon)

        embed.add_field(
            name="Role ID",
            value=f"`{role.id}`",
            inline=True,
        )
        embed.add_field(
            name="Guild",
            value=f"{ctx.guild} (`{ctx.guild.id}`)",
            inline=True,
        )
        embed.add_field(
            name="Color",
            value=f"`{str(role.color).upper()}`",
            inline=True,
        )
        embed.add_field(
            name="Creation Date",
            value=(
                format_dt(role.created_at, style="f")
                + " **("
                + format_dt(role.created_at, style="R")
                + ")**"
            ),
            inline=False,
        )
        embed.add_field(
            name=f"{len(role.members):,} Member(s)",
            value=(
                "No members in this role"
                if not role.members
                else ", ".join([user.name for user in role.members][:7])
                + ("..." if len(role.members) > 7 else "")
            ),
            inline=False,
        )

        return await ctx.send(embed=embed)

    @command(
        name="channelinfo",
        usage="<channel>",
        example="#general",
        aliases=[
            "cinfo",
            "ci",
        ],
    )
    async def channelinfo(
        self,
        ctx: Context,
        *,
        channel: discord.TextChannel
        | discord.VoiceChannel
        | discord.CategoryChannel = None,
    ) -> Message:
        """
        View information about a channel
        """

        channel = channel or ctx.channel
        if not isinstance(
            channel,
            (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel),
        ):
            return await ctx.send_help()

        embed = Embed(title=channel.name)

        embed.add_field(
            name="Channel ID",
            value=f"`{channel.id}`",
            inline=True,
        )
        embed.add_field(
            name="Type",
            value=f"`{channel.type}`",
            inline=True,
        )
        embed.add_field(
            name="Guild",
            value=f"{ctx.guild} (`{ctx.guild.id}`)",
            inline=True,
        )

        if category := channel.category:
            embed.add_field(
                name="Category",
                value=f"{category} (`{category.id}`)",
                inline=False,
            )

        if isinstance(channel, discord.TextChannel) and channel.topic:
            embed.add_field(
                name="Topic",
                value=channel.topic,
                inline=False,
            )

        elif isinstance(channel, discord.VoiceChannel):
            embed.add_field(
                name="Bitrate",
                value=f"{int(channel.bitrate / 1000)} kbps",
                inline=False,
            )
            embed.add_field(
                name="User Limit",
                value=(channel.user_limit or "Unlimited"),
                inline=False,
            )

        elif isinstance(channel, discord.CategoryChannel) and channel.channels:
            embed.add_field(
                name=f"{len(channel.channels)} Children",
                value=", ".join([child.name for child in channel.channels]),
                inline=False,
            )

        embed.add_field(
            name="Creation Date",
            value=(
                format_dt(channel.created_at, style="f")
                + " **("
                + format_dt(channel.created_at, style="R")
                + ")**"
            ),
            inline=False,
        )

        return await ctx.send(embed=embed)

    @command(
        name="inviteinfo",
        usage="(invite)",
        example="bleed",
        aliases=[
            "ii",
        ],
    )
    async def inviteinfo(self, ctx: Context, invite: Invite) -> Message:
        """
        View basic invite code information
        """

        embed = Embed(title=f"Invite Code: {invite.code}")
        embed.set_thumbnail(url=invite.guild.icon)

        embed.add_field(
            name="Channel & Invite",
            value=(
                f"**Name:** {invite.channel.name} (`{invite.channel.type}`)\n"
                f"**ID:** `{invite.channel.id}`\n"
                "**Created:** "
                + format_dt(
                    invite.channel.created_at,
                    style="f",
                )
                + "\n"
                "**Invite Expiration:** "
                + (
                    format_dt(
                        invite.expires_at,
                        style="R",
                    )
                    if invite.expires_at
                    else "Never"
                )
                + "\n"
                "**Inviter:** Unknown\n"
                "**Temporary:** N/A\n"
                "**Usage:** N/A"
            ),
            inline=True,
        )
        embed.add_field(
            name="Guild",
            value=(
                f"**Name:** {invite.guild.name}\n"
                f"**ID:** `{invite.guild.id}`\n"
                "**Created:** "
                + format_dt(
                    invite.guild.created_at,
                    style="f",
                )
                + "\n"
                f"**Members:** {invite.approximate_member_count:,}\n"
                f"**Members Online:** {invite.approximate_presence_count:,}\n"
                f"**Verification Level:** {invite.guild.verification_level.name.title()}"
            ),
            inline=True,
        )

        view = View()
        for button in [
            Button(
                emoji=emoji,
                label=key,
                url=asset.url,
            )
            for emoji, key, asset in [
                ("🖼", "Icon", invite.guild.icon),
                ("🎨", "Splash", invite.guild.splash),
                ("🏳", "Banner", invite.guild.banner),
            ]
            if asset
        ]:
            view.add_item(button)

        return await ctx.send(embed=embed, view=view)

    @group(
        name="boosters",
        invoke_without_command=True,
    )
    async def boosters(self, ctx: Context) -> Message:
        """
        View all recent server boosters
        """

        if not (
            members := sorted(
                filter(
                    lambda member: member.premium_since,
                    ctx.guild.members,
                ),
                key=lambda member: member.premium_since,
                reverse=True,
            )
        ):
            return await ctx.warn("No **members** are currently boosting!")

        return await ctx.paginate(
            Embed(
                title="Current boosters",
                description=[
                    (
                        f"**{member}** boosted "
                        + format_dt(
                            member.premium_since,
                            style="R",
                        )
                    )
                    for member in members
                ],
            )
        )

    @boosters.command(
        name="lost",
    )
    async def boosters_lost(self, ctx: Context) -> Message:
        """
        View list of most recent lost boosters
        """

        if not (
            boosters_lost := await self.bot.db.fetch(
                """
            SELECT *
            FROM boosters_lost
            ORDER BY expired_at DESC
            """
            )
        ):
            return await ctx.warn("No **boosters** have been lost recently!")

        return await ctx.paginate(
            Embed(
                title="Recently lost boosters",
                description=[
                    (
                        f"**{user}** stopped "
                        + format_dt(
                            row["expired_at"],
                            style="R",
                        )
                        + " (lasted "
                        + human_timedelta(
                            row["started_at"], accuracy=1, brief=True, suffix=False
                        )
                        + ")"
                    )
                    for row in boosters_lost
                    if (user := self.bot.get_user(row["user_id"]))
                ],
            )
        )

    @command(
        name="invites",
    )
    @has_permissions(manage_guild=True)
    async def invites(self, ctx: Context) -> Message:
        """
        View all active invites
        """

        if not (
            invites := sorted(
                await ctx.guild.invites(),
                key=lambda invite: invite.expires_at,
                reverse=True,
            )
        ):
            return await ctx.warn("No **active invites** found")

        return await ctx.paginate(
            Embed(
                title="Server invites",
                description=[
                    (
                        f"[**{invite.code}**]({invite.url}) expires "
                        + format_dt(
                            invite.expires_at,
                            style="R",
                        )
                    )
                    for invite in invites
                ],
            )
        )

    @command(
        name="roles",
    )
    async def roles(self, ctx: Context) -> Message:
        """
        View all roles in the server
        """

        if not (roles := reversed(ctx.guild.roles[1:])):
            return await ctx.warn("No **roles** found")

        return await ctx.paginate(
            Embed(title="List of roles", description=[role.mention for role in roles])
        )

    @command(
        name="emotes",
        aliases=[
            "emojis",
        ],
    )
    async def emotes(self, ctx: Context) -> Message:
        """
        View all emotes in the server
        """

        if not ctx.guild.emojis:
            return await ctx.warn("No **emotes** found")

        return await ctx.paginate(
            Embed(
                title="List of emotes",
                description=[
                    f"{emote} [{emote.name}]({emote.url})" for emote in ctx.guild.emojis
                ],
            )
        )

    @command(
        name="bots",
    )
    async def bots(self, ctx: Context) -> Message:
        """
        View all bots in the server
        """

        if not (
            bots := filter(
                lambda member: member.bot,
                ctx.guild.members,
            )
        ):
            return await ctx.warn("No **bots** found")

        return await ctx.paginate(
            Embed(
                title="List of bots",
                description=[f"**{bot}**" for bot in bots],
            )
        )

    @command(
        name="members",
        usage="<role>",
        example="Friends",
        aliases=["inrole"],
    )
    async def members(self, ctx: Context, *, role: Role = None) -> Message:
        """
        View members in a role
        """

        role = role or ctx.author.top_role

        if not role.members:
            return await ctx.warn(f"No **members** have {role.mention}")

        return await ctx.paginate(
            Embed(
                title=f"Members in {role}",
                description=[
                    (
                        f"**{member}**"
                        + (" (you)" if member == ctx.author else "")
                        + (" (BOT)" if member.bot else "")
                    )
                    for member in role.members
                ],
            )
        )

    @command(
        name="avatar",
        usage="<user>",
        example="jonathan",
        aliases=[
            "av",
            "avi",
            "pfp",
            "ab",
            "ag",
        ],
        information={"note": "User ID available"},
    )
    async def avatar(self, ctx: Context, *, user: Member | User = None) -> Message:
        """
        Get avatar of a member or yourself
        """

        user = user or ctx.author

        return await ctx.send(
            embed=Embed(
                url=(user.avatar or user.default_avatar),
                title=f"{user.name}'s avatar",
            ).set_image(url=(user.avatar or user.default_avatar))
        )

    @command(
        name="serveravatar",
        usage="<member>",
        example="jonathan",
        aliases=[
            "sav",
            "savi",
            "spfp",
            "serverav",
            "gav",
            "guildav",
        ],
        information={"note": "User ID available"},
    )
    async def serveravatar(self, ctx: Context, *, member: Member = None) -> Message:
        """
        Get the server avatar of a member or yourself
        """

        member = member or ctx.author
        if not member.guild_avatar:
            return await ctx.warn(
                "You don't have a **server avatar** set!"
                if member == ctx.author
                else f"**{member}** doesn't have a **server avatar** set!"
            )

        return await ctx.send(
            embed=Embed(
                url=member.guild_avatar,
                title=f"{member.name}'s server avatar",
            ).set_image(url=member.guild_avatar)
        )

    @command(
        name="banner",
        usage="<user>",
        example="jonathan",
        aliases=[
            "ub",
            "userbanner",
        ],
        information={"note": "User ID available"},
    )
    async def banner(self, ctx: Context, *, user: Member | User = None) -> Message:
        """
        Get the banner of a member or yourself
        """

        if not isinstance(user, discord.User):
            user = await self.bot.fetch_user(user.id if user else ctx.author.id)

        banner_url = (
            user.banner
            if user.banner
            else (
                "https://singlecolorimage.com/get/"
                + str(user.accent_color or discord.Color(0)).replace("#", "")
                + "/400x100"
            )
        )

        return await ctx.send(
            embed=Embed(
                url=banner_url,
                title=f"{user.name}'s banner",
            ).set_image(url=banner_url)
        )

    @command(
        name="icon",
        usage="<guild>",
        example="1115389989..",
        aliases=[
            "servericon",
            "guildicon",
            "sicon",
            "gicon",
        ],
        information={"note": "Server ID & Invite available"},
    )
    async def icon(self, ctx: Context, *, guild: Guild | Invite = None) -> Message:
        """
        Returns guild icon
        """

        if isinstance(guild, Invite):
            guild = guild.guild
        else:
            guild = guild or ctx.guild

        if not guild.icon:
            return await ctx.warn("No **server icon** is set!")

        return await ctx.send(
            embed=Embed(
                url=guild.icon,
                title=f"{guild.name}'s icon",
            ).set_image(url=guild.icon)
        )

    @command(
        name="guildbanner",
        usage="<guild>",
        example="1115389989..",
        aliases=[
            "serverbanner",
            "gbanner",
            "sbanner",
        ],
        information={"note": "Server ID & Invite available"},
    )
    async def guildbanner(
        self, ctx: Context, *, guild: Guild | Invite = None
    ) -> Message:
        """
        Returns guild banner
        """

        if isinstance(guild, Invite):
            guild = guild.guild
        else:
            guild = guild or ctx.guild

        if not guild.banner:
            return await ctx.warn("No **server banner** is set!")

        return await ctx.send(
            embed=Embed(
                url=guild.banner,
                title=f"{guild.name}'s guild banner",
            ).set_image(url=guild.banner)
        )

    @command(
        name="splash",
        usage="<guild>",
        example="1115389989..",
        information={"note": "Server ID & Invite available"},
    )
    async def splash(self, ctx: Context, *, guild: Guild | Invite = None) -> Message:
        """
        Returns splash background
        """

        if isinstance(guild, Invite):
            guild = guild.guild
        else:
            guild = guild or ctx.guild

        if not guild.splash:
            return await ctx.warn("No **server splash** is set!")

        return await ctx.send(
            embed=Embed(
                url=guild.splash,
                title=f"{guild.name}'s guild splash",
            ).set_image(url=guild.splash)
        )

    @command(
        name="serverinfo",
        usage="<guild>",
        example="1115389989..",
        aliases=[
            "guildinfo",
            "sinfo",
            "ginfo",
            "si",
            "gi",
        ],
    )
    async def serverinfo(self, ctx: Context, *, guild: Guild = None) -> Message:
        """
        View information about a guild
        """

        guild = guild or ctx.guild

        embed = Embed(
            title=guild.name,
            description=(
                "Server created on "
                + (
                    format_dt(guild.created_at, style="D")
                    + " **("
                    + format_dt(guild.created_at, style="R")
                    + ")**"
                )
                + f"\n__{guild.name}__ is on bot shard ID: **{guild.shard_id}/{self.bot.shard_count}**"
            ),
            timestamp=guild.created_at,
        )
        embed.set_thumbnail(url=guild.icon)

        embed.add_field(
            name="Owner",
            value=(guild.owner or guild.owner_id),
            inline=True,
        )
        embed.add_field(
            name="Members",
            value=(
                f"**Total:** {guild.member_count:,}\n"
                f"**Humans:** {len([m for m in guild.members if not m.bot]):,}\n"
                f"**Bots:** {len([m for m in guild.members if m.bot]):,}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Information",
            value=(
                f"**Verification:** {guild.verification_level.name.title()}\n"
                f"**Level:** {guild.premium_tier}/{guild.premium_subscription_count:,} boosts"
            ),
            inline=True,
        )
        embed.add_field(
            name="Design",
            value=(
                f"**Banner:** "
                + (f"[Click here]({guild.banner})\n" if guild.banner else "N/A\n")
                + f"**Splash:** "
                + (f"[Click here]({guild.splash})\n" if guild.splash else "N/A\n")
                + f"**Icon:** "
                + (f"[Click here]({guild.icon})\n" if guild.icon else "N/A\n")
            ),
            inline=True,
        )
        embed.add_field(
            name=f"Channels ({len(guild.channels)})",
            value=f"**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}\n**Category:** {len(guild.categories)}\n",
            inline=True,
        )
        embed.add_field(
            name="Counts",
            value=(
                f"**Roles:** {len(guild.roles)}/250\n"
                f"**Emojis:** {len(guild.emojis)}/{guild.emoji_limit}\n"
                f"**Boosters:** {len(guild.premium_subscribers):,}\n"
            ),
            inline=True,
        )

        if guild.features:
            embed.add_field(
                name="Features",
                value=(
                    "```\n"
                    + ", ".join(
                        [
                            feature.replace("_", " ").title()
                            for feature in guild.features
                        ]
                    )
                    + "```"
                ),
                inline=False,
            )

        embed.set_footer(text=f"Guild ID: {guild.id}")

        return await ctx.send(embed=embed)

    @command(
        name="userinfo",
        usage="<user>",
        example="jonathan",
        aliases=[
            "whois",
            "uinfo",
            "info",
            "ui",
        ],
        information={"note": "User ID available"},
    )
    async def userinfo(self, ctx: Context, *, user: Member | User = None) -> Message:
        """
        View information about a member or yourself
        """

        user = user or ctx.author

        embed = Embed(
            color=(user.color if (user.color != discord.Color.default()) else None),
            description=" ".join(user.badges()),
        )
        embed.set_author(
            name=f"{user} ({user.id})",
            icon_url=user.display_avatar,
        )
        embed.set_thumbnail(url=user.display_avatar)
        footer = list()
        if user.bot:
            footer.append("Discord Bot")
        elif user.id in config.owner_ids:
            footer.append("bleed dev")
        elif user.id in config.admin_ids:
            footer.append("bleed admin")
        elif user.id in (469965172702969877, 186532514163064842):
            footer.append("bleed skid")
        elif user.id in (
            980198139669643304,
            1082063330191085588,
            542184217707151377,
            496867638350184458,
        ):
            footer.append("bleed glazer")

        embed.add_field(
            name="Dates",
            value=(
                f"**Created:** "
                + (
                    format_dt(user.created_at, style="f")
                    + " ("
                    + format_dt(user.created_at, style="R")
                    + ")"
                )
                + (
                    f"\n**Joined:** "
                    + format_dt(user.joined_at, style="f")
                    + " ("
                    + format_dt(user.joined_at, style="R")
                    + ")"
                    if isinstance(user, discord.Member)
                    else ""
                )
                + (
                    f"\n**Boosted:** "
                    + format_dt(user.premium_since, style="f")
                    + " ("
                    + format_dt(user.premium_since, style="R")
                    + ")"
                    if isinstance(user, discord.Member) and user.premium_since
                    else ""
                )
            ),
            inline=False,
        )
        if isinstance(user, discord.Member):
            if voice := user.voice:
                embed.description += (
                    f"\n**In voice chat:** {voice.channel.mention} "
                    + (
                        f"by themselves"
                        if len(voice.channel.members) == 1
                        else f"with {plural(len(voice.channel.members) - 1):other}"
                    )
                )

            embed.add_field(
                name=f"Roles ({len(user.roles) - 1})",
                value=(
                    "No **roles** in this server"
                    if not user.roles[1:]
                    else ", ".join(
                        reversed(
                            [
                                role.mention
                                for role in user.roles
                                if not role.is_default()
                            ][:7]
                        )
                    )
                    + ("..." if len(user.roles) > 7 else "")
                ),
                inline=False,
            )

            if (
                any(
                    [
                        user.guild_permissions.ban_members,
                        user.guild_permissions.kick_members,
                        user.guild_permissions.manage_channels,
                        user.guild_permissions.manage_roles,
                        user.guild_permissions.manage_emojis_and_stickers,
                        user.guild_permissions.manage_messages,
                        user.guild_permissions.mention_everyone,
                        user.guild_permissions.manage_nicknames,
                        user.guild_permissions.manage_webhooks,
                    ]
                )
                and not user.guild_permissions.administrator
            ):
                embed.add_field(
                    name="Key Permissions",
                    value=", ".join(
                        [
                            perm.replace("_", " ").title()
                            for perm, value in user.guild_permissions
                            if perm
                            in [
                                "ban_members",
                                "kick_members",
                                "manage_channels",
                                "manage_roles",
                                "manage_emojis_and_stickers",
                                "manage_messages",
                                "mention_everyone",
                                "manage_nicknames",
                                "manage_webhooks",
                            ]
                            and value
                        ]
                    ),
                    inline=False,
                )
            elif len(footer) == 1:
                pass
            elif user.guild_permissions.administrator:
                footer.append("Server Administrator")
            elif user.id == user.guild.owner_id:
                footer.append("Server Owner")

        if isinstance(user, discord.Member):
            footer.append(f"Join Position: {user.join_position:,}")
        if not user == self.bot.user:
            footer.append(f"{plural(len(user.mutual_guilds)):Shared Server}")

        if footer:
            embed.set_footer(text=" ∙ ".join(footer))

        message = await ctx.send(embed=embed)
        return message

    @command(
        name="weather",
        usage="(location)",
        example="Los Angeles",
    )
    async def weather(self, ctx: Context, *, city: str) -> Message:
        """
        Gets simple weather using openweathermap API
        """

        data = await self.bot.session.request(
            "GET",
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "appid": config.Authorization.openweathermap,
                "q": city,
            },
            raise_for={404: f"No location was found for: **{city}**"},
        )

        embed = Embed(
            url=f"https://openweathermap.org/city/{data.id}",
            title=f"{data.weather[0].description.title()} in {data.name}, {data.sys.country}",
        )
        embed.set_thumbnail(
            url=f"https://openweathermap.org/img/w/{data.weather[0].icon}.png"
        )

        embed.add_field(
            name="Temperature",
            value=f"{data.main.temp - 273.15:.2f} °C / {(data.main.temp - 273.15) * 9/5 + 32:.2f} °F",
            inline=True,
        )
        embed.add_field(name="Wind", value=f"{data.wind.speed} mph", inline=True)
        embed.add_field(
            name="Humidity",
            value=f"{data.main.humidity}%",
            inline=True,
        )
        embed.add_field(
            name="Sun Rise",
            value=f"<t:{data.sys.sunrise}:t>",
            inline=True,
        )
        embed.add_field(
            name="Sun Set",
            value=f"<t:{data.sys.sunset}:t>",
            inline=True,
        )
        embed.add_field(
            name="Visibility",
            value=f"{(data.visibility / 1000):.1f} km",
        )

        return await ctx.send(embed=embed)

    @command(
        name="steam",
        usage="(profile id)",
        example="76561197965761821",
    )
    async def steam(self, ctx: Context, profile: str) -> Message:
        """
        Get information about a Steam profile
        """

        data = await self.bot.session.request(
            "GET",
            f"https://playerdb.co/api/player/steam/{profile}",
            raise_for={400: f"Found no account with the ID: **{profile}**"},
        )

        embed = Embed(
            url=data.player.meta.profileurl,
            title=f"ID: {profile}",
        )
        embed.set_thumbnail(url=data.player.meta.avatarfull)

        embed.add_field(
            name="Profile State",
            value="Public" if data.player.meta.profilestate else "Private",
            inline=True,
        )
        embed.add_field(
            name="Current State",
            value="Online" if data.player.meta.personastate else "Offline",
            inline=True,
        )
        embed.add_field(
            name="SteamID64",
            value=data.player.meta.steam64id,
            inline=True,
        )
        embed.add_field(
            name="Profile/Real Name",
            value=f"{data.player.username} | {data.player.meta.realname if hasattr(data.player.meta, 'realname') else 'Unknown'}",
            inline=True,
        )
        embed.add_field(
            name="Registered",
            value=f"<t:{data.player.meta.timecreated}:f> (<t:{data.player.meta.timecreated}:R>)",
            inline=True,
        )
        embed.add_field(
            name="Last Online",
            value="Unknown",
            inline=True,
        )

        embed.set_footer(
            text="Information from Steam",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/1024px-Steam_icon_logo.svg.png",
        )

        return await ctx.send(embed=embed)

    @command(
        name="github",
        usage="(username)",
        example="iCrawl",
        aliases=["git", "gh"],
    )
    async def github(self, ctx: Context, username: str) -> Message:
        """
        Gets profile information on the given Github user
        """

        data = await self.bot.session.request(
            "GET",
            f"https://api.github.com/users/{username}",
            raise_for={404: f"**{username}** is an invalid **Github** account"},
        )

        embed = Embed(
            url=data.html_url,
            title=(f"{data.name} (@{data.login})" if data.name else data.login),
            timestamp=datetime.strptime(
                data.created_at,
                "%Y-%m-%dT%H:%M:%SZ",
            ),
        )
        embed.set_thumbnail(url=data.avatar_url)

        if information := (
            (data.bio or "")
            + (f"\n📧 {data.email}" if data.email else "")
            + (
                f"\n🏢 [{data.company}]({URL(f'https://google.com/search?q={data.company}')})"
                if data.company
                else ""
            )
            + (
                f"\n🌎 [{data.location}]({URL(f'https://maps.google.com/search?q={data.company}')})"
                if data.location
                else ""
            )
            + (
                f"\n{config.Emoji.twitter} [{data.twitter_username}](https://twitter.com/{data.twitter_username})"
                if data.twitter_username
                else ""
            )
        ):
            embed.add_field(
                name="Information",
                value=information,
                inline=False,
            )

        if data.public_repos:
            repos = await self.bot.session.request(
                "GET",
                data.repos_url,
            )

            embed.add_field(
                name=f"Repositories ({len(repos)})",
                value="\n".join(
                    [
                        f"[`⭐ {repo.stargazers_count:,},"
                        f" {datetime.strptime(repo.created_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%m/%d/%y')} {repo.name}`]({repo.html_url})"
                        for repo in sorted(
                            repos, key=lambda r: r.stargazers_count, reverse=True
                        )[:3]
                    ]
                ),
                inline=False,
            )

        embed.add_field(
            name="Following",
            value=f"{data.following:,}",
            inline=True,
        )
        embed.add_field(
            name="Followers",
            value=f"{data.followers:,}",
            inline=True,
        )
        embed.add_field(
            name="Public Repos",
            value=f"{data.public_repos:,}",
            inline=True,
        )

        embed.set_footer(
            text="Created on",
            icon_url="https://cdn.discordapp.com/emojis/843537056541442068.png",
        )

        return await ctx.send(embed=embed)

    @command(
        name="tiktok",
        usage="(username)",
        example="kyliejenner",
        aliases=["tt"],
    )
    async def tiktok(self, ctx: Context, username: str) -> Message:
        """
        Gets profile information on the given TikTok user
        """

        async with ctx.typing():
            data = await services.tiktok.profile(
                self.bot.session,
                username=username,
            )

        embed = Embed(
            url=data.url,
            title=(
                f"{data.display_name} (@{data.username})"
                if data.username != data.display_name
                else data.username
            ),
            description=data.description,
        )
        embed.set_thumbnail(url=data.avatar_url)

        embed.add_field(
            name="Likes",
            value=data.statistics.likes,
            inline=True,
        )
        embed.add_field(
            name="Followers",
            value=data.statistics.followers,
            inline=True,
        )
        embed.add_field(
            name="Following",
            value=data.statistics.following,
            inline=True,
        )

        embed.set_footer(
            text="TikTok",
            icon_url="https://seeklogo.com/images/T/tiktok-icon-logo-1CB398A1BD-seeklogo.com.png",
        )

        return await ctx.send(embed=embed)

    @command(
        name="roblox",
        usage="(username)",
        example="ProjectSupreme",
        aliases=["rblx"],
    )
    async def roblox(self, ctx: Context, username: str) -> Message:
        """
        Gets profile information on the given Roblox user
        """

        async with ctx.typing():
            data = await services.roblox.profile(
                self.bot.session,
                username=username,
            )

        embed = Embed(
            url=data.url,
            title=(
                f"{data.display_name} (@{data.username})"
                if data.username != data.display_name
                else data.username
            ),
            description=data.description,
        )
        embed.set_thumbnail(url=data.avatar_url)

        embed.add_field(
            name="Created",
            value=format_dt(
                data.created_at,
                style="D",
            ),
            inline=True,
        )
        embed.add_field(
            name="Last Online",
            value=(
                format_dt(
                    data.last_online,
                    style="R",
                )
                if data.last_online
                else "Unknown"
            ),
            inline=True,
        )
        embed.add_field(
            name="Presence",
            value=data.presence,
            inline=True,
        )
        embed.add_field(
            name="Following",
            value=f"{data.statistics.following:,}",
            inline=True,
        )
        embed.add_field(
            name="Followers",
            value=f"{data.statistics.followers:,}",
            inline=True,
        )
        embed.add_field(
            name=f"Badges ({len(data.badges)})",
            value=", ".join(data.badges),
            inline=True,
        )

        embed.set_footer(
            text=f"ID: {data.id}",
            icon_url="https://static.wikia.nocookie.net/ipod/images/5/59/Roblox.png/revision/latest",
        )

        return await ctx.send(embed=embed)

    @command(
        name="xbox",
        usage="(gamertag)",
        example="OmariCast",
        aliases=["xb", "xbl"],
    )
    async def xbox(self, ctx: Context, *, gamertag: str) -> Message:
        """
        Gets profile information on the given Xbox gamertag
        """

        data = await self.bot.session.request(
            "GET",
            f"https://playerdb.co/api/player/xbox/{gamertag}",
            raise_for={500: f"**{gamertag}** is an invalid **Xbox** gamertag"},
        )

        embed = Embed(
            url=URL(f"https://xboxgamertag.com/search/{gamertag}"),
            title=data.player.username,
        )
        embed.set_image(
            url=URL(
                f"https://avatar-ssl.xboxlive.com/avatar/{data.player.username}/avatar-body.png"
            )
        )

        embed.add_field(
            name="Tenure Level",
            value=f"{int(data.player.meta.tenureLevel):,}",
            inline=True,
        )
        embed.add_field(
            name="Gamerscore",
            value=f"{int(data.player.meta.gamerscore):,}",
            inline=True,
        )
        embed.add_field(
            name="Account Tier",
            value=data.player.meta.accountTier,
            inline=True,
        )

        embed.set_footer(
            text="Xbox",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1200px-Xbox_one_logo.svg.png",
        )

        return await ctx.send(embed=embed)

    @command(
        name="snapchat",
        usage="(username)",
        example="xaviersobased",
        aliases=["snap"],
    )
    async def snapchat(self, ctx: Context, username: str) -> Message:
        """
        Get bitmoji and QR scan code for user
        """

        data = await services.snapchat.profile(
            self.bot.session,
            username=username,
        )

        embed = Embed(
            url=data.url,
            title=(
                (
                    f"{data.display_name} (@{data.username})"
                    if data.username != data.display_name
                    else data.username
                )
                + " on Snapchat"
            ),
            description=data.description,
        )
        if not data.bitmoji:
            embed.set_thumbnail(url=data.snapcode)
        else:
            embed.set_image(url=data.bitmoji)

        embed.set_footer(
            text="Snapchat",
            icon_url="https://assets.stickpng.com/images/580b57fcd9996e24bc43c536.png",
        )

        return await ctx.send(embed=embed)

    @command(
        name="snapchatstory",
        usage="(username)",
        example="xaviersobased",
        aliases=["snapstory"],
    )
    async def snapchatstory(self, ctx: Context, username: str) -> Message:
        """
        Gets all current stories for the given Snapchat user
        """

        data = await services.snapchat.profile(
            self.bot.session,
            username=username,
        )

        if not data.stories:
            return await ctx.warn(
                f"No **story results** found for [`{username}`]({URL(f'https://snapchat.com/add/{username}')})"
            )

        await ctx.paginate(
            [
                f"**@{data.username}** — ({index + 1}/{len(data.stories)}){hidden(story.url)}"
                for index, story in enumerate(data.stories)
            ]
        )

    @command(
        name="createembed",
        usage="(embed code)",
        example="{title: hi}",
        aliases=["ce"],
    )
    @has_permissions(manage_messages=True)
    async def createembed(self, ctx: Context, *, script: TagScript) -> Message:
        """
        Create your own embed
        """

        message = await ctx.channel.send(**script.dump)
        await cache.set(f"embed:{message.id}", str(script), expire="1h")
        return message

    @command(
        name="editembed",
        usage="(message link) (embed code)",
        example=".../channels/... {title",
        aliases=[
            "edite",
            "ee",
        ],
    )
    @has_permissions(manage_messages=True)
    async def editembed(
        self, ctx: Context, message: Message, *, script: TagScript
    ) -> Message:
        """
        Edit an embed you created
        """

        if not (message.channel == ctx.channel) or not message.author == ctx.guild.me:
            return await ctx.send_help()

        return await message.edit(**script.dump)

    @command(
        name="embedcode",
        usage="(message link)",
        example=".../channels/...",
        aliases=[
            "copyembed",
            "ec",
        ],
    )
    async def embedcode(self, ctx: Context, message: Message) -> Message:
        """
        Copy an existing embeds code for creating an embed
        """

        if cached := await cache.get(f"embed:{message.id}"):
            return await ctx.approve(
                f"**Successfully copied the embed code**" f"```\n{cached}```"
            )

        result: List = []

        if content := message.content:
            result.append(f"{{message: {content}}}")

        if embeds := message.embeds:
            embed: Embed = embeds[0]

            if color := embed.color:
                result.append(f"{{color: {color}}}")

            if author := embed.author:
                _author: List = [
                    author.name,
                ]

                if icon_url := author.icon_url:
                    _author.append(icon_url)

                if external_url := author.url:
                    _author.append(external_url)

                result.append(f"{{author: {' && '.join(_author)}}}")

            if url := embed.url:
                result.append(f"{{url: {url}}}")

            if title := embed.title:
                result.append(f"{{title: {title}}}")

            if description := embed.description:
                result.append(f"{{description: {description}}}")

            if image := embed.image:
                result.append(f"{{image: {image.url}}}")

            if thumbnail := embed.thumbnail:
                result.append(f"{{thumbnail: {thumbnail.url}}}")

            for field in embed.fields:
                _field: List = [
                    field.name,
                    field.value,
                ]

                if inline := field.inline:
                    _field.append("inline")

                result.append(f"{{field: {' && '.join(_field)}}}")

            if footer := embed.footer:
                _footer: List = [
                    footer.text,
                ]

                if icon_url := footer.icon_url:
                    _footer.append(icon_url)

                result.append(f"{{footer: {' && '.join(_footer)}}}")

            if timestamp := embed.timestamp:
                result.append(
                    f"{{timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}}}"
                )

        return await ctx.approve(
            f"**Successfully copied the embed code**" f"```\n{'$v'.join(result)}```"
        )
