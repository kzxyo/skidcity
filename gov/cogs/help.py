import discord, time, datetime, psutil, button_paginator as pg
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
from utility import Emotes, Colours

class help(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command(aliases=['h', 'commands'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx):
        commands = len(self.bot.commands)
        help_embed = discord.Embed(description=f"{Emotes.replyemote} - **View gov's commands using the menu below.**\n{Emotes.replyemote} - **Gov features [` {commands} `](https://govbot.gitbook.io/docs/) commands.**", color=Colours.standard)
        help_embed.set_author(name=f"{self.bot.user.name}'s command help menu", icon_url=f"{self.bot.user.display_avatar}")
        help_embed.add_field(name=f"{Emotes.infoemote} __Get started using Gov__", value=f"{Emotes.replyemote} - **Developer:** [**` asf#1337 `**](https://discord.com/users/983815296760549426)\n{Emotes.replyemote} - **Support:** [**` Invite `**](https://discord.gg/BcdZd7hPyn)")
        await ctx.reply(embed=help_embed)
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def support(self, ctx):
        support_embed = discord.Embed(description=f"*Visit our [**Support Server**](https://discord.gg/BcdZd7hPyn) to find out more.*", color=Colours.standard)
        support_embed.set_author(name=f"{self.bot.user.name}", icon_url=f"{self.bot.user.display_avatar}")
        support_button = Button(label="Support", url="https://discord.gg/BcdZd7hPyn")
        view = View()
        view.add_item(support_button)
        await ctx.reply(embed=support_embed, view=view)


async def setup(bot) -> None:
    await bot.add_cog(help(bot))