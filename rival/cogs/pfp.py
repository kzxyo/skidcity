import discord
from discord.ext import commands

from modules import emojis, exceptions, util
import typing
import datetime
import tweepy
import random, re, asyncio
from discord import ui
from datetime import timedelta
from discord.ext import menus
from discord.ext.commands import errors
import requests
from bs4 import BeautifulSoup
import time
from modules.MyMenuPages import MyMenuPages, MySource
from modules import exceptions, util, consts, queries


def dt(time):
	dt=f"<t:{time}:R>"
	return dt


headers = {
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'GET',
	'Access-Control-Allow-Headers': 'Content-Type',
	'Access-Control-Max-Age': '3600',
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
	}



color=0x303135

def get_badges(url):

	html = BeautifulSoup(r.content, 'html.parser')


async def getwhi(query):
	url = f"https://weheartit.com/search/entries?query={query}"
	r = requests.get(url, headers=util.getheaders())
	soup = BeautifulSoup(r.content, features="html.parser")
	divs = str(soup.find_all('div', class_='entry grid-item'))
	soup2 = BeautifulSoup(divs, features="html.parser")
	badge=soup2.find_all(class_='entry-badge')
	images = soup2.find_all('img')
	links = []
	for image in images:
		if "data.whicdn.com/images/" in str(image):
			links.append(image['src'])
			
	return links

async def getwhiuser(query):
	url = f"https://weheartit.com/{query}"
	r = requests.get(url, headers=util.getheaders())
	soup = BeautifulSoup(r.content, features="html.parser")
	divs = str(soup.find_all('div', class_='entry grid-item'))
	soup2 = BeautifulSoup(divs, features="html.parser")
	badge=soup2.find_all(class_='entry-badge')
	images = soup2.find_all('img')
	links = []
	for image in images:
		if "data.whicdn.com/images/" in str(image):
			links.append(image['src'])
			
	return links



class pfp(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.add="<:plus:947812413267406848>"
		self.yes="<:yes:940723483204255794>"
		self.good=0xa5eb78
		self.rem="<:rem:947812531509026916>"
		self.no="<:no:940723951947120650>"
		self.bad=0xff6465
		self.color=0x303135


	@commands.command(name='pfpgen', aliases=['pfpgenerator', 'avgen', 'avsearch'], description="weheartit pfp scraper", brief='query')
	async def pfpgen(self, ctx, *, query=None):
		"""Syntax: !pfpgen <keywords/tags>
		Example: !pfpgen soft cute"""
		if query == None:
			return await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.no} {ctx.author.mention}: please provide a query to search"))
		else:
			links = await getwhi(query)
		
			def randlink():
				link = random.choice(links)
				links.remove(link)
				return str(link)
			embeds=[]
			try:
				imgs=[link for link in links]
				for img in imgs:
					embed=discord.Embed(description=f"<:whi:952399852527046687> [Results for {query}]({img})", color=0x303135).set_image(url=img)
					embeds.append(embed)
				await util.imgpage(ctx, embeds)
			except IndexError:
				return await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.no} {ctx.author.mention}: no results found for **{query}**"))
			except:
				return await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.no} {ctx.author.mention}: no results found for **{query}**"))

	@commands.command(name='posts', description='show a users posts on weheartit', brief='username')
	async def posts(self, ctx, *, user=None):
		"""Syntax: !posts <user>
		Example: !posts perv"""
		if user == None:
			return await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.no} {ctx.author.mention}: please provide a username to search"))
		else:
			links = await getwhiuser(user)
		
			def randlink():
				link = random.choice(links)
				links.remove(link)
				return str(link)
			embeds=[]
			try:
				imgs=[link for link in links]
				for img in imgs:
					embed=discord.Embed(description=f"<:whi:952399852527046687> [Results for {user}]({img})", color=0x303135).set_image(url=img)
					embeds.append(embed)
				await util.imgpage(ctx, embeds)
			except IndexError:
				return await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.no} {ctx.author.mention}: no results found for **{user}**"))



async def setup(bot):
	await bot.add_cog(pfp(bot))