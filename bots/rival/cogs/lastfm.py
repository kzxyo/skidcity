import asyncio,html,io,math,os,random,re,orjson,urllib.parse,contextlib,tabulate
from io import BytesIO
from libraries import emoji_literals
import aiohttp,arrow,colorgram,discord,time,kdtree
from bs4 import BeautifulSoup
from discord.ext import commands
from PIL import Image
import humanize
from collections import deque
from typing import Union
import json
import requests
from discord.asset import Asset
from modules.lastfm_modules import AsyncIter
from discord.ext.commands import Context
from discord.guild import Guild
from discord.ext.commands.converter import MessageConverter
from cogs.embed import embed
from modules.scrapers import ScrapingMixin

from modules import emojis, exceptions, util, consts, queries, default, Message, DL, DisplayName, permissions

def check_num(n):
	remain=n/10
	if remain >= 1 and float(remain%10).is_integer():
		return True
	else:
		return False
lfm={}

GOOGLE_API_KEY=os.environ.get("GOOGLE_KEY")
AUDDIO_TOKEN=os.environ.get("AUDDIO_TOKEN")
token=os.environ.get("TOKEN")
headers = {"Authorization": f"Bot {token}"}

def config(filename: str = "config"):
	""" Fetch default config file """
	try:
		with open(f"{filename}.json", encoding='utf8') as data:
			return json.load(data)
	except FileNotFoundError:
		raise FileNotFoundError("JSON file wasn't found")


def _from_guild_avatar(state, guild_id: int, member_id: int, avatar: str) -> Asset:
	animated = avatar.startswith('a_')
	format = 'gif' if animated else 'png'
	return Asset(
		state,
		url=f"/guilds/{guild_id}/users/{member_id}/avatars/{avatar}.{format}?size=1024"
	)

def _from_guild_banner(state, guild_id: int, member_id: int, banner: str) -> Asset:
	animated = banner.startswith('a_')
	format = 'gif' if animated else 'png'
	return Asset(
		state,
		url=f"/guilds/{guild_id}/users/{member_id}/banners/{banner}.{format}?size=300"
	)




owners = config()["owners"]
donors = config()["donors"]
kill = config()["kill"]
admins = config()["admins"]
dev = config()["dev"]

mob="<:mobile:918446884459274240>"
dsk="<:dsk1:1005926902319558696>"
webb="<a:globe:1005927025497866300>"

def generate_user_statuses(member: discord.Member):
	if member.status == discord.Status.offline:
		return consts.statuses.OFFLINE
	mobile = {
		discord.Status.online: mob,
		discord.Status.idle: mob,
		discord.Status.dnd: mob,
		discord.Status.offline: ""
	}[member.mobile_status]
	desktop = {
		discord.Status.online: dsk,
		discord.Status.idle: dsk,
		discord.Status.dnd: dsk,
		discord.Status.offline: ""
	}[member.desktop_status]
	web = {
		discord.Status.online: webb,
		discord.Status.idle: webb,
		discord.Status.dnd: webb,
		discord.Status.offline: ""
	}[member.web_status]
	return f"\u200b{desktop}\u200b{mobile}\u200b{web}"
	
help1=(
	"  @ Commands:\n"
	"`!whoknows` ・ [artistname]\n"
	"`!whoknowsalbum` ・ <album> | <artist>\n"
	"`!whoknowstrack` ・ [track]\n"
	"`!np`\n"
	"`!crowns` ・ [user]\n\n"
	"  @ Grouped Commands:\n"
	"`!fm / !lf` ・ [subcommand]\n"
	" └ `set`, `unset`, `topalbums`, `server`,`topartists`, `topalbums`, `toptracks`, `recent`, `last`, `album`, `artist`, `cover`, `chart`, `colorchart`, `milestone`, `customcommand/cc`, `reactions`\n`lf/fm server`\n└ `np`, `recent/re`, `topartists/ta`, `topalbums/tab`, `toptracks/tt` "
	)

voting_help=(
	"!lf voting enabled on\n!lf voting up/down <emote>"
	)

#LASTFM_APPID = "40cd92261cc8b0dc0f3674c631fb33c5"
LASTFM_APPID="1968900fb0070b611741d0920a59f303"
LASTFM_TOKEN="a6e238510d35e97c58c4a9c19d5b7aad"
#LASTFM_TOKEN = "10bdfb6d20edeef25ee924122e0aed89"

MISSING_IMAGE_HASH = "2a96cbd8b46e442fc41c2b86b821562f"


def is_small_server():
	async def predicate(ctx):
		users = await ctx.bot.db.execute(
			"""
			SELECT count(*) FROM user_settings WHERE user_id IN %s
			AND lastfm_username IS NOT NULL
			""",
			[user.id for user in ctx.guild.members],
			one_value=True,
		)
		if users > 150:
			raise exceptions.ServerTooBig(ctx.guild.member_count)
		return True

	return commands.check(predicate)


class AlbumColorNode:
	def __init__(self, rgb, image_url):
		self.rgb = rgb
		self.data = image_url

	def __len__(self):
		return len(self.rgb)

	def __getitem__(self, i):
		return self.rgb[i]

	def __str__(self):
		return f"rgb{self.rgb}"

	def __repr__(self):
		return f"AlbumColorNode({self.rgb}, {self.data})"


class LastFm(commands.Cog):
	"""LastFM commands"""

	def __init__(self, bot) -> None:
		self.bot = bot
		self.icon = "🎵"
		self.color=self.bot.color
		self.owners = config()["owners"]
		self.config = config()
		self.donors = config()["donors"]
		self.kill = config()["kill"]
		self.admins = config()["admins"]
		self.icons = config()["ICONS"]
		self.dev = config()["dev"]
		self.add="<:plus:947812413267406848>"
		self.yes=self.bot.yes
		self.good=self.bot.color#0x0xD6BCD0
		self.rem="<:rem:947812531509026916>"
		self.no=self.bot.no
		self.bad=self.bot.color#0xff6465
		self.tasks = {}
		self.ch='<:yes:940723483204255794>'
		self.error=self.bot.color#0xfaa61a
		self.warn=self.bot.warn
		self.lastfm_red = "b90000"
		self.cover_base_urls = [
			"https://lastfm.freetls.fastly.net/i/u/34s/{0}",
			"https://lastfm.freetls.fastly.net/i/u/64s/{0}",
			"https://lastfm.freetls.fastly.net/i/u/174s/{0}",
			"https://lastfm.freetls.fastly.net/i/u/300x300/{0}",
			"https://lastfm.freetls.fastly.net/i/u/{0}",
		]
		with open("html/fm_chart.min.html", "r", encoding="utf-8") as file:
			self.chart_html = file.read().replace("\n", "")
		self.hs = {
			"aquarius": {
				"name": "Aquarius",
				"emoji": ":aquarius:",
				"date_range": "Jan 20 - Feb 18",
			},
			"pisces": {
				"name": "Pisces",
				"emoji": ":pisces:",
				"date_range": "Feb 19 - Mar 20",
			},
			"aries": {
				"name": "Aries",
				"emoji": ":aries:",
				"date_range": "Mar 21 - Apr 19",
			},
			"taurus": {
				"name": "Taurus",
				"emoji": ":taurus:",
				"date_range": "Apr 20 - May 20",
			},
			"gemini": {
				"name": "Gemini",
				"emoji": ":gemini:",
				"date_range": "May 21 - Jun 20",
			},
			"cancer": {
				"name": "Cancer",
				"emoji": ":cancer:",
				"date_range": "Jun 21 - Jul 22",
			},
			"leo": {
				"name": "Leo",
				"emoji": ":leo:",
				"date_range": "Jul 23 - Aug 22",
			},
			"virgo": {
				"name": "Virgo",
				"emoji": ":virgo:",
				"date_range": "Aug 23 - Sep 22",
			},
			"libra": {
				"name": "Libra",
				"emoji": ":libra:",
				"date_range": "Sep 23 - Oct 22",
			},
			"scorpio": {
				"name": "Scorpio",
				"emoji": ":scorpius:",
				"date_range": "Oct 23 - Nov 21",
			},
			"sagittarius": {
				"name": "Sagittarius",
				"emoji": ":sagittarius:",
				"date_range": "Nov 22 - Dec 21",
			},
			"capricorn": {
				"name": "Capricorn",
				"emoji": ":capricorn:",
				"date_range": "Dec 22 - Jan 19",
			},
		}

	async def badges(self, user):
		d={}
		s=[]
		d['status']="Success"
		try:
			## happy path where name is set
			## Process our new user
			async with aiohttp.ClientSession() as qqq:
				async with qqq.get(f"https://japi.rest/discord/v1/user/{user}") as r:
					p=await r.json()
			try:
				p.pop("cached")
				p.pop("cache_expiry")
			except:
				pass
			try:
				d['source']='https://rival.rocks'
				try:
					guilds=[]
					bb=''.join(b for b in p['public_flags_array'])
					if "boost" not in bb.lower():
						u=await self.bot.fetch_user(user)
						for g in u.mutual_guilds:
							vanity=str(await d.vanity_invite())
							if vanity:
								v=vanity
							else:
								v="None"
							guilds.append({'name':d.name,'owner_id':d.owner.id,'owner_tag':str(d.owner),'member_count':len(d.members),'vanity':v,'permissions':str(g.get_member(u).permissions)})
							if u in g.premium_subscribers:
								p=g.get_member(u)
								s.append(p.premium_since)
					else:
						u=await self.bot.fetch_user(user)
						for g in u.mutual_guilds:
							d=self.bot.get_guild(g.id)
							if d:
								vanity=str(await g.vanity_invite())
								if vanity:
									v=vanity
								else:
									v="None"
								guilds.append({'name':d.name,'owner_id':d.owner.id,'owner_tag':str(d.owner),'member_count':len(d.members),'vanity':v,'permissions':str(g.get_member(u).permissions)})
						if s:
							s.sort()
							if s[0] < await util.datetime_delta(1):
								p['public_flags_array'].append('Booster_1')
							elif s[0] < await util.datetime_timedelta(2):
								p['public_flags_array'].appemd('Booster_2')
							elif s[0] < await util.datetime_delta(3):
								p['public_flags_array'].append('Booster_3')
							elif s[0] < await util.datetime_delta(6):
								p['public_flags_array'].append('Booster_6')
							elif s[0] < await util.datetime_delta(9):
								p['public_flags_array'].append('Booster_9')
							elif s[0] < await util.datetime_delta(12):
								p['public_flags_array'].append('Booster_12')
							elif s[0] < await util.datetime_delta(15):
								p['public_flags_array'].append('Booster_15')
							elif s[0] < await util.datetime_delta(18):
								p['public_flags_array'].append('Booster_18')
							elif s[0] < await util.datetime_delta(21):
								p['public_flags_array'].append('Booster_21')
							elif s[0] < await util.datetime_delta(24):
								p['public_flags_array'].append('Booster_24')
							else:
								p['public_flags_array'].append('Booster_1')
					if "nitro" not in bb.lower():
						if u.display_avatar.is_animated() or u.banner:
							p['public_flags_array'].append("NITRO")
				except Exception as e:
					print(f'error 1: {e}')
					pass
				for key,value in p.items():
					d[key]=value
				d['guilds']=guilds
				# data = await self.bot.db.execute("SELECT name, ts FROM namehistory WHERE user_id = %s ORDER BY ts DESC", user)
				# q=[]
				# if data:
				#     for name, ts in data:
				#         q.append({'name':name,'timestamp':f"{ts}"})
				# d['names']=q
			except Exception as e:
				print(f'error 2: {e}')
				d['message']="Unknown User"
				d['status']='Fail'


			response_obj = { 'status' : 'success' }
			## return a success json response with status code 200 i.e. 'OK'
			return d
		except Exception as e:
			print(e)
			## Bad path where name is not set
			response_obj = { 'status' : 'failed', 'reason': str(e) }
			## return failed with a status code of 500 i.e. 'Server Error'
			return d


	def _get_embed_from_json(self, ctx, embed_json):
		# Helper method to ensure embed_json is valid, and doesn't bypass limits
		# Let's attempt to serialize the json
		try:
			embed_dict = json.loads(embed_json)
			# Let's parse the author and color
			if embed_dict.get("color") and not isinstance(embed_dict["color"],list):
				# We got *something* for the color - let's first check if it's an int between 0 and 16777215
				if not isinstance(embed_dict["color"],int) or not 0<=embed_dict["color"]<=16777215:
					color_value = None
					if str(embed_dict["color"]).lower().startswith(("#","0x")):
						# Should be a hex color code
						try:
							color_value = int(str(embed_dict["color"]).lower().lstrip("#").lstrip("0x"),16)
							if not 0<=color_value<=16777215: color_value = None # Out of range
						except:
							pass
					# Let's try to resolve it to a user
					embed_dict["color"] = color_value if color_value is not None else DisplayName.memberForName(str(embed_dict["color"]),ctx.guild)
			if embed_dict.get("author") and not isinstance(embed_dict["author"],dict):
				# Again - got *something* for the author - try to resolve it
				embed_dict["author"] = DisplayName.memberForName(str(embed_dict["author"]),ctx.guild)
		except Exception as e:
			return e
		# Only allow owner to modify the limits
		if not commands.is_owner():
			embed_dict["title_max"] = 256
			embed_dict["desc_max"] = 2048
			embed_dict["field_max"] = 25
			embed_dict["fname_max"] = 256
			embed_dict["fval_max"] = 1024
			embed_dict["foot_max"] = 2048
			embed_dict["auth_max"] = 256
			embed_dict["total_max"] = 6000
		return embed_dict	

	async def chart_factory(self, chart_items, width, height, show_labels=True):
		if show_labels:
			img_div_template = '<div class="art"><img src="{0}"><p class="label">{1}</p></div>'
		else:
			img_div_template = '<div class="art"><img src="{0}"></div>'

		img_divs = "\n".join(img_div_template.format(*chart_item) for chart_item in chart_items)

		replacements = {
			"WIDTH": 300 * width,
			"HEIGHT": 300 * height,
			"CHART_ITEMS": img_divs,
		}

		payload = {
			"html": util.format_html(self.chart_html, replacements),
			"width": 300 * width,
			"height": 300 * height,
			"imageFormat": "jpeg",
		}

		return await util.render_html(self.bot, payload)

	async def server_lastfm_usernames(self, ctx, filter_cheaters=False):
		guild_user_ids = [user.id for user in ctx.guild.members]
		l={username: value for username, value in self.bot.cache.lastfm.items() if username in guild_user_ids}
		data=l.items()
		# data = await self.bot.db.execute(
		# 	"""
		# 	SELECT user_id, lastfm_username FROM user_settings WHERE user_id IN %s
		# 	AND lastfm_username IS NOT NULL
		# 	"""
		# 	+ (
		# 		" AND lastfm_username not in (SELECT lastfm_username FROM lastfm_cheater)"
		# 		if filter_cheaters
		# 		else ""
		# 	),
		# 	guild_user_ids,
		# )
		return data

	async def global_lastfm_usernames(self, ctx, filter_cheaters=False):
		guild_user_ids = [user.id for user in self.bot.users]
		l={username: value for username, value in self.bot.cache.lastfm.items() if username in guild_user_ids}
		data=l.items()
		# data = await self.bot.db.execute(
		# 	"""
		# 	SELECT user_id, lastfm_username FROM user_settings WHERE user_id IN %s
		# 	AND lastfm_username IS NOT NULL
		# 	"""
		# 	+ (
		# 		" AND lastfm_username not in (SELECT lastfm_username FROM lastfm_cheater)"
		# 		if filter_cheaters
		# 		else ""
		# 	),
		# 	guild_user_ids,
		# )
		return data

	@commands.group(aliases=["lf", "if", "lastfm", "lfm"], description="LastFM Command Group")
	async def fm(self, ctx):
		if ctx.subcommand_passed:
			cmd=self.bot.get_command(f'lf {ctx.subcommand_passed}')
			if cmd == None or not cmd or cmd is None:
				return await util.command_group_help(ctx)
			else:
				return
		elif ctx.invoked_subcommand is None:
			await ctx.invoke(self.bot.get_command("nowplaying"))
			# embed=discord.Embed(title=f"{emojis.LASTFM}", description=help1).set_footer(text="Prefix = !")
			# await ctx.send(embed=embed)
			#await util.command_group_help(ctx)

	@fm.command(name='set', description="Save your Last.fm username", usage="```Swift\nSyntax: !lf set <username>\nExample: !lf set cop0001```",brief='username')
	async def set(self, ctx, username=None):
		if not username:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention} *please provide a username in the command*", color=0x303135))
		if username==None:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention} *please provide a username in the command*", color=0x303135))

		content = await self.get_userinfo_embed(username)
		if content is None:
			raise exceptions.Warning(f"Last.fm profile `{username}` was not found")
		msg=await util.send_good(ctx, f"setting your lastfm username as `{username}`")
		if ctx.author.id not in self.bot.cache.lastfm:
			self.bot.cache.lastfm[int(ctx.author.id)]=username
		else:
			self.bot.cache.lastfm[int(ctx.author.id)]=username
		await asyncio.sleep(2)
		await msg.edit(embed=discord.Embed(color=self.color, description=f"<a:loading:940728015640481822> {ctx.author.mention}: Indexing your **plays**"))
		await asyncio.sleep(2)
		tasks=[]
		data = await self.api_request({"user": username,"method": "user.gettopartists","period": "overall","limit": 15})
		user_attr = data["topartists"]["@attr"]
		artists = data["topartists"]["artist"][: 15]
		for artist in artists:
			try:
				artistname = discord.utils.escape_markdown(artist)
			except:
				artistname = artist
			plays = artist["playcount"]
			try:
				old_king = await self.bot.db.execute("SELECT cached_playcount FROM artist_crown WHERE artist_name = %s AND guild_id = %s",artistname,ctx.guild.id,one_value=True)
				if int(plays) > int(old_king):
					await self.bot.db.execute(
						"""
						INSERT INTO artist_crown (guild_id, user_id, artist_name, cached_playcount)
							VALUES (%s, %s, %s, %s)
						ON DUPLICATE KEY UPDATE
							cached_playcount = VALUES(cached_playcount),
							user_id = VALUES(user_id)
						""",
						ctx.guild.id,
						ctx.author.id,
						artistname,
						plays,
					)
			except:
				pass
		await self.bot.db.execute(
			"""
			INSERT INTO user_settings (user_id, lastfm_username)
				VALUES (%s, %s)
			ON DUPLICATE KEY UPDATE
				lastfm_username = VALUES(lastfm_username)
			""",
			ctx.author.id,
			username,
		)
		await msg.edit(embed=discord.Embed(color=self.good, description=f"{self.bot.yes} {ctx.author.mention}: successfully **indexed** your `plays`"))
		#await util.send_success(ctx, f" {ctx.author.mention}: Last.FM username set to `{username}`")

	@fm.command(name='customcommand', aliases=['cc'], description="Set your custom NowPlaying Command", brief='command', usage="```Swift\nSyntax: !lf cc <command>\nExample: !lf cc cop```",extras={'perms':'donator'})
	@util.donor()
	async def customcommand(self, ctx, customcommand=None):
		if customcommand == None:
			return await ctx.send(embed=discord.Embed(color=0x303135, description="please include a custom command"))
		if not customcommand:
			return await ctx.send(embed=discord.Embed(color=0x303135, description="please include a custom command"))
		if customcommand == "clear":
			if ctx.author.id in self.bot.lastfm_cc:
				self.bot.lastfm_cc.pop(ctx.author.id)
			await self.bot.db.execute("DELETE FROM cf WHERE user_id = %s",ctx.message.author.id,)
			return await util.send_success(ctx, f"{ctx.author.mention}: deleted your lastfm custom command")
		if await self.bot.db.execute("SELECT cc FROM cf WHERE user_id = %s",ctx.message.author.id,one_value=True,):
			await self.bot.db.execute("DELETE FROM cf WHERE user_id = %s",ctx.message.author.id,)
			await self.bot.db.execute("INSERT INTO cf VALUES(%s, %s)",ctx.message.author.id,customcommand,)
			self.bot.cache.lastfm_cc[ctx.author.id]=customcommand
			return await util.send_success(ctx, f"{ctx.author.mention}: set your lastfm custom command as {customcommand}")
		else:
			await self.bot.db.execute(
				"INSERT INTO cf VALUES(%s, %s)",
				ctx.message.author.id,
				customcommand,
			)
			self.bot.cache.lastfm_cc[ctx.author.id]=customcommand
			await util.send_success(ctx, f"{ctx.author.mention}: set your lastfm custom command as {customcommand}")

	@fm.command(name='embed', description="Set your custom NowPlaying Command Embed", extras={'perms': 'donator'}, brief='mode, embedjson')
	@util.donor()
	async def embed(self, ctx, *, embed_json=None):
		if embed_json == None:
			return await ctx.reply(embed=discord.Embed(color=self.bot.color,description=f"For Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)"))
		if not embed_json:
			return await ctx.reply(embed=discord.Embed(color=self.bot.color,description=f"For Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)"))
		if embed_json.lower() == "help":
			return await ctx.reply(embed=discord.Embed(color=self.bot.color,description=f"For Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)"))
		if embed_json.lower() == "current":
			emb=await self.bot.db.execute("""SELECT message FROM last_fm_embed WHERE user_id = %s""", ctx.author.id, one_value=True)
			if emb:
				return await ctx.send(content=f"```{emb}```")
		if embed_json.lower() == "clear":
			if ctx.author.id in self.bot.cache.lastfm_embeds:
				self.bot.cache.lastfm_embeds.pop(ctx.author.id)
			await self.bot.db.execute("DELETE FROM last_fm_embed WHERE user_id = %s",ctx.author.id,)
			return await util.send_success(ctx, f"{ctx.author.mention}: deleted your lastfm custom embed")
		if await self.bot.db.execute("SELECT message FROM last_fm_embed WHERE user_id = %s",ctx.author.id,one_value=True,):
			await self.bot.db.execute("DELETE FROM last_fm_embed WHERE user_id = %s",ctx.author.id,)
			if "\\n" in embed_json:
				embed_json=embed_json.replace('\\\\','\\')
			await self.bot.db.execute("INSERT INTO last_fm_embed VALUES(%s, %s)",ctx.author.id,embed_json)
			self.bot.cache.lastfm_embeds[ctx.author.id]=embed_json
			embed_dict=self._get_embed_from_json(ctx, embed_json)
			try:
				await Message.Embed(**embed_dict).send(ctx.channel)
			except:
				pass
			return await util.send_success(ctx, f"{ctx.author.mention}: set your lastfm custom embed as {embed_json}")
		else:
			if "\\n" in embed_json:
				embed_json=embed_json.replace('\\\\','\\')
			await self.bot.db.execute(
				"INSERT INTO last_fm_embed VALUES(%s, %s)",
				ctx.author.id,
				embed_json,
			)
			await util.send_success(ctx, f"{ctx.author.mention}: set your lastfm custom embed as {embed_json}")
			self.bot.cache.lastfm_embeds[ctx.author.id]=embed_json
			embed_dict=self._get_embed_from_json(ctx, embed_json)
			try:
				await Message.Embed(**embed_dict).send(ctx.channel)
			except:
				pass

	@fm.command(name='mode', description="Set your custom NowPlaying Command Embed", extras={'perms': 'donator'}, brief='mode, embedjson')
	@util.donor()
	async def mode(self, ctx, mode:str, *, embed_json=None):
		dm=['default','None',None,'none','DEFAULT']

		if mode.lower() in dm:
			await self.bot.db.execute("""DELETE FROM last_fm_embed WHERE user_id = %s""", ctx.author.id)
			if ctx.author.id in self.bot.cache.lastfm_embeds:
				self.bot.cache.lastfm_embeds.pop(ctx.author.id)
				return await util.send_good(ctx, f"set your **lastfm mode** to **default**")
		if embed_json == None:
			return await ctx.reply(embed=discord.Embed(color=self.bot.color,description=f"For Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)"))
		if not embed_json:
			return await ctx.reply(embed=discord.Embed(color=self.bot.color,description=f"For Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)"))
		if embed_json.lower() == "help":
			return await ctx.reply(embed=discord.Embed(color=self.bot.color,description=f"For Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)"))
		if embed_json.lower() == "current":
			emb=await self.bot.db.execute("""SELECT message FROM last_fm_embed WHERE user_id = %s""", ctx.author.id, one_value=True)
			if emb:
				return await ctx.send(content=f"```{emb}```")
		if embed_json.lower() == "clear":
			if ctx.author.id in self.bot.cache.lastfm_embeds:
				self.bot.cache.lastfm_embeds.pop(ctx.author.id)
			await self.bot.db.execute("DELETE FROM last_fm_embed WHERE user_id = %s",ctx.author.id,)
			return await util.send_success(ctx, f"{ctx.author.mention}: deleted your lastfm custom embed")
		if await self.bot.db.execute("SELECT message FROM last_fm_embed WHERE user_id = %s",ctx.author.id,one_value=True,):
			await self.bot.db.execute("DELETE FROM last_fm_embed WHERE user_id = %s",ctx.author.id,)
			if "\\n" in embed_json:
				embed_json=embed_json.replace('\\\\','\\')
			await self.bot.db.execute("INSERT INTO last_fm_embed VALUES(%s, %s)",ctx.author.id,embed_json)
			self.bot.cache.lastfm_embeds[ctx.author.id]=embed_json
			embed_dict=self._get_embed_from_json(ctx, embed_json)
			try:
				await Message.Embed(**embed_dict).send(ctx.channel)
			except:
				pass
			return await util.send_success(ctx, f"{ctx.author.mention}: set your lastfm custom embed as {embed_json}")
		else:
			if "\\n" in embed_json:
				embed_json=embed_json.replace('\\\\','\\')
			await self.bot.db.execute(
				"INSERT INTO last_fm_embed VALUES(%s, %s)",
				ctx.author.id,
				embed_json,
			)
			await util.send_success(ctx, f"{ctx.author.mention}: set your lastfm custom embed as {embed_json}")
			self.bot.cache.lastfm_embeds[ctx.author.id]=embed_json
			embed_dict=self._get_embed_from_json(ctx, embed_json)
			try:
				await Message.Embed(**embed_dict).send(ctx.channel)
			except:
				pass

	@fm.command(name='unset', description="Unlink your Last.fm")
	async def unset(self, ctx):
		await self.bot.db.execute(
			"""
			INSERT INTO user_settings (user_id, lastfm_username)
				VALUES (%s, %s)
			ON DUPLICATE KEY UPDATE
				lastfm_username = VALUES(lastfm_username)
			""",
			ctx.author.id,
			None,
		)
		if ctx.author.id in self.bot.cache.lastfm:
			self.bot.cache.lastfm.pop(ctx.author.id)
		await util.send_good(ctx, f"cleared your last.fm")

	@fm.group(name='reaction', aliases=['react', 'reacts', 'reactions', 'emoji', 'emojis'], description='Set your LastFM NowPlaying Reactions', brief='emoji1, emoji2', usage="```Swift\nSyntax: !lf reaction <emoji> <emoji>\nExample: !lf reaction :rage: :happy:```",extras={'perms': 'donator'})
	@util.donor()
	async def reaction(self, ctx, emoji1=None, emoji2=None):
		if ctx.invoked_subcommand is None:
			if not emoji1:
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **please provide two emojis with the command**"))
			if emoji1.lower()=="clear" or emoji1.lower()=="reset":
				await self.bot.db.execute("""DELETE FROM lastfm_vote_setting WHERE user_id = %s""", ctx.author.id)
				return await util.send_success(ctx, f"{ctx.author.mention}: **cleared custom reactions**")
			if emoji1.lower() == 'none':
				await self.bot.db.execute(
				"""
				INSERT INTO lastfm_vote_setting (user_id, is_enabled)
					VALUES (%s, %s)
				ON DUPLICATE KEY UPDATE
					is_enabled = VALUES(is_enabled)
				""",
				ctx.author.id,
				0,
			)
				return await util.send_good(ctx, f"disabled your reactions")
			if not emoji2:
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **please provide two emojis with the command**"))
			await ctx.message.add_reaction(emoji1)
			await ctx.message.add_reaction(emoji2)
			if emoji1.startswith("<"):
				emoji1=str(emoji1)
			else:
				emoji1=emoji_literals.UNICODE_TO_NAME.get(emoji1)
			if emoji2.startswith("<"):
				emoji2=str(emoji2)
			else:
				emoji2=emoji_literals.UNICODE_TO_NAME.get(emoji2)
			await self.bot.db.execute(
				"""
				INSERT INTO lastfm_vote_setting (user_id, is_enabled, upvote_emoji, downvote_emoji)
					VALUES (%s, %s, %s, %s)
				ON DUPLICATE KEY UPDATE
					upvote_emoji = VALUES(upvote_emoji), downvote_emoji = VALUES(downvote_emoji), is_enabled = VALUES(is_enabled)
				""",
				ctx.author.id,
				1,
				emoji1,
				emoji2,
			)
			await util.send_success(ctx, f" {ctx.author.mention}: your last.fm reaction emojis are now {emoji1} and {emoji2}")

	@reaction.command(name='clear', aliases=['reset'], description='Clear your LastFM NowPlaying Reactions', extras={'perms': 'donator'})
	async def clear(self, ctx):
		pass

	async def aapi_request(self, ctx, params, supress_errors=False):
		"""Get json data from the lastfm api"""
		url = "http://ws.audioscrobbler.com/2.0/"
		params["api_key"] = "a6e238510d35e97c58c4a9c19d5b7aad"
		params["format"] = "json"
		async with aiohttp.ClientSession() as session:
			async with session.get(url, params=params) as response:
				with contextlib.suppress(aiohttp.ContentTypeError):
					content = await response.json()
					if "error" in content or response.status != 200:
						if supress_errors:
							return
						raise exceptions.LastFMError(
							error_code=408,
							message="Could not connect to LastFM",
						)
					return content

	async def gget_playcount(self, ctx, username, artist, period, reference=None):
		if period != "overall":
			return await self.get_playcount_scraper(ctx, username, artist, period)

		try:
			data = await self.aapi_request(
				ctx,
				{
					"method": "artist.getinfo",
					"user": username,
					"artist": artist,
					"autocorrect": 1,
				},
			)
		except:
			data = {}
		try:
			count = int(data["artist"]["stats"]["userplaycount"])
			name = data["artist"]["name"]
		except (KeyError, TypeError):
			count = 0
			name = None

		if not reference:
			return count

		return count, reference, name


	@fm.command(name='taste', aliases=['compare'], description='compare music taste', usage='```Swift\nSyntax: !lf taste <@member>\nExample: !lf taste @cop#0001```', brief='member')
	async def fm_taste(self, ctx, user: discord.Member, *args):
		await username_to_ctx(ctx)
		arguments = parse_arguments(args)
		if ctx.author.id in self.bot.cache.lastfm:
			author_username=self.bot.cache.lastfm[ctx.author.id]
		else:
			return await util.send_error(ctx, f"`you haven't set your **lastfm** username")
		if user.id in self.bot.cache.lastfm:
			user_username=self.bot.cache.lastfm[user.id]
		else:
			return await util.send_error(ctx, f"`{str(user)}` hasn't set their **lastfm** username")
		if user == ctx.author:
			return await util.send_error(ctx, "You need to compare with someone else.")
		period=arguments['period']
		author_data = await self.api_request(
			{
				"user": author_username,
				"method": "library.getartists",
				"period": arguments["period"],
				"limit": 1000,#arguments["amount"],
			}
		)
		user_data = await self.api_request(
			{
				"user": user_username,
				"method": "library.getartists",
				"period": arguments["period"],
				"limit": 1000,#arguments["amount"],
			}
		)
		l={}
		tt=[]
		mm=[]
		n=[]
		t=[]
		m=[]
		for artist in author_data["artists"]["artist"]:
			l.update({artist['name']:(int(artist['playcount']))})
		for artist in user_data['artists']['artist']:
			if artist['name'] in l:
				t.append(artist['name'])
				m.append(int(l.get(artist['name'])))
				n.append(artist['url'])
				mm.append(int(artist['playcount']))
		data={"artists":t, ctx.author:m,user:mm,"urls":n}
#		author_artists = author_data["topartists"]["artist"]
		if not t:
			if period == "overall":
				await util.send_error(ctx,"You haven't listened to any artists yet.")
			else:
				await util.send_error(ctx,"You haven't listened to any artists in the last {}s.".format(period))
			return
		rows=[]
		# author_plays = []
		# artist_names = []
		# for artist in author_artists:
		# 	author_plays.append(int(artist['playcount']))
		# 	artist_names.append(artist["name"])

		# user_plays = []
		# async for artist in AsyncIter(artist_names):
		# 	play = await self.get_playcount(artist, user_username, user)
		# 	plays=str(play[0])
		# 	user_plays.append(int(plays))
		# tt=[]
		#data = {"Artist": artist_names, ctx.author.name: author_plays, user.name: user_plays}
		ddddd=0
		loopamount=len(data['artists'])
		amount=len(max(data['artists'][:10],key=len))
		dd=[]
		for i,artist_name in enumerate(t,start=0):
			authp=int(data[ctx.author][i])
			userp=int(data[user][i])
			artist=data['artists'][i]
			ddddd+=1
			if authp > userp: sym=" > "
			else: sym=" < "
			spaces_needed=int(amount) - int(len(data['artists'][i])) + 1
			space=" "
			spaces=space*int(spaces_needed)
			dd.append(f"{spaces_needed} {amount} {len(artist_name)}")
			rows.append(f"{artist}{spaces}{authp}{sym}{userp}\n")
			if ddddd==10:
				break
			if i == loopamount:
				break
		desc="".join(r for r in rows)
		#table=tabulate.tabulate(data, headers="keys")
		embed=discord.Embed(title=f"Taste Comparison {ctx.author.name} vs {user.name}", description=f"```{desc}```", color=self.bot.color).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)


		with contextlib.suppress(discord.NotFound):
			await ctx.send(embed=embed)

		#await ctx.send(file=img, embed=embed)

	@fm.command(name='topartists', aliases=["tar"], description='Most listened artists', usage="```Swift\nSyntax: !lf topartists <timeframe> <amount>\nExample: !lf tar alltime 10```",brief='timeframe, amount')
	async def topartists(self, ctx, *args):
		arguments = parse_arguments(args)
		await username_to_ctx(ctx)
		if arguments["period"] == "today":
			data = await self.custom_period(ctx.username, "artist")
		else:
			data = await self.api_request(
				{
					"user": ctx.username,
					"method": "user.gettopartists",
					"period": arguments["period"],
					"limit": arguments["amount"],
				}
			)
		user_attr = data["topartists"]["@attr"]
		artists = data["topartists"]["artist"][: arguments["amount"]]

		if not artists:
			raise exceptions.Info("You have not listened to anything yet!")

		rows = []
		for i, artist in enumerate(artists, start=1):
			name = util.escape_md(artist["name"])
			plays = artist["playcount"]
			rows.append(f"`{i}` [**{name}**](https://last.fm) ({plays} plays)")

		image_url = await self.get_artist_image(artists[0]["name"])
		formatted_timeframe = humanized_period(arguments["period"]).capitalize()

		content = discord.Embed()
		content.colour = await self.cached_image_color(image_url)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Total unique artists: {user_attr['total']}")
		content.set_author(
			name=f"{util.displayname(ctx.usertarget, escape=False)}'s {formatted_timeframe} top artists",
			icon_url=ctx.usertarget.display_avatar,
		)

		await util.send_as_pages(ctx, content, rows)

	@fm.command(aliases=["talb", 'ta'], description="Most Listened To Albums", usage="```Swift\nSyntax: !lf topalbums <timeframe> <amount>\nExample: !lf ta alltime 10```",brief='timeframe, amount')
	async def topalbums(self, ctx, *args):
		await username_to_ctx(ctx)
		arguments = parse_arguments(args)
		if arguments["period"] == "today":
			data = await self.custom_period(ctx.username, "album")
		else:
			data = await self.api_request(
				{
					"user": ctx.username,
					"method": "user.gettopalbums",
					"period": arguments["period"],
					"limit": arguments["amount"],
				}
			)
		user_attr = data["topalbums"]["@attr"]
		albums = data["topalbums"]["album"][: arguments["amount"]]

		if not albums:
			raise exceptions.Info("You have not listened to anything yet!")

		rows = []
		for i, album in enumerate(albums, start=1):
			name = util.escape_md(album["name"])
			artist_name = util.escape_md(album["artist"]["name"])
			plays = album["playcount"]
			rows.append(
				f"`{i}` [**{name}**](https://last.fm) by **{artist_name}** ({plays} plays)"
			)

		image_url = albums[0]["image"][-1]["#text"]
		formatted_timeframe = humanized_period(arguments["period"]).capitalize()

		content = discord.Embed()
		content.colour = await self.cached_image_color(image_url)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Total unique albums: {user_attr['total']}")
		content.set_author(
			name=f"{util.displayname(ctx.usertarget, escape=False)}'s {formatted_timeframe} top albums",
			icon_url=ctx.usertarget.display_avatar,
		)

		await util.send_as_pages(ctx, content, rows)

	
	@fm.command(name="nowplaying", aliases=['np'], description='show your last scrobble', brief='member[optional]')
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	@commands.guild_only()
	async def fm_nowplaying(self, ctx):
		await username_to_ctx(ctx)
		data = await self.api_request(
			{"user": ctx.username, "method": "user.getrecenttracks", "limit": 1}
		)

		tracks = data["recenttracks"]["track"]

		if not tracks:
			raise exceptions.Info("You have not listened to anything yet!")

		udata = await self.api_request(
			{"user": ctx.username, "method": "user.getinfo"}, ignore_errors=True
		)
		if udata is None:
			return None

		ign = udata["user"]["name"]
		pcc = udata["user"]["playcount"]
		dd=[]

		artist = tracks[0]["artist"]["#text"]
		album = tracks[0]["album"]["#text"]
		albumurl=tracks[0]['url']
		track = tracks[0]["name"]
		album_play=await self.get_playcount_album(artist, album, ctx.username, ctx.usertarget)
		track_play=await self.get_playcount_track(artist, track, ctx.username, ctx.usertarget)
		artist_play=await self.get_playcount(artist, ctx.username, ctx.usertarget)
		artist_plays=str(artist_play[0])
		if not artist_plays:
			artist_plays="0"
		album_plays=str(album_play[0])
		if not album_plays:
			album_plays="0"
		track_plays=str(track_play[0])
		if not track_plays:
			track_plays="0"
		image_url = tracks[0]["image"][-1]["#text"]
		url = tracks[0]["url"]
		trackurl=url or "https://last.fm"
		artistt=artist.replace(" ", "+")
		arturl=f"https://www.last.fm/music/{artistt}"
		content = discord.Embed()
		content.colour = await self.cached_image_color(image_url)
		#content.description = f"🎵 **{util.escape_md(album)}**"
		content.add_field(name="**Track**", value=f"[{util.escape_md(track)}]({trackurl})")
		content.add_field(name="**Artist**", value=f"[{util.escape_md(artist)}]({arturl})")
		#content.description = f"🎵 **{util.escape_md(album)}**"
		#content.title = f"**{util.escape_md(artist)} — *{util.escape_md(track)}* **"
		content.set_thumbnail(url=image_url)


		# tags and playcount
		trackdata = await self.api_request(
			{"user": ctx.username, "method": "track.getInfo", "artist": artist, "track": track},
			ignore_errors=True,
		)
		if trackdata is not None:
			tags = []
			try:
				trackdata = trackdata["track"]
				playcount = int(trackdata["userplaycount"])
				if playcount > 0:
					pc=f"{playcount} {format_plays(playcount)}"
					pccc=playcount
				else:
					pc="0"
					pccc="0"
				for tag in trackdata["toptags"]["tag"]:
					tags.append(tag["name"])
					taglist=", ".join(tags)
					dd.append(taglist)
				#content.set_footer(text=", ".join(tags))
				content.set_footer(text=f"Playcount: {pc} ・ Scrobbles: {pcc} ・ Album: {util.escape_md(album)}")
			except (KeyError, TypeError):
				pass

		# play state
		np = "@attr" in tracks[0] and "nowplaying" in tracks[0]["@attr"]
		state = " > Now Playing" if np else "'s Last track"
		if not np:
			content.timestamp = arrow.get(int(tracks[0]["date"]["uts"])).datetime
		if ctx.usertarget.id == 956618986110476318:
			content.set_author(
				name=f"{util.displayname(ctx.usertarget, escape=False)}{state}",
				icon_url=ctx.usertarget.display_avatar,
			)
		else:
			content.set_author(
				name=f"Last.fm: {ctx.username}",
				icon_url=ctx.usertarget.display_avatar,
			)
		if ctx.author.id in self.bot.cache.lastfm_embeds:
			msg=self.bot.cache.lastfm_embeds[int(ctx.usertarget.id)]
		else:
			msg=None
		#msg=await self.bot.db.execute("""SELECT message FROM last_fm_embed WHERE user_id = %s""", ctx.author.id, one_value=True)
		if msg:
			if msg.startswith("{embed}"):
				try:
				# if msg:
					msg=msg.replace('{artist}', util.escape_md(artist))
					msg=msg.replace("{playcount}", f"{pc.strip(' plays')}")
					msg=msg.replace("{user}", util.displayname(ctx.usertarget, escape=False))
					msg=msg.replace('{avatar}', f'{ctx.usertarget.display_avatar}')
					msg=msg.replace("{track.url}", trackurl)
					msg=msg.replace("{artist.url}", arturl)
					msg=msg.replace("{album.plays}", str(album_plays))
					msg=msg.replace("{track.plays}", str(track_plays))
					msg=msg.replace("{artist.plays}",str(artist_plays))
					track=track.replace("_", r'\\_')
					msg=msg.replace("{track.lower}", str(track).lower())
					msg=msg.replace("{artist.lower}", str(artist).lower())
					msg=msg.replace("{album.lower}", str(album).lower())
					msg=msg.replace("{track.hyper.lower}", f"[{str(track).lower()}]({trackurl})")
					msg=msg.replace("{artist.hyper.lower}", f"[{str(artist).lower()}]({arturl})")
					msg=msg.replace("{album.hyper.lower}",f"[{str(album).lower()}]({albumurl})")
					msg=msg.replace("{album.hyper}",f"[{str(album)}]({albumurl})")
					msg=msg.replace("{track.hyper}", f"[{util.escape_md(track)}]({trackurl})")
					msg=msg.replace("{artist.hyper}", f"[{util.escape_md(artist)}]({arturl})")
					if dd:
						msg=msg.replace("{tags}", dd[0])
					msg=msg.replace("{scrobbles}", f"{pcc}")
					msg=msg.replace("{track.color}", f"{await self.cached_image_color(image_url)}")
					msg=msg.replace("{track.image}", image_url)
					msg=msg.replace("{album}", util.escape_md(album))
					msg=msg.replace("{lastfm.user}", f'{ctx.username}')
					sg=msg.replace("{state}", state)
					msg=msg.replace("{track}", util.escape_md(track))
					params=await util.embed_replacement(ctx.author,ctx.guild,msg)
					message = await util.to_embed(ctx.channel,ctx.author,ctx.guild,params)
				except Exception as e:
					await ctx.send(e)
			else:
				try:
					if "$(artist)" in msg:
						msg=msg.replace('$(artist)', util.escape_md(artist))

					if "$(playcount)" in msg:
						msg=msg.replace("$(playcount)", pc.strip(" plays"))
					if "$(user)" in msg:
						msg=msg.replace("$(user)", util.displayname(ctx.usertarget, escape=False))
					if "$(avatar)" in msg:
						msg=msg.replace('$(avatar)', f'{ctx.usertarget.display_avatar}')
					if "$(track.url)" in msg:
						msg=msg.replace("$(track.url)", trackurl)
					if "$(artist.url)" in msg:
						msg=msg.replace("$(artist.url)", arturl)
					if "$(track.lower)" in msg:
						if "_" in track:
							track=track.replace("_", r'\\_')
						msg=msg.replace("$(track)", str(track).lower())
					if "$(artist.lower)" in msg:
						msg=msg.replace('$(artist)', str(artist).lower())
					if "$(track.hyper.lower)" in msg:
						msg=msg.replace("$(track.hyper.lower)", f"[{str(track).lower()}]({trackurl})")
					if "$(artist.hyper.lower)" in msg:
						msg=msg.replace("$(artist.hyper.lower)", f"[{str(artist).lower()}]({arturl})")
					if "$(track.hyper)" in msg:
						msg=msg.replace("$(track.hyper)", f"[{util.escape_md(track)}]({trackurl})")
					if "$(artist.hyper)" in msg:
						msg=msg.replace("$(artist.hyper)", f"[{util.escape_md(artist)}]({arturl})")
					if "$(tags)" in msg:
						msg=msg.replace("$(tags)", taglist)
					if "$(scrobbles)" in msg:
						msg=msg.replace("$(scrobbles)", pcc)
					if "$(track.color)" in msg:
						msg=msg.replace("$(track.color)", await self.cached_image_color(image_url))
					if "$(track.image)" in msg:
						msg=msg.replace("$(track.image)", image_url)
					if "$(album)" in msg:
						msg=msg.replace("$(album)", util.escape_md(album))
					if "$(lastfm.user)" in msg:
						msg=msg.replace("$(lastfm.user)", ctx.username)
					if "$(state)" in msg:
						msg=msg.replace("$(state)", state)
					if "$(track)" in msg:
						msg=msg.replace("$(track)", util.escape_md(track))
					if "$(" in msg:
							try:
								jd=[]
								kd=[]
								jd=msg.split("$")
								for jd in jd:
									result = jd[jd.find('(')+1:jd.find(')')]
									kd.append(result)
								kd.pop(0)
								for kd in kd:
									msg=msg.replace(f"$({kd})", f"{eval(kd)}")
							except:
								pass
					embed_dict = self._get_embed_from_json(ctx.channel,msg)
					message=await Message.Embed(**embed_dict).send(ctx)
				except Exception as e:
					try:
						if "$(track)" in msg:
							if "_" in track:
								track=track.replace("_", r'\\_')
							msg=msg.replace("$(track)", track)
						if "$(artist)" in msg:
							msg=msg.replace('$(artist)', artist)
						if "$(track.lower)" in msg:
							if "_" in track:
								track=track.replace("_", r'\\_')
							msg=msg.replace("$(track)", str(track).lower())
						if "$(artist.lower)" in msg:
							msg=msg.replace('$(artist)', str(artist).lower())
						if "$(track.hyper)" in msg:
							msg=msg.replace("$(track.hyper)", f"[{track}]({trackurl})")
						if "$(track.hyper.lower)" in msg:
							msg=msg.replace("$(track.hyper.lower)", f"[{str(track).lower()}]({trackurl})")
						if "$(artist.hyper.lower)" in msg:
							msg=msg.replace("$(artist.hyper.lower)", f"[{str(artist).lower()}]({arturl})")
						if "$(artist.hyper)" in msg:
							msg=msg.replace("$(artist.hyper)", f"[{artist}]({arturl})")
						if "$(playcount)" in msg:
							msg=msg.replace("$(playcount)", pc.strip(" plays"))
						if "$(user)" in msg:
							msg=msg.replace("$(user)", util.displayname(ctx.usertarget, escape=False))
						if "$(avatar)" in msg:
							msg=msg.replace('$(avatar)', f'{ctx.usertarget.display_avatar}')
						if "$(track.url)" in msg:
							msg=msg.replace("$(track.url)", trackurl)
						if "$(artist.url)" in msg:
							msg=msg.replace("$(artist.url)", arturl)
						if "$(tags)" in msg:
							msg=msg.replace("$(tags)", taglist)
						if "$(scrobbles)" in msg:
							msg=msg.replace("$(scrobbles)", pcc)
						if "$(track.color)" in msg:
							msg=msg.replace("$(track.color)", await self.cached_image_color(image_url))
						if "$(track.image)" in msg:
							msg=msg.replace("$(track.image)", image_url)
						if "$(album)" in msg:
							msg=msg.replace("$(album)", util.escape_md(album))
						if "$(lastfm.user)" in msg:
							msg=msg.replace("$(lastfm.user)", ctx.username)
						if "$(state)" in msg:
							msg=msg.replace("$(state)", state)
						if "$(" in msg:
							try:
								jd=[]
								kd=[]
								jd=msg.split("$")
								for jd in jd:
									result = jd[jd.find('(')+1:jd.find(')')]
									kd.append(result)
								kd.pop(0)
								for kd in kd:
									msg=msg.replace(f"$({kd})", f"{eval(kd)}")
							except:
								pass
						embed_dict = self._get_embed_from_json(ctx.channel,msg)
						message=await Message.Embed(**embed_dict).send(ctx)
					except Exception as e:
						message=await ctx.send(embed=content)
		if not msg:
			message = await ctx.send(embed=content)
		voting_settings = await ctx.bot.db.execute(
			"""
			SELECT is_enabled, upvote_emoji, downvote_emoji
			FROM lastfm_vote_setting WHERE user_id = %s
			""",
			ctx.author.id,
			one_row=True,
		)
		if voting_settings:
			(voting_mode, upvote, downvote) = voting_settings
			if voting_mode:
				if upvote:
					if upvote.startswith("<"): 
						await message.add_reaction(upvote)
					else:
						await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(upvote))
				else:
					await message.add_reaction("🔥")
				if downvote:
					if downvote.startswith("<"): 
						await message.add_reaction(downvote)
					else:
						await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(downvote))
				else:
					await message.add_reaction("🗑️")
		else:
			await message.add_reaction("🔥")
			await message.add_reaction("🗑️")

	@fm.command(name="crowns", description='check your artist crowns', brief='member[optional]')
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	@commands.guild_only()
	async def fm_crowns(self, ctx, *, user: discord.Member = None):
		if user is None:
			user = ctx.author

		crownartists = await self.bot.db.execute(
			"""
			SELECT artist_name, cached_playcount FROM artist_crown
			WHERE guild_id = %s AND user_id = %s ORDER BY cached_playcount DESC
			""",
			ctx.guild.id,
			user.id,
		)
		if not crownartists:
			return await ctx.send(
				"You haven't acquired any crowns yet! "
				"Use the `!whoknows` command to claim crowns of your favourite artists :crown:"
			)

		rows = []
		for artist, playcount in crownartists:
			artistt=artist.replace(" ", "+")
			arturl=f"https://www.last.fm/music/{artistt}"
			rows.append(
				f"[{util.escape_md(str(artist))}]({arturl}) ({playcount} {format_plays(playcount)})"
			)

		content = discord.Embed(color=discord.Color.gold())
		content.set_author(
			name=f"👑 {util.displayname(user, escape=False)}'s artist crowns",
			icon_url=user.display_avatar.url,
		)
		content.set_footer(text=f"Total {len(crownartists)} crowns")
		await util.send_as_pages(ctx, content, rows)

	@fm.command(name='index', aliases=['i'],description='index all plays')
	async def fm_index(self, ctx):
		await username_to_ctx(ctx)
		msg=await ctx.send(embed=discord.Embed(color=self.color, description=f"<a:loading:940728015640481822> {ctx.author.mention}: Indexing your **plays**"))
		tasks=[]
		data = await self.api_request({"user": ctx.username,"method": "user.gettopartists","period": "overall","limit": 15})
		user_attr = data["topartists"]["@attr"]
		artists = data["topartists"]["artist"][: 15]
		for artist in artists:
			try:
				artistname = discord.utils.escape_markdown(artist)
			except:
				artistname = artist
			plays = artist["playcount"]
			try:
				old_king = await self.bot.db.execute("SELECT cached_playcount FROM artist_crown WHERE artist_name = %s AND guild_id = %s",artistname,ctx.guild.id,one_value=True)
				if int(plays) > int(old_king):
					await self.bot.db.execute(
						"""
						INSERT INTO artist_crown (guild_id, user_id, artist_name, cached_playcount)
							VALUES (%s, %s, %s, %s)
						ON DUPLICATE KEY UPDATE
							cached_playcount = VALUES(cached_playcount),
							user_id = VALUES(user_id)
						""",
						ctx.guild.id,
						ctx.author.id,
						artistname,
						plays,
					)
			except:
				pass
		await msg.edit(embed=discord.Embed(color=self.good, description=f"{self.bot.yes} {ctx.author.mention}: successfully **indexed** your `plays`"))


	@fm.command(name="whoknows", aliases=["wk", "whomstknows"], description='Who has listened to a given artist the most', usage="```Swift\nSyntax: !lf whoknows <artist name>\nExample: !lf wk xxxtentacion```",brief='artist')
	@commands.guild_only()
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	async def fm_whoknows(self, ctx, *, artistname=None):
		if artistname is None:
			artistname = (await self.getnowplaying(ctx))["artist"]

		artistname = remove_mentions(artistname)
		if artistname.lower() == "np":
			artistname = (await self.getnowplaying(ctx))["artist"]
			if artistname is None:
				raise exceptions.Warning("Could not get currently playing artist!")

		listeners = []
		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_playcount(artistname, lastfm_username, member))

		if tasks:
			data = await asyncio.gather(*tasks)
			try:
				for playcount, member, name, lastfm_username in data:
					artistname = name
					if playcount > 0:
						listeners.append((playcount, member, lastfm_username))
			except Exception as err:
				error=default.traceback_maker(err)
				print(error)
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		artistname = util.escape_md(artistname)

		rows = []
		old_king = None
		new_king = None
		totallisteners=len(listeners)
		total = 0
		rrrr=0
		pcc=0
		count=0
		end=len(listeners)
		for i, (playcount, member, lastfm_username) in enumerate(sorted(listeners, key=lambda p: p[0], reverse=True), start=1):
			if i == 1:
				rank = ":crown:"
				old_king = await self.bot.db.execute(
					"SELECT user_id FROM artist_crown WHERE artist_name = %s AND guild_id = %s",
					artistname,
					ctx.guild.id,
					one_value=True,
				)
				await self.bot.db.execute(
					"""
					INSERT INTO artist_crown (guild_id, user_id, artist_name, cached_playcount)
						VALUES (%s, %s, %s, %s)
					ON DUPLICATE KEY UPDATE
						cached_playcount = VALUES(cached_playcount),
						user_id = VALUES(user_id)
					""",
					ctx.guild.id,
					member.id,
					artistname,
					playcount,
				)
				if old_king:
					old_king = ctx.guild.get_member(old_king)
				new_king = member
			else:
				rank = f"`{i}`"
			if ctx.author == member:
				rrrr+=i
				pcc+=playcount
			crown=f"Your plays: **{pcc}** - Rank: `{rrrr}`"
			try:
				if not old_king or old_king is None or old_king.id != new_king.id:
					crrr=f"\n> **{new_king.name}#{new_king.discriminator}** just stole the **{artistname}** crown from **{old_king.name}#{old_king.discriminator}**"
				else:
					crrr=""
			except:
				crrr=""
			crown=f"Your plays: **{pcc}** - Rank: `{rrrr}`{crrr}"
			if check_num(i) or i == end:
				rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** has **{playcount}** {format_plays(playcount)}\n{crown}")
			else:
				#rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** — **{playcount}** {format_plays(playcount)}")
				rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** has **{playcount}** {format_plays(playcount)}")
			total += playcount

		if not rows:
			return await ctx.send(f"Nobody on this server has listened to **{artistname}**")

		content = discord.Embed(title=f"Top Listeners for artist {artistname}").set_author(name=ctx.author.display_name,icon_url=ctx.author.display_avatar.url)
		image_url = await self.get_artist_image(artistname)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Collective plays: {total}")

		content.colour = await self.cached_image_color(image_url)

		await util.send_as_pages(ctx, content, rows)
		if not old_king or old_king is None or old_king.id == new_king.id:
			return #await ctx.send(embed=discord.Embed(color=self.color, description=f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**"))

		#await ctx.send(f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**")

		#await ctx.send(f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**")

	# @fm.command(name="globalwhoknows", aliases=["gwk", "gwhomstknows"], description='Who has listened to a given artist the most', usage="```Swift\nSyntax: !lf whoknows <artist name>\nExample: !lf wk xxxtentacion```",brief='artist', hidden=True, disabled=True)
	# @commands.guild_only()
	# @commands.cooldown(2, 5, type=commands.BucketType.user)
	# async def fm_g_whoknows(self, ctx, *, artistname=None):
	# 	if artistname is None:
	# 		artistname = (await self.getnowplaying(ctx))["artist"]

	# 	artistname = remove_mentions(artistname)
	# 	if artistname.lower() == "np":
	# 		artistname = (await self.getnowplaying(ctx))["artist"]
	# 		if artistname is None:
	# 			raise exceptions.Warning("Could not get currently playing artist!")

	# 	listeners = []
	# 	tasks = []
	# 	for user_id, lastfm_username in await self.global_lastfm_usernames(
	# 		ctx, filter_cheaters=True
	# 	):
	# 		member = self.bot.get_user(user_id)
	# 		if member is None:
	# 			continue

	# 		tasks.append(self.get_playcount(artistname, lastfm_username, member))

	# 	if tasks:
	# 		data = await asyncio.gather(*tasks)
	# 		try:
	# 			for playcount, member, name, lastfm_username in data:
	# 				artistname = name
	# 				if playcount > 0:
	# 					listeners.append((playcount, member, lastfm_username))
	# 		except Exception as err:
	# 			error=default.traceback_maker(err)
	# 			print(error)
	# 	else:
	# 		return await ctx.send("Nobody on this server has connected their last.fm account yet!")

	# 	artistname = util.escape_md(artistname)

	# 	rows = []
	# 	old_king = None
	# 	new_king = None
	# 	totallisteners=len(listeners)
	# 	total = 0
	# 	rrrr=0
	# 	pcc=0
	# 	count=0
	# 	end=len(listeners)
	# 	for i, (playcount, member, lastfm_username) in enumerate(
	# 		sorted(listeners, key=lambda p: p[0], reverse=True), start=1
	# 	):
	# 		if i == 1:
	# 			rank = ":crown:"
	# 			old_king = await self.bot.db.execute(
	# 				"SELECT user_id FROM artist_crown WHERE artist_name = %s AND guild_id = %s",
	# 				artistname,
	# 				ctx.guild.id,
	# 				one_value=True,
	# 			)
	# 			await self.bot.db.execute(
	# 				"""
	# 				INSERT INTO artist_crown (guild_id, user_id, artist_name, cached_playcount)
	# 					VALUES (%s, %s, %s, %s)
	# 				ON DUPLICATE KEY UPDATE
	# 					cached_playcount = VALUES(cached_playcount),
	# 					user_id = VALUES(user_id)
	# 				""",
	# 				ctx.guild.id,
	# 				member.id,
	# 				artistname,
	# 				playcount,
	# 			)
	# 			if old_king:
	# 				old_king = ctx.guild.get_member(old_king)
	# 			new_king = member
	# 		else:
	# 			rank = f"`{i}`"
	# 		if ctx.author == member:
	# 			rrrr+=i
	# 			pcc+=playcount
	# 		crown=f"Your plays: **{pcc}** - Rank: `{rrrr}`"
	# 		try:
	# 			if not old_king or old_king is None or old_king.id != new_king.id:
	# 				crrr=f"> **{new_king.name}#{new_king.discriminator}** just stole the **{artistname}** crown from **{old_king.name}#{old_king.discriminator}**\n{crown}"
	# 			else:
	# 				crrr=crown
	# 		except:
	# 			crrr=crown
	# 		if check_num(i) or i == end:
	# 			rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** has **{playcount}** {format_plays(playcount)}\n\n{crown}")
	# 		else:
	# 			#rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** — **{playcount}** {format_plays(playcount)}")
	# 			rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** has **{playcount}** {format_plays(playcount)}")
	# 		total += playcount

	# 	if not rows:
	# 		return await ctx.send(f"Nobody on this server has listened to **{artistname}**")

	# 	content = discord.Embed(title=f"Who knows **{artistname}**?")
	# 	image_url = await self.get_artist_image(artistname)
	# 	content.set_thumbnail(url=image_url)
	# 	content.set_footer(text=f"Collective plays: {total}")

	# 	content.colour = await self.cached_image_color(image_url)

	# 	await util.send_as_pages(ctx, content, rows)
	# 	if not old_king or old_king is None or old_king.id == new_king.id:
	# 		return #await ctx.send(embed=discord.Embed(color=self.color, description=f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**"))

	# 	#await ctx.send(f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**")

	# 	#await ctx.send(f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**")


	@fm.command(name="whoknowstrack", aliases=["wkt", "whomstknowstrack"], description='Who has listened to a given song the most', usage="```Swift\nSyntax: !lf whoknowstrack <track name> | <artist name>\nExample: !lf whoknowstrack np```",brief='track | artist / np')
	@commands.guild_only()
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	async def fm_whoknowstrack(self, ctx, *, track=None):
		try:
			track = remove_mentions(track)
		except:
			pass

		if track is None:
			npd = await self.getnowplaying(ctx)
			trackname = npd["track"]
			trackurl=npd['track']
			artistname = npd["artist"]
		else:
			try:
				trackname, artistname = [x.strip() for x in track.split("|")]
				if "" in (trackname, artistname):
					raise ValueError
			except ValueError:
				raise exceptions.Warning("Incorrect format! use `track | artist`")

		listeners = []
		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_playcount_track(artistname, trackname, lastfm_username, member))

		if tasks:
			data = await asyncio.gather(*tasks)
			for playcount, user, metadata, username in data:
				artistname, trackname, image_url = metadata
				if playcount > 0:
					listeners.append((playcount, user, username))
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		artistname = util.escape_md(artistname)
		trackname = util.escape_md(trackname)

		rows = []
		total = 0
		for i, (playcount, user, username) in enumerate(
			sorted(listeners, key=lambda p: p[0], reverse=True), start=1
		):
			rows.append(
				f"`#{i}` **[{util.displayname(user)}](https://last.fm/{username})** has **{playcount}** {format_plays(playcount)}"
			)
			total += playcount

		if not rows:
			return await ctx.send(
				f"Nobody on this server has listened to **{trackname}** by **{artistname}**"
			)

		if image_url is None:
			image_url = await self.get_artist_image(artistname)

		content = discord.Embed(title=f"Top Listeners for track {trackname}").set_author(name=ctx.author.display_name,icon_url=ctx.author.display_avatar.url)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Collective plays: {total}")

		content.colour = await self.cached_image_color(image_url)

		await util.send_as_pages(ctx, content, rows)

	@fm.command(name="whoknowsalbum", aliases=["wka", "whomstknowsalbum"], description='Who has listened to a given album the most', usage="```Swift\nSyntax: !lf whoknowsalbum <album name> | <artist name>\nExample: !lf whoknowsalbum np```",brief='album | artist / np')
	@commands.guild_only()
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	async def fm_whoknowsalbum(self, ctx, *, album="np"):
		if album is None:
			npd = await self.getnowplaying(ctx)
			albumname = npd["album"]
			artistname = npd["artist"]

		try:
			album = remove_mentions(album)
		except:
			album=album
		if album.lower() == "np":
			npd = await self.getnowplaying(ctx)
			albumname = npd["album"]
			artistname = npd["artist"]
			if None in [albumname, artistname]:
				raise exceptions.Warning("Could not get currently playing album!")
		else:
			try:
				albumname, artistname = [x.strip() for x in album.split("|")]
				if "" in (albumname, artistname):
					raise ValueError
			except ValueError:
				raise exceptions.Warning("Incorrect format! use `album | artist`")

		listeners = []
		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_playcount_album(artistname, albumname, lastfm_username, member))

		if tasks:
			data = await asyncio.gather(*tasks)
			for playcount, user, metadata, username in data:
				artistname, albumname, image_url = metadata
				if playcount > 0:
					listeners.append((playcount, user, username))
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		artistname = util.escape_md(artistname)
		albumname = util.escape_md(albumname)

		rows = []
		total = 0
		for i, (playcount, user, username) in enumerate(
			sorted(listeners, key=lambda p: p[0], reverse=True), start=1
		):
			rows.append(
				f"`{i}` **[{util.displayname(user)}](https://last.fm/{username})** has **{playcount}** {format_plays(playcount)}"
			)
			total += playcount

		if not rows:
			return await ctx.send(
				f"Nobody on this server has listened to **{albumname}** by **{artistname}**"
			)

		if image_url is None:
			image_url = await self.get_artist_image(artistname)

		content = discord.Embed(title=f"Top Listeners for album {albumname}").set_author(name=ctx.author.display_name,icon_url=ctx.author.display_avatar.url)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Collective plays: {total}")

		content.colour = await self.cached_image_color(image_url)

		await util.send_as_pages(ctx, content, rows)

	@fm.command(aliases=["tt"], description='Most listened track', usage="```Swift\nSyntax: !lf toptracks <timeframe> <amount>\nExample: !lf toptracks```",brief='timeframe, amount[optional]')
	async def toptracks(self, ctx, *args):
		arguments = parse_arguments(args)
		await username_to_ctx(ctx)
		if arguments["period"] == "today":
			data = await self.custom_period(ctx.username, "track")
		else:
			data = await self.api_request(
				{
					"user": ctx.username,
					"method": "user.gettoptracks",
					"period": arguments["period"],
					"limit": arguments["amount"],
				}
			)
		user_attr = data["toptracks"]["@attr"]
		tracks = data["toptracks"]["track"][: arguments["amount"]]

		if not tracks:
			raise exceptions.Info("You have not listened to anything yet!")

		rows = []
		for i, track in enumerate(tracks, start=1):
			if i == 1:
				image_url = await self.get_artist_image(tracks[0]["artist"]["name"])

			name = util.escape_md(track["name"])
			artist_name = util.escape_md(track["artist"]["name"])
			plays = track["playcount"]
			rows.append(
				f"`{i}` **[{name}](https://last.fm)** by **{artist_name}** ({plays} plays)"
			)

		formatted_timeframe = humanized_period(arguments["period"]).capitalize()

		content = discord.Embed()
		content.colour = await self.cached_image_color(image_url)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Total unique tracks: {user_attr['total']}")
		content.set_author(
			name=f"{util.displayname(ctx.usertarget, escape=False)}'s {formatted_timeframe} top tracks",
			icon_url=ctx.usertarget.display_avatar,
		)

		await util.send_as_pages(ctx, content, rows)

	@fm.command(aliases=["recents", "re"], description="Recently listened to tracks", usage="```Swift\nSyntax: !lf recent <size>\nExample: !lf recent 10```",brief='size[optional]')
	async def recent(self, ctx, size="15"):
		await username_to_ctx(ctx)
		try:
			size = abs(int(size))
		except ValueError:
			size = 15

		data = await self.api_request(
			{"user": ctx.username, "method": "user.getrecenttracks", "limit": size}
		)
		user_attr = data["recenttracks"]["@attr"]
		tracks = data["recenttracks"]["track"][:size]

		if not tracks:
			raise exceptions.Info("You have not listened to anything yet!")

		rows = []
		for track in tracks:
			name = util.escape_md(track["name"])
			artist_name = util.escape_md(track["artist"]["#text"])
			rows.append(f"**{artist_name}** by ***{name}***")

		image_url = tracks[0]["image"][-1]["#text"]

		content = discord.Embed()
		content.colour = await self.cached_image_color(image_url)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Total scrobbles: {user_attr['total']}")
		content.set_author(
			name=f"{util.displayname(ctx.usertarget, escape=False)}'s Recent tracks",
			icon_url=ctx.usertarget.display_avatar,
		)

		await util.send_as_pages(ctx, content, rows)

	@fm.command(description='Your week/month/year listening overview', usage="```Swift\nUsage:\n!fm last week\n!fm last month (requires lastfm pro)\n!fm last year```",brief='timeframe')
	async def last(self, ctx, timeframe):
		timeframe = timeframe.lower()
		if timeframe not in ["week", "month", "year"]:
			raise exceptions.Info("Available timeframes: `[ week | month | year ]`")

		if timeframe != "week":
			raise exceptions.Warning(
				"Only the weekly listening report is currently available due to a Last.fm change, sorry for the inconvenience!"
			)

		await self.listening_report(ctx, timeframe)

	@fm.command(description='Artist specific data', brief='timeframe, data, artist',usage="```Swift\nSyntax !fm artist [timeframe] <data> <artist name>\n!fm artist week topalbums xxxtentacion```")
	async def artist(self, ctx, timeframe, datatype, *, artistname=""):
		await username_to_ctx(ctx)
		period = get_period(timeframe)
		if period in [None, "today"]:
			artistname = " ".join([datatype, artistname]).strip()
			datatype = timeframe
			period = "overall"

		artistname = remove_mentions(artistname)
		if artistname.lower() == "np":
			artistname = (await self.getnowplaying(ctx))["artist"]
			if artistname is None:
				raise exceptions.Warning("Could not get currently playing artist!")

		if artistname == "":
			return await ctx.send("Missing artist name!")

		if datatype in ["toptracks", "tt", "tracks", "track"]:
			datatype = "tracks"

		elif datatype in ["topalbums", "talb", "albums", "album"]:
			datatype = "albums"

		elif datatype in ["overview", "stats", "ov"]:
			return await self.artist_overview(ctx, period, artistname)

		else:
			return await util.send_command_help(ctx)

		artist, data = await self.artist_top(ctx, period, artistname, datatype)
		if artist is None or not data:
			artistname = util.escape_md(artistname)
			if period == "overall":
				return await ctx.send(f"You have never listened to **{artistname}**!")
			return await ctx.send(
				f"You have not listened to **{artistname}** in the past {period}s!"
			)

		total = 0
		rows = []
		for i, (name, playcount) in enumerate(data, start=1):
			rows.append(
				f"`#{i}` **{playcount}** {format_plays(playcount)} — **{util.escape_md(name)}**"
			)
			total += playcount

		artistname = urllib.parse.quote_plus(artistname)
		content = discord.Embed()
		content.set_thumbnail(url=artist["image_url"])
		content.colour = await self.cached_image_color(artist["image_url"])
		content.set_author(
			name=f"{util.displayname(ctx.usertarget, escape=False)} — "
			+ (f"{humanized_period(period)} " if period != "overall" else "")
			+ f"Top {datatype} by {artist['formatted_name']}",
			icon_url=ctx.usertarget.display_avatar,
			url=f"https://last.fm/user/{ctx.username}/library/music/{artistname}/"
			f"+{datatype}?date_preset={period_http_format(period)}",
		)
		content.set_footer(
			text=f"Total {total} {format_plays(total)} across {len(rows)} {datatype}"
		)

		await util.send_as_pages(ctx, content, rows)

	@fm.command(name="cover", description="Ger the album cover of your current song")
	async def cover(self, ctx):
		await username_to_ctx(ctx)
		data = await self.api_request(
			{"user": ctx.username, "method": "user.getrecenttracks", "limit": 1}
		)
		image_url = data["recenttracks"]["track"][0]["image"][-1]["#text"]
		image_hash = image_url.split("/")[-1].split(".")[0]
		big_image_url = self.cover_base_urls[4].format(image_hash)
		artist_name = data["recenttracks"]["track"][0]["artist"]["#text"]
		album_name = data["recenttracks"]["track"][0]["album"]["#text"]

		async with aiohttp.ClientSession() as session:
			async with session.get(big_image_url) as response:
				buffer = io.BytesIO(await response.read())
				await ctx.send(
					f"**{artist_name} — {album_name}**",
					file=discord.File(fp=buffer, filename=image_hash + ".jpg"),
				)

	@fm.command(name="album", description="Get your top tracks from an album", usage="```Swift\nSyntax: !lf album <album>\nExample: !lf album feelz```",brief='album')
	async def album(self, ctx, *, album):
		period = "overall"
		await username_to_ctx(ctx)
		if album is None:
			return await util.send_command_help(ctx)

		album = remove_mentions(album)
		if album.lower() == "np":
			npd = await self.getnowplaying(ctx)
			albumname = npd["album"]
			artistname = npd["artist"]
			if None in [albumname, artistname]:
				raise exceptions.Warning("Could not get currently playing album!")
		else:
			try:
				albumname, artistname = [x.strip() for x in album.split("|")]
				if "" in (albumname, artistname):
					raise ValueError
			except ValueError:
				raise exceptions.Warning("Incorrect format! use `album | artist`")

		album, data = await self.album_top_tracks(ctx, period, artistname, albumname)
		if album is None or not data:
			if period == "overall":
				return await ctx.send(
					f"You have never listened to **{albumname}** by **{artistname}**!"
				)
			return await ctx.send(
				f"You have not listened to **{albumname}** by **{artistname}** in the past {period}s!"
			)

		artistname = album["artist"]
		albumname = album["formatted_name"]

		total_plays = 0
		rows = []
		for i, (name, playcount) in enumerate(data, start=1):
			total_plays += playcount
			rows.append(
				f"`#{i:2}` **{playcount}** {format_plays(playcount)} **{util.escape_md(name)}**"
			)

		titlestring = f"top tracks from {albumname}\n— by {artistname}"
		artistname = urllib.parse.quote_plus(artistname)
		albumname = urllib.parse.quote_plus(albumname)
		content = discord.Embed()
		content.set_thumbnail(url=album["image_url"])
		content.set_footer(text=f"Total album plays: {total_plays}")
		content.colour = await self.cached_image_color(album["image_url"])
		content.set_author(
			name=f"{util.displayname(ctx.usertarget, escape=False)} — "
			+ (f"{humanized_period(period)} " if period != "overall" else "")
			+ titlestring,
			icon_url=ctx.usertarget.display_avatar,
			url=f"https://last.fm/user/{ctx.username}/library/music/{artistname}/"
			f"{albumname}?date_preset={period_http_format(period)}",
		)

		await util.send_as_pages(ctx, content, rows)

	async def album_top_tracks(self, ctx, period, artistname, albumname):
		"""Scrape the top tracks of given album from lastfm library page."""
		artistname = urllib.parse.quote_plus(artistname)
		albumname = urllib.parse.quote_plus(albumname)
		async with aiohttp.ClientSession() as session:
			url = (
				f"https://last.fm/user/{ctx.username}/library/music/{artistname}/"
				f"{albumname}?date_preset={period_http_format(period)}"
			)
			data = await fetch(session, url, handling="text")
			if data is None:
				raise exceptions.LastFMError(404, "Album page not found")

			soup = BeautifulSoup(data, "html.parser")

			album = {
				"image_url": soup.find("header", {"class": "library-header"})
				.find("img")
				.get("src")
				.replace("64s", "300s"),
				"formatted_name": soup.find("h2", {"class": "library-header-title"}).text.strip(),
				"artist": soup.find("header", {"class": "library-header"})
				.find("a", {"class": "text-colour-link"})
				.text.strip(),
			}

			all_results = get_list_contents(soup)
			all_results += await get_additional_pages(session, soup, url)

			return album, all_results

	async def artist_top(self, ctx, period, artistname, datatype):
		"""Scrape either top tracks or top albums from lastfm library page."""
		artistname = urllib.parse.quote_plus(artistname)
		async with aiohttp.ClientSession() as session:
			url = (
				f"https://last.fm/user/{ctx.username}/library/music/{artistname}/"
				f"+{datatype}?date_preset={period_http_format(period)}"
			)
			data = await fetch(session, url, handling="text")
			if data is None:
				raise exceptions.LastFMError(404, "Artist page not found")

			soup = BeautifulSoup(data, "html.parser")

			artist = {
				"image_url": soup.find("span", {"class": "library-header-image"})
				.find("img")
				.get("src")
				.replace("avatar70s", "avatar300s"),
				"formatted_name": soup.find("a", {"class": "library-header-crumb"}).text.strip(),
			}

			all_results = get_list_contents(soup)
			all_results += await get_additional_pages(session, soup, url)

			return artist, all_results

	async def artist_overview(self, ctx, period, artistname):
		"""Overall artist view."""
		albums = []
		tracks = []
		metadata = [None, None, None]
		artistinfo = await self.api_request({"method": "artist.getInfo", "artist": artistname})
		async with aiohttp.ClientSession() as session:
			url = (
				f"https://last.fm/user/{ctx.username}/library/music/"
				f"{urllib.parse.quote_plus(artistname)}"
				f"?date_preset={period_http_format(period)}"
			)
			data = await fetch(session, url, handling="text")
			if data is None:
				raise exceptions.LastFMError(404, "Artist page not found")

			soup = BeautifulSoup(data, "html.parser")
			try:
				albumsdiv, tracksdiv, _ = soup.findAll(
					"tbody", {"data-playlisting-add-entries": ""}
				)

			except ValueError:
				artistname = util.escape_md(artistname)
				if period == "overall":
					return await ctx.send(f"You have never listened to **{artistname}**!")
				return await ctx.send(
					f"You have not listened to **{artistname}** in the past {period}s!"
				)

			for container, destination in zip([albumsdiv, tracksdiv], [albums, tracks]):
				items = container.findAll("tr", {"class": "chartlist-row"})
				for item in items:
					name = item.find("td", {"class": "chartlist-name"}).find("a").get("title")
					playcount = (
						item.find("span", {"class": "chartlist-count-bar-value"})
						.text.replace("scrobbles", "")
						.replace("scrobble", "")
						.strip()
					)
					destination.append((name, int(playcount.replace(",", ""))))

			metadata_list = soup.find("ul", {"class": "metadata-list"})
			for i, metadata_item in enumerate(
				metadata_list.findAll("p", {"class": "metadata-display"})
			):
				metadata[i] = int(metadata_item.text.replace(",", ""))

		artist = {
			"image_url": soup.find("span", {"class": "library-header-image"})
			.find("img")
			.get("src")
			.replace("avatar70s", "avatar300s"),
			"formatted_name": soup.find("h2", {"class": "library-header-title"}).text.strip(),
		}

		artistname = urllib.parse.quote_plus(artistname)
		listeners = artistinfo["artist"]["stats"]["listeners"]
		globalscrobbles = artistinfo["artist"]["stats"]["playcount"]
		similar = [a["name"] for a in artistinfo["artist"]["similar"]["artist"]]
		tags = [t["name"] for t in artistinfo["artist"]["tags"]["tag"]]

		content = discord.Embed()
		content.set_thumbnail(url=artist["image_url"])
		content.colour = await self.cached_image_color(artist["image_url"])
		content.set_author(
			name=f"{util.displayname(ctx.usertarget, escape=False)} — {artist['formatted_name']} "
			+ (f"{humanized_period(period)} " if period != "overall" else "")
			+ "Overview",
			icon_url=ctx.usertarget.display_avatar,
			url=f"https://last.fm/user/{ctx.username}/library/music/{artistname}"
			f"?date_preset={period_http_format(period)}",
		)

		content.set_footer(text=f"{', '.join(tags)}")

		crown_holder = await self.bot.db.execute(
			"""
			SELECT user_id FROM artist_crown WHERE guild_id = %s AND artist_name = %s
			""",
			ctx.guild.id,
			artist["formatted_name"],
			one_value=True,
		)

		if crown_holder == ctx.usertarget.id:
			crownstate = " 👑"
		else:
			crownstate = ""

		scrobbles, albums_count, tracks_count = metadata
		content.add_field(name="Listeners", value=f"**{listeners}**")
		content.add_field(name="Scrobbles", value=f"**{globalscrobbles}**")
		content.add_field(name="Your scrobbles", value=f"**{scrobbles}**{crownstate}")

		content.add_field(
			name=f":cd: {albums_count} Albums",
			value="\n".join(
				f"`#{i:2}` **{util.escape_md(item)}** ({playcount})"
				for i, (item, playcount) in enumerate(albums, start=1)
			),
			inline=True,
		)
		content.add_field(
			name=f":musical_note: {tracks_count} Tracks",
			value="\n".join(
				f"`#{i:2}` **{util.escape_md(item)}** ({playcount})"
				for i, (item, playcount) in enumerate(tracks, start=1)
			),
			inline=True,
		)

		if similar:
			content.add_field(name="Similar artists", value=", ".join(similar), inline=False)

		await ctx.send(embed=content)

	async def fetch_color(self, session, album_art_id):
		async def get_image(url):
			async with session.get(url) as response:
				try:
					return Image.open(io.BytesIO(await response.read()))
				except Exception:
					return None

		image = None
		for base_url in self.cover_base_urls:
			image = await get_image(base_url.format(album_art_id))
			if image is not None:
				break

		if image is None:
			return None

		colors = colorgram.extract(image, 1)
		dominant_color = colors[0].rgb

		return (
			album_art_id,
			dominant_color.r,
			dominant_color.g,
			dominant_color.b,
			util.rgb_to_hex(dominant_color),
		)

	async def get_all_albums(self, username):
		params = {
			"user": username,
			"method": "user.gettopalbums",
			"period": "overall",
			"limit": 500,  # 1000 doesnt work due to lastfm bug
		}
		data = await self.api_request(dict(params, **{"page": 1}))
		topalbums = data["topalbums"]["album"]
		total_pages = int(data["topalbums"]["@attr"]["totalPages"])

		# get additional page if exists for a total of 1000
		if total_pages > 1:
			data = await self.api_request(dict(params, **{"page": 2}))
			topalbums += data["topalbums"]["album"]

		return topalbums

	@fm.group(aliases=["s", "guild"], description="Server wide statistics")
	@commands.guild_only()
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	async def server(self, ctx):
		if ctx.invoked_subcommand is None:
			#embed=discord.Embed(title=f"{emojis.LASTFM}", description="`lf/fm server`\n└ `np`, `recent/re`, `topartists/ta`, `topalbums/tab`, `toptracks/tt`").set_footer(text="Prefix = !")
			#await ctx.send(embed=embed)
			await util.command_group_help(ctx)

	@server.command(name="chart", aliases=["collage"], brief="[album | artist] [timeframe] [size] 'notitle'", usage="```Swift\nSyntax: !lf server chart [album | artist] [timeframe] [width]x[height] [notitle]\nExample: !lf server chart feelz lilpeep alltime```",description="Collage of the server's top albums or artists")
	async def server_chart(self, ctx: commands.Context, *args):
		arguments = parse_chart_arguments(args)

		if arguments["width"] + arguments["height"] > 30:
			raise exceptions.Info(
				"Size is too big! Chart `width` + `height` total must not exceed `30`"
			)

		chart_total = arguments["width"] * arguments["height"]

		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(
				self.get_server_top(
					lastfm_username,
					"album" if arguments["method"] == "user.gettopalbums" else "artist",
					period=arguments["period"],
				)
			)

		chart_type = "ERROR"
		content_map = {}
		if tasks:
			data = await asyncio.gather(*tasks)
			chart = []

			if arguments["method"] == "user.gettopalbums":
				chart_type = "top album"
				for user_data in data:
					if user_data is None:
						continue
					for album in user_data:
						album_name = album["name"]
						artist = album["artist"]["name"]
						name = f"{album_name} — {artist}"
						plays = int(album["playcount"])
						image_url = album["image"][3]["#text"]
						if name in content_map:
							content_map[name]["plays"] += plays
						else:
							content_map[name] = {"plays": plays, "image": image_url}

			elif arguments["method"] == "user.gettopartists":
				chart_type = "top artist"
				for user_data in data:
					if user_data is None:
						continue
					for artist in user_data:
						name = artist["name"]
						plays = int(artist["playcount"])
						if name in content_map:
							content_map[name]["plays"] += plays
						else:
							content_map[name] = {"plays": plays, "image": None}

		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		for i, (name, content_data) in enumerate(
			sorted(content_map.items(), key=lambda x: x[1]["plays"], reverse=True),
			start=1,
		):
			chart.append(
				(
					content_data["image"]
					if chart_type == "top album"
					else await self.get_artist_image(name),
					f"{content_data['plays']} {format_plays(content_data['plays'])}<br>{name}",
				)
			)
			if i >= chart_total:
				break

		buffer = await self.chart_factory(
			chart,
			arguments["width"],
			arguments["height"],
			show_labels=arguments["showtitles"],
		)

		await ctx.send(
			f"`{ctx.guild} {humanized_period(arguments['period'])} "
			f"{arguments['width']}x{arguments['height']} {chart_type} chart`",
			file=discord.File(
				fp=buffer, filename=f"fmchart_{ctx.guild}_{arguments['period']}.jpeg"
			),
		)



	@server.command(name="nowplaying", aliases=["np"], description="What this server is listening to", usage="```Swift\nSyntax: !lf server np <member>\nExample: !lf server np @cop#0001```",brief='member[optional]')
	async def server_nowplaying(self, ctx):
		listeners = []
		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(ctx):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_np(lastfm_username, member))

		total_linked = len(tasks)
		if tasks:
			data = await asyncio.gather(*tasks)
			for song, member_ref in data:
				if song is not None:
					listeners.append((song, member_ref))
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		if not listeners:
			return await ctx.send("Nobody on this server is listening to anything at the moment!")

		total_listening = len(listeners)
		rows = []
		maxlen = 0
		for song, member in listeners:
			dn = util.displayname(member)
			if len(dn) > maxlen:
				maxlen = len(dn)

		for song, member in listeners:
			rows.append(
				f"[{util.displayname(member)}](https://last.fm) | **{util.escape_md(song.get('artist'))}** — ***{util.escape_md(song.get('name'))}***"
			)

		content = discord.Embed()
		content.set_author(
			name=f"What is {ctx.guild.name} listening to?",
			icon_url=ctx.guild.icon,
		)
		content.colour = int(
			await util.color_from_image_url(str(ctx.guild.icon)), 16
		)
		content.set_footer(
			text=f"{total_listening} / {total_linked} Members are listening to music"
		)
		await util.send_as_pages(ctx, content, rows)

	@server.command(name="recent", aliases=["re"], usage="```Swift\nSyntax: !lf server recent\nExample: !lf server recent```",description='What this server has recently listened')
	async def server_recent(self, ctx):
		listeners = []
		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(ctx):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_lastplayed(lastfm_username, member))

		total_linked = len(tasks)
		total_listening = 0
		if tasks:
			data = await asyncio.gather(*tasks)
			for song, member_ref in data:
				if song is not None:
					if song.get("nowplaying"):
						total_listening += 1
					listeners.append((song, member_ref))
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		if not listeners:
			return await ctx.send("Nobody on this server is listening to anything at the moment!")

		listeners = sorted(listeners, key=lambda l: l[0].get("date"), reverse=True)
		rows = []
		for song, member in listeners:
			suffix = ""
			if song.get("nowplaying"):
				suffix = ":musical_note: "
			else:
				suffix = f"({arrow.get(song.get('date')).humanize()})"

			rows.append(
				f"{util.displayname(member)} | **{util.escape_md(song.get('artist'))}** by ***{util.escape_md(song.get('name'))}*** {suffix}"
			)

		content = discord.Embed()
		content.set_author(
			name=f"What has {ctx.guild.name} been listening to?",
			icon_url=ctx.guild.icon.with_size(64),
		)
		content.colour = int(
			await util.color_from_image_url(str(ctx.guild.icon.with_size(64))), 16
		)
		content.set_footer(
			text=f"{total_listening} / {total_linked} Members are listening to music right now"
		)
		await util.send_as_pages(ctx, content, rows)

	@server.command(name="topartists", aliases=["tar"], description='Combined top artists of server members', usage="```Swift\nSyntax: !lf server tar <timeframe>\nExample: !lf server tar alltime```",brief='timeframe')
	async def server_topartists(self, ctx, *args):
		artist_map = {}
		tasks = []
		total_users = 0
		total_plays = 0
		arguments = parse_arguments(args)
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(
				self.get_server_top(lastfm_username, "artist", period=arguments["period"])
			)

		if tasks:
			data = await asyncio.gather(*tasks)
			for user_data in data:
				if user_data is None:
					continue
				total_users += 1
				for data_block in user_data:
					name = data_block["name"]
					plays = int(data_block["playcount"])
					total_plays += plays
					if name in artist_map:
						artist_map[name] += plays
					else:
						artist_map[name] = plays
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		rows = []
		formatted_timeframe = humanized_period(arguments["period"]).capitalize()
		content = discord.Embed()
		content.set_author(
			name=f"{ctx.guild} — {formatted_timeframe} top artists",
			icon_url=ctx.guild.icon.with_size(64),
		)
		content.set_footer(text=f"Taking into account top 100 artists of {total_users} members")
		for i, (artistname, playcount) in enumerate(
			sorted(artist_map.items(), key=lambda x: x[1], reverse=True), start=1
		):
			if i == 1:
				image_url = await self.get_artist_image(artistname)
				content.colour = await self.cached_image_color(image_url)
				content.set_thumbnail(url=image_url)
			rows.append(
				f"`#{i}` [**{util.escape_md(artistname)}**](https://last.fm) ({playcount} plays)"
			)

		await util.send_as_pages(ctx, content, rows, 15)

	@server.command(name="topalbums", aliases=["talb", "tab", "ta"], brief='timeframe', usage="```Swift\nSyntax: !lf server tar <timeframe>\nExample: !lf server tar alltime```",description='Combined top albums of server members')
	async def server_topalbums(self, ctx, *args):
		album_map = {}
		tasks = []
		total_users = 0
		total_plays = 0
		arguments = parse_arguments(args)
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_server_top(lastfm_username, "album", period=arguments["period"]))

		if tasks:
			data = await asyncio.gather(*tasks)
			for user_data in data:
				if user_data is None:
					continue
				total_users += 1
				for data_block in user_data:
					name = f'{util.escape_md(data_block["artist"]["name"])} by *{util.escape_md(data_block["name"])}*'
					plays = int(data_block["playcount"])
					image_url = data_block["image"][-1]["#text"]
					total_plays += plays
					if name in album_map:
						album_map[name]["plays"] += plays
					else:
						album_map[name] = {"plays": plays, "image": image_url}
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		rows = []
		formatted_timeframe = humanized_period(arguments["period"]).capitalize()
		content = discord.Embed()
		content.set_author(
			name=f"{ctx.guild} — {formatted_timeframe} top albums",
			icon_url=ctx.guild.icon.with_size(64),
		)
		content.set_footer(text=f"Taking into account top 100 albums of {total_users} members")
		for i, (albumname, albumdata) in enumerate(
			sorted(album_map.items(), key=lambda x: x[1]["plays"], reverse=True), start=1
		):
			if i == 1:
				image_url = albumdata["image"]
				content.colour = await self.cached_image_color(image_url)
				content.set_thumbnail(url=image_url)

			playcount = albumdata["plays"]
			rows.append(f"`{i}` [**{albumname}**](https://last.fm) ({playcount} plays)")

		await util.send_as_pages(ctx, content, rows)

	@server.command(name="toptracks", aliases=["tt"], description='Combined top tracks of server members', usage="```Swift\nSyntax: !lf server tt <timeframe>\nExample: !lf server tt alltime```",brief='timeframe')
	async def server_toptracks(self, ctx, *args):
		track_map = {}
		tasks = []
		total_users = 0
		total_plays = 0
		arguments = parse_arguments(args)
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_server_top(lastfm_username, "track", period=arguments["period"]))

		if tasks:
			data = await asyncio.gather(*tasks)
			for user_data in data:
				if user_data is None:
					continue
				total_users += 1
				for data_block in user_data:
					name = f'{util.escape_md(data_block["artist"]["name"])} by *{util.escape_md(data_block["name"])}*'
					plays = int(data_block["playcount"])
					artistname = data_block["artist"]["name"]
					total_plays += plays
					if name in track_map:
						track_map[name]["plays"] += plays
					else:
						track_map[name] = {"plays": plays, "artist": artistname}
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		rows = []
		formatted_timeframe = humanized_period(arguments["period"]).capitalize()
		content = discord.Embed()
		content.set_author(
			name=f"{ctx.guild} — {formatted_timeframe} top tracks",
			icon_url=ctx.guild.icon.with_size(64),
		)
		content.set_footer(text=f"Taking into account top 100 tracks of {total_users} members")
		for i, (trackname, trackdata) in enumerate(
			sorted(track_map.items(), key=lambda x: x[1]["plays"], reverse=True), start=1
		):
			if i == 1:
				image_url = await self.get_artist_image(trackdata["artist"])
				content.colour = await self.cached_image_color(image_url)
				content.set_thumbnail(url=image_url)

			playcount = trackdata["plays"]
			rows.append(f"`#{i}` **[{trackname}](https://last.fm)** ({playcount} plays)")

		await util.send_as_pages(ctx, content, rows)

	async def get_server_top(self, username, datatype, period="overall"):
		limit = 100
		if datatype == "artist":
			data = await self.api_request(
				{
					"user": username,
					"method": "user.gettopartists",
					"limit": limit,
					"period": period,
				},
				ignore_errors=True,
			)
			return data["topartists"]["artist"] if data is not None else None
		if datatype == "album":
			data = await self.api_request(
				{
					"user": username,
					"method": "user.gettopalbums",
					"limit": limit,
					"period": period,
				},
				ignore_errors=True,
			)
			return data["topalbums"]["album"] if data is not None else None
		if datatype == "track":
			data = await self.api_request(
				{
					"user": username,
					"method": "user.gettoptracks",
					"limit": limit,
					"period": period,
				},
				ignore_errors=True,
			)
			return data["toptracks"]["track"] if data is not None else None

	@commands.command(aliases=["wk", "whomstknows"], description='Who has listened to a given artist the most', usage="```Swift\nSyntax: !whoknows <artist>\nExample: !whoknows np```",brief='artist')
	@commands.guild_only()
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	async def whoknows(self, ctx, *, artistname=None):
		if artistname is None:
			artistname = (await self.getnowplaying(ctx))["artist"]

		artistname = remove_mentions(artistname)
		if artistname.lower() == "np":
			artistname = (await self.getnowplaying(ctx))["artist"]
			if artistname is None:
				raise exceptions.Warning("Could not get currently playing artist!")

		listeners = []
		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_playcount(artistname, lastfm_username, member))

		if tasks:
			data = await asyncio.gather(*tasks)
			try:
				for playcount, member, name, lastfm_username in data:
					artistname = name
					if playcount > 0:
						listeners.append((playcount, member, lastfm_username))
			except Exception as err:
				error=default.traceback_maker(err)
				print(error)
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		artistname = util.escape_md(artistname)

		rows = []
		old_king = None
		new_king = None
		totallisteners=len(listeners)
		total = 0
		rrrr=0
		pcc=0
		count=0
		end=len(listeners)
		for i, (playcount, member, lastfm_username) in enumerate(
			sorted(listeners, key=lambda p: p[0], reverse=True), start=1
		):
			if i == 1:
				rank = ":crown:"
				old_king = await self.bot.db.execute(
					"SELECT user_id FROM artist_crown WHERE artist_name = %s AND guild_id = %s",
					artistname,
					ctx.guild.id,
					one_value=True,
				)
				await self.bot.db.execute(
					"""
					INSERT INTO artist_crown (guild_id, user_id, artist_name, cached_playcount)
						VALUES (%s, %s, %s, %s)
					ON DUPLICATE KEY UPDATE
						cached_playcount = VALUES(cached_playcount),
						user_id = VALUES(user_id)
					""",
					ctx.guild.id,
					member.id,
					artistname,
					playcount,
				)
				if old_king:
					old_king = ctx.guild.get_member(old_king)
				new_king = member
			else:
				rank = f"`{i}`"
			if ctx.author == member:
				rrrr+=i
				pcc+=playcount
			try:
				if not old_king or old_king is None or old_king.id != new_king.id:
					crrr=f"\n> **{new_king.name}#{new_king.discriminator}** just stole the **{artistname}** crown from **{old_king.name}#{old_king.discriminator}**"
				else:
					crrr=""
			except:
				crrr=""
			crown=f"Your plays: **{pcc}** - Rank: `{rrrr}`{crrr}"
			if check_num(i) or i == end:
				rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** has **{playcount}** {format_plays(playcount)}\n{crown}")
			else:
				#rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** — **{playcount}** {format_plays(playcount)}")
				rows.append(f"{rank} **[{util.displayname(member)}](https://last.fm/{lastfm_username})** has **{playcount}** {format_plays(playcount)}")
			total += playcount

		if not rows:
			return await ctx.send(f"Nobody on this server has listened to **{artistname}**")

		content = discord.Embed(title=f"Top Listeners for artist {artistname}").set_author(name=ctx.author.display_name,icon_url=ctx.author.display_avatar.url)
		image_url = await self.get_artist_image(artistname)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Collective plays: {total}")

		content.colour = await self.cached_image_color(image_url)

		await util.send_as_pages(ctx, content, rows)
		if not old_king or old_king is None or old_king.id == new_king.id:
			return #await ctx.send(embed=discord.Embed(color=self.color, description=f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**"))

		#await ctx.send(f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**")

		#await ctx.send(f"> **{util.displayname(new_king)}** just stole the **{artistname}** crown from **{util.displayname(old_king)}**")

	@fm.command(description='See what your n:th scrobble was', usage="```Swift\nSyntax: !lf milestone <int>\nExample: !lf milestone 10```",brief='int')
	async def milestone(self, ctx: commands.Context, n: int):
		n_display = util.ordinal(n)
		await username_to_ctx(ctx)
		if n < 1:
			raise exceptions.Warning(
				"Please give a number between 1 and your total amount of listened tracks."
			)
		per_page = 100
		pre_data = await self.api_request(
			{"user": ctx.username, "method": "user.getrecenttracks", "limit": per_page}
		)
		total = int(pre_data["recenttracks"]["@attr"]["total"])
		if n > total:
			raise exceptions.Warning(
				f"You have only listened to **{total}** tracks! Unable to show {n_display} track"
			)

		remainder = total % per_page
		total_pages = int(pre_data["recenttracks"]["@attr"]["totalPages"])
		if n > remainder:
			n = n - remainder
			containing_page = total_pages - math.ceil(n / per_page)
		else:
			containing_page = total_pages

		final_data = await self.api_request(
			{
				"user": ctx.username,
				"method": "user.getrecenttracks",
				"limit": per_page,
				"page": containing_page,
			}
		)

		# if user is playing something, the current nowplaying song will be appended to the list at index 101
		# cap to 100 first items after reversing to remove it
		tracks = list(reversed(final_data["recenttracks"]["track"]))[:100]
		nth_track = tracks[(n % 100) - 1]
		await ctx.send(
			f"Your {n_display} scrobble was **{nth_track['name']}** by **{nth_track['artist']['#text']}**"
		)

	@fm.command(aliases=["colourchart"], description='Collage based on colors', usage="```Swift\nSyntax !lf colorchart #<hex color> [NxN]\nExample: !lf colorchart #000001 3x3```",brief='color, size')
	async def colorchart(self, ctx: commands.Context, colour, size="3x3"):
		rainbow = colour.lower() in ["rainbow", "rainbowdiagonal"]
		await username_to_ctx(ctx)
		diagonal = colour.lower() == "rainbowdiagonal"
		if not rainbow:
			max_size = 30
			try:
				colour = discord.Color(value=int(colour.strip("#"), 16))
				query_color = colour.to_rgb()
			except ValueError:
				raise exceptions.Warning(f"`{colour}` is not a valid hex colour")

			dim = size.split("x")
			width = int(dim[0])
			if len(dim) > 1:
				height = abs(int(dim[1]))
			else:
				height = abs(int(dim[0]))

			if width + height > max_size:
				raise exceptions.Info(
					f"Size is too big! Chart `width` + `height` total must not exceed `{max_size}`"
				)
		else:
			width = 7
			height = 7

		topalbums = await self.get_all_albums(ctx.username)

		albums = set()
		album_color_nodes = []
		for album in topalbums:
			album_art_id = album["image"][0]["#text"].split("/")[-1].split(".")[0]
			if album_art_id.strip() == "":
				continue

			albums.add(album_art_id)

		if not albums:
			raise exceptions.Error("There was an unknown error while getting your albums!")

		to_fetch = []
		albumcolors = await self.bot.db.execute(
			"""
			SELECT image_hash, r, g, b FROM image_color_cache WHERE image_hash IN %s
			""",
			tuple(albums),
		)
		albumcolors_dict = {}
		for image_hash, r, g, b in albumcolors:
			albumcolors_dict[image_hash] = (r, g, b)
		warn = None

		async with aiohttp.ClientSession() as session:
			for image_id in albums:
				color = albumcolors_dict.get(image_id)
				if color is None:
					to_fetch.append(image_id)
				else:
					album_color_nodes.append(AlbumColorNode(color, image_id))

			if to_fetch:
				to_cache = []
				tasks = []
				for image_id in to_fetch:
					tasks.append(self.fetch_color(session, image_id))

				if len(tasks) > 500:
					warn = await ctx.send(
						":exclamation:Your library includes over 500 uncached album colours, "
						f"this might take a while {emojis.LOADING}"
					)

				colordata = await asyncio.gather(*tasks)
				for colortuple in colordata:
					if colortuple is None:
						continue
					image_hash, r, g, b, hexcolor = colortuple
					to_cache.append((image_hash, r, g, b, hexcolor))
					album_color_nodes.append(AlbumColorNode((r, g, b), image_hash))

				await self.bot.db.executemany(
					"INSERT IGNORE image_color_cache (image_hash, r, g, b, hex) VALUES (%s, %s, %s, %s, %s)",
					to_cache,
				)

			if rainbow:
				if diagonal:
					rainbow_colors = [
						(255, 79, 0),
						(255, 33, 0),
						(217, 29, 82),
						(151, 27, 147),
						(81, 35, 205),
						(0, 48, 255),
						(0, 147, 147),
						(0, 249, 0),
						(203, 250, 0),
						(255, 251, 0),
						(255, 200, 0),
						(255, 148, 0),
					]
				else:
					rainbow_colors = [
						(255, 0, 0),  # red
						(255, 127, 0),  # orange
						(255, 255, 0),  # yellow
						(0, 255, 0),  # green
						(0, 0, 255),  # blue
						(75, 0, 130),  # purple
						(148, 0, 211),  # violet
					]

				chunks = []
				tree = kdtree.create(album_color_nodes)
				for rgb in rainbow_colors:
					chunks.append(list(tree.search_knn(rgb, width + height)))

				random_offset = random.randint(0, 6)
				final_albums = []
				for album_index in range(width * height):
					if diagonal:
						choice_index = (
							album_index % width + (album_index // height) + random_offset
						) % len(chunks)
					else:
						choice_index = album_index % width

					choose_from = chunks[choice_index]
					choice = choose_from[album_index // height]
					final_albums.append(
						(
							self.cover_base_urls[3].format(choice[0].data.data),
							f"rgb{choice[0].data.rgb}, dist {choice[1]:.2f}",
						)
					)

			else:
				tree = kdtree.create(album_color_nodes)
				nearest = tree.search_knn(query_color, width * height)

				final_albums = [
					(
						self.cover_base_urls[3].format(alb[0].data.data),
						f"rgb{alb[0].data.rgb}, dist {alb[1]:.2f}",
					)
					for alb in nearest
				]

		buffer = await self.chart_factory(final_albums, width, height, show_labels=False)

		if rainbow:
			colour = f"{'diagonal ' if diagonal else ''}rainbow"

		await ctx.send(
			f"`{util.displayname(ctx.usertarget)} {colour} album chart"
			+ (f" | {len(to_fetch)} new`" if to_fetch else "`"),
			file=discord.File(
				fp=buffer,
				filename=f"fmcolorchart_{ctx.username}_{str(colour).strip('#').replace(' ', '_')}.jpeg",
			),
		)

		if warn is not None:
			await warn.delete()

	@fm.command(name="chart",aliases=["collage"], brief="[album | artist] [timeframe] [size] 'notitle'", description='Collage of your top albums or artists',usage="```Swift\nSyntax: !lf chart [album | artist] [timeframe] [width]x[height] [notitle]\nExample: !lf chart xxxtentacion alltime / !lf chart alltime```")
	async def aaaachart(self, ctx: commands.Context, *args):
		await username_to_ctx(ctx)
		arguments = parse_chart_arguments(args)
		if arguments["width"] + arguments["height"] > 30:
			raise exceptions.Info(
				"Size is too big! Chart `width` + `height` total must not exceed `30`"
			)

		if arguments["period"] == "today":
			data = await self.custom_period(ctx.username, arguments["method"])
		else:
			data = await self.api_request(
				{
					"user": ctx.username,
					"method": arguments["method"],
					"period": arguments["period"],
					"limit": arguments["amount"],
				}
			)
		chart = []
		chart_type = "ERROR"
		if arguments["method"] == "user.gettopalbums":
			chart_type = "top album"
			albums = data["topalbums"]["album"]
			for album in albums:
				name = album["name"]
				artist = album["artist"]["name"]
				plays = album["playcount"]
				chart.append(
					(
						album["image"][3]["#text"],
						f"{plays} {format_plays(plays)}<br>" f"{name} — {artist}",
					)
				)

		elif arguments["method"] == "user.gettopartists":
			chart_type = "top artist"
			artists = data["topartists"]["artist"]
			scraped_images = await scrape_artists_for_chart(
				ctx.username, arguments["period"], arguments["amount"]
			)
			for i, artist in enumerate(artists):
				name = artist["name"]
				plays = artist["playcount"]
				chart.append((scraped_images[i], f"{plays} {format_plays(plays)}<br>{name}"))

		elif arguments["method"] == "user.getrecenttracks":
			chart_type = "recent tracks"
			tracks = data["recenttracks"]["track"]
			for track in tracks:
				name = track["name"]
				artist = track["artist"]["#text"]
				chart.append((track["image"][3]["#text"], f"{name} — {artist}"))

		buffer = await self.chart_factory(
			chart,
			arguments["width"],
			arguments["height"],
			show_labels=arguments["showtitles"],
		)

		await ctx.send(
			f"`{util.displayname(ctx.usertarget, escape=False)}'s {humanized_period(arguments['period'])} "
			f"{arguments['width']}x{arguments['height']} {chart_type} chart`",
			file=discord.File(
				fp=buffer, filename=f"fmchart_{ctx.username}_{arguments['period']}.jpeg"
			),
		)

	@commands.command(name='nowplaying', aliases=["np"], description='Show Current LastFM Scrobble', brief='member[optional]')
	@commands.guild_only()
	async def nowplaying(self, ctx):
		await username_to_ctx(ctx)
		data = await self.api_request(
			{"user": ctx.username, "method": "user.getrecenttracks", "limit": 1}
		)

		tracks = data["recenttracks"]["track"]

		if not tracks:
			raise exceptions.Info("You have not listened to anything yet!")

		udata = await self.api_request(
			{"user": ctx.username, "method": "user.getinfo"}, ignore_errors=True
		)
		if udata is None:
			return None

		ign = udata["user"]["name"]
		pcc = udata["user"]["playcount"]
		dd=[]

		artist = tracks[0]["artist"]["#text"]
		album = tracks[0]["album"]["#text"]
		albumurl=tracks[0]['url']
		track = tracks[0]["name"]
		album_play=await self.get_playcount_album(artist, album, ctx.username, ctx.usertarget)
		track_play=await self.get_playcount_track(artist, track, ctx.username, ctx.usertarget)
		artist_play=await self.get_playcount(artist, ctx.username, ctx.usertarget)
		artist_plays=str(artist_play[0])
		if not artist_plays:
			artist_plays="0"
		album_plays=str(album_play[0])
		if not album_plays:
			album_plays="0"
		track_plays=str(track_play[0])
		if not track_plays:
			track_plays="0"
		image_url = tracks[0]["image"][-1]["#text"]
		url = tracks[0]["url"]
		trackurl=url or "https://last.fm"
		artistt=artist.replace(" ", "+")
		arturl=f"https://www.last.fm/music/{artistt}"
		content = discord.Embed()
		content.colour = await self.cached_image_color(image_url)
		#content.description = f"🎵 **{util.escape_md(album)}**"
		content.add_field(name="**Track**", value=f"[{util.escape_md(track)}]({trackurl})")
		content.add_field(name="**Artist**", value=f"[{util.escape_md(artist)}]({arturl})")
		#content.description = f"🎵 **{util.escape_md(album)}**"
		#content.title = f"**{util.escape_md(artist)} — *{util.escape_md(track)}* **"
		content.set_thumbnail(url=image_url)


		# tags and playcount
		trackdata = await self.api_request(
			{"user": ctx.username, "method": "track.getInfo", "artist": artist, "track": track},
			ignore_errors=True,
		)
		if trackdata is not None:
			tags = []
			try:
				trackdata = trackdata["track"]
				playcount = int(trackdata["userplaycount"])
				if playcount > 0:
					pc=f"{playcount} {format_plays(playcount)}"
					pccc=playcount
				else:
					pc="0"
					pccc="0"
				for tag in trackdata["toptags"]["tag"]:
					tags.append(tag["name"])
					taglist=", ".join(tags)
					dd.append(taglist)
				#content.set_footer(text=", ".join(tags))
				content.set_footer(text=f"Playcount: {pc} ・ Scrobbles: {pcc} ・ Album: {util.escape_md(album)}")
			except (KeyError, TypeError):
				pass

		# play state
		np = "@attr" in tracks[0] and "nowplaying" in tracks[0]["@attr"]
		state = " > Now Playing" if np else "'s Last track"
		if not np:
			content.timestamp = arrow.get(int(tracks[0]["date"]["uts"])).datetime
		if ctx.usertarget.id == 956618986110476318:
			content.set_author(
				name=f"{util.displayname(ctx.usertarget, escape=False)}{state}",
				icon_url=ctx.usertarget.display_avatar,
			)
		else:
			content.set_author(
				name=f"Last.fm: {ctx.username}",
				icon_url=ctx.usertarget.display_avatar,
			)

		#msg=await self.bot.db.execute("""SELECT message FROM last_fm_embed WHERE user_id = %s""", ctx.author.id, one_value=True)
		if ctx.author.id in self.bot.cache.lastfm_embeds:
			msg=self.bot.cache.lastfm_embeds[int(ctx.usertarget.id)]
		else:
			msg=None
		if msg:
			if msg.startswith("{embed}"):
				try:
				# if msg:
					msg=msg.replace('{artist}', util.escape_md(artist))
					msg=msg.replace("{playcount}", f"{pc.strip(' plays')}")
					msg=msg.replace("{user}", util.displayname(ctx.usertarget, escape=False))
					msg=msg.replace('{avatar}', f'{ctx.usertarget.display_avatar}')
					msg=msg.replace("{track.url}", trackurl)
					msg=msg.replace("{artist.url}", arturl)
					msg=msg.replace("{album.plays}", str(album_plays))
					msg=msg.replace("{track.plays}", str(track_plays))
					msg=msg.replace("{artist.plays}",str(artist_plays))
					track=track.replace("_", r'\\_')
					msg=msg.replace("{track.lower}", str(track).lower())
					msg=msg.replace("{artist.lower}", str(artist).lower())
					msg=msg.replace("{album.lower}", str(album).lower())
					msg=msg.replace("{track.hyper.lower}", f"[{str(track).lower()}]({trackurl})")
					msg=msg.replace("{artist.hyper.lower}", f"[{str(artist).lower()}]({arturl})")
					msg=msg.replace("{album.hyper.lower}",f"[{str(album).lower()}]({albumurl})")
					msg=msg.replace("{album.hyper}",f"[{str(album)}]({albumurl})")
					msg=msg.replace("{track.hyper}", f"[{util.escape_md(track)}]({trackurl})")
					msg=msg.replace("{artist.hyper}", f"[{util.escape_md(artist)}]({arturl})")
					if dd:
						msg=msg.replace("{tags}", dd[0])
					msg=msg.replace("{scrobbles}", f"{pcc}")
					msg=msg.replace("{track.color}", f"{await self.cached_image_color(image_url)}")
					msg=msg.replace("{track.image}", image_url)
					msg=msg.replace("{album}", util.escape_md(album))
					msg=msg.replace("{lastfm.user}", f'{ctx.username}')
					sg=msg.replace("{state}", state)
					msg=msg.replace("{track}", util.escape_md(track))
					params=await util.embed_replacement(ctx.author,ctx.guild,msg)
					message = await util.to_embed(ctx.channel,ctx.author,ctx.guild,params)
				except Exception as e:
					await ctx.send(e)
			else:
				try:
					if "$(artist)" in msg:
						msg=msg.replace('$(artist)', util.escape_md(artist))

					if "$(playcount)" in msg:
						msg=msg.replace("$(playcount)", pc.strip(" plays"))
					if "$(user)" in msg:
						msg=msg.replace("$(user)", util.displayname(ctx.usertarget, escape=False))
					if "$(avatar)" in msg:
						msg=msg.replace('$(avatar)', f'{ctx.usertarget.display_avatar}')
					if "$(track.url)" in msg:
						msg=msg.replace("$(track.url)", trackurl)
					if "$(artist.url)" in msg:
						msg=msg.replace("$(artist.url)", arturl)
					if "$(track.lower)" in msg:
						if "_" in track:
							track=track.replace("_", r'\\_')
						msg=msg.replace("$(track)", str(track).lower())
					if "$(artist.lower)" in msg:
						msg=msg.replace('$(artist)', str(artist).lower())
					if "$(track.hyper.lower)" in msg:
						msg=msg.replace("$(track.hyper.lower)", f"[{str(track).lower()}]({trackurl})")
					if "$(artist.hyper.lower)" in msg:
						msg=msg.replace("$(artist.hyper.lower)", f"[{str(artist).lower()}]({arturl})")
					if "$(track.hyper)" in msg:
						msg=msg.replace("$(track.hyper)", f"[{util.escape_md(track)}]({trackurl})")
					if "$(artist.hyper)" in msg:
						msg=msg.replace("$(artist.hyper)", f"[{util.escape_md(artist)}]({arturl})")
					if "$(tags)" in msg:
						msg=msg.replace("$(tags)", taglist)
					if "$(scrobbles)" in msg:
						msg=msg.replace("$(scrobbles)", pcc)
					if "$(track.color)" in msg:
						msg=msg.replace("$(track.color)", await self.cached_image_color(image_url))
					if "$(track.image)" in msg:
						msg=msg.replace("$(track.image)", image_url)
					if "$(album)" in msg:
						msg=msg.replace("$(album)", util.escape_md(album))
					if "$(lastfm.user)" in msg:
						msg=msg.replace("$(lastfm.user)", ctx.username)
					if "$(state)" in msg:
						msg=msg.replace("$(state)", state)
					if "$(track)" in msg:
						msg=msg.replace("$(track)", util.escape_md(track))
					if "$(" in msg:
							try:
								jd=[]
								kd=[]
								jd=msg.split("$")
								for jd in jd:
									result = jd[jd.find('(')+1:jd.find(')')]
									kd.append(result)
								kd.pop(0)
								for kd in kd:
									msg=msg.replace(f"$({kd})", f"{eval(kd)}")
							except:
								pass
					embed_dict = self._get_embed_from_json(ctx.channel,msg)
					message=await Message.Embed(**embed_dict).send(ctx)
				except Exception as e:
					try:
						if "$(track)" in msg:
							if "_" in track:
								track=track.replace("_", r'\\_')
							msg=msg.replace("$(track)", track)
						if "$(artist)" in msg:
							msg=msg.replace('$(artist)', artist)
						if "$(track.lower)" in msg:
							if "_" in track:
								track=track.replace("_", r'\\_')
							msg=msg.replace("$(track)", str(track).lower())
						if "$(artist.lower)" in msg:
							msg=msg.replace('$(artist)', str(artist).lower())
						if "$(track.hyper)" in msg:
							msg=msg.replace("$(track.hyper)", f"[{track}]({trackurl})")
						if "$(track.hyper.lower)" in msg:
							msg=msg.replace("$(track.hyper.lower)", f"[{str(track).lower()}]({trackurl})")
						if "$(artist.hyper.lower)" in msg:
							msg=msg.replace("$(artist.hyper.lower)", f"[{str(artist).lower()}]({arturl})")
						if "$(artist.hyper)" in msg:
							msg=msg.replace("$(artist.hyper)", f"[{artist}]({arturl})")
						if "$(playcount)" in msg:
							msg=msg.replace("$(playcount)", pc.strip(" plays"))
						if "$(user)" in msg:
							msg=msg.replace("$(user)", util.displayname(ctx.usertarget, escape=False))
						if "$(avatar)" in msg:
							msg=msg.replace('$(avatar)', f'{ctx.usertarget.display_avatar}')
						if "$(track.url)" in msg:
							msg=msg.replace("$(track.url)", trackurl)
						if "$(artist.url)" in msg:
							msg=msg.replace("$(artist.url)", arturl)
						if "$(tags)" in msg:
							msg=msg.replace("$(tags)", taglist)
						if "$(scrobbles)" in msg:
							msg=msg.replace("$(scrobbles)", pcc)
						if "$(track.color)" in msg:
							msg=msg.replace("$(track.color)", await self.cached_image_color(image_url))
						if "$(track.image)" in msg:
							msg=msg.replace("$(track.image)", image_url)
						if "$(album)" in msg:
							msg=msg.replace("$(album)", util.escape_md(album))
						if "$(lastfm.user)" in msg:
							msg=msg.replace("$(lastfm.user)", ctx.username)
						if "$(state)" in msg:
							msg=msg.replace("$(state)", state)
						if "$(" in msg:
							try:
								jd=[]
								kd=[]
								jd=msg.split("$")
								for jd in jd:
									result = jd[jd.find('(')+1:jd.find(')')]
									kd.append(result)
								kd.pop(0)
								for kd in kd:
									msg=msg.replace(f"$({kd})", f"{eval(kd)}")
							except:
								pass
						embed_dict = self._get_embed_from_json(ctx.channel,msg)
						message=await Message.Embed(**embed_dict).send(ctx)
					except Exception as e:
						message=await ctx.send(embed=content)
		if not msg:
			message = await ctx.send(embed=content)
		voting_settings = await ctx.bot.db.execute(
			"""
			SELECT is_enabled, upvote_emoji, downvote_emoji
			FROM lastfm_vote_setting WHERE user_id = %s
			""",
			ctx.author.id,
			one_row=True,
		)
		if voting_settings:
			(voting_mode, upvote, downvote) = voting_settings
			if voting_mode:
				if upvote:
					if upvote.startswith("<"): 
						await message.add_reaction(upvote)
					else:
						await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(upvote))
				else:
					await message.add_reaction("🔥")
				if downvote:
					if downvote.startswith("<"): 
						await message.add_reaction(downvote)
					else:
						await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(downvote))
				else:
					await message.add_reaction("🗑️")
		else:
			await message.add_reaction("🔥")
			await message.add_reaction("🗑️")


	@commands.command(aliases=["wkt", "whomstknowstrack"], description='Who has listened to a given song the most', usage="```Swift\nSyntax: !whoknowstrack <track name> | <artist name>\nExample: !whoknowstrack np```",brief='track')
	@commands.guild_only()
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	async def whoknowstrack(self, ctx, *, track=None):
		await username_to_ctx(ctx)
		try:
			track = remove_mentions(track)
		except:
			pass

		if track is None:
			npd = await self.getnowplaying(ctx)
			trackname = npd["track"]
			artistname = npd["artist"]
		else:
			try:
				trackname, artistname = [x.strip() for x in track.split("|")]
				if "" in (trackname, artistname):
					raise ValueError
			except ValueError:
				raise exceptions.Warning("Incorrect format! use `track | artist`")

		listeners = []
		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_playcount_track(artistname, trackname, lastfm_username, member))

		if tasks:
			data = await asyncio.gather(*tasks)
			for playcount, user, metadata, username in data:
				artistname, trackname, image_url = metadata
				if playcount > 0:
					listeners.append((playcount, user, username))
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		artistname = util.escape_md(artistname)
		trackname = util.escape_md(trackname)

		rows = []
		total = 0
		for i, (playcount, user, username) in enumerate(
			sorted(listeners, key=lambda p: p[0], reverse=True), start=1
		):
			rows.append(
				f"`{i}` **[{util.displayname(user)}](https://last.fm/{username})** has **{playcount}** {format_plays(playcount)}"
			)
			total += playcount

		if not rows:
			return await ctx.send(
				f"Nobody on this server has listened to **{trackname}** by **{artistname}**"
			)

		if image_url is None:
			image_url = await self.get_artist_image(artistname)

		content = discord.Embed(title=f"Top Listeners for track {trackname}").set_author(name=ctx.author.display_name,icon_url=ctx.author.display_avatar.url)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Collective plays: {total}")

		content.colour = await self.cached_image_color(image_url)

		await util.send_as_pages(ctx, content, rows)

	@commands.command(aliases=["wka", "whomstknowsalbum"], description='Who has listened to a given album the most', usage="```Swift\nSyntax: !whoknowsalbum <album name> | <artist name>\nExample: !whoknowsalbum np```",brief='album')
	@commands.guild_only()
	@commands.cooldown(2, 5, type=commands.BucketType.user)
	async def whoknowsalbum(self, ctx, *, album="np"):
		if album is None:
			npd = await self.getnowplaying(ctx)
			albumname = npd["album"]
			artistname = npd["artist"]

		try:
			album = remove_mentions(album)
		except:
			album=album
		if album.lower() == "np":
			npd = await self.getnowplaying(ctx)
			albumname = npd["album"]
			artistname = npd["artist"]
			if None in [albumname, artistname]:
				raise exceptions.Warning("Could not get currently playing album!")
		else:
			try:
				albumname, artistname = [x.strip() for x in album.split("|")]
				if "" in (albumname, artistname):
					raise ValueError
			except ValueError:
				raise exceptions.Warning("Incorrect format! use `album | artist`")

		listeners = []
		tasks = []
		for user_id, lastfm_username in await self.server_lastfm_usernames(
			ctx, filter_cheaters=True
		):
			member = ctx.guild.get_member(user_id)
			if member is None:
				continue

			tasks.append(self.get_playcount_album(artistname, albumname, lastfm_username, member))

		if tasks:
			data = await asyncio.gather(*tasks)
			for playcount, user, metadata, username in data:
				artistname, albumname, image_url = metadata
				if playcount > 0:
					listeners.append((playcount, user, username))
		else:
			return await ctx.send("Nobody on this server has connected their last.fm account yet!")

		artistname = util.escape_md(artistname)
		albumname = util.escape_md(albumname)

		rows = []
		total = 0
		for i, (playcount, user, username) in enumerate(
			sorted(listeners, key=lambda p: p[0], reverse=True), start=1
		):
			rows.append(
				f"`{i}` **[{util.displayname(user)}](https://last.fm/{username})** has **{playcount}** {format_plays(playcount)}"
			)
			total += playcount

		if not rows:
			return await ctx.send(
				f"Nobody on this server has listened to **{albumname}** by **{artistname}**"
			)

		if image_url is None:
			image_url = await self.get_artist_image(artistname)

		content = discord.Embed(title=f"Top Listeners for album {albumname}").set_author(name=ctx.author.display_name,icon_url=ctx.author.display_avatar.url)
		content.set_thumbnail(url=image_url)
		content.set_footer(text=f"Collective plays: {total}")

		content.colour = await self.cached_image_color(image_url)

		await util.send_as_pages(ctx, content, rows)

	@commands.command(description='check your artist crowns', usage="```Swift\nSyntax: !crowns <member>\nExample: !crowns @cop#0001```",brief='member')
	@commands.guild_only()
	async def crowns(self, ctx, *, user: discord.Member = None):
		if user is None:
			user = ctx.author

		crownartists = await self.bot.db.execute(
			"""
			SELECT artist_name, cached_playcount FROM artist_crown
			WHERE guild_id = %s AND user_id = %s ORDER BY cached_playcount DESC
			""",
			ctx.guild.id,
			user.id,
		)
		if not crownartists:
			return await ctx.send(
				"You haven't acquired any crowns yet! "
				"Use the `!whoknows` command to claim crowns of your favourite artists :crown:"
			)

		rows = []
		for artist, playcount in crownartists:
			artistt=artist.replace(" ", "+")
			arturl=f"https://www.last.fm/music/{artistt}"
			rows.append(
				f"[{util.escape_md(str(artist))}]({arturl}) ({playcount} {format_plays(playcount)})"
			)

		content = discord.Embed(color=discord.Color.gold())
		content.set_author(
			name=f"👑 {util.displayname(user, escape=False)} artist crowns",
			icon_url=user.display_avatar.url,
		)
		content.set_footer(text=f"Total {len(crownartists)} crowns")
		await util.send_as_pages(ctx, content, rows)

	@commands.command(hidden=True, disabled=True)
	async def report(self, ctx, lastfm_username, *, reason):
		lastfm_username = lastfm_username.strip("/").split("/")[-1].lower()
		url = f"https://www.last.fm/user/{lastfm_username}"
		data = await self.api_request(
			{"user": lastfm_username, "method": "user.getinfo"}, ignore_errors=True
		)
		if data is None:
			raise exceptions.Warning(f"`{url}` is not a valid Last.fm profile.")

		exists = await self.bot.db.execute(
			"SELECT * FROM lastfm_cheater WHERE lastfm_username = %s", lastfm_username.lower()
		)
		if exists:
			raise exceptions.Info("This Last.fm account is already flagged")

		content = discord.Embed(title="New Last.fm user report")
		content.add_field(name="Profile", value=url)
		content.add_field(name="Reason", value=reason)

		content.description = (
			"Are you sure you want to report this lastfm account?"
			" Please note sending false reports or spamming **will get you blacklisted**."
		)

		# send confirmation message
		msg = await ctx.send(embed=content)

		async def confirm_ban():
			content.add_field(
				name="Reported by",
				value=f"{ctx.author} (`{ctx.author.id}`)",
				inline=False,
			)
			user_ids = await self.bot.db.execute(
				"SELECT user_id FROM user_settings WHERE lastfm_username = %s", lastfm_username
			)
			if user_ids:
				connected_accounts = []
				for x in user_ids:
					user = self.bot.get_user(x[0])
					connected_accounts.append(f"{user} (`{user.id}`)")

				content.add_field(
					name="Connected by",
					value=", ".join(connected_accounts),
					inline=False,
				)
			content.set_footer(text=f">fmflag {lastfm_username} [reason]")
			content.description = ""

			await self.send_report(ctx, content, lastfm_username, reason)
			await msg.edit(content="📨 Report sent!", embed=None)

		async def cancel_ban():
			await msg.edit(content="❌ Report cancelled.", embed=None)

		functions = {"✅": confirm_ban, "❌": cancel_ban}

		asyncio.ensure_future(
			util.reaction_buttons(ctx, msg, functions, only_author=True, single_use=True)
		)

	async def send_report(self, ctx, content, lastfm_username, reason=None):
		reports_channel = self.bot.get_channel(729736304677486723)
		if reports_channel is None:
			raise exceptions.Warning("Something went wrong.")

		msg = await reports_channel.send(embed=content)

		async def confirm_ban():
			await self.bot.db.execute(
				"INSERT INTO lastfm_cheater VALUES(%s, %s, %s)",
				lastfm_username.lower(),
				arrow.utcnow().datetime,
				reason,
			)
			content.description = "Account flagged"
			content.color = discord.Color.green()
			await msg.edit(embed=content)

		async def cancel_ban():
			content.description = "Report ignored"
			content.color = discord.Color.red()
			await msg.edit(embed=content)

		functions = {"✅": confirm_ban, "❌": cancel_ban}

		asyncio.ensure_future(
			util.reaction_buttons(ctx, msg, functions, single_use=True, only_owner=True)
		)

	@commands.hybrid_command(name='userinfo',aliases=['ui', 'whois'], with_app_command=True, usage="```Swift\nSyntax: !userinfo <mention/id>\nExample: !userinfo @cop#0001```",description="show a discord account's stats", brief='member/user')
	@commands.guild_only()
	async def userinfo(self, ctx, member: Union[discord.Member, discord.User] = None):
		publicFlags = deque()
		blink=""
		if member is None:
			member = ctx.author
		if not member:
			if self.bot.get_user(member) != None:
				member=self.bot.get_user(member)
			else:
				member=await self.bot.fetch_user(member)
		user=member
		sunsign = await self.bot.db.execute("SELECT sunsign FROM user_settings WHERE user_id = %s", member.id, one_value=True)
		if sunsign:
			sign = self.hs.get(sunsign)
			badge=sign['emoji']
		else:
			badge=""
		if member in ctx.guild.members:
			emote=[]
			if member.voice:
				voice=member.voice.channel
				#emote=""
				number=len(voice.members)
				if member.voice.self_mute:
					emote.append("<:muted:1005611745605328906>")
				else:
					emote.append("<:unmuted:1005611744166690816>")
				if member.voice.self_deaf:
					emote.append("<:deafened:986615855418839050>")
				else:
					emote.append("<:undeafened:1005611742983888906>")
				if member.voice.self_stream:
					emote.append("<:stream:1004112343275409429>")
				if member.voice.self_video:
					emote.append("<:video:1004112681680252969>")
				emotes="".join([emote for emote in emote])
				if number > 0:
					n=number-1
					v=f" with {n} others"
				else:
					v=" "
				vc=f"\n**{emotes} in voice chat:** {voice.name}{v}"
			else:
				vc=""
		else:
			vc=""
		try:
			ctx.username = await ctx.bot.db.execute("SELECT lastfm_username FROM user_settings WHERE user_id = %s", member.id, one_value=True)
			data = await self.api_request(
			{"user": ctx.username, "method": "user.getrecenttracks", "limit": 1}
			)
			tracks = data["recenttracks"]["track"]
			lfmemote="<:lfm:945412052074242139>"
			if not tracks:
				raise exceptions.Info("You have not listened to anything yet!")
			artist = tracks[0]["artist"]["#text"]
			album = tracks[0]["album"]["#text"]
			track = tracks[0]["name"]
			image_url = tracks[0]["image"][-1]["#text"]
			randomascii="—"
			nowplaying=tracks[0]["@attr"]
			if nowplaying:
				np = f"\n{lfmemote} Listening to **[{util.escape_md(track)}](https://last.fm/)** by **{util.escape_md(artist)}**"
		except:
			np=""
		prem=0
		if user.id == ctx.guild.owner.id:
			publicFlags.append(" <:owner:918635065758605372>")
		if user.public_flags.hypesquad_balance:
			publicFlags.append(" <:x_HypeSquadBalance:1006308099344318585>")
		if user.public_flags.hypesquad_bravery:
			publicFlags.append(" <:x_HypeSquadBravery:1006308109817483388>")
		if user.public_flags.hypesquad_brilliance:
			publicFlags.append(" <:x_HypeSquadBrilliance:1006308111616856155>")
		if user.bot:
			publicFlags.append(" <:bot_tag:932050216964718602>")
		if user.public_flags.partner:
			publicFlags.append(" <:x_NewPartner:1006308115077157035>")
		if user.public_flags.hypesquad:
			publicFlags.append(" <:x_HypeSquadEvents:1006308105929363457>")
		if user.public_flags.early_supporter:
			publicFlags.append(" <:x_EarlySupporter:1006308364432719913>")
		if user.public_flags.bug_hunter:
			publicFlags.append(" <:bughunter:943944180948959233>")
		if user.public_flags.verified_bot:
			publicFlags.append(" <:DBE_verifiedbot:1006308103853191329>")
		if user.public_flags.verified_bot_developer:
			publicFlags.append(" <:DBE_EarlyVerifiedBotDeveloper:1006308097893076992>")
		if user.public_flags.discord_certified_moderator:
			publicFlags.append(" <:CertifiedModerator:934765761803718656>")
		if user.public_flags.bug_hunter_level_2:
			publicFlags.append(" <:DBE_BugHunterTier2:929519765473599499>")
		if user.public_flags.staff:
			publicFlags.append("<:DBE_DiscordStaff:1006308108412399698>")
		try:
			#r=await self.bot.session.get(f"http://127.0.0.1:6969/lookup?id={member.id}&key=adminrivalkey1337")
			#p=await r.json(content_type=None)
			p=await self.badges(member.id)
		except Exception as e:
			print(e)
			await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warn} {ctx.author.mention}: The webserver is down please report this to our developer"))
		if p:
			if p.get("data"):
				profile=p['data']
				if profile.get('bannerURL'):
					blink=f"[Banner]({profile['bannerURL']}?size=512)"
				tag=profile['tag']
				flags=profile.get('public_flags_array')
				if flags and not profile.get('message') == "Unknown User" and flags != None:
					if "NITRO" in flags:
						publicFlags.append("<:x_Nitro:1006308389795672164>")
					if "BOOSTER_1" in flags:
						publicFlags.append('<a:0_boost1:921806963359252480>')
					elif "BOOSTER_2" in flags:
						publicFlags.append('<a:0_boost2:921806992799055932>')
					elif "BOOSTER_3" in flags:
						publicFlags.append('<a:0_boost3:921807005591670856>')
					elif "BOOSTER_6" in flags:
						publicFlags.append('<a:0_boost6:921807011874766958>')
					elif "BOOSTER_9" in flags:
						publicFlags.append('<a:0_boost9:921807018308821042>')
					elif "BOOSTER_12" in flags:
						publicFlags.append('<a:0_boost12:921806969990434898>')
					elif "BOOSTER_15" in flags:
						publicFlags.append('<a:0_boost15:921806976822956032> ')
					elif "BOOSTER_18" in flags:
						publicFlags.append('<a:0_boost18:921806985022803968>')
					elif "BOOSTER_21" in flags:
						publicFlags.append('<a:0_boost2:921806992799055932>')
					elif "BOOSTER_24" in flags:
						publicFlags.append('<a:0_boost24:921806999077924884>')
				else:
					discrims=['0001', '0002', '9999', '0666', '6666', '7777', '8888', '6900', '0069', '1337']
					if member.discriminator in discrims:
						if not "<:x_Nitro:1006308389795672164>" in publicFlags:
							publicFlags.append("<:x_Nitro:1006308389795672164>")
					if member.avatar:
						if member.avatar.is_animated():
							if not "<:x_Nitro:1006308389795672164>" in publicFlags:
								publicFlags.append("<:x_Nitro:1006308389795672164>")
					if user.banner:
						if not "<:x_Nitro:1006308389795672164>" in publicFlags:
							publicFlags.append("<:x_Nitro:1006308389795672164>")
		bb=' '.join(p for p in publicFlags)
		if not "<:x_Nitro:1006308389795672164>" in publicFlags:
			if user.banner:
				if not "<:x_Nitro:1006308389795672164>" in publicFlags:
					publicFlags.append("<:x_Nitro:1006308389795672164>")
			if member.display_avatar.is_animated():
				if not "<:x_Nitro:1006308389795672164>" in publicFlags:
					publicFlags.append("<:x_Nitro:1006308389795672164>")
		s=[]
		if "boost" not in bb.lower():
			try:	
				for g in member.mutual_guilds:
					if member in g.premium_subscribers:
						u=g.get_member(member.id)
						s.append(u.premium_since)
			except Exception as e:
				print(e)
				pass
		booster_flags=['<:DBE_1MonthsServerBoosting:1006308031421755592>','<a:0_boost2:921806992799055932>','<a:0_boost3:921807005591670856>','<a:0_boost6:921807011874766958>','<a:0_boost9:921807018308821042>','<a:0_boost12:921806969990434898>','<a:0_boost15:921806976822956032>','<a:0_boost18:921806985022803968>','<a:0_boost2:921806992799055932>','<a:0_boost24:921806999077924884>']
		try:
			if s:
				s.sort()
				if s[0] < await util.datetime_delta(2):
					publicFlags.append('<a:0_boost2:921806992799055932>')
				elif s[0] < await util.datetime_delta(3):
					publicFlags.append('<a:0_boost3:921807005591670856>')
				elif s[0] < await util.datetime_delta(6):
					publicFlags.append('<a:0_boost6:921807011874766958>')
				elif s[0] < await util.datetime_delta(9):
					publicFlags.append('<a:0_boost9:921807018308821042>')
				elif s[0] < await util.datetime_delta(12):
					publicFlags.append('<a:0_boost12:921806969990434898>')
				elif s[0] < await util.datetime_delta(15):
					publicFlags.append('<a:0_boost15:921806976822956032>')
				elif s[0] < await util.datetime_delta(18):
					publicFlags.append('<a:0_boost18:921806985022803968>')
				elif s[0] < await util.datetime_delta(21):
					publicFlags.append('<a:0_boost2:921806992799055932>')
				elif s[0] < await util.datetime_delta(24):
					publicFlags.append('<a:0_boost24:921806999077924884>')
				else:
					if not "<:DBE_1MonthsServerBoosting:1006308031421755592>" in publicFlags:
						publicFlags.append('<:DBE_1MonthsServerBoosting:1006308031421755592>')
		except Exception as e:
			print(e)
			pass


		# async with aiohttp.ClientSession(headers=headers) as session:
		# 	async with session.get(f"https://discord.com/api/v10/users/{user.id}") as res:
		# 		try:
		# 			r = await res.json()
		# 			if not str(r['banner']) == "None":
		# 				if str(r['banner']).startswith("a_"): 
		# 					blink = f"[Banner](https://cdn.discordapp.com/banners/{user.id}/{str(r['banner'])}.gif?size=1024)"
		# 				else:
		# 					blink=f"[Banner](https://images.discordapp.net/banners/{user.id}/{str(r['banner'])}?size=512)"
		# 				if "<:x_Nitro:1006308389795672164> <:DBE_1MonthsServerBoosting:1006308031421755592>" not in publicFlags:
		# 					publicFlags.append("<:x_Nitro:1006308389795672164> <:DBE_1MonthsServerBoosting:1006308031421755592>")
		# 			else:
		# 				blink=""
		# 		except:
		# 			blink=""
		# 			pass
		if await queries.is_donator(ctx, user):
			publicFlags.append("<a:Money:964673324011638784>")
		if user.id in self.bot.owner_ids:
			publicFlags.append(" <a:Verify_red:1006312875243085844>")
		# if member in ctx.guild.members: 
		# 	if "offline" != str(member.mobile_status):
		# 		platform = "📱:"
		# 	if "offline" != str(member.desktop_status):
		# 		platform = "🖥️:"
		# 	if "offline" != str(member.web_status):
		# 		platform = "🌐:"
		# 	else:
		# 		platform = ""
		# 	if member.status.name == "online":
		# 		if member.is_on_mobile() is True:
		# 			statusemoji = " <:mobile:918446884459274240>"
		# 		else:
		# 			statusemoji = consts.statuses.ONLINE
		# 	if member.status.name == "idle":
		# 		statusemoji = consts.statuses.IDLE
		# 	if member.status.name == "dnd":
		# 		statusemoji = consts.statuses.DND
		# 	if member.status.name == "streaming":
		# 		statusemoji = " <:status_streaming:1006312609106100355>"
		# 	if member.status.name == "offline":
		# 		statusemoji=consts.statuses.OFFLINE
		# else:
		# 	statusemoji=consts.statuses.OFFLINE
		if member in ctx.guild.members:
			roles = member.roles[-1:0:-1]
		user = member
		guild = ctx.guild
		user_created = member.created_at.strftime("%d %b %Y")
		since_created = (ctx.message.created_at - user.created_at).days
		createdon = ("{}\n({} days ago)").format(user_created, since_created)
		if member in ctx.guild.members:
			if roles:
				role_str = ", ".join([x.mention for x in roles])
				if len(role_str) > 1024:
					continuation_string = (
						"***and {numeric_number} more***"
					)
					available_length = 1024 - len(continuation_string)
					role_chunks = []
					remaining_roles = 0
					for r in roles:
						chunk = f"{r.mention}, "
						chunk_size = len(chunk)

						if chunk_size < available_length:
							available_length -= chunk_size
							role_chunks.append(chunk)
						else:
							remaining_roles += 1
					role_chunks.append(continuation_string.format(numeric_number=remaining_roles))
					role_str = "".join(role_chunks)
			else:
				role_str = None
		created_ats = member.created_at.strftime("%m/%d/%Y")
		if member in ctx.guild.members:
			joined_ats = member.joined_at.strftime("%m/%d/%Y at %H:%M")
		if member in ctx.guild.members:
			if member.top_role.name == "@everyone":
				top_role="N/A"
			else:
				top_role=member.top_role.mention
		if member in ctx.guild.members:
			member_number = sum(m.joined_at < member.joined_at for m in ctx.guild.members if m.joined_at is not None)
		key_perms = []
		has_key_perms = True
		if member in ctx.guild.members:
			if member.guild_permissions.administrator:
				key_perms.append("Server Administrator")

			if len(key_perms) == 0:
				has_key_perms = False
		flags = list(member.public_flags.all())
		if member.avatar:
			if member.avatar.is_animated():
				avatar=f"[Avatar]({member.avatar})"
			else:
				avatar=f"[Avatar]({member.avatar})"
		else:
			avatar=f"[Avatar]({member.default_avatar})"
		if member in ctx.guild.members:
			if not member.nick:
				mem=f"{member.name}#{member.discriminator}"
			else:
				mem=f"{member.display_name}"
		else:
			mem=f"{member.name}#{member.discriminator}"
		if vc:
			np=vc
		else:
			np=np
		# if member in ctx.guild.members:
		# 	try:
		# 		if member.activity:
		# 			if member.activity.emoji:
		# 				try:
		# 					emoji=member.activity.emoji.id
		# 					emote=self.bot.get_emoji(emoji)
		# 				except:
		# 					emote=""
		# 			else:
		# 				emote=""
		# 			if member.activity.name:
		# 				name=member.activity.name
		# 			else:
		# 				name=""
		# 			activity=f'{emote}{name}'
		# 	except AttributeError:
		# 		emote=""
		# 		pass

		if member in ctx.guild.members:
			if member.guild_avatar:
				sav=f"\n[Server Avatar]({member.guild_avatar})"
			else:
				sav=""
		else:
			sav=""
		if member in ctx.guild.members:
			if member.is_timed_out():
				timeoutemoji=self.bot.get_emoji(965425026096578560)
				timedout=f"{timeoutemoji}"
			else:
				timedout=""
		else:
			timedout=""
		# try:
		# 	statuses=generate_user_statuses(member)
		# except:
		# 	pass
		em=discord.Embed(description=f"{timedout}**{mem}** ∙ \u200b{''.join(publicFlags)}{badge}{np}", color=user.color).set_author(name=f"""{str(member)} ({member.id})""", icon_url=member.display_avatar.url, url=f"https://discord.com/users/{member.id}/")
		#em.add_field(name="***Created at:***", value=f"<t:{int(created_at)}:R>", inline=True)
		em.add_field(name="**Created**", value=discord.utils.format_dt(member.created_at, style='R'), inline=True)
		# if member in ctx.guild.members: 
		# 	if member.activity:
		# 		activity_display = util.activities_string(member.activities)
		# 		em.add_field(name=f"**Activity** ", value=activity_display)
		# else:
		if user not in ctx.guild.members:
			if user.id != self.bot.user.id:
				em.set_footer(text=f"{len(member.mutual_guilds)} Servers")
		if has_key_perms:   
			kkey_perms = "".join(key_perms)
		if member in ctx.guild.members: 
			#em.add_field(name="**Status**", value=f''.join(f"{consts.statuses.OFFLINE}" if statuses is None else statuses), inline=True)
			if member.premium_since:
				em.add_field(name="**Boosted**", value=discord.utils.format_dt(member.premium_since, style='R'), inline=True)
			#em.add_field(name="***Joined at:***", value=f"<t:{int(joined_at)}:R>", inline=True)
			em.add_field(name="**Joined**", value=discord.utils.format_dt(member.joined_at, style='R'), inline=True)
			em.add_field(name="**Links**", value=f"{avatar}{sav}\n{blink}", inline=True)
			#em.add_field(name=f"**Roles({len(member.roles[-1:0:-1])})**", value=f"{top_role}", inline=False)
			if member.roles:
				if len(member.roles) >= 1:
					role_listed=" ,".join(i.mention for i in member.roles[::-1][:6] if i.is_assignable())
					if len(member.roles) > 6:
						amount=len(member.roles) - 1 - len(role_listed.split(","))
						more=f"+ {amount} more"
					else:
						more=" "
					if role_listed:
						em.add_field(name=f"**Roles**", value=f'{role_listed} {more}', inline=False)
			if has_key_perms:
				em.set_footer(text=f"{kkey_perms} ∙ Join Position: {member_number} ∙ {len(member.mutual_guilds)} Servers")
			else:
				em.set_footer(text=f"Join Position: {member_number} ∙ {len(member.mutual_guilds)} Servers")
		else:
			em.add_field(name="**Links**", value=f"{avatar}{sav}\n{blink}", inline=True)
		em.set_thumbnail(url=member.display_avatar.url)
		await ctx.send(embed=em)

	# @util.donor_server()
	# @commands.command(hidden=True)
	# async def lyrics(self, ctx, *, query):
	# 	"""Search for song lyrics."""
	# 	if query.lower() == "np":
	# 		npd = await self.getnowplaying(ctx)
	# 		trackname = npd["track"]
	# 		artistname = npd["artist"]
	# 		if None in [trackname, artistname]:
	# 			return await ctx.send(":warning: Could not get currently playing track!")
	# 		query = artistname + " " + trackname

	# 	url = "https://api.audd.io/findLyrics/"
	# 	request_data = {
	# 		"api_token": AUDDIO_TOKEN,
	# 		"q": query,
	# 	}
	# 	async with aiohttp.ClientSession() as session:
	# 		async with session.post(url=url, data=request_data) as response:
	# 			data = await response.json()

	# 	if data["status"] != "success":
	# 		raise exceptions.Warning(
	# 			f"Something went wrong! `error {data['error']['error_code']}: {data['error']['error_message']}`"
	# 		)

	# 	results = data["result"]
	# 	if not results:
	# 		return await ctx.send("Found nothing!")

	# 	if len(results) > 1:
	# 		picker_content = discord.Embed(title=f"Search results for `{query}`")
	# 		picker_content.set_author(name="Type number to choose result")
	# 		found_titles = []
	# 		for i, result in enumerate(results, start=1):
	# 			found_titles.append(f"`{i}.` {result['full_title']}")

	# 		picker_content.description = "\n".join(found_titles)
	# 		bot_msg = await ctx.send(embed=picker_content)

	# 		def check(message):
	# 			if message.author == ctx.author and message.channel == ctx.channel:
	# 				try:
	# 					num = int(message.content)
	# 				except ValueError:
	# 					return False
	# 				else:
	# 					return num <= len(results) and num > 0
	# 			else:
	# 				return False

	# 		try:
	# 			msg = await self.bot.wait_for("message", check=check, timeout=60)
	# 		except asyncio.TimeoutError:
	# 			return await ctx.send("number selection timed out")
	# 		else:
	# 			result = results[int(msg.content) - 1]
	# 			await bot_msg.delete()

	# 	else:
	# 		result = results[0]

	# 	rows = html.unescape(result["lyrics"]).split("\n")
	# 	content = discord.Embed(title=result["full_title"])
	# 	await util.send_as_pages(ctx, content, rows, maxrows=20)

	async def cached_image_color(self, image_url):
		"""Get image color, cache if new."""
		image_hash = image_url.split("/")[-1].split(".")[0]
		cached_color = await self.bot.db.execute(
			"SELECT hex FROM image_color_cache WHERE image_hash = %s",
			image_hash,
			one_value=True,
		)
		if cached_color:
			return int(cached_color, 16)
		color = await util.color_from_image_url(image_url, fallback=None, return_color_object=True)
		if color is None:
			return int(self.lastfm_red, 16)

		hex_color = util.rgb_to_hex(color)
		await self.bot.db.execute(
			"INSERT IGNORE image_color_cache (image_hash, r, g, b, hex) VALUES (%s, %s, %s, %s, %s)",
			image_hash,
			color.r,
			color.g,
			color.b,
			hex_color,
		)

		return int(hex_color, 16)

	async def get_userinfo_embed(self, username):
		data = await self.api_request(
			{"user": username, "method": "user.getinfo"}, ignore_errors=True
		)
		if data is None:
			return None

		username = data["user"]["name"]
		blacklisted = await self.bot.db.execute(
			"SELECT * from lastfm_cheater WHERE lastfm_username = %s", username.lower()
		)
		playcount = data["user"]["playcount"]
		profile_url = data["user"]["url"]
		profile_pic_url = data["user"]["image"][3]["#text"]
		timestamp = arrow.get(int(data["user"]["registered"]["unixtime"]))

		content = discord.Embed(
			title=f"{emojis.LASTFM} {username}"
			+ (" `LAST.FM PRO`" if int(data["user"]["subscriber"]) == 1 else "")
		)
		content.add_field(name="Profile", value=f"[Link]({profile_url})", inline=True)
		content.add_field(
			name="Registered",
			value=f"{timestamp.humanize()}\n{timestamp.format('DD/MM/YYYY')}",
			inline=True,
		)
		content.add_field(name="Country", value=data["user"]["country"])
		content.set_thumbnail(url=profile_pic_url)
		content.set_footer(text=f"Total plays: {playcount}")
		content.colour = int(self.lastfm_red, 16)
		if blacklisted:
			content.description = ":warning: `This account is flagged as a cheater`"

		return content

	async def listening_report(self, ctx, timeframe):
		current_day_floor = arrow.utcnow().floor("day")
		week = []
		# for i in range(7, 0, -1):
		for i in range(1, 8):
			dt = current_day_floor.shift(days=-i)
			week.append(
				{
					"dt": dt,
					"ts": dt.timestamp,
					"ts_to": dt.shift(days=+1, minutes=-1).timestamp,
					"day": dt.format("ddd, MMM Do"),
					"scrobbles": 0,
				}
			)

		params = {
			"method": "user.getrecenttracks",
			"user": ctx.username,
			"from": week[-1]["ts"],
			"to": current_day_floor.shift(minutes=-1).timestamp,
			"limit": 1000,
		}
		content = await self.api_request(params)
		tracks = content["recenttracks"]["track"]

		# get rid of nowplaying track if user is currently scrobbling.
		# for some reason even with from and to parameters it appears
		if tracks[0].get("@attr") is not None:
			tracks = tracks[1:]

		day_counter = 1
		for trackdata in reversed(tracks):
			scrobble_ts = int(trackdata["date"]["uts"])
			if scrobble_ts > week[-day_counter]["ts_to"]:
				day_counter += 1

			week[day_counter - 1]["scrobbles"] += 1

		scrobbles_total = sum(day["scrobbles"] for day in week)
		scrobbles_average = round(scrobbles_total / len(week))

		rows = []
		for day in week:
			rows.append(f"`{day['day']}`: **{day['scrobbles']}** Scrobbles")

		content = discord.Embed(color=int(self.lastfm_red, 16))
		content.set_author(
			name=f"{util.displayname(ctx.usertarget, escape=False)} | LAST.{timeframe.upper()}",
			icon_url=ctx.usertarget.display_avatar,
		)
		content.description = "\n".join(rows)
		content.add_field(
			name="Total scrobbles", value=f"{scrobbles_total} Scrobbles", inline=False
		)
		content.add_field(
			name="Avg. daily scrobbles", value=f"{scrobbles_average} Scrobbles", inline=False
		)
		# content.add_field(name="Listening time", value=listening_time)
		await ctx.send(embed=content)

	async def get_artist_image(self, artist):
		image_life = 604800  # 1 week
		cached = await self.bot.db.execute(
			"SELECT image_hash, scrape_date FROM artist_image_cache WHERE artist_name = %s",
			artist,
			one_row=True,
		)

		if cached:
			lifetime = arrow.utcnow().timestamp - cached[1].timestamp()
			if (lifetime) < image_life:
				return self.cover_base_urls[3].format(cached[0])

		image = await scrape_artist_image(artist)
		if image is None:
			return ""
		image_hash = image["src"].split("/")[-1].split(".")[0]
		if image_hash == MISSING_IMAGE_HASH:
			# basic star image, dont save it
			return ""

		await self.bot.db.execute(
			"""
			INSERT INTO artist_image_cache (artist_name, image_hash, scrape_date)
				VALUES (%s, %s, %s)
			ON DUPLICATE KEY UPDATE
				image_hash = VALUES(image_hash),
				scrape_date = VALUES(scrape_date)
			""",
			artist,
			image_hash,
			arrow.now().datetime,
		)
		return self.cover_base_urls[3].format(image_hash)

	async def api_request(self, params, ignore_errors=False):
		"""Get json data from the lastfm api."""
		url = "http://ws.audioscrobbler.com/2.0/"
		params["api_key"] = LASTFM_APPID
		params["format"] = "json"
		tries = 0
		max_tries = 2
		while True:
			async with aiohttp.ClientSession() as session:
				async with session.get(url, params=params) as response:
					self.bot.cache.stats_lastfm_requests += 1
					try:
						content = await response.json(loads=orjson.loads)
					except aiohttp.client_exceptions.ContentTypeError:
						if ignore_errors:
							return None
						text = await response.text()
						raise exceptions.LastFMError(error_code=response.status, message=text)

					if content is None:
						raise exceptions.LastFMError(
							error_code=408,
							message="Could not connect to LastFM",
						)
					if response.status == 200 and content.get("error") is None:
						return content
					if int(content.get("error")) == 8:
						tries += 1
						if tries < max_tries:
							continue

					if ignore_errors:
						return None
					raise exceptions.LastFMError(
						error_code=content.get("error"),
						message=content.get("message"),
					)

	async def custom_period(self, user, group_by, shift_hours=24):
		"""Parse recent tracks to get custom duration data (24 hour)."""
		limit_timestamp = arrow.utcnow().shift(hours=-shift_hours)
		data = await self.api_request(
			{
				"user": user,
				"method": "user.getrecenttracks",
				"from": limit_timestamp.timestamp,
				"limit": 200,
			}
		)
		loops = int(data["recenttracks"]["@attr"]["totalPages"])
		if loops > 1:
			for i in range(2, loops + 1):
				newdata = await self.api_request(
					{
						"user": user,
						"method": "user.getrecenttracks",
						"from": limit_timestamp.timestamp,
						"limit": 200,
						"page": i,
					}
				)
				data["recenttracks"]["track"] += newdata["recenttracks"]["track"]

		formatted_data = {}
		if group_by in ["album", "user.gettopalbums"]:
			for track in data["recenttracks"]["track"]:
				album_name = track["album"]["#text"]
				artist_name = track["artist"]["#text"]
				if (artist_name, album_name) in formatted_data:
					formatted_data[(artist_name, album_name)]["playcount"] += 1
				else:
					formatted_data[(artist_name, album_name)] = {
						"playcount": 1,
						"artist": {"name": artist_name},
						"name": album_name,
						"image": track["image"],
					}

			albumsdata = sorted(
				formatted_data.values(), key=lambda x: x["playcount"], reverse=True
			)
			return {
				"topalbums": {
					"album": albumsdata,
					"@attr": {
						"user": data["recenttracks"]["@attr"]["user"],
						"total": len(formatted_data.values()),
					},
				}
			}

		if group_by in ["track", "user.gettoptracks"]:
			for track in data["recenttracks"]["track"]:
				track_name = track["name"]
				artist_name = track["artist"]["#text"]
				if (track_name, artist_name) in formatted_data:
					formatted_data[(track_name, artist_name)]["playcount"] += 1
				else:
					formatted_data[(track_name, artist_name)] = {
						"playcount": 1,
						"artist": {"name": artist_name},
						"name": track_name,
						"image": track["image"],
					}

			tracksdata = sorted(
				formatted_data.values(), key=lambda x: x["playcount"], reverse=True
			)
			return {
				"toptracks": {
					"track": tracksdata,
					"@attr": {
						"user": data["recenttracks"]["@attr"]["user"],
						"total": len(formatted_data.values()),
					},
				}
			}

		if group_by in ["artist", "user.gettopartists"]:
			for track in data["recenttracks"]["track"]:
				artist_name = track["artist"]["#text"]
				if artist_name in formatted_data:
					formatted_data[artist_name]["playcount"] += 1
				else:
					formatted_data[artist_name] = {
						"playcount": 1,
						"name": artist_name,
						"image": track["image"],
					}

			artistdata = sorted(
				formatted_data.values(), key=lambda x: x["playcount"], reverse=True
			)
			return {
				"topartists": {
					"artist": artistdata,
					"@attr": {
						"user": data["recenttracks"]["@attr"]["user"],
						"total": len(formatted_data.values()),
					},
				}
			}

	async def get_np(self, username, ref):
		data = await self.api_request(
			{"method": "user.getrecenttracks", "user": username, "limit": 1},
			ignore_errors=True,
		)
		song = None
		if data is not None:
			try:
				tracks = data["recenttracks"]["track"]
				if tracks and "@attr" in tracks[0] and "nowplaying" in tracks[0]["@attr"]:
					song = {
						"artist": tracks[0]["artist"]["#text"],
						"name": tracks[0]["name"],
					}
			except KeyError:
				pass

		return song, ref

	async def get_lastplayed(self, username, ref):
		data = await self.api_request(
			{"method": "user.getrecenttracks", "user": username, "limit": 1},
			ignore_errors=True,
		)
		song = None
		if data is not None:
			try:
				tracks = data["recenttracks"]["track"]
				if tracks:
					nowplaying = False
					if tracks[0].get("@attr"):
						if tracks[0]["@attr"].get("nowplaying"):
							nowplaying = True

					if tracks[0].get("date"):
						date = tracks[0]["date"]["uts"]
					else:
						date = arrow.now().timestamp

					song = {
						"artist": tracks[0]["artist"]["#text"],
						"name": tracks[0]["name"],
						"nowplaying": nowplaying,
						"date": int(date),
					}
			except KeyError:
				pass

		return song, ref

	async def getnowplaying(self, ctx):
		await username_to_ctx(ctx)
		playing = {"artist": None, "album": None, "track": None}

		data = await self.api_request(
			{"user": ctx.username, "method": "user.getrecenttracks", "limit": 1}
		)

		try:
			tracks = data["recenttracks"]["track"]
			if tracks:
				playing["artist"] = tracks[0]["artist"]["#text"]
				playing["album"] = tracks[0]["album"]["#text"]
				playing["track"] = tracks[0]["name"]
		except KeyError:
			pass

		return playing

	async def get_playcount_track(self, artist, track, username, reference=None):
		data = await self.api_request(
			{
				"method": "track.getinfo",
				"user": username,
				"track": track,
				"artist": artist,
				"autocorrect": 1,
			}
		)
		try:
			count = int(data["track"]["userplaycount"])
		except (KeyError, TypeError):
			count = 0

		artistname = data["track"]["artist"]["name"]
		trackname = data["track"]["name"]

		try:
			image_url = data["track"]["album"]["image"][-1]["#text"]
		except KeyError:
			image_url = None

		if reference is None:
			return count
		return count, reference, (artistname, trackname, image_url), username

	async def get_playcount_album(self, artist, album, username, reference=None):
		data = await self.api_request(
			{
				"method": "album.getinfo",
				"user": username,
				"album": album,
				"artist": artist,
				"autocorrect": 1,
			}
		)
		try:
			count = int(data["album"]["userplaycount"])
		except (KeyError, TypeError):
			count = 0

		artistname = data["album"]["artist"]
		albumname = data["album"]["name"]

		try:
			image_url = data["album"]["image"][-1]["#text"]
		except KeyError:
			image_url = None

		if reference is None:
			return count
		return count, reference, (artistname, albumname, image_url), username

	async def get_playcount(self, artist, username, reference=None):
		data = await self.api_request(
			{"method": "artist.getinfo", "user": username, "artist": artist, "autocorrect": 1}
		)
		try:
			count = int(data["artist"]["stats"]["userplaycount"])
		except (KeyError, TypeError):
			count = 0

		name = data["artist"]["name"]

		if reference is None:
			return count
		return count, reference, name, username


# class ends here


async def scrape_artist_image(artist):
	url = f"https://www.last.fm/music/{urllib.parse.quote_plus(str(artist))}/+images"
	async with aiohttp.ClientSession() as session:
		data = await fetch(session, url, handling="text")
	if data is None:
		return None

	soup = BeautifulSoup(data, "html.parser")
	image = soup.find("img", {"class": "image-list-image"})
	if image is None:
		try:
			image = soup.find("li", {"class": "image-list-item-wrapper"}).find("a").find("img")
		except AttributeError:
			image = None

	return image


async def setup(bot):
	await bot.add_cog(LastFm(bot))


def format_plays(amount):
	if amount == 1:
		return "play"
	return "plays"


def get_period(timeframe, allow_custom=True):
	if timeframe in ["day", "today", "1day", "24h"] and allow_custom:
		period = "today"
	elif timeframe in ["7day", "7days", "weekly", "week", "1week"]:
		period = "7day"
	elif timeframe in ["30day", "30days", "monthly", "month", "1month"]:
		period = "1month"
	elif timeframe in ["90day", "90days", "3months", "3month"]:
		period = "3month"
	elif timeframe in ["180day", "180days", "6months", "6month", "halfyear"]:
		period = "6month"
	elif timeframe in ["365day", "365days", "1year", "year", "12months", "12month"]:
		period = "12month"
	elif timeframe in ["at", "alltime", "all", "overall"]:
		period = "overall"
	else:
		period = None

	return period


def humanized_period(period):
	if period == "today":
		humanized = "daily"
	elif period == "7day":
		humanized = "weekly"
	elif period == "1month":
		humanized = "monthly"
	elif period == "3month":
		humanized = "past 3 months"
	elif period == "6month":
		humanized = "past 6 months"
	elif period == "12month":
		humanized = "yearly"
	else:
		humanized = "alltime"

	return humanized


def parse_arguments(args):
	parsed = {"period": None, "amount": None}
	for a in args:
		if parsed["amount"] is None:
			try:
				parsed["amount"] = int(a)
				continue
			except ValueError:
				pass
		if parsed["period"] is None:
			parsed["period"] = get_period(a)

	if parsed["period"] is None:
		parsed["period"] = "overall"
	if parsed["amount"] is None:
		parsed["amount"] = 15
	return parsed


def parse_chart_arguments(args, server_version=False):
	parsed = {
		"period": None,
		"amount": None,
		"width": None,
		"height": None,
		"method": None,
		"path": None,
		"showtitles": None,
	}
	for a in args:
		a = a.lower()
		if parsed["amount"] is None:
			try:
				size = a.split("x")
				parsed["width"] = abs(int(size[0]))
				if len(size) > 1:
					parsed["height"] = abs(int(size[1]))
				else:
					parsed["height"] = abs(int(size[0]))
				continue
			except ValueError:
				pass

		if parsed["method"] is None:
			if a in ["talb", "topalbums", "albums", "album"]:
				parsed["method"] = "user.gettopalbums"
				continue

			if a in ["ta", "topartists", "artists", "artist"]:
				parsed["method"] = "user.gettopartists"
				continue

			if a in ["re", "recent", "recents"] and not server_version:
				parsed["method"] = "user.getrecenttracks"
				continue

		if parsed["period"] is None:
			parsed["period"] = get_period(a, allow_custom=not server_version)

		if parsed["showtitles"] is None and a == "notitle":
			parsed["showtitles"] = False

	if parsed["period"] is None:
		parsed["period"] = "7day"
	if parsed["width"] is None:
		parsed["width"] = 3
		parsed["height"] = 3
	if parsed["method"] is None:
		parsed["method"] = "user.gettopalbums"
	if parsed["showtitles"] is None:
		parsed["showtitles"] = True
	parsed["amount"] = parsed["width"] * parsed["height"]
	return parsed


async def fetch(session, url, params=None, handling="json"):
	async with session.get(url, params=params) as response:
		if response.status != 200:
			return None
		if handling == "json":
			return await response.json()
		if handling == "text":
			return await response.text()
		return await response


def period_http_format(period):
	period_format_map = {
		"7day": "LAST_7_DAYS",
		"1month": "LAST_30_DAYS",
		"3month": "LAST_90_DAYS",
		"6month": "LAST_180_DAYS",
		"12month": "LAST_365_DAYS",
		"overall": "ALL",
	}
	return period_format_map.get(period)


async def scrape_artists_for_chart(username, period, amount):
	tasks = []
	url = f"https://www.last.fm/user/{username}/library/artists"
	async with aiohttp.ClientSession() as session:
		for i in range(1, math.ceil(amount / 50) + 1):
			params = {"date_preset": period_http_format(period), "page": i}
			task = asyncio.ensure_future(fetch(session, url, params, handling="text"))
			tasks.append(task)

		responses = await asyncio.gather(*tasks)

	images = []
	for data in responses:
		if len(images) >= amount:
			break

		soup = BeautifulSoup(data, "html.parser")
		imagedivs = soup.findAll("td", {"class": "chartlist-image"})
		images += [div.find("img")["src"].replace("/avatar70s/", "/300x300/") for div in imagedivs]

	return images


async def username_to_ctx(ctx):
	if ctx.message.mentions:
		msg=ctx.message
		if f"<@!{ctx.bot.user.id}>" in ctx.message.content or f"<@{ctx.bot.user.id}>" in ctx.message.content:
			if len(ctx.message.mentions) > 1:
				ctx.usertarget=ctx.message.mentions[1]
			else:
				ctx.usertarget = ctx.author
			ctx.foreign_target = True
		else:
			ctx.foreign_target = True
			ctx.usertarget = ctx.message.mentions[0]
	else:
		ctx.foreign_target = False
		ctx.usertarget = ctx.author
	if ctx.usertarget.id in ctx.bot.cache.lastfm:
		ctx.username = ctx.bot.cache.lastfm[int(ctx.usertarget.id)]
	else:
	#if ctx.usertarget.id in lfm:
		#ctx.username=lfm[ctx.usertarget.id]
	#else:
		ctx.username = await ctx.bot.db.execute(
			"SELECT lastfm_username FROM user_settings WHERE user_id = %s",
			ctx.usertarget.id,
			one_value=True,
		)
		#lfm[ctx.usertarget.id]=ctx.username
	if not ctx.username and str(ctx.invoked_subcommand) not in ["fm set"]:
		if not ctx.foreign_target:
			msg = f"No last.fm username saved! Please use `{ctx.prefix}fm set <lastfm username>`"
		else:
			msg = f"{ctx.usertarget.mention} has not saved their lastfm username!"

		raise exceptions.Warning(msg)


def remove_mentions(text):
	"""Remove mentions from string."""
	return (re.sub(r"<@\!?[0-9]+>", "", text)).strip()


def get_list_contents(soup):
	"""Scrape lastfm for listing pages"""
	try:
		chartlist = soup.find("tbody", {"data-playlisting-add-entries": ""})
	except ValueError:
		return []

	results = []
	items = chartlist.findAll("tr", {"class": "chartlist-row"})
	for item in items:
		name = item.find("td", {"class": "chartlist-name"}).find("a").get("title")
		playcount = (
			item.find("span", {"class": "chartlist-count-bar-value"})
			.text.replace("scrobbles", "")
			.replace("scrobble", "")
			.strip()
		)
		results.append((name, int(playcount.replace(",", ""))))

	return results


async def get_additional_pages(session, soup, url):
	"""Check for pagination on listing page and asynchronously fetch all the remaining pages"""
	pagination = soup.find("ul", {"class": "pagination-list"})

	if pagination is None:
		return []

	page_count = len(pagination.findAll("li", {"class": "pagination-page"}))

	async def get_additional_page(n):
		new_url = url + f"&page={n}"
		data = await fetch(session, new_url, handling="text")
		soup = BeautifulSoup(data, "html.parser")
		return get_list_contents(soup)

	tasks = []
	if page_count > 1:
		for i in range(2, page_count + 1):
			tasks.append(get_additional_page(i))

	results = []
	for result in await asyncio.gather(*tasks):
		results += result

	return results
