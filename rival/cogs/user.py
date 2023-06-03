import asyncio
import typing

import arrow,datetime
import bleach
import discord, difflib
import nekos
import humanize
from discord.ext import commands
from typing import Union

from libraries import plotter
from modules import emojis, exceptions, queries, util, confirmation

def prepend(list, str):
		# Using format()
	str += '{0}'
	list = [str.format(i) for i in list]
	return(list)

class User(commands.Cog):
	"""User related commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "👤"
		self.color=self.bot.color
		self.proposals = set()
		self.medal_emoji = [":first_place:", ":second_place:", ":third_place:"]
		
	async def get_rank(self, user, table="user_activity", guild=None):
		"""Get user's xp ranking from given table."""
		if guild is None:
			total, pos = (
				await self.bot.db.execute(
					f"""
					SELECT (SELECT COUNT(DISTINCT(user_id)) FROM {table} WHERE not is_bot),
					ranking FROM (
						SELECT RANK() OVER(ORDER BY xp DESC) AS ranking, user_id,
							SUM(h0+h1+h2+h3+h4+h5+h6+h7+h8+h9+h10+h11+h12+h13+h14+h15+h16+h17+h18+h19+h20+h21+h22+h23) as xp
						FROM {table}
						WHERE not is_bot
						GROUP BY user_id
					) as sub
					WHERE user_id = %s
					""",
					user.id,
					one_row=True,
				)
				or (None, None)
			)

		else:
			total, pos = (
				await self.bot.db.execute(
					f"""
					SELECT (SELECT COUNT(user_id) FROM {table} WHERE not is_bot AND guild_id = %s),
					ranking FROM (
						SELECT RANK() OVER(ORDER BY xp DESC) AS ranking, user_id,
							SUM(h0+h1+h2+h3+h4+h5+h6+h7+h8+h9+h10+h11+h12+h13+h14+h15+h16+h17+h18+h19+h20+h21+h22+h23) as xp
						FROM {table}
						WHERE not is_bot
						AND guild_id = %s
						GROUP BY user_id
					) as sub
					WHERE user_id = %s
					""",
					guild.id,
					guild.id,
					user.id,
					one_row=True,
				)
				or (None, None)
			)

		if pos is None or total is None:
			return "N/A"
		return f"#{int(pos)} / {total}"


	async def geninvite(self, guild_id):
		guild=self.bot.get_guild(guild_id)
		for channel in guild.text_channels:
			try:
				invite=await channel.create_invite()
				return invite
			except:
				pass

	async def get_ranking(self, ctx, user):
		time, table = get_activity_table("alltime")
		data = await self.bot.db.execute(f"""
			SELECT user_id, SUM(h0+h1+h2+h3+h4+h5+h6+h7+h8+h9+h10+h11+h12+h13+h14+h15+h16+h17+h18+h19+h20+h21+h22+h23) as xp,
				message_count FROM {table}
			WHERE guild_id = %s AND NOT is_bot
			GROUP BY user_id ORDER BY xp DESC
			""",
			ctx.guild.id,
		)
		rows = []
		for i, (user_id, xp, message_count) in enumerate(data, start=1):
			if user_id == user.id:
				return f"#{i} out of {len(data)}"


	@commands.command(name='clearlevel', aliases=['clearlvl', 'clearlevels', 'clearlvls'], description="clear a member's level", extras={'perms':'manage_guild'}, brief="member", usage="```Swift\nSyntax: !clearlevel <member>\nExample: !clearlevel @cop#0001```")
	@commands.has_permissions(manage_guild=True)
	async def clearlevel(self, ctx, member:discord.Member):
		try:
			await self.bot.db.execute("""DELETE FROM user_activity WHERE user_id = %s AND guild_id = %s""",member.id,ctx.guild.id)
		except:
			pass
		await util.send_good(ctx, f"cleared {member.mention}'s level")

	@commands.command(name='setlevel', aliases=['setlvl', 'setlevels', 'setlvls'], description="set a member's level", extras={'perms':'manage_guild'}, brief="member", usage="```Swift\nSyntax: !setlevel <member> <level>\nExample: !setlevel @cop#0001 10```")
	@commands.has_permissions(manage_guild=True)
	async def setlevel(self, ctx, member:discord.Member, level:int):
		try:
			await self.bot.db.execute("""DELETE FROM user_activity WHERE user_id = %s AND guild_id = %s""",member.id,ctx.guild.id)
		except:
			pass
		values=[]
		currenthour = arrow.utcnow().hour
		xp=util.get_xp(level)
		values.append(
			(
			int(ctx.guild.id),
			int(member.id),
			False,
			xp,
			100,
			)
		)
		for activity_table in [
			"user_activity",
			"user_activity_day",
			"user_activity_week",
			"user_activity_month",
		]:
			await self.bot.db.executemany(
				f"""
				INSERT INTO {activity_table} (guild_id, user_id, is_bot, h{currenthour}, message_count)
				VALUES (%s, %s, %s, %s, %s)
				ON DUPLICATE KEY UPDATE
					h{currenthour} = h{currenthour} + VALUES(h{currenthour}),
					message_count = message_count + VALUES(message_count)
				""",
					values,
				)
		return await util.send_good(ctx, f"set {member.mention}'s level to `{level}`")

	@commands.command(name="leaderboard", aliases=['lb'], description="level leaderboard", brief="scope, timeframe", usage="```Swift\nSyntax: !leaderboard <scope> <timeframe>\nExample: !leaderboard global alltime```")
	async def leaderboard(self, ctx, scope="", timeframe=""):
		_global_ = scope == "global"
		if timeframe == "":
			timeframe = scope

		time, table = get_activity_table(timeframe)
		if _global_:
			data = await self.bot.db.execute(
				f"""
				SELECT user_id, SUM(h0+h1+h2+h3+h4+h5+h6+h7+h8+h9+h10+h11+h12+h13+h14+h15+h16+h17+h18+h19+h20+h21+h22+h23) as xp,
					SUM(message_count) FROM {table}
				WHERE NOT is_bot
				GROUP BY user_id ORDER BY xp DESC
				"""
			)
		else:
			data = await self.bot.db.execute(
				f"""
				SELECT user_id, SUM(h0+h1+h2+h3+h4+h5+h6+h7+h8+h9+h10+h11+h12+h13+h14+h15+h16+h17+h18+h19+h20+h21+h22+h23) as xp,
					message_count FROM {table}
				WHERE guild_id = %s AND NOT is_bot
				GROUP BY user_id ORDER BY xp DESC
				""",
				ctx.guild.id,
			)

		rows = []
		l=0
		for i, (user_id, xp, message_count) in enumerate(data, start=1):
			if _global_:
				user = self.bot.get_user(user_id)
			else:
				user = ctx.guild.get_member(user_id)

			if user is None:
				continue
			else:
				l+=1
			
			ranking = f"`{l}`"

			rows.append(
				f"{ranking} **{util.displayname(user)}** — "
				+ (f"LVL **{util.get_level(xp)}**, " if time == "" else "")
				+ f"**{xp}** XP, **{message_count}** message{'' if message_count == 1 else 's'}"
			)

		content = discord.Embed(
			color=self.color,
			title=f"{'Global' if _global_ else ctx.guild.name} {time}levels leaderboard",
		)

		if not rows:
			rows = ["No data."]

		await util.send_as_pages(ctx, content, rows)


	@commands.command(name="activity", description="See your hourly activity chart (GMT)", brief="member", usage="```Swift\nSyntax: !activity <user>\nExample: !activity @cop#0001```", aliases=["level", "lvl", "rank"])
	async def activity(self, ctx, user: typing.Optional[discord.Member] = None, scope=""):
		if user is None:
			user = ctx.author

		is_global = scope.lower() == "global"
		wright=str(self.bot.get_emoji(1005219842271498314))
		white=str(self.bot.get_emoji(1005219840723779604))
		wleft=str(self.bot.get_emoji(1005222349693521960))
		#bleft=str(self.bot.get_emoji(1005219832213557440))
		#blue=str(self.bot.get_emoji(1005219834361040976))
		#bright=str(self.bot.get_emoji(1005222500252262440))
		bleft=str(self.bot.get_emoji(1024113159419731988))
		blue=str(self.bot.get_emoji(1024114520878239825))
		bright=str(self.bot.get_emoji(1024112657176997888))
		bar=[wleft, white, white, white, white, white, white, white, white, wright]

		if is_global:
			global_activity = await self.bot.db.execute(
				"""
				SELECT h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13,h14,h15,h16,h17,h18,h19,h20,h21,h22,h23
					FROM user_activity
				WHERE user_id = %s
				GROUP BY guild_id
				""",
				user.id,
			)
			if global_activity:
				activity_data = []
				for i in range(24):
					activity_data.append(sum(r[i] for r in global_activity))
				xp = sum(activity_data)
			else:
				activity_data = [0] * 24
				xp = 0
		else:
			activity_data = await self.bot.db.execute(
				"""
				SELECT h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13,h14,h15,h16,h17,h18,h19,h20,h21,h22,h23
					FROM user_activity
				WHERE user_id = %s AND guild_id = %s
				""",
				user.id,
				ctx.guild.id,
				one_row=True,
			)
			xp = sum(activity_data) if activity_data else 0

		level = util.get_level(xp)
		before=level-1
		lbefore=int(util.get_xp(level)) - int(util.xp_to_next_level(before))
		quote=int(xp - util.get_xp(level)) / util.xp_to_next_level(level)
		percent=int(quote*100)
		if percent > 2:
			bar[0] = bleft
		string=str(percent)
		total=string[0]
		total=int(total)
		if percent > 10 :
			if percent != 100:
				for i in range(total):
					if i == 9:
						bar[i] = bright
					elif i == 0:
						bar[i] = bleft
					else:
						bar[i] = blue
			else:
				bar=['<:bround:1005219832213557440>', '<:blue:1005219834361040976>', '<:blue:1005219834361040976>', '<:blue:1005219834361040976>', '<:blue:1005219834361040976>', '<:blue:1005219834361040976>', '<:blue:1005219834361040976>', '<:blue:1005219834361040976>', '<:blue:1005219834361040976>', str(self.bot.get_emoji(1005222500252262440))]

		title = (
			f"LVL {level} | {xp - util.get_xp(level)}/"
			f"{util.xp_to_next_level(level)} XP to levelup | Total xp: {xp}"
		)
		bbar="".join(bar for bar in bar)
		embed=discord.Embed(color=self.bot.color, timestamp=datetime.datetime.now()).set_thumbnail(url=user.display_avatar).set_author(name=user, icon_url=user.display_avatar).add_field(name='Level', value=level, inline=True).add_field(name='Server Rank', value=await self.get_ranking(ctx, user), inline=True).add_field(name='Experience', value=f"{xp - util.get_xp(level)}/{util.xp_to_next_level(level)}XP").add_field(name=f"Progress ({percent}%)", value=bbar, inline=False).set_footer(text=f"Total Experience: {xp}")
		await ctx.send(embed=embed)
		#plotter.create_graph(activity_data, str(user.color), title=title)

		#with open("downloads/graph.png", "rb") as img:
			#await ctx.send(f"`Hourly cumulative {'global' if is_global else 'server'} activity for {user}`",file=discord.File(img),)


	@commands.command(name="rrank", description="see your server rank", brief="member", usage="```Swift\nSyntax: !rank <user>\nExample: !rank @cop#0001```", aliases=["ranking"])
	@commands.cooldown(1, 30, type=commands.BucketType.member)
	async def rrank(self, ctx, user: discord.Member = None):
		if user is None:
			user = ctx.author

		content = discord.Embed(color=user.color)
		content.set_author(
			name=f"Server activity ranks for {util.displayname(user, escape=False)}",
			icon_url=user.display_avatar.url,
		)

		textbox = ""
		for table, label in [
			("user_activity_day", "Daily  "),
			("user_activity_week", "Weekly "),
			("user_activity_month", "Monthly"),
			("user_activity", "Overall"),
		]:
			ranking = await self.get_rank(user, table, ctx.guild)
			textbox += f"\n{label} : {ranking}"

		content.description = f"```\n{textbox}\n```"
		await ctx.send(embed=content)

	@commands.command(name="globalrank", description="see your global rank", brief="member", usage="```Swift\nSyntax: !globalrank <member>\nExample: !globalrank @cop#0001```",aliases=["globalranking", "grank"])
	@commands.cooldown(1, 60, type=commands.BucketType.member)
	async def globalrank(self, ctx, user: discord.Member = None):
		if user is None:
			user = ctx.author

		content = discord.Embed(color=user.color)
		content.set_author(
			name=f"Global activity ranks for {util.displayname(user, escape=False)}",
			icon_url=user.display_avatar.url,
		)

		textbox = ""
		for table, label in [
			("user_activity_day", "Daily  "),
			("user_activity_week", "Weekly "),
			("user_activity_month", "Monthly"),
			("user_activity", "Overall"),
		]:
			ranking = await self.get_rank(user, table)
			textbox += f"\n{label} : {ranking}"

		content.description = f"```\n{textbox}\n```"
		await ctx.send(embed=content)

	@commands.command(aliases=['recentjoins'], description="Show the newest members of this server")
	async def members(self, ctx):
		sorted_members = sorted(ctx.guild.members, key=lambda x: x.joined_at, reverse=True)
		membercount = len(sorted_members)
		content = discord.Embed(title=f"{ctx.guild.name} members", color=self.color)
		rows = []
		for i, member in enumerate(sorted_members, start=1):
			jointime = discord.utils.format_dt(member.joined_at, style='R')
			rows.append(f"`{i}` **{member}** - {jointime}")

		await util.send_as_pages(ctx, content, rows, 10, 1000)

	@commands.command(aliases=['botlist'], description="Show the bots the server has")
	async def bots(self, ctx):
		members=[member for member in ctx.guild.members if member.bot]
		sorted_members = sorted(members, key=lambda x: x.joined_at, reverse=True)
		membercount = len(sorted_members)
		content = discord.Embed(title=f"{ctx.guild.name} bots", color=self.color)
		rows = []
		for i, member in enumerate(sorted_members, start=1):
			jointime = discord.utils.format_dt(member.joined_at, style='R')
			rows.append(f"`{i}` **{member}** - {jointime}")
		if rows:
			await util.send_as_pages(ctx, content, rows, 10, 1000)
		else:
			return await util.send_error(ctx, f"guild has no `bots`")

	@commands.command(aliases=["roles"], description="List the roles of this server")
	async def roleslist(self, ctx):
		content = discord.Embed(title=f"Roles in {ctx.message.guild.name}", color=self.color)
		rows = []
		for i,role in enumerate(reversed(ctx.message.guild.roles), start=1):
			rows.append(
				f"`{i}` {role.mention} - {len(role.members)} members"
			)

		await util.send_as_pages(ctx, content, rows, 10, 1000)

	@commands.command(aliases=["whohas"], description="List the roles of this server", usage="```Swift\nSyntax: !inrole <role>\nExample: !inrole users```",brief='role')
	async def inrole(self, ctx, *, r: typing.Union[ discord.Role, str ]):
		rows = []
		try:
			if isinstance(r, discord.Role):
				role=r
				for i,member in enumerate(role.members, start=1):
					if member != ctx.author:
						rows.append(f"`{i}` **{member}**")
					else:
						rows.append(f"`{i}` **{member}** (you)")
				content = discord.Embed(title=f"who has {role.name}", color=self.color, )
				await util.send_as_pages(ctx, content, rows, 10, 1000)
			if isinstance(r, str):
				r=r.lower()
				roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
				closest=difflib.get_close_matches(r, roles,n=1, cutoff=0)
				if closest:
					for role in ctx.guild.roles:
						if role.name.lower() == closest[0].lower():
							rr=role
					for i,member in enumerate(rr.members, start=1):
						if member != ctx.author:
							rows.append(f"`{i}` **{member}**")
						else:
							rows.append(f"`{i}` **{member}** (you)")
					content = discord.Embed(title=f"who has {rr.name}", color=self.color)
					await util.send_as_pages(ctx, content, rows, 10, 1000)
				else:
					r=r.lower()
					roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable()]
					closest=difflib.get_close_matches(r, roles,n=1, cutoff=0)
					if closest:
						for role in ctx.guild.roles:
							if role.name.lower() == closest[0].lower():
								rr=role
						for i,member in enumerate(rr.members, start=1):
							if member != ctx.author:
								rows.append(f"`{i}` **{member}**")
							else:
								rows.append(f"`{i}` **{member}** (you)")
						content = discord.Embed(title=f"who has {rr.name}", color=self.color)
						await util.send_as_pages(ctx, content, rows, 10, 1000)
					else:
						return await util.send_error(ctx, f"no role found named {r}")
		except Exception as e:
			print(e)
			return await util.send_error(ctx, f"no role found named {r}")

	@commands.command(name='troy', description="troyify a message")
	async def troy(self, ctx, *, message):
		list=message.split(" ")
		str="troy "
		msg=prepend(list, str)
		msgg=" ".join(msg for msg in msg)
		await ctx.send(msgg)

	@commands.command(aliases=["accept", "propose"], description='Marry Someone', usage="```Swift\nSyntax: !marry <member>\nExample: !marry @cop#0001```",brief='member')
	async def marry(self, ctx, user: discord.Member=None):
		if user == None:
			return await util.send_command_help(ctx)
		if user == ctx.author:
			return await ctx.send(embed=discord.Embed(color=self.color, description="You cannot marry yourself..."))
		if {user.id, ctx.author.id} in self.bot.cache.marriages:
			return await ctx.send(embed=discord.Embed(color=self.color, description="You two are already married!"))
		for el in self.bot.cache.marriages:
			if ctx.author.id in el:
				pair = list(el)
				if ctx.author.id == pair[0]:
					partner = ctx.guild.get_member(pair[1]) or self.bot.get_user(pair[1])
				else:
					partner = ctx.guild.get_member(pair[0]) or self.bot.get_user(pair[0])
				return await ctx.send(embed=discord.Embed(color=self.color, description=f":confused: You are already married to **{util.tag(partner)}**! You must divorce before marrying someone else..."))
			if user.id in el:
				return await ctx.send(embed=discord.Embed(color=self.color, description=f":grimacing: **{user}** is already married to someone else, sorry!"))

		else:
			self.proposals.add((ctx.author.id, user.id))
			msg=await ctx.send(
				embed=discord.Embed(
					color=self.color,
					description=f":heartpulse: ***{ctx.author.mention}** proposed to **{user.mention}***",
				)
			)

		async def confirm():
			await self.bot.db.execute(
				"INSERT INTO marriage VALUES (%s, %s, %s)",
				user.id,
				ctx.author.id,
				arrow.now().datetime,
			)
			self.bot.cache.marriages.append({user.id, ctx.author.id})
			await msg.edit(view=None, embed=discord.Embed(color=self.color, description=f":revolving_hearts: **{user.mention}** and **{ctx.author.mention}** are now married :wedding:",))
			new_proposals = set()
			for el in self.proposals:
				if el[0] not in [user.id, ctx.author.id]:
					new_proposals.add(el)
			self.proposals = new_proposals

		async def cancel():
			await msg.edit(view=None, embed=discord.Embed(color=self.color,description=f":revolving_hearts: **{user.mention}** rejected your proposal **{ctx.author.mention}**"))
			pass

		confirmed:bool = await confirmation.confirm(self, ctx, msg, invoker=user, invoked=ctx.author)
		if confirmed:
			await confirm()
		else:
			await cancel()

	@commands.command(description='divorce your current partner',usage="```Swift\nSyntax: !divorce\nExample: !divorce```")
	async def divorce(self, ctx):
		partner = ""
		to_remove = []
		for el in self.bot.cache.marriages:
			if ctx.author.id in el:
				to_remove.append(el)
				pair = list(el)
				if ctx.author.id == pair[0]:
					partner = await self.bot.fetch_user(pair[1])
				else:
					partner = await self.bot.fetch_user(pair[0])

		if partner == "":
			return await ctx.send(embed=discord.Embed(description=f":thinking: {ctx.author.mention} you are not married!", color=self.color))

		content = discord.Embed(
			description=f":broken_heart: Divorce **{partner.name}#{partner.discriminator}**?",
			color=self.color,
		)
		msg = await ctx.send(embed=content)

		async def confirm():
			for x in to_remove:
				self.bot.cache.marriages.remove(x)
			await self.bot.db.execute(
				"DELETE FROM marriage WHERE first_user_id = %s OR second_user_id = %s",
				ctx.author.id,
				ctx.author.id,
			)
			await msg.edit(view=None,
				embed=discord.Embed(
					color=self.color,
					description=f":pensive: **{util.tag(ctx.author)}** and **{partner.name}#{partner.discriminator}** are now divorced...",
				)
			)

		async def cancel():
			await msg.edit(view=None, embed=discord.Embed(description=f":heart: {ctx.author.mention} cancelled the divorce **{partner.mention}**",color=self.color))
			pass

		confirmed:bool = await confirmation.confirm(self, ctx, msg)
		if confirmed:
			await confirm()
		else:
			await cancel()

	@commands.command(aliases=["partner", "husband", "wife", "spouse", "daddy", "mommy"], description='show your marriage', usage="```Swift\nSyntax: !marriage <user/member>\nExample: !marriage @cop#0001```",brief='member/user[optional]')
	async def marriage(self, ctx, member: Union[discord.Member,discord.User]=None):
		if member is None:
			member = ctx.author
		if not member:
			member=self.bot.fetch_user(member)
		"""Check your marriage status."""
		data = await self.bot.db.execute(
			"""
			SELECT first_user_id, second_user_id, marriage_date
				FROM marriage
			WHERE first_user_id = %s OR second_user_id = %s""",
			member.id,
			member.id,
			one_row=True,
		)
		if data:
			if data[0] == member.id:
				partner = ctx.guild.get_member(data[1]) or await self.bot.fetch_user(data[1])
			else:
				partner = ctx.guild.get_member(data[0]) or await self.bot.fetch_user(data[0])
			marriage_date = data[2]
			length = humanize.naturaldelta(
				arrow.utcnow().timestamp - marriage_date.timestamp(), months=False
			)
			part=partner
			ptag=f"{part.name}#{part.discriminator}"
			await ctx.send(
				embed=discord.Embed(
					color=self.color,
					description=f":wedding: **{util.tag(member)}** and **{ptag}** have been married for **{length}**",
				)
			)
		else:
			await ctx.send(embed=discord.Embed(description=f":thinking: {member.mention} you are not married!", color=self.color))

	@commands.command()
	@commands.is_owner()
	async def forcemarriage(self, ctx: commands.Context, member1:int, member2:int):
		user1=member1
		user2=member2
		self.proposals.add((user1, user2))
		await self.bot.db.execute(
				"INSERT INTO marriage VALUES (%s, %s, %s)",
				user1,
				user2,
				arrow.now().datetime,
			)
		self.bot.cache.marriages.append({user1, user2})
		new_proposals = set()
		for el in self.proposals:
			if el[0] not in [user1, user2]:
				new_proposals.add(el)
		self.proposals = new_proposals

	@commands.command()
	@commands.is_owner()
	async def forcedivorce(self, ctx: commands.Context, member1:int):
		try:
			await self.bot.db.execute(
					"DELETE FROM marriage WHERE first_user_id = %s OR second_user_id = %s",
					member1,
					member1,
				)
			member=self.bot.fetch_user(member1)
			await ctx.send(embed=discord.Embed(color=self.color, description=f"successfully forcefully divorced {member.mention}"))
		except:
			return await ctx.send(embed=discord.Embed(color=self.color, description=f"failed to find marriage with user id {member1}"))

async def setup(bot):
	await bot.add_cog(User(bot))


def get_activity_table(timeframe):
	if timeframe in ["day", "daily"]:
		return "daily ", "user_activity_day"
	if timeframe in ["week", "weekly"]:
		return "weekly ", "user_activity_week"
	if timeframe in ["month", "monthly"]:
		return "monthly ", "user_activity_month"
	if timeframe in ["year", "yearly"]:
		return "yearly ", "user_activity_year"
	return "", "user_activity"