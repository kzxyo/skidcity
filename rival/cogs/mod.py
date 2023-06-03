import asyncio

import arrow
from typing import Union
import discord
import typing
import datetime
import humanfriendly
from discord.ext import commands, tasks
from modules.asynciterations import aiter
from modules import exceptions, log, util, confirmation

import logging
logger = logging.getLogger(__name__)


class Mod(commands.Cog):
	"""Moderation commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "🔨"
		self.color=self.bot.color
		self.add="<:plus:947812413267406848>"
		self.yes=self.bot.yes
		self.good=self.bot.color#0x0xD6BCD0
		self.rem="<:rem:947812531509026916>"
		self.no=self.bot.no
		self.bad=0xff6465
		self.ch='{self.bot.yes}'
		self.error=self.bot.color#0xfaa61a
		self.warn=self.bot.warn

	async def geninvite(self, guild_id):
		guild=self.bot.get_guild(guild_id)
		for channel in guild.text_channels:
			try:
				invite=await channel.create_invite()
				return invite
			except:
				pass

	async def mass_add_roles(self, ctx, member:discord.Member):
		try:
			rrr=[]
			counter=0
			roles=await self.bot.db.execute("""SELECT roles FROM jail WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, member.id, one_value=True)
			roles=roles.split(",")
			for rr in roles:
				roled = discord.utils.get(ctx.guild.roles, id=int(rr))
				if roled and roled.is_assignable() and not roled.is_bot_managed():
					rrr.append(roled)
				if roled.is_bot_managed():
					rrr.append(roled)
			for r in member.roles:
				if not r in rrr:
					rrr.append(r)
			return await member.edit(roles=[role for role in rrr])
		except Exception as e:
			print(e)

	async def strip_roles(self, guild:discord.Guild, member:discord.Member):
		guild=self.bot.get_guild(guild.id)
		totalroles=[]
		removedroles=[]
		for role in member.roles:
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
			for role in removedroles:
				roles.append(f"{role.id}")
			new_lst=(','.join(str(a)for a in roles))
			newroles=f"{new_lst}"
			if await self.bot.db.execute("""SELECT * FROM restore WHERE guild_id = %s AND member_id = %s""", guild.id, member.id):
				await self.bot.db.execute("""DELETE FROM restore WHERE guild_id = %s AND member_id = %s""", guild.id, member.id)
			await self.bot.db.execute("""INSERT INTO restore VALUES(%s, %s, %s)""", guild.id, member.id, newroles)
		except:
			pass
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



	@commands.command(name='massban', description='ban user(s)', extras={'perms': 'ban members'}, usage="```Swift\nSyntax: !massban <@users>\nExample: !massban @cop @rival @prada```",brief='user(s)', hidden=True)
	@commands.has_permissions(ban_members=True)
	async def massban(self, ctx, *discord_users):
		guild=ctx.guild
		if not discord_users:
			return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: **please include a member/user**",color=self.error))
		for discord_user in discord_users:
			user = await util.get_member(ctx, discord_user)
			if user is None:
				try:
					user = await self.bot.fetch_user(int(discord_user))
				except (ValueError, discord.NotFound):
					await ctx.send(
						embed=discord.Embed(
							description=f"<:warn:940732267406454845 >{ctx.author.mention}: **Invalid user or id** `{discord_user}`",
							color=self.error
						)
					)
					continue

			if user.id == 133311691852218378:
				return await ctx.send("no.")
			member=user
			if user in ctx.guild.members:
				if ctx.author.id == ctx.guild.owner.id:
					pass
				else:
					if ctx.author.id != ctx.guild.owner.id:
						if member.id == ctx.guild.owner.id:
							return await ctx.send(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: **you can't {ctx.command.name} the owner**"))
						if ctx.author.top_role == member.top_role:
							return await ctx.send(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: **you can't {ctx.command.name} someone who has the same permissions as you**"))
						if ctx.author.top_role < member.top_role:
							return await ctx.send(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: **you can't {ctx.command.name} someone higher than yourself**"))
			else:
				pass

			# confirmation dialog for guild members
			if isinstance(user, discord.Member):
				if user.premium_since:
					boost=f"booster?"
				else:
					boost="user?"
				await self.ssend_ban_confirmation(ctx, user, boost)

			elif isinstance(user, discord.User):
				boost='user?'
				try:
					try:
						await user.send(embed=discord.Embed(title='Banned', color=self.color).add_field(name='You have been banned in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author))
						await asyncio.sleep(1)
						await ctx.guild.ban(user, reason=f"User Responsible: {ctx.author}", delete_message_days=0)
					except:
						await ctx.guild.ban(user, reason=f"User Responsible: {ctx.author}", delete_message_days=0)
						pass
				except discord.errors.Forbidden:
					await ctx.send(
						embed=discord.Embed(
							description=f"{self.bot.no} {ctx.author.mention}: i can't ban **{user}**",
							color=self.bad,
						)
					)
				else:
					await ctx.send(
						embed=discord.Embed(
							description=f"<:hammer:940737261761335296> Banned `{user}`", color=self.color
						)
					)
			else:
				await ctx.send(
					embed=discord.Embed(
						description=f"{self.bot.warn} {ctx.author.mention}: **invalid user or id** `{discord_user}`",
						color=self.error,
					)
				)


	async def ssend_ban_confirmation(self, ctx, user, boost):
		content = discord.Embed(title=f"<:hammer:940737261761335296> Ban {boost}", color=self.color)
		content.description = f"{user.mention}\n**{user.name}#{user.discriminator}**\n{user.id}"
		msg = await ctx.send(embed=content)

		async def confirm_ban():
			try:
				try:
					await ctx.guild.ban(user, reason=f"User Responsible: {ctx.author}", delete_message_days=0)
					await asyncio.sleep(1)
					await user.send(embed=discord.Embed(title='Banned', color=self.color).add_field(name='You have been banned in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author))
				except:
					await ctx.guild.ban(user, reason=f"User Responsible: {ctx.author}", delete_message_days=0)
					pass
				content.title = f"{self.bot.yes} Banned user"
			except discord.errors.Forbidden:
				content.title = None
				content.description = f"{self.bot.no} {ctx.author.mention}: i can't ban  **{user}** {user.mention}"
				content.colour = self.bad
			await msg.edit(embed=content)

		async def cancel_ban():
			content.title = f"{self.bot.no} Ban cancelled"
			content.colour=self.bad
			await msg.edit(embed=content)

		functions = {"✅": confirm_ban, "❌": cancel_ban}
		asyncio.ensure_future(
			util.reaction_buttons(ctx, msg, functions, only_author=True, single_use=True)
		)

	@commands.command(name='reactionmute', aliases=['reactmute','rmute','rm'], description="mute or unmute a member from reacting", brief='member', usage='```Swift\nSyntax: !reactionmute <user>\nExample: !reactionmute @cop#0001```', extras={'perms':'Moderate Members'})
	@commands.has_permissions(moderate_members=True)
	async def reactionmute(self, ctx, *, member:discord.Member):
		if member == ctx.guild.owner:
			return await util.send_error(ctx, f"you cannot `reaction mute` the owner")
		if ctx.author != ctx.guild.owner:
			if member.top_role.position >= ctx.author.top_role.position:
				return await util.send_error(ctx, f"you cannot `reaction mute` {member.mention}")
		if member in ctx.channel.overwrites:
			try:
				await ctx.channel.set_permissions(member, overwrite=None, reason=f"reaction mute undone by {ctx.author}")
				return await util.send_good(ctx, f"{member.mention} can now `add reactions` again")
			except:
				return await util.send_error(ctx, f"unable to undo `reaction mute` on {member.mention}")
		else:
			try: 
				await ctx.channel.set_permissions(member, overwrite=discord.PermissionOverwrite(add_reactions=False), reason=f"reaction muted by {ctx.author}")
				return await util.send_good(ctx, f"successfully `reaction muted` {member.mention}")
			except:
				return await util.send_error(ctx, f"unable to `reaction mute` {member.mention}")

	@commands.command(name='imagemute', aliases=['imgmute','imute','im'], description="mute or unmute a member from sending images", brief='member', usage='```Swift\nSyntax: !imagemute <user>\nExample: !imagemute @cop#0001```', extras={'perms':'Moderate Members'})
	@commands.has_permissions(moderate_members=True)
	async def imagemute(self, ctx, *, member:discord.Member):
		if member == ctx.guild.owner:
			return await util.send_error(ctx, f"you cannot `image mute` the owner")
		if ctx.author != ctx.guild.owner:
			if member.top_role.position >= ctx.author.top_role.position:
				return await util.send_error(ctx, f"you cannot `image mute` {member.mention}")
		if member in ctx.channel.overwrites:
			try:
				await ctx.channel.set_permissions(member, overwrite=None, reason=f"image mute undone by {ctx.author}")
				return await util.send_good(ctx, f"{member.mention} can now `send images` again")
			except:
				return await util.send_error(ctx, f"unable to undo `image mute` on {member.mention}")
		else:
			try: 
				await ctx.channel.set_permissions(member, overwrite=discord.PermissionOverwrite(embed_links=False,attach_files=False), reason=f"image muted by {ctx.author}")
				return await util.send_good(ctx, f"successfully `image muted` {member.mention}")
			except:
				return await util.send_error(ctx, f"unable to `image mute` {member.mention}")

	async def ban_dm(self, ctx, member, reason):
		msg=await self.bot.db.execute("""SELECT message FROM ban_message WHERE guild_id = %s""", ctx.guild.id, one_value=True)
		if msg:
			try:
				msg=msg.replace("{moderator}",str(ctx.author))
				msg=msg.replace("{reason}",reason)
				params=await util.embed_replacement(ctx.author,ctx.guild,msg)
				message = await util.to_object(ctx,member,ctx.guild,params)
			except Exception as e:
				print(e)
				pass
		else:
			try:
				guild=ctx.guild
				await user.send(embed=discord.Embed(title='Banned', color=self.bad).add_field(name='You have been banned in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author, inline=True).add_field(name='Reason', value=reason, inline=True))
			except:
				pass

	@commands.hybrid_command(name='ban', aliases=['deport'], with_app_command=True, description='Ban a user', brief='member/user, reason[optional]', usage="```Swift\nSyntax: !ban <user> <reason>\nExample: !ban @cop racism```",extras={'perms': 'ban members'})
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: typing.Union[discord.Member, discord.User]=None, *, reason:str=None):
		if not reason:
			reason="No Reason Provided"
		rs=f"{reason} | {ctx.author}"
		guild=ctx.guild
		user=member
		if not member:
			return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: **please include a member/user**",color=self.error))

		if user.id == 133311691852218378:
			return await ctx.send("no.")
		member=user

			# confirmation dialog for guild members
		if isinstance(member, discord.Member):
			if ctx.author.id == ctx.guild.owner.id:
				pass
			else:
				if member.id == ctx.guild.owner.id :
					return await ctx.send(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: **you can't {ctx.command.name} the owner**"))
				if ctx.author.top_role <= member.top_role and ctx.author.id != ctx.guild.owner.id:
					return await ctx.send(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: **you can't {ctx.command.name} someone higher than yourself**"))
			if user.premium_since:
				boost=f"booster?"
			else:
				boost="user?"
			if not await self.bot.db.execute("""SELECT * FROM confirmations WHERE guild_id = %s""", ctx.guild.id):
				await self.send_ban_confirmation(ctx, user, boost, rs)
			else:
				content=discord.Embed()
				try:
					try:
						if not await self.bot.db.execute("""SELECT * FROM moddm WHERE guild_id = %s""", ctx.guild.id):
							await self.ban_dm(ctx, member, reason)
							# try:
							# 	guild=ctx.guild
							# 	await user.send(embed=discord.Embed(title='Banned', color=self.bad).add_field(name='You have been banned in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author, inline=True).add_field(name='Reason', value=reason, inline=True))
								
							# except:
							# 	pass
						await ctx.guild.ban(user, reason=reason, delete_message_days=0)
						await asyncio.sleep(1)
					except:
						if not await self.bot.db.execute("""SELECT * FROM moddm WHERE guild_id = %s""", ctx.guild.id):
							await self.ban_dm(ctx, member, reason)
						await ctx.guild.ban(user, reason=reason, delete_message_days=0)
						pass
					content.title = f"{self.bot.yes} Banned user"
					content.description = f"{user.mention}\n**{user.name}#{user.discriminator}**\n{user.id}"
					content.colour = self.good
				except discord.errors.Forbidden:
					content.title = None
					content.description = f"{self.bot.no} {ctx.author.mention}: i can't ban  **{user}** {user.mention}"
					content.colour = self.bad
				msg = await ctx.send(embed=content)


		elif isinstance(member, discord.User):
			boost='user?'
			try:
				try:
					await self.ban_dm(ctx, member, reason)
					#await user.send(embed=discord.Embed(title='Banned', color=self.color).add_field(name='You have been banned in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author))
					await asyncio.sleep(1)
					await ctx.guild.ban(user, reason=rs, delete_message_days=0)
				except:
					await ctx.guild.ban(user, reason=rs, delete_message_days=0)
					pass
			except discord.errors.Forbidden:
				await ctx.send(
					embed=discord.Embed(
						description=f"{self.bot.no} {ctx.author.mention}: i can't ban **{user}**",
						color=self.bad,
					)
				)
			else:
				await ctx.send(
					embed=discord.Embed(
						description=f"<:hammer:940737261761335296> Banned `{user}`", color=self.color
					)
				)
		else:
			await ctx.send(
				embed=discord.Embed(
					description=f"{self.bot.warn} {ctx.author.mention}: **invalid user or id** `{discord_user}`",
					color=self.error,
				)
			)


	async def send_ban_confirmation(self, ctx, user, boost, reason):
		content = discord.Embed(title=f"<:hammer:940737261761335296> Ban {boost}", color=self.color)
		content.description = f"{user.mention}\n**{user.name}#{user.discriminator}**\n{user.id}"
		msg = await ctx.send(embed=content)

		async def confirm_ban():
			try:
				try:
					if not await self.bot.db.execute("""SELECT * FROM moddm WHERE guild_id = %s""", ctx.guild.id):
						try:
							guild=ctx.guild
							await self.ban_dm(ctx, user, reason)
							#await user.send(embed=discord.Embed(title='Banned', color=self.bad).add_field(name='You have been banned in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author, inline=True).add_field(name='Reason', value=reason, inline=True))
						except Exception as e:
							print(e)
							pass
					await ctx.guild.ban(user, reason=reason, delete_message_days=0)
					await asyncio.sleep(1)
				except:
					if not await self.bot.db.execute("""SELECT * FROM moddm WHERE guild_id = %s""", ctx.guild.id):
						try:
							guild=ctx.guild
							await self.ban_dm(ctx, user, reason)
							#await user.send(embed=discord.Embed(title='Banned', color=self.bad).add_field(name='You have been banned in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author, inline=True).add_field(name='Reason', value=reason, inline=True))
						except Exception as e:
							print(e)
							pass
					await ctx.guild.ban(user, reason=reason, delete_message_days=0)
					pass
				content.title = f"{self.bot.yes} Banned user"
			except discord.errors.Forbidden:
				content.title = None
				content.description = f"{self.bot.no} {ctx.author.mention}: i can't ban  **{user}** {user.mention}"
				content.colour = self.bad
			await msg.edit(embed=content, view=None)

		async def cancel_ban():
			content.title = f"{self.bot.no} Ban cancelled"
			content.colour=self.bad
			await msg.edit(embed=content, view=None)

		confirmed:bool = await confirmation.confirm(self, ctx, msg)
		if confirmed:
			await confirm_ban()
		else:
			await cancel_ban()

	@commands.command(name='kick', description='Kick User(s)', brief='users', usage="```Swift\nSyntax: !kick <@users>\nExample: !kick @cop @prada @rival```",extras={'perms': 'kick members'})
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, *discord_users):
	   
		if not discord_users:
			return await ctx.send(embed=discord.Embed(color=self.color, description=f"please specify a user"))

		for discord_user in discord_users:
			user = await util.get_member(ctx, discord_user)
			if user is None:
				try:
					user = self.bot.get_user(int(discord_user))
				except (ValueError, discord.NotFound):
					await ctx.send(
						embed=discord.Embed(
							description=f"{self.bot.warn} Invalid user or id `{discord_user}`",
							color=self.color,
						)
					)
					continue

			if user.id == 133311691852218378:
				return await ctx.send("no.")
			member=user
			if user in ctx.guild.members:
				if ctx.author.id == ctx.guild.owner.id:
					pass
				else:
					if ctx.author.id != ctx.guild.owner.id:
						if member.id == ctx.guild.owner.id:
							return await ctx.send(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: **you can't {ctx.command.name} the owner**"))
						if ctx.author.top_role == member.top_role:
							return await ctx.send(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: **you can't {ctx.command.name} someone who has the same permissions as you**"))
						if ctx.author.top_role < member.top_role:
							return await ctx.send(embed=discord.Embed(color=self.error, description=f"{self.bot.warn} {ctx.author.mention}: **you can't {ctx.command.name} someone higher than yourself**"))
			else:
				pass

			# confirmation dialog for guild members
			if isinstance(user, discord.Member):
				if not await self.bot.db.execute("""SELECT * FROM confirmations WHERE guild_id = %s""", ctx.guild.id):
					try:
						await self.send_Kick_confirmation(ctx, user)
					except:
						await ctx.send(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **i cannot kick that member**", color=self.error))
				else:
					try:
						if not await self.bot.db.execute("""SELECT * FROM moddm WHERE guild_id = %s""", ctx.guild.id):
							try:
								await user.send(embed=discord.Embed(title='Kicked', color=self.bad).add_field(name='You have been kicked in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author, inline=True).add_field(name='Reason', value="None Provided", inline=True))
							except:
								pass
						await user.kick(reason=f"User Responsible {ctx.author}")
						await util.send_good(ctx, f"kicked <@!{user.id}>")
					except:
						await util.send_error(ctx, f"I cannot kick that user")
			else:
				await ctx.send(
					embed=discord.Embed(
						description=f"{self.bot.warn} Invalid user or id `{discord_user}`",
						color=self.error,
					)
				)



	async def send_Kick_confirmation(self, ctx, user):
		content = discord.Embed(title="<:hammer:940737261761335296> Kick user?", color=self.color)
		content.description = f"{user.mention}\n**{user.name}#{user.discriminator}**\n{user.id}"
		msg = await ctx.send(embed=content)

		async def confirm_Kick():
			try:
				guild=ctx.guild
				if not await self.bot.db.execute("""SELECT * FROM moddm WHERE guild_id = %s""", ctx.guild.id):
					try:
						await user.send(embed=discord.Embed(title='Kicked', color=self.bad).add_field(name='You have been kicked in', value=guild.name, inline=True).add_field(name='Moderator', value=ctx.author, inline=True).add_field(name='Reason', value="None Provided", inline=True))
					except:
						pass                
				await user.kick(reason=f"User Responsible: {ctx.author}")
				content.title = f"{self.bot.yes} kicked user"
				content.colour=self.good
			except discord.errors.Forbidden:
				content.title = None
				content.description = f"{self.bot.no} It seems I don't have the permission to kick **{user}** {user.mention}"
				content.colour = self.bad
			await msg.edit(embed=content, view=None)

		async def cancel_Kick():
			content.title = f"{self.bot.no} Kick cancelled"
			content.colour=self.bad
			await msg.edit(embed=content, view=None)

		confirmed:bool = await confirmation.confirm(self, ctx, msg)
		if confirmed:
			await confirm_Kick()
		else:
			await cancel_Kick()

	async def unban_dm(self, ctx, user, reason):
		if ctx.guild.premium_tier >= 3:
			invite=await ctx.guild.vanity_invite()
		else:
			invite=await self.geninvite(ctx.guild.id)
		try:
			await user.send(embed=discord.Embed(color=self.good, title="Unbanned").add_field(name=f"You have been unbanned in", value=ctx.guild.name, inline=True).add_field(name="Moderator", value=ctx.author, inline=True).add_field(name="Invite", value=f"[Here]({invite})", inline=True))
		except Exception as e:
			print(e)
			pass

	async def guild_unban(self, ctx, user:typing.Union[int,str], reason, bans):
		# if isinstance(user, discord.User):
		# 	try:
		# 		await ctx.guild.unban(user)
		# 		user=self.bot.get_user(user)
		# 		if user:
		# 			await self.unban_dm(ctx, user)
		# 		return True
		# 	except:
		# 		banned_user = discord.utils.get(bans, user__name=user.name)
		# 		if banned_user:
		# 			await ctx.guild.unban(banned_user.user)
		# 			user=self.bot.get_user(user)
		# 			if user:
		# 				await self.unban_dm(ctx, user)
		# 			return True
		# else:
		if isinstance(user, int):
			banned_user=discord.utils.get(bans, user__id=user)
			if not banned_user: return False
			else: return banned_user
		if isinstance(user, str):
			if "#" in user:
				try:
					name, tag = user.split('#')
				except:
					embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: *Please format the username like this: \nUsername#0000*", color=self.error)
					await ctx.send(embed=embed)
					return
				banned_user = discord.utils.get(
					bans, user__name=name,
					user__discriminator=tag
				)
				if not banned_user:
					return False
			else:
				banned_user = discord.utils.get(bans, user__name=user)
				if not banned_user:
					return False
		else:
			if isinstance(user, int):
				banned_user=discord.utils.get(bans, user__id=user)
				if not banned_user: return False
				else: return banned_user
			else:
				return False
		try:
			await ctx.guild.unban(discord.Object(int(banned_user.user.id)), reason=reason)
			user=self.bot.get_user(banned_user.user.id)
			if user:
				await self.unban_dm(ctx, user, reason)
			return True
		except:
			return False



	@commands.command(name='unban', description='unban a user', brief='id/name#discriminator, reason[optional]', usage="```Swift\nSyntax: !unban <name#discrim/id> <reason>\nExample: !unban cop#0001```",extras={'perms': 'ban members'})
	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	async def unban(self, ctx, user: typing.Union[int,str], *, reason:str=None):
		bans=[ban async for ban in ctx.guild.bans(limit=5000)]
		if not reason:
			reason=f"unbanned by {ctx.author}"
		# if isinstance(user, str):
		# 	# try:
		# 	# 	await ctx.guild.unban(discord.Object(user), reason=reason)
		# 	# 	await self.unban_dm(ctx,user,reason)
		# 	# 	return await ctx.send("👍")
		# 	# except:
		# 	unban=await self.guild_unban(ctx, user, reason, bans)
		# 	if unban == True:
		# 		return await ctx.send("👍")
		# 	else:
		# 		u=discord.utils.find(lambda u: u.user.name.lower().startswith(str(user).lower()), bans)
		# 		if u:
		# 			try:
		# 				await ctx.guild.unban(discord.Object(u.user.id))
		# 				m=self.bot.get_user(u.user.id)
		# 				if m:
		# 					await self.unban_dm(ctx,user,reason)
		# 				return await ctx.send("👍")
		# 			except Exception as e:
		# 				return await util.send_error(ctx, f"unable to find **{str(user)}**")
		# 		else:
		# 			return await util.send_error(ctx, f"unable to find **{str(user)}**")
		# else:
		unban=await self.guild_unban(ctx, user, reason, bans)
		if unban == True:
			return await ctx.send("👍")
		else:
			try:
				await ctx.guild.unban(discord.Object(user), reason=reason)
				await self.unban_dm(ctx,user,reason)
				return await ctx.send("👍")
			except:
				return await util.send_error(ctx, f"unable to find **{str(user)}**")

	@commands.hybrid_command(name='timeout', aliases=['mute'], with_app_command=True, description="Timeout/Mute a user in the server", usage="```Swift\nSyntax: !timeout <member> <time> <reason>\nExample: !timeout @cop 1hour racism```",brief='member, time, reason[optional]', extras={'perms': 'moderate members'})
	@commands.has_permissions(moderate_members=True)
	@commands.bot_has_permissions(moderate_members=True)
	async def timeout(self, ctx: commands.Context, user: discord.Member, time:typing.Optional[str], *, reason: str = "No reason provided"):
		if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} {user.mention} **is higher then you** {ctx.author.mention}", color=self.color))
		if ctx.author.id == ctx.guild.owner.id:
			pass
		if user == ctx.author:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} **You can't mute yourself!**", color=self.color))
		if not time:
			time="1hour"
		try:
			rs=reason+f"by {ctx.author}"
			timeConvert = humanfriendly.parse_timespan(time)
			await user.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason=rs)
			embed = discord.Embed(description=f"**{self.bot.yes} muted {user.mention} for {time} | Reason: {reason}**", color=self.color)
			await ctx.send(embed=embed)
			#await user.send(embed=discord.Embed(description=f"**You were muted in {ctx.guild.name} | Reason: {reason}**", color=self.color))
		except discord.Forbidden:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} **This user has a higher or equal role to me. **", color=self.color))
		except discord.errors.HTTPException:
			return await ctx.reply(embed=discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: **max mute time is `30days`**", color=self.error))
		except humanfriendly.InvalidTimespan:
			reason=time+" "+reason
			rs=reason+f" by {ctx.author}"
			timeConvert = humanfriendly.parse_timespan("1hour")
			await user.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason=rs)
			embed = discord.Embed(description=f"**{self.bot.yes} muted {user.mention} for 1hour | Reason: {reason}**", color=self.color)
			await ctx.send(embed=embed)

	@commands.hybrid_command(name='untimeout', aliases=['unmute'], with_app_command=True, description="Unmutes a user from the server", usage="```Swift\nSyntax: !untimeout <member> <reason>\nExample: !untimeout @cop#0001```",brief='member, reason', extras={'perms': 'moderate members'})
	@commands.has_permissions(moderate_members=True)
	@commands.bot_has_permissions(moderate_members=True)
	async def untimeout(self, ctx: commands.Context, user: discord.Member, *, reason: str = "No reason provided"):
		if user == ctx.author:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: **You can't unmute yourself!**", color=self.color))
		if not user.is_timed_out():
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: **That user isn't muted!**", color=self.color))
		
		rs=reason+f"by {ctx.author}"
		await user.timeout(discord.utils.utcnow(), reason=rs)
		embed = discord.Embed(description=f"{self.bot.yes} **unmuted  {user.mention} | Reason: {reason}**", color=self.color)
		await ctx.send(embed=embed)

	@commands.command(name='stfu', description="make a member's messages auto delete", usage="```Swift\nSyntax: !stfu <mention/id>\nExample: !stfu @cop#0001```",extras={'perms': 'administrator / donator server'}, brief='member')
	@commands.has_permissions(administrator=True)
	@util.donor_server()
	async def stfu(self, ctx, member:discord.Member):
		#idea from melanie bot / monty
		if ctx.author.top_role.position <= member.top_role.position and ctx.author != ctx.guild.owner:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: {member.mention} **is higher then you**", color=self.color))
		if ctx.author.id == ctx.guild.owner.id:
			pass
		if member == ctx.author:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: **You can't silence yourself!**", color=self.color))
		if ctx.guild.id in self.bot.cache.stfu:
			if member.id in self.bot.cache.stfu[ctx.guild.id]:
#		if await self.bot.db.execute("""SELECT * FROM stfu WHERE guild_id = %s and user_id = %s""", ctx.guild.id, member.id):
				await self.bot.db.execute("""DELETE FROM stfu WHERE guild_id = %s and user_id = %s""", ctx.guild.id, member.id)
				try:
					self.bot.cache.stfu[ctx.guild.id].remove(member.id)
				except:
					pass
				return await util.send_success(ctx, f"{ctx.author.mention}: **unsilenced** {member.mention}")
		if ctx.guild.id not in self.bot.cache.stfu:
			self.bot.cache.stfu[ctx.guild.id]=[]
		self.bot.cache.stfu[ctx.guild.id].append(member.id)
		await self.bot.db.execute("""INSERT INTO stfu VALUES(%s, %s)""", ctx.guild.id, member.id)
		return await util.send_success(ctx, f"{ctx.author.mention}: **silenced** {member.mention}")

	@commands.command(name='jail', description='takes users roles and gives them a jailed role', brief='member', usage="```Swift\nSyntax: !jail <mention/id>\nExample: !jail @cop#0001```",extras={'perms': 'moderate members'})
	@commands.has_permissions(moderate_members=True)
	async def jail(self, ctx, member: discord.Member=None):
		roles=[]
		obj=[]
		if member == None:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **You must specify a member to jail**"))
		if await self.bot.db.execute("""SELECT * FROM jail WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, member.id):
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **{member.mention} is already jailed**"))
		jail_role = discord.utils.get(ctx.guild.roles, name="jailed")
		if ctx.author.top_role.position <= member.top_role.position and ctx.author != ctx.guild.owner:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: {member.mention} **is higher then you**", color=self.color))
		if member == ctx.author:
			return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: **You can't silence yourself!**", color=self.color))
		if member.roles:
			if len(member.roles) >= 1:
				member_roles = [role async for role in aiter(member.roles) if role.is_assignable()]
				async for role in aiter(member.roles):
					if role.is_assignable():
						roles.append(f"{role.id}")
				try:
					await self.strip_roles(ctx.guild, member)
				except:
					await member.remove_roles(*member_roles)
			else:
				roles=None
		else:
			roles=None
		try: 
			await member.add_roles(jail_role)
		except:
			return await ctx.reply(embed=discord.Embed(description=f"{self.warn} {ctx.author.mention}: **jail isn't setup please run !setme**", color=self.error))
		if roles:
			new_lst=(','.join(str(a)for a in roles))
			newroles=f"{new_lst}"
		else:
			newroles="None"
		await self.bot.db.execute("""INSERT INTO jail VALUES(%s, %s, %s)""", ctx.guild.id, member.id, newroles)
		await util.send_success(ctx, f"{ctx.author.mention}: **jailed {member.mention}**")

	@commands.command(name='unjail', description='unjail a jailed user and restore their roles', brief='member / all', usage="```Swift\nSyntax: !unjail <mention/id/all>\nExample: !unjail @cop#0001```",extras={'perms': 'moderate members'})
	@commands.has_permissions(moderate_members=True)
	async def unjail(self, ctx, member: typing.Union[discord.Member, str]=None):
		
		obj=[]
		if member == None:
			return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{ctx.author.mention}: **please mention a member or use `all` to unjail all jailed members"))
		if isinstance(member, discord.Member):
			if member == ctx.author:
				return await ctx.send(embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: **You can't silence yourself!**", color=self.color))
			if not await self.bot.db.execute("""SELECT * FROM jail WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, member.id):
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **{member.mention} isn't jailed**"))
			jail_role = discord.utils.get(ctx.guild.roles, name="jailed")
			try:
				await member.remove_roles(jail_role)
			except:
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **Jail Role Not Found, try setting up jail using !setme**"))
			data=await self.bot.db.execute("""SELECT * FROM jail WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, member.id)
			if data:
				pass
			else:
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **{member.mention} is not jailed**"))
			try:
				roles=await self.bot.db.execute("""SELECT roles FROM jail WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, member.id, one_value=True)
				if roles != "None":
					roles=roles.split(",")
					rr=[]
					async for r in aiter(roles):
						#role=ctx.guild.get_role(int(r))
					   # rr.append(role)
						role = discord.utils.get(ctx.guild.roles, id=int(r))
						if role and role.is_assignable():
							rr.append(role)
					try:
						await self.mass_add_roles(ctx, member)
					except:
						await member.add_roles(*rr, reason=f"unjailed by {ctx.author}")
			except:
				pass
			await self.bot.db.execute("""DELETE FROM jail WHERE guild_id = %s AND user_id = %s""", ctx.guild.id, member.id)
			await util.send_success(ctx, f"{ctx.author.mention}: **unjailed {member.mention}**")
		else:
			if member.lower() == "all":
				jail_role = discord.utils.get(ctx.guild.roles, name="jailed")
				for member in jail_role.members:
					data=await self.bot.db.execute("""SELECT user_id, roles FROM jail WHERE guild_id = %s""", ctx.guild.id)
					async for user_id, roles in aiter(data):
						member=ctx.guild.get_member(user_id)
						roles=roles.split(",")
						rr=[]
						try:
							await member.remove_roles(jail_role)
						except:
							return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.warn} {ctx.author.mention}: **Jail Role Not Found, try setting up jail using !setme**"))
						if roles != "None":
							async for r in aiter(roles):
								#role=ctx.guild.get_role(int(r))
							   # rr.append(role)
								role = discord.utils.get(ctx.guild.roles, id=int(r))
								if role and role.is_assignable():
									rr.append(role)
							try:
								await self.mass_add_roles(ctx, member)
							except:
								await member.add_roles(*rr, reason=f"unjailed by {ctx.author}")
				await self.bot.db.execute("""DELETE FROM jail WHERE guild_id = %s""", ctx.guild.id)
				await util.send_success(ctx, f"{ctx.author.mention}: **unjailed all jailed members**")
			else:
				return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{ctx.author.mention}: **please mention a member or use `all` to unjail all jailed members"))

	@commands.command(name='jailed', description="shows all jailed members", extras={'perms': 'moderate members'})
	@commands.has_permissions(moderate_members=True)
	async def jailed(self, ctx):
		guild=ctx.guild
		rows=[]
		data=await self.bot.db.execute("""SELECT user_id FROM jail WHERE guild_id = %s""", ctx.guild.id)
		if data:
			for user_id in data:
				u=self.bot.get_user(user_id[0])
				if not u:
					u=await self.bot.fetch_user(user_id[0])
				rows.append(f"{user}")
		if rows:
			content = discord.Embed(title=f"{guild.name}'s jailed members")
			await util.send_as_pages(ctx, content, rows)
		else:
			raise exceptions.Info("No Jailed Users")


async def setup(bot):
	await bot.add_cog(Mod(bot))
