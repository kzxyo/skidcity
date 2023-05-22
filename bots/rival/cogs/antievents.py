
import discord,sqlite3,arrow
from discord.ext import commands, tasks
from typing import Dict, Callable
import collections
from modules import emojis, exceptions, util
import typing
import datetime,pytz
import humanfriendly
import tweepy
import random, re, asyncio, aiohttp
from discord import ui
from datetime import timedelta
from typing import Union
from datetime import datetime
from io import BytesIO
import datetime
from discord.ext import menus
import traceback
from discord.enums import StickerFormatType
from discord.errors import HTTPException
from discord.ext.commands import Context
from discord.ext.commands.errors import BadArgument
from discord.message import Message
from discord.sticker import GuildSticker, StandardSticker, StickerItem
from discord.ext.commands import errors
import psutil,requests, os, ast, inspect,ssl,certifi
from bs4 import BeautifulSoup
from typing import Union
cnnnnn = aiohttp.TCPConnector(limit=0,ssl=False)
sslcontext = ssl.create_default_context(cafile=certifi.where())
import time
from modules.MyMenuPages import MyMenuPages, MySource
from modules import exceptions, util, consts, queries, http, default, permissions, log, GetImage
from colorama import Fore as C
from colorama import Fore
from modules.asynciterations import aiter
from aiohttp_proxy import ProxyConnector, ProxyType
import logging
logger = logging.getLogger(__name__)


token=os.environ["TOKEN"]
headers=util.getheaders(token)
dt="Banned 1 User"


async def not_server_owner_msg(ctx, text=None):
	if text:
		text=text
	else:
		text="Guild Owner"
	embed = discord.Embed(
		description=f"{ctx.bot.warn} {ctx.author.mention}: this command can **only** be used by the `{text}`",
		colour=ctx.bot.color,
	)
	return embed


def create_embed(text):
	embed = discord.Embed(
		description=text,
		colour=0xD6BCD0
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
		colour=0xD6BCD0,
	)
	return embed


class antievents(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.colour = 0xD6BCD0
		self.color=self.bot.color
		self.joins={}
		self.mention={}
		self.perpetrators={}
		self.trigger={}
		self.sesh=1
		self.bump_list = []
		self.connector1=ProxyConnector.from_url('http://14acd04c580ce:cf437bf954@http://168.158.200.49:12323')
		self.connector2=ProxyConnector.from_url('http://14acd04c580ce:cf437bf954@31.131.11.197:12323')
		self.session1=aiohttp.ClientSession(connector=cnnnnn,headers={'Authorization':'Bot MTAwMjI5NDc2MzI0MTg4NTg0Nw.GpX-Q5.oQB61lRTTlYcjPikv-zbEkBYUwJaMgQC2-OsfU'})
		self.session2=aiohttp.ClientSession(connector=cnnnnn,headers={'Authorization':'Bot MTAwMjI5NDc2MzI0MTg4NTg0Nw.GpX-Q5.oQB61lRTTlYcjPikv-zbEkBYUwJaMgQC2-OsfU'})
		self.cache_needs_refreshing = True
		self.admins={714703136270581841,822245516461080606, 420525168381657090, 956618986110476318,904832583551057950}
		self.bump_loop.start()
		self.perp_loop.start()
		self.trigger_loop.start()
		self.antiraidloop.start()

	def cog_unload(self):
		self.bump_loop.cancel()
		self.perp_loop.cancel()
		self.trigger_loop.cancel()
		self.antiraidloop.cancel()


	async def audit_access(self, guild):
		if self.sesh == 1:
			async with self.session1.get(f"https://discord.com/api/v9/guilds/{guild.id}/audit-logs?limit=1", proxy='http://14abea38a24b7:30b94753d2@168.158.200.49:12323',ssl=False) as r:
				if r.status in (200, 201, 204):
					q=await r.json(content_type=None)
					entry = q['audit_log_entries'][0]
					return entry
				elif r.status == 429:
					self.sesh=2
					async with self.session2.get(f"https://discord.com/api/v9/guilds/{guild.id}/audit-logs?limit=1", proxy='http://14acd04c580ce:cf437bf954@31.131.11.197:12323',ssl=False) as d:
						if d.status in (200, 201, 204):
							q=await r.json(content_type=None)
							entry = q['audit_log_entries'][0]
							return entry
						elif d.status == 429:
							return False
						else:
							return False
				else:
					return False
		else:
			async with self.session2.get(f"https://discord.com/api/v9/guilds/{guild.id}/audit-logs?limit=1", proxy='http://14acd04c580ce:cf437bf954@31.131.11.197:12323',ssl=False) as r:
				if r.status in (200, 201, 204):
					q=await r.json(content_type=None)
					entry = q['audit_log_entries'][0]
					return entry
				elif r.status == 429:
					self.sesh=1
					async with self.session1.get(f"https://discord.com/api/v9/guilds/{guild.id}/audit-logs?limit=1", proxy='http://14abea38a24b7:30b94753d2@168.158.200.49:12323',ssl=False)as d:
						if d.status in (200, 201, 204):
							q=await r.json(content_type=None)
							entry = q['audit_log_entries'][0]
							return entry
						elif d.status == 429:
							return False
				else:
					return False


	async def strip_roles(self, guild:discord.Guild, member:discord.Member, reason=None):
		guild=self.bot.get_guild(guild.id)
		totalroles=[]
		removedroles=[]
		async for role in aiter(member.roles):
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
			async for role in aiter(removedroles):
				roles.append(f"{role.id}")
			new_lst=(','.join(str(a) async for a in aiter(roles)))
			newroles=f"{new_lst}"
			if await self.bot.db.execute("""SELECT * FROM restore WHERE guild_id = %s AND member_id = %s""", guild.id, member.id):
				await self.bot.db.execute("""DELETE FROM restore WHERE guild_id = %s AND member_id = %s""", guild.id, member.id)
			await self.bot.db.execute("""INSERT INTO restore VALUES(%s, %s, %s)""", guild.id, member.id, newroles)
		except:
			pass
		try:
			if not reason:
				return await member.edit(roles=[role async for role in aiter(removedroles)], reason="Rival Anti Nuke - Staff Stripped")
			else:
				return await member.edit(roles=[role async for role in aiter(removedroles)], reason=reason)
		except Exception as e:
			print(f"{e} in {guild.name}")
			try:
				async for role in aiter(member.roles):
					if role.permissions.administrator or role.permissions.manage_guild or role.permissions.manage_roles or role.permissions.manage_channels or role.permissions.ban_members or role.permissions.kick_members or role.permissions.manage_emojis_and_stickers or role.permissions.manage_webhooks or role.permissions.moderate_members:
						try: 
							if not reason:
								await member.remove_roles(role, reason='Rival Anti Nuke - Staff Stripped') 
							else:
								await member.remove_roles(role, reason=reason)
						except: 
							pass
			except:
				await member.ban("Rival Anti Nuke - Strip Staff Failed")

	# Anti Nuke Database Table Add
	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		try:
			if await self.bot.db.execute("""SELECT FROM whitelist WHERE guild_id = %s AND user_id = %s""", guild.id, guild.owner.id):
				pass
			else:
				await self.bot.db.execute("""INSERT INTO whitelist VALUES (%s, %s)""", guild.id, guild.owner.id)
			await self.bot.db.execute("""INSERT INTO antinuke VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE ban = 0, kick = 0, bot = 0, webhook = 0, role = 0, channel = 0, vanity = 0""", guild.id, 0, 0, 0, 0, 0, 0, 0)
			await self.bot.db.execute("""INSERT INTO antibot VALUES (%s, %s)""", guild.id, 0)
			logger.info(f"Inserted {guild.name} Into Anti DB")
		except:
			logger.info(f"Failed Inserting {guild.name} Into Anti DB")
			pass

	# Anti Nuke Database Table Delete
	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		try:
			await self.bot.db.execute("""DELETE FROM antinuke WHERE guild_id = %s""", guild.id)
			await self.bot.db.execute("""DELETE FROM antibot WHERE guild_id = %s""", guild.id)
			await self.bot.db.execute("""DELETE FROM punishment WHERE guild_id = %s""", guild.id)
			logger.info(f"Deleted {guild.name} from Anti DB")
		except:
			logger.info(f"Failed to Delete {guild.name} from Anti DB")
			pass

	# Anti Nuke - Anti Emoji Update
	@commands.Cog.listener()
	async def on_guild_emojis_update(self, guild, before, after):
		if not guild.me.guild_permissions.view_audit_log:
			return
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['channel'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		# data = await self.bot.db.execute("""SELECT channel FROM antinuke WHERE guild_id = %s""", guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		# punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", guild.id, one_value=True)
		#threshold=await self.bot.db.execute("""SELECT asset FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "asset" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['asset']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		try:
			async for entry in guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
			#entry=entry[0]
				if entry.action != discord.AuditLogAction.emoji_delete:
					return
				if entry.user.id == self.bot.user.id:
					return
				if entry.user.id == guild.owner.id:
					return
				#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id):
					#return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				reappend=[]
				for before in before:
					if before not in after:
						reappend.append(before)
				try:
					data = re.findall(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>", str(reappend[0]))
					for _a, emoji_name, emoji_id in data:
						animated = _a == "a"
						if animated:
							url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".gif"
						else:
							url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".png"
						f=await GetImage.download(url)
						with open(f,"rb") as e:
							img=e.read()
						#img=response.content
						emote=await guild.create_custom_emoji(name=emoji_name, image=img, reason="[ Rival Anti ]\n・Anti Emoji Delete")
						GetImage.remove(f)
				except:
					pass
				if global_thres:
					if int(global_thres) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(global_thres):
							return
				if threshold:
					if int(threshold) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(threshold) - 1:
							return
				if punishment:
					try:
						return await self.strip_roles(guild, entry.user, "[ Rival Anti ]\n・User Caught Deleting Emojis")
					except Exception as e:
						print(f"{e} in {guild.name}")
				else:
					try:
						return await entry.user.ban(reason="[ Rival Anti ]\n・User Caught Deleting Emojis")
					except:
						pass
		except Exception as e:
			print(f"{e} in {guild.name}")

	# Anti Nuke - Anti Sticker Update
	@commands.Cog.listener()
	async def on_guild_stickers_update(self, guild, before, after):
		if not guild.me.guild_permissions.view_audit_log:
			return
		dic={}
		# data = await self.bot.db.execute("""SELECT channel FROM antinuke WHERE guild_id = %s""", guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['channel'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", guild.id, one_value=True)
		#threshold=await self.bot.db.execute("""SELECT asset FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "asset" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['asset']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		try:
			async for entry in guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
			#entry=entry[0]
				if entry.action != discord.AuditLogAction.sticker_delete:
					return
				if entry.user.id == self.bot.user.id:
					return
				if entry.user.id == guild.owner.id:
					return
				#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id):
					#return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				for before in before:
					if before not in after:
						dic['name']=before.name
						dic['url']=before.url
				emurl=dic.get("url")
				emname=dic.get("name")
				img=await GetImage.download(emurl)
				added_sticker: GuildSticker = await guild.create_sticker(name=emname, description="sticker", emoji="🥛", file=discord.File(img),reason=f"[ Rival Anti ]\n・Anti Sticker Delete")
				GetImage.remove(img)
				if global_thres:
					if int(global_thres) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(global_thres):
							return
				if threshold:
					if int(threshold) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(threshold) - 1:
							return
				if punishment:
					try:
						return await self.strip_roles(guild, entry.user, '[ Rival Anti ]\n・User Caught Deleting Stickers')
					except Exception as e:
						print(f"{e} in {guild.name}")
				else:
					try:
						return await entry.user.ban(reason="[ Rival Anti ]\n・User Caught Deleting Stickers")
					except:
						pass
		except Exception:
			return print(f"{Fore.RED}[Anti Error]: ({channel.guild.name}){Fore.RESET}") 

	# Anti Nuke - Anti Channel Delete
	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		if not channel.guild.me.guild_permissions.view_audit_log:
			return
		#data = await self.bot.db.execute("""SELECT channel FROM antinuke WHERE guild_id = %s""", channel.guild.id, one_value=True)
		#if not data:
		if str(channel.guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(channel.guild.id)]['channel'] != 'true':
			return
		#if data != 'true':
			#return
		guild=channel.guild
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", channel.guild.id, one_value=True)
		if str(channel.guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(channel.guild.id)]
		else:
			punishment=None
		#threshold=await self.bot.db.execute("""SELECT channel FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "channel" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['channel']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		try:
			async for entry in channel.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3), action=discord.AuditLogAction.channel_delete):
			#entry=entry[0]
				if entry.user.id == self.bot.user.id:
					return
				if entry.user.id == channel.guild.owner.id:
					return
				#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", channel.guild.id, entry.user.id):
					#return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				try:
					await channel.clone()
				except:
					pass
				if global_thres:
					if int(global_thres) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(global_thres):
							return
				if threshold:
					if int(threshold) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(threshold) - 1:
							return
				if punishment:
					try:
						await self.strip_roles(channel.guild, entry.user, "[ Rival Anti ]\n・User Caught Deleting Channels.")
					except Exception as e:
						print(f"{e} in {guild.name}")
				else:
					try:
						await entry.user.ban(reason="[ Rival Anti ]\n・User Caught Deleting Channels.")
					except Exception as error:
						if isinstance(error, discord.Forbidden):
							return
						else:
							return print(f"{Fore.RED}[Anti Error]: Deleted Channel. ({channel.guild.name}){Fore.RESET}")
				try:
					ch=await channel.clone()
				except:
					pass
				try:
					return await ch.edit(position=ch.position)
				except:
					pass
				return
		except Exception as error:
			if isinstance(error, discord.Forbidden):
				return
			else:
				return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Channel-Delete. ({channel.guild.name}){Fore.RESET}") 

	# Anti Nuke - Anti Channel Create
	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		if not channel.guild.me.guild_permissions.view_audit_log:
			return
		guild=channel.guild
		if str(channel.guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(channel.guild.id)]['channel'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		# data = await self.bot.db.execute("""SELECT channel FROM antinuke WHERE guild_id = %s""", channel.guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", channel.guild.id, one_value=True)
		audithang=['rules', 'moderator-only']
		guild=channel.guild
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		#threshold=await self.bot.db.execute("""SELECT channel FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "channel" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['channel']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		if channel.name == 'rules' or channel.name == 'moderator-only':
			reason="[Rival Anti]\n・Anti Audit Hang"
			lsd=[]
			for channel in channel.guild.channels:
				if channel.name == 'rules' or channel.name == 'moderator-only':
					lsd.append(channel)
			if len(lsd) > 4:
				pass
			else:
				return
			try:
				if await self.bot.db.execute("""SELECT * FROM antihang WHERE guild_id = %s""", channel.guild.id):
					pass
				else:
					return
				entry=[entry async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.bot_add,limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3))]
				entry=entry[0]
				#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", channel.guild.id, entry.user.id):
					#return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				if entry.user.id == self.bot.user.id:
					return
				if entry.user.id == channel.guild.owner.id and entry.user.id != 714703136270581841 and entry.user.id != 904832583551057950:
					return
				whitelistedbots=[776128410547126322,472911936951156740,826240098235449366,1002294763241885847,235148962103951360,578258045889544192,508391840525975553,994052621570687158,942674412178653184,593921296224747521,302050872383242240,412347553141751808,412347780841865216,155149108183695360,294882584201003009,547905866255433758,356268235697553409,298822483060981760,468281173072805889,432610292342587392,412347257233604609]
				members=[member for member in channel.guild.members if member.bot and not member.id in whitelistedbots]
				sorted_members = sorted(members, key=lambda x: x.joined_at, reverse=True)
				try:
					entry.user.ban(reason=reason)
				except Exception as error:
					if isinstance(error, discord.Forbidden):
						pass
					else:
						return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Audit-Hang. ({channel.guild.name}){Fore.RESET}") 
				if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", channel.guild.id, sorted_members[0].id):
					return
				try:
					await sorted_members[0].ban(reason=reason)
				except Exception as error:
					if isinstance(error, discord.Forbidden):
						pass
					else:
						return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Audit-Hang. ({channel.guild.name}){Fore.RESET}") 
				for member in sorted_members:
					if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", channel.guild.id, member.id):
						return
					try:
						await member.ban(reason=reason)
					except Exception as error:
						if isinstance(error, discord.Forbidden):
							return
						else:
							print(f"Anti-Audit-Hang Error: {error}")
				for channel in lsd:
					try:
						await channel.delete(reason=reason)
					except:
						pass
			except Exception as error:
				if isinstance(error, discord.Forbidden):
					return
				else:
					return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Audit-Hang. ({channel.guild.name}){Fore.RESET}") 

		else:
			pass
		async for entry in channel.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
		#entry=entry[0]
			try:
				#roles=[role for role in entry.user.roles if role.is_assignable()]
				if entry.user.id == self.bot.user.id:
					return
				if entry.user.id == channel.guild.owner.id:
					return
				if entry.action != discord.AuditLogAction.channel_create:
					return
				#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", channel.guild.id, entry.user.id):
					#return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				if global_thres:
					if int(global_thres) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(global_thres):
							return
				if threshold:
					if int(threshold) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(threshold) - 1:
							return
				if punishment:
					try:
						await self.strip_roles(channel.guild, entry.user, "[ Rival Anti ]\n・User Caught Creating Channels.")
					except Exception as e:
						print(f"{e} in {guild.name}")
					await channel.delete()
				else:
					try:
						await entry.user.ban(reason="[ Rival Anti ]\n・User Caught Creating Channels.")
						await channel.delete()
					except:
						pass
				return
			except Exception as error:
				if isinstance(error, discord.Forbidden):
					return
				else:
					return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Channel-Create. ({channel.guild.name}){Fore.RESET}") 

	# Anti Nuke - Anti Channel Update
	@commands.Cog.listener()
	async def on_guild_channel_update(self, before, after):
		if not after.guild.me.guild_permissions.view_audit_log:
			return
		# data = await self.bot.db.execute("""SELECT channel FROM antinuke WHERE guild_id = %s""", after.guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		guild=before.guild
		if str(before.guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(before.guild.id)]['channel'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		count=0
		# for channel in after.guild.channels:
		# 	if channel.permissions_for(channel.guild.default_role).view_channel == True: count+=1
		# try:
		# 	if count == 0:
		# 		guild=after.guild
		# 		channel=before
		# 		if guild.rules_channel: await guild.rules_channel.set_permissions(channel.guild.default_role, view_channel=True)
		# 		elif guild.system_channel: await guild.system_channel.set_permissions(channel.guild.default_role, view_channel=True)
		# 		else: await channel.guild.channels[0].set_permissions(channel.guild.default_role, view_channel=True)
		# except:
		# 	pass
		guild=before.guild
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		#threshold=await self.bot.db.execute("""SELECT channel FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "channel" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['channel']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", before.guild.id, one_value=True)
		try:
			async for entry in before.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
			#entry=entry[0]
				if entry.action != discord.AuditLogAction.channel_update:
					return
				try:
					#roles=[role for role in entry.user.roles if role.is_assignable()]
					entryuser = entry.user
					if entry.user.id == self.bot.user.id:
						return
					#if await self.bot.db.execute("""SELECT * FROM whitelist where guild_id = %s and user_id = %s""", before.guild.id, entry.user.id):
						#return
					if str(guild.id) in self.bot.cache.whitelist:
						if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
							return
					if entry.user.id == after.guild.owner.id:
						return
					if global_thres:
						if int(global_thres) > 1:
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(global_thres):
								return
					if threshold:
						if int(threshold) > 1:
							#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
							#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(threshold) - 1:
								return
					if punishment:
						roles=[]
						try:
							await self.strip_roles(before.guild, entry.user, '[ Rival Anti ]\n・User Caught Updating Channels.')
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							jail_role = discord.utils.get(before.guild.roles, name="jailed")
							if jail_role: await entry.user.add_roles(jail_role)
						except:
							pass
					else:
						try:
							await entry.user.ban(reason='[ Rival Anti ]\n・User Caught Updating Channels.')
						except:
							pass
					try:
						await after.edit(name=before.name, position=before.position, overwrites=before.overwrites)
					except:
						pass
					return
				except Exception:
					return print(f"{Fore.RED}[Anti Error]: ({channel.guild.name}){Fore.RESET}") 		
		except discord.Forbidden:
			await self.bot.db.execute("""DELETE FROM antinuke WHERE guild_id = %s""", before.guild.id)	

	 # Anti Nuke - Anti Ban
	@commands.Cog.listener()
	async def on_member_ban(self, guild, user):
		if not guild.me.guild_permissions.view_audit_log:
			return
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['ban'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		# data = await self.bot.db.execute("""SELECT ban FROM antinuke WHERE guild_id = %s""", guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		reason = '[ Rival Anti ]\n・User Caught Banning Members.'
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		#threshold=await self.bot.db.execute("""SELECT ban FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "ban" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['ban']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", guild.id, one_value=True)
		async for entry in guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
		#entry=entry[0]
			try:
				if entry.action != discord.AuditLogAction.ban:
					return
				entryuser = entry.user
				if entry.user.id == self.bot.user.id:
					return
				if entry.user.id == guild.owner.id:
					return
				#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id):
					#return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				if global_thres:
					if int(global_thres) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(global_thres):
							return
				if threshold:
					if int(threshold) > 1:
						#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
						#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
						try:	
							if entry.user.id not in self.perpetrators:
								self.perpetrators[entry.user.id]=[]
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							try:
								self.perpetrators[entry.user.id]+=1
							except:
								self.perpetrators[entry.user.id]=1
						except Exception as e:
							print(f"{e} in {guild.name}")
						amount = self.perpetrators[entry.user.id]
						if amount <= int(threshold) - 1:
							return
				if punishment:
					try:
						await self.strip_roles(guild, entry.user, reason)
					except Exception as e:
						print(f"{e} in {guild.name}")
				else:
					try:
						await guild.ban(discord.Object(entry.user.id),reason=reason)
					except Exception as error:
						if isinstance(error, discord.Forbidden):
							return
						else:
							print(f"Anti-Ban-Error: {error}")
				await guild.unban(user)
				return
			except Exception:
				return print(f"{Fore.RED}[Anti Error]: ({channel.guild.name}){Fore.RESET}") 

	# Anti Nuke - Anti Kick
	@commands.Cog.listener()
	async def on_member_remove(self, member):
		if not member:
			return
		if not member.guild.me.guild_permissions.view_audit_log:
			return
		# data = await self.bot.db.execute("""SELECT kick FROM antinuke WHERE guild_id = %s""", member.guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		guild=member.guild
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['kick'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 3:
		# 		return
		#threshold=await self.bot.db.execute("""SELECT kick FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "kick" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['kick']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", member.guild.id, one_value=True)
		audit=await self.audit_access(member.guild)
		if not audit:
			async for entry in member.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
			#entry=entry[0]
				try:
					#print(entry)
					if entry.action != discord.AuditLogAction.kick:
						if entry.action != discord.AuditLogAction.member_prune:
							return
					if entry.user.id == member.guild.id:
						return
					if entry.user.id == self.bot.user.id:
						return
					#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", member.guild.id, entry.user.id):
						#return
					if str(guild.id) in self.bot.cache.whitelist:
						if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
							return
					try:
						reason="[ Rival Anti ]\n・User Caught Kicking Members."
						if global_thres:
							if int(global_thres) > 1:
								#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
								#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
								try:	
									if entry.user.id not in self.perpetrators:
										self.perpetrators[entry.user.id]=[]
								except Exception as e:
									print(f"{e} in {guild.name}")
								try:
									try:
										self.perpetrators[entry.user.id]+=1
									except:
										self.perpetrators[entry.user.id]=1
								except Exception as e:
									print(f"{e} in {guild.name}")
								amount = self.perpetrators[entry.user.id]
								if amount <= int(global_thres):
									return
						if threshold:
							if int(threshold) > 1:
								#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
								#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
								try:	
									if entry.user.id not in self.perpetrators:
										self.perpetrators[entry.user.id]=[]
								except Exception as e:
									print(f"{e} in {guild.name}")
								try:
									try:
										self.perpetrators[entry.user.id]+=1
									except:
										self.perpetrators[entry.user.id]=1
								except Exception as e:
									print(f"{e} in {guild.name}")
								amount = self.perpetrators[entry.user.id]
								if amount <= int(threshold) - 1:
									return
						if punishment:
							try:
								await self.strip_roles(member.guild, entry.user, "[ Rival Anti ]\n・User Caught Kicking Members.")
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								jail_role = discord.utils.get(member.guild.roles, name="jailed")
								if jail_role: await entry.user.add_roles(jail_role)
							except:
								pass
						else:
							try:
								await member.guild.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・User Caught Kicking Members.")
							except:
								pass
						return
					except Exception:
						return print(f"{Fore.RED}[Anti Error]: ({channel.guild.name}){Fore.RESET}") 
				except Exception:
					return print(f"{Fore.RED}[Anti Error]: ({channel.guild.name}){Fore.RESET}") 
		else:
			try:
				action_type=audit['action_type']
				if action_type in (21, 20):
					user=int(audit['user_id'])
					user_object=member.guild.get_member(user)
					if user_object is None:
						return
					if user == member.guild.id:
						return
					if user == self.bot.user.id:
						return
					if str(member.guild.id) in self.bot.cache.whitelist:
						if user in self.bot.cache.whitelist[str(member.guild.id)]:
							return
						if threshold:
							if int(threshold) > 1:
								#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
								#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
								try:	
									if user not in self.perpetrators:
										self.perpetrators[user]=[]
								except Exception as e:
									print(f"{e} in {guild.name}")
								try:
									try:
										self.perpetrators[user]+=1
									except:
										self.perpetrators[user]=1
								except Exception as e:
									print(f"{e} in {guild.name}")
								amount = self.perpetrators[user]
								if amount <= int(threshold) - 1:
									return
						if punishment:
							try:
								await self.strip_roles(member.guild, user_object, "[ Rival Anti ]\n・User Caught Kicking Members.")
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								jail_role = discord.utils.get(member.guild.roles, name="jailed")
								if jail_role: await user_object.add_roles(jail_role)
							except:
								pass
						else:
							try:
								await member.guild.ban(discord.Object(user),reason="[ Rival Anti ]\n・User Caught Kicking Members.")
							except:
								pass
			except Exception as e:
				print(f"Anti Kick Error: {e} in {member.guild.name}")


	# Anti Nuke - Anti Webhook
	@commands.Cog.listener()
	async def on_webhooks_update(self, channel):
		if not channel.guild.me.guild_permissions.view_audit_log:
			return
		# data = await self.bot.db.execute("""SELECT webhook FROM antinuke WHERE guild_id = %s""", channel.guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", channel.guild.id, one_value=True)
		guild=channel.guild
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['webhook'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		#threshold=await self.bot.db.execute("""SELECT kick FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "kick" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['kick']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		async for entry in channel.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
		#entry=entry[0]
			try:
				if entry.action != discord.AuditLogAction.webhook_create:
					return
				else:
					if entry.user.id == self.bot.user.id:
						return
					if entry.user.id == channel.guild.owner.id:
						return
					#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", channel.guild.id, entry.user.id):
						#return
					if str(guild.id) in self.bot.cache.whitelist:
						if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
							return
				try:
					if global_thres:
						if int(global_thres) > 1:
							#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
							#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(global_thres):
								return
					if threshold:
						if int(threshold) > 1:
							#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
							#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(threshold) - 1:
								return
					if punishment:
						reason="[ Rival Anti ]\n・User Caught Creating Webhooks."
						roles=[]
						try:
							await self.strip_roles(channel.guild, entry.user, reason)
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							jail_role = discord.utils.get(channel.guild.roles, name="jailed")
							if jail_role: await entry.user.add_roles(jail_role)
						except:
							pass
					else:
						try:
							await channel.guild.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・User Caught Creating Webhooks.")
						except:
							pass
					return await entry.target.delete()
				except Exception as error:
					if isinstance(error, discord.Forbidden):
						return
					else:
						return print(f"{Fore.RED}[Anti Error]: Webhook Creation. ({channel.guild.name}){Fore.RESET}") 
			except Exception as error:
				if isinstance(error, discord.Forbidden):
					return
				else:
					return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Webhook. ({channel.guild.name}){Fore.RESET}") 


	# bot
	@commands.Cog.listener()
	async def on_member_join(self, member):
		if not member.guild.me.guild_permissions.view_audit_log:
			return
		if not member.bot:
			return
		#data = await self.bot.db.execute("""SELECT * FROM antibot WHERE guild_id = %s""", member.guild.id, one_value=True)
		#if not data:
		if member.guild.id not in self.bot.cache.antibot:
			return
		guild=member.guild
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", member.guild.id, one_value=True)
		try:
			async for entry in member.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
			#entry=entry[0]
				if member.bot:
					try:
						if entry.action == discord.AuditLogAction.bot_add:
							pass
						else:
							return
						if entry.user.id == self.bot.user.id:
							return
						if entry.user.id == member.guild.owner.id:
							return
						#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", member.guild.id, entry.user.id):
							#return
						if str(guild.id) in self.bot.cache.whitelist:
							if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
								return
						try:
							await member.ban(reason="[ Rival Anti ]\n・Anti-Bot is enabled.")
						except Exception as error:
							if isinstance(error, discord.Forbidden):
								return
							else:
								return print(f"{Fore.RED}[Anti Error]: Added Bot. ({member.guild.name}){Fore.RESET}")
						if punishment:
							reason="[ Rival Anti ]\n・Anti-Bot is enabled."
							try:
								await self.strip_roles(member.guild, entry.user, reason)
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								jail_role = discord.utils.get(member.guild.roles, name="jailed")
								if jail_role: await entry.user.add_roles(jail_role)
							except:
								pass
						else:
							try:
								await member.guild.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・User Caught Adding Bots.")
							except Exception as error:
								if isinstance(error, discord.Forbidden):
									return
								else:
									return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Bot. ({member.guild.name}){Fore.RESET}") 
					except Exception as error:
						if isinstance(error, discord.Forbidden):
							return
						else:
							return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Bot. ({member.guild.name}){Fore.RESET}") 
				else:
					return
		except:
			self.bot.cache.antibot.remove(member.guild.id)
			return

	# rcreate
	@commands.Cog.listener()
	async def on_guild_role_create(self, role):
		if not role.guild.me.guild_permissions.view_audit_log:
			return
		# data = await self.bot.db.execute("""SELECT role FROM antinuke WHERE guild_id = %s""", role.guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		guild=role.guild
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['role'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		#threshold=await self.bot.db.execute("""SELECT role FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "role" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['role']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", role.guild.id, one_value=True)
		async for entry in role.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
		#entry=entry[0]
			try:
				if entry.user.id == self.bot.user.id:
					return
				if entry.user.id == role.guild.owner.id:
					return
				if entry.action == discord.AuditLogAction.bot_add:
					return
				if entry.action == discord.AuditLogAction.integration_create:
					return
				if entry.action != discord.AuditLogAction.role_create:
					return
				#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", role.guild.id, entry.user.id):
					#return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				try:
					if global_thres:
						if int(global_thres) > 1:
							#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
							#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(global_thres):
								return
					if threshold:
						if int(threshold) > 1:
							#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
							#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(threshold) - 1:
								return
					if punishment:
						reason="[ Rival Anti ]\n・User Caught Creating Roles."
						try:
							await self.strip_roles(role.guild, entry.user, reason)
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							jail_role = discord.utils.get(role.guild.roles, name="jailed")
							if jail_role: await entry.user.add_roles(jail_role)
						except:
							pass
					else:
						await role.guild.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・User Caught Creating Roles.")
				except Exception as error:
					if isinstance(error, discord.Forbidden):
						return
					else:
						return print(f"{Fore.RED}[Anti Error]: Role-Creation. ({role.guild.name}){Fore.RESET}")
				try:
					await role.delete()
				except:
					pass
				return
			except Exception as error:
				if isinstance(error, discord.Forbidden):
					return
				else:
					return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Role-Create. ({role.guild.name}){Fore.RESET}") 

	# rdel
	@commands.Cog.listener()
	async def on_guild_role_delete(self, role):
		if not role.guild.me.guild_permissions.view_audit_log:
			return
		guild=role.guild
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['role'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		if str(guild.id) in self.bot.cache.threshold:
			if "role" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['role']
			else:
				threshold=None
		else:
			threshold=None
		global_thres=None
		async for entry in role.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):	
			try:
				if entry.user.id == self.bot.user.id:
					return
				if entry.user.id == role.guild.owner.id:
					return
				if entry.action != discord.AuditLogAction.role_delete:
					return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				try:
					if global_thres:
						if int(global_thres) > 1:
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(global_thres):
								return
					if threshold:
						if int(threshold) > 1:
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(threshold) - 1:
								return
					if punishment:
						reason="[ Rival Anti ]\n・User Caught Deleting Roles."
						roles=[]
						try:
							await self.strip_roles(role.guild, entry.user, reason)
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							jail_role = discord.utils.get(role.guild.roles, name="jailed")
							if jail_role:
								await entry.user.add_roles(jail_role)
						except:
							pass
					else:
						await role.guild.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・User Caught Deleting Roles.")
					try:
						await role.guild.create_role(name=role.name, position=role.position, color=role.color,permissions=role.permissions,hoist=role.hoist, display_icon=role.display_icon,mentionable=role.mentionable, reason=reason)
					except:
						pass
					return
				except Exception as error:
					if isinstance(error, discord.Forbidden):
						return
					else:
						return print(f"{Fore.RED}[Anti Error]: Role-Deletion. ({role.guild.name}){Fore.RESET}")
			except Exception as error:
				if isinstance(error, discord.Forbidden):
					return
				else:
					return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Role-Delete. ({role.guild.name}){Fore.RESET}") 

	# rperms
	@commands.Cog.listener()
	async def on_guild_role_update(self, before, after):
		if not before.guild.me.guild_permissions.view_audit_log:
			return
		# data = await self.bot.db.execute("""SELECT role FROM antinuke WHERE guild_id = %s""", after.guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		guild=before.guild
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['role'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		#threshold=await self.bot.db.execute("""SELECT role FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "role" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['role']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		# try:
		# 	self.trigger[guild.id]+=1
		# except:
		# 	self.trigger[guild.id]=1
		# if guild.id in self.trigger:
		# 	if self.trigger[guild.id] < 10:
		# 		return
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", before.guild.id, one_value=True)
		async for entry in before.guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
		#entry=entry[0]
			reason="[ Rival Anti ]\n・User Caught Giving Role Unsafe Permissions.."
			try:
				if entry.action != discord.AuditLogAction.role_update:
					return
				else:
					if entry.user.id == self.bot.user.id:
						return
					if entry.user.id == before.guild.owner.id:
						return
					#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", after.guild.id, entry.user.id):
						#return
					if str(guild.id) in self.bot.cache.whitelist:
						if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
							return
					if not before.permissions.manage_channels and after.permissions.manage_channels or not before.permissions.manage_webhooks and after.permissions.manage_webhooks or not before.permissions.manage_guild and after.permissions.manage_guild or not before.permissions.kick_members and after.permissions.kick_members or not before.permissions.ban_members and after.permissions.ban_members or not before.permissions.administrator and after.permissions.administrator or not before.permissions.mention_everyone and after.permissions.mention_everyone or not before.permissions.manage_roles and after.permissions.manage_roles:
						try:
							if global_thres:
								if int(global_thres) > 1:
									#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
									#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
									try:	
										if entry.user.id not in self.perpetrators:
											self.perpetrators[entry.user.id]=[]
									except Exception as e:
										print(f"{e} in {guild.name}")
									try:
										try:
											self.perpetrators[entry.user.id]+=1
										except:
											self.perpetrators[entry.user.id]=1
									except Exception as e:
										print(f"{e} in {guild.name}")
									amount = self.perpetrators[entry.user.id]
									if amount <= int(global_thres):
										return
							if threshold:
								if int(threshold) > 1:
									#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
									#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
									try:	
										if entry.user.id not in self.perpetrators:
											self.perpetrators[entry.user.id]=[]
									except Exception as e:
										print(f"{e} in {guild.name}")
									try:
										try:
											self.perpetrators[entry.user.id]+=1
										except:
											self.perpetrators[entry.user.id]=1
									except Exception as e:
										print(f"{e} in {guild.name}")
									amount = self.perpetrators[entry.user.id]
									if amount <= int(threshold) - 1:
										return
							if punishment:
								try:
									await after.edit(permissions=1166401, reason="[ Rival Anti ]\n・Anti Permissions..")
									try:
										await self.strip_roles(before.guild, entry.user, reason)
									except Exception as e:
										print(f"{e} in {guild.name}")
									try:
										jail_role = discord.utils.get(before.guild.roles, name="jailed")
										if jail_role:
											await entry.user.add_roles(jail_role)
									except:
										pass
								except:
									pass
							else:
								await after.guild.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・User Caught Giving Role Unsafe Permissions..")
								return await after.edit(permissions=1166401, reason="[ Rival Anti ]\n・Anti Permissions..")
							return
						except Exception as error:
							if isinstance(error, discord.Forbidden):
								return
							else:
								return print(f"{Fore.RED}[Anti Error]: Kick_Ban_Admin_Mention_Roles-Permissions ({after.guild.name}){Fore.RESET}")
							return
			except Exception as error:
				if isinstance(error, discord.Forbidden):
					return
				else:
					return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Permissions. ({after.guild.name}){Fore.RESET}") 


# vanity
	@commands.Cog.listener()
	async def on_guild_update(self, before, after):
		if not after.me.guild_permissions.view_audit_log:
			return
		if before.vanity_invite == after.vanity_invite:
			return
		#vanity_check=await self.bot.db.execute("""SELECT vanity FROM antinuke WHERE guild_id = %s""", after.id, one_value=True)
		#data=await self.bot.db.execute("""SELECT channel FROM antinuke WHERE guild_id = %s""", after.id, one_value=True)
		guild=after
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['vanity'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", before.id, one_value=True)
		try:
			async for entry in guild.audit_logs(limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
			#entry=entry[0]
				if entry.action != discord.AuditLogAction.guild_update:
					return
				if after.me.guild_permissions.view_audit_log:
					try:
						vanity_url_before: discord.AuditLogDiff = entry.before
						vanity_url: str = vanity_url_before.vanity_url_code
						vanity_url_after: discord.AuditLogDiff = entry.after
						after_url: str = vanity_url_after.vanity_url_code
					except:
						return
				if entry.user.id == before.owner.id:
					try:
						return await self.bot.db.execute("""INSERT INTO antivanity(%s, %s) ON DUPLICATE KEY UPDATE vanity = VALUES(vanity)""", before.id, after_url) 
					except Exception as e:
						return
				if entry.user.id == self.bot.user.id:
					return
				if before.premium_tier == 3:
					if not vanity_check: return
					if vanity_check != 'true': return
					if before.vanity_invite == after.vanity_invite: return
					try:
						#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", after.id, entry.user.id):
						if str(guild.id) in self.bot.cache.whitelist:
							if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
								try:
									return await self.bot.db.execute("""INSERT INTO antivanity(%s, %s) ON DUPLICATE KEY UPDATE vanity = VALUES(vanity)""", before.id, vanity2) 
								except Exception as e:
									return	
						try:
							await after.edit(vanity_code=vanity_url)
						except Exception as e:
							print(f"{e} in {guild.name}")	
							pass
						if punishment:
							try:
								#roles=[role for role in entry.user.roles if role.is_assignable()]
								reason="[ Rival Anti ]\n・Unauthorized user changing vanity."
								try:
									await self.strip_roles(guild, entry.user, reason)
								except Exception as e:
									print(f"{e} in {guild.name}")
								try:
									jail_role = discord.utils.get(guild.roles, name="jailed")
									await entry.user.add_roles(jail_role)
								except:
									pass
							except Exception as e:
								print(f"{e} in {guild.name}")
								pass
						else:
							try:
								await after.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・Unauthorized user changing vanity.")
							except Exception as error:
								if isinstance(error, discord.Forbidden):
									return
								else:
									return print(f"{Fore.RED}[Anti Error]: Vanity Protection ({after.name}){Fore.RESET}")
					except Exception as error:
						if isinstance(error, discord.Forbidden):
							return
						else:
							return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Vanity. ({after.name}){Fore.RESET}") 
		except Exception as error:
			if isinstance(error, discord.Forbidden):
				return
			else:
				return print(f"{Fore.RED}[Anti Error]: Guild Protection ({after.name}){Fore.RESET}")
		#print(f"{vanity_url_before} - {vanity_url} - {vanity_url_after} - {after_url}")

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if not after.guild.me.guild_permissions.view_audit_log:
			return
		# data = await self.bot.db.execute("""SELECT role FROM antinuke WHERE guild_id = %s""", before.guild.id, one_value=True)
		# if not data:
		# 	return
		# if data != 'true':
		# 	return
		if len(before.roles) == len(after.roles):
			return
		#punishment=await self.bot.db.execute("""SELECT * FROM punishment WHERE guild_id = %s""", before.guild.id, one_value=True)
		guild = after.guild
		if str(guild.id) not in self.bot.cache.antinuke:
			return
		if self.bot.cache.antinuke[str(guild.id)]['role'] != 'true':
			return
		if str(guild.id) in self.bot.cache.punishment:
			punishment=self.bot.cache.punishment[str(guild.id)]
		else:
			punishment=None
		#threshold=await self.bot.db.execute("""SELECT role FROM antinuke_thresholds WHERE guild_id = %s""", guild.id, one_value=True)
		if str(guild.id) in self.bot.cache.threshold:
			if "role" in self.bot.cache.threshold[str(guild.id)]:
				threshold=self.bot.cache.threshold[str(guild.id)]['role']
			else:
				threshold=None
		else:
			threshold=None
		#global_thres=await self.bot.db.execute("""SELECT threshold FROM guild_threshold WHERE guild_id = %s""", guild.id, one_value=True)
		global_thres=None
		try:
			newrole=next(role for role in after.roles if role not in before.roles)
		except:
			return
		try:
			async for entry in before.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3)):
			#entry=entry[0]
				if entry.user.id == after.guild.owner.id:
					return
				if entry.user.id == self.bot.user.id:
					return
				#if await self.bot.db.execute("""SELECT * FROM whitelist WHERE guild_id = %s AND user_id = %s""", after.guild.id, entry.user.id):
					#return
				if str(guild.id) in self.bot.cache.whitelist:
					if entry.user.id in self.bot.cache.whitelist[str(guild.id)]:
						return
				role=newrole
				if role.permissions.administrator or role.permissions.manage_guild or role.permissions.kick_members or role.permissions.ban_members or role.permissions.manage_roles or role.permissions.manage_channels or role.permissions.manage_webhooks:
					try:
						await entry.target.remove_roles(newrole, reason="[ Rival Anti ]\n・Anti Permissions..")
					except:
						pass
					if global_thres:
						if int(global_thres) > 1:
							#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
							#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(global_thres):
								return
					if threshold:
						if int(threshold) > 1:
							#await self.bot.db.execute("""INSERT INTO an_thresholds VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", entry.user.id, guild.id, 1)
							#amount=await self.bot.db.execute("""SELECT amount FROM an_thresholds WHERE guild_id = %s AND user_id = %s""", guild.id, entry.user.id, one_value=True)
							try:	
								if entry.user.id not in self.perpetrators:
									self.perpetrators[entry.user.id]=[]
							except Exception as e:
								print(f"{e} in {guild.name}")
							try:
								try:
									self.perpetrators[entry.user.id]+=1
								except:
									self.perpetrators[entry.user.id]=1
							except Exception as e:
								print(f"{e} in {guild.name}")
							amount = self.perpetrators[entry.user.id]
							if amount <= int(threshold) - 1:
								return
					if punishment:
						#roles=[role for role in entry.user.roles if role.is_assignable()]
						reason="[ Rival Anti ]\n・Anti Permissions.."
						try:
							await self.strip_roles(before.guild, entry.user, reason)
						except Exception as e:
							print(f"{e} in {guild.name}")
						try:
							jail_role = discord.utils.get(before.guild.roles, name="jailed")
							if jail_role: await entry.user.add_roles(jail_role)
						except:
							pass
					else:
						return await before.guild.ban(discord.Object(entry.user.id),reason="[ Rival Anti ]\n・Giving members unsafe roles")
		except Exception as error:
			if isinstance(error, discord.Forbidden):
				return
			else:
				return print(f"{Fore.RED}[Anti Error]: {error} | Anti-Role-Give. ({entry.guild.name}){Fore.RESET}") 
			
	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if message.author == self.bot.user:
			return
		try:
			if message.author.id == 302050872383242240 and len(message.embeds) == 1 and "Bump done!" in message.embeds[0].description:
				if not await self.bot.db.execute("""SELECT * FROM bumpstate WHERE guild_id = %s""", message.guild.id, one_value=True):
					return
				if message.guild.id not in self.mention:
					self.mention[message.guild.id] = []
				try:
					if len(self.mention[message.guild.id]) > 1:
						self.mention[message.guild.id].pop(0)
				except:
					pass
				self.mention[message.guild.id].append(message.interaction.user.id)
				embed = discord.Embed(description="**Thanks for bumping the server <3**", color=0x303135)
				await message.channel.send(embed=embed)
				now = arrow.utcnow()
				dt = now.datetime
				await self.bot.db.execute("""INSERT INTO bumper (guild_id, channel_id, ts)VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id) AND ts = VALUES(ts)""",message.guild.id, message.channel.id, dt)
		except Exception as e:
			print(f"{e} in {guild.name}")

	@tasks.loop(seconds=5.0)
	async def bump_loop(self):
		try:
			await self.check_bump()
		except Exception as e:
			logger.error(f"bump loop error: {e}")

	@bump_loop.before_loop
	async def before_bump_loop(self):
		await self.bot.wait_until_ready()
		logger.info("Starting bump loop")

	async def check_bump(self):
		"""Check all current bumpers"""
		self.bump_list = await self.bot.db.execute("""SELECT guild_id, channel_id, ts FROM bumper""")
		#print(self.bump_list)

		if not self.bump_list:
			return #print("no bumps")

		now_ts = arrow.utcnow().timestamp
		for (guild_id,channel_id, ts) in self.bump_list:
			#print("checking")
			date=arrow.get(ts).shift(seconds=7201).timestamp
			ts = ts.timestamp()
			if date > now_ts:
				continue
			#print("ya")

			channel = self.bot.get_channel(channel_id)
			if not channel:
				return
			if channel is not None:
				guild = channel.guild
				if guild is None:
					guild = "Unknown guild"
				if now_ts - date > 21600:
					logger.info(
						f"Deleting bump set for {channel.guild.id} for being over 6 hours late"
					)
				else:
					try:	
						mention=self.mention[guild.id][0]
					except:
						mention=None
					if mention:
						men=f"<@!{mention}>"
					else:
						men=None
					embed = discord.Embed(title="It's time to bump!", description="Use `/bump` to bump the server!", color=0x303135)
					try:
						await channel.send(content=men, embed=embed, allowed_mentions=discord.AllowedMentions(users=True))
					except discord.errors.Forbidden:
						pass
			else:
				logger.info(f"Deleted expired Bumper by unknown guild {channel.guild.id}")

			await self.bot.db.execute(
				"""
				DELETE FROM bumper
					WHERE guild_id = %s AND channel_id = %s
				""",
				guild_id,
				channel_id,
			)


	@tasks.loop(hours=1)
	async def antiraidloop(self):
		#db=await self.bot.db.execute("""SELECT guild_id FROM joins""")
		#for guild_id in db:
			#await self.bot.db.execute("""DELETE FROM joins WHERE guild_id = %s""", guild_id)
		self.bot.cache.antiraid_joins.clear()
		logger.info("Cleared AntiRaid Table")

	@antiraidloop.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		logger.info("Starting AntiRaid Clear Loop")

	@tasks.loop(minutes=2)
	async def perp_loop(self):
		if len(self.perpetrators) >= 1:
			self.perpetrators.clear()
		#self.perpetrators={}

	@perp_loop.before_loop
	async def before_perp(self):
		await self.bot.wait_until_ready()
		logger.info("Starting AntiNuke Perp Clear Loop")

	@tasks.loop(seconds=30)
	async def trigger_loop(self):
		try:
			self.trigger.clear()
		except Exception as e:
			logger.error(f"antinuke trigger loop error: {e}")

	@trigger_loop.before_loop
	async def before_trigger_loop (self):
		await self.bot.wait_until_ready()
		logger.info("Starting AntiNuke Trigger Loop")


	@commands.group(name='antiraid', description='antiraid command group')
	async def antiraid(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@antiraid.command(name='trigger', description="amount of joins in 1 hour to trigger anti raid", extras={'perms':'administrator'},usage="```Syntax: !antiraid trigger <joins>\nExample: !antiraid trigger 5```", brief="amount")
	@commands.has_permissions(administrator=True)
	async def atrigger(self, ctx, amount: int):
		if amount > 0:
			if await self.bot.db.execute("""SELECT * FROM antiraidtrigger WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM antiraidtrigger WHERE guild_id = %s""", ctx.guild.id)
				self.bot.cache.antiraid_trigger.pop(ctx.guild.id)
			self.bot.cache.antiraid_trigger.update({ctx.guild.id:amount})
			await self.bot.db.execute("""INSERT INTO antiraidtrigger VALUES(%s, %s)""", ctx.guild.id, amount)
			await util.send_success(ctx, f"{ctx.author.mention}: **Anti Raid Trigger set to `{amount}` joins in 1 hour**")
		else:
			await self.bot.db.execute("""DELETE FROM antiraidtrigger WHERE guild_id = %s""", ctx.guild.id)
			if ctx.guild.id in self.bot.cache.antiraid_trigger:
				self.bot.cache.antiraid_trigger.pop(ctx.guild.id)
			await util.send_success(ctx, f"{ctx.author.mention}: **Anti Raid Trigger Disabled**")


	@antiraid.command(namme='age', usage="```Syntax: !antiraid age <number of days>\nExample: !antiraid age 7```",extras={'perms':'administrator'}, description="set minimum account age in days", brief="amount")
	@commands.has_permissions(administrator=True)
	async def age(self, ctx, days:int):
		if days > 0:
			amount=days
			if await self.bot.db.execute("""SELECT * FROM antiraid WHERE guild_id = %s""", ctx.guild.id, one_value=True):
				await self.bot.db.execute("""DELETE FROM antiraid WHERE guild_id = %s""", ctx.guild.id)
				self.bot.cache.antiraid_age.update({ctx.guild.id:days})
			await self.bot.db.execute("""INSERT INTO antiraid VALUES(%s, %s)""", ctx.guild.id, amount)
			await util.send_success(ctx, f"{ctx.author.mention}: **Anti Raid Minimum Set To {days} Days**")
		else:
			await self.bot.db.execute("""DELETE FROM antiraid WHERE guild_id = %s""", ctx.guild.id)
			if ctx.guild.id in self.bot.cache.antiraid_age:
				self.bot.cache.antiraid_age.pop(ctx.guild.id)
			await util.send_success(ctx, f"{ctx.author.mention}: **Anti Raid Age Disabled**")

	@antiraid.command(name='avatar', aliases=['defaultavatar', 'av'], description="checks if user has a avatar", extras={'perms':'administrator'}, brief='bool', usage='```Swift\nSyntax: !antiraid avatar <bool>\nExample: !antiraid avatar True```')
	@commands.has_permissions(administrator=True)
	async def antiraid_avatar(self, ctx, state:bool):
		if state:
			try:
				await self.bot.db.execute("""INSERT INTO antiraidav VALUES(%s) ON DUPLICATE KEY UPDATE guild_id = VALUES(guild_id)""", ctx.guild.id)
			except:
				pass
			try:
				if ctx.guild.id not in self.bot.cache.antiraid_av:
					self.bot.cache.antiraid_av.append(ctx.guild.id)
			except:
				pass
			return await util.send_good(ctx, f"successfully `enabled` antiraid avatar check")
		else:
			try:
				await self.bot.db.execute("""DELETE FROM antiraidav WHERE guild_id = %s""", ctx.guild.id)
			except:
				pass
			try:
				self.bot.cache.antiraid_av.remove(ctx.guild.id)
			except:
				pass
			return await util.send_good(ctx, f"successfully `disabled` antiraid avatar check")

	@antiraid.command(name='whitelist', aliases=['wl'], description="Toggles Antiraid from triggering from a specific user",brief="user/member", extras={'perms':'Guild Owner / Anti Admin'})
	async def aawhitelist(self, ctx: commands.Context, *, user: typing.Union[discord.Member, discord.User]=None):
		if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
			return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
		else:
			pass
		if user is None:
			return await ctx.reply(embed=create_error_embed(f"{self.warn} {ctx.author.mention}: **please provide a member**"))
		if user:
			if isinstance(user, discord.Member):
				if await self.bot.db.execute("""SELECT * FROM awhitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM awhitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.bot.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** to join the server."))
				else:
					await self.bot.db.execute("""INSERT INTO awhitelist VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await ctx.send(embed=create_embed(f"{self.bot.yes} {ctx.author.mention}: `{user}` is now **whitelisted** to join the server."))
			if isinstance(user, discord.User):
				if not await self.bot.db.execute("""SELECT * FROM trusted WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, ctx.author.id) and ctx.author.id not in self.admins and ctx.author.id != ctx.guild.owner.id:
					return await ctx.reply(embed=await not_server_owner_msg(ctx, text="Guild Owner / Anti Admins"))
				else:
					pass
				if await self.bot.db.execute("""SELECT * FROM awhitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id):
					await self.bot.db.execute("""DELETE FROM awhitelist WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, user.id)
					await ctx.send(embed=create_embed(f"{self.bot.yes} {ctx.author.mention}: `{user}` is no longer **whitelisted** to join the server."))
				else:
					await self.bot.db.execute("""INSERT INTO awhitelist VALUES (%s, %s)""", ctx.guild.id, user.id)
					return await ctx.send(embed=create_embed(f"{self.bot.yes} {ctx.author.mention}: `{user}` is now **whitelisted** to join the server."))
		else:
			return await ctx.reply(embed=create_error_embed(f"{self.bot.warn} {ctx.author.mention}: **invalid user provided**"))

	
	@antiraid.command(name='settings', aliases=['cfg', 'config'], description="show current anti raid config", extras={'perms':'administrator'})
	@commands.has_permissions(administrator=True)
	async def antiraidsettings(self, ctx):
		data=await self.bot.db.execute("""SELECT * FROM antiraid WHERE guild_id = %s""", ctx.guild.id)
		ag=await self.bot.db.execute("""SELECT * FROM antiraid WHERE guild_id = %s""", ctx.guild.id)
		trig=await self.bot.db.execute("""SELECT * FROM antiraidtrigger WHERE guild_id = %s""", ctx.guild.id)
		av=await self.bot.db.execute("""SELECT * FROM antiraidav WHERE guild_id = %s""", ctx.guild.id)
		try:
			for guild_id, trigger in trig:
				trigger=trigger
		except:
			trigger=consts.no
		try:
			for guild_id, age in ag:
				age=age
		except:
			age=consts.no
		if av:
			check=consts.yes
		else:
			check=consts.no
		if data:
			embed=discord.Embed(title=f"{ctx.guild.name}'s anti raid config", color=0xffffff).add_field(name="Minimum Account Age", value=age, inline=True).add_field(name='Trigger', value=trigger, inline=True).add_field(name="Default Avatar", value=check, inline=True)
			await ctx.reply(embed=embed)
		else:
			await util.send_failure(ctx, f"{ctx.author.mention}: **Anti Raid Not Setup**")

	@antiraid.command(name='clear', description='clear anti raid status', usage='administrator')
	@commands.has_permissions(administrator=True)
	async def aaclear(self, ctx):
		try:
			self.bot.cache.antiraid_joins.update({ctx.guild.id:0})
		except:
			pass
		#await self.bot.db.execute("""DELETE FROM joins WHERE guild_id = %s""", ctx.guild.id)
		await util.send_success(ctx, f"{ctx.author.mention}: **Raid Status Cleared**")


async def setup(bot):
	await bot.add_cog(antievents(bot))
