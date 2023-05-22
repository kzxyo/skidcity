import discord,orjson,socket
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

class namehistory(commands.Cog, name="namehistory"):
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
		self.error=0xfaa61a
		self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),timeout=aiohttp.ClientTimeout(total=30),connector=aiohttp.TCPConnector(verify_ssl=False,family=socket.AF_INET, keepalive_timeout=30, limit=500, limit_per_host=100, ttl_dns_cache=3600),headers={"CF-Access-Client-Id": "5fad336113f621b1e4a6f5be8f4e1481.access","CF-Access-Client-Secret": "95c00e3196f1dfbebd0f5247e09a7a118ec6403b0c2957ce6ed963694c1e262f"},)
		self.warn=self.bot.warn
		self.cd_mapping = commands.CooldownMapping.from_cooldown(10, 10, commands.BucketType.member)
		self.tagloop.start()
		self._cd = commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member)
		self._cd2 = commands.CooldownMapping.from_cooldown(1, 30.0, commands.BucketType.member)
		self._cd3 = commands.CooldownMapping.from_cooldown(1, 15.0, commands.BucketType.channel)

	def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		"""Returns the ratelimit left"""
		bucket = self._cd.get_bucket(message)
		return bucket.update_rate_limit()

	def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		"""Returns the ratelimit left"""
		bucket = self._cd2.get_bucket(message)
		return bucket.update_rate_limit()

	def get_channel_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		"""Returns the ratelimit left"""
		bucket = self._cd3.get_bucket(message)
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

	@commands.command(name="nodata", description="opt out of ur data being collected", brief='bool', usage='```Syntax: !nodata <bool>\nExample: !nodata true')
	async def nodata(self, ctx, state: bool):
		if state:
			await self.bot.db.execute("""INSERT INTO nodata VALUES(%s) ON DUPLICATE KEY UPDATE user_id = VALUES(user_id)""", ctx.author.id)
			self.bot.cache.nodata.append(ctx.author.id)
			return await util.send_bad(ctx, "no longer using your data")
		else:
			try:
				await self.bot.db.execute("""DELETE FROM nodata WHERE user_id = %s""", ctx.author.id)
			except:
				pass
			try:
				self.bot.cache.nodata.remove(ctx.author.id)
			except:
				pass
			return await util.send_good(ctx, "data collection now allowed")

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
				if str(before.discriminator) not in self.bot.cache.tags:
					self.bot.cache.tags[str(before.discriminator)]=[]
				self.bot.cache.tags[str(before.discriminator)].append(f"**{discord.utils.escape_markdown(before.name)}#{before.discriminator}** - {discord.utils.format_dt(datetime.now(), style='R')}")
				if 0 in self.bot.shard_ids:
					cluster="1"
				elif 2 in self.bot.shard_ids:
					cluster="2"
				else:
					cluster="3"
				await self.bot.redis.set(f"tags{cluster}", orjson.dumps(self.bot.cache.tags))
				#await self.bot.redis.set(f"tags{self.bot.shard_id}", orjson.dumps(self.bot.cache.tags))
		tag=f"{after.name}#{after.discriminator}"
		if not await self.bot.db.execute("""SELECT * FROM namehistory WHERE user_id = %s AND name = %s AND ts = %s""", before.id, tag, datetime.now()):
			await self.bot.db.execute("""INSERT INTO namehistory VALUES(%s, %s, %s)""", before.id, tag, datetime.now())

	@commands.command(name='uwu')
	async def uwu(self, ctx, *, message=None):
		if not message:
			if ctx.message.reference:
				message=await ctx.channel.fetch_message(ctx.message.reference.message_id)
				uwu=await UWUTextResponse.from_url(self.session, message.content)
				return await ctx.send(content=uwu.get_text())
		uwu=await UWUTextResponse.from_url(self.session, message)
		return await ctx.send(content=uwu.get_text())

	@commands.command(name='uwulock')
	async def uwulock(self, ctx, *, member:discord.Member):
		if ctx.author.id not in self.bot.owner_ids:
			return
		if member.id == 352190010998390796:
			return await ctx.send("nice try pal")
		if ctx.guild.id not in self.webhook:
			self.webhook[ctx.guild.id]={}
		if member.id not in self.webhook[ctx.guild.id]:
			async with aiohttp.ClientSession() as session:
				async with session.get(member.display_avatar.url) as response:
					avatar = await response.read()
			webhook = await ctx.channel.create_webhook(name=member.name, avatar=avatar, reason=f"Webhook created by {ctx.author}")
			self.webhook[ctx.guild.id][member.id]=webhook.url
			return await util.send_good(ctx, f"{member.mention} is now **hentai locked**")
		else:
			if ctx.guild.id in self.webhook:
				if member.id in self.webhook[ctx.guild.id]:
					wb=self.webhook[ctx.guild.id][member.id]
					async with aiohttp.ClientSession() as session:
						webhook = discord.Webhook.from_url(f'{wb}', session=session)
						await webhook.delete(reason=f"Deleted by {ctx.author}")
					self.webhook[ctx.guild.id].pop(member.id)
			return await util.send_good(ctx, f"{member.mention} is no longer **hentai locked**")

	@commands.command(name='tags', description="shows tags that became available recently")
	@util.donor()
	@commands.cooldown(1, 60, commands.BucketType.channel)
	async def tags(self, ctx, *, search:str="0001"):
		rows=[]
		content=discord.Embed(title="recently available tags", color=self.color)
		if not self.bot.cache.tags:
			return await util.send_error(ctx, f"no recent **{search}** tags available")
		cc=await self.bot.redis.get("tags1")
		cf=await self.bot.redis.get("tags2")
		cd=await self.bot.redis.get("tags3")
		cg=await self.bot.redis.get("tagsblame")
		if search not in self.bot.cache.tags:
			return await util.send_error(ctx, f"no recent **{search}** tags available")
		#cv=await self.bot.redis.get("tags0")
		#cs=await self.bot.redis.get("tags4")
		#ck=await self.bot.redis.get("tags5")
		if cg:
			tagg=orjson.loads(cc) | orjson.loads(cf) | orjson.loads(cd) | orjson.loads(cg)
		else:
			tagg=orjson.loads(cc) | orjson.loads(cf) | orjson.loads(cd)# | orjson.loads(cv) | orjson.loads(cs) | orjson.loads(ck) | orjson.loads(cg)
		tags=reversed(tagg[search])
		for i, tag in enumerate(tags, start=1):
			rows.append(f"`{i}` {tag}")
		if rows:
			await util.send_as_pages(ctx, content, rows, 10,50)
		else:
			return await util.send_error(ctx, f"no recent **{search}** tags available")

	@tags.error
	async def tags_error(self, ctx, error):
		error = getattr(error, "original", error)
		if isinstance(error, commands.CommandOnCooldown):
			if ctx.author.id in ctx.bot.owner_ids:
				return await ctx.reinvoke()
			ratelimit = self.get_ratelimit(ctx.message)
			if ratelimit is None:
				pass
			else:
				return
			return await util.send_error(ctx, f"The Channel is on cooldown. Please wait `{error.retry_after:.0f} seconds`")
		elif isinstance(error, util.donorCheckFailure):
			if ctx.author.id in ctx.bot.owner_ids:
				return await ctx.reinvoke()
			await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.author.mention}: `Donator Only`"))

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		if message.guild is None:
			return
		bucket = self.cd_mapping.get_bucket(message)
		retry_after = bucket.update_rate_limit()
		if retry_after:
			await asyncio.sleep(2)
		else:
			pass
		if message.guild.id in self.webhook:
			if message.author.id in self.webhook[message.guild.id]:
				await message.delete()
				webhbook=self.webhook[message.guild.id][message.author.id]
				async with aiohttp.ClientSession() as session:
					webhook = discord.Webhook.from_url(f'{webhbook}', session=session)
					uwu=await UWUTextResponse.from_url(self.session, message.content)
					return await webhook.send(content=uwu.get_text())
		#if await self.bot.db.execute("""SELECT * FROM stfu WHERE guild_id = %s and user_id = %s""", message.guild.id, message.author.id):
		if message.guild.id in self.bot.cache.stfu:
			if message.author.id in self.bot.cache.stfu[message.guild.id]:
				if message.guild.me.guild_permissions.manage_messages:
					try:
						return await message.delete()
					except:
						pass
		ctx=await self.bot.get_context(message)
		if message.guild.id in self.bot.cache.paginator:
			if not message.guild.me.guild_permissions.administrator:
				return
			rk = self.get_ratelimit(message)
			if rk is not None:
				await asyncio.sleep(2)
			async for k,v in aiter(self.bot.cache.paginator[message.guild.id].items()):
				if message.content.lower().startswith(k.lower()) or message.content.lower() == k.lower():
					await util.create_embed_paginator(ctx, v, True)
		
		if message.content.startswith(f"{ctx.prefix}afk"):
			return
		#afk=await self.bot.db.execute("SELECT reason, ts FROM afks WHERE user_id = %s",message.author.id)
		#if afk:
			# for reason, ts in afk:
			# 	await self.bot.db.execute(
			# 	"DELETE FROM afks WHERE user_id = %s",
			# 	message.author.id
			# 	)
			# 	ago=humanize.naturaltime(ts)
			# 	embed=discord.Embed(color=self.color, description=f"> welcome back <@!{message.author.id}>, you were last seen ***{ago}***")
			# 	embed.set_author(icon_url=message.author.display_avatar, name=f"{message.author.name}#{message.author.discriminator} is no longer afk")
			# 	try:
			# 		await message.reply(embed=embed)
			# 	except:
			# 		pass
		if ctx.author.id in self.bot.cache.afk:
			reason=self.bot.cache.afk[ctx.author.id]['reason']
			ts=self.bot.cache.afk[ctx.author.id]['ts']
			ago=humanize.naturaltime(ts)
			await self.bot.db.execute("""DELETE FROM afks WHERE user_id = %s""", message.author.id)
			embed=discord.Embed(color=self.bot.color, description=f"> welcome back <@!{message.author.id}>, you were last seen **{ago}**")
			embed.set_author(icon_url=message.author.display_avatar, name=f"{message.author.name}#{message.author.discriminator} is no longer afk")
			try:
				self.bot.cache.afk.pop(ctx.author.id)
			except:
				pass
			try:
				return await message.reply(embed=embed)
			except:
				pass
		if message.mentions:
			async for member in aiter(message.mentions):
				if member.id in self.bot.cache.afk:
					rk = self.get_channel_ratelimit(message)
					if rk is not None:
						return
					reason=self.bot.cache.afk[member.id]['reason']
					ts=self.bot.cache.afk[member.id]['ts']
					ago=humanize.naturaltime(ts)
					embed=discord.Embed(color=self.bot.color, description=f"> {reason}")
					embed.set_footer(text=f"last seen {ago}")
					embed.set_author(icon_url=member.display_avatar, name=f"{member.name}#{member.discriminator} is currently afk")
					try:
						return await message.reply(embed=embed)
					except:
						pass
				# afk=await self.bot.db.execute("SELECT reason, ts FROM afks WHERE user_id = %s",member.id)
				# if afk:
				# 	for reason, ts in afk:
				# 		ago=humanize.naturaltime(ts)
				# 		embed=discord.Embed(color=self.color, description=f"{reason}")
				# 		embed.set_footer(text=f"last seen {ago}")
				# 		embed.set_author(icon_url=member.display_avatar, name=f"{member.name}#{member.discriminator} is currently afk")
				# 		try:
				# 			await message.reply(embed=embed)
				# 		except:
				# 			pass

	@commands.command(name='namehistory', aliases=['names'], description='show a members name history', usage="```Swift\nSyntax: !namehistory <id/mention>\nExample: !namehistory @cop#0001```",brief='member/user')
	async def namehistory(self, ctx, *, member:typing.Union[discord.Member, discord.User]=None):
		rows = []
		if member is None:
			member = ctx.author
		if not member:
			member=self.bot.get_user(member)
			if member == None:
				member=await self.bot.fetch_user(member)
		tag=f"{member.name}#{member.discriminator}"
		async for i, (command) in aiter(enumerate(await self.name_list(member.id), start=1)):
			rows.append(f"`{i}` {command}")
		if rows:
			content = discord.Embed(title=f"{tag}'s name history", color=self.color)
			await util.send_as_pages(ctx, content, rows)
		else:
			await util.send_failure(ctx, f"{ctx.author.mention}: **user has no name history**")

	@commands.command(name='clearnames', aliases=['nameclear', 'namesclear'], description="clear name history")
	async def clearnames(self, ctx):
		await self.send_clear_confirmation(ctx)

	async def send_clear_confirmation(self, ctx):
		content = discord.Embed(color=self.bot.color)
		content.description = f"**Are you sure you want to clear your name history?**"
		msg = await ctx.send(embed=content)

		async def confirm_clear():
			content.colour=self.bot.color
			content.description=f"**cleared your name history {ctx.author.mention}**"
			await msg.edit(embed=content, view=None, delete_after=10)
			await self.clear_name_history(ctx.author.id)

		async def cancel_clear():
			content.colour=self.bot.color
			content.description=f"{self.bot.no} {ctx.author.mention}: **cancelled namehistory clear**"
			await msg.edit(embed=content, view=None)

		confirmed:bool = await confirmation.confirm(self, ctx, msg)
		if confirmed:
			await confirm_clear()
		else:
			await cancel_clear()

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
	await bot.add_cog(namehistory(bot))