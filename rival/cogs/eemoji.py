import discord, os, re, requests, json, asyncio, aiohttp, psutil, sys, base64, io,asyncpraw,random,secrets,unicodedata,contextlib,string,secrets,random
from modules import GetImage, util
from typing import TYPE_CHECKING, List, Optional, Tuple, Union, Dict
import typing
from modules import util, default, permissions, cache, queries, consts, exceptions, log, confirmation, search
import discord, unicodedata
from discord.ext import commands
from discord.ext.commands import errors
from io import BytesIO
import typing, functools
from PIL import Image
from discord.enums import StickerFormatType
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from discord.errors import HTTPException
import numpy as np
try:
	import cairosvg
	svg_convert='cairo'
except:
	svg_convert="wand"
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("agg")
plt.switch_backend("agg")
from discord import MessageType, PartialEmoji, app_commands, ui
from discord.enums import ButtonStyle
import button_paginator as pg
from discord.ext.commands import Context
from discord.ext.commands.errors import BadArgument
from discord import ui
from discord.ext import menus
from discord.message import Message
from discord.sticker import GuildSticker, StandardSticker, StickerItem
from modules.asynciterations import aiter

def get_message_stickers(message: Message) -> typing.List[StickerItem]:
	"""Returns a list of StickerItem found in a message."""
	stickers = message.stickers
	if len(stickers) == 0:
		raise BadArgument("I was not able to find any stickers in the message!")
	return stickers

def trans(myimage):
	img = Image.open(myimage)
	img = img.convert("RGBA")

	pixdata = img.load()

	width, height = img.size
	for y in range(height):
		for x in range(width):
			if pixdata[x, y][3] > 250:
				pixdata[x, y] = (255, 255, 255, 0)

	img.save(myimage, "PNG")

emoji_steal={}

class MySource(menus.ListPageSource):
	async def format_page(self, menu, entries):
		if self.get_max_pages() > 1:
			ee="entries"
		else:
			ee='entry'
		entries.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()} ({self.get_max_pages()} {ee})")
		return entries

class EmojiStealView(discord.ui.View,menus.MenuPages):
	def __init__(self, bot, source):
		super().__init__(timeout=60)
		self._source = source
		self.value = 0
		self.bot = bot
		self.current_page = 0
		self.ctx = None
		self.message = None

	async def start(self, ctx, *, channel=None, wait=False):
		# We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
		await self._source._prepare_once()
		self.ctx = ctx
		self.message = await self.send_initial_message(ctx, ctx.channel)

	async def on_timeout(self):
		await self.message.edit(view=None,embed=discord.Embed(description=f"{self.bot.no} {self.ctx.author.mention}: **cancelled** emoji steal", color=0xD6BCD0))
		if self.ctx.guild.id in emoji_steal:
			emoji_steal.pop(self.ctx.guild.id)
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
			await interaction.response.send_message(ephemeral=True, embed=discord.Embed(description=f"{self.bot.warn} <@!{interaction.user.id}>: **You aren't the author of this embed**", color=0xD6BCD0))
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

	@discord.ui.button(emoji='<:check:1021252651809259580>', style=discord.ButtonStyle.grey)
	async def confirm(self, button, interaction):
		e=emoji_steal[self.ctx.guild.id][self.current_page]
		name=e.get('name')
		e_id=e.get('id')
		url=e.get('url')
		if len(self.ctx.guild.emojis) == self.ctx.guild.emoji_limit:
			return await self.message.edit(view=None,embed=discord.Embed(color=0xD6BCD0,description=f"{self.bot.warn} {self.ctx.author.mention}: guild **emoji** limit reached"))
		f=await GetImage.download(url)
		with open(f,"rb") as e:
			img=e.read()
		emote=await self.ctx.guild.create_custom_emoji(name=name, image=img)
		await self.message.edit(view=None,embed=discord.Embed(description=f"{self.bot.yes} {self.ctx.author.mention}: **successfully** added {emote}", color=0xD6BCD0))
		emoji_steal.pop(self.ctx.guild.id)
		return

	@discord.ui.button(emoji='<:x_:1021273367749337089>', style=discord.ButtonStyle.grey)
	async def deny(self, button, interaction):
		emoji_steal.pop(self.ctx.guild.id)
		await self.message.edit(view=None,embed=discord.Embed(description=f"{self.bot.no} {self.ctx.author.mention}: **cancelled** emoji steal", color=0xD6BCD0))

class eemoji(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.max_emojis = 10
		self.add="<:plus:947812413267406848>"
		self.yes=self.bot.yes
		self.rem="<:rem:947812531509026916>"
		self.no=self.bot.no
		self.bad=0xD6BCD0#0xff6465
		self.color=0xD6BCD0
		self.value=None
		self.session = aiohttp.ClientSession()
		self.config = default.config()
		self.tasks = {}
		self.bot.uptime=self.bot.user.created_at
		self.ch='{self.bot.yes}'
		self.process = psutil.Process(os.getpid())
		self.error=0xD6BCD0#0xfaa61a
		self.warn=self.bot.warn
		self.last_posted: Dict[int, float] = {}
		self.EMOJI_REGEX = re.compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>")

	async def find(self, ctx):
		l=[]
		msgs=[message async for message in ctx.channel.history()]
		k=[]
		for msg in msgs:
			data = re.findall(r"<(a?):([a-zA-Z0-9_]+):([0-9]+)>", msg.content)
			for _a, emoji_name, emoji_id in data:
				animated = _a == "a"
				if animated:
					url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".gif"
				else:
					url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".png"
				name=emoji_name
				dic={}
				dic["name"]=f"{name}"
				dic['url']=f"{url}"
				dic['id']=f"{emoji_id}"
				if len(k) >= 10: return k
				k.append(f"{name} $vv {emoji_id} $vv {url}")
		return k

	def _get_emoji_url(self, emoji):
		emojiparts = emoji.replace("<","").replace(">","").split(":") if emoji else []
		if not len(emojiparts) == 3:
			# Emoji is likely a built-in like :)
			h = "-".join([hex(ord(x)).lower()[2:] for x in emoji])
			if any((len(x)<4 for x in h.split("-"))): return None # We got a built-in emoji, but it lacks proper hex setup
			return ("https://github.com/twitter/twemoji/raw/master/assets/72x72/{}.png".format(h),h)
			#return ("https://github.com/twitter/twemoji/raw/master/assets/480x480/{}.png".format(h),h)
		# Build a custom emoji object
		emoji_obj = discord.PartialEmoji(animated=len(emojiparts[0]) > 0, name=emojiparts[1], id=emojiparts[2])
		# Return the url
		return (emoji_obj.url,emoji_obj.name)

	async def _get_eemoji_url(self, emoji):
		chars = []
		name = []
		for char in emoji:
			chars.append(str(hex(ord(char)))[2:])
			try:
				name.append(unicodedata.name(char))
			except ValueError:
					# Sometimes occurs when the unicodedata library cannot
					# resolve the name, however the image still exists
				name.append("none")
		name = '_'.join(name)
		url = 'https://twemoji.maxcdn.com/2/svg/' + '-'.join(chars) + '.svg'
		async with self.session.get(url) as resp:
			if resp.status != 200:
				print('Emoji not found.')
				return
			img = await resp.read()

		kwargs = {'parent_width': 1024,
				  'parent_height': 1024}   

		task = functools.partial(self.generate, img, convert=True, **kwargs)
		task = self.bot.loop.run_in_executor(None, task)

		try:
			img = await asyncio.wait_for(task, timeout=15)
		except asyncio.TimeoutError:
			print("Image creation timed out.")
			return
		return img

	def _get_emoji_mention(self, emoji):
		return "<{}:{}:{}>".format("a" if emoji.animated else "",emoji.name,emoji.id)

	async def stealEmoji(self, interaction: discord.Interaction, message: discord.Message):
		raw_emojis = self.EMOJI_REGEX.findall(message.content)
		emojis = [
			PartialEmoji.with_state(self.bot._connection, animated=(e[0] == 'a'), name=e[1], id=e[2])
			for e in raw_emojis
		]
		if len(emojis) == 0:
			await interaction.response.send_message("there's no Emoji to steal :(", ephemeral=True)
		bot = self.bot

		class IndexSelector(ui.Modal, title="Which emoji?"):
			index = ui.Select(
				max_values=len(emojis),
				options=[
					discord.SelectOption(label=e.name, value=str(index), emoji=PartialEmoji.from_dict(e.to_dict()))
					for index, e in enumerate(emojis)
				],
			)

			async def on_submit(self, interaction: discord.Interaction):
				await interaction.response.send_message("i'll get right on that!", ephemeral=True)

				nerdiowo = message.guild
				for i in self.index.values:
					index = int(i)
					emoji = emojis[index]
					data = await emoji.read()
					uploaded = await nerdiowo.create_custom_emoji(name=emoji.name, image=data)
					await interaction.followup.send(f"{uploaded}", ephemeral=True)

		await interaction.response.send_modal(IndexSelector())

	async def eemoji_find(self, ctx):
		content=[]
		async for message in ctx.channel.history(limit=50):
			data = re.findall(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>", message.content)
			for _a, emoji_name, emoji_id in data:
				animated = _a == "a"
				if animated:
					url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".gif"
				else:
					url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".png"
				name=emoji_name
				dic={}
				dic["name"]=f"{name}"
				dic['url']=f"{url}"
				dic['id']=f"{emoji_id}"
							
				content.append(dic)
				return content

	@staticmethod
	def generate(img):
		# Designed to be run in executor to avoid blocking
		if svg_convert == "cairo":
			kwargs = {"parent_width": 1024, "parent_height": 1024}
			return io.BytesIO(cairosvg.svg2png(bytestring=img, **kwargs))
		elif svg_convert == "wand":
			with imgg(blob=img, format="svg", resolution=2160) as bob:
				return bob.make_blob("png")
		else:
			return io.BytesIO(img)

	@commands.command(name='transparent', aliases=['tr','tp'], description="make an image with a white background transparent", brief="image")
	async def transparent(self, ctx, image_url=None):
		if ctx.message.attachments:
			attachment=ctx.message.attachments[0].url
		else:
			if image_url:
				attachment=image_url
			else:
				return await util.send_error(ctx, f"please include an image or url")
		# async with self.bot.session.get(f"http://127.0.0.1:5000/?url={attachment}") as r:
		# 	img=await r.read()
		# img = io.BytesIO(img)
		# name='rivaltransparaent.png'
		# await ctx.reply(file=discord.File(img, name))
		await search.transparent(image=attachment, url=True)
		await ctx.reply(file=discord.File("no-bg.png"))	

	async def multi_emoji_steal(self, ctx):
		l=[]
		urls=[]
		if not ctx.author.nick:
			author_name=str(ctx.author)
		else:
			author_name=ctx.author.display_name
		async for message in ctx.channel.history(limit=100):
			print(message.content)
			data = re.findall(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>", message.content)
			print(data)
			for _a, emoji_name, emoji_id in data:
				#if len(data) > 1:
				dic={}
				url=f"https://cdn.discordapp.com/emojis/{emoji_id}.gif" if _a else f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
				if url not in urls:
					urls.append(f"https://cdn.discordapp.com/emojis/{emoji_id}.gif" if _a else f"https://cdn.discordapp.com/emojis/{emoji_id}.png")
					dic["name"]=emoji_name
					dic["id"]=emoji_id
					ee=self.bot.get_emoji(int(emoji_id))
					dic["url"]=f"https://cdn.discordapp.com/emojis/{emoji_id}.gif" if _a else f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
					try:
						if ee:
							if ee.guild.id != ctx.guild.id:
								l.append(dic)
						else:
							l.append(dic)
					except:
						l.append(dic)
		if l:
			if len(l) <= 1:
				dic=l[0]
				return [False,dic]
		else:
			return None
		emoji_steal[ctx.guild.id]=l
		embeds=[]
		async for i,e in aiter(enumerate(l, start=0)):
			bb=l[i]
			eee=self.bot.get_emoji(int(bb['id']))
			try:
				if eee:
					guild=eee.guild.name
				else:
					guild="Unknown"
			except:
				guild="Unknown"

			embeds.append(discord.Embed(title=bb['name'],color=0xD6BCD0).add_field(name='Emoji ID', value=f"`{bb['id']}`", inline=True).add_field(name='Guild', value=guild,inline=True).add_field(name="Image URL", value=f"[Here]({bb['url']})", inline=False).set_author(name=author_name, icon_url=ctx.author.display_avatar).set_image(url=bb['url']))
		return [True,embeds]

	@commands.command(name='steal', description='steal the most recent emoji or a specific emoji', brief='message / emoji[optional]', extras={'perms': 'manage emojis'})
	@commands.has_permissions(manage_emojis=True)
	async def ssteal(self, ctx: commands.Context, message: typing.Union[discord.Message, discord.PartialEmoji, discord.Emoji]=None):
		try:
			emoji_steal.pop(ctx.guild.id)
		except:
			pass
		if message:
			if len(ctx.guild.emojis) == ctx.guild.emoji_limit:
				return await ctx.reply(embed=discord.Embed(color=0xD6BCD0, description=f"{self.warn} {ctx.author.mention}: **guild has hit emoji limit**"))
			if isinstance(message, discord.PartialEmoji):
				emojii=message
				url = emojii
				name = emojii.name
				asset=url
				try:
					e = await ctx.guild.create_custom_emoji(name=name, image=await asset.read())
				except discord.HTTPException as e:
					return await ctx.send(embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.no} {ctx.author.mention}: **i couldn't create that emoji** {e}"))
				except:
					return await ctx.send(embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.no} {ctx.author.mention}: **unsupported image type**"))
				embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.yes} {ctx.author.mention}: **added emoji:** {e}")
				return await ctx.send(embed=embed)  

			if isinstance(message, discord.Emoji):
				emojii=message
				url = emojii
				name = emojii.name
				asset=url
				try:
					e = await ctx.guild.create_custom_emoji(name=name, image=await asset.read())
				except discord.HTTPException as e:
					return await ctx.send(embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.no} {ctx.author.mention}: **i couldn't create that emoji** {e}"))
				except:
					return await ctx.send(embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.no} {ctx.author.mention}: **unsupported image type**"))
				embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.yes} {ctx.author.mention}: **added emoji:** {e}")
				return await ctx.send(embed=embed)    
										  
			if isinstance(message, discord.Message):
				try:
					message=message.referenced
					msg = await ctx.fetch_message(message.id)
					text=msg.content
					data = re.findall(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>", text)
					for _a, emoji_name, emoji_id in data:
						animated = _a == "a"
						if animated:
							url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".gif"
						else:
							url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".png"
						emoteurl=url
						name=emoji_name
					#response=requests.get(emoteurl)
					#img=response.content
					f=await GetImage.download(emoteurl)
					with open(f,"rb") as e:
						img=e.read()
					emote=await ctx.guild.create_custom_emoji(name=name, image=img)
					await message.edit(embed=discord.Embed(description=f"{self.bot.yes} **added emoji:** {emote}", color=0xD6BCD0))
					GetImage.remove(f)
				except:
					return await ctx.send(embed=discord.Embed(title=self.bot.user.name, color=0x303135, description="invalid message id"))
				emb=discord.Embed(color=0xD6BCD0, description="No emoji to steal, you can also use a message ID by doing !steal <messageid>\n alternatively do !addmultiple <emojis>")
				return await ctx.send(embed=emb, delete_after=15)
		try:
			emojis=await self.multi_emoji_steal(ctx=ctx)
			if not emojis:
				return await util.send_no(ctx, f"no **emoji** to steal")
			if emojis[0] == False:
				emname=emojis[1].get("name")
				emurl=emojis[1].get("url")
				emid=emojis[1].get("id")
			else:
				emotes=emojis[1]
				formatter=MySource(emotes, per_page=1)
				menu = EmojiStealView(self.bot,formatter)
				return await menu.start(ctx)
		except Exception as e:
			print(e)
			return await ctx.reply(embed=discord.Embed(color=0xD6BCD0, description=f"{self.warn} {ctx.author.mention}: **no grabbable previously sent emoji detected**"))
		if emid:
			try:
				message = await ctx.send(embed=discord.Embed(title=emname, color=0xD6BCD0).add_field(name=f"Emoji ID", value=f"`{emid}`").add_field(name="Image URL", value=f"[Here]({emurl})").set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar).set_image(url=emurl).set_footer(text="Page 1/1 (1 entry)"))
			except:
				return await ctx.reply(embed=discord.Embed(color=0xD6BCD0, description=f"{self.warn} {ctx.author.mention}: **no grabbable previously sent emoji detected**"))
			confirmed:bool = await confirmation.confirm(self, ctx, message)
			if confirmed:
				#response=requests.get(emurl)
				#img = response.content
				f=await GetImage.download(emurl)
				with open(f,"rb") as e:
					img=e.read()
				emote=await ctx.guild.create_custom_emoji(name=emname, image=img)
				await message.edit(view=None, embed=discord.Embed(description=f"{self.bot.yes} **added emoji:** {emote}", color=0xD6BCD0))
				GetImage.remove(f)
			else:
				await message.edit(view=None, embed=discord.Embed(description=f"{self.bot.no} **cancelled emoji steal**", color=0xD6BCD0))

	async def emoji_find(self, ctx):
		content=[]
		async for message in ctx.channel.history(limit=500):
			data = re.findall(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>", message.content)
			for _a, emoji_name, emoji_id in data:
				animated = _a == "a"
				if animated:
					url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".gif"
				else:
					url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".png"
				name=emoji_name
				dic={}
				dic["name"]=f"{name}"
				dic['url']=f"{url}"
				dic['id']=f"{emoji_id}"
				return dic

	@commands.command(name='enlarge', aliases=['e','bigemoji'],description='enlarge an emoji', brief='emoji', usage='```Swift\nSyntax: !enlarge <emoji>\nExample: !enlarge :cat:```')
	async def enlarge(self, ctx, emoji: str = None):
		"""Post a large .png of an emoji"""
		if emoji is None:
			return await ctx.invoke(self.bot.get_command('eetnlarge'))
		else:
			convert = False
			if emoji[0] == "<":
				# custom Emoji
				try:
					name = emoji.split(":")[1]
				except IndexError:
					return await util.send_error(ctx, f"that isn't an emoji")
				emoji_name = emoji.split(":")[2][:-1]
				if emoji.split(":")[0] == "<a":
					# animated custom emoji
					url = f"https://cdn.discordapp.com/emojis/{emoji_name}.gif"
					name += ".gif"
				else:
					url = f"https://cdn.discordapp.com/emojis/{emoji_name}.png"
					name += ".png"
			else:
				chars = []
				name = []
				for char in emoji:
					chars.append(hex(ord(char))[2:])
					try:
						name.append(unicodedata.name(char))
					except ValueError:
						# Sometimes occurs when the unicodedata library cannot
						# resolve the name, however the image still exists
						name.append("none")
				name = "_".join(name) + ".png"
				if len(chars) == 2 and "fe0f" in chars:
					# remove variation-selector-16 so that the appropriate url can be built without it
					chars.remove("fe0f")
				if "20e3" in chars:
					# COMBINING ENCLOSING KEYCAP doesn't want to play nice either
					chars.remove("fe0f")
				if svg_convert is not None:
					url = "https://twemoji.maxcdn.com/2/svg/" + "-".join(chars) + ".svg"
					convert = True
				else:
					url = (
						"https://twemoji.maxcdn.com/2/72x72/" + "-".join(chars) + ".png"
					)
			async with self.session.get(url) as resp:
				if resp.status != 200:
					return await util.send_error(ctx, f"that isn't an emoji")
				img = await resp.read()
			if convert:
				task = functools.partial(eemoji.generate, img)
				task = self.bot.loop.run_in_executor(None, task)
				try:
					img = await asyncio.wait_for(task, timeout=15)
				except asyncio.TimeoutError:
					return await util.send_error(ctx, f"Image Creation Timed Out")
			else:
				img = io.BytesIO(img)
			await ctx.send(file=discord.File(img, name))

	@commands.command(name='eetnlarge', hidden=True,case_insensitive=True, description='enlarge a specific emoji or the most recent', extras={'perms': 'manage emojis'}, brief='message / emoji[optional]')
	@commands.guild_only()
	async def eetnlarge(self, ctx: commands.Context, message: Union[discord.Message, discord.Emoji, discord.PartialEmoji]=None):
		if message:
			if isinstance(message, discord.Emoji):
				emojii=message
				url = str(emojii.url)
				name = emojii.name
				embed=discord.Embed(title=self.bot.user.name, color=0xD6BCD0).set_image(url=url)
				embed.add_field(name=name, value=f"`{emojii.id}`")
				return await ctx.send(embed=embed)

			if isinstance(message, discord.PartialEmoji):
				emojii=message
				url = str(emojii.url)
				name = emojii.name
				embed=discord.Embed(title=self.bot.user.name, color=0xD6BCD0).set_image(url=url)
				embed.add_field(name=name, value=f"`{emojii.id}`")
				return await ctx.send(embed=embed)    
										  
			if isinstance(message, discord.Message):
				try:
					if message.referenced:
						message=message
					msg = await ctx.fetch_message(message.id)
					text=msg.content
					data = re.findall(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>", text)
					for _a, emoji_name, emoji_id in data:
						animated = _a == "a"
						if animated:
							url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".gif"
						else:
							url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".png"
						emoteurl=url
						name=emoji_name
					#response=requests.get(emoteurl)
					#img=response.content
					#img=await GetImage.download(emoteurl)
					await ctx.send(embed=discord.Embed(title=name, description=f"`{emoji_id}`", color=0xD6BCD0).set_image(url=emoteurl))
					#return GetImage.remove(img)
				except:
					return await ctx.send(embed=discord.Embed(title=self.bot.user.name, color=0x303135, description="invalid message id"))
				emb=discord.Embed(color=0xD6BCD0, description="No emoji to enlarge, you can also use a message ID by doing !enlarge <messageid>\n alternatively do !enlarge <emoji>")
				return await ctx.send(embed=emb, delete_after=15)
		try:
			emojis=await self.emoji_find(ctx=ctx)
			emname=emojis.get("name")
			emurl=emojis.get("url")
			emid=emojis.get("id")
		except AttributeError:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **no grabbable previously sent emoji detected**"))
		try:
			message = await ctx.send(embed=discord.Embed(title=self.bot.user.name, color=0xD6BCD0).add_field(name=f"{emname}", value=f"```{emid}```").set_image(url=emurl))
		except:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **no grabbable previously sent emoji detected**"))


	@commands.command(name='addmultiple', extras={'perms': 'manage emojis'}, aliases=['addemojis', 'addemoji'], description='adds passed emojis from emotes/urls with names (max of 10)', usage="```Swift\nSyntax: !addmultiple [emoji, url, attachment] [name]\nExample: !addmultiple link smile```",brief='emoji, name')
	@commands.has_permissions(manage_emojis=True)
	async def addmultiple(self, ctx, *, emoji = None, name = None):
		if not len(ctx.message.attachments) and emoji == name == None:
			return await util.send_command_help(ctx)
		# Let's find out if we have an attachment, emoji, or a url
		# Check attachments first - as they'll have priority
		if len(ctx.message.attachments):
			name = emoji
			emoji = " ".join([x.url for x in ctx.message.attachments])
			if name: # Add the name separated by a space
				emoji += " "+name
		# Now we split the emoji string, and walk it, looking for urls, emojis, and names
		emojis_to_add = []
		last_name = []
		for x in emoji.split():
			# Check for a url
			urls = util.get_urls(x)
			if len(urls):
				url = (urls[0], os.path.basename(urls[0]).split(".")[0])
			else:
				# Check for an emoji
				url = self._get_emoji_url(x)
				if not url:
					# Gotta be a part of the name - add it
					last_name.append(x)
					continue
			if len(emojis_to_add) and last_name:
				# Update the previous name if need be
				emojis_to_add[-1][1] = "".join([z for z in "_".join(last_name) if z.isalnum() or z == "_"])
			# We have a valid url or emoji here - let's make sure it's unique
			if not url[0] in [x[0] for x in emojis_to_add]:
				emojis_to_add.append([url[0],url[1]])
			# Reset last_name
			last_name = []
		if len(emojis_to_add) and last_name:
			# Update the final name if need be
			emojis_to_add[-1][1] = "".join([z for z in "_".join(last_name) if z.isalnum() or z == "_"])
		if not emojis_to_add: return await util.send_command_help(ctx)
		# Now we have a list of emojis and names
		added_emojis = []
		allowed = len(emojis_to_add) if len(emojis_to_add)<=self.max_emojis else self.max_emojis
		omitted = " ({} omitted, beyond the limit of {})".format(len(emojis_to_add)-self.max_emojis,self.max_emojis) if len(emojis_to_add)>self.max_emojis else ""
		message = await ctx.send(embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.yes} {ctx.author.mention}: " + "Adding {} emoji{}{}...".format(
			allowed,
			"" if allowed==1 else "s",
			omitted)))
		for emoji_to_add in emojis_to_add[:self.max_emojis]:
			# Let's try to download it
			emoji,e_name = emoji_to_add # Expand into the parts
			f = await GetImage.download(emoji)
			if not f: continue
			# Open the image file
			with open(f,"rb") as e:
				image = e.read()
			# Clean up
			GetImage.remove(f)
			if not e_name.replace("_",""): continue
			# Create the emoji and save it
			try: new_emoji = await ctx.guild.create_custom_emoji(name=e_name,image=image,roles=None,reason="Added by {}#{}".format(ctx.author.name,ctx.author.discriminator))
			except: continue
			added_emojis.append(new_emoji)
		msg = "Created {} of {} emoji{}{}.".format(
			len(added_emojis),
			allowed,"" if allowed==1 else "s",
			omitted
			)
		if len(added_emojis):
			msg += "\n\n"
			emoji_text = ["{} - `:{}:`".format(self._get_emoji_mention(x),x.name) for x in added_emojis]
			msg += "\n".join(emoji_text)
		await message.edit(embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.yes} {ctx.author.mention}: "+msg))

	@commands.command(name='delemoji', aliases=["delemote"], description="deletes an emoji", usage="```Swift\nSyntax: !delmoji <emojis>\nExample: !delmoji :smile: :smile2:```",brief='emojis', extras={'perms': 'manage emojis'})
	@commands.has_permissions(manage_emojis=True)
	async def delemoji(self, ctx, emoji: commands.Greedy[discord.Emoji]):
		if len(emoji) > 10:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **max of 10 emojis**"))
		emojis=[]
		num=0
		failed=0
		for emoji in emoji:
			if emoji in list(ctx.guild.emojis):
				emojis.append(emoji.name)
				num+=1
				await emoji.delete()
			else:
				failed+=1
				pass
		if emojis:
			if failed==0:
				embed = discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: **deleted emojis:** \n"+"\n".join(emojis for emojis in emojis), color=0xD6BCD0)
				await ctx.reply(embed=embed)
			else:
				embed = discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: "+"**deleted %s emojis, but failed to delete %S**"% (num, failed), color=0xD6BCD0)
				await ctx.reply(embed=embed)
		else:
			embed = discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: could not find those emojis", color=self.bad)
			await ctx.reply(embed=embed)


	@commands.command(name='editemoji', aliases=["editemote"], description='edits the name of an emoji', usage="```Swift\nSyntax: !editemoji <emoji> <name>\nExample: !editemoji :smile: ssmile```",extras={'perms': 'manage emojis'}, brief='emoji, name')
	@commands.has_permissions(manage_emojis=True)
	async def editemoji(self, ctx, emoji: discord.Emoji, new_name):
		emoji_name = emoji.name
		if emoji.animated:
			emote=f"<a:{emoji.name}:{emoji.id}>"
		else:
			emote=f"<:{emoji.name}:{emoji.id}>"
		if emoji in list(ctx.guild.emojis):
			await emoji.edit(name=new_name)
			embed = discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: {emoji} **renamed to** `{new_name}`", color=0xD6BCD0)
			await ctx.reply(embed=embed)
		else:
			embed = discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: could not find that emoji", color=self.bad)
			await ctx.reply(embed=embed)

	@commands.group(name='emoji', aliases=['emojis', 'emote', 'emotes'], description="emoji editing commands")
	async def emoji(self, ctx):
		if ctx.invoked_subcommand == None:
			return await util.command_group_help(ctx)

	@emoji.command(name='add', aliases=['addmultiple', 'a', 'create', 'c'], description='adds passed emojis from emotes/urls with names (max of 10)', brief='emoji, name', usage="```Swift\nSyntax: !emoji add [emoji, url, attachment] [name]\nExample: !emoji add link smile```",extras={'perms': 'manage emojis'})
	@commands.has_permissions(manage_emojis=True)
	async def aaadd(self, ctx, *, emoji = None, name = None):
		if len(ctx.guild.emojis) == ctx.guild.emoji_limit:
			return await util.send_error(ctx, f"guild emoji limit reached")
		if not ctx.author.guild_permissions.manage_emojis:
			raise commands.MissingPermissions(["MANAGE EMOJIS"])
		if not len(ctx.message.attachments):
			if not emoji:
				if not name:
					return await ctx.invoke(self.bot.get_command('steal'))
		if not len(ctx.message.attachments) and emoji == name == None:
			#return await ctx.send(embed=discord.Embed(color=0x303135, description="Usage: `{}addmultiple [emoji, url, attachment] [name]`".format(ctx.prefix)))
			#return await util.command_group_help(ctx)
			return await ctx.invoke(self.bot.get_command('steal'))
		# Let's find out if we have an attachment, emoji, or a url
		# Check attachments first - as they'll have priority
		if len(ctx.message.attachments):
			name = emoji
			emoji = " ".join([x.url for x in ctx.message.attachments])
			if name: # Add the name separated by a space
				emoji += " "+name
		# Now we split the emoji string, and walk it, looking for urls, emojis, and names
		emojis_to_add = []
		last_name = []
		for x in emoji.split():
			# Check for a url
			urls = util.get_urls(x)
			if len(urls):
				url = (urls[0], os.path.basename(urls[0]).split(".")[0])
			else:
				# Check for an emoji
				url = self._get_emoji_url(x)
				if not url:
					# Gotta be a part of the name - add it
					last_name.append(x)
					continue
			if len(emojis_to_add) and last_name:
				# Update the previous name if need be
				emojis_to_add[-1][1] = "".join([z for z in "_".join(last_name) if z.isalnum() or z == "_"])
			# We have a valid url or emoji here - let's make sure it's unique
			if not url[0] in [x[0] for x in emojis_to_add]:
				emojis_to_add.append([url[0],url[1]])
			# Reset last_name
			last_name = []
		if len(emojis_to_add) and last_name:
			# Update the final name if need be
			emojis_to_add[-1][1] = "".join([z for z in "_".join(last_name) if z.isalnum() or z == "_"])
		if not emojis_to_add: return await util.command_group_help(ctx) #return await ctx.send(embed=discord.Embed(color=0x303135, description="Usage: `{}addmultiple [emoji, url, attachment] [name]`".format(ctx.prefix)))
		# Now we have a list of emojis and names
		added_emojis = []
		allowed = len(emojis_to_add) if len(emojis_to_add)<=self.max_emojis else self.max_emojis
		omitted = " ({} omitted, beyond the limit of {})".format(len(emojis_to_add)-self.max_emojis,self.max_emojis) if len(emojis_to_add)>self.max_emojis else ""
		message = await ctx.send(embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.yes} {ctx.author.mention}: " + "Adding {} emoji{}{}...".format(
			allowed,
			"" if allowed==1 else "s",
			omitted)))
		for emoji_to_add in emojis_to_add[:self.max_emojis]:
			# Let's try to download it
			emoji,e_name = emoji_to_add # Expand into the parts
			f = await GetImage.download(emoji)
			if not f: continue
			# Open the image file
			with open(f,"rb") as e:
				image = e.read()
			# Clean up
			GetImage.remove(f)
			if not e_name.replace("_",""): continue
			# Create the emoji and save it
			try: new_emoji = await ctx.guild.create_custom_emoji(name=e_name,image=image,roles=None,reason="Added by {}#{}".format(ctx.author.name,ctx.author.discriminator))
			except: continue
			added_emojis.append(new_emoji)
		msg = "Created {} of {} emoji{}{}.".format(
			len(added_emojis),
			allowed,"" if allowed==1 else "s",
			omitted
			)
		if len(added_emojis):
			msg += "\n\n"
			emoji_text = ["{} - `:{}:`".format(self._get_emoji_mention(x),x.name) for x in added_emojis]
			msg += "\n".join(emoji_text)
		await message.edit(embed=discord.Embed(color=0xD6BCD0, description=f"{self.bot.yes} {ctx.author.mention}: "+msg))

	@emoji.command(name='delete', aliases=['del', 'd', 'remove', 'r'], description="deletes emojis passed (max of 10)", brief='emojis', usage="```Swift\nSyntax: !emoji delete <emojis>\nExample: !emoji delete :smile1: :smile2:```",extras={'perms': 'manage emojis'})
	@commands.has_permissions(manage_emojis=True)
	async def delete(self, ctx, emoji: commands.Greedy[discord.Emoji]):
		if not ctx.author.guild_permissions.manage_emojis:
			raise commands.MissingPermissions(["MANAGE EMOJIS"])
		if len(emoji) > 10:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **max of 10 emojis**"))
		emojis=[]
		num=0
		failed=0
		for emoji in emoji:
			if emoji in list(ctx.guild.emojis):
				emojis.append(emoji.name)
				num+=1
				await emoji.delete()
			else:
				failed+=1
				pass
		if emojis:
			if failed==0:
				embed = discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: **deleted emojis:** \n"+"\n".join(emojis for emojis in emojis), color=0xD6BCD0)
				await ctx.reply(embed=embed)
			else:
				embed = discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: "+"**deleted %s emojis, but failed to delete %S**"% (num, failed), color=0xD6BCD0)
				await ctx.reply(embed=embed)
		else:
			embed = discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: could not find those emojis", color=self.bad)
			await ctx.reply(embed=embed)

	@emoji.command(name='edit', aliases=['rename', 'change'], description="edits the name of an emoji", usage="```Swift\nSyntax: !emoji edit <emoji> <name>\nExample: !emoji edit :smile1: smile2```",extras={'perms': 'manage emojis'}, brief='emoji, name')
	@commands.has_permissions(manage_emojis=True)
	async def edit(self, ctx, emoji: discord.Emoji, new_name):
		if not ctx.author.guild_permissions.manage_emojis:
			raise commands.MissingPermissions(["MANAGE EMOJIS"])
		emoji_name = emoji.name
		if emoji.animated:
			emote=f"<a:{emoji.name}:{emoji.id}>"
		else:
			emote=f"<:{emoji.name}:{emoji.id}>"
		if emoji in list(ctx.guild.emojis):
			await emoji.edit(name=new_name)
			embed = discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: {emoji} **renamed to** `{new_name}`", color=0xD6BCD0)
			await ctx.reply(embed=embed)
		else:
			embed = discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: could not find that emoji", color=self.bad)
			await ctx.reply(embed=embed)

	@emoji.command(name='enlarge', aliases=['e','bigemoji'],description='enlarge an emoji', brief='emoji', usage='```Swift\nSyntax: !emoji enlarge <emoji>\nExample: !emoji enlarge :cat:```')
	async def emoji_enlarge(self, ctx, emoji: str = None):
		"""Post a large .png of an emoji"""
		if emoji is None:
			return await ctx.invoke(self.bot.get_command('eetnlarge'))
		else:
			convert = False
			if emoji[0] == "<":
				# custom Emoji
				try:
					name = emoji.split(":")[1]
				except IndexError:
					return await util.send_error(ctx, f"that isn't an emoji")
				emoji_name = emoji.split(":")[2][:-1]
				if emoji.split(":")[0] == "<a":
					# animated custom emoji
					url = f"https://cdn.discordapp.com/emojis/{emoji_name}.gif"
					name += ".gif"
				else:
					url = f"https://cdn.discordapp.com/emojis/{emoji_name}.png"
					name += ".png"
			else:
				chars = []
				name = []
				for char in emoji:
					chars.append(hex(ord(char))[2:])
					try:
						name.append(unicodedata.name(char))
					except ValueError:
						# Sometimes occurs when the unicodedata library cannot
						# resolve the name, however the image still exists
						name.append("none")
				name = "_".join(name) + ".png"
				if len(chars) == 2 and "fe0f" in chars:
					# remove variation-selector-16 so that the appropriate url can be built without it
					chars.remove("fe0f")
				if "20e3" in chars:
					# COMBINING ENCLOSING KEYCAP doesn't want to play nice either
					chars.remove("fe0f")
				if svg_convert is not None:
					url = "https://twemoji.maxcdn.com/2/svg/" + "-".join(chars) + ".svg"
					convert = True
				else:
					url = (
						"https://twemoji.maxcdn.com/2/72x72/" + "-".join(chars) + ".png"
					)
			async with self.session.get(url) as resp:
				if resp.status != 200:
					return await util.send_error(ctx, f"that isn't an emoji")
				img = await resp.read()
			if convert:
				task = functools.partial(eemoji.generate, img)
				task = self.bot.loop.run_in_executor(None, task)
				try:
					img = await asyncio.wait_for(task, timeout=15)
				except asyncio.TimeoutError:
					return await util.send_error(ctx, f"Image Creation Timed Out")
			else:
				img = io.BytesIO(img)
			await ctx.send(file=discord.File(img, name))

	@commands.group(name='sticker', description='sticker editing commands')
	@commands.has_permissions(manage_emojis=True)
	async def sticker(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@sticker.command(name='add', aliases=['create','a','c'], description='add most recent sticker or sticker in a specific message', brief='message[optional]', extras={'perms': 'manage emojis'})
	@commands.has_permissions(manage_emojis=True)
	async def add(self, ctx: Context, message: typing.Union[discord.Message, str]=None, *, name:str=None):
		if len(ctx.guild.stickers) == ctx.guild.sticker_limit:
			return await util.send_error(ctx, f"guild sticker limit reached")
		if ctx.message.attachments:
			if not message: message=''.join((secrets.choice(string.ascii_letters) for i in range(6)))
			try:
				img=await GetImage.download(ctx.message.attachments[0].url)
				added_sticker: GuildSticker = await ctx.guild.create_sticker(name=message, description="sticker", emoji="🥛", file=discord.File(img),reason=f"{ctx.author} added sticker")
				return await util.send_good(ctx, f"added sticker named [{message}]({ctx.message.attachments[0].url})")
			except:
				return await util.send_error(ctx, f"image to large")
		if ctx.message.reference:
			message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
		if isinstance(message,str):
			if message:
				if message.startswith("https://"):
					try:
						async with aiohttp.ClientSession() as session:
							async with session.get(message) as r:
								img=BytesIO(await r.read())
								refcode=''.join((secrets.choice(string.ascii_letters) for i in range(6)))
								name=name or f"rivalsticker{refcode}"
								added_sticker: GuildSticker = await ctx.guild.create_sticker(name=name, description="sticker", emoji="🥛", file=discord.File(img),reason=f"Stolen by {ctx.author.name}#{ctx.author.discriminator}")
								return await util.send_good(ctx, f"sticker [{added_sticker.name}]({added_sticker.url}) has been added!")
					except:
						return await util.send_error(ctx, f"make sure it is a gif, jpeg or png file or url")
		message = message or ctx.message
		sticker_items = get_message_stickers(message)
		sticker_item = sticker_items[0]
		sticker = await sticker_item.fetch()
		if isinstance(sticker, StandardSticker):
			raise BadArgument("Specified sticker is already in-built. It'd be dumb to add it again.")
		b = BytesIO(await sticker.read())
		try:
			# Returns bad request, possible problem with the library, henceforth, the command is disabled
			added_sticker: GuildSticker = await ctx.guild.create_sticker(
				name=sticker.name, description="sticker", emoji="🥛", file=discord.File(b),
				reason=f"Stolen by {ctx.author.name}#{ctx.author.discriminator}"
			)
			b.close()
		except HTTPException as exc:
			if exc.code == 30039:
				return await ctx.reply(embed=error("The server sticker list is full. I can't add more!"))
			raise exc
		else:
			return await util.send_good(ctx, f"sticker [{added_sticker.name}]({added_sticker.url}) has been added!")

	@sticker.command(name='delete', aliases=['del','d','remove','rem','r'],description="remove a sticker", extras={'perms':'manage emojis'})
	@commands.has_permissions(manage_emojis=True)
	async def sticker_delete(self, ctx, message: typing.Optional[Message]):
		if ctx.message.reference:
			message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
		message = message or ctx.message

		sticker_items = get_message_stickers(message)
		sticker_item = sticker_items[0]

		sticker = await sticker_item.fetch()
		name=sticker.name
		if sticker.guild == ctx.guild:
			await sticker.delete()
			return await util.send_good(ctx, f"successfully deleted {name}")
		else:
			return await util.send_error(ctx, f"sticker not found in guild stickers")


	@sticker.command(name='steal', aliases=['recent'], extras={'perms': 'manage emojis'}, description='steal most recent sent sticker')
	@commands.has_permissions(manage_emojis=True)
	async def steal(self, ctx):
		if len(ctx.guild.stickers) == ctx.guild.sticker_limit:
			return await util.send_error(ctx, f"guild sticker limit reached")
		dic=await self.fetch_stickers(ctx=ctx)
		emname=dic.get("name")
		emurl=dic.get("url")
		emid=dic.get("id")
		try:
			message = await ctx.send(embed=discord.Embed(title=emname, color=0xD6BCD0).add_field(name=f"Sticker ID", value=f"`{emid}`").add_field(name="Image URL", value=f"[Here]({emurl})").set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar).set_image(url=emurl).set_footer(text="react to steal"))
		except:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **no grabbable previously sent sticker detected**"))
		confirmed:bool = await confirmation.confirm(self, ctx, message)
		if confirmed:
			#response=requests.get(emurl)
			#img = response.content
			b=await GetImage.download(emurl)
			#b = BytesIO(img)
			try:
				added_sticker: GuildSticker = await ctx.guild.create_sticker(name=emname, description="sticker", emoji="🥛", file=discord.File(b),reason=f"Stolen by {ctx.author.name}#{ctx.author.discriminator}")
				#b.close()
				await message.edit(view=None, embed=discord.Embed(description=f"{self.bot.yes} **added sticker [{emname}]({emurl})**", color=0xD6BCD0).set_image(url=added_sticker.url))
				GetImage.remove(b)
			except:
				return await message.edit(view=None, embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **guild max sticker limit reached**"))
		else:
			await message.edit(view=None, embed=discord.Embed(description=f"{self.bot.no} **cancelled sticker steal**", color=0xD6BCD0))

	async def fetch_stickers(self, ctx):
		dic={}
		async for message in ctx.channel.history(limit=50):
			if message.stickers:
				for sticker in message.stickers:
					dic['name']=sticker.name
					dic['url']=sticker.url
					dic['id']=sticker.id
					return dic

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def mmove(self, ctx:commands.Context, origin: discord.VoiceChannel, destination:discord.VoiceChannel):
		if origin.members:
			if origin != destination:
				moved = []
				for member in origin.members:
					await member.edit(voice_channel=destination, reason=f"Massmoved by {ctx.author}")
					moved.append(member)
				embed = discord.Embed(title=f"***{self.bot.user.name}#{self.bot.user.discriminator}***", description=f"*Moved {len(moved)} members from {origin.name} to {destination.name}*")
				await ctx.send(embed=embed)
			else:
				await ctx.send(f"You can't move people to the same voice channel that they're already in!")
		else:
			await ctx.send(f"{origin.name} is empty!")

	@commands.command(name='move', description='move all members from a members channel to your channel', extras={'perms': 'administrator'}, usage="```Swift\nSyntax: !move <member>\nExample: !move @cop#000```",brief='member')
	@commands.has_permissions(administrator=True)
	async def move(self, ctx:commands.Context, member: discord.Member):
		origin=member.voice.channel
		destination=ctx.author.voice.channel
		if origin.members:
			if origin != destination:
				moved = []
				for member in origin.members:
					await member.edit(voice_channel=destination, reason=f"Massmoved by {ctx.author}")
					moved.append(member)
				embed = discord.Embed(title=f"***{self.bot.user.name}#{self.bot.user.discriminator}***", description=f"*Moved {len(moved)} members from {origin.name} to {destination.name}*")
				await ctx.send(embed=embed)
			else:
				await ctx.send(f"You can't move people to the same voice channel that they're already in!")
		else:
			await ctx.send(f"{origin.name} is empty!")


async def setup(bot):
	await bot.add_cog(eemoji(bot))