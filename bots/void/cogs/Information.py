import discord
from discord.ext import commands
import datetime
import typing

color = 0x2b2d31

from discord import Embed
from typing import Optional, Set
from utils.paginator import Paginator


class Help(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return f'{self.context.clean_prefix}{command.qualified_name}'
    
    async def help_embed(self, title: Optional[str] = None, description: Optional[str] = None, mapping: Optional[dict] = None, command_set: Optional[Set[commands.Command]] = None, horseshit: Optional[bool] = False):
            helpdesc = ''
            e = Embed(color=color, description=helpdesc)  
            if title:
                e.title = title
            if description:
                e.description = description
            if command_set:
                filtered = await self.filter_commands(command_set, sort=True)
                for command in filtered:
                    e.add_field(name=command.qualified_name, value=command.help, inline=False)
            elif mapping:
                if horseshit:
                    embeds = []
                    cogs = ''
                    pagenum = 1
                    maxpages = 1
                    for cog, command_set in mapping.items():
                        filtered = await self.filter_commands(command_set, sort=True)
                        if not filtered:
                            continue
                        if cog.qualified_name != 'Jishaku': pass
                        maxpages += 1
                    for cog, command_set in mapping.items():
                        filtered = await self.filter_commands(command_set, sort=True)
                        if not filtered:
                            continue
                        if cog.qualified_name != 'Jishaku': pass
                        pagenum += 1
                        embed = discord.Embed(color=color,)
                        commands = ''
                        for command in sorted(self.context.bot.get_cog(cog.qualified_name).walk_commands(), key=lambda x: x.qualified_name):
                            commands += f"> [{command}](https://discord.gg/voidbot)\n"
                        embed.description = f'```ini\n[ {cog.qualified_name} ]\n[ {len(set(self.context.bot.get_cog(cog.qualified_name).walk_commands()))} commands ]```\n{commands}'
                        embed.set_footer(text=f"Page {pagenum}/{maxpages}")
                        embed.set_thumbnail(url=self.context.bot.user.display_avatar)
                        embeds.append(embed)
                        cogs += f"> [{cog.qualified_name}](https://discord.gg/voidbot)\n"
                    totalcommands = [command for command in self.context.bot.walk_commands() if command.cog_name != 'Jishaku']
                    mainEmbed = discord.Embed(
                        color=color,
                        description=f"""
                        ```ini\n[ {len(totalcommands)} commands ]```
                        {cogs}

                        """).set_thumbnail(url=self.context.bot.user.display_avatar).set_footer(text=f"Page 1/{maxpages}")
                    embeds.insert(0, mainEmbed)
                    pag = Paginator(self.context.bot, embeds, self.context, invoker=self.context.author.id)
                    pag.add_button('prev', emoji='<:void_previous:1082283002207424572>')
                    pag.add_button('goto', emoji='<:void_goto:1082282999187517490>')
                    pag.add_button('next', emoji='<:void_next:1082283004321341511>')
                    pag.add_button('delete', emoji='<:void_cross:1082283006649188435>')
                    await pag.start()
                    return
                for cog, command_set in sorted(mapping.items(), key=lambda item: item[0].qualified_name):
                    filtered = await self.filter_commands(command_set, sort=True)
                    if not filtered:
                        continue
                    name = cog.qualified_name if cog else 'no category'
                    command_list = ', '.join(f'`{command.name}`' for command in sorted(filtered, key=lambda x: x.name))
                    for command in filtered:
                        if isinstance(command, commands.Group):
                            command_list = command_list.replace(f'`{command.name}`', f'`{command.name}*`')
                    value = (
                        f'{command_list}'
                    )
                    e.add_field(name=name, value=value, inline=False)
            return e

    async def send_bot_help(self, mapping: dict):
        e = await self.help_embed(
            mapping=mapping,
            horseshit=True
        )
        if e:
            await self.get_destination().send(embed=e)
        else:
            pass

    async def send_command_help(self, command: commands.Command):
        e = await self.help_embed(
            title=f'Command: {command.qualified_name}',
            description=command.description
        )
        e.set_author(
            name=self.context.bot.user.name,
            icon_url=self.context.bot.user.display_avatar)
        e.set_footer(text=f'Module: {command.cog_name}')
        aliases = ', '.join(alias for alias in command.aliases if alias != command.name)
        if aliases:
            e.add_field(name="Aliases", value=aliases)
        else:
            e.add_field(name='Aliases', value='N/A')
        if command.brief:
            e.add_field(name='Parameters', value=command.brief, inline=True)
        else:
            e.add_field(name='Parameters', value='N/A', inline=True)
        if command.extras:
            perms=command.extras.get('perms')
            if "_" in perms:
                perms=perms.replace("_", " ")
            e.add_field(name="Permissions", value=perms, inline=True)
        else:
            e.add_field(name='Permissions', value='N/A', inline=True)
        if command.usage:
            usage = command.usage
            if "Syntax: " in usage:
                if not "Syntax: ," in usage:
                    usage=usage.replace(f"Syntax: ", f"Syntax: {self.context.clean_prefix}{command.qualified_name} ")
                else:
                    usage=usage.replace("Syntax: ,", f"Syntax: {self.context.clean_prefix}{command.qualified_name} ")
            if "Example: " in usage:
                if "Example: ," not in usage:
                    usage=usage.replace("Example: ", f"Example: {self.context.clean_prefix}{command.qualified_name} ")
                else:
                    usage=usage.replace("Example: ,", f"Example: {self.context.clean_prefix}{command.qualified_name} ")
            e.add_field(name="Usage", value=f'```{usage}```', inline=False)
        await self.get_destination().send(embed=e)

    async def send_group_help(self, group: commands.Group):
        if not group.commands:
            group.aliases.append('')
        e = await self.help_embed(
            title=f'Group Command: {group.qualified_name}',
            description=group.description
        )
        e.set_author(
            name=self.context.bot.user.name,
            icon_url=self.context.bot.user.display_avatar)
        e.set_footer(text=f'Module: {group.cog_name}')
        aliases = ', '.join(alias for alias in group.aliases if alias != group.name)
        if aliases:
            e.add_field(name="Aliases", value=aliases)
        else:
            e.add_field(name='Aliases', value='N/A')
        if group.brief:
            e.add_field(name='Parameters', value=group.brief, inline=True)
        else:
            e.add_field(name='Parameters', value='N/A', inline=True)
        if group.extras:
            perms=group.extras.get('perms')
            if "_" in perms:
                perms=perms.replace("_", " ")
            e.add_field(name="Permissions", value=perms, inline=True)
        else:
            e.add_field(name='Permissions', value='N/A', inline=True)
        if group.usage:
            usage = group.usage
            if "Syntax: " in usage:
                if not "Syntax: ," in usage:
                    usage=usage.replace(f"Syntax: ", f"Syntax: {self.context.clean_prefix}{group.qualified_name} ")
                else:
                    usage=usage.replace("Syntax: ,", f"Syntax: {self.context.clean_prefix}{group.qualified_name} ")
            if "Example: " in usage:
                if "Example: ," not in usage:
                    usage=usage.replace("Example: ", f"Example: {self.context.clean_prefix}{group.qualified_name} ")
                else:
                    usage=usage.replace("Example: ,", f"Example: {self.context.clean_prefix}{group.qualified_name} ")
            e.add_field(name="Usage", value=f'```{usage}```', inline=False)
        filtered = await self.filter_commands(group.walk_commands(), sort=True)
        if filtered:
            if any(command.usage for command in filtered):
                e.add_field(name='Subcommands', value=''.join(f'> {self.context.clean_prefix}{command.qualified_name} - {command.description}\n' for command in filtered), inline=False)
        await self.get_destination().send(embed=e)


class Information(commands.Cog):

    def __init__(self, bot):
        attrs = {
            'help': '',
            'description': 'View the bot commands',
            'usage': 'Syntax: <command>',
            'aliases': ['commands', 'cmds']
            }
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = Help(command_attrs=attrs)
        bot.help_command.cog = self
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")
        
    @commands.command(
        name='serverinfo',
        description='View information about a server',
        brief='guild',
        usage='Syntax: <guild>',
        aliases=['guildinfo', 'sinfo', 'ginfo', 'si', 'gi']
    )
    async def serverinfo(self, ctx, *, guild: discord.Guild = None):

        await ctx.typing()
        guild = ctx.guild if guild is None else guild
        channel_count = len(guild.text_channels) + len(guild.voice_channels)
        invite = 'N/A'
        if guild.vanity_url is not None:
            invite = f'[{guild.vanity_url_code}]({guild.vanity_url})'
        e = discord.Embed(
            color=color,
            title=f'{guild.name} ({guild.id})',
            description=f'Created {discord.utils.format_dt(guild.created_at, style="F")}'
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
        e.set_thumbnail(url=guild.icon.url)
        e.set_author(name=f'{ctx.author.display_name}', icon_url=ctx.author.display_avatar)
        await ctx.reply(embed=e, mention_author=False)
    
    @commands.command(
        name='userinfo',
        description='View the information about a user',
        brief='user',
        usage='Syntax: <user>',
        aliases=['ui', 'whois', 'user', 'uinfo']
    )
    async def userinfo(self, ctx, *, user: discord.Member = None):

        await ctx.typing()
        user = ctx.author if user is None else user
        position = sorted(ctx.guild.members, key=lambda m: m.joined_at).index(user) + 1
        
        e = discord.Embed(
            color=color
        )
        e.add_field(name='Created', value=f'{discord.utils.format_dt(user.created_at, style="D")}\n{discord.utils.format_dt(user.created_at, style="R")}')
        e.add_field(name='Joined', value=f'{discord.utils.format_dt(user.joined_at, style="D")}\n{discord.utils.format_dt(user.joined_at, style="R")}')
        if user.premium_since:
            e.add_field(name='Boosted', value=f'{discord.utils.format_dt(user.premium_since, style="D")}\n{discord.utils.format_dt(user.premium_since, style="R")}')
        e.add_field(name=f'Roles ({len(user.roles[1:])})', value=f', '.join([r.mention for r in reversed(user.roles[1:])]), inline=False)
        e.set_author(name=f'{user} ({user.id})', icon_url=user.display_avatar)
        e.set_thumbnail(url=user.display_avatar)
        e.set_footer(text=f'Join position: {position}')
        await ctx.send(embed=e)

    @commands.command(
        name='avatar',
        description='View the avatar of a user',
        brief='user',
        usage='Syntax: <user>',
        aliases=['av']
    )
    async def avatar(self, ctx, *, user: discord.Member = None):

        await ctx.typing()
        user = ctx.author if user is None else user
        e = discord.Embed(
            title=f'{user.name}\'s avatar',
            url=user.display_avatar,
            color=color
        )
        e.set_author(name=f'{ctx.author.display_name}', icon_url=ctx.author.display_avatar)
        e.set_image(url=user.display_avatar)
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(
        name='banner',
        description='View the banner of a user',
        brief='user',
        usage='Syntax: <user>',
        aliases=['userbanner', 'ub']
    )
    async def banner(self, ctx, *, user: discord.Member = None):

        await ctx.typing()
        member = ctx.author if user is None else user
        user = await self.bot.fetch_user(member.id)
        e = discord.Embed(
            title=f'{user.name}\'s banner',
            url=user.banner,
            color=color
        )
        e.set_author(name=f'{ctx.author.display_name}', icon_url=ctx.author.display_avatar)
        e.set_image(url=user.banner)
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(
        name='servericon',
        description='View the icon of a server',
        brief='guild',
        usage='Syntax: <guild>',
        aliases=['icon', 'guildicon', 'sicon', 'gicon']
    )
    async def servericon(self, ctx, *, guild: discord.Guild = None):
        
        ctx.typing()
        guild = ctx.guild if guild is None else guild
        e = discord.Embed(
            title=f'{guild.name}\'s server icon',
            url=guild.icon.url,
            color=color
        )
        e.set_author(name=f'{ctx.author.display_name}', icon_url=ctx.author.avatar.url)
        e.set_image(url=guild.icon.url)
        await ctx.send(embed=e)

    @commands.command(
        name='serverbanner',
        description='View the banner of a server',
        brief='guild',
        usage='Syntax: <guild>',
        aliases=['sb']
    )
    async def serverbanner(self, ctx, *, guild: discord.Guild = None):

        ctx.typing()
        guild = ctx.guild if guild is None else guild
        e = discord.Embed(
            title=f'{guild.name}\'s server banner',
            url=guild.banner,
            color=color
        )
        e.set_author(name=f'{ctx.author.display_name}', icon_url=ctx.author.avatar.url)
        e.set_image(url=guild.banner)
        await ctx.send(embed=e)

    @commands.command(
        name='serversplash',
        description='View the splash of a server',
        brief='guild',
        usage='Syntax: <guild>',
        aliases=['ss', 'splash']
    )
    async def serversplash(self, ctx, *, guild: discord.Guild = None):

        ctx.typing()
        guild = ctx.guild if guild is None else guild
        e = discord.Embed(
            color=color,
            title=f'{guild.name}\'s server splash',
            url=guild.splash
        )
        e.set_author(name=f'{ctx.author.display_name}', icon_url=ctx.author.avatar.url)
        e.set_image(url=guild.splash)
        await ctx.send(embed=e)

    @commands.command(
        name='membercount',
        description='View the member count of a server',
        brief='guild',
        usage='Syntax: <guild>',
        aliases=['mc'],
    )
    async def membercount(self, ctx, *, guild: discord.Guild = None):
        await ctx.typing()
        
        guild = ctx.guild if guild is None else guild
        e=discord.Embed(
            color=color)
        e.set_author(name=guild.name, icon_url=guild.icon)
        e.add_field(name="Total", value=guild.member_count)
        e.add_field(name="Humans", value=len(list(filter(lambda m: not m.bot, guild.members))))
        e.add_field(name="Bots", value=len(list(filter(lambda m: m.bot, guild.members))))
        await ctx.send(embed=e)

    @commands.command(
        name='ping',
        description='View the bots latency',
        usage='Syntax: ',
        aliases=['latency']
    )
    async def ping(self, ctx):
        await ctx.typing()

        await ctx.success(f'Websocket: `{round(self.bot.latency * 1000, 2)}ms`')

    @commands.command(
        name='botinfo',
        description='View information about the bot',
        usage='Syntax: ',
        aliases=['about', 'info']
    )
    async def botinfo(self, ctx):

        await ctx.typing()
        invite = 'https://discord.com/api/oauth2/authorize?client_id=1075226332935503913&permissions=8&scope=bot'
        servercount = len(self.bot.guilds)
        usercount = len(self.bot.users)
        current_time = datetime.datetime.utcnow()
        difference = current_time - self.bot.startup_time
        hours, remainder = divmod(int(difference.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        e = discord.Embed(
            color=color,
            description=f'**[Support](https://discord.gg/voidbot)** | **[Invite]({invite})**\n'
                        f'Multipurpose bot\n'
        )
        totalcommands = [command for command in self.bot.walk_commands() if command.cog_name != 'Jishaku']
        e.add_field(name='Statistics', value=f'**Guilds:** {servercount} guild(s)\n'
                                             f'**Users:** {usercount} user(s)\n'
                                             f'**Commands:** {len(totalcommands)}\n'
                                             f'**Uptime:** {days}d {hours}h {minutes}m {seconds}s')
        e.set_thumbnail(url=self.bot.user.avatar.url)
        e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        e.set_footer(text=f'{self.bot.user.name}/{self.bot.version}')
        await ctx.send(embed=e)
    
    @commands.command(
        name='roles',
        description='View the server roles',
        usage='Syntax: ',
        aliases=['rolelist']
    )
    async def roles(self, ctx):
        
        await ctx.typing()
        embeds = []
        ret = []
        num = 0
        pagenum = 0
        if ctx.guild.roles is None:
            return
        for role in ctx.guild.roles[::-1]:
            if role.name != "@everyone":
                num += 1
                ret.append(f'**{num}.** {role.mention} ({role.id})')
                pages = [p for p in discord.utils.as_chunks(ret, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(discord.Embed(
                title=f'Roles in {ctx.guild.name}',
                color=color, 
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
        name='inrole',
        description='View the users in a role',
        brief='role',
        aliases=['members'],
        usage='Syntax: (role)',
    )
    async def inrole(self, ctx, *, role: discord.Role):
        """View the users in a role"""
        
        await ctx.typing()
        embeds = []
        ret = []
        num = 0
        pagenum = 0
        for m in ctx.guild.members:
            if m in role.members:
                num += 1
                ret.append(f'**{num}.** {m.mention} ({m.id})')
                pages = [p for p in discord.utils.as_chunks(ret, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(discord.Embed(
                color=color,
                title=f'Members with {role.name}',
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
        name='roleinfo',
        description='View the information about a role',
        brief='role',
        usage='Syntax: (role)',
        aliases=['ri', 'rinfo'],
    )
    async def roleinfo(self, ctx, *, role: discord.Role):
        e = discord.Embed(
            color=role.color,
            title=f'{role.name} ({role.id})',
        )
        
        e.add_field(name='Created', value=f'{discord.utils.format_dt(role.created_at, style="D")}\n{discord.utils.format_dt(role.created_at, style="R")}')
        e.add_field(name='Color', value=f'**Hex:** {role.color}\n'
                                        f'**RGB:** {role.color.to_rgb()}')
        e.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
        e.set_footer(text=f'{role.id}')
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(
        name='boosters',
        description='View the boosters of a guild',
        brief='guild',
        usage='Syntax: <guild>'
    )
    async def boosters(self, ctx, *, guild: discord.Guild = None):

        await ctx.typing()
        guild = ctx.guild if guild is None else guild
        embeds = []
        ret = []
        num = 0
        pagenum = 0
        for m in ctx.guild.members:
            if m.premium_since:
                num += 1
                ret.append(f'**{num}.** {m.mention} ({m.id})')
                pages = [p for p in discord.utils.as_chunks(ret, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(discord.Embed(
                title=f'Boosters in {guild.name}',
                color=color, 
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
    await bot.add_cog(Information(bot))