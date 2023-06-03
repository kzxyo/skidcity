import discord, time, difflib, os, arrow, pathlib, random, pytz, subprocess, asyncio, psutil
from aiohttp import BasicAuth
from utilities import DL, utils, confirmation, models, config
from utilities.redis import VileRedis
from utilities.cache import VileCache
from utilities.watcher import RebootRunner
from utilities.context import Context
from utilities.vileapi import VileAPI
from utilities.maria import MariaDB
from typing import Optional, Union, Any
from datetime import datetime, timedelta
from discord.ext import commands, tasks


commands.Context = Context
commands.has_permissions = models.has_permissions
discord.Role.is_dangerous = models.is_dangerous
discord.Message.refer = lambda self: self.reference.resolved if self.reference else self
discord.Message.invites = models.invites
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'


# bot


from utilities.baseclass import Vile
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = Vile(
    command_prefix=utils.determine_prefix,
    intents=intents,
    chunk_guilds_at_startup=False,
    help_command=None,
    case_insensitive=True,
    activity=discord.Streaming(
        name='in discord.gg/vilebot',
        url='https://twitch.tv/directory'
    ),
    strip_after_prefix=True,
    allowed_mentions=discord.AllowedMentions(
        everyone=False, 
        replied_user=False, 
        users=True, 
        roles=False
    ),
    max_messages=5000,
    shard_count=2,
    heartbeat_timeout=120
)


# events


@bot.event
async def on_connect():
    dump_database.start()
    
    
@bot.event
async def on_disconnect():
    dump_database.cancel()


@bot.event
async def on_ready():
    
    await bot.load_extensions()
    await RebootRunner(bot, path='cogs').start()
    await RebootRunner(bot, path='events').start()
    bot.ready = datetime.now(pytz.timezone('America/New_York'))
    subtract_warden_threshold.start()
    subtract_dm_threshold.start()
    
    
@bot.event 
async def on_message(message: discord.Message):
    
    if message.guild is None or message.author.bot:
        return

    bot.cache.event_triggers['message'] += 1

    if bot.cache.afk.get(message.author.id):
        entry = utils.find(bot.cache.afk[message.author.id], key=lambda e: e['guild_id'] == message.guild.id)
        if entry:
            status = entry['status']
            lastseen = arrow.get(entry['lastseen']).humanize()

            await bot.db.execute('DELETE FROM afk WHERE user_id = %s AND guild_id = %s', message.author.id, message.guild.id)
            bot.cache.afk[message.author.id].remove(entry)
            if not bot.cache.afk[message.author.id]:
                bot.cache.afk.pop(message.author.id)

            embed = discord.Embed(
                color=0x2f3136,
                description=f':wave: {message.author.mention}**:** welcome back, you were last seen **{lastseen}**'
            )
            await message.reply(embed=embed)


    if utils.determine_filter(bot, message):
        await message.reply(
            embed=discord.Embed(
                color=bot.color,
                description=f'{bot.fail} {message.author.mention}**:** watch your mouth! that word is **filtered** in this server'
            ),
            delete_after=5
        )
        try:
            await message.delete()
        except:
            pass

    if message.channel.id not in bot.cache.image_only.get(message.guild.id, []):
        await bot.process_commands(message)

    if message.type == discord.MessageType.premium_guild_subscription:
        bot.dispatch('boost', message.author)


@bot.event
async def on_message_delete(message: discord.Message):

    if message.guild is None or message.author.bot:
        return

    bot.cache.event_triggers['message_delete'] += 1


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):

    if before.guild is None or before.author.bot:
        return
    
    bot.cache.event_triggers['message_edit'] += 1
    if before.content != after.content:
        bot.dispatch('message', after)


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):

    if isinstance(user, discord.User) or user.bot:
        return

    bot.cache.event_triggers['reaction_add'] += 1


@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):

    if isinstance(user, discord.User) or user.bot:
        return

    bot.cache.event_triggers['reaction_remove'] += 1


@bot.event
async def on_member_join(member: discord.Member):

    if member.bot:
        return

    bot.cache.event_triggers['member_join'] += 1


@bot.event
async def on_member_remove(member: discord.Member):

    if member.bot:
        return

    bot.cache.event_triggers['member_remove'] += 1

    if member.guild.id not in bot.cache.member_joins:
        bot.cache.member_joins[member.guild.id] = 0

    bot.cache.member_joins[member.guild.id] -= 1
    
    if member.guild.me.guild_permissions.view_audit_log:
        audit_log = [entry async for entry in member.guild.audit_logs(limit=1, after=datetime.now() - timedelta(seconds=3), action=discord.AuditLogAction.kick)]
        if audit_log:
            
            if member.guild.id not in bot.cache.limits['kicks']:
                bot.cache.limits['kicks'][member.guild.id] = 0

            bot.cache.limits['kicks'][member.guild.id] += 1

            audit_log = audit_log[0]
            await bot.db.execute(
                'INSERT INTO moderation_history (guild_id, user_id, action, moderator_id, reason, timestamp) VALUES (%s, %s, %s, %s, %s, %s)',
                member.guild.id, member.id, 'kick', audit_log.user.id, audit_log.reason or 'N/A', int(datetime.now().timestamp())
            )

    for role in member.roles:
        if role.id not in set(await bot.db.fetch('SELECT role FROM restore WHERE guild_id = %s AND user_id = %s', member.guild.id, member.id)):
            await bot.db.execute(
                'INSERT INTO restore (guild_id, user_id, role) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE role = VALUES(role)', member.guild.id, member.id, role.id
            )
        


@bot.event
async def on_guild_join(guild: discord.Guild):

    bot.cache.event_triggers['guild_join'] += 1


@bot.event
async def on_guild_remove(guild: discord.Guild):

    bot.cache.event_triggers['guild_remove'] += 1


@bot.event
async def on_member_ban(guild: discord.Guild, user: Union[discord.Member, discord.User]):

    if isinstance(user, discord.User) or user.bot:
        return

    bot.cache.event_triggers['member_ban'] += 1

    if guild.id not in bot.cache.limits['bans']:
        bot.cache.limits['bans'][guild.id] = 0

    if 20 >= bot.cache.limits['bans'][guild.id]:
        try:
            await guild.unban(self.bot.get_user(user.id), reason=f'{self.bot.user.name.lower()} warden: ban limit exceeded')
        except:
            pass

    bot.cache.limits['bans'][guild.id] += 1

    if guild.me.guild_permissions.view_audit_log:
        audit_log = [entry async for entry in guild.audit_logs(limit=1, after=datetime.now() - timedelta(seconds=3), action=discord.AuditLogAction.ban)]
        if audit_log:

            audit_log = audit_log[0]
            await bot.db.execute(
                'INSERT INTO moderation_history (guild_id, user_id, action, moderator_id, reason, timestamp) VALUES (%s, %s, %s, %s, %s, %s)',
                guild.id, user.id, 'ban', audit_log.user.id, audit_log.reason or 'N/A', int(datetime.now().timestamp())
            )

    for role in user.roles:
        if role.id not in set(await bot.db.fetch('SELECT role FROM restore WHERE guild_id = %s AND user_id = %s', guild.id, user.id)):
            await bot.db.execute('INSERT INTO restore (guild_id, user_id, role) VALUES (%s, %s, %s)', guild.id, user.id, role.id)


@bot.event
async def on_member_unban(guild: discord.Guild, user: discord.User):

    if user.bot:
        return

    bot.cache.event_triggers['member_unban'] += 1


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    
    if before.timed_out_until != after.timed_out_until:
        if before.guild.me.guild_permissions.view_audit_log:
            audit_log = [entry async for entry in before.guild.audit_logs(limit=1, after=datetime.now() - timedelta(seconds=3), action=discord.AuditLogAction.member_update)]
            
            if audit_log:
                audit_log = audit_log[0]
                await bot.db.execute(
                    'INSERT INTO moderation_history (guild_id, user_id, action, moderator_id, reason, timestamp) VALUES (%s, %s, %s, %s, %s, %s)',
                    before.guild.id, before.id, 'mute', audit_log.user.id, audit_log.reason or 'N/A', int(datetime.now().timestamp())
                )


# checks


@bot.check
async def cooldown_check(ctx: Context) -> bool:

    bucket = ctx.bot.global_cd.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()

    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.member)

    return True


@bot.check
async def spam_check(ctx: Context) -> bool:

    bucket = ctx.bot.spam_cd.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()

    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.member)

    return True


@bot.check
async def warden_check(ctx: Context) -> bool:
    
    if ctx.command.name == 'ban':
        if 20 <= ctx.bot.cache.limits['bans'].get(ctx.guild.id, 0):
            await ctx.send_error('cannot **ban** any members; ban limit has been exceeded')
            return False

    elif ctx.command.name == 'kick':
        if 20 <= ctx.bot.cache.limits['kicks'].get(ctx.guild.id, 0):
            await ctx.send_error('cannot **kick** any members; kick limit has been exceeded')
            return False

    else:
        return True
    
    return True


@bot.check
async def blacklist_check(ctx: Context) -> bool:

    if ctx.author.id in ctx.bot.cache.global_bl['users'] or ctx.guild.id in ctx.bot.cache.global_bl['guilds']:
        return False

    return True


@bot.check
async def permission_check(ctx: Context) -> bool:

    if ctx.channel.permissions_for(ctx.guild.me).send_messages is False or ctx.channel.permissions_for(ctx.guild.me).embed_links is False:
        return False
        
    return True


@bot.check
async def privacy_check(ctx: Context) -> bool:

    if ctx.bot.cache.nodata.get(ctx.author.id) is None:

        message = await ctx.send_error(f"do you **agree** to vile's [**privacy policy**]({ctx.bot.privacy_policy})?")
        conf = await confirmation.confirm(ctx, message)
        if conf is True:
            await ctx.bot.db.execute('INSERT INTO nodata (user_id, data) VALUES (%s, 1)', ctx.author.id)
            ctx.bot.cache.nodata[ctx.author.id] = 1
            return True
        
        elif conf is False:
            await ctx.bot.db.execute('INSERT INTO nodata (user_id, data) VALUES (%s, 0)', ctx.author.id)
            ctx.bot.cache.nodata[ctx.author.id] = 0
            return False

    if bot.cache.nodata[ctx.author.id] == 0:
        return False

    if bot.cache.nodata[ctx.author.id] == 1:
        return True


@bot.check
async def disabled_check(ctx: Context) -> bool:

    if ctx.command.name in bot.cache.disabled_commands.get(ctx.guild.id, list()):
        await ctx.send_error('that command is **disabled** in this server')
        return False

    return True


@bot.before_invoke
async def chunk_guild(ctx: Context) -> None:
    
    if ctx.guild and ctx.guild.chunked is False:
        await ctx.guild.chunk(cache=True)


# loops


@tasks.loop(minutes=5)
async def subtract_warden_threshold():
        
    for guild_id in bot.cache.limits['bans']:
        if bot.cache.limits['bans'][guild_id] > 0:
            bot.cache.limits['bans'][guild_id] -= 1

    for guild_id in bot.cache.limits['kicks']:
        if bot.cache.limits['kicks'][guild_id] > 0:
            bot.cache.limits['kicks'][guild_id] -= 1


@tasks.loop(minutes=5)
async def subtract_dm_threshold():

    for guild_id in bot.cache.limits['dms']:
        if bot.cache.limits['dms'][guild_id] > 0:
            bot.cache.limits['dms'][guild_id] -= 1

    for guild_id in bot.cache.limits['dms']:
        if bot.cache.limits['dms'][guild_id] > 0:
            bot.cache.limits['dms'][guild_id] -= 1


@tasks.loop(minutes=1)
async def subtract_join_threshold():

    for guild_id in bot.cache.antiraid_trigger:
        if bot.cache.antiraid_trigger[guild_id] > 0:
            bot.cache.antiraid_trigger[guild_id] -= 1


@tasks.loop(minutes=10)
async def dump_database():
    await asyncio.create_subprocess_shell(f'{os.getcwd()}/dump.sh', stdout=subprocess.PIPE, stderr=subprocess.PIPE)


if __name__ == '__main__':
    bot.run(config.authorization.vile_token)
