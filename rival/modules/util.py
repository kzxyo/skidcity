import asyncio, copy, io, math, os, re, discord, regex, colorgram, json, aiohttp, arrow, orjson, sys, platform, ctypes, requests, time,difflib,datetime,socket
from colorama import Fore
from time import sleep
from itertools import cycle
from discord.ext import commands
from durations_nlp import Duration
from durations_nlp.exceptions import InvalidTokenError
from PIL import Image, UnidentifiedImageError
import button_paginator as pg
from bs4 import BeautifulSoup
from modules import emojis, exceptions, queries
yes=""

url_regex = re.compile(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")

IMAGE_SERVER_HOST = "0.0.0.0"

add="<:plus:947812413267406848>"
#yes="<:yes:940723483204255794>"
good=0xD6BCD0
rem="<:rem:947812531509026916>"
#no="<:no:940723951947120650>"
no='<:x_:1021273367749337089>'
yes="<:check:1021252651809259580>"
bad=0xff6465
color=0xD6BCD0
ch='<:yes:940723483204255794>'
error=0xfaa61a
warn='<:warning:1021286736883621959>'

class ErrorMessage(Exception):
	pass


class donorCheckFailure(commands.CheckFailure):
	pass

def proxy_scrape():
	startTime = time.time()
	temp = os.getenv("temp")+"\\proxies.txt"
	print(f"{Fore.YELLOW}Please wait while Enemy Scrapes proxies for you!")
	r = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=8500&country=all&ssl=all&anonymity=elite&simplified=true", headers=getheaders())
	with open(temp, "wb") as f:
		f.write(r.content)
	execution_time = (time.time() - startTime)
	print(f"{Fore.GREEN}Done scraping proxies {Fore.RESET} | {execution_time}ms")

async def datetime_delta(t):
	d=discord.utils.utcnow() - datetime.timedelta(weeks=t*4)
	return d

async def invite_find(message):
	DISCORD_INVITE = r'(?:https?://)?(?:www.:?)?discord(?:(?:app)?.com/invite|.gg)/?[a-zA-Z0-9]+/?'
	dsg=r'(https|http)://(dsc.gg|discord.gg|discord.io|dsc.lol)/?[\S]+/?'
	r=re.compile(DISCORD_INVITE)
	rr=re.compile(dsg)
	invites=r.findall(message)
	invs=rr.findall(message)
	if len(invites) >= 1 or len(invs) >= 1:
		return True
	else:
		return False

def convertTuple(tup):
		# initialize an empty string
	str = ''
	for item in tup:
		str = str + item
	return str
 

def is_owner(self,ctx,member=None):
	if ctx.author.id or ctx.member.id == 714703136270581841:
		return True
	else:
		return False

async def find_role(ctx, role):
	r=role
	roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r.lower() in role.name.lower()]
	closest=discord.utils.find(lambda r: r.name.lower().startswith(role), ctx.guild.roles)
	if closest: 
		for role in ctx.guild.roles:
			if role.name.lower() == closest:
				return role
	else:
		r=role
		roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable()]
		closest=difflib.get_close_matches(r.lower(), roles,n=1, cutoff=0)
		if closest:
			for role in ctx.guild.roles:
				if role.name.lower() == closest[0].lower():
					rr=role
					if rr:
						return rr
		else:
			closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
			if closest:
				for role in ctx.guild.roles:
					if role.name.lower() == closest:
						return role
			else:
				return None

async def find_member(ctx, member):
	me=member
	members=[m for m in ctx.guild.members]
	mem=[member.name.lower() for member in ctx.guild.members]
	user=discord.utils.find(lambda m: m.name.lower().startswith(member.lower()), ctx.guild.members)
	if user:
		return user
	else:
	#for member in ctx.guild.members:
		#mem.append(member.name)
		closest=difflib.get_close_matches(me.lower(), mem,n=1, cutoff=0)
		user=discord.utils.find(lambda m: m.name.lower() == closest[0], ctx.guild.members)
		if user: 
			return user
		else:
			return None
		
def proxy():
	temp = os.getenv("temp")+"\\proxies.txt"
	if not os.path.exists(temp):
		with open(temp, "w") as f:
			f.close()
	if os.stat(temp).st_size == 0:
		proxy_scrape()
	proxies = open(temp).read().split('\n')
	proxy = proxies[1]

	with open(temp, 'r+') as fp:
		lines = fp.readlines()
		fp.seek(0)
		fp.truncate()
		fp.writelines(lines[1:])
	return proxy


def getheaders(token=None, content_type="application/json"):
	headers = {
		"Content-Type": content_type,
		"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
	}
	if token:
		headers.update({"Authorization": token})
	return headers

def getHeaders(token=None, content_type="application/json"):
	headers = {
		"Content-Type": content_type,
		"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
	}
	if token:
		headers.update({"Authorization": token})
	return headers

def displayname(member, escape=True):
	if member is None:
		return None

	name = member.name
	if isinstance(member, discord.Member):
		name =f"{member.name}#{member.discriminator}"
	if isinstance(member, discord.User):
		name =f"{member.name}#{member.discriminator}"

	if escape:
		return escape_md(name)
	return name

def tag(member, escape=True):
	if member is None:
		return None

	name = member.name
	dis = member.discriminator
	tag=f"{name}#{dis}"
	if isinstance(member, discord.Member):
		name = member.name
		dis = member.discriminator
		tag=f"{name}#{dis}"
	if isinstance(member, discord.User): 
		name = member.name
		dis = member.discriminator
		tag=f"{name}#{dis}"
	if escape:
		return escape_md(tag)
	return tag

async def get_commits(author, repository):
	url = f"https://api.github.com/repos/{author}/{repository}/commits"
	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers={'accept': 'application/vnd.github.v3.raw', 'authorization': 'token {}'.format(os.environ["GH_TOKEN"])
			}) as response:
			data = await response.json()
	return data

async def member_scrape(ctx, member):
	async with aiohttp.ClientSession() as s:
		async with s.get(f"https://japi.rest/discord/v1/user/{member}") as r:
			return await r.json()

async def send_success(ctx, message):
	#77b255
	await ctx.send(embed=discord.Embed(description=f"<:check:1021252651809259580> " + message, color=color))

async def send_successs(ctx, message):
	await ctx.send(delete_after=15, embed=discord.Embed(description=f"<:check:1021252651809259580> {ctx.author.mention}: {message}", color=color))

async def send_error(ctx, message, delete=True):
	if delete:
		msg=await ctx.send(delete_after=15, embed=discord.Embed(description=f"<:warning:1021286736883621959> {ctx.author.mention}: {message}", color=color))
	else:
		msg=await ctx.send(embed=discord.Embed(description=f"<:warning:1021286736883621959> {ctx.author.mention}: {message}", color=color))
	return msg

async def send_failure(ctx, message):
	await ctx.send(embed=discord.Embed(description="<:x_:1021273367749337089> " + message, color=color))

async def send_good(ctx, message, delete=False):
	if delete==True:
		msg=await ctx.send(delete_after=5,embed=discord.Embed(description=f"<:check:1021252651809259580> {ctx.author.mention}: {message}", color=color))
	else:
		msg=await ctx.send(embed=discord.Embed(description=f"<:check:1021252651809259580> {ctx.author.mention}: {message}", color=color))
	return msg

async def send_bad(ctx, message):
	msg=await ctx.send(embed=discord.Embed(description=f"<:x_:1021273367749337089> {ctx.author.mention}: {message}", color=color))
	return msg

async def determine_prefix(bot, message):
	"""Get the prefix used in the invocation context."""
	if message.author == bot.user:
		return
	if isinstance(message.channel, discord.DMChannel):
		return
	if message.guild:
		if message.guild.id == 336642139381301249:
			return commands.when_mentioned_or("!!!!!!!")
		prefix = bot.cache.prefixes.get(str(message.author.id), '!!!!')
		prefixx = bot.cache.prefixess.get(str(message.guild.id), "!")
		return commands.when_mentioned_or(prefix, prefixx)(bot, message)
	else:
		prefix="!!"

async def get_prefix(ctx):
	"""Get the prefix used in the invocation context."""
	bot=ctx.bot
	if ctx.author == ctx.me:
		return
	if isinstance(ctx.channel, discord.DMChannel):
		return
	if ctx.guild:
		prefix = bot.cache.prefixes.get(str(ctx.author.id), '!!!!')
		prefixx = bot.cache.prefixess.get(str(ctx.guild.id), "!")
	return prefixx

async def vanity_prefix(bot, message):
	"""Get the prefix used in the invocation context."""
	if message.author == bot.user:
		return
	if isinstance(message.channel, discord.DMChannel):
		return
	if message.guild:
		prefix = bot.cache.prefixes.get(str(message.author.id), '!!!!')
		prefixx = bot.cache.prefixess.get(str(message.guild.id), "!!")
		return commands.when_mentioned_or("!!", 'rival ', 'rival', 'r', 'r ')(bot, message)
	else:
		prefix="!!"

async def geninvite(self, guild_id):
	guild=self.bot.get_guild(guild_id)
	for channel in guild.text_channels:
		try:
			invite=await channel.create_invite()
			return invite
		except:
			pass


async def do_removal(ctx, limit, predicate, *, before=None, after=None, message=True):
	if limit > 2000:
		return await ctx.send(f"Too many messages to search given ({limit}/2000)")

	if not before:
		before = ctx.message
	else:
		before = discord.Object(id=before)

	if after:
		after = discord.Object(id=after)

	try:
		deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
	except discord.Forbidden:
		return await ctx.send("I do not have permissions to delete messages.")
	except discord.HTTPException as e:
		return await ctx.send(f"Error: {e} (try a smaller search?)")

	deleted = len(deleted)
	return deleted


async def is_blacklisted(ctx):
	"""Check command invocation context for blacklist triggers."""
	if ctx.command.name != "nodata" and await ctx.bot.db.execute("""SELECT * FROM nodata WHERE user_id = %s""", ctx.author.id):
		raise exceptions.NoData()
	if ctx.guild is not None and ctx.guild.id in ctx.bot.cache.blacklist["global"]["guild"]:
		raise exceptions.BlacklistedGuild()
	if ctx.channel.id in ctx.bot.cache.blacklist["global"]["channel"]:
		raise exceptions.BlacklistedChannel()
	if ctx.author.id in ctx.bot.cache.blacklist["global"]["user"]:
		raise exceptions.BlacklistedUser()
	if ctx.guild is not None and ctx.bot.cache.blacklist.get(str(ctx.guild.id)) is not None:
		if ctx.author.id in ctx.bot.cache.blacklist[str(ctx.guild.id)]["member"]:
			raise exceptions.BlacklistedMember()
		if (
			ctx.command.qualified_name.lower()
			in ctx.bot.cache.blacklist[str(ctx.guild.id)]["command"]
		):
			raise exceptions.BlacklistedCommand()

	return True

async def getwhi(query):
	url = f"https://weheartit.com/search/entries?query={query}"
	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers={"Content-Type": "application/json","User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"}) as r:
			d=await r.content.read()
	soup = BeautifulSoup(d, features="html.parser")
	divs = str(soup.find_all('div', class_='entry grid-item'))
	soup2 = BeautifulSoup(divs, features="html.parser")
	badge=soup2.find_all(class_='entry-badge')
	images = soup2.find_all('img')
	links = []
	for image in images:
		if "data.whicdn.com/images/" in str(image):
			links.append(image['src'])
			
	return links

async def getwhiuser(query):
	url = f"https://weheartit.com/{query}"
	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers={"Content-Type": "application/json","User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"}) as r:
			d=await r.content.read()
	soup = BeautifulSoup(d, features="html.parser")
	divs = str(soup.find_all('div', class_='entry grid-item'))
	soup2 = BeautifulSoup(divs, features="html.parser")
	badge=soup2.find_all(class_='entry-badge')
	images = soup2.find_all('img')
	links = []
	for image in images:
		if "data.whicdn.com/images/" in str(image):
			links.append(image['src'])
			
	return links

async def imgpage(ctx, embeds):
	paginator = pg.Paginator(ctx.bot, embeds, ctx, invoker=ctx.author.id)
	if len(embeds) > 1:
		paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
		paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
		paginator.add_button('goto', label=None, emoji="<:filter:1000215652591734874>", style=discord.ButtonStyle.red)
		paginator.add_button('delete', emoji='<:stop:958054042637054013>', label=None, style=discord.ButtonStyle.red)
	await paginator.start()

async def pagecreate(self, ctx, embeds):
	paginator = pg.Paginator(bot, embeds, ctx)
	if len(embeds) > 1:
		paginator.add_button('prev', emoji='<:left:934237439772483604>')
	#paginator.add_button('delete', label='Close the paginator', emoji='⏹')
		paginator.add_button('next', emoji='<:right:934237462660788304>')
	await paginator.start()

async def contentpage(ctx, content, rows):
	maxrows=10
	maxpages=10
	embeds=create_pages(content, rows, maxrows, maxpages)
	paginator = pg.Paginator(ctx.bot, embeds, ctx)
	if len(embeds) > 1:
		paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
	#paginator.add_button('delete', label='Close the paginator', emoji='⏹')
		paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
	await paginator.start()


async def send_embed_list(ctx, embeds):
	paginator = pg.Paginator(ctx.bot, embeds, ctx, invoker=ctx.author.id)
	if len(embeds) > 1:
		paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
	#paginator.add_button('delete', label='Close the paginator', emoji='⏹')
		paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
	await paginator.start()


async def create_embed_paginator(ctx, embeds, send=False):
	embed_finished=[]
	embed_list=[m for m in re.finditer("{embed}", embeds)]
	if len(embed_list) > 1:
		embeds=embeds.split("{embed}")
		embeds.pop(0)
		for e in embeds:
			params=await embed_replacement(ctx.author,ctx.guild,e)
			em = await to_objectt(ctx,params)
			embed_finished.append(em)
	if len(embed_finished) > 0:
		if send:
			#await ctx.send(f"```{embed_finished}```")
			paginator = pg.Paginator(ctx.bot, embed_finished, ctx, invoker=ctx.author.id)
			if len(embeds) > 1:
				paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
			#paginator.add_button('delete', label='Close the paginator', emoji='⏹')
				paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
			await paginator.start()


def flags_to_badges(user):
	"""Get list of badge emojis from public user flags."""
	result = []
	for flag, value in iter(user.public_flags):
		if value:
			result.append(emojis.Badge[flag].value)
	if isinstance(user, discord.Member) and user.premium_since is not None:
		result.append(emojis.Badge["boosting"].value)
	return result or ["-"]

def get_urls(message):
	# Returns a list of valid urls from a passed message/context/string
	message = message.content if isinstance(message,discord.Message) else message.message.content if isinstance(message,discord.ext.commands.Context) else str(message)
	return [x.group(0) for x in re.finditer(url_regex,message)]

def truncate_string(self,value=None,limit=128,suffix="...",replace_newlines=True,complete_codeblocks=True):
	if not isinstance(value,str) : return value
	# Truncates the string to the max chars passed
	if replace_newlines:
		new_val = [line+"\n" if complete_codeblocks and line.startswith("```") and line[3:].isalpha() else line for line in value.split("\n")]
		value = " ".join(new_val)
	if len(value)>limit: # We need to truncate
		value = value[:limit-len(suffix)]+suffix
		# Check if we need to complete an orphaned codeblock
		if complete_codeblocks and value.count("```") % 2: value += "```"
	return value

def get_xp(level):
	"""
	:param level : Level
	:return      : Amount of xp needed to reach the level
	"""
	return math.ceil(math.pow((level - 1) / (0.05 * (1 + math.sqrt(5))), 2))


def get_level(xp):
	"""
	:param xp : Amount of xp
	:returns  : Current level based on the amount of xp
	"""
	return math.floor(0.05 * (1 + math.sqrt(5)) * math.sqrt(xp)) + 1


def xp_to_next_level(level):
	return get_xp(level + 1) - get_xp(level)


def xp_from_message(message):
	"""
	:param message : Message to get the xp from
	:returns       : Amount of xp rewarded from given message. Minimum 1
	"""
	words = message.content.split(" ")
	eligible_words = 0
	for x in words:
		if len(x) > 1:
			eligible_words += 1
	xp = eligible_words + (10 * len(message.attachments))
	if xp == 0:
		xp = 1

	return min(xp, 50)

async def send_as_pages(ctx, content, rows, maxrows:int=10, maxpages:int=300):
	"""
	:param ctx     : Context
	:param content : Base embed
	:param rows    : Embed description rows
	:param maxrows : Maximum amount of rows per page
	:param maxpages: Maximum amount of pages untill cut off
	"""
	if not content.author:
		if not ctx.author.nick:
			content.set_author(name=str(ctx.author),icon_url=ctx.author.display_avatar.url)
		else:
			content.set_author(name=ctx.author.display_name,icon_url=ctx.author.display_avatar.url)
	embeds=create_pages(content, rows, maxrows, maxpages)
	paginator = pg.Paginator(ctx.bot, embeds, ctx, invoker=ctx.author.id)
	if len(embeds) > 1:
		paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
	#paginator.add_button('delete', label='Close the paginator', emoji='⏹')
		paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
	await paginator.start()

async def yes(ui : discord.ui.View, interaction : discord.Interaction, button : discord.ui.button):
	if interaction.user != ctx.author:
		await interaction.response.send_message(content = f"{pain}", ephemeral = True)    
		for view in ui.children:
			view.disabled = True            
		await interaction.response.edit_message(content = f"\u2001", embed = ban_emb, view = ui)

async def no(ui : discord.ui.View, interaction : discord.Interaction, button : discord.ui.button):
	if interaction.user != ctx.author:
		await interaction.response.send_message(content = f"{pain}", ephemeral = True)
	for view in ui.children:
		view.disabled = True
	await interaction.response.edit_message(content = f"**{user.mention}** will not be banned.", allowed_mentions = self.bot.mentions, view = ui)
	
	Interface.Confirmation.response = await ctx.send(f"Are you sure you want to ban {user.mention}", view = Interface.Confirmation(yes, no), allowed_mentions = self.bot.mentions)
  

async def old_pages(ctx, content, rows, maxrows=10, maxpages=10):
	"""
	:param ctx     : Context
	:param content : Base embed
	:param rows    : Embed description rows
	:param maxrows : Maximum amount of rows per page
	:param maxpages: Maximum amount of pages untill cut off
	"""
	pages = create_pages(content, rows, maxrows, maxpages)
	if len(pages) > 1:
		await page_switcher(ctx, pages)
	else:
		await ctx.send(embed=pages[0])


async def text_based_page_switcher(ctx, pages, prefix="```", suffix="```", numbers=True):
	"""
	:param ctx    : Context
	:param pages  : List of strings
	:param prefix : String to prefix every page with
	:param suffix : String to suffix every page with
	:param numbers: Add page numbers to suffix
	"""
	total_rows = len("\n".join(pages).split("\n"))

	# add all page numbers
	if numbers:
		seen_rows = 0
		for i, page in enumerate(pages, start=1):
			seen_rows += len(page.split("\n"))
			page += f"\n{i}/{len(pages)} | {seen_rows}/{total_rows}{suffix}"
			page = prefix + "\n" + page
			pages[i - 1] = page

	pages = TwoWayIterator(pages)

	msg = await ctx.send(pages.current())

	async def switch_page(new_page):
		await msg.edit(content=new_page)

	async def previous_page():
		content = pages.previous()
		if content is not None:
			await switch_page(content)

	async def next_page():
		content = pages.next()
		if content is not None:
			await switch_page(content)

	functions = {"<:left:934237439772483604>": previous_page, "<:right:934237462660788304>": next_page}
	asyncio.ensure_future(reaction_buttons(ctx, msg, functions))


async def page_switcher(ctx, pages):
	"""
	:param ctx   : Context
	:param pages : List of embeds to use as pages
	"""
	embeds=pages
	paginator = pg.Paginator(ctx.bot, embeds, ctx)
	paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
	#paginator.add_button('delete', label='Close the paginator', emoji='⏹')
	paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
	await paginator.start()

async def ppage_switcher(ctx, pages):
	"""
	:param ctx   : Context
	:param pages : List of embeds to use as pages
	"""
	if len(pages) == 1:
		return await ctx.send(embed=pages[0])

	pages = TwoWayIterator(pages)

	# add all page numbers
	for i, page in enumerate(pages.items, start=1):
		old_footer = page.footer.text
		if old_footer == discord.Embed.Empty:
			old_footer = None
		page.set_footer(
			text=f"{i}/{len(pages.items)}" + (f" | {old_footer}" if old_footer is not None else "")
		)

	msg = await ctx.send(embed=pages.current())

	async def switch_page(content):
		await msg.edit(embed=content)

	async def previous_page():
		content = pages.previous()
		if content is not None:
			await switch_page(content)

	async def next_page():
		content = pages.next()
		if content is not None:
			await switch_page(content)

	functions = {"<:left:934237439772483604>": previous_page, "<:right:934237462660788304>": next_page}
	asyncio.ensure_future(reaction_buttons(ctx, msg, functions))


def create_pages(content, rows, maxrows=15, maxpages=10):
	"""
	:param content : Embed object to use as the base
	:param rows    : List of rows to use for the embed description
	:param maxrows : Maximum amount of rows per page
	:param maxpages: Maximu amount of pages until cut off
	:returns       : List of Embed objects
	"""
	pages = []
	pg=[]
	content.description = ""
	thisrow = 0
	rowcount = len(rows)
	rc=len(rows)
	ct=0
	pagecount=rowcount / maxrows
	if pagecount > int(pagecount):
		pagecount=int(pagecount+1)
	if pagecount > maxpages:
		pagecount=int(maxpages)
	elif pagecount < 1:
		pagecount=1
	if "#" in rows[0]:
		if content.title and content.title!="recently available tags" and "name history" not in content.title.lower() and "webhook" not in content.title.lower():
			if len(rows) > 1:
				eeeee="Members"
			else:
				eeeee="Member"
		elif content.title and "name history" in content.title.lower():
			if len(rows) > 1:
				eeeee="Names"
			else:
				eeeee="Name"
		elif content.title and "webhooks" in content.title.lower():
			if len(rows) > 1:
				eeeee="Webhooks"
			else:
				eeeee="Webhook"
		else:
			if content.title:
				if content.title == "recently available tags":
					if len(rows) > 1:
						eeeee="Tags"
					else:
						eeeee="Tag"
				else:
					if len(rows) > 1:
						eeeee="Members"
					else:
						eeeee="Member"
	elif content.title and "guild" in content.title.lower():
		if len(rows) > 1:
			eeeee='Guilds'
		else:
			eeeee='Guild'
	elif content.title and "role" in content.title.lower():
		if len(rows) > 1:
			eeeee="Roles"
		else:
			eeeee="Role"
	else:
		if len(rows) > 1:
			eeeee="Entries"
		else:
			eeeee="Entry"
	for row in rows:
		thisrow += 1
		if len(content.description) + len(row) < 2000 and thisrow < maxrows + 1:
			content.description += f"\n{row}"
			rowcount -= 1
		else:
			thisrow = 1
			if len(pages) == maxpages - 1:
				content.description += f"\n*+ {rowcount} more entries...*"
				pages.append(content)
				content = None
				break
			pages.append(content)
			content = copy.deepcopy(content)
			content.description = f"{row}"
			rowcount -= 1
	if content is not None and not content.description == "":
		pages.append(content)
	for i,page in enumerate(pages, start=1):
		if not page.footer:
			page.set_footer(text=f"Page {i}/{int(pagecount)} ({rc} {eeeee})")
			pg.append(page)
		else:
			pg.append(page)

	return pg

async def embed_replacement(user,guild,params):
	params=params.replace(r"\n","\n")
	if "{user}" in params:
		params = params.replace("{user}", str(user))
	if "{now}" in params:
		params = params.replace("{now}", datetime.datetime.now())
	if "{user.mention}" in params:
		params = params.replace("{user.mention}", str(user.mention))
	if "{user.name}" in params:
		params = params.replace("{user.name}", str(user.name))
	if "{user.avatar}" in params:
		params = params.replace("{user.avatar}", str(user.display_avatar.url))
	if "{user.joined_at}" in params:
		params = params.replace("{user.joined_at}", user.joined_at)
	if "{user.created_at}" in params:
		params=params.replace("{user.created_at}", user.created_at)
	if "{user.discriminator}" in params:
		params = params.replace("{user.discriminator}", str(user.discriminator))
	if "{guild.name}" in params:
		params = params.replace("{guild.name}", str(user.guild.name))
	if "{guild.count}" in params:
		params = params.replace("{guild.count}", str(user.guild.member_count))
	if "{guild.count.format}" in params:
		ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
		params=params.replace("{guild.count.format}", str(ordinal(len(user.guild.members))))
	if "{guild.id}" in params:
		params = params.replace("{guild.id}", str(user.guild.id))
	if "{guild.created_at}" in params:
		params = params.replace("{guild.created_at}", user.guild.created_at)
	if "{guild.boost_count}" in params:
		params = params.replace("{guild.boost_count}", str(user.guild.premium_subscription_count))
	if "{guild.boost_count}" in params:
		params = params.replace("{guild.booster_count}", str(len(user.guild.premium_subscribers)))
	if "{guild.boost_count.format}" in params:
		ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
		params = params.replace("{guild.boost_count.format}", str(ordinal(len(user.guild.premium_subscription_count))))
	if "{guild.boost_count.format}" in params:
		ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
		params = params.replace("{guild.booster_count.format}", str(ordinal(len(user.guild.premium_subscribers))))
	if "{guild.boost_tier}" in params:
		params = params.replace("{guild.boost_tier}", str(user.guild.premium_tier))
	if "{guild.icon}" in params:
		if user.guild.icon:
			params = params.replace("{guild.icon}", str(user.guild.icon.url))
		else:
			params=params.replace("{guild.icon}", "")
	return params

async def to_objectt(ctx,params):
	params=params.replace("{embed}","")
	em = discord.Embed()
	if "label:" in params or "emoji:" in params:
		view = discord.ui.View()
	else:
		view=None
	if not params.count('{'):
		if not params.count('}'):
			em.description = params
	#if "title" in params or "description" in params:
	if "description:" in params or "title:" in params or "image:" in params or "thumbnail:" in params or "field:" in params:
		try:
			for field in get_parts(params):
				data = parse_field(field)
				content = data.get('content') or None
				color = data.get('color') or data.get('colour')
				if color == 'random':
					em.color = random.randint(0, 0xFFFFFF)
				elif color == 'chosen':
					maybe_col = os.environ.get('COLOR')
					if maybe_col:
						raw = int(maybe_col.strip('#'), 16)
						return discord.Color(value=raw)
					else:
						return await ctx.send('color error')
				elif color:
					color = int(color.strip('#'), 16)
					em.color = discord.Color(color)
				if data.get('description'):
					em.description = data['description']
				if data.get('desc'):
					em.description = data['desc']
				if data.get('title'):
					em.title = data['title']
				if data.get('url'):
					em.url = data['url']
				author = data.get('author')
				icon, url = data.get('icon'), data.get('url')

				if author:
					em._author = {'name': author}
					if icon:
						em._author['icon_url'] = icon
					if url:
						em._author['url'] = url

				label,link,emoji = data.get("label") or None, data.get("link" or None),data.get('emoji' or None)
				if label:
					if link:
						url=link
						view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
				else:
					if link:
						if emoji:
							view.add_item(discord.ui.Button(label=label, emoji=emoji, url=link))

				field, value = data.get('field'), data.get('value')
				inline = False if str(data.get('inline')).lower() == 'false' else True
				if field and value:
					em.add_field(name=field, value=value, inline=inline)

				if data.get('thumbnail'):
					em._thumbnail = {'url': data['thumbnail']}

				if data.get('image'):
					em._image = {'url': data['image']}

				if data.get('delete'):
					delete=int(data['delete'])
				else:
					delete=None

				if data.get('footer'):
					em._footer = {'text': data.get('footer')}
					if data.get('icon'):
						em._footer['icon_url'] = data.get('icon')

				if 'timestamp' in data.keys() and len(data.keys()) == 1:
					em.timestamp = datetime.datetime.now()
		except IndexError:
			return await send_error(ctx, f"Syntax Error in Embed Format Please use [this embed creator](https://rival.rocks/embed)")
		except Exception as e:
			return await send_error(ctx, f"{e}")
	else:
		try:
			em=None
			for field in get_parts(params):
				data = parse_field(field)
				if data.get('delete'):
					delete=int(str(data['delete']))
				else:
					delete=None
				if data.get('content'):
					content=data['content']
				else:
					content=None
				label,link,emoji = data.get("label") or None, data.get("link" or None),data.get('emoji' or None)
				if label:
					if link:
						url=link
						view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
				else:
					if link:
						if emoji:
							view.add_item(discord.ui.Button(label=label, emoji=emoji, url=link))
		except IndexError:
			return await send_error(ctx, f"Syntax Error in Embed Format Please use [this embed creator](https://rival.rocks/embed)")
		except Exception as e:
			return await send_error(ctx, f"{e}")

	return em

async def to_object(ctx,user,guild,params):
	params=params.replace("{embed}","")
	em = discord.Embed()
	if "label:" in params or "emoji:" in params:
		view = discord.ui.View()
	else:
		view=None
	if not params.count('{'):
		if not params.count('}'):
			em.description = params
	#if "title" in params or "description" in params:
	if "description:" in params or "title:" in params or "image:" in params or "thumbnail:" in params or "field:" in params:
		try:
			for field in get_parts(params):
				data = parse_field(field)
				content = data.get('content') or None
				color = data.get('color') or data.get('colour')
				if color == 'random':
					em.color = random.randint(0, 0xFFFFFF)
				elif color == 'chosen':
					maybe_col = os.environ.get('COLOR')
					if maybe_col:
						raw = int(maybe_col.strip('#'), 16)
						return discord.Color(value=raw)
					else:
						return await ctx.send('color error')
				elif color:
					color = int(color.strip('#'), 16)
					em.color = discord.Color(color)
				if data.get('description'):
					em.description = data['description']
				if data.get('desc'):
					em.description = data['desc']
				if data.get('title'):
					em.title = data['title']
				if data.get('url'):
					em.url = data['url']
				author = data.get('author')
				icon, url = data.get('icon'), data.get('url')

				if author:
					em._author = {'name': author}
					if icon:
						em._author['icon_url'] = icon
					if url:
						em._author['url'] = url

				label,link,emoji = data.get("label") or None, data.get("link" or None),data.get('emoji' or None)
				if label:
					if link:
						url=link
						view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
				else:
					if link:
						if emoji:
							view.add_item(discord.ui.Button(label=label, emoji=emoji, url=link))

				field, value = data.get('field'), data.get('value')
				inline = False if str(data.get('inline')).lower() == 'false' else True
				if field and value:
					em.add_field(name=field, value=value, inline=inline)

				if data.get('thumbnail'):
					em._thumbnail = {'url': data['thumbnail']}

				if data.get('image'):
					em._image = {'url': data['image']}

				if data.get('delete'):
					delete=int(data['delete'])
				else:
					delete=None

				if data.get('footer'):
					em._footer = {'text': data.get('footer')}
					if data.get('icon'):
						em._footer['icon_url'] = data.get('icon')

				if 'timestamp' in data.keys() and len(data.keys()) == 1:
					em.timestamp = datetime.datetime.now()
		except IndexError:
			return await send_error(ctx, f"Syntax Error in Embed Format Please use [this embed creator](https://rival.rocks/embed)")
		except Exception as e:
			return await send_error(ctx, f"{e}")
	else:
		try:
			em=None
			for field in get_parts(params):
				data = parse_field(field)
				if data.get('delete'):
					delete=int(str(data['delete']))
				else:
					delete=None
				if data.get('content'):
					content=data['content']
				else:
					content=None
				label,link,emoji = data.get("label") or None, data.get("link" or None),data.get('emoji' or None)
				if label:
					if link:
						url=link
						view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
				else:
					if link:
						if emoji:
							view.add_item(discord.ui.Button(label=label, emoji=emoji, url=link))
				# label,link = data.get("label") or None, data.get("link" or None)
				# if label:
				# 	if link:
				# 		try:
				# 			emoji=label[i].get("emoji")
				# 		except:
				# 			emoji=None
				# 		url=link
				# 		view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
		except IndexError:
			return await send_error(ctx, f"Syntax Error in Embed Format Please use [this embed creator](https://rival.rocks/embed)")
		except Exception as e:
			return await send_error(ctx, f"{e}")

	message=await user.send(delete_after=delete,content=content, embed=em, view=view)
	return message

async def to_embed(ctx,user,guild,params):
	em = discord.Embed()
	if "label:" in params or "emoji:" in params:
		view = discord.ui.View()
	else:
		view=None
	if not params.count('{'):
		if not params.count('}'):
			em.description = params
	#if "title" in params or "description" in params:
	if "description:" in params or "title:" in params or "image:" in params or "thumbnail:" in params or "field:" in params:
		try:
			for field in get_parts(params):
				data = parse_field(field)
				content = data.get('content') or None
				color = data.get('color') or data.get('colour')
				if color == 'random':
					em.color = random.randint(0, 0xFFFFFF)
				elif color == 'chosen':
					maybe_col = os.environ.get('COLOR')
					if maybe_col:
						raw = int(maybe_col.strip('#'), 16)
						return discord.Color(value=raw)
					else:
						return await ctx.send('color error')
				elif color:
					color = int(color.strip('#'), 16)
					em.color = discord.Color(color)
				if data.get('description'):
					em.description = data['description']
				if data.get('desc'):
					em.description = data['desc']
				if data.get('title'):
					em.title = data['title']
				if data.get('url'):
					em.url = data['url']
				author = data.get('author')
				icon, url = data.get('icon'), data.get('url')

				if author:
					em._author = {'name': author}
					if icon:
						em._author['icon_url'] = icon
					if url:
						em._author['url'] = url
				label,link,emoji = data.get("label") or None, data.get("link" or None),data.get('emoji' or None)
				if label:
					if link:
						url=link
						view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
				else:
					if link:
						if emoji:
							view.add_item(discord.ui.Button(label=label, emoji=emoji, url=link))
				# label,link = data.get("label") or None, data.get("link" or None)
				# if label:
				# 	if link:
				# 		try:
				# 			emoji=label[i].get("emoji")
				# 		except:
				# 			emoji=None
				# 		url=link
				# 		view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))

				field, value = data.get('field'), data.get('value')
				inline = False if str(data.get('inline')).lower() == 'false' else True
				if field and value:
					em.add_field(name=field, value=value, inline=inline)

				if data.get('thumbnail'):
					em._thumbnail = {'url': data['thumbnail']}

				if data.get('image'):
					em._image = {'url': data['image']}

				if data.get('delete'):
					delete=int(data['delete'])
				else:
					delete=None

				if data.get('footer'):
					em._footer = {'text': data.get('footer')}
					if data.get('icon'):
						em._footer['icon_url'] = data.get('icon')

				if 'timestamp' in data.keys() and len(data.keys()) == 1:
					em.timestamp = datetime.datetime.now()
		except IndexError:
			return await send_error(ctx, f"Syntax Error in Embed Format Please use [this embed creator](https://rival.rocks/embed)")
		except Exception as e:
			return await send_error(ctx, f"{e}")
	else:
		em=None
		try:
			for field in get_parts(params):
				data = parse_field(field)
				if data.get('delete'):
					delete=int(str(data['delete']))
				else:
					delete=None
				if data.get('content'):
					content=data['content']
				else:
					content=None
				label,link,emoji = data.get("label") or None, data.get("link" or None),data.get('emoji' or None)
				if label:
					if link:
						url=link
						view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
				else:
					if link:
						if emoji:
							view.add_item(discord.ui.Button(label=label, emoji=emoji, url=link))
				# label,link = data.get("label") or None, data.get("link" or None)
				# if label:
				# 	if link:
				# 		try:
				# 			emoji=label[i].get("emoji")
				# 		except:
				# 			emoji=None
				# 		url=link
				# 		view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
		except IndexError:
			return await send_error(ctx, f"Syntax Error in Embed Format Please use [this embed creator](https://rival.rocks/embed)")
		except Exception as e:
			return await send_error(ctx, f"{e}")

	message=await ctx.send(delete_after=delete,content=content, embed=em, view=view)
	return message

def get_parts(string):
	for i, char in enumerate(string):
		if char == "{":
			ret = ""
			while char != "}":
				i += 1
				char = string[i]
				ret += char
			yield ret.rstrip('}')

def parse_field(string):
	ret = {}

	parts = string.split(':', 1)
	key = parts[0].strip().lower()
	val = ':'.join(parts[1:]).strip()

	ret[key] = val

	if '&&' in string:
		string = string.split('&&')
		for part in string:
			ret.update(parse_field(part))
	return ret

async def paginate_list(ctx, items, use_locking=False, only_author=False, index_entries=True):
	pages = TwoWayIterator(items)
	if index_entries:
		msg = await ctx.send(f"`{pages.index + 1}.` {pages.current()}")
	else:
		msg = await ctx.send(pages.current())

	async def next_result():
		new_content = pages.next()
		if new_content is None:
			return
		if index_entries:
			await msg.edit(content=f"`{pages.index + 1}.` {new_content}", embed=None)
		else:
			await msg.edit(content=new_content, embed=None)

	async def previous_result():
		new_content = pages.previous()
		if new_content is None:
			return
		await msg.edit(content=new_content, embed=None)

	async def done():
		await msg.edit(content=f"{pages.current()}")
		return True

	functions = {"<:left:934237439772483604>": previous_result, "<:right:934237462660788304>": next_result}
	if use_locking:
		functions["<:stop:958054042637054013>"] = done

	asyncio.ensure_future(reaction_buttons(ctx, msg, functions, only_author=only_author))



async def gpaginate_list(ctx, items, use_locking=False, only_author=False, index_entries=True):
	pages = TwoWayIterator(items)
	if index_entries:
		link=f"`{pages.index + 1}.` {pages.current()}"
		msg = await ctx.send(embed=discord.Embed(title='enemy', description=f"[image link]({link})", color=0x303135).set_image(url=f"`{pages.index + 1}.` {pages.current()}"))
	else:
		msg = await ctx.send(embed=discord.Embed(title='enemy', description=f"[image link]({pages.current()})", color=0x303135).set_image(url=pages.current()))

	async def next_result():
		new_content = pages.next()
		if new_content is None:
			return
		if index_entries:
			link=f"`{pages.index + 1}.` {new_content}"
			await msg.edit(embed=discord.Embed(title='enemy', description=f"[image link]({link})", color=0x303135).set_image(url=f"`{pages.index + 1}.` {new_content}"))
		else:
			await msg.edit(embed=discord.Embed(title='enemy', description=f"[image link]({new_content})", color=0x303135).set_image(url=new_content))

	async def previous_result():
		new_content = pages.previous()
		if new_content is None:
			return
		await msg.edit(embed=discord.Embed(title='enemy', description=f"[image link]({new_content})", color=0x303135).set_image(url=new_content))

	async def done():
		await msg.edit(embed=discord.Embed(title='enemy', description=f"[image link]({pages.current()})", color=0x303135).set_image(url=f"{pages.current()}"))
		return True

	functions = {"<:left:934237439772483604>": previous_result, "<:right:934237462660788304>": next_result}
	if use_locking:
		functions["<:stop:958054042637054013>"] = done

	asyncio.ensure_future(reaction_buttons(ctx, msg, functions, only_author=only_author))


async def reaction_buttons(
	ctx, message, functions, timeout=300.0, only_author=False, single_use=False, only_owner=False
):
	"""
	Handler for reaction buttons
	:param message     : message to add reactions to
	:param functions   : dictionary of {emoji : function} pairs. functions must be async.
						 return True to exit
	:param timeout     : time in seconds for how long the buttons work for.
	:param only_author : only allow the user who used the command use the buttons
	:param single_use  : delete buttons after one is used
	"""
	try:
		for emojiname in functions:
			await message.add_reaction(emojiname)
	except discord.errors.Forbidden:
		return

	def check(payload):
		return (
			payload.message_id == message.id
			and str(payload.emoji) in functions
			and not payload.member == ctx.bot.user
			and (
				(payload.member.id == ctx.bot.owner_id)
				if only_owner
				else (payload.member == ctx.author or not only_author)
			)
		)

	while True:
		try:
			payload = await ctx.bot.wait_for("raw_reaction_add", timeout=timeout, check=check)

		except asyncio.TimeoutError:
			break
		else:
			try:
				exits = await functions[str(payload.emoji)]()
			except discord.errors.NotFound:
				# message was deleted
				return
			try:
				await message.remove_reaction(payload.emoji, payload.member)
			except discord.errors.NotFound:
				pass
			except discord.errors.Forbidden:
				await ctx.send(
					"`error: I'm missing required discord permission [ manage messages ]`"
				)
			if single_use or exits is True:
				break

	for emojiname in functions:
		try:
			await message.clear_reactions()
		except (discord.errors.NotFound, discord.errors.Forbidden):
			pass

async def marriage_buttons(
	ctx, message, functions, user, timeout=300.0, single_use=False, only_owner=False
):
	"""
	Handler for reaction buttons
	:param message     : message to add reactions to
	:param functions   : dictionary of {emoji : function} pairs. functions must be async.
						 return True to exit
	:param timeout     : time in seconds for how long the buttons work for.
	:param only_author : only allow the user who used the command use the buttons
	:param single_use  : delete buttons after one is used
	"""
	try:
		for emojiname in functions:
			await message.add_reaction(emojiname)
	except discord.errors.Forbidden:
		return

	def check(payload):
		return (
			payload.message_id == message.id
			and str(payload.emoji) in functions
			and not payload.member == ctx.bot.user
			and (
				(payload.member.id == ctx.bot.owner_id)
				if only_owner
				else (payload.member == user)
			)
		)

	while True:
		try:
			payload = await ctx.bot.wait_for("raw_reaction_add", timeout=timeout, check=check)

		except asyncio.TimeoutError:
			await message.edit(embed=discord.Embed(color=0x303135, description=f"`{user.mention} you ran out of time to accept {ctx.author.mention}'s proposal`"))
			break
		else:
			try:
				exits = await functions[str(payload.emoji)]()
			except discord.errors.NotFound:
				# message was deleted
				return
			try:
				await message.remove_reaction(payload.emoji, payload.member)
			except discord.errors.NotFound:
				pass
			except discord.errors.Forbidden:
				await ctx.send(
					"`error: I'm missing required discord permission [ manage messages ]`"
				)
			if single_use or exits is True:
				break

	for emojiname in functions:
		try:
			await message.clear_reactions()
		except (discord.errors.NotFound, discord.errors.Forbidden):
			pass


def message_embed(message):
	"""
	Creates a nice embed from message
	:param: message : discord.Message you want to embed
	:returns        : discord.Embed
	"""
	content = discord.Embed()
	content.set_author(name=f"{message.author}", icon_url=message.author.avatar_url)
	content.description = message.content
	content.set_footer(text=f"{message.guild.name} | #{message.channel.name}")
	content.timestamp = message.created_at
	content.colour = message.author.color
	if message.attachments:
		content.set_image(url=message.attachments[0].proxy_url)

	return content


def timefromstring(s):
	"""
	:param s : String to parse time from
	:returns : Time in seconds
	"""
	s = s.removeprefix("for")
	try:
		return int(Duration(s).to_seconds())
	except InvalidTokenError:
		return None


def stringfromtime(t, accuracy=4):
	"""
	:param t : Time in seconds
	:returns : Formatted string
	"""
	m, s = divmod(t, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)

	components = []
	if d > 0:
		components.append(f"{int(d)} day" + ("s" if d != 1 else ""))
	if h > 0:
		components.append(f"{int(h)} hour" + ("s" if h != 1 else ""))
	if m > 0:
		components.append(f"{int(m)} minute" + ("s" if m != 1 else ""))
	if s > 0:
		components.append(f"{int(s)} second" + ("s" if s != 1 else ""))

	return " ".join(components[:accuracy])



async def get_user(ctx, argument, fallback=None):
	if argument is None:
		return fallback
	try:
		return await commands.UserConverter().convert(ctx, argument)
	except commands.errors.BadArgument:
		return fallback


async def get_member(ctx, argument, fallback=None, try_user=False):
	if argument is None:
		return fallback
	try:
		return await commands.MemberConverter().convert(ctx, argument)
	except commands.errors.BadArgument:
		if try_user:
			return await get_user(ctx, argument, fallback)
		return fallback


async def get_textchannel(ctx, argument, fallback=None, guildfilter=None):
	if argument is None:
		return fallback
	if guildfilter is None:
		try:
			return await commands.TextChannelConverter().convert(ctx, argument)
		except commands.errors.BadArgument:
			return fallback
	else:
		result = discord.utils.find(
			lambda m: argument in (m.name, m.id), guildfilter.text_channels
		)
		return result or fallback


async def get_role(ctx, argument, fallback=None):
	if argument is None:
		return fallback
	try:
		return await commands.RoleConverter().convert(ctx, argument)
	except commands.errors.BadArgument:
		return fallback


async def get_color(ctx, argument: str, fallback=None):
	"""
	:param argument : hex or discord color name
	:param fallback : return this if not found
	:returns        : discord.Color or None
	"""
	if argument is None:
		return fallback
	try:
		return await commands.ColourConverter().convert(ctx, argument)
	except commands.errors.BadArgument:
		try:
			return await commands.ColourConverter().convert(ctx, "#" + argument)
		except commands.errors.BadArgument:
			return fallback


async def get_emoji(ctx, argument, fallback=None):
	if argument is None:
		return fallback
	try:
		return await commands.EmojiConverter().convert(ctx, argument)
	except commands.errors.BadArgument:
		try:
			return await commands.PartialEmojiConverter().convert(ctx, argument)
		except commands.errors.BadArgument:
			return fallback


async def get_guild(ctx, argument, fallback=None):
	result = discord.utils.find(lambda m: argument in (m.name, m.id), ctx.bot.guilds)
	return result or fallback


async def command_group_help(ctx, command=None):
	if command != None:
		commands=ctx.bot.get_command(command)
	else:
		commands=ctx.command
	count=0
	counter=0
	for command in commands.walk_commands():
		counter+=1
	embedss=[]
	l=[]
	if commands.name ==  "role":
		emb = discord.Embed(colour=int("747f8d", 16))
		count+=1
		emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
		emb.set_footer(text=f"Aliases: N/A ・ Module: cmds.py"+f" ・ Entry({count}/{counter})")
		emb.title=f"Command: role"
		emb.description="give or take a members roles"

		emb.add_field(name="Parameters", value="member, role", inline=True)
		emb.add_field(name="Permissions", value="Manage Roles", inline=True)
		emb.add_field(name="Usage", value=f"```Ruby\nSyntax: {await get_prefix(ctx=ctx)}role <@member> <role>\nExample: {await get_prefix(ctx=ctx)}role @cop#0001 img```", inline=False)
		embedss.insert(0, emb)
	for command in commands.walk_commands():  # iterate through all of the command's parents/subcommands
		if command.parents[0] == commands:  # check if the latest parent of the subcommand is the command itself
				#total=sum(1 for command in commands.cog)
			try:
				for command in command.walk_commands():
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
						emb.add_field(name="Permissions", value=perms.title(), inline=True)
					else:
						if command.brief:
							brief=command.brief
							emb.add_field(name="Parameters", value=brief, inline=True)
					if command.usage:
						usage=command.usage.replace("Swift", "")
						usage=usage.strip("```")
						if "Syntax: " in usage:
							if not "Syntax: !" in usage:
								usage=usage.replace("Syntax: ", f"Syntax: {await get_prefix(ctx=ctx)}")
							else:
								usage=usage.replace("Syntax: !", f"Syntax: {await get_prefix(ctx=ctx)}")
						if "Example: " in usage:
							if "Example: !" not in usage:
								usage=usage.replace("Example: ", f"Example: {await get_prefix(ctx=ctx)}")
							else:
								usage=usage.replace("Example: !", f"Example: {await get_prefix(ctx=ctx)}")
						emb.add_field(name="Usage", value=f"```Ruby\n{usage}```", inline=False)
					embedss.append(emb)
			except:
				pass
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
				emb.add_field(name="Permissions", value=perms.title(), inline=True)
			else:
				if command.brief:
					brief=command.brief
					emb.add_field(name="Parameters", value=brief, inline=True)
				emb.add_field(name="Permissions", value="Send Messages", inline=True)
			if command.usage:
				usage=command.usage.replace("Swift", "")
				usage=usage.strip("```")
				if "Syntax: " in usage:
					if not "Syntax: !" in usage:
						usage=usage.replace("Syntax: ", f"Syntax: {await get_prefix(ctx=ctx)}")
					else:
						usage=usage.replace("Syntax: !", f"Syntax: {await get_prefix(ctx=ctx)}")
				if "Example: " in usage:
					if "Example: !" not in usage:
						usage=usage.replace("Example: ", f"Example: {await get_prefix(ctx=ctx)}")
					else:
						usage=usage.replace("Example: !", f"Example: {await get_prefix(ctx=ctx)}")
				emb.add_field(name="Usage", value=f"```Ruby\n{usage}```", inline=False)
			embedss.append(emb)
		else:  # the else statement is optional.
			continue
		#embed.description="..."
		#embed.title=f"!{command.qualified_name}"
	# if commands.name ==  "role":
	# 	emb = discord.Embed(colour=int("747f8d", 16))
	# 	emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
	# 	emb.set_footer(text=f"Aliases: N/A ・ Module: cmds.py"+f" ・ Entry({count}/{counter})")
	# 	emb.title=f"Command: role"
	# 	emb.description="give or take a members roles"
	# 	emb.add_field(name="Parameters", value="member, role", inline=True)
	# 	emb.add_field(name="Permissions", value="Manage Roles", inline=True)
	# 	emb.add_field(name="Usage", value="```Swift\nSyntax: !role <@member> <role>\nExample: !role @cop#0001 img````", inline=False)
	# 	embedss.insert(0, emb)
	paginator = pg.Paginator(ctx.bot, embedss, ctx, invoker=ctx.author.id)
	if len(embedss) > 1:
		paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.red)
	#paginator.add_button('delete', label='Close the paginator', emoji='⏹')
		paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.red)
	await paginator.start()
	#await ctx.send_help(ctx.command or ctx.command.root_parent.name)


async def send_command_help(ctx):
	"""Sends default command help"""
	await ctx.send_help(ctx.invoked_subcommand or ctx.command)

async def check_priv(ctx, user):
	member=user
	try:
		# Self checks
		if member == ctx.author:
			return await ctx.reply(embed=discord.Embed(color=0xfaa61a, description=f"<:warning:1021286736883621959> {ctx.author.mention}: **you can't {ctx.command.name} yourself**"))
		if member.id == ctx.bot.user.id:
			return await ctx.send(":clown:")

		# Check if user bypasses
		if ctx.author.id == ctx.guild.owner.id:
			return False
		if member.id == ctx.guild.owner.id:
			return await ctx.reply(embed=discord.Embed(color=0xfaa61a, description=f"<:warning:1021286736883621959> {ctx.author.mention}: **you can't {ctx.command.name} the owner**"))
		if ctx.author.top_role == member.top_role:
			return await ctx.reply(embed=discord.Embed(color=0xfaa61a, description=f"<:warning:1021286736883621959> {ctx.author.mention}: **you can't {ctx.command.name} someone who has the same permissions as you**"))
		if ctx.author.top_role < member.top_role:
			return await ctx.reply(embed=discord.Embed(color=0xfaa61a, description=f"<:warning:1021286736883621959> {ctx.author.mention}: **nope, you can't {ctx.command.name} someone higher than yourself**"))
	except Exception:
		pass



def escape_md(s):
	transformations = {regex.escape(c): "\\" + c for c in ("*", "`", "__", "~", "\\", "||")}

	def replace(obj):
		return transformations.get(regex.escape(obj.group(0)), "")

	pattern = regex.compile("|".join(transformations.keys()))
	return pattern.sub(replace, s)

def escape_mdd(s):
	transformations = {regex.escape(c): "\\" + c for c in ("*", "`", "", "~", "\\", "||")}

	def replace(obj):
		return transformations.get(regex.escape(obj.group(0)), "")

	pattern = regex.compile("|".join(transformations.keys()))
	return pattern.sub(replace, s)


def map_to_range(input_value, input_start, input_end, output_start, output_end):
	return output_start + ((output_end - output_start) / (input_end - input_start)) * (
		input_value - input_start
	)


def rgb_to_hex(rgb):
	"""
	:param rgb : RBG color in tuple of 3
	:return    : Hex color string
	"""
	r, g, b = rgb

	def clamp(x):
		return max(0, min(x, 255))

	return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))


async def color_from_image_url(url,
	fallback="E74C3C",
	return_color_object=False,
	size_limit=False,
	ignore_errors=True,
):
	"""
	:param url      : image url
	:param fallback : the color to return in case the operation fails
	:return         : hex color code of the most dominant color in the image
	"""
	if url.strip() == "":
		return fallback
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				image = Image.open(io.BytesIO(await response.read()))
				if size_limit and sum(image.size) > 2048:
					raise ValueError("Image is too large")
				colors = await asyncio.get_running_loop().run_in_executor(
					None, lambda: colorgram.extract(image, 1)
				)
				dominant_color = colors[0].rgb
	except Exception as e:
		if ignore_errors:
			return fallback
		else:
			raise e

	if return_color_object:
		return dominant_color
	else:
		return rgb_to_hex(dominant_color)


def find_unicode_emojis(text):
	"""Finds and returns all unicode emojis from a string"""
	emoji_list = set()

	# yeah.
	# it's an emoji regex.
	# what do you want from me.
	data = regex.findall(
		r"(?:\U0001f1e6[\U0001f1e8-\U0001f1ec\U0001f1ee\U0001f1f1\U0001f1f2\U0001f1f4\U0001f1f6-\U0001f1fa\U0001f1fc\U0001f1fd\U0001f1ff])\|(?:\U0001f1e7[\U0001f1e6\U0001f1e7\U0001f1e9-\U0001f1ef\U0001f1f1-\U0001f1f4\U0001f1f6-\U0001f1f9\U0001f1fb\U0001f1fc\U0001f1fe\U0001f1ff])|(?:\U0001f1e8[\U0001f1e6\U0001f1e8\U0001f1e9\U0001f1eb-\U0001f1ee\U0001f1f0-\U0001f1f5\U0001f1f7\U0001f1fa-\U0001f1ff])|(?:\U0001f1e9[\U0001f1ea\U0001f1ec\U0001f1ef\U0001f1f0\U0001f1f2\U0001f1f4\U0001f1ff])|(?:\U0001f1ea[\U0001f1e6\U0001f1e8\U0001f1ea\U0001f1ec\U0001f1ed\U0001f1f7-\U0001f1fa])|(?:\U0001f1eb[\U0001f1ee-\U0001f1f0\U0001f1f2\U0001f1f4\U0001f1f7])|(?:\U0001f1ec[\U0001f1e6\U0001f1e7\U0001f1e9-\U0001f1ee\U0001f1f1-\U0001f1f3\U0001f1f5-\U0001f1fa\U0001f1fc\U0001f1fe])|(?:\U0001f1ed[\U0001f1f0\U0001f1f2\U0001f1f3\U0001f1f7\U0001f1f9\U0001f1fa])|(?:\U0001f1ee[\U0001f1e8-\U0001f1ea\U0001f1f1-\U0001f1f4\U0001f1f6-\U0001f1f9])|(?:\U0001f1ef[\U0001f1ea\U0001f1f2\U0001f1f4\U0001f1f5])|(?:\U0001f1f0[\U0001f1ea\U0001f1ec-\U0001f1ee\U0001f1f2\U0001f1f3\U0001f1f5\U0001f1f7\U0001f1fc\U0001f1fe\U0001f1ff])|(?:\U0001f1f1[\U0001f1e6-\U0001f1e8\U0001f1ee\U0001f1f0\U0001f1f7-\U0001f1fb\U0001f1fe])|(?:\U0001f1f2[\U0001f1e6\U0001f1e8-\U0001f1ed\U0001f1f0-\U0001f1ff])|(?:\U0001f1f3[\U0001f1e6\U0001f1e8\U0001f1ea-\U0001f1ec\U0001f1ee\U0001f1f1\U0001f1f4\U0001f1f5\U0001f1f7\U0001f1fa\U0001f1ff])|\U0001f1f4\U0001f1f2|(?:\U0001f1f4[\U0001f1f2])|(?:\U0001f1f5[\U0001f1e6\U0001f1ea-\U0001f1ed\U0001f1f0-\U0001f1f3\U0001f1f7-\U0001f1f9\U0001f1fc\U0001f1fe])|\U0001f1f6\U0001f1e6|(?:\U0001f1f6[\U0001f1e6])|(?:\U0001f1f7[\U0001f1ea\U0001f1f4\U0001f1f8\U0001f1fa\U0001f1fc])|(?:\U0001f1f8[\U0001f1e6-\U0001f1ea\U0001f1ec-\U0001f1f4\U0001f1f7-\U0001f1f9\U0001f1fb\U0001f1fd-\U0001f1ff])|(?:\U0001f1f9[\U0001f1e6\U0001f1e8\U0001f1e9\U0001f1eb-\U0001f1ed\U0001f1ef-\U0001f1f4\U0001f1f7\U0001f1f9\U0001f1fb\U0001f1fc\U0001f1ff])|(?:\U0001f1fa[\U0001f1e6\U0001f1ec\U0001f1f2\U0001f1f8\U0001f1fe\U0001f1ff])|(?:\U0001f1fb[\U0001f1e6\U0001f1e8\U0001f1ea\U0001f1ec\U0001f1ee\U0001f1f3\U0001f1fa])|(?:\U0001f1fc[\U0001f1eb\U0001f1f8])|\U0001f1fd\U0001f1f0|(?:\U0001f1fd[\U0001f1f0])|(?:\U0001f1fe[\U0001f1ea\U0001f1f9])|(?:\U0001f1ff[\U0001f1e6\U0001f1f2\U0001f1fc])|(?:\U0001f3f3\ufe0f\u200d\U0001f308)|(?:\U0001f441\u200d\U0001f5e8)|(?:[\U0001f468\U0001f469]\u200d\u2764\ufe0f\u200d(?:\U0001f48b\u200d)?[\U0001f468\U0001f469])|(?:(?:(?:\U0001f468\u200d[\U0001f468\U0001f469])|(?:\U0001f469\u200d\U0001f469))(?:(?:\u200d\U0001f467(?:\u200d[\U0001f467\U0001f466])?)|(?:\u200d\U0001f466\u200d\U0001f466)))|(?:(?:(?:\U0001f468\u200d\U0001f468)|(?:\U0001f469\u200d\U0001f469))\u200d\U0001f466)|[\u2194-\u2199]|[\u23e9-\u23f3]|[\u23f8-\u23fa]|[\u25fb-\u25fe]|[\u2600-\u2604]|[\u2638-\u263a]|[\u2648-\u2653]|[\u2692-\u2694]|[\u26f0-\u26f5]|[\u26f7-\u26fa]|[\u2708-\u270d]|[\u2753-\u2755]|[\u2795-\u2797]|[\u2b05-\u2b07]|[\U0001f191-\U0001f19a]|[\U0001f1e6-\U0001f1ff]|[\U0001f232-\U0001f23a]|[\U0001f300-\U0001f321]|[\U0001f324-\U0001f393]|[\U0001f399-\U0001f39b]|[\U0001f39e-\U0001f3f0]|[\U0001f3f3-\U0001f3f5]|[\U0001f3f7-\U0001f3fa]|[\U0001f400-\U0001f4fd]|[\U0001f4ff-\U0001f53d]|[\U0001f549-\U0001f54e]|[\U0001f550-\U0001f567]|[\U0001f573-\U0001f57a]|[\U0001f58a-\U0001f58d]|[\U0001f5c2-\U0001f5c4]|[\U0001f5d1-\U0001f5d3]|[\U0001f5dc-\U0001f5de]|[\U0001f5fa-\U0001f64f]|[\U0001f680-\U0001f6c5]|[\U0001f6cb-\U0001f6d2]|[\U0001f6e0-\U0001f6e5]|[\U0001f6f3-\U0001f6f6]|[\U0001f910-\U0001f91e]|[\U0001f920-\U0001f927]|[\U0001f933-\U0001f93a]|[\U0001f93c-\U0001f93e]|[\U0001f940-\U0001f945]|[\U0001f947-\U0001f94b]|[\U0001f950-\U0001f95e]|[\U0001f980-\U0001f991]|\u00a9|\u00ae|\u203c|\u2049|\u2122|\u2139|\u21a9|\u21aa|\u231a|\u231b|\u2328|\u23cf|\u24c2|\u25aa|\u25ab|\u25b6|\u25c0|\u260e|\u2611|\u2614|\u2615|\u2618|\u261d|\u2620|\u2622|\u2623|\u2626|\u262a|\u262e|\u262f|\u2660|\u2663|\u2665|\u2666|\u2668|\u267b|\u267f|\u2696|\u2697|\u2699|\u269b|\u269c|\u26a0|\u26a1|\u26aa|\u26ab|\u26b0|\u26b1|\u26bd|\u26be|\u26c4|\u26c5|\u26c8|\u26ce|\u26cf|\u26d1|\u26d3|\u26d4|\u26e9|\u26ea|\u26fd|\u2702|\u2705|\u270f|\u2712|\u2714|\u2716|\u271d|\u2721|\u2728|\u2733|\u2734|\u2744|\u2747|\u274c|\u274e|\u2757|\u2763|\u2764|\u27a1|\u27b0|\u27bf|\u2934|\u2935|\u2b1b|\u2b1c|\u2b50|\u2b55|\u3030|\u303d|\u3297|\u3299|\U0001f004|\U0001f0cf|\U0001f170|\U0001f171|\U0001f17e|\U0001f17f|\U0001f18e|\U0001f201|\U0001f202|\U0001f21a|\U0001f22f|\U0001f250|\U0001f251|\U0001f396|\U0001f397|\U0001f56f|\U0001f570|\U0001f587|\U0001f590|\U0001f595|\U0001f596|\U0001f5a4|\U0001f5a5|\U0001f5a8|\U0001f5b1|\U0001f5b2|\U0001f5bc|\U0001f5e1|\U0001f5e3|\U0001f5e8|\U0001f5ef|\U0001f5f3|\U0001f6e9|\U0001f6eb|\U0001f6ec|\U0001f6f0|\U0001f930|\U0001f9c0|[#|0-9]\u20e3",
		text,
	)
	for word in data:
		name = emoji_literals.UNICODE_TO_NAME.get(word)
		if name is not None:
			emoji_list.add(name)

	return emoji_list


def find_custom_emojis(text):
	"""Finds and returns all custom discord emojis from a string"""
	emoji_list = set()
	data = regex.findall(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>", text)
	for _a, emoji_name, emoji_id in data:
		emoji_list.add((emoji_name, emoji_id))

	return emoji_list


async def image_info_from_url(url):
	"""Return dictionary containing filesize, filetype and dimensions of an image."""
	async with aiohttp.ClientSession() as session:
		async with session.get(str(url)) as response:
			filesize = int(response.headers.get("Content-Length")) / 1024
			filetype = response.headers.get("Content-Type")
			try:
				image = Image.open(io.BytesIO(await response.read()))
			except UnidentifiedImageError:
				return None

			dimensions = image.size
			if filesize > 1024:
				filesize = f"{filesize/1024:.2f}MB"
			else:
				filesize = f"{filesize:.2f}KB"

			return {
				"filesize": filesize,
				"filetype": filetype,
				"dimensions": f"{dimensions[0]}x{dimensions[1]}",
			}


class OptionalSubstitute(dict):
	def __missing__(self, key):
		return "{" + key + "}"

def substitute(user, guild, message):
	substitutes = OptionalSubstitute(
		{
			"mention": user.mention,
			"user": user,
			"id": user.id,
			"server": guild.name,
			"guild": guild.name,
			"icon": guild.icon,
			"username": user.name,
			"mc": guild.member_count,
			"av": user.display_avatar
		}
	)
	content = message.format_map(substitutes)
	return content

def sub(user, guild, messageformat):
	"""Creates and returns embed for welcome message."""
	if messageformat is None:
		messageformat = ""

	substitutes = OptionalSubstitute(
		{
			"mention": user.mention,
			"user": user,
			"id": user.id,
			"server": guild.name,
			"guild": guild.name,
			"icon": guild.icon,
			"username": user.name,
			"mc": guild.member_count,
			"av": user.display_avatar
		}
	)
	content = messageformat.format_map(substitutes)
	return content


def create_welcome_embed(user, guild, messageformat):
	"""Creates and returns embed for welcome message."""
	if messageformat is None:
		messageformat = ""

	#content = discord.Embed(title="New member! :wave:", color=int("5dadec", 16))
	#content.set_thumbnail(url=user.avatar_url)
	#content.timestamp = arrow.utcnow().datetime
	#content.set_footer(text=f"👤#{len(guild.members)}")
	substitutes = OptionalSubstitute(
		{
			"mention": user.mention,
			"user": user,
			"id": user.id,
			"server": guild.name,
			"guild": guild.name,
			"username": user.name,
			"mc": guild.member_count
		}
	)
	content = messageformat.format_map(substitutes)
	return content


def create_goodbye_message(user, guild, messageformat):
	"""Formats a goodbye message."""
	if messageformat is None:
		messageformat = "Goodbye **{username}** {mention}"

	substitutes = OptionalSubstitute(
		{
			"mention": user.mention,
			"user": user,
			"id": user.id,
			"server": guild.name,
			"guild": guild.name,
			"username": user.name,
		}
	)
	return messageformat.format_map(substitutes)


def activities_string(activities, markdown=True, show_emoji=True):
	"""Print user activity as it shows up on the sidebar."""
	if not activities:
		return None

	custom_activity = None
	base_activity = None
	spotify_activity = None
	for act in activities:
		if isinstance(act, discord.CustomActivity):
			custom_activity = act
		elif isinstance(act, discord.BaseActivity):
			base_activity = act
		elif isinstance(act, discord.Spotify):
			spotify_activity = act
		else:
			print(act)
			return "Unknown activity"

	emoji = custom_activity.emoji if custom_activity else None
	message = None

	if message is None and spotify_activity is not None:
		message = "Listening to " + ("**Spotify**" if markdown else "Spotify")

	if custom_activity:
		emoji = custom_activity.emoji
		message = custom_activity.name

	if message is None and base_activity is not None:
		if base_activity.type == discord.ActivityType.playing:
			prefix = "Playing"
		elif base_activity.type == discord.ActivityType.streaming:
			prefix = "Streaming"
		elif base_activity.type == discord.ActivityType.listening:
			prefix = "Listening"
		elif base_activity.type == discord.ActivityType.watching:
			prefix = "Watching"
		elif base_activity.type == discord.ActivityType.streaming:
			prefix = "Streaming"

		message = prefix + " " + (f"**{base_activity.name}**" if markdown else base_activity.name)

	text = ""
	if emoji is not None and show_emoji:
		text += f"{emoji} "

	if message is not None:
		text += message

	return text if text != "" else None


async def send_tasks_result_list(ctx, successful_operations, failed_operations):
	content = discord.Embed(
		color=(color if successful_operations else int("dd2e44", 16))
	)
	rows = []
	for op in successful_operations:
		rows.append(f":white_check_mark: {op}")
	for op in failed_operations:
		rows.append(f":x: {op}")

	content.description = "\n".join(rows)
	await ctx.send(embed=content)


def donor():
	async def predicate(ctx):
		if ctx.author.id in ctx.bot.owner_ids:
			return True
		if ctx.author.id in ctx.bot.cache.donators:
			return True
		if await queries.is_donator(ctx, ctx.author):
			return True
		if ctx.author in orjson.loads(await ctx.bot.redis.get("donators")):
			return True
		ls=await ctx.bot.db.execute("""SELECT user_id FROM dnrr""", as_list=True)
		if ctx.author.id in ls:
			return True
		raise donorCheckFailure

	return commands.check(predicate)

def donor_server():
	async def predicate(ctx):
		if ctx.author.id in ctx.bot.owner_ids:
			return True
		if ctx.author.id in ctx.bot.cache.donators:
			return True
		if ctx.guild.owner.id in ctx.bot.cache.donators:
			return True
		if await queries.is_donator(ctx, ctx.guild.owner):
			return True
		if await queries.is_donator(ctx, ctx.author):
			return True
		raise donorCheckFailure

	return commands.check(predicate)

def get_member_permissions(permissions):
	perms = []
	
	if permissions.administrator:
		perms.append("Administrator")
		
		return "Administrator"
	
	if permissions.manage_guild:
		perms.append("Manage guild")
		
	if permissions.ban_members:
		perms.append("Ban members")
		
	if permissions.kick_members:
		perms.append("Kick members")
		
	if permissions.manage_channels:
		perms.append("Manage channels")
		
	if permissions.manage_emojis:
		perms.append("Manage custom emotes")
		
	if permissions.manage_messages:
		perms.append("Manage messages")
		
	if permissions.manage_permissions:
		perms.append("Manage permissions")
		
	if permissions.manage_roles:
		perms.append("Manage roles")
		
	if permissions.mention_everyone:
		perms.append("Mention everyone")
		
	if permissions.manage_emojis:
		perms.append("Manage emojis")
		
	if permissions.manage_webhooks:
		perms.append("Manage webhooks")
		
	if permissions.move_members:
		perms.append("Move members")
		
	if permissions.mute_members:
		perms.append("Mute members")
		
	if permissions.deafen_members:
		perms.append("Deafen members")
		
	if permissions.priority_speaker:
		perms.append("Priority speaker")
		
	if permissions.view_audit_log:
		perms.append("See audit log")
		
	if permissions.create_instant_invite:
		perms.append("Create instant invites")
	
	return ", ".join(perms) if perms else 'No permissions'


def format_html(template, replacements):
	def dictsub(m):
		return str(replacements[m.group().strip("$")])

	return re.sub(r"\$(\S*?)\$", dictsub, template)


async def render_html(bot, payload):
	async with aiohttp.ClientSession() as session:
		try:
			async with session.post(
				f"http://127.0.0.1:3000/html", data=payload
			) as response:
				if response.status == 200:
					bot.cache.stats_html_rendered += 1
					buffer = io.BytesIO(await response.read())
					return buffer
				raise exceptions.RendererError(f"{response.status} : {await response.text()}")
		#except aiohttp.client_exceptions.ClientConnectorError:
		except Exception as e:
			print(e)
			#raise exceptions.RendererError("Unable to connect to the HTML Rendering server")

def ordinal(n):
	"""Return number with ordinal suffix eg. 1st, 2nd, 3rd, 4th..."""
	return str(n) + {1: "st", 2: "nd", 3: "rd"}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")

class TwoWayIterator:
	"""Two way iterator class that is used as the backend for paging."""

	def __init__(self, list_of_stuff):
		self.items = list_of_stuff
		self.index = 0

	def next(self):
		if self.index == len(self.items) - 1:
			return None
		self.index += 1
		return self.items[self.index]

	def previous(self):
		if self.index == 0:
			return None
		self.index -= 1
		return self.items[self.index]

	def current(self):
		return self.items[self.index]
