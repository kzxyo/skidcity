import discord 
import discord_paginator as pg 

from typing import List
from discord.ext import commands 

class HarmContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def success(self, message: str) -> discord.Message: 
        embed = discord.Embed(
            color=0x32CD32,
            description=f"> {self.author.mention}: {message}"
        )
        return await self.send(embed=embed)

    async def error(self, message: str) -> discord.Message: 
        embed = discord.Embed(
            color=0xff0000,
            description=f"> {self.author.mention}: {message}"
        )    

        return await self.send(embed=embed)
    
    async def paginate(
        self, 
        contents: List[str], 
        title: str=None, 
        author: dict={'name': '', 'icon_url': None}
    ):
        iterator = [m for m in discord.utils.as_chunks(contents, 10)]
        embeds = [
            discord.Embed(
              color=self.bot.color, 
              title=title, 
              description='\n'.join([f"`{(m.index(f)+1)+(iterator.index(m)*10)}.` {f}" for f in m])
            ).set_author(**author)
            for m in iterator
        ]
        return await self.paginator(embeds)
     
    async def paginator(self, embeds: List[discord.Embed]):
        paginator = pg.Paginator(
            self,
            embeds
        )

        paginator.add_button(
            "prev", 
            emoji="<:left:1152990746362781706>",
            style=discord.ButtonStyle.blurple
        )
        
        paginator.add_button(
            "delete",
            emoji="<:stop:1152990644759957555>",
            style=discord.ButtonStyle.red
        )

        paginator.add_button(
            "next",
            emoji="<:right:1152990816734826507>",
            style=discord.ButtonStyle.blurple
        )

        await paginator.start()