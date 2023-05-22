import discord
from discord.ext import commands
import button_paginator as pg
from modules import util
from modules.MyMenuPages import MyMenuPages, MySource
emote=" ・ "
help1=(
	"@ Admin:\n\n"    
	"`!ban` ・ <@user> bans the user\n" 
	"`!massban` ・ <users> to ban multiple users\n"
	"`!blacklist` ・ <user> to blacklist or unblacklist a member from joining\n"
	"`!unban` ・ user#0000 or ID to unban the banned user\n"
	"`!kick` ・ <@user> kicks the user\n"   
	"`!mute` ・ <@user> mutes the user\n"   
	"`!unmute` ・ <@user> unmutes the user\n"   
	"`!mutes` ・ shows all muted users\n"   
	"`!stfu` ・ shuts a member up for an hour(donor only)\n"
#	"`!unmuteall` ・  unmutes all muted users\n"
	"`!jail` ・ <@user> jails a user to the specified channel\n"
	"`!unjail` ・ <@user> unjails specified user\n"
	"`!jailed` ・ lists jailed users\n"
	"`!unjail all` ・ unjails all jailed users\n"
	"`!role` ・ <user> <role> will add or remove a role\n"
	"`!createrole` ・ <hex> <name> to create a role\n"
	"`!nuke` ・ clones the current channel and deletes it\n"
	"`!lock` ・ locks the current channel\n"
	"`!unlock` ・ unlocks the current channel\n"
	"`!removerole` ・ <name> to delete a specified role\n\n"
)

help2=(
	"@ Misc 1:\n\n"
	"`!contact` ・ <reason> will contact the bot owner\n"
	"`!urban` ・ Find the best definition to your words \n"
	"`!ar` ・ to setup autoresponses\n"
	f"`!ar react`{emote} to setup autoreacts\n"
	"`!roles` ・ shows all roles\n"
	"`!whohas` ・ <rolename> to show users of a role\n"
	"`!serverinfo` ・ to show server info\n"
	"`!bandm` ・ <state> to enable or disable ban dms\n"
#	"`!inviteinfo` ・ <invite code> to show a invites info\n"
	"`!userinfo` ・ <@user> to show info sbout a specified user\n"
	"`!revav` ・ <@user> to reverse search a users avatar\n"
	"`!reverse` ・ <url> to reverse search an img\n"
	"`!status` ・ <@user> shows user platforms and status\n"
	"`!steal` ・ <messageid> to steal a previously sent emote\n"
	"`!sticker` ・ sticker commands\n"
	"`!names` ・ <@user> view name history\n"
	"`!clearnames` ・ clear your name history\n"
	"`!emoji` ・ emoji commands\n\n"
#	"`!bio` ・ <@user> shows the users bio\n"
#	"`!connections` ・ <@user> shows the users connections\n"
#	"`!template` ・ to create and send the server template\n"
#	"`!synctemplate` ・ to sync the server template\n\n"
)

help3=(
	"@ Misc 2:\n\n"
	"`!listtz` ・ List available timezones\n"
	"`!tz` ・ @user to list a users time\n"
	"`!recentjoins` ・ to list recent user joins\n"
#	"`!gmute` ・ @user to mute a user with the unbypassable method\n"
#	"`!gunmute` ・ @user to unmute the user that was muted with that method\n"
#	"`!erip` ・ <account> to check if a e.rip account is available\n"
#	"`!tumblr` ・ <account> to show a tumblr account\n"
	"`!twitter` ・ <username> to show a twitter account\n"
	"`!ig` ・ <usernane> to link a instagram account\n"
	"`!tiktok` ・ <username> to lookup a tiktok user\n"
	"`!roblox` ・ <username> to lookup a roblox user\n" 
	"`!whi` ・ <username> to show a weheartit account\n"
	"`!pfpgen` ・ <query> to generate pfps from weheartit\n"
	"`!automod` ・ auto moderation\n"
	"`!joindm` ・ to setup joindm \n"
	"`!welcome help` ・ welcome message setup\n"
	"`!boost` ・ boost message setup\n"
	"`!autorole` ・ autorole setup\n"
	"`!filter` ・ to setup chat filters\n"
#	"`!btcbal` ・ <address> to check a wallet\n"
#	"`!eth` ・ <address> to check a eth wallet\n"
#	"`!fuck` ・ @user\n"
#	"`!kiss` ・ @user\n"
#	"`!hug` ・ @user\n"
#	"`!smug` ・ @user\n"
#	"`!cuddle` ・ @user\n"
	"`!marry` ・ @user to propose\n"
	"`!divorce` ・ to divorce\n"
	"`!marriage` ・ <@user> to see someones marriage\n"
#	"`!pat` ・ @user\n\n"
)

help4=(
	"@ Info:\n\n"    
	"`!about` ・ About the bot \n"  
	"`!invite` ・ Invite me to your server \n"  
	"`!changelog` ・ To view the latest changes\n"
	"`!ping` ・ Check bot delay,\n"  
	"`!snipe` ・ snipes the last deleted message\n"
	"`!editsnipe` ・ snipes the last editted message(not enabled)\n"
	"`!role restore` ・ @member to restore roles\n"
#	"`!pingsnipe/ps` ・ snipes the last deleted ping\n"
#	"`!reactsnipe/rs` ・ snipes the last removed reaction\n"
#	"`!clearsnipe/cs` ・ removes a selected snipe and clears all snipes\n"
	"`!removesnipe/rms` ・ <position> removes a snipe in the selected position\n"
	"`!avatar` ・ <@user> shows users avatar\n"
	"`!afk` ・ sets your afk status if you are pinged\n"
	"`!img` ・ to show a query from google\n"
	"`!google` ・ to show a google search query\n"
	"`!bc` ・ clears all messages from bots\n"
	"`!ocr` ・ <image/url> to grab all text from an image\n"
#	"`!off` ・ <@user> to toggle a user off\n"
#	"`!on` ・ <@user> to toggle a user back on\n"
#	"`!forceon` ・ <@user> to force toggle (Server Owner Only)\n"
	"`!banner` ・ <@user> will return the users banner\n"
	"`!server banner` ・ will return the servers banner\n"
	"`!server splash` ・ will return the servers invite background\n"
	"`!server icon` ・ will return the servers icon\n"
	"`!moveall` ・ <channel id> to move all users in a current vc\n\n"
)

help5=(
	"<:lfm:945412052074242139> Commands:\n"
	"`!whoknows` ・ [artistname]\n"
	"`!whoknowsalbum` ・ <album> | <artist>\n"
	"`!whoknowstrack` ・ [track]\n"
	"`!np`\n"
	"`!crowns` ・ [user]\n\n"
	"  @ Grouped Commands:\n"
	"`!fm / !lf` ・ [subcommand]\n"
	" └ `set`, `unset`, `topalbums`, `server`, `topartists`, `topalbums`, `toptracks`, `recent`, `last`, `album`, `artist`, `cover`, `chart`, `colorchart`, `milestone`, `customcommand/cc`, `embed`, `embed help`, `reaction/react`\n`lf/fm server`\n└ `np`, `recent/re`, `topartists/ta`, `topalbums/tab`, `toptracks/tt` "
	)


ansetup1=(
	"@ Anti Nuke:\n\n"
#   "`!setup` ・ Anti Feature | Fully Setup the Anti feature.\n"
	"`!antinuke/an` ・ anti nuke command group\n"
   	"`!an punishment` ・ ban/stripstafff\n"
	"`!an settings` ・ returns current server anti settings.\n"
	"`!an whitelisted` ・ returns list of whitelisted users.\n"
	"`!an vanity` ・ <vanity> to set the anti vanity vanity\n"
	"`!an wl` ・ adds or removes mentioned user to whitelisted members.\n"
	"`!trusted` ・ returns list of anti administrator users.\n"
	"`!trust` ・ adds or removes mentioned user to anti administrators.\n"
#   "`!toggle` ・ toggle an anti nuke module off.\n"
	"`!an on` ・ turn on all anti nuke features\n"
	"`!an off` ・ turn off all anti nuke features\n"
	"`!an toggle` ・ toggle certain antinuke features\n"
	"`!an features` ・ show all the togglable antinuke features\n"
	"`!antibot` ・ <on/off> turn the anti bot on or off\n"
#   "`!toggles` ・ Shows how to toggle modules off.\n\n"
)


e1 = help1
e2 = help2
e3 = help3
e4 = help4
e5 = help5
e6 = ansetup1

embeds = [e1, e2, e3, e4, e5, e6]

async def bothelp(ctx):
	#formatter=MySource(embeds, per_page=1)
	#menu = MyMenuPages(formatter)
	#await menu.start(ctx)
	await ctx.send(content=f"{ctx.author.mention}: <https://rival.rocks/help>, join the discord server @ <https://rival.rocks/discord>")

class EmbedHelpCommand(commands.HelpCommand):
	"""
	HelpCommand that utilizes embeds.
	It's pretty basic but it lacks some nuances that people might expect.
	1. It breaks if you have more than 25 cogs or more than 25 subcommands.
	2. It doesn't DM users. To do this, you have to override `get_destination`. It's simple.
	"""

	# Set the embed colour here
	COLOUR = int("747f8d", 16)

	def get_command_signature(self, command):
		return f"{command.signature}"

	def get_subcommands(self, c, depth=1):
		self.verify_checks = False
		this_cmd = ""
		if hasattr(c, "commands"):
			for subc in c.commands:
				this_cmd += f"\n{' '*depth}└ **{subc.name}**" + (
					f"\n{' '*(depth+1)}{subc.short_doc}" if subc.short_doc is not None else "-"
				)
				this_cmd += self.get_subcommands(subc, depth + 1)

		return this_cmd

	async def send_bot_help(self, ctx):
		ctx=self.context
		await bothelp(ctx=ctx)

	async def send_cog_help(self, cog):
		embed = discord.Embed(
			title=(f"{cog.icon} " if hasattr(cog, "icon") else "") + cog.qualified_name,
			colour=self.COLOUR,
		)
		if cog.description:
			embed.description = cog.description

		filtered = await self.filter_commands(cog.get_commands(), sort=True)
		for command in filtered:
			embed.add_field(
				name=f"{self.get_command_signature(command)}",
				value=(f"{command.short_doc}\n" if command.short_doc is not None else "-")
				+ self.get_subcommands(command),
				inline=False,
			)

		embed.set_footer(text=f"{self.context.clean_prefix}help [command] for more details.")
		await self.get_destination().send(embed=embed)

	def command_not_found(self, string):
		return

	async def on_help_command_error(self, ctx, error):
		pass

	async def send_group_help(self, group):
		self.verify_checks = False
		ctx=self.context
		embed = discord.Embed(colour=self.COLOUR)
		embed.description="..."
		if group.description:
			embed.description=group.description
		else:
			if group.help:
				embed.description = f"<:blank:947623028286685194>{group.help}"
			elif group.short_doc:
				embed.description = f"<:blank:947623028286685194>{group.short_doc}"
			else:
				embed.description="..."

		if isinstance(group, commands.Group):
			pass
		else:
			return
		try:
			filtered = await self.filter_commands(group.commands, sort=True)
			embedss=[]
			count=0
			counter=0
			counter+=len(filtered)
			for command in filtered:
				try:
					for command in command.walk_commands():
						counter+=1
				except:
					pass
			if group.name == "role":
				emb1 = discord.Embed(colour=int("747f8d", 16))
				count+=1
				emb1.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
				emb1.set_footer(text=f"Aliases: N/A ・ Module: cmds.py"+f" ・ Entry({count}/{counter})")
				emb1.title=f"Command: role"
				emb1.description="give or take a members roles"

				emb1.add_field(name="Parameters", value="member, role", inline=True)
				emb1.add_field(name="Permissions", value="Manage Roles", inline=True)
				emb1.add_field(name="Usage", value=f"```Ruby\nSyntax: {await util.get_prefix(ctx=ctx)}role <@member> <role>\nExample: {await util.get_prefix(ctx=ctx)}role @cop#0001 img```", inline=False)
				embedss.insert(0, emb1)
			for command in filtered:
				try:
					ls=sorted([command.qualified_name for command in command.walk_commands()])
					for l in ls:
						command=ctx.bot.get_command(l)
						emb = discord.Embed(colour=int("747f8d", 16))
						count+=1
						emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
						if command.aliases:
							emb.set_footer(text="Aliases: " + ", ".join(command.aliases)+f" ・ Module: {command.cog_name}.py"+f" ・ Entry({count}/{counter})")
						else:
							emb.set_footer(text=f"Aliases: N/A ・ Module: {command.cog_name}.py"+f" ・ Entry({count}/{counter})")
						if command.description:
							emb.title=f"Command: {command.qualified_name}"
							emb.description=command.description
						else:
							if command.help:
								emb.description = command.help
							else:
								if command.signature:
									emb.description=command.signature
								else:
									emb.description="..."
							emb.title=f"Command: {command.qualified_name}"
						if command.extras:
							perms=command.extras.get('perms')
							if "_" in perms:
								perms=perms.replace("_", " ")
							if command.brief:
								emb.add_field(name="Parameters", value=command.brief, inline=True)
							emb.add_field(name="Permissions", value=f'`{perms.title()}`', inline=True)
						else:
							if command.brief:
								brief=command.brief
								emb.add_field(name="Parameters", value=brief, inline=True)
							emb.add_field(name="Permissions", value="`Send Messages`", inline=True)
						if command.usage:
							usage=command.usage.replace("Swift", "")
							usage=usage.strip("```")
							if "Syntax: " in usage:
								if not "Syntax: !" in usage:
									usage=usage.replace("Syntax: ", f"Syntax: {await util.get_prefix(ctx=self.context)}")
								else:
									usage=usage.replace("Syntax: !", f"Syntax: {await util.get_prefix(ctx=self.context)}")
							if "Example: " in usage:
								if "Example: !" not in usage:
									usage=usage.replace("Example: ", f"Example: {await util.get_prefix(ctx=self.context)}")
								else:
									usage=usage.replace("Example: !", f"Example: {await util.get_prefix(ctx=self.context)}")
							emb.add_field(name="Usage", value=f"```Ruby\n{usage}```", inline=False)
						embedss.append(emb)
				except:
					pass
				emb = discord.Embed(colour=self.COLOUR)
				count+=1
				emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
				if command.aliases:
					emb.set_footer(text="Aliases: " + ", ".join(command.aliases)+f" ・ Module: {command.cog_name}.py"+f" ・ Entry({count}/{counter})")
				else:
					emb.set_footer(text=f"Aliases: N/A ・ Module: {command.cog_name}.py"+f" ・ Entry({count}/{counter})")
				if command.description:
					emb.title=f"Command: {command.qualified_name}"
					emb.description=command.description
				else:
					if command.help:
						emb.description = command.help
					else:
						if command.signature:
							emb.description=command.signature
						else:
							emb.description="..."
					emb.title=f"Command: {command.qualified_name}"
				if command.extras:
					perms=command.extras.get('perms')
					if "_" in perms:
						perms=perms.replace("_", " ")
					if command.brief:
						emb.add_field(name="Parameters", value=command.brief, inline=True)
					emb.add_field(name="Permissions", value=f'`{perms.title()}`', inline=True)
				else:
					if command.brief:
						brief=command.brief
						emb.add_field(name="Parameters", value=brief, inline=True)
					emb.add_field(name="Permissions", value="`Send Messages`", inline=True)
				if command.usage:
					usage=command.usage.replace("Swift", "")
					usage=usage.strip("```")
					if "Syntax: " in usage:
						if not "Syntax: !" in usage:
							usage=usage.replace("Syntax: ", f"Syntax: {await util.get_prefix(ctx=self.context)}")
						else:
							usage=usage.replace("Syntax: !", f"Syntax: {await util.get_prefix(ctx=self.context)}")
					if "Example: " in usage:
						if "Example: !" not in usage:
							usage=usage.replace("Example: ", f"Example: {await util.get_prefix(ctx=self.context)}")
						else:
							usage=usage.replace("Example: !", f"Example: {await util.get_prefix(ctx=self.context)}")
					emb.add_field(name="Usage", value=f"```Ruby\n{usage}```", inline=False)
				embedss.append(emb)
		except Exception as e:
			print(e)

		embed.set_footer(text=f"!help [command] for more details.")
		paginator = pg.Paginator(ctx.bot, embedss, ctx, invoker=ctx.author.id)
		if len(embeds) > 1:
			paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
			paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
		await paginator.start()

	async def send_command_help(self, command):
		self.verify_checks = False
		ctx=self.context
		embed = discord.Embed(colour=self.COLOUR)
		embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
		if command.aliases:
			embed.set_footer(text="Aliases: " + ", ".join(command.aliases)+f" ・ Module: {command.cog_name}.py")
		else:
			embed.set_footer(text=f"Aliases: N/A ・ Module: {command.cog_name}.py")
		if command.extras:
			perms=command.extras.get('perms')
			if "_" in perms:
				perms=perms.replace("_", " ")
			if command.brief:
				embed.add_field(name="Parameters", value=command.brief, inline=True)
			embed.add_field(name="Permissions", value=f'`{perms.title()}`', inline=True)
		else:
			if command.brief:
				brief=f"{command.brief}"
				embed.add_field(name="Parameters", value=brief, inline=True)
		#if command.short_doc:
			#embed.add_field(name="<:blank:947623028286685194>", value=command.short_doc, inline=True)
		if command.description:
			embed.title=f"Command: {command.qualified_name}"
			embed.description=command.description
		else:
			if command.help:
				embed.description = command.help
			else:
				if command.signature:
					embed.add_field(name="<:blank:947623028286685194>", value=command.signature, inline=True)
				

			embed.title=f"Command: {command.qualified_name}"
		if command.usage:
			usage=command.usage.replace("Swift", "")
			usage=usage.strip("```")
			if "Syntax: " in usage:
				if not "Syntax: !" in usage:
					usage=usage.replace("Syntax: ", f"Syntax: {await util.get_prefix(ctx=self.context)}")
				else:
					usage=usage.replace("Syntax: !", f"Syntax: {await util.get_prefix(ctx=self.context)}")
			if "Example: " in usage:
				if "Example: !" not in usage:
					usage=usage.replace("Example: ", f"Example: {await util.get_prefix(ctx=self.context)}")
				else:
					usage=usage.replace("Example: !", f"Example: {await util.get_prefix(ctx=self.context)}")
			embed.add_field(name="Usage", value=f"```Ruby\n{usage}```", inline=False)
		#embed.description="..."
		#embed.title=f"!{command.qualified_name}"
		#if command.short_doc:
			#embed.add_field(name="<:blank:947623028286685194>", value=command.short_doc, inline=True)
		#elif command.brief:
			#embed.description = command.brief
		#else:
			#embed.description = "..."

		await self.get_destination().send(embed=embed)

	async def group_help_brief(self, ctx, group):
		embed = discord.Embed(colour=self.COLOUR)
		embed.description = "`" + ctx.prefix + group.qualified_name
		embed.description += f" [{' | '.join(c.name for c in group.commands)}]`"
		embed.set_footer(text=f"{ctx.prefix}help {group.qualified_name} for more detailed help")
		await ctx.send(embed=embed)