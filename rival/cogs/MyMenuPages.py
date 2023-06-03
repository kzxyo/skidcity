import discord
from discord import ui
from discord.ext import menus


color=0x303135

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

    @ui.button(style=discord.ButtonStyle.green, label="Yes")
    async def confirm(self, interaction:discord.Interaction, button:discord.ui.Button):
        await self.confirmation(interaction, True)

    @ui.button(style=discord.ButtonStyle.red, label="No")
    async def cancel(self, interaction:discord.Interaction, button: discord.ui.Button):
        await self.confirmation(interaction, False)

    async def on_timeout(self):
        #await view.clear_items()
        return None

    async def confirmation(self, interaction:discord.Interaction, confirm:bool):
        if confirm:
            if not interaction.user.id == self.ctx.author.id:
                await interaction.response.send_message(embed=discord.Embed(description=f"<:warn:940732267406454845> {interaction.user.mention}: **You cannot interact with this**", color=int("faa61a", 16)), ephemeral=True)
                return
        else:
            if not interaction.user.id == self.ctx.author.id:
                if interaction.user.id == self.ctx.author.id:
                    pass
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"<:warn:940732267406454845> {interaction.user.mention}: **You cannot interact with this**", color=int("faa61a", 16)), ephemeral=True)
                    return
        if confirm:
            await interaction.response.defer()
        else:
           await interaction.response.defer()
        return self.current_page
        self.stop()

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
