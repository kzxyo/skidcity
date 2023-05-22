import imghdr
import discord, os, sys, asyncio, datetime, textwrap, pathlib, traceback, json, time, random, humanize, typing, timeago
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class info(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        #
        self.done = utils.emoji("done")
        self.fail = utils.emoji("fail")
        self.warn = utils.emoji("warn")
        self.reply = utils.emoji("reply")
        self.dash = utils.emoji("dash")
        #
        self.success = utils.color("done")
        self.error = utils.color("fail")
        self.warning = utils.color("warn")
        #
        self.av = "https://cdn.discordapp.com/attachments/989422588340084757/1008195005317402664/vile.png"

    @commands.hybrid_command(aliases=["bi", "about", "info"])
    async def botinfo(self, ctx):

        async with ctx.channel.typing():
            system = {
                "os": "Windows 11 Pro",
                # "storage": "2TB SSD (1TB Samsung SSD x2)",
                "memory": "64GB DDR4",
                # "graphics": "NVIDIA GeForce RTX 3070, 8GB",
                "processing": "AMD Ryzen 7",
            }

            bot = {
                "guilds": f"{len(self.bot.guilds):,}",
                "users": f"{sum(g.member_count for g in self.bot.guilds):,}",
                "commands": f"{len(set(self.bot.walk_commands())):,}",
                "modules": len(
                    [
                        f
                        for f in os.listdir("cogs")
                        if "pycache" not in f
                        and "events" not in f
                        and "owner" not in f
                        and "contextmenu" not in f
                        and "logging" not in f
                    ]
                ),
                "processed_cmds": f"{utils.read_json('cache')['cmds']:,}",
                "dev": "[**glory#0007**](https://discord.com/users/812126383077457921)",
            }

            import psutil

            embed = discord.Embed(color=0x2F3136)
            embed.description = f"```.           Vile Statistics```\nDeveloped & Maintained by {bot['dev']}\nProcessed {bot['processed_cmds']} commands\nConsuming {psutil.cpu_percent()}% & {utils.size(psutil.Process().memory_full_info().rss)}/{utils.size(psutil.virtual_memory().total)}\n"  # \n    \n   \n  \n   Registered {bot['commands']} & processed over {bot['processed_cmds']} commands\n    Running on Python v3.10.4 on win32 x64\n    Consuming 0.{random.randint(50, 99)}% & {random.randint(50, 65)}.{random.randint(10, 99)}/15,890 MB\n```"""
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(
                name=f"{utils.read_json('emojis')['dash']} Stats",
                value=f"```toml\n[users] {bot['users']}\n\n[guilds] {bot['guilds']}\n\n[global] {bot['processed_cmds']}\n\n```",
            )
            embed.add_field(
                name=f"{utils.read_json('emojis')['dash']} Channels",
                value=f"```toml\n[total]   {len(set(self.bot.get_all_channels()))}\n\n[text]    {sum([len(guild.text_channels) async for guild in utils.aiter(self.bot.guilds)])}\n\n[voice]   {sum([len(guild.voice_channels) async for guild in utils.aiter(self.bot.guilds)])}```",
            )
            embed.add_field(
                name=f"{utils.read_json('emojis')['dash']} Client",
                value=f"```toml\n[commands] {bot['commands']}\n\n[modules]  {bot['modules']}\n\n[ping]    {int(round(self.bot.latency * 1000) / 11)}ms```",
            )

        await ctx.reply(
            embed=embed,
            view=discord.ui.View().add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="invite vile",
                    url="https://discord.com/api/oauth2/authorize?client_id=991695573965099109&permissions=8&scope=bot%20applications.commands",
                )
            ),
        )

    @commands.command(
        name='ping',
        aliases=['latency'],
        description='get the bot\'s latency in ms'
    )
    async def ping(self, ctx):

        start=int(time.time())
        await (await ctx.reply(
            f'ws: **`{round(self.bot.latency * 1000)}`**')).edit(
            content=f'ws: **`{round(self.bot.latency * 1000)}`**, rest: **`{round((time.time()-start)*1000)}`**')

    @commands.hybrid_command()
    async def uptime(self, ctx):

        x = f"vile has been up for {utils.moment(self.bot.uptime).replace('ago', '')}"
        await ctx.reply(x)

    @commands.hybrid_command(aliases=["creds", "credit", "credits"])
    #
    async def _credits(self, ctx):

        embed = (
            discord.Embed(
                color=utils.color("main"),
                title="Vile Credit Menu",
                timestamp=datetime.now(),
            )
            .set_footer(
                text="vile")
            .set_thumbnail(url=self.bot.user.avatar)
        )
        embed.add_field(
            name=f"{utils.read_json('emojis')['dash']} Credits",
            value=f"{self.reply} `1` ***{await self.bot.fetch_user(812126383077457921)}*** - Developer & Owner (`812126383077457921`)\n{self.reply} `2` ***{await self.bot.fetch_user(979978940707930143)}*** - Owner (`979978940707930143`)\n{self.reply} `3` ***{await self.bot.fetch_user(714703136270581841)}*** - Owner (`714703136270581841`)",
        )
        view = discord.ui.View().add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.grey, label="owners", disabled=True
            )
        )
        await ctx.reply(embed=embed, view=view)

    @commands.hybrid_command(name="help", aliases=["h"])
    async def _help(self, ctx):

        await ctx.typing()
        num = 1
        totalcogs = len(
            [
                self.bot.get_cog(cog)
                async for cog in utils.aiter(self.bot.cogs)
                if self.bot.get_cog(cog).get_commands()
                and self.bot.get_cog(cog).qualified_name not in ["Jishaku", "owner"]
            ]
        )
        embeds = []
        embeds.append(
            discord.Embed(
                color=0x2F3136,
            )
            .set_author(name="Vile Cmd Menu", icon_url=self.bot.user.avatar)
            .set_thumbnail(url=self.bot.user.avatar)
            .add_field(
                name=f"{utils.read_json('emojis')['dash']} **Recent Updates**",
                value=f"{self.reply} **[-]** removed some useless cmds\n{self.reply} **[+]** added transparent to image module",
            )
            .add_field(
                name=f"{self.dash} Links",
                value=f"{self.reply} [**invite**](https://discord.com/api/oauth2/authorize?client_id=991695573965099109&permissions=8&scope=bot%20applications.commands) . [**support**](https://tiny.cc/vilecord) . [**docs**](https://tiny.cc/vilebot)",
                inline=False,
            )
            .set_footer(
                text=f"{num}/{totalcogs}",
                icon_url=None,
            )
        )

        async for cog in utils.aiter(self.bot.cogs):
            cog = self.bot.get_cog(cog)
            if cog.qualified_name in ["Jishaku", "owner"]:
                continue
            if cog.get_commands():
                num += 1
                embeds.append(
                    discord.Embed(
                        color=0x2F3136,
                        description=f"\n```YAML\n{', '.join([cmd.name.replace('_', '') async for cmd in utils.aiter(cog.get_commands()) if 'help' not in cmd.name])}\n\n```",
                    )
                    .set_author(name=cog.qualified_name, icon_url=self.bot.user.avatar)
                    .set_footer(
                        text=f"{num}/{totalcogs}",
                        icon_url=None,
                    )
                )

        from modules import paginator as pg

        paginator = pg.Paginator(self.bot, embeds, ctx, timeout=30, invoker=None)
        paginator.add_button("first", emoji=utils.emoji("firstpage"))
        paginator.add_button("prev", emoji=utils.emoji("prevpage"))
        paginator.add_button("next", emoji=utils.emoji("nextpage"))
        paginator.add_button("last", emoji=utils.emoji("lastpage"))
        paginator.add_button("goto", emoji=utils.emoji("choosepage"))
        await paginator.start()
        # await ctx.reply(f'{ctx.author.mention}: <https://tiny.cc/vilehelp>, join the discord server @ <https://tiny.cc/vilecord>')

    @commands.hybrid_command(aliases=["ui", "whois"])
    async def userinfo(self, ctx, user: discord.Member | discord.User = None):

        try:
            await ctx.typing()
            user = ctx.author if not user else user
            x = await self.bot.get_user_data(user)
            if x.premium_guild_since != None:
                boosted = round(datetime.fromisoformat(x["premium_since"]).timestamp())
            else:
                boosted = "N/A"

            created = round(user.created_at.timestamp())
            try:
                joined = round(user.joined_at.timestamp())
            except:
                joined = None
            try:
                members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
                jp = int(members.index(user) + 1)
                joinpos = f"\njoin pos: {utils.ordinal(jp)}"
            except:
                joinpos = ""

            devices = []
            try:
                if str(user.web_status) != "offline":
                    devices.append("web")
                if str(user.mobile_status) != "offline":
                    devices.append("mobile")
                if str(user.desktop_status) != "offline":
                    devices.append("desktop")
            except:
                pass

            badges = []
            emojis = {
                "nitro": "<:vile_nitro:1022941557541847101>",
                "hsbrilliance": "<:vile_hsbrilliance:1022941561392209991>",
                "hsbravery": "<:vile_hsbravery:1022941564349194240>",
                "hsbalance": "<:vile_hsbalance:1022941567318765619>",
                "bhunter": "<:vile_bhunter:991776532227969085>",
                "bhunterplus": "<:vile_bhunterplus:991776477278388386>",
                "cmoderator": "<:vile_cmoderator:1022943277340692521>",
                "esupporter": "<:vile_esupporter:1022943630945685514>",
                "dev": "<:vile_dev:1042082778629537832>",
                "partner": "<:vile_partner:1022944710895075389>",
                "dstaff": "<:vile_dstaff:1022944972858720327>",
                "vbot": "<:vile_vbot:1022945560094834728>",
                "sboost": "<:vile_sboost:1022950372576342146>",
                "activedev": "<:vile_activedev:1043160384124751962>",
            }
            flags = user.public_flags
            ui = await self.bot.get_user_data(user)

            if ui.premium_since:
                badges.append(emojis["nitro"])
            if ui.premium_guild_since:
                badges.append(emojis["sboost"])

            flags = user.public_flags
            if flags.bug_hunter:
                badges.append(emojis["bhunter"])
            if flags.bug_hunter_level_2:
                badges.append(emojis["bhunterplus"])
            if flags.discord_certified_moderator:
                badges.append(emojis["cmoderator"])
            if flags.early_supporter:
                badges.append(emojis["esupporter"])
            if flags.hypesquad_balance:
                badges.append(emojis["hsbalance"])
            if flags.hypesquad_bravery:
                badges.append(emojis["hsbravery"])
            if flags.hypesquad_brilliance:
                badges.append(emojis["hsbrilliance"])
            if flags.partner:
                badges.append(emojis["partner"])
            if flags.staff:
                badges.append(emojis["dstaff"])
            if flags.verified_bot:
                badges.append(emojis["vbot"])
            if flags.verified_bot_developer:
                badges.append(emojis["dev"])
            if "ACTIVE_DEVELOPER" in ui["public_flags_array"]:
                badges.append(emojis["activedev"])

            # roles = ', '.join([role.mention async for role in utils.aiter(user.roles)][::-1])

            try:
                roles = list(user.roles)
                roles.reverse()
                rolestr = ""
                for role in roles:
                    if role.name == "@everyone":
                        rolestr += "@everyone"
                    else:
                        rolestr += role.mention + ", "

                roles = rolestr
            except:
                roles = None

            x = await self.bot.fetch_user(user.id)
            banner = x.banner
            tfavatar = False
            tfbanner = True if not banner else False

            guilds = None
            try:
                guilds = len([g for g in user.mutual_guilds])
            except:
                pass

            stat = "none"
            try:
                stat = user.activity.name
            except:
                pass

            vc = None
            try:
                for g in user.mutual_guilds:
                    try:
                        x = g.get_member(user.id)
                        if not x.voice.channel:
                            continue
                        vc = f"\nin vc **{x.voice.channel.name}** with **{len(x.voice.channel.members)-1}** others"
                        break
                    except:
                        pass
            except:
                pass

            x = None
            if badges:
                x = f" {' '.join(badges)}"

            perm = ""
            try:
                if (
                    user.guild_permissions.create_instant_invite
                    and not user.guild_permissions.administrator
                ):
                    perm = "create invite"
                else:
                    perm = "administrator"
            except:
                pass

            embed = discord.Embed(
                color=utils.color("main"), title=f"{user}{x if x != None else ''}"
            )
            embed.set_author(
                name=f"{user.name} ( {user.id} )", icon_url=user.display_avatar
            )
            embed.set_thumbnail(url=ctx.author.display_avatar)
            embed.description = (
                f"{perm if perm else ''}{joinpos if joinpos else ''}{vc if vc else ''}"
            )
            if guilds:
                embed.set_footer(text=f"{guilds} mutual servers")
            if devices:
                embed.add_field(
                    name=f"{self.dash} presence", value=f"{self.reply} {user.status}"
                )
            embed.add_field(
                name=f"{self.dash} devices [{len(devices)}]",
                value=f"{self.reply} {'none' if not devices else ', '.join(devices)}",
            )
            embed.add_field(name=f"{self.dash} status", value=f"{self.reply} {stat}")
            embed.add_field(
                name=f"{self.dash} created", value=f"{self.reply} <t:{created}:D>"
            )
            if joined:
                embed.add_field(
                    name=f"{self.dash} joined", value=f"{self.reply} <t:{joined}:D>"
                )
            embed.add_field(
                name=f"{self.dash} boosted",
                value=f"{self.reply} {f'<t:{boosted}:D>' if boosted != 'N/A' else boosted}",
            )
            if roles:
                embed.add_field(
                    name=f"{self.dash} roles [{len(user.roles)}]",
                    value=roles,
                    inline=False,
                )

            b1 = discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="avatar",
                url=user.display_avatar,
                disabled=tfavatar,
            )
            b2 = discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="banner",
                url=user.banner,
                disabled=tfbanner,
            )
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="avatar",
                    url=str(user.display_avatar),
                    disabled=tfavatar,
                )
            )
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="banner",
                    url=f"{'https://discord.com' if not banner else str(banner)}",
                    disabled=tfbanner,
                )
            )
            await ctx.reply(embed=embed, view=view)

        except Exception as e:
            return  # await ctx.reply(traceback.format_exc())

    @commands.command(
        name='serverinfo',
        aliases=['guildinfo', 'sinfo', 'si'],
        description='get info about the current or provided server',
        syntax=',serverinfo [invite]',
        example=',serverinfo or ,serverinfo heist'
    )
    async def serverinfo(self, ctx, invite: typing.Optional[discord.Invite]=None):
        
        guild = ctx.guild if not invite else invite.guild
        
        embed=discord.Embed(
            color=self.bot.color,
            title=guild.name
        )
        view=discord.ui.View()
        owner_parts=[]
        other_parts=[]
        boost_parts=[]
        member_parts=[]
        channel_parts=[]
        activity_parts=[]
        platform_parts=[]
        
        dicon, icon = (
            str(guild.icon)=='None',
            'https://rival.rocks' if not guild.icon else str(guild.icon)
        )
        
        dbanner, banner = (
            str(guild.banner) == 'None',
            'https://rival.rocks' if not guild.banner else str(guild.banner)
        )
            
        dsplash, splash = (
            str(guild.splash) == 'None',
            'https://rival.rocks' if not guild.splash else str(guild.splash)
        )
        
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.url,
                label='icon',
                url=icon,
                disabled=dicon
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.url,
                label='banner',
                url=banner,
                disabled=dbanner
            )
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.url,
                label='splash',
                url=splash,
                disabled=dsplash
            )
        )
        
        partnered = 'PARTNERED' in guild.features
        vanity = f'.gg/{guild.vanity_url_code if guild.vanity_url_code else None}'
        created=timeago.format(guild.created_at, datetime.now().astimezone())
        
        if isinstance(guild, discord.Guild):
            
            #variables
            boostcount=guild.premium_subscription_count
            boostercount=len(guild.premium_subscribers)
            boosttier=guild.premium_tier
            owner=guild.owner
            members=len(guild.members)
            humans=len([m for m in guild.members if not m.bot])
            bots=len([m for m in guild.members if m.bot])
            
            large = 'true' if guild.large else 'false'
            id=guild.id
            
            offline, online, idle, dnd = (
                len([m for m in guild.members if str(m.status) == 'offline']),
                len([m for m in guild.members if str(m.status) == 'online']),
                len([m for m in guild.members if str(m.status) == 'idle']),
                len([m for m in guild.members if str(m.status) == 'dnd'])
            )
            pc, web, phone = (
                len([m for m in guild.members if str(m.desktop_status) != 'offline']),
                len([m for m in guild.members if str(m.web_status) != 'offline']),
                len([m for m in guild.members if str(m.mobile_status) != 'offline'])
            )
            
            textchannels=len(guild.text_channels)
            voicechannels=len(guild.voice_channels)
            channels=textchannels+voicechannels
            roles=len(guild.roles[1:])
            emojis=len(guild.emojis)
            vlevel=str(guild.verification_level)
            
            owner_parts=[
                f'{self.reply} **mention:** {owner.mention} ( `{str(owner)}` )',
                f'{self.reply} {owner.id}'
            ]
            boost_parts=[
                f'{self.reply} **level:** {boosttier}',
                f'{self.reply} **boosters:** {boostercount}',
                f'{self.reply} **boosts:** {boostcount}'
            ]
            member_parts=[
                f'{self.reply} **total:** {members}',
                f'{self.reply} **humans:** {humans}',
                f'{self.reply} **bots:** {bots}'
            ]
            channel_parts=[
                f'{self.reply} **total:** {channels}',
                f'{self.reply} **text:** {textchannels}',
                f'{self.reply} **voice:** {voicechannels}'
            ]
            activity_parts=[
                f'{self.reply} **online:** {online}',
                f'{self.reply} **idle:** {idle}',
                f'{self.reply} **dnd:** {dnd}',
                f'{self.reply} **offline:** {offline}'
            ]
            platform_parts=[
                f'{self.reply} **desktop:** {pc}',
                f'{self.reply} **web:** {web}',
                f'{self.reply} **mobile:** {phone}'
            ]
            other_parts=[
                f'{self.reply} **roles:** {roles}',
                f'{self.reply} **emojis:** {emojis}',
                f'{self.reply} **verification:** {vlevel}'
            ]
            
            embed.add_field(
                name='owner',
                value='\n'.join(owner_parts)
            )
            embed.add_field(
                name='boost',
                value='\n'.join(boost_parts)
            )
            embed.add_field(
                name='members',
                value='\n'.join(member_parts)
            )
            embed.add_field(
                name='channels',
                value='\n'.join(channel_parts)
            )
            embed.add_field(
                name='platforms',
                value='\n'.join(platform_parts)
            )
            embed.add_field(
                name='activity',
                value='\n'.join(activity_parts)
            )
            embed.add_field(
                name='other',
                value='\n'.join(other_parts)
            )
            embed.description='\n'.join([
                f'{self.reply} **id:** {guild.id}',
                f'{self.reply} **created:** {created}'
            ])
            
        elif isinstance(guild, discord.PartialInviteGuild):
            
            #variables
            boostcount=guild.premium_subscription_count
            vlevel=str(guild.verification_level)
            
            embed.description='\n'.join([
                f'{self.reply} **id:** {guild.id}',
                f'{self.reply} **created:** {created}'
            ])
            embed.add_field(
                name='boost',
                value=f'{self.reply} **boosts:** {boostcount}'
            )
            embed.add_field(
                name='other',
                value=f'{self.reply} **verification:** {vlevel}'
            )
            
            
        if icon:
            embed.set_thumbnail(
                url=icon
            )
            
        if vanity:
            embed.set_footer(
                text=vanity,
                icon_url=None
            )
                
        await ctx.reply(embed=embed, view=view)

    @commands.hybrid_command(aliases=["mc"])
    async def membercount(self, ctx):

        total = ctx.guild.member_count
        humans = len([m async for m in utils.aiter(ctx.guild.members) if not m.bot])
        bots = len([m async for m in utils.aiter(ctx.guild.members) if m.bot])

        embed = discord.Embed(color=utils.color("main"), timestamp=datetime.now())
        embed.set_author(
            name=f"{ctx.guild.name}'s membercount", icon_url=ctx.guild.icon
        )
        embed.add_field(
            name=f"{self.dash} Members", value=f"{self.reply} {total:,}", inline=True
        )
        embed.add_field(
            name=f"{self.dash} Users", value=f"{self.reply} {humans:,}", inline=True
        )
        embed.add_field(
            name=f"{self.dash} Bots", value=f"{self.reply} {bots:,}", inline=True
        )

        await ctx.reply(embed=embed)

    @commands.hybrid_command()
    async def version(self, ctx):

        return await ctx.reply(
            embed=discord.Embed(
                color=utils.color("main"),
                description=f"{self.bot.user.mention}: vile ***v3.8.1***",
            )
        )

    @commands.hybrid_command(aliases=["inv"])
    async def invite(self, ctx):
        await ctx.reply(
            view=discord.ui.View().add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="invite vile",
                    url="https://discord.com/api/oauth2/authorize?client_id=991695573965099109&permissions=8&scope=bot%20applications.commands",
                )
            )
        )


async def setup(bot):

    await bot.add_cog(info(bot))
