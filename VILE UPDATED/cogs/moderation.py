import discord, typing, time, arrow, psutil, copy, aiohttp
from datetime import datetime, timedelta
from typing import Optional, Union
from utilities import utils, confirmation
from utilities.baseclass import Vile
from utilities.context import Context
from utilities.advancedutils import parse_timespan
from utilities.tasks import submit
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot: Vile) -> None:
        self.bot = bot


    @commands.command(
        name='moderationhistory',
        aliases=['modhistory', 'history', 'mh', 'mhistory', 'modh'],
        description="view the mentioned user's moderation history",
        brief='modhistory <user>',
        help='modhistory @glory#0007',
        extras={'permissions': 'moderate members'}
    )
    @commands.has_permissions(moderate_members=True)
    async def moderationhistory(self, ctx: Context, user: Union[discord.Member, discord.User] = commands.Author):

        if not await self.bot.db.execute('SELECT * FROM moderation_history WHERE user_id = %s AND guild_id = %s', user.id, ctx.guild.id):
            return await ctx.send_error(f"couldn't find any **moderation history** for {user.name}")

        embed = discord.Embed(
            color=self.bot.color,
            title=f'Moderation history for {user.name}',
            description=list()
        )
        for action, moderator_id, reason, timestamp in await self.bot.db.execute('SELECT action, moderator_id, reason, timestamp FROM moderation_history WHERE user_id = %s AND guild_id = %s', user.id, ctx.guild.id):
            embed.description.append(f"**{action}**\n{self.bot.reply} **moderator:** {self.bot.get_user(moderator_id)}\n{self.bot.reply} **reason:** {reason}\n{self.bot.reply} **recorded:** {datetime.fromtimestamp(timestamp).strftime('%B %-d, %Y %I:%M %p')}")

        return await ctx.paginate(embed)


    @commands.hybrid_command(
        name='ban',
        aliases=['deport'],
        description='bans the mentioned user',
        brief='ban <user> [reason]',
        help='ban @glory#0007 breaking rules',
        extras={'permissions': 'ban members'}
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: Context, user: Union[discord.Member, discord.User], *, reason: Optional[str] = 'no reason'):
            
        if await ctx.can_moderate(user, 'ban') is not None:
            return

        audit_reason = f'ban: used by {ctx.author}'
        if reason != 'no reason':
            audit_reason=f'"{reason}" - ban: used by {ctx.author}'

        if ctx.guild.id not in self.bot.cache.limits['bans']:
            self.bot.cache.limits['bans'][ctx.guild.id] = 0

        await ctx.guild.ban(user, reason=audit_reason)
        self.bot.cache.limits['bans'][ctx.guild.id] += 1
        
        if await self.bot.db.fetchval('SELECT message FROM ban_message WHERE guild_id = %s', ctx.guild.id):
            custom_ban_message = await self.bot.db.fetchval('SELECT message FROM ban_message WHERE guild_id = %s', ctx.guild.id)
            await ctx.send(**await utils.to_object(await utils.embed_replacement(user, custom_ban_message)))
            
        else:
            await ctx.send_success(f'{user} (`{user.id}`) was **banned** for {reason}')

        if isinstance(user, discord.User):
            return

        if await self.bot.db.execute('SELECT state FROM mod_dms WHERE guild_id = %s', ctx.guild.id) == () or await self.bot.db.execute('SELECT state FROM mod_dms WHERE guild_id = %s', ctx.guild.id) == True:
            try:
                return await ctx.dm(
                    user, 
                    embed=discord.Embed(
                        color=self.bot.color,
                        description=f"you were **banned** from **{ctx.guild.name}**\n{self.bot.reply} **moderator:** {ctx.author}\n{self.bot.reply} **reason:** {reason or 'none'}"
                    )
                )
            except:
                return


    @commands.command(
        name='kick',
        description='kicks the mentioned user',
        brief='kick <user> [reason]',
        help='kick @glory#0007 spamming',
        extras={'permissions': 'kick members'}
    )
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: discord.Member, *, reason: Optional[str] = 'no reason'):
            
        if await ctx.can_moderate(member, 'kick') is not None:
            return

        audit_reason = f'kick: used by {ctx.author}'
        if reason != 'no reason':
            audit_reason=f'"{reason}" - kick: used by {ctx.author}'
        if ctx.guild.id not in self.bot.cache.limits['kicks']:
            self.bot.cache.limits['kicks'][ctx.guild.id] = 0

        await member.kick(reason=audit_reason)
        self.bot.cache.limits['kicks'][ctx.guild.id] += 1

        await ctx.send_success(f'{member} (`{member.id}`) was **kicked** for {reason}')

        if await self.bot.db.execute('SELECT state FROM mod_dms WHERE guild_id = %s', ctx.guild.id) == () or await self.bot.db.execute('SELECT state FROM mod_dms WHERE guild_id = %s', ctx.guild.id) == True:
            try:
                await ctx.dm(
                    member, 
                    embed=discord.Embed(
                        color=self.bot.color,
                        description=f"you were **kicked** from **{ctx.guild.name}**\n{self.bot.reply} **moderator:** {ctx.author}\n{self.bot.reply} **reason:** {reason or 'none'}"
                    )
                )
            except:
                pass


    @commands.command(
        name='unban',
        description='unbans the provided user',
        brief='unban <user>',
        help='unban glory#0007',
        extras={'permissions': 'ban members'}
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: Context, user: discord.User):

        await ctx.guild.unban(user, reason=f'unban: used by {ctx.author}')

        try:
            await ctx.dm(
                user,
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.fail} {member.mention}**:** you were **unbanned** from **{ctx.guild.name}**\n{self.bot.reply} **moderator:** {ctx.author}\n{self.bot.reply} **invite:** {await ctx.channel.create_invite(max_uses=1, unique=False)}"
                )
            )
        except:
            pass
        
        return await ctx.send_success(f'successfully **unbanned** {user} from {ctx.guild.name}')

    
    @commands.hybrid_command(
        name='mute',
        aliases=['m', 'timeout'],
        description='mute the mentioned member',
        brief='mute <member> [time d/h/m/s]',
        help='mute @glory#0007 1h',
        extras={'permissions': 'moderate members'}
    )
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx: Context, member: discord.Member, time: str):

        if await ctx.can_moderate(member, 'mute') is not None:
            return

        try:
            time = parse_timespan(time)
        except:
            return await ctx.send_error('please provide a **valid** time')

        await member.edit(
            timed_out_until=datetime.now().astimezone() + timedelta(seconds=time),
            reason=f'mute: used by {ctx.author}'
        )

        return await ctx.send_success(f'{member} (`{member.id}`) was **muted** for {utils.fmtseconds(time)}')


    @commands.command(
        name='unmute',
        aliases=['um'],
        description='unmute the mentioned member',
        brief='unmute <member>',
        help='unmute @glory#0007'
    )
    @commands.bot_has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx: Context, member: discord.Member):

        if await ctx.can_moderate(member, 'unmute') is not None:
            return

        await member.edit(timed_out_until=None)
        return await ctx.send_success(f"{member} (`{member.id}`) was **unmuted** ")


    @commands.command(
        name='imagemute',
        aliases=['imute', 'imgmute'],
        description="take away, or return, the mentioned member's image perms",
        brief='imagemute <member>',
        help='imagemute @glory#0007',
        extras={'permissions': 'moderate members'}
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def imagemute(self, ctx: Context, member: discord.Member):

        await ctx.typing()
        if await ctx.can_moderate(member, 'image-mute') is not None:
            return

        overwrites = ctx.channel.overwrites_for(member)
        if overwrites.is_empty() or overwrites.attach_files == True and overwrites.embed_links == True:
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(
                    member, 
                    overwrite=discord.PermissionOverwrite(attach_files=False, embed_links=False), 
                    reason=f'imagemute: used by {ctx.author}'
                )

            return await ctx.send_success(f'{member} (`{member.id}`) was **image muted**')

        elif overwrites.attach_files == False and overwrites.embed_links == False:
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(
                    member, 
                    overwrite=discord.PermissionOverwrite(attach_files=True, embed_links=True), 
                    reason=f'imagemute: used by {ctx.author}'
                )

            return await ctx.send_success(f"{member}'s **image mute** has been removed")

        return await ctx.send_error(f"{member} isn't **image muted**")


    @commands.command(
        name='reactionmute',
        aliases=['rmute', 'reactmute'],
        description="take away, or return, the mentioned member's reaction perms",
        brief='reactionmute <member>',
        help='reactionmute @glory#0007',
        extras={'permissions': 'moderate members'}
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(moderate_members=True)
    async def reactionmute(self, ctx: Context, member: discord.Member):

        await ctx.typing()
        if await ctx.can_moderate(member, 'reaction-mute') is not None:
            return

        overwrites = ctx.channel.overwrites_for(member)
        if overwrites.is_empty() or overwrites.add_reactions == True or overwrites.add_reactions is None:
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(
                    member, 
                    overwrite=discord.PermissionOverwrite(add_reactions=False), 
                    reason=f'reactionmute: used by {ctx.author}'
                )

            return await ctx.send_success(f'{member} (`{member.id}`) was **reaction muted**')

        elif overwrites.add_reactions == False:
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(
                    member, 
                    overwrite=discord.PermissionOverwrite(add_reactions=True), 
                    reason=f'reactionmute: used by {ctx.author}'
                )

            return await ctx.send_success(f"{member}'s **reaction mute** has been removed")

        return await ctx.send_error(f"{member} isn't **reaction muted**")


    @commands.command(
        name='nuke',
        description='delete the channel and clone it',
        extras={'permissions': 'administrator'},
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx: Context):

        if ctx.channel == ctx.guild.system_channel or ctx.channel == ctx.guild.rules_channel:
            return await ctx.send_error('you cant **nuke** this channel')

        with submit(ctx):
            bot_message = await ctx.send_error(f'are you sure you want to **nuke** this channel?')
            conf = await confirmation.confirm(ctx, bot_message)
            if conf is True:
                new_channel = await ctx.channel.clone(
                    name=ctx.channel.name,
                    reason=f'nuke: used by {ctx.author}'
                )
                await ctx.channel.delete(reason=f'nuke: used by {ctx.author}')
                await new_channel.edit(position=ctx.channel.position)
                
                return await new_channel.send(
                    embed=discord.Embed(
                        color=self.bot.color,
                        description=f'{self.bot.done} {ctx.author.mention}**:** successfully **nuked** #{ctx.channel.name}'
                    )
                )
            else:
                return await ctx.send_error('channel nuke has been **cancelled**')


    @commands.group(
        name='forcenickname',
        aliases=['forcenick'],
        description='add or remove a forced nickname',
        brief='forcenick <sub command>',
        help='forcenick add @glory#0007 bad dev',
        extras={'permissions': 'moderate members'},
        invoke_without_command=True
    )
    @commands.has_permissions(moderate_members=True)
    async def forcenickname(self, ctx: Context):
        
        return await ctx.send_help()


    @forcenickname.command(
        name='add',
        aliases=['create'],
        description='add a forced nickname to a user',
        brief='forcenick add <user> <nickname>',
        help='forcenick add @glory#0007 bad dev',
        extras={'permissions': 'moderate members'}
    )
    @commands.has_permissions(moderate_members=True)
    async def forcenick_add(self, ctx: Context, member: discord.Member, *, nickname: str):
        
        if await ctx.can_moderate(member, 'forcenick') is not None:
            return
            
        await self.bot.db.execute('INSERT INTO forcenick (guild_id, user_id, nickname) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE nickname = VALUES(nickname)', ctx.guild.id, member.id, nickname)

        self.bot.cache.force_nickname.setdefault(ctx.guild.id, dict())[member.id] = nickname

        try:
            await member.edit(nick=nickname)
        except:
            return await ctx.send_error(f"failed to change {member.mention}'s nicknme to **`{discord.utils.escape_markdown(nickname)}`**")

        
        await ctx.send_success(f"successfully **binded** {member.mention}'s forced nickname to **`{discord.utils.escape_markdown(nickname)}`**")


    @forcenickname.command(
        name="remove",
        aliases=['delete'],
        description='remove a forced nickname to a user',
        brief=',forcenick remove <user>',
        help=',forcenick remove gwen',
        extras={'permissions': 'moderate members'}
    )
    @commands.has_permissions(moderate_members=True)
    async def forcenick_remove(self, ctx: Context, member: discord.Member):
        
        if await ctx.can_moderate(member, 'forcenick') is not None:
            return
            
        await self.bot.db.execute('DELETE FROM forcenick WHERE user_id = %s AND guild_id = %s', member.id, ctx.guild.id)

        try:
            self.bot.cache.force_nickname.setdefault(ctx.guild.id, dict()).pop(member.id)
        except:
            pass

        await member.edit(nick=None)
        
        await ctx.send_success(f"successfully **removed** {member.mention}'s forced nickname")


    @forcenickname.command(
        name='list',
        aliases=['show'],
        description="show all the server's forced nicknames",
        extras={'permissions': 'moderate members'}
    )
    @commands.has_permissions(moderate_members=True)
    async def forcenick_list(self, ctx: Context):
        
        if not await self.bot.db.execute('SELECT * FROM forcenick WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **forced nicknames** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Forced nicknames in {ctx.guild.name}',
            description=list()
        )
        for user_id, nickname in await self.bot.db.execute('SELECT user_id, nickname FROM forcenick WHERE guild_id = %s', ctx.guild.id):
            if ctx.guild.get_member(user_id) is not None:
                embed.description.append(f'{ctx.guild.get_member(user_id).mention}\n{self.bot.reply} **nickname:** {nickname}')
            
        return await ctx.paginate(embed)


    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        
        if before.nick != after.nick:
            if self.bot.cache.force_nickname.get(after.guild.id) is not None:
                if self.bot.cache.force_nickname[after.guild.id].get(after.id) is not None:
                    forcenick = self.bot.cache.force_nickname[after.guild.id][after.id]
                    await after.edit(nick=forcenick)


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if self.bot.cache.force_nickname.get(member.guild.id) is not None:
            if self.bot.cache.force_nickname[member.guild.id].get(member.id) is not None:
                forcenick = self.bot.cache.force_nickname[member.guild.id][member.id]
                await member.edit(nick=forcenick)


    @commands.group(
        name='purge',
        aliases=['clear', 'p', 'c'],
        description='purge messages in a channel',
        brief='purge [amount]',
        help='purge 5',
        extras={'permissions': 'manage messages'},
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: Context, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages')
        
        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=amount+1))} messages", delete_after=3
        )


    @purge.command(
        name='user',
        description='purge messages from a user',
        brief='purge user <member> [amount]',
        help='purge user 5',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_user(self, ctx: Context, member: discord.Member, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages from {member.mention}')
        
        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=amount+1, check=lambda m: m.author == member))} messages from {member.mention}", delete_after=3
        )


    @purge.command(
        name='humans',
        description='purge messages from humans',
        brief='purge humans [amount]',
        help='purge humans 5',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_humans(self, ctx: Context, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages from humans')
        
        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=amount+1, check=lambda m: not m.author.bot))} messages from humans", delete_after=3
        )


    @purge.command(
        name='bots',
        description='purge messages from bots',
        brief='purge bots [amount]',
        help='purge bots 5',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_bots(self, ctx: Context, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages from bots')
        
        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=amount+1, check=lambda m: m.author.bot))} messages from bots", delete_after=3
        )


    @purge.command(
        name='images',
        aliases=['files', 'attachments'],
        description='purge messages with images & attachments',
        brief='purge images [amount]',
        help='purge images 5',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_images(self, ctx: Context, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages with images')
        
        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=amount+1, check=lambda m: m.attachments))} messages with images", delete_after=3
        )


    @purge.command(
        name='mentions',
        aliases=['ping'],
        description='purge role & user mentions',
        brief='purge mentions [amount]',
        help='purge mentions 5',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_mentions(self, ctx: Context, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages with mentions')

        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=amount+1, check=lambda m: m.mentions))} messages with mentions", delete_after=3
        )

        
    @purge.command(
        name='links',
        aliases=['embeds'],
        description='purge messages with embeds or links',
        brief='purge links [amount]',
        help='purge links 5',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_links(self, ctx: Context, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages with links')

        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=amount+1, check=lambda m: m.embeds or 'http://' in m.content or 'https://' in m.content))} messages with embeds/links", delete_after=3
        )


    @purge.command(
        name='invites',
        aliases=['invite', 'inv'],
        description='purge messages with invites',
        brief='purge invites [amount]',
        help='purge invites 5',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_invites(self, ctx: Context, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages with invites')

        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=amount+1, check=lambda m: '.gg/' in m.content or '/invite/' in m.content))} messages with invites", delete_after=3
        )


    @purge.command(
        name='matches',
        aliases=['match'],
        description='purge messages matching the word/substring',
        brief='purge matches <word> [amount]',
        help='purge matches hi 5',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge_matches(self, ctx: Context, word: str, amount: Optional[int] = 10):

        if amount > 1000:
            return await ctx.send_success("you can't purge more than **1000 messages**")
        
        if amount in [0, 1]:
            return await ctx.send_success(f'successfully **purged** 0 messages that match the word **`{word}`**')

        return await ctx.send_success(
            f'successfully **purged** {len(await ctx.channel.purge(limit=amount+1, check=lambda m: word in m.content))} messages that match the word **`{word}`**', delete_after=3
        )


    @commands.hybrid_command(
        name='botclear',
        aliases=['cleanup', 'bc'],
        description='clear messages from bots',
        extras={'permissions': 'manage messages'}
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def botclear(self, ctx: Context):

        await ctx.typing()
        return await ctx.send_success(f'successfully **cleared** {len(await ctx.channel.purge(limit=100, check=lambda m: m.author.bot or m.content.startswith(ctx.prefix)))} messages from bots')

    
    @commands.command(
        name='massunban',
        aliases=['unbanall'],
        description='unban every banned user from the server',
        extras={'permissions': 'administrator'}
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(administrator=True)
    async def massunban(self, ctx: Context):
        
        message = await ctx.send_error('are you **sure** you want to unban every banned user?')
        conf = await confirmation.confirm(ctx, message)

        with submit(ctx):
            if conf is True:
                to_delete = await ctx.send_success('**unbanning** all banned users, please wait...')
                async with ctx.handle_response():
                    async for entry in ctx.guild.bans(limit=None):
                        try:
                            await ctx.guild.unban(entry.user, reason=f'massunban: used by {ctx.author}')
                        except:
                            continue

                await to_delete.delete()
                return await ctx.send_success('successfully **unbanned** all banned users')

            await message.edit(view=None)
            return await message.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.fail} {ctx.author.mention}**:** action has been **cancelled**'
                )
            )

    
    @commands.command(
        name='stripstaff',
        aliases=['strip'],
        description="remove a member's dangerous roles",
        brief='stripstaff <member>',
        help='stripstaff @glory#0007',
        extras={'permissions': 'moderate members'}
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(moderate_members=True)
    async def stripstaff(self, ctx: Context, member: discord.Member):


        if await ctx.can_moderate(member, 'strip') is not None:
            return

        with submit(ctx):
            await member.edit(roles=[role for role in member.roles if role.is_assignable() and not role.is_dangerous()])
            return await ctx.send_success("successfully **stripped** that member's dangerous roles")


    @commands.command(
        name='lock',
        description='lock the current channel'
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx: Context, channel: Optional[discord.TextChannel] = None):
        
        channel = channel or ctx.channel
        await channel.set_permissions(
            ctx.guild.default_role, 
            overwrite=discord.PermissionOverwrite(send_messages=False),
            reason=f'unlock: used by {ctx.author}'
        )
        return await ctx.send_success(f'successfully **locked** #{channel.name}')
        

    @commands.command(
        name='unlock',
        description='unlock the current channel'
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx: Context, channel: Optional[discord.TextChannel] = None):
        
        channel = channel or ctx.channel
        await channel.set_permissions(
            ctx.guild.default_role, 
            overwrite=discord.PermissionOverwrite(send_messages=True),
            reason=f'unlock: used by {ctx.author}'
        )
        return await ctx.send_success(f'successfully **unlocked** #{channel.name}')


    @commands.command(
        name='uwulock',
        aliases=['ul'],
        description="uwuify all of a member's messages",
        brief='uwulock <member>',
        help='uwulock @glory#0007',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def uwulock(self, ctx: Context, member: discord.Member):
        
        if await ctx.can_moderate(member, 'uwulock') is not None:
            return

        if member.id in set(await self.bot.db.fetch('SELECT user_id FROM uwulock WHERE guild_id = %s', ctx.guild.id)):
            await self.bot.db.execute('DELETE FROM uwulock WHERE guild_id = %s AND user_id = %s', ctx.guild.id, member.id)
            await self.bot.cache.cache_uwulock()
            
            return await ctx.send_success(f"successfully **removed** {member.mention}'s uwu lock")
            
        await self.bot.db.execute('INSERT INTO uwulock (guild_id, user_id) VALUES (%s, %s)', ctx.guild.id, member.id)
        if ctx.guild.id not in self.bot.cache.uwulock:
            self.bot.cache.uwulock[ctx.guild.id] = set()
            
        self.bot.cache.uwulock[ctx.guild.id].add(member.id)
        return await ctx.send_success(f'successfully **uwulocked** {member.mention}')


    @commands.command(
        name='semimute',
        aliases=['stfu'],
        description="delete all of a member's messages",
        brief='semimute <member>',
        help='semimute @glory#0007',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def semimute(self, ctx: Context, member: discord.Member):
        
        if await ctx.can_moderate(member, 'semimute') is not None:
            return
        
        if member.id in set(await self.bot.db.fetch('SELECT user_id FROM semimute WHERE guild_id = %s', ctx.guild.id)):
            await self.bot.db.execute('DELETE FROM semimute WHERE guild_id = %s AND user_id = %s', ctx.guild.id, member.id)
            await self.bot.cache.cache_semimute()
            
            return await ctx.send_success(f"successfully **removed** {member.mention}'s semi mute")
            
        await self.bot.db.execute('INSERT INTO semimute (guild_id, user_id) VALUES (%s, %s)', ctx.guild.id, member.id)
        if ctx.guild.id not in self.bot.cache.semimute:
            self.bot.cache.semimute[ctx.guild.id] = set()
            
        self.bot.cache.semimute[ctx.guild.id].add(member.id)
        return await ctx.send_success(f'{member} (`{member.id}`) was **semi-muted** indefinitely')


    @commands.command(
        name='revokefiles',
        aliases=['revokeimages'],
        description="take away, or return, everyone's image perms",
        brief='revokefiles [channel]',
        help='revokefiles #chat',
        extras={'permissions': 'manage channels'}
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def revokefiles(self, ctx: Context, channel: Optional[discord.TextChannel] = None):
        
        channel = channel or ctx.channel
        if (channel.permissions_for(ctx.guild.default_role).attach_files is True) or (channel.permissions_for(ctx.guild.default_role).embed_links is True):
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=discord.PermissionOverwrite(attach_files=False, embed_links=False)
            )
            return await ctx.send_success(f"successfully **revoked** everyone's image permissions in #{channel.name}")
            
        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=discord.PermissionOverwrite(attach_files=True, embed_links=True)
        )
        return await ctx.send_success(f"successfully **granted** everyone image permissions in #{channel.name}")


    @commands.command(
        name='naughty',
        description='toggle nsfw in a channel',
        brief='naughty [channel]',
        help='naughty #nsfw',
        extras={'permissions': 'manage channels'}
    )
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    async def naughty(self, ctx: Context, channel: Optional[discord.TextChannel] = None):
        
        channel = channel or ctx.channel
        if channel.nsfw is True:
            await channel.edit(nsfw=False)
            return await ctx.send_success(f'successfully **disabled** nsfw in #{channel.name}')
            
        else:
            await channel.edit(nsfw=True)
            return await ctx.send_success(f'successfully **enabled** nsfw in #{channel.name}')


async def setup(bot: Vile):
    await bot.add_cog(Moderation(bot))
