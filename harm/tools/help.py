import discord 
from discord.ext import commands

class HarmHelp(commands.HelpCommand):
    async def command_not_found(self, string: str) -> str:
        return f"{string} is not an actual command"
    
    async def send_command_help(self, command):
        if command.hidden: 
            return 
        
        embed = discord.Embed(
           color=self.context.bot.color, 
           title=command.qualified_name, 
           description=command.help.capitalize()
        ) 
        embed.set_author(
           name=self.context.bot.user.name, 
           icon_url=self.context.bot.user.display_avatar.url
        )
        embed.add_field(
           name="permissions", 
           value=command.brief or "any"
        )
        embed.add_field(
           name="usage", 
           value=f"```{self.context.clean_prefix}{command.qualified_name} {' '.join([f'[{a}]' for a in command.clean_params]) if command.clean_params != {} else ''}\n{command.usage or ''}```",
           inline=False
        )
      
        await self.context.send(embed=embed)

    async def send_group_help(self, group) -> None:
        embeds = []
        bot = self.context.bot
        i=0
        for command in group.commands: 
         i+=1 
         embeds.append(
            discord.Embed(
                color=bot.color, 
                title=command.qualified_name, 
                description=command.help.capitalize()
            ).set_author(
                name=bot.user.name, 
                icon_url=bot.user.display_avatar.url
            ).add_field(
                name="usage", 
                value=f"```{command.qualified_name} {' '.join([f'[{a}]' for a in command.clean_params]) if command.clean_params != {} else ''}\n{command.usage or ''}```",
                inline=False
            ).set_footer(text=f"{i}/{len(group.commands)}")
         )
         
        await self.context.paginator(embeds)

    async def send_bot_help(self, mapping):
        embeds = [
            discord.Embed(
                title="harm menu",
                color=self.context.bot.color,
                description=f">>> **Prefix:** `;`\n**Commands:** {len(set(self.context.bot.walk_commands()))}\n[**Add me**]({self.context.bot.invite_url})"
            )
        ]

        for shit in mapping.items(): 
          if shit[0]:  
            if not shit[0].qualified_name.lower() in ["owner", "jishaku"]:
                    cmds = '\n'.join(list(map(lambda c: c.qualified_name, set(shit[0].walk_commands()))))
                    embeds.append(
                        discord.Embed(
                            color=self.context.bot.color, 
                            description=f">>> {cmds}"
                        ).set_author(name=shit[0].qualified_name.lower())
                    )

        await self.context.paginator(embeds)       