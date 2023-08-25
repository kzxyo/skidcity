from inspect import iscoroutinefunction as iscoro, isfunction as isfunc
from typing import Optional, Iterable
import discord


class GotoModal(discord.ui.Modal, title="Vile Pagination"):
    def __init__(self, button: discord.ui.Button):
        super().__init__()

        self.button = button
        self.page_num = discord.ui.TextInput(
            label="Vile Page Menu",
            placeholder="Type numbers to advance to it's corresponding page",
            style=discord.TextStyle.short,
            required=True,
        )
        self.add_item(self.page_num)


    async def on_submit(self, interaction: discord.Interaction):
        
        await interaction.response.defer()

        try:
            view = self.button.view
            num = int(self.page_num.value) - 1

            assert num in range(len(view.embeds)), await interaction.followup.send(
                ephemeral=True, 
                embed=discord.Embed(
                    color=interaction.client.color,
                    description=f"{interaction.client.warn} {interaction.user.mention}**:** Please provide a **valid** number."
                )
            )
            
            view.page = num
            await view.edit_embed(interaction)

        except AssertionError:
            pass


class Paginator(discord.ui.View):
    def __init__(
        self, 
        bot: "VileBot", 
        embeds: Iterable, 
        destination: "Context", 
        /, 
        *, 
        invoker: Optional[discord.Member] = None, 
        attachments: Optional[Iterable] = None
    ) -> None:
        super().__init__(timeout=None)

        self.bot = bot
        self.attachments = attachments
        self.embeds = embeds
        self.page = 0
        self.destination = destination
        self.invoker = invoker
        self.page_button = None
        
        
    @discord.ui.button(
        style=discord.ButtonStyle.grey, 
        emoji="<:v_first_page:1067034043901804564>"
    )
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        await interaction.response.defer()
        view = self
        view.page = 0
        await view.edit_embed(interaction)
        
        
    @discord.ui.button(
        style=discord.ButtonStyle.grey, 
        emoji="<:v_previous_page:1067034040223420467>"
    )
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        await interaction.response.defer()
        view = self
        view.page -= 1
        
        if view.page < 0:
            view.page = len(view.embeds)-1
        
        await view.edit_embed(interaction)
        

    @discord.ui.button(
        style=discord.ButtonStyle.grey, 
        emoji="<:v_next_page:1067034038386303016>"
    )
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        await interaction.response.defer()
        view = self
        view.page += 1
        
        if view.page == len(view.embeds):
            view.page = 0
        
        await view.edit_embed(interaction)


    @discord.ui.button(
        style=discord.ButtonStyle.grey, 
        emoji="<:v_last_page:1067034034946977792>"
    )
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        await interaction.response.defer()
        view = self
        view.page = len(view.embeds)-1
        await view.edit_embed(interaction)


    @discord.ui.button(
        style=discord.ButtonStyle.grey, 
        emoji="<:v_page_skip:1067034020489220166>"
    )
    async def goto_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GotoModal(button))
        

    async def edit_embed(self, interaction: discord.Interaction) -> None:
        
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
            
            elif isinstance(current, discord.Embed):
                await interaction.message.edit(
                    content=None, 
                    mbed=current, 
                    view=self, 
                    attachments=current_attachment
                )
            
            elif isinstance(current, tuple):
                data = {}
                for item in current:
                    if isinstance(item, str):
                        data["content"] = item

                    elif isinstance(item, discord.Embed):
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
            
            elif isinstance(current, discord.Embed):
                await interaction.message.edit(
                    content=None, 
                    embed=current, 
                    view=self
                )
            
            elif isinstance(current, tuple):
                data = {}
                for item in current:
                    if isinstance(item, str):
                        data["content"] = item
                    
                    elif isinstance(item, discord.Embed):
                        data["embed"] = item
                
                await interaction.message.edit(
                    content=data.get("content", None), 
                    embed=data.get("embed", None), 
                    view=self
                )


    async def start(self) -> None:
        
        try:
            current = self.embeds[self.page]
            if self.attachments:
                current_attachment = self.attachments[self.page]
                
                if isinstance(current, str):
                    self.message = await self.destination.send(
                        content=current, 
                        embed=None, 
                        view=self, 
                        file=current_attachment
                    )
                
                elif isinstance(current, discord.Embed):
                    self.message = await self.destination.send(
                        content=None, 
                        embed=current, 
                        view=self, 
                        file=current_attachment
                    )
                
                elif isinstance(current, tuple):
                    data = {}
                    for item in current:
                        if isinstance(item, str):
                            data["content"] = item
                        
                        elif isinstance(item, discord.Embed):
                            data["embed"] = item
                    
                    self.message = await self.destination.send(
                        content=data.get("content", None), 
                        embed=data.get("embed", None), 
                        view=self, 
                        file=current_attachment
                    )
            
            else:
                if isinstance(current, str):
                    self.message = await self.destination.send(content=current,embed=None, view=self)
                
                elif isinstance(current, discord.Embed):
                    self.message = await self.destination.send(content=None, embed=current, view=self)
                
                elif isinstance(current, tuple):
                    data = {}
                    for item in current:
                        if isinstance(item, str):
                            data["content"] = item
                            
                        elif isinstance(item, discord.Embed):
                            data["embed"] = item
                    
                    self.message = await self.destination.send(
                        content=data.get("content", None), 
                        embed=data.get("embed", None), 
                        view=self, 
                        file=current_attachment
                    )
        
        except discord.HTTPException:
            self.stop()
            

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if self.invoker:
            if interaction.user.id != self.invoker:
                return await interaction.response.send_message(
                    ephemeral=True, 
                    embed=discord.Embed(
                        color=interaction.client.color,
                        description=f"{interaction.client.fail} {interaction.user.mention}**:** You can't interact with this menu."
                    )
                )
            
        return True
            

    async def on_timeout(self):
        view = self.view
        view.clear_items()
        self.stop()


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
    return tuple(
        discord.Embed(
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
    return tuple(
        prefix + (text[i:i+num]) + suffix
        for i in range(0, len(text), num)
    )