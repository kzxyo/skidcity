import copy
import math
import os
import time

import aiohttp
import arrow
from typing import Union
import asyncio
import requests
import humanize
import discord,json,psutil,itertools,asyncio,arrow,datetime,humanfriendly,aiohttp
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta
from itertools import takewhile
from operator import attrgetter, itemgetter
from typing import Dict, Iterable, List, Set
from discord import Colour, Member, Message, NotFound, Object, TextChannel
#from datetime import datetime
from discord.ext.commands.cooldowns import BucketType, CooldownMapping
from discord.ext import commands, tasks
from numpy import nan

from libraries import emoji_literals, plotter
from modules import exceptions, util, consts, queries, help
from modules.asynciterations import aiter

def config(filename: str = "config"):
	""" Fetch default config file """
	try:
		with open(f"{filename}.json", encoding='utf8') as data:
			return json.load(data)
	except FileNotFoundError:
		raise FileNotFoundError("JSON file wasn't found")

owners = config()["owners"]
donors = config()["donors"]
kill = config()["kill"]
admins = config()["admins"]
dev = config()["dev"]
token=os.environ["TOKEN"]
headers = {"Authorization": f"Bot {token}"}


class Information(commands.Cog):
	"""See bot related information"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "ℹ️"
		self.color=0x303135
		self.owners = config()["owners"]
		self.config = config()
		self.donors = config()["donors"]
		self.kill = config()["kill"]
		self.admins = config()["admins"]
		self.icons = config()["ICONS"]
		self.dev = config()["dev"]
		self.bad=0xff6465
		self.options={}
		self.map: CooldownMapping = commands.CooldownMapping.from_cooldown(5, 2, commands.BucketType.member)
		self.spam_cd_mapping = commands.CooldownMapping.from_cooldown(4, 7, commands.BucketType.member)
		self.clear_counter.start()
		self.spam_count = {}
		self.spam_cache = {}
		self.punish={}

	def convert_to_bool(self, int: int) -> bool:
		return (False if int == 0 else True)


	@tasks.loop(minutes=5)
	async def clear_counter(self):
		self.spam_count.clear()


	@commands.Cog.listener()
	async def on_message(self, message):
		if not self.bot.is_ready():
			return
		if message.guild is None or not message.guild or message.guild == None:
			return
		if not message.guild.me.guild_permissions.administrator:
			return
		if message.author == self.bot.user:
			return
		def check(m):
			return (m.author == message.author and len(m.content) and (discord.utils.utcnow() - m.created_at).seconds < 4)
		#mentionspam=await self.bot.db.execute("SELECT max FROM antimention WHERE guild_id = %s", message.guild.id, one_value=True)
		#data=await self.bot.db.execute("SELECT * FROM antispam WHERE guild_id = %s", message.guild.id, one_value=True)
		if message.guild.id in self.bot.cache.antispam:
			data=True
		else:
			data=False
		if message.guild.id in self.bot.cache.antimention:
			mentionspam=self.bot.cache.antimention.get(message.guild.id)
		else:
			mentionspam=False
		try:
			if message.author.guild_permissions.administrator:
				return
			#role=await self.bot.db.execute("""SELECT role_id FROM spambyp WHERE guild_id = %s""", message.guild.id, one_value=True)
			if message.guild.id in self.bot.cache.role_bypass:
				async for r in aiter(self.bot.cache.role_bypass[message.guild.id]):
					d=message.guild.get_role(int(r))
					if d in message.author.roles:
						return
		except:
			pass
		if data:
			# if len(list(filter(lambda message: check(message), self.bot.cached_messages))) >= 6:
			# 	try:
			# 		if message.author.guild_permissions.manage_messages:
			# 			return
			# 	except:
			# 		return
			# 	try:
			# 		role=await self.bot.db.execute("""SELECT role_id FROM spambyp WHERE guild_id = %s""", message.guild.id, one_value=True)
			# 		if role:
			# 			r=message.guild.get_role(role)
			# 			if r in message.author.roles:
			# 				return
			# 			else:
			# 				pass
			# 	except:
			# 		pass
			# 	try:
			# 		if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", message.guild.id, message.author.id):
			# 			return
			# 	except:
			# 		pass
			# 	time="10seconds"
			# 	timeConvert = humanfriendly.parse_timespan(time)
			# 	await message.author.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason=f"{self.bot.user.name} auto mod | anti spam")
			# 	await message.channel.send(delete_after=10, embed=discord.Embed(
			# 		title="Rival Auto-Mod",
			# 		color=self.bad,
			# 		description=f"{message.author.mention} **has been timed out for repeated spamming**"
			# 	))
			# 	await message.channel.purge(limit=6, check=check, bulk=True)
			# 	await asyncio.sleep(1)
			# 	try:
			# 		await message.author.send(embed=discord.Embed(title="Rival Auto-Mod", color=self.bad, description="You have been timed out for **10 seconds** for spamming"))
			# 	except:
			# 		pass
			bucket = self.spam_cd_mapping.get_bucket(message)
			retry = bucket.update_rate_limit()
			if retry:
				try:
					if message.author.guild_permissions.manage_messages:
						return
				except:
					return
				try:
					#role=await self.bot.db.execute("""SELECT role_id FROM spambyp WHERE guild_id = %s""", message.guild.id, one_value=True)
					if message.guild.id in self.bot.cache.role_bypass:
						async for dddddd in aiter(self.bot.cache.role_bypass[message.guild.id]):
							r=message.guild.get_role(dddddd)
							if r in message.author.roles:
								return
					if str(message.guild.id) in self.bot.cache.whitelist:
						if message.author.id in self.bot.cache.whitelist[str(message.guild.id)]:
							return
				except:
					pass
				try:	
					if message.author.id not in self.punish:
					    self.punish[message.author.id]=[]
				except Exception as e:
					print(e)
				try:
					try:
						self.punish[message.author.id]+=1
					except:
						self.punish[message.author.id]=1
				except Exception as e:
					print(e)
				try:
					if self.punish[message.author.id] > 5:
						time='5minutes'
						self.punish[message.author.id].clear()
					else:
						time="10seconds"
				except:
					time='10seconds'
				try:
					timeConvert = humanfriendly.parse_timespan(time)
					if not message.author.guild_permissions.manage_messages:
						await message.author.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason=f"{self.bot.user.name} auto mod | anti spam")
						await message.channel.send(delete_after=10, embed=discord.Embed(
							title="Rival Auto-Mod",
							color=self.bad,
							description=f"{message.author.mention} **has been timed out for repeated spamming**"
						))
					#await message.channel.purge(limit=6, check=check, bulk=True)
					await asyncio.sleep(1)
					try:
						await message.author.send(embed=discord.Embed(title="Rival Auto-Mod", color=self.bad, description=f"You have been timed out for **{time}** for spamming"))
					except:
						pass
				except:
					return self.bot.cache.antispam.remove(message.guild.id)

		if message.guild.id in self.bot.cache.antimention:
			try:
				if not message.author.guild_permissions.manage_messages:
					await self.mention_filter(message, mentionspam)
			except:
				pass
		if "discord.gg" in message.content.lower():
			if await self.bot.db.execute("""SELECT * FROM antiinvite WHERE guild_id = %s""", message.guild.id, one_value=True):
				time="5minutes"
				timeConvert = humanfriendly.parse_timespan(time)
				if not message.author.guild_permissions.manage_messages:
					await message.author.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason=f"{self.bot.user.name} auto mod | anti invite")
					await message.channel.send(delete_after=10, embed=discord.Embed(
						title="Rival Auto-Mod",
						color=self.bad,
						description=f"{message.author.mention} **has been timed out for sending invites**"
					))
					try:
						return await message.delete()
					except:
						pass
	

	async def mention_filter(self, message: discord.Message, max_mentions: int):
		if len(message.raw_mentions) >= max_mentions:
			time="5minutes"
			timeConvert = humanfriendly.parse_timespan(time)
			await message.author.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason=f"{self.bot.user.name} auto mod | anti mass mention")
			await message.channel.send(embed=discord.Embed(
				title="Rival Auto-Mod",
				color=self.bad,
				description=f"{message.author.mention} has been Timed Out for Mass Mention."
			), delete_after=10)
			return await message.delete()



	async def sspam_filter(self, message: discord.Message):
		def check(payload):
			return payload.author.id == message.author.id

		if message.author.guild_permissions.administrator:
			return

		bucket = self.map.get_bucket(message)
		now = message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()
		bucket_full = bucket.update_rate_limit(now)
		if bucket_full:
			try:
				self.spam_count[message.author.id] += 1
			except KeyError:
				self.spam_count[message.author.id] = 0
				self.spam_count[message.author.id] += 1
			if self.spam_count[message.author.id] >= 3:
				del self.spam_count[message.author.id]
				#print(message.author)
				time="5minutes"
				timeConvert = humanfriendly.parse_timespan(time)
				await message.author.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason=f"{self.bot.user.name} auto mod | anti spam")
				return await message.channel.send(delete_after=10, embed=discord.Embed(
					title="Rival Auto-Mod",
					color=Color.red(),
					description=f"{message.author.mention} has been Timed Out for repeated spamming."
				))
			else:
				await message.channel.purge(limit=5, check=check, bulk=True)
				embed = discord.Embed(title="Rival Auto-Mod", color=Color.red(), description="Slow your roll buddy")
				return await message.channel.send(content="||%s||" % (message.author.mention), embed=embed, delete_after=10)

	@commands.command()
	async def emojistats(self, ctx: commands.Context, user: discord.Member = None, *args):
		"""See most used emojis on the server, optionally filtered by user"""
		global_user = False
		if "global" in [x.lower() for x in args] and user is not None:
			global_user = True
			custom_emojis = await self.bot.db.execute(
				"""
				SELECT sum(uses), emoji_id, emoji_name
					FROM custom_emoji_usage
					WHERE user_id = %s
				GROUP BY emoji_id
				""",
				user.id,
			)
			default_emojis = await self.bot.db.execute(
				"""
				SELECT sum(uses), emoji_name
					FROM unicode_emoji_usage
					WHERE user_id = %s
				GROUP BY emoji_name
				""",
				user.id,
			)
		else:
			opt = [] if user is None else [user.id]
			custom_emojis = await self.bot.db.execute(
				f"""
				SELECT sum(uses), emoji_id, emoji_name
					FROM custom_emoji_usage
					WHERE guild_id = %s
					{'AND user_id = %s' if user is not None else ''}
				GROUP BY emoji_id
				""",
				ctx.guild.id,
				*opt,
			)
			default_emojis = await self.bot.db.execute(
				f"""
				SELECT sum(uses), emoji_name
					FROM unicode_emoji_usage
					WHERE guild_id = %s
					{'AND user_id = %s' if user is not None else ''}
				GROUP BY emoji_name
				""",
				ctx.guild.id,
				*opt,
			)

		if not custom_emojis and not default_emojis:
			return await ctx.send("No emojis have been used yet!")

		all_emojis = []
		for uses, emoji_name in default_emojis:
			emoji_repr = emoji_literals.NAME_TO_UNICODE.get(emoji_name)
			all_emojis.append((uses, emoji_repr))

		for uses, emoji_id, emoji_name in custom_emojis:
			emoji = self.bot.get_emoji(int(emoji_id))
			if emoji is not None and emoji.is_usable():
				emoji_repr = str(emoji)
			else:
				emoji_repr = "`" + emoji_name + "`"
			all_emojis.append((uses, emoji_repr))

		rows = []
		for i, (uses, emoji_name) in enumerate(
			sorted(all_emojis, key=lambda x: x[0], reverse=True), start=1
		):
			rows.append(f"`#{i:2}` {emoji_name} — **{uses}** Use" + ("s" if uses > 1 else ""))

		content = discord.Embed(
			title="Most used emojis"
			+ (f" by {user.name}" if user is not None else "")
			+ (" globally" if global_user else f" in {ctx.guild.name}"),
			color=int("ffcc4d", 16),
		)
		await util.send_as_pages(ctx, content, rows, maxrows=15)

	@commands.group()
	async def commandstats(self, ctx):
		"""
		See statistics of command usage.
		Use commandstats <command name> for stats of a specific command.
		"""
		if ctx.invoked_subcommand is None:
			args = ctx.message.content.split()[1:]
			if not args:
				await util.send_command_help(ctx)
			else:
				await self.commandstats_single(ctx, " ".join(args))

	@commandstats.command(name="server", aliases=['guild'])
	async def commandstats_server(self, ctx, user: discord.Member = None):
		"""Most used commands in this server."""
		content = discord.Embed(
			title=f":bar_chart: Most used commands in {ctx.guild.name}"
			+ ("" if user is None else f" by {user}")
		)
		opt = []
		if user is not None:
			opt = [user.id]

		data = await self.bot.db.execute(
			f"""
			SELECT command_name, SUM(use_sum) as total FROM (
				SELECT command_name, SUM(uses) as use_sum, user_id FROM command_usage
					WHERE command_type = 'internal'
					  AND guild_id = %s
					{'AND user_id = %s' if user is not None else ''}
				GROUP BY command_name, user_id
			) as subq
			GROUP BY command_name
			ORDER BY total DESC
			""",
			ctx.guild.id,
			*opt,
		)
		rows = []
		total = 0
		for i, (command_name, count) in enumerate(data, start=1):
			total += count
			rows.append(
				f"`#{i:2}` **{count}** use{'' if count == 1 else 's'} : `{ctx.prefix}{command_name}`"
			)

		if rows:
			content.set_footer(text=f"Total {total} commands")
			await util.send_as_pages(ctx, content, rows)
		else:
			content.description = "No data :("
			await ctx.send(embed=content)

	@commandstats.command(name="global", aliases=['all'])
	async def commandstats_global(self, ctx, user: discord.Member = None):
		"""Most used commands globally."""
		content = discord.Embed(
			title=":bar_chart: Most used commands" + ("" if user is None else f" by {user}")
		)
		opt = []
		if user is not None:
			opt = [user.id]

		data = await self.bot.db.execute(
			f"""
			SELECT command_name, SUM(use_sum) as total FROM (
				SELECT command_name, SUM(uses) as use_sum, user_id FROM command_usage
					WHERE command_type = 'internal'
					{'AND user_id = %s' if user is not None else ''}
				GROUP BY command_name, user_id
			) as subq
			GROUP BY command_name
			ORDER BY total DESC
			""",
			*opt,
		)
		rows = []
		total = 0
		for i, (command_name, count) in enumerate(data, start=1):
			total += count
			rows.append(
				f"`#{i:2}` **{count}** use{'' if count == 1 else 's'} : `{ctx.prefix}{command_name}`"
			)

		if rows:
			content.set_footer(text=f"Total {total} commands")
			await util.send_as_pages(ctx, content, rows)
		else:
			content.description = "No data :("
			await ctx.send(embed=content)

	async def commandstats_single(self, ctx, command_name):
		"""Stats of a single command."""
		command = self.bot.get_command(command_name)
		if command is None:
			raise exceptions.Info(f"Command `{ctx.prefix}{command_name}` does not exist!")

		content = discord.Embed(title=f":bar_chart: `{ctx.prefix}{command.qualified_name}`")

		# set command name to be tuple of subcommands if this is a command group
		group = hasattr(command, "commands")
		if group:
			command_name = tuple(
				[f"{command.name} {x.name}" for x in command.commands] + [command_name]
			)
		else:
			command_name = command.qualified_name

		total_uses, most_used_by_user_id, most_used_by_user_amount = await self.bot.db.execute(
			f"""
			SELECT SUM(use_sum) as total, user_id, MAX(use_sum) FROM (
				SELECT SUM(uses) as use_sum, user_id FROM command_usage
					WHERE command_type = 'internal'
					  AND command_name {'IN %s' if group else '= %s'}
				GROUP BY user_id
			) as subq
			""",
			command_name,
			one_row=True,
		)

		most_used_by_guild_id, most_used_by_guild_amount = await self.bot.db.execute(
			f"""
			SELECT guild_id, MAX(use_sum) FROM (
				SELECT guild_id, SUM(uses) as use_sum FROM command_usage
					WHERE command_type = 'internal'
					  AND command_name {'IN %s' if group else '= %s'}
				GROUP BY guild_id
			) as subq
			""",
			command_name,
			one_row=True,
		)

		uses_in_this_server = (
			await self.bot.db.execute(
				f"""
				SELECT SUM(uses) FROM command_usage
					WHERE command_type = 'internal'
					  AND command_name {'IN %s' if group else '= %s'}
					  AND guild_id = %s
				GROUP BY guild_id
				""",
				command_name,
				ctx.guild.id,
				one_value=True,
			)
			or 0
		)

		# show the data in embed fields
		content.add_field(name="Uses", value=total_uses or 0)
		content.add_field(name="on this server", value=uses_in_this_server)
		content.add_field(
			name="Server most used in",
			value=f"{self.bot.get_guild(most_used_by_guild_id)} ({most_used_by_guild_amount or 0})",
			inline=False,
		)
		content.add_field(
			name="Most total uses by",
			value=f"{self.bot.get_user(most_used_by_user_id)} ({most_used_by_user_amount or 0})",
		)

		# additional data for command groups
		if group:
			content.description = "Command Group"
			subcommands_tuple = tuple([f"{command.name} {x.name}" for x in command.commands])
			subcommand_usage = await self.bot.db.execute(
				"""
				SELECT command_name, SUM(uses) FROM command_usage
					WHERE command_type = 'internal'
					  AND command_name IN %s
				GROUP BY command_name ORDER BY SUM(uses) DESC
				""",
				subcommands_tuple,
			)
			content.add_field(
				name="Subcommand usage",
				value="\n".join(f"{s[0]} - **{s[1]}**" for s in subcommand_usage),
				inline=False,
			)

		await ctx.send(embed=content)

	@commands.command()
	async def statsgraph(self, ctx, stat, hours: int = 24):
		"""Show various stat graphs."""
		stat = stat.lower()
		available = [
			"messages",
			"reactions",
			"commands_used",
			"guild_count",
			"member_count",
			"notifications_sent",
			"lastfm_api_requests",
			"html_rendered",
		]
		if stat not in available:
			raise exceptions.Warning(f"Available stats: {', '.join(available)}")

		data = await self.bot.db.execute(
			f"""
			SELECT UNIX_TIMESTAMP(ts), DAY(ts), HOUR(ts), MINUTE(ts), {stat}
				FROM stats
				WHERE ts >= NOW() + INTERVAL -{hours} HOUR
				AND ts <  NOW() + INTERVAL 0 DAY
			ORDER BY ts
			"""
		)
		datadict = {}
		for row in data:
			datadict[str(row[0])] = row[-1]

		patched_data = []
		frame = []
		now = arrow.utcnow()
		first_data_ts = arrow.get(data[0][0])
		start = max(now.shift(hours=-hours), first_data_ts)
		for dt in arrow.Arrow.span_range("minute", start, now.shift(minutes=-1)):
			dt = dt[0]
			value = datadict.get(str(dt.timestamp), nan)
			frame.append(dt.datetime)
			patched_data.append(value)

		plotter.time_series_graph(frame, patched_data, str(discord.Color.random()))
		with open("downloads/graph.png", "rb") as img:
			await ctx.send(
				file=discord.File(img),
			)



async def setup(bot):
	await bot.add_cog(Information(bot))
