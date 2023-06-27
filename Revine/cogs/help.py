# This source code is 100% original, any contents will be credited in revine's credits command. Created by fsb#1337 & report#0001

import discord, time, datetime, psutil
from discord.ext import commands
from typing import Union
from discord.ui import View, Button, Select
from classes import Colors, Emotes, Images

class help(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

# --------------------------------------------------------------------------------------- Help Command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx):
        embed = discord.Embed(description="> - *View revine's commands using the menu below.*\n> - *Or view the commands on our [**` Docs `**](https://revine.gitbook.io/docs/)*", color=Colors.normal)
        embed.set_author(name="Revine's Command Menu", icon_url=f"{self.bot.user.display_avatar}", url="https://discord.gg/revine")
        embed.add_field(name=f"{Emotes.reply_emote} {Emotes.support_emote} Need Extra Help?", value=f"> - Visit our [**` Support Server `**](https://discord.gg/revine) on how to get started\n> - Developers: [**fsb#0001**](https://discord.com/users/983815296760549426) & [**report#0001**](https://discord.com/users/1069726264983818340).")
        await ctx.send(embed=embed ,view=SelectView())

class Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Main Menu", description="Go back to the main menu."),
            discord.SelectOption(label="Information", description="View revine's information commands."),
            discord.SelectOption(label="Moderation", description="View revine's moderation commands."),
            discord.SelectOption(label="Image", description="View revine's image commands."),
            discord.SelectOption(label="Miscellaneous", description="View revine's miscellaneous commands."),
            discord.SelectOption(label="Anti-Raid", description="View revine's anti-raid commands.")
            ]

        super().__init__(placeholder="Revine's Command Modules",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Main Menu":
            e1 = discord.Embed(description="> - *View revine's commands using the menu below.*\n> - *Or view the commands on our [**` Docs `**](https://revine.gitbook.io/docs/)*", color=Colors.normal)
            e1.set_author(name="Revine's Command Menu", icon_url=f"{Images.revine_pfp}", url="https://discord.gg/revine")
            e1.add_field(name=f"{Emotes.reply_emote} {Emotes.support_emote} Need Extra Help?", value=f"> - Visit our [**` Support Server `**](https://discord.gg/revine) on how to get started\n> - Developers: [**fsb#0001**](https://discord.com/users/983815296760549426) & [**report#0001**](https://discord.com/users/1069726264983818340).")
            await interaction.response.edit_message(embed=e1)
        elif self.values[0] == "Information":
            e2 = discord.Embed(title="Information Commands", description="The commands list of information commands is in development.", color=Colors.normal)
            e2.set_author(name="Revine's Command Menu", icon_url=f"{Images.revine_pfp}", url="https://discord.gg/revine")
            await interaction.response.edit_message(embed=e2)
        elif self.values[0] == "Moderation":
            e3 = discord.Embed(title="Moderation Commands", description="The commands list of moderation commands is in development.", color=Colors.normal)
            e3.set_author(name="Revine's Command Menu", icon_url=f"{Images.revine_pfp}", url="https://discord.gg/revine")
            await interaction.response.edit_message(embed=e3)
        elif self.values[0] == "Image":
            e4 = discord.Embed(title="Image Commands", description="The commands list of image commands is in development.", color=Colors.normal)
            e4.set_author(name="Revine's Command Menu", icon_url=f"{Images.revine_pfp}", url="https://discord.gg/revine")
            await interaction.response.edit_message(embed=e4)
        elif self.values[0] == "Miscellaneous":
            e5 = discord.Embed(title="Miscellaneous Commands", description="The commands list of miscellaneous commands is in development.", color=Colors.normal)
            e5.set_author(name="Revine's Command Menu", icon_url=f"{Images.revine_pfp}", url="https://discord.gg/revine")
            await interaction.response.edit_message(embed=e5)
        elif self.values[0] == "Anti-Raid":
            e6 = discord.Embed(title="Anti-Raid Commands", description="The commands list of anti-raid commands is in development.", color=Colors.normal)
            e6.set_author(name="Revine's Command Menu", icon_url=f"{Images.revine_pfp}", url="https://discord.gg/revine")
            await interaction.response.edit_message(embed=e6)

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(Select())
        
async def setup(bot) -> None:
    await bot.add_cog(help(bot))