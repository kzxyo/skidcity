from discord import Embed, Message
from discord.channel import TextChannel

import config


async def neutral(
    self, content: str, color: int = config.Color.neutral, emoji: str = "", **kwargs
) -> Message:
    return await self.send(
        embed=Embed(
            color=color,
            description=f"{emoji} {content}",
        ),
        **kwargs,
    )


async def approve(
    self, content: str, emoji: str = config.Emoji.approve, **kwargs
) -> Message:
    return await self.send(
        embed=Embed(
            color=config.Color.approve,
            description=f"{emoji} {content}",
        ),
        **kwargs,
    )


async def warn(self, content: str, emoji: str = config.Emoji.warn, **kwargs) -> Message:
    return await self.send(
        embed=Embed(
            color=config.Color.warn,
            description=f"{emoji} {content}",
        ),
        **kwargs,
    )


async def deny(self, content: str, emoji: str = config.Emoji.deny, **kwargs) -> Message:
    return await self.send(
        embed=Embed(
            color=config.Color.deny,
            description=f"{emoji} {content}",
        ),
        **kwargs,
    )


TextChannel.neutral = neutral
TextChannel.approve = approve
TextChannel.warn = warn
TextChannel.deny = deny
