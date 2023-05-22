import asyncio

import arrow
import discord
from discord.ext import commands
import discord
import io
from collections import Counter
from wordcloud import WordCloud
from libraries import emoji_literals
import humanize
#from TwitterAPI import TwitterAPI

#api = TwitterAPI("SR9nr1xr7o79QPXADusgXq7hI", "M922c3FddKMVEXJUg3tPS22dzSlN7TNzLJS13i7T51aMuCkTt7", "4259600601-UCiyHEXu69m48zmQDTl5sSU8umhub1fjpvDghQb", "hSkKM3VvW6f7ccic0XvJ4aplEAi9bvCUJwCNj7btlJT0n", auth_type='oAuth1')

from modules import exceptions, log, queries, util

import ast
import inspect
import re


# s: https://medium.com/@chipiga86/python-monkey-patching-like-a-boss-87d7ddb8098e
#def source(o):
#	s = inspect.getsource(o).split("\n")
#	indent = len(s[0]) - len(s[0].lstrip())
#	return "\n".join(i[indent:] for i in s)


#source_ = source(discord.gateway.DiscordWebSocket.identify)
#patched = re.sub(
#	r'([\'"]\$browser[\'"]:\s?[\'"]).+([\'"])',  # hh this regex
#	r"\1Discord Android\2",  # s: https://luna.gitlab.io/discord-unofficial-docs/mobile_indicator.html
#	source_
#)

#loc = {}
#exec(compile(ast.parse(patched), "<string>", "exec"), discord.gateway.__dict__, loc)

#discord.gateway.DiscordWebSocket.identify = loc["identify"]

class ChannelSetting(commands.TextChannelConverter):
	"""This enables removing a channel from the database in the same command that adds it."""

	async def convert(self, ctx, argument):
		if argument.lower() in ["disable", "none", "delete", "remove"]:
			return None
		return await super().convert(ctx, argument)

class word(commands.Cog, name="word"):
	"""Custom server commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "📌"
		self.color=0x303135
		self.LIMIT = 20000
		self.url=re.compile(r'[A-Za-z0-9]+://[A-Za-z0-9%-_]+(/[A-Za-z0-9%-_])*(#|\\?)[A-Za-z0-9%-_&=]*')
		self.emote_regex = re.compile(r"<(a)?:[a-zA-Z0-9\_]+:([0-9]+)>")
		self.mention_regex = re.compile(r"<@!?([0-9]+)>")
		

	def create_word_cloud(self, messages: list):
		# We join all strings together and then split them into a list of words.
		list_of_words = " ".join(messages).split(" ")

		c = Counter(list_of_words)

		# We convert tuples in format (word, frequency) to dictionary {word: frequency}
		frequencies = {t[0]: t[1] for t in c.most_common(500) if len(t[0]) > 4}

		wc = WordCloud(
			font_path="cogs/bebasneue-wordcloud.ttf",
			background_color="white",
			max_words=250,
			width=2000,
			height=1000,
			min_word_length=4,
			normalize_plurals=True,
		)
		wc.generate_from_frequencies(frequencies)

		image = wc.to_image()

		binary = io.BytesIO()

		image.save(binary, format="PNG")

		binary.seek(0)

		return discord.File(binary, filename="wordcloud.png")

	@commands.guild_only()
	@commands.group(name="wordcloud", aliases=["words", "cloud", "wc"], description="wordcloud command group")
	async def wordcloud_base(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@commands.guild_only()
	@commands.cooldown(rate=1, per=300, type=commands.BucketType.user)
	@wordcloud_base.command(name="guild", description="generate a wc for the whole guild")
	async def wordcloud_guild(self, ctx: commands.Context):

		await ctx.send(
			"This process will take some time. I will ping you when I'm done."
		)

		# Hard limit is 50000 messages, so break it between all channels
		limit = int(self.LIMIT / len(ctx.guild.text_channels))

		messages = []

		for channel in ctx.guild.text_channels:
			# We use .map() to retrieve only the message.content property so
			# we won't have to hold the whole message object in memory.
			# We also .lower() all message contents so "Hi", "hi" and "hI" will be counted together
			async for message in channel.history(limit=limit):
				message.content=discord.utils.escape_mentions(message.content)
				if "https://" in message.content:
					pass
				elif "http://" in message.content:
					pass
				elif "www." in message.content.lower():
					pass
				else:
					messages.append(message.content.lower())

		image = self.create_word_cloud(messages)

		await ctx.send(
			content="{}\nHere's a word cloud that you requested.".format(
				ctx.author.mention
			),
			file=image,
		)

	@commands.guild_only()
	@commands.cooldown(rate=1, per=300, type=commands.BucketType.user)
	@wordcloud_base.command(name="channel", description="generate a wordcloud for a channel", brief="channel")
	async def wordcloud_channel(
		self, ctx: commands.Context, text_channel: discord.TextChannel = None
	):

		if text_channel is None:
			text_channel = ctx.message.channel

		await ctx.send(
			"This process will take some time. I will ping you when I'm done."
		)
		async for message in text_channel.history(limit=self.LIMIT / 3):
			message.content=discord.utils.escape_mentions(message.content)
			if "https://" in message.content:
				pass
			elif "http://" in message.content:
				pass
			elif "www." in message.content.lower():
				pass
			else:
				messages.append(message.content.lower())

		image = self.create_word_cloud(messages)

		await ctx.send(
			content="{}\nHere's a word cloud of #{} that you requested.".format(
				ctx.author.mention, text_channel.name
			),
			file=image,
		)

	@commands.guild_only()
	@wordcloud_base.command(name="user", aliases=["member"], description="generate a wordcloud for a member or yourself", brief="member")
	async def wordcloud_user(
		self, ctx: commands.Context, member: discord.Member = None
	):

		if member is None:
			member = ctx.author

		await ctx.send(
			"This process will take some time. I will ping you when I'm done."
		)

		# Hard limit is 50000 messages, so break it between all channels
		limit = int(self.LIMIT / len(ctx.guild.text_channels))

		messages = []

		for tc in ctx.guild.text_channels:
			# We use .map() to retrieve only the message.content property so
			# we won't have to hold the whole message object in memory.
			# We also .lower() all message contents so "Hi", "hi" and "hI" will be counted together
			async for message in tc.history(limit=limit):
				message.content=discord.utils.escape_mentions(message.content)
				if "https://" in message.content:
					pass
				elif "http://" in message.content:
					pass
				elif "www." in message.content.lower():
					pass
				else:
					if message.author.id == member.id:
						messages.append(message.content.lower())
		image = self.create_word_cloud(messages)

		await ctx.send(
			content="{}\nHere's a word cloud of {}'s most used words.".format(
				ctx.author.mention, member
			),
			file=image,
		)



async def setup(bot):
	await bot.add_cog(word(bot))