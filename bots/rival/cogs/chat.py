import arrow, unidecode, discord, humanize, datetime, asyncio, re, regex, requests, random, json, tempfile, shutil, os, typing
from discord.ext import commands,tasks
from libraries import emoji_literals
from typing import Union
import multiprocessing
from bs4 import BeautifulSoup
from modules import exceptions, log, queries, util, Message, DL, DisplayName, permissions
from ast import Bytes
from io import BytesIO
from shazamio import Shazam
from cogs.embed import embed
from pydub import AudioSegment
from modules.asynciterations import aiter
AudioSegment.converter = "/usr/bin/ffmpeg"
AudioSegment.ffmpeg = "/usr/bin/ffmpeg"
AudioSegment.ffprobe ="/usr/bin/ffprobe"


tikTokDomains = ('http://vt.tiktok.com', 'http://app-va.tiktokv.com', 'http://vm.tiktok.com', 'http://m.tiktok.com', 'http://tiktok.com', 'http://www.tiktok.com', 'http://link.e.tiktok.com', 'http://us.tiktok.com','https://vt.tiktok.com', 'https://app-va.tiktokv.com', 'https://vm.tiktok.com', 'https://m.tiktok.com', 'https://tiktok.com', 'https://www.tiktok.com', 'https://link.e.tiktok.com', 'https://us.tiktok.com')
headers = {
	'user-agent': 'Mozilla/5.0 (Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
}


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

async def not_server_owner_msg(ctx, text):
	if text:
		text=text
	else:
		text="Guild Owner"
	embed = discord.Embed(
		description=f"{self.bot.warn} {ctx.author.mention}: this command can **only** be used by the `{text}`",
		colour=0xfaa61a,
	)
	return embed

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

class ChannelSetting(commands.TextChannelConverter):
	"""This enables removing a channel from the database in the same command that adds it."""

	async def convert(self, ctx, argument):
		if argument.lower() in ["disable", "none", "delete", "remove"]:
			return None
		return await super().convert(ctx, argument)

class chat(commands.Cog, name="chat"):
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
		self.events={}
		self.no=self.bot.no
		self.bad=self.bot.color#0xff6465
		self.color=self.bot.color
		self.ch='<:yes:940723483204255794>'
		self.error=self.bot.color#0xfaa61a
		self.warn=self.bot.warn
		self.event_loop.start()
		self.cd_mapping = commands.CooldownMapping.from_cooldown(10, 10, commands.BucketType.member)
		self._cd = commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member)

	def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		"""Returns the ratelimit left"""
		bucket = self._cd.get_bucket(message)
		return bucket.update_rate_limit()

	def _get_embed_from_json(self, ctx, embed_json):
		# Helper method to ensure embed_json is valid, and doesn't bypass limits
		# Let's attempt to serialize the json
		try:
			embed_dict = json.loads(embed_json)
		except:
			embed_dict=embed_json
		try:
			# Let's parse the author and color
			if embed_dict.get("thumbnail"):
				if "www." in embed_dict["thumbnail"]: embed_dict["thumbnail"] = embed_dict["thumbnail"].replace("www.","https://")
				if "http://" in embed_dict["thumbnail"]: embed_dict["thumbnail"] = embed_dict["thumbnail"].replace("http://","https://")
				if not "https://" in embed_dict["thumbnail"]: embed_dict["thumbnail"] = f"https://"+embed_dict["thumbnail"]
			if embed_dict.get("image"):
				if "www." in embed_dict["image"]: embed_dict["image"] = embed_dict["image"].replace("www.","https://")
				if "http://" in embed_dict["image"]: embed_dict["image"] = embed_dict["image"].replace("http://","https://")
				if not "https://" in embed_dict["image"]: embed_dict["image"] = f"https://"+embed_dict["image"]
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
					embed_dict["color"] = color_value if color_value is not None else "#303135"
			if embed_dict.get("author") and not isinstance(embed_dict["author"],dict):
				# Again - got *something* for the author - try to resolve it
				embed_dict["author"] = DisplayName.memberForName(str(embed_dict["author"]),ctx.guild)
			if embed_dict.get("timestamp"):
				#ts=embed_dict.get("timestamp")
				#embed_dict["timestamp"]=datetime.datetime.strptime(ts, format=)
				dt=datetime.datetime.now().timestamp()
				embed_dict["timestamp"]=f"{dt}"
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

	@tasks.loop(minutes=2)
	async def events_clear(self):
		self.events.clear()
		logger.info("Event Cache Loop Cleared")


	async def custom_command_list(self, guild_id, match=""):
		"""Returns a list of custom commands on server."""
		command_list = set()
		data = await self.bot.db.execute(
			"SELECT command_trigger, content FROM custom_command WHERE guild_id = %s", guild_id
		)
		async for command_trigger, content in aiter(data):
			command_name = str(command_trigger)
			content = content
			if match == "" or match in command_name:
				command_list.add(f"**{command_name}** ・ `{str(content)}`")

		return command_list

	async def react_command_list(self, guild_id, match=""):
		"""Returns a list of custom commands on server."""
		react_list = set()
		data = await self.bot.db.execute(
			"SELECT trig,content FROM react WHERE guild_id = %s", guild_id
		)
		async for command_name, content in aiter(data):
			command_name = str(command_name)
			content=content
			if match == "" or match in command_name:
				react_list.add(f"**{command_name}** ・ {content}")

		return react_list

	async def filter_llist(self, guild_id, match=""):
		"""Returns a list of custom commands on server."""
		filter_llist = set()
		data = await self.bot.db.execute(
			"SELECT strr FROM chatfilter WHERE guild_id = %s", guild_id
		)
		async for strr in aiter(data):
			strr = strr[0]
			if match == "" or match in strr:
				filter_llist.add(strr)

		return filter_llist

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""Check for custom commands on CommandNotFound."""
		# no custom commands in DMs
		if ctx.guild is None:
			return

		error = getattr(error, "original", error)
		if isinstance(error, commands.CommandNotFound):
			keyword = ctx.message.content[len(ctx.prefix) :].split(" ", 1)[0]
			response = await self.bot.db.execute(
				"SELECT content FROM custom_command WHERE guild_id = %s AND command_trigger = %s",
				ctx.guild.id,
				keyword,
				one_value=True,
			)
			if response:
				await ctx.send(response)
				await self.bot.db.execute(
					"""
					INSERT INTO command_usage (guild_id, user_id, command_name, command_type)
						VALUES (%s, %s, %s, %s)
					ON DUPLICATE KEY UPDATE
						uses = uses + 1
					""",
					ctx.guild.id,
					ctx.author.id,
					keyword,
					"custom",
				)

	@tasks.loop(minutes=5)
	async def event_loop(self):
		self.events.clear()

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if not member.guild.me.guild_permissions.administrator:
			return
		if await self.bot.db.execute("""SELECT * FROM jail WHERE user_id = %s AND guild_id = %s""", member.id, member.guild.id):
			try:
				jail_role = discord.utils.get(member.guild.roles, name="jailed")
				await member.add_roles(jail_role)
			except:
				pass
		#data=await self.bot.db.execute("""SELECT * FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
		#if not data:
		#	return
		#if member.guild.id not in self.bot.cache.welcomechannels:
			#return
		joins=await self.bot.db.execute("""SELECT amount FROM joins WHERE guild_id = %s""", member.guild.id, one_value=True)
		trig=await self.bot.db.execute("""SELECT * FROM antiraidtrigger WHERE guild_id = %s""", member.guild.id)
		if member.guild.id not in self.events:
			self.events[member.guild.id]=0
		self.events[member.guild.id]+=1
		if self.events[member.guild.id] >= 20:
			return
		if trig:	
			async for trigger in aiter(trig):
				trigger=trigger
			try:
				if joins > trigger:
					return
			except:
				pass
		await asyncio.sleep(1)
		if member.guild.id in self.bot.cache.welcomechannels:
		#welcchannel=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
			pass
		else:
			if member.guild.name == 'rival':
				return print('no channel')
			else:
				return
		if member.guild.id in self.bot.cache.welcomemessages:
			pass
		else:
			if member.guild.name == 'rival':
				return print('no message')
			else:
				return
		welcchannel=self.bot.cache.welcomechannels[member.guild.id]
		if welcchannel:
			welcchannel=self.bot.cache.welcomechannels[member.guild.id]
			channel=self.bot.get_channel(welcchannel)
			if not channel:
				return
			if not channel.guild.me.guild_permissions.send_messages:
				return
			if not channel.guild.me.guild_permissions.embed_links or not channel.guild.me.guild_permissions.attach_files:
				return
			if not member.guild.id in self.events:
				self.events[member.guild.id]=1
			else:
				self.events[member.guild.id]+=1
			if self.events[member.guild.id] >= 10:
				await asyncio.sleep(5)
			#msg=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", member.guild.id, one_value=True)
			msg=self.bot.cache.welcomemessages[member.guild.id]
			if msg:
				if msg.startswith("{embed}") or "content:" in msg:
					params=await util.embed_replacement(member,member.guild,msg)
					return await util.to_embed(channel,member,member.guild,params)
				else:
					msg=await util.embed_replacement(member,member.guild,msg)
					if "$(server)" in str(msg):
						msg = msg.replace("$(server)", member.guild.name)
					if "$(server.count)" in msg:
						msg = msg.replace("$(server.count)", str(len([m for m in member.guild.members])))
					if "$(server.avatar)" in msg:
						if member.guild.icon:
							avatar=member.guild.icon.url
						else:
							avatar=None
						msg = msg.replace("$(server.avatar)", avatar)
					if "\\n" in msg:
						msg=msg.replace('\\\\','\\')
					if "$(mention)" in msg:
						msg = msg.replace("$(mention)", member.mention)
					if "$(user.name)" in msg:
						msg = msg.replace("$(user.name)", member.name)
					if "$(user)" in msg:
						msg = msg.replace("$(user)", str(member))
					if "$(joindate)" in msg:
						msg = msg.replace("$(joindate)", discord.utils.format_dt(member.joined_at, style="R"))
					if "$(memberdate)" in msg:
						msg = msg.replace("$(memberdate)", discord.utils.format_dt(member.created_at, style="R"))
					if "$(guilddate)" in msg:
						msg = msg.replace("$(guilddate)", discord.utils.format_dt(member.guild.created_at, style="R"))
					if "$(now)" in msg:
						#msg = msg.replace("$(now)", discord.utils.format_dt(datetime.datetime.now(), style="R"))
						dt=datetime.datetime.now().timestamp()
						msg = msg.replace("$(now)", f"{dt}")
					if "$(user.tag)" in msg:
						usertag=f"{member.name}#{member.discriminator}"
						msg = msg.replace("$(user.tag)", usertag)
					if "$(server.avatar)" in msg:
						if member.guild.icon:
							avatar=member.guild.icon.url
						else:
							avatar=None
						msg = msg.replace("$(server.avatar)", avatar)
					if "$(server.count.display)" in msg:
						ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
						msg = msg.replace("$(server.count.display)", ordinal(len(member.guild.members)))
					if "$(user.avatar)" in msg:
						msg = msg.replace("$(user.avatar)", member.display_avatar.url)
					if "{" in msg:
						embed_dict = self._get_embed_from_json(channel,msg)
						embedd=json.loads(msg)
						if not embedd.get("description") and not embedd.get("title") and embedd.get("content"):
							delete=embedd.get("autodelete", None)        
							await channel.send(delete_after=delete, content=embedd["content"])
						if isinstance(embed_dict,Exception):
							return await Message.EmbedText(title="Something went wrong...", description=str(embed_dict)).send(channel)
					try:
						if not msg.startswith("{"):
							return await channel.send(msg)
						elif "}" not in msg:
							return await channel.send(msg)
						else:
							try:
								await Message.Embed(**embed_dict).send(channel)
							except Exception as e:
								print(e)
								pass
					except Exception as e:
						print(e)
						pass

	# @commands.Cog.listener()
	# async def on_member_join(self, member):
	# 	if await self.bot.db.execute("""SELECT * FROM jail WHERE user_id = %s AND guild_id = %s""", member.id, member.guild.id):
	# 		try:
	# 			jail_role = discord.utils.get(member.guild.roles, name="jailed")
	# 			await member.add_roles(jail_role)
	# 		except:
	# 			pass
	# 	data=await self.bot.db.execute("""SELECT * FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
	# 	if not data:
	# 		return
	# 	joins=await self.bot.db.execute("""SELECT amount FROM joins WHERE guild_id = %s""", member.guild.id, one_value=True)
	# 	trig=await self.bot.db.execute("""SELECT * FROM antiraidtrigger WHERE guild_id = %s""", member.guild.id)
	# 	if trig:	
	# 		for trigger in trig:
	# 			trigger=trigger
	# 		try:
	# 			if joins > trigger:
	# 				return
	# 		except:
	# 			pass
	# 	await asyncio.sleep(1)
	# 	welcchannel=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
	# 	channel=self.bot.get_channel(welcchannel)
	# 	if not channel:
	# 		return
	# 	msg=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", member.guild.id, one_value=True)
	# 	dic=json.loads(msg)
	# 	for msg in dic.values():
	# 		if "{server}" in str(msg):
	# 			msg = msg.replace("{server}", member.guild.name)
	# 		if "{server.count}" in msg:
	# 			msg = msg.replace("{server.count}", str(len([m for m in member.guild.members])))
	# 		if "{server.avatar}" in msg:
	# 			if member.guild.icon:
	# 				avatar=member.guild.icon.url
	# 			else:
	# 				avatar=None
	# 			msg = msg.replace("{server.avatar}", avatar)
	# 		if "\\n" in msg:
	# 			msg=msg.replace('\\\\','\\')
	# 		if "{mention}" in msg:
	# 			msg = msg.replace("{mention}", member.mention)
	# 		if "{user.name}" in msg:
	# 			msg = msg.replace("{user.name}", member.name)
	# 		if "{user}" in msg:
	# 			msg = msg.replace("{user}", str(member))
	# 		if "{joindate}" in msg:
	# 			msg = msg.replace("{joindate}", discord.utils.format_dt(member.joined_at, style="R"))
	# 		if "{memberdate}" in msg:
	# 			msg = msg.replace("{memberdate}", discord.utils.format_dt(member.created_at, style="R"))
	# 		if "{guilddate}" in msg:
	# 			msg = msg.replace("{guilddate}", discord.utils.format_dt(member.guild.created_at, style="R"))
	# 		if "{now}" in msg:
	# 			#msg = msg.replace("{now}", discord.utils.format_dt(datetime.datetime.now(), style="R"))
	# 			dt=datetime.datetime.now().timestamp()
	# 			msg = msg.replace("{now}", f"{dt}")
	# 		if "{user.tag}" in msg:
	# 			usertag=f"{member.name}#{member.discriminator}"
	# 			msg = msg.replace("{user.tag}", usertag)
	# 		if "{server.avatar}" in msg:
	# 			if member.guild.icon:
	# 				avatar=member.guild.icon.url
	# 			else:
	# 				avatar=None
	# 			msg = msg.replace("{server.avatar}", avatar)
	# 		if "{server.count.display}" in msg:
	# 			ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
	# 			msg = msg.replace("{server.count.display}", ordinal(len(member.guild.members)))
	# 		if "{user.avatar}" in msg:
	# 			msg = msg.replace("{user.avatar}", member.display_avatar.url)
	# 	if "{" in dic:
	# 		embed_dict = self._get_embed_from_json(channel,dic)
	# 		embedd=json.loads(msg)
	# 		if not embedd.get("description") and not embedd.get("title") and embedd.get("content"):
	# 			delete=embedd.get("autodelete", None)        
	# 			await channel.send(delete_after=delete, content=embedd["content"])
	# 		if isinstance(embed_dict,Exception):
	# 			return await Message.EmbedText(title="Something went wrong...", description=str(embed_dict)).send(channel)
	# 	try:
	# 		if not msg.startswith("{"):
	# 			return await channel.send(msg)
	# 		elif "}" not in msg:
	# 			return await channel.send(msg)
	# 		else:
	# 			try:
	# 				await Message.Embed(**embed_dict).send(channel)
	# 			except:
	# 				pass
	# 	except:
	# 		pass

	@commands.group(name='welcome', aliases=['welc','wlc'],description='welcome message setup')
	@commands.has_permissions(administrator=True)
	async def welcome(self, ctx):
		if ctx.invoked_subcommand is None:
			embed=discord.Embed(color=self.bot.color, description=f"""**Valid SubCommands:**\n`message`, `channel`, `config`, `test`, `help`\nFor Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)""")
			await ctx.reply(embed=embed)

	@welcome.command(name='help', description='shows commands / variables for welcome messages')
	@commands.has_permissions(administrator=True)
	async def aaaahelp(self, ctx):
		embed=discord.Embed(color=self.bot.color, description=f"""**Valid SubCommands:**\n`message`, `channel`, `config`, `test`, `help`\nFor Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)""")
		await ctx.reply(embed=embed)

	@welcome.command(name='message', aliases=['msg'], description='sets the welcome message', extras={'perms':'Guild Owner'}, brief="message")
	@commands.has_permissions(administrator=True)
	async def amessage(self, ctx: commands.Context, *, args=None):
		if args:
			if await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id)
			if "\\n" in args:
				args=args.replace('\\\\','\\')
			self.bot.cache.welcomemessages[ctx.guild.id]=args
			await self.bot.db.execute("""INSERT INTO wlcmsg (guild_id, message) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message)""", ctx.guild.id, args)
			await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome message to `{args}`", color=self.good))
		else:
			if await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id)
				if ctx.guild.id in self.bot.cache.welcomemessages:
					self.bot.cache.welcomemessages.pop(ctx.guild.id)
				await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome message cleared**", color=self.good))
			else:
				await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a message**", color=self.error))

	@welcome.command(name='channel', aliases=['c'], description='sets the welcome channel', extras={'perms':'Guild Owner'}, brief="channel")
	@commands.has_permissions(administrator=True)
	async def achannel(self, ctx, textchannel:discord.TextChannel=None):
		if textchannel:
			if await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM welcome WHERE guild_id = %s""", ctx.guild.id)
			await self.bot.db.execute("""INSERT INTO welcome (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)""", ctx.guild.id, textchannel.id)
			self.bot.cache.welcomechannels[ctx.guild.id]=int(textchannel.id)
			await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome channel to {textchannel.mention}", color=self.good))
		else:
			if await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM welcome WHERE guild_id = %s""", ctx.guild.id)
				if ctx.guild.id in self.bot.cache.welcomechannels:
					self.bot.cache.welcomechannels.pop(ctx.guild.id)
				await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome channel cleared**", color=self.good))
			else:
				await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a channel**", color=self.error))

	@welcome.command(name='test', description='test the current welcome config')
	@commands.has_permissions(administrator=True)
	async def aatest(self, ctx):
		member=ctx.author
		data=await self.bot.db.execute("""SELECT * FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
		if not data:
			return await util.send_error(ctx, f"no data found")
		welcchannel=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
		channel=self.bot.get_channel(welcchannel)
		if not channel:
			return await util.send_failure(ctx, f"{ctx.author.mention}: **welcome channel not set**")
		msg=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", member.guild.id, one_value=True)
		if not msg:
			return await util.send_failure(ctx, f"{ctx.author.mention}: **welcome message not set**")
		if msg.startswith("{embed}"):
			params=await util.embed_replacement(member,ctx.guild,msg)
			return await util.to_embed(channel,member,ctx.guild,params)
		else:
			if "\\n" in msg:
				msg=msg.replace('\\\\','\\')
			if "$(server)" in str(msg):
				msg = msg.replace("$(server)", member.guild.name)
			if "$(server.count)" in msg:
				msg = msg.replace("$(server.count)", str(len([m for m in member.guild.members])))
			if "$(server.count.display)" in msg:
				ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
				msg = msg.replace("$(server.count.display)", ordinal(len(ctx.guild.members)))
			if "$(mention)" in msg:
				msg = msg.replace("$(mention)", member.mention)
			if "$(user.name)" in msg:
				msg = msg.replace("$(user.name)", member.name)
			if "$(user)" in msg:
				msg = msg.replace("$(user)", str(member))
			if "$(user.tag)" in msg:
				usertag=f"{member.name}#{member.discriminator}"
				msg = msg.replace("$(user.tag)", usertag)
			if "$(joindate)" in msg:
				msg = msg.replace("$(joindate)", discord.utils.format_dt(member.joined_at, style="R"))
			if "$(memberdate)" in msg:
				msg = msg.replace("$(memberdate)", discord.utils.format_dt(member.created_at, style="R"))
			if "$(guilddate)" in msg:
				msg = msg.replace("$(guilddate)", discord.utils.format_dt(member.guild.created_at, style="R"))
			if "$(now)" in msg:
				#msg = msg.replace("$(now)", discord.utils.format_dt(f"{datetime.datetime.now()}", style="R"))
				dt=datetime.datetime.now().timestamp()
				msg = msg.replace("$(now)", f"{dt}")
			if "$(server.avatar)" in msg:
				if member.guild.icon:
					avatar=member.guild.icon.url
				else:
					avatar=None
				msg = msg.replace("$(server.avatar)", avatar)
			if "$(user.avatar)" in msg:
				msg = msg.replace("$(user.avatar)", member.display_avatar.url)
			if msg.startswith("{"):
				embed_dict = self._get_embed_from_json(channel,msg)
				embedd=json.loads(msg)
				if not embedd.get("description") and not embedd.get("title") and embedd.get("content"):
					delete=embedd.get("autodelete", None)        
					return await channel.send(delete_after=delete, content=embedd["content"])
				else:				
					if isinstance(embed_dict,Exception):
						return await Message.EmbedText(title="Something went wrong...", description=str(embed_dict)).send(channel)
					await Message.Embed(**embed_dict).send(channel)
			else:
				await channel.send(content=msg)

	@welcome.command(name='config', aliases=['settings', 'cfg'], description='shows the current welcome config')
	@commands.has_permissions(administrator=True)
	async def config(self, ctx):
		data=await self.bot.db.execute("""SELECT * FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		welcchannel=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if not welcchannel:
			return await util.send_failure(ctx, f"{ctx.author.mention}: welcome **channel** not set")
		if not data:
			return await util.send_failure(ctx, f"{ctx.author.mention}: welcome **message** not set")
		channel=self.bot.get_channel(welcchannel)
		msg=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if data:
			if channel:
				c=channel.mention
			else:
				c="None"
			embed=discord.Embed(title=f"{ctx.guild.name}'s welcome config", color=self.bot.color)
			embed.add_field(name='Message', value=f"`{msg}`", inline=True)
			embed.add_field(name='Channel', value=c, inline=True)
			await ctx.send(embed=embed)

	@commands.command(name='setme', aliases=['setup'], description="setup the moderation system", extras={'perms':'administrator'})
	@commands.has_permissions(administrator=True)
	async def setme(self, ctx):
		loading=str(self.bot.get_emoji(940728015640481822))
		embed=discord.Embed(color=self.bot.color, description=f"{loading} *Setting up Jail permissions...*").set_thumbnail(url=self.bot.user.avatar.url).set_footer(text="Prefix = !")
		guild = ctx.guild
		jail_c = discord.utils.get(ctx.guild.text_channels, name="jail")
		jail_r = discord.utils.get(ctx.guild.roles, name="jailed")
		if not jail_c:	
			await guild.create_text_channel(name="jail")
		if not jail_r:
			await guild.create_role(name="jailed")
		jail_channel = discord.utils.get(ctx.guild.text_channels, name="jail")
		jail_role = discord.utils.get(ctx.guild.roles, name="jailed")
		jail_deny_text = discord.PermissionOverwrite(read_messages=False)
		jail_deny_voice = discord.PermissionOverwrite(connect=False)
		jail_allow = discord.PermissionOverwrite(read_messages=True, send_messages=True)

		msg=await ctx.send(embed=embed)

		for channel in ctx.guild.channels:
			if isinstance(channel, discord.TextChannel):
				if channel == jail_channel:
					await channel.set_permissions(jail_role, overwrite=jail_allow)
					await channel.set_permissions(ctx.guild.default_role, overwrite=jail_deny_text)
				else:
					await channel.set_permissions(jail_role, overwrite=jail_deny_text)
			elif isinstance(channel, discord.VoiceChannel):
				await channel.set_permissions(jail_role, overwrite=jail_deny_voice)
		return await msg.edit(embed=discord.Embed(color=self.good, description=f"{self.yes} {ctx.author.mention}: **successfully setup jail**"))

	@commands.command(name="skullleaderboard", description="shows top amount of skulls in the guild", aliases=["slb"])
	async def skullleaderboard(self, ctx):
		if ctx.guild.id == 1014050111367684146:
			i=0
			top=[]
			content=discord.Embed(title="Skull Leaderboard", color=self.color)
			rows=[]
			data=await self.bot.db.execute("""SELECT user_id, amount FROM skull ORDER BY amount DESC LIMIT 100""")
			for user_id, amount in data:
			#print(user_id,amount)
				if int(amount) > 0:
					user=self.bot.get_user(user_id)
					i+=1
					rows.append(f"`{i}:` **{user}** - `{amount}` **skulls**")
			await util.send_as_pages(ctx, content, rows)
		if ctx.guild.id == 962744326591484044:
			i=0
			top=[]
			content=discord.Embed(title="Skull Leaderboard", color=self.color)
			rows=[]
			data=await self.bot.db.execute("""SELECT user_id, amount FROM skull2 ORDER BY amount DESC LIMIT 10""")
			for user_id, amount in data:
			#print(user_id,amount)
				if int(amount) > 0:
					user=self.bot.get_user(user_id)
					i+=1
					rows.append(f"`{i}:` **{user}** - `{amount}` **skulls**")
			await util.send_as_pages(ctx, content, rows)

	@commands.command(name='skulls', description="shows your skull amount")
	async def skulls(self, ctx, member: discord.Member=None):
		if ctx.guild.id != 1014050111367684146:
			return
		if member == None:
			member=ctx.author
		if ctx.guild.id == 1014050111367684146:
			skulls=await self.bot.db.execute("""SELECT amount FROM skull WHERE user_id = %s""", member.id, one_value=True)
		if skulls == "()":
			skulls=0
		if not skulls:
			skulls=0
		if skulls == None:
			skulls=0
		await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{member.mention}**'s current balance is `{skulls}` skulls**"))

	@commands.command(name="clearskulls", description="clear a members skulls", brief="member")
	async def clearskulls(self, ctx, member:discord.Member):
		if ctx.guild.id != 839795057041211392:
			return
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id):
			return await util.send_failure(ctx, f"{ctx.author.mention}: **you must be trusted to use this command**")
		if ctx.guild.id == 839795057041211392:
			if await self.bot.db.execute("""SELECT * FROM skull WHERE user_id = %s""", member.id):
				await self.bot.db.execute("""DELETE FROM skull WHERE user_id = %s""", member.id)
				await util.send_success(ctx, f"{ctx.author.mention}: **cleared {member.mention}'s skulls**")
		if ctx.guild.id == 962744326591484044:
			if await self.bot.db.execute("""SELECT * FROM skull2 WHERE user_id = %s""", member.id):
				await self.bot.db.execute("""DELETE FROM skull2 WHERE user_id = %s""", member.id)
				await util.send_success(ctx, f"{ctx.author.mention}: **cleared {member.mention}'s skulls**")

	@commands.group(name='levelroles', aliases=['lvlroles', 'lvlaward', 'levelaward', 'levelrole', 'lvlrole'], description='level role reward group')
	async def levelroles(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@levelroles.command(name='add', aliases=['a','create','set'], description="add level based role rewards", extras={'perms':'manage_guild'}, usage="```Swift\nSyntax: !levelroles add <level> <role>\nExample: !levelroles add 5 level5users```", brief="level,role")
	@commands.has_permissions(manage_guild=True)
	async def levelroles_add(self, ctx, level:int, *, role:discord.Role):
		if await self.bot.db.execute("""SELECT * FROM levelroles WHERE role_id = %s AND level = %s AND guild_id = %s""", role.id, level, ctx.guild.id):
			await self.bot.db.execute("""DELETE FROM levelroles WHERE role_id = %s AND level = %s""", role.id, level)
		await self.bot.db.execute("""INSERT INTO levelroles (role_id, level, guild_id) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id) AND level = VALUES(level) AND guild_id = VALUES(guild_id)""", role.id, level, ctx.guild.id)
		await util.send_good(ctx, f"users level `{level}` will now receive {role.mention}")

	@levelroles.command(name='delete', aliases=['del', 'remove', 'rem'], description="delete level based role rewards", usage="```Swift\nSyntax: !levelroles remove <level> <role>\nExample: !levelroles remove 5 level5users```", brief='level,role', extras={'perms':'manage_guild'})
	@commands.has_permissions(manage_guild=True)
	async def levelroles_remove(self, ctx, level:int, *, role:discord.Role):
		if await self.bot.db.execute("""SELECT * FROM levelroles WHERE role_id = %s AND level = %s""", role.id, level):
			await self.bot.db.execute("""DELETE FROM levelroles WHERE role_id = %s and level = %s""", role.id, level)
			await util.send_good(ctx, f"users level `{level}` will no longer receive {role.mention}")
		else:
			await util.send_error(ctx, f"no reward found for level `{level}` with {role.mention}")

	@levelroles.command(name='list', description="show level based role rewards", extras={'perms':'manage_guild'})
	@commands.has_permissions(manage_guild=True)
	async def levelroles_list(self, ctx):
		data=await self.bot.db.execute("""SELECT role_id, level FROM levelroles WHERE guild_id = %s""", ctx.guild.id)
		rows=[]
		content=discord.Embed(title=f"{ctx.guild.name}'s level rewards", color=self.color)
		if data:
			for role_id, level in data:
				role=ctx.guild.get_role(role_id)
				rows.append(f"**level:** `{level}` - {role.mention}")
		if rows:
			await util.send_as_pages(ctx, content, rows)
		else:
			await util.send_error(ctx, f"no level rewards found")

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if len(before.roles) != len(after.roles):
			if before.guild.premium_subscriber_role not in before.roles:
				if after.guild.premium_subscriber_role in after.roles and await self.bot.db.execute("""SELECT channel_id from boostchannel WHERE guild_id = %s""", after.guild.id, one_value=True):
					boostchannel=await self.bot.db.execute("""SELECT channel_id from boostchannel WHERE guild_id = %s""", after.guild.id, one_value=True)
					msg=await self.bot.db.execute("""SELECT message from boost WHERE guild_id = %s""", after.guild.id, one_value=True)
					if not boostchannel:
						return
					if not msg:
						return
					channel=self.bot.get_channel(int(boostchannel))
					if not channel:
						return
					if channel:
						member=after
						if msg.startswith("{embed}"):
							boosters=after.guild.premium_subscribers
							if "{boosters}" in msg:
								msg=msg.replace('{boosters}', len(boosters))
							if "{guild.count.format}" in msg:
								msg = msg.replace("{guild.count.format}", str(len([m for m in after.guild.members])))
							if "{boosts}" in msg:
								msg=msg.replace('{boosts}', len(after.guild.premium_subscription_count))
							params=await util.embed_replacement(after,after.guild,msg)
							return await util.to_embed(channel,after,after.guild,params)
						else:
							if "\\n" in msg:
								msg=msg.replace('\\\\','\\')
							if "$(server)" in str(msg):
								msg = msg.replace("$(server)", member.guild.name)
							if "\\n" in msg:
								msg=msg.replace('\\\\','\\')
							if "$(server.count)" in msg:
								msg = msg.replace("$(server.count)", str(len([m for m in member.guild.members])))
							if "$(server.count.display)" in msg:
								ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
								msg = msg.replace("$(server.count.display)", ordinal(len(ctx.guild.members)))
							if "$(mention)" in msg:
								msg = msg.replace("$(mention)", member.mention)
							if "$(user.name)" in msg:
								msg = msg.replace("$(user.name)", member.name)
							if "$(user)" in msg:
								msg = msg.replace("$(user)", str(member))
							if "$(user.tag)" in msg:
								usertag=f"{member.name}#{member.discriminator}"
								msg = msg.replace("$(user.tag)", usertag)
							if "$(boosters)" in msg:
								boosters=ctx.guild.premium_subscribers
								msg=msg.replace("$(boosters)", boosters)
							if "$(boost.count)" in msg:
								msg=msg.replace("$(boost.count)", str(member.guild.premium_subscription_count))
							if "$(joindate)" in msg:
								msg = msg.replace("$(joindate)", discord.utils.format_dt(member.joined_at, style="R"))
							if "$(memberdate)" in msg:
								msg = msg.replace("$(memberdate)", discord.utils.format_dt(member.created_at, style="R"))
							if "$(boostdate)" in msg:
								msg = msg.replace("$(boostdate)", discord.utils.format_dt(member.premium_since, style="R"))
							if "$(guilddate)" in msg:
								msg = msg.replace("$(guilddate)", discord.utils.format_dt(member.guild.created_at, style="R"))
							if "$(now)" in msg:
								dt=datetime.datetime.now().timestamp()
								msg = msg.replace("$(now)", f"{dt}")
							if "$(user.avatar)" in msg:
								msg = msg.replace("$(user.avatar)", f"{member.display_avatar.url}")
							if "$(server.avatar)" in msg:
								if member.guild.icon.url:
									avatar=member.guild.icon.url
								else:
									avatar=None
								msg = msg.replace("$(server.avatar)", avatar)
							if msg.startswith("{"):
								embed_dict = self._get_embed_from_json(channel,msg)
								embedd=json.loads(msg)
								if not embedd.get("description") and not embedd.get("title") and embedd.get("content"):
									delete=embedd.get("autodelete", None)        
									await channel.send(delete_after=delete, content=embedd["content"])
								else:
									if isinstance(embed_dict,Exception):
										return await after.EmbedText(title="Something went wrong...", description=str(embed_dict)).send(channel)
									await Message.Embed(**embed_dict).send(channel)
							else:
								try:
									await channel.send(content=msg)
								except Exception as e:
									await channel.send(e)
				# boostchannel=await self.bot.db.execute("""SELECT channel_id from boostchannel WHERE guild_id = %s""", after.guild.id, one_value=True)
				# msg=await self.bot.db.execute("""SELECT message from boost WHERE guild_id = %s""", after.guild.id, one_value=True)
				# if not boostchannel:
				# 	return print("ya")
				# channel=self.bot.get_channel(int(boostchannel))
				# if not channel:
				# 	print(f"no channel in {after.guild}")
				# 	return
				# if channel:
				# 	member=after
				# 	if msg.startswith("{embed}"):
				# 		params=await util.embed_replacement(after,before.guild,msg)
				# 		return await util.to_embed(channel,after,after.guild,params)
				# 	else:
				# 		if "\\n" in msg:
				# 			msg=msg.replace('\\\\','\\')
				# 		if "$(server)" in str(msg):
				# 			msg = msg.replace("$(server)", member.guild.name)
				# 		if "\\n" in msg:
				# 			msg=msg.replace('\\\\','\\')
				# 		if "$(server.count)" in msg:
				# 			msg = msg.replace("$(server.count)", str(len([m for m in member.guild.members])))
				# 		if "$(server.count.display)" in msg:
				# 			ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
				# 			msg = msg.replace("$(server.count.display)", ordinal(len(ctx.guild.members)))
				# 		if "$(mention)" in msg:
				# 			msg = msg.replace("$(mention)", member.mention)
				# 		if "$(user.name)" in msg:
				# 			msg = msg.replace("$(user.name)", member.name)
				# 		if "$(user)" in msg:
				# 			msg = msg.replace("$(user)", str(member))
				# 		if "$(user.tag)" in msg:
				# 			usertag=f"{member.name}#{member.discriminator}"
				# 			msg = msg.replace("$(user.tag)", usertag)
				# 		if "$(boosters)" in msg:
				# 			boosters=ctx.guild.premium_subscribers
				# 			msg=msg.replace("$(boosters)", boosters)
				# 		if "$(boost.count)" in msg:
				# 			msg=msg.replace("$(boost.count)", str(member.guild.premium_subscription_count))
				# 		if "$(joindate)" in msg:
				# 			msg = msg.replace("$(joindate)", discord.utils.format_dt(member.joined_at, style="R"))
				# 		if "$(memberdate)" in msg:
				# 			msg = msg.replace("$(memberdate)", discord.utils.format_dt(member.created_at, style="R"))
				# 		if "$(boostdate)" in msg:
				# 			msg = msg.replace("$(boostdate)", discord.utils.format_dt(member.premium_since, style="R"))
				# 		if "$(guilddate)" in msg:
				# 			msg = msg.replace("$(guilddate)", discord.utils.format_dt(member.guild.created_at, style="R"))
				# 		if "$(now)" in msg:
				# 			dt=datetime.datetime.now().timestamp()
				# 			msg = msg.replace("$(now)", f"{dt}")
				# 		if "$(user.avatar)" in msg:
				# 			msg = msg.replace("$(user.avatar)", f"{member.display_avatar.url}")
				# 		if "$(server.avatar)" in msg:
				# 			if member.guild.icon.url:
				# 				avatar=member.guild.icon.url
				# 			else:
				# 				avatar=None
				# 			msg = msg.replace("$(server.avatar)", avatar)
				# 		if msg.startswith("{"):
				# 			embed_dict = self._get_embed_from_json(channel,msg)
				# 			embedd=json.loads(msg)
				# 			if not embedd.get("description") and not embedd.get("title") and embedd.get("content"):
				# 				delete=embedd.get("autodelete", None)        
				# 				await channel.send(delete_after=delete, content=embedd["content"])
				# 			else:
				# 				if isinstance(embed_dict,Exception):
				# 					return await after.EmbedText(title="Something went wrong...", description=str(embed_dict)).send(channel)
				# 				await after.Embed(**embed_dict).send(channel)
				# 		else:
				# 			try:
				# 				await channel.send(content=msg)
				# 			except Exception as e:
				# 				await channel.send(e)

	@commands.Cog.listener()
	async def on_message(self, message):
		if not self.bot.is_ready():
			return
		if message.author.bot:
			return
		self.bot.cache.last_seen.update({str(message.author.id):datetime.datetime.now()})
		if message.guild is None:
			return
		ctx=await self.bot.get_context(message)
		if message.channel.id in self.bot.cache.image_only and message.guild.me.guild_permissions.manage_messages:
			if not message.attachments and message.author.id != self.bot.user.id:
				try:
					return await message.delete()
				except:
					pass
		#if cc:
		if message.author.id in self.bot.cache.lastfm_cc:
			if ctx.valid:
				return
			cc=self.bot.cache.lastfm_cc[message.author.id]
			if message.content == str(cc):
				await ctx.invoke(self.bot.get_command('nowplaying'))
		if message.channel.id in self.bot.cache.antilink and message.guild.me.guild_permissions.manage_messages:
			try:
				if int(message.guild.id) in self.bot.cache.exempt:
					if message.author.guild_permissions.administrator:
						pass
					else:
						if message.guild.id in self.bot.cache.role_bypass:
							async for r in aiter(self.bot.cache.role_bypass[message.guild.id]):
								d=message.guild.get_role(int(r))
								if d in message.author.roles:
									return
							if await util.invite_find(message.content):
								try:
									return await message.delete()
								except:
									pass
							regex = r"((http(s)?(\:\/\/))+(www\.)?([\w\-\.\/])*(\.[a-zA-Z]{2,3}\/?))[^\s\b\n|]*[^.,;:\?\!\@\^\$ -]"
							results=re.findall(regex, message.content)
							if "discord.gg/" in message.content or "discord.com/invite" in message.content or "discordapp.com/" in message.content:
								try:
									return await message.delete()
								except:
									pass
							if results:
								try:
									return await message.delete()
								except:
									pass
			except:
				pass
		if str(message.guild.id) in self.bot.cache.chatfilter and message.guild.me.guild_permissions.manage_messages:
			for strr in self.bot.cache.chatfilter[str(message.guild.id)]:
				try:
					m=re.sub(r"[^a-zA-Z0-9]"," ",unidecode.unidecode(message.content.lower()))
					if str(strr).endswith("*") and str(strr).strip("*").lower() in m:
						if int(message.guild.id) in self.bot.cache.exempt:
							try:
								if not message.author.guild_permissions.administrator:
									try:
										return await message.delete()
									except Exception as e:
										print(e)
										pass
							except Exception as e:
								print(e)
								pass
						else:
							try:
								return await message.delete()
							except Exception as e:
								print(e)
								pass
				except Exception as e:
					print(e)
					pass
				ls=unidecode.unidecode(message.content.lower())
				if message.guild.me.guild_permissions.manage_messages:
					if f"{str(strr).lower()} " in ls or unidecode.unidecode(message.content.lower()) == str(strr).lower():
						if int(message.guild.id) in self.bot.cache.exempt:
							try:
								if not message.author.guild_permissions.administrator:
									try:
										await message.delete()
										return
									except:
										pass
							except AttributeError:
								pass
						else:
							try:
								await message.delete()
								return
							except:
								pass
					else:
						if int(message.guild.id) in self.bot.cache.exempt:
							try:
								if not message.author.guild_permissions.administrator:
									s=""
									async for l in aiter(ls):
										if l.isalnum():
											s+=l
										else:
											l=" "
											s+=l
									l=s.split(" ")
									if str(strr.lower()) in l:
										try:
											return await message.delete()
										except:
											pass
							except:
								pass
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
									try:
										return await message.delete()
									except:
										pass
							except:
								pass
							if str(strr.lower()) in message.content.lower():
								try:
									return await message.delete()
								except:
									pass
		if ctx.valid:
			return
		ratelimit = self.get_ratelimit(message)
		if ratelimit is None:
			#await asyncio.sleep(1)
			try:
				if message.guild.id in self.bot.cache.level_roles:
					if len(self.bot.cache.level_roles[message.guild.id]) >= 1:
						activity_data = await self.bot.db.execute(
							"""
							SELECT h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13,h14,h15,h16,h17,h18,h19,h20,h21,h22,h23
								FROM user_activity
							WHERE user_id = %s AND guild_id = %s
							""",
							message.author.id,
							message.guild.id,
							one_row=True,
						)
						xp = sum(activity_data) if activity_data else 0
						if xp > 0:
							for key,value in self.bot.cache.level_roles[message.guild.id].items():
								level=key
								role_id=value
								lvl = util.get_level(xp)
								role = message.guild.get_role(role_id)
								if lvl >= level:
									await message.author.add_roles(role, reason="Level Role")
			except:
				pass
			mention = f'<@!{self.bot.user.id}>'
			invlink=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=applications.commands%20bot"
			if message.content == mention:
				prefix=await self.bot.db.execute("""SELECT prefix FROM guild_prefixx WHERE guild_id = %s""", message.guild.id, one_value=True)
				if prefix:
					pre=prefix
				else:
					pre="!"
				embed=discord.Embed(description=f"**prefix =** `{pre}`", color=self.color)
				await asyncio.sleep(1)
				view = discord.ui.View()
				view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite', url=invlink))
				await message.channel.send(view=view, embed=embed)
			if message.content == self.bot.user.mention:
				prefix=await self.bot.db.execute("""SELECT prefix FROM guild_prefixx WHERE guild_id = %s""", message.guild.id, one_value=True)
				if prefix:
					pre=prefix
				else:
					pre="!"
				embed=discord.Embed(description=f"**prefix =** `{pre}`", color=self.color)
				await asyncio.sleep(1)
				view = discord.ui.View()
				view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite', url=invlink))
				await message.channel.send(view=view, embed=embed)
			word=message.content.lower().split()
			if not ctx.valid and str(message.guild.id) in self.bot.cache.autoresponses and message.guild.me.guild_permissions.manage_messages:
				for key, value in self.bot.cache.autoresponses[str(message.guild.id)].items():
					rk = self.get_ratelimit(message)
					if rk is not None:
						await asyncio.sleep(1)
					command_trigger=key.lower()
					content=value
					msg=str(command_trigger.lower())
					data=message.content.lower().split()
					if msg in data:
						if content.startswith("{embed}") or "{content:" in content:
							params=await util.embed_replacement(message.author,message.guild,content)
							await util.to_embed(message.channel,message.author,message.guild,params)
						elif content.startswith("{"):
							if "$(ctx.author.mention)" in content:
								content=content.replace("$(ctx.author.mention)", message.author.mention)
							if "$(" in content:
								try:
									jd=[]
									kd=[]
									jd=content.split("$")
									for jd in jd:
										result = jd[jd.find('(')+1:jd.find(')')]
										kd.append(result)
									kd.pop(0)
									for kd in kd:
										content=content.replace(f"$({kd})", f"{eval(kd)}")
								except:
									pass
							if "\\n" in content:
								content=content.replace('\\\\','\\')
							embed_dict = self._get_embed_from_json(ctx, content)
							await Message.Embed(**embed_dict).send(ctx)
						else:
							if "$(" in content:
								try:
									jd=[]
									kd=[]
									jd=content.split("$")
									for jd in jd:
										result = jd[jd.find('(')+1:jd.find(')')]
										kd.append(result)
									kd.pop(0)
									for kd in kd:
										content=content.replace(f"$({kd})", f"{eval(kd)}")
								except:
									pass
							await message.channel.send(content=content, allowed_mentions=discord.AllowedMentions.all())
			#trigga=await self.bot.db.execute("SELECT trig, content FROM react WHERE guild_id = %s",message.guild.id)
			if str(message.guild.id) in self.bot.cache.autoreacts:
				for key, value in self.bot.cache.autoreacts[str(message.guild.id)].items():
					rk = self.get_ratelimit(message)
					if rk is not None:
						await asyncio.sleep(1)
					trig=key.lower()
					content=value
					trig=str(trig).lower()
					data=message.content.lower().split()
					if data:
						if trig in data:
							if "," in content:
								content=content.split(",")
								async for content in aiter(content):
									if content.startswith("<"): 
										try:
											await ctx.message.add_reaction(content)
										except:
											pass
									else:
										try:
											await ctx.message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(content))
										except:
											pass
							elif " , " in content:
								content=content.split(",")
								async for content in aiter(content):
									if content.startswith("<"): 
										try:
											await ctx.message.add_reaction(content)
										except:
											pass
									else:
										try:
											await ctx.message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(content))
										except:
											pass
							else:
								if content.startswith("<"): 
									try:
										await ctx.message.add_reaction(content)
									except:
										pass
								else:
									try:
										await ctx.message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(content))
									except:
										pass
		else:
			if str(message.guild.id) in self.bot.cache.autoreacts:
				rk = self.get_ratelimit(message)
				if rk is not None:
					await asyncio.sleep(1)
				for trig, content in self.bot.cache.autoreacts[str(message.guild.id)].items():
					trig=str(trig).lower()
					data=message.content.lower().split()
					#for data in data:
					if data:
						if trig in data:
							if "," in content:
								content=content.split(",")
								async for content in aiter(content):
									if content.startswith("<"): 
										try:
											await ctx.message.add_reaction(content)
										except:
											pass
									else:
										try:
											await ctx.message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(content))
										except:
											pass
							elif " , " in content:
								content=content.split(",")
								async for content in aiter(content):
									if content.startswith("<"): 
										try:
											await ctx.message.add_reaction(content)
										except:
											pass
									else:
										try:
											await ctx.message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(content))
										except:
											pass
							else:
								if content.startswith("<"): 
									try:
										await ctx.message.add_reaction(content)
									except:
										pass
								else:
									try:
										await ctx.message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(content))
									except:
										pass

	@commands.group(name='boost', description="set a boost message", extras={'perms': 'administrator'})
	@commands.has_permissions(administrator=True)
	async def boost(self, ctx):
		if ctx.invoked_subcommand is None:
			embed=discord.Embed(color=self.bot.color, description=f"""**Valid SubCommands:**\n`message`, `channel`, `config`, `test`, `help`\nFor Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)""")
			await ctx.reply(embed=embed)

	@boost.command(name='help')
	@commands.has_permissions(administrator=True)
	async def help(self, ctx):
		embed=discord.Embed(color=self.bot.color, description=f"""**Valid SubCommands:**\n`message`, `channel`, `config`, `test`, `help`\nFor Embed Creation use [This Embed Creator](https://rival.rocks/embedbuilder/) with [These Variables](https://docs.rival.rocks)""")
		await ctx.reply(embed=embed)

	@boost.command(name='message', description="set boost message", extras={'perms': 'administrator'}, brief='message')
	@commands.has_permissions(administrator=True)
	async def aamessage(self, ctx, *, message=None):
		args=message
		if message:
			if await self.bot.db.execute("""SELECT message FROM boost WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM boost WHERE guild_id = %s""", ctx.guild.id)
			if "\\n" in args:
				args=args.replace('\\\\','\\')
			await self.bot.db.execute("""INSERT INTO boost (guild_id, message) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message)""", ctx.guild.id, args)
			await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set boost message to `{args}`", color=self.good))
		else:
			if await self.bot.db.execute("""SELECT message FROM boost WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM boost WHERE guild_id = %s""", ctx.guild.id)
				await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **boost message cleared**", color=self.good))
			else:
				await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a message**", color=self.error))

	@boost.command(name='channel', description="set boost message channel", extras={'perms': 'administrator'}, brief='channel')
	@commands.has_permissions(administrator=True)
	async def aachannel(self, ctx, textchannel:discord.TextChannel=None):
		if textchannel:
			if await self.bot.db.execute("""SELECT channel_id FROM boostchannel WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM boostchannel WHERE guild_id = %s""", ctx.guild.id)
			await self.bot.db.execute("""INSERT INTO boostchannel (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)""", ctx.guild.id, textchannel.id)
			await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set boost channel to {textchannel.mention}", color=self.good))
		else:
			if await self.bot.db.execute("""SELECT channel_id FROM boostchannel WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM boostchannel WHERE guild_id = %s""", ctx.guild.id)
				await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **boost channel cleared**", color=self.good))
			else:
				await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a channel**", color=self.error))

	@boost.command(name='settings', aliases=['config'], description="check boost message settings", extras={'perms': 'administrator'})
	@commands.has_permissions(administrator=True)
	async def settings(self, ctx):
		data=await self.bot.db.execute("""SELECT * FROM boost WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		boostchannel=await self.bot.db.execute("""SELECT channel_id FROM boostchannel WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		channel=self.bot.get_channel(boostchannel)
		msg=await self.bot.db.execute("""SELECT message FROM boost WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if data:
			if channel:
				c=channel.mention
			else:
				c="None"
			embed=discord.Embed(title=f"{ctx.guild.name}'s boost message config", color=self.bot.color)
			embed.add_field(name='Message', value=f"`{msg}`", inline=True)
			embed.add_field(name='Channel', value=c, inline=True)
			await ctx.send(embed=embed)

	@boost.command(name='test', description="test boost message", extras={'perms': 'administrator'})
	@commands.has_permissions(administrator=True)
	async def test(self, ctx):
		member=ctx.author
		data=await self.bot.db.execute("""SELECT * FROM boost WHERE guild_id = %s""", member.guild.id, one_value=True)
		if not data:
			return await util.send_error(ctx, f"no message setup for boost messages")
		boostchannel=await self.bot.db.execute("""SELECT channel_id FROM boostchannel WHERE guild_id = %s""", member.guild.id, one_value=True)
		channel=self.bot.get_channel(boostchannel)
		if not channel:
			return await util.send_error(ctx, f"no channel set for boost messages")
		msg=await self.bot.db.execute("""SELECT message FROM boost WHERE guild_id = %s""", member.guild.id, one_value=True)
		if msg.startswith("{embed}"):
			params=await util.embed_replacement(ctx.author,ctx.guild,msg)
			return await util.to_embed(channel,ctx.author,ctx.guild,params)
		if "\\n" in msg:
			msg=msg.replace('\\\\','\\')
		if "$(server)" in str(msg):
			msg = msg.replace("$(server)", member.guild.name)
		if "$(server.count)" in msg:
			msg = msg.replace("$(server.count)", str(len([m for m in member.guild.members])))
		if "$(mention)" in msg:
			msg = msg.replace("$(mention)", member.mention)
		if "$(user.name)" in msg:
			msg = msg.replace("$(user.name)", member.name)
		if "$(user)" in msg:
			msg = msg.replace("$(user)", str(member))
		if "$(boosters)" in msg:
			boosters=ctx.guild.premium_subscribers
			msg=msg.replace("$(boosters)", boosters)
		if "$(boost.count)" in msg:
			msg=msg.replace("$(boost.count)", str(member.guild.premium_subscription_count))
		if "$(user.tag)" in msg:
			usertag=f"{member.name}#{member.discriminator}"
			msg = msg.replace("$(user.tag)", usertag)
		if "$(server.avatar)" in msg:
			if member.guild.icon.url:
				avatar=member.guild.icon.url
			else:
				avatar=None
			msg = msg.replace("$(server.avatar)", avatar)
		if "$(user.avatar)" in msg:
			msg = msg.replace("$(user.avatar)", f"{member.display_avatar.url}")
		if msg.startswith("{"):
			embed_dict = self._get_embed_from_json(channel,msg)
			if isinstance(embed_dict,Exception):
				return await Message.EmbedText(title="Something went wrong...", description=str(embed_dict)).send(channel)
			await Message.Embed(**embed_dict).send(channel)
		else:
			await channel.send(content=msg)

	@commands.hybrid_command(name='afk', with_app_command=True, description="set afk status for when afk", brief="status")
	async def afk(self, ctx, *, reason:str=None):
		"""Syntax: !afk <reason>
		Example: !afk sleep
		"""
		if reason == None:
			reason="AFK"
		if not reason:
			reason="AFK"
		if ctx.author.id in self.bot.cache.afk:
			reason=self.bot.cache.afk[ctx.author.id]['reason']
			ts=self.bot.cache.afk[ctx.author.id]['ts']
			ago=humanize.naturaltime(ts)
			embed=discord.Embed(color=self.color, description=f"> welcome back <@!{ctx.author.id}>, you were last seen **{ago}**")
			embed.set_author(icon_url=ctx.author.display_avatar, name=f"{ctx.author.name}#{ctx.author.discriminator} is no longer afk")
			await self.bot.db.execute("""DELETE FROM afks WHERE user_id = %s""", ctx.author.id)
			self.bot.cache.afk.pop(ctx.author.id)
			try:
				await ctx.reply(embed=embed)
				return
			except:
				await ctx.send(embed=embed)
				return
		else:
			if "discord.gg" in reason:
				reason="AFK"
			await self.bot.db.execute(
				"""
				INSERT INTO afks VALUES (%s, %s, %s)
				ON DUPLICATE KEY UPDATE
					reason = VALUES(reason)
				""",
				ctx.author.id,
				reason,
				datetime.datetime.now(),
			)
			self.bot.cache.afk[ctx.author.id]={'reason':reason,'ts':datetime.datetime.now()}
			embed=discord.Embed(color=self.color, description=f"> {reason}")
			embed.set_author(icon_url=ctx.author.display_avatar, name=f"{ctx.author.name}#{ctx.author.discriminator} is now afk with the status..")
			await ctx.send(embed=embed)

	@commands.hybrid_command(name='selfprefix', with_app_command=True, description='set a custom user prefix for most commands', brief='prefix')
	@commands.guild_only()
	async def selfprefix(self, ctx, prefix):
		"""Syntax: !selfprefix <prefix>
		Example: !selfprefix ?
		"""
		if len(prefix) > 32:
			raise exceptions.Warning("Prefix cannot be more than 32 characters")
		if prefix.strip() == "":
			raise exceptions.Warning("Prefix cannot be empty.")

		if prefix.startswith(" "):
			raise exceptions.Warning("Prefix cannot start with a space.")

		prefix = prefix.lstrip()
		await self.bot.db.execute(
			"""
			INSERT INTO guild_prefix (user_id, prefix)
				VALUES (%s, %s)
			ON DUPLICATE KEY UPDATE
				prefix = VALUES(prefix)
			""",
			ctx.author.id,
			prefix,
		)
		self.bot.cache.prefixes[str(ctx.author.id)] = prefix
		await util.send_success(
			ctx,
			f"{ctx.author.mention} your prefix is now `{prefix}`"
		)

	@commands.hybrid_command(name='prefix', aliases=['setprefix'], with_app_command=True, description='set a custom guild prefix for most commands', brief='prefix', extras={'perms': 'manage guild'}, usage="```Swift\nSyntax: !prefix <prefix>\nExample: !prefix ,```")
	@commands.has_permissions(manage_guild=True)
	@commands.guild_only()
	async def prefix(self, ctx, prefix=None):
		"""Syntax: !prefix <prefix>
		Example: !prefix ?
		"""
		if not prefix:
			return await ctx.reply(embed=discord.Embed(color=self.color, description=f"**current prefix is `{await util.get_prefix(ctx)}`**"))
		if len(prefix) > 32:
			raise exceptions.Warning("Prefix cannot be more than 32 character")
		if prefix.strip() == "":
			raise exceptions.Warning("Prefix cannot be empty.")

		if prefix.startswith(" "):
			raise exceptions.Warning("Prefix cannot start with a space.")

		prefix = prefix.lstrip()
		await self.bot.db.execute(
			"""
			INSERT INTO guild_prefixx (guild_id, prefix)
				VALUES (%s, %s)
			ON DUPLICATE KEY UPDATE
				prefix = VALUES(prefix)
			""",
			ctx.guild.id,
			prefix,
		)
		self.bot.cache.prefixess[str(ctx.guild.id)] = prefix
		await util.send_success(
			ctx,
			f"{ctx.author.mention}: **the guild prefix is now `{prefix}`**"
		)

	@commands.group(name='chatfilter', aliases=["cf", "filter"], description="filter keywords from chat")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	async def chatfilter(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@chatfilter.command(name='add', aliases=['a', 'c', 'create'], description="Add a new Chat Filter", brief="keyword", extras={'perms': 'manage guild'}, usage="```Swift\nSyntax: !filter add <word>\nExample: !filter add fuck```")
	@commands.has_permissions(manage_guild=True)
	async def aaadd(self, ctx, *, name):
		if await self.bot.db.execute(
			"SELECT * FROM chatfilter WHERE guild_id = %s AND strr = %s",
			ctx.guild.id,
			name,
			one_value=True,
		):
			raise exceptions.Warning(
				f"Filter `{name}` already exists on this server!"
			)

		await self.bot.db.execute(
			"INSERT INTO chatfilter VALUES(%s, %s)",
			ctx.guild.id,
			name,
		)
		if str(ctx.guild.id) not in self.bot.cache.chatfilter:
			self.bot.cache.chatfilter[str(ctx.guild.id)]=[]
		self.bot.cache.chatfilter[str(ctx.guild.id)].append(name)
		await util.send_success(
			ctx, f"Filter `{name}` added"
		)

	@chatfilter.command(name='remove', aliases=['rem', 'del', 'delete', 'd', 'r'], description="Remove an Chat Filter", brief="word", usage="```Swift\nSyntax: !filter remove <word>\nExample: !filter remove discord```",extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def aaremove(self, ctx, *, name):
		"""Syntax: !filter remove <word>
		Example: !filter remove fuck"""
		await self.bot.db.execute(
			"DELETE FROM chatfilter WHERE guild_id = %s AND strr = %s",
			ctx.guild.id,
			name,
		)
		try:
			self.bot.cache.chatfilter[str(ctx.guild.id)].remove(name)
		except:
			pass
		await util.send_success(ctx, f"Filter `{name}` has been deleted")

	@chatfilter.command(name='list', aliases=['config'], description="list all filtered words")
	@commands.has_permissions(manage_guild=True)
	async def dlist(self, ctx):
		rows = []
		guild=ctx.guild
		for strr in await self.filter_llist(guild.id):
			rows.append(f"{strr}")

		if rows:
			content = discord.Embed(title=f"{guild.name} Filters", color=self.color)
			await util.send_as_pages(ctx, content, rows)
		else:
			raise exceptions.Info("No Filters")

	@chatfilter.command(name='exempt', description='set if admins are exempt or not', brief='state', usage="```Swift\nSyntax: !filter exempt <state>\nExample: !filter exempt true```",extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def exempt(self, ctx, state:bool=None):
		if not state:
			if await self.bot.db.execute("SELECT state FROM exempt WHERE guild_id = %s", ctx.guild.id, one_value=True):
				await self.bot.db.execute("DELETE FROM exempt WHERE guild_id = %s",ctx.guild.id,)
				try:
					self.bot.cache.exempt.remove(ctx.guild.id)
				except:
					pass
		if state:
			if await self.bot.db.execute("SELECT state FROM exempt WHERE guild_id = %s", ctx.guild.id, one_value=True):
				await self.bot.db.execute("DELETE FROM exempt WHERE guild_id = %s",ctx.guild.id,)
				try:
					self.bot.cache.exempt.remove(ctx.guild.id)
				except:
					pass
			value="1"
			await self.bot.db.execute("INSERT INTO exempt VALUES(%s, %s)",ctx.guild.id, value)
			self.bot.cache.exempt.append(ctx.guild.id)
			await util.send_success(ctx, f"exempt set to {state}")
		else:
			await self.bot.db.execute("DELETE FROM exempt WHERE guild_id = %s",ctx.guild.id,)
			try:
				self.bot.cache.exempt.remove(ctx.guild.id)
			except:
				pass
			await util.send_failure(ctx, f"exempt set to {state}")


	@commands.group(name='autoresponder', aliases=["autorespond", "autoresponders", "ar", "autoresponse"], description="responds based off message content with a set message")
	@commands.has_permissions(manage_guild=True)
	@commands.guild_only()
	async def autoresponder(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@autoresponder.command(name='add', aliases=['a', 'c', 'create'], description="add a new auto response", brief='trigger, response', usage="```Swift\nSyntax: !ar add <trigger> <response>\nExample: !ar add rival best bot```",extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def aadd(self, ctx, name, *, response):
		if await self.bot.db.execute(
			"SELECT content FROM custom_command WHERE guild_id = %s AND command_trigger = %s",
			ctx.guild.id,
			name,
			one_value=True,
		):
			raise exceptions.Warning(
				f"AutoResponse `{name}` already exists on this server!"
			)

		await self.bot.db.execute(
			"INSERT INTO custom_command VALUES(%s, %s, %s, %s, %s)",
			ctx.guild.id,
			name,
			response,
			arrow.utcnow().datetime,
			ctx.author.id,
		)
		if str(ctx.guild.id) not in self.bot.cache.autoresponses:
			self.bot.cache.autoresponses[str(ctx.guild.id)]={}
		self.bot.cache.autoresponses[str(ctx.guild.id)].update({f'{name}':f'{response}'})
		await util.send_success(
			ctx, f"AutoResponse `{name}` added with the response \n```{response}```"
		)

	@autoresponder.command(name='remove', aliases=['rem', 'del', 'delete', 'd', 'r'], description="Remove an AR", brief='trigger', usage="```Swift\nSyntax: !ar remove <trigger>\nExample: !ar remove rival```",extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def aremove(self, ctx, *, name):
		owner_id = await self.bot.db.execute(
			"SELECT added_by FROM custom_command WHERE command_trigger = %s AND guild_id = %s",
			name,
			ctx.guild.id,
			one_value=True,
		)
		if not owner_id:
			raise exceptions.Warning(f"AutoResponse `{name}` does not exist")

		owner = ctx.guild.get_member(owner_id)
		if not ctx.author.guild_permissions.manage_guild:
			raise exceptions.Warning(
				f"`{name}` can only be removed by **{owner}** unless you have `manage_guild` permission."
			)

		await self.bot.db.execute(
			"DELETE FROM custom_command WHERE guild_id = %s AND command_trigger = %s",
			ctx.guild.id,
			name,
		)
		try:
			self.bot.cache.autoresponses[str(ctx.guild.id)].pop(name)
		except:
			pass
		await util.send_success(ctx, f"AutoResponse `{name}` has been deleted")

	@autoresponder.command(name='edit', description="edit an existing AR", brief="name, response", usage="```Swift\nSyntax: !ar edit <trigger> <response>\nExample: !ar edit rival good bot```",extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def edit(self, ctx, name, *, response):
		owner_id = await self.bot.db.execute(
			"SELECT added_by FROM custom_command WHERE command_trigger = %s AND guild_id = %s",
			name,
			ctx.guild.id,
			one_value=True,
		)
		if not owner_id:
			raise exceptions.Warning(f"AutoResponse `{name}` does not exist")

		owner = ctx.guild.get_member(owner_id)

		await self.bot.db.execute(
			"DELETE FROM custom_command WHERE guild_id = %s AND command_trigger = %s",
			ctx.guild.id,
			name,
		)
		await self.bot.db.execute(
			"INSERT INTO custom_command VALUES(%s, %s, %s, %s, %s)",
			ctx.guild.id,
			name,
			response,
			arrow.utcnow().datetime,
			ctx.author.id,
		)
		try:
			self.bot.cache.autoresponses[str(ctx.guild.id)].update({f'{name}':f'{response}'})
		except:
			pass
		await util.send_success(ctx, f"AutoResponse `{name}` has been changed to respond with {response}")


	@autoresponder.command(name='list', description="List all ars on this server", extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def ar_list(self, ctx):
		rows = []
		guild=ctx.guild.id
		for command in await self.custom_command_list(ctx.guild.id):
			rows.append(f"{command}")

		if rows:
			content = discord.Embed(title=f"{ctx.guild.name} auto responses", color=self.color)
			await util.send_as_pages(ctx, content, rows)
		else:
			raise exceptions.Info("No AutoResponses")

	@autoresponder.command(name="clear", description='Delete all the ars on this server', extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def command_clear(self, ctx):
		count = (
			await self.bot.db.execute(
				"SELECT COUNT(*) FROM custom_command WHERE guild_id = %s",
				ctx.guild.id,
				one_value=True,
			)
			or 0
		)
		if count < 1:
			raise exceptions.Warning("This server has no autoresponses yet!")

		content = discord.Embed(title=f"{self.bot.warn} Are you sure?", color=self.bot.color)
		content.description = f"This action will delete all **{count}** autoresponses on this server and is **irreversible**."
		msg = await ctx.send(embed=content)

		async def confirm():
			await self.bot.db.execute(
				"DELETE FROM custom_command WHERE guild_id = %s",
				ctx.guild.id,
			)
			content.title = f"{self.bot.yes} Cleared autoresponses in {ctx.guild}"
			self.bot.cache.autoresponses[str(ctx.guild.id)].clear()
			content.description = ""
			content.color = self.bot.color
			await msg.edit(embed=content)

		async def cancel():
			content.title = f"{self.bot.no} Action cancelled"
			content.description = ""
			content.color = self.bot.color
			await msg.edit(embed=content)

		functions = {"✅": confirm, "❌": cancel}
		asyncio.ensure_future(
			util.reaction_buttons(ctx, msg, functions, only_author=True, single_use=True)
		)

	@commands.group(name='react', aliases=['reaction'], description="auto react command group")
	@commands.has_permissions(manage_guild=True)
	async def react(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@react.command(name='add', aliases=['create','a','c'],description='Add a new auto reaction', brief='trigger, emojis', usage="```Swift\nSyntax: !react add <trigger> <emojis>\nExample: !react add yesno <:yes:940723483204255794><:no:940723951947120650>```",extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def react_add(self, ctx, name, emoji: commands.Greedy[typing.Union[discord.Emoji,str]]):
		try:
			data=await self.bot.db.execute("""SELECT * FROM react WHERE trig = %s AND guild_id = %s""", name, ctx.guild.id)
			if data:
				raise exceptions.Warning(f"AutoReaction `{name}` already exists on this server!")
			if len(emoji)>4:
				return await util.send_error(ctx, "auto reaction emoji limit set to `4`")
			emo=[]
			for e in emoji:
				if str(e).startswith("<"):
					emo.append(str(e))
				else:
					emo.append(emoji_literals.UNICODE_TO_NAME.get(e))
			emojis=",".join(str(emoji) for emoji in emo)
			for e in emo:
				if e.startswith("<"): 
					await ctx.message.add_reaction(e)
				else:
					await ctx.message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(e))
			await self.bot.db.execute(
				"""
				INSERT INTO react (guild_id, trig, content)
					VALUES (%s, %s, %s)
				ON DUPLICATE KEY UPDATE
					content = VALUES(content)
				""",
				ctx.guild.id,
				name,
				emojis,
			)
			if str(ctx.guild.id) not in self.bot.cache.autoreacts:
				self.bot.cache.autoreacts[str(ctx.guild.id)]={}
			if not self.bot.cache.autoreacts[str(ctx.guild.id)].get(name):
				self.bot.cache.autoreacts[str(ctx.guild.id)].update({f'{name}':f'{emojis}'})
			else:
				self.bot.cache.autoreacts[str(ctx.guild.id)].pop(name)
				self.bot.cache.autoreacts[str(ctx.guild.id)].update({f'{name}':f'{emojis}'})
			return await util.send_success(ctx, f"Auto Reaction for {name} set to {emojis}")
		except Exception as e:
			print(e)
			return await util.send_error(ctx, f"add a space inbetween the emojis")

	@react.command(name='remove', aliases=['delete','del','d','rem','r'],description="remove an auto react", usage="```Swift\nSyntax: !react remove <trigger>\nExample: !react remove rival```",extras={'perms': 'manage guild'}, brief='trigger')
	@commands.has_permissions(manage_guild=True)
	async def react_remove(self, ctx, *, name):
		owner_id = await self.bot.db.execute(
			"SELECT * FROM react WHERE trig = %s AND guild_id = %s",
			name,
			ctx.guild.id,
		)
		if not owner_id:
			raise exceptions.Warning(f"Auto Reaction `{name}` does not exist")
		await self.bot.db.execute(
			"DELETE FROM react WHERE guild_id = %s AND trig = %s",
			ctx.guild.id,
			name,
		)
		try:
			self.bot.cache.autoreacts[str(ctx.guild.id)].pop(name)
		except:
			pass
		await util.send_success(ctx, f"Auto Reaction `{name}` has been deleted")

	@react.command(name='clear', description='clear all reacts', usage='```Swift\nSyntax: !react clear\nExample: !react clear```', extras={'perms':'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def react_clear(self, ctx):
		count = (
			await self.bot.db.execute(
				"SELECT COUNT(*) FROM react WHERE guild_id = %s",
				ctx.guild.id,
				one_value=True,
			)
			or 0
		)
		if count < 1:
			raise exceptions.Warning("This server has no autoresponses yet!")

		content = discord.Embed(title=f"{self.bot.warn} Are you sure?", color=self.bot.color)
		content.description = f"This action will delete all **{count}** auto reactions on this server and is **irreversible**."
		msg = await ctx.send(embed=content)

		async def confirm():
			await self.bot.db.execute(
				"DELETE FROM react WHERE guild_id = %s",
				ctx.guild.id,
			)
			content.title = f"{self.bot.yes} Cleared AutoReactions in {ctx.guild}"
			content.description = ""
			content.color = self.bot.color
			try:
				self.bot.cache.autoreacts[str(ctx.guild.id)].clear()
			except:
				pass
			await msg.edit(embed=content)

		async def cancel():
			content.title = f"{self.bot.no} Action cancelled"
			content.description = ""
			content.color = self.bot.color
			await msg.edit(embed=content)

		functions = {"✅": confirm, "❌": cancel}
		asyncio.ensure_future(
			util.reaction_buttons(ctx, msg, functions, only_author=True, single_use=True)
		)

	@react.command(name='edit', description='edit an auto react', extras={'perms': 'manage guild'}, usage="```Swift\nSyntax: !react edit <trigger> <emojis>\nExample: !react edit rival emoji1,emoji2```",brief='trigger, emojis')
	@commands.has_permissions(manage_guild=True)
	async def react_edit(self, ctx, name, *, emoji: commands.Greedy[typing.Union[discord.Emoji,str]]):
		try:	
			if len(emoji)>=4:
				return await util.send_error(ctx, "auto reaction emoji limit set to `4`")
		except:
			pass
		owner_id = await self.bot.db.execute(
			"SELECT * FROM react WHERE trig = %s AND guild_id = %s",
			name,
			ctx.guild.id,
		)
		if not owner_id:
			raise exceptions.Warning(f"Auto Reaction `{name}` does not exist")

		await self.bot.db.execute(
			"DELETE FROM react WHERE guild_id = %s AND trig = %s",
			ctx.guild.id,
			name,
		)
		emo=[]
		for e in emoji:
			if str(e).startswith("<"):
				emo.append(str(e))
			else:
				emo.append(emoji_literals.UNICODE_TO_NAME.get(e))
		emojis=",".join(str(emoji) for emoji in emo)
		await self.bot.db.execute(
			"""
			INSERT INTO react (guild_id, trig, content)
				VALUES (%s, %s, %s)
			ON DUPLICATE KEY UPDATE
				content = VALUES(content)
			""",
			ctx.guild.id,
			name,
			emojis,
		)
		self.bot.cache.autoreacts[str(ctx.guild.id)].update({f'{name}':f'{emojis}'})
		await util.send_success(ctx, f"Auto Reaction `{name}` has been changed to react with {emojis}")

	@react.command(name='list', description="List all Auto Reactions on this server", extras={'perms': 'manage guild'})
	@commands.has_permissions(manage_guild=True)
	async def re_list(self, ctx):
		rows = []
		for command in await self.react_command_list(ctx.guild.id):
			rows.append(f"{command}")

		if rows:
			content = discord.Embed(title=f"{ctx.guild.name} auto reactions", color=self.color)
			await util.send_as_pages(ctx, content, rows)
		else:
			raise exceptions.Info("No Auto Reactions have been added on this server yet")

	@commands.group(description='configure the starboard')
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	async def starboard(self, ctx):
		"""Configure the starboard."""
		if ctx.invoked_subcommand == None:
			await util.command_group_help(ctx)

	@starboard.command(name="channel", description='set the starboard channel', extras={'perms': 'manage channels'}, brief='channel',usage="```Swift\nSyntax: !starboard channel <channel>\nExample: !starboard channel #msg```")
	async def starboard_channel(self, ctx, channel: discord.TextChannel):
		await queries.update_setting(ctx, "starboard_settings", "channel_id", channel.id)
		await util.send_success(ctx, f"Starboard channel is now {channel.mention}")
		await self.bot.cache.cache_starboard_settings()

	@starboard.command(name="amount", description="Change the amount of reactions required to starboard a message", brief='amount', usage="```Swift\nSyntax: !starboard amount <int>\nExample: !starboard amount 1```",extras={'perms': 'manage channels'})
	async def starboard_amount(self, ctx, amount: int):
		await queries.update_setting(ctx, "starboard_settings", "reaction_count", amount)
		emoji_name, emoji_id, emoji_type = await self.bot.db.execute(
			"""
			SELECT emoji_name, emoji_id, emoji_type
			FROM starboard_settings WHERE guild_id = %s
			""",
			ctx.guild.id,
			one_row=True,
		)
		if emoji_type == "custom":
			emoji = self.bot.get_emoji(emoji_id)
		else:
			emoji = emoji_name

		await util.send_success(
			ctx, f"Messages now need **{amount}** {emoji} reactions to get into the starboard."
		)
		await self.bot.cache.cache_starboard_settings()

	@starboard.command(name="toggle", aliases=["enabled"], description="Enable or disable the starboard", extras={'perms': 'manage channels'}, usage="```Swift\nSyntax: !starboard toggle <bool>\nExample: !starboard toggle true```",brief='state:bool')
	async def starboard_toggle(self, ctx, value: bool):
		await queries.update_setting(ctx, "starboard_settings", "is_enabled", value)
		if value:
			await util.send_success(ctx, "Starboard is now **enabled**")
		else:
			await util.send_success(ctx, "Starboard is now **disabled**")
		await self.bot.cache.cache_starboard_settings()

	@starboard.command(name="emoji", description='sets the starboard reaction emoji', extras={'perms': 'manage channels'}, usage="```Swift\nSyntax: !starboard emoji <emoji>\nExample: !starboard emoji <:no:940723951947120650>```",brief='emoji')
	async def starboard_emoji(self, ctx, emoji):
		if emoji[0] == "<":
			# is custom emoji
			emoji_obj = await util.get_emoji(ctx, emoji)
			if emoji_obj is None:
				raise exceptions.Warning("I don't know this emoji!")

			await self.bot.db.execute(
				"""
				INSERT INTO starboard_settings (guild_id, emoji_name, emoji_id, emoji_type)
					VALUES (%s, %s, %s, %s)
				ON DUPLICATE KEY UPDATE
					emoji_name = VALUES(emoji_name),
					emoji_id = VALUES(emoji_id),
					emoji_type = VALUES(emoji_type)
				""",
				ctx.guild.id,
				emoji_obj.name,
				emoji_obj.id,
				"custom",
			)
			await util.send_success(
				ctx, f"Starboard emoji is now {emoji} (emoji id `{emoji_obj.id}`)"
			)
		else:
			# unicode emoji
			emoji_name = emoji_literals.UNICODE_TO_NAME.get(emoji)
			if emoji_name is None:
				raise exceptions.Warning("I don't know this emoji!")

			await self.bot.db.execute(
				"""
				INSERT INTO starboard_settings (guild_id, emoji_name, emoji_id, emoji_type)
					VALUES (%s, %s, %s, %s)
				ON DUPLICATE KEY UPDATE
					emoji_name = VALUES(emoji_name),
					emoji_id = VALUES(emoji_id),
					emoji_type = VALUES(emoji_type)
				""",
				ctx.guild.id,
				emoji_name,
				None,
				"unicode",
			)
			await util.send_success(ctx, f"Starboard emoji is now {emoji}")
		await self.bot.cache.cache_starboard_settings()

	@starboard.command(name="log", description="Set starboard logging channel to log starring events", brief='channel', usage="```Swift\nSyntax: !starboard log <channel>\nExample: !starboard log #msg```",extras={'perms': 'manage channels'})
	async def starboard_log(self, ctx, channel: ChannelSetting):
		if channel is None:
			await queries.update_setting(ctx, "starboard_settings", "log_channel_id", None)
			await util.send_success(ctx, "Starboard log is now disabled")
		else:
			await queries.update_setting(ctx, "starboard_settings", "log_channel_id", channel.id)
			await util.send_success(ctx, f"Starboard log channel is now {channel.mention}")
		await self.bot.cache.cache_starboard_settings()

	@starboard.command(name="blacklist", description="Blacklist a channel from being counted for starboard", brief='channel',usage="```Swift\nSyntax: !starboard blacklist <channel>\nExample: !starboard blacklist #msg```", extras={'perms': 'manage channels'})
	async def starboard_blacklist(self, ctx, channel: discord.TextChannel):
		await self.bot.db.execute(
			"""
			INSERT INTO starboard_blacklist (guild_id, channel_id)
				VALUES (%s, %s)
			ON DUPLICATE KEY UPDATE
				channel_id = channel_id
			""",
			ctx.guild.id,
			channel.id,
		)
		await util.send_success(ctx, f"Stars are no longer counted in {channel.mention}")
		await self.bot.cache.cache_starboard_settings()

	@starboard.command(name="unblacklist", description="Unblacklist a channel from being counted for starboard", usage="```Swift\nSyntax: !starboard unblacklist <channel>\nExample: !starboard unblacklist #msg```",extras={'perms': 'manage channels'}, brief='channel')
	async def starboard_unblacklist(self, ctx, channel: discord.TextChannel):
		await self.bot.db.execute(
			"""
			DELETE FROM starboard_blacklist WHERE guild_id = %s AND channel_id = %s
			""",
			ctx.guild.id,
			channel.id,
		)
		await util.send_success(ctx, f"Stars are now again counted in {channel.mention}")
		await self.bot.cache.cache_starboard_settings()

	@starboard.command(name="current", description="See current starboard config", extras={'perms': 'manage channels'})
	async def starboard_current(self, ctx):
		starboard_settings = self.bot.cache.starboard_settings.get(str(ctx.guild.id))
		if not starboard_settings:
			raise exceptions.Warning("Nothing has been configured on this server yet!")

		(
			is_enabled,
			board_channel_id,
			required_reaction_count,
			emoji_name,
			emoji_id,
			emoji_type,
			log_channel_id,
		) = starboard_settings

		if emoji_type == "custom":
			emoji = self.bot.get_emoji(emoji_id)
		else:
			emoji = emoji_name

		blacklisted_channels = await self.bot.db.execute(
			"""
			SELECT channel_id FROM starboard_blacklist WHERE guild_id = %s
			""",
			ctx.guild.id,
			as_list=True,
		)

		content = discord.Embed(title=":star: Current starboard settings", color=int("ffac33", 16))
		content.add_field(
			name="State", value=f"{self.bot.yes} Enabled" if is_enabled else f"{self.bot.no} Disabled"
		)
		content.add_field(name="Emoji", value=emoji)
		content.add_field(name="Reactions required", value=required_reaction_count)
		content.add_field(
			name="Board channel",
			value=f"<#{board_channel_id}>" if board_channel_id is not None else None,
		)
		content.add_field(
			name="Log channel",
			value=f"<#{log_channel_id}>" if log_channel_id is not None else None,
		)
		content.add_field(
			name="Blacklisted channels",
			value=" ".join(f"<#{cid}>" for cid in blacklisted_channels)
			if blacklisted_channels
			else None,
		)

		await ctx.send(embed=content)

async def setup(bot):
	await bot.add_cog(chat(bot))
