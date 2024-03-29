import discord, asyncio, logging
from discord.ext import commands
from mgk.cfg import MGKCFG, CLR
from modules.errors import *

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("rl handler")

    async def prefixes(self, message):
        p = MGKCFG.DEFAULT_PREFIX
        r = await self.bot.db.fetchone("SELECT prefix FROM prefix WHERE guild = %s", (message.guild.id,))
        guild = r['prefix'] if r is not None else p
        r = await self.bot.db.fetchone("SELECT prefix FROM selfprefix WHERE user = %s", (message.author.id,))
        user = r['prefix'] if r is not None else guild
        prefix = []
        if guild: prefix.append(guild)
        if user: prefix.append(user)
        return prefix
    @commands.Cog.listener("on_message")
    async def mention(self, message: discord.Message):
        if message.author != message.author.bot or message.author != self.bot.user:
            formats = [
            f"<@{self.bot.user.id}>",
            f"<@!{self.bot.user.id}>",
            f"<@{self.bot.user.id}> ",
            f"<@!{self.bot.user.id}> "
            ]
            if message.content in formats:
                prefix = await self.prefixes(message)
                await message.reply(embed=discord.Embed(description=f"Your prefix is **{prefix[1]}** and guild prefix is **{prefix[0]}**", color=CLR.default))
                
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # rl handler
        if isinstance(error, commands.CommandOnCooldown):
            rl = round(error.retry_after, 2)
            if error.retry_after > 60:
                await asyncio.sleep(error.retry_after)
            else:
                await asyncio.sleep(error.retry_after / 2)
            #self.log.warning(f"{ctx.author.name} ({ctx.author.id}) cause a rate limit on command {ctx.command.name} on guild with id {ctx.guild.id}")
            await ctx.reinvoke()
        elif isinstance(error, Moderate):
            await ctx.error(error)
        elif isinstance(error, Perm):
            await ctx.error(error)
        elif isinstance(error, Var):
            await ctx.error(error)

async def setup(bot):
    await bot.add_cog(events(bot))
