import config
import discord
from discord import Message, Embed, Color
from discord.ext import commands
from discord.utils import as_chunks
from helpers.utilities import plural, shorten

from helpers.utilities.paginator import Paginator

class Context(commands.Context):
    @discord.utils.cached_property
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

        return await super().send(*args, **kwargs)

    async def neutral(
        self,
        content: str,
        color: int = config.Colors.neutral,
        emoji: str = "",
        **kwargs,
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=color,
                description=f"{content}",
            ),
            **kwargs,
        )

    async def approve(self, content: str, emoji: str = "", **kwargs) -> Message:
        return await self.send(
            embed=Embed(
                color=config.Colors.neutral,
                description=f"{content}",
            ),
            **kwargs,
        )

    async def warn(
        self, content: str, emoji: str = config.Emojis.warn, **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=config.Colors.warn,
                description=f"{content}",
            ),
            **kwargs,
        )

    async def deny(
        self, content: str, emoji: str = config.Emojis.deny, **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=config.Colors.deny,
                description=f"{content}",
            ),
            **kwargs,
        )

    async def paginate(
        self,
        data: Embed | list[Embed | str],
        chunk_after: int = 10,
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
                        _chunk.append(f"`{entries}` {entry}")

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
            for page, embed in enumerate(data):
                await self.style_embed(embed)
                if footer := embed.footer:
                    embed.set_footer(
                        text=(
                            f"Page {page + 1}/{len(data):,} "
                            + (
                                f"({plural(entries):{text}:,})"
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
                else config.Colors.neutral
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
