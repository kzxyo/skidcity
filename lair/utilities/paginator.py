from inspect import iscoroutinefunction as iscoro
from inspect import isfunction as isfunc

from discord import ButtonStyle, Embed, HTTPException, Interaction, TextStyle
from discord.ui import Button, Modal, TextInput, View

from . import config


class prev_page(Button):
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


class first_page(Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page = 0
        view.update_view()
        await view.edit_embed(interaction)


class next_page(Button):
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


class last_page(Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        await interaction.response.defer()
        view = self.view
        view.page = len(view.embeds) - 1
        view.update_view()
        await view.edit_embed(interaction)


class delete_page(Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        view = self.view
        await view.message.delete()
        view.stop()


class end_page(Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        view = self.view
        for child in view.children:
            child.disabled = True
        await view.edit_embed(interaction)
        view.stop()


class show_page(Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, disabled=True, row=row)

    async def callback(self, interaction):
        view = self.view
        await view.message.channel.send(str(view.page))


class goto_modal(Modal, title="Lair Pagination"):
    def __init__(self, button):
        super().__init__()
        self.button = button
        self.page_num = TextInput(
            label="Lair Menu",
            placeholder="Type integers to view the corresponding page",
            style=TextStyle.short,
            required=True,
        )
        self.add_item(self.page_num)

    async def on_submit(self, interaction: Interaction):
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
                content="that isn't a number", ephemeral=True
            )


class goto_page(Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        await interaction.response.send_modal(goto_modal(self))


class lock_page(Button):
    def __init__(self, label, emoji, style, row):
        super().__init__(label=label, emoji=emoji, style=style, row=row)

    async def callback(self, interaction):
        view = self.view
        view.clear_items()
        await view.edit_embed(interaction)
        view.stop()


class Paginator(View):
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
        super().__init__(timeout=timeout)  # timeout=timeout
        self.check = check
        self.bot = bot
        self.defer = defer
        self.embeds = embeds
        self.page = 0
        self.destination = destination
        self.interactionfailed = interactionfailed
        self.invoker = invoker
        self.page_button = None

    def default_pagination(self, show_page: bool = False):
        self.add_button("first", emoji=config.Emoji.first)
        self.add_button("prev", emoji=config.Emoji.previous)

        if show_page is True:
            self.add_button("show")

        self.add_button("next", emoji=config.Emoji.next)
        self.add_button("last", emoji=config.Emoji.last)
        self.add_button("goto", emoji=config.Emoji.goto)

    async def edit_embed(self, interaction, remove: bool = False):
        current = self.embeds[self.page]
        if remove:
            await interaction.message.edit(content=None, embed=current, view=None)
        if isinstance(current, str):
            await interaction.message.edit(content=current, embed=None, view=self)
        elif isinstance(current, Embed):
            await interaction.message.edit(content=None, embed=current, view=self)
        elif isinstance(current, tuple):
            dct = dict()
            for item in current:
                if isinstance(item, str):
                    dct["content"] = item
                elif isinstance(item, Embed):
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
            elif isinstance(current, Embed):
                self.message = await self.destination.reply(
                    content=None, embed=current, view=self
                )
            elif isinstance(current, tuple):
                dct = dict()
                for item in current:
                    if isinstance(item, str):
                        dct["content"] = item
                    elif isinstance(item, Embed):
                        dct["embed"] = item
                self.message = await self.destination.reply(
                    content=dct.get("content", None),
                    embed=dct.get("embed", None),
                    view=self,
                )
        except HTTPException:
            self.stop()

    async def interaction_check(self, interaction):
        if not self.invoker:
            pass
        else:
            if interaction.user.id != self.invoker:
                return await interaction.response.send_message(
                    ephemeral=True,
                    embed=Embed(
                        color=config.Color.error,
                        description=f"<:emoji_7:1067814032607809667> {interaction.user.mention}: you can't **interact** with this",
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
        except Exception:
            raise ValueError

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.edit_embed(self)
        self.stop()

    def update_view(self):
        try:
            self.page_button.label = f"{self.page+1:,} / {len(self.embeds):,}"
        except Exception:
            pass

    def add_button(
        self,
        action,
        /,
        *,
        label="",
        emoji=None,
        style=ButtonStyle.grey,
        row=None,
    ):
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
            self.add_item(goto_page(None, emoji, style, row))
        elif action == "next":
            self.add_item(next_page(label, emoji, style, row))
        elif action == "last":
            self.add_item(last_page(label, emoji, style, row))
        elif action == "end":
            self.add_item(end_page(label, emoji, ButtonStyle.red, row))
        elif action == "delete":
            self.add_item(delete_page(label, emoji, ButtonStyle.red, row))
        elif action == "lock":
            self.add_item(lock_page(label, emoji, style, row))


def embed_creator(
    text: str,
    num: int = 1980,
    /,
    *,
    title: str = "",
    prefix: str = "",
    suffix: str = "",
    color: int = config.Color.main,
):
    return [
        Embed(
            title=title,
            description=prefix + (text[i : i + num]) + suffix,
            color=color if color else config.Color.main,
        )
        for i in range(0, len(text), num)
    ]


def text_creator(text: str, num: int = 1980, /, *, prefix: str = "", suffix: str = ""):
    return [prefix + (text[i : i + num]) + suffix for i in range(0, len(text), num)]
