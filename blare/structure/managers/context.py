from .paginator import Paginator
from .database import Record

from discord import Embed, Message
from discord.embeds import EmbedProxy
from discord.utils import as_chunks
from discord.ext.commands import Context as DefaultContext, MinimalHelpCommand


from typing import List, TYPE_CHECKING, Optional
from math import ceil

if TYPE_CHECKING:
    from structure.blare import Blare

class Context(DefaultContext):
    bot: "Blare"
    lastfm: Record

    async def send(self: "Context", *args, **kwargs) -> Message:
        embeds: List[Embed] = kwargs.get("embeds", [])
        if embed := kwargs.get("embed"):
            embeds.append(embed)

        for embed in embeds:
            self.style(embed)

        if patch := kwargs.pop("patch", None):
            kwargs.pop("reference", None)

            if args:
                kwargs["content"] = args[0]

            self.response = await patch.edit(**kwargs)
        else:
            self.response = await super().send(*args, **kwargs)

        return self.response
    
    async def confirm(
        self: "Context", 
        value: str, 
        *args, 
        **kwargs
    ) -> Message:
        embed = Embed(
            description=(f"> {self.author.mention}: " if not ">" in value else "") + value,
            color=0x83FF4F,
        )

        return await self.send(
            embed=embed,
            *args,
            **kwargs,
        )
    
    async def alert(
        self: "Context", 
        value: str, 
        *args, 
        **kwargs
    ) -> Message:
        embed = Embed(
            description=(f"> {self.author.mention}: " if not ">" in value else "") + value,
            color=0xFFD04F,
        )

        return await self.send(
            embed=embed,
            *args,
            **kwargs,
        )

    async def neutral(
        self: "Context", 
        value: str, 
        *args, 
        **kwargs
    ) -> Message:
        embed = Embed(
            description=(f"> {self.author.mention}: " if not ">" in value else "") + value,
            color=0x2B2D31,
        )

        return await self.send(
            embed=embed,
            *args,
            **kwargs,
        )

    async def paginate(
        self: "Context",
        data: List[Embed | EmbedProxy | str],
        embed: Optional[Embed] = None,
        max_results: int = 10,
        counter: bool = True,
    ) -> Message:
        compiled: List[Embed | str] = []

        # Initialize total line count
        total_lines = 0

        if isinstance(data[0], Embed):
            for index, page in enumerate(data):
                if not isinstance(page, Embed):
                    continue

                self.style(page)
                if len(data) > 1:
                    if footer := page.footer:
                        page.set_footer(
                            text=f"{footer.text} ∙ Page {index + 1} / {len(data)}",
                            icon_url=footer.icon_url,
                        )
                    else:
                        page.set_footer(
                            text=f"Page {index + 1} / {len(data)}",
                        )

                compiled.append(page)

        elif isinstance(data[0], str) and embed:
            pages = ceil(len(data) / max_results)
            self.style(embed)

            for chunk in as_chunks(data, max_results):
                page = embed.copy()
                page.description = f"{embed.description or ''}\n\n"

                for line_num, line in enumerate(chunk, start=1 + total_lines):
                    formatted_line_num = f"{line_num:02}"  # Add leading zero if necessary
                    page.description += (
                        f"`{formatted_line_num}` {line}\n" if counter else f"{line}\n"
                    )

                # Increment total lines by the number of lines in the current chunk
                total_lines += len(chunk)

                if pages > 1:
                    if footer := page.footer:
                        page.set_footer(
                            text=f"{footer.text} ∙ Page {len(compiled) + 1} / {pages}",
                            icon_url=footer.icon_url,
                        )
                    else:
                        page.set_footer(
                            text=f"Page {len(compiled) + 1} / {pages}",
                        )

                compiled.append(page)

        elif isinstance(data[0], str) and not embed:
            for index, page in enumerate(data):
                compiled.append(f"{index + 1}/{len(data)} {page}")

        paginator = Paginator(self, compiled)
        return await paginator.begin()
    
    def style(self: "Context", embed: Embed) -> Embed:
        if not embed.color:
            embed.color = 0x2B2D31

        return embed
    

class Help(MinimalHelpCommand):
    context: Context

    def __init__(self, **options):
        super().__init__(
            command_attrs={
                "aliases": [
                    "h",
                    "cmds"
               ],
               "hidden": True
            },
            **options,
        )
    
    async def send_pages(self) -> Message:
        return await self.context.paginate(
            [
                Embed(description=page)
                for page in self.paginator.pages
            ]
        )
