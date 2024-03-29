import discord, subprocess
from discord.ext import commands
from modules.func import general
from mgk.cfg import MGKCFG, CLR, E


class dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pkill = ["pkill", "-f", "main.py"]
        
    @commands.command(aliases=['restart', 'rs'], hidden=True)
    @general.ownerOnly()
    async def pkill(self, ctx):
        await ctx.succes("your main.py is killed!")
        ch = self.bot.get_channel(1147914717365534831)
        await ch.send(embed=discord.Embed(description=f"{E.L} - **Restarting...**", color=CLR.red))
        subprocess.run(self.pkill, check=True)
        
    @commands.command(hidden=True)
    @general.ownerOnly()
    async def st(self, ctx):
        await ctx.succes("status was updated")
        await self.bot.change_presence(activity=discord.CustomActivity(name=f"{self.bot.cmds}{MGKCFG.ACTIVITY}"))
        
    @commands.command(hidden=True)
    @general.ownerOnly()
    async def neofetch(self, ctx):
        from modules.neofetch import neofetch
        await ctx.reply(f"```ansi {neofetch()}```")

async def setup(bot):
    await bot.add_cog(dev(bot))
