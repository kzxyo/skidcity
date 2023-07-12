from typing import Any, Callable, Coroutine, List, Mapping, Optional
from discord.ext.commands import HelpCommand
from utilities.managers import Wrench
from discord import Embed
from discord.ext.commands.core import Command
from utilities import config
import datetime

class Help(HelpCommand):
    def get_command_signature(self, command):
        return "%s%s %s" % (
            self.context.clean_prefix,
            command.qualified_name,
            command.signature,
        )
    
    async def send_bot_help(self, mapping: Mapping[Wrench | None, List[Command[Any, Callable[..., Any], Any]]]) -> Coroutine[Any, Any, None]:
        await self.context.send('https://lair.one/commands')
        return await super().send_bot_help(mapping)
    
    async def send_command_help(self, command: Command[Any, Callable[..., Any], Any]) -> Coroutine[Any, Any, None]:
        embed = Embed(
            color=config.Color.main, timestamp=datetime.datetime.now()
        )
        command_perms = command.perms
        embed.set_author(name=command.name, icon_url=self.context.bot.user.avatar.url)
        embed.description = f'> {command.brief}'
        embed.add_field(
            name='Aliases',
            value=", ".join(command.aliases) if command.aliases else None,
            inline=True
        )
        embed.add_field(
            name='Command Parameters',
            value=', '.join(command.params) if command.params else None,
            inline=True
        )
        embed.add_field(
            name='Required Permissions',
            value=", ".join(command_perms).replace('_', " ").title() if command_perms else "Send Messages",
        )
        embed.add_field(
            name='Command Syntax',
            value=f'```{self.get_command_signature(command)}```',
            inline=False
        )
        embed.set_footer(
            text=f"Command Module: {command.cog_name}",
        )
        return await self.context.reply(embed=embed)