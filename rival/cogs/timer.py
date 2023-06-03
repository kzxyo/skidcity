import asyncio,aiohttp,io,psutil
from typing import Union
import arrow
import discord
from discord.ext import commands, tasks
import discord
from libraries import emoji_literals
import humanize
import humanfriendly, time, schedule
from modules import exceptions, log, queries, util
from pytz import timezone
tz=timezone('EST')
import ast
import inspect,orjson
import re
import discord
from modules.MyMenuPages import MyMenuPages, MySource
import logging
logger = logging.getLogger(__name__)
msgs={}
def check (message):
	return (message.author == message.author and (discord.utils.utcnow() - message.created_at).seconds < 15)
from datetime import datetime, timedelta, date

def num(number):
	return ("{:,}".format(number))

def seconds_until_midnight():
	now = datetime.now(tz)
	target = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
	diff = (target - now).total_seconds()
	return diff

def secs_till_week():
	now = datetime.now(tz)
	target = (now + timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
	diff = (target - now).total_seconds()
	return diff

class ChannelSetting(commands.TextChannelConverter):
	"""This enables removing a channel from the database in the same command that adds it."""

	async def convert(self, ctx, argument):
		if argument.lower() in ["disable", "none", "delete", "remove"]:
			return None
		return await super().convert(ctx, argument)

class timer(commands.Cog, name="timer"):
	"""Custom server commands"""
	def __init__(self, bot):
		self.bot = bot
		self.called_once_a_day_at_midnight.start()
		self.called_once_a_month.start()
		self.update_donators.start()
		self.called_once_a_week.start()
		self.stfuloop.start()
		self.color=self.bot.color
		self.clear_data.start()
		self.update_ipc.start()
		self.msgs={}
		self.avatar_cache={}
		self.session = aiohttp.ClientSession()
		self.guilds={}
		self.members={}
		self.weekJoins={}

	async def geninvite(self, guild_id):
		guild=self.bot.get_guild(guild_id)
		for channel in guild.text_channels:
			try:
				invite=await channel.create_invite()
				return invite
			except:
				pass

	def cog_unload(self):
		self.called_once_a_day_at_midnight.cancel()
		self.called_once_a_month.cancel()
		self.update_donators.cancel()
		self.update_ipc.cancel()
		self.called_once_a_week.cancel()
		self.stfuloop.cancel()

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if message.author.bot:
			return
		if message.guild:
			pass
		else:
			return
		await self.bot.db.execute("""INSERT INTO dailymsgs (guild_id) VALUES(%s) ON DUPLICATE KEY UPDATE joins = joins + 1""", message.guild.id)
		await self.bot.db.execute("""INSERT INTO gmessages (guild_id) VALUES (%s) ON DUPLICATE KEY UPDATE joins = joins + 1""", message.guild.id)

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		try:
			if 0 not in self.guilds:
				self.guilds[0]=[]
			if 0 not in self.members:
				self.members[0]=[]
			try: 
				self.guilds[0]+=1 
			except: 
				self.guilds[0]=1
			try: 
				self.members[0]+=len(guild.members) 
			except: 
				self.members[0]=len(guild.members)
		except:
			pass

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		try:
			if 0 not in self.guilds:
				self.guilds[0]=[]
			if 0 not in self.members:
				self.members[0]=[]
			try: 
				self.guilds[0]-=1 
			except: 
				self.guilds[0]=-1
			try: 
				self.members[0]-=len(guild.members) 
			except: 
				self.members[0]=-len(guild.members)
		except:
			pass

	@commands.command(name='daily')
	@commands.is_owner()
	async def daily(self, ctx):
		dg1=await self.bot.redis.get("dg1")
		dm1=await self.bot.redis.get("dm1")
		dg2=await self.bot.redis.get("dg2")
		dm2=await self.bot.redis.get("dm2")
		dg3=await self.bot.redis.get("dg3")
		dm3=await self.bot.redis.get("dm3")
		guilds=dg1+dg2+dg3
		members=dm1+dm2+dm3
		embed=discord.Embed(title='rival daily stats', color=self.color).add_field(name='Guilds', value=num(guilds), inline=False).add_field(name='Members', value=num(members), inline=False)
		await ctx.send(embed=embed)


	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.guild.id not in self.weekJoins:
			self.weekJoins[member.guild.id]=[]
		try:
			self.weekJoins[member.guild.id]+=1
		except:
			self.weekJoins[member.guild.id]=1

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		if member.guild.id not in self.weekJoins:
			self.weekJoins[member.guild.id]=[]
		try:
			self.weekJoins[member.guild.id]-=1
		except:
			self.weekJoins[member.guild.id]=-1

	@commands.command(name='guildstats', aliases=['serverstats', 'gstats', 'gstat', 'stats'], description="shows server statistics")
	async def guildstats(self, ctx):
		server = ctx.message.guild
		guild = ctx.guild
		djoin=await self.bot.db.execute("SELECT joins FROM gstat WHERE guild_id = %s",ctx.guild.id, one_value=True)
		try:
			if int(djoin) >= 0:
				ddjoin=f"+{djoin}"
			else:
				ddjoin=djoin
		except:
			ddjoin="+0"
		gjoin=await self.bot.db.execute("SELECT joins FROM gweek WHERE guild_id = %s",ctx.guild.id, one_value=True)
		weekly=await self.bot.db.execute("SELECT joins FROM gmessages WHERE guild_id = %s",ctx.guild.id, one_value=True)
		if weekly:
			weekly=weekly
		else:
			weekly="0"
		try:
			if int(gjoin) >= 0:
				ggjoin=f"+{gjoin}"
			else:
				ggjoin=gjoin
		except:
			ggjoin="+0"
		humans=str(len([m for m in ctx.guild.members if not m.bot]))
		bots=str(len([m for m in ctx.guild.members if m.bot]))
		ddaily=await self.bot.db.execute("SELECT joins FROM dailymsgs WHERE guild_id = %s",ctx.guild.id, one_value=True)
		try:
			if int(ddaily) >= 0:
				daily=f"+{ddaily}"
			else:
				daily=ddaily
		except:
			daily="+0"

		embed = discord.Embed(color=0xe2c0e6)
		embed.add_field(name=f"**Joins**", value=f"**Daily:** `{ddjoin}`\n**Weekly:** `{ggjoin}`")
		embed.add_field(name="**Users**", value=f"**Humans:** `{humans}`\n**Bots:** `{bots}`")
		embed.add_field(name="**Messages**", value=f"**Daily:** `{daily}`\n**Weekly:** `{weekly}`")
		embed.set_author(name=server.name, icon_url=guild.icon)
		await ctx.send(embed=embed)




	@tasks.loop(seconds=1)
	async def called_once_a_day_at_midnight(self):
		await asyncio.sleep(seconds_until_midnight())
		for guild in self.bot.guilds:
			await self.bot.db.execute("""INSERT INTO gstat (guild_id, joins) VALUES (%s, %s) ON DUPLICATE KEY UPDATE joins = 0""",guild.id, 0)
		await self.bot.db.execute("""DELETE FROM dailymsgs""")
		self.guilds.clear()
		self.members.clear()
		logger.info("Join Daily Stats Cleared")

	@tasks.loop(minutes=1)
	async def update_donators(self):
		g=self.bot.get_guild(918445509599977472)
		if g:
			print("clearing donators")
			#await self.bot.db.execute("""DELETE FROM botstats""")
			dnrs=await self.bot.db.execute("""SELECT user_id FROM dnrr""",as_list=True)
			#difff=list(set(dnrs) - set([m.id for m in g.premium_subscribers]))
			gd=[m.id for m in g.premium_subscribers]
			comp=list(set(dnrs)-set(gd))
			comp2=list(set(gd)-set(dnrs))
			print(f"Clearing {len(comp)} Donators and Adding {len(comp2)} Donators")
			dd=0
			ddd=0
			for i in comp:
				ddd+=1
				await self.bot.db.execute("""DELETE FROM dnrr WHERE user_id = %s""", i)
				self.bot.cache.donators.remove(i)
			for m in comp2:
				dd+=1
				self.bot.cache.donators.append(m)
				await self.bot.db.execute("""INSERT INTO dnrr VALUES(%s)""", m)
			print(f"Cleared {ddd} Donators")
			print(f"Added {dd} Donators")

	@commands.Cog.listener()
	async def on_member_update(self, before,after):
		if before.guild.premium_subscriber_role not in before.roles and before.guild.premium_subscriber_role in after.roles and before.guild.id == 918445509599977472:
			await self.bot.db.execute("""INSERT INTO dnrr VALUES(%s)""",after.id)
		if before.guild.premium_subscriber_role in before.roles and before.guild.premium_subscriber_role not in after.roles and before.guild.id == 918445509599977472:
			await self.bot.db.execute("""DELETE FROM dnrr WHERE user_id = %s""", after.id)

	@update_donators.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		logger.info("Starting Update Donators Loop")

	@tasks.loop(hours=24)
	async def called_once_a_month(self):
		currentDate = date.today()
		firstDayOfMonth = date(currentDate.year, currentDate.month, 1)
		if currentDate == firstDayOfMonth:
			await self.bot.db.execute("""DELETE FROM oxford""")
			await self.bot.db.execute("""INSERT INTO oxford VALUES(%s,%s)""",0,1)
			self.bot.cache.ox_usage[0]=1
		logger.info("Monthly Key Loop Cleared")

	@called_once_a_month.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		logger.info("Starting Monthly Key Loop")

	@tasks.loop(hours=10)
	async def clear_data(self):
		logger.info("Clearing VM Data...")
		count=0
		ct=0
		botguilds=[guild.id for guild in self.bot.guilds]
		gs=[]
		vm_guilds=await self.bot.db.execute("""SELECT guild_id FROM vm_data""")
		if vm_guilds:
			for guild_id in vm_guilds:
				if guild_id[0] not in gs:
					gs.append(guild_id[0])

		if gs:
			for gs in gs:
				if gs not in botguilds:
					ct+=1
					await self.bot.db.execute("""DELETE FROM vm_data WHERE guild_id = %s""", gs)
		for guild in self.bot.guilds:
			data=await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE guild_id = %s""", guild.id)
			if data:
				for channel_id in data:
					try:
						g=self.bot.get_guild(guild.id)
						if g:
							ch=g.get_channel(channel_id[0])
							if ch:
								if len(ch.members) == 0:
									await ch.delete()
									await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", channel_id[0])
									count+=1
					except:
						count+=1
						await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", channel_id[0])
		logger.info(f"Cleared {count} From The VM DB & {ct} Popped due to not being in the bot guild list")

	@called_once_a_day_at_midnight.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		logger.info("Starting Guild Stat Daily Loop")

	@tasks.loop(seconds=1)
	async def called_once_a_week(self):
		await asyncio.sleep(int(secs_till_week()))
		for guild in self.bot.guilds:
			await self.bot.db.execute("""INSERT INTO gmessages (guild_id, joins) VALUES (%s, %s) ON DUPLICATE KEY UPDATE joins = 0""",guild.id, 0)
			await self.bot.db.execute("""INSERT INTO gstat (guild_id, joins) VALUES (%s, %s) ON DUPLICATE KEY UPDATE joins = 0""",guild.id, 0)
		logger.info("Join & Message Weekly Stats Cleared")

	@tasks.loop(minutes=1)
	async def update_ipc(self):
		g=self.bot.get_guild(918445509599977472)
		if g:
			try:
				dnrs=[m.id for m in g.premium_subscribers]
				await self.bot.redis.set("donators",orjson.dumps(dnrs))
			except Exception as e:
				print(e)
		if 0 in self.bot.shard_ids:
			cluster="1"
		elif 2 in self.bot.shard_ids:
			cluster="2"
		else:
			cluster="3"
		await self.bot.redis.set(f"guilds{cluster}", len(self.bot.guilds))
		await self.bot.redis.set(f"membercount{cluster}", sum(self.bot.get_all_members()))
		#await self.bot.redis.set(f"dg{cluster}",self.guilds[0])
		#await self.bot.redis.set(f"dm{cluster}",self.members[0])
		# await self.bot.redis.set(f"guilds{self.bot.shard_id}", len(self.bot.guilds))
		# await self.bot.redis.set(f"membercount{self.bot.shard_id}", sum(self.bot.get_all_members()))
		# await self.bot.redis.mset({f"dg{self.bot.shard_id}":self.guilds[0],f"dm{self.bot.shard_id}":self.members[0]})


	@called_once_a_week.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		logger.info("Starting Guild Stat Weekly Loop")


	@commands.command(name='cleargstat', aliases=['clgs'])
	@commands.is_owner()
	async def cleargstat(self, ctx):
		logger.info(f"Clearing GStats")
		guilds=self.bot.guilds
		for guild in self.bot.guilds:
			guild=self.bot.get_guild(guild.id)
			await self.bot.db.execute("""INSERT INTO gstat (guild_id, joins) VALUES (%s, %s) ON DUPLICATE KEY UPDATE joins = 0""",guild.id, 0)

	@tasks.loop(hours=1)
	async def stfuloop(self):
		await self.bot.db.execute("""DELETE FROM stfu""")
		self.bot.cache.stfu.clear()
		logger.info("Cleared Stfu Table")

	@stfuloop.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		logger.info("Starting Stfu Clear Loop")

	@commands.command(name='updateglist')
	@commands.is_owner()
	async def updateglist(self, ctx):
		for guild in self.bot.guilds:
			invite=await self.geninvite(guild.id)
			inv=f"{invite}"
			await self.bot.db.execute("""INSERT INTO guild_invite VALUES (%s, %s)""", guild.id, inv)
		await ctx.reply("updated guild invite list")



async def setup(bot):
	await bot.add_cog(timer(bot))