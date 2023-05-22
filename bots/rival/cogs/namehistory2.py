import discord,orjson
from discord.ext import commands, tasks

from modules import emojis, exceptions, util
import typing, humanize
import datetime,unidecode
import humanfriendly
import tweepy
import random, re, asyncio, aiohttp
from discord import ui, Interaction, app_commands, Object, AppCommandType
from datetime import timedelta
from typing import Union
from datetime import datetime
from io import BytesIO
from discord.ext import menus
from collections import deque
from discord.ext.commands import errors
import psutil
import requests, os, ast, inspect
from bs4 import BeautifulSoup
from typing import Union
import time
from modules.asynciterations import aiter
from modules.MyMenuPages import MyMenuPages, MySource
from modules.melanieapi import UWUTextResponse
from modules import exceptions, util, consts, queries, http, default, permissions, log, confirmation
import logging
logger = logging.getLogger(__name__)

class namehistory2(commands.Cog, name="namehistory2"):
	"""Custom server commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "📌"
		self.url_regex = re.compile(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")
		self.keyword_regex = r"(?:^|\s|[\~\"\'\+\*\`\_\/])(\L<words>)(?:$|\W|\s|s)"
		self.add="<:plus:947812413267406848>"
		self.yes=self.bot.yes
		self.good=self.bot.color#0x0xD6BCD0
		self.rem="<:rem:947812531509026916>"
		self.no=self.bot.no
		self.bad=self.bot.color#0xff6465
		self.color=self.bot.color
		self.ch='<:yes:940723483204255794>'
		self.webhook={}
		self.tags={}
		self.error=0xfaa61a
		self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),timeout=aiohttp.ClientTimeout(total=30),connector=aiohttp.TCPConnector(verify_ssl=False,family=socket.AF_INET, keepalive_timeout=30, limit=500, limit_per_host=100, ttl_dns_cache=3600),headers={"CF-Access-Client-Id": "5fad336113f621b1e4a6f5be8f4e1481.access","CF-Access-Client-Secret": "95c00e3196f1dfbebd0f5247e09a7a118ec6403b0c2957ce6ed963694c1e262f"},)
		self.warn=self.bot.warn
		self.cd_mapping = commands.CooldownMapping.from_cooldown(10, 10, commands.BucketType.member)
		self.tagloop.start()
		self._cd = commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member)
		self._cd2 = commands.CooldownMapping.from_cooldown(1, 30.0, commands.BucketType.member)

	def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		"""Returns the ratelimit left"""
		bucket = self._cd.get_bucket(message)
		return bucket.update_rate_limit()

	def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		"""Returns the ratelimit left"""
		bucket = self._cd2.get_bucket(message)
		return bucket.update_rate_limit()


	async def name_list(self, user_id, match=""):
		command_list = deque()
		data = await self.bot.db.execute(
			"SELECT name, ts FROM namehistory WHERE user_id = %s ORDER BY ts DESC", user_id
		)
		cd=deque()
		for name, ts in data:
			name = name
			ts = ts
			timestamp=discord.utils.format_dt(ts, style="R")
			if match == "" or match in name:
				if name == "None":
					us=await self.bot.fetch_user(user_id)
					name=us.name
				if name not in cd:
					command_list.append(f"{discord.utils.escape_markdown(name)} ・ {timestamp}")
					cd.append(name)

		return command_list

	async def clear_name_history(self, user_id):
		await self.bot.db.execute("DELETE FROM namehistory WHERE user_id = %s",user_id,)

	@commands.Cog.listener()
	async def on_user_update(self, before, after):
		if before.name == after.name:
			return
		beforetag=f"{before.name}#{before.discriminator}"
		aftertag=f"{after.name}#{after.discriminator}"
		if beforetag != aftertag and not after.id in self.bot.cache.nodata:#await self.bot.db.execute("""SELECT * FROM nodata WHERE user_id = %s""", before.id):
			tag=f"{before.name}#{before.discriminator}"
			if before.name.isalpha() and before.name == unidecode.unidecode(before.name) and len(before.name) < 9:
				#self.tags.append(f"{before.name}#{before.discriminator} • {discord.utils.format_dt(datetime.now(), style='R')}")
				if str(before.discriminator) not in self.tags:
					self.tags[str(before.discriminator)]=[]
				self.tags[str(before.discriminator)].append(f"**{discord.utils.escape_markdown(before.name)}#{before.discriminator}** - {discord.utils.format_dt(datetime.now(), style='R')}")
				if 0 in self.bot.shard_ids:
					cluster="1"
				elif 2 in self.bot.shard_ids:
					cluster="2"
				else:
					cluster="3"
				await self.bot.redis.set(f"tagsblame", orjson.dumps(self.tags))
		tag=f"{after.name}#{after.discriminator}"
		if not await self.bot.db.execute("""SELECT * FROM namehistory WHERE user_id = %s AND name = %s AND ts = %s""", before.id, tag, datetime.now()):
			await self.bot.db.execute("""INSERT INTO namehistory VALUES(%s, %s, %s)""", before.id, tag, datetime.now())

	@tasks.loop(hours=5)
	async def tagloop(self):
		#self.tags.clear()
		self.bot.cache.tags.clear()
		logger.info("Cleared Tag Table")

	@tagloop.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		logger.info("Starting Tag Clear Loop")



async def setup(bot):
	await bot.add_cog(namehistory2(bot))