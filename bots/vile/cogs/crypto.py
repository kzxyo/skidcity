import discord, os, sys, asyncio, aiohttp, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class crypto(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        #
        self.done = utils.emoji("done")
        self.fail = utils.emoji("fail")
        self.warn = utils.emoji("warn")
        self.reply = utils.emoji("reply")
        self.dash = utils.emoji("dash")
        #
        self.success = utils.color("done")
        self.error = utils.color("fail")
        self.warning = utils.color("warn")
        #
        self.av = "https://cdn.discordapp.com/attachments/989422588340084757/1008195005317402664/vile.png"

    # @commands.hybrid_group(invoke_without_command=True)
    # async def crypto(self, ctx):
    #
    #    cc = discord.Embed(color = 0x2f3136, timestamp = datetime.now())
    #    cc.set_footer(text = "crypto", icon_url='https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless')
    #    cc.set_author(name = "crypto", icon_url = self.bot.user.avatar)
    #    cc.add_field(name = f"{utils.read_json('emojis')['dash']} Info", value = f"{self.reply} **description:** get information about cryptocurrencies", inline = False)
    #    cc.add_field(name = f"{utils.read_json('emojis')['dash']} Usage",value = f"{self.reply} syntax: ,crypto <cryptocurrency>\n{self.reply} example: ,crypto btc OR ,crypto bitcoin", inline = False)
    #    await ctx.reply(embed=cc)

    @commands.command(aliases=["bitcoin"])
    async def btc(self, ctx):

        symbol = "BTC"
        name = "Bitcoin"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ethereum"])
    async def eth(self, ctx):

        symbol = "ETH"
        name = "Ethereum"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["tether"])
    async def usdt(self, ctx):

        symbol = "USDT"
        name = "Tether"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["USD Coin"])
    async def usdc(self, ctx):

        symbol = "USDC"
        name = "USD Coin"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def bnb(self, ctx):

        symbol = "BNB"
        name = "BNB"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def xrp(self, ctx):

        symbol = "XRP"
        name = "XRP"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["binanceusd"])
    async def busd(self, ctx):

        symbol = "BUSD"
        name = "Binance USD"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["cardano"])
    async def ada(self, ctx):

        symbol = "ADA"
        name = "Cardano"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["solana"])
    async def sol(self, ctx):

        symbol = "SOL"
        name = "Solana"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["dogecoin"])
    async def doge(self, ctx):

        symbol = "DOGE"
        name = "Dogecoin"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["polkadot"])
    async def dot(self, ctx):

        symbol = "DOT"
        name = "Polkadot"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def dai(self, ctx):

        symbol = "DAI"
        name = "Dai"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["polygon"])
    async def matic(self, ctx):

        symbol = "MATIC"
        name = "Polygon"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["avalanche"])
    async def avax(self, ctx):

        symbol = "AVAX"
        name = "Avalanche"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["shiba"])
    async def shib(self, ctx):

        symbol = "SHIB"
        name = "Shiba Inu"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["tron"])
    async def trx(self, ctx):

        symbol = "TRX"
        name = "TRON"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["uniswap"])
    async def uni(self, ctx):

        symbol = "UNI"
        name = "Uniswap"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["wrappedbitcoin"])
    async def wbtc(self, ctx):

        symbol = "WBTC"
        name = "Wrapped Bitcoin"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ethereumclassic"])
    async def etc(self, ctx):

        symbol = "ETC"
        name = "Ethereum Classic"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["unussedleo"])
    async def leo(self, ctx):

        symbol = "LEO"
        name = "UNUS SED LEO"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["litecoin"])
    async def ltc(self, ctx):

        symbol = "LTC"
        name = "Litecoin"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["cronos"])
    async def cro(self, ctx):

        symbol = "CRO"
        name = "Cronos"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["nearprotocol"])
    async def near(self, ctx):

        symbol = "NEAR"
        name = "NEAR Protocol"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["stellar"])
    async def xlm(self, ctx):

        symbol = "XLM"
        name = "Stellar"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["cosmos"])
    async def atom(self, ctx):

        symbol = "ATOM"
        name = "Cosmos"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["montero"])
    async def xmr(self, ctx):

        symbol = "XMR"
        name = "Montero"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["bitcoincash"])
    async def bch(self, ctx):

        symbol = "BCH"
        name = "Bitcoin Cash"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["filecoin"])
    async def fil(self, ctx):

        symbol = "FIL"
        name = "Filecoin"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["algorand"])
    async def algo(self, ctx):

        symbol = "ALGO"
        name = "Algorand"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["apecoin"])
    async def ape(self, ctx):

        symbol = "APE"
        name = "ApeCoin"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    # @commands.command(aliases=['flow'])
    # async def flow(self, ctx):

    # symbol = 'FLOW' ; name = 'Flow'
    # request = await self.bot.session.get(f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN')
    # data = await request.json()
    # usd = data['USD']
    # eur = data['EUR']
    # gbp = data['GBP']

    # embed = discord.Embed(color=0xFEE65C, title=f"Current {name} Value", description=f"1 Single {name}", timestamp=datetime.utcnow())
    # embed.add_field(name="USD", value=f"{usd:,}", inline=True)
    # embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
    ##embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
    # embed.set_footer(text="vile", icon_url='https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless')
    # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
    # await ctx.reply(embed=embed)

    @commands.command(aliases=["vechain"])
    async def vet(self, ctx):

        symbol = "VET"
        name = "VeChain"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["decentraland"])
    async def mana(self, ctx):

        symbol = "MANA"
        name = "Decentraland"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["hedera"])
    async def hbar(self, ctx):

        symbol = "HBAR"
        name = "Hedera"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["tezos"])
    async def xtz(self, ctx):

        symbol = "XTZ"
        name = "Tezos"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def aave(self, ctx):

        symbol = "AAVE"
        name = "Aave"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["elrond"])
    async def egld(self, ctx):

        symbol = "EGLD"
        name = "Elrond"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def eos(self, ctx):

        symbol = "EOS"
        name = "EOS"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["quant"])
    async def qnt(self, ctx):

        symbol = "QNT"
        name = "Quant"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["trueusd"])
    async def tusd(self, ctx):

        symbol = "TUSD"
        name = "TrueUSD"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["helium"])
    async def hnt(self, ctx):

        symbol = "HNT"
        name = "Helium"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["maker"])
    async def mkr(self, ctx):

        symbol = "MKR"
        name = "Maker"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def okb(self, ctx):

        symbol = "OKB"
        name = "OKB"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["zcash"])
    async def zec(self, ctx):

        symbol = "ZEC"
        name = "Zcash"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["paxdollar"])
    async def usdp(self, ctx):

        symbol = "USDP"
        name = "Pax Dollar"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["iota"])
    async def miota(self, ctx):

        symbol = "MIOTA"
        name = "IOTA"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["klaytn"])
    async def klay(self, ctx):

        symbol = "KLAY"
        name = "Klaytn"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["fantom"])
    async def ftm(self, ctx):

        symbol = "FTM"
        name = "Fantom"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["ecash"])
    async def xec(self, ctx):

        symbol = "XEC"
        name = "eCash"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def neo(self, ctx):

        symbol = "NEO"
        name = "Neo"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["chiliz"])
    async def chz(self, ctx):

        symbol = "CHZ"
        name = "Chiliz"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def usdd(self, ctx):

        symbol = "USDD"
        name = "USDD"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["neutrinousd"])
    async def usdn(self, ctx):

        symbol = "USDN"
        name = "Neutrino USD"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["lidodao"])
    async def ldo(self, ctx):

        symbol = "LDO"
        name = "Lido DAO"
        request = await self.bot.session.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN"
        )
        data = await request.json()
        usd = data["USD"]
        eur = data["EUR"]
        gbp = data["GBP"]

        embed = discord.Embed(
            color=0xFEE65C,
            title=f"Current {name} Value",
            description=f"1 Single {name}",
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="USD", value=f"{usd:,}", inline=True)
        embed.add_field(name="GBP", value=f"{gbp:,}", inline=True)
        embed.add_field(name="EUR", value=f"{eur:,}", inline=True)
        embed.set_footer(
            text="vile",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        # embed.set_thumbnail(url="https://pngimg.com/uploads/bitcoin/bitcoin_PNG48.png")
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(crypto(bot))
