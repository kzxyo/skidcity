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
class enemy(commands.AutoShardedBot):
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
	help_command=None,
	command_prefix="saddssdasai34ij44i3j2234ijkiojdfweijkoedoi3j24oi34j2oji423ij4dfeijkodfsioj435",
	case_insensitive=True,
	strip_after_prefix=True,
	allowed_mentions=discord.AllowedMentions(users=True, roles=False, replied_user=True, everyone=False),
	max_messages=500,
	#activity=Activity(type=ActivityType.playing, name="Booting up..."),
	status=Status.offline,
	#activity=discord.Activity(name="!help", type=5),
	shard_count=2,
	shard_ids=[0,1],
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
# 	"errorhandler",
# 	"events",
# 	"VoiceMasterr",
# 	"information",
# 	"google",
# 	"mod",
# 	"owner",
# 	"miscellaneous",
# 	"lastfm",
# 	"user",
# 	"chat",
# 	"settingss",
# 	"asyncstreamer",
# 	"twitterr",
# #	"vanitycog",
# 	"utility",
# 	"crypto",
# #	"stats",
# #	"words",
# 	"cmds",
# 	"timer",
# 	"embed",
# 	"eemoji",
# 	"conversion",
# 	"docs",
# 	"antievents",
# 	"anticmds",
	"namehistory2",
#	"cluster",
]


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
	tokens=["Nzc2MTI4NDEwNTQ3MTI2MzIy.GnqD41.2yiQUXIBLOJD0kqIPOQ1eOTpkd6aHP5ri3i-wA","MTAwMjI5NDc2MzI0MTg4NTg0Nw.GpX-Q5.oQB61lRTTlYcjPikv-zbEkBYUwJaMgQC2-OsfU"]
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
	run(tokens[0])


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