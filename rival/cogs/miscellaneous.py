import random,tweepy,yarl,os,sys,json,requests,io,re,regex,asyncio,time,orjson,string,random,typing,aiohttp,arrow,pytz,discord,humanize,datetime,socket
from discord.ext import commands
import instaloader
from typing import Union
from instaloader import Post,Profile
from urllib.parse import urlsplit
from urllib.request import urlopen
from libraries import emoji_literals, minestat
from modules import exceptions, util
from bs4 import BeautifulSoup
from modules.buttons import LinkButton
from pathlib import Path
import button_paginator as pg
from concurrent.futures import ThreadPoolExecutor
import instagram_reel as instagram
from discord import Webhook
cached=None
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import modules.instagram as instagram
from modules.melanieapi import InstagramPostResponse
i: instaloader.Instaloader = instaloader.Instaloader()
i.context._session.proxies.update({'http':'http://14abea38a24b7:30b94753d2@http://168.158.200.49:12323','https':'https://14abea38a24b7:30b94753d2@https://168.158.200.49:12323'})
try:
	#i.login("imgoinginguys","Speed6386$")
	#i.save_session_to_file()
	i.load_session_from_file("imgoinginguys")
except:
	try:
		i.login("imgoinginguys","Speed6386$")
		i.save_session_to_file()
	except:
		i=instaloader.Instaloader().login("imgoinginguys","Speed6386$")


from moviepy.editor import *
import glob, re
from yt_dlp import YoutubeDL
from io import BytesIO

cookies= {}
regexes = [
	'https:\/\/www\.instagram\.com\/reel\/([a-zA-Z0-9_\-]*)',
]
regexes = [re.compile(x) for x in regexes]

async def codeGen(size=6, chars=string.ascii_uppercase + string.ascii_lowercase):
	return ''.join(random.choice(chars) for _ in range(size))

def strip_codeblock(content):
	if content.startswith('```') and content.endswith('```'):
		return content.strip('```')
	return content.strip('` \n')

class Flags(commands.FlagConverter, prefix='--', delimiter=' ', case_insensitive=True):
	@classmethod
	async def convert(cls, ctx, argument: str):
		argument = strip_codeblock(argument).replace(' —', ' --')
		return await super().convert(ctx, argument)
	channel: discord.TextChannel =None
	name: str 
	avatar: str=None


class Miscellaneous(commands.Cog):
	"""Miscellaneous commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "🔮"
		self.color=self.bot.color
		self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),timeout=aiohttp.ClientTimeout(total=30),connector=aiohttp.TCPConnector(verify_ssl=False,family=socket.AF_INET, keepalive_timeout=30, limit=500, limit_per_host=100, ttl_dns_cache=3600),headers={"CF-Access-Client-Id": "d11815fca1544bb56c87a44b6fd192cd.access","CF-Access-Client-Secret": "3510d242c26414a1bda7163120344c2aa54f56ee56782a343bf2d205293bf1df"},)
		auth = tweepy.OAuthHandler("4R8BAE5oIi2PbmoVdSfAP7fQC", "caDyyTyOahyTTRjT59ZCYxBEbprOltC3HrtxhxOO9Ouv3m5VMR")
		auth.set_access_token("4259600601-RUI8J2afi16LCTgfPsRJ8jFtR5PDgxEc8s3oRnc", "nTWXjuMhnF3vFVLdgvbaMrvjkvQ4qfMAyBhCBzhM9Ax2v")
		self.twitter_api = tweepy.API(auth)
		self.cd_mapping = commands.CooldownMapping.from_cooldown(10, 10, commands.BucketType.member)
		self._cd = commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member)
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

	# async def download(self, url, filename):
	# 	opts = {
	# 		'outtmpl': f'reel/{filename}.%(ext)s',
	# 		'format': 'bestaudio/best',
	# 		'username': 'imgoinginguys',
	# 		'password': 'Fuckyou123',
	# 		'nocheckcertificate': True,
	# 		'proxy': proxy,
	# 	}
	# 	with YoutubeDL(opts) as ytdl:
	# 		ytdl.download([str(url)])
	# 	path = glob.glob(f'reel/{filename}.*')[0]
	# 	clip = VideoFileClip(path)
	# 	clip1 = clip.subclip(0, 7)
	# 	w1 = clip1.w
	# 	h1 = clip1.h
	# 	print("Width x Height of clip 1 : ", end = " ")
	# 	print(str(w1) + " x ", str(h1))
	# 	clip2 = clip1.resize(0.5)
	# 	w2 = clip2.w
	# 	h2 = clip2.h
	# 	print("Width x Height of clip 2 : ", end = " ")
	# 	print(str(w2) + " x ", str(h2))
	# 	a = clip2.write_videofile("outputs/reel.mp4")
	# 	os.remove(path)

	@commands.command(name='testig')
	async def testig(self, ctx, username:str):
		profile=await self.bot.loop.run_in_executor(None, lambda:Profile.from_username(i.context,username))
		await ctx.send(profile.username)

	async def download(self, url, filename):
		executor=ThreadPoolExecutor(max_workers=2)
		ydl = YoutubeDL({
			'outtmpl': f'reel/{filename}.%(ext)s',
			'format': 'bestaudio/best',
			'nocheckcertificate': True,
			'proxy': 'socks5://14acd04c580ce:cf437bf954@31.131.11.197:12324'
		})
		await self.bot.loop.run_in_executor(executor, lambda: ydl.download([str(url)]))
		path = glob.glob(f'reel/{filename}.*')[0]
		clip = VideoFileClip(path)
		clip1 = clip.subclip(0, 7)
		w1 = clip1.w
		h1 = clip1.h
		print("Width x Height of clip 1 : ", end = " ")
		print(str(w1) + " x ", str(h1))
		print("---------------------------------------")
		clip2 = clip1.resize(0.7)
		w2 = clip2.w
		h2 = clip2.h
		print("Width x Height of clip 2 : ", end = " ")
		print(str(w2) + " x ", str(h2))
		a = clip2.write_videofile("outputs/reel.mp4", threads = 12, fps=24, audio=True)


	def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		"""Returns the ratelimit left"""
		bucket = self._cd.get_bucket(message)
		return bucket.update_rate_limit()

	async def binary(self):
		with open("outputs/reel.mp4", "rb") as fh:
			return BytesIO(fh.read())

	async def check_url(self, content):
		for regex in regexes:
			matches = re.search(regex, content)

			if matches:
				state = bool(matches)
				url = matches[0]
				id = matches[1]
				return state, url, id
		return False, None, None

	async def download_media(self, media_url: str, filename: str, max_filesize: int):
		# The url params are unescaped by aiohttp's built-in yarl
		# This causes problems with the hash-based request signing that instagram uses
		# Thankfully you can plug your own yarl.URL with encoded=True so it wont get encoded twice
		async with self.bot.session.get(yarl.URL(media_url, encoded=True)) as response:
			if not response.ok:
				logger.error(await response.text())
				response.raise_for_status()

			if int(response.headers.get("content-length", max_filesize)) > max_filesize:
				return f"\n{media_url}"
			else:
				buffer = io.BytesIO(await response.read())
				return discord.File(fp=buffer, filename=filename)

	async def download_ig(self, media_url: str):
		# The url params are unescaped by aiohttp's built-in yarl
		# This causes problems with the hash-based request signing that instagram uses
		# Thankfully you can plug your own yarl.URL with encoded=True so it wont get encoded twice
		url=media_url
		seed = str(int(arrow.now().timestamp))
		file_name, ext = os.path.splitext(os.path.basename(urlsplit(url).path))
		filename = "{}_{}{}".format(seed, file_name, ext)
		async with self.bot.session.get(yarl.URL(media_url, encoded=True)) as response:
			if not response.ok:
				logger.error(await response.text())
				response.raise_for_status()
			
			buffer = io.BytesIO(await response.read())
			return discord.File(fp=buffer, filename=filename)

	async def get_medal_clip(self,clip_path: str) -> dict:
		original_url = f"https://medal.tv/games/{clip_path}"
		async with aiohttp.ClientSession() as session:
			# get page source to extract __NEXT_DATA__
			async with session.get(original_url) as response:
				source = await response.text()
				next_data = orjson.loads(
					BeautifulSoup(source, "lxml").find("script", {"id": "__NEXT_DATA__"}).text
				)

			# get the build id from next_data
			build_id = next_data["buildId"]

			# get clip data from newest build
			async with session.get(
				f"https://medal.tv/_next/data/{build_id}/en/games/{clip_path}.json"
			) as response:
				return await response.json()

	async def get_post(self, context, shorted_url):
		return Post.from_shortcode(context,shorted_url)

	# @commands.command(name='igstory', description="get a user's instagram story", brief='username',usage='```Swift\nSyntax: !igstory <username>\nExample: !igstory snoopdog```')
	# async def igstory(self, ctx, *, username):
	# 	async def ya():
	# 		id=i.check_profile_id(username=username)
	# 		post = await ctx.bot.loop.run_in_executor(
	# 					None,
	# 					lambda: Post.from_shortcode(i.context,shorted_url),)

	@commands.command(name='reskin', description='change the bots look', brief='theme')
	async def reskin(self, ctx, *, name):
		await ctx.reply('head aaaaaa :rofl:')

	@commands.group(name='paginator', aliases=['page','pages','createpage','createpages'], description='make paginated custom commands', extras={'perms':'manage messages'})
	@commands.has_permissions(manage_messages=True)
	async def paginator(self, ctx):
		if ctx.invoked_subcommand is None:
			return await util.command_group_help(ctx)

	@paginator.command(name='add', aliases=['a','create','c'], description='add paginated custom commands using [this embed creator](https://rival.rocks/embed)', extras={'perms':'manage messages'}, brief='trigger, embeds', usage='```Swift\nSyntax: !paginator add <trigger> <embeds>\nExample: !paginator add !cop {embed1}{embed2}```')
	@commands.has_permissions(manage_messages=True)
	async def paginator_add(self, ctx, trigger, *, embeds):
		if ctx.guild.id not in self.bot.cache.paginator:
			self.bot.cache.paginator[ctx.guild.id]={}
		if trigger in self.bot.cache.paginator[ctx.guild.id]:
			return await util.send_error(ctx, f"paginator `{trigger}` already **found**")
		self.bot.cache.paginator[ctx.guild.id].update({trigger:embeds})
		await self.bot.db.execute("""INSERT INTO paginator VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE content = VALUES(content)""", ctx.guild.id, trigger, embeds,datetime.datetime.now())
		return await util.send_good(ctx, f"successfully **Created** paginator with trigger `{trigger}`")

	@paginator.command(name='remove', aliases=['rem','delete','del','r','d'], description='remove paginated custom commands', extras={'perms':'manage messages'}, brief='trigger', usage='```Swift\nSyntax: !paginator remove <trigger>\nExample: !paginator remove !cop```')
	@commands.has_permissions(manage_messages=True)
	async def paginator_remove(self, ctx, *, trigger):
		if ctx.guild.id in self.bot.cache.paginator:
			if trigger in self.bot.cache.paginator[ctx.guild.id]:
				content=self.bot.cache.paginator[ctx.guild.id].get(trigger)
				await self.bot.db.execute("""DELETE FROM paginator WHERE guild_id = %s AND trig = %s AND content = %s""",ctx.guild.id,trigger,content)
				self.bot.cache.paginator[ctx.guild.id].pop(trigger)
				return await util.send_good(ctx, f"successfully **deleted** paginator with trigger `{trigger}`")
			else:
				return await util.send_error(ctx, f"no **paginator** found with trigger `{trigger}`")
		else:
			return await util.send_error(ctx, f"no **paginator** found with trigger `{trigger}`")

	@paginator.command(name='list', description='list paginated custom commands', extras={'perms':'manage messages'})
	@commands.has_permissions(manage_messages=True)
	async def paginator_list(self, ctx):
		if ctx.guild.id in self.bot.cache.paginator:
			rows=[]
			for k,v in self.bot.cache.paginator[ctx.guild.id].items():
				rows.append(f"**{k}** - `{v}`")
			if rows:
				content=discord.Embed(title=f"{ctx.guild.name}'s paginators", color=self.bot.color)
				await util.send_as_pages(ctx, content, rows)
			else:
				return await util.send_error(ctx, f"no **paginators** found")
		else:
			return await util.send_error(ctx, f"no **paginators** found")


	@commands.group(aliases =['webhooks', 'w'])
	async def webhook(self, ctx):
		if ctx.invoked_subcommand is None:
			return await util.command_group_help(ctx)

	@webhook.command(name='flags', description='shows optional flags for webhook create/edit')
	async def webhook_flags(self, ctx):
		return await ctx.reply(embed=discord.Embed(title='rival webhhook flags',description='--avatar <link>\n--name <name>\n--channel <channel>', color=self.bot.color))

	@webhook.command(name='create',aliases =['add','a','c','make'],extras={"perms":"Manage Webhooks"},description = "Create a webhook through the bot",brief = "subcommand, flags",help = "```Swift\nSyntax: !webhook create --name [name] --channel [channel] --avatar [URL/IMG]\nExample: !webhook create --name hi --channel #general --avatar URL```")
	@commands.has_permissions(manage_webhooks=True)
	async def create(self, ctx, *, flags: Flags):
		async with ctx.typing():
			if flags.channel==None:
				flags.channel = ctx.channel
			if flags.name == None:
				return await utils.send_command_help(ctx)
			if flags.avatar and flags.avatar.startswith('https://'):
				async with aiohttp.ClientSession() as session:
					async with session.get(flags.avatar) as response:
						flags.avatar = await response.read()
			webhook = await flags.channel.create_webhook(name=flags.name, avatar=flags.avatar, reason=f"Webhook created by {ctx.author}")
			code = await codeGen()
			await util.send_good(ctx, f"created **webhook** with code `{code}`")
			await self.bot.db.execute("""INSERT INTO webhook VALUES(%s,%s,%s,%s)""", code, flags.channel.id, ctx.guild.id, webhook.url)

	@webhook.command(name='delete',aliases =['del', 'remove', 'r', 'd'],extras={"perms":"Manage Webhooks"},description = "Delete a webhook through the bot",brief = "code",usage="```Swift\nSyntax: !webhook delete [code]\nExample: !webhook delete DaVjD```")
	@commands.has_permissions(manage_webhooks=True)
	async def delete(self, ctx, code:str):
		check=await self.bot.db.execute("""SELECT url FROM webhook WHERE guild_id = %s AND ref = %s""", ctx.guild.id, code, one_value=True)
		if check:
			async with aiohttp.ClientSession() as session:
				webhook = Webhook.from_url(f'{check}', session=session)
				await webhook.delete(reason=f"Deleted by {ctx.author}")
			await util.send_good(ctx, f"webhook **deleted** with code `{code}`")
			await self.bot.db.execute("""DELETE FROM webhook WHERE guild_id = %s AND ref = %s""", ctx.guild.id, code)
		else:
			return await utils.send_error(ctx, f"invalid webhook with code **`{code}`**")

	@webhook.command(name='send',aliases=['post'],extras={"perms":"Manage Webhooks"},description = "Send a message or embed to a webhook via the bot",brief = "code, message",usage="```Swift\nSyntax: !webhook send [code] [message]\nExample: !webhook send daFgJ {embed}{title: hi}```")
	@commands.has_permissions(manage_webhooks=True)
	async def send(self, ctx, code, *, message):
		check = await self.bot.db.execute("""SELECT url FROM webhook WHERE guild_id = %s AND ref = %s""", ctx.guild.id, code, one_value=True)
		if not check:
			return await utils.send_error(ctx, f"no **webhook** found with code `{code}`")
		else:
			if message.startswith("{embed}"):
			   #message = await utils.test_vars(ctx, user, params=message)
				em = await util.to_objectt(ctx, params=message)
				async with aiohttp.ClientSession() as session:
					webhook = Webhook.from_url(f'{check}', session=session)
					try:
						await webhook.send(embed=em)
					except Exception as e:
						return await ctx.send(f"```{e}```")
				return await util.send_good(ctx, f"webhook **sent**")
			elif not message.startswith("{embed}"):
				async with aiohttp.ClientSession() as session:
					webhook = Webhook.from_url(f'{check}', session=session)
					try:
						await webhook.send(f'{message}')
					except Exception as e:
						return await ctx.send(f"```{e}```")
				return await util.send_good(ctx, f"webhook **sent**")

	@webhook.command(name='view',aliases=['list', 'all'],extras={"perms":"Manage_webhooks"},description = "View the servers existing webhooks",brief="None",usage="```Swift\nExample: !webhook view```")
	@commands.has_permissions(manage_webhooks=True)
	async def view(self, ctx):
		check = await self.bot.db.execute("""SELECT ref,channel_id FROM webhook WHERE guild_id = %s""", ctx.guild.id)
		if check:
			i=0
			rows=[]
			for code,channel_id in check:
				i+=1
				channel=ctx.guild.get_channel(channel_id)
				rows.append(f"`{i}` **{code}** - {channel.mention}")
			content = discord.Embed(title=f"{ctx.guild.name}'s webhooks", color=self.bot.color, url="https://rival.rocks")
			content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
			await util.send_as_pages(ctx, content, rows)
		else:
			return await util.send_error(ctx, f"no existing webhooks found in this guild")

	@webhook.group(name='edit',aliases =['e'],extras={"perms":"Manage Webhooks"},description = "Edit existing webhooks through the bot",brief = "[subcommand] <argument>",usage = "```Swift\nSyntax: !webhook edit [subcommand] <argument>\nExample: !webhook edit name rival```")
	async def edit(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@edit.command(name='name',aliases =['n'],extras={"perms":"Manage Webhooks"},description = "Edit an existing webhook name",brief = "code, name",usage = "```Swift\nSyntax: !webhook edit name [code] [new_name]\nExample: !webhook edit name daBga newname```")
	@commands.has_permissions(manage_webhooks=True)
	async def name(self, ctx, code, *, name):
		check = await self.bot.db.execute("""SELECT url FROM webhook WHERE guild_id = %s AND ref = %s""", ctx.guild.id, code, one_value=True)
		if not check:
			return await util.send_error(ctx, f"inavlid webhook with code **`{code}`**")
		else:
			async with aiohttp.ClientSession() as session:
				webhook = Webhook.from_url(f'{check}', session=session)
				await webhook.edit(name=str(name))
			return await util.send_good(ctx, f"webhook **renamed** to `{name}`")

	@edit.command(name='avatar',aliases =['av', 'pfp', 'icon'],extras={"perms":"Manage Webhooks"},description = "Edit an existing webhook avatar",brief = "code, new_avatar",usage = "```Swift\nSyntax: !webhook edit avatar [code] [new_avatar]\nExample: !webhook edit avatar daJkda https://rival.rocks/cat.png```")
	@commands.has_permissions(manage_webhooks=True)
	async def avatar(self, ctx, code, avatar=None):
		vaild_urls = ['https', 'http']
		check = await self.bot.db.execute("""SELECT url FROM webhook WHERE guild_id = %s AND ref = %s""", ctx.guild.id, code, one_value=True)
		zz = None
		if not check:
			return await util.send_error(ctx, f"invalid webhook with code **`{code}`**")
		
		if ctx.message.attachments:
			async with aiohttp.ClientSession() as sess:
				async with sess.get(ctx.message.attachments[0].url) as response:
					avatar = await response.read() 
					zz = ctx.message.attachments[0].url
		if str(avatar).lower().startswith(tuple(vaild_urls)):
			async with aiohttp.ClientSession() as sess:
				async with sess.get(avatar) as response:
					avatar = await response.read()
					zz = avatar
		if avatar == None:
			return await util.send_command_help(ctx)
		async with aiohttp.ClientSession() as session:
			webhook = Webhook.from_url(f'{check}', session=session)
			await webhook.edit(avatar=avatar)
		return await util.send_good(ctx, f"changed webhook **avatar** to [url]({zz})")


	@commands.Cog.listener()
	async def on_message(self, message:discord.Message):
		if message.author.bot:
			return
		if not message.guild:
			return
		if not message.content:
			return
		if not message.content.startswith("rival "):
			return
		ctx=await self.bot.get_context(message)
		use_embeds = False
		if message.guild.get_member(928394879200034856):
			return
		urls=message.content.strip('rival ')
		regex = r"https://medal\.tv/games/([^\s?]*)"
		matches = re.finditer(regex, message.content)
		if matches:
			for match in matches:
				data = await self.get_medal_clip(match.group(1))
				content_url = data["pageProps"]["clip"]["contentUrl"]
				content_title = data["pageProps"]["clip"]["contentTitle"]
				async with aiohttp.ClientSession() as session:
					async with session.get(content_url) as s:
						f=discord.File(fp=io.BytesIO(await s.read()),filename="rivalmedal.mp4")
						return await ctx.send(file=f)
		if "instagram" in urls:
			print('trying')
			if not message.author.bot:
				rk = self.get_ratelimit(message)
				if rk is not None:
					return
				if "reel" in urls:
					if message.author.id not in self.bot.cache.donators:
						#if message.guild.owner.id not in self.bot.cache.donators:
						return await util.send_error(ctx, f"only for **donators**")
					try:
						ig=await InstagramPostResponse.from_url(self.session,ctx,urls)
						if len(ig.items) <= 1:
							async with aiohttp.ClientSession() as sesh:
								async with sesh.get(ig.items[0].video_url) as r:
									b=await r.read()
						return await message.channel.send(embed=ig.make_embed(ctx=ctx),file=discord.File(fp=io.BytesIO(b), filename="rivalinstagram.mp4"))
					except Exception as e:
						try:
							state, url, id = await self.check_url(urls)
							await self.download(url, id)
							await message.channel.send(file=discord.File(fp=await self.binary(), filename='rivalreels.mp4'))
							os.remove('outputs/reel.mp4')
							return
						except Exception as e:
							pass
				url=urls
				a=url[26:28]  
				b=url[26:27]
				c=url[26:30]
				# b='tv'
				if a=='tv':
					shorted_url=url[29:40]
					post = await ctx.bot.loop.run_in_executor(
						None,
						lambda: Post.from_shortcode(i.context,shorted_url),
					)
					file=await self.download_ig(post.video_url)
					try:
						return await message.channel.send(file=file)
					except:
						return await message.channel.send(post.video_url)
					#i.download_post(post, target='download_post'))
				if b=='p':
					shorted_url=url[28:39]
					post = await ctx.bot.loop.run_in_executor(
						None,
						lambda: Post.from_shortcode(i.context,shorted_url),
					)
					images=[]
					files=[]
					r=0
					if post.typename == 'GraphSidecar':
						post.sidecar_nodes=post.get_sidecar_nodes()
						for sidecar_node in post.sidecar_nodes:
							if post.caption:
								desc=post.caption
							else:
								if post.title:
									desc=post.title
								else:
									desc=""
							if post.owner_profile.profile_pic_url:
								pic=post.owner_profile.profile_pic_url
							else:
								pic=None
							images.append(discord.Embed(description=f"[Post]({url}) Requested by {message.author.mention}\n"+desc, color=self.color).set_image(url=sidecar_node.display_url).set_author(name=post.owner_username, icon_url=post.owner_profile.profile_pic_url or None))
						img=[]
						for image in images:
							r+=1
							image.set_footer(text=f"Page {r}/{len(images)}")
							img.append(image)
						paginator = pg.Paginator(self.bot, img, ctx, invoker=ctx.author.id)
						if len(img) > 1:
							paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
						#paginator.add_button('delete', label='Close the paginator', emoji='⏹')
							paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
						return await paginator.start()
					elif post.video_url:
						file=await self.download_ig(post.video_url)
						try:
							return await message.channel.send(file=file)
						except:
							return await message.channel.send(post.video_url)
					else:
						try:
							file=await self.download_ig(post.url)
							if file:
								return await message.channel.send(file=file)
							else:
								return await message.channel.send(post.url)
						except:
							return await message.channel.send(post.url)
					#i.download_post(post, target='download_post')
				# if c=='reel':
				# 	shorted_url=url[31:42]
				# 	post = await ctx.bot.loop.run_in_executor(
				# 		None,
				# 		lambda: Post.from_shortcode(i.context,shorted_url),
				# 	)
				# 	if post.video_url:
				# 		file=await self.download_ig(post.video_url)
				# 		try:
				# 			return await message.channel.send(file=file)
				# 		except:
				# 			return await message.channel.send(post.video_url)
		elif "twitter" in urls:
			if not message.author.bot:
				tweet_url=urls
				if "status" in tweet_url:
					tweet_id = re.search(r"status/(\d+)", tweet_url).group(1)
				else:
					tweet_id = tweet_url

				try:
					tweet = await ctx.bot.loop.run_in_executor(
						None,
						lambda: self.twitter_api.get_status(str(tweet_id), tweet_mode="extended"),
					)

				except Exception:
					await ctx.send(f":warning: Could not get tweet `{tweet_url}`")
				if tweet.possibly_sensitive and not message.channel.nsfw:
					return await util.send_error(ctx, f"I can't embed NSFW Content in a Non-NSFW Channel")
				media_files = []
				try:
					media = tweet.extended_entities.get("media", [])
				except AttributeError:
					media = []

				if not media:
					await ctx.send(f":warning: Could not find any images from tweet id `{tweet_id}`")
	
				for resource in media:
					media_url = resource["media_url"]
					video_url = None
					if not resource["type"] == "photo":
						video_variants = resource["video_info"]["variants"]
						largest_rate = -1
						for video in video_variants:
							if (
								video["content_type"] == "video/mp4"
								and video["bitrate"] > largest_rate
							):
								largest_rate = video["bitrate"]
								video_url = video["url"]
								media_url = video["url"]

					media_files.append((media_url, video_url))

				content = discord.Embed(colour=int(tweet.user.profile_link_color, 16))
				content.set_author(
					icon_url=tweet.user.profile_image_url,
					name=f"@{tweet.user.screen_name}",
					url=f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
				)

				if use_embeds:
					# just send link in embed
					embeds = []
					videos = []
					for n, (media_url, video_url) in enumerate(media_files, start=1):
						url = media_url.replace(".jpg", "?format=jpg&name=orig")
						content.set_image(url=url)
						if n == len(media_files):
							content.timestamp = tweet.created_at
						embeds.append(content.copy())
						if video_url is not None:
							# contains a video/gif, send it separately
							videos.append(video_url)
						content._author = None

					if embeds:
						await ctx.send(embeds=embeds)
					if videos:
						await ctx.send("\n".join(videos))
				else:
					# download file and rename, upload to discord
					tweet_link = "https://" + tweet.full_text.split(" ")[-1].split("https://")[-1]
					username = discord.utils.escape_markdown(tweet.user.screen_name)
					tasks = []
					for n, (media_url, video_url) in enumerate(media_files, start=1):
						# is image not video
						if video_url is None:
							extension = "jpg"
						else:
							extension = "mp4"

						filename = f"@{tweet.user.screen_name}-{tweet.id}-{n}.{extension}"
						# discord normally has 8MB file size limit, but it can be increased in some guilds
						max_filesize = getattr(ctx.guild, "filesize_limit", 8388608)
						url = media_url.replace(".jpg", "?format=jpg&name=orig")
						tasks.append(self.download_media(url, filename, max_filesize))

					files = []
					results = await asyncio.gather(*tasks)
					for result in results:
						if isinstance(result, discord.File):
							files.append(result)
						else:
							caption += result

					await ctx.send( files=files, view=LinkButton("View on twitter", tweet_link))
			try:
				# delete discord automatic embed
				await ctx.message.edit(suppress=True)
			except (discord.Forbidden, discord.NotFound):
				pass

	@commands.group(aliases=["hs"])
	async def horoscope(self, ctx):
		"""Get your daily horoscope."""
		if ctx.invoked_subcommand is None:
			await self.send_hs(ctx, "today")

	@horoscope.command(name="tomorrow")
	async def horoscope_tomorrow(self, ctx):
		"""Get tomorrow's horoscope."""
		await self.send_hs(ctx, "tomorrow")

	@horoscope.command(name="yesterday")
	async def horoscope_yesterday(self, ctx):
		"""Get yesterday's horoscope."""
		await self.send_hs(ctx, "yesterday")

	async def send_hs(self, ctx, day):
		sunsign = await self.bot.db.execute(
			"SELECT sunsign FROM user_settings WHERE user_id = %s", ctx.author.id, one_value=True
		)
		if not sunsign or sunsign is None:
			raise exceptions.Info(
				"Please save your zodiac sign using `!horoscope set <sign>`\n"
				"Use `!horoscope list` if you don't know which one you are."
			)
		params = {"sign": sunsign, "day": day}
		async with aiohttp.ClientSession() as session:
			async with session.post(
				"https://aztro.sameerkumar.website/", params=params
			) as response:
				data = await response.json()

		sign = self.hs.get(sunsign)
		content = discord.Embed(
			color=int("9266cc", 16),
			title=f"{sign['emoji']} {sign['name']} - {data['current_date']}",
			description=data["description"],
		)

		content.add_field(name="Mood", value=data["mood"], inline=True)
		content.add_field(name="Compatibility", value=data["compatibility"], inline=True)
		content.add_field(name="Color", value=data["color"], inline=True)
		content.add_field(name="Lucky number", value=data["lucky_number"], inline=True)
		content.add_field(name="Lucky time", value=data["lucky_time"], inline=True)
		content.add_field(name="Date range", value=data["date_range"], inline=True)

		await ctx.send(embed=content)

	@horoscope.command()
	async def set(self, ctx, sign):
		"""Save your zodiac sign."""
		sign = sign.lower()
		if self.hs.get(sign) is None:
			raise exceptions.Info(
				f"`{sign}` is not a valid zodiac! Use `!horoscope list` for a list of zodiacs."
			)

		await ctx.bot.db.execute(
			"""
			INSERT INTO user_settings (user_id, sunsign)
				VALUES (%s, %s)
			ON DUPLICATE KEY UPDATE
				sunsign = VALUES(sunsign)
			""",
			ctx.author.id,
			sign,
		)
		await ctx.send(f"Zodiac saved as **{sign.capitalize()}** {self.hs.get(sign)['emoji']}")

	@horoscope.command()
	async def list(self, ctx):
		"""Get list of all zodiac signs."""
		content = discord.Embed(
			color=int("9266cc", 16),
			title=":crystal_ball: Zodiac signs",
			description="\n".join(
				f"{sign['emoji']} **{sign['name']}**: {sign['date_range']}"
				for sign in self.hs.values()
			),
		)
		return await ctx.send(embed=content)

	@commands.command(aliases=["colour"], description='Different color sources can be chained together to create patterns', brief='hex/member/role/random/image')
	async def color(self,ctx,*sources: Union[int, discord.Member, discord.Role, str],):
		"""
		Visualise colors
		Different color sources can be chained together to create patterns.
		Usage:
			>color <hex>
			>color <@member>
			>color <@role>
			>color random [amount]
			>color <image url>
		"""
		if not sources and not ctx.message.attachments:
			return await util.send_command_help(ctx)

		if len(sources) > 50:
			await ctx.send("Maximum amount of colors is 50, ignoring rest...")

		colors = []
		next_is_random_count = False
		for source in sources[:50]:
			# random used with an amount
			if next_is_random_count and isinstance(source, int):
				slots = 50 - len(colors)
				amount = min(source, slots)
				colors += ["{:06x}".format(random.randint(0, self.color)) for _ in range(amount)]
			# member or role color
			elif isinstance(source, (discord.Member, discord.Role)):
				colors.append(str(source.color))

			else:
				source = str(source).strip("#")
				converted_color = await util.get_color(ctx, source)
				# random without an amount
				if next_is_random_count:
					colors.append("{:06x}".format(random.randint(0, self.color)))
					next_is_random_count = False

				# image url
				elif source.startswith("http"):
					try:
						url_color = await util.color_from_image_url(
							source,
							fallback=None,
							size_limit=True,
							ignore_errors=False,
						)
					except ValueError:
						await ctx.send("Supplied image is too large!")
					except UnidentifiedImageError:
						await ctx.send("Supplied url is not an image!")
					else:
						if url_color is not None:
							colors.append(url_color)

				# random
				elif source.lower() == "random":
					next_is_random_count = True

				# hex or named discord color
				elif converted_color is not None:
					colors.append(str(converted_color))

				else:
					await ctx.send(f"I don't know what to do with `{source}`")

		# random was last input without an amount
		if next_is_random_count:
			colors.append("{:06x}".format(random.randint(0, self.color)))

		# try attachments too
		for a in ctx.message.attachments:
			try:
				url_color = await util.color_from_image_url(
					a.url,
					fallback=None,
					size_limit=True,
					ignore_errors=False,
				)
			except ValueError:
				await ctx.send("Supplied attachment is too large!")
			except UnidentifiedImageError:
				await ctx.send("Supplied attachment is not an image!")
			else:
				if url_color is not None:
					colors.append(url_color)

		if not colors:
			return await util.send_error(ctx, "There is nothing to show")

		colors = [x.strip("#") for x in colors]
		content = discord.Embed(colour=int(colors[0], 16))

		url = "https://api.color.pizza/v1/" + ",".join(colors)
		async with self.bot.session.get(url) as response:
			colordata = (await response.json(loads=orjson.loads)).get("colors")

		if len(colors) == 1:
			discord_color = await util.get_color(ctx, colors[0])
			hexvalue = colordata[0]["requestedHex"]
			rgbvalue = discord_color.to_rgb()
			name = colordata[0]["name"]
			luminance = colordata[0]["luminance"]
			image_url = f"http://www.colourlovers.com/img/{colors[0]}/200/200/color.png"
			content.title = name
			content.description = "\n".join(
				[
					f"**HEX:** `{hexvalue}`",
					f"**RGB:** {rgbvalue}",
					f"**Luminance:** {luminance:.4f}",
				]
			)
		else:
			content.description = "\n".join(
				[f'`{c["requestedHex"]}` **| {c["name"]}**' for c in colordata]
			)
			image_url = f"https://www.colourlovers.com/paletteImg/{'/'.join(colors)}/palette.png"

		content.set_image(url=image_url)
		await ctx.send(embed=content)

async def setup(bot):
	await bot.add_cog(Miscellaneous(bot))
