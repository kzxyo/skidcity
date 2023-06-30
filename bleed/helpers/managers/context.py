from typing import Any, Dict

from discord import Color, Embed, Message
from discord.ext import commands
from discord.utils import as_chunks, cached_property

import config

from helpers.paginator import Paginator
from helpers.utilities import plural, shorten


class Context(commands.Context):
    flags: Dict[str, Any] = {}

    @cached_property
    def replied_message(self) -> Message:
        if (reference := self.message.reference) and isinstance(
            reference.resolved, Message
        ):
            return reference.resolved

    async def send(self, *args, **kwargs) -> Message:
        if embed := kwargs.get("embed"):
            await self.style_embed(embed)

        elif embeds := kwargs.get("embeds"):
            for embed in embeds:
                await self.style_embed(embed)

        if previous_message := kwargs.pop("previous_message", None):
            return await previous_message.edit(*args, **kwargs)

        return await super().send(*args, **kwargs)

    async def neutral(
        self, content: str, color: int = config.Color.neutral, emoji: str = "", **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=color,
                description=f"{emoji} {self.author.mention}: {content}",
            ),
            **kwargs,
        )

    async def search(
        self, content: str, color: int = config.Color.search, emoji: str = "🔎", **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=color,
                description=f"{emoji} {self.author.mention}: {content}",
            ),
            **kwargs,
        )

    async def approve(
        self, content: str, emoji: str = config.Emoji.approve, **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=config.Color.approve,
                description=f"{emoji} {self.author.mention}: {content}",
            ),
            **kwargs,
        )

    async def warn(
        self, content: str, emoji: str = config.Emoji.warn, **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=config.Color.warn,
                description=f"{emoji} {self.author.mention}: {content}",
            ),
            **kwargs,
        )

    async def deny(
        self, content: str, emoji: str = config.Emoji.deny, **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=config.Color.deny,
                description=f"{emoji} {self.author.mention}: {content}",
            ),
            **kwargs,
        )

    async def paginate(
        self,
        data: Embed | list[Embed | str],
        chunk_after: int = 10,
        entry_difference: int = 0,
        display_entries: bool = True,
        text: str = "entry|entries",
        of_text: str = None,
    ) -> Message:
        if isinstance(data, Embed):
            entries: int = 0
            temp_data: list[Embed] = []
            embed: Embed = data.copy()
            if description := data.description:
                for chunk in as_chunks(description, chunk_after):
                    _chunk = list()
                    for entry in chunk:
                        entries += 1
                        _chunk.append(
                            (f"`{entries}` " if display_entries else "") + entry
                        )

                    embed.description = "\n".join(_chunk)
                    temp_data.append(embed.copy())
            elif fields := data._fields:
                for chunk in as_chunks(fields, chunk_after):
                    embed._fields = list()
                    for field in chunk:
                        entries += 1
                        embed.add_field(**field)

                    temp_data.append(embed.copy())

            data = temp_data
        else:
            entries = len(data)

        if isinstance(data[0], Embed):
            if entry_difference:
                entries -= entry_difference

            for page, embed in enumerate(data):
                await self.style_embed(embed)
                if footer := embed.footer:
                    embed.set_footer(
                        text=(
                            f"Page {page + 1}/{len(data)} "
                            + (
                                f"({plural(entries):{text}})"
                                if of_text is None
                                else f"of {of_text}"
                            )
                            + (f" ∙ {footer.text}" if footer.text else "")
                        ),
                        icon_url=footer.icon_url,
                    )
                else:
                    embed.set_footer(
                        text=(
                            f"Page {page + 1}/{len(data)} "
                            + (
                                f"({plural(entries):{text}})"
                                if of_text is None
                                else f"of {of_text}"
                            )
                            + (f" ∙ {footer.text}" if footer.text else "")
                        ),
                    )

        paginator = Paginator(self, data)
        return await paginator.start()

    async def style_embed(self, embed: Embed) -> Embed:
        if not embed.color:
            embed.color = (
                self.author.color
                if (self.author.color != Color.default()) and embed.title
                else config.Color.info
            )

        if not embed.author and embed.title:
            embed.set_author(
                name=self.author.display_name,
                icon_url=self.author.display_avatar,
            )

        if embed.title:
            embed.title = shorten(embed.title, 256)

        if embed.description:
            embed.description = shorten(embed.description, 4096)

        for field in embed.fields:
            embed.set_field_at(
                index=embed.fields.index(field),
                name="**" + field.name + "**",
                value=shorten(field.value, 1024),
                inline=field.inline,
            )

        return embed

    async def send_help(self) -> Message:
        return await self.send(
            embed=Embed(
                color=config.Color.info,
                title="Command: " + self.command.qualified_name,
                description=(
                    (self.command.short_doc or "")
                    + f"```\nSyntax: {self.prefix}{self.command.qualified_name} {self.command.usage or ''}"
                    + (
                        f"\nExample: {self.prefix}{self.command.qualified_name} {self.command.example}"
                        if self.command.example
                        else ""
                    )
                    + "```"
                ),
            ).set_author(
                name="bleed help",
                icon_url=self.bot.user.avatar,
            )
        )
