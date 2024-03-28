from .paginator import Paginator

from discord import Embed, Message
from discord.utils import as_chunks
from discord.embeds import EmbedProxy
from discord.ext.commands import Context as DefaultContext, MinimalHelpCommand, Command

from typing import List, TYPE_CHECKING, Any, Callable, Optional
from math import ceil
if TYPE_CHECKING:
    from puke import Puke

class Context(DefaultContext):
    bot: "Puke"
    
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

    async def neutral(
        self: "Context", 
        value: str, 
        color: int = 0x2B2D31, 
        **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=color,
                description=f"> " + value if not ">" in value else value,
            ),
            **kwargs,
        )

    async def approve(
        self: "Context", 
        value: str, 
        **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=0x83FF4F,
                description=f"> " + value if not ">" in value else value,
            ),
            **kwargs,
        )

    async def warn(
        self: "Context", 
        value: str, 
        **kwargs
    ) -> Message:
        return await self.send(
            embed=Embed(
                color=0xFFD04F,
                description=f"> " + value if not ">" in value else value,
            ),
            **kwargs,
        )

    async def paginate(
        self: "Context",
        data: List[Embed | EmbedProxy | str],
        embed: Optional[Embed] = None,
        max_results: int = 10,
        counter: bool = True,
    ) -> Message: # NOT MY PAGINATOR :p
        compiled: List[Embed | str] = []

        if isinstance(data[0], Embed):
            for index, page in enumerate(data):
                if not isinstance(page, Embed):
                    continue

                self.style(page)
                if len(data) > 1:
                    if footer := page.footer:
                        page.set_footer(
                            text=f"{footer.text} ∙ Page {index + 1} of {len(data)}",
                            icon_url=footer.icon_url,
                        )
                    else:
                        page.set_footer(
                            text=f"Page {index + 1} of {len(data)}",
                        )

                compiled.append(page)

        elif isinstance(data[0], str) and embed:
            lines = 0
            pages = ceil(len(data) / max_results)
            self.style(embed)

            for chunk in as_chunks(data, max_results):
                page = embed.copy()
                page.description = f"{embed.description or ''}\n\n"

                for line in chunk:
                    lines += 1
                    page.description += (
                        f"`{lines}` {line}\n" if counter else f"{line}\n"
                    )

                if pages > 1:
                    if footer := page.footer:
                        page.set_footer(
                            text=f"{footer.text} ∙ Page {len(compiled) + 1} of {pages}",
                            icon_url=footer.icon_url,
                        )
                    else:
                        page.set_footer(
                            text=f"Page {len(compiled) + 1} of {pages}",
                        )

                compiled.append(page)

        elif isinstance(data[0], str) and not embed:
            for index, page in enumerate(data):
                compiled.append(f"{index + 1}/{len(data)} {page}")

        paginator = Paginator(self, compiled)
        return await paginator.start()

    
    def style(self, embed: Embed) -> Embed:
        if not embed.color:
            embed.color = 0x2B2D31

        return embed
    
class Help(MinimalHelpCommand):
    context: Context

    def __init__(self: "Help", **options):
        super().__init__(
            command_attrs={
                "hidden": True,
                "aliases": ["h"],
            },
            **options,
        )

    def add_command_formatting(self, command: Command[Any, Callable[..., Any], Any]):
        super().add_command_formatting(command)


    def command_not_found(self, string: str) -> str:
        return f"The command `{string}` does not exist!"

    async def send_error_message(self, error: str) -> Message:
        return await self.context.warn(error)


    async def send_pages(self) -> Message:
        pages = [Embed(description=page) for page in self.paginator.pages]
        return await self.context.paginate(pages)
