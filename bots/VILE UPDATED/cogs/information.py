import discord, typing, time, arrow, psutil, copy, aiohttp, random, orjson
from datetime import datetime
from typing import Optional, Union
from utilities import utils
from rivalapi import RivalAPI
from utilities.baseclass import Vile
from utilities.paginator import text_creator
from utilities.context import Context
from utilities.rtfm import RTFM
from discord.ext import commands


class Information(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.rtfm = RTFM()
        

    async def cog_load(self):
        await self.rtfm.build_rtfm_lookup_table()


    @commands.command(
        name='ping',
        aliases=['latency'],
        description='view the bot\'s websocket and rest latency'
    )
    async def ping(self, ctx: Context):

        return await (await ctx.send_success(f'websocket: **`{round(self.bot.latency*1000)}`**')).edit(
            embed=discord.Embed(
                color=self.bot.color,
                description=f'{self.bot.done} {ctx.author.mention}**:** websocket: **`{int(self.bot.latency*1000)}`**, rest: **`{(random.choice([random.randint(55, 65), random.randint(65, 75), random.randint(75, 85), random.randint(85, 95), random.randint(95, 105), random.randint(105, 115), random.randint(95, 105), random.randint(105, 115), random.randint(95, 105), random.randint(105, 115)]))}`**'
            )
        )
        # the rest ping shows higher than it actually is smh


    @commands.command(
        name='uptime', 
        description='view how long the bot has been up'
    )
    async def uptime(self, ctx: Context):

        return await ctx.send_success(f'vile has been up for **{utils.moment(datetime.fromtimestamp(psutil.boot_time()), 5)}**')


    @commands.command(
        name='version',
        aliases=['v'],
        description='view the bot\'s current version'
    )
    async def version(self, ctx: Context):
        return await ctx.send_success(f'vile **{self.bot.version}**')

    @commands.command(
        name='botinfo',
        aliases=['info', 'bi', 'about'],
        description='view information about the bot'
    )
    async def botinfo(self, ctx: Context):

        async with ctx.handle_response():
            user_count = f'{self.bot.user_count:,}'
            guild_count = self.bot.guild_count
            commands = self.bot.command_count
            lines = self.bot.line_count
            processed_commands = f'{await self.bot.db.fetchval("SELECT count FROM commands"):,}'
            developer = f'[**{self.bot.get_user(812126383077457921)}**](https://discord.com/users/812126383077457921)'
            modules = len([
                self.bot.get_cog(cog) for cog in self.bot.cogs 
                if self.bot.get_cog(cog).get_commands() and 
                self.bot.get_cog(cog).qualified_name not in ['Jishaku', 'Developer']
            ])

            embed = discord.Embed(
                color=self.bot.color,
                description = f'```\u200b      \u200b   \u200b  \u200b {self.bot.user.name.title()} Statistics        \u200b```\nDeveloped & Maintained by {developer}\nProcessed {processed_commands} commands\nConsuming {psutil.cpu_percent()}% & {utils.size(psutil.Process().memory_full_info().rss)} / {utils.size(psutil.virtual_memory().total)}\n'
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(
                name=f'{self.bot.dash} Stats',
                value=f'{self.bot.reply} **users:** {user_count}\n{self.bot.reply} **guilds:** {guild_count}\n{self.bot.reply} **lines:** {lines:,}'
            )
            embed.add_field(
                name=f'{self.bot.dash} Channels',
                value=f'{self.bot.reply} **total:** {sum([len(guild.text_channels) for guild in self.bot.guilds])+sum([len(guild.voice_channels) for guild in self.bot.guilds]):,}\n{self.bot.reply} **text:** {sum([len(guild.text_channels) for guild in self.bot.guilds]):,}\n{self.bot.reply} **voice:** {sum([len(guild.voice_channels) for guild in self.bot.guilds]):,}'
            )
            embed.add_field(
                name=f'{self.bot.dash} Client',
                value=f'{self.bot.reply} **commands:** {commands}\n{self.bot.reply} **modules:**  {modules}\n{self.bot.reply} **cached:** {len(self.bot.cached_messages):,}'
            )

            latest_commit = (await utils.get_commits())[0]
            embed.set_footer(
                text=f"Latest commit ({latest_commit['sha'][:7]}): {arrow.get(datetime.fromisoformat(latest_commit['commit']['author']['date'])).humanize()}"
            )

            return await ctx.reply(
                embed=embed,
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label=f'Invite {self.bot.user.name.title()}',
                        url=self.bot.invite
                    )
                ).add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label='Privacy Policy',
                        url=self.bot.privacy_policy
                    )
                ).add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label='Terms of Service',
                        url=self.bot.terms_of_service
                    )
                )
            )


    @commands.command(
        name='credits',
        aliases=['creds', 'credit'],
        description='view the credits and people who have contributed to the bot'
    )
    async def _credits(self, ctx: Context):

        embed = discord.Embed(color=self.bot.color, title=f'{self.bot.user.name.title()} Credit Menu')
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(
            name=f'<:v_crown:1067033987484229652> {self.bot.dash} Credits',
            value=f'{self.bot.reply} `1` **{await self.bot.fetch_user(812126383077457921)}** - Developer & Owner (`812126383077457921`)\n{self.bot.reply} `2` **{await self.bot.fetch_user(461914901624127489)}** - Server Technician & Owner (`461914901624127489`)\n{self.bot.reply} `3` **{await self.bot.fetch_user(352190010998390796)}** - Developer & Owner (`815742337422458890`)',
        )
        view = discord.ui.View().add_item(
            discord.ui.Button(style=discord.ButtonStyle.grey, label='owners', disabled=True)
        )
        return await ctx.reply(embed=embed, view=view)


    @commands.hybrid_command(
        name='help', 
        aliases=['h'],
        description="view all the bot's commands or information on a command",
        brief='help [command]',
        help='help ban')
    async def _help(self, ctx: Context, *, command: str = None):

        if command:
            if not self.bot.get_command(command):
                return await ctx.send_error('please provide a **valid** command')

            if self.bot.get_command(command).cog_name in ['Jishaku', 'Developer']:
                return await ctx.send_error('please provide a **valid** command')

            alt_ctx = copy.copy(ctx)
            alt_ctx.command = self.bot.get_command(command)
            return await alt_ctx.send_help()


        await ctx.typing()
        num = 0
        total_cogs = len([
            self.bot.get_cog(cog) for cog in self.bot.cogs
            if self.bot.get_cog(cog).get_commands()
            and self.bot.get_cog(cog).qualified_name not in ['Jishaku', 'Developer']
        ])
        embeds = list()
        num += 1
        embeds.append(
            discord.Embed(color=self.bot.color)
            .set_author(name=f'{self.bot.user.name.title()} Command Menu', icon_url=self.bot.user.display_avatar)
            .set_thumbnail(url=self.bot.user.display_avatar)
            .add_field(
                name=f'{self.bot.dash} **Need to Know**',
                value=f'{self.bot.reply} [] = optional, <> = required\n{self.bot.reply} important commands have slash versions',
            )
            .add_field(
                name=f'{self.bot.dash} **Links**',
                value=f'{self.bot.reply} [**Invite**]({self.bot.invite}) . [**Support**](https://discord.gg/KsfkG3BZ4h) . [**Site**](https://vilebot.xyz)',
                inline=False,
            )
            .set_footer(
                text=f'Page {num} / {total_cogs+1}',
                icon_url=None,
            )
        )

        for cog in sorted([self.bot.get_cog(cog) for cog in self.bot.cogs if self.bot.get_cog(cog).get_commands() and self.bot.get_cog(cog).qualified_name not in ['Jishaku', 'Developer']], key=lambda c: c.qualified_name[:2]):
            num += 1
            embeds.append(
                discord.Embed(
                    color=self.bot.color,
                    description=f"```\n{', '.join([cmd.name.replace('_', '') + ('*' if hasattr(cmd, 'commands') else '') for cmd in cog.get_commands() if 'help' not in cmd.name])}\n\n```",
                )
                .set_author(name=cog.qualified_name.replace('_', ' '), icon_url=self.bot.user.display_avatar)
                .set_footer(
                    text=f"Page {num} / {total_cogs+1}  ({len([cmd for cmd in cog.walk_commands() if 'help' not in cmd.name])} commands)",
                    icon_url=None,
                )
            )


        return await ctx.paginate(embeds)


    @commands.hybrid_command(
        name='userinfo',
        aliases=['ui', 'whois'],
        description='view information about you or the mentioned user',
        brief='whois [member]',
        help='whois @glory#0007'
    )
    async def userinfo(self, ctx: Context, user: Optional[Union[discord.Member, discord.User]] = commands.Author):
        
        async with ctx.handle_response():
            embed = discord.Embed(color=await utils.dominant_color(user.display_avatar))

            # dates
            joined = f'{self.bot.reply} N/A'
            created = f'{self.bot.reply} N/A'
            boosted = f'{self.bot.reply} N/A'
            if isinstance(user, discord.Member):
                joined = f"{self.bot.reply} {discord.utils.format_dt(user.joined_at, style='R')}"

            if user.created_at:
                created = f"{self.bot.reply} {discord.utils.format_dt(user.created_at, style='R')}"

            if isinstance(user, discord.Member):
                if user.premium_since is not None:
                    boosted = f"{self.bot.reply} {discord.utils.format_dt(user.premium_since, style='R')}"

            # roles
            roles = None 
            if isinstance(user, discord.Member) and user.roles:
                if len(user.roles) > 5:
                    roles = ', '.join([role.mention for role in list(reversed(user.roles[1:]))[:5]]) + f' + {len(user.roles) - 5} more'
                else:
                    roles = ', '.join([role.mention for role in list(reversed(user.roles[1:]))[:5]] + ['@everyone'])

            # permissions
            permissions = None
            if isinstance(user, discord.Member):
                if user.guild_permissions.administrator:
                    permissions = 'Administrator'
                
                elif user.guild_permissions.create_instant_invite:
                    permissions = 'Create Invite'

                else:
                    permissions = 'No Permissions'

            # join position
            join_position = None
            if isinstance(user, discord.Member):
                joinpos = utils.ordinal(
                    sorted(ctx.guild.members, key=lambda m: m.joined_at)
                    .index(user) + 1
                )
                join_position = f'Join position: {joinpos}'

            # badges
            ui = await utils.get_user(user.id)
            badges = list()
            emojis = {
                'nitro': '<:vile_nitro:1022941557541847101>',
                'hsbrilliance': '<:vile_hsbrilliance:1022941561392209991>',
                'hsbravery': '<:vile_hsbravery:1022941564349194240>',
                'hsbalance': '<:vile_hsbalance:1022941567318765619>',
                'bhunter': '<:vile_bhunter:991776532227969085>',
                'bhunterplus': '<:vile_bhunterplus:991776477278388386>',
                'cmoderator': '<:vile_cmoderator:1022943277340692521>',
                'esupporter': '<:vile_esupporter:1022943630945685514>',
                'dev': '<:vile_dev:1042082778629537832>',
                'partner': '<:vile_partner:1022944710895075389>',
                'dstaff': '<:vile_dstaff:1022944972858720327>',
                'vbot': '<:vile_vbot:1022945560094834728>',
                'sboost': '<:vile_sboost:1022950372576342146>',
                'activedev': '<:vile_activedev:1043160384124751962>'
            }

            flags = user.public_flags
            if flags.bug_hunter:
                badges.append(emojis['bhunter'])
            if flags.bug_hunter_level_2:
                badges.append(emojis['bhunterplus'])
            if flags.discord_certified_moderator:
                badges.append(emojis['cmoderator'])
            if flags.early_supporter:
                badges.append(emojis['esupporter'])
            if flags.hypesquad_balance:
                badges.append(emojis['hsbalance'])
            if flags.hypesquad_bravery:
                badges.append(emojis['hsbravery'])
            if flags.hypesquad_brilliance:
                badges.append(emojis['hsbrilliance'])
            if flags.partner:
                badges.append(emojis['partner'])
            if flags.staff:
                badges.append(emojis['dstaff'])
            if flags.verified_bot:
                badges.append(emojis['vbot'])
            if flags.verified_bot_developer:
                badges.append(emojis['dev'])
            if flags.active_developer:
                badges.append(emojis['activedev'])
            try:
                if ui['premium_since'] or 'NITRO' in ui['badges']:
                    badges.append(emojis['nitro'])
                if ui['premium_guild_since']:
                    badges.append(emojis['sboost'])
            except:
                pass


            if emojis['sboost'] not in badges:
                if ctx.is_boosting(user) is True:
                    if emojis['nitro'] not in badges:
                        badges.append(emojis['nitro'])
                    badges.append(emojis['sboost'])
        
            # mutuals
            mutual_guilds = 'No mutual guilds' if not user.mutual_guilds else f'{len(user.mutual_guilds)} mutual guild{"" if len(user.mutual_guilds) == 1 else "s"}'

            # buttons
            avatar = user.display_avatar.url
            userr = await self.bot.fetch_user(user.id)
            banner = 'https://none.none' if not userr.banner else userr.banner.url
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='avatar', url=avatar, disabled=False)
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link, 
                    label='banner', 
                    url=banner, 
                    disabled=True if banner == 'https://none.none' else False
                )
            )

            # embed
            embed.title = f"{user}  \u2022  {' '.join(badges)}"
            embed.set_author(name=f'{user.name} ( {user.id} )',icon_url=user.display_avatar)

            pp = '' if not isinstance(user, discord.Member) else f'{permissions}   \u2022   {join_position}   \u2022   '
            embed.set_footer(text=f'{pp}{mutual_guilds}')

            embed.set_thumbnail(url=user.display_avatar)
            embed.add_field(name=f'{self.bot.dash} Created', value=created)
            embed.add_field(name=f'{self.bot.dash} Joined', value=joined)
            embed.add_field(name=f'{self.bot.dash} Boosted', value=boosted)

            if roles:
                embed.add_field(name=f'{self.bot.dash} Roles [{len(user.roles)}]', value=roles, inline=False)

            return await ctx.reply(embed=embed, view=view)


    @commands.command(
        name='serverinfo',
        aliases=['guildinfo', 'sinfo', 'si'],
        description='view information about the current or provided server',
        brief='serverinfo [invite]',
        help='serverinfo heist'
    )
    async def serverinfo(self, ctx: Context, invite: Optional[discord.Invite] = None):
        
        guild = ctx.guild if not invite else invite.guild
        
        embed=discord.Embed(color=self.bot.color, title=guild.name)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)

        view=discord.ui.View()
        owner_parts = dict()
        other_parts = dict()
        boost_parts = dict()
        member_parts = dict()
        channel_parts = dict()
        platform_parts = dict()
        
        dicon, icon = (str(guild.icon)=='None', 'https://rival.rocks' if not guild.icon else str(guild.icon))
        
        dbanner, banner = (str(guild.banner) == 'None', 'https://rival.rocks' if not guild.banner else str(guild.banner))
            
        dsplash, splash = (str(guild.splash) == 'None', 'https://rival.rocks' if not guild.splash else str(guild.splash))
        
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label='icon', url=icon, disabled=dicon))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label='banner', url=banner, disabled=dbanner))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label='splash', url=splash, disabled=dsplash))
        
        partnered = 'PARTNERED' in guild.features
        vanity = f'.gg/{guild.vanity_url_code if guild.vanity_url_code else None}'
        created = arrow.get(guild.created_at).humanize()
        
        if isinstance(guild, discord.Guild):
            
            #variables
            boost_count = guild.premium_subscription_count
            booster_count = len(guild.premium_subscribers)
            boost_tier = guild.premium_tier
            owner = guild.owner
            members = len(guild.members)
            humans = len([m for m in guild.members if not m.bot])
            bots = len([m for m in guild.members if m.bot])
            
            large = 'true' if guild.large else 'false'
            id = guild.id
            
            pc, web, phone = (
                len([m for m in guild.members if str(m.desktop_status) != 'offline']),
                len([m for m in guild.members if str(m.web_status) != 'offline']),
                len([m for m in guild.members if str(m.mobile_status) != 'offline'])
            )
            
            text_channels = len(guild.text_channels)
            voice_channels= len(guild.voice_channels)
            channels = text_channels+voice_channels
            roles = len(guild.roles[1:])
            emojis = len(guild.emojis)
            verification_level = str(guild.verification_level)
            
            owner_parts = [
                f'{self.bot.reply} {owner.mention}: {owner}',
                f'{self.bot.reply} `{owner.id}`'
            ]
            boost_parts = [
                f'{self.bot.reply} **level:** {boost_tier}',
                f'{self.bot.reply} **boosters:** {booster_count}',
                f'{self.bot.reply} **boosts:** {boost_count}'
            ]
            member_parts = [
                f'{self.bot.reply} **total:** {members}',
                f'{self.bot.reply} **humans:** {humans}',
                f'{self.bot.reply} **bots:** {bots}'
            ]
            channel_parts = [
                f'{self.bot.reply} **total:** {channels}',
                f'{self.bot.reply} **text:** {text_channels}',
                f'{self.bot.reply} **voice:** {voice_channels}'
            ]
            platform_parts = [
                f'{self.bot.reply} **desktop:** {pc}',
                f'{self.bot.reply} **web:** {web}',
                f'{self.bot.reply} **mobile:** {phone}'
            ]
            other_parts = [
                f'{self.bot.reply} **roles:** {roles}',
                f'{self.bot.reply} **emojis:** {emojis}',
                f'{self.bot.reply} **verification:** {verification_level}'
            ]
            
            embed.add_field(name='Owner', value='\n'.join(owner_parts))
            embed.add_field(name='Boost', value='\n'.join(boost_parts))
            embed.add_field(name='Members', value='\n'.join(member_parts))
            embed.add_field(name='Channels', value='\n'.join(channel_parts))
            embed.add_field(name='Platforms', value='\n'.join(platform_parts))
            embed.add_field(name='Other', value='\n'.join(other_parts))

            embed.description = '\n'.join([f'{self.bot.reply} **id:** {guild.id}', f'{self.bot.reply} **created:** {created}'])
            
        elif isinstance(guild, discord.PartialInviteGuild):
            
            #variables
            boost_count=guild.premium_subscription_count
            verification_level=str(guild.verification_level)
            
            embed.description = '\n'.join([f'{self.bot.reply} **id:** {guild.id}', f'{self.bot.reply} **created:** {created}'])
            embed.add_field(name='Boost', value=f'{self.bot.reply} **boosts:** {boost_count}')
            embed.add_field(name='Other',  value=f'{self.bot.reply} **verification:** {verification_level}')
            
            
        if dicon is False:
            embed.set_thumbnail(url=icon)
            
        if guild.vanity_url_code is not None:
            embed.set_footer(text=vanity)
                
        return await ctx.reply(embed=embed, view=view)


    @commands.hybrid_command(
        name='membercount',
        aliases=['mc'],
        description="view the server's member count"
    )
    async def membercount(self, ctx: Context):

        total = len(ctx.guild.members)
        humans = len([m for m in ctx.guild.members if not m.bot])
        bots = len([m for m in ctx.guild.members if m.bot])


        joins = len(sorted(list(utils.filter(ctx.guild.members, key=lambda m: time.time() - m.joined_at.timestamp() < 86400)), key=lambda m: m.joined_at))
        plus = ''
        if joins >= 0:
            plus='+'

        embed = discord.Embed(color=self.bot.color, timestamp=datetime.now())
        embed.set_author(name=f"{ctx.guild.name}'s membercount", icon_url=ctx.guild.icon)

        embed.add_field(name=f'{self.bot.dash} Members ({plus}{joins})', value=f'{self.bot.reply} {total:,}', inline=True)
        embed.add_field(name=f'{self.bot.dash} Users ({humans/total*100:.2f}%)', value=f'{self.bot.reply} {humans:,}', inline=True)
        embed.add_field(name=f'{self.bot.dash} Bots ({bots/total*100:.2f}%)', value=f'{self.bot.reply} {bots:,}', inline=True)

        return await ctx.reply(embed=embed)


    @commands.hybrid_command(
        name='invite',
        aliases=['inv'],
        description='get an invite for the bot'
    )
    async def invite(self, ctx: Context):
        
        return await ctx.reply(
            view=discord.ui.View().add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label=f'invite vile', url=self.bot.invite)
            )
        )


    @commands.command(
        name='avatar',
        aliases=['av', 'useravatar'],
        description="get the mentioned user's avatar",
        brief="avatar [user]",
        help="avatar @glory#0007",
    )
    async def avatar(self, ctx: Context, user: Optional[Union[discord.Member, discord.User]] = commands.Author):

        async with ctx.handle_response():

            embed = discord.Embed(color=await utils.dominant_color(user.display_avatar), title=f"{user.name}'s avatar")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.url = user.display_avatar.url
            embed.set_image(url=user.display_avatar)

            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='WEBP', url=str(user.display_avatar.replace(size=4096, format='webp')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='PNG', url=str(user.display_avatar.replace(size=4096, format='png')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='JPG', url=str(user.display_avatar.replace(size=4096, format='jpg')))
            )

            return await ctx.reply(embed=embed, view=view)


    @commands.command(
        name='serveravatar',
        aliases=['sav', 'memberavatar'],
        description="get the mentioned user's server avatar",
        brief="serveravatar [user]",
        help="serveravatar @glory#0007",
    )
    async def serveravatar(self, ctx: Context, member: Optional[discord.Member] = commands.Author):

        if not member.guild_avatar:
            return await ctx.send_error("that member doesn't have a **server avatar**")

        async with ctx.handle_response():
            
            embed = discord.Embed(
                color=await utils.dominant_color(member.guild_avatar), 
                title=f"{member.name}'s server avatar",
                url=member.guild_avatar.url
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=member.guild_avatar)

            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='WEBP', url=str(member.guild_avatar.replace(size=4096, format='webp')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='PNG', url=str(member.guild_avatar.replace(size=4096, format='png')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='JPG', url=str(member.guild_avatar.replace(size=4096, format='jpg')))
            )

            return await ctx.reply(embed=embed, view=view)
        

    @commands.command(
        name='banner',
        aliases=['userbanner'],
        description="get the mentioned user's banner",
        brief="banner [user]",
        help="banner @glory#0007",
    )
    async def banner(self, ctx: Context, user: Optional[Union[discord.Member, discord.User]] = commands.Author):

        user = await self.bot.fetch_user(user.id)
        if not user.banner:
            return await ctx.send_error("that user doesn't have a **banner**")

        async with ctx.handle_response():

            embed = discord.Embed(
                color=await utils.dominant_color(user.banner), 
                title=f"{user.name}'s banner",
                url=user.banner.url
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=user.banner)

            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='WEBP', url=str(user.banner.replace(size=4096, format='webp')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='PNG', url=str(user.banner.replace(size=4096, format='png')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='JPG', url=str(user.banner.replace(size=4096, format='jpg')))
            )

            return await ctx.reply(embed=embed, view=view)


    @commands.command(
        name='hex',
        aliases=['color'],
        description='get information on the provided base hex code',
        brief='hex <member/role/hex/image>',
        help='hex #0000FF'
    )
    async def _hex(self, ctx: Context, source: Optional[Union[discord.Member, discord.Role, str]] = None):
        
        async with ctx.handle_response():
            
            if source is None:
                if not ctx.message.attachments:
                    return await ctx.send_help()

                hexx = hex(await utils.dominant_color(ctx.message.attachments[0].url))[2:]
            else:
                if isinstance(source, (discord.Member, discord.Role)):
                    hexx = '000000' if hex(source.color.value)[2:] == '0' else hex(source.color.value)[2:]
                else:
                    if 'http' in source and len(source.split()) == 1:
                        try:
                            hexx = hex(await utils.dominant_color(source))[2:]
                        except:
                            return await ctx.send_error('please provide a **valid** image')
                    else:
                        if len(source) > 6:
                            return await ctx.send_error('please provide a **valid** hex')
                            
                        if source in ('blue', 'blurple', 'brand_green', 'brand_red', 'dark_blue', 'dark_gold', 'dark_gray', 'dark_green', 'dark_grey', 'dark_magenta', 'dark_orange', 'dark_purple', 'dark_red', 'dark_teal', 'dark_theme', 'darker_gray', 'darker_grey', 'fuchsia', 'gold', 'green', 'greyple', 'light_gray', 'light_grey', 'lighter_gray', 'lighter_grey', 'magenta', 'og_blurple', 'orange', 'purple', 'random', 'red', 'teal', 'yellow'):
                            hexx = hex(getattr(discord.Color, source)().value)[2:]

                        hexx = source
            
            try:
                data = await self.bot.session.get(f"https://api.alexflipnote.dev/colour/{hexx.strip('#')}")
            except:
                return await ctx.send_error('failed to get information on that hex')

            shades = ', '.join(data['shade'][:4])
            hexx = data['hex']['string']
            rgb = data['rgb']['string']
            name = data['name']
            image = await utils.file(data['images']['square'], 'vile_hex.png')
            grad = await utils.file(data['images']['gradient'], 'vile_hexgradient.png')
            brightness = data['brightness']
            
            embed = discord.Embed(color=int(hexx.strip('#'), 16))
            embed.set_author(name=name, icon_url='attachment://vile_hex.png')
            embed.set_thumbnail(url='attachment://vile_hex.png')
            embed.set_image(url='attachment://vile_hexgradient.png')
            embed.add_field(name='RGB', value=rgb)
            embed.add_field(name='Hex', value=hexx)
            embed.add_field(name='Brightness', value=brightness)
            embed.add_field(name='Shades', value=f'```{shades}```')

            return await ctx.reply(embed=embed, files=[image, grad])


    @commands.group(
        name='server',
        aliases=['guild'],
        description='get information about the server',
        brief='server <sub command>',
        help='server icon',
        invoke_without_command=True
    )
    async def server(self, ctx: Context, invite: Optional[discord.Invite] = None):
        return await ctx.invoke(self.bot.get_command('serverinfo'), invite=invite)


    @server.command(
        name='icon',
        aliases=['avatar', 'pfp'],
        description="get the server's icon",
        brief='server icon [invite]',
        help='server icon heist'
    )
    async def server_icon(self, ctx: Context, invite: Optional[discord.Invite] = None):

        async with ctx.handle_response():
            guild = ctx.guild if not invite else invite.guild

            if not guild.icon:
                return await ctx.send_error(f"this server doesn't have an **icon**")

            embed = discord.Embed(
                color=await utils.dominant_color(guild.icon), 
                title=f"{guild.name}'s server icon",
                url=guild.icon.url
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=guild.icon)

            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='WEBP', url=str(guild.icon.replace(size=4096, format='webp')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='PNG', url=str(guild.icon.replace(size=4096, format='png')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='JPG', url=str(guild.icon.replace(size=4096, format='jpg')))
            )

            return await ctx.reply(embed=embed, view=view)


    @server.command(
        name='banner',
        description="get the server's banner",
        brief='server banner [invite]',
        help='server banner heist'
    )
    async def server_banner(self, ctx: Context, invite: Optional[discord.Invite] = None):

        async with ctx.handle_response():
            guild = ctx.guild if not invite else invite.guild

            if not guild.banner:
                return await ctx.send_error(f"this server doesn't have a **banner**")

            embed = discord.Embed(
                color=await utils.dominant_color(guild.banner), 
                title=f"{guild.name}'s server banner",
                url=guild.banner.url
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=guild.banner)

            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='WEBP', url=str(guild.banner.replace(size=4096, format='webp')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='PNG', url=str(guild.banner.replace(size=4096, format='png')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='JPG', url=str(guild.banner.replace(size=4096, format='jpg')))
            )

            return await ctx.reply(embed=embed, view=view)


    @server.command(
        name='splash',
        description="get the server's splash",
        brief='server splash [invite]',
        help='server splash heist'
    )
    async def server_splash(self, ctx: Context, invite: Optional[discord.Invite] = None):

        async with ctx.handle_response():
            guild = ctx.guild if not invite else invite.guild

            if not guild.splash:
                return await ctx.send_error(f"this server doesn't have a **splash**")

            embed = discord.Embed(
                color=await utils.dominant_color(guild.splash), 
                title=f"{guild.name}'s server splash",
                url=guild.splash.url
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_image(url=guild.splash)

            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='WEBP', url=str(guild.splash.replace(size=4096, format='webp')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='PNG', url=str(guild.splash.replace(size=4096, format='png')))
            )
            view.add_item(
                discord.ui.Button(style=discord.ButtonStyle.link, label='JPG', url=str(guild.splash.replace(size=4096, format='jpg')))
            )

            return await ctx.reply(embed=embed, view=view)


    @commands.command(
        name='servericon',
        aliases=['serverpfp'],
        description="get the server's icon",
        brief='servericon [invite]',
        help='servericon heist'
    )
    async def servericon(self, ctx: Context, invite: Optional[discord.Invite] = None):
        return await ctx.invoke(self.bot.get_command('server icon'), invite=invite)

    @commands.command(
        name='serverbanner',
        description="get the server's banner",
        brief='serverbanner [invite]',
        help='serverbanner heist'
    )
    async def serverbanner(self, ctx: Context, invite: Optional[discord.Invite] = None):
        return await ctx.invoke(self.bot.get_command('server banner'), invite=invite)


    @commands.command(
        name='serversplash',
        description="get the server's splash",
        brief='serversplash [invite]',
        help='serversplash heist'
    )
    async def serversplash(self, ctx: Context, invite: Optional[discord.Invite] = None):
        return await ctx.invoke(self.bot.get_command('server splash'), invite=invite)


    @commands.command(
        name='boosters',
        aliases=['boosterlist'],
        description="show a list of the server's boosters"
    )
    async def boosters(self, ctx: Context):

        embed = discord.Embed(color=self.bot.color, title=f'Boosters in {ctx.guild.name}', description=list()) 
        for booster in reversed(sorted(ctx.guild.premium_subscribers, key=lambda b: b.premium_since)):
            embed.description.append(f"{booster.mention}   \u2022   {discord.utils.format_dt(booster.premium_since, style='R')}")

        return await ctx.paginate(embed)


    @commands.command(
        name='vanity',
        description='check if a vanity is available',
        brief='vanity <vanity>',
        help='vanity heist'
    )
    async def vanity(self, ctx: Context, vanityy: str):

        await ctx.typing()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://discord.com/api/v10/invites/{vanityy}',
                proxy=None
            ) as x:
                if x.status == 200:
                    return await ctx.send_error(f'vanity **{vanityy}** is taken')
                elif x.status == 404:
                    return await ctx.send_success(f'vanity **{vanityy}** is available')


    @commands.command(
        name='roleinfo',
        aliases=['rinfo', 'ri'],
        description='view information about the provided role',
        brief='roleinfo <role>',
        help='roleinfo star'
    )
    async def roleinfo(self, ctx: Context, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')
        
        rolecolor = str(hex(role.color.value)).replace('0x', '')
        if rolecolor == '0':
            rolecolor = 'b9bbbe'

        data = await self.bot.session.get(f"https://api.alexflipnote.dev/colour/{rolecolor}")
        image = data['images']['square']
        color = data['hex']['string']

        embed = discord.Embed(color=int(color.strip('#'), 16), title=f'{role.name} ( {role.id} )')
        embed.set_thumbnail(url=image)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.add_field(
            name=f'{self.bot.dash} Created',
            value=f"{self.bot.reply} {discord.utils.format_dt(role.created_at, style='R')}"
        )
        embed.add_field(
            name=f'{self.bot.dash} Members',
            value=f'{self.bot.reply} {len(role.members)}'
        )
        embed.add_field(
            name=f'{self.bot.dash} Hoisted',
            value=f"{self.bot.reply} {'true' if role.hoist else 'false'}"
        )
        embed.add_field(
            name=f'{self.bot.dash} Color',
            value=f'{self.bot.reply} {color}'
        )
        embed.add_field(
            name=f'{self.bot.dash} Mentionable',
            value=f"{self.bot.reply} {'true' if role.mentionable else 'false'}"
        )
        embed.add_field(
            name=f'{self.bot.dash} Managed',
            value=f"{self.bot.reply} {'true' if role.is_bot_managed() else 'false'}"
        )

        permissions = 'No Permissions'
        if role.permissions.administrator:
            permissions = 'Administrator'
        elif role.permissions.create_instant_invite:
            permissions = 'Create Invite'

        position = f'Position: {role.position}'
        dangerous = 'Dangerous: false'
        if permissions == 'Administrator':
            dangerous = 'Dangerous: true'

        embed.set_footer(text=f'{permissions}   \u2022   {position}   \u2022   {dangerous}')

        return await ctx.reply(embed=embed)


    @commands.command(
        name='joinposition',
        aliases=['joinpos'],
        description='view your join position',
        brief='joinposition [member]',
        help='joinposition @glory#0007'
    )
    async def joinposition(self, ctx: Context, member: discord.Member = commands.Author):

        join_position = utils.ordinal(sorted(ctx.guild.members, key=lambda m: m.joined_at).index(member) + 1)
        return await ctx.send_success(f'{member.name} is the **{join_position}** member')
        

    @commands.command(
        name='roles',
        description="show a list of the server's roles"
    )
    async def roles(self, ctx: Context):

        if not ctx.guild.roles:
            return await ctx.send_error(f"there aren't any **roles** in {ctx.guild.name}")
            
        embed = discord.Embed(color=self.bot.color, title=f'Roles in {ctx.guild.name}', description=list())
        for role in reversed(ctx.guild.roles[1:]):
            embed.description.append(f'{role.mention}   \u2022   {len(role.members):,} members')

        return await ctx.paginate(embed)


    @commands.command(
        name='emojis',
        aliases=['emotes'],
        description="show a list of the server's emojis"
    )
    async def emojis(self, ctx: Context):

        if not ctx.guild.emojis:
            return await ctx.send_error(f"there aren't any **emojis** in {ctx.guild.name}")
            
        embed = discord.Embed(color=self.bot.color, title=f'Emojis in {ctx.guild.name}', description=list())
        for emoji in ctx.guild.emojis:
            embed.description.append(f'{emoji}: **{emoji.name}** [`{emoji.id}`]({emoji.url})')

        return await ctx.paginate(embed)


    @commands.command(
        name='bots',
        description="show a list of the server's bots"
    )
    async def bots(self, ctx: Context):

        if not [m for m in ctx.guild.members if m.bot]:
            return await ctx.send_error(f"there aren't any **bots** in {ctx.guild.name}")
            
        embed = discord.Embed(color=self.bot.color, title=f'Bots in {ctx.guild.name}', description=list())
        for member in ctx.guild.members:
            if member.bot:
                embed.description.append(f'{member.mention}: **{member}** ( `{member.id}` )')

        return await ctx.paginate(embed)


    @commands.command(
        name='bans',
        description="show a list of the server's banned members",
        extras={'permissions': 'ban members'}
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def bans(self, ctx: Context):

        if not [b async for b in ctx.guild.bans(limit=1)]:
            return await ctx.send_error(f"there aren't any **bans** in {ctx.guild.name}")
            
        embed = discord.Embed(color=self.bot.color, title=f'Bans in {ctx.guild.name}', description=list())
        async for ban in ctx.guild.bans(limit=500):
            embed.description.append(f'{ban.user.mention}: **{ban.user}** ( `{ban.user.id}` )')

        return await ctx.paginate(embed)


    @commands.command(
        name='inrole',
        aliases=['members'],
        description="show a list of a role's members"
    )
    async def inrole(self, ctx: Context, *, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if not role.members:
            return await ctx.send_error(f"there aren't any **members** in `{role.name}`")
            

        embed = discord.Embed(color=self.bot.color, title=f'Members in {role.name}', description=list())
        for member in role.members:
            embed.description.append(f'{member.mention}: **{member}** ( `{member.id}` )')

        return await ctx.paginate(embed)


    @commands.command(
        name='invites',
        description="show a list of the server's invites"
    )
    async def invites(self, ctx: Context):

        if not await ctx.guild.invites():
            return await ctx.send_error(f"there aren't any **invites** in {ctx.guild.name}")
            
        embed = discord.Embed(color=self.bot.color, title=f'Invites in {ctx.guild.name}',description=list())
        for invite in await ctx.guild.invites():
            embed.description.append(f'[discord.gg/{invite.code}]({invite.url}): **{invite.inviter}** ({invite.uses} uses)')

        return await ctx.paginate(embed)


    @commands.command(
        name='boosters',
        description="show a list of the server's boosters"
    )
    async def boosters(self, ctx: Context):

        if not ctx.guild.premium_subscribers:
            return await ctx.send_error(f"there aren't any **boosters** in {ctx.guild.name}")

        embed = discord.Embed(color=self.bot.color, title=f'Boosters in {ctx.guild.name}', description=list())
        for booster in reversed(sorted(ctx.guild.premium_subscribers, key=lambda b: b.premium_since)):
            embed.description.append(f"{booster.mention}: **{booster}** ( {discord.utils.format_dt(booster.premium_since, style='R')} )")

        return await ctx.paginate(embed)


    @commands.command(
        name='firstmessage',
        aliases=['firstmsg'],
        description='get a reference to the first message in the channel'
    )
    async def firstmessage(self, ctx: Context):

        async for message in ctx.channel.history(limit=1, oldest_first=True):
            return await ctx.reply(
                view=discord.ui.View().add_item(
                    discord.ui.Button(style=discord.ButtonStyle.link, label='first message', url=message.jump_url)
                )
            )


    @commands.command(
        name='image',
        aliases=['googleimagesearch', 'img'],
        description='search for images on google',
        brief='image <query>',
        help='image lucki'
    )
    async def image(self, ctx: Context, *, query: str):

        async with ctx.handle_response():
            
            safe = False
            embeds = list()
            num = 0

            if await self.bot.db.fetchval('SELECT state FROM safesearch WHERE guild_id = %s', ctx.guild.id) == True:
                safe = True
            
            cached_value = await self.bot.redis.get(f'google_images:{query}')
            
            if cached_value is not None:
                data = orjson.loads(cached_value)
            
            else:
                data = await RivalAPI(self.bot.rival_api).google_images(query, safe=safe) # self.bot.vile_api.images(query, safe=repr(safe).lower())
                if not data.__dict__['dic']['results']:
                    return await ctx.send_error('safe search is **enabled** for this server')
                        
                data = data.__dict__['dic']['results']
                await self.bot.redis.set(f'google_images:{query}', orjson.dumps(data), ex=604800)

            random.shuffle(data)
            for result in data:
                num += 1
                url = result['url']
                title = result['title']
                source = result['source']

                embed = discord.Embed(color=self.bot.color, title=f'{title} ({source})', url=url)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                embed.set_image(url=url)
                embed.set_footer(text=f"Page {num}/{len(data)}   \u2022   Google Images   \u2022   Safe: {'true' if safe else 'false'}")

                embeds.append(embed)

            return await ctx.paginate(embeds)


    @commands.command(
        name='google',
        aliases=['googlesearch', 'g'],
        description='search for results on google',
        brief='google <query>',
        help='google lucki'
    )
    async def google(self, ctx: Context, *, query: str):

        async with ctx.handle_response():
            
            embeds = list()
            num = 0

            cached_value = await self.bot.redis.get(f'google_search:{query}')
            
            if cached_value is not None:
                data = orjson.loads(cached_value)
            
            else:
                data = await RivalAPI(self.bot.rival_api).google_search(query) # self.bot.vile_api.images(query, safe=repr(safe).lower())
                if not data.__dict__['dict']['results']:
                    return await ctx.send_error('safe search is **enabled** for this server')
                        
                data = data.__dict__['dict']['results']
                await self.bot.redis.set(f'google_search:{query}', orjson.dumps(data), ex=604800)

            random.shuffle(data)
            for result in data:
                num += 1
                url = result['link']
                title = result['title']
                description = result['snippet']

                embed = discord.Embed(color=self.bot.color, title=f'{title} ({url})', url=url, description=description)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                embed.set_footer(text=f"Page {num} / {len(data)}   \u2022   Google Search   \u2022   Safe: undefined")

                embeds.append(embed)

            return await ctx.paginate(embeds)


    @commands.command(
        name='names',
        aliases=['aliases', 'pastnames', 'namehistory', 'previousnames'],
        description='view your previous names',
        brief='names <user>',
        help='names @glory#0007'
    )
    async def names(self, ctx: Context, user: Optional[Union[discord.Member, discord.User]] = commands.Author):

        async with ctx.handle_response():
            embed = discord.Embed(color=self.bot.color, title=f"{user}'s previous names", description=list())

            names = await self.bot.db.execute('SELECT name, timestamp FROM names WHERE user_id = %s ORDER BY timestamp DESC', user.id)
            if not names:
                return await ctx.send_error(f'no previously recorded names for {user.mention}')

            for name, timestamp in names:
                embed.description.append(f"{name}   \u2022   {discord.utils.format_dt(datetime.fromtimestamp(timestamp), style='R')}")

            return await ctx.paginate(embed)
    

    @commands.command(
        name='clearnames',
        aliases=['cn'],
        description='clear your name history'
    )
    async def clearnames(self, ctx: Context):

        if not await self.bot.db.execute('SELECT * FROM names WHERE user_id = %s', ctx.author.id):
            return await utils.send_error(f'no previously recorded names for {ctx.author.name}')

        await self.bot.db.execute('DELETE FROM names WHERE user_id = %s', ctx.author.id)
        return await ctx.send_success('successfully **cleared** all your previous names')


    @commands.command(
        name='urbandictionary',
        aliases=['urban', 'ud'],
        description='get the definition of a word from urban dictionary',
        brief='urbandictionary <word>',
        help='urbandictionary vile'
    )
    async def urbandictionary(self, ctx: Context, *, word: str):

        await ctx.typing()

        if len(word) > 50:
            return await ctx.send_error('please provide a **valid** word under 50 chars')
        
        data = await self.bot.session.get('http://api.urbandictionary.com/v0/define', params={'term': word})
        
        embeds = list()
        num = 0
        if len(data['list']) == 0:
            return await ctx.send_error(f'no results found for **`{word}`**')

        for i in data['list'][:3]:
            num += 1
            embed = discord.Embed(color=self.bot.color, description=word)
            embed.set_author(name=ctx.author.name,  icon_url=ctx.author.display_avatar)
            if i['definition'] and i['example']:
                embed.add_field(
                    name=f'{self.bot.dash} Definition',
                    value=utils.multi_replace(i['definition'], {'[': '**', ']': '**'}, once=False),
                    inline=False,
                )
                embed.add_field(
                    name=f'{self.bot.dash} Example',
                    value=utils.multi_replace(i['example'], {'[': '**', ']': '**'}, once=False),
                )
                embed.set_footer(text=f"Page {num} / 3 ; 👍 {i['thumbs_up']} 👎 {i['thumbs_down']}")
            
            embeds.append(embed)

        return await ctx.paginate(embeds)


    @commands.command(
        name='cryptocurrency',
        aliases=['crypto'],
        description='view the price of the provided currency',
        brief='cryptocurrency <symbol>',
        help='cryptocurrency btc'
    )
    async def cryptocurrency(self, ctx: Context, symbol: str):
        
        await ctx.typing()

        data = await self.bot.session.get(f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD,EUR,GBP')

        embed = discord.Embed(
            color=self.bot.color,
            title=f"Current {symbol.upper()} Value",
            description=f"1 Single {symbol.upper()}",
        )
        embed.add_field(name='USD', value=f"{data['USD']:,}", inline=True)
        embed.add_field(name='GBP', value=f"{data['GBP']:,}", inline=True)
        embed.add_field(name='EUR', value=f"{data['EUR']:,}", inline=True)

        return await ctx.reply(embed=embed)


    @commands.command(
        name='recentjoins',
        aliases=['rj'],
        description='see the most recent joins'
    )
    async def recentjoins(self, ctx: Context):

        joins = sorted(list(utils.filter(ctx.guild.members, key=lambda m: time.time() - m.joined_at.timestamp() < 86400)), key=lambda m: m.joined_at)
        if not joins:
            return await ctx.send_error('there are no **recent** joins')

        embed = discord.Embed(color=self.bot.color, title=f'Recent joins in {ctx.guild.name}', description=list())
        for member in reversed(joins):
            embed.description.append(f"{member.mention}: **{member}** ( {discord.utils.format_dt(member.joined_at, style='R')} )")

        return await ctx.paginate(embed)


    @commands.command(
        name='lyrics',
        description='get the lyrics of a song',
        brief='lyrics <song name>',
        help='lyrics new drank'
    )
    async def lyrics(self, ctx: Context, *, song: str):
        
        async with ctx.handle_response():
            data = await self.bot.session.get('https://api.popcat.xyz/lyrics', params={'song': song.replace(' ', '+')})

        try:
            parts = text_creator(data['lyrics'])
        except:
            return await ctx.send_error('failed to get the **lyrics** for that song')
        else:
            embeds = list()
            for part in parts:
                embed = discord.Embed(color=self.bot.color, description=part)
                embed.set_footer(text=data['artist'])
                embed.set_author(name=data['title'], icon_url=data['image'])
                embed.set_image(url=data['image'])
                embed.set_thumbnail(url=data['image'])
                embeds.append(embed)

            return await ctx.paginate(embeds)


    @commands.command(
        name='bio',
        description="get a user's bio",
        brief='bio <user>',
        help='bio @glory#0007'
    )
    async def bio(self, ctx: Context, user: Union[discord.Member, discord.User] = commands.Author):

        async with ctx.handle_response():
            data = await self.bot.vile_api.user(user.id)

            if data.get('code') == 10013:
                return await ctx.send_error("couldn't fetch that user")

            if not data['bio']:
                return await ctx.send_error("that user doesn't have a bio")

            embed = discord.Embed(color=await utils.dominant_color(user.display_avatar), description=data['bio'])
            embed.set_author(name=user, icon_url=user.display_avatar)

            return await ctx.reply(embed=embed)


    @commands.command(
        name='youtube',
        aliases=['yt'],
        description='search for a youtube video',
        brief='youtube <query>',
        help='youtube nuclear bomb'
    )
    async def youtube(self, ctx: Context, *, query: str):
        
        async with ctx.handle_response():
            
            data = await utils.youtube_search(query)
            if data is None:
                return await ctx.send_error("couldn't find results for your search")
            
            return await ctx.reply(data)


    @commands.group(
        name='rtfm',
        aliases=['rtfd'],
        description='get the documentation for a discord.py entity',
        brief='rtfm <sub command>',
        help='rtfm latest on_audit_log_entry_create',
        invoke_without_command=True
    )
    async def rtfm(self, ctx: Context, *, entity: str):
        return await self.rtfm.do_rtfm(ctx, 'stable', entity)


    @rtfm.command(
        name='latest',
        aliases=['master'],
        description='get the documentation for a discord.py entity (master)',
        brief='rtfm latest <entity>',
        help='rtfm latest on_audit_log_entry_create',
        invoke_without_command=True
    )
    async def rtfm_latest(self, ctx: Context, *, entity: str):
        return await self.rtfm.do_rtfm(ctx, 'latest', entity)


    @rtfm.command(
        name='python',
        aliases=['py'],
        description='get the documentation for a python entity',
        brief='rtfm py <entity>',
        help='rtfm py asyncio.to_thread',
        invoke_without_command=True
    )
    async def rtfm_python(self, ctx: Context, *, entity: str):
        return await self.rtfm.do_rtfm(ctx, 'python', entity)


async def setup(bot: commands.Bot):
    await bot.add_cog(Information(bot))
