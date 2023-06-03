import discord
from discord.ext import commands

from modules import emojis, exceptions, util
import datetime,pytz,typing
import humanfriendly
import tweepy
import random, re, asyncio, aiohttp
from discord import ui
from datetime import timedelta
from typing import Union
from datetime import datetime as datetim
from io import BytesIO
from discord.ext import menus

from discord.ext.commands import errors
import psutil
import requests, os, ast, inspect
from bs4 import BeautifulSoup
from typing import Union
import time
from modules.MyMenuPages import MyMenuPages, MySource
from modules import exceptions, util, consts, queries, http, default, permissions, log

async def not_server_owner_msg(ctx, text=None):
	if text:
		text=text
	else:
		text="Guild Owner"
	embed = discord.Embed(
		description=f"<:warn:940732267406454845> {ctx.author.mention}: this command can **only** be used by the `{text}`",
		colour=0xfaa61a,
	)
	return embed


def create_embed(text):
	embed = discord.Embed(
		description=text,
		colour=0xa5eb78
	)
	return embed

def create_invis_embed(text):
	embed = discord.Embed(
		description=text,
		colour=0x303135,
	)
	return embed

def create_error_embed(text):
	embed = discord.Embed(
		description=f"{text}",
		colour=0xfaa61a,
	)
	return embed


class anticmds(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.add="<:plus:947812413267406848>"
		self.yes=self.bot.yes
		self.good=0xa5eb78
		self.rem="<:rem:947812531509026916>"
		self.no=self.bot.no
		self.bad=0xff6465
		self.color=0x303135
		self.cache={}
		self.perms=["add_reactions","administrator","attach_files","ban_members","change_nickname","deafen_members","embed_links","external_emojis","external_stickers","kick_members","manage_channels","manage_emojis","manage_emojis_and_stickers","manage_events","manage_guild","manage_messages","manage_nicknames","manage_permissions","manage_roles","manage_threads","manage_webhooks","moderate_members","move_members","mute_members"]
		self.ch='<:yes:940723483204255794>'
		self.error=0xfaa61a
		self.warn=self.bot.warn
		self.admins={714703136270581841,822245516461080606, 420525168381657090, 956618986110476318}


	async def whitelist_list(self, guild_id):
		"""Returns a list of custom commands on server."""
		whitelist_list = set()
		data = await self.bot.db.execute(
			"SELECT user_id FROM whitelist WHERE guild_id = %s", guild_id
		)
		for user_id in data:
			guild=self.bot.get_guild(guild_id)
			i=user_id
			if self.bot.get_user(i) != None:
				if self.bot.get_user(i) == guild.owner:
					whitelist_list.add(f"<:owner:918635065758605372>・{self.bot.get_user(i)} - {i}")
				if self.bot.get_user(i) != guild.owner:
					if self.bot.get_user(i).bot:
						whitelist_list.add(f"<:ClydeBot:940710979120029707>・{self.bot.get_user(i)} - {i}")
					else:
						whitelist_list.add(f"<:users_logo:940711249107386377>・{self.bot.get_user(i)} - {i}")

		return whitelist_list

	async def strip_roles(self, guild:discord.Guild, member:discord.Member):
		try:
			guild=self.bot.get_guild(guild.id)
		except:
			g=await self.bot.fetch_guild(guild.id)
			guild=self.bot.get_guild(g.id)
		totalroles=[]
		removedroles=[]
		for role in member.roles:
			if role.is_bot_managed():
				await role.edit(permissions=discord.Permissions(137474982912))
				removedroles.append(role)
			elif role.is_assignable() and not role.is_integration() and role.id != guild.premium_subscriber_role.id and role.position >= guild.me.top_role.position:
				totalroles.append(role.id)
		for i in totalroles:
			r=ctx.guild.get_role(i)
			removedroles.append(r)
		roles=[]
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
		if guild.premium_subscriber_role in member.roles: 
			removedroles.append(guild.premium_subscriber_role)
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


	async def trusted_list(self, guild_id, match=""):
		"""Returns a list of custom commands on server."""
		trusted_list = set()
		data = await self.bot.db.execute(
			"SELECT * FROM trusted WHERE guild_id = %s", guild_id
		)
		for user_id in data:
			guild=self.bot.get_guild(guild_id)
			i=user_id
			if self.bot.get_user(i) != None:
				if self.bot.get_user(i) == guild.owner:
					trusted_list.add(f"<:owner:918635065758605372>・{self.bot.get_user(i)} - {i}")
				if self.bot.get_user(i) != guild.owner:
					if self.bot.get_user(i).bot:
						trusted_list.add(f"<:ClydeBot:940710979120029707>・{self.bot.get_user(i)} - {i}")
					else:
						trusted_list.add(f"<:users_logo:940711249107386377>・{self.bot.get_user(i)} - {i}")

		return trusted_list

	async def perm_list(self, guild_id, match=""):
		"""Returns a list of custom commands on server."""
		perm_list = set()
		data = await self.bot.db.execute(
			"SELECT * FROM fakeperms WHERE guild_id = %s", guild_id
		)
		for role_id, perm in data:
			guild=self.bot.get_guild(guild_id)
			role=guild.get_role(role_id)
			perm_list.add(f"{role.mention} ・ `{perm}`")

		return perm_list

	async def audit(self, guild):
		entry=[entry async for entry in guild.audit_logs(limit=2, action=discord.AuditLogAction.guild_update,after=discord.utils.utcnow() - datetime.timedelta(seconds=3))]
		for entry in entry:
			if entry.user != self.bot.user:
				entry=entry
				return entry

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		guild=channel.guild
		punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", guild.id, one_value=True)
		data=await self.bot.db.execute("""SELECT channel FROM antinuke WHERE guild_id = %s""", guild.id, one_value=True)
		d=['moderator-only','rules']
		if channel.name not in d:
			return
		if not data:
			return
		dt=await self.bot.db.execute("""SELECT public,rules FROM community WHERE guild_id = %s""", guild.id)
		if not dt:
			return
		for public,rules in dt:
			public=channel.guild.get_channel(int(public))
			rules=channel.guild.get_channel(int(rules))
		try:
			await channel.guild.edit(community=True, public_updates_channel=public, rules_channel=rules,reason="[ Rival Anti Nuke] Audit Hang Detected")
		except:
			return
		try:
			try:
				entry=await self.audit(channel.guild)
			except Exception as e:
				print(e)
			try:
				if entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id or await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id):
					return
				if punishment:
					try:
						#roles=[role for role in entry.user.roles if role.is_assignable()]
						reason="[ Rival Anti ]\n・Unauthorized user updating guild."
						try:
							await self.strip_roles(channel.guild, entry.user)
						except Exception as e:
							print(e)
						try:
							jail_role = discord.utils.get(channel.guild.roles, name="jailed")
							await entry.user.add_roles(jail_role)
						except:
							pass
					except Exception as e:
						print(e)
						pass
				else:
					try:
						await channel.guild.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・Unauthorized user updating guild.")
					except Exception as error:
						print(error)
				for channel in channel.guild.channels:
					if channel == channel.guild.public_updates_channel and channel != public.id:
						pub=public
					if channel == channel.guild.rules_channel and channel != rules.id:
						ru=rules
					try:
						await guild.edit(community=True, public_updates_channel=public, rules_channel=rules, reason="[ Rival Anti Nuke ] Audit Hang CleanUp")
					except:
						pass
					if channel.name == "rules" or channel.name == "moderator-only" and not await self.bot.db.execute("""SELECT * FROM community WHERE public = %s""", channel.id) and not await self.bot.db.execute("""SELECT * FROM community WHERE rules = %s""", channel.id):
						try:
							await channel.delete(reason="[Rival Anti Nuke] Audit Hang CleanUp")
						except:
							pass
			except Exception as e:
				print(e)
		except Exception as e:
			print(e)


	@commands.command(name="raid", description="ban a certain amount of joins", aliases=["chunkban"], brief="number", extras={'perms':'Guild Owner / Anti Admin'})
	async def raid(self, ctx, number:int):
		c=0
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		if number > 500:
			return await util.send_error(ctx, f"limit of chunkban is `500`")
		sorted_members = sorted(ctx.guild.members, key=lambda x: x.joined_at, reverse=True)
		for i, member in enumerate(sorted_members, start=1):
			if not member.premium_since:
				try:
					await ctx.guild.ban(member, reason=f"ChunkBan Executed By {ctx.author}")
					c+=1
				except:
					pass
				if i >= number:
					return await util.send_good(ctx, f"successfully banned the last `{c}` joined members")

	@commands.command(name="whitelisted",description="Returns list of whitelisted users.",aliases=["wld"], extras={'perms':'Guild Owner / Anti Admin'})
	async def whitelisted(self, ctx: commands.Context):
		trusted_list = []
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		data = await self.bot.db.execute("""SELECT user_id FROM whitelist WHERE guild_id = %s""", ctx.guild.id, as_list=True)
		for user_id in data:
			guild=ctx.guild
			i=user_id
			if self.bot.get_user(i) != None:
				if self.bot.get_user(i) == guild.owner:
					trusted_list.append(f"<:owner:918635065758605372>・{self.bot.get_user(i)} - {i}")
				if self.bot.get_user(i) != guild.owner:
					if self.bot.get_user(i).bot:
						trusted_list.append(f"<:ClydeBot:940710979120029707>・{self.bot.get_user(i)} - {i}")
					else:
						trusted_list.append(f"<:users_logo:940711249107386377>・{self.bot.get_user(i)} - {i}")

		if trusted_list:
			content = discord.Embed(title=f"{guild.name}'s Whitelist")
			await util.send_as_pages(ctx, content, trusted_list)
		else:
			raise exceptions.Info("No Whitelisted Users")


	@commands.command(name='whitelist',description="Adds or Removes mentioned user to trusted members.",brief="user/member",aliases=['wl'], extras={'perms':'Guild Owner / Anti Admin'})
	async def whitelist(self, ctx: commands.Context, *, user: typing.Union[discord.Member, discord.User]=None):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		if user is None:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **please provide a member**"))
		if user:
			if isinstance(user, discord.Member):
				if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** in this server."))
				else:
					await self.bot.db.execute("""INSERT INTO whitelist VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is now **whitelisted** in this server."))
			if isinstance(user, discord.User):
				if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
					return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
				else:
					pass
				if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** in this server."))
				else:
					await self.bot.db.execute("""INSERT INTO whitelist VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is now **whitelisted** in this server."))
		else:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **invalid user provided**"))



	@commands.command(name='unwhitelist', extras={'perms':'Guild Owner / Anti Admin'}, description="Removes mentioned user from trusted/whitelisted list.",brief="user/member",aliases=["dewhitelist", "dwl", "uwl", "unwl"])
	async def unwhitelist(self, ctx: commands.Context, *, user: typing.Union[discord.Member, discord.User]=None):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		if user is None:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **please provide a member**"))
		if user:
			if isinstance(user, discord.Member):
				if not await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					return await ctx.send(embed=create_error_embed(f"{self.yes} {ctx.author.mention}: `{user}` is not whitelisted."))
				if user.id == ctx.guild.owner.id:
					return await ctx.send(embed=create_error_embed(f"{self.yes} {ctx.author.mention}: **the server owner cannot be unwhitelisted**"))
				else:
					await self.bot.db.execute("""DELETE FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** in this server."))
			if isinstance(user, discord.User):
				if not await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					return await ctx.send(embed=create_error_embed(f"{self.yes} {ctx.author.mention}: `{user}` is not whitelisted."))
				if user.id == ctx.guild.owner.id:
					return await ctx.send(embed=create_error_embed(f"{self.yes} {ctx.author.mention}: **the server owner cannot be unwhitelisted**"))
				else:
					await self.bot.db.execute("""DELETE FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** in this server."))



	@commands.command(name="trusted",description="Returns list of trusted users.",aliases=["trd", "admins"], extras={'perms': 'Guild Owner'})
	async def trusted(self, ctx: commands.Context):
		if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in self.admins:
			return await ctx.reply(embed=await not_server_owner_msg(ctx))
		else:
			pass
		trusted_list = []
		data = await self.bot.db.execute("""SELECT user_id FROM trusted WHERE guild_id = %s""", ctx.guild.id, as_list=True)
		for user_id in data:
			guild=ctx.guild
			i=user_id
			if self.bot.get_user(i) != None:
				if self.bot.get_user(i) == guild.owner:
					trusted_list.append(f"<:owner:918635065758605372>・{self.bot.get_user(i)} - {i}")
				if self.bot.get_user(i) != guild.owner:
					if self.bot.get_user(i).bot:
						trusted_list.append(f"<:ClydeBot:940710979120029707>・{self.bot.get_user(i)} - {i}")
					else:
						trusted_list.append(f"<:users_logo:940711249107386377>・{self.bot.get_user(i)} - {i}")

		if trusted_list:
			content = discord.Embed(title=f"{guild.name}'s Anti Admins")
			await util.send_as_pages(ctx, content, trusted_list)
		else:
			raise exceptions.Info("No Anti Admins")



	@commands.command(name='trust',aliases=['admin'], description="Adds mentioned user to anti admins.",brief="user/member", extras={'perms': 'Guild Owner'})
	async def trust(self, ctx: commands.Context, *, user: typing.Union[discord.Member, discord.User]=None):
		"""Syntax: !trust <@user>
		Example: !trust @cop#0001"""
		if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in self.admins:
			return await ctx.reply(embed=await not_server_owner_msg(ctx))
		else:
			pass
		if user is None:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **please provide a member**"))
		if user:
			if isinstance(user, discord.Member):
				if await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					return await util.send_success(ctx, f"{ctx.author.mention}: `{user}` **is no longer antinuke admin**")
				else:
					await self.bot.db.execute("""INSERT INTO trusted VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await util.send_success(ctx, f"{ctx.author.mention}: `{user}` **is now antinuke admin**")
			if isinstance(user, discord.User):
				if await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					return await util.send_success(ctx, f"{ctx.author.mention}: `{user}` **is no longer antinuke admin**")
				else:
					await self.bot.db.execute("""INSERT INTO trusted VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await util.send_success(ctx, f"{ctx.author.mention}: `{user}` **is now antinuke admin**")

	@commands.command(name='punishment', extras={'perms':'Guild Owner / Anti Admin'}, description="change anti punishment", brief="ban/stripstaff")
	async def punishment(self, ctx, punishment=None):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		if punishment == None:
			return await ctx.reply(embed=discord.Embed(description=f"options are ban or stripstaff"))
		if punishment.lower() == "stripstaff" or "strip" in punishment.lower():
			if await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				pass
			else:
				await self.bot.db.execute("""INSERT INTO punishment VALUES(%s, %s)""", ctx.guild.id, 1)
			await util.send_success(ctx, f"{ctx.author.mention}: **set punishment to strip staff**")
		else:
			if await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM punishment WHERE guild_id = %s""", ctx.guild.id)
			else:
				pass
			await util.send_success(ctx, f"{ctx.author.mention}: **set punishment to ban**")


	@commands.group(name="antinuke", aliases=["anti", "an"], extras={'perms':'Guild Owner / Anti Admin'})
	@commands.has_permissions(administrator=True)
	async def antinuke(self, ctx):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		if ctx.invoked_subcommand is None:
			#await ctx.send(embed=discord.Embed(title="Rival AntiNuke Commands", description=f"`!antinuke`\n{consts.down}`whitelist`{consts.dot}whitelist/unwhitelist users\n`admin`{consts.dot}give/take ability for a user to edit anti settings/whitelist others\n`admins`{consts.dot}show anti admins\n`whitelisted`{consts.dot}show whitelisted users\n`punishment`{consts.dot}change anti punishment, options are ban / stripstaff\n`settings`{consts.dot}show current anti settings\n`bot`{consts.dot}turn anti bot on or off\n`enable`{consts.dot}enable the anti nuke\n`disable`{consts.dot}disable the anti nuke\n`toggle`{consts.dot}toggle certain anti features"))
			await util.command_group_help(ctx)

	@antinuke.command(name='threshold', aliases=['limit','limits','thresholds'], description="add limits per event or just all events", extras={'perms':'Guild Owner / Anti Admin'}, brief='flag, amount')
	async def antinuke_threshold(self, ctx, flag=None, value:int=1):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		flags=['role','channel','kick','ban','webhook']
		all=['all','guild']
		if not flag:
			return await ctx.send(embed=discord.Embed(color=0xffffff, title=f"Rival Anti Nuke Thresholds", description=f"**Valid Flags:** \n`role`, `channel`, `emoji`, `sticker`, `kick`, `ban`, `webhook` or `all` for all of the above"))
		if value > 10:
			return await util.send_error(ctx, f"max threshold of `10`")
		if "emoji" in flag.lower() or "sticker" in flag.lower():
			await self.bot.db.execute("""INSERT INTO antinuke_thresholds (guild_id, asset) VALUES(%s, %s) ON DUPLICATE KEY UPDATE asset = VALUES(asset)""", ctx.guild.id, value)
			return await util.send_good(ctx, f"set limit for {flag}s to `{value}`")
		elif flag.lower() in all:
			#await self.bot.db.execute("""INSERT INTO guild_threshold VALUES(%s, %s) ON DUPLICATE KEY UPDATE threshold = VALUES(threshold)""", ctx.guild.id, value)
			try:
				await self.bot.db.execute("""DELETE FROM antinuke_thresholds WHERE guild_id = %s""", ctx.guild.id)
			except:
				pass
			await self.bot.db.execute("""INSERT INTO antinuke_thresholds (guild_id, ban, kick, webhook, role, channel, vanity, asset) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE ban = VALUES(ban) AND kick = VALUES(kick) AND webhook = VALUES(webhook) AND role = VALUES(role) AND channel = VALUES(channel) AND vanity = VALUES(vanity) AND asset = VALUES(asset)""", ctx.guild.id, value, value, value, value, value, value, value)
			return await util.send_good(ctx, f"set limit for all flags to `{value}`")
		elif flag.lower() in flags:
			await self.bot.db.execute(f"""INSERT INTO antinuke_thresholds (guild_id, {flag}) VALUES(%s, %s) ON DUPLICATE KEY UPDATE {flag} = VALUES({flag})""", ctx.guild.id, value)
			return await util.send_good(ctx, f"set limit for {flag}s to `{value}`")
		else:
			return await ctx.send(embed=discord.Embed(color=0xffffff, title=f"Rival Anti Nuke Thresholds", description=f"**Valid Flags:** \n`role`, `channel`, `emoji`, `sticker`, `kick`, `ban`, `webhook` or `all` for all of the above"))

	@antinuke.command(name='whitelist', aliases=['wl'], description="Adds or Removes mentioned user to trusted members.",brief="user/member", extras={'perms':'Guild Owner / Anti Admin'})
	async def awhitelist(self, ctx: commands.Context, *, user: typing.Union[discord.Member, discord.User]=None):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		if user is None:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **please provide a member**"))
		if user:
			if isinstance(user, discord.Member):
				if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** in this server."))
				else:
					await self.bot.db.execute("""INSERT INTO whitelist VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is now **whitelisted** in this server."))
			if isinstance(user, discord.User):
				if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
					return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
				else:
					pass
				if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** in this server."))
				else:
					await self.bot.db.execute("""INSERT INTO whitelist VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is now **whitelisted** in this server."))
		else:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **invalid user provided**"))


	@antinuke.command(name="whitelisted",description="Returns list of whitelisted users.",aliases=["wld"], extras={'perms':'Guild Owner / Anti Admin'})
	async def awhitelisted(self, ctx: commands.Context):
		trusted_list = []
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		data = await self.bot.db.execute("""SELECT user_id FROM whitelist WHERE guild_id = %s""", ctx.guild.id, as_list=True)
		for user_id in data:
			guild=ctx.guild
			i=user_id
			if self.bot.get_user(i) != None:
				if self.bot.get_user(i) == guild.owner:
					trusted_list.append(f"<:owner:918635065758605372>・{self.bot.get_user(i)} - {i}")
				if self.bot.get_user(i) != guild.owner:
					if self.bot.get_user(i).bot:
						trusted_list.append(f"<:ClydeBot:940710979120029707>・{self.bot.get_user(i)} - {i}")
					else:
						trusted_list.append(f"<:users_logo:940711249107386377>・{self.bot.get_user(i)} - {i}")

		if trusted_list:
			content = discord.Embed(title=f"{guild.name}'s Whitelist")
			await util.send_as_pages(ctx, content, trusted_list)
		else:
			raise exceptions.Info("No Whitelisted Users")


	@antinuke.command(name='unwhitelist', extras={'perms':'Guild Owner / Anti Admin'}, description="Removes mentioned user from trusted/whitelisted list.",brief="user/member",aliases=["dewhitelist", "dwl", "uwl", "unwl"])
	async def aunwhitelist(self, ctx: commands.Context, *, user: typing.Union[discord.Member, discord.User]=None):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		if user is None:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **please provide a member**"))
		if user:
			if isinstance(user, discord.Member):
				if not await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					return await ctx.send(embed=create_error_embed(f"{self.yes} {ctx.author.mention}: `{user}` is not whitelisted."))
				if user.id == ctx.guild.owner.id:
					return await ctx.send(embed=create_error_embed(f"{self.yes} {ctx.author.mention}: **the server owner cannot be unwhitelisted**"))
				else:
					await self.bot.db.execute("""DELETE FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** in this server."))
			if isinstance(user, discord.User):
				if not await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					return await ctx.send(embed=create_error_embed(f"{self.yes} {ctx.author.mention}: `{user}` is not whitelisted."))
				if user.id == ctx.guild.owner.id:
					return await ctx.send(embed=create_error_embed(f"{self.yes} {ctx.author.mention}: **the server owner cannot be unwhitelisted**"))
				else:
					await self.bot.db.execute("""DELETE FROM whitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** in this server."))


	@antinuke.command(name="trusted",description="Returns list of trusted users.",aliases=["trd", "admins"], extras={'perms': 'Guild Owner'})
	async def atrusted(self, ctx: commands.Context):
		if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in self.admins:
			return await ctx.reply(embed=await not_server_owner_msg(ctx))
		else:
			pass
		trusted_list = []
		data = await self.bot.db.execute("""SELECT user_id FROM trusted WHERE guild_id = %s""", ctx.guild.id, as_list=True)
		for user_id in data:
			guild=ctx.guild
			i=user_id
			if self.bot.get_user(i) != None:
				if self.bot.get_user(i) == guild.owner:
					trusted_list.append(f"<:owner:918635065758605372>・{self.bot.get_user(i)} - {i}")
				if self.bot.get_user(i) != guild.owner:
					if self.bot.get_user(i).bot:
						trusted_list.append(f"<:ClydeBot:940710979120029707>・{self.bot.get_user(i)} - {i}")
					else:
						trusted_list.append(f"<:users_logo:940711249107386377>・{self.bot.get_user(i)} - {i}")

		if trusted_list:
			content = discord.Embed(title=f"{guild.name}'s Anti Admins")
			await util.send_as_pages(ctx, content, trusted_list)
		else:
			raise exceptions.Info("No Anti Admins")


	@antinuke.command(name='trust',aliases=['admin'], description="Adds mentioned user to anti admins.",brief="user/member", extras={'perms': 'Guild Owner'})
	async def atrust(self, ctx: commands.Context, *, user: typing.Union[discord.Member, discord.User]=None):
		"""Syntax: !anti trust <@user>
		Example: !anti trust @cop#0001"""
		if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in self.admins:
			return await ctx.reply(embed=await not_server_owner_msg(ctx))
		else:
			pass
		if user is None:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **please provide a member**"))
		if user:
			if isinstance(user, discord.Member):
				if await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					return await util.send_success(ctx, f"{ctx.author.mention}: `{user}` **is no longer antinuke admin**")
				else:
					await self.bot.db.execute("""INSERT INTO trusted VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await util.send_success(ctx, f"{ctx.author.mention}: `{user}` **is now antinuke admin**")
			if isinstance(user, discord.User):
				if await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					return await util.send_success(ctx, f"{ctx.author.mention}: `{user}` **is no longer antinuke admin**")
				else:
					await self.bot.db.execute("""INSERT INTO trusted VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await util.send_success(ctx, f"{ctx.author.mention}: `{user}` **is now antinuke admin**")

	@antinuke.command(name='punishment', extras={'perms':'Guild Owner / Anti Admin'}, description="change anti punishment", brief="ban/stripstaff")
	async def apunishment(self, ctx, punishment=None):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		if punishment == None:
			return await ctx.reply(embed=discord.Embed(description=f"options are ban or stripstaff"))
		if punishment.lower() == "stripstaff" or "strip" in punishment.lower():
			if await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				pass
			else:
				await self.bot.db.execute("""INSERT INTO punishment VALUES(%s, %s)""", ctx.guild.id, 1)
			await util.send_success(ctx, f"{ctx.author.mention}: **set punishment to strip staff**")
		else:
			if await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM punishment WHERE guild_id = %s""", ctx.guild.id)
			else:
				pass
			await util.send_success(ctx, f"{ctx.author.mention}: **set punishment to ban**")

	@antinuke.command(name='settings',description="Returns Current Server Anti Settings",aliases=['config'], extras={'perms':'Guild Owner / Anti Admin'})
	async def asettings(self, ctx: commands.Context):
		# TYPES/HANDLERS #
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		enabled_true = "<:enabled:926194469840236605>"
		enabled_false = "<:disabled:926194368631697489>"
		errtext = "dm cop#0001 if you see this."
		# MAIN CHECKING #
		#-- limits
		limit=1
		#-- welcome
		#welcome_toggle = welcome.find_one({ "guild_id": ctx.guild.id })
		#-- toggles
		ban_toggle = await self.bot.db.execute("""SELECT ban FROM antinuke WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		kick_toggle = await self.bot.db.execute("""SELECT kick FROM antinuke WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		chanadd_toggle = await self.bot.db.execute("""SELECT channel FROM antinuke WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		roleadd_toggle = await self.bot.db.execute("""SELECT role FROM antinuke WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		webhook_toggle = await self.bot.db.execute("""SELECT webhook FROM antinuke WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		bot_toggle = await self.bot.db.execute("""SELECT * FROM antibot WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		vanitylol=await self.bot.db.execute("""SELECT vanity FROM antivanity WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		limits=await self.bot.db.execute("""SELECT ban,kick,channel,role,webhook,asset FROM antinuke_thresholds WHERE guild_id = %s""", ctx.guild.id)
		global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if global_thres:
			ban_limit=int(global_thres)
			kick_limit=int(global_thres)
			channel_limit=int(global_thres)
			role_limit=int(global_thres)
			webhook_limit=int(global_thres)
			asset_limit=int(global_thres)
		elif limits:
			for ban,kick,channel,role,webhook,asset in limits:
				ban_limit=int(ban)
				kick_limit=int(kick)
				channel_limit=int(channel)
				role_limit=int(role)
				webhook_limit=int(webhook)
				asset_limit=int(asset)
		else:
			ban_limit=1
			kick_limit=1
			channel_limit=1
			role_limit=1
			webhook_limit=1
			asset_limit=1
		if not vanitylol:
			try:
				inv=await ctx.guild.vanity_invite()
				vanitylol=inv.code
			except: 
				vanitylol="None"
		#b_toggle = "".join(bo_toggle)
		#b_toggle=str(b_toggle)
		vanitysteal_toggle = await self.bot.db.execute("""SELECT vanity FROM antinuke WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		#ban_toggle=str(ba_toggle)
		#kick_toggle=str(kic_toggle)
		#bot_toggle=str(bo_toggle)
		#chanadd_toggle=str(chanad_toggle)
		#roleadd_toggle=str(rolead_toggle)
		#vanitysteal_toggle=str(vanitystea_toggle)
		#webhook_toggle=str(webhoo_toggle)
		#welcome_toggle = await self.bot.db.execute("""SELECT ban FROM antinuke WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		#dmlog = db.find_one({'guild_id': ctx.guild.id})['dm_logs']
		premium = await self.bot.db.execute("""SELECT * FROM dnr WHERE user_id = %s""", ctx.guild.owner.id, one_value=True)
		punish = await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if premium:
			togglecheck_premium = enabled_true
			title = f"__Rival Premium Anti Settings__ ~ {ctx.guild.name}"
		else: 
			togglecheck_premium=enabled_false
			title = f"__Rival Anti-Nuke Settings__ ~ {ctx.guild.name}"
		if punish:
			punishment="stripstaff"
		else:
			punishment="ban"
		# TOGGLE CHECKS #
		if ban_toggle == 'true': 
			togglecheck_ban = enabled_true
		elif ban_toggle == 'false': 
			togglecheck_ban = enabled_false
		else:
			togglecheck_ban = enabled_false
		if bot_toggle:
			togglecheck_bot = enabled_true
		else:
			togglecheck_bot = enabled_false
		#if welcome_toggle == 'true': togglecheck_welcome = enabled_true
		#elif welcome_toggle == 'false': togglecheck_welcome = enabled_false
		#else: return await ctx.send(embed=create_error_embed(errtext))
		if kick_toggle == 'true': 
			togglecheck_kick = enabled_true
		elif kick_toggle == 'false': 
			togglecheck_kick = enabled_false
		else: 
			togglecheck_kick = enabled_false
		if chanadd_toggle == 'true': 
			togglecheck_channels = enabled_true
		elif chanadd_toggle == 'false': 
			togglecheck_channels = enabled_false
		else:
			togglecheck_channels = enabled_false
		if roleadd_toggle == 'true': 
			togglecheck_roles = enabled_true
		elif roleadd_toggle == 'false': 
			togglecheck_roles = enabled_false
		else:
			togglecheck_roles = enabled_false
		if webhook_toggle == 'true': 
			togglecheck_webhook = enabled_true
		elif webhook_toggle == 'false': 
			togglecheck_webhook = enabled_false
		else:
			togglecheck_webhook = enabled_false
		if vanitysteal_toggle == 'true': 
			togglecheck_vanity = enabled_true
		elif vanitysteal_toggle == 'false': 
			togglecheck_vanity = enabled_false
		else:
			togglecheck_vanity = enabled_false
		if togglecheck_bot != enabled_true:
			botval="\u200b"
		else:
			botval=f"・ Punishment: `{punishment}`"
		if togglecheck_roles != enabled_true:
			roleval="\u200b"
		else:
			roleval=f"・ Punishment: `{punishment}`"
		if togglecheck_ban == enabled_false:
			banval = f"\u200b"
		if togglecheck_ban == enabled_true:
			banval = f"・ Threshold: `{ban_limit}`/`60s`\n・ Punishment: `{punishment}`"
		if togglecheck_kick == enabled_false:
			kickval = f"\u200b"
		if togglecheck_kick == enabled_true:
			kickval = f"・ Threshold: `{kick_limit}`/`60s`\n・ Punishment: `{punishment}`"
		if togglecheck_channels == enabled_false:
			chanaddval = f"\u200b"
		if togglecheck_channels == enabled_true:
			chanaddval = f"・ Threshold: `{channel_limit}`/`60s`\n・ Punishment: `{punishment}`"
		if togglecheck_roles == enabled_false:
			roledelval = "\u200b"
		if togglecheck_roles == enabled_true:
			roledelval = f"・ Threshold: `{role_limit}`/`60s`\n・ Punishment: `{punishment}`"
		if ctx.guild.premium_tier == 3:
			if togglecheck_vanity == enabled_true:
				vanityval = f"・ Punishment: `{punishment}`\n・ Vanity: {vanitylol}"
			if togglecheck_vanity == enabled_false:
				vanityval = "\u200b"
		else:
			togglecheck_vanity = enabled_false
			vanityval = f"・ Your server does not support the vanity setting."
		if togglecheck_premium == enabled_true:
			premiumval=f"・ Premium Shard: {togglecheck_premium}"
		if togglecheck_premium == enabled_false:
			premiumval="\u200b"
		if togglecheck_webhook == enabled_false:
			webhookval = "\u200b"
		if togglecheck_webhook == enabled_true:
			webhookval = f"・ Threshold: `{webhook_limit}`/`60s`\n・ Punishment: `{punishment}`"

		# EMBED/MAIN MESSAGE #
		embed = discord.Embed(title=title, description="Rival Anti Nuke")
		embed.add_field(
		name=f"Premium・{togglecheck_premium}",
		value=premiumval,
		inline=True
		)
		embed.add_field(
		name=f"Anti-Ban・{togglecheck_ban}",
		value=banval,
		inline=True
		)
		embed.add_field(
		name=f"Anti-Kick・{togglecheck_kick}",
		value=kickval,
		inline=True
		)
		embed.add_field(
		name=f"Anti-Bot・{togglecheck_bot}",
		value=botval,
		inline=True
		)
		embed.add_field(
		name=f"Anti-Roles・{togglecheck_roles}",
		value=roledelval,
		inline=True
		)
		embed.add_field(
		name=f"Anti-Permissions・{togglecheck_roles}",
		value=roleval,
		inline=True
		)
		embed.add_field(
		name=f"Anti-Channels・{togglecheck_channels}",
		value=chanaddval,
		inline=True
		)
		embed.add_field(
		name=f"Anti-Webhook・{togglecheck_webhook}",
		value=webhookval,
		inline=True
		)
		embed.add_field(
		name=f"Anti-Vanity-Steal・{togglecheck_vanity}",
		value=vanityval,
		inline=True
		)
		#if togglecheck_welcome == enabled_true:
		#welcomeval=f"・JoinDM: ```{joinmsg}```"
		#embed.add_field(
		#name=f"Welcome・{togglecheck_welcome}",
		#value=welcomeval,
		#inline=True
		#)
		await ctx.send(embed=embed)

	@antinuke.command(name="toggle", extras={'perms':'Guild Owner / Anti Admin'}, description="toggle set anti features", brief="feature, state/bool",usage="```Swift\nFeatures: vanity, role, ban, kick, webhook, channel\nSyntax: !an toggle <feature> <state:bool>\nExample: !an toggle ban off```")
	async def toggle(self, ctx, feature:str, state:bool):
		features={'vanity', 'ban', 'kick', 'role', 'webhook', 'channel', 'bot','audithang'}
		if state:
			value='true'
			setting="ON"
		else:
			value='false'
			setting="OFF"
		if feature in features:
			if "audit" in feature.lower():
				if state:
					await self.bot.db.execute("""INSERT INTO antihang VALUES(%s)""", ctx.guild.id)
				else:
					try:
						await self.bot.db.execute("""DELETE FROM antihang WHERE guild_id = %s""",ctx.guild.id)
					except:
						pass
			if feature.lower() == "vanity":
				await self.bot.db.execute("""INSERT INTO antinuke (guild_id, vanity) VALUES(%s, %s) ON DUPLICATE KEY UPDATE vanity = VALUES(vanity)""", ctx.guild.id, value)
			if feature.lower() == "ban":
				await self.bot.db.execute("""INSERT INTO antinuke (guild_id, ban) VALUES(%s, %s) ON DUPLICATE KEY UPDATE ban = VALUES(ban)""", ctx.guild.id, value)
			if feature.lower() == "kick":
				await self.bot.db.execute("""INSERT INTO antinuke (guild_id, kick) VALUES(%s, %s) ON DUPLICATE KEY UPDATE kick = VALUES(kick)""", ctx.guild.id, value)
			if feature.lower() == "role":
				await self.bot.db.execute("""INSERT INTO antinuke (guild_id, role) VALUES(%s, %s) ON DUPLICATE KEY UPDATE role = VALUES(role)""", ctx.guild.id, value)
			if feature.lower() == "channel":
				await self.bot.db.execute("""INSERT INTO antinuke (guild_id, channel) VALUES(%s, %s) ON DUPLICATE KEY UPDATE channel = VALUES(channel)""", ctx.guild.id, value)
			if feature.lower() == "webhook":
				await self.bot.db.execute("""INSERT INTO antinuke (guild_id, webhook) VALUES(%s, %s) ON DUPLICATE KEY UPDATE webhook = VALUES(webhook)""", ctx.guild.id, value)
			if feature.lower() == "bot":
				if await self.bot.db.execute("""SELECT * FROM antibot WHERE guild_id = %s""", ctx.guild.id):
					await self.bot.db.execute("""DELETE FROM antibot WHERE guild_id = %s""", ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO antibot (guild_id) VALUES (%s)""", ctx.guild.id)
			await util.send_success(ctx, f"{ctx.author.mention}: ``{feature.lower()}`` is now **{setting}**")
			if "COMMUNITY" not in ctx.guild.features:
				rules=ctx.guild.text_channels[1]
				public=ctx.guild.text_channels[2]
			else:
				rules=ctx.guild.rules_channel
				public=ctx.guild.public_updates_channel
			await self.bot.db.execute("""INSERT INTO community VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE public = VALUES(public) AND rules = VALUES(rules)""", ctx.guild.id, public.id, rules.id)
		else:
			return await ctx.reply(embed=discord.Embed(title='Rival AntiNuke Features', color=0x303135, description="**Valid Togglable Features:**\n`role`, `channel`, `webhook`, `vanity`, `kick`, `ban`, `bot`"))

	@antinuke.command(name='features', aliases=['toggles', 'feature'], extras={'perms':'Guild Owner / Anti Admin'}, description="list all togglable antinuke features")
	async def features(self, ctx):
		await ctx.reply(embed=discord.Embed(title='Rival AntiNuke Features', color=0x303135, description="**Valid Togglable Features:**\n`role`, `channel`, `webhook`, `vanity`, `kick`, `ban`, `bot`"))

	@antinuke.command(name='off', aliases=["false", "disable"], description="turn off the anti nuke", extras={'perms':'Guild Owner / Anti Admin'})
	async def antinuke_off(self, ctx):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		try:
			if await self.bot.db.execute("""SELECT * FROM antinuke WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM antinuke WHERE guild_id = %s""", ctx.guild.id)
			await self.bot.db.execute("""INSERT INTO antinuke VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE ban = %s, kick = %s, webhook = %s, role = %s, channel = %s, vanity = %s""", ctx.guild.id, 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false')
			await ctx.send(embed=create_embed(f'{self.yes} {ctx.author.mention}: `Anti Nuke` Is Now Disabled.'))
		except Exception as e:
			await ctx.send(f"There was an error while changing toggle for: `AntiNuke`")
			raise e
			return

	@antinuke.command(name='vanity', description='set the anti vanity vanity', extras={'perms':'Guild Owner / Anti Admin'})
	async def avanity(self, ctx, vanity):
		await self.bot.db.execute("""INSERT INTO antivanity VALUES(%s, %s) ON DUPLICATE KEY UPDATE vanity = VALUES(vanity)""", ctx.guild.id, vanity)
		await util.send_success(ctx, f"{ctx.author.mention}: **set antinuke anti vanity to {vanity}**") 

	@antinuke.command(name='on', aliases=["true", "enable"], extras={'perms':'Guild Owner / Anti Admin'}, description="turn on the anti nuke")
	async def antinuke_on(self, ctx):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		try:
			if await self.bot.db.execute("""SELECT * FROM antinuke WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM antinuke WHERE guild_id = %s""", ctx.guild.id)
			try:
				if "COMMUNITY" not in ctx.guild.features:
					rules=ctx.guild.text_channels[1]
					public=ctx.guild.text_channels[2]
				else:
					rules=ctx.guild.rules_channel
					public=ctx.guild.public_updates_channel
			except:
				rules=await ctx.guild.create_text_channel(name='rules')
				public=await ctx.guild.create_text_channel(name='community')
			if await self.bot.db.execute("""SELECT * FROM community WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM community WHERE guild_id = %s""", ctx.guild.id)
			await self.bot.db.execute("""INSERT INTO community VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE public = VALUES(public) AND rules = VALUES(rules)""", ctx.guild.id, public.id, rules.id)
			await self.bot.db.execute("""INSERT INTO antinuke (guild_id, ban, kick, webhook, role, channel, vanity) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE ban = VALUES(ban), kick = VALUES(kick), webhook = VALUES(webhook), role = VALUES(role), channel = VALUES(channel), vanity = VALUES(vanity)""", ctx.guild.id, 'true', 'true', 'true', 'true', 'true', 'true')
			
			await ctx.send(embed=create_embed(f'{self.yes} {ctx.author.mention}: `Anti Nuke` Is Now Enabled.'))
		except Exception as e:
			await ctx.send(f"There was an error while changing toggle for: `AntiNuke`")
			raise e

	@commands.group(name="antibot", extras={'perms':'Guild Owner / Anti Admin'}, description="toggle anti bot")
	async def antibot(self, ctx: commands.Context):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		if ctx.invoked_subcommand is None:
			await ctx.send(embed=discord.Embed(title="Enemy Anti Nuke", description=f"type !antibot on or !antibot off to toggle the anti bot completely"))

	@antibot.command(name='off', aliases=["false", "disable"], extras={'perms':'Guild Owner / Anti Admin'}, description="turn off the anti bot")
	async def off(self, ctx: commands.Context):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		try:
			if await self.bot.db.execute("""SELECT * FROM antibot WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM antibot WHERE guild_id = %s""", ctx.guild.id)
			await ctx.send(embed=create_embed(f'{self.yes} {ctx.author.mention}: `Anti Bot` Is Now Disabled.'))
		except Exception as e:
			await ctx.send(f"There was an error while changing toggle for: `AntiBot`")
			raise e
			return

	@antibot.command(name='on', aliases=["true", "enable"], extras={'perms':'Guild Owner / Anti Admin'}, description="turn on the anti bot")
	async def on(self, ctx: commands.Context):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		try:
			if await self.bot.db.execute("""SELECT * FROM antibot WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM antibot WHERE guild_id = %s""", ctx.guild.id)
			await self.bot.db.execute("""INSERT INTO antibot (guild_id) VALUES (%s)""", ctx.guild.id)
			await ctx.send(embed=create_embed(f'{self.yes} {ctx.author.mention}: `Anti Bot` Is Now Enabled.'))
		except Exception as e:
			await ctx.send(f"There was an error while changing toggle for: `Anti Bot `")
			raise e
			return	 


	@commands.command(name='guildblacklist', aliases=['gbl'], description="blacklist a member from joining the server", brief="member", extras={'perms':'Guild Owner / Anti Admin'})
	@commands.has_permissions(administrator=True)
	async def guildblacklist(self, ctx, member:typing.Union[discord.Member, discord.User]):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		if isinstance(member, discord.Member):
			member=member
		else:
			member=await self.bot.fetch_user(member.id)
		if await self.bot.db.execute("SELECT * FROM abump WHERE guild_id = %s AND g_id = %s", member.id, ctx.guild.id):
			await self.bot.db.execute("DELETE FROM abump WHERE guild_id = %s and g_id = %s",member.id, ctx.guild.id)
			return await ctx.reply(embed=discord.Embed(color=self.good, description=f'unblacklisted member {member.name}#{member.discriminator}'))

		await self.bot.db.execute("INSERT INTO abump VALUES(%s, %s)",member.id, ctx.guild.id)
		await ctx.reply(embed=discord.Embed(color=self.good, description=f'blacklisted user {member.name}#{member.discriminator}'))

	@commands.group(name="fakepermissions", aliases=["fakeperms","fakeperm"], description="give a role a permission for only rival commands")
	async def fakepermissions(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@fakepermissions.command(name="add", aliases=['a'], description="add fakepermissions to a role", usage="```Swift\nSyntax: !fakepermissions add <role> <permission>\nExample: !fakepermissions add admins administrator```", brief="role, permission", extras={'perms':'Guild Owner / Anti Admin'})
	async def fake_add(self, ctx, role:discord.Role, *, permission):
		permission=permission.lower()
		if "kick " in permission:
		    permission=permission.replace("kick ","kick_")
		if "ban " in permission:
		    permission=permission.replace("ban ","ban_")
		if "move " in permission:
		    permission=permission.replace("move ","move_")
		if "mute " in permission:
		    permission=permission.replace("mute ","mute_")
		if "manage " in permission:
		    permission=permission.replace("manage ","manage_")
		if "moderate " in permission:
		    permission=permission.replace("moderate ","moderate_")
		if " " in permission:
			permission=permission.replace(" ",",")
		if "," in permission:
			permission=permission.split(",")
			permission=",".join(permission.lower() for permission in permission)
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		perms=permission.lower()
		#permission=permission.lower()
		if "," in permission:
			for permission in perms.split(","):
				if permission not in self.perms:
					return await util.send_error(ctx, f"unknown permission `{permission}`, please use an actual permission")
		else:
			if permission not in self.perms:
				return await util.send_error(ctx, f"unknown permission `{permission}`, please use an actual permission")

		await self.bot.db.execute("""INSERT INTO fakeperms VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id) AND guild_id = VALUES(guild_id) AND perm = VALUES(perm)""", role.id, ctx.guild.id, perms)
		await util.send_good(ctx, f"`{perms}` added to {role.mention}")


	@fakepermissions.command(name="remove", aliases=['r','delete','del','d','rem'], description="remove fakepermissions from a role", usage="```Swift\nSyntax: !fakepermissions remove <role> <permission>\nExample: !fakepermissions remove admins administrator```", brief="role, permission", extras={'perms':'Guild Owner / Anti Admin'})
	async def fake_rem(self, ctx, role:discord.Role):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		if await self.bot.db.execute("""SELECT * FROM fakeperms WHERE role_id = %s""", role.id):
			await self.bot.db.execute("""DELETE FROM fakeperms WHERE role_id = %s""", role.id)
			return await util.send_good(ctx, f"deleted fake permissions from {role.mention}")
		else:
			return await util.send_error(ctx, f"no fake permissions found for {role.mention}")

	@fakepermissions.command(name="permissions", aliases=['perms','help'], description="show all permissions")
	async def fake_permissions(self, ctx):
		rows=[]
		content=discord.Embed(title="Rival Permissions", color=0xfffff, url="https://rival.rocks")
		for perm in self.perms:
			rows.append(f"`{perm}`")
		await util.send_as_pages(ctx, content, rows)


	@fakepermissions.command(name="list", description="show fakepermission roles", usage="```Swift\nSyntax: !fakepermissions list```", extras={'perms':'Guild Owner / Anti Admin'})
	async def fake_list(self, ctx):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		rows=[]
		ct=0
		data=await self.bot.db.execute("""SELECT role_id, perm FROM fakeperms WHERE guild_id = %s""", ctx.guild.id)
		if data:
			content=discord.Embed(color=0xffffff, title=f"{ctx.guild.name}'s fakepermissions")
			for role_id, perm in data:
				r=ctx.guild.get_role(role_id)
				rows.append(f"{r.mention} ・ `{perm.lower()}`")
		if rows:
			await util.send_as_pages(ctx, content, rows)
		else:
			return await util.send_bad(ctx, f"no fakepermissions found")




async def setup(bot):
	await bot.add_cog(anticmds(bot))