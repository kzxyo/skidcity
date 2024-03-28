from contextlib import suppress

from discord import Embed, InteractionResponded, WebhookMessage
from discord.interactions import Interaction

async def neutral(
    self, value: str, **kwargs
) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            description=f"> " + value if not ">" in value else value,
        ),
        ephemeral=True,
        **kwargs,
    )


async def approve(
    self, value: str, **kwargs
) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            color=0x83FF4F,
            description=f"> " + value if not ">" in value else value,
        ),
        ephemeral=True,
        **kwargs,
    )


async def warn(
    self, value: str, **kwargs
) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            color=0xFFD04F,
            description=f"> " + value if not ">" in value else value,
        ),
        ephemeral=True,
        **kwargs,
    )

Interaction.neutral = neutral
Interaction.approve = approve
Interaction.warn = warn
