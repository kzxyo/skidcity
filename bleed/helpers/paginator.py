from asyncio import TimeoutError
from contextlib import suppress

from discord import ButtonStyle, Embed, HTTPException, Interaction, Message
from discord.ext.commands import Context
from discord.ui import Button, View

import config


class PaginatorButton(Button):
    def __init__(self, emoji: str, style: ButtonStyle) -> None:
        super().__init__(
            emoji=emoji,
            style=style,
            custom_id=emoji,
        )
        self.disabled: bool = False

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        if self.custom_id == config.Emoji.Paginator.previous:
            if self.view.current_page <= 0:
                self.view.current_page = len(self.view.pages) - 1
            else:
                self.view.current_page -= 1

        elif self.custom_id == config.Emoji.Paginator.next:
            if self.view.current_page >= len(self.view.pages) - 1:
                self.view.current_page = 0
            else:
                self.view.current_page += 1

        elif self.custom_id == config.Emoji.Paginator.navigate:
            for child in self.view.children:
                child.disabled = True

            await self.view.message.edit(view=self.view)
            prompt = await interaction.neutral(
                "What **page** would you like to skip to?",
                emoji="🔢",
            )

            try:
                response = await self.view.ctx.bot.wait_for(
                    "message",
                    timeout=6,
                    check=lambda m: m.author.id == interaction.user.id
                    and m.channel.id == interaction.channel.id
                    and m.content
                    and m.content.isdigit()
                    and int(m.content) <= len(self.view.pages),
                )
            except TimeoutError:
                for child in self.view.children:
                    child.disabled = False

                await self.view.message.edit(view=self.view)
                await prompt.delete()
                return
            else:
                self.view.current_page = int(response.content) - 1
                for child in self.view.children:
                    child.disabled = False

                with suppress(HTTPException):
                    await prompt.delete()
                    await response.delete()

        elif self.custom_id == config.Emoji.Paginator.cancel:
            with suppress(HTTPException):
                await self.view.message.delete()

            return

        page = self.view.pages[self.view.current_page]
        if self.view.type == "embed":
            await self.view.message.edit(embed=page, view=self.view)
        else:
            await self.view.message.edit(content=page, view=self.view)


class Paginator(View):
    def __init__(self, ctx: Context, pages: list[Embed | str]) -> None:
        super().__init__()
        self.ctx: Context = ctx
        self.current_page: int = 0
        self.pages: list[Embed | str] = pages
        self.message: Message
        self.add_initial_buttons()

    def add_initial_buttons(self) -> "Paginator":
        for button in (
            PaginatorButton(
                emoji=config.Emoji.Paginator.previous,
                style=ButtonStyle.blurple,
            ),
            PaginatorButton(
                emoji=config.Emoji.Paginator.next,
                style=ButtonStyle.blurple,
            ),
            PaginatorButton(
                emoji=config.Emoji.Paginator.navigate,
                style=ButtonStyle.grey,
            ),
            PaginatorButton(
                emoji=config.Emoji.Paginator.cancel,
                style=ButtonStyle.red,
            ),
        ):
            self.add_item(button)

        return self

    @property
    def type(self) -> str:
        return "embed" if isinstance(self.pages[0], Embed) else "text"

    async def send(self, content: str | Embed, **kwargs) -> Message:
        if self.type == "embed":
            return await self.ctx.send(embed=content, **kwargs)
        else:
            return await self.ctx.send(content=content, **kwargs)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.warn("You're not the **author** of this embed!")
            return False

        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)

    async def start(self) -> Message:
        if len(self.pages) == 1:
            self.message = await self.send(self.pages[0])
        else:
            self.message = await self.send(self.pages[self.current_page], view=self)

        return self.message
