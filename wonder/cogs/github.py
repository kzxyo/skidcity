import json
import discord
import aiohttp
import datetime
import giphy_client

from pyfiglet import Figlet
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import ui

fig = Figlet(font='standard')  # Change fonts here, try 'banner' for readability
fig_small = Figlet(font='small')

async def _fetch(url: str):
	""" function to fetch data from api in asynchronous way """
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			if response.status == 200:
				return await response.json()

class github(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "github", description = "Shows information on a Github user", usage = "$github <username>")
    async def github(self, ctx, username: str):
        try:
            git_api = f'https://api.github.com/users/{username}'
            async with ctx.typing():
                    user_data = await _fetch(git_api)
                    embed = discord.Embed(title = f"{username}", description = f"{user_data['bio']}", colour=0x2F3136)
                    embed.add_field(name = "**Overview**", value = f"""**Public repos:** {user_data['public_repos']}
**Public gists:** {user_data['public_gists']}""")
                    embed.add_field(name = "**Dates**", value = f"""**Created at:** {user_data['created_at'][:10]}
**Updated at:** {user_data['updated_at'][:10]}""", inline = False)
                    embed.add_field(name = "**Statistics**", value = f"""**Followers:** {user_data['followers']}
**Following:** {user_data['following']}""", inline = False)
                    embed.set_thumbnail(
                        url= user_data['avatar_url'])
                    embed.set_author(
                        name = ctx.message.author.name, icon_url = ctx.message.author.display_avatar
                    )
                    embed.url = (f"https://github.com/{username}")
                    embed.set_footer(text = "Github", icon_url = "https://cdn.discordapp.com/emojis/998324589832716298.webp?size=4096&quality=lossless")
                    await ctx.reply(embed=embed)
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(github(bot))