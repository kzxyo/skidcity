import discord

from discord import Embed, HTTPException, Message, RateLimited, VoiceState
from discord.ext.commands import (
    BucketType,
    Cog,
    CommandError,
    cooldown,
    group,
    has_permissions,
)
from discord.utils import format_dt

import config

from helpers.bleed import Bleed
from helpers.converters import Bitrate, Member, Region, Role
from helpers.managers import Context, ratelimiter

from .interface import Interface


class VoiceMaster(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot
        self.bot.add_view(Interface(bot))

    async def cog_load(self) -> None:
        schedule_deletion: List[int] = list()

        for row in await self.bot.db.fetch(
            """
            SELECT channel_id FROM voicemaster.channels
            """
        ):
            channel_id: int = row.get("channel_id")
            if channel := self.bot.get_channel(channel_id):
                if not channel.members:
                    try:
                        await channel.delete(
                            reason="VoiceMaster: Flush empty voice channels"
                        )
                    except HTTPException:
                        pass

                    schedule_deletion.append(channel_id)

            else:
                schedule_deletion.append(channel_id)

        if schedule_deletion:
            await self.bot.db.executemany(
                """
                DELETE FROM voicemaster.channels
                WHERE channel_id = $1
                """,
                [(channel_id) for channel_id in schedule_deletion],
            )

    @Cog.listener("on_voice_state_update")
    async def create_channel(
        self, member: discord.Member, before: VoiceState, after: VoiceState
    ) -> None:
        if not after.channel:
            return

        elif before and before.channel == after.channel:
            return

        elif not (
            configuration := await self.bot.db.fetchrow(
                """
                SELECT * FROM voicemaster.configuration
                WHERE guild_id = $1
                """,
                member.guild.id,
            )
        ):
            return

        elif configuration.get("channel_id") != after.channel.id:
            return

        if retry_after := ratelimiter(
            "voicemaster:create",
            key=member,
            rate=1,
            per=10,
        ):
            try:
                await member.move_to(None)
            except HTTPException:
                pass

            return

        channel = await member.guild.create_voice_channel(
            name=f"{member.display_name}'s channel",
            category=(
                member.guild.get_channel(configuration.get("category_id"))
                or after.channel.category
            ),
            bitrate=(
                (
                    bitrate := configuration.get(
                        "bitrate", int(member.guild.bitrate_limit)
                    )
                )
                and (
                    bitrate
                    if bitrate <= int(member.guild.bitrate_limit)
                    else int(member.guild.bitrate_limit)
                )
            ),
            rtc_region=configuration.get("region"),
            reason=f"VoiceMaster: Created a voice channel for {member}",
        )

        try:
            await member.move_to(
                channel,
                reason="VoiceMaster: Created their own voice channel",
            )
        except HTTPException:
            await channel.delete(reason="VoiceMaster: Failed to move member")
            return

        await channel.set_permissions(
            member,
            read_messages=True,
            connect=True,
            reason=f"VoiceMaster: {member} created a new voice channel",
        )

        await self.bot.db.execute(
            """
            INSERT INTO voicemaster.channels (
                guild_id,
                channel_id,
                owner_id
            ) VALUES ($1, $2, $3)
            """,
            member.guild.id,
            channel.id,
            member.id,
        )

        if (
            role := member.guild.get_role(configuration.get("role_id"))
        ) and not role in member.roles:
            try:
                await member.add_roles(
                    role,
                    reason="VoiceMaster: Gave the owner the default role",
                )
            except Exception:
                pass

    @Cog.listener("on_voice_state_update")
    async def remove_channel(
        self, member: discord.Member, before: VoiceState, after: VoiceState
    ) -> None:
        if not before.channel:
            return

        elif after and before.channel == after.channel:
            return

        if (
            (
                role_id := await self.bot.db.fetchval(
                    """
                SELECT role_id FROM voicemaster.configuration
                WHERE guild_id = $1
                """,
                    member.guild.id,
                )
            )
            and role_id in (role.id for role in member.roles)
        ):
            try:
                await member.remove_roles(
                    member.guild.get_role(role_id),
                    reason="VoiceMaster: Removed the default role",
                )
            except Exception:
                pass

        if list(filter(lambda m: not m.bot, before.channel.members)):
            return

        elif not (
            owner_id := await self.bot.db.fetchval(
                """
                DELETE FROM voicemaster.channels
                WHERE channel_id = $1
                RETURNING owner_id
                """,
                before.channel.id,
            )
        ):
            return

        try:
            await before.channel.delete()
        except HTTPException:
            pass

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.command.qualified_name in (
            "voicemaster",
            "voicemaster setup",
            "voicemaster reset",
            "voicemaster category",
            "voicemaster defaultrole",
            "voicemaster defaultregion",
            "voicemaster defaultbitrate",
        ):
            return True

        if not ctx.author.voice:
            raise CommandError("You're not connected to a **voice channel**")

        elif not (
            owner_id := await ctx.bot.db.fetchval(
                """
            SELECT owner_id FROM voicemaster.channels
            WHERE channel_id = $1
            """,
                ctx.author.voice.channel.id,
            )
        ):
            raise CommandError("You're not in a **VoiceMaster** channel!")

        elif ctx.command.qualified_name == "voicemaster claim":
            if ctx.author.id == owner_id:
                raise CommandError(
                    "You already have **ownership** of this voice channel!"
                )

            elif owner_id in (member.id for member in ctx.author.voice.channel.members):
                raise CommandError(
                    "You can't claim this **voice channel**, the owner is still active here."
                )

            return True

        elif ctx.author.id != owner_id:
            raise CommandError("You don't own a **voice channel**!")

        return True

    @group(
        name="voicemaster",
        usage="(subcommand) <args>",
        example="setup",
        aliases=[
            "voice",
            "vm",
            "vc",
        ],
        invoke_without_command=True,
    )
    async def voicemaster(self, ctx: Context) -> Message:
        """
        Make temporary voice channels in your server!
        """

        return await ctx.send_help()

    @voicemaster.command(name="setup")
    @has_permissions(manage_guild=True)
    @cooldown(1, 30, BucketType.guild)
    async def voicemaster_setup(self, ctx: Context) -> Message:
        """
        Begin VoiceMaster server configuration setup
        """

        if await self.bot.db.fetchrow(
            """
            SELECT * FROM voicemaster.configuration
            WHERE guild_id = $1
            """,
            ctx.guild.id,
        ):
            return await ctx.warn(
                "Server is already configured for **VoiceMaster**, run `voicemaster reset` to reset the **VoiceMaster** server configuration"
            )

        category = await ctx.guild.create_category("Voice Channels")
        interface = await category.create_text_channel("interface")
        channel = await category.create_voice_channel("Join to Create")

        embed = Embed(
            color=config.Color.bleed,
            title="VoiceMaster Interface",
            description="Click the buttons below to control your voice channel",
        )
        embed.set_author(
            name=ctx.guild.name,
            icon_url=ctx.guild.icon,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar)

        embed.add_field(
            name="**Button Usage**",
            value=(
                f"{config.Emoji.Interface.lock} — [`Lock`]({config.support_server}) the voice channel\n"
                f"{config.Emoji.Interface.unlock} — [`Unlock`]({config.support_server}) the voice channel\n"
                f"{config.Emoji.Interface.ghost} — [`Ghost`]({config.support_server}) the voice channel\n"
                f"{config.Emoji.Interface.reveal} — [`Reveal`]({config.support_server}) the voice channel\n"
                f"{config.Emoji.Interface.claim} — [`Claim`]({config.support_server}) the voice channel\n"
                f"{config.Emoji.Interface.disconnect} — [`Disconnect`]({config.support_server}) a member\n"
                f"{config.Emoji.Interface.activity} — [`Start`]({config.support_server}) a new voice channel activity\n"
                f"{config.Emoji.Interface.information} — [`View`]({config.support_server}) channel information\n"
                f"{config.Emoji.Interface.increase} — [`Increase`]({config.support_server}) the user limit\n"
                f"{config.Emoji.Interface.decrease} — [`Decrease`]({config.support_server}) the user limit\n"
            ),
        )

        await interface.send(
            embed=embed,
            view=Interface(self.bot),
        )

        await self.bot.db.execute(
            """
            INSERT INTO voicemaster.configuration (
                guild_id,
                category_id,
                interface_id,
                channel_id
            ) VALUES ($1, $2, $3, $4)
            """,
            ctx.guild.id,
            category.id,
            interface.id,
            channel.id,
        )

        return await ctx.approve(
            "Finished setting up the **VoiceMaster** channels. A category and two channels have been created, you can move the channels or rename them if you want."
        )

    @voicemaster.command(name="reset", aliases=["resetserver"])
    @has_permissions(manage_guild=True)
    @cooldown(1, 60, BucketType.guild)
    async def voicemaster_reset(self, ctx: Context) -> Message:
        """
        Reset server configuration for VoiceMaster
        """

        if channel_ids := await self.bot.db.fetchrow(
            """
            DELETE FROM voicemaster.configuration
            WHERE guild_id = $1
            RETURNING category_id, interface_id, channel_id
            """,
            ctx.guild.id,
        ):
            for channel in (
                channel
                for channel_id in channel_ids
                if (channel := ctx.guild.get_channel(channel_id))
            ):
                await channel.delete()

            return await ctx.approve("Reset the **VoiceMaster** configuration")
        else:
            return await ctx.warn(
                "Server is not configured in the **database**, you need to run `voicemaster setup` to be able to run this command"
            )

    @voicemaster.command(
        name="category",
        usage="(channel)",
        example="Voice Channels",
    )
    @has_permissions(manage_guild=True)
    async def voicemaster_category(
        self, ctx: Context, *, channel: discord.CategoryChannel
    ) -> Message:
        """
        Redirect voice channels to custom category
        """

        try:
            await self.bot.db.execute(
                """
                UPDATE voicemaster.configuration
                SET category_id = $2
                WHERE guild_id = $1
                """,
                ctx.guild.id,
                channel.id,
            )
        except Exception:
            return await ctx.warn(
                "Server is not configured in the **database**, you need to run `voicemaster setup` to be able to run this command"
            )

        return await ctx.approve(
            f"Set **{channel}** as the default voice channel category"
        )

    @voicemaster.command(
        name="defaultrole",
        usage="(role)",
        example="@vc",
    )
    @has_permissions(manage_guild=True, manage_roles=True)
    async def voicemaster_defaultrole(self, ctx: Context, *, role: Role) -> Message:
        """
        Set a role that members get for being in a VM channel
        """

        try:
            await self.bot.db.execute(
                """
                UPDATE voicemaster.configuration
                SET role_id = $2
                WHERE guild_id = $1
                """,
                ctx.guild.id,
                role.id,
            )
        except Exception:
            return await ctx.warn(
                "Server is not configured in the **database**, you need to run `voicemaster setup` to be able to run this command"
            )

        return await ctx.approve(
            f"Set {role.mention} as the default role for members in voice channels"
        )

    @voicemaster.command(
        name="defaultregion",
        usage="(region)",
        example="russia",
    )
    @has_permissions(manage_guild=True)
    async def voicemaster_defaultregion(
        self, ctx: Context, *, region: Region
    ) -> Message:
        """
        Edit default region for new Voice Channels
        """

        try:
            await self.bot.db.execute(
                """
                UPDATE voicemaster.configuration
                SET region = $2
                WHERE guild_id = $1
                """,
                ctx.guild.id,
                region,
            )
        except Exception:
            return await ctx.warn(
                "Server is not configured in the **database**, you need to run `voicemaster setup` to be able to run this command"
            )

        return await ctx.approve(
            f"Set **{region}** as the default voice channel region"
        )

    @voicemaster.command(
        name="defaultbitrate",
        usage="(bitrate)",
        example="80kbps",
    )
    @has_permissions(manage_guild=True)
    async def voicemaster_defaultbitrate(
        self, ctx: Context, *, bitrate: Bitrate
    ) -> Message:
        """
        Edit default bitrate for new Voice Channels
        """

        try:
            await self.bot.db.execute(
                """
                UPDATE voicemaster.configuration
                SET bitrate = $2
                WHERE guild_id = $1
                """,
                ctx.guild.id,
                bitrate * 1000,
            )
        except Exception:
            return await ctx.warn(
                "Server is not configured in the **database**, you need to run `voicemaster setup` to be able to run this command"
            )

        return await ctx.approve(
            f"Set `{bitrate} kbps` as the default voice channel bitrate"
        )

    @voicemaster.command(
        name="configuration",
        aliases=[
            "config",
            "show",
            "view",
            "info",
        ],
    )
    async def voicemaster_configuration(self, ctx: Context) -> Message:
        """
        See current configuration for current voice channel
        """

        channel = ctx.author.voice.channel

        embed = Embed(
            color=config.Color.neutral,
            title=channel.name,
            description=(
                f"**Owner:** {ctx.author} (`{ctx.author.id}`)"
                + f"\n**Locked:** "
                + (
                    config.Emoji.approve
                    if channel.permissions_for(ctx.guild.default_role).connect is False
                    else config.Emoji.deny
                )
                + f"\n**Created:** "
                + format_dt(
                    channel.created_at,
                    style="R",
                )
                + f"\n**Bitrate:** {int(channel.bitrate / 1000)}kbps"
                + f"\n**Connected:** `{len(channel.members)}`"
                + (f"/`{channel.user_limit}`" if channel.user_limit else "")
            ),
        )

        if roles_permitted := (
            list(
                target
                for target, overwrite in channel.overwrites.items()
                if overwrite.connect is True and isinstance(target, discord.Role)
            )
        ):
            embed.add_field(
                name="Role Permitted",
                value=", ".join(role.mention for role in roles_permitted),
                inline=False,
            )

        if members_permitted := (
            list(
                target
                for target, overwrite in channel.overwrites.items()
                if overwrite.connect is True
                and isinstance(target, discord.Member)
                and target != ctx.author
            )
        ):
            embed.add_field(
                name="Member Permitted",
                value=", ".join(member.mention for member in members_permitted),
                inline=False,
            )

        return await ctx.send(embed=embed)

    @voicemaster.command(name="claim")
    async def voicemaster_claim(self, ctx: Context) -> Message:
        """
        Claim an inactive voice channel
        """

        await self.bot.db.execute(
            """
            UPDATE voicemaster.channels
            SET owner_id = $2
            WHERE channel_id = $1
            """,
            ctx.author.voice.channel.id,
            ctx.author.id,
        )

        if ctx.author.voice.channel.name.endswith("channel"):
            try:
                await ctx.author.voice.channel.edit(
                    name=f"{ctx.author.display_name}'s channel"
                )
            except Exception:
                pass

        return await ctx.approve("You are now the owner of this **channel**!")

    @voicemaster.command(
        name="transfer",
        usage="(member)",
        example="jonathan",
    )
    async def voicemaster_transfer(self, ctx: Context, *, member: Member) -> Message:
        """
        Transfer ownership of your channel to another member
        """

        if member == ctx.author or member.bot:
            return await ctx.send_help()

        elif not member.voice or member.voice.channel != ctx.author.voice.channel:
            return await ctx.warn(f"**{member}** is not in your channel!")

        await self.bot.db.execute(
            """
            UPDATE voicemaster.channels
            SET owner_id = $2
            WHERE channel_id = $1
            """,
            ctx.author.voice.channel.id,
            member.id,
        )

        if ctx.author.voice.channel.name.endswith("channel"):
            try:
                await ctx.author.voice.channel.edit(
                    name=f"{member.display_name}'s channel"
                )
            except Exception:
                pass

        return await ctx.approve(f"**{member}** now has ownership of this channel")

    @voicemaster.command(
        name="name",
        usage="(new name)",
        example="priv channel",
        aliases=["rename"],
    )
    async def voicemaster_name(self, ctx: Context, *, name: str) -> Message:
        """
        Rename your voice channel
        """

        if len(name) > 100:
            return await ctx.warn(
                "Your channel's name cannot be longer than **100 characters**"
            )

        try:
            await ctx.author.voice.channel.edit(
                name=name,
                reason=f"VoiceMaster: {ctx.author} renamed voice channel",
            )
        except HTTPException:
            return await ctx.warn("Voice channel name cannot contain **vulgar words**")
        except RateLimited:
            return await ctx.warn(
                "Voice channel is being **rate limited**, try again later"
            )
        else:
            return await ctx.approve(
                f"Your **voice channel** has been renamed to `{name}`"
            )

    @voicemaster.command(
        name="bitrate",
        usage="(bitrate)",
        example="80kbps",
        aliases=["quality"],
    )
    async def voicemaster_bitrate(self, ctx: Context, bitrate: Bitrate) -> Message:
        """
        Edit bitrate of your voice channel
        """

        await ctx.author.voice.channel.edit(
            bitrate=bitrate * 1000,
            reason=f"VoiceMaster: {ctx.author} edited voice channel bitrate",
        )

        return await ctx.approve(
            f"Your **voice channel**'s bitrate has been updated to `{bitrate} kbps`"
        )

    @voicemaster.command(
        name="limit",
        usage="(limit)",
        example="3",
        aliases=["userlimit"],
    )
    async def voicemaster_limit(self, ctx: Context, limit: int) -> Message:
        """
        Edit user limit of your voice channel
        """

        if limit < 0:
            return await ctx.warn(
                "Channel member limit must be greater than **0 members**"
            )

        elif limit > 99:
            return await ctx.warn(
                "Channel member limit cannot be more than **99 members**"
            )

        await ctx.author.voice.channel.edit(
            user_limit=limit,
            reason=f"VoiceMaster: {ctx.author} edited voice channel user limit",
        )

        return await ctx.approve(
            f"Your **voice channel**'s limit has been updated to `{limit}`"
        )

    @voicemaster.command(name="lock")
    async def voicemaster_lock(self, ctx: Context) -> Message:
        """
        Lock your voice channel
        """

        await ctx.author.voice.channel.set_permissions(
            ctx.guild.default_role,
            connect=False,
            reason=f"VoiceMaster: {ctx.author} locked voice channel",
        )

        return await ctx.warn(
            "Your **voice channel** has been locked",
            emoji=":lock:",
        )

    @voicemaster.command(name="unlock")
    async def voicemaster_unlock(self, ctx: Context) -> Message:
        """
        Unlock your voice channel
        """

        await ctx.author.voice.channel.set_permissions(
            ctx.guild.default_role,
            connect=None,
            reason=f"VoiceMaster: {ctx.author} unlocked voice channel",
        )

        return await ctx.warn(
            "Your **voice channel** has been unlocked",
            emoji=":unlock:",
        )

    @voicemaster.command(name="ghost", aliases=["hide"])
    async def voicemaster_ghost(self, ctx: Context) -> Message:
        """
        Hide your voice channel
        """

        await ctx.author.voice.channel.set_permissions(
            ctx.guild.default_role,
            view_channel=False,
            reason=f"VoiceMaster: {ctx.author} made voice channel hidden",
        )

        return await ctx.approve("Your **voice channel** has been hidden")

    @voicemaster.command(name="unghost", aliases=["reveal", "unhide"])
    async def voicemaster_unghost(self, ctx: Context) -> Message:
        """
        Reveal your voice channel
        """

        await ctx.author.voice.channel.set_permissions(
            ctx.guild.default_role,
            view_channel=None,
            reason=f"VoiceMaster: {ctx.author} revealed voice channel",
        )

        return await ctx.approve("Your **voice channel** has been revealed")

    @voicemaster.command(
        name="permit",
        usage="(member or role)",
        example="jonathan",
        aliases=["allow"],
    )
    async def voicemaster_permit(
        self, ctx: Context, *, target: Member | Role
    ) -> Message:
        """
        Permit a member or role to join your VC
        """

        await ctx.author.voice.channel.set_permissions(
            target,
            connect=True,
            view_channel=True,
            reason=f"VoiceMaster: {ctx.author} permitted {target} to join voice channel",
        )

        return await ctx.approve(
            f"Granted **connect permission** to {target.mention} to join"
        )

    @voicemaster.command(
        name="reject",
        usage="(member or role)",
        example="jonathan",
        aliases=[
            "remove",
            "deny",
            "kick",
        ],
    )
    async def voicemaster_reject(
        self, ctx: Context, *, target: Member | Role
    ) -> Message:
        """
        Reject a member or role from joining your VC
        """

        await ctx.author.voice.channel.set_permissions(
            target,
            connect=False,
            view_channel=None,
            reason=f"VoiceMaster: {ctx.author} rejected {target} from joining voice channel",
        )

        if isinstance(target, discord.Member):
            if (voice := target.voice) and voice.channel == ctx.author.voice.channel:
                await target.move_to(None)

        return await ctx.approve(
            f"Removed **connect permission** from {target.mention} to join"
        )
