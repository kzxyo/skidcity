import asyncio
import json
import os
import random
import re,html,re
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

class Google(commands.Cog):
	"""Fetch various media"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "🌐"
		self.color=self.bot.color
		self.options = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36","Content-Type": "application/json"}
		self.cookies = None
		self.link_regex = re.compile(r"https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*(?:\.png|\.jpe?g|\.gif))")
		self.google_client = async_cse.Search(GCS_DEVELOPER_KEY)
		self.user_agents = UserAgent()
		self.used=[]
		self.keys=["a104027a2933a765fa0b8da772a957488e1a3a6df9f9cf9ac20748704fbd6ee5","170bcc2786b87c2ebb94fbb173d0b2afb589afd068dadd207ad1679864611737","997f9a9b94571a528c48672a16c9d8842aab70ca229d8512a99966bfb187fa39","649cf4f187527f4d60cb1efec983fccd11680bbcea8554229629b67537eb54d2","3d0d12ff18b748b4cf7c16dbee59708fde11e64b4946f00a188bfec4ce4aa71e","b356e7397009f91f60bec1ac466c775de74330ee374e439336db769efae2e15b","071d1f4e9a9f90ad40308c6e8dd0b2e8aec459cadf9d86922fdbb49aa9377f7e","e5e7aa210b09924241b24931e89f05d833126b444b134e84e4a10c2236916aa0",'d48f6de7f9b90e9cbbbada29b6974c60cfa807866bbdc98e978ff912fd737495','dc0903d7836331ff17d754e9a911f76934bc324d9d1bff4f2215ef81b4db303d','2bc7bcbcebf8f8078c10cd7a8a5d8ced1c33cbdb9f0843bc6612bda46d184d53','68a6e4edc26c5d8898b85d7f9c660ba96951c76ee9129a83fc69aba55b6139a0','807029fe995002454a71205be65cb7a676b8c4e05311609899c3b85501c60792','dd0b9d307c0bc3bcc8591887a9682b2b4d7f48ea4a52c538cc28e491ba77c156','8a631ea8ef86c08d0be2c7cec51e247f6b11cfb867b8057a60cbcd2248881916','cf4632b77e91f79200164758f6bd66f4f9e6ed28a29ad651d2fe984802bfeb2c','7958fc119b95d3335b6fddcfcc4c6ddeee824c5b756d452aa9ce002c11021ce0','52325e766d85f7d92821ca4e3b7a7b5ae1f69fe17bd16504a8c4ad123e32739a','b45080bc2b1e4f6e6706c37ff7350aac11f96223e6b971f83feeaa532d10e4ae','a9555833f16381d748a7c08d4224845ab02b6ab1716d36749f7ff2907429d2c0','9a6c01815f04f8f65ba241bed0ff674cbf602faf7e2b50d0aef6d818089c03d6','ae59551c82b9aa24b8f666b9adae54deed3381a30190e5019ba94c318d7d0e2e','b0d49713aa41a82ad31a0b1f697b3f789e8f3227f6a6ba8f4aca260fc1542b08','d0a80f261d874340e43080954d63f2311da4446fb31dc38af17f6614b644d83a','46186dbde3c6a401ef6e690e2fead5ba84a39c93fc85f2c5216167a39b234b74']


	# # Filtered Words & Anti IP Filter
	# @commands.Cog.listener()
	# async def on_message(self, message):
	# 	if message.guild is None:
	# 		return
	# 	if message.author.bot:
	# 		return
	# 	if not message.guild.me.guild_permissions.manage_messages:
	# 		return 
	# 	word=message.content.lower().split()
	# 	cf=await self.bot.db.execute("SELECT strr FROM chatfilter WHERE guild_id = %s",message.guild.id)
	# 	for strr in cf:
	# 		strr=''.join(strr)
	# 		if str(strr) in message.content.lower() and not message.author.guild_permissions.administrator:
	# 			try: 
	# 				return await message.delete()
	# 			except: 
	# 				pass
	# 	data=await self.bot.db.execute("SELECT * FROM antiips WHERE guild_id = %s", message.guild.id, one_value=True)
	# 	if data:
	# 		msg=message.content
	# 		match_obj = re.findall(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})", msg)
	# 		if match_obj:
	# 			if message.author.guild_permissions.administrator:
	# 				return 
	# 			else:
	# 				try: 
	# 					return await message.delete() 
	# 				except: 
	# 					pass

	@commands.command(name="imgtest")
	async def imgtest(self, ctx, *, query):
		gs = self.bot.cache.googlesafe.get(str(ctx.guild.id), True)
		if gs:
			gs_state="[SAFE]"
			try:
				results = await self.google_client.search(query, safesearch=True, image_search=True)
			except:
				return await ctx.send(embed=discord.Embed(color=self.color, description=f"<:google:949069791283511356> *no results found for* ***{query}***").set_footer(text="SafeSearch[ON]\nToggle using !ss"))
		else:
			gs_state=""
			try:
				results = await self.google_client.search(query, safesearch=False, image_search=True)
				print(len(results))
			except:
				return await ctx.send(embed=discord.Embed(color=self.color, description=f"<:google:949069791283511356> *no results found for* ***{query}***"))
		imgs=[result.image_url for result in results]
		embeds=[]
		for result in results:
			embeds.append(discord.Embed(title=f"<:google:949069791283511356> Results for {query}", description=f"[{result.title}]({result.image_url})", color=self.color).set_image(url=result.image_url).set_footer(text=f"Google Image Results{gs_state}"))
		await util.imgpage(ctx=ctx, embeds=embeds)



	@commands.command(name='google', description='search google for a specific query', brief='query')
	async def google(self, ctx, *, query):
		"""Syntax: !google <query>
		Example: !google rival bot"""
		gs = self.bot.cache.googlesafe.get(str(ctx.guild.id), True)
		if not ctx.channel.is_nsfw():
			results = await self.google_client.search(query, safesearch=True)
		else:
			results = await self.google_client.search(query, safesearch=False)

		await util.paginate_list(
			ctx,
			[f"**{result.title}**\n{result.url}" for result in results],
			use_locking=True,
			only_author=True,
			index_entries=True,
		)
	async def searchapi(self, query, nsfw=True):
		tries=len(self.keys)
		for i in range(tries):
			try:
				if nsfw:
					params = {"api_key": self.keys[i],"engine": "google","q": query,"google_domain": "google.com","gl": "us","hl": "en","num": "100","tbm": "isch","safe": "active"}
					search = GoogleSearch(params)
					try:
						if search.get_dict()['error'] == "Your searches for the month are exhausted. You can upgrade plans on SerpApi.com website.":
							self.used.append(self.keys[i])
							self.keys.pop(i)
					except:
						pass
					results = search.get_dict()['images_results']
					status=search.get_dict()["search_information"]["image_results_state"]
					if status=="Fully empty":
						return
					if "https://serpapi.com/search" not in results and results and results != None and results != "https://serpapi.com/search":
						return results
				else:
					params = {"api_key": self.keys[i],"engine": "google","q": query,"google_domain": "google.com","gl": "us","hl": "en","num": "100","tbm": "isch"}
					search = GoogleSearch(params)
					results = search.get_dict()['images_results']
					try:
						if search.get_dict()['error'] == "Your searches for the month are exhausted. You can upgrade plans on SerpApi.com website.":
							self.used.append(self.keys[i])
							self.keys.pop(i)
					except:
						pass
					status=search.get_dict()["search_information"]["image_results_state"]
					if status=="Fully empty":
						return
					if "https://serpapi.com/search" not in results and results and results != None and results != "https://serpapi.com/search":
						return results
			except KeyError as e:
				print(e)
				if i == tries:
					break
				elif i < tries - 1:
					continue
				else:
					raise
			break

	@commands.hybrid_command(name='image', aliases=["img"], description="searches for images on google with a given query", brief='query', with_app_command=True)
	@commands.cooldown(1, 30, commands.BucketType.member)
	async def image(self, ctx, *, query):
		"""Syntax: !image <query>
		Example: !image fruit"""
		collection={}
		gs = self.bot.cache.googlesafe.get(str(ctx.guild.id), True)
		if ctx.channel.is_nsfw():
			gs_state="[SAFE]"
			results = await self.get_result(query, images=True, nsfw=True)
			titles = await self.get_titles(query, images=True, nsfw=True)
		else:
			gs_state=""
			results = await self.get_result(query, images=True, nsfw=False)
			titles = await self.get_titles(query, images=True, nsfw=False)
		try:
			results.pop(0)
		except:
			pass
		for i, j in enumerate(results, 1):
				if "gstatic" not in j and "i.guim.co.uk" not in j:
					size = len(tuple(results))
					pages = [discord.Embed(title=f"<:google:949069791283511356> Results for {query}", description=f"[{titles[i-1]}]({j})",color=0xfffff).set_image(url=j).set_footer(text=f"Page: {i}/{size} For Google Image Results{gs_state}", icon_url="https://images-ext-2.discordapp.net/external/2X-ElcbGoaIJUc8yTuboiHqMF0N9C3dDUyOsT9n14po/https/bleed.bot/img/google.png")for i, j in enumerate(results, 1)]
		try:
			await util.imgpage(ctx=ctx, embeds=pages)
		except:
			return await ctx.send(embed=discord.Embed(color=0x303135, description=f"<:google:949069791283511356> *no results found for* ***{query}***"))

	@image.error
	async def image_error(self, ctx, error):
		error = getattr(error, "original", error)
		if isinstance(error, commands.CommandOnCooldown):
			if ctx.author.id in self.bot.owner_ids:
				return await ctx.reinvoke()
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} You are on cooldown. Please wait `{error.retry_after:.0f} seconds`", color=self.bot.color))


	@commands.command(name='immage', aliases=["immg"], description="searches for images on google with a given query, use !ss true/false to toggle safe search", brief='query', with_app_command=False)
	async def immage(self, ctx, *, query):
		gs = self.bot.cache.googlesafe.get(str(ctx.guild.id), True)
		if not ctx.channel.is_nsfw():
			gs_state="ON"
			saf="[SAFE]"
			#try:
			results = await self.searchapi(query=query, nsfw=True)
			#except Exception as e:
				#print(e)
				#return await ctx.send(embed=discord.Embed(color=0x303135, description=f"<:google:949069791283511356> *no results found for* ***{query}***"))
		else:
			gs_state="OFF"
			saf=""
			try:
				results = await self.searchapi(query=query, nsfw=False)
			except Exception as e:
				print(e)
				return await ctx.send(embed=discord.Embed(color=0x303135, description=f"<:google:949069791283511356> *no results found for* ***{query}***"))
		if results:
			#print(results)
			try:
				color=0xa3a3a3
				embeds=[discord.Embed(title=f"<:google:949069791283511356> Results for {query}", description=f"[{result['title']}]({result['link']})", color=color).set_image(url=result['original']).set_footer(text=f"Page: {result['position']}/100 For Google Image Results{saf}", icon_url="https://images-ext-2.discordapp.net/external/2X-ElcbGoaIJUc8yTuboiHqMF0N9C3dDUyOsT9n14po/https/bleed.bot/img/google.png").set_author(name=ctx.author, icon_url=ctx.author.display_avatar) for result in results]
				await util.imgpage(ctx=ctx, embeds=embeds)
				for key in self.used:
					self.keys.append(key)
			except:
				return await ctx.send(embed=discord.Embed(color=0x303135, description=f"<:google:949069791283511356> *no results found for* ***{query}***"))
		else:
			return await ctx.send(embed=discord.Embed(color=0x303135, description=f"<:google:949069791283511356> *no results found for* ***{query}***"))
		# footer url taken from bleed credits to jon

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


	async def get_titles(self, query, images=True, nsfw=False):
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
			title=[]
			# TYSM fixator, for the non-js query url
			url = "https://www.google.com/search?tbm=isch&q="
			text = await get_html(url, encoded)
			soup=BeautifulSoup(text, 'html.parser')
			divs = str(soup.find_all('div'))
			soup2 = BeautifulSoup(divs, features="html.parser")
			titles=soup2.find_all("h3")
			for titles in titles:
				text=titles.text
				title.append(text)
		return title

	async def get_results(self, query, images=False, nsfw=False):
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
	await bot.add_cog(Google(bot))

