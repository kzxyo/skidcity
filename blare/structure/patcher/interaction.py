from discord import Embed, WebhookMessage, InteractionResponded
from discord.interactions import Interaction
from contextlib import suppress

async def neutral(
    self,
    value: str, 
    **kwargs
) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            description=(f"> {self.user.mention}: " if not ">" in value else "") + value,
            color=0x2B2D31,
        ),
        ephemeral=True,
        **kwargs,
    )


async def alert(
    self,
    value: str, 
    **kwargs
) -> WebhookMessage:
    with suppress(InteractionResponded):
        await self.response.defer(
            ephemeral=True,
        )

    return await self.followup.send(
        embed=Embed(
            description=(f"> {self.user.mention}: " if not ">" in value else "") + value,
            color=0xFFD04F,
        ),
        ephemeral=True,
        **kwargs,
    )


Interaction.neutral = neutral
Interaction.alert = alert