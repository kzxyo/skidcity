from discord import (
    Colour,
    Message,
    Embed,
    User,
    Member,
    PartialInviteGuild,
    Invite,
    File,
    Role,
    ButtonStyle,
    Permissions,
)
from discord.ext.commands import Cog, command, group, parameter
from discord.utils import format_dt, utcnow, oauth_url
from discord.ui import Button, View

from typing import List, Optional
from io import BytesIO

from humanize import ordinal

import config
from tools import Blair
from tools.converters.text import plural
from tools.discord import Context


class Information(Cog):
    def __init__(self, bot: Blair) -> None:
        self.bot: Blair = bot

        """
        This is only here and not in the configuration file so the
        details can be updated without requiring a full reload of the bot.
        """

        self.version = 2.2
        self.changelog = "\n".join(
            [
                "This is a temporary Blair instance, do not add it to your server.",
            ]
        )

        self.donators = {
            1083131355984044082: "<a:black_dance:1284272942246789142> <a:aw_dance:1281686087072354358> <:Verified:1280521718170914826> <:1798earlyverifiedbotdeveloper:1253147578045038604>",
            1030552136494366852: "<a:aw_dance:1281686087072354358>",
        }

    @command(name="about", aliases=["abt", "blair", "botinfo", "bi"])
    async def about(self: "Information", ctx: Context) -> Message:
        """
        View the bot statistics aswell as generic information.
        """

        embed = Embed(
            description=(
                "\n".join(
                    [
                        f"{self.bot.user.name.capitalize()} is a utility bot built with efficiency in mind.",
                        f"Currently providing `{self.bot.command_count - 44 }` commands for `{len(self.bot.users):,}` users!",
                        f"Developed and maintained by [**`saint`**](https://discord.com/users/{self.bot.owner_ids[0]}) & [**`adrian`**](https://discord.com/users/{self.bot.owner_ids[2]})",
                    ]
                )
            )
        )

        embed.add_field(
            name="Information",
            value=(
                "\n".join(
                    [
                        f">>> **Servers:** `{len(self.bot.guilds):,}`",
                        f"**Latency:** `{round(self.bot.latency * 1000)}ms`",
                        f"**Started:** {format_dt(self.bot.uptime, 'R')}",
                    ]
                )
            ),
            inline=False,
        )

        embed.add_field(
            name=f"Changelog (v{self.version})",
            value=(f">>> {self.changelog}"),
            inline=False,
        )

        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar,
        )

        invite = Button(
            label="Invite Me",
            style=ButtonStyle.url,
            url=oauth_url(self.bot.user.id, permissions=Permissions.all()),
        )

        support = Button(
            label="Support Server",
            style=ButtonStyle.url,
            url=config.SUPPORT,
        )

        view = View()
        view.add_item(invite)
        view.add_item(support)

        return await ctx.send(embed=embed, view=view)

    @command(name="avatar", aliases=["av", "avi", "pfp"])
    async def avatar(
        self,
        ctx: Context,
        *,
        user: User | Member = parameter(default=lambda ctx: ctx.author),
    ) -> Message:
        """
        Display a user's avatar.
        """

        embed = Embed(
            title=("Your avatar" if user == ctx.author else f"{user.name}'s avatar"),
            url=user.avatar or user.default_avatar,
        )

        embed.set_image(url=user.avatar or user.default_avatar)

        return await ctx.send(embed=embed)

    @command(name="banner", aliases=["userbanner", "ubanner", "ub"])
    async def banner(
        self,
        ctx: Context,
        *,
        user: User | Member = parameter(default=lambda ctx: ctx.author),
    ) -> Message:
        """
        Display a user's banner if one exists.
        """

        user = await self.bot.fetch_user(user.id)
        if not user.banner:
            return await ctx.respond(
                "`You` don't have a banner set!"
                if user == ctx.author
                else f"`{user.name}` doesn't have a banner set!"
            )

        embed = Embed(
            title=("Your banner" if user == ctx.author else f"{user.name}'s banner"),
            url=user.banner,
        )

        embed.set_image(url=user.banner)

        return await ctx.send(embed=embed)

    @command(name="ping", aliases=["beep", "latency", "ms"])
    async def ping(self: "Information", ctx: Context) -> Message:
        """
        Display the bot's latency.
        """

        return await ctx.send(f"... `{round(self.bot.latency * 1000)}ms`")

    @command(name="inviteinfo", aliases=["ii", "invinfo"])
    async def inviteinfo(
        self: "Information", ctx: Context, *, invite: Invite
    ) -> Message:
        """
        Display information on the provided invite.
        """

        if not isinstance(invite.guild, PartialInviteGuild):
            return await ctx.respond(
                "Improper invite provided, please ensure the invitation is **valid** and try again!"
            )

        guild = invite.guild
        embed = Embed(
            description=(
                f"{guild.description if guild.description else ""}"
                + (
                    f"\n\n> Click [**here**]({guild.icon.url}) to download the guild icon!"
                    if guild.icon
                    else ""
                )
            )
        )

        embed.set_author(name=guild.name, icon_url=guild.icon, url=invite.url)

        if guild.banner:
            embed.set_image(url=guild.banner)

        embed.add_field(
            name="Details",
            value=(
                "\n".join(
                    [
                        f">>> **Inviter:** `{invite.inviter or 'Vanity URL'}`",
                        f"**Channel:** `#{invite.channel or 'N/A'}`",
                        f"**Created:** {format_dt(guild.created_at)} / {format_dt(guild.created_at, 'R')}",
                    ]
                )
            ),
            inline=False,
        )

        embed.add_field(
            name="Statistics",
            value=(
                "\n".join(
                    [
                        f">>> **Members:** `{invite.approximate_member_count:,}`",
                        f"**Active Members:** `{invite.approximate_presence_count:,}`",
                        f"**Verification Level:** `{guild.verification_level.name.title()}`",
                    ]
                )
            ),
            inline=False,
        )

        return await ctx.send(embed=embed)

    @command(name="serverbanner", aliases=["sbanner", "sb"])
    async def serverbanner(
        self: "Information", ctx: Context
    ) -> Message:
        """
        Display the server's banner if one exists.
        """

        guild = ctx.guild

        if not guild.banner:
            return await ctx.respond(f"`{guild.name}` doesn't have a banner set!")

        embed = Embed()
        embed.set_author(
            name=guild.name,
            icon_url=guild.icon.url if guild.icon else None,
            url=ctx.guild.banner.url,
        )

        embed.set_image(url=guild.banner)

        return await ctx.send(embed=embed)

    @command(
        name="serveravatar",
        aliases=[
            "spfp",
            "savi",
            "sav",
        ],
    )
    async def serveravatar(
        self,
        ctx: Context,
        *,
        member: Member = parameter(
            default=lambda ctx: ctx.author,
        ),
    ) -> Message:
        """
        Display a user's server avatar.
        """

        member = member or ctx.author
        if not member.guild_avatar:
            return await ctx.respond(
                "`You` don't have a server avatar set!"
                if member == ctx.author
                else f"`{member.name}` doesn't have a server avatar set!"
            )

        embed = Embed(
            url=member.guild_avatar,
            title=(
                "Your server avatar"
                if member == ctx.author
                else f"{member.name}'s server avatar"
            ),
        )
        embed.set_image(url=member.guild_avatar)

        return await ctx.send(embed=embed)

    @command(name="serverinfo", aliases=["sinfo", "si"])
    async def serverinfo(self: "Information", ctx: Context) -> Message:
        """
        Display information on the server.
        """

        guild = ctx.guild

        embed = Embed(
            description=f"{format_dt(guild.created_at)} / {format_dt(guild.created_at, 'R')}"
        )
        embed.set_author(name=guild.name, icon_url=guild.icon)

        embed.add_field(
            name="Details",
            value=(
                "\n".join(
                    [
                        f">>> **Owner:** `{guild.owner or guild.owner_id}`",
                        f"**Verification:** `{guild.verification_level.name.title()}`",
                        f"**Boosts:** `{guild.premium_subscription_count}` / Level `{guild.premium_tier}`",
                    ]
                )
            ),
            inline=False,
        )

        embed.add_field(
            name="Statistics",
            value=(
                "\n".join(
                    [
                        f">>> **Members:** `{guild.member_count:,}`",
                        f"**Text Channels:** `{len(guild.text_channels)}`",
                        f"**Voice Channels:** `{len(guild.voice_channels)}`",
                    ]
                )
            ),
            inline=False,
        )

        embed.set_thumbnail(url=guild.icon)
        if guild.banner:
            embed.set_image(url=guild.banner)

        return await ctx.send(embed=embed)

    @command(name="roles", aliases=["rs"])
    async def roles(self: "Information", ctx: Context) -> Message:
        """
        Displays all the roles in the server.
        """

        if not (roles := reversed(ctx.guild.roles[1:])):
            return await ctx.respond(f"`{ctx.guild.name}` doesn't have any roles!")

        return await ctx.paginate(
            [f"{role.mention}" for role in roles],
            Embed(title=f"{ctx.guild.name}'s roles"),
        )

    @command(name="boosters", aliases=["supporters", "boosts"])
    async def boosters(self: "Information", ctx: Context) -> Message:
        """
        Display all the current server boosters, if any.
        """

        if not (
            boosters := [member for member in ctx.guild.members if member.premium_since]
        ):
            return await ctx.respond(f"`{ctx.guild.name}` doesn't have any boosters!")

        return (
            await ctx.paginate(
                [
                    f"{member.mention} / {format_dt(member.premium_since, 'R')}"
                    for member in boosters
                ],
                Embed(title=f"{ctx.guild.name}'s boosters"),
            ),
        )

    @command(name="bots", aliases=["robots", "apps"])
    async def bots(self: "Information", ctx: Context) -> Message:
        """
        Displays all the bots in the server.
        """

        if not (
            bots := filter(
                lambda member: member.bot,
                ctx.guild.members,
            )
        ):
            return await ctx.respond(f"`{ctx.guild.name}` doesn't have any bots!")

        return await ctx.paginate(
            [f"{bot.mention}" for bot in bots], Embed(title=f"{ctx.guild.name}'s bots")
        )

    @command(name="emojis", aliases=["emotes", "es"])
    async def emojis(self: "Information", ctx: Context) -> Message:
        """
        Displays all the emojis in the server.
        """

        if not ctx.guild.emojis:
            return await ctx.respond(f"`{ctx.guild.name}` doesn't have any emojis!")

        return await ctx.paginate(
            [f"{emoji} [*`{emoji.name}`*]({emoji.url})" for emoji in ctx.guild.emojis],
            Embed(title=f"{ctx.guild.name}'s emojis"),
        )

    @command(name="stickers", aliases=["sticks"])
    async def stickers(self: "Information", ctx: Context) -> Message:
        """
        Displays all the stickers in the server.
        """

        if not ctx.guild.stickers:
            return await ctx.respond(f"`{ctx.guild.name}` doesn't have any stickers!")

        return await ctx.paginate(
            [f"[*`{sticker.name}`*]({sticker.url})" for sticker in ctx.guild.stickers],
            Embed(title=f"{ctx.guild.name}'s stickers"),
        )

    @command(name="invites", aliases=["invs", "invitations"])
    async def invites(self: "Information", ctx: Context) -> Message:
        """
        Displays the invites for the server.
        """

        if not (
            invites := sorted(
                [invite for invite in await ctx.guild.invites() if invite.expires_at],
                key=lambda invite: invite.expires_at,
                reverse=True,
            )
        ):
            return await ctx.respond(
                f"`{ctx.guild.name}` doesn't have any active invites!"
            )

        return await ctx.paginate(
            [
                f"[*`{invite.code}`*]({invite.url}) / expires {format_dt(invite.expires_at, 'R')}"
                for invite in invites
            ],
            Embed(title=f"{ctx.guild.name}'s invites"),
        )

    @group(name="fortnite", aliases=["fn", "fnbr"], invoke_without_command=True)
    async def fortnite(self: "Information", ctx: Context) -> Message:
        """
        Various Fortnite related commands.
        """

        return await ctx.send_help(ctx.command)

    @fortnite.command(name="shop", aliases=["itemshop", "is", "s"])
    async def fortnite_shop(self: "Information", ctx: Context) -> Message:
        """
        Displays the current Fortnite shop.
        """

        buffer = await self.bot.session.request(
            f"https://bot.fnbr.co/shop-image/fnbr-shop-{utcnow().strftime('%-d-%-m-%Y')}.png"
        )

        return await ctx.send(file=File(BytesIO(buffer), filename="itemshop.png"))

    @command(name="withrole", aliases=["hasrole", "inrole"])
    async def withrole(
        self: "Information", ctx: Context, *, role: Optional[Role]
    ) -> Message:
        """
        Display all the members with the provided role.
        If no role is provided, the command will default to your `highest` role.
        """

        role = role or ctx.author.top_role

        if not role.members:
            return await ctx.respond(f"{role.mention} doesn't contain any members!")

        return await ctx.paginate(
            [f"{user.mention}" for user in role.members],
            Embed(title=f"Members with {role.name}"),
        )

    @command(name="bans", aliases=["listbans", "allbans", "sbans"])
    async def bans(self: "Information", ctx: Context) -> Message:
        """
        Displays all the users banned from the server.
        """

        bans = [entry async for entry in ctx.guild.bans()]

        if not bans:
            return await ctx.respond(
                f"`{ctx.guild.name}` doesn't have any banned users!"
            )

        return await ctx.paginate(
            [
                f"**{entry.user}** / `{entry.user.id}` - {entry.reason or "No reason."}"
                for entry in bans
            ],
            Embed(title=f"{ctx.guild.name}'s ban list ({len(bans)})"),
        )

    @command(name="invite", aliases=["inv", "support"])
    async def invite(self: "Information", ctx: Context) -> Message:
        """
        Generate an invite for the bot, along with the URL to the support server.
        """

        invite = Button(
            label="Invite Me",
            style=ButtonStyle.url,
            url=oauth_url(self.bot.user.id, permissions=Permissions.all()),
        )

        support = Button(
            label="Support Server",
            style=ButtonStyle.url,
            url=config.SUPPORT,
        )

        view = View()
        view.add_item(invite)
        view.add_item(support)

        return await ctx.send(view=view)

    @command(name="userinfo", aliases=["uinfo", "ui", "whois"])
    async def userinfo(
        self,
        ctx: Context,
        *,
        user: Member | User = parameter(
            default=lambda ctx: ctx.author,
        ),
    ) -> Message:
        """
        View information about a user.
        """

        emojis = self.donators.get(user.id, "")

        embed = Embed(color=user.color if user.color != Colour.default() else Colour.dark_embed())
        embed.title = f"{user} {emojis} {'[BOT]' if user.bot else ''}"
        embed.description = ""
        embed.set_thumbnail(url=user.display_avatar)

        embed.add_field(
            name="**Created**",
            value=(
                format_dt(user.created_at, "D")
                + "\n> "
                + format_dt(user.created_at, "R")
            ),
        )

        if isinstance(user, Member) and user.joined_at:
            join_pos = sorted(
                user.guild.members,
                key=lambda member: member.joined_at or utcnow(),
            ).index(user)

            embed.add_field(
                name=f"**Joined ({ordinal(join_pos + 1)})**",
                value=(
                    format_dt(user.joined_at, "D")
                    + "\n> "
                    + format_dt(user.joined_at, "R")
                ),
            )

            if user.premium_since:
                embed.add_field(
                    name="**Boosted**",
                    value=(
                        format_dt(user.premium_since, "D")
                        + "\n> "
                        + format_dt(user.premium_since, "R")
                    ),
                )

            if roles := user.roles[1:]:
                embed.add_field(
                    name="**Roles**",
                    value=", ".join(role.mention for role in list(reversed(roles))[:5])
                    + (f" (+{len(roles) - 5})" if len(roles) > 5 else ""),
                    inline=False,
                )

            if (voice := user.voice) and voice.channel:
                members = len(voice.channel.members) - 1
                phrase = "Streaming inside" if voice.self_stream else "Inside"
                embed.description += f"🎙 {phrase} {voice.channel.mention} " + (
                    f"with {plural(members):other}" if members else "by themselves"
                )

        if ctx.author.id in self.bot.owner_ids:
            guilds: List[str] = []
            for guild in user.mutual_guilds:
                member = guild.get_member(user.id)
                if not member:
                    continue

                owner = "👑 " if member.id == guild.owner_id else ""
                display_name = (
                    f"`{member.display_name}` in "
                    if member.display_name != member.name
                    else ""
                )
                guilds.append(f"{owner}{display_name}**{guild}** (`{guild.id}`)")

            if guilds:
                embed.add_field(
                    name="**Shared Servers**",
                    value="\n".join(guilds[:15]),
                    inline=False,
                )

        return await ctx.send(embed=embed)