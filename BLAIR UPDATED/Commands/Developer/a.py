# -*- coding: utf-8 -*-

"""
jishaku.paginators
~~~~~~~~~~~~~~~~~~

Paginator-related tools and interfaces for Jishaku.

:copyright: (c) 2021 Devon (Gorialis) R
:license: MIT, see LICENSE for more details.

"""

from __future__ import annotations

import asyncio
import typing

import discord
from discord import ui
from discord.ext import commands

from jishaku.flags import Flags
from jishaku.hljs import get_language, guess_file_traits
from jishaku.types import BotT, ContextA

__all__ = ('EmojiSettings', 'PaginatorInterface', 'PaginatorEmbedInterface',
           'WrappedPaginator', 'FilePaginator', 'use_file_check')


class WrappedPaginator(commands.Paginator):
    def __init__(
        self,
        *args: typing.Any,
        wrap_on: typing.Tuple[str, ...] = ('\n', ' '),
        include_wrapped: bool = True,
        force_wrap: bool = False,
        **kwargs: typing.Any
    ):
        super().__init__(*args, **kwargs)
        self.wrap_on = wrap_on
        self.include_wrapped = include_wrapped
        self.force_wrap = force_wrap

    def add_line(self, line: str = '', *, empty: bool = False):
        true_max_size = self.max_size - self._prefix_len - self._suffix_len - 2 * self._linesep_len
        start = 0
        needle = 0
        last_delimiter = -1
        last_space = -1

        while needle < len(line):
            if needle - start >= true_max_size:
                if last_delimiter != -1:
                    if self.include_wrapped and line[last_delimiter] != '\n':
                        super().add_line(line[start:last_delimiter + 1])
                        needle = last_delimiter + 1
                        start = last_delimiter + 1
                    else:
                        super().add_line(line[start:last_delimiter])
                        needle = last_delimiter + 1
                        start = last_delimiter + 1
                elif last_space != -1:
                    super().add_line(line[start:last_space])
                    needle = last_space + 1
                    start = last_space
                else:
                    super().add_line(line[start:needle])
                    start = needle

                last_delimiter = -1
                last_space = -1

            if line[needle] in self.wrap_on:
                last_delimiter = needle
            elif line[needle] == ' ':
                last_space = needle

            needle += 1

        last_line = line[start:needle]
        if last_line:
            super().add_line(last_line)

        if empty:
            self._current_page.append('')
            self._count += self._linesep_len


def use_file_check(
    ctx: ContextA,
    size: int
) -> bool:
    """
    A check to determine if uploading a file and relying on Discord's file preview is acceptable over a PaginatorInterface.
    """

    return all([
        size < 50_000,  # Check the text is below the Discord cutoff point;
        not Flags.FORCE_PAGINATOR,  # Check the user hasn't explicitly disabled this;
        (
            # Ensure the user isn't on mobile
            not ctx.author.is_on_mobile()
            if ctx.guild and ctx.bot.intents.presences and isinstance(ctx.author, discord.Member)
            else True
        )
    ])


_Emoji = typing.Union[str, discord.PartialEmoji, discord.Emoji]


class EmojiSettings(typing.NamedTuple):
    """
    Emoji settings, this sets what emoji are used for PaginatorInterface
    """

    start: _Emoji
    back: _Emoji
    forward: _Emoji
    end: _Emoji
    close: _Emoji


EMOJI_DEFAULT = EmojiSettings(
    start="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}",
    back="\N{BLACK LEFT-POINTING TRIANGLE}",
    forward="\N{BLACK RIGHT-POINTING TRIANGLE}",
    end="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}",
    close="\N{BLACK SQUARE FOR STOP}",
)


T = typing.TypeVar('T', bound=ui.View)

MaybeButton = typing.Union[discord.Interaction, ui.Button[T]]


def button_either_arg(
    a: MaybeButton[T],
    b: MaybeButton[T]
) -> typing.Tuple[discord.Interaction, ui.Button[T]]:
    """
    Compatibility function to allow interaction and button to come in either order
    """

    if isinstance(a, discord.Interaction):
        return (a, b)  # type: ignore
    return (b, a)  # type: ignore


class PaginatorInterface(ui.View):  # pylint: disable=too-many-instance-attributes
    def __init__(self, bot: BotT, paginator: commands.Paginator, **kwargs: typing.Any):
        if not isinstance(paginator, commands.Paginator):  # type: ignore
            raise TypeError('paginator must be a commands.Paginator instance')

        self._display_page = 0

        self.bot = bot

        self.message = None
        self.paginator = paginator

        self.owner = kwargs.pop('owner', None)
        self.emojis = kwargs.pop('emoji', EMOJI_DEFAULT)
        self.timeout_length = kwargs.pop('timeout', 7200)
        self.delete_message = kwargs.pop('delete_message', False)

        self.sent_page_reactions = False

        self.task: typing.Optional[asyncio.Task[None]] = None
        self.send_lock: asyncio.Event = asyncio.Event()

        self.close_exception: typing.Optional[BaseException] = None

        if self.page_size > self.max_page_size:
            raise ValueError(
                f'Paginator passed has too large of a page size for this interface. '
                f'({self.page_size} > {self.max_page_size})'
            )

        super().__init__(timeout=self.timeout_length)

    @property
    def pages(self):
        """
        Returns the paginator's pages without prematurely closing the active page.
        """
        # protected access has to be permitted here to not close the paginator's pages

        # pylint: disable=protected-access
        paginator_pages = list(self.paginator._pages)  # type: ignore
        if len(self.paginator._current_page) > 1:  # type: ignore
            paginator_pages.append(
                '\n'.join(self.paginator._current_page)  # type: ignore
                + '\n'
                + (self.paginator.suffix or '')
            )
        # pylint: enable=protected-access

        return paginator_pages

    @property
    def page_count(self):
        """
        Returns the page count of the internal paginator.
        """

        return len(self.pages)

    @property
    def display_page(self):
        """
        Returns the current page the paginator interface is on.
        """

        self._display_page = max(0, min(self.page_count - 1, self._display_page))
        return self._display_page

    @display_page.setter
    def display_page(self, value: int):
        """
        Sets the current page the paginator is on. Automatically pushes values inbounds.
        """

        self._display_page = max(0, min(self.page_count - 1, value))

    max_page_size = 2000

    @property
    def page_size(self) -> int:
        """
        A property that returns how large a page is, calculated from the paginator properties.

        If this exceeds `max_page_size`, an exception is raised upon instantiation.
        """
        page_count = self.page_count
        return self.paginator.max_size + len(f'\nPage {page_count}/{page_count}')

    @property
    def send_kwargs(self) -> typing.Dict[str, typing.Any]:
        """
        A property that returns the kwargs forwarded to send/edit when updating the page.

        As this must be compatible with both `discord.TextChannel.send` and `discord.Message.edit`,
        it should be a dict containing 'content', 'embed' or both.
        """

        content = self.pages[self.display_page]
        return {'content': content, 'view': self}

    def update_view(self):
        """
        Updates view buttons to correspond to current interface state.
        This is used internally.
        """

        self.button_start.label = f"1 \u200b {self.emojis.start}"
        self.button_previous.label = str(self.emojis.back)
        self.button_current.label = str(self.display_page + 1)
        self.button_next.label = str(self.emojis.forward)
        self.button_last.label = f"{self.emojis.end} \u200b {self.page_count}"
        self.button_close.label = f"{self.emojis.close} \u200b Close paginator"

    async def add_line(self, *args: typing.Any, **kwargs: typing.Any):
        """
        A proxy function that allows this PaginatorInterface to remain locked to the last page
        if it is already on it.
        """

        display_page = self.display_page
        page_count = self.page_count

        self.paginator.add_line(*args, **kwargs)

        new_page_count = self.page_count

        if display_page + 1 == page_count:
            # To keep position fixed on the end, update position to new last page and update message.
            self._display_page = new_page_count

        # Unconditionally set send lock to try and guarantee page updates on unfocused pages
        self.send_lock.set()

    async def send_to(self, destination: discord.abc.Messageable):
        """
        Sends a message to the given destination with this interface.

        This automatically creates the response task for you.
        """

        self.message = await destination.send(
            **self.send_kwargs, allowed_mentions=discord.AllowedMentions.none()
        )

        self.send_lock.set()

        if self.task:
            self.task.cancel()

        self.task = self.bot.loop.create_task(self.wait_loop())

        return self

    @property
    def closed(self):
        """
        Is this interface closed?
        """

        if not self.task:
            return False
        return self.task.done()

    async def send_lock_delayed(self):
        """
        A coroutine that returns 1 second after the send lock has been released
        This helps reduce release spam that hits rate limits quickly
        """

        gathered = await self.send_lock.wait()
        self.send_lock.clear()
        await asyncio.sleep(1)
        return gathered

    async def wait_loop(self):
        """
        Waits on a loop for updates to the interface. This should not be called manually - it is handled by `send_to`.
        """

        if not self.message:
            raise RuntimeError("Message not set on PaginatorInterface")

        if not self.bot.user:
            raise RuntimeError("A PaginatorInterface cannot be started while the bot is offline")

        try:  # pylint: disable=too-many-nested-blocks
            while not self.bot.is_closed():
                await asyncio.wait_for(self.send_lock_delayed(), timeout=self.timeout_length)

                self.update_view()

                try:
                    await self.message.edit(**self.send_kwargs)
                except discord.NotFound:
                    # something terrible has happened
                    return

        except (asyncio.CancelledError, asyncio.TimeoutError) as exception:
            self.close_exception = exception

            if self.bot.is_closed():
                # Can't do anything about the messages, so just close out to avoid noisy error
                return

            # If the message was already deleted, this part is unnecessary
            if not self.message:
                return

            if self.delete_message:
                await self.message.delete()
            else:
                await self.message.edit(view=None)

    async def interaction_check(self, *args: typing.Any):  # pylint: disable=arguments-differ
        """Check that determines whether this interaction should be honored"""
        *_, interaction = args  # type: ignore  #149
        interaction: discord.Interaction
        return not self.owner or interaction.user.id == self.owner.id

    @ui.button(label="1 \u200b \N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}", style=discord.ButtonStyle.secondary)
    async def button_start(self, a: MaybeButton['PaginatorInterface'], b: MaybeButton['PaginatorInterface']):  # pylint: disable=unused-argument
        """Button to send interface to first page"""

        interaction, _ = button_either_arg(a, b)

        self._display_page = 0
        self.update_view()
        await interaction.response.edit_message(**self.send_kwargs)

    @ui.button(label="\N{BLACK LEFT-POINTING TRIANGLE}", style=discord.ButtonStyle.secondary)
    async def button_previous(self, a: MaybeButton['PaginatorInterface'], b: MaybeButton['PaginatorInterface']):  # pylint: disable=unused-argument
        """Button to send interface to previous page"""

        interaction, _ = button_either_arg(a, b)

        self._display_page -= 1
        self.update_view()
        await interaction.response.edit_message(**self.send_kwargs)

    @ui.button(label="1", style=discord.ButtonStyle.primary)
    async def button_current(self, a: MaybeButton['PaginatorInterface'], b: MaybeButton['PaginatorInterface']):  # pylint: disable=unused-argument
        """Button to refresh the interface"""

        interaction, _ = button_either_arg(a, b)

        self.update_view()
        await interaction.response.edit_message(**self.send_kwargs)

    @ui.button(label="\N{BLACK RIGHT-POINTING TRIANGLE}", style=discord.ButtonStyle.secondary)
    async def button_next(self, a: MaybeButton['PaginatorInterface'], b: MaybeButton['PaginatorInterface']):  # pylint: disable=unused-argument
        """Button to send interface to next page"""

        interaction, _ = button_either_arg(a, b)

        self._display_page += 1
        self.update_view()
        await interaction.response.edit_message(**self.send_kwargs)

    @ui.button(label="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR} \u200b 1", style=discord.ButtonStyle.secondary)
    async def button_last(self, a: MaybeButton['PaginatorInterface'], b: MaybeButton['PaginatorInterface']):  # pylint: disable=unused-argument
        """Button to send interface to last page"""

        interaction, _ = button_either_arg(a, b)

        self._display_page = self.page_count - 1
        self.update_view()
        await interaction.response.edit_message(**self.send_kwargs)

    if typing.TYPE_CHECKING or hasattr(ui, 'TextInput'):
        class PageChangeModal(ui.Modal, title="Go to page"):
            """Modal that prompts users for the page number to change to"""

            page_number: ui.TextInput[ui.Modal] = ui.TextInput(label="Page number", style=discord.TextStyle.short)

            def __init__(self, interface: 'PaginatorInterface', *args: typing.Any, **kwargs: typing.Any):
                super().__init__(*args, timeout=interface.timeout_length, **kwargs)
                self.interface = interface
                self.page_number.label = f"Page number (1-{interface.page_count})"
                self.page_number.min_length = 1
                self.page_number.max_length = len(str(interface.page_count))

            async def on_submit(self, interaction: discord.Interaction, /):
                try:
                    if not self.page_number.value:
                        raise ValueError("Page number not filled")

                    self.interface.display_page = int(self.page_number.value) - 1
                except ValueError:
                    await interaction.response.send_message(
                        content=f"``{self.page_number.value}`` could not be converted to a page number",
                        ephemeral=True
                    )
                else:
                    self.interface.update_view()
                    await interaction.response.edit_message(**self.interface.send_kwargs)

        @ui.button(label="\N{RIGHTWARDS ARROW WITH HOOK} \u200b Go to page", style=discord.ButtonStyle.primary)
        async def button_goto(self, a: MaybeButton['PaginatorInterface'], b: MaybeButton['PaginatorInterface']):  # pylint: disable=unused-argument
            """Button to jump directly to a page"""

            interaction, _ = button_either_arg(a, b)

            await interaction.response.send_modal(self.PageChangeModal(self))

    @ui.button(label="\N{BLACK SQUARE FOR STOP} \u200b Close paginator", style=discord.ButtonStyle.danger)
    async def button_close(self, a: MaybeButton['PaginatorInterface'], b: MaybeButton['PaginatorInterface']):  # pylint: disable=unused-argument
        """Button to close the interface"""

        message = self.message
        self.message = None
        if self.task:
            self.task.cancel()
        self.stop()
        if message:
            await message.delete()