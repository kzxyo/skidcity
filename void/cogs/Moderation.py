import discord
from discord.ext import commands
import asyncio
from utils.paginator import Paginator
import typing
import humanfriendly
import datetime
from typing import Union, Optional
import re

color = 0x2b2d31

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    def convert(self, time):
        pos = ["s", "m", "h", "d"]

        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2

        return val * time_dict[unit]
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command(
        name='ban',
        description='Ban a user from the server',
        brief='user, reason',
        usage=
        'Syntax: (user) <reason>\n'
        'Example: @void#0480 ban evading',
        aliases=['deport', 'yeet'],
        extras={'perms': 'Ban Members'})
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Union[discord.Member, discord.User] = None, *, reason: str = 'No reason provided'):
        await ctx.typing()
    
        if not reason:
            reason=f'{ctx.author}: {reason}'
        if reason:
            reason=f'{ctx.author}: {reason}'
        if member is None:
            return await ctx.send_help(ctx.command)
        async for ban in ctx.guild.bans():
            if ban.user.id == member.id:
                return await ctx.success(f'{member.mention} is already **banned**')
        if isinstance(member, discord.User):
            await ctx.guild.ban(member, reason=reason)
            await ctx.reply('👍🏾', mention_author=False)
            return
        if ctx.author is ctx.guild.owner:
            pass
        if member is ctx.author:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** yourself')
        if member is ctx.guild.owner:
            return await ctx.success(f'You\'re unable to {ctx.invoked_with} the **server owner**')
        if ctx.author.top_role.position <= member.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** {member.mention} because they are **above** you in the role hierarchy')
        else:
            await member.ban(reason=reason)
            await ctx.reply('👍🏾', mention_author=False)

    @commands.command(
        name='unban',
        description='Unban a user from the server.',
        brief='user',
        usage=
        'Syntax: (user)\n'
        'Example: @void#0480',
        aliases=['pardon'],
        extras={'perms': 'Ban Members'}
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user: str):
        await ctx.typing()

        if user.count('#') == 1:
            username, discriminator = user.split('#')
            async for ban in ctx.guild.bans():
                if (ban.user.name, ban.user.discriminator) == (username, discriminator):
                    await ctx.guild.unban(ban.user)
                    await ctx.reply(f'👍🏾', mention_author=False)
                    return
        else:
            try:
                user_id = int(user)
                member = await self.bot.fetch_user(user_id)
            except ValueError:
                member = discord.utils.find(lambda m: str(m) == user, ctx.guild.bans)
            except discord.NotFound:
                return await ctx.success(f'No user found with ID: `{user}`')
            async for ban in ctx.guild.bans():
                if ban.user.id == member.id:
                    await ctx.guild.unban(ban.user)
                    await ctx.reply(f'👍🏾', mention_author=False)
                    return
        await ctx.success(f'`{user}` has not been **banned**')

    @commands.command(
        name='kick',
        description='Kick a user from the server',
        brief='user, reason',
        usage=
        'Syntax: (user) <reason>\n'
        'Example: @void#0480 calm down',
        aliases=['boot'],
        extras={'perms': 'Kick Members'})
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = None):

        await ctx.typing()
        if not reason:
            reason=f'Banned by {ctx.author}'
        if ctx.author is ctx.guild.owner:
            pass
        if user is ctx.author:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** yourself')
        if user is ctx.guild.owner:
            return await ctx.success(f'You\'re unable to {ctx.invoked_with} the **server owner**')
        if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** {user.mention} because they are **above** you in the role hierarchy')
        else:
            await user.kick(reason=f"{reason}")
            await ctx.reply('👍🏾', mention_author=False)

    @commands.command(
        name='mute',
        description='Mute a user in all channels',
        brief='user, time, reason',
        usage=
        'Syntax: (user) <time> <reason>\n'
        'Example: @void#0480 7d spam',
        aliases=['stfu', 'timeout'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.Member, time=None, *, reason=None):
        await ctx.typing()

        if ctx.author is ctx.guild.owner:
            pass
        if user is ctx.author:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** yourself')
        if user is ctx.guild.owner:
            return await ctx.success(f'You\'re unable to {ctx.invoked_with} the **server owner**')
        if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** {user.mention} because they are **above** you in the role hierarchy')
        
        if not reason and not time:
            time = '28d'
            reason = f'{ctx.author}: Muted indefinitely'
        elif not reason:
            reason = f'{ctx.author}: Muted for {time}'
        elif not time:
            time = '28d'
            reason = f'{ctx.author}: {reason}'
        
        if not re.match(r'^\d+[smhdw]$', time):
            return await ctx.success('Invalid time format. Please use a valid timespan format (e.g. 1s, 2m, 3h, 4d)')
        
        amount = humanfriendly.parse_timespan(time)
        await user.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=amount), reason=reason)
        await ctx.reply('👍🏾', mention_author=False)

    @commands.command(
        name='reactionmute',
        description='Reaction mute a user in all channels',
        brief='user, time, reason',
        usage=
        'Syntax: (user) <time> <reason>\n'
        'Example: @void#0480 7d spam',
        aliases=['rmute'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def reactionmute(self, ctx, user: discord.Member, time=None, *, reason='No reason provided'):
        role = discord.utils.get(ctx.guild.roles, name='rmuted')

        await ctx.typing()
        if role in user.roles:
            return await ctx.success(f'**{user}** is already **reaction muted**')
        if not role:
            role = await ctx.guild.create_role(name='rmuted')
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, add_reactions=False)
        if ctx.author is ctx.guild.owner:
            pass
        if user is ctx.author:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** yourself')
        if user is ctx.guild.owner:
            return await ctx.success(f'You\'re unable to {ctx.invoked_with} the **server owner**')
        if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** {user.mention} because they are **above** you in the role hierarchy')
        if time:
            if self.convert(time) > -1:
                    if reason:
                        tempmute = self.convert(time)
                        await user.add_roles(role)
                        await ctx.reply('👍🏾', mention_author=False)
                        await asyncio.sleep(tempmute)
                        await user.remove_roles(role)
                        return
                    elif not reason:
                        tempmute = self.convert(time)
                        await user.add_roles(role)
                        await ctx.reply('👍🏾', mention_author=False)
                        await asyncio.sleep(tempmute)
                        await user.remove_roles(role)
                        return
            elif self.convert(time) == -1:
                reason = time
                time = 'Indefinite'
                if reason:
                    await user.add_roles(role)
                    return await ctx.reply('👍🏾', mention_author=False)
                elif not reason:
                    await user.add_roles(role)
                    return await ctx.reply('👍🏾', mention_author=False)
        elif not time:
            await user.add_roles(role)
            return await ctx.reply('👍🏾', mention_author=False)

    @commands.command(
        name='imagemute',
        description='Image mute a user in all channels',
        brief='user, time, reason',
        usage=
        'Syntax: (user) <time> <reason>\n'
        'Example: @void#0480 7d gore',
        aliases=['imute'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def imagemute(self, ctx, user: discord.Member, time=None, *, reason='No reason provided'):
        role = discord.utils.get(ctx.guild.roles, name='imuted')

        await ctx.typing()
        if role in user.roles:
            return await ctx.success(f'**{user}** is already **image muted**')
        if not role:
            role = await ctx.guild.create_role(name='imuted')
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, attach_files=False, embed_links=False)
        if ctx.author is ctx.guild.owner:
            pass
        if user is ctx.author:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** yourself')
        if user is ctx.guild.owner:
            return await ctx.success(f'You\'re unable to {ctx.invoked_with} the **server owner**')
        if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** {user.mention} because they are **above** you in the role hierarchy')
        if time:
            if self.convert(time) > -1:
                    if reason:
                        tempmute = self.convert(time)
                        await user.add_roles(role)
                        await ctx.send('👍🏾')
                        await asyncio.sleep(tempmute)
                        await user.remove_roles(role)
                        return
                    elif not reason:
                        tempmute = self.convert(time)
                        await user.add_roles(role)
                        await ctx.send('👍🏾')
                        await asyncio.sleep(tempmute)
                        await user.remove_roles(role)
                        return
            elif self.convert(time) == -1:
                reason = time
                time = 'Indefinite'
                if reason:
                    await user.add_roles(role)
                    return await ctx.send('👍🏾')
                elif not reason:
                    await user.add_roles(role)
                    return await ctx.send('👍🏾')
        elif not time:
            await user.add_roles(role)
            return await ctx.send('👍🏾')
        
    @commands.command(
        name='unmute',
        description='Unmute a user from all channels',
        brief='user',
        usage=
        'Syntax: unmute (user)\n'
        'Example: @void#0480',
        aliases=['unstfu', 'untimeout'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, user: discord.Member):
        await ctx.typing()

        if user.is_timed_out():
            await user.timeout(discord.utils.utcnow())
            await ctx.reply('👍🏾', mention_author=False)
        else:
            await ctx.success(f'**{user}** hasn\'t been **muted**')
                
    @commands.command(
        name='reactionunmute',
        description='Reaction unmute a user from all channels',
        brief='user',
        usage=
        'Syntax: reactionunmute (user)\n'
        'Example: @void#0480',
        aliases=['runmute'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def reactionunmute(self, ctx, user: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="rmuted")
        await ctx.typing()
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send('👍🏾')
        else:
            await ctx.success(f'**{user}** hasn\'t been **reaction muted**')

    @commands.command(
        name='imageunmute',
        description='Image unmute a user from all channels',
        brief='user',
        usage=
        'Syntax: imageunmute (user)\n'
        'Example: @void#0480',
        aliases=['iunmute'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def imageunmute(self, ctx, user: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="imuted")

        await ctx.typing()
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send('👍🏾')
        else:
            await ctx.success(f'**{user}** hasn\'t been **image muted**')

    @commands.group(
        name='purge',
        description='Purge a specified amount of messages',
        brief='amount',
        usage='Syntax: <user> (amount)\n'
            'Example: @void#0480 5',
        aliases=['clear', 'c'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, member: typing.Optional[discord.Member] = None, amount: int = None):
        if amount is None:
            await ctx.send_help(ctx.command)
            return

        messages_purged = 0
        messages = []

        async for message in ctx.channel.history(limit=None):
            if messages_purged >= amount:
                break
            if member is None or message.author == member:
                messages.append(message)
                messages_purged += 1

        if messages:
            await ctx.channel.delete_messages(messages)
            await ctx.success(f'> Purged {messages_purged}', delete_after=1)
        else:
            pass

    @purge.group(
        name='bots',
        description='Purge all the bot messages',
        brief='amount',
        usage=
        'Syntax: (amount)\n'
        'Example: 5',
        aliases=['botclear', 'bc'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_bots(self, ctx, amount: int = None):
        await ctx.message.delete()
        if amount is None:
            await ctx.send_help(ctx.command)
            return
        await ctx.channel.purge(limit=amount, check=lambda msg: msg.author.bot)

    @purge.group(
        name='all',
        description='Purge all messages in a channel',
        usage='Syntax: ',
        aliases=['masspurge', 'purgeall'],
        extras={'perms': 'Manage Messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_all(self, ctx):
        await ctx.channel.purge()
        
    @commands.group(
        invoke_without_command=True,
        name='lockdown',
        description='Lockdown the current channel',
        usage=
        'Syntax: <channel>\n'
        'Example: #general',
        aliases=['l', 'lock'],
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels = True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        await ctx.typing()

        channel = ctx.channel if channel is None else channel
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.success(f'Locked {channel.mention}')
    
    @lockdown.group(
        name='all',
        description='Lockdown the entire server',
        usage='Syntax: all',
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels = True)
    async def lockdown_all(self, ctx):
        await ctx.typing()
        for channels in ctx.guild.text_channels:
            await channels.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.success(f'All channels have been unlocked')

    @commands.group(
        invoke_without_command=True,
        name='unlockdown',
        description='Unlockdown a channel',
        brief='channel',
        usage=
        'Syntax: <channel>\n'
        'Example: #general',
        aliases=['ul', 'unlock'],
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels = True)
    async def unlockdown(self, ctx, channel: discord.TextChannel = None):
        await ctx.typing()

        channel = ctx.channel if channel is None else channel
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.success(f'Unlocked {channel.mention}')

    @unlockdown.group(
        name='all',
        description='Unlockdown the entire server',
        usage='Syntax: all',
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels=True)
    async def unlockdown_all(self, ctx):
        await ctx.typing()
        for channels in ctx.guild.text_channels:
            await channels.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.success(f'> All channels have been unlocked')

    @commands.group(
        invoke_without_command=True,
        name='role',
        description='Add or remove a role to/from a user',
        brief='user, role',
        usage=
        'Syntax: (user) (role)\n'
        'Example: @void#0480 Admin',
        aliases=['r'],
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, user: discord.Member, *, role: discord.Role):
        await ctx.typing()

        if ctx.author is ctx.guild.owner:
            pass
        if user is ctx.guild.owner:
            return await ctx.success(f'You\'re unable to {ctx.invoked_with} the **server owner**')
        if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** {user.mention} because they are **above** you in the role hierarchy')
        elif role in user.roles:
            await user.remove_roles(role)
            await ctx.success(f"Removed {role.mention} from **{user.mention}**")
        else:
            await user.add_roles(role)
            await ctx.success(f"Added {role.mention} to **{user.mention}**")

    @role.group(
        name='add',
        description='Add a role to a user',
        brief='user, role',
        usage=
        'Syntax: (user) (role)\n'
        'Example: @void#0480 Admin',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, user: discord.Member, *, role: discord.Role):
        await ctx.typing()

        if ctx.author is ctx.guild.owner:
            pass
        if user is ctx.author:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** yourself')
        if user is ctx.guild.owner:
            return await ctx.success(f'You\'re unable to {ctx.invoked_with} the **server owner**')
        if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** {user.mention} because they are **above** you in the role hierarchy')
        await user.add_roles(role)
        await ctx.success(f"> Added {role.mention} to **{user.display_name}**")

    @role.group(
        name='remove',
        description='Remove a role from a user',
        brief='user, role',
        usage=
        'Syntax: (user) (role)\n'
        'Example: @void#0480 Admin',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def role_remove(self, ctx, user: discord.Member, *, role: discord.Role):
        await ctx.typing()

        if ctx.author is ctx.guild.owner:
            pass
        if user is ctx.author:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** yourself')
        if user is ctx.guild.owner:
            return await ctx.success(f'You\'re unable to {ctx.invoked_with} the **server owner**')
        if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.success(f'You\'re unable to **{ctx.invoked_with}** {user.mention} because they are **above** you in the role hierarchy')
        await user.remove_roles(role)
        await ctx.success(f"Removed {role.mention} from **{user.display_name}**")
    
    @role.group(
        name='create',
        description='Create a role',
        brief='role',
        usage=
        'Syntax: (role)\n'
        'Example: Admin',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def create(self, ctx, *, role):
        await ctx.typing()

        await ctx.guild.create_role(name=role)
        role = discord.utils.get(ctx.guild.roles, name=role)
        await ctx.success(f'Created {role.mention}')

    @role.group(
        name='delete',
        description='Delete a role',
        brief='role',
        usage=
        'Syntax: (role)\n'
        'Example: Admin',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def delete(self, ctx, *, role):
        await ctx.typing()

        role = discord.utils.get(ctx.guild.roles, name=role)
        await ctx.success(f'Deleted **{role}**')
        await role.delete()

    @role.group(
        invoke_without_command=True,
        name='humans',
        description='Add a role to all humans',
        brief='role',
        usage=
        'Syntax: (role)\n'
        'Example: Members',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def humans(self, ctx, *, role: discord.Role):
        await ctx.typing()

        e = discord.Embed(color=color, description=f'Adding {role.mention} to all humans')
        msg = await ctx.reply(embed=e, mention_author=False)
        for m in filter(lambda m: not m.bot, ctx.guild.members):
            if role in m.roles:
                pass
            else:
                await m.add_roles(role)
        e = discord.Embed(color=color, description=f'Added {role.mention} to all humans')
        await msg.edit(embed=e)

    @humans.group(
        name='remove',
        description='Remove a role from all humans',
        brief='role',
        usage=
        'Syntax: (role)\n'
        'Example: Members',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def humans_remove(self, ctx, *, role: discord.Role):
        await ctx.typing()

        e = discord.Embed(color=color, description=f'Removing {role.mention} from all humans')
        msg = await ctx.reply(embed=e, mention_author=False)
        for m in filter(lambda m: not m.bot, ctx.guild.members):
            if role in m.roles:
                await m.remove_roles(role)
        e = discord.Embed(color=color, description=f'Removed {role.mention} from all humans')
        await msg.edit(embed=e)

    @role.group(
        name='rename',
        description='Change the name of a role',
        brief='role, name',
        usage=
        'Syntax: (role) (name)\n'
        'Example: Community Member',
        extras={'perms': 'Manage Roles'}
    )
    async def rename(self, ctx, role: discord.Role, *, name):
        role.edit(name=name)
        await ctx.success(f'Renamed {role.mention} to **{name}**')

    @role.group(
        invoke_without_command=True,
        name='bots',
        description='Add a role to all bots',
        brief='role',
        usage=
        'Syntax: (role)\n'
        'Example: Bot',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def bots(self, ctx, *, role: discord.Role):
        await ctx.typing()

        e = discord.Embed(color=color, description=f'Adding {role.mention} to all bots')
        msg = await ctx.reply(embed=e, mention_author=False)
        for m in filter(lambda m: m.bot, ctx.guild.members):
            if role in m.roles:
                pass
            else:
                await m.add_roles(role)
        e = discord.Embed(color=color, description=f'Added {role.mention} to all bots')
        await msg.edit(embed=e)

    @bots.group(
        name='remove',
        description='Remove a role from all bots',
        brief='role',
        usage=
        'Syntax: (role)\n'
        'Example: Bot',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def bots_remove(self, ctx, *, role: discord.Role):
        await ctx.typing()

        e = discord.Embed(color=color, description=f'Removed {role.mention} from all bots')
        msg = await ctx.reply(embed=e, mention_author=False)
        for m in filter(lambda m: m.bot, ctx.guild.members):
            if role not in m.roles:
                pass
            else:
                await m.remove_roles(role)
        e = discord.Embed(color=color, description=f'Removed {role.mention} from all bots')
        await msg.edit(embed=e)

    @commands.command(
        name='nickname',
        description='Change a nickname of a user',
        brief='user, nickname',
        usage=
        'Syntax: (user) (nickname)\n'
        'Example: @void#0480 Best Bot WW',
        aliases=['nick'],
        extras={'perms': 'Manage Nicknames'}
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, user: discord.Member, *, name: str = None):
        await ctx.typing()

        if name is None:
            await ctx.success(f'Reset **{user.name}\'s** nickname')
            await user.edit(nick=name)
        else:
            await ctx.success(f'Changed **{user.name}\'s** nickname to **{name}**')
            await user.edit(nick=name)

    @commands.group( # addmany, rename and information  
        invoke_without_command=True,
        name='emote',
        description='Enlarge an emote',
        brief='emote',
        usage=
        'Syntax: <emote>\n'
        'Example: 😈',
        aliases=['emoji'],
        extras={'perms': 'Manage Emojis'}
    )
    async def emote(self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji] = None):
        await ctx.typing()

        if not emoji:
            await ctx.send_help(ctx.command)
        e = discord.Embed(
            color=color,
            title=f'{emoji.name}',
            url=emoji.url)
        e.set_image(url=emoji.url)
        await ctx.send(embed=e)

    @emote.group(
        name='add',
        description='Add an emoji to the server',
        brief='emote',
        usage=
        'Syntax: (emote)\n'
        'Example: 😈',
        aliases=['steal'],
        extras={'perms': 'Manage Emojis'}
    )
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def add(self, ctx, emoji: discord.PartialEmoji):
        await ctx.typing()

        e = await ctx.guild.create_custom_emoji(name=emoji.name, image=await emoji.read())
        await ctx.success(f'Added {e}')

    @emote.group(
        name='delete',
        description='Remove an emoji to the server',
        brief='emote',
        usage=
        'Syntax: (emote)\n'
        'Example: 😈',
        aliases=['remove'],
        extras={'perms': 'Manage Emojis'}
    )
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def emote_delete(self, ctx, emoji: discord.Emoji):       
        await ctx.typing()

        if emoji in list(ctx.guild.emojis):
            await emoji.delete()
        await ctx.success(f'Deleted `{emoji.name}`')
    
    @emote.group(
        name='rename',
        description='Rename an emote from the server',
        usage=
        'Syntax: (emote) (new name)\n'
        'Example: smiling_imp demon',
        aliases=['name'],
        extras={'perms': 'Manage Emojis'}
    )
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def rename(self, ctx, emoji: discord.Emoji, *, name=str):
        await ctx.typing()

        if emoji in list(ctx.guild.emojis):
            await emoji.edit(name=name)
            await ctx.success(f'`{emoji}` renamed to **{name}**')

    @emote.group(
        name='list',
        description='View all the motes in the server',
        usage='Syntax: ',
    )
    async def _list(self, ctx):
        await ctx.typing()

        embeds = []
        ret = []
        num = 0
        pagenum = 0
        for m in ctx.guild.emojis:
            num += 1
            ret.append(f'**{num}.** {m} - [{m.name}]({m.url})')
            pages = [p for p in discord.utils.as_chunks(ret, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(discord.Embed(
                color=color,
                title=f'Emojis in {ctx.guild.name}',
                description="\n".join(page))
                .set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                .set_footer(text=f'Page {pagenum}/{len(pages)}')
                )
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        else:
            pag = Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            pag.add_button('prev', emoji='<:void_previous:1082283002207424572>')
            pag.add_button('goto', emoji='<:void_goto:1082282999187517490>')
            pag.add_button('next', emoji='<:void_next:1082283004321341511>')
            pag.add_button('delete', emoji='<:void_cross:1082283006649188435>')
            await pag.start()
    
    @commands.command(
        name='bans',
        description='View the banned users of the server',
        usage='Syntax: ',
        aliases=['banlist'],
        extras={'perms': 'Ban Members'}
    )
    @commands.has_permissions(ban_members=True)
    async def bans(self, ctx):

        await ctx.typing()
        embeds=[]
        entries=[]
        pagenum=0
        async for entry in ctx.guild.bans():
            entries.append(entry)
        if entry is None:
            return await ctx.success(f"This guild doesn\'t have any bans")
        formatted_entries = [f"**{number + 1}.** {entry.user} - *{entry.reason}*" for number, entry in enumerate(entries)]
        pages = [p for p in discord.utils.as_chunks(formatted_entries, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(discord.Embed(
                color=color,
                title=f'Bans in {ctx.guild.name}',
                description="\n".join(page))
                .set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                .set_footer(text=f'Page {pagenum}/{len(pages)}')
                )
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        else:
            pag = Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            pag.add_button('prev', emoji='<:void_previous:1082283002207424572>')
            pag.add_button('goto', emoji='<:void_goto:1082282999187517490>')
            pag.add_button('next', emoji='<:void_next:1082283004321341511>')
            pag.add_button('delete', emoji='<:void_cross:1082283006649188435>')
            await pag.start()
                                   
async def setup(bot):
    await bot.add_cog(Moderation(bot))
