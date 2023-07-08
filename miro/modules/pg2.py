from inspect import iscoroutinefunction as iscoro, isfunction as isfunc
import discord, typing


async def aiter(
    iterable: typing.Iterator[typing.Any],
) -> typing.AsyncIterator[typing.Any]:
    for i in iterable:
        yield i


class prev_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page -= 1
        if view.page < 0:
            view.page = len(view.embeds) - 1
        view.update_view()
        await view.edit_embed(interaction)


class first_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page = 0
        view.update_view()
        await view.edit_embed(interaction)


class next_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page += 1
        if view.page == len(view.embeds):
            view.page = 0
        view.update_view()
        await view.edit_embed(interaction)


class last_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page = len(view.embeds) - 1
        view.update_view()
        await view.edit_embed(interaction)


class delete_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        view = self.view
        await view.message.delete()
        view.stop()


class end_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        view = self.view
        async for child in aiter(view.children):
            child.disabled = True
        await view.edit_embed(interaction)
        view.stop()


class show_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, disabled=True, row=row)

    async def callback(self, interaction):
        view = self.view
        await view.message.channel.send(str(view.page))


class goto_modal(discord.ui.Modal, title="Miro pagination"):
    def __init__(self, button):
        super().__init__()
        self.button = button
        self.page_num = discord.ui.TextInput(
            label="Miro Cmd Menu",
            placeholder=f"type numbers to advance to its corresponding page",
            style=discord.TextStyle.short,
            required=True,
        )
        self.add_item(self.page_num)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            view = self.button.view
            num = int(self.page_num.value) - 1

            if num in range(len(view.embeds)):
                view.page = num
            else:
                return await interaction.followup.send(
                    content="invalid number", ephemeral=True
                )

            view.update_view()
            await view.edit_embed(interaction)

        except ValueError:
            return await interaction.response.send_message(
                content="that ain't a number lol", ephemeral=True
            )


class goto_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        await interaction.response.send_modal(goto_modal(self))


class lock_page(discord.ui.Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        view = self.view
        view.clear_items()
        await view.edit_embed(interaction)
        view.stop()


class Paginator(discord.ui.View):
    def __init__(
        self,
        bot,
        embeds,
        destination,
        /,
        *,
        interactionfailed=None,
        check=None,
        timeout=None,
        invoker=None,
        defer=True,
    ):
        """A class which controls everything that happens
        Parameters
        -----------
        bot: :class:`Bot`
            The bot object
        embeds: :class:`list`
            The embeds that will be paginated
        destination: :class:`discord.abc.Messageable`
            The channel the pagination message will be sent to
        interactionfailed: Optional[Callable[..., :class:`bool`]]
            A function that will be called when the check fails
        check: Optional[Callable[..., :class:`bool`]]
            A predicate to check what to wait for.
        timeout: Optional[:class:`float`]
            The number of seconds to wait before timing out.
        """
        super().__init__(timeout=timeout)
        self.check = check
        self.bot = bot
        self.defer = defer
        self.embeds = embeds
        self.page = 0
        self.destination = destination
        self.interactionfailed = interactionfailed
        self.invoker = invoker
        self.page_button = None

    async def edit_embed(self, interaction):
        current = self.embeds[self.page]
        if isinstance(current, str):
            await interaction.message.edit(content=current, embed=None, view=self)
        elif isinstance(current, discord.Embed):
            await interaction.message.edit(content=None, embed=current, view=self)
        elif isinstance(current, tuple):
            dct = {}
            async for item in aiter(current):
                if isinstance(item, str):
                    dct["content"] = item
                elif isinstance(item, discord.Embed):
                    dct["embed"] = item
            await interaction.message.edit(
                content=dct.get("content", None),
                embed=dct.get("embed", None),
                view=self,
            )

    async def start(self):
        try:
            current = self.embeds[self.page]
            if isinstance(current, str):
                self.message = await self.destination.reply(
                    content=current, embed=None, view=self
                )
            elif isinstance(current, discord.Embed):
                self.message = await self.destination.reply(
                    content=None, embed=current, view=self
                )
            elif isinstance(current, tuple):
                dct = {}
                async for item in aiter(current):
                    if isinstance(item, str):
                        dct["content"] = item
                    elif isinstance(item, discord.Embed):
                        dct["embed"] = item
                self.message = await self.destination.reply(
                    content=dct.get("content", None),
                    embed=dct.get("embed", None),
                    view=self,
                )
        except discord.HTTPException:
            self.stop()

    async def interaction_check(self, interaction):
        if not self.invoker:
            pass
        else:
            if interaction.user.id != self.invoker:
                return await interaction.response.send_message(
                    ephemeral=True,
                    embed=discord.Embed(
                        color=0xffbb5e,
                        description=f"<:mirow:1117144157992009728> {interaction.user.mention}: you can't **interact** with this",
                    ),
                )
            else:
                return interaction.user.id == self.invoker
        if self.check is None:
            return True
        if not isfunc(self.check):
            raise ValueError
        try:
            if not self.check(interaction):
                if self.interactionfailed:
                    if iscoro(self.interactionfailed):
                        await self.interactionfailed(interaction)
                        await interaction.response.defer()
                return False
            return True
        except:
            raise ValueError

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.edit_embed(self)
        self.stop()

    def update_view(self):
        try:
            self.page_button.label = None
        except (NameError, AttributeError):
            pass

    def add_button(
        self,
        action,
        /,
        *,
        label="",
        emoji=None,
        style=discord.ButtonStyle.grey,
        row=None,
    ):
        defer = self.defer
        action = action.strip().lower()
        if action not in [
            "first",
            "prev",
            "previous",
            "back",
            "delete",
            "next",
            "last",
            "end",
            "page",
            "show",
            "goto",
            "lock",
        ]:
            return
        elif action == "first":
            self.add_item(first_page(label, emoji, style, row))
        elif action in ["back", "prev", "previous"]:
            self.add_item(prev_page(label, emoji, style, row))
        elif action in ["page", "show"]:
            button = show_page("yes", emoji, style, row)
            self.page_button = button
            self.add_item(button)
            self.update_view()
        elif action == "goto":
            button = goto_page(None, emoji, style, row)
            self.page_button = button
            self.add_item(button)
            self.update_view()
        elif action == "next":
            self.add_item(next_page(label, emoji, style, row))
        elif action == "last":
            self.add_item(last_page(label, emoji, style, row))
        elif action == "end":
            self.add_item(end_page(label, emoji, discord.ButtonStyle.red, row))
        elif action == "delete":
            self.add_item(delete_page(label, emoji, discord.ButtonStyle.red, row))
        elif action == "lock":
            self.add_item(lock_page(label, emoji, style, row))

def embed_creator(
    text, num, /, *, title="", prefix="", suffix="", color=None, colour=None
):
    if color != None and colour != None:
        raise ValueError

    return [
        discord.Embed(
            title=title,
            description=prefix + (text[i : i + num]) + suffix,
            color=color if color != None else colour if colour != None else 0xFF0000,
        )
        for i in range(0, len(text), num)
    ]

# Example usage:
# Create a list of embeds with a maximum of 2000 characters per embed
embeds = embed_creator("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ultrices vulputate ligula ut sollicitudin. Nullam malesuada sagittis pellentesque. Phasellus cursus dolor ac odio auctor, vitae fermentum enim elementum. Nulla quis nibh id urna placerat fringilla. Vestibulum eleifend varius tortor et cursus. Nunc luctus, mauris ac fringilla luctus, enim mi tincidunt nisi, vel blandit neque enim nec purus. Sed rutrum felis nec pharetra condimentum. Fusce lobortis lacus quis dolor iaculis, non efficitur lorem tristique. Pellentesque in urna ullamcorper, blandit felis at, feugiat turpis. Donec eu nibh vel odio lacinia fringilla. Aliquam gravida, nunc at congue lobortis, tellus ligula consectetur mauris, id auctor turpis turpis in urna. Phasellus fermentum accumsan quam, vitae condimentum lectus interdum sit amet. Etiam sit amet malesuada sem. Sed lacinia, nisi vitae finibus elementum, ipsum nunc finibus sapien, eu lacinia quam est ut metus. Vestibulum sodales urna eu semper luctus.", 2000)
