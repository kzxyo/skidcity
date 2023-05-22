import abc
import discord, time, datetime, psutil, aiohttp, io, button_paginator as pg
from discord.ext import commands
from typing import Union
from discord.ui import View, Button, Select
from utility import Colours, Emotes
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
                    embed = discord.Embed(description=f"{Emotes.spotifyemote} {ctx.author.mention}: **You are not currently listening to Spotify.**", color=Colours.spotify)
                    await ctx.reply(embed=embed)
                    return
        if user == user:
            if spotify_result is None:
                embed = discord.Embed(description=f"{Emotes.spotifyemote} **{user.mention} is currently not listening to Spotify.**", color=Colours.spotify)
                await ctx.reply(embed=embed)
            else:
                artist = spotify_result.artist.replace(";", ",")
                loading  = discord.Embed(description=f"**{Emotes.spotifyemote} {ctx.author.mention}: Loading the current song...**", color=Colours.standard)
                await ctx.send(embed=loading, delete_after=2.7)
                spotify = f"https://api.jeyy.xyz/discord/spotify?title={spotify_result.title}&cover_url={spotify_result.album_cover_url}&duration_seconds={spotify_result.duration.seconds}&start_timestamp={spotify_result.created_at.timestamp()}&artists={', '.join(spotify_result.artists).replace(',', '%2C').replace(' ', '%20')}"
                spotify = await utils.file(spotify, "spotify.png")
                embed = discord.Embed(color=Colours.spotify)
                embed.set_author(name=f"{user.name}#{user.discriminator} is currently listening to:", icon_url=f"{user.display_avatar}")
                embed.set_image(url="attachment://spotify.png")
                trackurl = Button(label="Track URL", url=f"{spotify_result.track_url}")
                view = View()
                view.add_item(trackurl)
                embed = await ctx.reply(view=view, file=spotify, embed=embed, mention_author=False)
    
async def setup(bot):
    await bot.add_cog(spotify(bot))
