import discord
from discord.ext import commands
import humanize
import difflib
import datetime
import aiohttp
import requests
import io
from utils.embed import to_object, embed_replacement
import re
import asyncio

color = 0x2b2d31
class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.available_tags = []
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        data = await self.bot.db.fetchval('SELECT prefix FROM prefix WHERE guild_id = $1', guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO prefix(guild_id, prefix) VALUES ($1, $2)', guild.id, ',')
        if data:
            pass
        # authorized = await self.bot.db.fetchval('SELECT guild_id FROM whitelist WHERE guild_id = $1', str(guild.id))
        # if authorized:
        #     owner = '<@323118319144271872>'
        #     e = discord.Embed(
        #         color=color,
        #         title=f'Thank you for inviting {self.bot.user.name}!',
        #         description=f'**{self.bot.user.name}** needs the **administrator** permission or commands might not work properly',
        #         url='https://discord.gg/voidbot'
        #     )
        #     e.add_field(name='Prefix',
        #                 value='> The default prefix is `,` You can change this using `,prefix set (new prefix)`',
        #                 inline=False)
        #     e.add_field(name='Setup', value='> Use the `,setup` command in order to setup the **moderation system**',
        #                 inline=False)
        #     e.add_field(name='Support',
        #                 value=f'> For support join the **[support server](https://discord.gg/voidbot)** or contact **{owner}** if it\'s urgent',
        #                 inline=False)
        #     await guild.owner.send(embed=e)
        # else:
        #     await self.bot.get_guild(int(guild.id)).leave()
        #     print(f'Left {guild.name} ({guild.id}), guild is not authorized')
        channel_count = len(guild.text_channels) + len(guild.voice_channels)
        invite = 'N/A'
        if guild.vanity_url is not None:
            invite = f'[{guild.vanity_url_code}]({guild.vanity_url})'
        e = discord.Embed(
            color=color,
            title=f'{guild.name} ({guild.id})',
            description=
            f'Created {discord.utils.format_dt(guild.created_at, style="F")}'
        )
        e.add_field(name='Members', value=f'**Total:** {guild.member_count}\n'
                                          f'**Humans:** {len(list(filter(lambda m: not m.bot, guild.members)))}\n'
                                          f'**Bots:** {len(list(filter(lambda m: m.bot, guild.members)))}')
        e.add_field(name='Channels', value=f'**Total:** {channel_count}\n'
                                            f'**Text:** {len(guild.text_channels)}\n'
                                            f'**Voice:** {len(guild.voice_channels)}')
        e.add_field(name='Other', value=f'**Categories:** {len(guild.categories)}\n'
                                        f'**Roles:** {len(guild.roles)}\n'
                                        f'**Emotes:** {len(guild.emojis)}')
        e.add_field(name='Boost', value=f'**Level:** {guild.premium_tier}/3\n'
                                        f'**Boosts:** {guild.premium_subscription_count}')
        e.add_field(name='Information', value=f'**Verification:** {guild.verification_level}\n'
                                              f'**Vanity:** {invite}')
        e.set_footer(text=f'{guild.owner} ({guild.owner_id})')
        e.set_author(name=f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar)
        channel = self.bot.get_channel(1094398448020758578)
        await channel.send('**Joined:**')
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        channel_count = len(guild.text_channels) + len(guild.voice_channels)
        invite = 'N/A'
        if guild.vanity_url is not None:
            invite = f'[{guild.vanity_url_code}]({guild.vanity_url})'
        e = discord.Embed(
            color=color,
            title=f'{guild.name} ({guild.id})',
            description=
            f'Created {discord.utils.format_dt(guild.created_at, style="F")}'
        )
        e.add_field(name='Members', value=f'**Total:** {guild.member_count}\n'
                                          f'**Humans:** {len(list(filter(lambda m: not m.bot, guild.members)))}\n'
                                          f'**Bots:** {len(list(filter(lambda m: m.bot, guild.members)))}')
        e.add_field(name='Channels', value=f'**Total:** {channel_count}\n'
                                            f'**Text:** {len(guild.text_channels)}\n'
                                            f'**Voice:** {len(guild.voice_channels)}')
        e.add_field(name='Other', value=f'**Categories:** {len(guild.categories)}\n'
                                        f'**Roles:** {len(guild.roles)}\n'
                                        f'**Emotes:** {len(guild.emojis)}')
        e.add_field(name='Boost', value=f'**Level:** {guild.premium_tier}/3\n'
                                        f'**Boosts:** {guild.premium_subscription_count}')
        e.add_field(name='Information', value=f'**Verification:** {guild.verification_level}\n'
                                              f'**Vanity:** {invite}')
        e.set_footer(text=f'{guild.owner} ({guild.owner_id})')
        e.set_author(name=f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar)
        channel = self.bot.get_channel(1094398448020758578)
        await channel.send('**Left:**')
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_available_tag(self, user: discord.User):
        self.available_tags.insert(0,
            {
                "user": user,
                "time": datetime.datetime.utcnow()
            }
        )
        
    @commands.Cog.listener()
    async def on_user_update(self, before:discord.Member, after:discord.Member):
        if before.avatar == after.avatar:
            if before.discriminator == '0001':
                self.bot.dispatch('available_tag', before)
                for guild in self.bot.guilds:
                        data = await self.bot.db.fetchval(f"SELECT channel FROM tracker WHERE guild_id = $1", guild.id)
                        if data:
                            text = self.bot.get_channel(data)
                            await text.send(f"**New username available**: {before}")

        if before.name != after.name or before.discriminator != after.discriminator:
            timestamp = datetime.datetime.utcnow()
            await self.bot.db.execute('INSERT INTO names (user_id, username, discriminator, timestamp) VALUES ($1, $2, $3, $4)', after.id, before.name, before.discriminator, timestamp)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if after.bot:
            return
        if not after.activity or before.activity == after.activity:
            if before.status != discord.Status.offline and (after.status == discord.Status.offline or not after.activity):
                role_rows = await self.bot.db.fetch('SELECT role FROM vanity WHERE guild = $1', after.guild.id)
                roles = [after.guild.get_role(row['role']) for row in role_rows]
                member = after.guild.get_member(after.id)
                if member:
                    for role in roles:
                        if role in member.roles:
                            await member.remove_roles(role)
            return
        rows = await self.bot.db.fetch('SELECT channel, role, message FROM vanity WHERE guild = $1 AND substring = $2', after.guild.id, after.activity.name)
        if rows:
            channel = self.bot.get_channel(rows[0]['channel'])
            role = after.guild.get_role(rows[0]['role'])
            message = rows[0]['message']
            if channel and role:
                member = after.guild.get_member(after.id)
                if member:
                    if role not in member.roles:
                        await member.add_roles(role)
                        if message:
                            result = await to_object(message)
                            embed = result['embed']
                            if embed:
                                if embed.title:
                                    embed.title = await embed_replacement(member, embed.title)
                                if embed.description:
                                    embed.description = await embed_replacement(member, embed.description)
                                if embed.footer:
                                    if embed.footer.text and embed.footer.icon_url:
                                        embed.set_footer(text=await embed_replacement(member, embed.footer.text), icon_url=await embed_replacement(member, embed.footer.icon_url))
                                    elif embed.footer.text:
                                        embed.set_footer(text=await embed_replacement(member, embed.footer.text))
                                    elif embed.footer.icon_url:
                                        embed.set_footer(icon_url=await embed_replacement(member, embed.footer.icon_url))
                                if embed.author:
                                    if embed.author.name and embed.author.icon_url:
                                        embed.set_author(name=await embed_replacement(member, embed.author.name), icon_url=await embed_replacement(member, embed.author.icon_url))
                                    elif embed.author.name:
                                        embed.set_author(name=await embed_replacement(member, embed.author.name))
                                    elif embed.author.icon_url:
                                        embed.set_author(icon_url=await embed_replacement(member, embed.author.icon_url))
                                if embed.fields:
                                    for field in embed.fields:
                                        if field.name:
                                            embed.set_field_at(index=embed.fields.index(field), name=await embed_replacement(member, field.name), value=await embed_replacement(member, field.value), inline=field.inline)
                                if embed.image:
                                    embed.set_image(url=await embed_replacement(member, embed.image.url))
                                if embed.thumbnail:
                                    embed.set_thumbnail(url=await embed_replacement(member, embed.thumbnail.url))
                            content = result['content']
                            if content:
                                content = await embed_replacement(member, content)
                            if not channel: return
                            await channel.send(content=content, embed=embed, view=result['view'], files=result['files'], delete_after=result['delete_after'], allowed_mentions=discord.AllowedMentions(users=True, everyone=False))
        else:
            role_rows = await self.bot.db.fetch('SELECT role FROM vanity WHERE guild = $1', after.guild.id)
            roles = [after.guild.get_role(row['role']) for row in role_rows]
            member = after.guild.get_member(after.id)
            if member:
                for role in roles:
                    if role in member.roles:
                        if before.activity:
                            await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        data = await self.bot.db.fetchval('SELECT voice FROM voicemaster WHERE guild_id = $1', member.guild.id)
        if data:
            if after.channel and after.channel.id == data:
                voice = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE owner = $1', member.id)
                if voice:
                    channel = member.guild.get_channel(voice)
                    await member.move_to(channel)
                else:
                    existing_channel = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE guild = $1 AND owner = $2', member.guild.id, member.id)
                    if existing_channel:
                        channel = member.guild.get_channel(existing_channel)
                        await member.move_to(channel)
                    else:
                        channel = await member.guild.create_voice_channel(
                            name=f"{member.name}'s channel",
                            user_limit=0,
                            category=after.channel.category)
                        await member.move_to(channel)
                        await self.bot.db.execute('INSERT INTO voicemaster_data (voice, guild, owner) VALUES ($1, $2, $3)', channel.id, channel.guild.id, member.id)
            elif before and before.channel:
                voice = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1', before.channel.id)
                if len(before.channel.members) == 0 and voice:
                    if before.channel.id == voice:
                        await self.bot.db.execute('DELETE FROM voicemaster_data WHERE voice = $1', before.channel.id)
                        await before.channel.delete()
                    elif before.channel.id == data:
                        await asyncio.sleep(5)
                        voice = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE owner = $1', member.id)
                        if before.channel.id == voice:
                            await self.bot.db.execute('DELETE FROM voicemaster_data WHERE owner = $1', member.id)
                            await before.channel.delete()
        else:
            if after.channel:
                await self.bot.db.execute('INSERT INTO voicemaster (guild_id, voice) VALUES ($1, $2)', member.guild.id, after.channel.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        member = message.author
        if member.bot: return
        data = await self.bot.db.fetch('SELECT * FROM afk WHERE author = $1', member.id)
        if data:
            timestamp = data[0][2]
            time = humanize.precisedelta(timestamp - discord.utils.utcnow().timestamp(), format='%0.f')
            await self.bot.db.execute('DELETE FROM afk WHERE author = $1', member.id)
            await ctx.success(f'Welcome back! You were away for **{time}**')
        if message.mentions:
            for mention in message.mentions:
                data = await self.bot.db.fetch('SELECT * FROM afk WHERE author = $1', mention.id)
                if data and mention.id != member.id:
                    timestamp = data[0][2]
                    time = humanize.precisedelta(timestamp - discord.utils.utcnow().timestamp(), format='%0.f')
                    await ctx.success(f'**{mention}** is currently AFK: **{data[0][1]}** - {time} ago')

        if "tiktok.com/" in message.content:
            if message.content.startswith("void "):
                await message.delete()
                link = [i for i in message.content.split() if 'tiktok.com/' in i][0]
                async with aiohttp.ClientSession() as data:
                    async with data.get(f"https://tikwm.com/api?url={link}") as response:
                        x = await response.json()
                        video = x['data']
                        play = video['play']

                        r = requests.get(play).content
                        file = discord.File(io.BytesIO(r), f"{self.bot.user.name}tok.mp4")

                        e = discord.Embed(
                            color=color,
                            description=f"[**TikTok**]({link}) requested by {member.mention}")
                        e.set_author(name=member, icon_url=member.display_avatar.url)
                        await message.channel.send(file=file, embed=e)
            else:
                pass

        if message.guild:
            rows = await self.bot.db.fetch("SELECT * FROM response WHERE guild_id = $1", message.guild.id)
            for row in rows:
                trigger = row[2]
                response = row[3]
                is_strict = "--strict" in response
                if is_strict:
                    response = response.replace("--strict", "").strip()
                    if message.content.strip() == trigger:
                        await message.channel.send(response)
                        return
                else:
                    if trigger.lower() in message.content.lower():
                        await message.channel.send(response)

        if message.guild:
            rows = await self.bot.db.fetch("SELECT * FROM reaction_trigger WHERE guild_id = $1", message.guild.id)
            if rows:
                for row in rows:
                    trigger = row[1]
                    emoji = row[2]
                    if trigger.lower() in message.content.lower() and not message.author.bot:
                        await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if not message.content and not message.attachments:
            return


        attachment_url = ""
        attachment_type = ""
        if message.attachments:
            attachment = message.attachments[0]
            attachment_url = attachment.url
            attachment_type = attachment.content_type.split('/')[0]
        await self.bot.db.execute("INSERT INTO snipe (guild_id, channel_id, author_id, content, attachment_url, attachment_type) VALUES ($1, $2, $3, $4, $5, $6)", message.guild.id, message.channel.id, message.author.id, message.content, attachment_url, attachment_type)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if not before.content and not before.attachments:
            return
        if before.content == after.content and before.attachments == after.attachments:
            return

        # Get the attachment, if there is one
        attachment_url = ""
        attachment_type = ""
        if after.attachments:
            attachment = after.attachments[0]
            attachment_url = attachment.url
            attachment_type = attachment.content_type.split('/')[0]

        await self.bot.db.execute("INSERT INTO editsnipe (guild_id, channel_id, author_id, content, attachment_url, attachment_type) VALUES ($1, $2, $3, $4, $5, $6)", before.guild.id, before.channel.id, before.author.id, before.content, attachment_url, attachment_type)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.bot.db.fetchval(f'SELECT channel_id FROM welcome WHERE guild_id = $1', member.guild.id)
        if data:
            message = await self.bot.db.fetchval(f'SELECT message FROM welcome WHERE guild_id = $1', member.guild.id)
            result = await to_object(message)
            embed = result['embed']
            if embed:
                if embed.title:
                    embed.title = await embed_replacement(member, embed.title)
                if embed.description:
                    embed.description = await embed_replacement(member, embed.description)
                if embed.footer:
                    if embed.footer.text and embed.footer.icon_url:
                        embed.set_footer(text=await embed_replacement(member, embed.footer.text), icon_url=await embed_replacement(member, embed.footer.icon_url))
                    elif embed.footer.text:
                        embed.set_footer(text=await embed_replacement(member, embed.footer.text))
                    elif embed.footer.icon_url:
                        embed.set_footer(icon_url=await embed_replacement(member, embed.footer.icon_url))
                if embed.author:
                    if embed.author.name and embed.author.icon_url:
                        embed.set_author(name=await embed_replacement(member, embed.author.name), icon_url=await embed_replacement(member, embed.author.icon_url))
                    elif embed.author.name:
                        embed.set_author(name=await embed_replacement(member, embed.author.name))
                    elif embed.author.icon_url:
                        embed.set_author(icon_url=await embed_replacement(member, embed.author.icon_url))
                if embed.fields:
                    for field in embed.fields:
                        if field.name:
                            embed.set_field_at(index=embed.fields.index(field), name=await embed_replacement(member, field.name), value=await embed_replacement(member, field.value), inline=field.inline)
                if embed.image:
                    embed.set_image(url=await embed_replacement(member, embed.image.url))
                if embed.thumbnail:
                    embed.set_thumbnail(url=await embed_replacement(member, embed.thumbnail.url))
            content = result['content']
            if content:
                content = await embed_replacement(member, content)
            channel = self.bot.get_channel(int(data))
            if not channel: return
            await channel.send(content=content, embed=embed, view=result['view'], files=result['files'], delete_after=result['delete_after'], allowed_mentions=discord.AllowedMentions(users=True, everyone=False))
        if not data:
            return
        
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        data = await self.bot.db.fetchval(f'SELECT channel_id FROM goodbye WHERE guild_id = $1', member.guild.id)
        if data:
            message = await self.bot.db.fetchval(f'SELECT message FROM goodbye WHERE guild_id = $1', member.guild.id)
            result = await to_object(message)
            embed = result['embed']
            if embed:
                if embed.title:
                    embed.title = await embed_replacement(member, embed.title)
                if embed.description:
                    embed.description = await embed_replacement(member, embed.description)
                if embed.footer:
                    if embed.footer.text and embed.footer.icon_url:
                        embed.set_footer(text=await embed_replacement(member, embed.footer.text), icon_url=await embed_replacement(member, embed.footer.icon_url))
                    elif embed.footer.text:
                        embed.set_footer(text=await embed_replacement(member, embed.footer.text))
                    elif embed.footer.icon_url:
                        embed.set_footer(icon_url=await embed_replacement(member, embed.footer.icon_url))
                if embed.author:
                    if embed.author.name and embed.author.icon_url:
                        embed.set_author(name=await embed_replacement(member, embed.author.name), icon_url=await embed_replacement(member, embed.author.icon_url))
                    elif embed.author.name:
                        embed.set_author(name=await embed_replacement(member, embed.author.name))
                    elif embed.author.icon_url:
                        embed.set_author(icon_url=await embed_replacement(member, embed.author.icon_url))
                if embed.fields:
                    for field in embed.fields:
                        if field.name:
                            embed.set_field_at(index=embed.fields.index(field), name=await embed_replacement(member, field.name), value=await embed_replacement(member, field.value), inline=field.inline)
                if embed.image:
                    embed.set_image(url=await embed_replacement(member, embed.image.url))
                if embed.thumbnail:
                    embed.set_thumbnail(url=await embed_replacement(member, embed.thumbnail.url))
            content = result['content']
            if content:
                content = await embed_replacement(member, content)
            channel = self.bot.get_channel(int(data))
            if not channel: return
            await channel.send(content=content, embed=embed, view=result['view'], files=result['files'], delete_after=result['delete_after'], allowed_mentions=discord.AllowedMentions.none())
        if not data:
            return
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)

        if isinstance(error, commands.CommandNotFound):
            x=[cmd.name.lower() for cmd in self.bot.commands]
            cmd=ctx.message.content.split()[0].strip('#')
            
            z=difflib.get_close_matches(cmd, x)
            if z:
                match=z[0]
                await ctx.success(f'Command `{ctx.invoked_with}` doesn\'t exist, do you mean `{match}`?')

        if isinstance(error, commands.MissingPermissions):
            missing_perms = [p.replace("_", " ") for p in error.missing_permissions]
            formatted_perms = [f"{p.lower().replace(' ', '_')}" for p in missing_perms]
            await ctx.success(f"You're **missing** the `{', '.join(formatted_perms)}` permission")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.id == self.bot.user.id:
            return
        data = await self.bot.db.fetchval('SELECT role FROM reactionroles WHERE message = $1 AND emote = $2', str(payload.message_id), str(payload.emoji))
        if data:
            role = payload.member.guild.get_role(int(data))
            await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        data = await self.bot.db.fetchval('SELECT role FROM reactionroles WHERE message = $1 AND emote = $2', str(payload.message_id), str(payload.emoji))
        if data:
            guild = await self.bot.fetch_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            role = member.guild.get_role(int(data))
            await member.remove_roles(role)

        message_id = payload.message_id
        channel_id = payload.channel_id
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(channel_id)
        user = guild.get_member(payload.user_id)
        emoji = payload.emoji
        message = await channel.fetch_message(message_id)
        await self.bot.db.execute("INSERT INTO reactionsnipe (guild_id, channel_id, message_id, user_id, emoji) VALUES ($1, $2, $3, $4, $5)", guild.id, channel.id, message.id, user.id, str(emoji))

async def setup(bot):
    await bot.add_cog(Events(bot))
