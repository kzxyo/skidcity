import discord
from typing import Any
from utilities import utils
from utilities.baseclass import Vile
from datetime import datetime
from discord.ext import commands


class UserEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot


    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):

        if self.bot.cache.nodata.get(before.id, 1) == True:
            if before.name != after.name:
                await self.bot.db.execute(
                    'INSERT INTO names (user_id, name, timestamp) VALUES (%s, %s, %s)',
                    before.id, str(before), int(datetime.now().timestamp())
                )

                if any(list(map(lambda c: c.isalpha() is False, str(before)[:-5].replace(' ', '')))) is False:
                    for guild in self.bot.guilds:
                        if guild.id in self.bot.cache.tracker:
                            for entry in utils.filter(self.bot.cache.tracker[guild.id], lambda e: e['discriminator'] == before.discriminator):
                                channel = guild.get_channel(entry['channel_id'])
                                
                                if channel:
                                    if channel.permissions_for(guild.me).send_messages is True:
                                        await channel.send(f'**Available username:** {before}')


async def setup(bot: Vile):
    await bot.add_cog(UserEvents(bot))
