import discord, arrow, pytz, traceback
from typing import Union
from datetime import datetime
from collections import deque
from utilities import utils
from utilities.baseclass import Vile
from discord.ext import commands


class ReactionEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot

    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        if payload.guild_id is None or payload.member.bot:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = payload.member
        message = payload.message_id

        if self.bot.cache.reactionroles.get(guild.id) is not None:
            if self.bot.cache.reactionroles[guild.id].get(message) is not None:
                for role_id, emoji in list(map(lambda d: d.items(), self.bot.cache.reactionroles[guild.id][message])):
                    if guild.get_role(role_id[1]) is not None:
                        if emoji[1] == str(payload.emoji):
                            await member.add_roles(guild.get_role(role_id[1]), reason=f'reactionrole: reacted to {message}')


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        
        if payload.guild_id is None or self.bot.get_user(payload.user_id).bot:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        message = payload.message_id

        if self.bot.cache.reactionroles.get(guild.id) is not None:
            if self.bot.cache.reactionroles[guild.id].get(message) is not None:
                for role_id, emoji in list(map(lambda d: d.items(), self.bot.cache.reactionroles[guild.id][message])):
                    if guild.get_role(role_id[1]) is not None:
                        if emoji[1] == str(payload.emoji):
                            await member.remove_roles(guild.get_role(role_id[1]), reason=f'reactionrole: unreacted to {message}')

    
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):

        if isinstance(user, discord.User) or user.bot:
            return

        ch_id = reaction.message.channel.id

        if ch_id not in self.bot.reactionsnipes:
            self.bot.reactionsnipes[ch_id] = deque()

        self.bot.reactionsnipes[ch_id].appendleft((reaction, user, datetime.now(pytz.timezone('America/New_York'))))

        if len(self.bot.reactionsnipes[ch_id]) >= 1000:
             self.bot.reactionsnipes[ch_id].pop() 
        

async def setup(bot: Vile):
    await bot.add_cog(ReactionEvents(bot))