import typing, psutil, discord, datetime, traceback
from discord.ext import commands
from utilities.context import Context
from . import utils


async def confirm(ctx: Context, message: discord.Message) -> bool:
    view = Confirm(message=message, invoker=ctx.author)
    await message.edit(view=view)
    await view.wait()
    return view.value

class Confirm(discord.ui.View):
    def __init__(self, message: discord.Message, invoker: discord.Member = None):
        super().__init__(timeout=30)
        self.value = False
        self.message = message
        self.invoker = invoker

    
    async def on_timeout(self):
        await self.message.edit(view=None)


    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:v_done:1067033981452828692>')
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.confirmation(interaction, True)


    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:v_warn:1067034029569888266>')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.confirmation(interaction, False)


    async def confirmation(self, interaction: discord.Interaction, confirm: bool) -> None:
        
        if confirm:
            if interaction.user.id != self.invoker.id:
                return
            await interaction.response.defer()
        else:
            await interaction.response.defer()
        
        for c in self.children:
            c.disabled = True

        await interaction.message.edit(view=None)
        self.value = confirm
        self.stop()