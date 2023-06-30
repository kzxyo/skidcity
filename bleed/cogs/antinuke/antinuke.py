from typing import Dict, List, Literal

import discord

from discord import AuditLogEntry, Embed, Message
from discord.ext.commands import Cog, CommandError, group
from discord.ext.tasks import loop

import config

from helpers.bleed import Bleed
from helpers.converters import Member, Status, User
from helpers.flags.antinuke import Parameters
from helpers.managers import Context, ratelimiter
from helpers.models.antinuke import Configuration
from helpers.variables import dangerous_permissions


class Antinuke(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot
        self.config: Dict[int, Configuration] = dict()

    async def cog_load(self) -> None:
        self.revalidate_config.start()

    async def cog_unload(self) -> None:
        self.revalidate_config.cancel()

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.command.name == "admin":
            if not ctx.author.id == ctx.guild.owner_id:
                raise CommandError(
                    "You must be the **server owner** to run this command."
                )

            return True

        admins = set(
            await self.bot.db.fetchval(
                """
                SELECT admins FROM antinuke
                WHERE guild_id = $1
                """,
                ctx.guild.id,
            )
            or []
        )
        admins.add(ctx.guild.owner_id)

        if not ctx.author.id in admins:
            raise CommandError("You must be an **antinuke admin** to run this command.")

        return True

    @loop(seconds=30)
    async def revalidate_config(self):
        schedule_deletion: List[int] = list()

        for row in await self.bot.db.fetch(
            """
            SELECT * FROM antinuke
            """
        ):
            guild_id: int = row.get("guild_id")
            if guild := self.bot.get_guild(guild_id):
                self.config[guild_id] = Configuration(**row)
            else:
                schedule_deletion.append(guild_id)

        if schedule_deletion:
            await self.bot.db.executemany(
                """
                DELETE FROM antinuke
                WHERE guild_id = $1
                """,
                [(guild_id) for guild_id in schedule_deletion],
            )

    @Cog.listener()
    async def on_audit_log_entry_ban(self, entry: AuditLogEntry) -> None:
        data: Configuration = self.config.get(entry.guild.id)
        if not data:
            return

        elif not data.ban.status:
            return

        elif entry.user.id in (
            data.whitelist + data.admins + [entry.guild.owner_id, entry.guild.me.id]
        ):
            return

        elif not (
            retry_after := ratelimiter(
                bucket=f"antinuke:ban:{entry.guild.id}",
                key=entry.user.id,
                rate=data.ban.threshold,
                per=9,
            )
        ):
            return

        await entry.guild.kick(
            entry.user, reason=f"antinuke: banned X/{data.ban.threshold} in 9 seconds"
        )

    @group(
        name="antinuke",
        usage="(subcommand) <args>",
        example="ban on --do ban",
        aliases=["an"],
        invoke_without_command=True,
    )
    async def antinuke(self, ctx: Context) -> Message:
        """
        Antinuke to protect your server
        """

        return await ctx.send_help()

    @antinuke.command(
        name="config",
        aliases=[
            "configuration",
            "settings",
        ],
    )
    async def antinuke_config(self, ctx: Context) -> Message:
        """
        View server configuration for Antinuke
        """

        configuration: Configuration = Configuration(
            **await self.bot.db.fetchrow(
                """
            SELECT * FROM antinuke
            WHERE guild_id = $1
            """,
                ctx.guild.id,
            )
        )

        enabled: int = 0
        for module, value in configuration:
            if not (status := getattr(value, "status", False)):
                continue

            enabled += 1

        embed = Embed(
            color=config.Color.neutral,
            title="Settings",
            description=f"Antinuke is **{'enabled' if enabled else 'disabled'}** in this server",
        )

        embed.add_field(
            name="Modules",
            value=(
                "**Role Deletion:** "
                + (
                    config.Emoji.approve
                    if configuration.role.status
                    else config.Emoji.deny
                )
                + "\n**Emoji Deletion:** "
                + (
                    config.Emoji.approve
                    if configuration.emoji.status
                    else config.Emoji.deny
                )
                + "\n**Mass Member Ban:** "
                + (
                    config.Emoji.approve
                    if configuration.ban.status
                    else config.Emoji.deny
                )
                + "\n**Mass Member Kick:** "
                + (
                    config.Emoji.approve
                    if configuration.kick.status
                    else config.Emoji.deny
                )
                + "\n**Webhook Creation:** "
                + (
                    config.Emoji.approve
                    if configuration.webhook.status
                    else config.Emoji.deny
                )
                + "\n**Channel Creation/Deletion:** "
                + (
                    config.Emoji.approve
                    if configuration.channel.status
                    else config.Emoji.deny
                )
            ),
            inline=True,
        )
        embed.add_field(
            name="General",
            value=(
                f"**Super Admins:** {len(configuration.admins)}"
                + "\n**Whitelisted Bots:** "
                + str(
                    len(
                        [
                            member_id
                            for member_id in configuration.whitelist
                            if (member := self.bot.get_user(member_id)) and member.bot
                        ]
                    )
                )
                + "\n**Whitelisted Members:** "
                + str(
                    len(
                        [
                            member_id
                            for member_id in configuration.whitelist
                            if (member := self.bot.get_user(member_id))
                            and not member.bot
                        ]
                    )
                )
                + "\n**Protection Modules:** "
                + f"{enabled} enabled"
                + "\n**Watch Permission Grant:** "
                + (
                    str(
                        len(
                            [
                                permission
                                for permission in configuration.permissions
                                if permission.type == "grant"
                            ]
                        )
                    )
                    + "/"
                    + str(len(dangerous_permissions))
                    + " perms"
                )
                + "\n**Watch Permission Remove:** "
                + (
                    str(
                        len(
                            [
                                permission
                                for permission in configuration.permissions
                                if permission.type == "remove"
                            ]
                        )
                    )
                    + "/"
                    + str(len(dangerous_permissions))
                    + " perms"
                )
                + "\n**Deny Bot Joins (bot add):** "
                + (
                    config.Emoji.approve
                    if configuration.botadd.status
                    else config.Emoji.deny
                )
            ),
            inline=True,
        )

        return await ctx.send(embed=embed)

    @antinuke.command(
        name="whitelist",
        usage="(member or bot id)",
        example="593921296224747521",
    )
    async def antinuke_whitelist(
        self, ctx: Context, *, member: Member | User
    ) -> Message:
        """
        Whitelist a member from triggering antinuke or a bot to join
        """

        whitelist: List[int] = await self.bot.db.fetchval(
            """
            INSERT INTO antinuke (guild_id, whitelist)
            VALUES ($1, ARRAY[$2]::bigint[])
            ON CONFLICT (guild_id) DO UPDATE
            SET whitelist = CASE
                WHEN $2 = ANY(antinuke.whitelist) THEN array_remove(antinuke.whitelist, $2)
                ELSE antinuke.whitelist || ARRAY[$2]::bigint[]
                END
            RETURNING whitelist;
            """,
            ctx.guild.id,
            member.id,
        )

        if member.id in whitelist:
            return await ctx.approve(
                f"**{member}** is now whitelisted and "
                + (
                    "can join"
                    if member.bot and not isinstance(member, discord.Member)
                    else "will not trigger **antinuke**"
                )
            )
        else:
            return await ctx.approve(f"**{member}** is no longer whitelisted")

    @antinuke.command(
        name="admin",
        usage="(member)",
        example="jonathan",
    )
    async def antinuke_admin(self, ctx: Context, *, member: Member | User) -> Message:
        """
        Give a member permissions to edit antinuke settings
        """

        if member.bot:
            return await ctx.warn("You cannot make a bot an **antinuke admin**")

        admins: List[int] = await self.bot.db.fetchval(
            """
            INSERT INTO antinuke (guild_id, admins)
            VALUES ($1, ARRAY[$2]::bigint[])
            ON CONFLICT (guild_id) DO UPDATE
            SET admins = CASE
                WHEN $2 = ANY(antinuke.admins) THEN array_remove(antinuke.admins, $2)
                ELSE antinuke.admins || ARRAY[$2]::bigint[]
                END
            RETURNING admins;
            """,
            ctx.guild.id,
            member.id,
        )

        if member.id in admins:
            return await ctx.approve(
                f"**{member}** is now an **antinuke admin** and can edit **antinuke settings**"
            )
        else:
            return await ctx.approve(
                f"**{member}** is no longer an **antinuke admin** and can no longer edit **antinuke settings**"
            )

    @antinuke.command(name="admins")
    async def antinuke_admins(self, ctx: Context) -> Message:
        """
        View all antinuke admins
        """

        admins: List[int] = (
            await self.bot.db.fetchval(
                """
            SELECT admins FROM antinuke
            WHERE guild_id = $1;
            """,
                ctx.guild.id,
            )
            or []
        )

        if not admins:
            return await ctx.warn("There are no **antinuke admins**")

        return await ctx.paginate(
            Embed(
                title="Antinuke Admins",
                description=[f"<@{user_id}>" for user_id in admins],
            )
        )

    @antinuke.command(name="list")
    async def antinuke_list(self, ctx: Context) -> Message:
        """
        View all enabled modules along with whitelisted members & bots
        """

        configuration: Configuration = Configuration(
            **await self.bot.db.fetchrow(
                """
            SELECT * FROM antinuke
            WHERE guild_id = $1
            """,
                ctx.guild.id,
            )
        )

        entries: List = []

        if (ban := configuration.ban) and ban.status:
            entries.append(
                f"**ban** (do: {ban.punishment}, threshold: {ban.threshold}, cmd: {'on' if ban.command else 'off'})"
            )

        if (kick := configuration.kick) and kick.status:
            entries.append(
                f"**kick** (do: {kick.punishment}, threshold: {kick.threshold}, cmd: {'on' if kick.command else 'off'})"
            )

        if (role := configuration.role) and role.status:
            entries.append(
                f"**role** (do: {role.punishment}, threshold: {role.threshold}, cmd: {'on' if role.command else 'off'})"
            )

        if (channel := configuration.channel) and channel.status:
            entries.append(
                f"**channel** (do: {channel.punishment}, threshold: {channel.threshold})"
            )

        if (emoji := configuration.emoji) and emoji.status:
            entries.append(
                f"**emoji** (do: {emoji.punishment}, threshold: {emoji.threshold})"
            )

        if (webhook := configuration.webhook) and webhook.status:
            entries.append(
                f"**webhook** (do: {webhook.punishment}, threshold: {webhook.threshold})"
            )

        if (botadd := configuration.botadd) and botadd.status:
            entries.append(f"**botadd** (do: {botadd.punishment})")

        for user_id in configuration.whitelist:
            user: discord.Member = self.bot.get_user(user_id)

            entries.append(
                f"**{user or 'Unknown User'}** whitelisted (`{user_id}`) [`{'MEMBER' if not user.bot else 'BOT'}`]"
            )

        if not entries:
            return await ctx.warn("There are no **antinuke modules** enabled")

        return await ctx.paginate(
            Embed(
                title="Antinuke modules & whitelist",
                description=entries,
            )
        )

    @antinuke.command(
        name="botadd",
        usage="(on or off) --params",
        example="on --do ban",
        flags=Parameters,
    )
    async def antinuke_botadd(
        self, ctx: Context, status: Status, *, flags: str = None
    ) -> Message:
        """
        Prevent new bot additions
        """

        await self.bot.db.execute(
            """
            INSERT INTO antinuke (
                guild_id,
                botadd
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET
                botadd = EXCLUDED.botadd;
            """,
            ctx.guild.id,
            {
                "status": status,
                "punishment": ctx.flags.get("punishment"),
            },
        )

        if status:
            return await ctx.approve(
                "Updated **bot add** antinuke module."
                + (f"\nPunishment is set to **{ctx.flags.get('punishment')}** ")
            )
        else:
            return await ctx.approve("Disabled **bot add** antinuke module")

    @antinuke.command(
        name="webhook",
        usage="(on or off) --params",
        example="on --do ban --threshold 3",
        flags=Parameters,
    )
    async def antinuke_webhook(
        self, ctx: Context, status: Status, *, flags: str = None
    ) -> Message:
        """
        Prevent mass webhook creation
        """

        await self.bot.db.execute(
            """
            INSERT INTO antinuke (
                guild_id,
                webhook
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET
                webhook = EXCLUDED.webhook;
            """,
            ctx.guild.id,
            {
                "status": status,
                "punishment": ctx.flags.get("punishment"),
                "threshold": ctx.flags.get("threshold"),
            },
        )

        if status:
            return await ctx.approve(
                "Updated **webhook** antinuke module."
                + (
                    f"\nPunishment is set to **{ctx.flags.get('punishment')}** "
                    f"and threshold is set to **{ctx.flags.get('threshold')}**"
                )
            )
        else:
            return await ctx.approve("Disabled **webhook** antinuke module")

    @antinuke.command(
        name="emoji",
        usage="(on or off) --params",
        example="on --do kick --threshold 3",
        flags=Parameters,
    )
    async def antinuke_emoji(
        self, ctx: Context, status: Status, *, flags: str = None
    ) -> Message:
        """
        Prevent mass emoji delete
        Warning: This module may be unstable due to Discord's rate limit
        """

        await self.bot.db.execute(
            """
            INSERT INTO antinuke (
                guild_id,
                emoji
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET
                emoji = EXCLUDED.emoji;
            """,
            ctx.guild.id,
            {
                "status": status,
                "punishment": ctx.flags.get("punishment"),
                "threshold": ctx.flags.get("threshold"),
            },
        )

        if status:
            return await ctx.approve(
                "Updated **emoji** antinuke module."
                + (
                    f"\nPunishment is set to **{ctx.flags.get('punishment')}** "
                    f"and threshold is set to **{ctx.flags.get('threshold')}**"
                )
            )
        else:
            return await ctx.approve("Disabled **emoji** antinuke module")

    @antinuke.command(
        name="permissions",
        usage="(grant or remove) (permission)",
        example="grant administrator",
        aliases=["perms"],
        flags=Parameters,
    )
    async def antinuke_permissions(
        self,
        ctx: Context,
        option: Literal["grant", "remove"],
        permission: str,
        *,
        flags: str = None,
    ) -> Message:
        """
        Watch for dangerous permissions being granted or removed
        """

        permission = permission.lower()
        if not permission in dangerous_permissions:
            return await ctx.warn(
                "You passed an **invalid permission name**, please visit the documentation [here](https://docs.bleed.bot/help/commands/antinuke/antinuke-permissions)"
            )

        permission: Dict = {
            "type": option,
            "permission": permission,
            "punishment": ctx.flags.get("punishment"),
        }
        permissions: List[Dict] = (
            await self.bot.db.fetchval(
                """
            SELECT permissions FROM antinuke
            WHERE guild_id = $1;
            """,
                ctx.guild.id,
            )
            or []
        )

        for _permission in list(permissions):
            if _permission == permission:
                permissions.remove(permission)
                await self.bot.db.execute(
                    """
                    INSERT INTO antinuke (guild_id, permissions)
                    VALUES ($1, $2)
                    ON CONFLICT (guild_id) DO UPDATE
                    SET permissions = EXCLUDED.permissions;
                    """,
                    ctx.guild.id,
                    permissions,
                )

                return await ctx.approve(
                    f"No longer monitoring **{'granting' if option == 'grant' else 'removal'} of** permission `{permission['permission']}`"
                )

            elif (_permission["type"] == option) and (
                _permission["permission"] == permission["permission"]
            ):
                permissions.remove(_permission)

        permissions.append(permission)

        await self.bot.db.execute(
            """
            INSERT INTO antinuke (guild_id, permissions)
            VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE
            SET permissions = EXCLUDED.permissions;
            """,
            ctx.guild.id,
            permissions,
        )

        return await ctx.approve(
            f"Now monitoring **{'granting' if option == 'grant' else 'removal'} of** permission `{permission['permission']}`. Members **manually** giving out roles to others will be punished with `{permission['punishment']}`"
        )

    @antinuke.command(
        name="ban",
        usage="(on or off) --params",
        example="on --do ban --command on",
        flags=Parameters,
    )
    async def antinuke_ban(
        self, ctx: Context, status: Status, *, flags: str = None
    ) -> Message:
        """
        Prevent mass member ban
        """

        await self.bot.db.execute(
            """
            INSERT INTO antinuke (
                guild_id,
                ban
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET
                ban = EXCLUDED.ban;
            """,
            ctx.guild.id,
            {
                "status": status,
                "punishment": ctx.flags.get("punishment"),
                "threshold": ctx.flags.get("threshold"),
                "command": ctx.flags.get("command"),
            },
        )

        if status:
            return await ctx.approve(
                "Updated **ban** antinuke module."
                + (
                    f"\nPunishment is set to **{ctx.flags.get('punishment')}**, "
                    f"threshold is set to **{ctx.flags.get('threshold')}** "
                    f"and command detection is **{'on' if ctx.flags.get('command') else 'off'}**"
                )
            )
        else:
            return await ctx.approve("Disabled **ban** antinuke module")

    @antinuke.command(
        name="kick",
        usage="(on or off) --params",
        example="on --do stripstaff --threshold 3",
        flags=Parameters,
    )
    async def antinuke_kick(
        self, ctx: Context, status: Status, *, flags: str = None
    ) -> Message:
        """
        Prevent mass member kick
        """

        await self.bot.db.execute(
            """
            INSERT INTO antinuke (
                guild_id,
                kick
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET
                kick = EXCLUDED.kick;
            """,
            ctx.guild.id,
            {
                "status": status,
                "punishment": ctx.flags.get("punishment"),
                "threshold": ctx.flags.get("threshold"),
                "command": ctx.flags.get("command"),
            },
        )

        if status:
            return await ctx.approve(
                "Updated **kick** antinuke module."
                + (
                    f"\nPunishment is set to **{ctx.flags.get('punishment')}**, "
                    f"threshold is set to **{ctx.flags.get('threshold')}** "
                    f"and command detection is **{'on' if ctx.flags.get('command') else 'off'}**"
                )
            )
        else:
            return await ctx.approve("Disabled **kick** antinuke module")

    @antinuke.command(
        name="channel",
        usage="(on or off) --params",
        example="on --do ban --threshold 3",
        flags=Parameters,
    )
    async def antinuke_channel(
        self, ctx: Context, status: Status, *, flags: str = None
    ) -> Message:
        """
        Prevent mass channel create and delete
        """

        await self.bot.db.execute(
            """
            INSERT INTO antinuke (
                guild_id,
                channel
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET
                channel = EXCLUDED.channel;
            """,
            ctx.guild.id,
            {
                "status": status,
                "punishment": ctx.flags.get("punishment"),
                "threshold": ctx.flags.get("threshold"),
            },
        )

        if status:
            return await ctx.approve(
                "Updated **channel** antinuke module."
                + (
                    f"\nPunishment is set to **{ctx.flags.get('punishment')}** "
                    f"and threshold is set to **{ctx.flags.get('threshold')}**"
                )
            )
        else:
            return await ctx.approve("Disabled **channel** antinuke module")

    @antinuke.command(
        name="role",
        usage="(on or off) --params",
        example="on --do ban --threshold 3",
        flags=Parameters,
    )
    async def antinuke_role(
        self, ctx: Context, status: Status, *, flags: str = None
    ) -> Message:
        """
        Prevent mass role delete
        """

        await self.bot.db.execute(
            """
            INSERT INTO antinuke (
                guild_id,
                role
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET
                role = EXCLUDED.role;
            """,
            ctx.guild.id,
            {
                "status": status,
                "punishment": ctx.flags.get("punishment"),
                "threshold": ctx.flags.get("threshold"),
                "command": ctx.flags.get("command"),
            },
        )

        if status:
            return await ctx.approve(
                "Updated **role** antinuke module."
                + (
                    f"\nPunishment is set to **{ctx.flags.get('punishment')}**, "
                    f"threshold is set to **{ctx.flags.get('threshold')}** "
                    f"and command detection is **{'on' if ctx.flags.get('command') else 'off'}**"
                )
            )
        else:
            return await ctx.approve("Disabled **role** antinuke module")
