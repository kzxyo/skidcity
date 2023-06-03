import logging
logger = logging.getLogger(__name__)
import discord_ios,aiohttp, multiprocessing,tweepy,uvloop
import os,typing,sys,json,discord,ast,inspect,traceback,re, asyncio
from time import time
from discord import Activity, ActivityType, AllowedMentions, Intents, Status
from discord.ext import commands, ipc
from dotenv import load_dotenv
from cogs.VoiceMasterr import PersistentView
from modules import cache, cachee, log, maria, util,exceptions,consts,confirmation2,queries
from modules.util import getheaders, proxy_scrape
from modules.help import EmbedHelpCommand
from discord.ext.ipc.server import Server
from discord.ext.ipc.objects import ClientPayload
from redis.asyncio import Redis as rd
import orjson
from typing import Dict

load_dotenv(verbose=True)
log.make_dask_sink('rival')
TOKEN = os.environ["TOKEN"]
prefix = "!"
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_RETAIN'] = 'True'
from time import sleep

def progress(percent=0, width=30):
	# The number of hashes to show is based on the percent passed in. The
	# number of blanks is whatever space is left after.
	hashes = width * percent // 100
	blanks = width - hashes

	print('\r[', hashes*'#', blanks*' ', ']', f' {percent:.0f}%', sep='',
		end='', flush=True)

print('This will take a moment')
for i in range(101):
	progress(i)
	sleep(0.1)

# Newline so command prompt isn't on the same line
print()
#oauthclient=oauth.OAuth2Client(client_id=1002294763241885847,client_secret='Q0zs7UgvZeUN3EpXp2oYkMP7rZdOXHXM',redirect_uri="https://rival.rocks/",scopes=['identify','emailconnections','guilds','guilds.join','guilds.members.read','bot','messages.read','applications.commands'])

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
class enemy(commands.Bot):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.default_prefix = False
		self.logger = logger
		self.start_time = time()
		self.global_cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.member)
		self.dglobal_cd = commands.CooldownMapping.from_cooldown(1, 300, commands.BucketType.member)
		self.db = maria.MariaDB(self)
		self.cache = cache.Cache(self)
		self.version = "1.0"
		self.twitter_blue = int("1da1f2", 16)
		auth = tweepy.OAuthHandler("4R8BAE5oIi2PbmoVdSfAP7fQC", "caDyyTyOahyTTRjT59ZCYxBEbprOltC3HrtxhxOO9Ouv3m5VMR")
		auth.set_access_token("4259600601-RUI8J2afi16LCTgfPsRJ8jFtR5PDgxEc8s3oRnc", "nTWXjuMhnF3vFVLdgvbaMrvjkvQ4qfMAyBhCBzhM9Ax2v")
		self.twtapi = tweepy.API(auth)
		self.session=None
		self.donators=[]
		#self.yes="<:yes:940723483204255794>"
		self.yes="<:check:1021252651809259580>"
		#self.no="<:no:940723951947120650>"
		self.rival_api="https://japi.rest/discord/v1/"
		self.no='<:x_:1021273367749337089>'
		#self.warn='{self.bot.warn}'
		self.warn='<:warning:1021286736883621959>'
		self.color=0xD6BCD0
		self.token=os.environ["TOKEN"]
		self.extensions_loaded = False
		self.ipc = ipc.Server(self, secret_key="Q0zs7UgvZeUN3EpXp2oYkMP7rZdOXHXM")

	@Server.route()
	async def get_user_data(self, data: ClientPayload) -> Dict:
		user = self.get_user(data.user_id)
		return user._to_minimal_user_json()

	async def close(self):
		await self.db.cleanup()
		await super().close()

	async def on_message(self, message):
		if not bot.is_ready():
			return

		await super().on_message(message)

	@property
	def member_count(self) -> int:
		return sum(len(guild.members) for guild in self.guilds)

	@property
	def guild_count(self) -> int:
		return len(self.guilds)


	async def setup_hook(self):
		self.session = aiohttp.ClientSession(loop=self.loop)
		self.redis=await rd.from_url("redis://localhost")
		bot.loop.create_task(self.db.initialize_pool())
		bot.loop.create_task(self.cache.initialize_settings_cache())
		bot.add_view(PersistentView(bot))

bot = enemy(
	owner_ids=[983914775236980776,915674578259427348,236522835089031170,469965172702969877,714703136270581841,352190010998390796,704874297247924235,330445977183977483,956618986110476318,164189971673120768,728095627757486081],
	help_command=EmbedHelpCommand(),
	command_prefix=util.determine_prefix,
	case_insensitive=True,
	strip_after_prefix=True,
	allowed_mentions=discord.AllowedMentions(users=True, roles=False, replied_user=True, everyone=False),
	max_messages=500,
	#activity=Activity(type=ActivityType.playing, name="Booting up..."),
	#status=Status.idle
	activity=discord.Activity(name="!help", type=5),
	shard_count=6,
	shard_id=4,
	heartbeat_timeout=150,
	intents=discord.Intents(
		guilds=True,
		members=True,  # requires verification
		bans=True,
		emojis=True,
		integrations=True,
		webhooks=True,
		invites=True,
		voice_states=True,
		presences=False,  # requires verification
		messages=True,
		reactions=True,
		typing=True,
		message_content=True,
	))

extensions = [
	"errorhandler",
	"events",
	"VoiceMasterr",
	"information",
	"google",
	"mod",
	"owner",
	"miscellaneous",
	"lastfm",
	"user",
	"chat",
	"settingss",
	"asyncstreamer",
	"twitterr",
#	"vanitycog",
	"utility",
	"crypto",
#	"stats",
#	"words",
	"cmds",
	"timer",
	"embed",
	"eemoji",
	"conversion",
	"docs",
	"antievents",
	"anticmds",
	"namehistoryy",
#	"cluster",
]



@bot.before_invoke
async def before_any_command(ctx):
	ctx.timer = time()
	try:
		await ctx.typing()
	except discord.errors.Forbidden:
		pass


@bot.check
async def check_for_blacklist(ctx):
	"""Check command invocation context for blacklist triggers"""
	#if await bot.db.execute("""SELECT * FROM stfu WHERE user_id = %s AND guild_id = %s""", ctx.author.id, ctx.guild.id) and ctx.author.id != 714703136270581841:
	if ctx.guild.id in bot.cache.stfu:
		if ctx.author.id in bot.cache.stfu[ctx.guild.id]:
			raise exceptions.BlacklistedUser()
	return await util.is_blacklisted(ctx)

@bot.check
async def check_privacy_agreement(ctx):
	disabled=["jsk", "Jishaku","owners"]
	if not await bot.db.execute("""SELECT * FROM users WHERE user_id = %s""", ctx.author.id):
		content=discord.Embed()
		try:
			msg=await ctx.send(embed=discord.Embed(color=0xfffff,description="do you agree to our [privacy policy](https://rival.rocks/privacy) and for your data to be used for commands?\n**WARNING** disagreeing will blacklist you from using commands"))
		except:
			return
		async def confirm_agree():
			await msg.delete()
			await bot.db.execute("""INSERT INTO users VALUES(%s) ON DUPLICATE KEY UPDATE user_id = VALUES(user_id)""", ctx.author.id)
			return True

		async def cancel_agree():
			content.colour=consts.bad
			await bot.db.execute("""INSERT INTO nodata VALUES(%s) ON DUPLICATE KEY UPDATE user_id = VALUES(user_id)""", ctx.author.id)
			content.description=f"{consts.no} {ctx.author.mention}: **you have been blacklisted due to not agreeing to our policies**"
			await msg.edit(embed=content, view=None)
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'support server', url="https://discord.gg/72ZKdJhb8N"))
			await ctx.author.send(view=view,embed=discord.Embed(color=0xfffff, description="you pressed **NO** on the confirmation of agreeance to our privacy policy meaning you cannot use the bot if this is a mistake join the support server below and open a ticket in #support or send **!nodata False**"))
			return False

		confirmed=await confirmation2.confirm(ctx.bot, ctx, msg)
		if confirmed == True:
			await confirm_agree()
			if ctx.command.cog_name in disabled:
				return
			else:
				pass
			#await ctx.reinvoke()
			return
		elif confirmed == False:
			await cancel_agree()
		else:
			return
	else:
		return True


@bot.event
async def on_message_edit(before, after):
	if not before.author.bot and before.content != after.content:
		await bot.process_commands(after)


@bot.check
async def cooldown_check(ctx):
	if await queries.is_donator(ctx, ctx.author):
		return True
	if not await queries.is_donator(ctx, ctx.author):
		if str(ctx.invoked_with).lower() == "help":
			return True
		bucket = ctx.bot.global_cd.get_bucket(ctx.message)
		retry_after = bucket.update_rate_limit()
		if retry_after:
			raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.member)
		return True


@bot.event
async def on_ready():
	if not bot.extensions_loaded:
		await load_extensions()
	latencies = bot.latencies
	logger.info(f"Loading complete | running {len(latencies)} shards")
	for shard_id, latency in latencies:
		logger.info(f"Shard [{shard_id}] - HEARTBEAT {latency}s")


async def load_extensions():
	logger.info("Loading extensions...")
	for extension in extensions:
		try:
			await bot.load_extension(f"cogs.{extension}")
			logger.info(f"Loaded [ {extension} ]")
		except Exception as error:
			logger.error(f"Error loading [ {extension} ]")
			traceback.print_exception(type(error), error, error.__traceback__)

	await bot.load_extension("jishaku")
	bot.extensions_loaded = True
	logger.info("All extensions loaded successfully!")

def run(token):
	bot.run(token)

if __name__ == "__main__":
	tokens=["MTAyODE0NTEwOTU0MTMyNjkyOA.GjqSBS.gSTSXfeF3DnO6mxCXJsmgayT4EQccE6VyWSVtQ","MTAwMjI5NDc2MzI0MTg4NTg0Nw.GpX-Q5.oQB61lRTTlYcjPikv-zbEkBYUwJaMgQC2-OsfU"]
	logger.info(f'Using default prefix "{prefix}"')
	try:
		with open(os.getenv("temp")+"\\proxies.txt", 'w'): pass
		proxy_scrape()
	except:
		pass
	bot.start_time = time()
	bot.token=os.environ["TOKEN"]
	#for i in tokens:
	#	token=i
	#	jobs=[]
	#	p=multiprocessing.Process(target=run, args=(token,))
	#	jobs.append(p)
	#	p.start()
	run(tokens[1])


# class EnemyCluster(enemy):
# 	def __init__(self, **kwargs):
# 		self.cluster_name = kwargs.pop("cluster_name")
# 		self.cluster_id = kwargs.pop("cluster_id")
# 		super().__init__(**kwargs)

# 		self.logger = log.get_logger(f"Rival#{self.cluster_name}")

# 		self.run(kwargs["token"])

# 	async def on_ready(self):
# 		self.logger.info(f"Cluster {self.cluster_name} ready")

# 	async def on_shard_ready(self, shard_id):
# 		self.logger.info(f"Shard {shard_id} ready")