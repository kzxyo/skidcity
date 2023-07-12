from discord.ui import View, Button, button
from discord import Member, Interaction, ButtonStyle, Embed

class Confirm(View):
    def __init__(self, value: bool = False, invoker: Member = None):
        self.value = value
        self.invoker = invoker
        self.done = "<:34:1066028256190541894>"
        self.fail = "<:35:1066028249592905789>"
        super().__init__(timeout=30)

    async def confirmation(self, interaction: Interaction, confirm: bool):
        if interaction.user.id != self.invoker.id:
            return await interaction.response.send_message(
                ephemeral=True,
                embed=Embed(
                    color=0xFAA71B,
                    description=f"<:emoji_7:1067814032607809667> {interaction.user.mention}: you are not the **author** of this embed.",
                ),
            )
        else:
            await interaction.response.defer()
        self.value = confirm
        self.stop()

    @button(
        emoji="<:index2:1081651965857108041>", style=ButtonStyle.secondary
    )
    async def confirm(
        self, interaction: Interaction, button: Button
    ):
        await self.confirmation(interaction, True)

    @button(
        emoji="<:x_:1104809324108337193>", style=ButtonStyle.secondary
    )
    async def cancel(self, interaction: Interaction, button: Button):
        await self.confirmation(interaction, False)