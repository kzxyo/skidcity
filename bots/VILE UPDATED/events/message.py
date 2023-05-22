import discord, unicodedata, arrow, uwupy, shutil, traceback, copy, pytz, asyncio
from collections import deque
from utilities import utils
from utilities.baseclass import Vile
from datetime import datetime, timedelta
from discord.ext import commands
from utilities.chatbot import Chatbot


class MessageEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot
        self.cached_webhooks = dict()
        self.chatbot = Chatbot(api_key=self.bot.chatgpt_api)

    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if message.guild is None or message.author.bot:
            return

        if self.bot.user.mention == message.content:
            customprefix = self.bot.cache.customprefixes.get(message.author.id)
            guildprefix = self.bot.cache.guildprefixes.get(message.guild.id)
            prefixes = [f'global prefix: `{self.bot.prefix}`']
            if customprefix is not None:
                prefixes.append(f'your prefix: `{customprefix}`')
            if guildprefix is not None:
                prefixes.append(f'guild prefix: `{guildprefix}`')

            return await message.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.done} {message.author.mention}**:** {', '.join(prefixes)}"
                ),
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label=f'Invite {self.bot.user.name.title()}',
                        url=self.bot.invite
                    )
                )
            )

        for member in message.mentions:
            if self.bot.cache.afk.get(member.id):
                entry = utils.find(self.bot.cache.afk[member.id], key=lambda e: e['guild_id'] == message.guild.id)
                if entry:
                    status= entry['status']
                    lastseen = arrow.get(entry['lastseen']).humanize()

                    embed = discord.Embed(
                        color=0x2f3136, 
                        description=f'> **Reason:** {status}'
                    )
                    embed.set_author(
                        name=f'{member.name} is currently afk',
                        icon_url=member.display_avatar,
                    )
                    embed.set_footer(text=f'last seen {lastseen}')

                    await message.reply(embed=embed)

        if message.author.id in self.bot.cache.semimute.get(message.guild.id, set()):
            if message.guild.me.guild_permissions.manage_messages is True:
                await message.delete()

        if self.bot.cache.tiktok_reposting.get(message.guild.id, 1) == True:
            if message.content.startswith('vile ') and 'tiktok.com/' in message.content:
                link = utils.find(message.content.split(), key=lambda w: 'tiktok.com/' in w)
                async with (await self.bot.get_context(message)).handle_response():
                    await utils.get_tiktok(message, self.bot, link)

        if self.bot.cache.youtube_reposting.get(message.guild.id, 1) == True:
            if message.content.startswith('vile ') and ('/youtu' in message.content or '/www.youtu' in message.content):
                link = utils.find(message.content.split(), key=lambda w: '/youtu' in w or '/www.youtu' in w)
                async with (await self.bot.get_context(message)).handle_response():
                    await utils.get_youtube(message, self.bot, link)

        if message.content.startswith('vile ') and ('/twitter' in message.content or 't.co' in message.content):
            link = utils.find(message.content.split(), key=lambda w: '/twitter' in w or 't.co' in w)
            async with (await self.bot.get_context(message)).handle_response():
                await utils.get_twitter(message, self.bot, link)

        if message.content.startswith('vile ') and 'soundcloud' in message.content:
            link = utils.find(message.content.split(), key=lambda w: 'soundcloud' in w)
            async with (await self.bot.get_context(message)).handle_response():
                await utils.get_soundcloud(message, self.bot, link)

        if message.content.startswith('vile ') and 'medal.tv/' in message.content:
            link = utils.find(message.content.split(), key=lambda w: 'medal.tv/' in w)
            async with (await self.bot.get_context(message)).handle_response():
                await utils.get_medal(message, self.bot, link)

        if message.channel.id in self.bot.cache.image_only.get(message.guild.id, []):
            if message.content is not None and not message.attachments:
                await message.delete()
                if self.bot.cache.limits['dms'].get(message.guild.id, 0) < 15:
                    await message.author.send(
                        embed=discord.Embed(
                            color=self.bot.color,
                            description=f'{self.bot.fail} {message.author.mention}**:** cannot send messages in an image-only channel'
                        )
                    )

                    if message.guild.id not in self.bot.cache.limits['dms']:
                        self.bot.cache.limits['dms'][message.guild.id] = 0
                    
                    self.bot.cache.limits['dms'][message.guild.id] += 1

        if self.bot.cache.autoreact.get(message.guild.id) is not None:
            for w, r in self.bot.cache.autoreact[message.guild.id]:
                if w in message.content.lower().replace('\n', ' '):
                    await message.add_reaction(r)

        if self.bot.cache.autoresponder.get(message.guild.id) is not None:
            for w, r in self.bot.cache.autoresponder[message.guild.id]:
                if w in message.content.lower().replace('\n', ''):
                    await message.reply(
                        **await utils.to_object(await utils.embed_replacement(message.author, r))
                    )

        if self.bot.cache.verification.get(message.guild.id) is not None:
            if self.bot.cache.verification[message.guild.id].get(message.channel.id) is not None:
                if message.channel.permissions_for(message.guild.me).manage_messages is True:
                    await message.delete()
                    
                if message.content.lower() == self.bot.cache.verification[message.guild.id][message.channel.id]['text'].lower():
                    role = message.guild.get_role(self.bot.cache.verification[message.guild.id][message.channel.id]['role_id'])
                        
                    if message.channel.permissions_for(message.guild.me).manage_channels is True:
                        await message.channel.set_permissions(message.author, overwrite=discord.PermissionOverwrite(view_channel=False))
                    
                    if (message.channel.permissions_for(message.guild.me).manage_roles is True) and (role is not None):
                        await message.author.add_roles(role, reason='vile verification: message content matches verification string')

        if self.bot.cache.highlights.get(message.guild.id) is not None:
            for word in message.content.split():
                if self.bot.cache.highlights[message.guild.id].get(word) is not None:
                    to_dm = message.guild.get_member(self.bot.cache.highlights[message.guild.id][word])
                    if to_dm is not None:
                        if 15 > self.bot.cache.limits['dms'].get(message.guild.id, 0):
                            await to_dm.send(f"the highlight **{word}** was mentioned in **{message.guild.name}**\n{message.jump_url}")
                            if message.guild.id not in self.bot.cache.limits['dms']:
                                self.bot.cache.limits['dms'][message.guild.id] = 0
                            self.bot.cache.limits['dms'][message.guild.id] += 1

        if message.content.lower().startswith(('hey vile ', 'hello vile ')):
            if message.author.id not in self.bot.cache.global_bl['users'] and message.guild.id not in self.bot.cache.global_bl['guilds']:
                question = ' '.join(message.content.split()[2:])
                if len(question) < 400:
                    async with (await self.bot.get_context(message)).handle_response():
                        self.chatbot.load_conversation(message.author.id)
                        await message.reply(await self.chatbot.ask(question))
                        self.chatbot.save_conversation(message.author.id)

        if message.guild.id in self.bot.cache.uwulock:
            if message.author.id in self.bot.cache.uwulock[message.guild.id]:
                if message.guild.me.guild_permissions.manage_messages and message.guild.me.guild_permissions.manage_webhooks:
                    webhooks = self.cached_webhooks.setdefault(message.channel.id, await message.channel.webhooks())
                    if webhooks:
                        webhook = webhooks[0]
                    else:
                        webhook = await message.channel.create_webhook(name='Vile Uwulock', reason='vile uwulock: failed to find any existing webhooks')
                        
                    await message.delete()
                    await webhook.send(uwupy.uwuify_str(message.content), username=message.author.name, avatar_url=message.author.display_avatar.url)


    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):

        if message.guild is None or message.author.bot:
            return

        ch_id = message.channel.id

        if ch_id not in self.bot.snipes:
            self.bot.snipes[ch_id] = deque()

        alt_message = copy.copy(message)
        if utils.determine_filter(self.bot, message):
            alt_message.content = 'filtered message'
            self.bot.snipes[ch_id].appendleft((alt_message, datetime.now(pytz.timezone('America/New_York'))))
        else:
            self.bot.snipes[ch_id].appendleft((message, datetime.now(pytz.timezone('America/New_York'))))

        if len(self.bot.snipes[ch_id]) >= 1000:
             self.bot.snipes[ch_id].pop() 


    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        if before.guild is None or before.author.bot:
            return

        ch_id = before.channel.id

        if ch_id not in self.bot.editsnipes:
            self.bot.editsnipes[ch_id] = deque()

        self.bot.editsnipes[ch_id].appendleft((before, after))

        if len(self.bot.editsnipes[ch_id]) >= 1000:
             self.bot.editsnipes[ch_id].pop() 
                            

async def setup(bot: Vile):
    await bot.add_cog(MessageEvents(bot))
