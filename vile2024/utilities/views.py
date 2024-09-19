from contextlib import suppress

from discord import (
    ButtonStyle, 
    HTTPException, 
    Interaction, 
    Member, 
    Message
)

from discord.ui import (
    button as Button, 
    View
)

from typing_extensions import NoReturn
from .literals import Emojis


class Confirmation(View):
    def __init__(
        self: "Confirmation", 
        message: Message, 
        invoker: Member = None
    ) -> NoReturn:
        super().__init__(timeout=None)
        
        self.value = False
        self.message = message
        self.invoker = invoker
        

    @Button(
        style=ButtonStyle.green, 
        label="Approve"
    )
    async def approve(
        self: "Confirmation", 
        interaction: Interaction, 
        _: None
    ):
        """
        The approve button.

        Parameters:
            interaction (Interaction): The interaction object.
            _: Button: The unused button object.
        """

        await self.confirmation(
            interaction, 
            True
        )


    @Button(
        style=ButtonStyle.red, 
        label="Decline"
    )
    async def decline(
        self: "Confirmation", 
        interaction: Interaction, 
        _: None
    ):
        """
        The decline button.

        Parameters:
            interaction (Interaction): The interaction object.
            _: None: The unused button object.
        """

        await self.confirmation(
            interaction, 
            False
        )


    async def confirmation(
        self: "Confirmation", 
        interaction: Interaction, 
        value: bool
    ) -> NoReturn:
        """
        Handles the confirmation of an interaction.

        Parameters:
            interaction (Interaction): The interaction object representing the user's interaction.
            value (bool): The boolean value indicating the confirmation.
        """
        
        await interaction.response.defer()
        
        if interaction.user.id != self.invoker.id:
            return

        with suppress(HTTPException):
            await self.message.edit(view=None)

        self.value = value
        self.stop()
