import asyncio

from collections import Counter, defaultdict
from datetime import time

import discord
import psutil
import pytz

from discord.ext import commands, tasks

from helpers import functions, humanize, wock


class information(commands.Cog, name="Information"):
    def __init__(self, bot):
        self.bot: wock.wockSuper = bot
        self.buckets: dict = dict(
            # default dict which has a counter object for members & messages
            metrics=dict(lock=asyncio.Lock(), data=defaultdict(lambda: Counter())),
        )
        self.metrics_insert.start()
        self.metrics_reset.start()

    def cog_unload(self):
        self.metrics_insert.stop()
        self.metrics_reset.stop()

    @tasks.loop(seconds=60)
    async def metrics_insert(self):
        """Bulk insert new metrics in the bucket into the database"""

        bucket = self.buckets.get("metrics")
        async with bucket["lock"]:
            transformed = [
                dict(
                    guild_id=int(guild_id),
                    members=int(counter.get("members", 0)),
                    messages=int(counter.get("messages", 0)),
                )
                for guild_id, counter in bucket["data"].items()
            ]
            bucket["data"].clear()

            await self.bot.db.execute(
                "INSERT INTO metrics.guilds (guild_id, members, messages) SELECT x.guild_id, x.members, x.messages FROM jsonb_to_recordset($1::JSONB)"
                " as x(guild_id BIGINT, members BIGINT, messages BIGINT) ON CONFLICT (guild_id) DO UPDATE SET members = metrics.guilds.members +"
                " EXCLUDED.members, messages = metrics.guilds.messages + EXCLUDED.messages",
                transformed,
            )

    @metrics_insert.before_loop
    async def metrics_insert_before(self):
        await self.bot.wait_until_ready()

    # reset at 12am est
    @tasks.loop(time=time(0, 0, 0, tzinfo=pytz.timezone("US/Eastern")))
    async def metrics_reset(self):
        """Reset the metrics database at 12am UTC"""

        bucket = self.buckets.get("metrics")
        async with bucket["lock"]:
            await self.bot.db.execute("DELETE FROM metrics.guilds")

    @metrics_reset.before_loop
    async def metrics_reset_before(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_member_join")
    async def metrics_member_add(self, member: discord.Member):
        """Increase the members metric"""

        bucket = self.buckets.get("metrics")
        async with bucket["lock"]:
            bucket["data"][member.guild.id]["members"] += 1

    @commands.Cog.listener("on_member_remove")
    async def metrics_member_remove(self, member: discord.Member):
        """Decrease the members metric"""

        bucket = self.buckets.get("metrics")
        async with bucket["lock"]:
            bucket["data"][member.guild.id]["members"] -= 1

    @commands.Cog.listener("on_user_message")
    async def metrics_message_add(self, ctx: wock.Context, message: discord.Message):
        """Increase the messages metric"""

        bucket = self.buckets.get("metrics")
        async with bucket["lock"]:
            bucket["data"][message.guild.id]["messages"] += 1

    @commands.Cog.listener("on_member_unboost")
    async def on_member_unboost(self, member: discord.Member):
        """Track whenver someone unboosts a server"""

        await self.bot.db.execute(
            "INSERT INTO boosters_lost (guild_id, user_id, lasted, expired) VALUES($1, $2, $3, $4) ON CONFLICT (guild_id, user_id) DO UPDATE SET"
            " lasted = $3, expired = $4",
            member.guild.id,
            member.id,
            member.premium_since,
            discord.utils.utcnow(),
        )

    @commands.Cog.listener("on_member_boost")
    async def on_member_boost(self, member: discord.Member):
        """Remove a member from the boosters_lost schema"""

        await self.bot.db.execute(
            "DELETE FROM boosters_lost WHERE guild_id = $1 AND user_id = $2",
            member.guild.id,
            member.id,
        )

    @commands.command(
        name="help",
        usage="<command or module>",
        example="userinfo",
        aliases=["h"],
    )
    async def _help(self, ctx: wock.Context, *, command: str = None):
        """View information about a command"""

        if command is None:
            await ctx.neutral(
                f"Click [**here**](https://{self.bot.config['domain']}/commands) to view **{len(set(self.bot.walk_commands()))}** commands"
            )
            # embeds = list()

            # embed = discord.Embed(description=f"```ini\n[ {len(set(self.bot.walk_commands()))} commands ]\n```\n")
            # for category in sorted(
            #     self.bot.cogs,
            #     key=lambda c: len(c),
            # ):
            #     if category.lower() in ("jishaku", "developer", "sentry"):
            #         continue
            #     embed.description += f"> [`{category}`](https://wock.cloud)\n"

            # embed.set_thumbnail(url=self.bot.user.display_avatar)
            # embeds.append(embed)

            # for name, category in sorted(self.bot.cogs.items(), key=lambda c: len(c[0])):
            #     if name.lower() in ("jishaku", "developer", "sentry"):
            #         continue
            #     embed = discord.Embed(description=f"```ini\n[ {category.qualified_name} ]\n[ {len(set(category.walk_commands()))} commands ]\n```\n")
            #     for command in category.walk_commands():
            #         if command.hidden:
            #             continue
            #         embed.description += f"> [`{command.qualified_name}`](https://wock.cloud)\n"

            #     embed.set_thumbnail(url=self.bot.user.display_avatar)
            #     embeds.append(embed)

            # await ctx.paginate(embeds)
        else:
            _command = command
            command: commands.Command = self.bot.get_command(_command)
            if command is None:
                return await ctx.warn(f"Command `{_command}` doesn't exist")

            embed = discord.Embed(
                description=command.short_doc or "No description provided",
            )
            embed.description += (
                f"\n>>> ```bf\nSyntax: {ctx.prefix}{command.qualified_name} {command.usage or ''}\n"
                + (f"Example: {ctx.prefix}{command.qualified_name} {command.example}" if command.example else "")
                + "```"
            )
            embed.set_author(name=command.cog_name or "No category", icon_url=self.bot.user.display_avatar, url=f"https://docs.wock.cloud")

            embed.add_field(
                name="Aliases",
                value=", ".join([f"`{alias}`" for alias in command.aliases]) or "`N/A`",
                inline=(False if len(command.aliases) >= 4 else True),
            )
            embed.add_field(
                name="Parameters",
                value=", ".join([f"`{param}`" for param in command.clean_params]) or "`N/A`",
                inline=True,
            )
            embed.add_field(
                name="Permissions",
                value=", ".join(list(map(lambda p: "`" + p.replace("_", " ").title() + "`", await command.permissions()))) or "`N/A`",
                inline=True,
            )
            if command.parameters:
                embed.add_field(
                    name="Optional Parameters",
                    value="\n".join(
                        [
                            "`"
                            + ("--" if parameter.get("require_value", True) else "-")
                            + f"{parameter_name}` "
                            + (
                                (
                                    ("(" if not parameter.get("default") else "[")
                                    + " | ".join([f"`{choice}`" for choice in parameter.get("choices", [])])
                                    + (")" if not parameter.get("default") else "]")
                                )
                                if parameter.get("choices")
                                else (("`" + str(parameter["converter"]).split("'", 1)[1].split("'")[0] + "`" if parameter.get("converter") else ""))
                                if parameter.get("converter")
                                and not getattr(parameter.get("converter"), "__name__", "")
                                in ("int", "EmbedScriptValidator", "DiscriminatorValidator")
                                else (
                                    f"(`{parameter.get('minimum', 1)}`-`{parameter.get('maximum', 100)}`)"
                                    if getattr(parameter.get("converter"), "__name__", "") == "int"
                                    else ""
                                )
                            )
                            + f"\n> {parameter['description']}"
                            for parameter_name, parameter in command.parameters.items()
                        ]
                    ),
                    inline=False,
                )
            if isinstance(command, commands.Group):
                embed.add_field(
                    name="Subcommands",
                    value="\n".join(
                        [
                            f"> `{command.qualified_name}` - {functions.shorten(command.short_doc, 35)}"
                            for command in sorted(
                                command.walk_commands(),
                                key=lambda c: c.qualified_name.lower(),
                            )
                            if not command.hidden
                        ]
                    ),
                    inline=False,
                )
            await ctx.paginate(embed, max_entries=15, footer_override=isinstance(command, commands.Group))

    @commands.command(name="ping", aliases=["latency"])
    async def ping(self, ctx: wock.Context):
        """View the gateway latency"""

        await ctx.neutral(f"Gateway: `{(self.bot.latency * 1000):.2f}ms`")

    @commands.command(name="about", aliases=["botinfo", "system", "sys"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def about(self, ctx: wock.Context):
        """View system information about wock"""

        process = psutil.Process()

        embed = discord.Embed(
            description=(
                f"Developed by **rx#1337**" + f"\n**Memory:** {humanize.size(process.memory_full_info().uss)}, **CPU:** {psutil.cpu_percent()}%"
            )
        )
        embed.set_author(
            name=self.bot.user.display_name,
            icon_url=self.bot.user.display_avatar,
        )

        embed.add_field(
            name="Members",
            value=(
                f"**Total:** {humanize.comma(len(self.bot.users))}"
                + f"\n**Unique:** {humanize.comma(len(list(filter(lambda m: not m.bot, self.bot.users))))}"
                # + f"\n**Online:** {humanize.comma(len(list(filter(lambda m: not isinstance(m, discord.ClientUser) and m.status is not discord.Status.offline, self.bot.members))))}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Channels",
            value=(
                f"**Total:** {humanize.comma(len(self.bot.channels))}"
                + f"\n**Text:** {humanize.comma(len(self.bot.text_channels))}"
                + f"\n**Voice:** {humanize.comma(len(self.bot.voice_channels))}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Client",
            value=(f"**Servers:** {humanize.comma(len(self.bot.guilds))}" + f"\n**Commands:** {humanize.comma(len(set(self.bot.walk_commands())))}"),
            inline=True,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="membercount",
        usage="<server>",
        example="/wock",
        aliases=["members", "mc"],
    )
    async def membercount(
        self,
        ctx: wock.Context,
        *,
        server: discord.Guild | discord.Invite = None,
    ):
        """View a server's member count"""

        if isinstance(server, discord.Invite):
            invite = server
            server = server.guild

        server = server or ctx.guild

        embed = discord.Embed()
        embed.set_author(
            name=server,
            icon_url=server.icon,
        )

        embed.add_field(
            name="Members",
            value=(humanize.comma(len(server.members)) if isinstance(server, discord.Guild) else humanize.comma(invite.approximate_member_count)),
            inline=True,
        )
        if isinstance(server, discord.Guild):
            embed.add_field(
                name="Humans",
                value=humanize.comma(len(list(filter(lambda m: not m.bot, server.members)))),
                inline=True,
            )
            embed.add_field(
                name="Bots",
                value=humanize.comma(len(list(filter(lambda m: m.bot, server.members)))),
                inline=True,
            )

            metrics = await self.bot.db.fetchrow("SELECT * FROM metrics.guilds WHERE guild_id = $1", server.id)
            if metrics:
                members = metrics["members"]
                messages = metrics["messages"]
                embed.set_footer(
                    text=(
                        f"{'+' if members >= 0 else ''}{functions.plural(members):member},"
                        f" {'+' if messages >= 0 else ''}{functions.plural(messages):message}"
                    )
                )

        else:
            embed.add_field(
                name="Online",
                value=humanize.comma(invite.approximate_presence_count),
                inline=True,
            )

        await ctx.send(embed=embed)

    @commands.command(
        name="icon",
        usage="<server>",
        example="/wock",
        aliases=["servericon", "sicon", "guildicon", "gicon"],
    )
    async def icon(
        self,
        ctx: wock.Context,
        *,
        server: discord.Guild | discord.Invite = None,
    ):
        """View a server's icon"""

        if isinstance(server, discord.Invite):
            server = server.guild

        server = server or ctx.guild

        if not server.icon:
            return await ctx.warn(f"**{server}** doesn't have an **icon**")

        embed = discord.Embed(url=server.icon, title=f"{server}'s icon")
        embed.set_image(url=server.icon)
        await ctx.send(embed=embed)

    @commands.command(
        name="serverbanner",
        usage="<server>",
        example="/wock",
        aliases=["sbanner", "guildbanner", "gbanner"],
    )
    async def serverbanner(
        self,
        ctx: wock.Context,
        *,
        server: discord.Guild | discord.Invite = None,
    ):
        """View a server's banner"""

        if isinstance(server, discord.Invite):
            server = server.guild

        server = server or ctx.guild

        if not server.banner:
            return await ctx.warn(f"**{server}** doesn't have a **banner**")

        embed = discord.Embed(url=server.banner, title=f"{server}'s banner")
        embed.set_image(url=server.banner)
        await ctx.send(embed=embed)

    @commands.command(
        name="serverinfo",
        usage="<server>",
        example="/wock",
        aliases=["sinfo", "guildinfo", "ginfo", "si", "gi"],
    )
    async def serverinfo(
        self,
        ctx: wock.Context,
        *,
        server: discord.Guild | discord.Invite = None,
    ):
        """View information about a server"""

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
                value=">>> " + ", ".join([role.mention for role in roles[:7]]) + (f" (+{humanize.comma(len(roles) - 7)})" if len(roles) > 7 else ""),
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(
        name="inviteinfo",
        usage="<server>",
        example="/wock",
        aliases=["iinfo", "ii"],
    )
    async def inviteinfo(
        self,
        ctx: wock.Context,
        *,
        server: discord.Invite | discord.Guild,
    ):
        """View information about an invite"""

        if isinstance(server, discord.Guild):
            return await self.bot.get_command("serverinfo")(ctx, server=server)
        else:
            if self.bot.get_guild(server.guild.id):
                return await self.bot.get_command("serverinfo")(ctx, server=server.guild)

        invite = server
        server = invite.guild

        embed = discord.Embed(
            description=(discord.utils.format_dt(server.created_at, "f") + " (" + discord.utils.format_dt(server.created_at, "R") + ")")
        )
        embed.set_author(
            name=f"{server} ({server.id})",
            icon_url=server.icon,
        )
        embed.set_image(url=server.banner.with_size(1024).url if server.banner else None)

        embed.add_field(
            name="Invite",
            value=(f">>> **Channel:** {('#' + invite.channel.name) if invite.channel else 'N/A'}" + f"\n**Inviter:** {invite.inviter or 'N/A'}"),
            inline=True,
        )
        embed.add_field(
            name="Server",
            value=(f">>> **Members:** {invite.approximate_member_count:,}" + f"\n**Members Online:** {invite.approximate_presence_count:,}"),
            inline=True,
        )

        await ctx.send(embed=embed)

    @commands.command(
        name="userinfo",
        usage="<user>",
        example="rx#1337",
        aliases=["whois", "uinfo", "ui", "user"],
    )
    async def userinfo(self, ctx: wock.Context, *, user: wock.Member | wock.User = None):
        """View information about a user"""

        user = user or ctx.author

        embed = discord.Embed()
        embed.set_author(
            name=f"{user} ({user.id})",
            icon_url=user.display_avatar,
        )
        embed.set_thumbnail(url=user.display_avatar)

        embed.add_field(
            name="Account created",
            value=discord.utils.format_dt(user.created_at, "D") + "\n> " + discord.utils.format_dt(user.created_at, "R"),
            inline=True,
        )
        if isinstance(user, discord.Member):
            embed.add_field(
                name="Joined this server",
                value=discord.utils.format_dt(user.joined_at, "D") + "\n> " + discord.utils.format_dt(user.joined_at, "R"),
                inline=True,
            )
            if user.premium_since:
                embed.add_field(
                    name="Boosted this server",
                    value=discord.utils.format_dt(user.premium_since, "D") + "\n> " + discord.utils.format_dt(user.premium_since, "R"),
                    inline=True,
                )
        if isinstance(user, discord.Member):
            if roles := list(reversed(user.roles[1:])):
                embed.add_field(
                    name=f"Roles ({len(roles)})",
                    value=">>> "
                    + ", ".join([role.mention for role in roles[:7]])
                    + (f" (+{humanize.comma(len(roles) - 7)})" if len(roles) > 7 else ""),
                    inline=False,
                )
                embed.set_footer(text=f"Join position: {sorted(user.guild.members, key=lambda m: m.joined_at).index(user) + 1:,}")

        mutual_guilds = len(self.bot.guilds) if user.id == self.bot.user.id else len(user.mutual_guilds)
        if footer := embed.footer.text:
            embed.set_footer(text=footer + f" ∙ {functions.plural(mutual_guilds):mutual server}")
        else:
            embed.set_footer(text=f"{functions.plural(mutual_guilds):mutual server}")

        await ctx.send(embed=embed)

    @commands.command(
        name="avatar",
        usage="<user>",
        example="rx#1337",
        aliases=["av", "ab", "ag", "avi", "pfp"],
    )
    async def avatar(self, ctx: wock.Context, *, user: wock.Member | wock.User = None):
        """View a user's avatar"""

        user = user or ctx.author

        embed = discord.Embed(url=user.display_avatar.url, title=f"{user.name}'s avatar")
        embed.set_image(url=user.display_avatar)
        await ctx.send(embed=embed)

    @commands.command(
        name="serveravatar",
        usage="<user>",
        example="rx#1337",
        aliases=["sav", "sab", "sag", "savi", "spfp"],
    )
    async def serveravatar(self, ctx: wock.Context, *, user: wock.Member = None):
        """View a user's server avatar"""

        user = user or ctx.author
        if not user.guild_avatar:
            return await ctx.warn("You don't have a **server avatar**" if user == ctx.author else f"**{user}** doesn't have a **server avatar**")

        embed = discord.Embed(url=user.guild_avatar.url, title=f"{user.name}'s server avatar")
        embed.set_image(url=user.guild_avatar)
        await ctx.send(embed=embed)

    @commands.command(
        name="banner",
        usage="<user>",
        example="rx#1337",
        aliases=["ub"],
    )
    async def banner(self, ctx: wock.Context, *, user: wock.Member | wock.User = None):
        """View a user's banner"""

        user = user or ctx.author
        user = await self.bot.fetch_user(user.id)
        url = (
            user.banner.url
            if user.banner
            else ("https://singlecolorimage.com/get/" + str(user.accent_color or discord.Color(0)).replace("#", "") + "/400x100")
        )

        embed = discord.Embed(url=url, title=f"{user.name}'s banner")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(name="emojis", aliases=["emotes"])
    async def emojis(self, ctx: wock.Context):
        """View all emojis in the server"""

        if not ctx.guild.emojis:
            return await ctx.warn("No emojis are in this **server**")

        await ctx.paginate(
            discord.Embed(
                title=f"Emojis in {ctx.guild.name}",
                description=list(f"{emoji} (`{emoji.id}`)" for emoji in ctx.guild.emojis),
            )
        )

    @commands.command(name="stickers")
    async def stickers(self, ctx: wock.Context):
        """View all stickers in the server"""

        if not ctx.guild.stickers:
            return await ctx.warn("No stickers are in this **server**")

        await ctx.paginate(
            discord.Embed(
                title=f"Stickers in {ctx.guild.name}",
                description=list(f"[**{sticker.name}**]({sticker.url}) (`{sticker.id}`)" for sticker in ctx.guild.stickers),
            )
        )

    @commands.command(name="roles")
    async def roles(self, ctx: wock.Context):
        """View all roles in the server"""

        if not ctx.guild.roles[1:]:
            return await ctx.warn("No roles are in this **server**")

        await ctx.paginate(
            discord.Embed(
                title=f"Roles in {ctx.guild.name}",
                description=list(f"{role.mention} (`{role.id}`)" for role in reversed(ctx.guild.roles[1:])),
            )
        )

    @commands.command(name="inrole", usage="<role>", example="helper", aliases=["hasrole"])
    async def inrole(self, ctx: wock.Context, *, role: wock.Role = None):
        """View all members with a role"""

        role = role or ctx.author.top_role

        if not role.members:
            return await ctx.warn(f"No members have {role.mention}")

        await ctx.paginate(
            discord.Embed(
                title=f"Members with {role.name}",
                description=list(f"**{member}** (`{member.id}`)" for member in role.members),
            )
        )

    @commands.group(
        name="boosters",
        aliases=["boosts"],
        invoke_without_command=True,
    )
    async def boosters(self, ctx: wock.Context):
        """View all members boosting the server"""

        members = list(
            sorted(
                filter(
                    lambda m: m.premium_since,
                    ctx.guild.members,
                ),
                key=lambda m: m.premium_since,
                reverse=True,
            )
        )
        if not members:
            return await ctx.warn("No members are **boosting**")

        await ctx.paginate(
            discord.Embed(
                title="Boosters",
                description=list(f"**{member}** boosted {discord.utils.format_dt(member.premium_since, style='R')}" for member in members),
            )
        )

    @boosters.command(
        name="lost",
        aliases=["removed"],
    )
    async def boosters_lost(self, ctx: wock.Context):
        """View all members which stopped boosting"""

        members = [
            f"**{ctx.guild.get_member(row.get('user_id'))}** stopped {discord.utils.format_dt(row.get('expired'), style='R')}"
            async for row in self.bot.db.fetchiter(
                "SELECT user_id, expired FROM boosters_lost WHERE guild_id = $1 ORDER BY expired DESC", ctx.guild.id
            )
            if ctx.guild.get_member(row.get("user_id"))
        ]
        if not members:
            return await ctx.warn("No members have **stopped boosting**")

        await ctx.paginate(
            discord.Embed(
                title="Boosters Lost",
                description=members,
            )
        )

    @commands.command(
        name="recentmembers",
        usage="<amount>",
        example="50",
        aliases=["recentusers", "recentjoins", "newmembers", "newusers"],
    )
    @commands.has_permissions(manage_guild=True)
    async def recentmembers(self, ctx: wock.Context, amount: int = 50):
        """View the most recent members to join the server"""

        if not amount:
            return await ctx.warn("Please provide an **amount** of members to view")

        await ctx.paginate(
            discord.Embed(
                title="Recent Members",
                description=list(
                    f"**{member}** - {discord.utils.format_dt(member.joined_at, style='R')}"
                    for member in sorted(
                        ctx.guild.members,
                        key=lambda member: member.joined_at,
                        reverse=True,
                    )[:amount]
                ),
            )
        )

    @commands.group(
        name="timezone",
        usage="<member>",
        example="rx#1337",
        aliases=["time", "tz"],
        invoke_without_command=True,
    )
    async def timezone(self, ctx: wock.Context, *, member: wock.Member = None):
        """View a member's timezone"""

        member = member or ctx.author

        location = await self.bot.db.fetchval("SELECT location FROM timezone WHERE user_id = $1", member.id)
        if not location:
            return await ctx.warn(
                f"Your **timezone** hasn't been set yet\n> Use `{ctx.prefix}timezone set (location)` to set it"
                if member == ctx.author
                else f"**{member}** hasn't set their **timezone**"
            )

        timestamp = discord.utils.utcnow().astimezone(pytz.timezone(location))
        await ctx.neutral(
            f"Your current time is **{timestamp.strftime('%b %d, %I:%M %p')}**"
            if member == ctx.author
            else f"**{member}**'s current time is **{timestamp.strftime('%b %d, %I:%M %p')}**",
            emoji=":clock" + str(timestamp.strftime("%-I")) + ("30" if int(timestamp.strftime("%-M")) >= 30 else "") + ":",
        )

    @timezone.command(name="set", usage="(location)", example="Los Angeles")
    async def timezone_set(self, ctx: wock.Context, *, location: wock.Location):
        """Set your timezone"""

        await self.bot.db.execute(
            "INSERT INTO timezone (user_id, location) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET location = $2",
            ctx.author.id,
            location.get("tz_id"),
        )
        await ctx.approve(f"Your **timezone** has been set to `{location.get('tz_id')}`")

    @timezone.command(name="list", aliases=["all"])
    async def timezone_list(self, ctx: wock.Context):
        """View all member timezones"""

        locations = [
            f"**{ctx.guild.get_member(row.get('user_id'))}** (`{row.get('location')}`)"
            async for row in self.bot.db.fetchiter(
                "SELECT user_id, location FROM timezone WHERE user_id = ANY($1::BIGINT[]) ORDER BY location ASC",
                [member.id for member in ctx.guild.members],
            )
        ]
        if not locations:
            return await ctx.warn("No **timezones** have been set")

        await ctx.paginate(
            discord.Embed(
                title="Member Timezones",
                description=locations,
            )
        )


async def setup(bot: wock.wockSuper):
    await bot.add_cog(information(bot))
