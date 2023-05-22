import typing
import psutil

# import dotenv
import discord
import datetime

# import itertools
import traceback

from discord.ext import commands
from modules import utils


class Confirm(discord.ui.View):
    def __init__(self, value: bool = False, invoker: discord.Member = None):
        self.value = value
        self.invoker = invoker
        super().__init__(timeout=30)

    # When the confirm button is pressed, set the inner value to True and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.

    async def confirmation(self, interaction: discord.Interaction, confirm: bool):
        if confirm:
            if interaction.user.id != self.invoker.id:
                return
            await interaction.response.defer()
        else:
            await interaction.response.defer()
        self.value = confirm
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=utils.emoji("done"))
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.confirmation(interaction, True)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji=utils.emoji("fail"))
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.confirmation(interaction, False)


async def confirm(
    self: discord.ext.commands.Cog,
    ctx: discord.ext.commands.Context,
    msg: discord.Message,
):
    """Waits for confirmation via reaction from the user before continuing
    Parameters
    ----------
    self : discord.ext.commands.Cog
        Cog the command is invoked in
    ctx : discord.ext.commands.Context
        Command invocation context
    msg : discord.Message
        The message to prompt for confirmation on
    timeout = timeout : int, optional
        How long to wait before timing out (seconds), by default 20
    Returns
    -------
    output : bool or None
        True if user confirms action, False if user does not confirm action, None if confirmation times out
    """
    view = Confirm(invoker=ctx.author)
    await msg.edit(view=view)
    # Wait for the View to stop listening for input...
    await view.wait()
    return view.value
