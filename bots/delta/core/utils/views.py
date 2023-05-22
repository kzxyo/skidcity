import discord
from discord.ext import commands

class Views:
    class Paginator(discord.ui.View):
        def __init__(self, *,
                    timeout: int = 60,
                    previous_button: discord.ui.Button = None,
                    next_button: discord.ui.Button = None,
                    page_counter_style: discord.ButtonStyle = discord.ButtonStyle.grey,
                    initial_page: int = 0) -> None:
            self.previous_button = previous_button or discord.ui.Button(emoji="<:lol2:1031199327269433436>", style=discord.ButtonStyle.grey)
            self.next_button = next_button or discord.ui.Button(emoji="<:lol:1031199545775886346>", style=discord.ButtonStyle.grey)
            self.page_counter_style = page_counter_style
            self.initial_page = initial_page

            self.pages = None
            self.ctx = None
            self.message = None
            self.current_page = None
            self.page_counter = None
            self.total_page_count = None
            super().__init__(timeout=timeout)

        async def start(self, ctx: commands.Context, pages: list[discord.Embed], reply: bool=True):
            self.pages = pages
            self.total_page_count = len(pages)
            self.ctx = ctx
            self.author = self.ctx.author
            self.bot = self.ctx.bot
            self.current_page = self.initial_page
            self.previous_button.callback = self.previous_button_callback
            self.next_button.callback = self.next_button_callback
            self.page_counter = Views.PaginatorPageCounter(self.page_counter_style, len(self.pages), self.current_page)
            self.page_counter.disabled=True
            self.add_item(self.previous_button)
            self.add_item(self.page_counter)
            self.add_item(self.next_button)
            self.update_buttons()
            if reply:
                self.message = await ctx.reply(embed=self.pages[self.initial_page], view=self, mention_author=False)
            else:
                self.message = await ctx.send(embed=self.pages[self.initial_page], view=self)
        
        def update_buttons(self):
            self.previous_button.disabled = self.current_page + 1 <= 1
            self.next_button.disabled = self.current_page + 1 >= self.total_page_count

        async def previous(self, interaction: discord.Interaction=None):
            if self.current_page == 0:
                self.current_page = self.total_page_count - 1
            else:
                self.current_page -= 1
            self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
            self.update_buttons()
            if interaction:
                return await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
            else:
                await self.message.edit(embed=self.pages[self.current_page], view=self)

        async def next(self, interaction: discord.Interaction=None):
            if self.current_page == self.total_page_count - 1:
                self.current_page = 0
            else:
                self.current_page += 1
            self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
            self.update_buttons()
            if interaction:
                return await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
            else:
                await self.message.edit(embed=self.pages[self.current_page], view=self)
            
        async def next_button_callback(self, interaction: discord.Interaction):
            if interaction.user != self.ctx.author:
                return await interaction.response.send_message("You are not the author of this command!", ephemeral=True)
            await self.next(interaction=interaction)

        async def previous_button_callback(self, interaction: discord.Interaction):
            if interaction.user != self.ctx.author:
                return await interaction.response.send_message("You are not the author of this command!", ephemeral=True)
            await self.previous(interaction=interaction)
        
        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            return await self.message.edit(view=self)
        
        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.author:
                return await interaction.response.send_message("You are not the author of this command!", ephemeral=True)
            return True

    class PaginatorPageCounter(discord.ui.Button):
        def __init__(self, style: discord.ButtonStyle, total_pages, initial_page):
            super().__init__(label=f"{initial_page + 1}/{total_pages}", style=style, disabled=True)
