import abc
import discord, time, datetime, psutil, aiohttp, io
from discord.ext import commands
from typing import Union
from discord.ui import View, Button, Select
from classes import Colors, Emotes
from modules import utils

class spotify(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot   
            
    @commands.command(aliases = ['spotify', "sp"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def spotifytrack(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        spotify_result = next((activity for activity in user.activities if isinstance(activity, discord.Spotify)), None)
        if user == ctx.author:
                if spotify_result is None:
                    embed = discord.Embed(description=f"{Emotes.spotify_emote} {ctx.author.mention}: **You are not currently listening to Spotify.**", color=Colors.spotify)
                    embed.set_footer(icon_url="https://freeimage.host/i/spotify.HMt8JIa", text="Check that your spotify is playing or check your connections.")
                    await ctx.reply(embed=embed)
                    return
        if user == user:
            if spotify_result is None:
                embed = discord.Embed(description=f"{Emotes.spotify_emote} {ctx.author.mention}: **They are not currently listening to Spotify.**", color=Colors.spotify)
                embed.set_footer(icon_url="https://freeimage.host/i/spotify.HMt8JIa", text="They may not have there spotify connected.")
                await ctx.reply(embed=embed)
            else:
                artist = spotify_result.artist.replace(";", ",")
                loading  = discord.Embed(description=f"{ctx.author.mention}: Loading the current spotify song...", color=Colors.normal)
                await ctx.send(embed=loading, delete_after=3.0)
                report = f"https://api.jeyy.xyz/discord/spotify?title={spotify_result.title}&cover_url={spotify_result.album_cover_url}&duration_seconds={spotify_result.duration.seconds}&start_timestamp={spotify_result.created_at.timestamp()}&artists={', '.join(spotify_result.artists).replace(',', '%2C').replace(' ', '%20')}"
                report = await utils.file(report, "screw.png")
                embed = discord.Embed(description=f"**Track:** [***` {spotify_result.title} `***]({spotify_result.track_url})\n**Artist:** ***` {artist} `***\n**Album:** ***` {spotify_result.album} `***", color=Colors.spotify)
                embed.set_author(name=f"{user.name}#{user.discriminator} is listening to:", icon_url=f"{user.display_avatar}")
                embed.set_thumbnail(url=f'{spotify_result.album_cover_url}')
                embed.set_image(url="attachment://screw.png")
                embed.set_footer(icon_url="https://freeimage.host/i/HMt8JIa", text=f"category: spotify・revine ©️ 2023")
                trackurl = Button(label="Track URL", url=f"{spotify_result.track_url}")
                view = View()
                view.add_item(trackurl)
                embed = await ctx.reply(view=view, file=report, embed=embed, mention_author=False)
    
async def setup(bot):
    await bot.add_cog(spotify(bot))