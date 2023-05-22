import os, string, random, re,humanize,aiohttp,discord,time,io,socket,typing
from datetime import datetime
from shazamio import Shazam
from pydub import AudioSegment
from discord.ext import tasks, commands, menus
from ast import Bytes
from TTApi import TikTokApi
from io import BytesIO
from modules import util
from bs4 import BeautifulSoup
from modules.tiktok_m import TikTokVideoResponse
from modules.melanieapi import InstagramStoryResposne
import button_paginator as pg
tiktok = TikTokApi()

class MySource(menus.ListPageSource):
	async def format_page(self, menu, entries):
		if self.get_max_pages() > 1:
			ee="entries"
		else:
			ee='entry'
		entries.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()} ({self.get_max_pages()} {ee})")
		return entries

class StoryPaginator(discord.ui.View,menus.MenuPages):
	def __init__(self, bot, source, files):
		super().__init__(timeout=60)
		self._source = source
		self.value = 0
		self.bot = bot
		self.files = files
		self.current_page = 0
		self.ctx = None
		self.message = None

	async def start(self, ctx, *, files=None, channel=None,wait=False):
		# We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
		await self._source._prepare_once()
		self.ctx = ctx
		self.message = await self.send_initial_message(ctx, ctx.channel)

	async def on_timeout(self):
		await self.message.edit(view=None)
		return

	async def _get_kwargs_from_page(self, page):
		"""This method calls ListPageSource.format_page class"""
		value = await super()._get_kwargs_from_page(page)
		if 'view' not in value:
			value.update({'view': self})
		return value

	async def interaction_check(self, interaction):
		"""Only allow the author that invoke the command to be able to use the interaction"""
		if interaction.user != self.ctx.author:
			await interaction.response.send_message(ephemeral=True, embed=discord.Embed(description=f"{self.bot.warn} <@!{interaction.user.id}>: **You aren't the author of this embed**", color=self.bot.color))
		else:   
			await interaction.response.defer()      
			return interaction.user == self.ctx.author


	@discord.ui.button(emoji='<:shittyleft1:1032906735217819718>', style=discord.ButtonStyle.grey)
	async def before_page(self, button, interaction):
		if self.current_page == 0:
			await self.show_page(self._source.get_max_pages() - 1)
		else:
			await self.show_checked_page(self.current_page - 1)
		#await interaction.response.defer()


	@discord.ui.button(emoji='<:shittyright2:1032906840431923250>', style=discord.ButtonStyle.grey)
	async def next_page(self, button, interaction):
		if self.current_page == self._source.get_max_pages() -1:
			await self.show_page(0)
		else:
			await self.show_checked_page(self.current_page + 1)

class conversion(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.tikTokDomains = ('http://vt.tiktok.com/', 'http://app-va.tiktokv.com/', 'http://vm.tiktok.com/', 'http://m.tiktok.com/', 'http://tiktok.com/', 'http://www.tiktok.com/', 'http://link.e.tiktok.com/', 'http://us.tiktok.com/','https://vt.tiktok.com/', 'https://app-va.tiktokv.com/', 'https://vm.tiktok.com/', 'https://m.tiktok.com/', 'https://tiktok.com/', 'https://www.tiktok.com/', 'https://link.e.tiktok.com/', 'https://us.tiktok.com/')
		self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),timeout=aiohttp.ClientTimeout(total=30),connector=aiohttp.TCPConnector(verify_ssl=False,family=socket.AF_INET, keepalive_timeout=30, limit=500, limit_per_host=100, ttl_dns_cache=3600),headers={"CF-Access-Client-Id": "d11815fca1544bb56c87a44b6fd192cd.access","CF-Access-Client-Secret": "3510d242c26414a1bda7163120344c2aa54f56ee56782a343bf2d205293bf1df"},)
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

	async def download_data(self, url):
		video_data = await self.parse_video_data(url)
		return video_data

	async def download_video(self, url):
		video_binary = await self.get_video_binary(url)
		return video_binary

	async def checkURL(self, message):
		for link in self.tikTokDomains:
			if link in message:
				return True
		return False

	def format(self, text):
		if " thousand" in text:
			text=text.replace(" thousand", "k")
		if " million" in text:
			text=text.replace(" million", "m")
		return text

	async def igstats(self, username):
		async with aiohttp.ClientSession() as sesssion:
			async with session.get(f"https://www.instagram.com/{username}/?__a=1") as e:
				html=await e.text()
		pageSoup = BeautifulSoup(html, 'html.parser')
		user_stats_dict = {
		'user': username,
		'numberOfPosts' : str(pageSoup.find_all('span', {'class': 'g47SY'})[0].text).replace(',',''), #fix k
		'numberOfFollowers' : str(pageSoup.find_all('span', {'class': 'g47SY'})[1].text).replace(',',''),
		'numberOfFollowing' : str(pageSoup.find_all('span', {'class': 'g47SY'})[2].text).replace(',','')
		}
		avatar=soup.findall(text="profile_pic_url_hd")
		for number in ['numberOfPosts','numberOfFollowers','numberOfFollowing']:
			if user_stats_dict[number].__contains__('k'):
				if user_stats_dict[number].__contains__('.'):
					user_stats_dict[number] = user_stats_dict[number].replace('k',"00").replace('.','')
				else:
					user_stats_dict[number] = user_stats_dict[number].replace('k',"000")
		infoBox = pageSoup.find('div', {'class': '-vDIg'})
		if infoBox.find('h1', {'class': 'rhpdm'}) is not None:
			user_stats_dict['name'] = infoBox.find('h1', {'class': 'rhpdm'}).text
		else:
			user_stats_dict['name'] = None
		if infoBox.find('a', {'class': 'yLUwa'}) is not None:
			user_stats_dict['website'] = infoBox.find('a', {'class': 'yLUwa'}).text
		else:
			user_stats_dict['website'] = None

		if infoBox.find_all('span') is not None and len(
				[s for s in infoBox.find_all('span') if not s.has_attr('class')]) > 0:
			user_stats_dict['bio'] = [s for s in infoBox.find_all('span') if not s.has_attr('class')][0].text
		else:
			user_stats_dict['bio'] = None
		return user_stats_dict

	async def download_video(self, video_url, watermark=False, filename=None, path=None):
		try:
			if 'is_play_url' in video_url:
				video_binary = await self.get_video_binary(video_url)
				video_data = {'video_id': video_url.split("video_id=")[1].split("&")[0]}
			else:
				video_data = await self.parse_video_data(video_url)
				video_binary = await self.get_video_binary(video_data["download_urls"]["no_watermark" if not watermark else "watermark"])
			if not filename:
				filename = str(video_data["video_id"])+".mp4"
			if not path:
				path = filename
			with open(path, "wb") as v:
				v.write(video_binary)
				v.close()
			print(f"Successfully downloaded video by @{video_data['username'] if 'username' in video_data else 'Unknown User'} (path: {path})")
			return video_data
		except Exception as e:
			print(f"Failed to download video from url {video_url}: "+str(e))
			return False
		
	async def get_video_binary(self, download_url):
		"""
		DOWNLOAD_URL (str):
			Get this from the object that the parse_video_data function returns, it can either be download_video_url or download_video_url_watermark
			
		Returns:
			binary: Raw binary mp4 data        
		"""
		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(download_url) as video:
					binary=await video.read()
			#self.api.debug.success(f"Received binary data ({video.elapsed.total_seconds()}s)")
			return binary
		except Exception as e:
			print(e)
			
	async def parse_video_data(self, url, raw=False) -> dict:
		"""Grabs the video data from a tiktok video url
		
		URL/VIDEO_ID (str):
			https://vm.tiktok.com/ZMNnX3Q4q 
			7116227445648395526 
			https://www.tiktok.com/@peachyfitness4/video/7116227445648395526
		
		RAW (bool):
			Optional if u want the raw data tiktok provided from the video (this contains way more info)
			
		Returns:
			formatted data from the video in a json object 
			
		"""
		video_id = ""
		mobile_share_regex = "(http(s)?:\/\/(vm\.)tiktok.com\/[a-zA-Z0-9\/]+|http(s)?:\/\/(www\.)tiktok.com\/t\/[a-zA-Z0-9\/]+\/)"
		website_share_regex = "http(s)?:\/\/(www\.)?tiktok.com\/@[A-Za-z0-9._]+\/video\/[0-9]+"
		is_mobile_url = re.search(mobile_share_regex, url)
		if is_mobile_url:
			async with aiohttp.ClientSession() as session:
				async with session.get(url, allow_redirects=True) as sesh:
					url=str(sesh.url)
		is_website_url = re.search(website_share_regex, url)
		is_video_id = re.match("[0-9]+", url)
		if is_website_url:
			video_id = re.search("[0-9]+", url.split("/video/")[1])[0]
		if is_video_id:
			video_id = url
		if not is_website_url and not is_video_id:
			return False
		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(f"https://api2-19-h2.musical.ly/aweme/v1/aweme/detail/?aweme_id={video_id}&device_type=SM-G973N&region=US&media_type=4%22") as video_request:
					vv=await video_request.json()
					video_data=vv['aweme_detail']
			#self.api.debug.success(f"Found video data for video_id {video_id}")
			if raw:
				data = video_data
			else:
				data = await self.video_data_formatter(video_data)
		except Exception as e:
			print(e)
			return False
		return data

	async def video_data_formatter(self, video_data):
		data = {"download_urls": {}, "author": {}, "stats": {}, "music": {}}
		data["created_at_timestamp"] = video_data["create_time"]
		data["created_at"] = str(datetime.fromtimestamp(video_data["create_time"]))
		data["video_url"] = f'https://tiktok.com/@{video_data["author"]["unique_id"]}/video/{video_data["aweme_id"]}'
		data["video_id"] = video_data["aweme_id"]
		data["download_urls"]["no_watermark"] = video_data['video']['play_addr']['url_list'][0]
		data["download_urls"]["watermark"] = video_data["video"]["play_addr"]["url_list"][2]
		data["author"]["avatar_url"] = video_data["author"]["avatar_larger"]["url_list"][0].replace("webp", "jpeg")
		data["author"]["username"] = video_data["author"]["unique_id"]
		data["author"]["nickname"] = video_data["author"]["nickname"]
		data["author"]["sec_uid"] = video_data["author"]["sec_uid"]
		data["author"]["user_id"] = video_data["author"]["uid"]
		data["description"] = video_data["desc"]
		data["video_length"] = video_data["video"]["duration"]/1000
		data["stats"] = {
			"comment_count": video_data["statistics"]["comment_count"],
			"likes": video_data["statistics"]["digg_count"],
			"downloads": video_data["statistics"]["download_count"],
			"views": video_data["statistics"]["play_count"],
			"shares": video_data["statistics"]["share_count"],
		}
		data["music"] = {
			"music_id": video_data["music"]["mid"],
			"album": video_data["music"]["album"],
			"title": video_data["music"]["title"],
			"author": video_data["music"]["author"],
			"length": video_data["music"]["duration"] 
		}
		return data

	async def form(self, text):
		text=humanize.intword(text)
		if " thousand" in text:
			text=text.replace(" thousand", "k")
		if " million" in text:
			text=text.replace(" million", "m")
		return text

	async def embed(self, ctx, url):
		print(url)
		url = "https://tiktok-downloader-download-videos-without-watermark1.p.rapidapi.com/media-info/"
		querystring = {"link":f"{url}"}
		headers = {"X-RapidAPI-Key": "3cf4b96184msh8f9c91e898675b1p1e7ff2jsnefa6f2cc9859","X-RapidAPI-Host": "tiktok-downloader-download-videos-without-watermark1.p.rapidapi.com"}
		async with aiohttp.ClientSession() as session:
			async with session.request("GET",url=url,headers=headers,params=querystring) as response:
				data=await response.json()
				print(data)
			async with session.get(data['result']['video']['url_list'][0]) as r:
				f=io.BytesIO(await r.read())

		username=data['result']['aweme_detail']['author']['unique_id']
		stats=data['result']['aweme_detail']['statistics']
		likes=self.format(humanize.intword(int(stats['digg_count'])))
		comments=self.format(humanize.intword(int(stats['comment_count'])))
		views=self.format(humanize.intword(int(stats['play_count'])))
		song=data['result']['aweme_detail']['music']['title']
		author=data['result']['aweme_detail']['music']['author']
		embed = discord.Embed(color=0x303135).add_field(name=f"💬", value=f"{comments}", inline=True).add_field(name="👍",value=f"{likes}", inline=True).add_field(name="👀", value=f"{views}", inline=True).set_footer(text=f"🎵 {song} (by {author})")
		embed.description = f'**{data["result"]["aweme_detail"]["desc"]}**'
		embed.set_author(name="Tiktok by @"+username, icon_url="https://cdn.discordapp.com/emojis/1010602768660181012.png?size=256", url=url)
		await ctx.send(content=f"{ctx.author.mention} ",allowed_mentions=discord.AllowedMentions(users=True),file=discord.File(fp=f, filename="tiktok.mp4"), embed=embed)
				
	@commands.Cog.listener()
	async def on_message(self, message):
		if not self.bot.is_ready():
			return
		if message.author.bot:
			return
		if message.guild is None:
			return
		if message.content.startswith("blame ") or message.content.startswith("bleed "):
			return
		ctx=await self.bot.get_context(message)
		if message.guild.id != 918445509599977472:
			if message.guild.get_member(928394879200034856):
				return
		if message.content.startswith('rival ') and "tiktok" in message.content and await self.checkURL(message.content):
			regex = r"((http(s)?(\:\/\/))+(www\.)?([\w\-\.\/])*(\.[a-zA-Z]{2,3}\/?))[^\s\b\n|]*[^.,;:\?\!\@\^\$ -]"
			results=re.findall(regex, message.content)
			if results:
				if message.author.id not in self.bot.cache.donators:
					if message.guild.owner.id not in self.bot.cache.donators:
						return await util.send_error(ctx, f"only for **donators**")
				async with message.channel.typing():
					link = message.content.strip('rival ')
					await self.bot.db.execute("""INSERT INTO tiktok_usage VALUES(%s,%s) ON DUPLICATE KEY UPDATE amount = amount+1""", 0, 1)
					tiktok=await TikTokVideoResponse.from_url(self.session,ctx,link)
					if not tiktok.image_post_info:
						async with aiohttp.ClientSession() as session:
							async with session.get(tiktok.direct_download_urls[0]) as e:
								b=await e.read()
						embed=tiktok.make_embed(requester=message.author)
						return await ctx.send(content=f"{message.author.mention} ",allowed_mentions=discord.AllowedMentions(users=True),file=discord.File(fp=io.BytesIO(b), filename="rivaltiktok.mp4"),embed=embed)
					else:
						l=[i.display_image.url_list[0] for i in tiktok.image_post_info.images]
						embeds=tiktok.make_embeds(requester=message.author,urls=l)
						paginator = pg.Paginator(ctx.bot, embeds, ctx, invoker=ctx.author.id)
						if len(embeds) > 1:
							paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
							paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
							paginator.add_button('goto', label=None, emoji="<:filter:1000215652591734874>", style=discord.ButtonStyle.red)
							paginator.add_button('delete', emoji='<:stop:958054042637054013>', label=None, style=discord.ButtonStyle.red)
						await paginator.start()
		#elif await self.bot.db.execute("""SELECT * FROM autoembed WHERE guild_id = %s""", message.guild.id) and "tiktok" in message.content and await self.checkURL(message.content):
		elif message.guild.id in self.bot.cache.autoembed and "tiktok" in message.content and await self.checkURL(message.content):
			regex = r"((http(s)?(\:\/\/))+(www\.)?([\w\-\.\/])*(\.[a-zA-Z]{2,3}\/?))[^\s\b\n|]*[^.,;:\?\!\@\^\$ -]"
			results=re.findall(regex, message.content)
			if results:
				if message.author.id not in self.bot.cache.donators:
					if message.guild.owner.id not in self.bot.cache.donators:
						return await util.send_error(ctx, f"only for **donators**")
				async with message.channel.typing():
					m=message.content.split(" ")
					for a in m:
						if "tiktok.com" in a:
							link=a
					tiktok=await TikTokVideoResponse.from_url(self.session,ctx,link)
					await self.bot.db.execute("""INSERT INTO tiktok_usage VALUES(%s,%s) ON DUPLICATE KEY UPDATE amount = amount+1""", 0, 1)
					if not tiktok.image_post_info:
						async with aiohttp.ClientSession() as session:
							async with session.get(tiktok.direct_download_urls[0]) as e:
								b=await e.read()
						embed=tiktok.make_embed(requester=message.author)
						await ctx.send(content=f"{message.author.mention} ",allowed_mentions=discord.AllowedMentions(users=True),file=discord.File(fp=io.BytesIO(b), filename="rivaltiktok.mp4"),embed=embed)
					else:
						l=[i.display_image.url_list[0] for i in tiktok.image_post_info.images]
						embeds=tiktok.make_embeds(requester=message.author,urls=l)
						paginator = pg.Paginator(ctx.bot, embeds, ctx, invoker=ctx.author.id)
						if len(embeds) > 1:
							paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
							paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
							paginator.add_button('goto', label=None, emoji="<:filter:1000215652591734874>", style=discord.ButtonStyle.red)
							paginator.add_button('delete', emoji='<:stop:958054042637054013>', label=None, style=discord.ButtonStyle.red)
						await paginator.start()
					#await message.delete()

	@commands.command(name='fyp', description="gets a random tiktok video")
	async def fyp(self, ctx):
		fyp_videos = await tiktok.feed.for_you(count=1)
		videos = []
		for vid in fyp_videos:
			videos.append(vid)
		video = random.choice(videos)
		no_watermark_download = video["download_urls"]["no_watermark"]
		video_binary = await tiktok.video.get_video_binary(no_watermark_download)
		bytes_io = BytesIO(video_binary) 
		embed = discord.Embed(color=0x2f3136)
		if video.get('description'):
			des=video["description"]
			de=[]
			for d in des:
				if not d.startswith("#"):
					de.append(d)
			desc=" ".join(desc for desc in de)
		else:
			desc=""
		embed.description = f'[{desc}]({video["video_url"]})'
		embed.set_author(name="@"+video["author"]["username"], icon_url=video["author"]["avatar_url"])
		embed.set_footer(text=f"❤️ {await self.form(video['stats']['likes'])} 💬 {await self.form(video['stats']['comment_count'])} 🔗 {await self.form(video['stats']['shares'])} 👀 {await self.form(video['stats']['views'])}")
		await ctx.reply(file=discord.File(fp=bytes_io, filename="tiktok.mp4"), embed=embed, mention_author=False)

	@commands.command(name='igstory', aliases=['story'], description="show a instagram user's story", brief='username',usage='```Swift\nSyntax: !igstory <@username>\nExample: !igstory snoopdogg```')
	@commands.cooldown(1,300, commands.BucketType.member)
	@commands.has_permissions(embed_links=True)
	async def igstory(self, ctx, username):
		if ctx.author.id not in self.bot.owner_ids:
			return await util.send_error(ctx, f"disabled")
		st=await InstagramStoryResposne.from_url(self.session,ctx,username)
		embed=st.make_embed(ctx=ctx)
		if embed == None:
			return await util.send_error(ctx, f"unable to fetch **instagram story** of that user")
		if isinstance(embed, discord.Embed):
			async with aiohttp.ClientSession() as session:
				async with session.get(st.items[0].video_url) as r:
					img=discord.File(fp=io.BytesIO(await r.read()),filename='rivaligstory.mp4')
			return await ctx.send(embed=embed, file=img)
		elif isinstance(embed, dict):
			items=embed.get('items')
			emb=embed.get('embed')
			embeds=[]
			images=[]
			files=[]
			for i in items:
				#if i.is_video == True:
				async with aiohttp.ClientSession() as sesh:
					async with sesh.get(i.url) as f:
						files.append(discord.File(fp=io.BytesIO(await f.read()),filename=i.filename))
				#else:
					#images.append(i.url)
			# if len(images) > 1:
			# 	for i in images:
			# 		embeds.append(emb.set_image(url=i))
			# 	formatter=MySource(embeds, per_page=1)
			# 	menu = StoryPaginator(self.bot,formatter,files)
			# 	return await menu.start(ctx, files=files)
			if len(files) >= 1:
				await ctx.send(files=files,embed=emb)
			else:
				return await util.send_error(ctx, f"an error occurred please contact support")

	@igstory.error
	async def igstory_error(self, ctx, error):
		error = getattr(error, "original", error)
		if isinstance(error, commands.CommandOnCooldown):
			if ctx.author.id in ctx.bot.owner_ids:
				return await ctx.reinvoke()
			ratelimit = self.get_ratelimit(ctx.message)
			if ratelimit is None:
				pass
			else:
				return
			return await util.send_error(ctx, f"You are on cooldown. Please wait `{error.retry_after:.0f} seconds`")
		elif isinstance(error, commands.MissingPermissions):
			return await util.send_error(ctx, f"you are missing `embed links` permissions")


async def setup(bot):
	await bot.add_cog(conversion(bot))