import discord, typing, time, arrow, psutil, copy, aiohttp, random
from datetime import datetime
from typing import Optional, Union
from utilities import utils
from utilities.baseclass import Vile
from utilities.fortnite import Fortnite
from utilities.context import Context
from discord.ext import commands


class Fortnite_Integration(commands.Cog):
    def __init__(self, bot: Vile) -> None:
        self.bot = bot


    @commands.group(
        name='fortnite',
        aliases=['fn'],
        description='view infomation on fortnite cosmetics',
        brief='fortnite <sub command>',
        help='fortnite itemshop',
        invoke_without_command=True
    )
    async def fortnite(self, ctx: Context):
        return await ctx.send_help()


    @fortnite.command(
        name='itemshop',
        aliases=['shop', 'is'],
        description='view the current fortnite item shop'
    )
    async def fortnite_itemshop(self, ctx: Context):

        async with ctx.handle_response():
            itemshop = await utils.file(f"https://bot.fnbr.co/shop-image/fnbr-shop-{datetime.now().strftime('%-d-%-m-%Y')}.png", f'vile itemshop.png')

            return await ctx.reply(
                embed=discord.Embed(color=self.bot.color, description=f"{self.bot.done} {ctx.author.mention}**:** fortnite item shop as of `{datetime.now().strftime('%-m/%-d/%Y')}`"),
                file=itemshop
            )


    @fortnite.command(
        name='search',
        aliases=['lookup', 'find'],
        description='get information on the provided fortnite cosmetic',
        brief='fortnite search <cosmetic>',
        help='fortnite search dark bomber'
    )
    async def fortnite_search(self, ctx: Context, *, cosmetic: str):

        async with ctx.handle_response():
            
            try:
                data = await Fortnite(cosmetic=cosmetic).cosmetic_info()
                
                embed = discord.Embed(
                    color=self.bot.color,
                    title=data['name'],
                    description=f"{data['description']}\n> <:vbucks:1064583036118769754> {data['price']}",
                    url=f"https://fnbr.co/{data['type']}/{data['slug']}"
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                embed.set_thumbnail(url=data['images']['icon'])
                embed.add_field(name=f'{self.bot.dash} Type', value=f"{self.bot.reply} {data['type'].title()}")
                embed.add_field(name=f'{self.bot.dash} Rarity', value=f"{self.bot.reply} {data['rarity'].title()}")
                
                recent = [
                    datetime.fromisoformat(f'{iso[:-1]}+00:00')
                    for iso in data['history']['dates']
                ]
                recent = [
                    f"{discord.utils.format_dt(dt, style='D')} ( {discord.utils.format_dt(dt, style='R')} )"
                    for dt in sorted(recent, key=lambda dt: dt)[::-1][:5]
                ]

                embed.add_field(name=f'{self.bot.dash} Recent Occurences', value='\n'.join(recent), inline=False)

                return await ctx.reply(embed=embed)
            except:
                return await ctx.send_error('could not get information on this cosmetic')


    @commands.command(
        name='itemshop',
        aliases=['fnshop', 'is'],
        description='view the current fortnite item shop'
    )
    async def itemshop(self, ctx: Context):
        return await ctx.invoke(self.bot.get_command('fortnite itemshop'))


    @commands.command(
        name='search',
        aliases=['find'],
        description='get information on the provided fortnite cosmetic',
        brief='fsearch <cosmetic>',
        help='search dark bomber'
    )
    async def search(self, ctx: Context, *, cosmetic: str):
        return await ctx.invoke(self.bot.get_command('fortnite search'), cosmetic=cosmetic)


async def setup(bot: Vile):
    await bot.add_cog(Fortnite_Integration(bot))