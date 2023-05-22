import discord, typing, time, arrow, psutil, copy, aiohttp, json
from datetime import datetime
from typing import Optional, Union
from utilities import utils, confirmation
from utilities.baseclass import Vile
from utilities.context import Context
from utilities.advancedutils import parse_timespan
from discord.ext import commands, tasks


class Anti_Nuke(commands.Cog):
    def __init__(self, bot: Vile) -> None:
        self.bot = bot


    # @commands.group(
    #     name='antinuke',
    #     aliases=['an', 'aw', 'antiskid'],
    #     description='manage the anti-nuke module',
    #     brief='antinuke <sub command>',
    #     help='antinuke setup',
    #     extras={'permissions': 'server owner or trusted admin'},
    #     invoke_without_command=True
    # )
    # async def antinuke(self, ctx: Context):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     return await ctx.send_help()

    
    # @antinuke.command(
    #     name='setup',
    #     description='setup the default antinuke configurations',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_setup(self, ctx: Context):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if await self.bot.db.fetchrow('SELECT * FROM antinuke WHERE guild_id = %s', ctx.guild.id) or await self.bot.db.fetchrow('SELECT * FROM punishment WHERE guild_id = %s', ctx.guild.id):
    #         return await ctx.send_error('antinuke is already **set up** in this server')

    #     to_delete = await ctx.send_success('setting up **antinuke** in this server')

    #     async with ctx.handle_response():
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 1, 1, 1, 1, 1, 1, 1)', ctx.guild.id
    #         )
    #         self.bot.cache.antinuke[ctx.guild.id] = {'ban': 1, 'kick': 1, 'rolecreate': 1, 'roledelete': 1, 'channelcreate': 1, 'channeldelete': 1, 'webhook': 1}
            
    #         await self.bot.db.execute(
    #             'INSERT INTO punishment (guild_id, punishment) VALUES (%s, %s)', ctx.guild.id, 'stripstaff'
    #         )
    #         self.bot.cache.punishment[ctx.guild.id] = 'stripstaff'

    #         await to_delete.delete()
    #         return await ctx.send_success('successfully **set up** antinuke in this server')


    # @antinuke.command(
    #     name='punishment',
    #     description='set the punishment for possible nukes',
    #     brief='antinuke punishment <punishment>',
    #     help='antinuke punishment stripstaff'
    # )
    # async def antinuke_punishment(self, ctx: Context, punishment: str):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if punishment not in ['stripstaff', 'striproles', 'ban', 'kick']:
    #         return await ctx.send_error('please provide one of the following: **stripstaff**, **striproles**, **ban**, **kick**')

    #     await self.bot.db.execute(
    #         'INSERT INTO punishment (guild_id, punishment) VALUES (%s, %s) ON DUPLICATE KEY UPDATE punishment = VALUES(punishment)', ctx.guild.id, punishment
    #     )
    #     self.bot.cache.punishment[ctx.guild.id] = punishment

    #     return await ctx.send_success(f'successfully **binded** the antinuke punishment to `{punishment}`')


    # @antinuke.command(
    #     name='ban',
    #     description='prevent unwhitelisted members from banning people',
    #     brief='antinuke ban <state>',
    #     help='antinuke ban true',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_ban(self, ctx: Context, state: str):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if state == 'true':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 1, 0, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE ban = VALUES(ban)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['ban'] = 1
    #         return await ctx.send_success('anti ban has been **enabled**')

    #     elif state == 'false':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE ban = VALUES(ban)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['ban'] = 0
    #         return await ctx.send_success('anti ban has been **disabled**')
        
    #     else:
    #         return await ctx.send_error('please provide a **valid** state')


    # @antinuke.command(
    #     name='kick',
    #     description='prevent unwhitelisted members from kick people',
    #     brief='antinuke kick <state>',
    #     help='antinuke kick true',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_kick(self, ctx: Context, state: str):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if state == 'true':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 1, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE kick = VALUES(kick)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['kick'] = 1
    #         return await ctx.send_success('anti kick has been **enabled**')

    #     elif state == 'false':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE kick = VALUES(kick)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['kick'] = 0
    #         return await ctx.send_success('anti kick has been **disabled**')
        
    #     else:
    #         return await ctx.send_error('please provide a **valid** state')


    # @antinuke.command(
    #     name='rolecreate',
    #     description='prevent unwhitelisted members from creating roles',
    #     brief='antinuke rolecreate <state>',
    #     help='antinuke rolecreate true',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_rolecreate(self, ctx: Context, state: str):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if state == 'true':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 1, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE rolecreate = VALUES(rolecreate)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['rolecreate'] = 1
    #         return await ctx.send_success('anti role create has been **enabled**')

    #     elif state == 'false':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE rolecreate = VALUES(rolecreate)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['rolecreate'] = 0
    #         return await ctx.send_success('anti role create has been **disabled**')
        
    #     else:
    #         return await ctx.send_error('please provide a **valid** state')


    # @antinuke.command(
    #     name='roledelete',
    #     description='prevent unwhitelisted members from deleting roles',
    #     brief='antinuke roledelete <state>',
    #     help='antinuke roledelete true',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_roledelete(self, ctx: Context, state: str):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if state == 'true':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 1, 0, 0, 0) ON DUPLCIATE KEY UPDATE roledelete = VALUES(roledelete)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['roledelete'] = 1
    #         return await ctx.send_success('anti role delete has been **enabled**')

    #     elif state == 'false':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE roledelete = VALUES(roledelete)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['roledelete'] = 0
    #         return await ctx.send_success('anti role delete has been **disabled**')
        
    #     else:
    #         return await ctx.send_error('please provide a **valid** state')


    # @antinuke.command(
    #     name='channelcreate',
    #     description='prevent unwhitelisted members from creating channels',
    #     brief='antinuke channelcreate <state>',
    #     help='antinuke channelcreate true',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_channelcreate(self, ctx: Context, state: str):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if state == 'true':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 1, 0, 0) ON DUPLCIATE KEY UPDATE channelcreate = VALUES(channelcreate)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['channelcreate'] = 1
    #         return await ctx.send_success('anti channel create has been **enabled**')

    #     elif state == 'false':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE channelcreate = VALUES(channelcreate)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['channelcreate'] = 0
    #         return await ctx.send_success('anti channel create has been **disabled**')
        
    #     else:
    #         return await ctx.send_error('please provide a **valid** state')


    # @antinuke.command(
    #     name='channeldelete',
    #     description='prevent unwhitelisted members from deleting channels',
    #     brief='antinuke channeldelete <state>',
    #     help='antinuke channelcreate true',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_channeldelete(self, ctx: Context, state: str):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if state == 'true':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 1, 0) ON DUPLCIATE KEY UPDATE channeldelete = VALUES(channeldelete)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['channeldelete'] = 1
    #         return await ctx.send_success('anti channel delete has been **enabled**')

    #     elif state == 'false':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE channeldelete = VALUES(channeldelete)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['channeldelete'] = 0
    #         return await ctx.send_success('anti channel delete has been **disabled**')
        
    #     else:
    #         return await ctx.send_error('please provide a **valid** state')


    # @antinuke.command(
    #     name='webhook',
    #     description='prevent unwhitelisted members from creating/deleting webhooks',
    #     brief='antinuke webhook <state>',
    #     help='antinuke webhook true',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_webhook(self, ctx: Context, state: str):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if state == 'true':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 0, 1) ON DUPLCIATE KEY UPDATE webhook = VALUES(webhook)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['webhook'] = 1
    #         return await ctx.send_success('anti webhook has been **enabled**')

    #     elif state == 'false':
    #         await self.bot.db.execute(
    #             'INSERT INTO antinuke (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) VALUES (%s, 0, 0, 0, 0, 0, 0, 0) ON DUPLCIATE KEY UPDATE webhook = VALUES(webhook)', ctx.guild.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antinuke:
    #             self.bot.cache.antinuke[ctx.guild.id] = {'ban': 0, 'kick': 0, 'rolecreate': 0, 'roledelete': 0, 'channelcreate': 0, 'channeldelete': 0, 'webhook': 0}

    #         self.bot.cache.antinuke[ctx.guild.id]['webhook'] = 0
    #         return await ctx.send_success('anti webhook has been **disabled**')
        
    #     else:
    #         return await ctx.send_error('please provide a **valid** state')


    # @antinuke.command(
    #     name='whitelist',
    #     aliases=['exempt'],
    #     description='whitelist users from being punished',
    #     brief='antinuke whitelist <user>',
    #     help='antinuke whitelist @glory#0007',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_whitelist(self, ctx: Context, member: discord.Member):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')
        
    #     if member.id in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_whitelist WHERE guild_id = %s', ctx.guild.id)):
    #         await self.bot.db.execute(
    #             'DELETE FROM antinuke_whitelist WHERE guild_id = %s AND user_id = %s', ctx.guild.id, member.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.antiraid_whitelist:
    #             self.bot.cache.whitelist[ctx.guild.id] = []

    #         try:
    #             self.bot.cache.whitelist[ctx.guild.id].remove(member.id)
    #         except:
    #             pass
    #         return await ctx.send_success(f'successfully **unwhitelisted** {member.mention}')

    #     await self.bot.db.execute(
    #         'INSERT INTO antinuke_whitelist (guild_id, user_id) VALUES (%s, %s)', ctx.guild.id, member.id
    #     )
    #     if ctx.guild.id not in self.bot.cache.whitelist:
    #         self.bot.cache.whitelist[ctx.guild.id] = []

    #     self.bot.cache.whitelist[ctx.guild.id].append(member.id)
    #     return await ctx.send_success(f'successfully **whitelisted** {member.mention}')


    # @antinuke.command(
    #     name='admin',
    #     aliases=['trust'],
    #     description='allow a user to edit the antinuke configuration',
    #     brief='antinuke admin <user>',
    #     help='antinuke admin @glory#0007',
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_admin(self, ctx: Context, member: discord.Member):

    #     if ctx.author.id != ctx.guild.owner_id:
    #         return await ctx.send_error('command restricted to **server owners**')
        
    #     if member.id in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         await self.bot.db.execute(
    #             'DELETE FROM antinuke_admins WHERE guild_id = %s AND user_id = %s', ctx.guild.id, member.id
    #         )
    #         if ctx.guild.id not in self.bot.cache.admin:
    #             self.bot.cache.admin[ctx.guild.id] = []

    #         try:
    #             self.bot.cache.admin[ctx.guild.id].remove(member.id)
    #         except:
    #             pass
    #         return await ctx.send_success(f'successfully **untrusted** {member.mention}')

    #     await self.bot.db.execute(
    #         'INSERT INTO antinuke_admins (guild_id, user_id) VALUES (%s, %s)', ctx.guild.id, member.id
    #     )
    #     if ctx.guild.id not in self.bot.cache.admin:
    #         self.bot.cache.admin[ctx.guild.id] = []

    #     self.bot.cache.admin[ctx.guild.id].append(member.id)
    #     return await ctx.send_success(f'successfully **trusted** {member.mention}')


    # @antinuke.command(
    #     name='whitelisted',
    #     description='see every whitelisted user',
    # )
    # async def antinuke_whitelisted(self, ctx: Context):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if not await self.bot.db.fetch('SELECT user_id FROM antinuke_whitelist WHERE guild_id = %s', ctx.guild.id):
    #         return await ctx.send_error('there are no **whitelisted** users in this server')

    #     embed = discord.Embed(
    #         color=self.bot.color,
    #         title=f'Whitelisted Users in {ctx.guild.name}',
    #         description=list()
    #     )

    #     for user_id in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_whitelist WHERE guild_id = %s', ctx.guild.id)):
    #         if self.bot.get_user(user_id) is not None:
    #             user = self.bot.get_user(user_id)
    #             embed.description.append(f'{user.mention}: **{user}** ( `{user.id}` )')

    #     return await ctx.paginate(embed)


    # @antinuke.command(
    #     name='admins',
    #     aliases=['trusted'],
    #     description='see every trusted user',
    # )
    # async def antinuke_admins(self, ctx: Context):

    #     if ctx.author.id != ctx.guild.owner_id:
    #         return await ctx.send_error('command restricted to **server owners**')

    #     if not set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('there are no **trusted** users in this server')

    #     embed = discord.Embed(
    #         color=self.bot.color,
    #         title=f'Trusted Users in {ctx.guild.name}',
    #         description=list()
    #     )

    #     for user_id in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         if self.bot.get_user(user_id) is not None:
    #             user = self.bot.get_user(user_id)
    #             embed.description.append(f'{user.mention}: **{user}** ( `{user.id}` )')

    #     return await ctx.paginate(embed)


    # @antinuke.command(
    #     name='settings',
    #     aliases=['conf', 'config', 'cfg', 'configuration'],
    #     description="view the server's current anti-nuke configuration",
    #     extras={'permissions': 'administrator'}
    # )
    # @commands.has_permissions(administrator=True)
    # async def antinuke_settings(self, ctx: Context):

    #     if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in set(await self.bot.db.fetch('SELECT user_id FROM antinuke_admins WHERE guild_id = %s', ctx.guild.id)):
    #         return await ctx.send_error('command restricted to **server owners** and **trusted admins**')

    #     if not await self.bot.db.fetchrow('SELECT * FROM antinuke WHERE guild_id = %s', ctx.guild.id):
    #         return await ctx.send_error('the anti-nuke module is not **set up** in this server')

    #     ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook = await self.bot.db.fetchrow('SELECT ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook FROM antinuke WHERE guild_id = %s', ctx.guild.id)
    #     punishment = await self.bot.db.fetchval('SELECT punishment FROM punishment WHERE guild_id = %s', ctx.guild.id)

    #     embed = discord.Embed(color=self.bot.color, title='Anti-Nuke Configuration', timestamp=datetime.now())    
    #     embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
    #     embed.add_field(name=f'{self.bot.dash} Anti Member Ban', value=f'{self.bot.reply} status: {self.bot.enabled if ban else self.bot.disabled}')
    #     embed.add_field(name=f'{self.bot.dash} Anti Member Kick', value=f'{self.bot.reply} status: {self.bot.enabled if kick else self.bot.disabled}')
    #     embed.add_field(name=f'{self.bot.dash} Anti Role Create', value=f'{self.bot.reply} status: {self.bot.enabled if rolecreate else self.bot.disabled}')
    #     embed.add_field(name=f'{self.bot.dash} Anti Role Delete', value=f'{self.bot.reply} status: {self.bot.enabled if roledelete else self.bot.disabled}')
    #     embed.add_field(name=f'{self.bot.dash} Anti Channel Create', value=f'{self.bot.reply} status: {self.bot.enabled if channelcreate else self.bot.disabled}')
    #     embed.add_field(name=f'{self.bot.dash} Anti Channel Delete', value=f'{self.bot.reply} status: {self.bot.enabled if channeldelete else self.bot.disabled}')
    #     embed.add_field(name=f'{self.bot.dash} Anti Webhook Create', value=f'{self.bot.reply} status: {self.bot.enabled if webhook else self.bot.disabled}')
    #     embed.add_field(name=f'{self.bot.dash} Anti Webhook Delete', value=f'{self.bot.reply} status: {self.bot.enabled if webhook else self.bot.disabled}')
    #     embed.add_field(name=f'{self.bot.dash} Anti Punishment', value=f'{self.bot.reply} {punishment}')
        
    #     return await ctx.reply(embed=embed)


    @commands.group(
        name='antiraid',
        aliases=['raid'],
        description='manage the antiraid module',
        brief='antiraid <sub command>',
        help='antiraid setup',
        extras={'permissions': 'administrator'},
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def antiraid(self, ctx: Context):
        return await ctx.send_help()

    
    @antiraid.command(
        name='setup',
        description='setup the default antiraid configurations',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_setup(self, ctx: Context):

        if await self.bot.db.fetchrow('SELECT * FROM antiraid WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('antiraid is already **set up** in this server')

        to_delete = await ctx.send_success('setting up **antiraid** in this server')

        async with ctx.handle_response():
            await self.bot.db.execute(
                'INSERT INTO antiraid (guild_id, avatar, joins, age) VALUES (%s, 1, 5, 14)',
                ctx.guild.id
            )
            self.bot.cache.antiraid[ctx.guild.id] = {'avatar': 1, 'joins': 5, 'age': 14}

            await to_delete.delete()
            return await ctx.send_success('successfully **set up** antiraid in this server')

    
    @antiraid.command(
        name='ban',
        description='ban all members who joined within the provided timespan',
        brief='raid ban <time d/h/m/s>',
        help='raid ban 10m',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_ban(self, ctx: Context, timee: str):

        try:
            timee = parse_timespan(timee)
        except:
            return await ctx.send_error('please provide a **valid** time')

        if timee > 21600:
            return await ctx.send_error("you can't ban people who joined more than **6 hours** ago")

        to_ban = [m for m in ctx.guild.members if time.time() - m.joined_at.timestamp() < timee]
        if len(to_ban) == 0:
            return await ctx.send_error('there is no one to ban')

        msg = await ctx.send_error(f'are you **sure** you want to ban {len(to_ban):,} members?')
        conf = await confirmation.confirm(ctx, msg)
        num = 0

        if conf is True:
            for m in [m for m in ctx.guild.members if time.time() - m.joined_at.timestamp() < timee]:
                try:
                    await m.ban(reason=f'antiraid ban: used by {ctx.author}')
                    num += 1
                except:
                    continue

            return await ctx.send_success(f'successfully banned **{num}** members who joined less than **{utils.fmtseconds(timee)}** ago')

        return await ctx.send_error('antiraid ban has been **cancelled**')


    @antiraid.command(
        name='kick',
        description='kick all members who joined within the provided timespan',
        brief='raid kick <time d/h/m/s>',
        help='raid kick 10m',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_kick(self, ctx: Context, timee: str):

        try:
            timee = parse_timespan(timee)
        except:
            return await ctx.send_error('please provide a **valid** time')

        if timee > 21600:
            return await ctx.send_error("you can't kick people who joined more than **6 hours** ago")

        to_kick = [m for m in ctx.guild.members if time.time() - m.joined_at.timestamp() < timee]
        if len(to_kick) == 0:
            return await ctx.send_error('there is no one to kick')

        msg = await ctx.send_error(f'are you **sure** you want to kick {len(to_kick):,} members?')
        conf = await confirmation.confirm(ctx, msg)
        num = 0

        if conf is True:
            for m in [m for m in ctx.guild.members if time.time() - m.joined_at.timestamp() < timee]:
                try:
                    await m.kick(reason=f'antiraid kick: used by {ctx.author}')
                    num += 1
                except:
                    continue

            return await ctx.send_success(f'successfully kicked **{num}** members who joined less than **{utils.fmtseconds(timee)}** ago')

        return await ctx.send_error('antiraid kick has been **cancelled**')


    @antiraid.command(
        name='defaultavatar',
        aliases=['defaultpfp'],
        description='kick new members without avatars',
        brief='antiraid defaultavatar <state>',
        help='antiraid defaultavatar true',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_defaultavatar(self, ctx: Context, state: str):

        if state == 'true':
            await self.bot.db.execute(
                'INSERT INTO antiraid (guild_id, avatar, joins, age) VALUES (%s, 1, 0, 0) ON DUPLICATE KEY UPDATE avatar = 1', ctx.guild.id
            )
            if ctx.guild.id not in self.bot.cache.antiraid:
                self.bot.cache.antiraid[ctx.guild.id] = {'avatar': 0, 'joins': 0, 'age': 0}

            self.bot.cache.antiraid[ctx.guild.id]['avatar'] = 1
            return await ctx.send_success('antiraid avatar has been **enabled**')

        elif state == 'false':
            await self.bot.db.execute(
                'INSERT INTO antiraid (guild_id, avatar, joins, age) VALUES (%s, 0, 0, 0) ON DUPLICATE KEY UPDATE avatar = 0', ctx.guild.id
            )
            if ctx.guild.id not in self.bot.cache.antiraid:
                self.bot.cache.antiraid[ctx.guild.id] = {'avatar': 0, 'joins': 0, 'age': 0}

            self.bot.cache.antiraid[ctx.guild.id]['avatar'] = 0
            return await ctx.send_success('antiraid avatar has been **disabled**')
        
        else:
            return await ctx.send_error('please provide a **valid** state')


    @antiraid.command(
        name='massjoin',
        aliases=['join'],
        description='set a threshold on joins',
        brief='antiraid massjoin <threshold>',
        help='antiraid massjoin 5',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_massjoin(self, ctx: Context, threshold: int):

        await self.bot.db.execute(
            'INSERT INTO antiraid (guild_id, avatar, joins, age) VALUES (%s, 0, %s, 0) ON DUPLICATE KEY UPDATE joins = VALUES(joins)', ctx.guild.id, threshold
        )
        if ctx.guild.id not in self.bot.cache.antiraid:
            self.bot.cache.antiraid[ctx.guild.id] = {'avatar': 0, 'joins': 0, 'age': 0}

        self.bot.cache.antiraid[ctx.guild.id]['joins'] = threshold
        return await ctx.send_success(f'successfully **binded** the join threshold to **{threshold}/60s**')


    @antiraid.command(
        name='age',
        description='kick newly created accounts',
        brief='antiraid age <age in days>',
        help='antiraid age 14',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_age(self, ctx: Context, age: int):

        await self.bot.db.execute(
            'INSERT INTO antiraid (guild_id, avatar, joins, age) VALUES (%s, 0, 0, %s) ON DUPLICATE KEY UPDATE age = VALUES(age)', ctx.guild.id, age
        )
        if ctx.guild.id not in self.bot.cache.antiraid:
            self.bot.cache.antiraid[ctx.guild.id] = {'avatar': 0, 'joins': 0, 'age': 0}

        self.bot.cache.antiraid[ctx.guild.id]['age'] = age
        return await ctx.send_success(f'successfully **binded** the age limit to **{age}**')


    @antiraid.command(
        name='clear',
        aliases=['c'],
        description='clear the antiraid configuration',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM antiraid WHERE guild_id = %s', ctx.guild.id)
        await self.bot.db.execute('DELETE FROM antiraid_whitelist WHERE guild_id = %s', ctx.guild.id)
        await self.bot.cache.cache_antiraid()

        return await ctx.send_error('successfully **cleared** the antiraid configuration')


    @antiraid.command(
        name='whitelist',
        aliases=['exempt'],
        description='whitelist users from being punished',
        brief='antiraid whitelist <user>',
        help='antiraid whitelist @glory#0007',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_whitelist(self, ctx: Context, user: Union[discord.Member, discord.User]):
        
        if await ctx.can_moderate(user, 'whitelist') is not None:
            return

        if user.id in set(await self.bot.db.fetch('SELECT user_id FROM antiraid_whitelist WHERE guild_id = %s', ctx.guild.id)):
            await self.bot.db.execute(
                'DELETE FROM antiraid_whitelist WHERE guild_id = %s AND user_id = %s', ctx.guild.id, user.id
            )
            if ctx.guild.id not in self.bot.cache.antiraid_whitelist:
                self.bot.cache.antiraid_whitelist[ctx.guild.id] = []

            try:
                self.bot.cache.antiraid_whitelist[ctx.guild.id].remove(user.id)
            except:
                pass
            return await ctx.send_success(f'successfully **unwhitelisted** {user.mention}')

        await self.bot.db.execute(
            'INSERT INTO antiraid_whitelist (guild_id, user_id) VALUES (%s, %s)', ctx.guild.id, user.id
        )
        if ctx.guild.id not in self.bot.cache.antiraid_whitelist:
            self.bot.cache.antiraid_whitelist[ctx.guild.id] = []

        self.bot.cache.antiraid_whitelist[ctx.guild.id].append(user.id)
        return await ctx.send_success(f'successfully **whitelisted** {user.mention}')


    @antiraid.command(
        name='whitelisted',
        description='see every whitelisted user',
    )
    async def antiraid_whitelisted(self, ctx: Context):

        if not await self.bot.db.fetch('SELECT user_id FROM antiraid_whitelist WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('there are no **whitelisted** users in this server')

        embed = discord.Embed(
            color=self.bot.color,
            title=f'Whitelisted Users in {ctx.guild.name}',
            description=list()
        )

        for user_id in set(await self.bot.db.fetch('SELECT user_id FROM antiraid_whitelist WHERE guild_id = %s', ctx.guild.id)):
            if self.bot.get_user(user_id) is not None:
                user = self.bot.get_user(user_id)
                embed.description.append(f'{user.mention}: **{user}** ( `{user.id}` )')

        return await ctx.paginate(embed)


    @antiraid.command(
        name='settings',
        aliases=['conf', 'config', 'cfg', 'configuration'],
        description="view the server's current anti-raid configuration",
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def antiraid_settings(self, ctx: Context):

        if not await self.bot.db.fetchrow('SELECT * FROM antiraid WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('the anti-raid module is not **set up** in this server')

        avatar, joins, age = await self.bot.db.fetchrow('SELECT avatar, joins, age FROM antiraid WHERE guild_id = %s', ctx.guild.id)

        embed = discord.Embed(color=self.bot.color, title='Anti-Raid Configuration', timestamp=datetime.now())    
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.add_field(name=f'{self.bot.dash} Avatar', value=f"{self.bot.reply} {'true' if avatar else 'false'}")
        embed.add_field(name=f'{self.bot.dash} Joins', value=f'{self.bot.reply} {joins}/60s')
        embed.add_field(name=f'{self.bot.dash} Age', value=f'{self.bot.reply} {age} days')
        
        return await ctx.reply(embed=embed)


    @commands.group(
        name='fakepermissions',
        aliases=['fp', 'fakepermission', 'fakeperms'],
        description="manage the server's fake permissions",
        brief='fakepermissions <sub command>',
        help='fakepermissions add @mod ban_members',
        extras={'permissions': 'administrator'},
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def fakepermissions(self, ctx: Context):
        return await ctx.send_help()
        
        
    @fakepermissions.command(
        name='add',
        description='add an fake permission to a role',
        brief='fakepermissions add <role> <permission>',
        help='fakepermissions add ban pack',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def fakepermissions_add(self, ctx: Context, role: Union[discord.Role, str], permission: str):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')
        
        if permission not in set(discord.Permissions.VALID_FLAGS):
            return await ctx.send_error('please provide a **valid** permission')
            
        if permission in set(await self.bot.db.fetch('SELECT permission FROM fake_permissions WHERE guild_id = %s AND role_id = %s', ctx.guild.id, role.id)):
            return await ctx.send_error(f'that role **already has** the fake permission `{permission}`')
            
        if permission == 'administrator':
            return await ctx.send_error('**cannot assign** the administrator permission for safety reasons')
            
        await self.bot.db.execute('INSERT INTO fake_permissions (guild_id, role_id, permission) VALUES (%s, %s, %s)', ctx.guild.id, role.id, permission)
        if ctx.guild.id not in self.bot.cache.fakepermissions:
            self.bot.cache.fakepermissions[ctx.guild.id] = dict()
        
        if role.id not in self.bot.cache.fakepermissions[ctx.guild.id]:
            self.bot.cache.fakepermissions[ctx.guild.id][role.id] = set()
            
        self.bot.cache.fakepermissions[ctx.guild.id][role.id].add(permission)
        return await ctx.send_success(f'successfully **binded** the `{permission}` permission to {role.mention}')
        
        
    @fakepermissions.command(
        name='remove',
        description='remove a fake permission from a role',
        brief='fakepermissions remove <role> <permission>',
        help='fakepermissions remove @mod ban_members',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def fakepermissions_remove(self, ctx: Context, role: Union[discord.Role, str], permission: str):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')
        
        if permission not in set(discord.Permissions.VALID_FLAGS):
            return await ctx.send_error('please provide a **valid** permission')
            
        if permission not in set(await self.bot.db.fetch('SELECT permission FROM fake_permissions WHERE guild_id = %s AND role_id = %s', ctx.guild.id, role.id)):
            return await ctx.send_error(f'that role **does not have** the fake permission `{permission}')
            
        await self.bot.db.execute('DELETE FROM fake_permissions WHERE guild_id = %s AND role_id = %s AND permission = %s', ctx.guild.id, role.id, permission)
        await self.bot.cache.cache_fakepermissions()

        return await ctx.send_success(f'successfully **removed** the `{permission}` permission from {role.mention}')
        
        
    @fakepermissions.command(
        name='clear',
        description='clear every fake permission in this server',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def fakepermissions_clear(self, ctx: Context):
        
        await self.bot.db.execute('DELETE FROM fake_permissions WHERE guild_id = %s', ctx.guild.id)
        await self.bot.cache.cache_fakepermissions()
        
        return await ctx.send_success('successfully **cleared** all fake permissions in this server')
        
        
    @fakepermissions.command(
        name='list',
        aliases=['show'],
        description='view every fake permission in this server',
        extras={'permissions': 'administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def fakepermissions_list(self, ctx: Context):
        
        if not await self.bot.db.fetch('SELECT permission FROM fake_permissions WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **fake permissions** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Fake Permissions in {ctx.guild.name}',
            description=list()
        )
        
        for role_id in set(await self.bot.db.fetch('SELECT role_id FROM fake_permissions WHERE guild_id = %s', ctx.guild.id)):
            embed.description.append(f"{ctx.guild.get_role(role_id).mention}\n{self.bot.reply} **permissions:** {', '.join(await self.bot.db.fetch('SELECT permission FROM fake_permissions WHERE guild_id = %s AND role_id = %s', ctx.guild.id, role_id))}")
                
        return await ctx.paginate(embed)


async def setup(bot: Vile):
    await bot.add_cog(Anti_Nuke(bot))