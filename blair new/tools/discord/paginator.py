from asyncio import TimeoutError
from contextlib import suppress
from typing import TYPE_CHECKING, Dict, List, Optional

from discord import (
    Message,
    Reaction,
    TextChannel,
    User,
    Member,
    HTTPException,
    Embed,
)

if TYPE_CHECKING:
    from tools import Blair
    from tools.discord import Context


class Paginator(object):
    def __init__(self: "Paginator", ctx: "Context", data: List[Embed | str]) -> None:
        self.data: List[Embed | str] = data
        self.index: int = 0
        self.bot: "Blair" = ctx.bot
        self.author: Member = ctx.author
        self.channel: TextChannel = ctx.channel
        self.message: Optional[Message] = None
        self.reactions: Dict[str, str] = {
            "back": "⏪",
            "close": "⏹️",
            "next": "⏩",
            "navigate": "🔢",
        }

    async def display(self: "Paginator") -> Message:
        item = self.data[self.index]

        if not self.message:
            self.message = await self.channel.send(
                content=(isinstance(item, str) and item or None),
                embed=(isinstance(item, Embed) and item or None),
            )
        else:
            self.message = await self.message.edit(
                content=(isinstance(item, str) and item or None),
                embed=(isinstance(item, Embed) and item or None),
            )

    async def begin(self: "Paginator") -> Message:
        await self.display()
        if len(self.data) == 1:
            return self.message

        for emoji in self.reactions.values():
            await self.message.add_reaction(emoji)

        reaction: str
        while self.message:
            try:
                reaction = await self.wait_for()
            except TimeoutError:
                break

            if self.reactions["back"] == reaction:
                if self.index <= 0:
                    self.index = len(self.data) - 1
                else:
                    self.index -= 1

            elif self.reactions["next"] == reaction:
                if self.index >= len(self.data) - 1:
                    self.index = 0
                else:
                    self.index += 1

            elif self.reactions["navigate"] == reaction:
                embed = Embed(
                    color=0x2B2D31,
                    title="Page Navigator",
                    description="Reply to this message with the page you'd like to skip to!",
                )

                prompt = await self.channel.send(embed=embed)

                try:
                    response: Message = await self.bot.wait_for(
                        "message",
                        check=lambda m: (
                            m.content
                            and m.author.id == self.author.id
                            and m.channel.id == self.channel.id
                            and m.content.isdigit()
                            and int(m.content) <= len(self.data)
                        ),
                    )
                except TimeoutError:
                    with suppress(HTTPException):
                        await prompt.delete()

                    return self.message
                else:
                    with suppress(HTTPException):
                        await prompt.delete()
                        await response.delete()

                self.index = int(response.content) - 1

            else:
                break

            await self.display()

        with suppress(HTTPException):
            await self.message.clear_reactions()

        return self.message

    async def wait_for(self: "Paginator") -> str:
        reaction: Reaction
        member: Member | User

        while True:
            reaction, member = await self.bot.wait_for(
                "reaction_add",
                check=lambda reaction, member: (
                    str(reaction.emoji) in self.reactions.values()
                    and reaction.message == self.message
                ),
                timeout=60,
            )

            self.bot.ioloop.add_callback(
                self.message.remove_reaction,
                emoji=reaction,
                member=member,
            )

            if member == self.author:
                return str(reaction)
