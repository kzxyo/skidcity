import asyncio,logging,discord,datetime,arrow,pickle
from rival_redis import *
from rival_redis import get_redis
from contextlib import suppress
from async_rediscache import RedisCache
from discord.ext.commands import Cog, Context, command
from modules import log
import logging
logger = logging.getLogger(__name__)
log.get_logger(__name__)

class RedisCache:
	def __init__(self, bot):
		self.bot = bot
		self.log_emoji = False
		self.prefixes = {}
		self.prefixess = {}
		self.redis=get_redis()
		self.rolepickers = set()
		self.votechannels = set()
		self.googlesafe = {}
		self.tags=[]
		self.vm_locked=[]
		self.blacklist = {}
		self.autoresponses = {}
		self.autoreacts = {}
		self.apikeys = []
		self.chatfilter = {}
		self.levelupmessage = {}
		self.global_bl = {}
		self.whitelist = {}
		self.welcomechannels = {}
		self.exempt=[]
		self.welcomemessages = {}
		self.lastfm = {}
		self.autoreact = {}
		self.autoembed = []
		self.api_access_address=[]
		self.lastfm_embeds = {}
		self.filter_snipes=[]
		self.donators = []
		self.antinuke = {}
		self.whitelist = {}
		self.punishment = {}
		self.delete = []
		self.threshold = {}
		self.logging_settings = {}
		self.autoroles = {}
		self.afk={}
		self.marriages = set()
		self.starboard_settings = {}
		self.starboard_blacklisted_channels = set()
		self.event_triggers = {
			"message": 0,
			"message_delete": 0,
			"message_edit": 0,
			"reaction_add": 0,
			"reaction_remove": 0,
			"member_join": 0,
			"member_remove": 0,
			"guild_join": 0,
			"guild_remove": 0,
			"member_ban": 0,
			"member_unban": 0,
		}
		self.stats_notifications_sent = 0
		self.stats_lastfm_requests = 0
		self.stats_html_rendered = 0
		#bot.loop.create_task(self.initialize_settings_cache())

	async def cache_starboard_settings(self):
		data = await self.bot.db.execute(
			"""
			SELECT guild_id, is_enabled, channel_id, reaction_count,
				emoji_name, emoji_id, emoji_type, log_channel_id
			FROM starboard_settings
			"""
		)
		if not data:
			return
		for (
			guild_id,
			is_enabled,
			channel_id,
			reaction_count,
			emoji_name,
			emoji_id,
			emoji_type,
			log_channel_id,
		) in data:
			self.starboard_settings[str(guild_id)] = [
				is_enabled,
				channel_id,
				reaction_count,
				emoji_name,
				emoji_id,
				emoji_type,
				log_channel_id,
			]

		self.starboard_blacklisted_channels = set(
			await self.bot.db.execute(
				"SELECT channel_id FROM starboard_blacklist",
				as_list=True,
			)
		)

	async def cache_logging_settings(self):
		logging_settings = await self.bot.db.execute(
			"""
			SELECT guild_id, member_log_channel_id, ban_log_channel_id, message_log_channel_id
			FROM logging_settings
			"""
		)
		for (
			guild_id,
			member_log_channel_id,
			ban_log_channel_id,
			message_log_channel_id,
		) in logging_settings:
			self.logging_settings[str(guild_id)] = {
				"member_log_channel_id": member_log_channel_id,
				"ban_log_channel_id": ban_log_channel_id,
				"message_log_channel_id": message_log_channel_id,
			}

	async def cache_autoroles(self):
		for guild_id, role_id in await self.bot.db.execute(
			"SELECT guild_id, role_id FROM autorole"
		):
			try:
				self.autoroles[str(guild_id)].add(role_id)
			except KeyError:
				self.autoroles[str(guild_id)] = set([role_id])

	async def initialize_settings_cache(self):
		self.bot.logger.info("Caching settings...")
		prefixes = await self.bot.db.execute("SELECT user_id, prefix FROM guild_prefix")
		wl=await self.bot.db.execute("""SELECT guild_id, user_id FROM whitelist""")
		execs=await self.bot.db.execute("""SELECT guild_id FROM exempt""")
		wlcmsgs=await self.bot.db.execute("""SELECT guild_id,message FROm wlcmsg""")
		wlcchannels=await self.bot.db.execute("""SELECT guild_id,channel_id FROM welcome""")
		anti=await self.bot.db.execute("""SELECT guild_id, ban, kick, role, channel, webhook, vanity FROM antinuke""")
		punishments=await self.bot.db.execute("""SELECT guild_id, punishment FROM punishment""")
		cfs=await self.bot.db.execute("""SELECT guild_id,strr from chatfilter""")
		ars=await self.bot.db.execute("SELECT guild_id,command_trigger, content FROM custom_command")
		reacs=await self.bot.db.execute("SELECT guild_id, trig, content FROM react")
		ae=await self.bot.db.execute("""SELECT guild_id FROM autoembed""")
		afks=await self.bot.db.execute("""SELECT user_id,reason,ts FROM afks""")
		lfs = await self.bot.db.execute("SELECT user_id,lastfm_username FROM user_settings""")
		lfme=await self.bot.db.execute("""SELECT user_id,message FROM last_fm_embed""")
		keys=await self.bot.db.execute("""SELECT * FROM apikeys""")
		#imgonly=await self.bot.db.execute("""SELECT channel_id FROM imgonly""")
		filters=await self.bot.db.execute("""SELECT * from filtersnipes""")
		for key in keys:
			self.apikeys.append(str(key[0]))
		for guild_id in execs:
			self.exempt.append(int(str(guild_id[0])))
		for guild_id in filters:
			self.filter_snipes.append(int(guild_id[0]))
		#for channel_id in imgonly:
			#self.image_only.append(int(channel_id[0]))
		for user_id,message in lfme:
			#self.lastfm_embeds[int(str(user_id))]=str(message)
			self.redis.set(f"{user_id}_lastfm", message)
		for guild_id in ae:
			self.autoembed.append(int(str(guild_id[0])))
		for user_id,lastfm_username in lfs:
			if lastfm_username != None:
				self.lastfm[int(str(user_id))]=str(lastfm_username)
		for guild_id,message in wlcmsgs:
			self.welcomemessages[int(str(guild_id))]=message
		for guild_id,channel_id in wlcchannels:
			self.welcomechannels[int(str(guild_id))]=int(str(channel_id))
		for guild_id,trig,content in reacs:
			if str(guild_id) not in self.autoreacts:
				self.autoreacts[str(guild_id)]={}
			self.autoreacts[str(guild_id)][str(trig)]=str(content)
		for guild_id,command_trigger,content in ars:
			if str(guild_id) not in self.autoresponses:
				self.autoresponses[str(guild_id)]={}
			self.autoresponses[str(guild_id)][str(command_trigger)]=str(content)
		for guild_id,strr in cfs:
			if str(guild_id) not in self.chatfilter:
				self.chatfilter[str(guild_id)]=[]
			self.chatfilter[str(guild_id)].append(str(strr))
		thresholds=await self.bot.db.execute("""SELECT guild_id, ban, kick, webhook, role, channel, vanity, asset FROM antinuke_thresholds""")
		for guild_id,user_id in wl:
			if str(guild_id) not in self.whitelist:
				self.whitelist[str(guild_id)]=set()
			self.whitelist[str(guild_id)].add(int(user_id))
		for guild_id,ban,kick,webhook,role,channel,vanity,asset in thresholds:
			self.threshold[str(guild_id)]={'ban':ban,'kick':kick,'webhook':webhook,'role':role,'channel':channel,'vanity':vanity,'asset':asset}
		for guild_id,punishment in punishments:
			self.punishment[str(guild_id)]=int(punishment)
		for user_id,reason,ts in afks:
			self.afk[int(str(user_id))]={'reason':reason,'ts':ts}
		for guild_id,ban,kick,role,channel,webhook,vanity in anti:
			self.antinuke[str(guild_id)]={"ban":ban,"kick":kick,"channel":channel,"role":role,"webhook":webhook,"vanity":vanity}
		for user_id, prefix in prefixes:
			self.prefixes[str(user_id)] = prefix
		prefixess = await self.bot.db.execute("SELECT guild_id, prefix FROM guild_prefixx")
		for guild_id, prefix in prefixess:
			self.prefixess[str(guild_id)] = prefix
		guild_settings = await self.bot.db.execute(
			"SELECT guild_id, googlesafe, levelup_messages FROM guild_settings"
		)
		for guild_id, googlesafe, levelup_messages in guild_settings:
			self.googlesafe[str(guild_id)] = googlesafe
			self.levelupmessage[str(guild_id)] = levelup_messages
		try:
			delete=await self.bot.db.execute("""SELECT guild_id FROM delete""")
			if delete:
				for guild_id in delete:
					self.delete.append(guild_id)
		except:
			pass

		self.blacklist = {
			"global": {
				"user": set(
					await self.bot.db.execute("SELECT user_id FROM blacklisted_user", as_list=True)
				),
				"guild": set(
					await self.bot.db.execute(
						"SELECT guild_id FROM blacklisted_guild", as_list=True
					)
				),
				"channel": set(
					await self.bot.db.execute(
						"SELECT channel_id FROM blacklisted_channel", as_list=True
					)
				),
			}
		}

		self.marriages = [
			set(pair)
			for pair in await self.bot.db.execute(
				"SELECT first_user_id, second_user_id FROM marriage"
			)
		]

		for guild_id, user_id in await self.bot.db.execute(
			"SELECT guild_id, user_id FROM blacklisted_member"
		):
			try:
				self.blacklist[str(guild_id)]["member"].add(user_id)
			except KeyError:
				self.blacklist[str(guild_id)] = {"member": {user_id}, "command": set()}

		for guild_id, command_name in await self.bot.db.execute(
			"SELECT guild_id, command_name FROM blacklisted_command"
		):
			try:
				self.blacklist[str(guild_id)]["command"].add(command_name.lower())
			except KeyError:
				self.blacklist[str(guild_id)] = {
					"member": set(),
					"command": {command_name.lower()},
				}

		await self.cache_starboard_settings()
		await self.cache_logging_settings()
		await self.cache_autoroles()

	async def main(self):
	    session = async_rediscache.RedisSession()
	    await session.connect()
	    
