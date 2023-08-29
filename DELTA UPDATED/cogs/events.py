import discord 
from discord.ext import commands

class events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        embed = discord.Embed(color=0x2f3136, description=f"joined **{guild.name}**, owned by **{guild.owner}** with **{guild.member_count}** members")
        embed.set_footer(text=f"ID: {guild.id}")
        await self.bot.get_channel(1136729286313787504).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
       embed = discord.Embed(color=0x2f3136, description=f"left **{guild.name}**, owned by **{guild.owner}** with **{guild.member_count}** members")
       embed.set_footer(text=f"ID: {guild.id}")
       await self.bot.get_channel(1136729286313787504).send(embed=embed)
     
    
async def setup(bot) -> None: 
    await bot.add_cog(events(bot))        