from discord import Embed, Message
from discord.channel import TextChannel

import config


async def neutral(self, content: str, color: int = config.Colors.neutral, emoji: str = "", **kwargs) -> Message:
    return await self.send(
        embed=Embed(
            color=color,
            description=f"{emoji} {content}",
        ),
        **kwargs,
    )


async def approve(self, content: str, emoji: str = config.Emojis.approve, **kwargs) -> Message:
    return await self.send(
        embed=Embed(
            color=config.Colors.approve,
            description=f"{emoji} {content}",
        ),
        **kwargs,
    )


async def warn(self, content: str, emoji: str = config.Emojis.warn, **kwargs) -> Message:
    return await self.send(
        embed=Embed(
            color=config.Colors.warn,
            description=f"{emoji} {content}",
        ),
        **kwargs,
    )


async def deny(self, content: str, emoji: str = config.Emojis.deny, **kwargs) -> Message:
    return await self.send(
        embed=Embed(
            color=config.Colors.deny,
            description=f"{emoji} {content}",
        ),
        **kwargs,
    )


TextChannel.neutral = neutral
TextChannel.approve = approve
TextChannel.warn = warn
TextChannel.deny = deny