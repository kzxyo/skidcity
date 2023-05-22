import discord
from discord import app_commands
from discord.ext import commands

class ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        print(f'synced {len(fmt)} commands to the current guild')
        return

    @app_commands.command(name="ping", description="ping command")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"...pong :ping_pong: `{round(self.bot.latency * 1000)}ms`")

async def setup(bot):
    await bot.add_cog(ping(bot))