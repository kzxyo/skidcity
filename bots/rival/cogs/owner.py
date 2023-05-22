import asyncio,importlib,inspect,ast,collections,io,time,contextlib
import arrow
import discord, typing
from discord.ext import commands
import datetime
import collections
from modules import log, util, default, statusbuttons, botactivity

import logging
logger = logging.getLogger(__name__)


class Owner(commands.Cog):
	"""Bot owner only"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "👑"
		self.color=0x303135
		self.mirror=collections.defaultdict(dict)

	@commands.Cog.listener()
	async def on_message(self, message):
		if not message.guild:
			return
		if message.guild.id in self.mirror:
			if message.author.bot:
				return
			gchannel=self.mirror[message.guild.id]
			channel=self.bot.get_channel(gchannel)
			embed = discord.Embed(description=message.content)
			embed.set_author(name=message.author, icon_url=message.author.display_avatar)
			if message.attachments:
				embed.set_image(url=message.attachments[0].proxy_url)
			return await channel.send(embed=embed)

	async def cog_check(self, ctx):
		"""Check if command author is Owner."""
		return await self.bot.is_owner(ctx.author)

	async def geninvite(self, guild_id):
		guild=self.bot.get_guild(guild_id)
		for channel in guild.text_channels:
			try:
				invite=await channel.create_invite()
				return invite
			except:
				pass	

	@commands.command(name='globalban',description='globally ban a user from all guilds', aliases=['gban'], brief='user')
	async def globalban(self, ctx, user:typing.Union[discord.Member,discord.User]):
		if isinstance(user, discord.Member):
			if user.id not in self.bot.cache.globalban:
				await self.bot.db.execute("""INSERT INTO globalban VALUES(%s,%s) ON DUPLICATE KEY UPDATE admin = VALUES(admin)""",user.id,ctx.author.id)
				self.bot.cache.globalban.append(user.id)
				for g in user.mutual_guilds:
					try:
						await g.ban(discord.Object(user.id))
					except:
						pass
				return await util.send_good(ctx, f"{str(user)} **banned globally**")
			else:
				await self.bot.db.execute("""DELETE FROM globalban WHERE user_id = %s""", user.id)
				await util.send_good(ctx, f"{str(user)} **unbanned globally**")
				self.bot.cache.globalban.remove(user.id)
				return
		elif isinstance(user, discord.User):
			u=self.bot.get_user(user.id)
			if not u:
				u=await self.bot.fetch_user(user.id)
			if user.id not in self.bot.cache.globalban:
				await self.bot.db.execute("""INSERT INTO globalban VALUES(%s,%s) ON DUPLICATE KEY UPDATE admin = VALUES(admin)""",user.id,ctx.author.id)
				self.bot.cache.globalban.append(user.id)
				return await util.send_good(ctx, f"{str(u)} **banned globally**")
			else:
				await self.bot.db.execute("""DELETE FROM globalban WHERE user_id = %s""", user.id)
				await util.send_good(ctx, f"{str(u)} **unbanned globally**")
				self.bot.cache.globalban.remove(user.id)
				return

	@commands.command(name='reloadutils', aliases=['rlu'])
	async def reloadutils(self, ctx, name: str):
		""" Reloads a utils module. """
		name_maker = f"modules/{name}.py"
		module_name = importlib.import_module(f"modules.{name}")
		importlib.reload(module_name)
		await ctx.send(f"Reloaded module **{name_maker}**")

	@commands.command(name='shardguilds')
	async def shardguilds(self,ctx,shard:int):
		membercount = len(list(self.bot.get_all_members()))
		gs=[guild for guild in self.bot.guilds if guild.shard_id == shard]
		mc=[len(guild.members) for guild in self.bot.guilds if guild.shard_id == shard]
		content = discord.Embed(
			title=f"Total **{len(gs)}** guilds, **{sum(mc)}** unique users On **Shard {shard}**", color=0x303135
		)
		rows = []
		for i, (guild) in enumerate(
			sorted(gs, key=lambda x: x.member_count or 0, reverse=True), start=1
		):
		#for guild in sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True):
			g=self.bot.get_guild(guild.id)
			rows.append(f"[{i}](https://solo.to/fry) {discord.utils.escape_markdown(g.name)} ・ {g.member_count} members ID: \n`{g.id}` - {discord.utils.escape_markdown(str(g.owner))}\n")
			#except:
			#	rows.append(f"[{i}](https://solo.to/fry) {g.name} ・ {g.member_count} members ID: \n`{g.id}` - `{g.owner}`\n")

		await util.send_as_pages(ctx, content, rows, 10, 2000)


	@commands.command(name='mirror')
	async def mirror(self, ctx, guild:int):
		if guild in self.mirror:
			del self.mirror[guild]
			await ctx.reply(embed=discord.Embed(description=f"no longer mirroring {guild}", color=0x303135))
		else:
			self.mirror[guild]=ctx.channel.id
			await ctx.reply(embed=discord.Embed(description=f"now mirror all messages from {guild}", color=0x303135))

	@commands.command(name='spam')
	async def spam(self, ctx, times:int, *, content:str=None):
		for i in range(times):
			await ctx.send(content)

	@commands.command(name='ghostping')
	async def ghostping(self, ctx, times:int, *, content:str=None):
		for i in range(times):
			await ctx.send(content)
		def predicate(m):
			return m.author.bot or m.content.startswith(f"{ctx.prefix}") or m.content == content
		await ctx.message.delete()
		deleted=await util.do_removal(ctx, 30, predicate)

	@commands.command(name='botstatus')
	async def botstatus(self, ctx, *, status:str="!help"):
		msg=await ctx.send(embed=discord.Embed(color=0x303135, description="What activity would you like to use?"))
		confirmed:int = await botactivity.confirm(self, ctx, msg)
		stat=None
		if confirmed==0:
			stat="Playing "
		elif confirmed==2:
			stat="Listening to "
		elif confirmed==3:
			stat="Watching "
		elif confirmed==5:
			stat="Competing In "
		else:
			stat="Streaming "
		confirm:int = await statusbuttons.confirm(self, ctx, msg)
		if confirm == 0:
			statu=discord.Status.online
		elif confirm == 1:
			statu=discord.Status.idle
		elif confirm == 2:
			statu=discord.Status.dnd
		elif confirm == 3:
			statu= discord.Status.offline
		else:
			statu=discord.Status.idle
		await msg.edit(embed=discord.Embed(description="what status?"))
		if confirmed==1:
			await msg.edit(view=None, embed=discord.Embed(color=0x303135, description=f"**Status Changed to** `{stat}{status}`"))
			await self.bot.change_presence(status=statu,activity=discord.Activity(type=confirmed, name=status, url="https://www.youtube.com/watch?v=kgjIEVAFGrA"))
		else:
			await msg.edit(view=None, embed=discord.Embed(color=0x303135, description=f"**Status Changed to** `{stat}{status}`"))
			await self.bot.change_presence(status=statu,activity=discord.Activity(type=confirmed, name=status))

	@commands.command()
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def guilds(self, ctx):
		"""Show all connected guilds."""
		membercount = len(list(self.bot.get_all_members()))
		content = discord.Embed(
			title=f"Total **{len(self.bot.guilds)}** guilds, **{membercount}** unique users", color=0x303135
		)
		rows = []
		for i, (guild) in enumerate(
			sorted(self.bot.guilds, key=lambda x: x.member_count or 0, reverse=True), start=1
		):
		#for guild in sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True):
			g=self.bot.get_guild(guild.id)
			rows.append(f"[{i}](https://solo.to/fry) {discord.utils.escape_markdown(g.name)} ・ {g.member_count} members ID: \n`{g.id}` - {discord.utils.escape_markdown(str(g.owner))}\n")
			#except:
			#	rows.append(f"[{i}](https://solo.to/fry) {g.name} ・ {g.member_count} members ID: \n`{g.id}` - `{g.owner}`\n")

		await util.send_as_pages(ctx, content, rows, 10, 2000)

	@commands.command()
	async def reset(self, ctx, member:typing.Union[discord.Member, discord.User]):
		if isinstance(member, discord.Member):
			try:
				await self.bot.db.execute("""DELETE FROM nodata WHERE user_id = %s""", member.id)
			except:
				pass
			return await util.send_good(ctx, f"successfully reset {member.mention}")
		else:
			user=await self.bot.fetch_user(member.id)
			try:
				await self.bot.db.execute("""DELETE FROM nodata WHERE user_id = %s""", user.id)
			except:
				pass
			return await util.send_good(ctx, f"successfully reset {user.name}#{user.discriminator}")

	@commands.command()
	async def sync(self, ctx):
		await self.bot.tree.sync()
		await util.send_success(ctx, "successfully synced all guilds")

	@commands.command(name='getserver')
	async def getserver(self, ctx, *, guild: typing.Union[int, str]=None):
		"""Lists some info about the current or passed server."""
		
		# Check if we passed another guild
		#guild=ctx.guild
		if guild==None:
			guild = ctx.guild
		else:
			if isinstance(guild, int):
				guild=self.bot.get_guild(guild)
			if isinstance(guild, str):
				for g in self.bot.guilds:
					if g.name.lower() == guild_name.lower():
						guild = g
						break
					if str(g.id) == str(guild_name):
						guild = g
						break
				if guild == None:
					await ctx.send("I couldn't find that guild...")
					return
		
		server_embed = discord.Embed(color=0x303135).set_thumbnail(url=guild.icon)
		server_embed.title = guild.name
		last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
		if last_boost.premium_since is not None:
			bboost = (f"`{last_boost}` - {discord.utils.format_dt(last_boost.premium_since, style='R')}")
		else:
			bboost = "No active boosters"

		gcreated=guild.created_at
		
		server_embed.description = f"Server Created {discord.utils.format_dt(guild.created_at, style='R')}\n{bboost}"
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
		server_embed.add_field(name='Invite', value=await self.geninvite(guild.id))
		server_embed.add_field(name="Members", value=user_string+total_users, inline=True)
		server_embed.add_field(name="Info", value=f"**Verification: **{guild.verification_level}\n**Level:** {bcount}\n**Large:** {guild.large}", inline=True)
		server_embed.add_field(name="Design", value=f"{icon}\n{banner}\n{splash}", inline=True)
		chandesc = "**Categories:** {:,}\n**Text:** {:,}\n**Voice:** {:,} ".format(len(guild.text_channels), len(guild.voice_channels), len(guild.categories))
		server_embed.add_field(name=f"Channels({total_count})", value=chandesc, inline=True)
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
		


	@commands.command(name='fetchguild')
	async def fetchguild(self, ctx, id:int):
		output = ''
		guild = self.bot.get_guild(id)
		if not guild:
			return await ctx.send("Unkown Guild ID. This is likely caused by me not being in the specified guild id.")
		gn = guild.name
		gi = str(guild.id)
		gm = str(len(guild.members))
		go = str(guild.owner)
		invite=await self.geninvite(id)
		output += f'Name: `{gn}`\nID: `{gi}`\nMembers: `{gm}`\nOwner: `{go}`\nInvite: [Here]({invite})'
		embed = discord.Embed(
			colour=self.color,
			title=f'Guild Info For ID: {id}',
			description=output,
			timestamp=ctx.message.created_at
		)
		await ctx.send(embed=embed)

	@commands.command()
	async def findguild(self, ctx, *, search_term):
		"""Find a guild by name."""
		rows = []
		for guild in sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True):
			if search_term.lower() in guild.name.lower():
				rows.append(f"{guild.name} | {guild.member_count} members ID: \n`{guild.id}`\n")

		content = discord.Embed(title=f"Found **{len(rows)}** guilds matching search term")
		await util.send_as_pages(ctx, content, rows)

	@commands.command(aliases=['mutuals', 'mutual'])
	async def userguilds(self, ctx, user: discord.User):
		"""Get all guilds user is part of."""
		rows = []
		for guild in sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True):
			guildmember = guild.get_member(user.id)
			if guildmember is not None:
				rows.append(f"[`{guild.id}`] **{guild.member_count}** members : **{guild.name}**")

		content = discord.Embed(title=f"User **{user}** found in **{len(rows)}** guilds")
		if rows:
			await util.send_as_pages(ctx, content, rows)
		else:
			return await util.send_failure(ctx, f"{ctx.author.mention}: **no mutuals found for {user}**")

	@commands.command(hidden=True)
	async def eventstats(self, ctx: commands.Context):
		"""See bot stats"""
		content = discord.Embed(
			title="Events since last reboot",
			description="",
			color=int("5c913b", 16),
		)
		for event, count in self.bot.cache.event_triggers.items():
			content.description += f"\n`on_{event}`: **{count}**"
		await ctx.send(embed=content)

	@commands.command(name='guildinvite')
	async def guildinvite(self, ctx, guild:int):
		invite=await self.geninvite(guild)
		await ctx.reply(invite)

	@commands.group(aliases=["donor"], case_insensitive=True)
	async def donator(self, ctx):
		"""Manage sponsors and donations."""
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@donator.command(name="add")
	async def donator_add(self, ctx, user: typing.Union[discord.User,discord.Member], since_ts=None):
		"""Add a new monthly donator."""
		if isinstance(user, discord.User):
			if since_ts is None:
				since_ts = arrow.utcnow().datetime
			else:
				since_ts = arrow.get(since_ts).datetime
			if await self.bot.db.execute("""SELECT * FROM dnr WHERE user_id = %s""", user.id):
				return await ctx.reply(embed=discord.Embed(description=f"user is already donator"))
			await self.bot.db.execute(
				"INSERT INTO dnr (user_id, ts) VALUES (%s, %s)",
				user.id,
				datetime.datetime.now(),
			)
			self.bot.cache.donators.append(user.id)
			return await util.send_success(ctx, f"Added Donator to **{user}**")
		if isinstance(user, discord.Member):
			if since_ts is None:
				since_ts = arrow.utcnow().datetime
			else:
				since_ts = arrow.get(since_ts).datetime
			if await self.bot.db.execute("""SELECT * FROM dnr WHERE user_id = %s""", user.id):
				return await ctx.reply(embed=discord.Embed(description=f"user is already donator"))

			await self.bot.db.execute(
				"INSERT INTO dnr (user_id, ts) VALUES (%s, %s)",
				user.id,
				datetime.datetime.now(),
			)
			self.bot.cache.donators.append(user.id)
			return await util.send_success(ctx, f"Donator Added To **{util.displayname(user)}**")

	@donator.command(name="remove")
	async def donator_remove(self, ctx, user: discord.User):
		"""Remove a donator."""
		await self.bot.db.execute("DELETE FROM dnr WHERE user_id = %s", user.id)
		self.bot.cache.donators.remove(user.id)
		await util.send_success(ctx, f"Removed Donator From **{user}**.")

	@commands.command(name='flag', aliases=["fmban"])
	async def flag(self, ctx, lastfm_username, *, reason=None):
		if reason == None:
			reason="Play Botting"
		else:
			reason=reason
		await self.bot.db.execute(
			"INSERT INTO lastfm_cheater VALUES(%s, %s, %s)",
			lastfm_username.lower(),
			arrow.utcnow().datetime,
			reason,
		)
		await util.send_success(ctx, f"Flagged LastFM profile `{lastfm_username}` as a cheater.")

	@commands.command(name='unflag', aliases=["fmunban"])
	async def unflag(self, ctx, lastfm_username):
		await self.bot.db.execute(
			"DELETE FROM lastfm_cheater WHERE lastfm_username = %s", lastfm_username.lower()
		)
		await util.send_success(ctx, f"`{lastfm_username}` is no longer flagged as a cheater.")


def clean_codeblock(text):
	"""Remove codeblocks and empty lines, return lines."""
	text = text.strip(" `")
	lines = text.split("\n")
	clean_lines = []

	if lines[0] in ["py", "python"]:
		lines = lines[1:]

	for line in lines:
		if line.strip() != "":
			clean_lines.append(line)

	return clean_lines


async def setup(bot):
	await bot.add_cog(Owner(bot))
