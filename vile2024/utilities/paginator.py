from contextlib import suppress

from discord import (
    ButtonStyle, 
    Embed, 
    Member, 
    Message, 
    TextInput, 
    TextStyle, 
    Interaction
)

from discord.errors import HTTPException

from discord.ui import (
    button as Button,
    Modal, 
    View
)

from typing import (
    Callable,
    Iterable, 
    Optional, 
    List, 
    Tuple,
    Any
)

from logging import getLogger
from typing_extensions import NoReturn

logger = getLogger(__name__)


def chunk(_list: List[Any], n: int) -> Iterable[List[Any]]:
    """
    Generates chunks of a given list.

    Parameters:
        _list (List[Any]): The list to be chunked.
        n (int): The size of each chunk.

    Returns:
        Iterable[List[Any]]: A generator that yields chunks of the list.
    """
    
    for i in range(0, len(_list), n):
        yield _list[i:i+n]


class GotoModal(Modal, title="Advanced Pagination"):
    def __init__(self: "GotoModal", button: object):
        super().__init__()

        self.button = button
        self.page_num = TextInput(
            label="Page Number",  # Correct usage of label
            placeholder="Type numbers to advance to its corresponding page",
            style=TextStyle.short,
            required=True,
        )
        
        self.add_item(self.page_num)


    async def on_submit(self: "GotoModal", interaction: Interaction):
        """
        Handle the event when a user submits an interaction.

        Parameters:
            interaction (Interaction): The interaction object representing the user's interaction.
        """
        
        await interaction.response.defer()

        with suppress(AssertionError):
            view = self.button.view
            num = int(self.page_num.value) - 1

            assert num in range(len(view.embeds)), await interaction.followup.send(
                ephemeral=True, 
                embed=Embed(
                    color=interaction.client.color,
                    description=f"{interaction.client.warn} {interaction.user.mention}**:** Please provide a **valid** number."
                )
            )
            
            view.page = num
            await view.edit_embed(interaction)


class Paginator(View):
    def __init__(
        self: "Paginator", 
        bot: "VileBot", 
        embeds: Iterable, 
        destination: "Context", 
        /, 
        *, 
        patch: Optional[Message] = None,
        invoker: Optional[Member] = None, 
        attachments: Optional[Iterable] = None,
        execute: Optional[Tuple[Callable]] = None
    ) -> NoReturn:
        super().__init__(timeout=None)

        self.bot = bot
        self.attachments = attachments
        self.embeds = embeds
        self.page = 0
        self.destination = destination
        self.patch = patch
        self.invoker = invoker
        self.page_button = None
        self.execute = execute or ( )
        
        
    @Button(
        style=ButtonStyle.grey, 
        emoji="<:v_first_page:1067034043901804564>"
    )
    async def first_page(
        self: "Paginator", 
        interaction: Interaction, 
        _: None
    ):
        """
        The first-page button.

        Parameters:
            interaction (Interaction): The interaction object.
            _: Button: The unused button object.
        """

        await interaction.response.defer()

        view = self
        view.page = 0

        for func in self.execute:
            await func(self, interaction)

        await view.edit_embed(interaction)
        
        
    @Button(
        style=ButtonStyle.grey, 
        emoji="<:v_previous_page:1067034040223420467>"
    )
    async def previous_page(
        self: "Paginator", 
        interaction: Interaction, 
        _: None
    ):
        """
        The previous-page button.

        Parameters:
            interaction (Interaction): The interaction object.
            _: Button: The unused button object.
        """

        await interaction.response.defer()

        view = self
        view.page -= 1
        
        if view.page < 0:
            view.page = len(view.embeds)-1

        for func in self.execute:
            await func(self, interaction)
        
        await view.edit_embed(interaction)
        

    @Button(
        style=ButtonStyle.grey, 
        emoji="<:v_next_page:1067034038386303016>"
    )
    async def next_page(
        self: "Paginator", 
        interaction: Interaction, 
        _: None
    ):
        """
        The next-page button.

        Parameters:
            interaction (Interaction): The interaction object.
            _: Button: The unused button object.
        """

        await interaction.response.defer()
        
        view = self
        view.page += 1
        
        if view.page == len(view.embeds):
            view.page = 0

        for func in self.execute:
            await func(self, interaction)
        
        await view.edit_embed(interaction)


    @Button(
        style=ButtonStyle.grey, 
        emoji="<:v_last_page:1067034034946977792>"
    )
    async def last_page(
        self: "Paginator", 
        interaction: Interaction, 
        _: None
    ):
        """
        The last-page button.

        Parameters:
            interaction (Interaction): The interaction object.
            _: Button: The unused button object.
        """

        await interaction.response.defer()

        view = self
        view.page = len(view.embeds)-1

        for func in self.execute:
            await func(self, interaction)

        await view.edit_embed(interaction)


    @Button(
        style=ButtonStyle.grey, 
        emoji="<:v_page_skip:1067034020489220166>"
    )
    async def goto_page(
        self: "Paginator", 
        interaction: Interaction, 
        button: None
    ):
        """
        The modal button.

        Parameters:
            interaction (Interaction): The interaction object.
            _: Button: The button object.
        """

        await interaction.response.defer()
        await interaction.response.send_modal(GotoModal(button))
        

    async def edit_embed(self, interaction: Interaction) -> NoReturn:
        """
        Edit the embed for a discord interaction.

        Parameters:
            interaction (Interaction): The interaction object.
        """
        
        current = self.embeds[self.page]
        if self.attachments:
            current_attachment = [self.attachments[self.page]]
            
            if isinstance(current, str):
                await interaction.message.edit(
                    content=current, 
                    embed=None, 
                    view=self, 
                    attachments=current_attachment
                )
            
            elif isinstance(current, Embed):
                await interaction.message.edit(
                    content=None, 
                    embed=current, 
                    view=self, 
                    attachments=current_attachment
                )
            
            elif isinstance(current, tuple):
                data = { }
                for item in current:
                    if isinstance(item, str):
                        data["content"] = item

                    elif isinstance(item, Embed):
                        data["embed"] = item

                await interaction.message.edit(
                    content=data.get("content", None), 
                    embed=data.get("embed", None), 
                    view=self, 
                    attachments=current_attachment
                )

        else:
            if isinstance(current, str):
                await interaction.message.edit(
                    content=current, 
                    embed=None, 
                    view=self
                )
            
            elif isinstance(current, Embed):
                await interaction.message.edit(
                    content=None, 
                    embed=current, 
                    view=self
                )
            
            elif isinstance(current, tuple):
                data = { }
                for item in current:
                    if isinstance(item, str):
                        data["content"] = item
                    
                    elif isinstance(item, Embed):
                        data["embed"] = item
                
                await interaction.message.edit(
                    content=data.get("content", None), 
                    embed=data.get("embed", None), 
                    view=self
                )


    async def start(self) -> NoReturn:
        """
        Start the function execution.
        
        This function starts the execution of the function. 
        It first checks if the `patch` attribute is not `None`. 
        
        If it is not `None`, it assigns the `edit` method of the `patch` attribute to the variable `func`. 
        Otherwise, it assigns the `send` method of the `destination` attribute to `func`.
        
        The function then tries to access the `current` element of the `embeds` list using the `page` attribute. 
        
        If the `attachments` list is not empty, it assigns the `current_attachment` element of 
        the `attachments` list to the variable `current_attachment`.

        The function then checks the type of `current`. If it is a string, it calls the `func` method with the `content` parameter set to `current`, the `embed` parameter set to `None`, the `view` parameter set to `self`, and the `file` parameter set to `current_attachment`. If `current` is an instance of `Embed`, it calls the `func` method with the `content` parameter set to `None`, the `embed` parameter set to `current`, the `view` parameter set to `self`, and the `file` parameter set to `current_attachment`. If `current` is a tuple, it creates a dictionary `data` and iterates over the elements of `current`. If an element is a string, it assigns it to the `content` key of `data`. If an element is an instance of `Embed`, it assigns it to the `embed` key of `data`. Finally, it calls the `func` method with the `content` parameter set to `data.get("content", None)`, the `embed` parameter set to `data.get("embed", None)`, the `view` parameter set to `self`, and the `file` parameter set to `current_attachment`.

        If the `attachments` list is empty, the function follows the same logic as described above, but without the `file` parameter.

        If an exception of type `HTTPException` occurs, the function calls the `stop` method.
        """
        
        func = self.patch.edit if self.patch is not None else self.destination.send
        try:
            current = self.embeds[self.page]
            if self.attachments:
                current_attachment = self.attachments[self.page]
                
                if isinstance(current, str):
                    self.message = await func(
                        content=current, 
                        embed=None, 
                        view=self, 
                        file=current_attachment
                    )
                
                elif isinstance(current, Embed):
                    self.message = await func(
                        content=None, 
                        embed=current, 
                        view=self, 
                        file=current_attachment
                    )
                
                elif isinstance(current, tuple):
                    data = { }
                    for item in current:
                        if isinstance(item, str):
                            data["content"] = item
                        
                        elif isinstance(item, Embed):
                            data["embed"] = item
                    
                    self.message = await func(
                        content=data.get("content", None), 
                        embed=data.get("embed", None), 
                        view=self, 
                        file=current_attachment
                    )
            
            else:
                if isinstance(current, str):
                    self.message = await func(
                        content=current,
                        embed=None, 
                        view=self
                    )
                
                elif isinstance(current, Embed):
                    self.message = await func(
                        content=None, 
                        embed=current, 
                        view=self
                    )
                
                elif isinstance(current, tuple):
                    data = { }
                    for item in current:
                        if isinstance(item, str):
                            data["content"] = item
                            
                        elif isinstance(item, Embed):
                            data["embed"] = item
                    
                    self.message = await func(
                        content=data.get("content", None), 
                        embed=data.get("embed", None), 
                        view=self
                    )

            return self
        
        except HTTPException:
            self.stop()
            

    async def interaction_check(self, interaction: Interaction) -> bool:
        """
        Checks if the given interaction is valid.

        Parameters:
            interaction (Interaction): The interaction to be checked.

        Returns:
            bool: True if the interaction is valid, False otherwise.
        """

        if self.invoker:
            if interaction.user.id != self.invoker:
                return await interaction.response.send_message(
                    ephemeral=True, 
                    embed=Embed(
                        color=interaction.client.color,
                        description=f"{interaction.client.warn} {interaction.user.mention}**:** You can't interact with this menu."
                    )
                )
            
        return True
            

    async def on_timeout(self):
        """
        Handles the timeout event.
        This function is called when a timeout event occurs. 
        It disables all the child elements in the view and updates the message view accordingly. 
        """

        for child in self.view.children:
            child.disabled = True

        await self.message.edit(view=self.view)
        self.stop()


class FieldPaginator(Paginator):
    def __init__(
        self,
        bot: "VileBot", 
        destination: "Context",
        embed: Embed, 
        fields: list, 
        footer: Optional[dict] = None, 
        per_page: int = 5,
        patch: Optional[Message] = None,
        invoker: Optional[Member] = None, 
        **kwargs
    ) -> NoReturn:
        
        embeds = [ ]

        for index, fields_chunk in enumerate(chunk(fields, per_page), start=1):
            _embed = embed.copy()
            _embed._fields = fields_chunk

            if footer:
                _embed.set_footer(
                    text=footer["text"].format(index=index, total=int(len(fields)/5)+1),
                    icon_url=footer.get("icon_url")
                )

            embeds.append(_embed)
            del fields_chunk

        super().__init__(
            bot,
            embeds,
            destination,
            patch=patch,
            invoker=invoker
        )


def embed_creator(
    text: str, 
    num: int = 1980, 
    /, 
    *, 
    title: str = "", 
    prefix: str = "", 
    suffix: str = "", 
    color: int = 0xb1aad8
) -> tuple:
    """
    Creates a list of Embed objects, each containing a portion of the input text.
    
    Parameters:
        text (str): The input text to be divided into portions.
        num (int, optional): The number of characters in each portion. Defaults to 1980.
        title (str, optional): The title of the Embed objects. Defaults to "".
        prefix (str, optional): The prefix to be added to each portion of the text. Defaults to "".
        suffix (str, optional): The suffix to be added to each portion of the text. Defaults to "".
        color (int, optional): The color of the Embed objects. Defaults to 0xb1aad8.
        
    Returns:
        tuple: A tuple of Embed objects, each containing a portion of the input text.
    """
    
    return tuple(
        Embed(
            title=title,
            description=prefix + (text[i:i+num]) + suffix,
            color=color if color != None else 0x2f3136,
        )
        for i in range(0, len(text), num)
    ) 
    

def text_creator(
    text: str, 
    num: int = 1980, 
    /, 
    *, 
    prefix: str = "", 
    suffix: str = ""
) -> tuple:
    """
    Generates a tuple of text segments from a given text string, with a specified 
    maximum segment length and optional prefix and suffix.

    Parameters:
        text (str): The text string to generate segments from.
        num (int, optional): The maximum length of each segment. Defaults to 1980.
        prefix (str, optional): The prefix to add to each segment. Defaults to "".
        suffix (str, optional): The suffix to add to each segment. Defaults to "".

    Returns:
        tuple: A tuple containing the generated text segments.
    """

    return tuple(
        prefix + (text[i:i+num]) + suffix
        for i in range(0, len(text), num)
    )