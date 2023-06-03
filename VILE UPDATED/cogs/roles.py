import discord, typing, time, arrow, psutil, copy, aiohttp
from datetime import datetime
from typing import Optional, Union
from utilities import utils
from utilities.utils import aiter
from utilities.baseclass import Vile
from utilities.context import Context
from utilities.tasks import submit
from discord.ext import commands


class Roles(commands.Cog):
    def __init__(self, bot: Vile) -> None:
        self.bot = bot


    @commands.group(
        name='role',
        aliases=['r'],
        description='add/remove a role from a user',
        brief='role <user> <role>',
        help='role @glory#0007 star',
        invoke_without_command=True,
        extras={'permissions': 'manage roles'}
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx: Context, member: discord.Member, *, role: Union[discord.Role, str]):
            
        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if await ctx.can_moderate(member, 'role') is not None:
            return

        if role.is_dangerous() is True:
            return await ctx.send_error('that role has **dangerous** permissions')
                
        if member.get_role(role.id) is None:
            await member.add_roles(role, reason=f'role: used by {ctx.author}')
            return await ctx.send_success(f'updated {member.mention}, **added** +{role.mention}')

        elif member.get_role(role.id) is not None:
            await member.remove_roles(role, reason=f'role: used by {ctx.author}')
            return await ctx.send_success(f'updated {member.mention}, **removed** -{role.mention}')
                
    @role.command(
        name='create',
        aliases=['add', 'make'],
        description='create a role using the bot',
        brief='role create <hex> <name>',
        help='role create #b1aad8 mommy gwen',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_create(self, ctx: Context, color: str, *, name: str):

        role = await ctx.guild.create_role(
            name=name, color=int(color.strip('#'), 16)
        )
        await ctx.send_success(f'successfully **created** {role.name}')


    @role.command(
        name='delete',
        aliases=['del', 'd'],
        description='delete a role using the bot',
        brief='role delete <role>',
        help='role delete img',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_delete(self, ctx: Context, *, role: Union[discord.Role, str]):
        
        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't **delete** that role")

            
        await role.delete(reason=f'role delete: used by {ctx.author}')
        return await ctx.send_success(f'successfully **deleted** {role.name}')
    

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.Member, discord.User]):
        
        if isinstance(user, discord.User):
            return
            
        for role in user.roles:
            await self.bot.db.execute('INSERT INTO restore (guild_id, user_id, role) VALUES (%s, %s, %s)', user.guild.id, user.id, role.id)
            

    @role.command(
        name='restore',
        description="restore a user's role after they leave and rejoin",
        brief='role restore <user>',
        help='role restore @glory#0007',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_restore(self, ctx: Context, member: discord.Member):

        roles = await self.bot.db.fetch('SELECT role FROM restore WHERE user_id = %s AND guild_id = %s', member.id, ctx.guild.id)
        if not roles:
            return await ctx.send_error('there are no roles to **restore**')
            
        roles = [ctx.guild.get_role(role) for role in roles]
        await member.edit(roles=[role for role in roles if role and role.is_assignable() and not role.is_dangerous()])
        return await ctx.send_success(f"successfully **restored** all of {member.mention}'s roles")


    @role.command(
        name='all',
        description='role every member',
        brief='role all <role>',
        help='role all star',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_all(self, ctx: Context, *, role: Union[discord.Role, str]):
        
        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        with submit(ctx):
            async with ctx.handle_response():
                async for m in aiter([m for m in ctx.guild.members and not m.get_role(role.id)]):
                    try:
                        await m.add_roles(role, reason=f'role all: used by {ctx.author}')
                    except:
                        continue
                
            return await ctx.send_success(f'successfully added {role.mention} to all members')


    @role.command(
        name='bots',
        description='role every bot',
        brief='role bots <role>',
        help='role bots bot',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_bots(self, ctx: Context, *, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        with submit(ctx):
            async with ctx.handle_response():
                async for m in aiter([m for m in ctx.guild.members if m.bot and not m.get_role(role.id)]):
                    try:
                        await m.add_roles(role, reason=f'role bots: used by {ctx.author}')
                    except:
                        continue
                
            return await ctx.send_success(f'successfully added {role.mention} to all bots')


    @role.command(
        name='humans',
        description='role every humans',
        brief='role humans <role>',
        help='role humans member',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_humans(self, ctx: Context, *, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        with submit(ctx):
            async with ctx.handle_response():
                async for m in aiter([m for m in ctx.guild.members if not m.bot and not m.get_role(role.id)]):
                    try:
                        await m.add_roles(role, reason=f'role bots: used by {ctx.author}')
                    except:
                        continue
                
            return await ctx.send_success(f'successfully added {role.mention} to all humans')
        

    @role.group(
        name='edit',
        aliases=['update'],
        description='edit a role',
        brief='role edit <sub command>',
        help='role edit permissions admin 8',
        extras={'permissions': 'manage roles'},
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_edit(self, ctx: Context):
        return await ctx.send_help()
    

    @role_edit.command(
        name='mentionable',
        aliases=['ping', 'pingable', 'mention'],
        description='enable/disable pinging a role',
        brief='role edit mentionable <role> <state>',
        help='role edit mentionable staff true',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_edit_mentionable(self, ctx: Context, role: Union[discord.Role, str], state: str):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')
                
        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't **edit** that role")
        
        if state == 'true':
            await role.edit(mentionable=True)
            return await ctx.send_success(f'successfully **enabled** mention for {role.name}')

        elif state == 'false':
            await role.edit(mentionable=False)
            return await ctx.send_success(f'successfully **disabled** mention for {role.name}')
        else:
            await ctx.send_error('please provide a **valid** state')


    @role_edit.command(
        name='name',
        description='edit a roles name',
        brief='role edit name <role> <name>',
        help='role edit name users Users',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_edit_name(self, ctx: Context, role: Union[discord.Role, str], *, name: str):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')
                
        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't **edit** that role")
        
        if len(name) > 32:
            return await ctx.send_error('please provide a **valid** name under 32 chars')
                
        await role.edit(name=name)
        return await ctx.send_success(f'successfully edited the **name** for {role.name}')
        

    @role_edit.command(
        name='position',
        aliases=['pos'],
        description='edit a roles position',
        brief='role edit position <role> <position>',
        help='role edit position users 5',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_edit_position(self, ctx: Context, role: Union[discord.Role, str], position: int):
            
        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')
                
        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't **edit** that role")
                
        try:
            await role.edit(position=position)
        except:
            return await ctx.send_error('please provide a **valid** position')

        return await ctx.send_success(f'successfully edited the **position** for {role.name}')
        

    @role_edit.command(
        name='color',
        description='edit a roles color',
        brief='role edit color <role> <color>',
        help='role edit color users #636890',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_edit_color(self, ctx: Context, role: Union[discord.Role, str], color: str):
            
        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')
                
        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't **edit** that role")
        
        if len(color.strip('#')) > 6:
            return await ctx.send_error('please provide a **valid** color')
                
        try:
            int(color.strip('#'), 16)
        except:
            return await ctx.send_error('please provide a **valid** color')
            
        await role.edit(color=int(color.strip('#'), 16))
        return await ctx.send_success(f'successfully changed the **color** for {role.name}')
        

    @role_edit.command(
        name='permissions',
        aliases=['perms', 'perm'],
        description='edit a roles permissions',
        brief='role edit perm <role> <permission int>',
        help='role edit perm admin 8',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_edit_permissions(self, ctx: Context, role: Union[discord.Role, str], permissions: int):
            
        if isinstance(role, str):
            role = ctx.find_role(role)
            if role is None:
                return await ctx.send_error('please provide a **valid** role')
                
        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't **edit** that role")
                
        try:
            await role.edit(permissions=discord.Permissions(permissions))
        except:
            return await ctx.send_error('please provide a **valid** permission')
        
        return await ctx.send_success(f'successfully changed the **permissions** for {role.name}')
            

    @role_edit.command(
        name='hoist',
        description="toggle a role's hoist setting",
        brief='role edit hoist <role> <state>',
        help='role edit hoist users true',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(administrator=True)
    async def role_edit_hoist(self, ctx: Context, role: Union[discord.Role, str], state: str):
            
        if isinstance(role, str):
            role = ctx.find_role(role)
            if role is None:
                return await ctx.send_error('please provide a **valid** role')
                
        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't **edit** that role")
        
        if state == 'true':
            await role.edit(hoist=True)
            return await ctx.send_success(f'successfully **enabled** hoist for {role.name}')
        elif state == 'false':
            await role.edit(hoist=False)
            return await ctx.send_success(f'successfully **disabled** hoist for {role.name}')
        
        return await ctx.send_error('please provide a **valid** state')


    @role_edit.command(
        name='icon',
        description="change a role's icon",
        brief='role edit icon <role> <image>',
        help='role edit icon users https://media.discordapp.net/attachments/1022535209377333248/1049393366787436634/23ED1726-3252-4AC6-8A7E-F80B4FC3396B.png',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role_edit_icon(self, ctx: Context, role: Union[discord.Role, str], image: Union[discord.Attachment, str]):
            
        if isinstance(role, str):
            role = ctx.find_role(role)
            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't **edit** that role")
                
        if isinstance(image, discord.Attachment):
            await role.edit(display_icon=await image.read())
            
        elif isinstance(image, str):
            try:
                await role.edit(display_icon=await self.bot.session.read(image, proxy=True))
            except:
                return await ctx.send_error('please provide a **valid** link')
                
        return await ctx.send_success(f"successfully **edited** {role.name}'s icon")


    @commands.group(
        name='boosterrole',
        aliases=['br'],
        description='manage your custom booster role',
        brief='boosterrole <sub command>',
        help='boosterrole create flawless',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def boosterrole(self, ctx: Context):
        
        return await ctx.send_help()

    
    @boosterrole.command(
        name='toggle',
        description='toggle booster roles for the server',
        brief='boosterrole toggle <state>',
        help='boosterrole toggle true',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def boosterrole_toggle(self, ctx: Context, state: str):

        await ctx.typing()
        if await self.bot.db.fetchval('SELECT state FROM boosterrole_settings WHERE guild_id = %s', ctx.guild.id) is True:
            return await ctx.send_error('booster roles are already **enabled** for this server')
            
        if state == 'true':
            if await self.bot.db.fetchval('SELECT state FROM boosterrole_settings WHERE guild_id = %s', ctx.guild.id) is True:
                return await ctx.send_error('booster roles are already **enabled** for this server')
            
            await self.bot.db.execute(
                'INSERT INTO boosterrole_settings (guild_id, state) VALUES (%s, 1) ON DUPLICATE KEY UPDATE state = 1',
                ctx.guild.id
            )
            return await ctx.send_success('successfully **enabled** booster roles for this server')
        
        elif state == 'false':
            if await self.bot.db.fetchval('SELECT state FROM boosterrole_settings WHERE guild_id = %s', ctx.guild.id) is False:
                return await ctx.send_error('booster roles are already **disabled** for this server')

            await self.bot.db.execute(
                'INSERT INTO boosterrole_settings (guild_id, state) VALUES (%s, 0) ON DUPLICATE KEY UPDATE state = 0',
                ctx.guild.id
            )
            return await ctx.send_success('successfully **disabled** booster roles for this server')

        else:
            return await ctx.send_error('please provide a **valid** state')


    @boosterrole.command(
        name='base',
        description='set the base role for all booster roles to be under',
        brief='boosterrole base <role>',
        help='boosterrole base boosters',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def boosterrole_base(self, ctx: Context, role: Union[discord.Role, str]):

        await ctx.typing()
        if not await self.bot.db.fetchval('SELECT state FROM boosterrole_settings WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('booster roles are **disabled** for this server')

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await utils.send_error('please provide a **valid** role')

        await self.bot.db.execute('UPDATE boosterrole_settings SET base = %s WHERE guild_id = %s', role.id, ctx.guild.id)
        return await ctx.send_success(f'successfully **set** the booster role base as {role.name}')


    @boosterrole.command(
        name='create',
        description='create your own custom booster role',
        brief='boosterrole create <name>',
        help='boosterrole create flawless'
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_create(self, ctx: Context, *, name: str):

        await ctx.typing()
        if not await self.bot.db.fetchval('SELECT state FROM boosterrole_settings WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error('booster roles are **disabled** for this server')

        if not ctx.author.premium_since or ctx.author.get_role(ctx.guild.premium_subscriber_role.id) is None:
            return await ctx.send_error('booster roles are only available to boosters')
        
        boosterroleid = await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id)
        if boosterroleid:
            if ctx.guild.get_role(boosterroleid) is not None:
                return await ctx.send_error('you already have a **booster role**')

        role = await ctx.guild.create_role(name=name)
        base = await self.bot.db.fetchval('SELECT base FROM boosterrole_settings WHERE guild_id = %s', ctx.guild.id)
        if base:
            base_role = ctx.guild.get_role(base)
            await role.edit(position=base_role.position-1)
        await self.bot.db.execute('INSERT INTO boosterrole_roles (guild_id, user_id, role_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)', ctx.guild.id, ctx.author.id, role.id)

        await ctx.author.add_roles(role, reason=f'boosterrole create: used by {ctx.author}')
        return await ctx.send_success(f'successfully **created** a **booster role** with the name {name}')


    @boosterrole.command(
        name='delete',
        description='delete your booster role',
        brief='boosterrole delete',
        help='boosterrole delete'
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_delete(self, ctx: Context):

        await ctx.typing()
        if not ctx.author.premium_since or ctx.author.get_role(ctx.guild.premium_subscriber_role.id) is None:
            return await ctx.send_error('booster roles are only available to boosters')

        if not await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id):
            return await ctx.send_error("you don't have a **booster role**")

        rolee = await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id)
        if ctx.guild.get_role(rolee):
            await ctx.guild.get_role(rolee).delete(reason=f'boosterrole delete: used by {ctx.author}')
        await self.bot.db.execute('DELETE FROM boosterrole_roles WHERE guild_id = %s AND user_id = %s', ctx.guild.id, ctx.author.id)

        return await ctx.send_success('successfully **deleted** your **booster role**')


    @boosterrole.command(
        name='color',
        description="edit your booster role's color",
        brief='boosterrole color <color>',
        help='boosterrole color #b1aad8'
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_color(self, ctx: Context, color: str):

        await ctx.typing()
        if not ctx.author.premium_since or ctx.author.get_role(ctx.guild.premium_subscriber_role.id) is None:
            return await ctx.send_error('booster roles are only available to boosters')

        if not await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id):
            return await ctx.send_error("you don't have a **booster role**")

        rolee = await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id)
        if ctx.guild.get_role(rolee):
            await ctx.guild.get_role(rolee).edit(
                color=int(color.strip('#'), 16), reason=f'boosterrole color: used by {ctx.author}'
            )

        return await ctx.send_success('successfully **edited** your **booster role** color')


    @boosterrole.command(
        name='name',
        description="edit your booster role's name",
        brief='boosterrole name <name>',
        help='boosterrole name flaw'
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_name(self, ctx: Context, name: str):

        await ctx.typing()
        if not ctx.author.premium_since or ctx.author.get_role(ctx.guild.premium_subscriber_role.id) is None:
            return await ctx.send_error('booster roles are only available to boosters')

        if not await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id):
            return await ctx.send_error("you don't have a **booster role**")

        rolee = await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id)
        if ctx.guild.get_role(rolee):
            await ctx.guild.get_role(rolee).edit(
                name=name, reason=f'boosterrole name: used by {ctx.author}'
            )

        return await ctx.send_success('successfully **edited** your **booster role** name')


    @boosterrole.command(
        name='icon',
        description="edit your booster role's icon",
        brief='boosterrole icon <link or emoji>',
        help='boosterrole icon :star:'
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_icon(self, ctx: Context, icon: Union[discord.Emoji, discord.PartialEmoji, str]):

        await ctx.typing()
        if not ctx.author.premium_since or ctx.author.get_role(ctx.guild.premium_subscriber_role.id) is None:
            return await ctx.send_error('booster roles are only available to boosters')

        if not await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id):
            return await ctx.send_error("you don't have a **booster role**")

        rolee = await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE user_id = %s AND guild_id = %s', ctx.author.id, ctx.guild.id)
        if ctx.guild.get_role(rolee):
            if hasattr(icon, 'url'):
                link = icon.url
            else:
                link = icon
            await ctx.guild.get_role(rolee).edit(
                display_icon=await self.bot.session.read(link, proxy=True), reason=f'boosterrole icon: used by {ctx.author}'
            )

        return await ctx.send_success('successfully **edited** your **booster role** color')


    @commands.command(
        name='createrole',
        aliases=['makerole'],
        description='create a role using the bot',
        brief='createrole <hex> <name>',
        help='createrole #b1aad8 flawless',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def createrole(self, ctx: Context, color: str, *, name: str):

        return await ctx.invoke(self.bot.get_command('role create'), color, name)


    @commands.command(
        name='deleterole',
        aliases=['delrole'],
        description='delete a role using the bot',
        brief='deleterole <role>',
        help='deleterole img',
        extras={'permissions': 'manage roles'}
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def deleterole(self, ctx: Context, *, role: Union[discord.Role, str]):

        return await ctx.invoke(self.bot.get_command('role delete'), role)


    @commands.group(
        name='autorole',
        description="manage the server's auto-roles",
        brief='autorole <sub subcommand>',
        help='autorole add star',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def autorole(self, ctx: Context):

        return await ctx.send_help()


    @autorole.command(
        name='add',
        aliases=['create'],
        description='add an auto-role',
        brief='autorole add <role>',
        help='autorole add star',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autorole_add(self, ctx: Context, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if await self.bot.db.fetchrow('SELECT * FROM autorole WHERE guild_id = %s AND role_id = %s', ctx.guild.id, role.id):
            return await ctx.send_error('an auto-role like that **already exists**')

        if role.is_assignable() is False:
            return await ctx.send_error("i can't assign that role")

        if role.is_dangerous() is True:
            return await ctx.send_error('that role has **dangerous** permissions')

        await self.bot.db.execute('INSERT INTO autorole (guild_id, role_id) VALUES (%s, %s)', ctx.guild.id, role.id)

        self.bot.cache.autoroles.setdefault(ctx.guild.id, list()).append(role.id)
        return await ctx.send_success(f'successfully **added** {role.name} as an auto-role')


    @autorole.command(
        name='remove',
        aliases=['delete'],
        description='remove an auto-role',
        brief='autorole remove <role>',
        help='autorole remove star',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autorole_remove(self, ctx: Context, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if not await self.bot.db.fetchrow('SELECT * FROM autorole WHERE guild_id = %s AND role_id = %s', ctx.guild.id, role.id):
            return await ctx.send_error("an auto-role like that **doesnt't exists**")

        await self.bot.db.execute('DELETE FROM autorole WHERE guild_id = %s AND role_id = %s', ctx.guild.id, role.id)

        try:
            self.bot.cache.autoroles.setdefault(ctx.guild.id, list()).remove(role.id)
        except:
            pass
        return await ctx.send_success(f'successfully **removed** {role.name} from the server auto-roles')

    
    @autorole.command(
        name='clear',
        aliases=['c'],
        description="clear the server's auto-roles",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autorole_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM autorole WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.autoroles.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f"successfully **cleared** the server's auto-roles")


    @autorole.command(
        name='list',
        aliases=['show'],
        description="show all the server's auto-roles",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def autorole_list(self, ctx: Context):
        
        if not await self.bot.db.execute('SELECT role_id FROM autorole WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **auto-roles** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Auto-roles in {ctx.guild.name}',
            description=list()
        )
        for role_id in await self.bot.db.execute('SELECT role_id FROM autorole WHERE guild_id = %s', ctx.guild.id):
            if ctx.guild.get_role(role_id) is not None:
                embed.description.append(f'{ctx.guild.get_role(role_).mention} ( `{role_id}` )')
            
        return await ctx.paginate(embed)


    @commands.group(
        name='discriminator',
        aliases=['discrim'],
        description="manage the server's discriminator-roles",
        brief='discriminator <sub subcommand>',
        help='discriminator add 0001 #01',
        extras={'permissions': 'manage guild'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def discriminator(self, ctx: Context):

        return await ctx.send_help()


    @discriminator.command(
        name='add',
        aliases=['create'],
        description='add a discriminator-role',
        brief='discriminator add <discriminator> <role>',
        help='discriminator add 0001 #01',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def discriminator_add(self, ctx: Context, discriminator: str, role: Union[discord.Role, str]):
        
        if len(discriminator) != 4 or not discriminator.isdigit():
            return await ctx.send_error('please provide a **valid** discriminator')

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if await self.bot.db.fetchrow('SELECT * FROM discriminator_roles WHERE guild_id = %s AND role_id = %s AND discriminator = %s', ctx.guild.id, role.id, discriminator):
            return await ctx.send_error('a discriminator-role like that **already exists**')

        if role.is_assignable() is False:
            return await ctx.send_error("i can't assign that role")

        if role.is_dangerous() is True:
            return await ctx.send_error('that role has **dangerous** permissions')

        await self.bot.db.execute('INSERT INTO discriminator_roles (guild_id, role_id, discriminator) VALUES (%s, %s, %s)', ctx.guild.id, role.id, discriminator)

        self.bot.cache.discriminator_roles.setdefault(ctx.guild.id, list()).append({'role_id': role.id, 'discriminator': discriminator})
        return await ctx.send_success(f'successfully **binded** {role.mention} to `#{discriminator}`')


    @discriminator.command(
        name='remove',
        aliases=['delete'],
        description='remove a discriminator-role',
        brief='discriminator remove <role>',
        help='discriminator remove 0001 #01',
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def discriminator_remove(self, ctx: Context, discriminator: str, role: Union[discord.Role, str]):
        
        if len(discriminator) != 4 or not discriminator.isdigit():
            return await ctx.send_error('please provide a **valid** discriminator')

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if not await self.bot.db.fetchrow('SELECT * FROM discriminator_roles WHERE guild_id = %s AND role_id = %s AND discriminator = %s', ctx.guild.id, role.id, discriminator):
            return await ctx.send_error("a discriminator-role like that **doesnt't exists**")

        await self.bot.db.execute('DELETE FROM discriminator_roles WHERE guild_id = %s AND role_id = %s AND discriminator = %s', ctx.guild.id, role.id, discriminator)

        try:
            self.bot.cache.discriminator_roles.setdefault(ctx.guild.id, list()).remove({'role_id': role.id, 'discriminator': discriminator})
        except:
            pass
        return await ctx.send_success(f'successfully **removed** {role.mention} from `#{discriminator}`')

    
    @discriminator.command(
        name='clear',
        aliases=['c'],
        description="clear the server's discriminator-roles",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def discriminator_clear(self, ctx: Context):

        await self.bot.db.execute('DELETE FROM discriminator_roles WHERE guild_id = %s', ctx.guild.id)

        try:
            self.bot.cache.discriminator_roles.pop(ctx.guild.id)
        except:
            pass

        return await ctx.send_success(f"successfully **cleared** the server's discriminator-roles")


    @discriminator.command(
        name='list',
        aliases=['show'],
        description="show all the server's discriminator-roles",
        extras={'permissions': 'manage guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def discriminator_list(self, ctx: Context):
        
        if not await self.bot.db.execute('SELECT role_id FROM discriminator_roles WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **auto-roles** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Discriminator-roles in {ctx.guild.name}',
            description=list()
        )
        for role_id, discriminator in await self.bot.db.execute('SELECT role_id, discriminator FROM discriminator_roles WHERE guild_id = %s', ctx.guild.id):
            if ctx.guild.get_role(role_id) is not None:
                embed.description.append(f'{ctx.guild.get_role(role_).mention} {discriminator} ( `{role_id}` )')
            
        return await ctx.paginate(embed)


async def setup(bot: Vile):
    await bot.add_cog(Roles(bot))
