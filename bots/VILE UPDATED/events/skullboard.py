import discord, typing, time, arrow, psutil, copy, aiohttp, random
from datetime import datetime
from typing import Optional, Union
from utilities import utils
from utilities.baseclass import Vile
from discord.ext import commands


class SkullboardEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot
        self.sentmessages = dict()


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        if payload.emoji.name == '\N{SKULL}':
            if self.bot.cache.skullboard.get(payload.guild_id):
                channel = self.bot.cache.skullboard[payload.guild_id]

                if channel:

                    channel = self.bot.get_channel(channel)
                    message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

                    if message.author.bot:
                        return

                    reaction = [
                        reaction for reaction in message.reactions
                        if reaction.emoji == '💀'
                    ]

                    if not reaction:
                        return
                        
                    reaction = reaction[0]

                    embed = discord.Embed(color=self.bot.color, timestamp=datetime.now())

                    view = discord.ui.View().add_item(
                        discord.ui.Button(
                            style=discord.ButtonStyle.link,
                            label='message',
                            url=message.jump_url,
                        )
                    )

                    if self.sentmessages.get(channel.id) is None:
                        self.sentmessages[channel.id] = {}

                    if self.sentmessages[channel.id].get(message.id) is not None:

                        bot_message = await channel.fetch_message(self.sentmessages[channel.id][message.id])

                        embed = bot_message.embeds[0]
                        embed.set_footer(text=f'{reaction.count} 💀 #{message.channel.name}')

                        return await bot_message.edit(embed=embed)

                    embed.set_author(
                        name=str(message.author),
                        icon_url=message.author.display_avatar,
                    )
                    embed.description = message.content

                    if message.attachments:

                        embed.set_image(url=message.attachments[0].proxy_url)

                    embed.set_footer(text=f"{reaction.count} 💀 #{message.channel.name}")

                    self.sentmessages[channel.id][message.id] = (await channel.send(embed=embed, view=view)).id


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):

        if payload.emoji.name == "\N{SKULL}":
            if self.bot.cache.skullboard.get(payload.guild_id):
                channel = self.bot.cache.skullboard[payload.guild_id]

                if channel:

                    channel = self.bot.get_channel(channel)
                    message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

                if message.author.bot:
                    return

                reaction = [
                    reaction for reaction in message.reactions
                    if reaction.emoji == '💀'
                ]

                if not reaction:
                    return
                    
                reaction = reaction[0]

                embed = discord.Embed(
                    color=self.bot.color, 
                    timestamp=datetime.now()
                )
                view = discord.ui.View().add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label='message',
                        url=message.jump_url,
                    )
                )

                if self.sentmessages.get(channel.id) is None:
                    self.sentmessages[channel.id] = {}

                if self.sentmessages[channel.id]:
                    if self.sentmessages[channel.id].get(message.id) is not None:

                        bot_message = await channel.fetch_message(self.sentmessages[channel.id][message.id])  

                        embed = bot_message.embeds[0]
                        embed.set_footer(
                            text=f"{reaction.count} 💀 #{message.channel.name}"
                        )

                        return await bot_message.edit(embed=embed)


async def setup(bot: Vile):
    await bot.add_cog(SkullboardEvents(bot))