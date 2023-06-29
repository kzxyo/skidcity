import asyncio
import contextlib

from typing import List

import discord

from discord.ext import commands
from discord.ui import Button, View


class Paginator(View):
    """The main pagination class for the buttons"""

    def __init__(
        self,
        ctx: commands.Context,
        embeds: List[discord.Embed],
        timeout: float = 60.0,
    ):
        super().__init__(timeout=timeout)
        self.ctx: commands.Context = ctx
        self.bot: commands.Bot = ctx.bot
        self.embeds: List[discord.Embed] = embeds
        self.current_page: int = 0
        self.message: discord.Message | None = None
        self.timeout: float = timeout
        self.add_initial_buttons()

    def add_initial_buttons(self):
        """Add the buttons to the pagination view"""

        for button in (
            PaginatorButton(
                emoji=self.bot.config["styles"]["paginator"].get("previous"),
                style=discord.ButtonStyle.blurple,
                custom_id="previous",
            ),
            PaginatorButton(
                emoji=self.bot.config["styles"]["paginator"].get("next"),
                style=discord.ButtonStyle.blurple,
                custom_id="next",
            ),
            PaginatorButton(
                emoji=self.bot.config["styles"]["paginator"].get("skip"),
                style=discord.ButtonStyle.gray,
                custom_id="skip",
            ),
            PaginatorButton(
                emoji=self.bot.config["styles"]["paginator"].get("stop"),
                style=discord.ButtonStyle.red,
                custom_id="stop",
            ),
        ):
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction):
        """Check if the user is the author of the command"""

        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.warn(
                "You aren't the **author** of this embed",
                followup=False,
            )
            return False

    async def on_timeout(self):
        """Called when the view times out"""

        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(embed=self.embeds[self.current_page], view=None)

    async def on_error(self, error, item, interaction):
        """Called when an error occurs"""

        print(f"Error in {self.__class__.__name__}: {error} (item: {item}, interaction: {interaction})")

    async def execute(self):
        """Execute the pagination"""

        self.message = await self.ctx.send(embed=self.embeds[0], view=self)


class PaginatorButton(Button):
    """The button class for the pagination view"""

    def __init__(self, emoji: str, style: discord.ButtonStyle, custom_id: str):
        super().__init__(emoji=emoji, style=style, custom_id=custom_id)
        self.disabled: bool = False

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.custom_id == "previous":
            if self.view.current_page <= 0:
                self.view.current_page = len(self.view.embeds) - 1
            else:
                self.view.current_page -= 1
        elif self.custom_id == "next":
            if self.view.current_page >= len(self.view.embeds) - 1:
                self.view.current_page = 0
            else:
                self.view.current_page += 1
        elif self.custom_id == "skip":
            for child in self.view.children:
                child.disabled = True

            await self.view.message.edit(view=self.view)

            _message = await interaction.neutral("What **page** would you like to skip to?", emoji="🔢")
            try:
                response = await self.view.bot.wait_for(
                    "message",
                    timeout=6,
                    check=lambda m: m.author.id == interaction.user.id
                    and m.channel.id == interaction.channel.id
                    and m.content
                    and m.content.isdigit()
                    and int(m.content) <= len(self.view.embeds),
                )
            except asyncio.TimeoutError:
                for child in self.view.children:
                    child.disabled = False
                await self.view.message.edit(view=self.view)
                await _message.delete()
                return
            else:
                self.view.current_page = int(response.content) - 1
                for child in self.view.children:
                    child.disabled = False
                await self.view.message.edit(embed=self.view.embeds[self.view.current_page], view=self.view)
                with contextlib.suppress(discord.HTTPException):
                    await _message.delete()
                    await response.delete()

        elif self.custom_id == "stop":
            with contextlib.suppress(discord.HTTPException):
                await self.view.message.delete()
                await self.view.ctx.message.delete()
                self.view.stop()
            return

        await self.view.message.edit(embed=self.view.embeds[self.view.current_page])
