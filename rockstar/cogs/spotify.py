import discord, aiohttp, button_paginator as pg, time
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote
from discord.ui import View, Button, Select
from modules import utils

class spotify(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot   
            
    @commands.command(aliases=['sptrack', 'sp', 'spotifytrack', 'spotifysong', 'currentspotify'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def spotify(self, ctx, user: Union[discord.Member, discord.User]=None):
        user = user or ctx.author
        spotify_result = next((activity for activity in user.activities if isinstance(activity, discord.Spotify)), None)
        if user == None:user = ctx.author
        if spotify_result is None:
            embed = discord.Embed(description=f"{emote.warning} **I couldn't find the Spotify status of {user.mention}**", color=hex.warning)
            await ctx.reply(embed=embed)
        else:
            await ctx.channel.typing()
            loading = discord.Embed(colour=hex.normal, description=f"**{emote.spotify} loading {user.mention}'s current spotify status...**")
            await ctx.send(embed=loading, delete_after=3.2)
        await ctx.channel.typing()
        spotify = f"https://api.jeyy.xyz/discord/spotify?title={spotify_result.title}&cover_url={spotify_result.album_cover_url}&duration_seconds={spotify_result.duration.seconds}&start_timestamp={spotify_result.created_at.timestamp()}&artists={', '.join(spotify_result.artists).replace(',', '%2C').replace(' ', '%20')}"
        spotify = await utils.file(spotify, "spotify.png")
        artist = spotify_result.artist.replace(";", ",")
        embed = discord.Embed(color=hex.spotify)
        embed.set_author(name=f"{user.name}#{user.discriminator}'s current spotify song:", icon_url=f"{user.display_avatar}")
        embed.set_image(url="attachment://spotify.png")
        embed.set_footer(text=f"Album: {spotify_result.album}")
        trackurl = Button(label="Song URL", url=f"{spotify_result.track_url}")
        view = View()
        view.add_item(trackurl)
        embed = await ctx.reply(view=view, file=spotify, embed=embed, mention_author=False)
    
async def setup(bot):
    await bot.add_cog(spotify(bot))