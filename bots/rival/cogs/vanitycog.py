import asyncio

import arrow, os, aiohttp, requests, json, copy
import discord
from discord.ext import commands, tasks
import discord
from libraries import emoji_literals
from datetime import timedelta
from typing import Union
from datetime import datetime
import humanize
import datetime
import humanfriendly
#from datetime import datetime
from discord.ext.commands.cooldowns import BucketType, CooldownMapping
from modules import exceptions, log, queries, util
import logging
logger = logging.getLogger(__name__)
import ast
import inspect
import re

GH_TOKEN = os.environ.get("GH_TOKEN")
TOKEN = os.environ.get("TOKEN")

def check (message):
	return (message.author == message.author and (discord.utils.utcnow() - message.created_at).seconds < 15)

class ChannelSetting(commands.TextChannelConverter):
	"""This enables removing a channel from the database in the same command that adds it."""

	async def convert(self, ctx, argument):
		if argument.lower() in ["disable", "none", "delete", "remove"]:
			return None
		return await super().convert(ctx, argument)

class vanitycog(commands.Cog, name="vanitycog"):
	"""Custom server commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "📌"
		self.color=0x303135
		self.yes="<:yes:940723483204255794>"
		self.good=0x0xD6BCD0
		self.no="<:no:940723951947120650>"
		self.bad=0xff6465
		self.color=0x303135
		self.ch='<:yes:940723483204255794>'
		self.error=0xfaa61a
		self.warn='<:warn:940732267406454845>'
		self.bump_list = []
		self.cache_needs_refreshing = True

	@commands.command(name='test')
	async def test(self, ctx):
		view = discord.ui.View()
		#view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite rival', url=invlink2))
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.red, label=f'invite rival', url="https://nigger.com"))
		await ctx.send("hi", view=view)

	@commands.Cog.listener()
	async def on_presence_update(self, before, after):
		data=await self.bot.db.execute("SELECT vanity, role_id FROM vanity WHERE guild_id = %s", after.guild.id)
		if data:
			for vanity, role_id in data:
				try:
					#guild = await self.bot.fetch_guild(after.guild.id)
					role = after.guild.get_role(role_id)
					member=await after.guild.fetch_member(after.id)
					if vanity in str(after.activity) and not role in member.roles and not after.status == discord.Status.offline:
						await member.add_roles(role, reason="Rival Vanity Role")

					elif vanity not in str(after.activity) and role in member.roles and not after.status == discord.Status.offline:
						await member.remove_roles(role, reason="Rival Vanity Role")
				except Exception as e:
					print(e)
					pass

	@commands.group(name='vanityrole', description="vanityrole command group")
	@commands.has_permissions(administrator=True)
	async def vanityrole(self, ctx):
		if ctx.invoked_subcommand is None:
			await util.command_group_help(ctx)

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		if guild.premium_tier == 3:
			pass
		else:
			await guild.leave()

	# @commands.command(name='help')
	# async def help(self, ctx):
	# 	await ctx.send(embed=discord.Embed(title="Vanity Commands", description=f"!!vanityrole set <vanity> <role>\n!!vanityrole unset\n"))
		
	@commands.Cog.listener(name='invite', aliases=['inv'])
	async def invite(self, ctx):
		embed = discord.Embed(description=f"**rival's** *bot invite generated below*", color=self.color)
		embed.set_footer(text=f"requested by {ctx.author}")
		view = discord.ui.View()
		#view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite rival', url=invlink2))
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite rival', url=invlink))
		await ctx.send(embed=embed, view=view)

	@vanityrole.command(name='set', description="set a reward role for vanity in status", brief='vanity, role', usage='administrator')
	async def set(self, ctx, vanity: str, role: discord.Role):
		#await self.bot.db.execute("""INSERT INTO afks VALUES (%s, %s, %s)ON DUPLICATE KEY UPDATE reason = VALUES(reason)""",ctx.guild.id,vanity,role.id,)
		await self.bot.db.execute("INSERT INTO vanity VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE vanity = vanity, role_id = %s",ctx.guild.id, vanity, role.id, role.id)
		await util.send_success(ctx, f"{ctx.author.mention}: vanity is now **{vanity}** with the reward role {role.mention}")

	@vanityrole.command(name='unset',usage='administrator',description="clear vanity role settings")
	async def unset(self, ctx):
		data=await self.bot.db.execute("SELECT FROM vanity WHERE guild_id = %s", ctx.guild.id, one_value=True)
		if data:
			await self.bot.db.execute("DELETE FROM vanity WHERE guild_id = %s",ctx.guild.id)
			await util.send_success(ctx, f"{ctx.author.mention}: vanity reward **disabled**")
		else:
			await util.send_success(ctx, f"{ctx.author.mention}: vanity reward **disabled**")
			pass


async def setup(bot):
	await bot.add_cog(vanitycog(bot))