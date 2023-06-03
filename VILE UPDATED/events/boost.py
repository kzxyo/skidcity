import discord, arrow
from utilities import utils
from utilities.baseclass import Vile
from discord.ext import commands


class BoostEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot

    
    @commands.Cog.listener()
    async def on_boost(self, member: discord.Member):

        if self.bot.cache.boostchannel.get(member.guild.id) is not None:
            if self.bot.cache.boostmessage.get(member.guild.id) is not None:
                channel = self.bot.cache.boostchannel[member.guild.id]
                msg = self.bot.cache.boostmessage[member.guild.id]
                
                await member.guild.get_channel(channel).send(
                    **await utils.to_object(await utils.embed_replacement(member, msg))
                )


async def setup(bot: Vile):
    await bot.add_cog(BoostEvents(bot))