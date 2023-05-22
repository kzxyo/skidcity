import discord 
from discord.ext import commands

bot.lavanode = [
    {
        'host': 'us1.lavalink.creavite.co',
        'port': 20080,
        'password': 'auto.creavite.co'
        'secure': 'false',
    }
]

@bot.event
aync def on_ready():
    print('music ready')
    bot.load_extension('dismusic')

async def setup(bot) -> None: 
    await bot.add_cog(events(bot))   