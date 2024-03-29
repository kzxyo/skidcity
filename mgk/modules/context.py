import discord, typing, time, asyncio, requests
from typing import Optional, Union
from discord.ext import commands
from mgk.cfg import CLR, E
from modules.paginator import Paginator
from discord import Embed
from mgk.cfg import API
from translate import Translator
from langdetect import detect

class context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def get_color(self, clr: str):
        if clr == 1:
            return CLR.DEFAULT
        elif clr == 2:
            return CLR.RED
        elif clr == 3:
            return CLR.GREEN
        else:
            if not clr.startswith("0x"):
                clr = "0x" + clr
            return discord.Color.from_str(clr)
        
    async def error(self, error: str, interaction: Optional[discord.Interaction] = None):
        if interaction:
            return await interaction.response.send_message(embed=discord.Embed(description=f"{E.err}** {self.author.mention}** - {error}", color=self.get_color(2)), ephemeral = True)
        return await self.reply(embed=discord.Embed(description=f"{E.err}** {self.author.mention}** - {error}", color=self.get_color(2)))

    async def succes(self, msg: str):
        return await self.reply(embed=discord.Embed(description=f"{E.smile}** {self.author.mention}** - {msg}", color=self.get_color(3)))
    
    async def normal(self, msg: str, em: discord.PartialEmoji=None):
        if em is None:
            em = E.ok

        return await self.reply(embed=discord.Embed(description=f"{em}** {self.author.mention}** - {msg}", color=self.get_color(1)))
        
    async def check(self, msg: str, view=None):
        await self.reply(embed=discord.Embed(description=f"{E.warning}** {self.author.mention}** - {msg}", color=self.get_color(1)), view=view)

    async def cmd(self, bot, cmd: str):
        command = bot.get_command(cmd)
        if bool(command) == False or command.hidden:
            return await self.error(f"this command does not exist")
        e = discord.Embed(color=self.get_color(1))
        parent = getattr(command.parent, "name", None)
        t = f"{parent} {command.name}" if parent else command.name
        a = ", ".join(command.aliases)
        e.title = f"{t} ({a})" if command.aliases else t
        if command.help: e.description = f"{command.help}.\n\n`*` - **optional**\n`!` - **required**\n`**` - **can have multiple values**"
        if command.usage: e.set_footer(text=f"{self.prefix}{command.usage}", icon_url = "https://media.discordapp.net/attachments/1141383835746050139/1141383913005125662/command-line_1.png")
        if getattr(command, "extras", None): e.add_field(name="other informations", value=", ".join([f"``{key}``: **{value}**" for key, value in command.extras.items()]), inline=False)
        await self.reply(embed=e)
        
    def cmdembed(self, bot, cmd: str):
        command = bot.get_command(cmd)
        if command.hidden:
            pass
        e = discord.Embed(color=self.get_color(1))
        parent = getattr(command.parent, "name", None)
        t = f"{parent} {command.name}" if parent else command.name
        a = ", ".join(command.aliases)
        e.title = f"{t} ({a})" if command.aliases else t
        if command.help: e.description = f"{command.help}.\n\n`*` - **optional**\n`!` - **required**\n`**` - **can have multiple values**"
        if command.usage: e.set_footer(text=f"{self.prefix}{command.usage}", icon_url = "https://media.discordapp.net/attachments/1141383835746050139/1141383913005125662/command-line_1.png")
        if getattr(command, "extras", None): e.add_field(name="other informations", value=", ".join([f"``{key}``: **{value}**" for key, value in command.extras.items()]), inline=False)
        return e
        
    async def embed(self, title: str=None, *, description: str):
        embed = discord.Embed(description=description, color=self.get_color(1))
        if title:
            embed.title = title
        return await self.reply(embed=embed)
    
    async def paginate(self, count: bool, embeds: list):
        if len(embeds) == 1:
            if count:
                e = embeds[0]
                e.set_footer(text="1/1")
                await self.reply(embed=e)
            else:
                await self.reply(embed=embeds[0])
        else:
            if count:
                for i, embed in enumerate(embeds):
                    embed.set_footer(text=f"{i + 1}/{len(embeds)}")
                    i += 1
            view = Paginator(self, embeds)
            await self.reply(embed=embeds[0], view=view)
            
    async def gcmd(self, bot, group: str):
        g = bot.get_command(group)
        if g:
            cmds = [f"{subcommand.parent.name} {subcommand.name}" for subcommand in g.commands]
            embeds = []
            for c in cmds:
                embeds.append(self.cmdembed(bot, c))
            await self.paginate(False, embeds)
            
    def check_member(self, member: discord.Member, guild: discord.Guild):
        m = guild.get_member(member.id)
        bot = guild.get_member(self.bot.user.id)
        author = guild.get_member(self.author.id)
        if m == bot:
            return f"i cant moderate myself"
        elif m == author:
            return "you cant moderate yourself"
        elif guild.owner == m and author != guild.owner:
            return "this user is server owner"
        elif bot.top_role < m.top_role:
            return f"i dont have permission to moderate {m.mention}"
        elif m.top_role > author.top_role:
            return f"{m.mention} is higher than you"
        elif m.id in self.bot.owner_ids:
            return f"i cant moderate developers"
        else:
            return None
    
    def translate(self, to_lang: str, *, arg: str):
        lang = detect(arg).title()
        translator= Translator(to_lang=to_lang)
        src = translator.translate(arg)
        return src, lang
    
