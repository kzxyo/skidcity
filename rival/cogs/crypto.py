import re,orjson
from decimal import Decimal
from forex_python.converter import CurrencyRates
import aiohttp
import discord
from discord.ext import commands
from typing import Union
import typing

from modules import emojis, exceptions, util
def num(number):
	return ("{:,}".format(number))

class Cryptocurrency(commands.Cog):
	"""Cryptocurrency commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "🪙"
		self.binance_icon = "https://i.imgur.com/i7vdQjQ.png"
		with open("html/candlestick_chart.html", "r", encoding="utf-8") as file:
			self.candlestick_chart_html = file.read()
		self.binance_intervals = [
			"1m",
			"3m",
			"5m",
			"15m",
			"30m",
			"1h",
			"2h",
			"4h",
			"6h",
			"8h",
			"12h",
			"1d",
			"3d",
			"1w",
			"1M",
		]

	@commands.command(name="convert", usage="```Swift\nSyntax: !convert [amount] [from currency] [to currency]\nExample: !convert 1 USD EUR```",description="convert one currency to another", brief="amount currency1 currency2", aliases=['cc','currency'])
	async def convert(self, ctx, amount: typing.Optional[int], from_currency: str, to_currency: str):
		"""You can convert one currency to another"""
		try:
			if not amount: amount=1
			c = CurrencyRates()
			from_currency = from_currency.upper()
			to_currency = to_currency.upper()
			result = c.convert(from_currency, to_currency, amount)
			embed= discord.Embed(description= f'**{num(amount)}{from_currency}** `=` **{num(round(result, 2))}{to_currency}**', color=ctx.author.color).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar).set_footer(text="Results by Google", icon_url="https://images-ext-2.discordapp.net/external/2X-ElcbGoaIJUc8yTuboiHqMF0N9C3dDUyOsT9n14po/https/bleed.bot/img/google.png")
			await ctx.send(embed=embed)
		except Exception as e:
			print(e)
			return await util.send_error(ctx, f"incorrect currency codes given")

	@commands.group()
	async def crypto(self, ctx):
		"""Cryptocurrency price data."""
		if ctx.invoked_subcommand == None:
			await util.command_group_help(ctx)

	@crypto.command(name='chart', description="Generates candlestick chart for a given cryptocurrency pair", usage="```Swift\nSyntax: !crypto chart <coin> <currency> <interval> <limit>\nExample: !crypto chart BTC USDT```",brief='coin, currency, interval, limit')
	async def chart(self, ctx, coin, pair="USDT", interval="1h", limit: int = 50):
		if interval not in self.binance_intervals:
			raise exceptions.Error("invalid timeframe please give a timeframe")

		if limit > 100:
			raise exceptions.Error("less then 125 please")

		symbol = (coin + pair).upper()
		async with aiohttp.ClientSession() as session:
			url = "https://api.binance.com/api/v3/klines"
			params = {"symbol": symbol, "interval": interval, "limit": limit}
			async with session.get(url, params=params) as response:
				data = await response.json(loads=orjson.loads)

		if isinstance(data, dict):
			raise exceptions.Error(data.get("msg"))

		candle_data = []
		for ticker in data:
			candle_data.append(str(ticker[:5]))

		current_price = Decimal(data[-1][4]).normalize()

		replacements = {
			"HEIGHT": 512,
			"TITLE": f"{coin.upper()} / {pair.upper()} | {interval} | {current_price:,f}",
			"DATA": ",".join(candle_data),
		}

		def dictsub(m):
			return str(replacements[m.group().strip("$")])

		formatted_html = re.sub(r"\$(\S*)\$", dictsub, self.candlestick_chart_html)
		async with aiohttp.ClientSession() as session:
			data = {
				"html": formatted_html,
				"width": 720,
				"height": 512,
				"imageFormat": "png",
			}
			async with session.post("http://localhost:3000/html", data=data) as response:
				with open("downloads/candlestick.png", "wb") as f:
					while True:
						block = await response.content.read(1024)
						if not block:
							break
						f.write(block)

		with open("downloads/candlestick.png", "rb") as f:
			await ctx.send(file=discord.File(f))

	@crypto.command(name='price', description="See the current price and 25h statistics of cryptocurrency pair", usage="```Swift\nSyntax: !crypto price <coin> <currency>\nExample: !crypto price BTC USDT```",brief='coin, currency')
	async def price(self, ctx, coin, pair="USDT"):
		symbol = (coin + pair).upper()
		url = "https://api.binance.com/api/v3/ticker/24hr"
		params = {"symbol": symbol}
		async with aiohttp.ClientSession() as session:
			async with session.get(url, params=params) as response:
				data = await response.json()

		error = data.get("msg")
		if error:
			raise exceptions.Error(error)

		content = discord.Embed(color=int("f3ba2e", 16))
		content.set_author(
			name=f"{data.get('symbol')} | Binance",
			icon_url=self.binance_icon,
			url=f"https://www.binance.com/en/trade/{data.get('symbol')}",
		)
		content.add_field(
			name="Current price", value=f"{Decimal(data.get('lastPrice')).normalize():,f}"
		)
		content.add_field(
			name="24h High", value=f"{Decimal(data.get('highPrice')).normalize():,f}"
		)
		content.add_field(name="24h Low", value=f"{Decimal(data.get('lowPrice')).normalize():,f}")
		pricechange = Decimal(data.get("priceChange")).normalize()
		if pricechange > 0:
			direction = "<:uptriangle::943947249099100261>"
		elif pricechange < 0:
			direction = "<:downtriangle:943946738119606292>"
		else:
			direction = " "

		content.add_field(
			name="24h Change",
			value=f"{direction} {pricechange:,f} ({Decimal(data.get('priceChangePercent')).normalize():.2f}%)",
		)
		content.add_field(
			name=f"24h Volume ({coin.upper()})",
			value=f"{Decimal(data.get('volume')).normalize():,.2f}",
		)
		content.add_field(
			name=f"24h Volume ({pair.upper()})",
			value=f"{Decimal(data.get('quoteVolume')).normalize():,.2f}",
		)
		await ctx.send(embed=content)


async def setup(bot):
	await bot.add_cog(Cryptocurrency(bot))
