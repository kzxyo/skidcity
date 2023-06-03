import discord
from discord.ext import commands
import os

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        help="returns the bot ping",
        usage="ping",
        aliases=["pong", "latency", "ms", "lat"]
    )
    async def ping(self, ctx):
        embed = discord.Embed(color=self.bot.color, description=f"*pings a hot women*: {round(self.bot.latency * 1000)}ms")
        msg = await ctx.reply(embed=embed)


    @commands.command(
        help="returns all cmds",
        usage="help",
        aliases=["h", 'cmds', 'cmd']
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx, command: str = None):
        if command is None:
            categories = {}
            for category in os.listdir("cogs"):
                if category == "__pycache__":
                    continue
                commands = []
                for file in os.listdir(f"cogs/{category}"):
                    if file == "__pycache__":
                        continue
                    for command in ctx.bot.get_cog(file[:-3]).get_commands():
                        if isinstance(command, discord.ext.commands.Group):
                            for subcommand in command.commands:
                                if subcommand.hidden:
                                    continue
                                commands.append(f"{command.name} {subcommand.name}")
                        if command.hidden:
                            continue
                        commands.append(command.name)

                    if commands:
                        categories[category] = commands

            pages = [
                discord.Embed(
                    title="",
                    description="> **To see the commands use the button's below**",
                    color=self.bot.color
<<<<<<< HEAD
                ).set_footer(text="2.20.1 pretend rewrite version").set_author(name="pretend", icon_url=self.bot.user.avatar.url).set_thumbnail(url=self.bot.user.avatar.url).add_field(name="** **", value="> ** If you wanna join in the support serever click [here](https://discord.gg/whA2tm9yVb)**")
=======
                ).set_footer(text="2.20.1 pretend rewrite version").set_author(name="pretend", icon_url=self.bot.user.avatar.url).set_thumbnail(url=self.bot.user.display_avatar.url)
>>>>>>> 0767d3853d658e70d0942d1032be273f77ff0c9a
            ]
            for category in categories:
                embed = discord.Embed(
                    title=f"category: {category}",
                    description="```fix\n" + ", ".join(categories[category]) + "```",
                    color=self.bot.color
                )
                pages.append(embed)

            await self.bot.paginator(ctx, pages)
            
        else:
            command = self.bot.get_command(command)
            if command is None:
                for cog in self.bot.cogs:
                    for subcommand in self.bot.get_cog(cog).get_commands():
                        if isinstance(subcommand, discord.ext.commands.Group):
                            for subsubcommand in subcommand.commands:
                                if subsubcommand.name == command:
                                    command = subsubcommand
                                    break
                        if subcommand.name == command:
                            command = subcommand
                            break

                return await ctx.reply(embed=discord.Embed(description="Command not found", color=self.bot.color))
            embed = discord.Embed(
                title=f"command: {command.name}", description=command.help or "N/A", color=self.bot.color)
            if command.aliases:
                embed.add_field(name="Aliases", value="`" +
                                "`, `".join(command.aliases) + "`")
            if command.usage:
                embed.add_field(name="Usage", value=command.usage)
            if command.cooldown:
                embed.set_footer(
                    text=f"Cooldown: {command.cooldown.rate} uses per {int(command.cooldown.per)}s")
            if isinstance(command, discord.ext.commands.Group):
                subcommands = []
                for subcommand in command.commands:
                    if subcommand.usage:
                        subcommands.append(subcommand.usage)
                    else:
                        subcommands.append(subcommand.name)
                embed.add_field(name="Subcommands", value="```fix\n" + "\n".join(subcommands) + "```", inline=False)
            await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(help(bot))