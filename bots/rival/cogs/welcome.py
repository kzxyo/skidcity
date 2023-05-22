import discord
from discord.ext import commands

from modules import emojis, exceptions, util
import typing
import datetime
import humanfriendly
import tweepy
import random, re, asyncio, aiohttp
from discord import ui
from datetime import timedelta
from typing import Union
from datetime import datetime
from io import BytesIO
from discord.ext import menus

from discord.ext.commands import errors
import psutil
import requests, os, ast, inspect
from bs4 import BeautifulSoup
from typing import Union
import time,json
from modules.MyMenuPages import MyMenuPages, MySource
from modules import exceptions, util, consts, queries, http, default, permissions, log
logger = log.get_logger(__name__)


async def not_server_owner_msg(ctx, text):
	if text:
		text=text
	else:
		text="Guild Owner"
	embed = discord.Embed(
		description=f"<:warn:940732267406454845> {ctx.author.mention}: this command can **only** be used by the `{text}`",
		colour=0xfaa61a,
	)
	return embed

class welcome(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.add="<:plus:947812413267406848>"
		self.yes="<:yes:940723483204255794>"
		self.good=0xa5eb78
		self.rem="<:rem:947812531509026916>"
		self.no="<:no:940723951947120650>"
		self.bad=0xff6465
		self.color=0x303135
		self.ch='<:yes:940723483204255794>'
		self.error=0xfaa61a
		self.warn='<:warn:940732267406454845>'

	@commands.Cog.listener()
	async def on_member_join(self, member):
		data=await self.bot.db.execute("""SELECT * FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
		if not data:
			return
		welcchannel=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
		channel=self.bot.get_channel(welcchannel)
		if not channel:
			return
		msg=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", member.guild.id, one_value=True)
		if "{server}" in str(msg):
			msg = msg.replace("{server}", member.guild.name)
		if "{server.count}" in msg:
			msg = msg.replace("{server.count}", str(len([m for m in member.guild.members])))
		if "{mention}" in msg:
			msg = msg.replace("{mention}", member.mention)
		if "{user.name}" in msg:
			msg = msg.replace("{user.name}", member.name)
		if "{user}" in msg:
			msg = msg.replace("{user}", str(member))
		if "{user.tag}" in msg:
			usertag=f"{member.name}#{member.discriminator}"
			msg = msg.replace("{user.tag}", usertag)
		embed=await self.bot.db.execute("""SELECT embed FROM wlcembed WHERE guild_id = %s""", member.guild.id, one_value=True)
		if embed == 0:
			await channel.send(msg)
		else:
			pass
		data = await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
		if not data:
			return await member.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {member.author.mention}: **welcomer not setup**"))
		author=await self.bot.db.execute("""SELECT author FROM wlcauthor WHERE guild_id = %s""", member.guild.id, one_value=True)
		footer=await self.bot.db.execute("""SELECT footer FROM wlcfooter WHERE guild_id = %s""", member.guild.id, one_value=True)
		channel_id=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", member.guild.id, one_value=True)
		embed=await self.bot.db.execute("""SELECT embed FROM wlcembed WHERE guild_id = %s""", member.guild.id, one_value=True)
		message=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", member.guild.id, one_value=True)
		desc=await self.bot.db.execute("""SELECT description FROM wlcdesc WHERE guild_id = %s""", member.guild.id, one_value=True)
		title=await self.bot.db.execute("""SELECT title FROM wlctitle WHERE guild_id = %s""", member.guild.id, one_value=True)
		thumb=await self.bot.db.execute("""SELECT thumb FROM wlcthumb WHERE guild_id = %s""", member.guild.id, one_value=True)
		image=await self.bot.db.execute("""SELECT image FROM wlcimage WHERE guild_id = %s""", member.guild.id, one_value=True)
		if channel_id:
			channel_id=channel_id
		if message:
			message=message
		else:
			message=None
		if title:
			title=title
		else:
			title=None
		if desc:
			description=desc
		else:
			description=None
		color=self.color
		if author:
			author=author
		else:
			author=None
		if footer:
			footer=footer
		else:
			footer=None
		if image:
			image=image
		else:
			image=None
		if thumb:
			thumb=thumb
		else:
			thumb=None
		if "{server}" in content:
			content = content.replace("{server}", member.guild.name)
		if "{server.count}" in content:
			content = content.replace("{server.count}", str(len([m for m in member.guild.members])))
		if "{mention}" in content:
			content = content.replace("{mention}", f"<@!{member.id}>")
		if "{user.name}" in content:
			content = content.replace("{user.name}", member.name)
		if "{user}" in content:
			content = content.replace("{user}", str(member))
		if "{user.tag}" in content:
			usertag=f"{member.name}#{member.discriminator}"
			content = content.replace("{user.tag}", usertag)
		if "{server}" in description:
			description = description.replace("{server}", member.guild.name)
		if "{server.count}" in description:
			description = description.replace("{server.count}", str(len([m for m in member.guild.members])))
		if "{mention}" in msg:
			description = description.replace("{mention}", str(member.mention))
		if "{user.name}" in msg:
			description = description.replace("{user.name}", member.name)
		if "{user}" in msg:
			description = description.replace("{user}", str(member))
		if "{user.tag}" in description:
			usertag=f"{member.name}#{member.discriminator}"
			description = description.replace("{user.tag}", usertag)
		if title == None:
			embed=discord.Embed(description=description, color=0x303135)
		#
		if title != None:
			if "{user.tag}" in title:
				usertag=f"{member.name}#{member.discriminator}"
				title = title.replace("{user.tag}", usertag)
			if "{server}" in title:
				title = title.replace("{server}", member.guild.name)
			if "{server.count}" in title:
				title = title.replace("{server.count}", str(len([m for m in member.guild.members])))
			if "{mention}" in title:
				title = title.replace("{mention}", str(member.mention))
			if "{user.name}" in title:
				title = title.replace("{user.name}", member.name)
			if "{user}" in title:
				title = title.replace("{user}", str(member))
			if "{user.tag}" in title:
				usertag=f"{member.name}#{member.discriminator}"
				title = title.replace("{user.tag}", usertag)
			embed=discord.Embed(title=title, description=description, color=0x303135)
		#
		if author != None:
			if "{user.tag}" in author:
				usertag=f"{member.name}#{member.discriminator}"
				author = author.replace("{user.tag}", usertag)
			if "{server}" in author:
				author = author.replace("{server}", member.guild.name)
			if "{server.count}" in author:
				author = author.replace("{server.count}", str(len([m for m in member.guild.members])))
			if "{mention}" in author:
				author = author.replace("{mention}", str(member.mention))
			if "{user.name}" in author:
				author = author.replace("{user.name}", member.name)
			if "{user}" in author:
				author = author.replace("{user}", str(member))
			if "{user.tag}" in author:
				usertag=f"{member.name}#{member.discriminator}"
				author = author.replace("{user.tag}", usertag)
			embed.set_author(name=author)
		if footer != None:
			if "{user.tag}" in footer:
				usertag=f"{member.name}#{member.discriminator}"
				footer = footer.replace("{user.tag}", usertag)
			if "{server}" in footer:
				footer = footer.replace("{server}", member.guild.name)
			if "{server.count}" in footer:
				footer = footer.replace("{server.count}", str(len([m for m in member.guild.members])))
			if "{mention}" in footer:
				footer = footer.replace("{mention}", str(member.mention))
			if "{user.name}" in footer:
				footer = footer.replace("{user.name}", member.name)
			if "{user}" in footer:
				footer = footer.replace("{user}", str(member))
			if "{user.tag}" in footer:
				usertag=f"{member.name}#{member.discriminator}"
				footer = footer.replace("{user.tag}", usertag)
			embed.set_footer(text=footer)
		if thumb != None:
			if "{av}" in thumb:
				thumb=thumb.replace("{av}", str(member.display_avatar.url))
			if "{icon}" in thumb:
				thumb=thumb.replace("{icon}", str(member.guild.icon))
			embed.set_thumbnail(url=thumb)
		if image != None:
			if "{av}" in image:
				image=image.replace("{av}", str(member.display_avatar.url))
			if "{icon}" in image:
				image=image.replace("{icon}", str(member.guild.icon))
			embed.set_image(url=image)
		await channel.send(content=content, embed=embed)

	@commands.group(name="welcome", aliases=['welc', 'wlc'])
	@commands.has_permissions(administrator=True)
	async def welcome(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			await ctx.send(embed=discord.Embed(title="rival", description="!welcome <subcommand>\n ***valid subcommands are:***\n\n```message, channel, embed, title, description, image, thumbnail, footer, author, clear, config, test, channel```\n\n ***syntax:***\n {mention} - mentions user\n{server} - guild name\n{user} - username\n{user.tag} - user#discrim\n{server.count} - member count\n{av} - user av\n{icon} - server icon"))

	@welcome.command(name="config", aliases=["cfg", "settings"])
	async def config(self, ctx: commands.Context):
		enabled_true = "<:enabled:926194469840236605>"
		enabled_false = "<:disabled:926194368631697489>"
		data = await self.bot.db.execute("""SELECT channel_id, message, embed, title, description, color, author, footer, image, thumb FROM welcome WHERE guild_id = %s""", ctx.guild.id)
		if not data:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **welcomer not setup**"))
		
		author=await self.bot.db.execute("""SELECT author FROM wlcauthor WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		footer=await self.bot.db.execute("""SELECT footer FROM wlcfooter WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		channel_id=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		embed=await self.bot.db.execute("""SELECT embed FROM wlcembed WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		message=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		desc=await self.bot.db.execute("""SELECT description FROM wlcdesc WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		title=await self.bot.db.execute("""SELECT title FROM wlctitle WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		thumb=await self.bot.db.execute("""SELECT thumb FROM wlcthumb WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		image=await self.bot.db.execute("""SELECT image FROM wlcimage WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if channel_id:
			channel_id=channel_id
		if message:
			message=message
		else:
			message=None
		if title:
			title=title
		else:
			title=None
		if description:
			description=description
		else:
			description=None
		color=self.color
		if author:
			author=author
		else:
			author=None
		if footer:
			footer=footer
		else:
			footer=None
		if image:
			image=image
		else:
			image=None
		if thumb:
			thumb=thumb
		else:
			thumb=None
		if embed==1:
			embed=f"{enabled_true}"
		else:
			embed=f"{enabled_false}"
		try:
			channel=self.bot.get_channel(channel_id)
			channel=channel.mention
		except:
			channel=None
			pass
		embed=discord.Embed(title=f"***{ctx.guild.name}'s Welcome Settings***", color=0x303135)
		embed.add_field(name="***Channel:***", value="• {}".format(channel), inline=True)
		embed.add_field(name="***Message:***", value="• {}".format(message), inline=True)
		embed.add_field(name="***Embed:***", value="• {}".format(embed), inline=True)
		embed.add_field(name="***Title:***", value="• {}".format(title), inline=True)
		try:
			embed.set_thumbnail(url=ctx.guild.icon)
		except:
			pass
		embed.add_field(name="***Description:***", value="• {}".format(description), inline=True)
		embed.add_field(name="***Image:***", value="• {}".format(image), inline=True)
		embed.add_field(name="***ThumbNail:***", value="• {}".format(thumb), inline=True)
		embed.add_field(name="***Author:***", value="• {}".format(author), inline=True)
		embed.add_field(name="***Footer:***", value="• {}".format(footer), inline=True)
		await ctx.send(embed=embed)

	@welcome.command(name="test")
	async def test(self, ctx: commands.Context):
		member=ctx.author
		data=await self.bot.db.execute("""SELECT * FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if not data:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **no welcome message set**"))
		welcchannel=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		channel=self.bot.get_channel(welcchannel)
		if not channel:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **no welcome channel set**"))
		msg=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		#msg=str(ms)
		if await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True):
			if "{server}" in msg:
				msg = msg.replace("{server}", member.guild.name)
			if "{server.count}" in msg:
				msg = msg.replace("{server.count}", str(len([m for m in member.guild.members])))
			if "{mention}" in msg:
				msg = msg.replace("{mention}", member.mention)
			if "{user.name}" in msg:
				msg = msg.replace("{user.name}", member.name)
			if "{user}" in msg:
				msg = msg.replace("{user}", str(member))
			if "{user.tag}" in msg:
				usertag=f"{member.name}#{member.discriminator}"
				msg = msg.replace("{user.tag}", usertag)
		embed=await self.bot.db.execute("""SELECT embed FROM wlcembed WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if embed == 0:
			if msg != None:
				return await channel.send(msg)
		else:
			pass
		data = await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if not data:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **welcomer not setup**"))
		autho=await self.bot.db.execute("""SELECT author FROM wlcauthor WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		foote=await self.bot.db.execute("""SELECT footer FROM wlcfooter WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		channel_id=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		embed=await self.bot.db.execute("""SELECT embed FROM wlcembed WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		#messag=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		des=await self.bot.db.execute("""SELECT description FROM wlcdesc WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		titl=await self.bot.db.execute("""SELECT title FROM wlctitle WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		thum=await self.bot.db.execute("""SELECT thumb FROM wlcthumb WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		imag=await self.bot.db.execute("""SELECT image FROM wlcimage WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		#
		author=await self.bot.db.execute("""SELECT author FROM wlcauthor WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		color=await self.bot.db.execute("""SELECT color FROM wlccolor WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		footer=await self.bot.db.execute("""SELECT footer FROM wlcfooter WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		channel_id=await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		embed=await self.bot.db.execute("""SELECT embed FROM wlcembed WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		#messag=await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		desc=await self.bot.db.execute("""SELECT description FROM wlcdesc WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		title=await self.bot.db.execute("""SELECT title FROM wlctitle WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		thumb=await self.bot.db.execute("""SELECT thumb FROM wlcthumb WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		image=await self.bot.db.execute("""SELECT image FROM wlcimage WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		#author=str(autho)
		#footer=str(foote)
		#desc=str(des)
		#title=str(titl)
		#thumb=str(thum)
		#image=str(imag)
		if channel_id:
			channel_id=channel_id
		if msg != None:
			message=msg
		else:
			message=None
		if title:
			title=title
		else:
			title=None
		if desc:
			description=desc
		else:
			description=None
		if color == None:
			color=self.color
		else:
			c=await self.bot.db.execute("""SELECT color FROM wlccolor WHERE guild_id = %s""", ctx.guild.id, one_value=True)
			color=int(f"{c}", 16)
		if author:
			author=author
		else:
			author=None
		if footer:
			footer=footer
		else:
			footer=None
		if image:
			image=image
		else:
			image=None
		if thumb:
			thumb=thumb
		else:
			thumb=None
		if description != None:
			if "{server}" in description:
				description = description.replace("{server}", member.guild.name)
			if "{server.count}" in description:
				description = description.replace("{server.count}", str(len([m for m in member.guild.members])))
			if "{mention}" in msg:
				description = description.replace("{mention}", str(member.mention))
			if "{user.name}" in msg:
				description = description.replace("{user.name}", member.name)
			if "{user}" in msg:
				description = description.replace("{user}", str(member))
			if "{user.tag}" in description:
				usertag=f"{member.name}#{member.discriminator}"
				description = description.replace("{user.tag}", usertag)
		if title == None:
			embed=discord.Embed(description=description, color=color)
		#
		if title != None:
			if "{user.tag}" in title:
				usertag=f"{member.name}#{member.discriminator}"
				title = title.replace("{user.tag}", usertag)
			if "{server}" in title:
				title = title.replace("{server}", member.guild.name)
			if "{server.count}" in title:
				title = title.replace("{server.count}", str(len([m for m in member.guild.members])))
			if "{mention}" in title:
				title = title.replace("{mention}", str(member.mention))
			if "{user.name}" in title:
				title = title.replace("{user.name}", member.name)
			if "{user}" in title:
				title = title.replace("{user}", str(member))
			if "{user.tag}" in title:
				usertag=f"{member.name}#{member.discriminator}"
				title = title.replace("{user.tag}", usertag)
			embed=discord.Embed(title=title, description=description, color=color)
		#
		if author != None:
			if "{user.tag}" in author:
				usertag=f"{member.name}#{member.discriminator}"
				author = author.replace("{user.tag}", usertag)
			if "{server}" in author:
				author = author.replace("{server}", member.guild.name)
			if "{server.count}" in author:
				author = author.replace("{server.count}", str(len([m for m in member.guild.members])))
			if "{mention}" in author:
				author = author.replace("{mention}", str(member.mention))
			if "{user.name}" in author:
				author = author.replace("{user.name}", member.name)
			if "{user}" in author:
				author = author.replace("{user}", str(member))
			if "{user.tag}" in author:
				usertag=f"{member.name}#{member.discriminator}"
				author = author.replace("{user.tag}", usertag)
			embed.set_author(name=author)
		if footer != None:
			if "{user.tag}" in footer:
				usertag=f"{member.name}#{member.discriminator}"
				footer = footer.replace("{user.tag}", usertag)
			if "{server}" in footer:
				footer = footer.replace("{server}", member.guild.name)
			if "{server.count}" in footer:
				footer = footer.replace("{server.count}", str(len([m for m in member.guild.members])))
			if "{mention}" in footer:
				footer = footer.replace("{mention}", str(member.mention))
			if "{user.name}" in footer:
				footer = footer.replace("{user.name}", member.name)
			if "{user}" in footer:
				footer = footer.replace("{user}", str(member))
			if "{user.tag}" in footer:
				usertag=f"{member.name}#{member.discriminator}"
				footer = footer.replace("{user.tag}", usertag)
			embed.set_footer(text=footer)
		if thumb != None:
			if "{av}" in thumb:
				thumb=thumb.replace("{av}", str(member.display_avatar.url))
			if "{icon}" in thumb:
				thumb=thumb.replace("{icon}", str(member.guild.icon))
			embed.set_thumbnail(url=thumb)
		if image != None:
			if "{av}" in image:
				image=image.replace("{av}", str(member.display_avatar.url))
			if "{icon}" in image:
				image=image.replace("{icon}", str(member.guild.icon))
			embed.set_image(url=image)
		if message != None:
			await channel.send(content=message, embed=embed)
		else:
			await channel.send(embed=embed)


	@welcome.command(name="clear")
	async def clear(self, ctx: commands.Context):
		if ctx.message.author.id != ctx.guild.owner.id or 714703136270581841:
			if await self.bot.db.execute("""SELECT * FROM welcome WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM welcome WHERE guild_id = %s""", ctx.guild.id)
				try:
					await self.bot.db.execute("""DELETE FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id)
				except:
					pass
				try:
					await self.bot.db.execute("""DELETE FROM wlcembed WHERE guild_id = %s""", ctx.guild.id)
				except:
					pass
				try:
					await self.bot.db.execute("""DELETE FROM wlcdesc WHERE guild_id = %s""", ctx.guild.id)
				except:
					pass
				try:
					await self.bot.db.execute("""DELETE FROM wlctitle WHERE guild_id = %s""", ctx.guild.id)
				except:
					pass
				try:
					await self.bot.db.execute("""DELETE FROM wlcauthor WHERE guild_id = %s""", ctx.guild.id)
				except:
					pass
				try:
					await self.bot.db.execute("""DELETE FROM wlcfooter WHERE guild_id = %s""", ctx.guild.id)
				except:
					pass
				try:
					await self.bot.db.execute("""DELETE FROM  wlcimage WHERE guild_id = %s""", ctx.guild.id)
				except:
					pass
				try:
					await self.bot.db.execute("""DELETE FROM wlcthumb WHERE guild_id = %s""", ctx.guild.id)
				except:
					pass
				await ctx.send(embed=discord.Embed(description="welcomer cleared", color=0x303135))
		else:
			return await ctx.send(embed=await not_server_owner_msg())

	@welcome.command(name="message", aliases=["msg"], description="!welcome msg <message>")
	async def message(self, ctx: commands.Context, *, args=None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if args:
				if await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO wlcmsg (guild_id, message) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message)""", ctx.guild.id, args)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome message to `{args}`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT message FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcmsg WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome message cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a message**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())


	@welcome.command(name="embed", description="!welcome embed <true/false>")
	async def embed(self, ctx: commands.Context, *, state:bool):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if state:
				args=1
				if await self.bot.db.execute("""SELECT embed FROM wlcembed WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcembed WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO wlcembed (guild_id, embed) VALUES (%s, %s) ON DUPLICATE KEY UPDATE embed = VALUES(embed)""", ctx.guild.id, 1)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome embed** `enabled`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT embed FROM wlcembed WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					args=0
					await self.bot.db.execute("""INSERT INTO wlcembed (guild_id, embed) VALUES (%s, %s) ON DUPLICATE KEY UPDATE embed = VALUES(embed)""", ctx.guild.id, 0)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome embed** `disabled`", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **set to** `true/false`", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())

	@welcome.command(name="variables", aliases=["var", "help"])
	async def variables(self, ctx: commands.Context):
		await ctx.reply(embed=discord.Embed(title="rival", description="!welcome <subcommand>\n ***valid subcommands are:***\n\n```embed, channel, message, title, description, author, footer, image, thumbnail, variables, clear, config, test```\n\n ***syntax:***\n {mention} - mentions user\n{server} - guild name\n{user} - username\n{user.tag} - user#discrim\n{server.count} - member count\n{icon} - server icon\n{av} - users avatar"))

	@welcome.command(name="title", description="!welcome title <text>")
	async def title(self, ctx: commands.Context, *, args=None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if args:
				if await self.bot.db.execute("""SELECT title FROM wlctitle WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlctitle WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO wlctitle (guild_id, title) VALUES (%s, %s) ON DUPLICATE KEY UPDATE title = VALUES(title)""", ctx.guild.id, args)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome footer to `{args}`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT title FROM wlctitle WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlctitle WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome title cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a title**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())

	@welcome.command(name="footer", description="!welcome footer <text>")
	async def footer(self, ctx: commands.Context, *, args=None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if args:
				if await self.bot.db.execute("""SELECT footer FROM wlcfooter WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcfooter WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO wlcfooter (guild_id, footer) VALUES (%s, %s) ON DUPLICATE KEY UPDATE footer = VALUES(footer)""", ctx.guild.id, args)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome footer to `{args}`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT footer FROM wlcfooter WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcfooter WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome footer cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a footer**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())

	@welcome.command(name="author", description="!welcome author <text>")
	async def author(self, ctx: commands.Context, *, args=None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if args:
				if await self.bot.db.execute("""SELECT author FROM wlcauthor WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcauthor WHERE guild_id = %s""", ctx.guild.id)
					#await self.bot.db.execute("""INSERT INTO wlcauthor (guild_id, author) VALUES (%s, %s) ON DUPLICATE KEY UPDATE author = VALUES(author)""", ctx.guild.id, args)
#				else:
				await self.bot.db.execute("""INSERT INTO wlcauthor (guild_id, author) VALUES (%s, %s) ON DUPLICATE KEY UPDATE author = VALUES(author)""", ctx.guild.id, args)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome author to `{args}`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT author FROM wlcauthor WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcauthor WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome author cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include an author**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())


	@welcome.command(name="description", description="!welcome description <text>")
	async def description(self, ctx: commands.Context, *, args=None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if args:
				message=f"`{args}`"
				if await self.bot.db.execute("""SELECT description FROM wlcdesc WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcdesc WHERE guild_id = %s""", ctx.guild.id)
					#await self.bot.db.execute("""INSERT INTO wlcdesc (guild_id, description) VALUES (%s, %s) ON DUPLICATE KEY UPDATE description = VALUES(description)""", ctx.guild.id, args)
				#else:
				await self.bot.db.execute("""INSERT INTO wlcdesc (guild_id, description) VALUES (%s, %s) ON DUPLICATE KEY UPDATE description = VALUES(description)""", ctx.guild.id, args)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome description to `{args}`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT description FROM wlcdesc WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcdesc WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome description cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a description**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())

	@welcome.command(name="image", description="!welcome image <url/variable>")
	async def image(self, ctx: commands.Context, *, args=None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if args:
				if await self.bot.db.execute("""SELECT image FROM wlcimage WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcimage WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO wlcimage (guild_id, image) VALUES (%s, %s) ON DUPLICATE KEY UPDATE image = VALUES(image)""", ctx.guild.id, args)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome image to `{args}`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT image FROM wlcimage WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcimage WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome image cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a image**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())
	@welcome.command(name="color", description="!welcome color <color code>")
	async def color(self, ctx: commands.Context, *, args=None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if args:
				if "#" in args:
					args.strip("#")
				if await self.bot.db.execute("""SELECT color FROM wlccolor WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlccolor WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO wlccolor (guild_id, color) VALUES (%s, %s) ON DUPLICATE KEY UPDATE color = VALUES(color)""", ctx.guild.id, args)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome wlccolor to `{args}`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT color FROM wlccolor WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlccolor WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome wlccolor cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a wlccolor**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())

	@welcome.command(name="thumbnail", aliases=["thumb"], description="!welcome thumbnail <url/variable>")
	async def thumbnail(self, ctx: commands.Context, *, args=None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if args:
				if await self.bot.db.execute("""SELECT thumb FROM wlcthumb WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcthumb WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO wlcthumb (guild_id, thumb) VALUES (%s, %s) ON DUPLICATE KEY UPDATE thumb = VALUES(thumb)""", ctx.guild.id, args)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome thumbnail to `{args}`", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT thumb FROM wlcthumb WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM wlcthumb WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome thumbnail cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a thumbnail**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())

	@welcome.command(name="channel", aliases=["ch", "c"], description="!welcome channel <channel>")
	async def channel(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
		if ctx.message.author.id == ctx.guild.owner.id or 714703136270581841:
			if channel:
				if await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM welcome WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO welcome (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)""", ctx.guild.id, channel.id)
				await ctx.send(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: set welcome channel to {channel.mention}", color=self.good))
			else:
				if await self.bot.db.execute("""SELECT channel_id FROM welcome WHERE guild_id = %s""", ctx.guild.id, one_value=True):
					await self.bot.db.execute("""DELETE FROM welcome WHERE guild_id = %s""", ctx.guild.id)
					await ctx.reply(embed=discord.Embed(description=f"{self.yes} {ctx.author.mention}: **welcome channel cleared**", color=self.good))
				else:
					await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **please include a channel**", color=self.error))
		else:
			return await ctx.send(embed=await not_server_owner_msg())


async def setup(bot):
	await bot.add_cog(welcome(bot))