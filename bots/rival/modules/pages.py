import asyncio
import discord
from typing import Optional, Union, List
from discord.ext import commands
from discord import SelectOption


class SelectWithMultipleOptions(discord.ui.Select):
    def __init__(self, placeholder: str, options: List[str]):
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=len(options),
            options=[SelectOption(label=option.replace("_", " ").title(), value=option) for option in options],
        )


class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout: Optional[int] = None):
        super().__init__(timeout=timeout)
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(f"This is {self.ctx.author.mention}'s command, not yours.", ephemeral=True)
            return False
        return True


class Confirm(discord.ui.View):
    def __init__(self, context: commands.Context, timeout: Optional[int] = 300, user: Optional[Union[discord.Member, discord.User]] = None):
        super().__init__(timeout=timeout)
        self.value = None
        self.context = context
        self.user = user or self.context.author

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def yes(self, b, i):
        self.value = True
        self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def no(self, b, i):
        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot interact in other's commands.", ephemeral=True)
            return False
        return True


class Paginator(discord.ui.View):
    def __init__(self, ctx: commands.Context, embeds: List[discord.Embed]):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embeds = embeds
        self.current = 0
        self.value=None
        self.confirm = Confirm(context=ctx)

    async def edit(self, msg, pos):
        em = self.embeds[pos]
        em.set_footer(text=f"Page: {pos+1}/{len(self.embeds)}")
        await msg.edit(embed=em)

    @discord.ui.button(custom_id='bac', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
    async def bac(self, b, i):
        if self.current == 0:
            self.current += len(self.embeds)
            return await self.edit(i.message, self.current + len(self.embeds))
        await self.edit(i.message, self.current - 1)
        self.current -= 1

    @discord.ui.button(custom_id='stap',emoji="<:no:940723951947120650>", style=discord.ButtonStyle.red)
    async def stap(self, b, i):
        await i.message.delete()
        return self.value == False

    @discord.ui.button(custom_id='nex',emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
    async def nex(self, b, i):
        if self.current == len(self.embeds):
            self.current -= len(self.embeds) + 1
            return await self.edit(i.message, self.current - len(self.embeds)+1)
        await self.edit(i.message, self.current + 1)
        self.current += 1

    @discord.ui.button(custom_id='steal',emoji='<:yes:940723483204255794>', style=discord.ButtonStyle.green)
    async def steal(self, b, i):
        return self.value == True


    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            await interaction.response.defer()
            return True
        await interaction.response.send_message(ephemeral=True, embed=discord.Embed(description=f":warning: <@!{interaction.user.id}>: **You aren't the author of this embed**", color=int("faa61a", 16)))
