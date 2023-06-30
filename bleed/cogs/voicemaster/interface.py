from contextlib import suppress

from discord import (
    Embed,
    Guild,
    Interaction,
    InteractionResponded,
    InviteTarget,
    Member,
    Role,
    SelectOption,
    VoiceChannel,
    WebhookMessage,
)
from discord.ui import Button, Select, View, button
from discord.utils import format_dt

import config

from helpers.bleed import Bleed
from helpers.utilities import plural
from helpers.variables import activity_types


class DisconnectMembers(Select):
    def __init__(self, member: Member) -> None:
        self.member: Member = member
        self.guild: Guild = member.guild
        self.channel: VoiceChannel = member.voice.channel
        super().__init__(
            placeholder="Choose members...",
            min_values=1,
            max_values=len(self.channel.members),
            options=[
                SelectOption(
                    value=member.id,
                    label=f"{member} ({member.id})",
                    emoji="👤",
                )
                for member in self.channel.members
            ],
        )

    async def callback(self, interaction: Interaction) -> WebhookMessage:
        await interaction.response.defer()

        disconnected, failed = 0, 0

        for member_id in self.values:
            if member := self.guild.get_member(int(member_id)):
                if member == self.member:
                    failed += 1
                elif not member.voice or member.voice.channel != self.channel:
                    failed += 1
                else:
                    try:
                        await member.move_to(None)
                    except:
                        failed += 1
                    else:
                        disconnected += 1

        return await interaction.approve(
            f"Successfully **disconnected** {plural(disconnected, code=True):member} (`{failed}` failed)"
        )


class ActivitySelection(Select):
    def __init__(self, member: Member) -> None:
        self.member: Member = member
        self.guild: Guild = member.guild
        self.channel: VoiceChannel = member.voice.channel
        super().__init__(
            placeholder="Choose an activity...",
            min_values=1,
            max_values=1,
            options=[
                SelectOption(
                    value=activity["id"],
                    label=activity["name"],
                    emoji=activity["emoji"],
                )
                for activity in activity_types
            ],
        )

    async def callback(self, interaction: Interaction) -> WebhookMessage:
        await interaction.response.defer()

        try:
            invite = await self.channel.create_invite(
                max_age=0,
                target_type=InviteTarget.embedded_application,
                target_application_id=int(self.values[0]),
                reason=f"VoiceMaster: {self.member} started an activity",
            )
        except Exception:
            return await interaction.warn(
                "Failed to create an **invite** for the selected **activity**!"
            )

        return await interaction.followup.send(
            f"[Click here to join the activity!]({invite})",
            ephemeral=True,
        )


class Interface(View):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot
        super().__init__(
            timeout=None,
        )

    async def interaction_check(self, interaction: Interaction) -> bool:
        if not interaction.user.voice:
            await interaction.warn("You're not connected to a **voice channel**")
            return False

        elif not (
            owner_id := await self.bot.db.fetchval(
                """
            SELECT owner_id FROM voicemaster.channels
            WHERE channel_id = $1
            """,
                interaction.user.voice.channel.id,
            )
        ):
            await interaction.warn("You're not in a **VoiceMaster** channel!")
            return False

        elif interaction.data["custom_id"] == "voicemaster:claim":
            if interaction.user.id == owner_id:
                await interaction.warn(
                    "You already have **ownership** of this voice channel!"
                )
                return False

            elif owner_id in (
                member.id for member in interaction.user.voice.channel.members
            ):
                await interaction.warn(
                    "You can't claim this **voice channel**, the owner is still active here."
                )
                return False

            return True

        elif interaction.user.id != owner_id:
            await interaction.warn("You don't own a **voice channel**!")
            return False

        return True

    @button(
        emoji=config.Emoji.Interface.lock,
        custom_id="voicemaster:lock",
    )
    async def lock(self, interaction: Interaction, button: Button) -> WebhookMessage:
        """
        Lock your voice channel
        """

        await interaction.user.voice.channel.set_permissions(
            interaction.guild.default_role,
            connect=False,
            reason=f"VoiceMaster: {interaction.user} locked voice channel",
        )

        return await interaction.warn(
            "Your **voice channel** has been locked",
            emoji=":lock:",
        )

    @button(
        emoji=config.Emoji.Interface.unlock,
        custom_id="voicemaster:unlock",
    )
    async def unlock(self, interaction: Interaction, button: Button) -> WebhookMessage:
        """
        Unlock your voice channel
        """

        await interaction.user.voice.channel.set_permissions(
            interaction.guild.default_role,
            connect=None,
            reason=f"VoiceMaster: {interaction.user} unlocked voice channel",
        )

        return await interaction.warn(
            "Your **voice channel** has been unlocked",
            emoji=":unlock:",
        )

    @button(
        emoji=config.Emoji.Interface.ghost,
        custom_id="voicemaster:ghost",
    )
    async def ghost(self, interaction: Interaction, button: Button) -> WebhookMessage:
        """
        Hide your voice channel
        """

        await interaction.user.voice.channel.set_permissions(
            interaction.guild.default_role,
            view_channel=False,
            reason=f"VoiceMaster: {interaction.user} made voice channel hidden",
        )

        return await interaction.approve("Your **voice channel** has been hidden")

    @button(
        emoji=config.Emoji.Interface.reveal,
        custom_id="voicemaster:reveal",
    )
    async def reveal(self, interaction: Interaction, button: Button) -> WebhookMessage:
        """
        Reveal your voice channel
        """

        await interaction.user.voice.channel.set_permissions(
            interaction.guild.default_role,
            view_channel=None,
            reason=f"VoiceMaster: {interaction.user} revealed voice channel",
        )

        return await interaction.approve("Your **voice channel** has been revealed")

    @button(
        emoji=config.Emoji.Interface.claim,
        custom_id="voicemaster:claim",
    )
    async def claim(self, interaction: Interaction, button: Button) -> WebhookMessage:
        """
        Claim an inactive voice channel
        """

        await self.bot.db.execute(
            """
            UPDATE voicemaster.channels
            SET owner_id = $2
            WHERE channel_id = $1
            """,
            interaction.user.voice.channel.id,
            interaction.user.id,
        )

        if interaction.user.voice.channel.name.endswith("channel"):
            try:
                await interaction.user.voice.channel.edit(
                    name=f"{interaction.user.display_name}'s channel"
                )
            except Exception:
                pass

        return await interaction.approve("You are now the owner of this **channel**!")

    @button(
        emoji=config.Emoji.Interface.disconnect,
        custom_id="voicemaster:disconnect",
    )
    async def disconnect(
        self, interaction: Interaction, button: Button
    ) -> WebhookMessage:
        """
        Reject a member or role from joining your VC
        """

        view = View(timeout=None)
        view.add_item(DisconnectMembers(interaction.user))

        return await interaction.neutral(
            "Select members from the **dropdown** to disconnect.",
            emoji="🔨",
            view=view,
        )

    @button(
        emoji=config.Emoji.Interface.activity,
        custom_id="voicemaster:activity",
    )
    async def activity(self, interaction: Interaction, button: Button) -> None:
        """
        Start an activity in your voice channel
        """

        view = View(timeout=None)
        view.add_item(ActivitySelection(interaction.user))

        return await interaction.neutral(
            "Select an activity from the **dropdown** to start!",
            emoji=config.Emoji.Interface.activity,
            view=view,
        )

    @button(
        emoji=config.Emoji.Interface.information,
        custom_id="voicemaster:information",
    )
    async def information(
        self, interaction: Interaction, button: Button
    ) -> WebhookMessage:
        """
        See current configuration for current voice channel
        """

        with suppress(InteractionResponded):
            await interaction.response.defer(
                ephemeral=True,
            )

        channel = interaction.user.voice.channel

        embed = Embed(
            color=config.Color.neutral,
            title=channel.name,
            description=(
                f"**Owner:** {interaction.user} (`{interaction.user.id}`)"
                + f"\n**Locked:** "
                + (
                    config.Emoji.approve
                    if channel.permissions_for(interaction.guild.default_role).connect
                    is False
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
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar,
        )

        if roles_permitted := (
            list(
                target
                for target, overwrite in channel.overwrites.items()
                if overwrite.connect is True and isinstance(target, Role)
            )
        ):
            embed.add_field(
                name="**Role Permitted**",
                value=", ".join(role.mention for role in roles_permitted),
                inline=False,
            )

        if members_permitted := (
            list(
                target
                for target, overwrite in channel.overwrites.items()
                if overwrite.connect is True
                and isinstance(target, Member)
                and target != interaction.user
            )
        ):
            embed.add_field(
                name="**Member Permitted**",
                value=", ".join(member.mention for member in members_permitted),
                inline=False,
            )

        return await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )

    @button(
        emoji=config.Emoji.Interface.increase,
        custom_id="voicemaster:increase",
    )
    async def increase(
        self, interaction: Interaction, button: Button
    ) -> WebhookMessage:
        """
        Increase the user limit of your voice channel
        """

        limit = interaction.user.voice.channel.user_limit or 0

        if limit == 99:
            return await interaction.warn(
                "Channel member limit cannot be more than **99 members**!"
            )

        await interaction.user.voice.channel.edit(
            user_limit=limit + 1,
            reason=f"VoiceMaster: {interaction.user} increased voice channel user limit",
        )

        return await interaction.approve(
            f"Your **voice channel**'s limit has been updated to `{limit + 1}`"
        )

    @button(
        emoji=config.Emoji.Interface.decrease,
        custom_id="voicemaster:decrease",
    )
    async def decrease(
        self, interaction: Interaction, button: Button
    ) -> WebhookMessage:
        """
        Decrease the user limit of your voice channel
        """

        limit = interaction.user.voice.channel.user_limit or 0

        if limit == 0:
            return await interaction.warn(
                "Channel member limit must be greater than **0 members**"
            )

        await interaction.user.voice.channel.edit(
            user_limit=limit - 1,
            reason=f"VoiceMaster: {interaction.user} decreased voice channel user limit",
        )

        return await interaction.approve(
            f"Your **voice channel**'s limit has been **removed**"
            if (limit - 1) == 0
            else f"Your **voice channel**'s limit has been updated to `{limit - 1}`"
        )
