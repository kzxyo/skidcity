from discord import Embed
from discord import Message as MessageSuper
from discord.message import Message

import config


async def neutral(
    self, content: str, color: int = config.Color.neutral, emoji: str = "", **kwargs
) -> Message:
    return await self.channel.send(
        embed=Embed(
            color=color,
            description=f"{emoji} {self.author.mention}: {content}",
        ),
        **kwargs,
    )


MessageSuper.neutral = neutral
