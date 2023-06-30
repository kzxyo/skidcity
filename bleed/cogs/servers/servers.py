from asyncpg.exceptions import UniqueViolationError
from discord import Embed, Member, Message, TextChannel
from discord.ext.commands import Cog, group, has_permissions

import config

from helpers import tagscript
from helpers.bleed import Bleed
from helpers.converters import TagScript
from helpers.flags.servers import Parameters
from helpers.managers import Context
from helpers.models.tagscript import ScriptObject
from helpers.utilities import ensure_future


class Servers(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot

    @Cog.listener("on_member_agree")
    async def send_join_message(self, member: Member) -> None:
        for row in await self.bot.db.fetch(
            """
            SELECT * FROM join_messages
            WHERE guild_id = $1;
            """,
            member.guild.id,
        ):
            channel: TextChannel
            if not (channel := member.guild.get_channel(row["channel_id"])):
                continue

            script: ScriptObject = tagscript.parse(
                script=row["message"],
                user=member,
                channel=channel,
            )
            await ensure_future(
                channel.send(
                    **script.dump,
                    delete_after=row.get("self_destruct"),
                )
            )

    @Cog.listener("on_member_remove")
    async def send_leave_message(self, member: Member) -> None:
        for row in await self.bot.db.fetch(
            """
            SELECT * FROM leave_messages
            WHERE guild_id = $1;
            """,
            member.guild.id,
        ):
            channel: TextChannel
            if not (channel := member.guild.get_channel(row["channel_id"])):
                continue

            script: ScriptObject = tagscript.parse(
                script=row["message"],
                user=member,
                channel=channel,
            )
            await ensure_future(
                channel.send(
                    **script.dump,
                    delete_after=row.get("self_destruct"),
                )
            )

    @Cog.listener("on_member_boost")
    async def send_boost_message(self, member: Member) -> None:
        for row in await self.bot.db.fetch(
            """
            SELECT * FROM boost_messages
            WHERE guild_id = $1;
            """,
            member.guild.id,
        ):
            channel: TextChannel
            if not (channel := member.guild.get_channel(row["channel_id"])):
                continue

            script: ScriptObject = tagscript.parse(
                script=row["message"],
                user=member,
                channel=channel,
            )
            await ensure_future(
                channel.send(
                    **script.dump,
                    delete_after=row.get("self_destruct"),
                )
            )

    @group(
        name="prefix",
        invoke_without_command=True,
    )
    async def prefix(self, ctx: Context) -> Message:
        """
        View guild prefix
        """

        prefix = (
            await self.bot.db.fetchval(
                """
            SELECT prefix FROM config
            WHERE guild_id = $1
            """,
                ctx.guild.id,
            )
            or config.prefix
        )
        if prefix == "disabled":
            return await ctx.warn(
                f"Your guild doesn't have a **prefix set!** Set it using `@{self.bot.user} prefix add (prefix)`"
            )

        return await ctx.neutral(f"Guild Prefix: `{prefix}`")

    @prefix.command(
        name="remove",
        aliases=[
            "delete",
            "del",
            "clear",
        ],
    )
    @has_permissions(administrator=True)
    async def prefix_remove(self, ctx: Context) -> Message:
        """
        Remove command prefix for guild
        """

        await self.bot.db.execute(
            """
            UPDATE config SET
                prefix = $2
            WHERE guild_id = $1
            """,
            ctx.guild.id,
            "disabled",
        )

        return await ctx.approve(
            f"Your guild's prefix has been **removed**. You can set a **new prefix** using `@{self.bot.user} prefix add (prefix)`"
        )

    @prefix.command(
        name="set",
        usage="(prefix)",
        example="!",
        aliases=["add"],
    )
    @has_permissions(administrator=True)
    async def prefix_set(self, ctx: Context, prefix: str) -> Message:
        """
        Set command prefix for guild
        """

        if len(prefix) > 10:
            return await ctx.warn(
                "Your **prefix** cannot be longer than **10 characters**!"
            )

        await self.bot.db.execute(
            """
            INSERT INTO config (
                guild_id,
                prefix
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET
                prefix = EXCLUDED.prefix;
            """,
            ctx.guild.id,
            prefix.lower(),
        )

        return await ctx.approve(
            f"{'Set' if prefix == config.prefix else 'Replaced'} your current guild's prefix to `{prefix.lower()}`"
        )

    @group(
        name="settings",
        usage="(subcommand) <args>",
        example="jail #jail",
        aliases=["bind"],
        invoke_without_command=True,
    )
    @has_permissions(manage_guild=True)
    async def settings(self, ctx: Context) -> Message:
        """
        Server configuration - visit https://bleed.bot/help for all commands
        """

        return await ctx.send_help()

    @settings.group(
        name="welcome",
        usage="(subcommand) <args> --params",
        example="add #hi Hi {user.mention}! --self_destruct 10",
        aliases=["welc"],
        invoke_without_command=True,
    )
    @has_permissions(manage_guild=True)
    async def settings_welcome(self, ctx: Context) -> Message:
        """
        Set up a welcome message in one or multiple channels
        """

        return await ctx.send_help()

    @settings_welcome.command(
        name="add",
        usage="(channel) (message) --params",
        example="#hi Hi {user.mention}! --self_destruct 10",
        aliases=["create"],
        flags=Parameters,
    )
    @has_permissions(manage_guild=True)
    async def settings_welcome_add(
        self, ctx: Context, channel: TextChannel, *, message: TagScript
    ) -> Message:
        """
        Add a welcome message for a channel
        """

        if self_destruct := ctx.flags.get("self_destruct"):
            if self_destruct < 6:
                return await ctx.warn(
                    "**Self-destruct** timer must be at least `6` seconds"
                )

            elif self_destruct > 120:
                return await ctx.warn(
                    "**Self-destruct** timer must be below `120` seconds"
                )

        try:
            await self.bot.db.execute(
                """
                INSERT INTO join_messages (
                    guild_id,
                    channel_id,
                    message,
                    self_destruct
                ) VALUES ($1, $2, $3, $4);
                """,
                ctx.guild.id,
                channel.id,
                message.script,
                self_destruct,
            )
        except UniqueViolationError:
            return await ctx.deny(
                "Theres already a **join message** for this channel, you can't have multiple for one channel. Remove the current **join message** then try again."
            )
        else:
            return await ctx.approve(
                "Created "
                + ("an embed" if message.type == "embed" else "a")
                + f" **join message** and set the join channel to {channel.mention}"
                + (
                    f"\nEvery **join message** will self-destruct after `{self_destruct}` seconds"
                    if self_destruct
                    else ""
                )
            )

    @settings_welcome.command(
        name="remove",
        usage="(channel)",
        example="#joneral",
        aliases=[
            "delete",
            "del",
        ],
    )
    @has_permissions(manage_guild=True)
    async def settings_welcome_remove(
        self, ctx: Context, *, channel: TextChannel
    ) -> Message:
        """
        Remove a welcome message from a channel
        """

        if await self.bot.db.fetchval(
            """
            DELETE FROM join_messages
            WHERE guild_id = $1
            AND channel_id = $2
            RETURNING channel_id;
            """,
            ctx.guild.id,
            channel.id,
        ):
            return await ctx.approve(
                f"Removed the **join message** for {channel.mention}"
            )
        else:
            return await ctx.deny(f"No **join message** exists for {channel.mention}")

    @settings_welcome.command(
        name="view",
        usage="(channel)",
        example="#joneral",
        aliases=["check"],
    )
    @has_permissions(manage_guild=True)
    async def settings_welcome_view(
        self, ctx: Context, *, channel: TextChannel
    ) -> Message:
        """
        View welcome message for a channel
        """

        if not (
            message := await self.bot.db.fetchval(
                """
            SELECT message FROM join_messages
            WHERE guild_id = $1
            AND channel_id = $2;
            """,
                ctx.guild.id,
                channel.id,
            )
        ):
            return await ctx.deny(f"No **join message** exists for {channel.mention}")

        script: ScriptObject = tagscript.parse(
            script=message,
            user=ctx.author,
            channel=ctx.channel,
        )

        return await ctx.channel.send(**script.dump)

    @settings_welcome.command(name="list")
    @has_permissions(manage_guild=True)
    async def settings_welcome_list(self, ctx: Context) -> Message:
        """
        View all welcome messages
        """

        channels = [
            f"{channel.mention} (`{channel.id}`)"
            for row in await self.bot.db.fetch(
                """
                SELECT channel_id FROM join_messages
                WHERE guild_id = $1
                """,
                ctx.guild.id,
            )
            if (channel := ctx.guild.get_channel(row["channel_id"]))
        ]
        if not channels:
            return await ctx.search("No **welcome channels** are set")

        return await ctx.paginate(
            Embed(
                title="Welcome channels",
                description=channels,
            )
        )

    @settings_welcome.command(name="variables")
    @has_permissions(manage_guild=True)
    async def settings_welcome_variables(self, ctx: Context) -> Message:
        """
        View all available variables for welcome messages
        """

        return await ctx.neutral(
            "You can view all **variables** here: https://docs.bleed.bot/bot/embed-code-variables/variables",
            emoji=":information_source:",
        )

    @settings.group(
        name="goodbye",
        usage="(subcommand) <args> --params",
        example="add #goodbye See you soon! {user}",
        aliases=["bye"],
        invoke_without_command=True,
    )
    @has_permissions(manage_guild=True)
    async def settings_goodbye(self, ctx: Context) -> Message:
        """
        Set up a goodbye message in one or multiple channels
        """

        return await ctx.send_help()

    @settings_goodbye.command(
        name="add",
        usage="(channel) (message) --params",
        example="#goodbye See you soon! {user}",
        aliases=["create"],
        flags=Parameters,
    )
    @has_permissions(manage_guild=True)
    async def settings_goodbye_add(
        self, ctx: Context, channel: TextChannel, *, message: TagScript
    ) -> Message:
        """
        Add a goodbye message for a channel
        """

        if self_destruct := ctx.flags.get("self_destruct"):
            if self_destruct < 6:
                return await ctx.warn(
                    "**Self-destruct** timer must be at least `6` seconds"
                )

            elif self_destruct > 120:
                return await ctx.warn(
                    "**Self-destruct** timer must be below `120` seconds"
                )

        try:
            await self.bot.db.execute(
                """
                INSERT INTO leave_messages (
                    guild_id,
                    channel_id,
                    message,
                    self_destruct
                ) VALUES ($1, $2, $3, $4);
                """,
                ctx.guild.id,
                channel.id,
                message.script,
                self_destruct,
            )
        except UniqueViolationError:
            return await ctx.deny(
                "Theres already a **leave message** for this channel, you can't have multiple for one channel. Remove the current **leave message** then try again."
            )
        else:
            return await ctx.approve(
                "Created "
                + ("an embed" if message.type == "embed" else "a")
                + f" **leave message** and set the leave channel to {channel.mention}"
                + (
                    f"\nEvery **leave message** will self-destruct after `{self_destruct}` seconds"
                    if self_destruct
                    else ""
                )
            )

    @settings_goodbye.command(
        name="remove",
        usage="(channel)",
        example="#joneral",
        aliases=[
            "delete",
            "del",
        ],
    )
    @has_permissions(manage_guild=True)
    async def settings_goodbye_remove(
        self, ctx: Context, *, channel: TextChannel
    ) -> Message:
        """
        Remove a goodbye message from a channel
        """

        if await self.bot.db.fetchval(
            """
            DELETE FROM leave_messages
            WHERE guild_id = $1
            AND channel_id = $2
            RETURNING channel_id;
            """,
            ctx.guild.id,
            channel.id,
        ):
            return await ctx.approve(
                f"Removed the **leave message** for {channel.mention}"
            )
        else:
            return await ctx.deny(f"No **leave message** exists for {channel.mention}")

    @settings_goodbye.command(
        name="view",
        usage="(channel)",
        example="#joneral",
        aliases=["check"],
    )
    @has_permissions(manage_guild=True)
    async def settings_goodbye_view(
        self, ctx: Context, *, channel: TextChannel
    ) -> Message:
        """
        View goodbye message for a channel
        """

        if not (
            message := await self.bot.db.fetchval(
                """
            SELECT message FROM leave_messages
            WHERE guild_id = $1
            AND channel_id = $2;
            """,
                ctx.guild.id,
                channel.id,
            )
        ):
            return await ctx.deny(f"No **leave message** exists for {channel.mention}")

        script: ScriptObject = tagscript.parse(
            script=message,
            user=ctx.author,
            channel=ctx.channel,
        )

        return await ctx.channel.send(**script.dump)

    @settings_goodbye.command(name="list")
    @has_permissions(manage_guild=True)
    async def settings_goodbye_list(self, ctx: Context) -> Message:
        """
        View all goodbye messages
        """

        channels = [
            f"{channel.mention} (`{channel.id}`)"
            for row in await self.bot.db.fetch(
                """
                SELECT channel_id FROM leave_messages
                WHERE guild_id = $1
                """,
                ctx.guild.id,
            )
            if (channel := ctx.guild.get_channel(row["channel_id"]))
        ]
        if not channels:
            return await ctx.search("No **goodbye channels** are set")

        return await ctx.paginate(
            Embed(
                title="Goodbye channels",
                description=channels,
            )
        )

    @settings_goodbye.command(name="variables")
    @has_permissions(manage_guild=True)
    async def settings_goodbye_variables(self, ctx: Context) -> Message:
        """
        View all available variables for goodbye messages
        """

        return await ctx.neutral(
            "You can view all **variables** here: https://docs.bleed.bot/bot/embed-code-variables/variables",
            emoji=":information_source:",
        )

    @settings.group(
        name="boost",
        usage="(subcommand) <args> --params",
        example="add #hi Thanks {user.mention}!",
        aliases=["boosts"],
        invoke_without_command=True,
    )
    @has_permissions(manage_guild=True)
    async def settings_boost(self, ctx: Context) -> Message:
        """
        Set up a boost message in one or multiple channels
        """

        return await ctx.send_help()

    @settings_boost.command(
        name="add",
        usage="(channel) (message) --params",
        example="#hi Thanks {user.mention}!",
        aliases=["create"],
        flags=Parameters,
    )
    @has_permissions(manage_guild=True)
    async def settings_boost_add(
        self, ctx: Context, channel: TextChannel, *, message: TagScript
    ) -> Message:
        """
        Add a boost message for a channel
        """

        if self_destruct := ctx.flags.get("self_destruct"):
            if self_destruct < 6:
                return await ctx.warn(
                    "**Self-destruct** timer must be at least `6` seconds"
                )

            elif self_destruct > 120:
                return await ctx.warn(
                    "**Self-destruct** timer must be below `120` seconds"
                )

        try:
            await self.bot.db.execute(
                """
                INSERT INTO boost_messages (
                    guild_id,
                    channel_id,
                    message,
                    self_destruct
                ) VALUES ($1, $2, $3, $4);
                """,
                ctx.guild.id,
                channel.id,
                message.script,
                self_destruct,
            )
        except UniqueViolationError:
            return await ctx.deny(
                "Theres already a **boost message** for this channel, you can't have multiple for one channel. Remove the current **boost message** then try again."
            )
        else:
            return await ctx.approve(
                "Created "
                + ("an embed" if message.type == "embed" else "a")
                + f" **boost message** and set the boost channel to {channel.mention}"
                + (
                    f"\nEvery **boost message** will self-destruct after `{self_destruct}` seconds"
                    if self_destruct
                    else ""
                )
            )

    @settings_boost.command(
        name="remove",
        usage="(channel)",
        example="#joneral",
        aliases=[
            "delete",
            "del",
        ],
    )
    @has_permissions(manage_guild=True)
    async def settings_boost_remove(
        self, ctx: Context, *, channel: TextChannel
    ) -> Message:
        """
        Remove a boost message from a channel
        """

        if await self.bot.db.fetchval(
            """
            DELETE FROM boost_messages
            WHERE guild_id = $1
            AND channel_id = $2
            RETURNING channel_id;
            """,
            ctx.guild.id,
            channel.id,
        ):
            return await ctx.approve(
                f"Removed the **boost message** for {channel.mention}"
            )
        else:
            return await ctx.deny(f"No **boost message** exists for {channel.mention}")

    @settings_boost.command(
        name="view",
        usage="(channel)",
        example="#joneral",
        aliases=["check"],
    )
    @has_permissions(manage_guild=True)
    async def settings_boost_view(
        self, ctx: Context, *, channel: TextChannel
    ) -> Message:
        """
        View boost message for a channel
        """

        if not (
            message := await self.bot.db.fetchval(
                """
            SELECT message FROM boost_messages
            WHERE guild_id = $1
            AND channel_id = $2;
            """,
                ctx.guild.id,
                channel.id,
            )
        ):
            return await ctx.deny(f"No **boost message** exists for {channel.mention}")

        script: ScriptObject = tagscript.parse(
            script=message,
            user=ctx.author,
            channel=ctx.channel,
        )

        return await ctx.channel.send(**script.dump)

    @settings_boost.command(name="list")
    @has_permissions(manage_guild=True)
    async def settings_boost_list(self, ctx: Context) -> Message:
        """
        View all boost messages
        """

        channels = [
            f"{channel.mention} (`{channel.id}`)"
            for row in await self.bot.db.fetch(
                """
                SELECT channel_id FROM boost_messages
                WHERE guild_id = $1
                """,
                ctx.guild.id,
            )
            if (channel := ctx.guild.get_channel(row["channel_id"]))
        ]
        if not channels:
            return await ctx.search("No **boost channels** are set")

        return await ctx.paginate(
            Embed(
                title="Goodbye channels",
                description=channels,
            )
        )

    @settings_boost.command(name="variables")
    @has_permissions(manage_guild=True)
    async def settings_boost_variables(self, ctx: Context) -> Message:
        """
        View all available variables for boost messages
        """

        return await ctx.neutral(
            "You can view all **variables** here: https://docs.bleed.bot/bot/embed-code-variables/variables",
            emoji=":information_source:",
        )
