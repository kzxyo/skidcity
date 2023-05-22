import discord, arrow, shutil, traceback, copy, pytz
from collections import deque
from utilities import utils
from utilities.baseclass import Vile
from datetime import datetime, timedelta
from discord.ext import commands


class AutoModEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot
        self.spam_cd = commands.CooldownMapping.from_cooldown(4, 6, commands.BucketType.member)

    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if message.guild is None or message.author.bot:
            return
        
        if self.bot.cache.automod.get(message.guild.id) is None:
            return
        
        whitelist = self.bot.cache.automod_whitelist.get(message.guild.id, set())
        if message.author.id in whitelist or any(map(lambda r: r.id in whitelist, message.author.roles)) or message.channel.id in whitelist:
            return

        if message.guild.me.guild_permissions.administrator is False:
            return

        if (message.author.guild_permissions.administrator is True) or (message.author.id == message.guild.owner_id):
            return

        if message.author.top_role.position > message.guild.me.top_role.position:
            return

        # automod massmention
        if len(message.mentions) > 5:
            if self.bot.cache.automod[message.guild.id]['massmention'] == True:
                await message.delete()
                await message.author.edit(
                    timed_out_until=datetime.now().astimezone() + timedelta(minutes=3)
                )
                await message.channel.send(embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.done} {self.bot.user.mention}**:** {message.author} (`{message.author.id}`) was **muted** for 3 minutes\n{self.bot.reply} muted by my **automod (mass mention)**'
                ))

        # automod invites
        if self.bot.cache.automod[message.guild.id]['invites'] == True:
            if await message.invites():
                await message.delete()
                await message.author.edit(
                    timed_out_until=datetime.now().astimezone() + timedelta(minutes=3)
                )
                await message.channel.send(embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.done} {self.bot.user.mention}**:** {message.author} (`{message.author.id}`) was **muted** for 3 minutes\n{self.bot.reply} muted by my **automod (invites)**'
                ))

        # automod spam
        if self.bot.cache.automod[message.guild.id]['spam'] == True:
            bucket = self.spam_cd.get_bucket(message)
            retry_after = bucket.update_rate_limit()

            if retry_after:
                await message.delete()
                await message.author.edit(
                    timed_out_until=datetime.now().astimezone() + timedelta(minutes=3)
                )
                await message.channel.send(embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.done} {self.bot.user.mention}**:** {message.author} (`{message.author.id}`) was **muted** for 3 minutes\n{self.bot.reply} muted by my **automod (spam)**'
                ))


async def setup(bot: Vile):
    await bot.add_cog(AutoModEvents(bot))
