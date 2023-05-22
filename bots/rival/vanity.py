import discord_ios
import os,typing,sys,json,discord,ast,inspect,traceback,re, asyncio
from time import time

from discord.ext import commands
from dotenv import load_dotenv

from modules import cache, log, maria, util
from modules.util import getheaders, proxy_scrape
from modules.help import EmbedHelpCommand
import sqlite3

load_dotenv(verbose=True)
logger = log.get_logger(__name__)
TOKEN = os.environ["TOKEN"]
prefix = "?"
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


class enemy(commands.AutoShardedBot):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.default_prefix = False
		self.logger = logger
		self.start_time = time()
		self.global_cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.member)
		self.db = maria.MariaDB(self)
		self.cache = cache.Cache(self)
		self.version = "1.0"
		self.token=os.environ["TOKEN"]
		self.extensions_loaded = False
		self.bdb = sqlite3.connect("main.db")
		self.dbcursor = self.bdb.cursor()

	async def close(self):
		await self.db.cleanup()
		await super().close()

	async def on_message(self, message):
		if not bot.is_ready():
			return

		await super().on_message(message)

	async def setup_hook(self):
		bot.loop.create_task(self.db.initialize_pool())
		bot.loop.create_task(self.cache.initialize_settings_cache())

bot = enemy(
	owner_ids=[714703136270581841, 330445977183977483, 956618986110476318],
	#help_command=EmbedHelpCommand(),
	help_command=None,
	#command_prefix=util.determine_prefix,
	command_prefix=util.vanity_prefix,
	case_insensitive=True,
	strip_after_prefix=True,
	allowed_mentions=discord.AllowedMentions(users=True, roles=False, replied_user=True, everyone=False),
	max_messages=20000,
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
		presences=True,  # requires verification
		messages=True,
		reactions=True,
		typing=True,
		message_content=True,
	).all())

extensions = [
	"errorhandler",
	"events",
#	"information",
#	"google",
#	"mod",
#	"owner",
#	"miscellaneous",
#	"lastfm",
#	"user",
#	"chat",
	"vanitycog",
#	"utility",
#	"webserver",
#	"crypto",
#	"stats",
#	"word",
#	"cmds",
#	"timer",
#	"embed",
	"emoji",
#	"docs",
#	"antievents",
#	"anticmds",
#	"namehistory"
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
	return await util.is_blacklisted(ctx)

@bot.check
async def cooldown_check(ctx):
	if str(ctx.invoked_with).lower() == "help":
		return True
	bucket = ctx.bot.global_cd.get_bucket(ctx.message)
	retry_after = bucket.update_rate_limit()
	if retry_after:
		raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.member)
	return True

@bot.event
async def on_message_edit(before, after):
    await bot.process_commands(after)

@bot.event
async def on_ready():
	if not bot.extensions_loaded:
		await load_extensions()
	latencies = bot.latencies
	logger.info(f"Loading complete | running {len(latencies)} shards")
	await bot.change_presence(activity=discord.Activity(name="!!help", type=5))
	#await bot.tree.sync()
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

def run():
	bot.run(TOKEN)

if __name__ == "__main__":
	logger.info(f'Using default prefix "{prefix}"')
	with open(os.getenv("temp")+"\\proxies.txt", 'w'): pass
	proxy_scrape()
	bot.start_time = time()
	bot.token=os.environ["TOKEN"]
	run()
