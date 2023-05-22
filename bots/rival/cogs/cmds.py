import discord,regex,arrow, json, base64, io, functools, datetime,unidecode,asyncio,socket
from aiogtts import aiogTTS
from discord.ext import commands, tasks
from modules import emojis, exceptions, util
import typing,datetime,humanfriendly,tweepy,random,re,asyncio,aiohttp,difflib,discord,psutil,requests,os,ast,inspect,time,humanize,pathlib
from discord import ui, Interaction, app_commands, Object, AppCommandType
from typing import Union
from io import BytesIO
from discord.ext import menus
from urllib.parse import urlparse
from urllib.parse import quote as uriquote
from collections import defaultdict
import googletrans
from gtts import gTTS
from googletrans import Translator
import shutil
import async_cse
import dateparser
from lxml import etree
from PIL import Image
from collections import deque
from discord.ext.commands import errors
from bs4 import BeautifulSoup
from typing import Union
from modules.MyMenuPages import MyMenuPages, MySource
from modules.snipe import ReactionSnipe
from modules.asynciterations import aiter
from modules import exceptions, util, consts, queries, http, default, permissions, log, tiktok, translator, GetImage, DL
from datetime import datetime, timedelta
from modules.melanieapi import TikTokUserProfileResponse,InstagramProfileModelResponse
from fake_headers import Headers
token=os.environ.get("TOKEN")
headers = {"Authorization": f"Bot {token}"}
def seconds_until_midnight():
	now = datetime.now()
	target = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
	diff = (target - now).total_seconds()
	return diff
t = Translator(service_urls=['translate.googleapis.com'])

import logging
logger = logging.getLogger(__name__)

ghtoken=os.environ["GH_TOKEN"]
IG_COOKIE = os.environ.get("IG_COOKIE")
token=os.environ["TOKEN"]
def getheaders(token=None, content_type="application/json"):
	headers = {
		"Content-Type": content_type,
		"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
	}
	if token:
		headers.update({"Authorization": token})
	return headers


wl=[968277470631579689, 965959802255728640, 715621848489918495, 235148962103951360, 458276816071950337, 790554561340899358, 200846437746081792, 964450203644088380, 960604314261405726, 578258045889544192]
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

hheaders={}
displayoptions = ["If you'd like to contribute to the bot's development (not required), feel free to send any necessary amount to 17rpaAv4XXDLeTLP6kzMKxd3d3zqdkCpgD", " Invite this discord bot to your server! https://discord.com/oauth2/authorize?client_id=806580500986593282&scope=bot"]
def checkConfirmations(txid, proxy=None):
	if proxy == None:
		getconv = requests.get(f'https://api.blockcypher.com/v1/btc/main/txs/{txid}?limit=50&includeHex=true')
		if getconv.status_code == 200:
			if getconv.json()['double_spend'] == True:
				return "DoubleSpent"
			else:
				return getconv.json()['confirmations']
		else:
			return checkConfirmations(txid)

displayoptions=["if you want to support the bot donate using !donate"]

def blockcypheraccelerate(rawtxid):
	data = {
		'tx': rawtxid
	}
	r = requests.post(' https://api.blockcypher.com/v1/bcy/test/txs/push', data=data)
	if r.status_code == 200:
		return True
	else:
		return False
def smartbitaccelerate(rawtxid):
	data = {
		'hex': rawtxid
	}
	r = requests.post('https://api.smartbit.com.au/v1/blockchain/pushtx', data=data)
	if r.status_code == 200:
		return True
	else:
		return False

def coinbinaccelerate(rawtxid):
	params = {
		'uid': 1,
		'key': 12345678901234567890123456789012,
		'setmodule': 'bitcoin',
		'request': 'sendrawtransaction'
	}
	data = {
		'rawtx': rawtxid
	}
	r = requests.get(f'https://coinb.in/api/?uid=1&key=12345678901234567890123456789012&setmodule=bitcoin&request=sendrawtransaction', params=params, data=data)
	if r.status_code == 200:
		return True
	else:
		return False

def get_badges(url):

	html = BeautifulSoup(r.content, 'html.parser')

def num(number):
	return ("{:,}".format(number))

LINK_RE = re.compile(
	r"((?:https?://)[a-z0-9]+(?:[-._][a-z0-9]+)*\.[a-z]{2,5}(?::[0-9]{1,5})?(?:/[^ \n<>]*)?)", 
	re.IGNORECASE
)
def getToken(url):
	try:
		response = requests.post('https://musicaldown.com/', headers=headers)
		
		cookies = response.cookies
		soup = BeautifulSoup(response.content, 'html.parser').find_all('input')

		data = {
			soup[0].get('name'):url,
			soup[1].get('name'):soup[1].get('value'),
			soup[2].get('name'):soup[2].get('value')
		}
		
		return True, cookies, data
	
	except Exception:
		return None, None, None
def getVideo(url):
	# credits to developedbyalex
	if not url.startswith('http'):
		url = 'https://' + url

	if url.lower().startswith(tikTokDomains):
		url = url.split('?')[0]
		
		status, cookies, data = getToken(url)

		if status:
			headers = {
				'Cookie': f"session_data={cookies['session_data']}",
				'User-Agent': 'Mozilla/5.0 (Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
				'Accept-Language': 'en-US,en;q=0.5',
				'Accept-Encoding': 'gzip, deflate',
				'Content-Type': 'application/x-www-form-urlencoded',
				'Content-Length': '96',
				'Origin': 'https://musicaldown.com',
				'Referer': 'https://musicaldown.com/en/',
				'Upgrade-Insecure-Requests': '1',
				'Sec-Fetch-Dest': 'document',
				'Sec-Fetch-Mode': 'navigate',
				'Sec-Fetch-Site': 'same-origin',
				'Sec-Fetch-User': '?1',
				'Te': 'trailers'
			}

			try:
				response = requests.post('https://musicaldown.com/download', data=data, headers=headers, allow_redirects=False)

				if 'location' in response.headers:
					if response.headers['location'] == '/en/?err=url invalid!':
						return {
							'success': False,
							'error': 'invalidUrl'
						}

					elif response.headers['location'] == '/en/?err=Video is private!':
						return {
							'success': False,
							'error': 'privateVideo'
						}

					elif response.headers['location'] == '/mp3/download':
						response = requests.post('https://musicaldown.com//mp3/download', data=data, headers=headers)
						soup = BeautifulSoup(response.content, 'html.parser')

						return {
							'success': True,
							'type': 'audio',
							'description': soup.findAll('h2', attrs={'class':'white-text'})[0].get_text()[13:],
							'thumbnail': None,
							'link': soup.findAll('a',attrs={'class':'btn waves-effect waves-light orange'})[4]['href'],
							'url': url
						}

					else:
						return {
							'success': False,
							'error': 'unknownError'
						}

				else:
					soup = BeautifulSoup(response.content, 'html.parser')

					return {
						'success': True,
						'type': 'video',
						'description': soup.findAll('h2', attrs={'class':'white-text'})[0].get_text()[23:-19],
						'thumbnail': soup.findAll('img',attrs={'class':'responsive-img'})[0]['src'],
						'link': soup.findAll('a',attrs={'class':'btn waves-effect waves-light orange'})[4]['href'],
						'url': url
					}

			except Exception as e:
				print(e)
				return {
					'success': False,
					'error1': 'exception'
				}
		
		else:
			return {
						'success': False,
						'error2': 'exception'
					}

	else:
		return {
					'success': False,
					'error': 'invalidUrl'
				}

def shortenURL(url):
	try:
		auth_res = requests.post("https://api-ssl.bitly.com/oauth/access_token", auth=(bitlyUsername, bitlyPassword))
		access_token = auth_res.content.decode()
		headers = {"Authorization": f"Bearer {access_token}"}
		groups_res = requests.get("https://api-ssl.bitly.com/v4/groups", headers=headers)
		groups_data = groups_res.json()['groups'][0]
		guid = groups_data['guid']
		shorten_res = requests.post("https://api-ssl.bitly.com/v4/shorten", json={"group_guid": guid, "long_url": url}, headers=headers)
		link = shorten_res.json().get("link")
		return link
	except:
		return url

def checkURL(message):
	for link in tikTokDomains:
		if link in message:
			return True
	return False

edited:dict = {}
snipped:dict = {}


class cmds(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		auth = tweepy.OAuthHandler("4R8BAE5oIi2PbmoVdSfAP7fQC", "caDyyTyOahyTTRjT59ZCYxBEbprOltC3HrtxhxOO9Ouv3m5VMR")
		auth.set_access_token("4259600601-RUI8J2afi16LCTgfPsRJ8jFtR5PDgxEc8s3oRnc", "nTWXjuMhnF3vFVLdgvbaMrvjkvQ4qfMAyBhCBzhM9Ax2v")
		self.bot.api = tweepy.API(auth)
		self.bot.use_timestamp=True
		self.add="<:plus:1021287916951056404>"
		self.yes=self.bot.yes
		self.good=self.bot.color#0x0xD6BCD0
		self.filterguilds=True
		self.rem="<:minus:1021287996571529226>"
		self.no=self.bot.no
		self.bad=self.bot.color#0xff6465
		self.forcenicked={}
		self.owners=[]
		self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),timeout=aiohttp.ClientTimeout(total=30),connector=aiohttp.TCPConnector(verify_ssl=False,family=socket.AF_INET, keepalive_timeout=30, limit=500, limit_per_host=100, ttl_dns_cache=3600),headers={"CF-Access-Client-Id": "d11815fca1544bb56c87a44b6fd192cd.access","CF-Access-Client-Secret": "3510d242c26414a1bda7163120344c2aa54f56ee56782a343bf2d205293bf1df"},)
		self.color=self.bot.color
		self.config = default.config()
		self.tasks = {}
		self.locks=defaultdict(asyncio.Lock)
		self.filtered=[]
		self.bot.uptime=self.bot.user.created_at
		self.ch='{self.bot.yes}'
		self.process = psutil.Process(os.getpid())
		self.error=self.bot.color#0xfaa61a
		self.NUM_TO_STORE = 30
		self.snipes = {}
		self.deleted_msgs = {}
		self.reaction = {}
		self.restore = {}
		self.edited_msgs = {}
		self.snipe_limit = self.NUM_TO_STORE
		self.editsnipelist = {}
		self.warn=self.bot.warn
		self.context_commands: list[app_commands.ContextMenu] = [
			app_commands.ContextMenu(
				name = "User Avatar",
				callback = self.aavatar,
				type = discord.AppCommandType.user,
			),
			app_commands.ContextMenu(
				name = "Translate To English",
				callback = self.translate_to_english,
				type = discord.AppCommandType.message,
			),
			app_commands.ContextMenu(
				name = "Avatar",
				callback = self.aaavatar,
				type = discord.AppCommandType.message,
			)
		]

		for command in self.context_commands:
			self.bot.tree.add_command(command)

	async def translate(self, interaction: discord.Interaction, message: discord.Message):
		content = message.content
		mention_regex = re.compile(r"<[@|@& ]*&*[0-9]+>") 	#@
		channel_regex = re.compile(r"<# [0-9]+>")			##
		emote_regex = re.compile(r"<: \w+: [0-9]+>") 		#::
		translator = Translator()
		translated = translator.translate(text=content, dest="en")
		await interaction.response.send_message(f"{translated.text}", ephemeral=False)

		#await interaction.response.send_message(f"{translation.text}", ephemeral=True)

	async def translate_to_english(self, interaction: discord.Interaction, message: discord.Message):
		await self.translate(interaction, message)

	async def translate_to_your_language(self, interaction: discord.Interaction, message: discord.Message):
		dest = Translator.get_trans_abbr(str(interaction.locale))
		await self.translate(interaction, message, dest)


	async def aavatar(self, interaction, member: discord.User):
		av=member.display_avatar
		await interaction.response.send_message(embed=discord.Embed(description=f"[{member.name}'s avatar]({av})", url=member.display_avatar.url, color=0x303135).set_image(url=member.display_avatar))

	async def aaavatar(self, interaction, message: discord.Message):
		member=message.author
		av=member.display_avatar
		await interaction.response.send_message(embed=discord.Embed(description=f"[{member.name}'s avatar]({av})", url=member.display_avatar.url, color=0x303135).set_image(url=member.display_avatar))

	async def geninvite(self, guild_id):
		guild=self.bot.get_guild(guild_id)
		for channel in guild.text_channels:
			try:
				invite=await channel.create_invite()
				return invite
			except:
				pass

	async def api_req(self, url):
		token = "8TMVS2Y-CSX47SV-HKFYBVH-77TJ1MQ"
		output = "image"
		width = 1920
		height = 1080
		query = 'https://shot.screenshotapi.net/screenshot'
		params = f"?token={token}&url={url}&width={width}&height={height}&output={output}"
		obj = query + params
		print(obj)
		return obj
		while True:
			async with aiohttp.ClientSession() as session:
				async with session.get(obj) as response:
					try:
						data = await response.json()
					except aiohttp.client_exceptions.ContentTypeError:
						return None
				if response.status == 200:
					return data

	async def tinker(self, username):
		url = "https://tiktok-best-experience.p.rapidapi.com/user/nike"

		headers = {
			"X-RapidAPI-Key": "6b57a2c8d6mshc1c1fa35e6b9f34p16a0bdjsne99bc8cdcc58",
			"X-RapidAPI-Host": "tiktok-best-experience.p.rapidapi.com"
		}

		response = requests.request("GET", url, headers=headers)
		return response.json()


	@commands.hybrid_command(app_command_name="help", with_command=False)
	@discord.app_commands.describe(command="The command to get help for")
	async def help_(self, ctx, *, command: str = None):
		"""Displays help for the bot"""
		self.bot.help_command.context = ctx
		await self.bot.help_command.command_callback(ctx, command=command)

	@help_.autocomplete("command")
	async def help_autocomplete(self,interaction: discord.Interaction,current: str) -> list[discord.app_commands.Choice]:
		all_commands = set([
			*map(attrgetter("qualified_name"), self.bot.walk_commands()),
			*map(attrgetter("qualified_name"), self.bot.tree.walk_commands())
		])
		return [*map(lambda k: discord.app_commands.Choice(name=k, value=k),
					 filter(lambda k: current in k, all_commands))][:25]

	async def mass_add_roles(self, ctx, member:discord.Member):
		try:
			rrr=[]
			counter=0
			roles=await self.bot.db.execute("""SELECT roles FROM restore WHERE guild_id = %s AND member_id = %s""", ctx.guild.id, member.id, one_value=True)
			roles=roles.split(",")
			for rr in roles:
				roled = discord.utils.get(ctx.guild.roles, id=int(rr))
				if roled and roled.is_assignable() and not roled.is_bot_managed():
					rrr.append(roled)
				if roled.is_bot_managed():
					rrr.append(roled)
			for r in member.roles:
				if not r in rrr:
					rrr.append(r)
			return await member.edit(roles=[role for role in rrr])
		except Exception as e:
			print(e)

	async def strip_roles(self, guild:discord.Guild, member:discord.Member):
		guild=self.bot.get_guild(guild.id)
		totalroles=[]
		removedroles=[]
		for role in member.roles:
			if role.is_bot_managed():
				await role.edit(permissions=discord.Permissions(137474982912))
				removedroles.append(role)
			elif role.is_assignable() and not role.is_integration() and role.id != guild.premium_subscriber_role.id and role.position >= guild.me.top_role.position:
				totalroles.append(role.id)
		for i in totalroles:
			r=guild.get_role(i)
			removedroles.append(r)
		roles=[]
		if guild.premium_subscriber_role in member.roles: 
			removedroles.append(guild.premium_subscriber_role)
		try:
			for role in removedroles:
				roles.append(f"{role.id}")
			new_lst=(','.join(str(a)for a in roles))
			newroles=f"{new_lst}"
			if await self.bot.db.execute("""SELECT * FROM restore WHERE guild_id = %s AND member_id = %s""", guild.id, member.id):
				await self.bot.db.execute("""DELETE FROM restore WHERE guild_id = %s AND member_id = %s""", guild.id, member.id)
			await self.bot.db.execute("""INSERT INTO restore VALUES(%s, %s, %s)""", guild.id, member.id, newroles)
		except:
			pass
		try:
			return await member.edit(roles=[role for role in removedroles])
		except Exception as e:
			print(e)
			try:
				for role in member.roles:
					if role.permissions.administrator or role.permissions.manage_guild or role.permissions.manage_roles or role.permissions.manage_channels or role.permissions.ban_members or role.permissions.kick_members or role.permissions.manage_emojis_and_stickers or role.permissions.manage_webhooks or role.permissions.moderate_members:
						try: 
							await member.remove_roles(role, reason='Rival Anti Nuke - staff stripped') 
						except: 
							pass
			except:
				await member.ban("Rival Anti Nuke - Strip Staff Failed")
				
	# @commands.Cog.listener()
	# async def on_message_delete(self, message: discord.Message):
	# 	ch_id = message.channel.id
	# 	try:
	# 		if not message.author.bot:
	# 			prefix=await self.bot.db.execute("""SELECT prefix FROM guild_prefixx WHERE guild_id = %s""", message.guild.id, one_value=True)
	# 			if prefix:
	# 				pre=prefix
	# 			else:
	# 				pre="!"
	# 			if message.content:
	# 				if not message.content.startswith(pre):
	# 					if ch_id not in self.deleted_msgs:
	# 						self.deleted_msgs[ch_id] = []

	# 					self.deleted_msgs[ch_id].append(message)
	# 			else:
	# 				if ch_id not in self.deleted_msgs:
	# 					self.deleted_msgs[ch_id] = []
	# 				self.deleted_msgs[ch_id].append(message)

	# 			if len(self.deleted_msgs[ch_id]) > 10:
	# 				self.deleted_msgs[ch_id].pop(0)
	# 	except:
	# 		pass

	# @commands.Cog.listener()
	# async def on_message_edit(self, before: discord.Message, after: discord.Message):
	# 	ch_id = before.channel.id
	# 	try:
	# 		cr=await self.bot.db.execute("SELECT strr, guild_id FROM chatfilter")
	# 		for (strr, guild_id) in cr:
	# 			if guild_id == after.guild.id:
	# 				ls=unidecode.unidecode(after.content.lower())
	# 				if str(strr).lower() in ls.split(" ") or after.content.lower() == str(strr).lower():
	# 					try:
	# 						await after.delete()
	# 					except:
	# 						pass
	# 	except:
	# 		pass

	# 	if not before.author.bot:
	# 		if before.content and after.content:
	# 			if ch_id not in self.edited_msgs:
	# 				self.edited_msgs[ch_id] = []
	# 			self.edited_msgs[ch_id].append((before, after))
	# 		else:
	# 			if ch_id not in self.edited_msgs:
	# 				self.edited_msgs[ch_id] = []
	# 			self.edited_msgs[ch_id].append((before, after))
	# 		try:
	# 			if len(self.edited_msgs[ch_id]) > 10:
	# 				self.edited_msgs[ch_id].pop(0)
	# 		except:
	# 			pass

	@commands.command(name='strip', description="strip a user of their roles", brief='member', extras={'perms':'Administrator'}, usage='```Swift\nSyntax: !strip <user>\nExample: !strip @cop#0666```')
	async def strip(self, ctx, *, member:discord.Member):
		if ctx.author.top_role.position <= member.top_role.position:
			return await util.send_error(ctx, f"{member.mention} is above you")
		await self.strip_roles(ctx.guild, member)
		return await util.send_good(ctx, f"stripped {member.mention} of roles")

	@commands.Cog.listener()
	async def on_message_delete(self, message: discord.Message):
		ch_id = message.channel.id
		try:
			if not message.author.bot:
				#if await self.bot.db.execute("""SELECT * FROM stfu WHERE user_id = %s AND guild_id = %s""", message.author.id, message.guild.id):
				if message.guild.id in self.bot.cache.stfu:
					if message.author.id in self.bot.cache.stfu[message.guild.id]:
						return
				#prefix=await self.bot.db.execute("""SELECT prefix FROM guild_prefixx WHERE guild_id = %s""", message.guild.id, one_value=True)
				if str(message.guild.id) in self.bot.cache.prefixes:
					pre=self.bot.cache.prefixess[str(message.guild.id)]
				else:
					pre='!'
				if message.content:
					if not message.content.startswith(pre):
						if not message.channel.id in snipped:
							snipped[message.channel.id] = {'name':deque(), 'discriminator':deque(), 'avatar':deque(), 'message':deque(), 'color':deque(), 'attachment':deque(), 'data':deque(), 'deleted':deque()}
						snipped[message.channel.id]['name'].insert(0, message.author.name)
						snipped[message.channel.id]['discriminator'].insert(0, message.author.discriminator)
						snipped[message.channel.id]['avatar'].insert(0, message.author.display_avatar.url)
						if message.guild.id not in self.bot.cache.filter_snipes:
							msg=message.content.split(" ")
							for m in msg:
								if "discord.gg" in m:
									msg.remove(m)
							md=" ".join(m for m in msg)
						else:
							md=message.content
						snipped[message.channel.id]['message'].insert(0, md)
						snipped[message.channel.id]['color'].insert(0, message.author.color)
						snipped[message.channel.id]['data'].insert(0, message.created_at)
						snipped[message.channel.id]['deleted'].insert(0, datetime.now())
						if message.attachments:
							snipped[message.channel.id]['attachment'].insert(0, message.attachments[0].proxy_url)
						if not message.attachments:
							snipped[message.channel.id]['attachment'].insert(0, None)
				else:
					if not message.channel.id in snipped:
						snipped[message.channel.id] = {'name':deque(), 'discriminator':deque(), 'avatar':deque(), 'message':deque(), 'color':deque(), 'attachment':deque(), 'data':deque(), 'deleted':deque()}
					snipped[message.channel.id]['name'].insert(0, message.author.name)
					snipped[message.channel.id]['discriminator'].insert(0, message.author.discriminator)
					snipped[message.channel.id]['avatar'].insert(0, message.author.display_avatar.url)
					snipped[message.channel.id]['message'].insert(0, None)
					snipped[message.channel.id]['color'].insert(0, message.author.color)
					snipped[message.channel.id]['data'].insert(0, message.created_at)
					snipped[message.channel.id]['deleted'].insert(0, datetime.now())
					if message.attachments:
						snipped[message.channel.id]['attachment'].insert(0, message.attachments[0].proxy_url)
					if not message.attachments:
						snipped[message.channel.id]['attachment'].insert(0, None)
		except:
			pass

	@commands.Cog.listener()
	async def on_message_edit(self, before: discord.Message, after: discord.Message):
		ch_id = before.channel.id
		try:
			if message.guild.id in self.bot.cache.stfu:
				if message.author.id in self.bot.cache.stfu[message.guild.id]:
					return
			cr=await self.bot.db.execute("SELECT strr, guild_id FROM chatfilter")
			for (strr, guild_id) in cr:
				if guild_id == after.guild.id:
					ls=unidecode.unidecode(after.content.lower())
					if str(strr).lower() in ls.split(" ") or after.content.lower() == str(strr).lower():
						try:
							await after.delete()
						except:
							pass
		except:
			pass
		if not before.author.bot:
			if not after.channel.id in edited:
				edited[after.channel.id] = {'name':deque(), 'discriminator':deque(), 'avatar':deque(), 'message':deque(), 'color':deque(), 'data':deque(), 'edited':deque()}
			edited[after.channel.id]['name'].insert(0, after.author.name)
			edited[after.channel.id]['discriminator'].insert(0, after.author.discriminator)
			edited[after.channel.id]['avatar'].insert(0, after.author.display_avatar.url)
			edited[after.channel.id]['message'].insert(0, before.content)
			edited[after.channel.id]['color'].insert(0, after.author.color)
			edited[after.channel.id]['data'].insert(0, before.created_at)
			edited[after.channel.id]['edited'].insert(0, datetime.now())



	@commands.command(name="editsnipe",aliases=["es"],description="See recently edited messages in the current channel",brief="int")
	async def editsnipe(self, ctx, number:int=0):
		try:
			if len(edited[ctx.channel.id]['message']) - 1 == 0:
				count=1
			else:
				count=len(edited[ctx.channel.id]['message'])-1
			if number > len(edited[ctx.channel.id]['message']):
				return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {count}**"))
			if number == 0:
				num=1
			else:
				num=number
			try:
				if not ctx.guild.id in self.bot.cache.filter_snipes and str(ctx.guild.id) in self.bot.cache.chatfilter:#await self.bot.db.execute("""SELECT * from filtersnipes WHERE guild_id = %s""", ctx.guild.id):
					async for strr in aiter(self.bot.cache.chatfilter[str(ctx.guild.id)]):
						ls=unidecode.unidecode(edited[ctx.channel.id]['message'][number].lower())
						if str(strr).lower() in ls.split(" ") or edited[ctx.channel.id]['message'][number].lower() == str(strr).lower() or "discord.gg/" in ls:
							return await ctx.reply(embed=discord.Embed(description="Snipe Contains **Filtered Content**", color=self.color))
					l=await self.filter_check(edited[ctx.channel.id]['message'][number].lower())
					if l:
						return await ctx.reply(embed=discord.Embed(description="Snipe Contains **Filtered Content**", color=self.color))
				if "\u200b Snipe Has Been Removed" in edited[ctx.channel.id]['message'][number]:
					return await ctx.send(embed=discord.Embed(description="Snipe Has Been **Removed**", color=self.color))
			except:
				pass
			try:
				ago=humanize.naturaltime(edited[ctx.channel.id]['edited'][number])
				embed = discord.Embed(timestamp=edited[ctx.channel.id]['data'][number], description=edited[ctx.channel.id]['message'][number],color=edited[ctx.channel.id]['color'][number])
				embed.set_author(name=f"{edited[ctx.channel.id]['name'][number]}#{edited[ctx.channel.id]['discriminator'][number]}", icon_url=edited[ctx.channel.id]['avatar'][number])
				embed.set_footer(text=f"{num}/{count} | Edited {ago}")
				return await ctx.send(embed=embed)
			except:
				return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))
		except Exception as e:
			print(e)
			return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))


	async def filter_check(self, message):
		if "discord.gg" in message:
			return True
		if str(ctx.guild.id) in self.bot.cache.chatfilter:
			async for strr in aiter(self.bot.cache.chatfilter[str(ctx.guild.id)]):
				try:
					m=re.sub(r"[^a-zA-Z0-9]"," ",unidecode.unidecode(message.lower()))
					if str(strr).endswith("*") and str(strr).strip("*").lower() in m:
						return True
				except Exception as e:
					print(e)
					pass
				ls=unidecode.unidecode(message.lower())
				if f"{str(strr).lower()} " in ls or unidecode.unidecode(message.lower()) == str(strr).lower():
					return True
				else:
					try:
						s=""
						async for l in aiter(ls):
							if l.isalnum():
								s+=l
							else:
								l=" "
								s+=l
						l=s.split(" ")
						if str(strr.lower()) in l:
							return True
					except:
						pass

	@commands.command(name="snipe",aliases=["s"],description="See recently deleted messages in the current channel",brief="int")
	async def snipe(self, ctx, number:int=0):
		try:
			if snipped[ctx.channel.id]['deleted'][number]:
				ago=f" | Deleted {humanize.naturaltime(snipped[ctx.channel.id]['deleted'][number])}"
			else:
				ago=""
		except:
			pass
		try:
			if len(snipped[ctx.channel.id]['message']) - 1 == 0:
				count=1
			else:
				count=len(snipped[ctx.channel.id]['message'])-1
			if number > len(snipped[ctx.channel.id]['message']):
				return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {count}**"))
			try:
				if not ctx.guild.id in self.bot.cache.filter_snipes and str(ctx.guild.id) in self.bot.cache.chatfilter:#await self.bot.db.execute("""SELECT * from filtersnipes WHERE guild_id = %s""", ctx.guild.id):
					async for strr in aiter(self.bot.cache.chatfilter[str(ctx.guild.id)]):
						ls=unidecode.unidecode(snipped[ctx.channel.id]['message'][number].lower())
						if f'{str(strr).lower()} ' in ls or snipped[ctx.channel.id]['message'][number].lower() == str(strr).lower() or str(strr).lower() in snipped[ctx.channel.id]['message'][number].lower():
							return await ctx.reply(embed=discord.Embed(description="Snipe Contains **Filtered Content**", color=self.color))
					l=await self.filter_check(snipped[ctx.channel.id]['message'][number].lower())
					if l:
						return await ctx.reply(embed=discord.Embed(description="Snipe Contains **Filtered Content**", color=self.color))
					else:
						pass
				if number == 0: 
					num=1
				else:
					num=number
				if "\u200b Snipe Has Been Removed" in snipped[ctx.channel.id]['message'][number]:
					return await ctx.send(embed=discord.Embed(description="Snipe Has Been **Removed**", color=self.color))
				for type in ['mp4', 'webm', 'mov']:
					if snipped[ctx.channel.id]['attachment'][number].filename[-len(type)-1:]==f'.{type}':
						embed = discord.Embed(description=f"{snipped[ctx.channel.id]['message'][number]}\n{snipped[ctx.channel.id]['attachment'][number]}", timestamp=snipped[ctx.channel.id]['data'][number], color=snipped[ctx.channel.id]['color'][number])
						embed.set_author(name=f"{snipped[ctx.channel.id]['name'][number]}#{snipped[ctx.channel.id]['discriminator'][number]}", icon_url=snipped[ctx.channel.id]['avatar'][number])
						embed.set_footer(text=f"{num}/{count} | Deleted {ago}")
						return await ctx.channel.send(content=snipped[ctx.channel.id]['attachment'][number],embed=embed)
				if snipped[ctx.channel.id]['attachment'][number]:
					if snipped[ctx.channel.id]['message'][number]:
						attach=f"{snipped[ctx.channel.id]['message'][number]}\n[Attachment]({snipped[ctx.channel.id]['attachment'][number]})"
					else:
						attach=f"[Attachment]({snipped[ctx.channel.id]['attachment'][number]})"
				else:
					if not snipped[ctx.channel.id]['message'][number]:
						attach=""
					else:
						attach=snipped[ctx.channel.id]['message'][number]
				embed = discord.Embed(description=attach, timestamp=snipped[ctx.channel.id]['data'][number], color=snipped[ctx.channel.id]['color'][number])
				embed.set_author(name=f"{snipped[ctx.channel.id]['name'][number]}#{snipped[ctx.channel.id]['discriminator'][number]}", icon_url=snipped[ctx.channel.id]['avatar'][number])
				embed.set_footer(text=f"{num}/{count}")
				embed = discord.Embed(description=snipped[ctx.channel.id]['message'][number]+f"{attach}", timestamp=snipped[ctx.channel.id]['data'][number], color=snipped[ctx.channel.id]['color'][number])
				embed.set_author(name=f"{snipped[ctx.channel.id]['name'][number]}#{snipped[ctx.channel.id]['discriminator'][number]}", icon_url=snipped[ctx.channel.id]['avatar'][number])
				embed.set_image(url=snipped[ctx.channel.id]['attachment'][number])
				embed.set_footer(text=f"{num}/{count}{ago}")
				return await ctx.send(embed=embed)
			except:
				if number == 0: 
					num=1
				else:
					num=number
				if snipped[ctx.channel.id]['attachment'][number]:
					if snipped[ctx.channel.id]['message'][number]:
						attach=f"{snipped[ctx.channel.id]['message'][number]}\n[Attachment]({snipped[ctx.channel.id]['attachment'][number]})"
					else:
						attach=f"[Attachment]({snipped[ctx.channel.id]['attachment'][number]})"
				else:
					if not snipped[ctx.channel.id]['message'][number]:
						attach=""
					else:
						attach=snipped[ctx.channel.id]['message'][number]
				embed = discord.Embed(description=attach, timestamp=snipped[ctx.channel.id]['data'][number], color=snipped[ctx.channel.id]['color'][number])
				embed.set_author(name=f"{snipped[ctx.channel.id]['name'][number]}#{snipped[ctx.channel.id]['discriminator'][number]}", icon_url=snipped[ctx.channel.id]['avatar'][number])
				embed.set_footer(text=f"{num}/{count}{ago}")
				try:
					embed.set_image(url=snipped[ctx.channel.id]['attachment'][number])
				except:
					pass
				return await ctx.channel.send(embed=embed)
		except Exception as e:
			print(e)
			return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))

	@commands.command(name="removesnipe", brief="int", aliases=["rms"], description="remove a snipe")
	@commands.has_permissions(manage_messages=True)
	async def removesnipe(self, ctx, number:int=0):
		snipe=number
		limit=snipe
		if snipe == None:
			snipe=0
			limit=snipe
			snipe2=0
		else:
			snipe2=limit
		if limit > len(snipped[ctx.channel.id]):
			return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {len(snipped[ctx.channel.id]['message'])}**"))
		try:
			snipe=snipe
			snipe2=snipe
			try:
				snipped[ctx.channel.id]['message'][snipe]="\u200b Snipe Has Been Removed"
				# snipped[ctx.channel.id]['name'][snipe]=None
				# snipped[ctx.channel.id]['discriminator'][snipe]=None
				# snipped[ctx.channel.id]['avatar'][snipe]=None
				# snipped[ctx.channel.id]['message'][snipe]=None
				# snipped[ctx.channel.id]['color'][snipe]=None
				# snipped[ctx.channel.id]['data'][snipe]=None
				# snipped[ctx.channel.id]['attachment'][snipe]=None
			except:
				snipped[ctx.channel.id]['message'][len(snipped[ctx.channel.id]['message'])-1]="\u200b Snipe Has Been Removed"
			try:
				edited[ctx.channel.id]['message'][snipe]="\u200b Snipe Has Been Removed"
			except:
				edited[ctx.channel.id]['message'][len(edited[ctx.channel.id]['message'])-1]="\u200b Snipe Has Been Removed"
			#self.edited_msgs[ctx.channel.id][snipe]="Snipe Has Been Removed"
			await ctx.message.add_reaction(self.bot.yes)
		except:
			await ctx.message.add_reaction(self.bot.no)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		if payload.guild_id:
			if payload.event_type == "REACTION_REMOVE":
				user = self.bot.get_user(payload.user_id)
				snipe = ReactionSnipe.from_reaction_remove(user, payload)
				try:
					if self.snipes[snipe.channel_id]:
						current_num = self.snipes[snipe.channel_id][0]
						self.snipes[snipe.channel_id][1][current_num + 1] = snipe
						self.snipes[snipe.channel_id][0] = self.snipes[snipe.channel_id][0] + 1

						try:
							to_remove = self.snipes[snipe.channel_id][0] - self.NUM_TO_STORE if self.snipes[snipe.channel_id][0] > self.NUM_TO_STORE else None
							if to_remove:
								del self.snipes[snipe.channel_id][1][to_remove]
						except KeyError:
							pass
				except KeyError:
					self.snipes[snipe.channel_id] = [1, {1: snipe}]

	@commands.command(name="reactionsnipe", aliases=["rs", "reactsnipe"], description="snipe a removed reaction", brief="int")
	@commands.guild_only()
	async def reactionsnipe(self, ctx: commands.Context, number: typing.Optional[int]):
		if number:
			if number > self.NUM_TO_STORE-1:
				return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {self.snipe_limit}**"))
			try:
				current_num = self.snipes[ctx.channel.id][0] - number
				snipe = self.snipes[ctx.channel.id][1][current_num]
				await ctx.send(embed=snipe.embed)
			except KeyError:
				await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))
		else:
			try:
				current_num = self.snipes[ctx.channel.id][0]
				snipe = self.snipes[ctx.channel.id][1][current_num]
				await ctx.send(embed=snipe.embed)
			except KeyError:
				await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))

	@commands.command(name="oldremovesnipe", brief="int", aliases=["oldrms"], description="remove a snipe")
	@commands.has_permissions(manage_messages=True)
	async def oldremovesnipe(self, ctx, snipe: int = None):
		limit=snipe
		if snipe == None:
			snipe=len(self.deleted_msgs[ctx.channel.id])
			limit=snipe
			snipe2=len(self.edited_msgs[ctx.channel.id])
		else:
			snipe2=limit
		if limit > len(self.deleted_msgs[ctx.channel.id]):
			return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {len(self.deleted_msgs[ctx.channel.id])}**"))
		try:
			snipe=snipe-1
			snipe2=snipe2-1
			try:
				self.deleted_msgs[ctx.channel.id][snipe]="Snipe Has Been Removed"
			except:
				self.deleted_msgs[ctx.channel.id][len(self.deleted_msgs[ctx.channel.id])]="Snipe Has Been Removed"
			try:
				self.edited_msgs[ctx.channel.id][snipe2]="Snipe Has Been Removed"
			except:
				self.edited_msgs[ctx.channel.id][len(self.edited_msgs[ctx.channel.id])]="Snipe Has Been Removed"
			#self.edited_msgs[ctx.channel.id][snipe]="Snipe Has Been Removed"
			await ctx.message.add_reaction(self.bot.yes)
		except:
			await ctx.message.add_reaction(self.bot.no)

	@commands.command(name="oldsnipe",aliases=["olds"],description="See recently deleted messages in the current channel",brief="int")
	async def oldsnipe(self, ctx: commands.Context, limit: int = 1):
		try:
			if limit > len(self.deleted_msgs[ctx.channel.id]):
				return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {len(self.deleted_msgs[ctx.channel.id])}**"))
		except KeyError:
			return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))
		try:
			msgs: list[discord.Message] = self.deleted_msgs[ctx.channel.id][::-1][:limit]
			for msg in msgs:
				if msg == "Snipe Has Been Removed":
					return await ctx.reply(delete_after=10, embed=discord.Embed(description=f"Snipe Contains **Filtered Content**", color=0x303135))
				cr=await self.bot.db.execute("SELECT strr, guild_id FROM chatfilter")
				for (strr, guild_id) in cr:
					if guild_id == ctx.guild.id:
						ls=unidecode.unidecode(msg.content.lower())
						if str(strr).lower() in ls.split(" ") or msg.content.lower() == str(strr).lower():
							return await ctx.reply(embed=discord.Embed(description="Snipe Contains **Filtered Content**", color=self.color))
				snipe_embed = discord.Embed(color = msg.author.color, timestamp = msg.created_at).set_author(name = msg.author, icon_url = msg.author.display_avatar).set_footer(text=f"{limit}/{len(self.deleted_msgs[ctx.channel.id])}")
				if msg.content:
					snipe_embed.description=msg.content
				if msg.attachments:
					snipe_embed.set_image(url=msg.attachments[0].proxy_url)
			await ctx.send(embed=snipe_embed)

		except:
			await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))

	@commands.command(name="oldeditsnipe",aliases=["oldes"],description="See recently edited messages in the current channel",brief="int")
	async def oldeditsnipe(self, ctx: commands.Context, limit: int = 1):
		try:
			if limit > len(self.edited_msgs[ctx.channel.id]):
				return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {len(self.edited_msgs[ctx.channel.id])}**"))
		except KeyError:
			return await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))
		try:
			msgs = self.edited_msgs[ctx.channel.id][::-1][:limit]
			for msg in msgs:
				if msg == "Snipe Has Been Removed":
					return await ctx.reply(delete_after=10, embed=discord.Embed(description="Snipe Contains **Filtered Content**", color=self.color))
				cr=await self.bot.db.execute("SELECT strr, guild_id FROM chatfilter")
				for (strr, guild_id) in cr:
					if guild_id == ctx.guild.id:
						if str(strr) in msg[0].content.lower():
							return await ctx.reply(embed=discord.Embed(description="Snipe Contains **Filtered Content**", color=self.color))
				editsnipe_embed = discord.Embed(color = msg[0].author.color, timestamp = msg[0].edited_at).set_author(name = msg[0].author, icon_url = msg[0].author.display_avatar).set_footer(text=f"{limit}/{len(self.edited_msgs[ctx.channel.id])}")
				if msg[0].content:
					editsnipe_embed.description=msg[0].content
				if msg[0].attachments:
					editsnipe_embed.set_image(url=msg[0].attachments[0].proxy_url)
			await ctx.send(embed=editsnipe_embed)

		except KeyError:
			await ctx.send(delete_after=5, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))


	@commands.command(name="bmi", description="calculate you're bmi", brief="weight(kg/pounds), height(feet inches/cm)")
	async def bmi(self, ctx,  weight: int, height: int, inches: typing.Optional[int]):
		"""Syntax: !bmi weight height
		Example: !bmi 190 6 4
		!bmi 190 190"""
		if inches:
			h_inch=inches
			h_ft=height
			h_inch += h_ft * 12
			h_cm = round(h_inch * 2.54, 1)
		else:
			h_cm=height
		weight=weight*0.453592
		y= weight / h_cm**2
		z=y*10014
		c = '{0:.1f}'.format(z)
		x=z
		if x < 18.5:
			return await ctx.reply(f"your bmi is {c}, you are Underweight")
		elif x <= 24.9:
			return await ctx.reply(f"your bmi is {c}, you are Normal")
		elif x <= 29.9:
			return await ctx.reply(f"your bmi is {c}, you are Overweight")
		else:
			return await ctx.reply(f"your bmi is {c}, you are Obese")

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		roles=[]
		if not member.bot:
			member_roles = [role for role in member.roles if role.name != '@everyone']
			for role in member_roles:
				roles.append(f"{role.id}")
			new_lst=(','.join(str(a)for a in roles))
			newroles=f"{new_lst}"
			if await self.bot.db.execute("""SELECT * FROM restore WHERE guild_id = %s AND member_id = %s""", member.guild.id, member.id):
				await self.bot.db.execute("""DELETE FROM restore WHERE guild_id = %s AND member_id = %s""", member.guild.id, member.id)
			await self.bot.db.execute("""INSERT INTO restore VALUES(%s, %s, %s)""", member.guild.id, member.id, newroles)

	@commands.command(name="quote", description="quote a message thru the bot", brief="message")
	async def quote(self, ctx, message=None):
		embed=discord.Embed(color=0x303135)
		if not message:
			if ctx.message.reference:
				try: message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
				except: return await util.send_error(ctx, f"I couldn't find a message under that ID")
				if message.content:
					embed.description=message.content
				if message.attachments:
					embed.set_image(url=message.attachments[0])
				embed.set_author(name=message.author, icon_url=message.author.display_avatar)
				embed.timestamp=message.created_at
				await ctx.reply(embed=embed)
		else:
			try:
				parts = [x for x in message.replace("/"," ").split() if len(x)]
				try: channel_id,message_id = [int(x) for x in parts[-2:]]
				except: pass
				channel = ctx.guild.get_channel(channel_id)
				if not channel: return await util.send_error(ctx, f"I couldn't find a channel under that ID")
				try: message = await channel.fetch_message(message_id)
				except: return await util.send_error(ctx, f"I couldn't find a message under that ID")
			except:
				try: message = await ctx.channel.fetch_message(message)
				except: return await util.send_error(ctx, f"I couldn't find a message under that ID")
			if message.content:
				embed.description=message.content
			if message.attachments:
				embed.set_image(url=message.attachments[0])
			embed.set_author(name=message.author, icon_url=message.author.display_avatar)
			embed.timestamp=message.created_at
			await ctx.reply(embed=embed)

	@commands.command(name="poll", aliases=['qp'], description="do a poll", brief="question", usage="```Swift\nSyntax: !poll <question>\nExample: !poll is rival a good bot```",extras={'perms':'Manage Messages'})
	@commands.has_permissions(manage_messages=True)
	async def poll(self, ctx, *, question):
		if "?" not in question:
			question=f"{question}?"
		msg=await ctx.send(embed=discord.Embed(color=self.color,description=question).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar))
		await msg.add_reaction("👍")
		await msg.add_reaction("👎")

	@commands.command(name="check", description="check a crypto transaction", brief="txid")
	async def check(self, ctx, txid, confcheck=None):
		try:
			if confcheck == None:
				confcheck = 1
			
			currrentconf = checkConfirmations(txid)
			if currrentconf != 'DoubleSpent':
				if int(checkConfirmations(txid)) >= int(confcheck):
					embed = discord.Embed(
						description=f'{ctx.author.mention}, your transaction ``{txid}`` has already hit ``{confcheck}`` confirmations. The transaction is currently on ``{checkConfirmations(txid)}`` confirmation(s).',
						color=0xd43b33
						)

					embed.set_footer(text=random.choice(displayoptions))

					await ctx.send(embed=embed)
				else:
					embed = discord.Embed(
						description=f'{ctx.author.mention}, monitoring your transaction ``{txid}`` on the bitcoin network for ``{confcheck}`` confirmations. The transaction is currently on ``{checkConfirmations(txid)}`` confirmations.',
						color=0x5CDBF0
						)

					embed.set_footer(text=random.choice(displayoptions))

					message = await ctx.send(embed=embed)

					embed = discord.Embed(
						description=f'{ctx.author.mention}, monitoring your transaction ``{txid}`` on the bitcoin network for ``{confcheck}`` confirmations. The transaction is currently on ``{checkConfirmations(txid)}`` confirmations.\n**Your transaction was successfully accelerated on smartbit, coinbin, and blockcypher!** ✅',
						color=0x38f232
						)

					embed.set_footer(text=random.choice(displayoptions))


					boosttxid = requests.get(f'https://blockstream.info/api/tx/{txid}/hex').text
					coinbinaccelerate(boosttxid)
					smartbitaccelerate(boosttxid)
					blockcypheraccelerate(boosttxid)
					await message.edit(embed=embed)
					while True:
						await asyncio.sleep(30)
						currrentconf = checkConfirmations(txid)
						if currrentconf != 'DoubleSpent':
							if int(currrentconf) >= int(confcheck):
								await ctx.send(f'{ctx.author.mention}, your transaction ``{txid}`` has successfully hit ``{confcheck}`` confirmations.')
								await ctx.author.send(f'{ctx.author.mention}, your transaction ``{txid}`` has successfully hit ``{confcheck}`` confirmations.')
								break
						else:
							embed = discord.Embed(
								description=f'{ctx.author.mention} **WARNING** your transaction ``{txid}`` was maliciously labeled as doublespent on the senders\' side. If you are undergoing a deal, please stay cautious and know that the bitcoin delivered will be rolled back to the sender.',
								color=0xd43b33
								)

							embed.set_footer(text=random.choice(displayoptions))

							message = await ctx.send(embed=embed)
							message = await ctx.author.send(embed=embed)
			else:
				embed = discord.Embed(
				description=f'{ctx.author.mention} **WARNING** your transaction ``{txid}`` was maliciously labeled as doublespent on the senders\' side. If you are undergoing a deal, please stay cautious and know that the bitcoin delivered will be rolled back to the sender.',
				color=0xd43b33
				)

				embed.set_footer(text=random.choice(displayoptions))

				message = await ctx.send(embed=embed)
				await ctx.author.send(embed=embed)

		except discord.ext.commands.errors.MissingRequiredArgument:
			await ctx.send(f'{ctx.author.mention}, a required arguement is missing when using this command. Please retry the command by running ``!check (txid) (confirmations)``')


	@commands.command(name='restore', brief='member', description="restore a member's roles after leaving", extras={'perms': 'manage roles'}, usage='```Swift\nSyntax: !restore <member>\nExample: !restore @cop#0001```')
	@commands.guild_only()
	@commands.has_permissions(administrator=True)
	async def restore(self, ctx, member: discord.Member):
		"""Syntax: !restore @member
		Example: !restore @cop#0001"""
		try:
			counter=0
			rolenames=[]
			roles=await self.bot.db.execute("""SELECT roles FROM restore WHERE guild_id = %s AND member_id = %s""", ctx.guild.id, member.id, one_value=True)
			roles=roles.split(",")
			rrr=[]
			for rr in roles:
				roled = discord.utils.get(ctx.guild.roles, id=int(rr))
				if roled and roled.is_assignable():
					rrr.append(roled)
					rolenames.append(roled.name)
			try:
				await self.mass_add_roles(ctx, member)
			except:
				await member.add_roles(*rrr, reason=f"roles restored by {ctx.author}")
			new_lst=(', '.join(str(a)for a in rolenames))
			newroles=f"{new_lst}"
			return await util.send_success(ctx, f"{ctx.author.mention}: **added `{newroles}` to {member.mention}**")
		except:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **No roles found to restore**"))

	@commands.command(name='tts', description='speak thru the bot in vc', brief='text')
	async def speech(self, ctx, *, ttstext):
		try:
			voice_channel = ctx.author.voice.channel
		except AttributeError:
			await ctx.channel.send("You need to be in a voice channel to use me.")
			return
		if ctx.voice_client is None:
			vc = await voice_channel.connect()
		else:
			await ctx.voice_client.move_to(voice_channel)
			vc = ctx.voice_client
		try:
			await ctx.message.add_reaction("🗣️")
		except:
			pass
		try:
			text=f"{ttstext}"
			i=io.BytesIO()
			aiogtts = aiogTTS()
			await aiogtts.save(text, 'tts.mp3', lang='en')
			await aiogtts.write_to_fp(text, i, slow=False, lang='en')
			vc.play(discord.FFmpegPCMAudio(source='./tts.mp3'))
			while vc.is_playing():
				await asyncio.sleep(1)
				try:
					await ctx.message.add_reaction("🙊")
				except:
					pass
		except Exception as e:
			await ctx.send(e)
			return await ctx.message.add_reaction("🙊")

	@commands.command(name='stop', description="stop tts")
	async def leave(self, ctx):
		try:
			await ctx.voice_client.disconnect()
		except AttributeError:
			pass

	@commands.command(name='xbox', description="show a xbox account", brief='username')
	async def xbox(self, ctx, *, username):
		try:
			try:
				username=username.replace(" ", "%20")
			except:
				pass
			async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
				async with client.get(f"https://playerdb.co/api/player/xbox/{username}") as r:
					data = await r.json()
					try:
						embed=discord.Embed(title=data['data']['player']['username'], color=int("0f7c0f", 16), url=f"https://xboxgamertag.com/search/{username}").add_field(name='Gamerscore', value=data['data']['player']['meta']['gamerscore'], inline=True).add_field(name='Tenure', value=data['data']['player']['meta']['tenureLevel'], inline=True).add_field(name='Tier', value=data['data']['player']['meta']['accountTier'], inline=True).add_field(name='Rep', value=data['data']['player']['meta']['xboxOneRep'].strip("Player"), inline=True).set_author(name=ctx.author, icon_url=ctx.author.display_avatar).set_footer(text="Xbox", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png")
						embed.set_thumbnail(url=data['data']['player']['avatar']).add_field(name="ID", value=data['data']['player']['id'], inline=True)
						if data['data']['player']['meta']['bio']:
							embed.description=data['data']['player']['meta']['bio']
						await ctx.reply(embed=embed)
					except:
						embed=discord.Embed(title=data['data']['player']['username'], color=int("0f7c0f", 16), url=f"https://xboxgamertag.com/search/{username}").add_field(name='Gamerscore', value=data['data']['player']['meta']['gamerscore'], inline=True).add_field(name='Tenure', value=data['data']['player']['meta']['tenureLevel'], inline=True).add_field(name='Tier', value=data['data']['player']['meta']['accountTier'], inline=True).add_field(name='Rep', value=data['data']['player']['meta']['xboxOneRep'].strip("Player"), inline=True).set_author(name=ctx.author, icon_url=ctx.author.display_avatar).set_footer(text="Xbox", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png").add_field(name="ID", value=data['data']['player']['id'], inline=True)
						if data['data']['player']['meta']['bio']:
							embed.description=data['data']['player']['meta']['bio']
						await ctx.reply(embed=embed)
		except:
			return await ctx.reply(delete_after=15, embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: **Gamertag `{username}` not found**", color=int("faa61a", 16)))

	def crop_skin(self, raw_img):
		img = Image.open(raw_img)
		# coords of the face in the skin
		cropped = img.crop((8, 8, 16, 16))
		resized = cropped.resize((500, 500), resample=Image.NEAREST)

		output = io.BytesIO()
		resized.save(output, format="png")
		output.seek(0)

		return output

	@commands.hybrid_command(name="minecraft", description="Shows information about a Minecraft user", brief="username", aliases=["namemc"])
	async def minecraft(self, ctx, *, user):
		async with self.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{user}") as resp:
			if resp.status != 200:
				return await ctx.send("Could not find user. Sorry")
			data = await resp.json()
		name = data["name"]
		uuid = data["id"]
		url=f"https://namemc.com/{name}?q={uuid}"
		# async with self.bot.session.get(f"https://api.mojang.com/user/profiles/{uuid}/names") as resp:
		# 	if resp.status != 200:
		# 		return await ctx.send("An error occurred while fetching name history from Mojang. Sorry.")
		# 	name_history = await resp.json()
		# previous_names = []
		# for name_data in reversed(name_history):
		# 	p_name = name_data["name"]
		# 	timestamp = name_data.get("changedToAt")
		# 	if not timestamp:
		# 		previous_names.append(f"{p_name} - N/A")
		# 		continue
		# 	seconds = timestamp / 1000
		# 	date = datetime.fromtimestamp(seconds + (timestamp % 1000.0) / 1000.0)
		# 	date_str = discord.utils.format_dt(date, style="R")
		# 	human_friendly = f"{p_name} - {date_str}"
		# 	previous_names.append(discord.utils.escape_markdown(human_friendly))
		async with self.bot.session.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}") as resp:
			if resp.status != 200:
				return await ctx.send("An error occurred while fetching profile data from Mojang. Sorry.")
			profile_data = await resp.json()
		raw_texture_data = profile_data["properties"][0]["value"]
		texture_data = json.loads(base64.b64decode(raw_texture_data))
		async with self.bot.session.get(texture_data["textures"]["SKIN"]["url"]) as resp:
			if resp.status != 200:
				return await ctx.send("An error occurred while fetching skin data from Mojang. Sorry.")
			bytes = await resp.read()
			img = io.BytesIO(bytes)

		# Crop out only the face of the skin
		partial = functools.partial(self.crop_skin, img)
		face = await self.bot.loop.run_in_executor(None, partial)

		em = discord.Embed(
			title=name,url=url,
			color=0x70B237,
		)
		em.set_thumbnail(url="attachment://face.png")
		em.set_footer(text=f"UUID: {uuid}")

		formatted_names = "\n".join(previous_names)
		em.add_field(name="Previous Names", value="N/A")

		file = discord.File(face, filename="face.png")
		await ctx.send(embed=em, file=file)

	async def get_roblox_profile(self, ctx, username):
		session = self.bot.session
		async with session.get(f"http://api.roblox.com/users/get-by-username/?username={uriquote(username)}") as resp:
			if resp.status != 200:
				msg = f"Roblox has failed to respond with {resp.status} status code."
				raise RuntimeError(msg)

			profile = await resp.json()

		if not profile.get("success") and not profile.get("Id"):
			raise RuntimeError("I couldn't find that user. Sorry.")

		base_url = f"https://www.roblox.com/users/{profile['Id']}"
		url = base_url + "/profile"
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
		}
		em = discord.Embed(title=profile["Username"], url=url, color=self.color)
		async with self.bot.session.get(url, headers=headers, verify_ssl=False) as resp:
			if resp.status != 200:
				msg = f"Roblox has failed to respond with {resp.status} status code."
				raise RuntimeError(msg)
			root = etree.fromstring(await resp.text(), etree.HTMLParser())
		async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={profile['Id']}&size=420x420&format=Png&isCircular=false") as thumbnail:
			thumbnail=await thumbnail.json()
		image_url = thumbnail["data"][0]["imageUrl"]
		profile = root.xpath(".//div[contains(@class, 'profile-container')]")
		if profile is None or len(profile) == 0:
			raise RuntimeError("Failed to get info from Roblox.")
		profile = profile[0]
		avatar = profile.find(".//div[@id='UserAvatar']/span[@class='thumbnail-span-original hidden']/img")
		if image_url:
			em.set_thumbnail(url=image_url)
		divs = profile.xpath(
			"..//"
			"div[@class='section-content profile-header-content']/"
			"div"
		)
		def insert_detail(detail, value, **embed_kwargs):
			if detail and value:
				em.add_field(name=detail, value=value, **embed_kwargs)
		def format_f_detail(details, detail, *, add_s=False):
			tag = f"{detail}s" if add_s else detail
			value = details.get(f"data-{tag}count")
			if not value:
				return None
			#return f"{value} [(view)]({base_url}/friends#!/{detail})"
			return f"[{value}]({base_url}/friends#!/{detail})"
		if divs is not None and len(divs) > 0:
			details = divs[0]
			insert_detail("Friends", format_f_detail(details, "friends"))
			insert_detail("Followers", format_f_detail(details, "followers"))
			insert_detail("Following", format_f_detail(details, "following", add_s=True))
			status = details.get("data-statustext")
			set_status_at = details.get("data-statusdate")
			if status and set_status_at:
				cut = set_status_at.split()[0]
				status += f"\n(set on {cut})"
			insert_detail("Status", status, inline=False)
		stats = profile.xpath(".//ul[@class='profile-stats-container']/li")
		if stats is not None and len(stats) > 0:
			for stat in stats:
				try:
					paras = stat.xpath("./p")
					detail = paras[0].text  # the title
					value = paras[1].text  # the actual value
					insert_detail(detail, value)
				except Exception:
					continue
		emoji = "<:roblox:996951955446439997>"
		premium = profile.xpath(".//span[contains(@class, 'icon-premium')]")
		if premium is not None and len(premium) > 0:
			em.description = f"<:roblox:996951955446439997>"

		# get the description
		description = profile.find(
			".//span[@class='profile-about-content-text linkify']"
		)
		if description is not None:
			if em.description:
				em.description += f"\n\n{description.text}"
			else:
				em.description = description.text

		await ctx.send(embed=em)

	@commands.command(name="roblox", aliases=["rb"], description="lookup a roblox account", brief="username", usage="```Swift\nSyntax: !roblox <username>\nExample: !roblox cop```")
	async def roblox(self, ctx, *, username):
		"""Shows info about a Roblox user."""

		# Web scrape to get the rest of the info in one request instead of 4
		async with ctx.typing():
			try:
				em = await self.get_roblox_profile(ctx=ctx, username=username)
			except RuntimeError as e:
				return await ctx.send(str(e))

	async def send_user_info(self, ctx, data):
		if data["name"]:
			name = f"{data['name']} ({data['login']})"
		else:
			name = data["login"]

		created_at = dateparser.parse(data["created_at"])

		em = discord.Embed(
			title=name,
			description=data["bio"],
			color=0x4078C0,
			url=data["html_url"],
			timestamp=created_at,
		)

		em.set_footer(text="Joined")

		em.set_thumbnail(url=data["avatar_url"])

		em.add_field(
			name="Public Repos",
			value=data["public_repos"] or "No public repos",
			inline=True,
		)

		if data["public_gists"]:
			em.add_field(name="Public Gists", value=data["public_gists"], inline=True)

		value = [
			"Followers: " + str(data["followers"])
			if data["followers"]
			else "Followers: no followers"
		]
		value.append(
			"Following: " + str(data["following"])
			if data["following"]
			else "Following: not following anyone"
		)

		em.add_field(name="Followers/Following", value="\n".join(value), inline=True)

		if data["location"]:
			em.add_field(name="Location", value=data["location"], inline=True)
		if data["company"]:
			em.add_field(name="Company", value=data["company"], inline=True)
		if data["blog"]:
			blog = data["blog"]
			if blog.startswith("https://") or blog.startswith("http://"):
				pass
			else:
				blog = "https://" + blog
			em.add_field(name="Website", value=blog, inline=True)

		await ctx.send(embed=em)
		#except:
			#return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **no account found**"))

	@commands.hybrid_command(name='twitter', aliases=['twit'], with_app_command=True, description="twitter account lookup", brief="username", usage="```Swift\nSyntax: !twitter <username>\nExample: !twitter cop```")
	@commands.guild_only()
	async def twitter(self, ctx, *, username:str):
		logo=self.bot.get_emoji(989747227524210708)
		async with self.bot.session.get('https://twitter.com/i/api/graphql/mCbpQvZAw6zu_4PvuAUVVQ/UserByScreenName?variables=%7B%22screen_name%22%3A%22' + username + '%22%2C%22withSafetyModeUserFields%22%3Atrue%2C%22withSuperFollowsUserFields%22%3Atrue%7D', headers={"Cookie": "guest_id=v1%3A163519131615142822; kdt=dGB7SfUPKd3OrrnASFrmXzaoRVOEwodvrPetTKqS; twid=u%3D247051251; auth_token=12a8e074d3f45bec8e665f3bfd3e6a0f7ff52a0d; ct0=4d22e1f52cd8f01c9acfd59114a937ec533d46a1c9efe08ff394bdf00bad17234b97a57e5d6db9d5244a1ae65fb3fba394fa871f415b88b4267f05dea26b45ef12a51e09db284df1bed6ff324c975a60; lang=en","Sec-Ch-Ua": """-Not.A/Brand"";v=""8"", ""Chromium"";v=""102""","X-Twitter-Client-Language": "en","X-Csrf-Token": "4d22e1f52cd8f01c9acfd59114a937ec533d46a1c9efe08ff394bdf00bad17234b97a57e5d6db9d5244a1ae65fb3fba394fa871f415b88b4267f05dea26b45ef12a51e09db284df1bed6ff324c975a60","Sec-Ch-Ua-Mobile": "?0","Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA","Content-Type": "application/json","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36","X-Twitter-Auth-Type": "OAuth2Session","X-Twitter-Active-User": "yes","Sec-Ch-Ua-Platform": """macOS""","Accept": "*/*","Sec-Fetch-Site": "same-origin","Sec-Fetch-Mode": "cors","Sec-Fetch-Dest": "empty","Referer": "https://twitter.com/markus","Accept-Encoding": "gzip, deflate","Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",}) as userRequest:
			if await userRequest.text() == r'{"data":{}}':
				return await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: [**@{username}**](https://twitter.com/{username}) doesn't exist", color=self.error))
			elif '"reason":"Suspended"' in await userRequest.text():
				return await ctx.reply(embed=discord.Embed(description=f'{self.warn} {ctx.author.mention}: [**@{username}**](https://twitter.com/{username}) is suspended', color=self.error))
			async def down():
				return await self.bot.loop.run_in_executor(None, lambda: self.bot.api.get_user(screen_name=username))
			results=await down()
		if not results:
			embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **@{username}** doesn't exist",color=self.error)
			embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
			await ctx.reply(embed=embed)
		else:
			result = results
			imgurl=f"https://twitter.com/{username}/photo"
			if str(result.protected) == True:
				pv='🔒'
			else:
				pv=''
			if str(result.verified) == True:
				vf="<a:b_verifyblue:926931019339284561>"
			else:
				vf=""
			try:
				username=discord.utils.escape_markdown(username)
			except:
				username=username
			twtav=await http.get(imgurl, res_method="read")
			embed=discord.Embed(title=f"{result.name} (@{username}) {pv} {vf}",description=f"{result.description}", url="https://twitter.com/" + result.screen_name,color=0x1da1f2)
			embed.add_field(name="Tweets",value=num(result.statuses_count),inline=True)
			embed.add_field(name="Following",value=num(result.friends_count),inline=True)
			embed.add_field(name="Followers",value=num(result.followers_count),inline=True)
			embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
			embed.set_footer(text="Joined at "+result.created_at.strftime("%b, %Y"), icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
			try:
				embed.set_thumbnail(url=result.profile_image_url)
			except:
				pass
			link=f"https://twitter.com/{result.screen_name}"
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, emoji=logo, url=link))
			await ctx.reply(embed=embed, view=view)

	@commands.command(name='pfpgen', aliases=['pfpgenerator', 'avgen', 'avsearch'], usage="```Swift\nSyntax: !pfpgen <keywords/tags>\nExample: !pfpgen soft cute```",description="weheartit pfp scraper", brief='query')
	async def pfpgen(self, ctx, *, query=None):
		if query == None:
			return await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.no} {ctx.author.mention}: please provide a query to search"))
		else:
			links = await util.getwhi(query)
		
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
			except:
				return await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.no} {ctx.author.mention}: no results found for **{query}**"))

	@commands.command(name='posts', description='show a users posts on weheartit', usage="```Swift\nSyntax: !posts <user>\nExample: !posts perv```",brief='username')
	async def posts(self, ctx, *, user=None):
		if user == None:
			return await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.no} {ctx.author.mention}: please provide a username to search"))
		else:
			links = await util.getwhiuser(user)
		
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

	@commands.command(name='roleinfo', aliases=['ri', 'rinfo'], description="show information on a role",usage="```Swift\nSyntax: !roleinfo <role>\nExample: !roleinfo users```", brief='role')
	async def roleinfo(self, ctx, role: typing.Union[ discord.Role, str]):
		if isinstance(role, discord.Role):
			r=role
			role=role
			perms = []
			content = discord.Embed(title=f"@{role.name} | #{role.id}")
			content.colour = role.color
			if isinstance(role.icon, discord.Asset):
				content.set_thumbnail(url=role.display_icon)
			elif isinstance(role.icon, str):
				content.title = f"{role.icon} @{role.name} | #{role.id}"
			for perm, allow in iter(role.permissions):
				if allow:
					perms.append(f"`{perm.upper()}`")
			if role.managed:
				if role.tags.is_bot_managed():
					manager = ctx.guild.get_member(role.tags.bot_id)
				elif role.tags.is_integration():
					manager = ctx.guild.get_member(role.tags.integration_id)
				elif role.tags.is_premium_subscriber():
					manager = "Server boosting"
				else:
					manager = "UNKNOWN"
			content.add_field(name="Color", value=str(role.color).upper())
			content.add_field(name="Member count", value=len(role.members))
			content.add_field(name="Created at", value=discord.utils.format_dt(role.created_at, style="R"))
			content.add_field(name="Hoisted", value=str(role.hoist))
			content.add_field(name="Mentionable", value=role.mentionable)
			content.add_field(name="Mention", value=role.mention)
			if perms:
				content.add_field(name="Allowed permissions", value=" ".join(perms), inline=False)
			return await ctx.reply(embed=content)
		if isinstance(role, str):
			roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable()]
			closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
			if closest:
				for role in ctx.guild.roles:
					if role.name.lower() == closest[0].lower():
						role=role
				perms = []
				content = discord.Embed(title=f"@{role.name} | #{role.id}")
				content.colour = role.color
				if isinstance(role.icon, discord.Asset):
					content.set_thumbnail(url=role.display_icon)
				elif isinstance(role.icon, str):
					content.title = f"{role.icon} @{role.name} | #{role.id}"
				for perm, allow in iter(role.permissions):
					if allow:
						perms.append(f"`{perm.upper()}`")
				if role.managed:
					if role.tags.is_bot_managed():
						manager = ctx.guild.get_member(role.tags.bot_id)
					elif role.tags.is_integration():
						manager = ctx.guild.get_member(role.tags.integration_id)
					elif role.tags.is_premium_subscriber():
						manager = "Server boosting"
					else:
						manager = "UNKNOWN"
					manag=f"**Managed By:** {manager}"
				else:
					manag=""
				content.add_field(name="Color", value=str(role.color).upper())
				content.add_field(name="Member count", value=len(role.members))
				content.add_field(name="Created at", value=discord.utils.format_dt(role.created_at, style="R"))
				content.add_field(name="Hoisted", value=str(role.hoist))
				content.add_field(name="Mentionable", value=role.mentionable)
				content.add_field(name="Mention", value=role.mention)
				if perms:
					content.add_field(name="Allowed permissions", value=" ".join(perms), inline=False)
				return await ctx.reply(embed=content)
		return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: I was unable to find a role with the name: **{role}**", color=self.error))

	@commands.command(name='btstatus')
	@commands.is_owner()
	async def btstatus(self, ctx, activity:int, *args):
		"""Changes the bot's status. Syntax: !status type[str] status-to-show[str]"""  # play listen
		if not args:
			await self.bot.change_presence(activity=discord.Activity(
				type=discord.ActivityType.competing, name="!help"))
		else:
			args  # cut the activity's name from the tuple
			name = " ".join(args)
			if activity == 1:
				await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=name))
			elif activity == 3:
				await self.bot.change_presence(
					activity=discord.Activity(type=discord.ActivityType.listening, name=name))
			elif activity == 4:
				await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=name))
			elif activity == 2:
				await self.bot.change_presence(
					activity=discord.Activity(url="https://twitch.tv/rival", type=discord.ActivityType.streaming, name=name))
			elif activity == 5:
				await self.bot.change_presence(
					activity=discord.Activity(type=discord.ActivityType.competing, name=name))
			else:
				await ctx.send(embed=discord.Embed(title='status types', description=f"1: `playing`\n2: `streaming`\n3: `listening`\n4: `watching`\n5: `competing`"))
				return  # don't send the success message
		await ctx.send("Status updated. ✅")

	@commands.command(name='serverinfo',aliases=['si'], description='show info about a guild',brief='guild')
	async def serverinfo(self, ctx, *, guild_name=None):
		guild = None
		if guild_name == None:
			guild = ctx.guild
		else:
			for g in self.bot.guilds:
				if g.name.lower() == guild_name.lower():
					guild = self.bot.get_guild(g.id)
					break
				if str(g.id) == str(guild_name):
					guild = self.bot.get_guild(g.id)
					break
		if guild == None:
			guild=ctx.guild
			await util.send_error(ctx, f"couldn't find a guild named `{guild_name}`")
			guild=ctx.guild
		server_embed = discord.Embed(color=self.color).set_thumbnail(url=guild.icon)
		server_embed.title = guild.name
		last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
		if last_boost.premium_since is not None:
			bboost = (f"`{last_boost}` - {discord.utils.format_dt(last_boost.premium_since, style='R')}")
		else:
			bboost = "No Latest Booster"
		gcreated=guild.created_at
		server_embed.description = f"**Shard {guild.shard_id+1}/{self.bot.shard_count}**\nServer Created {discord.utils.format_dt(guild.created_at, style='R')}"
		online_members = 0
		bot_member     = 0
		bot_online     = 0
		for member in guild.members:
			if member.bot:
				bot_member += 1
				if not member.status == discord.Status.offline:
						bot_online += 1
				continue
			if not member.status == discord.Status.offline:
				online_members += 1
		# bot_percent = "{:,g}%".format((bot_member/len(guild.members))*100)
		user_string = "***Users:*** {:,} ({:,g}%)".format(
				online_members,
				round((online_members/(len(guild.members) - bot_member) * 100), 2)
		)
		b_string = "bot" if bot_member == 1 else "bots"
		user_string += "\n***Bots:*** {:,} ({:,g}%)".format(
				bot_online,
				round((bot_online/bot_member)*100, 2)
		)
		total_users="\n***Total:*** {:,}".format(len(guild.members))
		if guild.banner:
			banner=f"[Banner]({guild.banner})"
		else:
			banner=""
		if guild.splash:
			splash=f"[Splash]({guild.splash})"
		else:
			splash=""
		if guild.icon:
			icon=f"[Icon]({guild.icon})"
		else:
			icon=""
		bcounter=0
		for member in guild.members:
			if member.premium_since:
				bcounter+=1
		total_count = len(guild.text_channels) + len(guild.voice_channels) + len(guild.categories)
		bcount="{}/{}".format(guild.premium_tier, guild.premium_subscription_count)
		#server_embed.add_field(name="Members", value="{:,}/{:,} online ({:.2f}%)\n{:,} {} ({}%)".format(online_members, len(guild.members), bot_percent), inline=True)
		if await self.bot.db.execute("""SELECT * FROM dnr WHERE user_id = %s""", guild.owner.id):
			emote="<a:Money:964673324011638784>"
		else:
			emote=""
		server_embed.add_field(name="Owner", value=guild.owner.name + "#" + guild.owner.discriminator+emote, inline=True)
		server_embed.add_field(name="Members", value=user_string+total_users, inline=True)
		server_embed.add_field(name="Info", value=f"**Verification: **{guild.verification_level}\n**Level:** {bcount}\n**Large:** {guild.large}", inline=True)
		server_embed.add_field(name="Design", value=f"{icon}\n{banner}\n{splash}", inline=True)
		chandesc = "**Categories:** {:,}\n**Text:** {:,}\n**Voice:** {:,} ".format(len(guild.categories), len(guild.text_channels), len(guild.voice_channels))
		server_embed.add_field(name=f"Channels({total_count})", value=f"**Categories:** {len(guild.categories)}\n**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}", inline=True)
		server_embed.add_field(name="Counts", value=f"**Roles:** {str(len(guild.roles))}\n**Emojis:** {str(len(guild.emojis))}\n**Boosters:** {bcounter}", inline=True)
		
			# Find out where in our join position this server is
		joinedList = []
		popList    = []
		for g in self.bot.guilds:
			joinedList.append({ 'ID' : g.id, 'Joined' : g.me.joined_at })
			popList.append({ 'ID' : g.id, 'Population' : len(g.members) })
		
		# sort the guilds by join date
		joinedList = sorted(joinedList, key=lambda x:x["Joined"].timestamp() if x["Joined"] != None else -1)
		popList = sorted(popList, key=lambda x:x['Population'], reverse=True)
			
		check_item = { "ID" : guild.id, "Joined" : guild.me.joined_at }
		total = len(joinedList)
		position = joinedList.index(check_item) + 1
		#server_embed.add_field(name="Join Position", value="{:,} of {:,}".format(position, total), inline=True)
		
		# Get our population position
		gid=guild.id
		check_item = { "ID" : guild.id, "Population" : len(guild.members) }
		ttotal = len(popList)
		pposition = popList.index(check_item) + 1
			#server_embed.add_field(name="Population Rank", value="{:,} of {:,}".format(position, total), inline=True)
		server_embed.set_footer(text="Join Position: {:,}/{:,} ∙ Population Rank: {:,}/{:,}".format(position, total, pposition, ttotal))
		server_embed.set_author(name=f"ID:{gid}")
			
		# emojitext = ""
		# emojifields = []
		# disabledemojis = 0
		# twitchemojis = 0
		# for i,emoji in enumerate(guild.emojis):
		# 	if not emoji.available:
		# 		disabledemojis += 1
		# 		continue
		# 	if emoji.managed:
		# 		twitchemojis += 1
		await ctx.send(embed=server_embed)

	@commands.group(description="server info commands")
	@commands.guild_only()
	async def server(self, ctx):
		if ctx.invoked_subcommand is None:
			m=ctx.message.content
			m=m.strip(f"{ctx.prefix}{ctx.command}")
			m=m.strip(f"{ctx.prefix}")
			m=m.strip(f"{ctx.command}")
			m=m.strip("<@1002294763241885847>")
			m=m.strip("server")
			m=m.strip("serverinfo")
			m=m.strip("si")
			m=m.replace(" server","",1)
			m=m.replace(" serverinfo","",1)
			m=m.replace(" si","",1)
			if m.startswith(" "):
				m=m.replace(" ","",1)
			if len(m) > 0:
				guild_name=m
				guild = None
				if guild_name == None:
					guild = ctx.guild
				else:
					for g in self.bot.guilds:
						if g.name.lower() == guild_name.lower():
							guild = self.bot.get_guild(g.id)
							break
						if str(g.id) == str(guild_name):
							guild = self.bot.get_guild(g.id)
							break
				if guild == None:
					guild=ctx.guild
					await util.send_error(ctx, f"couldn't find a guild named `{guild_name}`")
			else:
				guild=ctx.guild
			server_embed = discord.Embed(color=self.color).set_thumbnail(url=guild.icon)
			server_embed.title = guild.name
			last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
			if last_boost.premium_since is not None:
				bboost = (f"`{last_boost}` - {discord.utils.format_dt(last_boost.premium_since, style='R')}")
			else:
				bboost = "No Latest Booster"
			gcreated=guild.created_at
			server_embed.description = f"Server Created {discord.utils.format_dt(guild.created_at, style='R')}"
			online_members = 0
			bot_member     = 0
			bot_online     = 0
			for member in guild.members:
				if member.bot:
					bot_member += 1
					if not member.status == discord.Status.offline:
							bot_online += 1
					continue
				if not member.status == discord.Status.offline:
					online_members += 1
			# bot_percent = "{:,g}%".format((bot_member/len(guild.members))*100)
			user_string = "***Users:*** {:,} ({:,g}%)".format(
					online_members,
					round((online_members/(len(guild.members) - bot_member) * 100), 2)
			)
			b_string = "bot" if bot_member == 1 else "bots"
			user_string += "\n***Bots:*** {:,} ({:,g}%)".format(
					bot_online,
					round((bot_online/bot_member)*100, 2)
			)
			total_users="\n***Total:*** {:,}".format(len(guild.members))
			if guild.banner:
				banner=f"[Banner]({guild.banner})"
			else:
				banner=""
			if guild.splash:
				splash=f"[Splash]({guild.splash})"
			else:
				splash=""
			if guild.icon:
				icon=f"[Icon]({guild.icon})"
			else:
				icon=""
			bcounter=0
			for member in guild.members:
				if member.premium_since:
					bcounter+=1
			total_count = len(guild.text_channels) + len(guild.voice_channels) + len(guild.categories)
			bcount="{}/{}".format(guild.premium_tier, guild.premium_subscription_count)
			#server_embed.add_field(name="Members", value="{:,}/{:,} online ({:.2f}%)\n{:,} {} ({}%)".format(online_members, len(guild.members), bot_percent), inline=True)
			if await self.bot.db.execute("""SELECT * FROM dnr WHERE user_id = %s""", guild.owner.id):
				emote="<a:Money:964673324011638784>"
			else:
				emote=""
			server_embed.add_field(name="Owner", value=guild.owner.name + "#" + guild.owner.discriminator+emote, inline=True)
			server_embed.add_field(name="Members", value=user_string+total_users, inline=True)
			server_embed.add_field(name="Info", value=f"**Verification: **{guild.verification_level}\n**Level:** {bcount}\n**Large:** {guild.large}", inline=True)
			server_embed.add_field(name="Design", value=f"{icon}\n{banner}\n{splash}", inline=True)
			chandesc = "**Categories:** {:,}\n**Text:** {:,}\n**Voice:** {:,} ".format(len(guild.categories), len(guild.text_channels), len(guild.voice_channels))
			server_embed.add_field(name=f"Channels({total_count})", value=f"**Categories:** {len(guild.categories)}\n**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}", inline=True)
			server_embed.add_field(name="Counts", value=f"**Roles:** {str(len(guild.roles))}\n**Emojis:** {str(len(guild.emojis))}\n**Boosters:** {bcounter}", inline=True)
			

			# Find out where in our join position this server is
			joinedList = []
			popList    = []
			for g in self.bot.guilds:
				joinedList.append({ 'ID' : g.id, 'Joined' : g.me.joined_at })
				popList.append({ 'ID' : g.id, 'Population' : len(g.members) })
			
			# sort the guilds by join date
			joinedList = sorted(joinedList, key=lambda x:x["Joined"].timestamp() if x["Joined"] != None else -1)
			popList = sorted(popList, key=lambda x:x['Population'], reverse=True)
			
			check_item = { "ID" : guild.id, "Joined" : guild.me.joined_at }
			total = len(joinedList)
			position = joinedList.index(check_item) + 1
			#server_embed.add_field(name="Join Position", value="{:,} of {:,}".format(position, total), inline=True)
			
			# Get our population position
			gid=guild.id
			check_item = { "ID" : guild.id, "Population" : len(guild.members) }
			ttotal = len(popList)
			pposition = popList.index(check_item) + 1
			#server_embed.add_field(name="Population Rank", value="{:,} of {:,}".format(position, total), inline=True)
			server_embed.set_footer(text="Join Position: {:,}/{:,} ∙ Population Rank: {:,}/{:,}".format(position, total, pposition, ttotal))
			server_embed.set_author(name=f"ID:{gid}")
			
			emojitext = ""
			emojifields = []
			disabledemojis = 0
			twitchemojis = 0
			for i,emoji in enumerate(guild.emojis):
				if not emoji.available:
					disabledemojis += 1
					continue
				if emoji.managed:
					twitchemojis += 1

			if len(server_embed.fields):
				await ctx.send(embed=server_embed)
			

	@server.command(name="avatar", aliases=["icon", "a"], description="send the guild's current avatar")
	async def server_avatar(self, ctx):
		""" Get the current server icon """
		if not ctx.guild.icon:
			return await ctx.send(embed=discord.Embed(color=0x303135, description=f"this server does not have a avatar"))
		embed=discord.Embed(color=0x303135, description=f"[{ctx.guild.name}'s icon]({ctx.guild.icon})")
		embed.set_image(url=ctx.guild.icon)
		await ctx.send(embed=embed)

	@server.command(name="banner", aliases=['ban', 'b'], description="send the guild's current banner")
	async def server_banner(self, ctx):
		""" Get the current banner image """
		if not ctx.guild.banner:
			return await ctx.send(embed=discord.Embed(color=0x303135, description="this server does not have a banner"))
		await ctx.send(embed=discord.Embed(color=0x303135, description=f"[{ctx.guild.name}'s banner]({ctx.guild.banner})").set_image(url=ctx.guild.banner))

	@server.command(name='splash', aliases=['invite', 'i', 's'], description="send the guild's current invite background")
	async def server_splash(self, ctx):
		guild=ctx.guild
		if not guild.splash:
			return await ctx.send(embed=discord.Embed(color=0x303135, description=f"{guild.name} has no splash"))
		await ctx.send(embed=discord.Embed(color=0x303135, description=f"[{guild.name}'s splash]({guild.splash})").set_image(url=guild.splash.url))

	@commands.command()
	async def vvoice(self, ctx):
		await ctx.author.voice.channel.connect()

	@commands.group(name='boosters', aliases=['boosts'], description="shows current boosters")
	@commands.guild_only()
	async def boosters(self, ctx):
		if ctx.invoked_subcommand is None:
			content=discord.Embed(title=f"{ctx.guild.name}'s boosters", color=self.color)
			rows=[]
			if len(ctx.guild.premium_subscribers) == 0:
				rows.append('Guild Has No Boosters')
			else:
				premium_subscribers = sorted(ctx.guild.premium_subscribers, key=lambda m: m.premium_since, reverse=True)
				for i,booster in enumerate(premium_subscribers, start=1):
					rows.append(f"`{i}` **{discord.utils.escape_markdown(booster.name)}#{booster.discriminator}** - {discord.utils.format_dt(booster.premium_since, style='R')}")
				await util.send_as_pages(ctx, content, rows)

	@boosters.command(name="lost", aliases=['l'], description="show lost boosters")
	async def boosters_lost(self, ctx):
		rows=[]
		i=0
		data=await self.bot.db.execute("""SELECT user_id, ts FROM lostboost WHERE guild_id = %s ORDER BY ts DESC""", ctx.guild.id)
		for user_id, ts in data:
			user=self.bot.get_user(user_id)
			if not user:
				user=await self.bot.fetch_user(user_id)
			i+=1
			rows.append(f"`{i}` **{user.name}#{user.discriminator}** - {discord.utils.format_dt(ts, style='R')}")
		if rows:
			content=discord.Embed(color=self.color, title=f"boosters lost")
			await util.send_as_pages(ctx, content, rows)
		else:
			await util.send_error(ctx, f"no lost boosters found")

	@commands.command(name='bans', aliases=['banlist'], description="send the guild's ban list")
	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	@commands.bot_has_permissions(manage_guild=True)
	async def bans(self, ctx):
		rows=[]
		bans=[]
		try:
			async for ban in ctx.guild.bans(limit=500):
				try:
					bans.append(f"**{discord.utils.escape_markdown(ban.user.name)}#{ban.user.discriminator}**")
				except:
					bans.append(f"**{ban.user.name}#{ban.user.discriminator}**")
			if len(bans) == 0:
				rows.append("No Bans")
			for i, ban in enumerate(bans, start=1):
				rows.append(f"`{i}` {ban}")
			content=discord.Embed(title=f"{ctx.guild.name}'s bans", color=self.color).set_footer(text=f"{len(bans)} Bans In Total")
			await util.send_as_pages(ctx, content, rows)
		except:
			return util.send_failure(ctx, f"{ctx.author.mention}: **no bans found in guild**")

	@commands.command(name='ratio')
	async def ratio(self, ctx):
		guild=ctx.guild
		online_members = 0
		bot_member     = 0
		bot_online     = 0
		for member in guild.members:
			if member.bot:
				bot_member += 1
				if not member.status == discord.Status.offline:
						bot_online += 1
				continue
			if not member.status == discord.Status.offline:
				online_members += 1
		# bot_percent = "{:,g}%".format((bot_member/len(guild.members))*100)
		offlineuser=100-round((online_members/(len(guild.members) - bot_member) * 100), 2)
		user_string = "***Users:*** {:,} \n**Online:**{:,g}".format(
				online_members,
				round((online_members/(len(guild.members) - bot_member) * 100), 2)
		)
		offlinebot=100-round((bot_online/bot_member)*100, 2)
		b_string = "bot" if bot_member == 1 else "bots"
		user_string += "\n***Bots:*** {:,} **Online:** {:,g}".format(
				bot_online,
				round((bot_online/bot_member)*100, 2)
		)
		total_users="\n***Total:*** {:,}".format(len(guild.members))
		return await ctx.send(embed=discord.Embed(title=f"{ctx.guild.name}'s ratio", description=f"**Online Users:** {online_members} - {round((online_members/(len(guild.members) - bot_member) * 100), 2)}%\n**Offline Users:** {len(guild.members)-online_members} - {round((bot_online/bot_member)*100, 2)}%\n**Online Bots:** {bot_online} - {round((bot_online/bot_member)*100, 2)}%\n**Offline Bots:** {bot_member - bot_online} - {offlinebot}%"))

	@commands.command(name='muted', aliases=['mutes', 'timedout'], description="send the guild's current muted members", extras={'perms': 'moderate_members'})
	@commands.has_permissions(moderate_members=True)
	@commands.bot_has_permissions(moderate_members=True)
	async def muted(self, ctx:commands.Context):
		rows=[]
		content=discord.Embed(title="Muted Members", color=self.color)
		for member in ctx.guild.members:
			if member.is_timed_out():
				rows.append(f"{member.mention}")
		if rows:
			await util.send_as_pages(ctx, content, rows)
		else:
			await ctx.send(embed=discord.Embed(description="no muted members", color=self.color))

	@commands.command(name='untimeoutall', aliases=['unmuteall', 'massunmute', 'uma', 'uta'], description="unmutes all muted members", extras={'perms': 'moderate_members'})
	@commands.has_permissions(moderate_members=True)
	@commands.bot_has_permissions(moderate_members=True)
	async def untimeoutall(self, ctx):
		suck=0
		fail=0
		rs=f"mass unmute by {ctx.author}"
		for member in ctx.guild.members:
			if member.is_timed_out():
				try:
					await member.timeout(discord.utils.utcnow(), reason=rs)
					suck+=1
				except:
					fail+1
					pass
		if fail > 0:
			fa=", and failed to unmute {} users".format(fail)
		else:
			fa=""
		await ctx.send(embed=discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: **unmuted {suck} users{fa}**", color=self.good))

	@commands.command(name='dm')
	@commands.is_owner()
	async def dm(self, ctx, user_id: int, *, message: str):
		""" DM the user of your choice """
		user = self.bot.get_user(user_id)
		if not user:
			return await ctx.send(f"Could not find any UserID matching **{user_id}**")

		try:
			await user.send(message)
			await ctx.send(f"✉️ Sent a DM to **{user_id}**")
		except discord.Forbidden:
			await ctx.send("This user might be having DMs blocked or it's a bot account...")

	@commands.command(name='contact', description="contacts the bot support team", brief="message", aliases=['support', 'feedback'])
	@commands.guild_only()
	async def contact(self, ctx, *, message: str):
		#user = self.bot.get_user(330445977183977483)
		try:
			support=self.bot.get_channel(926556244897071115)
			guild=ctx.guild
			embed = discord.Embed(title=ctx.author, description=f"{message}\n\n{await self.geninvite(ctx.guild.id)}", color=0x303135)
			embed.set_footer(text=f"{ctx.guild.name}")
			#await user.send(f"{ctx.channel.id}", embed=embed)
			invlink="https://discord.gg/ER2m3zfz"
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'join support server', url=invlink))
			await support.send(content=f"user: {ctx.author.id}\nchannel: {ctx.channel.id}\nguild: {ctx.guild.id}", embed=embed)
			await ctx.send(view=view, embed=discord.Embed(title=f"Contacted The Support Team", description=f"with the message {message}\n**Support Server:** https://discord.gg/d8qZXJFkUG").set_thumbnail(url=self.bot.user.display_avatar).set_footer(text="Prefix = !"))
		except:
			pass

	@commands.command(name='vanity', description="check if a vanity is available", brief="vanity", extras={'perms': 'administrator'})
	@commands.guild_only()
	@commands.has_permissions(administrator=True)
	async def vanity(self, ctx, x: str):
		if x:
			async with aiohttp.ClientSession() as session:
				async with session.get(f'https://discord.com/api/v9/invites/{x}', headers=util.getHeaders(token=token)) as r:
					if r.status == 200:
						return await util.send_bad(ctx, f"[{x}](https://discord.gg/{x}) is **unavailable**")
					if r.status == 404:
						await util.send_good(ctx, f"[{x}](https://discord.gg/{x}) is **available**")
#		except BaseException as err:
#			await ctx.send(embed=discord.Embed(description="discord is trash and blacklisted the proxy", color=0x303135))
#			print(err)

	@commands.command(name='forcevanity')
	@commands.is_owner()
	async def forcevanity(self, ctx, content:str):
		if ctx.author.id == 714703136270581841 or 888156435760943104:
			try:
				guild = ctx.guild
				await guild.edit(vanity_code=content)
				embed=discord.Embed(title=f"___**{self.bot.user.name}#{self.bot.user.discriminator}**___", description=f"*vanity changed to **{content}***", color=0x303135)
				embed.set_thumbnail(url=ctx.author.display_avatar)
				await ctx.send(embed=embed)
			except discord.Forbidden:
				pass
				server=ctx.message.guild
				em=discord.Embed(title=f"___**{self.bot.user.name}#{self.bot.user.discriminator}**___", description=f"***{server.name}** doesn't have enough boosts, it has **{server.premium_subscription_count}/14***", color=0x303135)
				em.set_thumbnail(url=ctx.author.display_avatar)
				await ctx.send(embed=em)
			except discord.HTTPException:
				pass
				server=ctx.message.guild
				em=discord.Embed(title=f"___**{self.bot.user.name}#{self.bot.user.discriminator}**___", description=f"https://discord.gg/{content} is either terminated or taken").set_thumbnail(url=ctx.guild.icon).set_footer(text=f"Requested by {ctx.author}")
				await ctx.send(embed=em)
		else:
			embed = discord.Embed(description="**Missing Permissions `guild_owner`**").set_thumbnail(url=self.bot.user.display_avatar)
			await ctx.send(embed=embed)

	@commands.command(name='setvanity', description="change guild vanity", extras={'perms': 'Guild Owner'}, brief="vanity",usage="```Swift\nSyntax: !setvanity <vanity>\nExample: !setvanity rival```")
	@commands.has_permissions(administrator=True)
	async def setvanity(self, ctx, content:str):
		if ctx.author == ctx.guild.owner:
			try:
				guild = ctx.guild
				await guild.edit(vanity_code=content)
				embed=discord.Embed(description=f"*vanity changed to **{content}***", color=0x303135)
				embed.set_thumbnail(url=ctx.author.display_avatar)
				await ctx.send(embed=embed)
			except discord.Forbidden:
				server=ctx.message.guild
				em=discord.Embed(description=f"***{server.name}** doesn't have enough boosts, it has **{server.premium_subscription_count}/14***", color=0x303135)
				em.set_thumbnail(url=ctx.author.display_avatar)
				return await ctx.send(embed=em)
			except discord.HTTPException:
				server=ctx.message.guild
				em=discord.Embed(description=f"https://discord.gg/{content} is either terminated or taken").set_thumbnail(url=ctx.guild.icon).set_footer(text=f"Requested by {ctx.author}")
				return await ctx.send(embed=em)
			except:
				return await util.send_error(ctx, f"vanity can't be set to {content}")
		else:
			embed = discord.Embed(description="**Missing Permissions `guild_owner`**").set_thumbnail(url=self.bot.user.display_avatar)
			await ctx.send(embed=embed)

	@commands.command(name='seticon', aliases=["changeserverav", 'changeicon', 'setavatar'], description="change guild banner", extras={'perms':'administrator'}, brief='url/image', usage='```Syntax: !seticon <url/image>\nExample: !seticon https://rival.rocks/image.png```')
	@commands.guild_only()
	@commands.has_permissions(administrator=True)
	async def seticon(self, ctx, url: str = None):
		if url is None and len(ctx.message.attachments) == 1:
			url = ctx.message.attachments[0].url
		else:
			url = url.strip("<>") if url else None
		try:
			bio = await http.get(url, res_method="read")
			guild = ctx.guild
			await guild.edit(icon=bio)
			embed=discord.Embed(title=f"___**{self.bot.user.name}#{self.bot.user.discriminator}**___", description=f"*guild icon changed to*", color=0x303135)
			embed.set_thumbnail(url=url)
			await ctx.send(embed=embed)
		except aiohttp.InvalidURL:
			await ctx.send("The URL is invalid...")
		except discord.HTTPException as err:
			await ctx.send(err)
		except TypeError:
			await ctx.send("You need to either provide an image URL or upload one with the command")
		except:
			await ctx.send("This URL does not contain a useable image")

	@commands.command(name='setbanner', description="change guild banner", extras={'perms':'administrator'}, brief='url/image', usage='```Syntax: !setbanner <url/image>\nExample: !setbanner https://rival.rocks/image.png```')
	@commands.has_permissions(administrator=True)
	async def setbanner(self, ctx, url: str = None):
		if url is None and len(ctx.message.attachments) == 1:
			url = ctx.message.attachments[0].url
		else:
			url = url.strip("<>") if url else None
		try:
			bio = await http.get(url, res_method="read")
			guild = ctx.guild
			await guild.edit(banner=bio)
			embed=discord.Embed(description=f"**guild banner changed to:**", color=self.good)
			embed.set_thumbnail(url=url)
			await ctx.send(embed=embed)
		except aiohttp.InvalidURL:
			await ctx.send("The URL is invalid...")
		except discord.HTTPException as err:
			await ctx.send(err)
		except TypeError:
			await ctx.send("You need to either provide an image URL or upload one with the command")
		except:
			await ctx.send("This URL does not contain a useable image")

	@commands.command(name='setsplash', aliases=['setinvite'], description="change guild splash", extras={'perms':'administrator'}, brief='url/image', usage='```Syntax: !setsplash <url/image>\nExample: !setsplash https://rival.rocks/image.png```')
	@commands.has_permissions(administrator=True)
	async def setsplash(self, ctx, url: str = None):
		""" Change avatar_ """
		if url is None and len(ctx.message.attachments) == 1:
			url = ctx.message.attachments[0].url
		else:
			url = url.strip("<>") if url else None

		try:
			bio = await http.get(url, res_method="read")
			guild = ctx.guild
			await guild.edit(splash=bio)
			embed=discord.Embed(description=f"**guild splash changed to:**", color=self.good)
			embed.set_thumbnail(url=url)
			await ctx.send(embed=embed)
		except aiohttp.InvalidURL:
			await ctx.send("The URL is invalid...")
		except discord.HTTPException as err:
			await ctx.send(err)
		except TypeError:
			await ctx.send("You need to either provide an image URL or upload one with the command")
		except:
			await ctx.send("This URL does not contain a useable image")

	@commands.command(name='setdiscoverysplash', aliases=['setdiscovery'], description="change guild discovery splash", extras={'perms':'administrator'}, brief='url/image', usage='```Syntax: !setdiscoverysplash <url/image>\nExample: !setdiscoverysplash https://rival.rocks/image.png```')
	@commands.has_permissions(administrator=True)
	async def setdiscoverysplash(self, ctx, url: str = None):
		if url is None and len(ctx.message.attachments) == 1:
			url = ctx.message.attachments[0].url
		else:
			url = url.strip("<>") if url else None

		try:
			bio = await http.get(url, res_method="read")
			guild = ctx.guild
			await guild.edit(discovery_splash=bio)
			embed=discord.Embed(description=f"**guild discovery splash changed to:**", color=self.good)
			embed.set_thumbnail(url=url)
			await ctx.send(embed=embed)
		except aiohttp.InvalidURL:
			await ctx.send("The URL is invalid...")
		except discord.HTTPException as err:
			await ctx.send(err)
		except TypeError:
			await ctx.send("You need to either provide an image URL or upload one with the command")
		except:
			await ctx.send("This URL does not contain a useable image")

	@commands.group(name='change')
	@commands.is_owner()
	async def change(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send_help(str(ctx.command))

	@change.command(name="playing")
	@commands.is_owner()
	async def change_playing(self, ctx, *, playing: str):
		""" Change playing status. """
		status = self.config["status_type"].lower()
		status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

		activity = self.config["activity_type"].lower()
		activity_type = {"listening": 2, "watching": 3, "competing": 5}

		try:
			await self.bot.change_presence(
				activity=discord.Game(
					type=activity_type.get(activity, 0), name=playing
				),
				status=status_type.get(status, discord.Status.online)
			)
			self.change_config_value("playing", playing)
			await ctx.send(f"Successfully changed playing status to **{playing}**")
		except discord.InvalidArgument as err:
			await ctx.send(err)
		except Exception as e:
			await ctx.send(e)

	@change.command(name="username")
	@commands.is_owner()
	async def change_username(self, ctx, *, name: str):
		""" Change username. """
		try:
			await self.bot.user.edit(username=name)
			await ctx.send(f"Successfully changed username to **{name}**")
		except discord.HTTPException as err:
			await ctx.send(err)

	@change.command(name="nickname")
	@commands.is_owner()
	async def change_nickname(self, ctx, *, name: str = None):
		""" Change nickname. """
		try:
			await ctx.guild.me.edit(nick=name)
			if name:
				await ctx.send(f"Successfully changed nickname to **{name}**")
			else:
				await ctx.send("Successfully removed nickname")
		except Exception as err:
			await ctx.send(err)

	@change.command(name="avatar")
	@commands.is_owner()
	async def change_avatar(self, ctx, url: str = None):
		""" Change avatar_ """
		return await util.send_error(ctx,f"Error 404 API Decommissioned Please change your application details via the Developer Portal")
		if url is None and len(ctx.message.attachments) == 1:
			url = ctx.message.attachments[0].url
		else:
			url = url.strip("<>") if url else None

		try:
			bio = await http.get(url, res_method="read")
			await self.bot.user.edit(avatar=bio)
			await ctx.send(f"Successfully changed the avatar_ Currently using:\n{url}")
		except aiohttp.InvalidURL:
			await ctx.send("The URL is invalid...")
		except discord.HTTPException as err:
			await ctx.send(err)
		except TypeError:
			await ctx.send("You need to either provide an image URL or upload one with the command")
		except:
			await ctx.send("This URL does not contain a useable image")

	@commands.command(name='guildfilter')
	@commands.is_owner()
	async def guildfilter(self, ctx, mc:int):
		l=await self.bot.db.execute("SELECT guild_id FROM bump", as_list=True)
		glist={856775654543196163, 924590565134327828, 852312486349766716, 947319129369620522}
		guilds=[guild async for guild in self.bot.fetch_guilds(limit=150)]
		num = 0
		for i, (guild) in enumerate(
			sorted(self.bot.guilds, key=lambda x: x.member_count or 0, reverse=True), start=1
		):
		#for guild in sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True):
			g=self.bot.get_guild(guild.id)
			if g.member_count <= mc and g.member_count != None and g.id != 918445509599977472 and g.id not in glist and g.id not in l:
				num += 1
				await guild.leave()
		await ctx.send(embed=discord.Embed(color=0x303135, description="Successfully left **`%s`** guilds below **`%s`** members" % (num, mc)))

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		if len(guild.members) is None:
			mc=guild.member_count
		else:
			mc=len(guild.members)
		if guild.id == 968277470631579689:
			return
		# ch=self.bot.get_channel(1008282997365153854)
		# try:
		# 	gname=discord.utils.escape_markdown(str(guild.name))
		# except:
		# 	gname=guild.name
		# try:
		# 	gowner=discord.utils.escape_markdown(str(guild.owner))			
		# except:
		# 	gowner=str(guild.owner)
		#if guild.owner.id in self.owners:
			#await guild.leave()
		if self.filterguilds==True:
			whitelist=await self.bot.db.execute("SELECT * FROM bump WHERE guild_id = %s", guild.id, one_value=True)
			if whitelist:
				return
				# channel = discord.utils.get(guild.text_channels, position = 0)
				# invite=await self.geninvite(guild.id)
				# if await self.bot.db.execute("""SELECT * FROM guild_invite WHERE guild_id = %s""", guild.id):
				# 	await self.bot.db.execute("""DELETE FROM guild_invite WHERE guild_id = %s""", guild.id)
				# inv=f"{invite}"
				# await self.bot.db.execute("""INSERT INTO guild_invite (guild_id, invite) VALUES (%s, %s) ON DUPLICATE KEY UPDATE invite = invite""", guild.id, inv)
				# # return await ch.send(embed=discord.Embed(color=self.color, description=f"joined **{gname}**, owned by **{gowner}** with **{mc}** members").set_footer(text=f"ID: {guild.id}"))
			try:	
				if len(guild.members) < 100 and not whitelist and guild.id != 968277470631579689:
					owner=guild.owner.id
					try:
						for channel in guild.text_channels:
							try:
								channel=guild.get_channel(channel.id)
								await channel.send(embed=discord.Embed(color=0x303135, description='leaving due to being below requirement of 100 members'))
								return await guild.leave()
							except:
								pass
							self.filtered.append(guild.id)
						return await guild.leave()
					except:
						await guild.leave()
						pass
				# else:
				# 	channel = discord.utils.get(guild.text_channels, position = 0)
				# 	embed = discord.Embed(title=f"Joined", description=f"Name: {guild.name}\n ID:{guild.id}\n Owner: {guild.owner}\n MemberCount: {len(guild.members)} members", color=self.color).set_thumbnail(url=self.bot.user.display_avatar)
				# 	return await bot_channel.send(embed=embed)
					#return await ch.send(embed=discord.Embed(color=self.color, description=f"joined **{gname}**, owned by **{gowner}** with **{mc}** members").set_footer(text=f"ID: {guild.id}"))
			except Exception as e:
				print(e)
				pass

	# @commands.Cog.listener()
	# async def on_guild_remove(self, guild: discord.Guild):
	# 	if guild.id in self.filtered:
	# 		return
	# 	bot_channel = self.bot.get_channel(918445509599977475)
	# 	embed = discord.Embed(title=f"Left", description=f"Name: {guild.name}\n ID:{guild.id}\n Owner: {guild.owner}\n MemberCount: {len(guild.members)} members", color=self.color).set_thumbnail(url=self.bot.user.display_avatar)
	# 	await bot_channel.send(embed=embed)  

	@commands.command(name='disallow')
	@commands.is_owner()
	async def disallow(self, ctx, guild:int):
		if not await self.bot.db.execute("SELECT * FROM bump WHERE guild_id = %s", guild, one_value=True,):
			raise exceptions.Warning(f"guild `{guild}` hasn't been allowed")
		await self.bot.db.execute(
			"DELETE FROM bump WHERE guild_id = %s",
			guild,
		)
		await ctx.reply(embed=discord.Embed(color=self.good, description=f'unwhitelisted guild {guild}'))


	@commands.command(name='allow', hidden=True)
	@commands.is_owner()
	async def allow(self, ctx, guild:int):
		if await self.bot.db.execute("SELECT * FROM bump WHERE guild_id = %s", guild, one_value=True):
			raise exceptions.Warning(f"guild `{guild}` already allowed")

		await self.bot.db.execute(
			"INSERT INTO bump VALUES(%s)",
			guild,
		)
		await ctx.reply(embed=discord.Embed(color=self.good, description=f'whitelisted guild {guild}'))

	@commands.command(name='disallow', hidden=True)
	@commands.is_owner()
	async def disallow(self, ctx, guild:int):
		if not await self.bot.db.execute("SELECT * FROM bump WHERE guild_id = %s", guild, one_value=True,):
			raise exceptions.Warning(f"guild `{guild}` hasn't been allowed")
		await self.bot.db.execute(
			"DELETE FROM bump WHERE guild_id = %s",
			guild,
		)
		await ctx.reply(embed=discord.Embed(color=self.good, description=f'unwhitelisted guild {guild}'))

	@commands.command(hidden=True,name='stopbot')
	@commands.is_owner()
	async def stopbot(self, ctx):
		await self.bot.close()

	@commands.group(name='role', description="give or take a role from a member", extras={'perms': 'manage roles'}, brief="member, role", invoke_without_command=True)
	@commands.guild_only()
	@commands.has_permissions(manage_roles=True)
	async def role(self, ctx, member: typing.Union[discord.Member, str], *, role: typing.Union[ discord.Role, discord.Member, str]):
		if ctx.invoked_subcommand is None:
			try:
				if isinstance(role, discord.Role):
					r=role
					if isinstance(member, discord.Member):
						pass
					else:
						return await util.send_error(ctx, f"no member found named `{member}`")
					try:
						if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
							if member.id == ctx.author.id:
								if role.position >= ctx.author.top_role.position:
									return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then your top role {ctx.author.mention}", color=self.color))
							return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then your top role {ctx.author.mention}", color=self.color))
						if member.top_role.position >= ctx.author.top_role.position and member.id != ctx.author.id and ctx.author.id != ctx.guild.owner.id:
							return await util.send_error(ctx, f"{member.mention} is higher then you")
					except:
						pass
					if r.position >= ctx.guild.me.top_role.position:
						return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then my top role therefore i cant give it", color=self.color))
					if ctx.author.id == ctx.guild.owner.id:
						pass
					if not role.is_assignable():
						return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **i cannot give a managed role**"))
					if r in member.roles:
						await member.remove_roles(r)
						embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Removed {r.mention} from {member.mention}", color=self.color)
						return await ctx.send(embed=embed)
					else:
						await member.add_roles(r)
						embed = discord.Embed(color=self.color, description=f"{self.add}{ctx.author.mention}: Added {r.mention} to {member.mention}")
						return await ctx.send(embed=embed)
				if isinstance(member, str):
					if isinstance(role, discord.Member):
						if member.lower() == "restore" and isinstance(role, discord.Member):
							if not ctx.author.guild_permissions.administrator:
								return await util.send_error(ctx, f"missing permissions `administrator`")
							try:
								if await self.bot.db.execute("""SELECT roles FROM restore WHERE guild_id = %s AND member_id = %s""", ctx.guild.id, role.id):
									rrr=[]
									counter=0
									rolenames=[]
									roles=await self.bot.db.execute("""SELECT roles FROM restore WHERE guild_id = %s AND member_id = %s""", ctx.guild.id, role.id, one_value=True)
									roles=roles.split(",")
									for rr in roles:
										roled = discord.utils.get(ctx.guild.roles, id=int(rr))
										if roled and roled.is_assignable():
											rrr.append(roled)
											rolenames.append(roled.name)
									try:
										await self.mass_add_roles(ctx, role)
									except:
										await role.add_roles(*rrr, reason=f"roles restored by {ctx.author}")
									new_lst=(', '.join(str(a)for a in rolenames))
									newroles=f"{new_lst}"
									return await util.send_success(ctx, f"{ctx.author.mention}: **added `{newroles}` to {role.mention}**")
								else:
									return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **No roles found to restore**"))
							except Exception as e:
								print(e)
								return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **please provide a member**"))
				if isinstance(role, str):
					r=role
					roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r.lower() in role.name.lower()]
					rr=await util.find_role(ctx, r.lower())
					if rr:
						if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
							return await ctx.send(embed=discord.Embed(description=f"{rr.mention} is higher then your top role {ctx.author.mention}", color=self.color))
						if rr.position >= ctx.guild.me.top_role.position:
							return await ctx.send(embed=discord.Embed(description=f"{rr.name} is higher then my top role therefore i cant give it", color=self.color))
						if ctx.author.id == ctx.guild.owner.id:
							pass
						if rr in member.roles:
							await member.remove_roles(rr)
							embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Removed  {rr.mention} from {member.mention}", color=self.color)
							return await ctx.send(embed=embed)
						else:
							await member.add_roles(rr)
							embed = discord.Embed(color=self.bot.color, description=f"{self.add}{ctx.author.mention}: Added {rr.mention} to {member.mention}")
							return await ctx.send(embed=embed)
					else:
						r=role
						roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable()]
						closest=difflib.get_close_matches(r.lower(), roles,n=1, cutoff=0)
						if closest:
							for role in ctx.guild.roles:
								if role.name.lower() == closest[0].lower():
									rr=role
							if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
								return await ctx.send(embed=discord.Embed(description=f"{rr.mention} is higher then your top role {ctx.author.mention}", color=self.color))
							if rr.position >= ctx.guild.me.top_role.position:
								return await ctx.send(embed=discord.Embed(description=f"{rr.name} is higher then my top role therefore i cant give it", color=self.color))
							if ctx.author.id == ctx.guild.owner.id:
								pass
							if rr in member.roles:
								await member.remove_roles(rr)
								embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Removed  {rr.mention} from {member.mention}", color=self.bot.color)
								return await ctx.send(embed=embed)
							else:
								await member.add_roles(rr)
								embed = discord.Embed(color=self.bot.color, description=f"{self.add}{ctx.author.mention}: Added {rr.mention} to {member.mention}")
								return await ctx.send(embed=embed)
						else:
							return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: **I was unable to find a role with the name: `{role}`**", color=self.error))
				return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: **I was unable to find a role with the name: `{role}`**", color=self.error))
			except:
				return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: **I was unable to find a role with the name: `{role}`**", color=self.error))

	@role.command(name='restore', description='restore a users role after they leave and rejoin', brief='member', extras={'perms':'manage roles'}, usage='```Swift\nSyntax: !role restore <member>\nExample: !role restore @cop#0001```')
	@commands.guild_only()
	@commands.has_permissions(administrator=True)
	async def role_restore(self, ctx, member: discord.Member):
		"""Syntax: !restore @member
		Example: !restore @cop#0001"""
		try:
			counter=0
			rolenames=[]
			roles=await self.bot.db.execute("""SELECT roles FROM restore WHERE guild_id = %s AND member_id = %s""", ctx.guild.id, member.id, one_value=True)
			roles=roles.split(",")
			rrr=[]
			for rr in roles:
				roled = discord.utils.get(ctx.guild.roles, id=int(rr))
				if roled and roled.is_assignable():
					rrr.append(roled)
					rolenames.append(roled.name)
			try:
				await self.mass_add_roles(ctx, member)
			except:
				await member.add_roles(*rrr, reason=f"roles restored by {ctx.author}")
			new_lst=(', '.join(str(a)for a in rolenames))
			newroles=f"{new_lst}"
			return await util.send_success(ctx, f"{ctx.author.mention}: **added `{newroles}` to {member.mention}**")
		except:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **No roles found to restore**"))
	
	@role.command(name='delete', aliases=['del','d'], description="delete a role", brief='role',extras={'perms':'manage roles'}, usage='```Swift\nSyntax: !role delete <role>\nExample: !role delete cop```')
	@commands.has_permissions(manage_roles=True)
	async def role_delete(self, ctx,  *, role: typing.Union[ discord.Role, str]):
		if isinstance(role, discord.Role):
			r=role
			if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
				return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then your top role {ctx.author.mention}", color=self.color))
			if r.position >= ctx.guild.me.top_role.position:
				return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then my top role therefore i cant give it", color=self.color))
			if ctx.author.id == ctx.guild.owner.id:
				pass
			embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Deleted {r.mention}", color=self.bot.color)
			await ctx.send(embed=embed)
			return await r.delete()
		if isinstance(role, str):
			roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable()]
			closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
			if closest:
				rr=discord.utils.get(ctx.guild.roles, name=closest[0])
				if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
					return await ctx.send(embed=discord.Embed(description=f"{rr.mention} is higher then your top role {ctx.author.mention}", color=self.color))
				if rr.position >= ctx.guild.me.top_role.position:
					return await ctx.send(embed=discord.Embed(description=f"{rr.name} is higher then my top role therefore i cant give it", color=self.color))
				if ctx.author.id == ctx.guild.owner.id:
					pass
				embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Deleted {r.mention}", color=self.bot.color)
				await ctx.send(embed=embed)
				return await r.delete()
		return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: I was unable to find a role with the name: **{role}**", color=self.error))

	async def check_role(self, ctx: commands.Context, role: discord.Role):
		if not ctx.author.top_role > role and not ctx.author.id == ctx.guild.owner.id:
			await util.send_error(ctx, f"{role.mention} is above your highest role")
			return False
		if not ctx.guild.me.top_role > role:
			await util.send_error(ctx, f"unable to edit {role.mention} as its higher or equal to my highest role")
			return False
		return True

	@role.group(name="edit", aliases=["er"])
	async def edit(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@edit.command(name="name", aliases=["n"], description="edit a roles name", usage="```Swift\nSyntax: !role edit name <role> <name>\nExample: !role edit name users Users```", brief="role, name", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def edit_name(self, ctx: commands.Context, role: discord.Role, name: str):
		"""Edit role name.
		"""
		if not await self.check_role(ctx, role):
			return
		try:
			await role.edit(name=name, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			await util.send_good(ctx, f"renamed {role.mention} to `{name}`")

	@edit.command(name="color", aliases=["colour"], description="edit a roles color", usage="```Swift\nSyntax: !role edit color <role> <color hex>\nExample: !role edit color users #00001```", brief="role, color", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def edit_color(self, ctx: commands.Context, role: discord.Role, colour: discord.Colour):
		"""Edit role colour.
		"""
		if not await self.check_role(ctx, role):
			return
		try:
			await role.edit(color=colour, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			await util.send_good(ctx, f"changed {role.mention}'s color to `{colour}`")


	@edit.command(name="mentionable", aliases=["ping", "pingable", "mention"], description="enable or disable pinging a role", usage="```Swift\nSyntax: !role edit mentionable <role> <state>\nExample: !role edit mentionable users true```", brief="role, state", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def edit_mentionable(self, ctx: commands.Context, role: discord.Role, state: bool):
		"""Edit role mentionable.
		"""
		if not await self.check_role(ctx, role):
			return
		try:
			await role.edit(mentionable=state, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			if state:
				await util.send_good(ctx, f"{role.mention} is now mentionable")
			else:
				await util.send_good(ctx, f"{role.mention} is no longer mentionable")


	@edit.command(name="hoist", description="toggle a roles hoist setting", usage="```Swift\nSyntax: !role edit hoist <role> <state>\nExample: !role edit hoist users true```", brief="role, state", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def edit_hoist(self, ctx, role:discord.Role, setting:bool):
		if not await self.check_role(ctx, role):
			return
		if setting:
			try:
				r=role
				rr=await role.edit(hoist=setting, reason=f"{ctx.author} edited a role")
				return await util.send_good(ctx, f"{r} **hoisting set to** `{setting}`")
			except Exception as e:
				await util.send_bad(ctx,f"role already hoisted or unable to edit role {role.mention}\n`{e}`")
				print(e)
				pass
		else:
			try:
				r=role
				rrr=await role.edit(hoist=setting, reason=f"{ctx.author} is a munch")
				return await util.send_good(ctx, f"{r} **hoisting set to** `{setting}`")
			except Exception as e:
				await util.send_bad(ctx,f"role already hoisted or unable to edit role {role.mention}\n`{e}`")
				print(e)
				pass


	@edit.command(name="position", aliases=["pos"], disabled=True,description="edit a roles position", usage="```Swift\nSyntax: !role edit position <role> <position>\nExample: !role edit position users 5```", brief="role, pos", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def edit_position(self, ctx: commands.Context, role: discord.Role, position: int):
		"""Edit role position.
		
		Warning: The role with a position 1 is the highest role in the Discord hierarchy.
		"""
		pos=position
		if not await self.check_role(ctx, role):
			return
		max_guild_roles_position = len(ctx.guild.roles)
		if not position > 0 or not position < max_guild_roles_position + 1:
			await util.send_error(ctx, f"The indicated position must be between 1 and {max_guild_roles_position}.")
			return
		l = [x for x in range(0, max_guild_roles_position - 1)]
		l.reverse()
		position = l[position - 1]
		position = position + 1
		if position >= ctx.author.top_role.position and not ctx.author.id == ctx.guild.owner.id:
			return await util.send_error(ctx, f"that is higher than your role")
		try:
			await role.edit(position=position, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			await util.send_good(ctx, f" changed {role.mention}'s position to `{pos}`")


	@edit.command(name="permissions", aliases=["perms","perm"], description="change a roles permissions", usage="```Swift\nSyntax: !role edit perm <role> <permission int>\nExample: !role edit perm admin 8```", brief="role, perm", extras={'perms': 'manage_roles / Guild Owner / Anti Admin'})
	@commands.has_permissions(manage_roles=True)
	async def edit_permissions(self, ctx: commands.Context, role: discord.Role, permissions: int):
		"""Edit role permissions.
		
		Warning: You must use the permissions value in numbers (admnistrator=8).
		You can use: https://discordapi.com/permissions.html
		"""
		if not ctx.author.id == ctx.guild.owner.id:
			if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id):
				return await util.send_error(ctx, f"missing permissions `Guild Owner`")
		if not await self.check_role(ctx, role):
			return
		permissions_none = discord.Permissions.none().value
		permissions_all = discord.Permissions.all().value
		if not permissions > permissions_none or not permissions < permissions_all:
			await util.send_error(ctx, f"The indicated permissions value must be between {permissions_none} and {permissions_all}.")
			return
		permissions = discord.Permissions(permissions=permissions)
		try:
			await role.edit(permissions=permissions, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			await util.send_good(ctx, f"changed permissions for {role.mention} to `{permissions}`")

	@edit.command(name='icon', description="change a roles icon", usage="```Swift\nSyntax: !role edit icon <role> <url or image>\nExample: !role e dit icon users https://rival.rocks/cat.png```", brief="role, image", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def edit_icon(self, ctx, role: discord.Role, *, url: typing.Union[discord.Emoji,str]=None):
		if not await self.check_role(ctx, role):
			return
		if url and isinstance(url, discord.Emoji):
			url=url.url
		if url is None and len(ctx.message.attachments) == 1:
			url = ctx.message.attachments[0].url
		else:
			url = url.strip("<>") if url else None

		if url:
			async with self.bot.session.get(url=url, raise_for_status=True) as resp:
				await role.edit(display_icon=await resp.read(), reason=f"role icon edited by {ctx.author}")
		else:
			return await util.send_error(ctx, f"please provide an image with the command")
		try:
			await ctx.reply(embed=discord.Embed(color=self.good, description=f"{self.bot.yes} {ctx.author.mention}: **successfully changed role icon to**").set_image(url=url))
		except aiohttp.InvalidURL:
			await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.bot.no} {ctx.author.mention}: **the url is invalid**"))
		except discord.HTTPException as err:
			await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.bot.no} {ctx.author.mention}: **the url is invalid**"))
		except TypeError:
			await ctx.send(embed=discord.Embed(color=self.bad, description=f"{self.bot.no} {ctx.author.mention}: **you need to either provide an image URL or upload one with the command**"))
		except:
			await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.bot.no} {ctx.author.mention}: **the url is invalid**"))



	@commands.command(name='deleterole', aliases=["delrole", "removerole"], description="delete a role", extras={'perms': 'manage roles'}, brief="role")
	@commands.has_permissions(manage_roles=True)
	async def deleterole(self, ctx,  *, role: typing.Union[ discord.Role, str]):
		if isinstance(role, discord.Role):
			r=role
			if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
				return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then your top role {ctx.author.mention}", color=self.color))
			if r.position >= ctx.guild.me.top_role.position:
				return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then my top role therefore i cant give it", color=self.color))
			if ctx.author.id == ctx.guild.owner.id:
				pass
			embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Deleted {r.mention}", color=self.bot.color)
			await ctx.send(embed=embed)
			return await r.delete()
		if isinstance(role, str):
			roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable()]
			closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
			if closest:
				rr=discord.utils.get(ctx.guild.roles, name=closest[0])
				if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
					return await ctx.send(embed=discord.Embed(description=f"{rr.mention} is higher then your top role {ctx.author.mention}", color=self.color))
				if rr.position >= ctx.guild.me.top_role.position:
					return await ctx.send(embed=discord.Embed(description=f"{rr.name} is higher then my top role therefore i cant give it", color=self.color))
				if ctx.author.id == ctx.guild.owner.id:
					pass
				embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Deleted {r.mention}", color=self.bot.color)
				await ctx.send(embed=embed)
				return await r.delete()
		return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: I was unable to find a role with the name: **{role}**", color=self.error))

	async def check_role(self, ctx: commands.Context, role: discord.Role):
		if not ctx.author.top_role > role and not ctx.author.id == ctx.guild.owner.id:
			await util.send_error(ctx, f"{role.mention} is above your highest role")
			return False
		if not ctx.guild.me.top_role > role:
			await util.send_error(ctx, f"unable to edit {role.mention} as its higher or equal to my highest role")
			return False
		return True

	@commands.guild_only()
	@commands.group(name="editrole", aliases=["er"])
	async def editrole(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@editrole.command(name="name", aliases=["n"], description="edit a roles name", usage="```Swift\nSyntax: !editrole name <role> <name>\nExample: !editrole name users Users```", brief="role, name", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def editrole_name(self, ctx: commands.Context, role: discord.Role, name: str):
		"""Edit role name.
		"""
		if not await self.check_role(ctx, role):
			return
		try:
			await role.edit(name=name, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			await util.send_good(ctx, f"renamed {role.mention} to `{name}`")

	@editrole.command(name="color", aliases=["colour"], description="edit a roles color", usage="```Swift\nSyntax: !editrole color <role> <color hex>\nExample: !editrole color users #00001```", brief="role, color", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def editrole_color(self, ctx: commands.Context, role: discord.Role, colour: discord.Colour):
		"""Edit role colour.
		"""
		if not await self.check_role(ctx, role):
			return
		try:
			await role.edit(color=colour, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			await util.send_good(ctx, f"changed {role.mention}'s color to `{colour}`")


	@editrole.command(name="mentionable", aliases=["ping", "pingable", "mention"], description="enable or disable pinging a role", usage="```Swift\nSyntax: !editrole mentionable <role> <state>\nExample: !editrole mentionable users true```", brief="role, state", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def editrole_mentionable(self, ctx: commands.Context, role: discord.Role, state: bool):
		"""Edit role mentionable.
		"""
		if not await self.check_role(ctx, role):
			return
		try:
			await role.edit(mentionable=state, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			if state:
				await util.send_good(ctx, f"{role.mention} is now mentionable")
			else:
				await util.send_good(ctx, f"{role.mention} is no longer mentionable")


	@editrole.command(name="hoist", description="toggle a roles hoist setting", usage="```Swift\nSyntax: !editrole hoist <role> <state>\nExample: !editrole hoist users true```", brief="role, state", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def editrole_hoist(self, ctx, role:discord.Role, setting:bool):
		if not await self.check_role(ctx, role):
			return
		if setting:
			try:
				r=role
				rr=await role.edit(hoist=setting, reason=f"{ctx.author} edited a role")
				return await util.send_good(ctx, f"{r} **hoisting set to** `{setting}`")
			except Exception as e:
				await util.send_bad(ctx,f"role already hoisted or unable to edit role {role.mention}\n`{e}`")
				print(e)
				pass
		else:
			try:
				r=role
				rrr=await role.edit(hoist=setting, reason=f"{ctx.author} is a munch")
				return await util.send_good(ctx, f"{r} **hoisting set to** `{setting}`")
			except Exception as e:
				await util.send_bad(ctx,f"role already hoisted or unable to edit role {role.mention}\n`{e}`")
				print(e)
				pass


	@editrole.command(name="position", aliases=["pos"], disabled=True,description="edit a roles position", usage="```Swift\nSyntax: !editrole position <role> <position>\nExample: !editrole position users 5```", brief="role, pos", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def editrole_position(self, ctx: commands.Context, role: discord.Role, position: int):
		"""Edit role position.
		
		Warning: The role with a position 1 is the highest role in the Discord hierarchy.
		"""
		pos=position
		if not await self.check_role(ctx, role):
			return
		max_guild_roles_position = len(ctx.guild.roles)
		if not position > 0 or not position < max_guild_roles_position + 1:
			await util.send_error(ctx, f"The indicated position must be between 1 and {max_guild_roles_position}.")
			return
		l = [x for x in range(0, max_guild_roles_position - 1)]
		l.reverse()
		position = l[position - 1]
		position = position + 1
		if position >= ctx.author.top_role.position and not ctx.author.id == ctx.guild.owner.id:
			return await util.send_error(ctx, f"that is higher than your role")
		try:
			await role.edit(position=position, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			await util.send_good(ctx, f" changed {role.mention}'s position to `{pos}`")


	@editrole.command(name="permissions", aliases=["perms","perm"], description="change a roles permissions", usage="```Swift\nSyntax: !editrole perm <role> <permission int>\nExample: !editrole perm admin 8```", brief="role, perm", extras={'perms': 'manage_roles / Guild Owner / Anti Admin'})
	@commands.has_permissions(manage_roles=True)
	async def editrole_permissions(self, ctx: commands.Context, role: discord.Role, permissions: int):
		"""Edit role permissions.
		
		Warning: You must use the permissions value in numbers (admnistrator=8).
		You can use: https://discordapi.com/permissions.html
		"""
		if not ctx.author.id == ctx.guild.owner.id:
			if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id):
				return await util.send_error(ctx, f"missing permissions `Guild Owner`")
		if not await self.check_role(ctx, role):
			return
		permissions_none = discord.Permissions.none().value
		permissions_all = discord.Permissions.all().value
		if not permissions > permissions_none or not permissions < permissions_all:
			await util.send_error(ctx, f"The indicated permissions value must be between {permissions_none} and {permissions_all}.")
			return
		permissions = discord.Permissions(permissions=permissions)
		try:
			await role.edit(permissions=permissions, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
		except discord.HTTPException:
			await util.send_error(ctx, f"I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.")
		else:
			await util.send_good(ctx, f"changed permissions for {role.mention} to `{permissions}`")

	@editrole.command(name='icon', description="change a roles icon", usage="```Swift\nSyntax: !editrole icon <role> <url or image>\nExample: !editrole icon users https://rival.rocks/cat.png```", brief="role, image", extras={'perms': 'manage_roles'})
	@commands.has_permissions(manage_roles=True)
	async def editrole_icon(self, ctx, role: discord.Role, *, url: typing.Union[discord.Emoji,str]=None):
		if not await self.check_role(ctx, role):
			return
		if url and isinstance(url, discord.Emoji):
			url=url.url
		if url is None and len(ctx.message.attachments) == 1:
			url = ctx.message.attachments[0].url
		else:
			url = url.strip("<>") if url else None

		if url:
			async with self.bot.session.get(url=url, raise_for_status=True) as resp:
				await role.edit(display_icon=await resp.read(), reason=f"role icon edited by {ctx.author}")
		else:
			return await util.send_error(ctx, f"please provide an image with the command")
		try:
			await ctx.reply(embed=discord.Embed(color=self.good, description=f"{self.bot.yes} {ctx.author.mention}: **successfully changed role icon to**").set_image(url=url))
		except aiohttp.InvalidURL:
			await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.bot.no} {ctx.author.mention}: **the url is invalid**"))
		except discord.HTTPException as err:
			await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.bot.no} {ctx.author.mention}: **the url is invalid**"))
		except TypeError:
			await ctx.send(embed=discord.Embed(color=self.bad, description=f"{self.bot.no} {ctx.author.mention}: **you need to either provide an image URL or upload one with the command**"))
		except:
			await ctx.reply(embed=discord.Embed(color=self.bad, description=f"{self.bot.no} {ctx.author.mention}: **the url is invalid**"))


	@commands.command(name='guildleave')
	@commands.is_owner()
	async def guildleave(self, ctx, *, targetServer):
		if targetServer == None:
			# No server passed
			msg = 'Usage: `{}leaveserver [id/name]`'.format(ctx.prefix)
			return await ctx.send(msg)
		# Check id first, then name
		guild = next((x for x in self.bot.guilds if str(x.id) == str(targetServer)),None)
		if not guild:
			guild = next((x for x in self.bot.guilds if x.name.lower() == targetServer.lower()),None)
		if guild:
			await guild.leave()
			try:
				await ctx.send(delete_after=10, embed=discord.Embed(color=0x303135, description=f"Alright - I left {guild.name}."))
			except:
				pass
			return
		await ctx.send(delete_after=10, embed=discord.Embed(color=0x303135, description=f"{self.bot.warn} I couldn't find that server."))


	@commands.command(name='banner', description='Show a users banner', usage="```Swift\nSyntax: !banner <member/user>Example: !banner @cop#0001```",brief="member/user")
	@commands.guild_only()
	async def banner(self, ctx, *, user:typing.Union[discord.Member, discord.User,str]=None):
		footer=f"Requested by {ctx.author}"
		user = user or ctx.author
		if isinstance(user, str):
			user=await util.find_member(ctx, user.lower())
		else:
			user=user
		user = await self.bot.fetch_user(user.id)
		if user.banner:
			link=user.banner.with_size(512)
			embed=discord.Embed(title=f"{user.name}'s banner", url=link,color=user.color).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
			embed.set_image(url=link)
			#embed.set_footer(text=footer)
			await ctx.send(embed=embed)
		else:
			webhexcolor = f"{str(user.accent_color)}"
			color=webhexcolor.strip("#")
			eembed=discord.Embed(description=f"**{user.mention} does not have a banner set**", color=user.color).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
			eembed.set_image(url=f"https://singlecolorimage.com/get/{color}/512x254")
			await ctx.send(embed=eembed)

	@commands.command(name='avatar', aliases=["av"], description='show a users avatar', usage="```Swift\nSyntax: !avatar <member/user>\nExample: !avatar @cop#0001```",brief="member/user")
	@commands.guild_only()
	async def avatar(self, ctx: commands.Context, *, member: Union[discord.Member, discord.User, str] = None):
		if isinstance(member, str):
			user=await util.find_member(ctx, member.lower())
			av=user.avatar or user.default_avatar
			avatarem=discord.Embed(color=user.color, title=f"{user.name}'s avatar", url=av.url).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)	
			avatarem.set_image(url=av)
			await ctx.send(embed=avatarem)
		else:
			if member is None:
				member = ctx.author
			if not member:
				member=self.bot.get_user(member)
				if member is None:
					member=await self.bot.fetch_user(member)
			user=member
			av=user.avatar or user.default_avatar
			avatarem=discord.Embed(color=member.color, url=av.url,title=f"{member.name}'s avatar").set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
			avatarem.set_image(url=av)
			await ctx.send(embed=avatarem)

	@commands.command(name='sav', aliases=['savatar', 'spfp','serverav'], description='show a users server avatar', usage="```Swift\nSyntax: !sav <member/user>\nExample: !sav @cop#0001```",brief="member/user")
	async def sav(self, ctx, member:typing.Union[discord.Member,str]=None):
		if isinstance(member, str):
			channel=ctx.channel
			memb=await util.find_member(ctx, member.lower())
			if not memb.guild_avatar:
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: {memb.mention} doesn't have a **server avatar** set"))
			em = discord.Embed(title=f"{memb.name}'s server avatar", url=memb.display_avatar.url,color=memb.color).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
			em.set_image(url=memb.display_avatar.url)
			await ctx.send(embed=em)
		else:
			member = member if member else ctx.author
			if not member.guild_avatar:
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: {member.mention} doesn't have a **server avatar** set"))
			em = discord.Embed(title=f"{member.name}'s server avatar", url=member.display_avatar.url,color=member.color).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
			em.set_image(url=member.display_avatar.url)
			await ctx.send(embed=em)

	@commands.hybrid_command(name='weheartit', aliases=['whi'], with_app_command=True, description='Show a weheartit accounts stats', usage="```Swift\nSyntax: !weheartit <username>\nExample: !weheartit perv```",brief="username")
	@commands.guild_only()
	async def weheartit(self, ctx, username: str=None):
		try:
			badges = []
			badges.clear()
			url=f"https://weheartit.com/{username}"
			async with self.bot.session.get(url,raise_for_status=True) as req:
				data=await req.text()
			soup = BeautifulSoup(data, 'html.parser')
			av=soup.find(class_="avatar")['src']
			display=soup.find('span', class_="text-big")
			title=soup.find("meta", property="og:title")["content"]
			user=soup.find('a', class_="js-blc js-blc-t-user")["href"]
			posts=soup.find('a', href=re.compile(f'{user}/uploads')).contents[0]
			posts=posts.replace(" Posts", "")
			hearts=soup.find("meta", property="weheartitapp:hearts").get('content')
			bio=soup.find('p', class_="lead text-gray-dark text-big").contents[0]
			if soup.find('span', class_="avatar-badge badge-premium"):
				badges.append("<:premium:955215936556789770>")
			if soup.find('span', class_="avatar-badge badge-verified"):
				badges.append("<:verified:955215415989121114>")
			if soup.find('span', class_="avatar-badge badge-premium") and soup.find('span', class_="avatar-badge badge-verified"):
				badges.clear()
				badges.append("<:premium:955215936556789770><:verified:955215415989121114>")
			if soup.find('span', class_="avatar-badge badge-heartist"):
				badges.append("<:heartist:972059059366797352>")
			if soup.find('span', class_="avatar-badge badge-writer"):
				badges.append("<:writer:972059727536209970>")
			try:
				soup.find('a', {'target':'_blank', 'rel': 'nofollow'})['href']
				link=soup.find('a', {'target':'_blank', 'rel': 'nofollow'})['href']
			except:
				pass
			try:
				soup.find('small', class_="text-gray-dark").contents[0]
				location=soup.find('small', class_="text-gray-dark").contents[0]
				location=location.replace('\n          ', '')
			except:
				pass
			collections=soup.find('a', href=re.compile(f'{user}/collections')).contents[0]
			collections=collections.replace(" Collections", "")
			un=user.replace("/", "")
			embed=discord.Embed(title=f"{title} (@{un})", description=location, color=0xfe4a84, url=url).set_thumbnail(url=av).set_footer(text="WeHeartIt", icon_url="https://pbs.twimg.com/profile_images/1004390651767578624/3z3MVyS2.jpg").set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
			try:
				followers=soup.find('a', href=re.compile(f'{user}/fans')).contents[0]
				followers=followers.replace(" Followers", "")
				following=soup.find('a', href=re.compile(f'{user}/contacts')).contents[0]
				embed.add_field(name="Followers", value=followers, inline=True)
			except:
				pass
			embed.add_field(name="Posts", value=posts, inline=True)
			embed.add_field(name="Collections", value=collections, inline=True)
			if badges:
				embed.add_field(name="Badges", value=''.join(badges), inline=True)
			view = discord.ui.View()
			logo=self.bot.get_emoji(952399852527046687)
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, emoji=logo, url=url))
			await ctx.reply(embed=embed, view=view)
		except TypeError:
			return await ctx.reply(delete_after=10, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: [{username}]({url}) is an invalid **WeHeartIt** profile"))
		except AttributeError:
			return await ctx.reply(delete_after=10, embed=discord.Embed(color=self.bad, description=f"{ctx.author.mention} weheartit profile {username} not found, please use correct casing"))
		except:
			return await ctx.reply(delete_after=10, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: [{username}]({url}) is an invalid **WeHeartIt** profile"))
			
	def format(self, text):
		if " thousand" in text:
			text=text.replace(" thousand", "k")
		if " million" in text:
			text=text.replace(" million", "m")
		return text

	# @commands.command(name='testig')
	# async def testig(self, ctx, username:str):
		# url = "https://instagram-scraper-data.p.rapidapi.com/userinfo/twitter"
		# headers = {
		# 	"X-RapidAPI-Key": "ca729cb7efmshf50604855102e52p188371jsn605dbd0266cd",
		# 	"X-RapidAPI-Host": "instagram-scraper-data.p.rapidapi.com"
		# }
		# async with aiohttp.ClientSession() as s:
		# 	async with s.get(url,headers=headers) as r:
		# 		d=await r.json(content_type=None)
		# 		data=d['data']
		# embed=discord.Embed(title=f"{data['full_name']} (@{username})",description=data['biography'], color=self.bot.color)
		# embed.add_field(name="Posts", inline=True,value=self.format(humanize.intword(data["edge_owner_to_timeline_media"].get("count"))))
		# embed.add_field(name='Following', value=self.format(humanize.intword(data['edge_follow']['count'])), inline=True)
		# embed.add_field(name='Followers', value=self.format(humanize.intword(data['edge_followed_by']['count'])), inline=True)
		# embed.set_thumbnail(url=data['profile_pic_url'])
		# return await ctx.send(embed=embed)

	@commands.hybrid_command(name="instagram", aliases=["ig", "insta", "gram"], with_app_command=True, description='Show stats on an instagram account', usage="```Swift\nSyntax: !instagram <username>\nExample: !instagram niih```",brief="username")
	@util.donor_server()
	async def instagram(self, ctx: commands.Context, username: str):
		#return await util.send_error(ctx, f"disabled blame **monty#0001** dm him for it to be fixed XD\nHIS ID IS: **728095627757486081**")
		#if username:
		try:
			# url = "https://instagram-scraper-data.p.rapidapi.com/userinfo/twitter"
			# headers = {
			# 	"X-RapidAPI-Key": "ca729cb7efmshf50604855102e52p188371jsn605dbd0266cd",
			# 	"X-RapidAPI-Host": "instagram-scraper-data.p.rapidapi.com"
			# }
			# async with aiohttp.ClientSession() as s:
			# 	async with s.get(url,headers=headers) as r:
			# 		d=await r.json(content_type=None)
			# 		data=d['data']
			# if data:
			# 	embed=discord.Embed(title=f"{data['full_name']} (@{username})",description=data['biography'], color=self.bot.color)
			# 	embed.add_field(name="Posts", inline=True,value=self.format(humanize.intword(data["edge_owner_to_timeline_media"].get("count"))))
			# 	embed.add_field(name='Following', value=self.format(humanize.intword(data['edge_folow']['count'])), inline=True)
			# 	embed.add_field(name='Followers', value=self.format(humanize.intword(data['edge_followed_by'])), inline=True)
			# 	embed.set_thumbnail(url=data['profile_pic_url'])
			# 	return await ctx.send(embed=embed)
		# 	url = "https://instagram-looter2.p.rapidapi.com/profile"

		# 	querystring = {"username":username}

		# 	headers = {
		# 	"X-RapidAPI-Key": "cbc61e618cmsh72b38b650efe7acp1f00a3jsna7d8a954a230",
		# 	"X-RapidAPI-Host": "instagram-looter2.p.rapidapi.com"
		# 	}
		# 	async with aiohttp.ClientSession() as session:
		# 		async with session.request("GET",url=url,headers=headers,params=querystring) as response:
		# 			data=await response.json()
		# 	try:
		# 		if data['status'] == 'False':
		# 			if data["errorMessage"] and data["errorMessage"] == "This account does not exist.":
		# 				igurl=f"https://instagram.com/{username}"
		# 				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **[{username}]({igurl})** is an invalid **instagram** account"))
		# 			else:
		# 				try:
		# 					url = "https://instagram-looter2.p.rapidapi.com/profile"

		# 					querystring = {"username":username}

		# 					headers = {
		# 					"X-RapidAPI-Key": "ca729cb7efmshf50604855102e52p188371jsn605dbd0266cd",
		# 					"X-RapidAPI-Host": "instagram-looter2.p.rapidapi.com"
		# 					}

		# 					async with aiohttp.ClientSession() as session:
		# 						async with session.request("GET",url=url,headers=headers,params=querystring) as response:
		# 							data=await response.json()
		# 					if data['status'] == 'False':
		# 						if data["errorMessage"] and data["errorMessage"] == "This account does not exist.":
		# 							igurl=f"https://instagram.com/{username}"
		# 							return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **[{username}]({igurl})** is an invalid **instagram** account"))
		# 				except:
		# 					igurl=f"https://instagram.com/{username}"
		# 					return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **[{username}]({igurl})** is an invalid **instagram** account"))
		# 		name = data['username']
		# 		posts = data['edge_owner_to_timeline_media']['count']
		# 		private=data['is_private']
		# 		verified=data['is_verified']
		# 		fullname=data['full_name']
		# 		followers = data['edge_follow']['count']
		# 		following=data['edge_followed_by']['count']
		# 		bio = data['biography']
		# 		if bio == 'None':
		# 			bio=None
		# 		pfp = data['profile_pic_url']
		# 		if fullname == "None":
		# 			us=f"{name}"
		# 		else:
		# 			us=f"{fullname} (@{name})"
		# 		if private==True:
		# 			pv='🔒'
		# 		else:
		# 			pv=''
		# 		if verified==True:
		# 			vf="<a:b_verifyblue:926931019339284561>"
		# 		else:
		# 			vf=""
		# 		igurl=f"https://instagram.com/{name}"
		# 		embed=discord.Embed(title=f"{us} {pv}{vf}", description=bio, url=igurl, color=0xaf2c9a)
		# 		embed.add_field(name="Posts", value=posts, inline=True)
		# 		embed.add_field(name="Following", value=followers, inline=True)
		# 		embed.add_field(name="Followers", value=following, inline=True)
		# 		embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
		# 		embed.set_thumbnail(url=pfp)
		# 		# ig=await InstagramProfileModelResponse.from_url(self.session,ctx,username)
		# 		# view = discord.ui.View()
		# 		# igurl=f"https://instagram.com/{username}"
		# 		logo=self.bot.get_emoji(949073464638201856)
		# 		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, emoji=logo, url=igurl))
		# 		await ctx.reply(embed=embed, view=view)
		# 	except Exception as e:
		# 		print(e)
		# 		igurl=f"https://instagram.com/{username}"
		# 		return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **[{username}]({igurl})** is an invalid **instagram** account"))
			ig=await InstagramProfileModelResponse.from_url(self.session,ctx,username)
			#view = discord.ui.View()
			igurl=f"https://instagram.com/{username}"
			#logo=self.bot.get_emoji(949073464638201856)
			#view.add_item(discord.ui.Button(style=discord.ButtonStyle.link,emoji="<:ig:949073464638201856>", url=igurl))
			await ctx.reply(embed=ig.make_embed(ctx=ctx))
		except Exception as e:
			#print(e)
			igurl=f"https://instagram.com/{username}"
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **[{username}]({igurl})** is an invalid **instagram** account"))
		#else:
			#await util.send_command_help(ctx)
			
	@commands.hybrid_command(aliases=['inv'], with_app_command=True, description="get the invite link for the bot")
	async def invite(self, ctx):
		link=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=applications.commands+bot"
		link2="https://discord.com/api/oauth2/authorize?client_id=989196958394613861&permissions=8&scope=bot%20applications.commands"
		#invlink2="https://discord.com/api/oauth2/authorize?client_id=989196958394613861&permissions=8&scope=bot%20applications.commands"
		invlink2="https://discord.com/oauth2/authorize?client_id=1002294763241885847&permissions=8&scope=applications.commands%20bot"
		invlink=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=applications.commands%20bot"
		#invlink=f"https://discord.com/oauth2/authorize?client_id=994052621570687158&permissions=8&scope=applications.commands%20bot"
		embed = discord.Embed(description=f"**rival's** *bot invite generated below*", color=self.color)
		embed.set_footer(text=f"requested by {ctx.author}")
		view = discord.ui.View()
		#view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite rival', url=invlink2))
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite rival', url=invlink))
		await ctx.send(embed=embed, view=view)

	@commands.command(name='firstmsg', aliases=["fmsg", "first"])
	@commands.guild_only()
	async def firstmsg(self, ctx, channel: discord.TextChannel = None):
		if channel is None:
			channel = ctx.channel
		try:
			async for message in channel.history(oldest_first=True): z = message
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label='first message', url=z.jump_url))
			await ctx.send(view=view, embed=discord.Embed(color=self.color, description=f"[First Message]({z.jump_url})"))
		except:
			pass

	@commands.command(name='reverse')
	@commands.guild_only()
	async def reverse(self, ctx, *, img):
		try:
			link=f"https://images.google.com/searchbyimage?image={img}"
			em = discord.Embed(description=f"{ctx.author}'s reverse search", color=self.color).set_footer(text=f"Requested by {ctx.author}")
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label='reverse', url=link))
			await ctx.send(embed=em, view=view)
		except Exception as e:
			print(f"{Fore.RED}[ERROR]: {Fore.YELLOW}{e}" + Fore.RESET)

	@commands.command(name='revav')
	@commands.guild_only()
	async def revav(self, ctx, *, user: Union[discord.Member, discord.User] = None):
		if user is None:
			user = ctx.author
		if not user:
			user=await self.bot.fetch_user(user)
		try:
			link=f"https://images.google.com/searchbyimage?image={user.display_avatar}"
			em = discord.Embed(color=self.color, description=f"{user.name}'s reverse search").set_footer(text=f"Requested by {ctx.author}")
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f"{user.name}'s revav", url=link))
			await ctx.send(embed=em, view=view)
		except Exception as e:
			print(f"{Fore.RED}[ERROR]: {Fore.YELLOW}{e}" + Fore.RESET)

	@commands.command(name='botinv', aliases=['botinvite'], description="get an invite for any bot", usage="```Swift\nSyntax: !botinv <id/@member>\nExample: !botinv @rival```",brief="member/user")
	@commands.guild_only()
	async def botinv(self, ctx, bot: typing.Union[discord.User, discord.Member]):
		b=await self.bot.fetch_user(bot.id)
		link=f"https://discord.com/oauth2/authorize?client_id={bot.id}&permissions=8&scope=applications.commands%20bot"
		embed = discord.Embed(description=f"**{b.name}'s** *bot invite generated below*", color=self.color)
		embed.set_footer(text=f"requested by {ctx.author}")
		view = discord.ui.View()
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite {b.name}', url=link))
		await ctx.send(embed=embed, view=view)

	@commands.command(description="show the bot's ping")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def ping(self, ctx):
		before = time.monotonic()
		before_ws = int(round(self.bot.latency * 1000, 1))
		ping = (time.monotonic() - before) * 1000
		messages = ["it took `putlatencyherems` to ping **your mom's basement**","it took `putlatencyherems` to ping **troy's family**","it took `putlatencyherems` to ping **jitcoin api**","it took `putlatencyherems` to ping **rival's vps**","it took `putlatencyherems` to ping **haunt's vps**","it took `putlatencyherems` to ping **ur step sis**","it took `putlatencyherems` to ping **localhost**","it took `putlatencyherems` to ping **twitter**","it took `putlatencyherems` to ping **your house**","it took `putlatencyherems` to ping **alexa**","it took `putlatencyherems` to ping **a connection to the server**","it took `putlatencyherems` to ping **@cop on discord**","it took `putlatencyherems` to ping **rival**","it took `putlatencyherems` to ping **some bitches**","it took `putlatencyherems` to ping **@antinuke0day on github**","it took `putlatencyherems` to ping **a bot**","it took `putlatencyherems` to ping **the database**"]
		msg = random.choice(messages)
		ran=random.randrange(1, 4)
		msg = msg.replace('putlatencyhere',  f"{16+ran}")
		message=await ctx.send(content=f"{msg}")
		await asyncio.sleep(0.1)
		rand=random.randrange(30, 110)
		await message.edit(content=f"{msg} (edit: `{15+rand}ms`)")

	@commands.command(name='shutdown')
	@commands.is_owner()
	async def shutdown(self, ctx):
		embed = discord.Embed(title="rival", description="Bot Shutdown Please Message lie#1337", color=0xCB3E3)
		await ctx.send(embed=embed)
		await self.bot.logout()

	@commands.command(name='credits', description='show credits to contributors of the bot')
	async def credits(self, ctx):
		return await ctx.reply(embed=discord.Embed(color=self.bot.color,description=f"**credits all of the following people**\n**jac#1337** - constantly pushing me to continue\n**jin#7777** - the name rival when enemy got old\n**monty#0001** - help with the scaling of rival and with advice anytime i've needed\n**jon#0006** - the aesthetic and commands page on the website all credits there goes to [bleed](https://bleed.bot)\n**xoxo#0911 & cal#0911** - Growing the bot significantly\n**yummy#0001** - help growing / marketing the bot\n"))

	@commands.command(name='about', aliases=['info', 'botinfo'], description="see information about the bot")
	async def about(self, ctx):
		#invlink2="https://discord.com/oauth2/authorize?client_id=1002294763241885847&permissions=8&scope=applications.commands%20bot"
		invlink=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=applications.commands%20bot"
		ramUsage = self.process.memory_full_info().rss / 1024**2
		# if 2 in self.bot.shard_ids:
		# 	async with aiohttp.ClientSession() as session:
		# 		async with session.get("http://127.0.0.1:6967/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			mcc=int(stats['users'])
		# 			guildsss=int(stats['guilds'])
		# 		async with session.get("http://127.0.0.1:6969/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			cc=int(stats['users'])
		# 			guildss=int(stats['guilds'])
		# elif 1 in self.bot.shard_ids:
		# 	async with aiohttp.ClientSession() as session:
		# 		async with session.get("http://127.0.0.1:6968/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			mcc=int(stats['users'])
		# 			guildsss=int(stats['guilds'])
		# 		async with session.get("http://127.0.0.1:6967/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			cc=int(stats['users'])
		# 			guildss=int(stats['guilds'])
		# else:
		# 	async with aiohttp.ClientSession() as session:
		# 		async with session.get("http://127.0.0.1:6969/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			mcc=int(stats['users'])
		# 			guildsss=int(stats['guilds'])
		# 		async with session.get("http://127.0.0.1:6968/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			cc=int(stats['users'])
		# 			guildss=int(stats['guilds'])
		# guilds=len(self.bot.guilds)+guildss+guildsss
		# mc=mcc+cc+sum(self.bot.get_all_members())
		mc=int(await self.bot.redis.get("membercount1"))+int(await self.bot.redis.get("membercount2"))+int(await self.bot.redis.get("membercount3"))#+int(await self.bot.redis.get(membercount0))+int(await self.bot.redis.get("membercount4"))+int(await self.bot.redis.get("membercount5"))
		guilds=int(await self.bot.redis.get("guilds1"))+int(await self.bot.redis.get("guilds2"))+int(await self.bot.redis.get("guilds3"))#+int(await self.bot.redis.get("guilds0"))+int(await self.bot.redis.get("guilds4"))+int(await self.bot.redis.get("guilds5"))
		av=int(mc)/int(guilds)
		bleed=self.bot.get_user(704874297247924235)
		ant=self.bot.get_user(904832583551057950)
		#embed = discord.Embed(colour=0x303135)
		cmdCount = sum(1 for i in self.bot.walk_commands())
		usedRam = float(str(psutil.virtual_memory()[3]/1000000000)[:4])#psutil.virtual_memory().percent
		totalCpu  = psutil.cpu_percent()
		channels=sum(self.bot.get_all_channels())
		view=discord.ui.View()
		p = pathlib.Path('./')
		imp = cm = cr = fn = cl = ls = fc = 0
		for f in p.rglob('*.py'):
			if str(f).startswith("venv"):
				continue
			if str(f).startswith('discord'):
				continue
			fc += 1
			with f.open() as of:
				for l in of.readlines():
					l = l.strip()
					if l.startswith('class'):
						cl += 1
					if l.startswith('def'):
						fn += 1
					if l.startswith('import'):
						imp += 1
					if l.startswith("from"):
						imp += 1
					if l.startswith('async def'):
						cr += 1
					if '#' in l:
						cm += 1
					ls += 1
		#credit="""```ini\n\n            __,__            \n   .--.  .-"     "-.  .--.   \n  / .. \/  .-. .-.  \/ .. \  \n | |  '|  /   Y   \  |'  | | \n | \   \  \ 0 | 0 /  /   / | \n  \ '- ,\.-"`` ``"-./, -' /  \n   `'-' /_   ^ ^   _\ '-'`   \n       |  \._   _./  |       \n       \   \ `~` /   /       \n        '._ '-=-' _.'        \n           '~---~'           ```"""
		credit="""```\n
  *    .  *       .             *
						 *
 *   .        *       .       .       *
   .     *
		   .     .  *        *
	   .                .        .
.  *           *                     *
							 .
		 *          .   *```"""
		supportinvite="https://discord.gg/cop"
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Invite",url=invlink))
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Support", url=supportinvite))
		process_uptime=time.time() - self.bot.start_time
		system_uptime=time.time() - psutil.boot_time()
		system_uptime=util.stringfromtime(system_uptime, 2)
		uptime=util.stringfromtime(process_uptime, 2)
		#desc = f'```yaml\nGuilds    : {len(self.bot.guilds)}\nUsers     : {len(set(self.bot.get_all_members()))}\nLibrary   : Discord.py{discord.__version__}\nDevs      : cop#0001(everything but the social commands that was found#9957)```\n\n \n\n```yaml\nPrefix   : ,\nStatus   : Online\nCmds     : {cmdCount}```\n\n \n\n```yaml\nPing     : {round(self.bot.latency * 1000, 1)}Ms```\n\n \n\n```yaml\nCpu Usage : {totalCpu}%\nTotal Ram : {totalRam}Gs\nRam Usage : {usedRam}%```'
		#mBed = discord.Embed(title=self.bot.user.name, url='https://discord.gg/bag', description=desc, color=0x303136)
		mBed=discord.Embed(color=self.color, description=f"**Developers:** `cop#0001`, `cop#0666`, `{str(ant)}`\n[Support]({supportinvite})").add_field(name="Commands", value=f"`{cmdCount}`", inline=True).add_field(name=f'Guilds', value=f"`{num(guilds)}`", inline=True).add_field(name="Memory", value=f"`{usedRam}G` Used", inline=True).add_field(name="Users", value=f"Unique: `{num(mc)}`\nAverage: `{num(int(av))}`", inline=True).add_field(name='Uptime', value=f"Bot: `{uptime}`\nSystem: `{system_uptime}`", inline=True).add_field(name="Library", value="`Discord.py`",inline=True)
		mBed.add_field(name=f"**Code Stats**", value=f"""
Total Files: `{fc:,}`
Total Imports: `{imp:,}`
						  """, inline=True)
		mBed.add_field(name='\u200b', value=f"""Lines Used: `{ls*2:,}`
Total Classes: `{cl*2:,}`""", inline=True)
		mBed.add_field(name='\u200b', value=f"""Functions Defined: `{fn*2:,}`
Total Corutines: `{cr*2:,}`""",inline=True)
		#mBed.set_thumbnail(url=self.bot.user.display_avatar)
		data = await util.get_commits("antinuke0day", "rival")
		last_update = data[0]["commit"]["author"].get("date")
		mBed.set_footer(text=f"Latest update: {arrow.get(last_update).humanize()}")
		await ctx.send(embed=mBed, view=view)
		#embed.add_field(name="Last boot", value=default.timeago(ctx.message.created_at - self.bot.user.created_at), inline=True)
		#embed.add_field(name="Library", value=f"discord.py v{discord.__version__}", inline=True)
		#embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)}", inline=True)
		#embed.add_field(name="Users", value=f"**Total**: `{mc}`\n**Average**: `{int(av)}`")
		#embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
		#embed.add_field(name="Cogs", value=len(self.bot.cogs))
		#embed.add_field(name="RAM", value=f"3{ramUsage:.2f} MB", inline=True)

		#await ctx.send(embed=embed)

	@commands.hybrid_command(name='membercount', aliases=["mc"], with_app_command=True, description="show guild's member count and daily joins")
	@commands.guild_only()
	async def membercount(self, ctx):
		server = ctx.message.guild
		guild = ctx.guild
		djoin=await self.bot.db.execute("SELECT joins FROM gstat WHERE guild_id = %s",ctx.guild.id, one_value=True)
		try:
			if int(djoin) >= 0:
				ddjoin=f"+{djoin}"
			else:
				ddjoin=djoin
		except:
			ddjoin="+0"
		embed = discord.Embed(color=self.bot.color)
		embed.add_field(name=f"**Users({ddjoin})**", value=num(int(len([m for m in ctx.guild.members]))))
		embed.add_field(name="**Humans**", value=num(int(len([m for m in ctx.guild.members if not m.bot]))))
		embed.add_field(name="**Bots**", value=num(int(len([m for m in ctx.guild.members if m.bot]))))
		embed.set_author(name=f"{server.name}'s statistics", icon_url=guild.icon)
		await ctx.send(embed=embed)

	@commands.command(name='botstats', aliases=["statistics", "botstat"])
	@commands.guild_only()
	async def botstats(self, ctx):
		server = ctx.message.guild
		# if 2 in self.bot.shard_ids:
		# 	async with aiohttp.ClientSession() as session:
		# 		async with session.get("http://127.0.0.1:6967/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			mcc=int(stats['users'])
		# 			guildsss=int(stats['guilds'])
		# 		async with session.get("http://127.0.0.1:6969/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			cc=int(stats['users'])
		# 			guildss=int(stats['guilds'])
		# elif 1 in self.bot.shard_ids:
		# 	async with aiohttp.ClientSession() as session:
		# 		async with session.get("http://127.0.0.1:6968/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			mcc=int(stats['users'])
		# 			guildsss=int(stats['guilds'])
		# 		async with session.get("http://127.0.0.1:6967/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			cc=int(stats['users'])
		# 			guildss=int(stats['guilds'])
		# else:
		# 	async with aiohttp.ClientSession() as session:
		# 		async with session.get("http://127.0.0.1:6969/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			mcc=int(stats['users'])
		# 			guildsss=int(stats['guilds'])
		# 		async with session.get("http://127.0.0.1:6968/stats") as r:
		# 			stats=await r.json(content_type=None)
		# 			cc=int(stats['users'])
		# 			guildss=int(stats['guilds'])
		mc=int(await self.bot.redis.get("membercount1"))+int(await self.bot.redis.get("membercount2"))+int(await self.bot.redis.get("membercount3"))#+int(await self.bot.redis.get(membercount0))+int(await self.bot.redis.get("membercount4"))+int(await self.bot.redis.get("membercount5"))
		guilds=int(await self.bot.redis.get("guilds1"))+int(await self.bot.redis.get("guilds2"))+int(await self.bot.redis.get("guilds3"))#+int(await self.bot.redis.get("guilds0"))+int(await self.bot.redis.get("guilds4"))+int(await self.bot.redis.get("guilds5"))
		#mc=mcc+cc+sum(self.bot.get_all_members())
		av=int(mc)/int(guilds)
		embed = discord.Embed(title=f"{self.bot.user.name}'s stats")
		embed.add_field(name="*Servers:*", value=f"{num(guilds)}", inline=True)
		embed.add_field(name="*Average Users:*", value=num(int(av)), inline=True)
		embed.add_field(name="*Total Users:*", value=f"{num(int(mc))}", inline=True)
		embed.set_thumbnail(url=self.bot.user.display_avatar)
		await ctx.send(embed=embed)

	@commands.command(name='selfunban')
	async def selfunban(self, ctx, guild:int):
		guild = await self.bot.fetch_guild(guild)
		member = 714703136270581841
		await guild.unban(discord.Object(id=member))
		await ctx.send("unbanned")

	@commands.command(name='nsfw', description="change channel nsfw setting", brief="true/false", usage="```Swift\nSyntax: !nsfw <bool>\nExample: !nsfw true```",extras={'perms': 'manage channels'})
	@commands.has_permissions(manage_channels=True)
	async def nsfw(self, ctx, value:bool):
		if value:
			await ctx.channel.edit(nsfw=True)
			await util.send_success(ctx, f" {ctx.author.mention}: set **channel nsfw** to `true`")
		else:
			await ctx.channel.edit(nsfw=False)
			await util.send_success(ctx, f" {ctx.author.mention}: set **channel nsfw** to `false`")


	def format(self, text):
		if " thousand" in text:
			text=text.replace(" thousand", "k")
		if " million" in text:
			text=text.replace(" million", "m")
		return text

	@commands.command(name='tiktok', description="show account stats on a tiktok account", usage="```Swift\nSyntax: !tiktok <username>\nExample: !tiktok cop```",brief="username", aliases=['tt'])
	@util.donor_server()
	async def tiktok(self, ctx, *, username=None):
		if username == None:
			return await util.send_command_help(ctx)
		try:
			ig=await TikTokUserProfileResponse.from_url(self.session,ctx,username)
			await ctx.send(embed=ig.make_embed(ctx=ctx))
		except Exception as e:
			print(e)
			return await util.send_error(ctx, f"[**@{username}**](https://tiktok.com/@{username}) is an **invalid TikTok account**")

	@commands.command(name='embedvideo', description="embed tiktok links in the chat", brief="link")
	async def embedvideo(self, ctx, *, url):
		msg=url
		target=msg
		if "tiktok.com" in url:
			try:
				if (checkURL(msg)):
					tikTok = getVideo(msg)
					directLink = tikTok["link"]
					randomm = str(random.randint(10000,90000)) + ".mp4"
					download = requests.get(directLink).content
					with open(randomm,"wb") as f:
						f.write(download)
					try:
						await ctx.send(content=ctx.author.mention,file=discord.File(random))
					except:
						try:
							uploadFile = requests.post("https://shdwrealm.com/upload-file",files = {'file': open(randomm,'rb')})
							await ctx.send(message.author.mention+"||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||"+uploadFile.json()["link"])
						except:
							pass
					await ctx.message.delete()
					os.remove(randomm)
			except:
				pass

	@commands.command(name='donate', description="show donation method")
	async def donate(self, ctx):
		cashapp=self.bot.get_emoji(1011513541032939540)
		bitcoin=self.bot.get_emoji(1006310686235828264)
		embed=discord.Embed(title='Donation Methods', color=0x303135, description=f"{bitcoin} - `3N9CsXwoGNhme9RttdSs8e8dP46FRtqpX5`\n[paypal](https://www.paypal.com/paypalme/rivaldiscordbot)\n[github](https://github.com/sponsors/antinuke0day)\n{cashapp} - `$RivalBot1`\n**5$ MINIMUM**\nInclude Discord ID in the note\n**And Make A Ticket With TransactionID**")
		await ctx.reply(embed=embed)

	@commands.group(name='automod', description="server automoderation")
	@commands.has_permissions(administrator=True)
	async def automod(self, ctx):
		"""Auto Moderation"""
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@automod.command(name="bypass", description="set or unset the automod bypass role", extras={'perms': 'administrator'}, brief="role", usage="```Swift\nSyntax: !automod bypass <role>\nExample: !automod bypass users```")
	@commands.has_permissions(administrator=True)
	async def bypass(self, ctx, *, role:discord.Role):
		if await self.bot.db.execute("""SELECT * FROM spambyp WHERE guild_id = %s""", ctx.guild.id):
			await self.bot.db.execute("""DELETE FROM spambyp WHERE guild_id = %s""", ctx.guild.id)

			self.bot.cache.role_bypass[ctx.guild.id].remove(ctx.guild.id)
			await util.send_good(ctx, f"deleted automod bypass for {role.mention}")
		else:
			await self.bot.db.execute("""INSERT INTO spambyp VALUES(%s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)""", ctx.guild.id, role.id)
			await util.send_good(ctx, f"added automod bypass for {role.mention}")


	@automod.command(name='nudity', aliases=['nude', 'antinude', 'antinudity'], description="Anti Nudity (WIP)", extras={'perms': 'administrator'}, usage="```Swift\nSyntax: !automod nudity <bool>\nExample: !automod nudity true```",brief="true/false")
	async def nudity(self, ctx, state:bool):
		if state:
			await self.bot.db.execute("INSERT INTO antinudity VALUES(%s)", ctx.guild.id)
			await util.send_success(ctx, f"**anti-nudity** set to `true`")
		else:
			if await self.bot.db.execute("SELECT * FROM antinudity WHERE guild_id = %s", ctx.guild.id, one_value=True):
				await self.bot.db.execute("DELETE FROM antinudity WHERE guild_id = %s", ctx.guild.id)
				await util.send_success(ctx, f"**anti-nudity** set to `false`")
			else:
				await util.send_success(ctx, f"**anti-nudity** set to `false`")

	@automod.command(name='exempt',description="Anti Auto Mod Exempt Admins", extras={'perms': 'administrator'}, usage="```Swift\nSyntax: !automod exempt <bool>\nExample: !automod exempt true```",brief="true/false")
	async def exempt(self, ctx, state:bool):
		if not state:
			if await self.bot.db.execute("SELECT state FROM exempt WHERE guild_id = %s", ctx.guild.id, one_value=True):
				await self.bot.db.execute("DELETE FROM exempt WHERE guild_id = %s",ctx.guild.id,)
				self.bot.cache.exempt.remove(ctx.guild.id)
		if state:
			if await self.bot.db.execute("SELECT state FROM exempt WHERE guild_id = %s", ctx.guild.id, one_value=True):
				self.bot.cache.exempt.remove(ctx.guild.id)
				await self.bot.db.execute("DELETE FROM exempt WHERE guild_id = %s",ctx.guild.id,)
			value="1"
			await self.bot.db.execute("INSERT INTO exempt VALUES(%s, %s)",ctx.guild.id, value)
			try:
				self.bot.cache.exempt.append(ctx.guild.id)
			except:
				pass
			await util.send_success(ctx, f"exempt set to {state}")
		else:
			try:
				self.bot.cache.exempt.remove(ctx.guild.id)
			except:
				pass
			await self.bot.db.execute("DELETE FROM exempt WHERE guild_id = %s",ctx.guild.id,)
			await util.send_failure(ctx, f"exempt set to {state}")

	@automod.command(name='antiinvite', aliases=['invite', 'antiinv', 'inv'], description="Anti Invite (WIP)", extras={'perms': 'administrator'}, usage="```Swift\nSyntax: !automod inv <bool>\nExample: !automod inv true```",brief="true/false")
	async def antiinvite(self, ctx, state:bool):
		if state:
			await self.bot.db.execute("INSERT INTO antiinvite VALUES(%s)", ctx.guild.id)
			await util.send_success(ctx, f"**anti-invite** set to `true`")
		else:
			if await self.bot.db.execute("SELECT * FROM antiinvite WHERE guild_id = %s", ctx.guild.id, one_value=True):
				await self.bot.db.execute("DELETE FROM antiinvite WHERE guild_id = %s", ctx.guild.id)
				await util.send_success(ctx, f"**anti-invite** set to `false`")
			else:
				await util.send_success(ctx, f"**anti-invite** set to `false`")

	@automod.command(name='spam', aliases=['antispam'], description="5 Message Spam Limit Admins Exempt", extras={'perms': 'administrator'}, usage="```Swift\nSyntax: !automod spam <bool>\nExample: !automod spam true```",brief="true/false")
	async def spam(self, ctx, state:bool):
		if state:
			if await self.bot.db.execute("SELECT * FROM antispam WHERE guild_id = %s", ctx.guild.id, one_value=True):
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **anti-spam** is already **enabled**"))
			if int(ctx.guild.id) not in self.bot.cache.antispam:
				self.bot.cache.antispam.append(int(ctx.guild.id))
			await self.bot.db.execute("INSERT INTO antispam VALUES(%s)", ctx.guild.id)
			await util.send_success(ctx, f"**anti-spam** set to `true`")
		else:
			if await self.bot.db.execute("SELECT * FROM antispam WHERE guild_id = %s", ctx.guild.id, one_value=True):
				await self.bot.db.execute("DELETE FROM antispam WHERE guild_id = %s", ctx.guild.id)
				self.bot.cache.antispam.remove(ctx.guild.id)
				await util.send_success(ctx, f"**anti-spam** set to `false`")
			else:
				await util.send_success(ctx, f"**anti-spam** set to `false`")

	@automod.command(name='antilink', aliases=['link'], description="auto deletes links in messages", extras={'perms':'administrator'},usage='```Swift\nSyntax: !automod antilink <bool>\nExample !automod antilink true```', brief='bool')
	async def antilink(self, ctx, state:bool, channel:discord.TextChannel=None):
		if channel is None:
			channel=ctx.channel
		if state:
			if await self.bot.db.execute("""SELECT * FROM antilink WHERE channel_id = %s""", channel.id):
				await self.bot.db.execute("""DELETE FROM antilink WHERE channel_id = %s""", channel.id)
			await self.bot.db.execute("""INSERT INTO antilink VALUES(%s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)""", channel.id)
			await util.send_good(ctx,f"antilink set to `true` in {channel.mention}")
		else:
			await self.bot.db.execute("""DELETE FROM antilink WHERE channel_id = %s""", channel.id)
			await util.send_bad(ctx, f"antilink set to `false` in {channel.mention}")


	@automod.command(name='massmention', aliases=['mention', 'mm'], description="Mass Mention Auto Moderation Admin Exempt", usage="```Swift\nSyntax: !automod massmention <int>\nExample: !automod massmention 15```",extras={'perms': 'administrator'}, brief="int")
	async def massmention(self, ctx, amount:int=None):
		if amount > 0:
			self.bot.cache.antimention.update({int(ctx.guild.id):int(amount)})
			await self.bot.db.execute("INSERT INTO antimention VALUES(%s, %s)", ctx.guild.id, amount)
			await util.send_success(ctx, f"**anti-massmention** set to `true`")
		else:
			if await self.bot.db.execute("SELECT * FROM antimention WHERE guild_id = %s", ctx.guild.id, one_value=True):
				self.bot.cache.antimention.pop(ctx.guild.id)
				await self.bot.db.execute("DELETE FROM antimention WHERE guild_id = %s", ctx.guild.id)
				await util.send_success(ctx, f"**anti-massmention** set to `false`")
			else:
				await util.send_success(ctx, f"**anti-massmention** set to `false`")

	@automod.command(name='ip', aliases=['ips', 'antiip', 'antiips'], description="Anti IP Filter", extras={'perms': 'administrator'}, usage="```Swift\nSyntax: !automod ip <bool>\nExample: !automod ip true```",brief="bool")
	async def ip(self, ctx, state:bool):
		if state:
			await self.bot.db.execute("INSERT INTO antiips VALUES(%s)", ctx.guild.id)
			await util.send_success(ctx, f"**anti-ips** set to `true`")
		else:
			if await self.bot.db.execute("SELECT * FROM antiips WHERE guild_id = %s", ctx.guild.id, one_value=True):
				await self.bot.db.execute("DELETE FROM antiips WHERE guild_id = %s", ctx.guild.id)
				await util.send_success(ctx, f"**anti-ips** set to `false`")
			else:
				await util.send_success(ctx, f"**anti-ips** set to `false`")

	@automod.command(name='settings', aliases=['config'], description="Show Current Auto Mod Config", extras={'perms': 'administrator'})
	async def settings(self, ctx):
		if await self.bot.db.execute("SELECT * FROM antispam WHERE guild_id = %s", ctx.guild.id, one_value=True):
			antispam=f"{self.yes}"
		else:
			antispam=f"{self.no}"
		if await self.bot.db.execute("SELECT * FROM antinudity WHERE guild_id = %s", ctx.guild.id, one_value=True):
			antinude=f"{self.yes}"
		else:
			antinude=f"{self.no}"
		if await self.bot.db.execute("SELECT * FROM antilink WHERE channel_id = %s", ctx.channel.id, one_value=True):
			antilink=f"{self.yes}"
		else:
			antilink=f"{self.no}"
		bypass=await self.bot.db.execute("""SELECT role_id FROM spambyp WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if await self.bot.db.execute("SELECT * FROM spambyp WHERE guild_id = %s", ctx.guild.id, one_value=True):
			role=ctx.guild.get_role(bypass) 
			role=role.mention
		else:
			role="None"
		if await self.bot.db.execute("SELECT * FROM antiips WHERE guild_id = %s", ctx.guild.id, one_value=True):
			antiips=f"{self.yes}"
		else:
			antiips=f"{self.no}"
		if await self.bot.db.execute("""SELECT * FROM antiinvite WHERE guild_id = %s""", ctx.guild.id, one_value=True):
			antiinvite=f"{self.yes}"
		else:
			antiinvite=f"{self.no}"
		if await self.bot.db.execute("SELECT * FROM antimention WHERE guild_id = %s", ctx.guild.id, one_value=True):
			ma=await self.bot.db.execute("SELECT max FROM antimention WHERE guild_id = %s", ctx.guild.id, one_value=True)
			antimention=f"{self.yes} ・ **Max**: {ma}"
		else:
			antimention=f"{self.no}"
		desc=f"**Anti-Spam** ・ {antispam}\n**Anti-Nudity** ・ {antinude}\n**Anti-IPS** ・ {antiips}\n**Anti-Link** ・ {antilink}\n**Anti-Invite** ・ {antiinvite}\n**Anti-MassMention** ・ {antimention}\n**Bypass-Role** ・ {role}"
		if ctx.guild.icon:
			thumbnail=ctx.guild.icon
		else:
			thumbnail=self.bot.user.display_avatar
		await ctx.reply(embed=discord.Embed(title=f"{ctx.guild.name}'s automoderation", color=self.color, description=desc).set_thumbnail(url=thumbnail))

	@automod.command(name='enable', aliases=['on', 'true'], description="Enables All Auto Moderation", extras={'perms': 'administrator'})
	async def enable(self, ctx):
		if await self.bot.db.execute("SELECT * FROM antinudity WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antinudity WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antispam WHERE guild_id = %s", ctx.guild.id, one_value=True):
			self.bot.cache.antispam.remove(ctx.guild.id)
			await self.bot.db.execute("DELETE FROM antispam WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antiips WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antiips WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antimention WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antimention WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antiinvite WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antiinvite WHERE guild_id = %s", ctx.guild.id)
		self.bot.cache.antispam.append(ctx.guild.id)
		await self.bot.db.execute("INSERT INTO antinudity VALUES(%s)", ctx.guild.id)
		await self.bot.db.execute("INSERT INTO antiinvite VALUES(%s)", ctx.guild.id)
		await self.bot.db.execute("INSERT INTO antilink VALUES(%s)", ctx.channel.id)
		await self.bot.db.execute("INSERT INTO antispam VALUES(%s)", ctx.guild.id)
		await self.bot.db.execute("INSERT INTO antiips VALUES(%s)", ctx.guild.id)
		await self.bot.db.execute("INSERT INTO antimention VALUES(%s, %s)", ctx.guild.id, 5)
		await util.send_success(ctx, f"**auto moderation** set to `true`")

	@automod.command(name='disable', aliases=['off', 'false'], description="Disables All Auto Moderation", extras={'perms': 'administrator'})
	async def disable(self, ctx):
		if await self.bot.db.execute("SELECT * FROM antinudity WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antinudity WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antiinvite WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antiinvite WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antispam WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antispam WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antiips WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antiips WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antimention WHERE guild_id = %s", ctx.guild.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antimention WHERE guild_id = %s", ctx.guild.id)
		if await self.bot.db.execute("SELECT * FROM antilink WHERE channel_id = %s", ctx.channel.id, one_value=True):
			await self.bot.db.execute("DELETE FROM antilink WHERE channel_id = %s", ctx.channel.id)
		if ctx.guild.id in self.bot.cache.antispam:
			self.bot.cache.antispam.remove(ctx.guild.id)
		await util.send_success(ctx, f"**auto moderation** set to `false`")

	@commands.group(name='roleall', description="give all users a role", extras={'perms': 'administrator'}, usage="```Swift\nSyntax: !roleall <role>\nExample: !roleall users```",brief="role")
	@commands.guild_only()
	@commands.has_permissions(administrator=True)
	async def roleall(self, ctx, *, role: discord.Role=None):
		if role and ctx.invoked_subcommand is None:
			if ctx.guild.id in self.tasks:
				return await ctx.send(embed=discord.Embed(title="roleall", description="There is a roleall task already running, please wait for it to finish", color=self.color))
			await ctx.message.add_reaction("✅")
			num = 0
			failed = 0
			for user in list(ctx.guild.members):
				if role not in user.roles and not user.bot:
					await user.add_roles(role)
					num += 1
			await util.send_success(ctx, f"Successfully added **`%s`** to **`%s`** users" % (role.name, num))
			
	@commands.command(name='nuke', description="recreate and delete current channel", extras={'perms': 'administrator'})
	@commands.guild_only()
	@commands.has_permissions(administrator=True)
	async def nuke(self, ctx):
		if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 714703136270581841:
			counter = 0
			await ctx.send(embed=discord.Embed(title=self.bot.user.name, description=f"Nuking Channel {ctx.channel.name}..."))
			channel_info = [ctx.channel.category, ctx.channel.position]
			channel_id = ctx.channel.id
			await ctx.channel.clone()
			await ctx.channel.delete()
			new_channel = channel_info[0].text_channels[-1]
			await new_channel.edit(position=channel_info[1])
			if await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				cid=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
				if cid==channel_id:
					await self.bot.db.execute("""DELETE FROM welcome WHERE guild_id = %s""", ctx.guild.id)
					await self.bot.db.execute("""INSERT INTO welcome (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)""", ctx.guild.id, new_channel.id)
			embed = discord.Embed(timestamp=ctx.message.created_at)
			embed.set_author(name=f"Channel Nuked.", icon_url=ctx.author.display_avatar)
			embed.set_footer(text=f"{ctx.author}")
			embed.set_image(url=self.bot.user.display_avatar)
			await new_channel.send(embed=embed)
		else:
			await ctx.send(embed=discord.Embed(title=self.bot.user.name, description=f"*Only Available to* ***{ctx.guild.owner}***").set_thumbnail(url=self.bot.user.display_avatar).set_footer(text="Prefix = !"))

	@commands.command(name='lock', description="lock the channel", extras={'perms': 'manage channels'}, usage="```Swift\nSyntax: !lock <channel> <reason> [both optional]\nExample: !lock #chat raid```",brief="channel[optional], reason[optional]")
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	async def lock(self, ctx, channel:discord.TextChannel = None, *, reason=None):
		await ctx.message.delete()
		if channel is None:
			channel = ctx.channel
		if reason:
			description=f"<:lock:1021614489294090240> {ctx.author.mention}: **{channel.mention} has been locked for `{reason}`**"
		else:
			description=f"<:lock:1021614489294090240> {ctx.author.mention}: **{channel.mention} has been locked**"
			try:
				await channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False), reason=f"locked by {ctx.author} for {reason}")
				await ctx.send(embed=discord.Embed(color=self.color, description=description))
			except:
				await util.send_failure(ctx, f"{ctx.author.mention}: **failed to lock {channel.mention}**")
			else:
				pass

	@commands.command(name='fix')
	async def fix(self, ctx, channel:discord.TextChannel=None):
		if not channel: channel=ctx.channel
		for overwrite in channel.overwrites:
			if channel.permissions_for(overwrite).send_messages == True:
				await channel.set_permissions(overwrite, send_messages=False,reason=f"locked by {ctx.author} for {reason}")
		await util.send_good(ctx, f"fixed perms for {channel.mention}")


	@commands.command(name='unlock', description="unlock the channel", extras={'perms': 'manage channels'}, usage="```Swift\nSyntax: !unlock <channel> <reason> [both optional]\nExample: !unlock #chat raid```",brief="channel[optional], reason[optional]")
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	async def unlock(self, ctx, channel:discord.TextChannel = None, *, reason=None):
		await ctx.message.delete()
		if channel is None:
			channel = ctx.channel
		if reason:
			description=f"<:unlock:1021287647206969405> {ctx.author.mention}: **{channel.mention} has been unlocked for `{reason}`**"
		else:
			description=f"<:unlock:1021287647206969405> {ctx.author.mention}: **{channel.mention} has been unlocked**"
			try:
				await channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages = None), reason=reason)
				await ctx.send(embed=discord.Embed(color=self.color, description=description))
			except:
				await util.send_failure(ctx, f"{ctx.author.mention}: **failed to unlock {channel.mention}**")
			else:
				pass

	@commands.command(name='passgen')
	async def passgen(self, ctx, *, numberofcharacters):
		url = f"https://passwordinator.herokuapp.com/generate?num=true&char=true&caps=true&len={numberofcharacters}"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as s:
				c=await s.json()
		em = discord.Embed(color=0xff0000)
		await ctx.send(c['data'])

	@commands.command(name='massmove', aliases=['moveall'], description="move all members from current channel to another channel", brief='destination', usage="```Swift\nSyntax: !massmove <channel>\nExample: !massmove 8434834333```",extras={'perms': 'administrator'})
	@commands.has_permissions(administrator=True)
	async def massmove(self, ctx, destination: discord.VoiceChannel):
		origin=ctx.author.voice.channel
		if origin.members:
			if origin != destination:
				moved = []
				for member in origin.members:
					await member.edit(voice_channel=destination, reason=f"Massmoved by {ctx.author}")
					moved.append(member)
				await util.send_success(ctx, f"{ctx.author.mention}: **Moved `{len(moved)}` members from `{origin.name}` to `{destination.name}`**")
			else:
				await ctx.send(f"You can't move people to the same voice channel that they're already in!")
		else:
			await ctx.send(f"{origin.name} is empty!")

	@commands.command(name='invites')
	@commands.guild_only()
	async def invites(self, ctx, member: discord.Member=None):
		totalInvites = 0
		if member == None:
			member = ctx.message.author
		for i in await ctx.guild.invites():
			if i.inviter == member:
				totalInvites += i.uses
		embed = discord.Embed(color=self.color, description=f"**{member.mention}** has **{str(totalInvites)}** invites").set_thumbnail(url=member.display_avatar)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	async def eid(self, ctx, emoji_id):
		png=f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
		gif=f"https://cdn.discordapp.com/emojis/{emoji_id}.gif"
		await ctx.send(embed=discord.Embed(color=self.color, title=self.bot.user.name, description=f"[png]({png})\n[gif]({gif})"))

	@commands.command(name='status', description="show a members status", brief="member")
	@commands.guild_only()
	async def status(self, ctx, member: discord.Member = None):
		return await util.send_error(ctx, f"disabled feature")
		'''Syntax: !status <member>
		Example: !status @cop#0001'''
		if member is None:
			member = ctx.author
		user = member
		customactivity = ''.join([str(a.name) for a in user.activities if a.type is discord.ActivityType.custom])

		if customactivity == '':
			customactivity = 'None'
		mobile = {
			discord.Status.online: consts.statuses.ONLINE,
			discord.Status.idle: consts.statuses.IDLE,
			discord.Status.dnd: consts.statuses.DND,
			discord.Status.offline: consts.statuses.OFFLINE
		}[member.mobile_status]

		web = {
			discord.Status.online: consts.statuses.ONLINE,
			discord.Status.idle: consts.statuses.IDLE,
			discord.Status.dnd: consts.statuses.DND,
			discord.Status.offline: consts.statuses.OFFLINE
		}[member.web_status]

		desktop = {
			discord.Status.online: consts.statuses.ONLINE,
			discord.Status.idle: consts.statuses.IDLE,
			discord.Status.dnd: consts.statuses.DND,
			discord.Status.offline: consts.statuses.OFFLINE
		}[member.desktop_status]
		status = (
			f"Computer: {desktop} \n"
			f"Web: {web} \n"
			f"Mobile: {mobile} \n"
			f"Activity: {customactivity}"
		)
		embed=discord.Embed(title=f"{member.name}#{member.discriminator}'s Status", description=status, color=self.color).set_thumbnail(url=member.display_avatar).set_footer(text=f"Requested by {ctx.author}")
		await ctx.send(embed=embed)

	@commands.command(name='nickname', aliases=["nick"], description="change a members nickname", brief="member, name", usage="```Swift\nSyntax: !nickname <member> <nick>\nExample: !nickname @cop#0001 dev```",extras={'perms': 'manage_nicknames'})
	@commands.guild_only()
	@commands.has_permissions(manage_nicknames=True)
	async def nickname(self, ctx, member: discord.Member, *, name: str = None):
		if await permissions.check_priv(ctx, member):
			return

		try:
			await member.edit(nick=name, reason=default.responsible(ctx.author, "Changed by command"))
			message = f"Changed **{member.name}'s** nickname to **{name}**"
			if name is None:
				message = f"Reset **{member.name}'s** nickname"
			await ctx.send(embed=discord.Embed(color=self.color, description=message))
		except:
			pass

	@commands.command(name="createrole", aliases=["addrole"], description="create a role", brief="name", usage="```Swift\nSyntax: !createrole <name>\nExample: !createrole dev```",extras={'perms': 'manage roles'})
	@commands.guild_only()
	@commands.has_permissions(manage_roles=True)
	async def createrole(self, ctx, *, name: str):
		guild=ctx.guild
		await guild.create_role(name=name, hoist=True)
		await util.send_success(ctx, f" {ctx.author.mention}: created role {name}")

	@commands.command(name='rcolor', aliases=["rolecolor"])
	@commands.guild_only()
	@commands.has_permissions(manage_roles=True)
	async def rcolor(self, ctx, value: str=None):
		guild=ctx.guild
		role = discord.utils.get(ctx.guild.roles, name=value)
		qul = await ctx.send("Please enter a hex colour:")
		rel = await self.bot.wait_for('message' ,check=(lambda message: message.author == ctx.message.author))
		if '#' in rel.content:
			colour = rel.content.split('#')
			nc = (colour[1])
			nnc = discord.Colour(int(f"0x{nc}", 16))
			await role.edit(color=discord.Colour(int(f"0x{nc}", 16)))
			await util.send_success(ctx, f" {ctx.author.mention}: {role.name}'s color changed to {value}")
		else:
			await ctx.send(embed=discord.Embed(title=self.bot.user.name, description=f"*please format the hex like this: #010202*", color=self.color))

	@commands.command(name='clear', aliases=["cl"], description="clear self or a member", usage="manage_messages[optional]", brief="member[optional]")
	async def clear(self, ctx, member: typing.Optional[discord.Member], search=100):
		if member:
			if not ctx.author.guild_permissions.manage_messages:
				raise commands.MissingPermissions(["manage_messages"])
			else:
				def predicate(m):
					return m.author == member
				try:
					await ctx.message.delete()
				except:
					pass
				await util.do_removal(ctx, search, predicate)
		else:
			try:
				await ctx.message.delete()
			except:
				pass
			def predicate(m):
				return m.author == ctx.author
			await util.do_removal(ctx, search, predicate)

	@commands.command(name='print')
	async def print(self, ctx, content: str = None):
		print(content)

	@commands.command(name='say')
	@commands.is_owner()
	async def say(self, ctx, channel_id: int, *, message):
		channel = self.bot.get_channel(channel_id)
		guild = channel.guild
		await ctx.send(f"Sending message to **{guild}** <#{channel.id}>\n> {message}")
		await channel.send(message)

	@commands.command(name='link')
	async def link(self, ctx, botid: int = None):
		if botid == None:
			botid=self.bot.user.id
		else:
			botid=botid
		link=f"https://discord.com/oauth2/authorize?client_id={botid}&permissions=8&scope=applications.commands%20bot"
		await ctx.send(link)

	@commands.hybrid_command(name='bc', with_app_command=True, description='purge bot msgs', extras={'perms': 'manage_messages'})
	@commands.has_permissions(manage_messages=True)
	async def bc(self, ctx):
		def predicate(m):
			return m.author.bot or m.content.startswith(f"{ctx.prefix}")
		try:
			await ctx.message.delete()
		except:
			pass
		deleted=await util.do_removal(ctx, 100, predicate)
		await util.send_good(ctx, f" purged {deleted} messages from bots", delete=5)

	@commands.command(name='selfrole')
	@commands.guild_only()
	@commands.is_owner()
	async def selfrole(self, ctx, member: discord.Member, *, r: discord.Role):
		if r in member.roles:
			await member.remove_roles(r)
			embed = discord.Embed(title=f"___**{self.bot.user.name}#{self.bot.user.discriminator}**___", description=f"{r.name} removed from {member.name}")
			await ctx.send(embed=embed)
		else:
			await member.add_roles(r)
			embed = discord.Embed(title=f"___**{self.bot.user.name}#{self.bot.user.discriminator}**___", description=f"{r.name} added to {member.name}")
			await ctx.send(embed=embed)

	@commands.command(name='cum', aliases=["jerkoff", "ejaculate", "orgasm"])
	@commands.is_owner()
	async def cum(self, ctx):
		message = await ctx.send(''''
			:ok_hand:            :smile:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8=:punch:=D 
			 :trumpet:      :eggplant:''')
		await asyncio.sleep(0.5)
		await message.edit(content='''
					  :ok_hand:            :smiley:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8==:punch:D 
			 :trumpet:      :eggplant:  
	 ''')
		await asyncio.sleep(0.5)
		await message.edit(content='''
					  :ok_hand:            :grimacing:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8=:punch:=D 
			 :trumpet:      :eggplant:  
	 ''')
		await asyncio.sleep(0.5)
		await message.edit(content='''
					  :ok_hand:            :persevere:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8==:punch:D 
			 :trumpet:      :eggplant:   
	 ''')
		await asyncio.sleep(0.5)
		await message.edit(content='''
					  :ok_hand:            :confounded:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8=:punch:=D 
			 :trumpet:      :eggplant: 
	 ''')
		await asyncio.sleep(0.5)
		await message.edit(content='''
					   :ok_hand:            :tired_face:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8==:punch:D 
			 :trumpet:      :eggplant:    
			 ''')
		await asyncio.sleep(0.5)
		await message.edit(content='''
					   :ok_hand:            :weary:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8=:punch:= D:sweat_drops:
			 :trumpet:      :eggplant:        
	 ''')
		await asyncio.sleep(0.5)
		await message.edit(content='''
					   :ok_hand:            :dizzy_face:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8==:punch:D :sweat_drops:
			 :trumpet:      :eggplant:                 :sweat_drops:
	 ''')
		await asyncio.sleep(0.5)
		await message.edit(content='''
					   :ok_hand:            :drooling_face:
   :eggplant: :zzz: :necktie: :eggplant: 
				   :oil:     :nose:
				 :zap: 8==:punch:D :sweat_drops:
			 :trumpet:      :eggplant:                 :sweat_drops:
	 ''')

	@commands.command(name='donators', aliases=['donors'], description='show current rival donators')
	async def donators(self, ctx):
		rows=[]
		users=[]
		db=await self.bot.db.execute("""SELECT * FROM dnr""")
		for user_id, ts in db:
			try:
				user = self.bot.get_user(user_id)
			except:
				user = await self.bot.fetch_user(user_id)
			users.append(user)
			timestamp=discord.utils.format_dt(ts, style="R")
			rows.append(f"{user} **・** {timestamp}")
		g=await self.bot.fetch_guild(918445509599977472)
		guild=self.bot.get_guild(g.id)
		for member in guild.premium_subscribers:
			if member not in users:
				timestamp=discord.utils.format_dt(member.premium_since, style="R")
				rows.append(f"{str(member)} **・** {timestamp}")
		if rows:
			content = discord.Embed(title="Rival's Donators", color=discord.Color.gold())
			await util.send_as_pages(ctx, content, rows)

	@commands.command(name='donorcheck')
	async def donorcheck(self, ctx):
		if await self.bot.db.execute("""SELECT * FROM dnr WHERE user_id = %s""", ctx.author.id):
			return await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} you **are** donator"))
		else:
			return await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} you **aren't** donator"))
		
	@commands.command(name='purge', description='purge messages', brief="member/amount/images/amount", usage="```Swift\nExamples: \n!purge @member <amount> \n!purge <amount>\n!purge images <amount>\n!purge help```",extras={'perms': 'manage_messages'}, aliases=['c'])
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, args:typing.Union[discord.Member, int, str, discord.User]=None, amount: typing.Optional[int]=None):
		async with self.locks[ctx.channel.id]:
			msgs=[]
			if args == None:
				return await ctx.reply(embed=discord.Embed(title="Purge Help", description="!purge @member <amount>\n!purge <amount>\n!purge images <amount>"))
			try:
				await ctx.message.delete()
			except:
				pass
			if isinstance(args, discord.Member):
				try:
					await ctx.message.delete()
				except:
					pass
				if amount:
					search=amount+1
				else:
					search=100
				if search >= 2000:
					return await util.send_failure(ctx, f"{ctx.author.mention}: **purge limit is 2000**")
				member=args
				async for m in ctx.channel.history():
					if len(msgs) == search:
						break
					if m.author == member:
						msgs.append(m)
				await ctx.channel.delete_messages(msgs)
				#deleted=await util.do_removal(ctx, search, lambda e: e.author == member)
				return await util.send_good(ctx, f" purged {len(msgs)} messages from {member.mention}", delete=True)
			if isinstance(args, int):
				search=args
				amount=search/100
				deleted=await util.do_removal(ctx, search, lambda e: True)
				return await util.send_good(ctx, f" purged {deleted} messages", delete=True)
			if isinstance(args, str):
				msgs=['messages', 'msgs']
				imgs=['imgs', 'images']
				h=['help', 'cmds', 'h']
				if amount is None:
					search=100
				else:
					search=amount
				if args.lower() in msgs:
					def predicate(m):
						return m.attachments is None
					deleted=await util.do_removal(ctx, search, predicate)
					try:
						await ctx.message.delete()
					except:
						pass
					return await util.send_good(ctx, f" **purged `{deleted}` messages that do not contain immages**", delete=True)
				if args.lower() in h:
					return await ctx.reply(embed=discord.Embed(title="Purge Help", description="!purge @member <amount>\n!purge <amount>\n!purge images <amount>\n!purge messages <amount>"))
				if args.lower() in imgs:
					try:
						await ctx.message.delete()
					except:
						pass
					deleted=await util.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))
					return await util.send_good(ctx, f" purged {deleted} images", delete=True)
				else:
					await ctx.reply(embed=discord.Embed(title="Purge Help", description="!purge @member <amount>\n!purge <amount>\n!purge images <amount>"))
			if isinstance(args, discord.User):
				try:
					await ctx.message.delete()
				except:
					pass
				if amount:
					search=amount+1
				else:
					search=100
				if search >= 2000:
					return await util.send_failure(ctx, f"{ctx.author.mention}: **purge limit is 2000**")
				member=args
				async for m in ctx.channel.history():
					if len(msgs) == search:
						break
					if m.author.id == member.id:
						msgs.append(m)
				await ctx.channel.delete_messages(msgs)
				#deleted=await util.do_removal(ctx, search, lambda e: e.author == member)
				return await util.send_good(ctx, f" purged {len(msgs)} messages from {member.mention}", delete=True)

	@commands.command(name='imageclear', aliases=["ic"], description='clear images', usage='manage_messages', brief='amount[optional]')
	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	async def imageclear(self, ctx, search=100):
		async def do_removal(self, ctx, limit, predicate, *, before=None, after=None, message=True):
			if limit > 2000:
				return await ctx.send(f"Too many messages to search given ({limit}/2000)")

			if not before:
				before = ctx.message
			else:
				before = discord.Object(id=before)

			if after:
				after = discord.Object(id=after)

			try:
				deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
			except discord.Forbidden:
				return await ctx.send("I do not have permissions to delete messages.")
			except discord.HTTPException as e:
				return await ctx.send(f"Error: {e} (try a smaller search?)")


		deleted=await util.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))
		await util.send_successs(ctx, f" purged {deleted} images")

	@commands.command(name='joinpos')
	@commands.guild_only()
	async def joinpos(self, ctx, member: discord.Member = None):
		joinedList = []
		if member == None:
			member = ctx.author
		for mem in ctx.message.guild.members:
			joinedList.append({ 'ID' : mem.id, 'Joined' : mem.joined_at })
		
		# sort the users by join date
		joinedList = sorted(joinedList, key=lambda x:x["Joined"].timestamp() if x["Joined"] != None else -1)

		check_item = { "ID" : member.id, "Joined" : member.joined_at }

		total = len(joinedList)
		position = joinedList.index(check_item) + 1

		before = ""
		after  = ""
		
		msg = "*{}'s* join position is **{:,}**.".format((member), position, total)
		if position-1 == 1:
			# We have previous members
			before = "**1** user"
		elif position-1 > 1:
			before = "**{:,}** users".format(position-1)
		if total-position == 1:
			# There were users after as well
			after = "**1** user"
		elif total-position > 1:
			after = "**{:,}** users".format(total-position)
		# Build the string!
		if len(before) and len(after):
			# Got both
			msg += "\n\n{} joined before, and {} after.".format(before, after)
		elif len(before):
			# Just got before
			msg += "\n\n{} joined before.".format(before)
		elif len(after):
			# Just after
			msg += "\n\n{} joined after.".format(after)
		await ctx.send(msg)

	@commands.command(name='forcenick', aliases=['fn'], description="force a member's nickname", extras={'perms':'administrator / donator server'}, usage="```Swift\nSyntax: !forcenick <user> <name>\nExample: !forcenick @rival best bot```",brief="member, text")
	@util.donor_server()
	@commands.has_permissions(administrator=True)
	async def forcenick(self, ctx, member: discord.Member, *, text=None):
		if text == None:
			if member.id in self.forcenicked:
				if self.forcenicked[member.id]:
					del self.forcenicked[member.id]
					await util.send_successs(ctx, f"**no longer forcing {member.mention}'s nickname**")
					await member.edit(nick=None)
				else:
					return await util.send_failure(ctx, f"**{member.mention} is not in the forcenick list**")
			else:
				return await util.send_failure(ctx, f"**{member.mention} is not in the forcenick list**")
		else:
			if member.id in self.forcenicked:
				if self.forcenicked[member.id]:
					self.forcenicked[member.id].pop()
			await util.send_successs(ctx, f"**forcing {member.mention}'s nickname to `{text}`**")
			self.forcenicked[member.id] = [f"{text}"]
			await member.edit(nick=text)

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if before.nick == after.nick:
			return
		try:
			if self.forcenicked[before.id]:
				txt=self.forcenicked[before.id][0]
				if after.nick != txt:
					await before.edit(nick=txt, reason="Forced Nickname")
					return
		except:
			pass
		data=await self.bot.db.execute("""SELECT ts FROM namehistory WHERE user_id = %s AND name = %s""", before.id, after.nick, one_value=True)
		if data:
			equation=datetime.now().timestamp() - data.timestamp()
			if equation >= 10800:
				return
		else:
			if after.nick == None:
				tag=f"{after.name}"
			else:
				tag=f"{after.nick}"
			await self.bot.db.execute("""INSERT INTO namehistory VALUES(%s, %s, %s)""", before.id, tag, datetime.now())

	@commands.Cog.listener()
	async def on_member_join(self, member):
		try:
			if self.forcenicked[member.id]:
				txt=self.forcenicked[member.id][0]
				if member.nick != txt:
					await member.edit(nick=txt, reason="Forced Nickname")
					return
		except:
			pass

async def setup(bot):
	await bot.add_cog(cmds(bot))


class InstagramIdCodec:
	ENCODING_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

	@staticmethod
	def encode(num, alphabet=ENCODING_CHARS):
		"""Covert a numeric value to a shortcode."""
		num = int(num)
		if num == 0:
			return alphabet[0]
		arr = []
		base = len(alphabet)
		while num:
			rem = num % base
			num //= base
			arr.append(alphabet[rem])
		arr.reverse()
		return "".join(arr)

	@staticmethod
	def decode(shortcode, alphabet=ENCODING_CHARS):
		"""Covert a shortcode to a numeric value."""
		base = len(alphabet)
		strlen = len(shortcode)
		num = 0
		idx = 0
		for char in shortcode:
			power = strlen - (idx + 1)
			num += alphabet.index(char) * (base**power)
			idx += 1
		return num