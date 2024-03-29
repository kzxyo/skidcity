import discord
from discord.ext import commands
from mgk.cfg import MGKCFG

class help(commands.Cog, description = None):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = {
            "info": "<:info:1141407920391733298>",
            "moderation": "<:mod:1141408209198911518>",
            "home": "<:home:1141408508764508210>",
            "config": "<:config:1142474527595573289>",
            "utility": "<:utility:1144731328521195640>",
            "youtube": "<:youtube:1178616197034553344>",
            "emoji": "<:emoji:1179710443267309588>",
            
        }

    @commands.command(extras={"Category": "Info"}, usage="help *command", help="View all commands or a command", aliases=["h"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help(self, ctx, *, command: str=None):
        if command:
            return await ctx.cmd(self.bot, command)
        a = list(self.bot.cogs)
        options = [discord.SelectOption(label="home", value="home", description="go to main page", emoji=self.emoji.get("home"))]
        for cog in a:
            if cog not in ["help", "dev", "events", "Jishaku", "ready", "guild"]:
                c = self.bot.get_cog(cog)
                options.append(discord.SelectOption(label=c.qualified_name, description=c.description, emoji=self.emoji.get(c.qualified_name)))
        
        e = discord.Embed(description = f"**{self.bot.user.name}** a simple bot with many features. If you need help join **[here]({MGKCFG.DSERVER})** and mention **{self.bot.get_user(self.bot.owner_ids[0])}**", color = ctx.get_color(1))
        e.set_thumbnail(url = self.bot.user.avatar.url)
        e.set_footer(text = "check select menu")
        
        select = discord.ui.Select(placeholder="select a category", min_values=1, max_values=1, options=options)
        
        async def callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return await ctx.error("this is not your message", interaction)
            a = list(self.bot.cogs)
            for c in a:
                cog = self.bot.get_cog(c)
                if select.values[0] == "home":
                    e = discord.Embed(description = f"**{self.bot.user.name}** a simple bot with many features. If you need help join **[here]({MGKCFG.DSERVER})** or **[here]({MGKCFG.MSERVER})** and mention **{self.bot.get_user(self.bot.owner_ids[0])}**", color = ctx.get_color(1))
                    e.set_thumbnail(url = self.bot.user.avatar.url)
                    e.set_footer(text = "check select menu")
                    await interaction.response.edit_message(embed=e)
                elif select.values[0] == cog.qualified_name:
                    cmds = ", ".join([(f"{c.parent.name} {c.name}" if c.parent else c.name) for c in cog.walk_commands() if not isinstance(c, commands.Group)])
                    if cog.qualified_name == "info":
                        cmds = "help, " + cmds
                    e = discord.Embed(description=cmds, color=ctx.get_color(1))
                    e.set_thumbnail(url = self.bot.user.avatar.url)
                    e.set_footer(text = "check select menu")
                    await interaction.response.edit_message(embed=e)
        
        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        await ctx.reply(embed=e, view=view)
        
async def setup(bot):
    await bot.add_cog(help(bot))