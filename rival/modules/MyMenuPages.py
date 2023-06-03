import discord
from discord import ui
from discord.ext import menus


color=0x303135


class MySource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        embed = discord.Embed(title="___***Rival Commands***___",url="https://pastebin.com/raw/njwQ7z5g",
            description=f"{entries}", 
            color=0x303135
        )
        embed.set_footer(text=f"\nPrefix = !\n\n{menu.current_page + 1}/{self.get_max_pages()}")
        return embed

class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(ephemeral=True, embed=discord.Embed(description=f":warning: <@!{interaction.user.id}>: **You aren't the author of this embed**", color=int("faa61a", 16)))
        else:   
            await interaction.response.defer()      
            return interaction.user == self.ctx.author


    @ui.button(emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
    async def before_page(self, button, interaction):
        if self.current_page == 0:
            await self.show_page(self._source.get_max_pages() - 1)
        else:
            await self.show_checked_page(self.current_page - 1)
        #await interaction.response.defer()


    @ui.button(emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
    async def next_page(self, button, interaction):
        if self.current_page == self._source.get_max_pages() -1:
            await self.show_page(0)
        else:
            await self.show_checked_page(self.current_page + 1)
        #await interaction.response.defer()
