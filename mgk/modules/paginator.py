import discord
from discord.ext import commands

class Paginator(discord.ui.View):
    def __init__(self, ctx: commands.Context, embeds):
        super().__init__()
        self.embeds = embeds
        self.ctx = ctx
        self.current_page = 0

    async def on_timeout(self):
        self.stop()

    @discord.ui.button(emoji="<:prev:1144535917546184815>", style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id: return
        if self.current_page > 0:
            self.current_page -= 1
        else:
            self.current_page = len(self.embeds) - 1
        await interaction.response.edit_message(embed=self.embeds[self.current_page])
            
    @discord.ui.button(emoji="<:next:1144536429863649300>", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id: return
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
        else:
            self.current_page = 0
        await interaction.response.edit_message(embed=self.embeds[self.current_page])
