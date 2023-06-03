import arrow, discord, humanize, datetime, asyncio, re, regex, requests, random, json, tempfile, shutil, os, typing,time
from discord.ext import commands
from pytz import timezone
from libraries import emoji_literals
import datetime,pytz
from datetime import timedelta
from typing import Union
from datetime import datetime
from typing import Union
from bs4 import BeautifulSoup
from modules import exceptions, log, queries, util, Message, DL, DisplayName, permissions
async def not_server_owner_msg(ctx, text=None):
	if text:
		text=text
	else:
		text="Guild Owner"
	embed = discord.Embed(
		description=f"{self.bot.warn} {ctx.author.mention}: this command can **only** be used by the `{text}`",
		colour=0xfaa61a,
	)
	return embed



class settingss(commands.Cog, name="settingss"):
	def __init__(self, bot):
		self.bot = bot
		self.url_regex = re.compile(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")
		self.keyword_regex = r"(?:^|\s|[\~\"\'\+\*\`\_\/])(\L<words>)(?:$|\W|\s|s)"
		self.add="<:plus:947812413267406848>"
		self.yes=self.bot.yes
		self.good=0xD6BCD0
		self.rem="<:rem:947812531509026916>"
		self.no=self.bot.no
		self.bad=0xD6BCD0
		self.color=self.bot.color
		self.ch='<:yes:940723483204255794>'
		self.error=0xD6BCD0
		self.perms=["add_reactions","administrator","attach_files","ban_members","change_nickname","deafen_members","embed_links","external_emojis","external_stickers","kick_members","manage_channels","manage_emojis","manage_emojis_and_stickers","manage_events","manage_guild","manage_messages","manage_nicknames","manage_permissions","manage_roles","manage_threads","manage_webhooks","moderate_members","move_members","mute_members"]
		self.admins={714703136270581841,822245516461080606, 420525168381657090, 956618986110476318,352190010998390796}
		self.warn=self.bot.warn
		self.cd_mapping = commands.CooldownMapping.from_cooldown(10, 10, commands.BucketType.member)
		self._cd = commands.CooldownMapping.from_cooldown(1, 7.0, commands.BucketType.member)

	def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		"""Returns the ratelimit left"""
		bucket = self._cd.get_bucket(message)
		return bucket.update_rate_limit()


	@commands.Cog.listener()	
	async def on_member_join(self, member):
		#if await self.bot.db.execute("SELECT * FROM abump WHERE guild_id = %s AND g_id = %s", member.guild.id,member.id):
			#return await member.guild.ban(member, reason="blacklisted member")
		try:
			if not member.avatar:
				#if await self.bot.db.execute("""SELECT * FROM antiraidav WHERE guild_id = %s""", member.guild.id):
				if member.guild.id in self.bot.cache.antiraid_av:
					return await member.kick(reason="Rival Anti Raid Triggered - No avatar Detected")
		except:
			if not member.avatar:
				#if await self.bot.db.execute("""SELECT * FROM antiraidav WHERE guild_id = %s""", member.guild.id):
				if member.guild.id in self.bot.cache.antiraid_av:
					return await member.kick(reason="Rival Anti Raid Triggered - No avatar Detected")
		if member.guild.id in self.bot.cache.antiraid_age:
			age=self.bot.cache.antiraid_age.get(member.guild.id)
			active=True
		else:
			age=False
			active=False
		#active=await self.bot.db.execute("""SELECT * FROM antiraid WHERE guild_id = %s""", member.guild.id)
		#ag=await self.bot.db.execute("""SELECT * FROM antiraid WHERE guild_id = %s""", member.guild.id)
		#await self.bot.db.execute("""INSERT INTO joins (guild_id) VALUES (%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", member.guild.id)
		if member.guild.id not in self.bot.cache.antiraid_joins:
			self.bot.cache.antiraid_joins[member.guild.id]=0
		self.bot.cache.antiraid_joins[member.guild.id]+=1
		#trig=await self.bot.db.execute("""SELECT * FROM antiraidtrigger WHERE guild_id = %s""", member.guild.id)
		if member.guild.id in self.bot.cache.antiraid_trigger:
			trig=self.bot.cache.antiraid_trigger.get(member.guild.id)
		else:
			trig=False
		if not trig:
			return
		#for guild_id, trigger in trig:
		trigger=trig
		joins=self.bot.cache.antiraid_joins[member.guild.id]
		#for guild_id, age in ag:
			#age=age
		#joins=await self.bot.db.execute("""SELECT amount FROM joins WHERE guild_id = %s""", member.guild.id, one_value=True)
		if not active:
			return
		else:
			if await self.bot.db.execute("""SELECT * FROM awhitelist WHERE guild_id = %s AND user_id = %s""", member.guild.id, member.id):
				return
			if joins > trigger:
				asyncio.sleep(1)
				return await member.kick(reason="Rival Anti Raid Triggered")
			if age:
				now=datetime.now()
				then=now.astimezone(pytz.utc)-timedelta(days=age)
				then_ts=int(round(then.timestamp()))
				account=member.created_at.astimezone(pytz.utc)
				account_ts=int(round(account.timestamp()))
				if account_ts >= then_ts:
					await asyncio.sleep(1)
					return await member.kick(reason="Rival Anti Raid Triggered - Account Age Too Young")

	@commands.group(name="settings", description="server configuration group", aliases=['configuration','config','setting'])
	async def settings(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)


	@settings.command(name='adminlock', aliases=['totallock','admindisconnect'], description="auto disconnect all unpermitted users from the vc", extras={'perms':'manage guild'}, brief='bool', usage='```Swift\nSyntax: !settings adminlock <bool>\nExample: !settings adminlock true```')
	@commands.has_permissions(manage_guild=True)
	async def settings_adminlock(self, ctx, state:bool):
		if state:
			if not ctx.guild.id in self.bot.cache.adminlock:
				self.bot.cache.adminlock.append(ctx.guild.id)
				await self.bot.db.execute("""INSERT INTO adminlock VALUES(%s)""", ctx.guild.id)
			return await util.send_good(ctx, f"voicemaster total lock **enabled**")
		else:
			if ctx.guild.id in self.bot.cache.adminlock:
				self.bot.cache.adminlock.remove(ctx.guild.id)
				await self.bot.db.execute("""DELETE FROM adminlock WHERE guild_id = %s""", ctx.guild.id)
			return await util.send_good(ctx, f"voicemaster total lock **disabled**")

	@settings.command(name='imageonly', aliases=['imgonly','io','ionly','image','img'], description='make a channel image only', extras={'perms':'Manage Guild'}, brief='state', usage='```Swift\nSyntax: !settings imageonly <state>\nExample: !settings imageonly true```')
	@commands.has_permissions(manage_guild=True)
	async def settings_imageonly(self, ctx, state:bool):
		if state:
			if not ctx.channel.id in self.bot.cache.image_only:
				self.bot.cache.image_only.append(ctx.channel.id)
			await self.bot.db.execute("""INSERT INTO imgonly VALUES(%s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)""", ctx.channel.id)
			return await util.send_good(ctx, f"{ctx.channel.mention} is now **image-only**")
		else:
			if ctx.channel.id in self.bot.cache.image_only:
				self.bot.cache.image_only.remove(ctx.channel.id)
			await self.bot.db.execute("""DELETE FROM imgonly WHERE channel_id = %s""", ctx.channel.id)
			return await util.send_good(ctx, f"{ctx.channel.mention} is no longer **image-only**")

	@settings.command(name='tiktok', aliases=['tiktokembed','embed','tt'], description="auto embed tiktok links", extras={'perms':'Manage_Guild'}, usage="```Swift\nSyntax: !settings tiktok <state>\nExample: !settings tiktok true```", brief="bool")
	@commands.has_permissions(manage_guild=True)
	@util.donor_server()
	async def settings_tiktok(self, ctx, state:bool):
		if state:
			if not await self.bot.db.execute("""SELECT * FROM autoembed WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""INSERT INTO autoembed VALUES(%s)""", ctx.guild.id)
			if not ctx.guild.id in self.bot.cache.autoembed:
				self.bot.cache.autoembed.append(ctx.guild.id)
			return await util.send_good(ctx, f"successfully `enabled` tiktok embedding")
		else:
			if ctx.guild.id in self.bot.cache.autoembed:
				self.bot.cache.autoembed.remove(ctx.guild.id)
			if await self.bot.db.execute("""SELECT * FROM autoembed WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM autoembed WHERE guild_id = %s""", ctx.guild.id)
			return await util.send_good(ctx, f"successfully `disabled` tiktok embedding")

	@settings.command(name='banembed', aliases=['banmessage'], description='set a custom ban embed', extras={'perms':'manage guild'}, usage='```Swift\nSyntax: !settings banembed <embed>\nExample: !settings banembed {embed}{description: you have been banned by {moderator}}```')
	@commands.has_permissions(manage_guild=True)
	async def settings_banembed(self, ctx, *, message):
		cl=['clear','none','disable','delete','remove']
		if message.lower() in cl:
			await self.bot.db.execute("""DELETE FROM ban_message WHERE guild_id = %s""", ctx.guild.id)
			await util.send_good(ctx, f"successfully **cleared** your ban message")
		else:
			await self.bot.db.execute("""INSERT INTO ban_message VALUES(%s,%s) ON DUPLICATE KEY UPDATE message = VALUES(message)""", ctx.guild.id, message)
			await util.send_good(ctx, f"successfully set your **ban embed**")
	@settings.command(name='bumpreminder', aliases=['br', 'bumpremind'], description='enable or disable bump reminder', usage="```Swift\nSyntax: !settings bumpreminder <bool>\nExample: !settings bumpreminder true```",extras={'perms': 'manage guild'}, brief='state:bool')
	@commands.has_permissions(manage_guild=True)
	async def settings_bumpreminder(self, ctx, state:bool):
		if state:
			await self.bot.db.execute("""INSERT INTO bumpstate (guild_id) VALUES(%s) ON DUPLICATE KEY UPDATE guild_id = VALUES(guild_id)""", ctx.guild.id)
			return await util.send_good(ctx, "**Enabled `bump reminding` service!**")
		else:
			await self.bot.db.execute("""DELETE FROM bumpstate WHERE guild_id = %s""", ctx.guild.id)
			return await util.send_good(ctx, "**Disabled `bump reminding` service!**")

	@settings.command(name='snipe', aliases=['filtersnipes','filtersnipe', 'snipes','snipefilter','snipefiltering'], description='enable or disable snipe filtering', usage="```Swift\nSyntax: !settings snipe <bool>\nExample: !settings snipe true```",extras={'perms': 'manage guild'}, brief='state:bool')
	@commands.has_permissions(manage_guild=True)
	async def settings_snipe(self, ctx, state:bool):
		if state:
			await self.bot.db.execute("""DELETE FROM filtersnipes WHERE guild_id = %s""", ctx.guild.id)
			if ctx.guild in self.bot.cache.filter_snipes:
				self.bot.cache.filter_snipes.remove(ctx.guild.id)
			return await util.send_good(ctx, "snipe filtering `enabled`")
		else:
			if ctx.guild.id not in self.bot.cache.filter_snipes:
				self.bot.cache.filter_snipes.append(ctx.guild.id)
			await self.bot.db.execute("""INSERT INTO filtersnipes (guild_id) VALUES(%s) ON DUPLICATE KEY UPDATE guild_id = VALUES(guild_id)""", ctx.guild.id)
			return await util.send_good(ctx, "snipe filtering `disabled`")

	@settings.command(name="levels", aliases=['lvls','lvl','level'], description="enable or disable guild leveling", extras={'perms':'manage_guild'}, brief="state", usage="```Swift\nSyntax: !settings levels <bool>\nExample: !settings levels on```")
	@commands.has_permissions(manage_guild=True)
	async def settings_levels(self, ctx, state:bool):
		if state:
			if await self.bot.db.execute("""SELECT * FROM leveling WHERE guild_id = %s""", ctx.guild.id):
				return await util.send_error(ctx, f"leveling already `enabled`")
			else:
				await self.bot.db.execute("""INSERT INTO leveling VALUES(%s)""", ctx.guild.id)
				return await util.send_good(ctx, f"guild leveling `enabled`")
		else:
			if await self.bot.db.execute("""SELECT * FROM leveling WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM leveling WHERE guild_id = %s""", ctx.guild.id)
			return await util.send_good(ctx, f"guild leveling `disabled`")

	@settings.command(name='googlesafe',aliases=['gs','safesearch','safe','ss'], brief='state:bool', extras={'perms': 'manage_guild'}, usage="```Swift\nSyntax: !safesearch <bool>\nExample: !safesearch true```",description='toggle safe search with google commands')
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	async def googlesafe(self, ctx, value:bool):
		true=['true', 'TRUE', 'True', 'on', 'On', 'ON']
		false=['false', 'False', 'FALSE', 'off', 'Off', 'OFF']
		await queries.update_setting(ctx, "guild_settings", "googlesafe", value)
		self.bot.cache.googlesafe[str(ctx.guild.id)] = value
		if value:
			await util.send_good(ctx, f"googlesafe is now `on`")
		else:
			await util.send_good(ctx, f"googlesafe is now `off`")

	@settings.command(name="levelmessages", aliases=['lvlmsgs','levelmsgs','lvlmsg','levelmessage','levelmsg','levelup','lvlup'],extras={'perms':'manage_guild'}, description="enable or disable level up messages", usage="```Swift\nSyntax: !settings levelmessages <bool>\nExample: !settings levelmessages on```", brief="state")
	@commands.has_permissions(manage_guild=True)
	async def settings_levelmessages(self, ctx, state: bool):
		await queries.update_setting(ctx, "guild_settings", "levelup_messages", state)
		self.bot.cache.levelupmessage[str(ctx.guild.id)] = state
		if state:
			await util.send_good(ctx, "Level up messages are now `enabled`")
		else:
			await util.send_good(ctx, "Level up messages are now `disabled`")

	@settings.command(name="bandm", description="toggle user getting a dm upon banning", aliases=['moddm', 'autodm'],extras={'perms': 'manage guild'}, brief="state", usage="```Swift\nSyntax: !settings moddm <bool>\nExample: !settings moddm true```")
	@commands.has_permissions(manage_guild=True)
	async def settings_bandm(self, ctx, state:bool):
		if state:
			if await self.bot.db.execute("""SELECT * FROM moddm WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM moddm WHERE guild_id = %s""", ctx.guild.id)
			status="enabled"
		else:
			if not await self.bot.db.execute("""SELECT * FROM moddm WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""INSERT INTO moddm VALUES(%s)""", ctx.guild.id)
			status="disabled"
		await util.send_good(ctx, f"Ban DMs are now `{status}`")

	@settings.command(name="confirmations", description="toggle moderator confirmations", aliases=['confirm', 'confirmation'],extras={'perms': 'manage guild'}, brief="state", usage="```Swift\nSyntax: !settings confirmations <bool>\nExample: !settings confirmations true```")
	@commands.has_permissions(manage_guild=True)
	async def settings_confirmations(self, ctx, state:bool):
		if state:
			if await self.bot.db.execute("""SELECT * FROM confirmations WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""DELETE FROM confirmations WHERE guild_id = %s""", ctx.guild.id)
			status="enabled"
		else:
			if not await self.bot.db.execute("""SELECT * FROM confirmations WHERE guild_id = %s""", ctx.guild.id):
				await self.bot.db.execute("""INSERT INTO confirmations VALUES(%s)""", ctx.guild.id)
			status="disabled"
		await util.send_good(ctx, f"Moderation Confirmations are now `{status}`")

	@settings.command(name='antinuke',description="Returns Current Server Anti Settings",aliases=['anti', 'an'], extras={'perms':'Guild Owner / Anti Admin'})
	async def settings_antinuke(self, ctx: commands.Context):
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


async def setup(bot):
	await bot.add_cog(settingss(bot))