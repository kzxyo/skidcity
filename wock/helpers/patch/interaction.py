import config
from discord import InteractionResponded, WebhookMessage, Embed
from discord.interactions import Interaction
from contextlib import suppress


async def neutral(
    self, content: str, color: int = config.Colors.neutral, emoji: str = ""
) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            color=color,
            description=f"{emoji} {self.user.mention}: {content}",
        ),
        ephemeral=True,
    )


async def approve(
    self, content: str, emoji: str = config.Emojis.approve
) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            color=config.Colors.neutral,
            description=f"{emoji} {self.user.mention}: {content}",
        ),
        ephemeral=True,
    )


async def warn(self, content: str, emoji: str = config.Emojis.warn) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            color=config.Colors.neutral,
            description=f"{emoji} {self.user.mention}: {content}",
        ),
        ephemeral=True,
    )


async def deny(self, content: str, emoji: str = config.Emojis.deny) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            color=config.Colors.neutral,
            description=f"{emoji} {self.user.mention}: {content}",
        ),
        ephemeral=True,
    )


Interaction.neutral = neutral
Interaction.approve = approve
Interaction.warn = warn
Interaction.deny = deny
