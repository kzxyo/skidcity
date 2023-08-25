import discord


class Confirm(discord.ui.View):
    def __init__(self, message: discord.Message, invoker: discord.Member = None) -> None:
        super().__init__(timeout=None)
        self.value = False
        self.message = message
        self.invoker = invoker

    
    async def on_timeout(self) -> None:
        await self.message.edit(view=None)


    @discord.ui.button(
        style=discord.ButtonStyle.grey, 
        emoji="<:v_done:1067033981452828692>"
    )
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.confirmation(interaction, True)


    @discord.ui.button(
        style=discord.ButtonStyle.grey, 
        emoji="<:v_warn:1067034029569888266>"
    )
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.confirmation(interaction, False)


    async def confirmation(self, interaction: discord.Interaction, value: bool) -> None:
        
        if interaction.user.id != self.invoker.id:
            return
            
        await interaction.response.defer()
        await self.message.edit(view=None)
        self.value = value
        self.stop()
