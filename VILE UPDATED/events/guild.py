import discord, difflib, random
from typing import Any
from utilities import utils
from utilities.baseclass import Vile
from discord.ext import commands


class GuildEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        
        if not guild.chunked:
            await guild.chunk(cache=True)
            
        await self.bot.get_channel(1002618168897970197).send(
            f'joined **{guild.name}** (`{guild.id}`), owned by **{guild.owner}**, **{len(guild.members)}** members'
        )

        if len(guild.members) < 20 and not await self.bot.db.fetch("""SELECT * FROM authorization WHERE guild_id = %s""",guild.id):
            if guild.owner_id not in self.bot.owner_ids:
                channels = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages == True]
                if channels:
                    await random.choice(channels).send(
                        embed=discord.Embed(
                            color=self.bot.color, 
                            description=f'{self.bot.fail} {self.bot.user.mention}**:** leaving server; server has less than 20 members'
                        )
                    )

                await guild.leave()

        if guild.id in self.bot.cache.global_bl['guilds'] or guild.owner_id in self.bot.cache.global_bl['users']:
            await guild.leave()


async def setup(bot: Vile):
    await bot.add_cog(GuildEvents(bot))
