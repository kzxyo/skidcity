import asyncio,pytesseract
import html
import json
import os,copy
from datetime import timedelta
import time
from PIL import Image 
from pytesseract import pytesseract 
import aiohttp
from timezonefinder import TimezoneFinder
import arrow
import discord,orjson
import aiohttp
from datetime import date as DATEE
from random import choice, randint
from asyncio import sleep
from contextlib import suppress
from datetime import datetime
import requests
import typing
from typing import Optional, Union
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from time import time

from modules import emojis, exceptions, log, queries, util,GetImage

TIMEZONE_API_KEY = os.environ.get("TIMEZONEDB_API_KEY")
GFYCAT_CLIENT_ID = os.environ.get("GFYCAT_CLIENT_ID")
GFYCAT_SECRET = os.environ.get("GFYCAT_SECRET")
#OX_ID = os.environ.get("OX_ID")
#OX_KEY = os.environ.get("OX_KEY")

NAVER_ID = os.environ.get("NAVER_ID")
NAVER_SECRET = os.environ.get("NAVER_SECRET")
GOOGLE_API_KEY = os.environ.get("GOOGLE_KEY")

class ChannelSetting(commands.TextChannelConverter):
	"""This enables removing a channel from the database in the same command that adds it."""

	async def convert(self, ctx, argument):
		if argument.lower() in ["disable", "none", "delete", "remove"]:
			return None
		return await super().convert(ctx, argument)


papago_pairs = [
	"ko/en",
	"ko/ja",
	"ko/zh-cn",
	"ko/zh-tw",
	"ko/vi",
	"ko/id",
	"ko/de",
	"ko/ru",
	"ko/es",
	"ko/it",
	"ko/fr",
	"en/ja",
	"ja/zh-cn",
	"ja/zh-tw",
	"zh-cn/zh-tw",
	"en/ko",
	"ja/ko",
	"zh-cn/ko",
	"zh-tw/ko",
	"vi/ko",
	"id/ko",
	"th/ko",
	"de/ko",
	"ru/ko",
	"es/ko",
	"it/ko",
	"fr/ko",
	"ja/en",
	"zh-cn/ja",
	"zh-tw/ja",
	"zh-tw/zh-tw",
]


import logging
logger = logging.getLogger(__name__)
command_logger=logger


class Utility(commands.Cog):
	"""Utility commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "🔧"
		self.reminder_list = []
		self.color=self.bot.color
		self.cache_needs_refreshing = True
		self.true=['true', 'TRUE', 'True', 'on', 'On', 'ON']
		self.bl=['https://', 'discord.gg', '.gg/', 'discordapp', 'www']
		self.false=['false', 'False', 'FALSE', 'off', 'Off', 'OFF']
		self.reminder_loop.start()

	def cog_unload(self):
		self.reminder_loop.cancel()

	@tasks.loop(seconds=5.0)
	async def reminder_loop(self):
		try:
			await self.check_reminders()
			#await self.bot.tree.sync()
		except Exception as e:
			logger.error(f"Reminder loop error: {e}")
		#await self.bot.clear()

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		if channel.guild.id == 918445509599977472:
			if channel.category:
				if channel.category.id == 927756048788488262:
					await channel.send(delete_after=1,content="<@&1002308893550067742>", allowed_mentions=discord.AllowedMentions(roles=True))

	@reminder_loop.before_loop
	async def before_reminder_loop(self):
		await self.bot.wait_until_ready()
		logger.info("Starting reminder loop")

	async def check_reminders(self):
		"""Check all current reminders"""
		if self.cache_needs_refreshing:
			self.cache_needs_refreshing = False
			self.reminder_list = await self.bot.db.execute(
				"""
				SELECT user_id, guild_id, created_on, reminder_date, content, original_message_url
				FROM reminder
				"""
			)

		if not self.reminder_list:
			return

		now_ts = arrow.utcnow().timestamp
		for (
			user_id,
			guild_id,
			created_on,
			reminder_date,
			content,
			original_message_url,
		) in self.reminder_list:
			reminder_ts = reminder_date.timestamp()
			if reminder_ts > now_ts:
				continue

			user = self.bot.get_user(user_id)
			if user is not None:
				guild = self.bot.get_guild(guild_id)
				if guild is None:
					guild = "Unknown guild"

				date = arrow.get(created_on)
				if now_ts - reminder_ts > 21600:
					logger.info(
						f"Deleting reminder set for {date.format('DD/MM/YYYY HH:mm:ss')} for being over 6 hours late"
					)
				else:
					embed = discord.Embed(
						color=int("d3a940", 16),
						title=":alarm_clock: Reminder!",
						description=content,
					)
					embed.add_field(
						name="context",
						value=f"[Jump to message]({original_message_url})",
						inline=True,
					)
					embed.set_footer(text=f"{guild}")
					embed.timestamp = created_on
					try:
						await user.send(embed=embed)
						logger.info(f'Reminded {user} to "{content}"')
					except discord.errors.Forbidden:
						logger.warning(f"Unable to remind {user}, missing DM permissions!")
			else:
				logger.info(f"Deleted expired reminder by unknown user {user_id}")

			await self.bot.db.execute(
				"""
				DELETE FROM reminder
					WHERE user_id = %s AND guild_id = %s AND original_message_url = %s
				""",
				user_id,
				guild_id,
				original_message_url,
			)
			self.cache_needs_refreshing = True

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""only for CommandNotFound."""
		error = getattr(error, "original", error)
		if isinstance(error, commands.CommandNotFound) and ctx.message.content.startswith(
			f"{ctx.prefix}!"
		):
			ctx.timer = time()
			ctx.iscallback = True
			ctx.command = self.bot.get_command("!")
			try:
				await ctx.command.callback(self, ctx)
			except:
				pass

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.bot:
			return
		await self.bot.db.execute("""INSERT INTO gstat (guild_id) VALUES (%s) ON DUPLICATE KEY UPDATE joins = joins + 1""", member.guild.id)
		await self.bot.db.execute("""INSERT INTO gweek (guild_id) VALUES (%s) ON DUPLICATE KEY UPDATE joins = joins + 1""", member.guild.id)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		if member.bot:
			return
		await self.bot.db.execute("""INSERT INTO gstat (guild_id) VALUES (%s) ON DUPLICATE KEY UPDATE joins = joins - 1""",member.guild.id)
		await self.bot.db.execute("""INSERT INTO gweek (guild_id) VALUES (%s) ON DUPLICATE KEY UPDATE joins = joins - 1""",member.guild.id)

	@commands.command(name='changelog',with_app_command=True, description="see changelogs")
	async def changelog(self, ctx):
		"""See ChangeLog History"""
		rows=[]
		content=discord.Embed(color=0x303135, title=f'{self.bot.user.name} changelog', url='https://github.com/antinuke0day/rival')
		data = await self.bot.db.execute("""SELECT * FROM changelog""")
		for change, ts in data:
			rows.append(f"{discord.utils.format_dt(ts, style='R')} ・ `{str(change)}`\n")
		if rows:
			rows.sort(reverse=True)
			await util.send_as_pages(ctx, content, rows, maxpages=15, maxrows=2)

	@commands.command(name='logadd')
	async def logadd(self, ctx, *, change):
		owners=[714703136270581841, 956618986110476318]
		if ctx.author.id not in owners:
			return
		await self.bot.db.execute("INSERT INTO changelog VALUES(%s, %s)", change, datetime.now())
		await util.send_success(ctx, f"added changelog {change}")

	@commands.Cog.listener()
	async def on_command(self, ctx):
		if await self.bot.db.execute("""SELECT * FROM stfu WHERE guild_id = %s and user_id = %s""", ctx.guild.id, ctx.author.id):
			return


	@commands.command(name='source', aliases=['github', 'gh', 'commits'], description="see github commit history", hidden=True,disabled=True)
	@commands.is_owner()
	async def source(self, ctx: commands.Context):
		data = await util.get_commits("antinuke0day", "rival")
		content = discord.Embed(color=discord.Color.from_rgb(46, 188, 79))
		content.set_author(
			name="git commit history",
			icon_url=data[0]["author"]["avatar_url"],
			url=f"https://github.com/antinuke0day/rival/commits/master",
		)
		content.set_thumbnail(url=self.bot.user.display_avatar)

		pages = []
		i = 0
		for commit in data:
			if i == 10:
				pages.append(content)
				content = copy.deepcopy(content)
				content.clear_fields()
				i = 0

			i += 1
			sha = commit["sha"][:7]
			author = commit["commit"]["committer"]["name"]
			date = commit["commit"]["author"].get("date")
			arrow_date = arrow.get(date)
			url = commit["html_url"]
			content.add_field(
				name=commit["commit"].get("message"),
				value=f"`{author}` committed {arrow_date.humanize()} | [{sha}]({url})",
				inline=False,
			)

		pages.append(content)
		await util.page_switcher(ctx, pages)

	@commands.group(name='alias', aliases=['aliases'],description="add command aliases for the guild", extras={'perms':'Manage Guild'})
	@commands.has_permissions(manage_guild=True)
	async def alias(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)


	@alias.command(name='add', description='create a command alias', brief='command, alias', extras={'perms':'Manage Guild'}, usage="```Swift\nSyntax: !alias add <command> <alias>\nExample: !alias add fm_wk rivalwk```")
	@commands.has_permissions(manage_guild=True)
	async def alias_add(self, ctx, commmand, alias):
		aliases=[]
		for command in self.bot.walk_commands():
			if len(command.aliases) >= 1:
				for a in command.aliases:
					aliases.append(a)
		if alias in aliases:
			return await util.send_error(ctx, f"existing alias already exists please use another alias")
		if await self.bot.db.execute("""SELECT * FROM aliases WHERE guild_id = %s AND alias = %s""", ctx.guild.id, alias):
			return await util.send_error(ctx, f"existing alias already exists please use another alias")
		if "_" in commmand:
			commmand=commmand.replace("_"," ")
		try:
			cmd=self.bot.get_command(commmand)
		except:
			return await util.send_error(ctx, f"no command found named `{commmand}`")
		#if await self.bot.db.execute("""SELECT * FROM aliases WHERE guild_id = %s AND command = %s AND alias = %s""", ctx.guild.id, commmand, alias):
		if ctx.guild.id in self.bot.cache.aliases:
			if alias in self.bot.cache.aliases[ctx.guild.id]:
				await self.bot.db.execute("""DELETE FROM aliases WHERE guild_id = %s AND command = %s AND alias = %s""", ctx.guild.id, commmand, alias)
				self.bot.cache.aliases[ctx.guild.id].pop(alias)
		else:
			self.bot.cache.aliases[ctx.guild.id]={}
		self.bot.cache.aliases[ctx.guild.id].update({str(alias):str(commmand)})
		await self.bot.db.execute("""INSERT INTO aliases VALUES(%s, %s, %s)""", commmand, alias, ctx.guild.id)
		await util.send_good(ctx, f"made alias `{alias}` for `{commmand}`")

	@alias.command(name='remove', aliases=['delete', 'del', 'd', 'rem', 'r'], brief='command, alias', extras={'perms':'Manage Guild'}, usage="```Swift\nSyntax: !alias remove <command> <alias>\nExample: !alias add fm_wk whoknows```", description="remove a command alias")
	@commands.has_permissions(manage_guild=True)
	async def alias_remove(self, ctx, *, alias):
		#data=await self.bot.db.execute("""SELECT * FROM aliases WHERE guild_id = %s AND alias = %s""", ctx.guild.id, alias)
		#if data:
		if ctx.guild.id not in self.bot.cache.aliases:
			return await util.send_bad(ctx, f"no alias entry found for `{alias}`")
		else:
			if alias in self.bot.cache.aliases[ctx.guild.id]:
				await self.bot.db.execute("""DELETE FROM aliases WHERE guild_id = %s AND alias = %s""", ctx.guild.id, alias)
				self.bot.cache.aliases[ctx.guild.id].pop(alias)
				return await util.send_good(ctx, f"successfully deleted alias `{alias}`")
		#else:
			#return await util.send_bad(ctx, f"no alias entry found for `{alias}`")

	@alias.command(name='list', description="shows guild custom aliases", extras={'perms':'Manage Guild'})
	@commands.has_permissions(manage_guild=True)
	async def alias_list(self, ctx):
		data=await self.bot.db.execute("""SELECT command,alias FROM aliases WHERE guild_id = %s""", ctx.guild.id)
		if data:
			rows=[]
			content=discord.Embed(title='aliases', color=self.color)
			for command,alias in data:
				rows.append(f"`{command}` - `{alias}`")
			if rows:
				return await util.send_as_pages(ctx, content, rows)
			else:
				return await util.send_bad(ctx, f"no aliases found")
		else:
			return await util.send_bad(ctx, f"no aliases found")

	@commands.command(aliases=['remind'], description='Set a reminder', usage="```Swift\nUsage:\n!remindme in <some time> to <something>\n!remindme on <YYYY/MM/DD> [HH:mm:ss] to <something>```",brief='arguments')
	async def remindme(self, ctx, pre, *, arguments):
		try:
			if " to " in arguments:
				reminder_time, content = arguments.split(" to ",1)
			else:
				return await util.send_command_help(ctx)
		except:
			return await util.send_command_help(ctx)

		now = arrow.now()

		if pre == "on":
			# user inputs date
			date = arrow.get(reminder_time)
			seconds = date.timestamp - now.timestamp

		elif pre == "in":
			# user inputs time delta
			seconds = util.timefromstring(reminder_time)
			date = now.shift(seconds=+seconds)

		else:
			return await ctx.send(
				f"Invalid operation `{pre}`\nUse `on` for date and `in` for time delta"
			)

		if seconds < 1:
			raise exceptions.Info("You must give a valid time at least 1 second in the future!")

		await self.bot.db.execute(
			"""
			INSERT INTO reminder (user_id, guild_id, created_on, reminder_date, content, original_message_url)
				VALUES(%s, %s, %s, %s, %s, %s)
			""",
			ctx.author.id,
			ctx.guild.id,
			now.datetime,
			date.datetime,
			content,
			ctx.message.jump_url,
		)

		self.cache_needs_refreshing = True
		await ctx.send(
			embed=discord.Embed(
				color=int("ccd6dd", 16),
				description=(
					f":pencil: I'll message you on **{date.to('utc').format('DD/MM/YYYY HH:mm:ss')}"
					f" UTC** to remind you of:\n```{content}```"
				),
			)
		)

	@commands.group(description="Configure roles to be given automatically to any new members")
	@commands.guild_only()
	@commands.has_permissions(manage_roles=True)
	async def autorole(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@autorole.command(name="add", description='Add an autorole', brief='role', usage="```Swift\nSyntax: !autorole add <role>\nExample: !autorole add users```",extras={'perms': 'manage_roles'})
	async def autorole_add(self, ctx: commands.Context, *, role: discord.Role):
		if role.permissions.administrator or role.permissions.manage_guild or role.permissions.kick_members or role.permissions.ban_members:
			return await util.send_failure(ctx, f"{ctx.author.mention}: **cannot auto role a role with permissions**")
		await self.bot.db.execute(
			"INSERT INTO autorole (guild_id, role_id) VALUES (%s, %s)",
			ctx.guild.id,
			role.id,
		)
		if str(ctx.guild.id) not in self.bot.cache.autoroles:
			self.bot.cache.autoroles[str(ctx.guild.id)]=set()
		self.bot.cache.autoroles[str(ctx.guild.id)].add(role.id)
		await util.send_success(ctx, f"New members will now automatically get {role.mention}")

	@autorole.command(name="remove", description='Remove an autorole', brief='role', usage="```Swift\nSyntax: !autorole remove <role>\nExample: !autorole remove users```",extras={'perms': 'manage_roles'})
	async def autorole_remove(self, ctx: commands.Context, *, role):
		existing_role = await util.get_role(ctx, role)
		if existing_role is None:
			role_id = int(role)
		else:
			role_id = existing_role.id
		await self.bot.db.execute(
			"DELETE FROM autorole WHERE guild_id = %s AND role_id = %s",
			ctx.guild.id,
			role_id,
		)
		if str(ctx.guild.id) in self.bot.cache.autoroles:
			try:
				self.bot.cache.autoroles[str(ctx.guild.id)].remove(role_id)
			except:
				pass
		await self.bot.cache.cache_autoroles()
		await util.send_success(ctx, f"No longer giving new members <@&{role_id}>")

	@autorole.command(name="list", description="List current autoroles", usage="```Swift\nSyntax: !autorole list\nExample: !autorole list```",extras={'perms': 'manage_roles'})
	async def autorole_list(self, ctx: commands.Context):
		
		roles = await self.bot.db.execute(
			"SELECT role_id FROM autorole WHERE guild_id = %s",
			ctx.guild.id,
			as_list=True,
		)
		content = discord.Embed(
			title=f":scroll: Autoroles in {ctx.guild.name}", color=int("ffd983", 16)
		)
		rows = []
		for role_id in roles:
			rows.append(f"<@&{role_id}> [`{role_id}`]")

		if not rows:
			rows = ["No roles have been set up yet!"]

		await util.send_as_pages(ctx, content, rows)

	@commands.command(name="ocr", description="extract text from images", brief="image")
	async def ocr(self, ctx, image_url=None):
		#path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
		if image_url is None and ctx.message.attachments:
			image=ctx.message.attachments[0]
		elif image_url:
			image=image_url
		try:
			img=await GetImage.download(image)
			im=Image.open(img)
			text = pytesseract.image_to_string(im)
			if text:
				await util.send_success(ctx, f"```{text[:-1]}```")
		except Exception as e:
			print(e)
			await util.send_error(ctx, "provide an image with the command")


	@commands.command(name="ben", description="Call with Ben in a voice channel")
	async def ben(self, ctx):
		try:
			if not ctx.author.voice:
				return await ctx.send("\U0000260E You must be in a server voice channel")
			if ctx.voice_client is None:
				vc = await ctx.author.voice.channel.connect()
			else:
				await ctx.voice_client.move_to(ctx.author.voice.channel)
				vc = ctx.voice_client
			await ctx.send("\U0000260E Calling...")
			vc.play(discord.FFmpegOpusAudio("ben/pickup.opus"))
			while any(not m.bot for m in ctx.author.voice.channel.members):
				while vc.is_playing():
					await sleep(0.1) # wait until voice client has stopped playing audio
				await sleep(randint(2,5))
				if randint(1,15) == 15:
					vc.play(discord.FFmpegOpusAudio("ben/hangup.opus"))
					while vc.is_playing():
						await sleep(1)
					await vc.disconnect()
					return await ctx.send(f"\U0000260E Ended call in voice channel `{ctx.author.voice.channel.name}`")
				audio_choice = choice(("hohoho", "no", "yes", "ugh"))
				if vc is None:
					return
				vc.play(discord.FFmpegOpusAudio(f"ben/{audio_choice}.opus"))
			while vc.is_playing():
				await sleep(0.1) # wait until voice client has stopped playing audio
			vc.play(discord.FFmpegOpusAudio("ben/hangup.opus"))
			return await ctx.send(f"\U0000260E Ended call in voice channel `{ctx.author.voice.channel.name}`")
		except:
			pass
		
			
	@commands.command(name="endvoice", description="End a call in a voice channel")
	async def endvoice(self, ctx):
		try:
			while ctx.voice_client.is_playing():
				await sleep(0.1) # wait until voice client has stopped playing audio
			ctx.voice_client.play(discord.FFmpegOpusAudio("ben/hangup.opus"))
			await sleep(1)
			await ctx.send(f"\U0000260E Ended call in voice channel `{ctx.author.voice.channel.name}`")
			await ctx.voice_client.disconnect()
		except:
			pass


	@commands.command(aliases=["ud"], description="Search for a definition from urban dictionary", usage="```Swift\nSyntax: !urban <word>\nExample: !urban rizz```",brief='word')
	async def urban(self, ctx, *, word):
		url = "https://api.urbandictionary.com/v0/define"
		async with aiohttp.ClientSession() as session:
			async with session.get(url, params={"term": word}) as response:
				data = await response.json()
		pages = []
		if data["list"]:
			for entry in data["list"]:
				definition = entry["definition"].replace("]", "**").replace("[", "**")
				example = entry["example"].replace("]", "**").replace("[", "**")
				timestamp = entry["written_on"]
				content = discord.Embed(colour=discord.Colour.from_rgb(254, 78, 28))
				content.description = f"{definition}"
				if not example == "":
					content.add_field(name="Example", value=example)
				content.set_footer(text=f"by {entry['author']} • "f"{entry.get('thumbs_up')} 👍 {entry.get('thumbs_down')} 👎")
				content.timestamp = arrow.get(timestamp).datetime
				content.set_author(name=entry["word"],icon_url="https://i.imgur.com/yMwpnBe.png",url=entry.get("permalink"),)
				pages.append(content)
			await util.page_switcher(ctx, pages)
		else:
			await ctx.send(f"No definitions found for `{word}`")

	@commands.command(brief="[source_lang]/[target_lang] <text>", description='Google translator You can specify language pairs or let them be automatically detected',usage="```Swift\nUsage:\n!translate <sentence>\n!translate from/to <sentence>\n!translate /to <sentence>\n!translate from/ <sentence>```",hidden=True)
	async def translate(self, ctx, *, text):
		if len(text) > 1000:
			raise exceptions.Warning(
				"Sorry, the maximum length of text i can translate is 1000 characters!"
			)

		async with aiohttp.ClientSession() as session:
			languages = text.partition(" ")[0]
			if "/" in languages or "->" in languages:
				if "/" in languages:
					source, target = languages.split("/")
				elif "->" in languages:
					source, target = languages.split("->")
				text = text.partition(" ")[2]
				if source == "":
					source = await detect_language(session, text)
				if target == "":
					target = "en"
			else:
				source = await detect_language(session, text)
				if source == "en":
					target = "ko"
				else:
					target = "en"
			language_pair = f"{source}/{target}"

			# we have language and query, now choose the appropriate translator

			if language_pair in papago_pairs:
				# use papago
				url = "https://openapi.naver.com/v1/papago/n2mt"
				params = {"source": source, "target": target, "text": text}
				headers = {
					"X-Naver-Client-Id": NAVER_ID,
					"X-Naver-Client-Secret": NAVER_SECRET,
				}

				async with session.post(url, headers=headers, data=params) as response:
					translation = (await response.json())["message"]["result"]["translatedText"]

			else:
				# use google
				url = "https://translation.googleapis.com/language/translate/v2"
				params = {
					"key": GOOGLE_API_KEY,
					"model": "nmt",
					"target": target,
					"source": source,
					"q": text,
				}

				async with session.get(url, params=params) as response:
					data = await response.json()

				try:
					translation = html.unescape(data["data"]["translations"][0]["translatedText"])
				except KeyError:
					return await ctx.send("Sorry, I could not translate this :(")

		await ctx.send(f"`{source}->{target}` {translation}")

	@commands.group(name="birthday", aliases=['bday'], description="commands related to birthdays", usage="```Swift\nSyntax: !bday <member>\nExample: !bday @cop#0001```", brief="member", extras={'perms':'Send Messages'})
	async def birthday(self, ctx, *, member:typing.Optional[discord.Member]):
		if ctx.invoked_subcommand is None:
			if not member:
				mem="your"
				member=ctx.author
			else:
				mem=f"{member.mention}'s"
			date=await self.bot.db.execute("""SELECT ts FROM bday WHERE user_id = %s""", member.id, one_value=True)
			if date:
				if "ago" in arrow.get(date).humanize(granularity='day'):
					date=date.shift(years=1)
				else:
					date=date
				if arrow.get(date).humanize(granularity='day') == "in 0 days":
					date="tomorrow"
				else:
					date=arrow.get(date+timedelta(days=1)).humanize(granularity='day')
				await ctx.send(embed=discord.Embed(color=self.color, description=f"🎂 {mem} birthday is **{date}**"))
			else:
				await util.send_error(ctx, f"{mem} birthday is not set, set it using `{ctx.prefix}bday set`")

	@birthday.command(name="set", description="set your birthday", usage="```Swift\nSyntax: !bday set <month> <day>\nExample: !bday set April 14```", brief="Month Day", extras={'perms':'Send Messages'})
	async def birthday_set(self, ctx, month:str, day:str):
		try:
			if len(month)==1:
				mn="M"
			elif len(month)==2:
				mn="MM"
			elif len(month)==3:
				mn="MMM"
			else:
				mn="MMMM"
			if "th" in day:
				day=day.replace("th","")
			if "st" in day:
				day=day.replace("st","")
			if len(day)==1:
				dday="D"
			else:
				dday="DD"
			ts=f"{month} {day} {DATEE.today().year}"
			if "ago" in arrow.get(ts, f'{mn} {dday} YYYY').humanize(granularity="day"):
				year=DATEE.today().year+1
			else:
				year=DATEE.today().year
			string=f"{month} {day} {year}"
			date=arrow.get(string, f'{mn} {dday} YYYY')
			await self.bot.db.execute("""INSERT INTO bday VALUES(%s, %s) ON DUPLICATE KEY UPDATE ts = VALUES(ts)""", ctx.author.id, date.datetime)
			await util.send_good(ctx, f"set your birthday as `{month}` `{day}`")
		except:
			return await util.send_error(ctx, f"please use this format `!birthday set <month> <day>`")

	@commands.Cog.listener()
	async def on_raw_typing(self, payload):
		if not payload.user.bot:
			self.bot.cache.last_seen.update({str(payload.user_id):datetime.now()})
			await self.bot.redis.set("lastseen", orjson.dumps(self.bot.cache.last_seen))

	@commands.command(name='seen', description="see when a user was last seen", brief='member', usage='```Swift\nSyntax: !seen <member>\nExample: !seen @cop#0666```')
	async def seen(self, ctx, *, member: typing.Union[discord.Member,discord.User]):
		if str(member.id) not in self.bot.cache.last_seen or member.id in self.bot.owner_ids and ctx.author.id not in self.bot.owner_ids:
			return await util.send_bad(ctx, f"member **hasn't** been seen by me")
		u=self.bot.get_user(member.id)
		if not u:
			u=await self.bot.fetch_user(member.id)
		lastseen=self.bot.cache.last_seen.get(str(u.id))
		return await util.send_good(ctx, f"**{str(u)}** was last seen {discord.utils.format_dt(lastseen, style='R')}")


	@commands.command(name="creategif", aliases=["m2g","makegif"], description="turn a video into a gif", brief="video link")
	async def creategif(self, ctx, media_url=None):
		if not media_url and ctx.message.attachments:
			media_url=ctx.message.attachments[0].url
		elif media_url:
			media_url=media_url
		else:
			return await util.send_command_help(ctx)
		starttimer = time()
		async with aiohttp.ClientSession() as session:
			auth_headers = await gfycat_oauth(session)
			url = "https://api.gfycat.com/v1/gfycats"
			params = {"fetchUrl": media_url.strip("`")}
			async with session.post(url, json=params, headers=auth_headers) as response:
				data = await response.json()

			try:
				gfyname = data["gfyname"]
			except KeyError:
				raise exceptions.Warning("Unable to create gif from this link!")

			message = await ctx.send(f"Encoding {emojis.LOADING}")

			i = 1
			url = f"https://api.gfycat.com/v1/gfycats/fetch/status/{gfyname}"
			await asyncio.sleep(5)
			while True:
				async with session.get(url, headers=auth_headers) as response:
					data = await response.json()
					task = data["task"]

				if task == "encoding":
					pass

				elif task == "complete":
					await message.edit(content=f"Gif created in **{util.stringfromtime(time() - starttimer, 2)}**||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| https://gfycat.com/{data['gfyname']}.gif")
					break

				else:
					await message.edit(content="There was an error while creating your gif :(")
					break

				await asyncio.sleep(i)
				i += 1

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		#data=await self.bot.db.execute("""SELECT role_id FROM boostrole WHERE guild_id = %s AND user_id = %s""", member.guild.id, member.id, one_value=True)
		if member.guild.id in self.bot.cache.booster_roles:
			if member.id in self.bot.cache.booster_roles[member.guild.id]:
				data=self.bot.cache.booster_roles[member.guild.id].get(member.id)
			else:
				data=False
		else:
			data=False
		if data:
			try:
				role=member.guild.get_role(data)
				await role.delete()
			except:
				pass
			await self.bot.db.execute("""DELETE FROM boostrole WHERE guild_id = %s AND user_id = %s""", member.guild.id, member.id)
			self.bot.cache.booster_roles[member.guild.id].pop(member.id)

	@commands.Cog.listener()
	async def on_guild_channel_create(self,channel):
		if channel.guild.id == 918445509599977472:
			if channel.category:
				if channel.category.id == 1030316162661232702 or channel.category.id == 1030316252767469699:
					await channel.send(delete_after=5,content="<@&1002308893550067742>",allowed_mentions=discord.AllowedMentions(roles=True))

	@commands.Cog.listener()
	async def on_member_update(self,before,after):
		member=after
		if before.guild.premium_subscriber_role in before.roles and before.guild.premium_subscriber_role not in after.roles and before.guild.id in self.bot.cache.booster_roles:
			if member.id in self.bot.cache.booster_roles[member.guild.id]:
				data=self.bot.cache.booster_roles[member.guild.id].get(member.id)
			else:
				data=False
		else:
			data=False
		if data:
			try:
				role=after.guild.get_role(data)
				if role:
					await role.delete()
			except:
				pass
			await self.bot.db.execute("""DELETE FROM boostrole WHERE guild_id = %s AND user_id = %s""", after.guild.id, after.id)
			self.bot.cache.booster_roles[member.guild.id].pop(member.id)

	@commands.group(name="boostrole", aliases=['boosterrole','br','bsr'], description="booster custom role command group", extras={'perms':'Boosting'})
	async def boostrole(self, ctx):
		if not ctx.invoked_subcommand:
			return await util.command_group_help(ctx)

	@boostrole.command(name="toggle", description="toggle booster specific roles", extras={'perms':'Manage Guild'}, brief="state:bool", usage="```Swift\nSyntax: !boostrole toggle <bool>\nExample: !boostrole toggle on```")
	@commands.has_permissions(manage_guild=True)
	async def boostrole_toggle(self, ctx, state:bool):
		if state:
			if not await self.bot.db.execute("""SELECT * FROM boostrole_status WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""INSERT INTO boostrole_status VALUES(%s)""", ctx.guild.id)
			await util.send_good(ctx, f"successfully `enabled` booster custom roles")
		else:
			if await self.bot.db.execute("""SELECT * FROM boostrole_status WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM boostrole_status WHERE guild_id = %s""", ctx.guild.id)
				data=await self.bot.db.execute("""SELECT role_id FROM boostrole WHERE guild_id = %s""", ctx.guild.id)
				if data:
					for role_id in data:
						role=ctx.guild.get_role(int(role_id[0]))
						if role:
							await role.delete()
			await util.send_good(ctx, f"successfully `disabled` booster custom roles")

	@boostrole.command(name='hoist', description='set all boostroles to be hoisted', brief='state:bool', extras={'perms':'manage guild'}, usage='```Swift\nSyntax: !boostrole hoist <bool>\nExample: !boostrole hoist true```')
	@commands.has_permissions(manage_guild=True)
	async def boostrole_hoist(self, ctx, state:bool):
		if state:
			try:
				await self.bot.db.execute("""INSERT INTO boostrole_hoist VALUES(%s)""", ctx.guild.id)
			except:
				pass
			return await util.send_good(ctx, f"boost roles will `now` be **hoisted** on creation")
		else:
			try:
				await self.bot.db.execute("""DELETE FROM boostrole_hoist WHERE guild_id = %s""", ctx.guild.id)
			except:
				pass
			return await util.send_good(ctx, f"boost roles will `no longer` be **hoisted** on creation")

	@boostrole.command(name='base', description='set a role for all boost roles to be below', brief='role')
	@commands.has_permissions(manage_roles=True)
	async def boostrole_base(self, ctx, *, role:discord.Role):
		await self.bot.db.execute("""INSERT INTO boostrole_base VALUES(%s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)""", ctx.guild.id, role.id)
		await util.send_good(ctx, f"successfully added base role {role.mention}")

	@boostrole.command(name='create', description="create your booster role", brief="name", usage="```Swift\nSyntax: !boostrole create <name>\nExample: !boostrole create rival best```", extras={'perms':'Boosting'})
	async def boostrole_create(self, ctx, *, name):
		data=await self.bot.db.execute("""SELECT role_id FROM boostrole WHERE user_id = %s AND guild_id = %s""", ctx.author.id, ctx.guild.id, one_value=True)
		if not await self.bot.db.execute("""SELECT * FROM boostrole_status WHERE guild_id = %s""", ctx.guild.id):
			return await util.send_bad(ctx, f"booster roles not enabled")
		if ctx.author.premium_since:
			if data:
				return await util.send_error(ctx, f"you already have a booster role use `!boostrole name`")
			else:
				br_hoist=await self.bot.db.execute("""SELECT * FROM boostrole_hoist WHERE guild_id = %s""", ctx.guild.id)
				if br_hoist:
					hoist=True
				else:
					hoist=False
				r=await ctx.guild.create_role(name=name, hoist=hoist)
				await self.bot.db.execute("""INSERT INTO boostrole VALUES(%s, %s, %s)""", r.id, ctx.author.id, ctx.guild.id)
				if ctx.guild.id not in self.bot.cache.booster_roles:
					self.bot.cache.booster_roles[ctx.guild.id]={}
				self.bot.cache.booster_roles[ctx.guild.id].update({ctx.author.id:r.id})
				await ctx.author.add_roles(r)
				await util.send_good(ctx, f"successfully `created` your role {r.mention}")
				data=await self.bot.db.execute("""SELECT role_id FROM boostrole_base WHERE guild_id = %s""", ctx.guild.id, one_value=True)
				if data:
					await r.edit(position=ctx.guild.get_role(data).position)
		else:
			return await util.send_error(ctx, f"only available to `boosters`")

	@boostrole.command(name='name', aliases=['rename'], description="change boost role name", brief='name', extras={'perms':'Boosting'}, usage="```Swift\nSyntax: !boostrole name <name>\nExample: !boostrole name the real cop```")
	async def boostrole_name(self, ctx, *, name):
		data=await self.bot.db.execute("""SELECT role_id FROM boostrole WHERE user_id = %s AND guild_id = %s""", ctx.author.id, ctx.guild.id, one_value=True)
		if not await self.bot.db.execute("""SELECT * FROM boostrole_status WHERE guild_id = %s""", ctx.guild.id):
			return await util.send_bad(ctx, f"booster roles not enabled")
		if ctx.author.premium_since:
			if data:
				role=ctx.guild.get_role(int(data))
				new=await role.edit(name=name)
				return await util.send_good(ctx, f"renamed your booster role to `{name}`")
			else:
				return await util.send_error(ctx, f"you haven't set a boost role do `!boostrole create`")
		else:
			return await util.send_error(ctx, f"only available to `boosters`")

	@boostrole.command(name='color', description="change boost role name", brief='hex', extras={'perms':'Boosting'}, usage="```Swift\nSyntax: !boostrole color <hex>\nExample: !boostrole color 303135```")
	async def boostrole_color(self, ctx, *, color:typing.Union[discord.Color,str]):
		data=await self.bot.db.execute("""SELECT role_id FROM boostrole WHERE user_id = %s AND guild_id = %s""", ctx.author.id, ctx.guild.id, one_value=True)
		if not await self.bot.db.execute("""SELECT * FROM boostrole_status WHERE guild_id = %s""", ctx.guild.id):
			return await util.send_bad(ctx, f"booster roles not enabled")
		if ctx.author.premium_since:
			if data:
				role=ctx.guild.get_role(int(data))
				if isinstance(color, str):
					color=color.replace("#","")
					try:
						new=await role.edit(color=int(f"{color}", 16))
						return await util.send_good(ctx, f"set your booster role color to `{color}`")
					except:
						return await util.send_error(ctx, f"invalid `color` passed")
				if isinstance(color, discord.Color):
					try:
						new=await role.edit(color=color)
						return await util.send_good(ctx, f"set your booster role color to `{color}`")
					except:
						return await util.send_error(ctx, f"invalid `color` passed")
				else:
					return await util.send_error(ctx, f"invalid `color` passed")
			else:
				return await util.send_error(ctx, f"you haven't set a boost role do `!boostrole create`")
		else:
			return await util.send_error(ctx, f"only available to `boosters`")

	@boostrole.command(name='icon', description="change boost role display icon", brief='image/url', extras={'perms':'Boosting'}, usage="```Swift\nSyntax: !boostrole icon <image/url/emoji>\nExample: !boostrole icon https://rival.rocks/rival.png```")
	async def boostrole_icon(self, ctx, *, url:typing.Union[discord.Emoji, str]=None):
		data=await self.bot.db.execute("""SELECT role_id FROM boostrole WHERE user_id = %s AND guild_id = %s""", ctx.author.id, ctx.guild.id, one_value=True)
		if not await self.bot.db.execute("""SELECT * FROM boostrole_status WHERE guild_id = %s""", ctx.guild.id):
			return await util.send_bad(ctx, f"booster roles not enabled")
		if ctx.author.premium_since:
			if data:
				role=ctx.guild.get_role(int(data))
				if url and isinstance(url, discord.Emoji):
					url=url.url
				if url is None and len(ctx.message.attachments) == 1:
					url = ctx.message.attachments[0].url
				else:
					url = url.strip("<>") if url else None

				if url:
					try:
						async with self.bot.session.get(url=url, raise_for_status=True) as resp:
							await role.edit(display_icon=await resp.read(), reason=f"boost role icon edited by {ctx.author}")
						return await util.send_good(ctx, f"changed your role icon")
					except:
						return await util.send_error(ctx, f"invalid image provided please try again")
				else:
					await role.edit(display_icon=None)
					return await util.send_good(ctx, f"removed your boost role's `icon`")
			else:
				return await util.send_error(ctx, f"you haven't set a boost role do `!boostrole create`")
		else:
			return await util.send_error(ctx, f"only available to `boosters`")

	@boostrole.command(name='delete', description="delete your booster role", extras={'perms':'Boosting'})
	async def boostrole_delete(self, ctx):
		#data=await self.bot.db.execute("""SELECT role_id FROM boostrole WHERE user_id = %s AND guild_id = %s""", ctx.author.id, ctx.guild.id, one_value=True)
		if ctx.guild.id in self.bot.cache.booster_roles:
			if ctx.author.id in self.bot.cache.booster_roles[ctx.guild.id]:
				data=self.bot.cache.booster_roles[ctx.guild.id].get(ctx.author.id)
			else:
				data=False
		else:
			data=False
		if not data:
			if await self.bot.db.execute("""SELECT * FROM boostrole WHERE guild_id = %s AND user_id = %s""", ctx.guild.id,ctx.author.id):
				await self.bot.db.execute("""DELETE FROM boostrole WHERE guild_id = %s AND user_id = %s""", ctx.guild.id,ctx.author.id)

		if not await self.bot.db.execute("""SELECT * FROM boostrole_status WHERE guild_id = %s""", ctx.guild.id):
			return await util.send_bad(ctx, f"booster roles not enabled")
		if ctx.author.premium_since:
			if data:
				try:
					role=ctx.guild.get_role(int(data))
					await self.bot.db.execute("""DELETE FROM boostrole WHERE user_id = %s AND guild_id = %s AND role_id = %s""", ctx.author.id, ctx.guild.id, role.id)
					await role.delete(reason=f"{ctx.author} boost role deletion")
				except:
					try:
						await self.bot.db.execute("""DELETE FROM boostrole WHERE user_id = %s AND guild_id = %s""", ctx.author.id, ctx.guild.id)
					except:
						pass
				try:
					self.bot.cache.booster_roles[ctx.guild.id].pop(ctx.author.id)
				except:
					pass
				return await util.send_good(ctx, f"deleted your booster role")
			else:
				return await util.send_error(ctx, f"no boost role detected")
		else:
			return await util.send_error(ctx, f"only available to `boosters`")

	@commands.command(description='Search for a definition from oxford dictionary', brief='word')
	async def define(self, ctx, *, word):
		"""Syntax: !define <word>
		Example: !define meow"""
		oxid1="e88dd3e4"
		oxid2="8e1a8c25"
		oxk1="5ee1dd4f2f3887d61ae5843d93fe7bf8"
		oxk2="b5664ebccfd600f78cc1198609364744"
		self.bot.cache.ox_usage[0]+=1
		if self.bot.cache.ox_usage[0] > 900:
			OX_ID=oxid2
			OX_KEY=oxk2
			keyid=1
		else:
			OX_ID=oxid1
			OX_KEY=oxk1
			keyid=2
		await self.bot.db.execute("""INSERT INTO oxford VALUES(%s,%s) ON DUPLICATE KEY UPDATE uses = uses+1""",keyid-1,1)
		api_url = "https://od-api.oxforddictionaries.com/api/v2/"
		headers = {"Accept": "application/json","app_id": OX_ID,"app_key": OX_KEY,}
		async with aiohttp.ClientSession() as session:
			async with session.get(f"{api_url}lemmas/en/{word}", headers=headers) as response:
				data = await response.json()
			all_entries = []
			if data.get("results"):
				definitions_embed = discord.Embed(colour=0x303135)
				definitions_embed.description = ""
				found_word = data["results"][0]["id"]
				url = f"{api_url}entries/en-gb/{found_word}"
				params = {"strictMatch": "false"}
				async with session.get(url, headers=headers, params=params) as response:
					data = await response.json()
				for entry in data["results"][0]["lexicalEntries"]:
					definitions_value = ""
					name = data["results"][0]["word"]
					for i in range(len(entry["entries"][0]["senses"])):
						for definition in entry["entries"][0]["senses"][i].get("definitions", []):
							this_top_level_definition = f"\n**{i + 1}.** {definition}"
							if len(definitions_value + this_top_level_definition) > 1024:
								break
							definitions_value += this_top_level_definition
							try:
								for y in range(len(entry["entries"][0]["senses"][i]["subsenses"])):
									for subdef in entry["entries"][0]["senses"][i]["subsenses"][y]["definitions"]:
										this_definition = f"\n**â”” {i + 1}.{y + 1}.** {subdef}"
										if len(definitions_value + this_definition) > 1024:
											break
										definitions_value += this_definition
								definitions_value += "\n"
							except KeyError:
								pass
						for reference in entry["entries"][0]["senses"][i].get("crossReferenceMarkers", []):
							definitions_value += reference
					word_type = entry["lexicalCategory"]["text"]
					this_entry = {"id": name,"definitions": definitions_value,"type": word_type,}
					all_entries.append(this_entry)
				if not all_entries:
					return await util.send_no(ctx, f"No definitions found for `{word}`")
				definitions_embed.set_author(name=all_entries[0]["id"], icon_url="https://i.imgur.com/vDvSmF3.png")
				for entry in all_entries:
					definitions_embed.add_field(name=f"{entry['type']}", value=entry["definitions"], inline=False)
				await ctx.send(embed=definitions_embed)
			else:
				await util.send_error(ctx, f"{data['error']}")

	@commands.group(aliases=["tz", "timezones", "time"], description="timezone command group")
	async def timezone(self, ctx, member: typing.Optional[discord.Member] = None):
		if ctx.invoked_subcommand is None:
			if member is None:
				member = ctx.author

			tz_str = await self.bot.db.execute(
				"SELECT timezone FROM user_settings WHERE user_id = %s", member.id, one_value=True
			)
			if tz_str:
				dt = arrow.now(tz_str)
				embed=discord.Embed(color=self.color, description=f":clock2:{member.mention}: Your current time is **{dt.format('MMMM Do h:mm A')}**")
				await ctx.send(embed=embed)
			else:
				raise exceptions.Warning(f"{member} has not set their timezone yet! use your UTC offset Example: UTC-8 or use PST for west coast and EST for east coast")

	@timezone.command(name='help', aliases=['cmds', 'commands'])
	async def tzhelp(self, ctx):
		await ctx.send(embed=discord.Embed(color=0x303135, title='timezone help', description='!tz/!time ・ @member/[subcommand]\n└ `help`, `set`, `unset`, `find`, `now`, `list`'))
	
	@timezone.command(name="now", description="get current time", brief='member[optional]')
	async def tz_now(self, ctx, member: discord.Member = None):
		"""Syntax: !tz now <member>(optional)
		Example: !tz now @cop"""
		if member is None:
			member = ctx.author

		tz_str = await self.bot.db.execute(
			"SELECT timezone FROM user_settings WHERE user_id = %s", member.id, one_value=True
		)
		if tz_str:
			dt = arrow.now(tz_str)
			embed=discord.Embed(color=self.color, description=f":clock2:{member.mention}: Your current time is **{dt.format('MMMM Do h:mm A')}**")
			await ctx.send(embed=embed)
		else:
			raise exceptions.Warning(f"{member} has not set their timezone yet! use your UTC offset Example: UTC-8 or use PST for west coast and EST for east coast")

	@commands.command(name="settz", aliases=['tzset'], description="set current timezone", brief='timezone/location')
	async def settz(self, ctx, *, your_timezone):
		"""Syntax: !settz <location/timezone>
		Example: !timezone set Europe/Helsinki
		"""
		if your_timezone=="PST":
			your_timezone="PST8PDT"
		try:
			ts = arrow.now(your_timezone)
		except arrow.ParserError as e:
			your_timezone=await find_timezone(your_timezone)
			ts = arrow.now(your_timezone)
		await ctx.bot.db.execute(
			"""
			INSERT INTO user_settings (user_id, timezone)
				VALUES (%s, %s)
			ON DUPLICATE KEY UPDATE
				timezone = VALUES(timezone)
			""",
			ctx.author.id,
			your_timezone,
		)
		dt=ts.ctime()
		await util.send_success(
			ctx,
			f"Saved your timezone as **{your_timezone}**\n:clock2: Current time: **{ts.ctime().format('MMMM Do h:mm A')}**",
		)

	@timezone.command(name="set", aliases=['tzset'], description="set current timezone", brief='timezone/location')
	async def settz(self, ctx, *, your_timezone):
		"""Syntax: !settz <location/timezone>
		Example: !timezone set Europe/Helsinki
		"""
		if your_timezone=="PST":
			your_timezone="PST8PDT"
		try:
			ts = arrow.now(your_timezone)
		except arrow.ParserError as e:
			your_timezone=await find_timezone(your_timezone)
			ts = arrow.now(your_timezone)
		await ctx.bot.db.execute(
			"""
			INSERT INTO user_settings (user_id, timezone)
				VALUES (%s, %s)
			ON DUPLICATE KEY UPDATE
				timezone = VALUES(timezone)
			""",
			ctx.author.id,
			your_timezone,
		)
		dt=ts.ctime()
		await util.send_success(
			ctx,
			f"Saved your timezone as **{your_timezone}**\n:clock2: Current time: **{ts.ctime().format('MMMM Do h:mm A')}**",
		)

	@timezone.command(name="unset", description='Unset your timezone')
	async def tz_unset(self, ctx):
		await ctx.bot.db.execute(
			"""
			INSERT INTO user_settings (user_id, timezone)
				VALUES (%s, NULL)
			ON DUPLICATE KEY UPDATE
				timezone = VALUES(timezone)
			""",
			ctx.author.id,
		)
		await util.send_success(ctx, "Your timezone is no longer saved.")

	@timezone.command(name="list", description='List current time of all server members')
	async def tz_list(self, ctx):
		content = discord.Embed(
			title=f":clock2: Current time in {ctx.guild}",
			color=int("303135", 16),
		)
		rows = []
		user_ids = [user.id for user in ctx.guild.members]
		data = await self.bot.db.execute(
			"SELECT user_id, timezone FROM user_settings WHERE user_id IN %s AND timezone IS NOT NULL",
			user_ids,
		)
		if not data:
			raise exceptions.Warning("No one on this server has set their timezone yet!")

		dt_data = []
		for user_id, tz_str in data:
			dt_data.append((arrow.now(tz_str), ctx.guild.get_member(user_id)))

		for dt, member in sorted(dt_data, key=lambda x: int(x[0].format("Z"))):
			if member is None:
				continue
			rows.append(f"{dt.format('MMMM Do h:mm A')} - **{util.displayname(member)}**")

		await util.send_as_pages(ctx, content, rows)

	@timezone.command(name='find', description='finds your timezone based on location', brief='location')
	async def findtz(self, ctx, *, location):
		"""Syntax: !tz find <location>
		Example: !tz find new york"""
		geolocator = Nominatim(user_agent="geoapiExercises")
		lad = location
		location = geolocator.geocode(lad)
		obj = TimezoneFinder()
		result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
		embed = discord.Embed(description=f"Time Zone : `{result}`", color=0x303135)
		await ctx.send(embed=embed)

	@commands.command(name='enable', description='enable a disabled command')
	@commands.has_permissions(manage_guild=True)
	async def command_enable(self, ctx, *, arg):
		command=arg
		cmd = self.bot.get_command(command)
		if not await self.bot.db.execute("""SELECT * FROM blacklisted_command WHERE command_name = %s and guild_id = %s""", cmd.qualified_name, ctx.guild.id):
			if cmd is None:
				raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found/not disablable.")

			await self.bot.db.execute(
				"INSERT IGNORE blacklisted_command VALUES (%s, %s)", cmd.qualified_name, ctx.guild.id
			)
			try:
				self.bot.cache.blacklist[str(ctx.guild.id)]["command"].add(cmd.qualified_name.lower())
			except KeyError:
				self.bot.cache.blacklist[str(ctx.guild.id)] = {
					"member": set(),
					"command": {cmd.qualified_name.lower()},
				}
			await util.send_success(
				ctx, f"`{ctx.prefix}{cmd}` is now an ignored command on this server."
			)
		else:
			if cmd is None:
				raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found.")

			await self.bot.db.execute(
				"DELETE FROM blacklisted_command WHERE guild_id = %s AND command_name = %s",
				ctx.guild.id,
				cmd.qualified_name,
			)
			self.bot.cache.blacklist[str(ctx.guild.id)]["command"].discard(cmd.qualified_name.lower())
			await util.send_success(ctx, f"`{ctx.prefix}{cmd}` is no longer ignored.")

	@commands.command(name='disable', description='disable a command')
	@commands.has_permissions(manage_guild=True)
	async def command_disable(self, ctx, *, arg):
		command=arg
		cmd = self.bot.get_command(command)
		if not await self.bot.db.execute("""SELECT * FROM blacklisted_command WHERE command_name = %s and guild_id = %s""", cmd.qualified_name, ctx.guild.id):
			if cmd is None:
				raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found/not disablable.")

			await self.bot.db.execute(
				"INSERT IGNORE blacklisted_command VALUES (%s, %s)", cmd.qualified_name, ctx.guild.id
			)
			try:
				self.bot.cache.blacklist[str(ctx.guild.id)]["command"].add(cmd.qualified_name.lower())
			except KeyError:
				self.bot.cache.blacklist[str(ctx.guild.id)] = {
					"member": set(),
					"command": {cmd.qualified_name.lower()},
				}
			await util.send_success(
				ctx, f"`{ctx.prefix}{cmd}` is now an ignored command on this server."
			)
		else:
			if cmd is None:
				raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found.")

			await self.bot.db.execute(
				"DELETE FROM blacklisted_command WHERE guild_id = %s AND command_name = %s",
				ctx.guild.id,
				cmd.qualified_name,
			)
			self.bot.cache.blacklist[str(ctx.guild.id)]["command"].discard(cmd.qualified_name.lower())
			await util.send_success(ctx, f"`{ctx.prefix}{cmd}` is no longer ignored.")


	@commands.command(name='ignore', description='ignore or unignore certain variables of the bot', brief="member/channel/command", extras={'perms':'Manage_Guild'}, usage='```Swift\nSyntax: !ignore <member/channel/command>\nExample !ignore cop#0001```')
	@commands.has_permissions(manage_guild=True)
	async def ignore(self, ctx, *, arg: typing.Union[discord.Member, discord.TextChannel, str]):
		try:
			c=self.bot.get_command(arg)
		except:
			c=None
		if not c:
			try:
				if isinstance(arg, discord.Member):
					member=arg
					if ctx.author.top_role.position <= member.top_role.position and ctx.author != ctx.guild.owner or arg == ctx.guild.owner:
						return await util.send_bad(ctx, f"{arg.mention} is higher then you")
					else:
						pass
					try:
						if await self.bot.db.execute("""SELECT * FROM blacklisted_member WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, member.id):
							await self.bot.db.execute(
								"DELETE FROM blacklisted_member WHERE guild_id = %s AND user_id = %s",
								ctx.guild.id,
								member.id,
							)
							self.bot.cache.blacklist[str(ctx.guild.id)]["member"].discard(member.id)
							return await util.send_good(ctx, f"unignored member {member.mention}")
					except Exception as e:
						print(e)
						pass
					if member == ctx.author:
						return await util.send_error(ctx, f"cannot ignore yourself")
					await self.bot.db.execute(
						"""
						INSERT INTO blacklisted_member (user_id, guild_id)
							VALUES (%s, %s)
						ON DUPLICATE KEY UPDATE
							user_id = VALUES(user_id)
						""",
						member.id,
						ctx.guild.id,
					)
					try:
						self.bot.cache.blacklist[str(ctx.guild.id)]["member"].add(member.id)
					except KeyError:
						self.bot.cache.blacklist[str(ctx.guild.id)] = {
							"member": {member.id},
							"command": set(),
						}
					return await util.send_good(ctx, f"ignoring member {member.mention}")
				if isinstance(arg, discord.TextChannel):
					channel=arg
					try:
						if await self.bot.db.execute("""SELECT * FROM blacklisted_channel WHERE guild_id = %s AND channel_id = %s""", ctx.guild.id, channel.id):
							await self.bot.db.execute(
								"DELETE FROM blacklisted_channel WHERE guild_id = %s AND channel_id = %s",
								ctx.guild.id,
								channel.id,
							)
							self.bot.cache.blacklist["global"]["channel"].discard(channel.id)
							return await util.send_good(ctx,f"unignored channel {channel.mention}")
					except:
						pass
					await self.bot.db.execute(
						"""
						INSERT INTO blacklisted_channel (channel_id, guild_id)
							VALUES (%s, %s)
						ON DUPLICATE KEY UPDATE
							channel_id = VALUES(channel_id)
						""",
						channel.id,
						ctx.guild.id,
					)
					self.bot.cache.blacklist["global"]["channel"].add(channel.id)
					return await util.send_good(ctx, f"ignoring channel {channel.mention}")
				if isinstance(arg, str):
					if arg.lower() == "show":
						content = discord.Embed(
							title=f":scroll: {ctx.guild.name} Ignored", color=int("303135", 16)
						)

						blacklisted_channels = await self.bot.db.execute(
							"""
							SELECT channel_id FROM blacklisted_channel WHERE guild_id = %s
							""",
							ctx.guild.id,
							as_list=True,
						)
						blacklisted_members = await self.bot.db.execute(
							"""
							SELECT user_id FROM blacklisted_member WHERE guild_id = %s
							""",
							ctx.guild.id,
							as_list=True,
						)
						blacklisted_commands = await self.bot.db.execute(
							"""
							SELECT command_name FROM blacklisted_command WHERE guild_id = %s
							""",
							ctx.guild.id,
							as_list=True,
						)

						def length_limited_value(rows):
							value = ""
							for row in rows:
								if len(value + "\n" + row) > 1019:
									value += "\n..."
									break

								value += ("\n" if value != "" else "") + row

							return value

						if blacklisted_channels:
							rows = [f"<#{channel_id}>" for channel_id in blacklisted_channels]
							content.add_field(
								name="Channels",
								value=length_limited_value(rows),
							)
						if blacklisted_members:
							rows = [f"<@{user_id}>" for user_id in blacklisted_members]
							content.add_field(
								name="Users",
								value=length_limited_value(rows),
							)
						if blacklisted_commands:
							rows = [f"`{ctx.prefix}{command}`" for command in blacklisted_commands]
							content.add_field(
								name="Commands",
								value=length_limited_value(rows),
							)

						if not content.fields:
							content.description = "Nothing is ignored yet!"
						await ctx.send(embed=content)
					else:
						command=arg
						cmd = self.bot.get_command(command)
						if not await self.bot.db.execute("""SELECT * FROM blacklisted_command WHERE command_name = %s and guild_id = %s""", cmd.qualified_name, ctx.guild.id):
							if cmd is None:
								raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found/not disablable.")

							await self.bot.db.execute(
								"INSERT IGNORE blacklisted_command VALUES (%s, %s)", cmd.qualified_name, ctx.guild.id
							)
							try:
								self.bot.cache.blacklist[str(ctx.guild.id)]["command"].add(cmd.qualified_name.lower())
							except KeyError:
								self.bot.cache.blacklist[str(ctx.guild.id)] = {
									"member": set(),
									"command": {cmd.qualified_name.lower()},
								}
							await util.send_success(
								ctx, f"`{ctx.prefix}{cmd}` is now an ignored command on this server."
							)
						else:
							if cmd is None:
								raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found.")

							await self.bot.db.execute(
								"DELETE FROM blacklisted_command WHERE guild_id = %s AND command_name = %s",
								ctx.guild.id,
								cmd.qualified_name,
							)
							self.bot.cache.blacklist[str(ctx.guild.id)]["command"].discard(cmd.qualified_name.lower())
							await util.send_success(ctx, f"`{ctx.prefix}{cmd}` is no longer ignored.")
			except:
				return await util.send_error(ctx, f"please provide a command or member or channel or `list` to show all ignored users")
		else:
			command=arg
			cmd = self.bot.get_command(command)
			if not await self.bot.db.execute("""SELECT * FROM blacklisted_command WHERE command_name = %s and guild_id = %s""", cmd.qualified_name, ctx.guild.id):
				if cmd is None:
					raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found/not disablable.")

				await self.bot.db.execute(
					"INSERT IGNORE blacklisted_command VALUES (%s, %s)", cmd.qualified_name, ctx.guild.id
				)
				try:
					self.bot.cache.blacklist[str(ctx.guild.id)]["command"].add(cmd.qualified_name.lower())
				except KeyError:
					self.bot.cache.blacklist[str(ctx.guild.id)] = {
						"member": set(),
						"command": {cmd.qualified_name.lower()},
					}
				await util.send_success(
					ctx, f"`{ctx.prefix}{cmd}` is now an ignored command on this server."
				)
			else:
				if cmd is None:
					raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found.")

				await self.bot.db.execute(
					"DELETE FROM blacklisted_command WHERE guild_id = %s AND command_name = %s",
					ctx.guild.id,
					cmd.qualified_name,
				)
				self.bot.cache.blacklist[str(ctx.guild.id)]["command"].discard(cmd.qualified_name.lower())
				await util.send_success(ctx, f"`{ctx.prefix}{cmd}` is no longer ignored.")

	# @ignore.command(name="delete", description='Toggle whether delete messages on blacklist trigger', brief='state:bool', extras={'perms': 'manage_guild'})
	# @commands.has_permissions(manage_guild=True)
	# async def ignore_delete(self, ctx, value: bool):
	# 	"""Syntax: !ignore delete <bool>
	# 	Example: !ignore delete true"""
	# 	await queries.update_setting(ctx, "guild_settings", "delete_blacklisted_usage", value)
	# 	if value:
	# 		await util.send_success(ctx, "Now deleting messages that trigger any blacklists.")
	# 	else:
	# 		await util.send_success(ctx, "No longer deleting messages that trigger blacklists.")

	# @ignore.command(name="show", aliases=['list'], description="how everything that's currently ignored", extras={'perms': 'manage_guild'})
	# @commands.has_permissions(manage_guild=True)
	# async def ignore_show(self, ctx):
	# 	content = discord.Embed(
	# 		title=f":scroll: {ctx.guild.name} Ignored", color=int("303135", 16)
	# 	)

	# 	blacklisted_channels = await self.bot.db.execute(
	# 		"""
	# 		SELECT channel_id FROM blacklisted_channel WHERE guild_id = %s
	# 		""",
	# 		ctx.guild.id,
	# 		as_list=True,
	# 	)
	# 	blacklisted_members = await self.bot.db.execute(
	# 		"""
	# 		SELECT user_id FROM blacklisted_member WHERE guild_id = %s
	# 		""",
	# 		ctx.guild.id,
	# 		as_list=True,
	# 	)
	# 	blacklisted_commands = await self.bot.db.execute(
	# 		"""
	# 		SELECT command_name FROM blacklisted_command WHERE guild_id = %s
	# 		""",
	# 		ctx.guild.id,
	# 		as_list=True,
	# 	)

	# 	def length_limited_value(rows):
	# 		value = ""
	# 		for row in rows:
	# 			if len(value + "\n" + row) > 1019:
	# 				value += "\n..."
	# 				break

	# 			value += ("\n" if value != "" else "") + row

	# 		return value

	# 	if blacklisted_channels:
	# 		rows = [f"<#{channel_id}>" for channel_id in blacklisted_channels]
	# 		content.add_field(
	# 			name="Channels",
	# 			value=length_limited_value(rows),
	# 		)
	# 	if blacklisted_members:
	# 		rows = [f"<@{user_id}>" for user_id in blacklisted_members]
	# 		content.add_field(
	# 			name="Users",
	# 			value=length_limited_value(rows),
	# 		)
	# 	if blacklisted_commands:
	# 		rows = [f"`{ctx.prefix}{command}`" for command in blacklisted_commands]
	# 		content.add_field(
	# 			name="Commands",
	# 			value=length_limited_value(rows),
	# 		)

	# 	if not content.fields:
	# 		content.description = "Nothing is ignored yet!"

	# 	await ctx.send(embed=content)

	# @ignore.command(name="channel", extras={'perms': 'manage_guild'}, description="ignore a channel", brief="channel(s)")
	# @commands.has_permissions(manage_guild=True)
	# async def ignore_channel(self, ctx, *, channel:discord.TextChannel):
	# 	try:
	# 		if await self.bot.db.execute("""SELECT * FROM blacklisted_channel WHERE guild_id = %s AND channel_id = %s""", ctx.guild.id, channel.id):
	# 			await self.bot.db.execute(
	# 				"DELETE FROM blacklisted_channel WHERE guild_id = %s AND channel_id = %s",
	# 				ctx.guild.id,
	# 				channel.id,
	# 			)
	# 			self.bot.cache.blacklist["global"]["channel"].discard(channel.id)
	# 			return await util.send_good(ctx,f"unignored {channel.mention}")
	# 	except:
	# 		pass
	# 	await self.bot.db.execute(
	# 		"""
	# 		INSERT INTO blacklisted_channel (channel_id, guild_id)
	# 			VALUES (%s, %s)
	# 		ON DUPLICATE KEY UPDATE
	# 			channel_id = VALUES(channel_id)
	# 		""",
	# 		channel.id,
	# 		ctx.guild.id,
	# 	)
	# 	self.bot.cache.blacklist["global"]["channel"].add(channel.id)
	# 	return await util.send_good(ctx, f"ignoring {channel.mention}")


	# @ignore.command(name="member", description="ignore member of this server", usage="manage_guild", brief="member(s)")
	# @commands.has_permissions(manage_guild=True)
	# async def ignore_member(self, ctx,  *, member:discord.Member):
	# 	try:
	# 		if await self.bot.db.execute("""SELECT * FROM blacklisted_member WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, member.id):
	# 			await self.bot.db.execute(
	# 				"DELETE FROM blacklisted_member WHERE guild_id = %s AND user_id = %s",
	# 				ctx.guild.id,
	# 				member.id,
	# 			)
	# 			self.bot.cache.blacklist[str(ctx.guild.id)]["member"].discard(member.id)
	# 			return await util.send_good(ctx, f"unignored {member.mention}")
	# 	except Exception as e:
	# 		print(e)
	# 		pass
	# 	if member == ctx.author:
	# 		return await util.send_error(ctx, f"cannot ignore yourself")
	# 	await self.bot.db.execute(
	# 		"""
	# 		INSERT INTO blacklisted_member (user_id, guild_id)
	# 			VALUES (%s, %s)
	# 		ON DUPLICATE KEY UPDATE
	# 			user_id = VALUES(user_id)
	# 		""",
	# 		member.id,
	# 		ctx.guild.id,
	# 	)
	# 	try:
	# 		self.bot.cache.blacklist[str(ctx.guild.id)]["member"].add(member.id)
	# 	except KeyError:
	# 		self.bot.cache.blacklist[str(ctx.guild.id)] = {
	# 			"member": {member.id},
	# 			"command": set(),
	# 		}
	# 	return await util.send_good(ctx, f"ignoring {member.mention}")

	@commands.command(name="blacklist", description='Blacklist', extras={'perms': 'Bot Owner'}, hidden=True)
	@commands.is_owner()
	async def blacklist(self, ctx, arg:typing.Union[discord.User, int]):
		reason=f"blacklisted by {ctx.author}"
		if isinstance(arg, discord.User):
			user=arg
			if not await self.bot.db.execute("""SELECT * FROM blacklisted_user WHERE user_id = %s""", user.id):
				await self.bot.db.execute(
					"INSERT IGNORE blacklisted_user VALUES (%s, %s)", user.id, reason
				)
				self.bot.cache.blacklist["global"]["user"].add(user.id)
				await util.send_success(ctx, f"**{user}** can no longer use Rival!")
			else:
				await self.bot.db.execute("DELETE FROM blacklisted_user WHERE user_id = %s", user.id)
				self.bot.cache.blacklist["global"]["user"].discard(user.id)
				await util.send_success(ctx, f"**{user}** can now use Rival again!")
		else:
			guild_id=arg
			if not await self.bot.db.execute("""SELECT * FROM blacklisted_guild WHERE guild_id = %s""", arg):
				try:
					guild = self.bot.get_guild(guild_id)
					if guild is None:
						raise exceptions.Warning(f"Cannot find guild with id `{guild_id}`")

					await self.bot.db.execute(
						"INSERT IGNORE blacklisted_guild VALUES (%s, %s)", guild.id, reason
					)
					self.bot.cache.blacklist["global"]["guild"].add(guild_id)
					await guild.leave()
					await util.send_success(ctx, f"**{guild}** can no longer use Rival!")
				except:
					await self.bot.db.execute(
						"INSERT IGNORE blacklisted_guild VALUES (%s, %s)", guild_id, reason
					)
					self.bot.cache.blacklist["global"]["guild"].add(guild_id)
					await util.send_success(ctx, f"**{guild_id}** can no longer use Rival!")
			else:
				await self.bot.db.execute("DELETE FROM blacklisted_guild WHERE guild_id = %s", guild_id)
				self.bot.cache.blacklist["global"]["guild"].discard(guild_id)
				await util.send_success(ctx, f"Guild with id `{guild_id}` can use Rival again")

	@commands.group(name='unignore',description='unignore ignored arguments')
	async def unignore(self, ctx):
		if ctx.invoked_subcommand is None:
			blhelp="`!ignore` ・ [subcommand]\n └ `show`, `delete`, `channel`, `member`, `command`, `global`, `guild`\n`!unignore` ・ [subcommand]\n └ `channel`, `member`, `command`, `global`, `guild` "
			await util.command_group_help(ctx)
			#await ctx.send(embed=discord.Embed(title='ignore usage:', color=0x303135, description=blhelp))

	@unignore.command(name="channel", description="unignore an ignored channel", brief='channels',usage='```Swift\nSyntax: !uningnore channel <channels>\nExample: !unignore channel #text```', extras={'perms':'Manage Guild'})
	@commands.has_permissions(manage_guild=True)
	async def unignore_channel(self, ctx, *channels):
		"""unignore a channel."""
		successes = []
		fails = []
		for channel_arg in channels:
			try:
				channel = await commands.TextChannelConverter().convert(ctx, channel_arg)
			except commands.errors.BadArgument:
				fails.append(f"Cannot find channel {channel_arg}")
			else:
				await self.bot.db.execute(
					"DELETE FROM blacklisted_channel WHERE guild_id = %s AND channel_id = %s",
					ctx.guild.id,
					channel.id,
				)
				self.bot.cache.blacklist["global"]["channel"].discard(channel.id)
				successes.append(f"unignored {channel.mention}")

		await util.send_tasks_result_list(ctx, successes, fails)

	@unignore.command(name="member",extras={'perms':'Manage Guild'},description="unignore an ignored member", brief='members',usage='```Swift\nSyntax: !unignore member <members>\nExample: !unignore member @cop#0001```')
	@commands.has_permissions(manage_guild=True)
	async def unignore_member(self, ctx, *, member:discord.Member):
		"""unignore a member of this server."""
		try:
			member = await commands.MemberConverter().convert(ctx, member)
		except commands.errors.BadArgument:
			await util.send_error(ctx, f"Cannot find member {member}")
		if member in self.bot.cache.blacklist[str(ctx.guild.id)]["member"]:
			await self.bot.db.execute(
				"DELETE FROM blacklisted_member WHERE guild_id = %s AND user_id = %s",
				ctx.guild.id,
				member.id,
			)
			self.bot.cache.blacklist[str(ctx.guild.id)]["member"].discard(member.id)
			await util.send_good(ctx, f"unignored {member.mention}")
		else:
			if member == ctx.author:
				return await util.send_error(ctx, f"cannot ignore yourself")
			await self.bot.db.execute(
				"""
				INSERT INTO blacklisted_member (user_id, guild_id)
					VALUES (%s, %s)
				ON DUPLICATE KEY UPDATE
					user_id = VALUES(user_id)
				""",
				member.id,
				ctx.guild.id,
			)
			try:
				self.bot.cache.blacklist[str(ctx.guild.id)]["member"].add(member.id)
			except KeyError:
				self.bot.cache.blacklist[str(ctx.guild.id)] = {
					"member": {member.id},
					"command": set(),
				}
			await util.send_good(ctx, f"ignoring {member.mention}")


	@unignore.command(name="command", description='unignore a command',brief='command',extras={'perms':'Manage Guild'},usage='```Swift\nSyntax: !unignore command <commands>\nExample: !unignore command snipe```')
	@commands.has_permissions(manage_guild=True)
	async def unignore_command(self, ctx, *, command):
		"""unignore a command."""
		cmd = self.bot.get_command(command)
		if cmd is None:
			raise exceptions.Warning(f"Command `{ctx.prefix}{command}` not found.")

		await self.bot.db.execute(
			"DELETE FROM blacklisted_command WHERE guild_id = %s AND command_name = %s",
			ctx.guild.id,
			cmd.qualified_name,
		)
		self.bot.cache.blacklist[str(ctx.guild.id)]["command"].discard(cmd.qualified_name.lower())
		await util.send_success(ctx, f"`{ctx.prefix}{cmd}` is no longer blacklisted.")

	@unignore.command(name="global")
	@commands.is_owner()
	async def unignore_global(self, ctx, *, user: discord.User):
		"""unignore someone globally."""
		await self.bot.db.execute("DELETE FROM blacklisted_user WHERE user_id = %s", user.id)
		self.bot.cache.blacklist["global"]["user"].discard(user.id)
		await util.send_success(ctx, f"**{user}** can now use Rival again!")

	@unignore.command(name="guild")
	@commands.is_owner()
	async def unignore_guild(self, ctx, guild_id: int):
		"""unignore a guild."""
		await self.bot.db.execute("DELETE FROM blacklisted_guild WHERE guild_id = %s", guild_id)
		self.bot.cache.blacklist["global"]["guild"].discard(guild_id)
		await util.send_success(ctx, f"Guild with id `{guild_id}` can use Rival again")


	# @commands.group(name="joindm", description="join dm setup")
	# @commands.guild_only()
	# @commands.has_permissions(manage_channels=True)
	# async def joindm(self, ctx):
	# 	if ctx.invoked_subcommand is None:
	# 		await util.command_group_help(ctx)

	# @joindm.command(name="toggle", aliases=["enabled"], description="toggle the joindm", brief="state:bool", extras={'perms':'manage_channels'}, usage="```Swift\nSyntax: !joindm toggle <bool>\nExample: !joindm toggle on```")
	# async def joindm_toggle(self, ctx, value: bool):
	# 	await queries.update_setting(ctx, "greeter_settings", "is_enabled", value)
	# 	if value:
	# 		await util.send_success(ctx, "joindm is now **enabled**")
	# 	else:
	# 		await util.send_success(ctx, "joindm is now **disabled**")

	# @joindm.command(name="message", aliases=['msg'], description="set the current joindm message", extras={'perms':'manage_channels'}, brief="message", usage="```Swift\nSyntax: !joindm message <message/embed json>\nExample: !joindm message welcome to our server```")
	# async def joindm_message(self, ctx, *, message):
	# 	if message.lower() == "default":
	# 		message = None

	# 	await queries.update_setting(ctx, "greeter_settings", "message_format", message)

	# 	preview = util.create_welcome_embed(ctx.author, ctx.guild, message)
	# 	await ctx.send(embed=discord.Embed(title='new joindm set', color=0x303135, description=f"{message}"))

	# @joindm.command(name='variables', aliases=['var', 'variable'], description="show joindm variables", extras={'perms':'manage_channels'})
	# async def joindm_variables(self, ctx):
	# 	await ctx.send(embed=discord.Embed(title="Enemy JoinDM Variables:", color=0x303135, description="{mention}, {user}, {id}, {server}, {username}, {mc}"))

	# @joindm.command(name='test', description="test the current joindm configuration", extras={'perms':'manage_channels'})
	# async def joindm_test(self, ctx):
	# 	member=ctx.author
	# 	greeter = await self.bot.db.execute(
	# 		"SELECT is_enabled, message_format FROM greeter_settings WHERE guild_id = %s",
	# 		ctx.guild.id,
	# 		one_row=True,
	# 	)
	# 	if greeter:
	# 		is_enabled, message_format = greeter
	# 		if is_enabled:
	# 			if message_format is not None:
	# 				try:
	# 					view = discord.ui.View()
	# 					view.add_item(discord.ui.Button(custom_id='yer', style=discord.ButtonStyle.grey, disabled=True, label=f"Sent from: {member.guild.name}"))
	# 					await member.send(content=util.create_welcome_embed(member, member.guild, message_format), view=view)
	# 				except discord.errors.Forbidden:
	# 					pass
	# 	else:
	# 		await ctx.reply(embed=discord.Embed(description=f"No joindm present"))

	# @joindm.command(name='settings', aliases=['config', 'cfg'], description="show current join dm config", extras={'perms':'manage_channels'})
	# async def joindm_settings(self, ctx):
	# 	member=ctx.author
	# 	greeter = await self.bot.db.execute(
	# 		"SELECT is_enabled, message_format FROM greeter_settings WHERE guild_id = %s",
	# 		member.guild.id,
	# 		one_row=True,
	# 	)
	# 	true = "<:enabled:926194469840236605>"
	# 	false = "<:disabled:926194368631697489>"
	# 	if greeter:
	# 		is_enabled, message_format = greeter
	# 		if is_enabled:
	# 			stat=true
	# 		else:
	# 			stat=false
	# 		if message_format:
	# 			message_format=message_format
	# 		else:
	# 			message_format=false
	# 		desc=f"""**Status:** {stat}\n**Message:** {message_format}"""
	# 		await ctx.reply(embed=discord.Embed(title=f"{ctx.guild.name}'s joindm setting", description=desc).set_thumbnail(url=ctx.guild.icon))

async def find_timezone(location):
  geolocator = Nominatim(user_agent="geoapiExercises")
  lad = location
  location = geolocator.geocode(lad)
  obj = TimezoneFinder()
  result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
  return result


async def setup(bot):
	await bot.add_cog(Utility(bot))


def profile_ticker(ticker):
	subs = {"GOOG": "GOOGL"}
	return subs.get(ticker) or ticker


async def detect_language(session, string):
	url = "https://translation.googleapis.com/language/translate/v2/detect"
	params = {"key": GOOGLE_API_KEY, "q": string[:1000]}

	async with session.get(url, params=params) as response:
		data = await response.json()
		language = data["data"]["detections"][0][0]["language"]

	return language


async def get_timezone(session, coord, clocktype="12hour"):
	url = "http://api.timezonedb.com/v2.1/get-time-zone"
	params = {
		"key": TIMEZONE_API_KEY,
		"format": "json",
		"by": "position",
		"lat": str(coord["lat"]),
		"lng": str(coord["lon"]),
	}
	async with session.get(url, params=params) as response:
		if response.status != 200:
			return f"HTTP ERROR {response.status}"

		timestring = (await response.json()).get("formatted").split(" ")
		try:
			hours, minutes = [int(x) for x in timestring[1].split(":")[:2]]
		except IndexError:
			return "N/A"

		if clocktype == "12hour":
			if hours > 12:
				suffix = "PM"
				hours -= 12
			else:
				suffix = "AM"
				if hours == 0:
					hours = 12
			return f"{hours}:{minutes:02d} {suffix}"
		return f"{hours}:{minutes:02d}"


async def gfycat_oauth(session):
	url = "https://api.gfycat.com/v1/oauth/token"
	params = {
		"grant_type": "client_credentials",
		"client_id": GFYCAT_CLIENT_ID,
		"client_secret": GFYCAT_SECRET,
	}

	async with session.post(url, json=params) as response:
		data = await response.json(loads=orjson.loads)
		access_token = data["access_token"]

	auth_headers = {"Authorization": f"Bearer {access_token}"}

	return auth_headers




def to_f(c):
	return c * (9.0 / 5.0) + 32
