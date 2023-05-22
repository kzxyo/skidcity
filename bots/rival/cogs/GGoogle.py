import asyncio
import json
import os
import random
import re,html,lxml
from urllib.parse import parse_qs
from urllib.parse import quote
from lxml import etree
from io import BytesIO, StringIO
import aiohttp
import arrow
import requests
import async_cse
import discord
import regex
import tweepy
import functools
import urllib
from collections import namedtuple
from io import BytesIO
from bs4 import BeautifulSoup
from discord.ext import commands
from random_user_agent.user_agent import UserAgent
from tweepy import OAuthHandler

from modules import exceptions, util, cache, google, search
import re,apipool, os
from apipool import ApiKey, ApiKeyManager
from modules import GetImage
import requests
from serpapi import GoogleSearch
#self.keys=["d48f6de7f9b90e9cbbbada29b6974c60cfa807866bbdc98e978ff912fd737495","dc0903d7836331ff17d754e9a911f76934bc324d9d1bff4f2215ef81b4db303d","2bc7bcbcebf8f8078c10cd7a8a5d8ced1c33cbdb9f0843bc6612bda46d184d53","68a6e4edc26c5d8898b85d7f9c660ba96951c76ee9129a83fc69aba55b6139a0","807029fe995002454a71205be65cb7a676b8c4e05311609899c3b85501c60792","dd0b9d307c0bc3bcc8591887a9682b2b4d7f48ea4a52c538cc28e491ba77c156","8a631ea8ef86c08d0be2c7cec51e247f6b11cfb867b8057a60cbcd2248881916","cf4632b77e91f79200164758f6bd66f4f9e6ed28a29ad651d2fe984802bfeb2c","7958fc119b95d3335b6fddcfcc4c6ddeee824c5b756d452aa9ce002c11021ce0","52325e766d85f7d92821ca4e3b7a7b5ae1f69fe17bd16504a8c4ad123e32739a","b45080bc2b1e4f6e6706c37ff7350aac11f96223e6b971f83feeaa532d10e4ae","a9555833f16381d748a7c08d4224845ab02b6ab1716d36749f7ff2907429d2c0","9a6c01815f04f8f65ba241bed0ff674cbf602faf7e2b50d0aef6d818089c03d6","ae59551c82b9aa24b8f666b9adae54deed3381a30190e5019ba94c318d7d0e2e","b0d49713aa41a82ad31a0b1f697b3f789e8f3227f6a6ba8f4aca260fc1542b08","d0a80f261d874340e43080954d63f2311da4446fb31dc38af17f6614b644d83a","46186dbde3c6a401ef6e690e2fead5ba84a39c93fc85f2c5216167a39b234b74"]
keys=["a104027a2933a765fa0b8da772a957488e1a3a6df9f9cf9ac20748704fbd6ee5","170bcc2786b87c2ebb94fbb173d0b2afb589afd068dadd207ad1679864611737","997f9a9b94571a528c48672a16c9d8842aab70ca229d8512a99966bfb187fa39","649cf4f187527f4d60cb1efec983fccd11680bbcea8554229629b67537eb54d2","3d0d12ff18b748b4cf7c16dbee59708fde11e64b4946f00a188bfec4ce4aa71e","b356e7397009f91f60bec1ac466c775de74330ee374e439336db769efae2e15b","071d1f4e9a9f90ad40308c6e8dd0b2e8aec459cadf9d86922fdbb49aa9377f7e","e5e7aa210b09924241b24931e89f05d833126b444b134e84e4a10c2236916aa0",'d48f6de7f9b90e9cbbbada29b6974c60cfa807866bbdc98e978ff912fd737495','dc0903d7836331ff17d754e9a911f76934bc324d9d1bff4f2215ef81b4db303d','2bc7bcbcebf8f8078c10cd7a8a5d8ced1c33cbdb9f0843bc6612bda46d184d53','68a6e4edc26c5d8898b85d7f9c660ba96951c76ee9129a83fc69aba55b6139a0','807029fe995002454a71205be65cb7a676b8c4e05311609899c3b85501c60792','dd0b9d307c0bc3bcc8591887a9682b2b4d7f48ea4a52c538cc28e491ba77c156','8a631ea8ef86c08d0be2c7cec51e247f6b11cfb867b8057a60cbcd2248881916','cf4632b77e91f79200164758f6bd66f4f9e6ed28a29ad651d2fe984802bfeb2c','7958fc119b95d3335b6fddcfcc4c6ddeee824c5b756d452aa9ce002c11021ce0','52325e766d85f7d92821ca4e3b7a7b5ae1f69fe17bd16504a8c4ad123e32739a','b45080bc2b1e4f6e6706c37ff7350aac11f96223e6b971f83feeaa532d10e4ae','a9555833f16381d748a7c08d4224845ab02b6ab1716d36749f7ff2907429d2c0','9a6c01815f04f8f65ba241bed0ff674cbf602faf7e2b50d0aef6d818089c03d6','ae59551c82b9aa24b8f666b9adae54deed3381a30190e5019ba94c318d7d0e2e','b0d49713aa41a82ad31a0b1f697b3f789e8f3227f6a6ba8f4aca260fc1542b08','d0a80f261d874340e43080954d63f2311da4446fb31dc38af17f6614b644d83a','46186dbde3c6a401ef6e690e2fead5ba84a39c93fc85f2c5216167a39b234b74']
start=0

GOOGLE_API_KEY = os.environ["GOOGLE_KEY"]
GCS_DEVELOPER_KEY = os.environ["GCS_DEVELOPER_KEY"]

def get_deep_text(element):
	try:
		text = element.text or ''
		for subelement in element:
		  text += get_deep_text(subelement)
		text += element.tail or ''
		return text
	except:
		return ''

def posnum(num): 
	if num < 0 : 
		return - (num)
	else:
		return num


def get_every_nth_element(values, start_index, n):
	return values[start_index::n] 

class GGoogle(commands.Cog):
	"""Fetch various media"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "🌐"
		self.options = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36","Content-Type": "application/json"}
		self.cookies = None
		self.link_regex = re.compile(
			r"https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*(?:\.png|\.jpe?g|\.gif))"
		)
		self.google_client = async_cse.Search(GCS_DEVELOPER_KEY)
		self.user_agents = UserAgent()
		self.used=[]
		self.keys=["a104027a2933a765fa0b8da772a957488e1a3a6df9f9cf9ac20748704fbd6ee5","170bcc2786b87c2ebb94fbb173d0b2afb589afd068dadd207ad1679864611737","997f9a9b94571a528c48672a16c9d8842aab70ca229d8512a99966bfb187fa39","649cf4f187527f4d60cb1efec983fccd11680bbcea8554229629b67537eb54d2","3d0d12ff18b748b4cf7c16dbee59708fde11e64b4946f00a188bfec4ce4aa71e","b356e7397009f91f60bec1ac466c775de74330ee374e439336db769efae2e15b","071d1f4e9a9f90ad40308c6e8dd0b2e8aec459cadf9d86922fdbb49aa9377f7e","e5e7aa210b09924241b24931e89f05d833126b444b134e84e4a10c2236916aa0",'d48f6de7f9b90e9cbbbada29b6974c60cfa807866bbdc98e978ff912fd737495','dc0903d7836331ff17d754e9a911f76934bc324d9d1bff4f2215ef81b4db303d','2bc7bcbcebf8f8078c10cd7a8a5d8ced1c33cbdb9f0843bc6612bda46d184d53','68a6e4edc26c5d8898b85d7f9c660ba96951c76ee9129a83fc69aba55b6139a0','807029fe995002454a71205be65cb7a676b8c4e05311609899c3b85501c60792','dd0b9d307c0bc3bcc8591887a9682b2b4d7f48ea4a52c538cc28e491ba77c156','8a631ea8ef86c08d0be2c7cec51e247f6b11cfb867b8057a60cbcd2248881916','cf4632b77e91f79200164758f6bd66f4f9e6ed28a29ad651d2fe984802bfeb2c','7958fc119b95d3335b6fddcfcc4c6ddeee824c5b756d452aa9ce002c11021ce0','52325e766d85f7d92821ca4e3b7a7b5ae1f69fe17bd16504a8c4ad123e32739a','b45080bc2b1e4f6e6706c37ff7350aac11f96223e6b971f83feeaa532d10e4ae','a9555833f16381d748a7c08d4224845ab02b6ab1716d36749f7ff2907429d2c0','9a6c01815f04f8f65ba241bed0ff674cbf602faf7e2b50d0aef6d818089c03d6','ae59551c82b9aa24b8f666b9adae54deed3381a30190e5019ba94c318d7d0e2e','b0d49713aa41a82ad31a0b1f697b3f789e8f3227f6a6ba8f4aca260fc1542b08','d0a80f261d874340e43080954d63f2311da4446fb31dc38af17f6614b644d83a','46186dbde3c6a401ef6e690e2fead5ba84a39c93fc85f2c5216167a39b234b74']


	@commands.command(name='fuckimage', description="searches for images on google with a given query", brief='query')
	async def fuckimage(self, ctx, *, query):
		"""Syntax: !image <query>
		Example: !image fruit"""
		collection={}
		pages=[]
		gs = self.bot.cache.googlesafe.get(str(ctx.guild.id), True)
		if gs:
			gs_state="[SAFE]"
			results = await self.get_result(query, images=True, nsfw=True)
		else:
			gs_state=""
			results = await self.get_result(query, images=True, nsfw=False)
		for i, j in enumerate(results, 1):
			size = len(tuple(results))
			pages.append(discord.Embed(title=f"<:google:949069791283511356> Results for {query}",description=f"[{j['title']}]({j['source']})", color=0xfffff).set_image(url=j['original']).set_footer(text=f"Page: {i}/{size} For Google Image Results{gs_state}", icon_url="https://images-ext-2.discordapp.net/external/2X-ElcbGoaIJUc8yTuboiHqMF0N9C3dDUyOsT9n14po/https/bleed.bot/img/google.png"))
		try:
			await util.imgpage(ctx=ctx, embeds=pages)
		except Exception as e:
			await ctx.send(e)
			await ctx.send(results)
			return await ctx.send(embed=discord.Embed(color=0x303135, description=f"<:google:949069791283511356> *no results found for* ***{query}***"))

	async def get_result(self, query, images=False, nsfw=False):
		"""Fetch the data"""
		# TODO make this fetching a little better
		encoded = urllib.parse.quote_plus(query, encoding="utf-8", errors="replace")

		async def get_html(url, encoded):
			async with aiohttp.ClientSession() as session:
				async with session.get(
					url + encoded, headers=self.options, cookies=self.cookies
				) as resp:
					self.cookies = resp.cookies
					return await resp.text()

		if nsfw:
			encoded += "&safe=active"
		if not images:
			url = "https://www.google.com/search?q="
			text = await get_html(url, encoded)
			prep = functools.partial(self.parser_text, text)
		else:
			# TYSM fixator, for the non-js query url
			url = "https://www.google.com/search?tbm=isch&q="
			text = await get_html(url, encoded)
			prep = functools.partial(self.parser_image, text)
		#returner(titles)
		return await self.bot.loop.run_in_executor(None, prep)

	async def combinator(self, data1, data2):
		data=[]
		a=[]
		b=[]
		for data1 in data1:
			a.append(data1)
		for data2 in data2:
			b.append(data2)
		merged=zip(a, b)
		google=list(merged)
		x=get_every_nth_element(google, 0, 2)
		y=get_every_nth_element(google, 1, 2)
		zipped=dict(zip(x,y))
		for key, value in zipped.items():
			data=[f"{key};{value}"]
		return data


	def parser_image(self, html):
		# first 2 are google static logo images
		return self.link_regex.findall(html)[7:]

	def returner(self, text):
		return text



async def setup(bot):
	await bot.add_cog(GGoogle(bot))

