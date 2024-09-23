from discord.ext.commands import Context, Bot as Bot
from discord.ext import commands
import discord, datetime, dateutil.parser, sys
from discord import Embed, TextChannel 
from discord.ui import Button, View
from patches.classes import Time, TimeConverter
from patches import functions

DISCORD_API_LINK = "https://discord.com/api/invite/"

class information(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.TimeConverter = TimeConverter

    def convert_datetime(self, date: datetime.datetime=None):
     if date is None: return None  
     month = f'0{date.month}' if date.month < 10 else date.month 
     day = f'0{date.day}' if date.day < 10 else date.day 
     year = date.year 
     minute = f'0{date.minute}' if date.minute < 10 else date.minute 
     if date.hour < 10: 
      hour = f'0{date.hour}'
      meridian = "AM"
     elif date.hour > 12: 
      hour = f'0{date.hour - 12}' if date.hour - 12 < 10 else f"{date.hour - 12}"
      meridian = "PM"
     else: 
      hour = date.hour
      meridian = "PM"  
     return f"{month}/{day}/{year} at {hour}:{minute} {meridian} ({discord.utils.format_dt(date, style='R')})" 

    @commands.command(aliases=["si"], description="show information about the server")
    async def serverinfo(self, ctx: Context):
        guild = ctx.guild        
        icon= f"[icon]({guild.icon.url})" if guild.icon is not None else "N/A"
        splash=f"[splash]({guild.splash.url})" if guild.splash is not None else "N/A"
        banner=f"[banner]({guild.banner.url})" if guild.banner is not None else "N/A"   
        desc=guild.description if guild.description is not None else ""
        embed = Embed(color=self.bot.color, title=f"{guild.name}", timestamp=datetime.datetime.now(), description=f"Server created on {self.convert_datetime(guild.created_at.replace(tzinfo=None))}\n{desc}")   
        embed.set_thumbnail(url=guild.icon)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Owner", value=f"{guild.owner.mention}\n{guild.owner}")
        embed.add_field(name="Members", value=f"**Users:** {len(set(i for i in guild.members if not i.bot))} ({((len(set(i for i in guild.members if not i.bot)))/guild.member_count) * 100:.2f}%)\n**Bots:** {len(set(i for i in guild.members if i.bot))} ({(len(set(i for i in guild.members if i.bot))/guild.member_count) * 100:.2f}%)\n**Total:** {guild.member_count}")
        embed.add_field(name="Information", value=f"**Verification:** {guild.verification_level}\n**Boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**Large:** {'yes' if guild.large else 'no'}")
        embed.add_field(name="Design", value=f"{icon}\n{splash}\n{banner}")
        embed.add_field(name=f"Channels ({len(guild.channels)})", value=f"**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}\n**Categories** {len(guild.categories)}")
        embed.add_field(name="Counts", value=f"**Roles:** {len(guild.roles)}/250\n**Emojis:** {len(guild.emojis)}/{guild.emoji_limit*2}\n**Stickers:** {len(guild.stickers)}/{guild.sticker_limit}")
        embed.set_footer(text=f"Guild ID: {guild.id}")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["banner", "ubanner", "ub"], description="see someone's banner", usage="<user>")
    async def userbanner(self, ctx: commands.Context, *, member: discord.User=commands.Author):
     user = await self.bot.fetch_user(member.id)
     if not user.banner: return await ctx.warning(f"**{user}** doesn't have a banner") 
     embed = discord.Embed(color=self.bot.color, title=f"{user.name}'s banner", url=user.banner.url)
     embed.set_image(url=user.banner.url)
     return await ctx.reply(embed=embed) 

    @commands.command(aliases=["pfp", "uav", "avatar", "av"], description="see user's avatar", usage="<user>")
    async def useravatar(self, ctx: commands.Context, *, member: discord.User = None):
      if member is None: member = ctx.author
      member = await self.bot.fetch_user(member.id)
      embed = Embed(color=self.bot.color, title=f"{member.name}'s avatar", url=member.display_avatar.url)
      embed.set_image(url=member.avatar.url)
      await ctx.reply(embed=embed)

    @commands.command(aliases=["sav", "savatar", "spfp"], description="see user's server avatar", usage="<user>")
    async def serveravatar(self, ctx: commands.Context, *, member: discord.Member = None):
      if member is None: member = ctx.author
      if member.guild_avatar is None: return await ctx.warning(f'**{member}** doesnt have a server avatar set.')
      embed = Embed(color=self.bot.color, title=f"{member.name}'s server avatar", url=member.display_avatar.url)
      embed.set_image(url=member.guild_avatar.url)
      await ctx.reply(embed=embed)

    @commands.command(aliases=["sbanner"], description="get the server's banner")
    async def serverbanner(self, ctx: commands.Context): 
        guild = ctx.guild
        if not guild.banner: return await ctx.warning( "this server has no banner".capitalize())
        embed = Embed(color=self.bot.color, title=f"{guild.name}'s banner", url=guild.banner.url)   
        embed.set_image(url=guild.banner.url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["sicon", "icon"], description="get the server's icon")
    async def servericon(self, ctx: Context, *, id: int=None): 
        guild = ctx.guild
        if not guild.icon: return await ctx.warning( "this server has no icon".capitalize())
        embed = Embed(color=self.bot.color, title=f"{guild.name}'s icon", url=guild.icon.url)   
        embed.set_image(url=guild.icon.url)
        await ctx.reply(embed=embed)   

    @commands.command(aliases=["splash", "ssplash"], description="get the server's invite background image")
    async def serversplash(self, ctx: Context): 
        guild = ctx.guild
        if not guild.splash: return await ctx.warning( "this server has no splash".capitalize())
        embed = Embed(color=self.bot.color, title=f"{guild.name}'s invite background", url=guild.splash.url)   
        embed.set_image(url=guild.splash.url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["gbanner"], description="gets the banner from a server based by invite code", usage="[invite code]")
    async def guildbanner(self, ctx, *, link: str):
     invite_code = link
     data = await self.bot.session.get_json(DISCORD_API_LINK + invite_code)
     format = ".gif" if "a_" in data["guild"]["banner"] else ".png"
     embed = Embed(color=self.bot.color, title=data["guild"]["name"] + "'s banner")
     embed.set_image(url="https://cdn.discordapp.com/banners/" + data["guild"]["id"] + "/" + data["guild"]["banner"] + f"{format}?size=1024")
     await ctx.reply(embed=embed)

    @commands.command(aliases=["gsplash"],description="gets the splash from a server based by invite code", usage="[invite code]")
    async def guildsplash(self, ctx, *, link: str):
      invite_code = link
      data = await self.bot.session.get_json(DISCORD_API_LINK + invite_code)
      embed = Embed(color=self.bot.color, title=data["guild"]["name"] + "'s splash")
      embed.set_image(url="https://cdn.discordapp.com/splashes/" + data["guild"]["id"] + "/" + data["guild"]["splash"] + ".png?size=1024")
      if data == None: return await ctx.warning("this server doesn't have a splash set.")
      else: await ctx.reply(embed=embed)
    
    @commands.command(aliases=["gicon"], description="gets the icon from a server based by invite code", usage="[invite code]")
    async def guildicon(self, ctx, *, link: str):
      invite_code = link
      data = await self.bot.session.get_json(DISCORD_API_LINK + invite_code)
      format = ".gif" if "a_" in data["guild"]["icon"] else ".png"
      embed = Embed(color=self.bot.color, title=data["guild"]["name"] + "'s icon")
      embed.set_image(url="https://cdn.discordapp.com/icons/" + data["guild"]["id"] + "/" + data["guild"]["icon"] + f"{format}?size=1024")
      await ctx.reply(embed=embed)

    @commands.command(description="sends a definition of a word", usage="[word]")
    async def urban(self, ctx, *, word):
      embeds = []
      try:
       data = await self.bot.session.get_json("http://api.urbandictionary.com/v0/define", params={"term": word})
       defs = data["list"]
       for defi in defs: 
        e = discord.Embed(color=self.bot.color, description=defi["definition"], timestamp=dateutil.parser.parse(defi["written_on"]))
        e.set_author(name=word, url=defi["permalink"])
        e.add_field(name="example", value=defi["example"], inline=False) 
        e.set_footer(text=f"{defs.index(defi)+1}/{len(defs)}")
        embeds.append(e)
       return await ctx.paginator(embeds)
      except Exception as e: await ctx.reply("no definition found for **{}**".format(word))

    @commands.command(description="gets information about a github user", aliases=["gh"], usage="[user]")
    async def github(self, ctx, *, user: str):
        res = await self.bot.session.get_json(f'https://api.github.com/users/{user}') 
        name=res['login']
        avatar_url=res['avatar_url']
        html_url=res['html_url']
        email=res['email']
        public_repos=res['public_repos']
        followers=res['followers']
        following=res['following']
        twitter = res['twitter_username']
        location=res['location']
        company=res['company']
        embed = Embed(color=self.bot.color, title = f"@{name}", url=html_url)
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Followers", value=followers)
        embed.add_field(name="Following", value=following)
        embed.add_field(name="Repos", value=public_repos)
        if email: embed.add_field(name="Email", value=email)
        if location: embed.add_field(name="Location", value=location)
        if twitter: embed.add_field(name="Twitter", value=twitter)
        if company: embed.add_field(name="Company", value=company)
        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(text='Github', icon_url='https://cdn.evict.dev/github.png')
        await ctx.reply(embed=embed)

    @commands.command(aliases=["firstmsg"], description="get the first message", usage="<channel>")
    async def firstmessage(self, ctx: Context, *, channel: TextChannel=None):
     channel = channel or ctx.channel 
     messages = [mes async for mes in channel.history(oldest_first=True, limit=1)]
     message = messages[0]
     embed = Embed(color=self.bot.color, title="first message in #{}".format(channel.name), description=message.content, timestamp=message.created_at)
     embed.set_author(name=message.author, icon_url=message.author.display_avatar)
     view = View()
     view.add_item(Button(label="jump to message", url=message.jump_url))
     await ctx.reply(embed=embed, view=view) 

    @commands.command(name="inviteinfo", aliases=["ii"], description="get information about an invite", usage="invite code")
    async def inviteinfo(self, ctx, code: str):
        if "/" in code:
            code = code.split("/", -1)[-1].replace(" ", "")

        try:
            invite = await ctx.bot.fetch_invite(url=code, with_counts=True, with_expiration=True)
        except discord.NotFound:
            return await ctx.warning('that was an invalid invite')
        icon= f"[icon]({invite.guild.icon.url})" if invite.guild.icon is not None else "N/A"
        splash=f"[splash]({invite.guild.splash.url})" if invite.guild.splash is not None else "N/A"
        banner=f"[banner]({invite.guild.banner.url})" if invite.guild.banner is not None else "N/A"
        members_total = f"{invite.approximate_member_count:,}"
        members_online_total = f"{invite.approximate_presence_count:,}"
        ratio_string = round(invite.approximate_presence_count / invite.approximate_member_count, 2) * 100
        urls = ""
        embed = discord.Embed(color=self.bot.color, title=f"Invite Code: {code}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Channel & Invite", value=f"**Name:** {invite.channel} (`{invite.channel.type}`)\n**ID:** `{invite.channel.id}`\n**Created:** <t:{str(invite.channel.created_at.timestamp()).split('.')[0]}> (<t:{str(invite.channel.created_at.timestamp()).split('.')[0]}:R>)\n**Invite Expiration:** {invite.max_age}\n**Inviter:** {invite.inviter}\n**Temporary:** {invite.temporary}\n**Usage:** {invite.uses}")
        embed.add_field(name="Guild", value=f"**Name:** {invite.guild.name}\n**ID:** `{invite.guild.id}`\n**Created:** <t:{str(invite.guild.created_at.timestamp()).split('.')[0]}> (<t:{str(invite.guild.created_at.timestamp()).split('.')[0]}:R>)\n**Members:** {members_total}\n**Members Online:** {members_online_total}\n**Member Online Ratio:** {ratio_string}\n**Verification Level:** {str(invite.guild.verification_level).title()}")
       # embed.add_field(name="Design", value=f"{icon}\n{splash}\n{banner}")
        if invite.guild.icon is not None:
          embed.set_thumbnail(url=invite.guild.icon.url)

        await ctx.reply(embed=embed)

    @commands.command(aliases=["sp"], name="spotify", description="send what you or another person is listening to on Spotify", usage="member")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def spotify(self, ctx, user: discord.Member = None):
        try:
            if user == None:
                user = ctx.author
                pass
            if user.activities:
                for activity in user.activities:
                    if str(activity).lower() == "spotify":
                        embed = discord.Embed(color=self.bot.color)
                        embed.add_field(
                            name="**Song**", value=f"**[{activity.title}](https://open.spotify.com/track/{activity.track_id})**", inline=True)
                        embed.add_field(
                            name="**Artist**", value=f"**[{activity.artist}](https://open.spotify.com/track/{activity.track_id})**", inline=True)
                        embed.set_thumbnail(url=activity.album_cover_url)
                        embed.set_author(
                            name=user.name, icon_url=user.display_avatar.url)
                        embed.set_footer(
                            text=f"Album: {activity.album}", icon_url=activity.album_cover_url)
                        button1 = discord.ui.Button(emoji="<:Spotifywhite:1208018664868286525>", label="Listen on Spotify", style=discord.ButtonStyle.url, url=f"https://open.spotify.com/track/{activity.track_id}")
                        view = discord.ui.View()
                        view.add_item(button1)
                        await ctx.reply(embed=embed, view=view, mention_author=False)
                        return
            embed = discord.Embed(
                description=f"{ctx.message.author.mention}: **{user}** is not listening to Spotify", colour=0x313338)
            await ctx.reply(embed=embed, mention_author=False)
            return
        except Exception as e:
            print(e)

    @commands.command(name="devices", description="send what device you or another person is using", usage="member")
    async def devices(self, ctx, *, member: discord.Member=None):
        if member is None:
            member = ctx.author
        d = str(member.desktop_status)
        m = str(member.mobile_status)
        w = str(member.web_status)
        if any([isinstance(a, discord.Streaming) for a in member.activities]):
            d = d if d == 'offline' else 'streaming'
            m = m if m == 'offline' else 'streaming'
            w = w if w == 'offline' else 'streaming'
        status = {
			'online': '\U0001f7e2',
			'idle': '\U0001f7e0',
			'dnd': '\N{LARGE RED CIRCLE}',
			'offline': '\N{MEDIUM WHITE CIRCLE}',
			'streaming': '\U0001f7e3'
		}
        embed = discord.Embed(color=self.bot.color, title=f'**{member.display_name}\'s devices:**',
			description=(
				f'{status[d]} Desktop\n'
				f'{status[m]} Mobile\n'
				f'{status[w]} Web'),)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)
    
    @commands.command(description="check how long the bot has been online for")
    async def uptime(self, ctx: commands.Context):
     e = discord.Embed(color=self.bot.color, description=f"⏰ **{self.bot.user.name}'s** uptime: **{self.bot.ext.uptime}**")
     await ctx.reply(embed=e)
    
    @commands.command(description="check bot connection")
    async def ping(self, ctx):
      await ctx.reply(f"....pong 🏓 `{self.bot.ext.ping}ms`")

    @commands.command(description="invite the bot", aliases=["support", "inv"])
    async def invite(self, ctx):
      embed = discord.Embed(color=self.bot.color, description="If your server is authorized [add me](https://discordapp.com/oauth2/authorize?client_id=1203514684326805524&scope=bot+applications.commands&permissions=8) otherwise join the [support server](https://discord.gg/evict) and request a whitelist.")
      await ctx.reply(embed=embed)
    
    @commands.command(aliases=["pos"], description='check member join position', usage="[member]")
    async def position(self, ctx, *, member: discord.Member=None):
        if member is None:
            member = ctx.author
        pos = sum(m.joined_at < member.joined_at for m in ctx.guild.members if m.joined_at is not None)
        embed=discord.Embed(color=self.bot.color, description=f'{member.mention} is member number {pos}.')
        await ctx.reply(embed=embed)
        
    @commands.command(description='shows bot information', help='information', aliases=['info', 'bi'])
    async def botinfo(self, ctx: commands.Context):
        embed = discord.Embed(title=f"{ctx.author.name}", description= 'Developers: [sin](https://discordapp.com/users/598125772754124823) **&** [fiji](https://discordapp.com/users/971464344749629512)', color=self.bot.color)
        embed.add_field(name='Created', value=f'<t:{int(self.bot.user.created_at.timestamp())}:R>', inline=True)
        embed.add_field(name='Servers', value=f"`{len(self.bot.guilds)}`", inline=True)
        embed.add_field(name='Users', value=f"`{len(self.bot.users)}`", inline=True)
        embed.add_field(name='Commands', value=f"`{len(self.bot.commands)}`", inline=True)
        embed.add_field(name='Cogs', value=f"`{len(self.bot.cogs)}`", inline=True)
        embed.add_field(name='Uptime', value=f"`{Time().format_duration(self.bot.uptime)}`", inline=True)
        embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        return await ctx.reply(embed=embed)
    
    @commands.command(description='shows avatar history', aliases=['avh'])
    async def avatarhistory(self, ctx: commands.Context, *, user: discord.Member | discord.User = None):
        """View a user's avatar history"""

        user = user or ctx.author

        avatars = await self.bot.db.fetch(
            "SELECT avatar, timestamp FROM avatars WHERE user_id = $1 ORDER BY timestamp DESC",
            user.id,
        )
        if not avatars:
            return await ctx.warning(
                "You don't have any **avatars** in the database" if user == ctx.author else f"**{user}** doesn't have any **avatars** in the database"
            )

        async with ctx.typing():
            image = await functions.collage([row.get("avatar") for row in avatars[:35]])
            if not image or sys.getsizeof(image.fp) > ctx.guild.filesize_limit:
                await ctx.neutral(
                    (
                        f"Click [**here**](https://evict.cc/avatars/{user.id}) to view"
                        f" {functions.plural(avatars, bold=True):of your avatar}"
                        if user == ctx.author
                        else (
                            f"Click [**here**](https://evict.cc/avatars/{user.id}) to view"
                            f" {functions.plural(avatars, bold=True):avatar} of **{user}**"
                        )
                    ),
                    emoji="🖼️",
                )
            else:
                embed = discord.Embed(
                    title="Avatar History",
                    color=self.bot.color,
                    description=(
                        f"Showing `{len(avatars[:35])}` of up to `{len(avatars)}` {'changes' if len(avatars) != 1 else 'change'}\n> For the full list"
                        f" including GIFs click [**HERE**](https://evict.cc/avatars/{user.id})"
                    ),
                )
                embed.set_author(
                    name=f"{user} ({user.id})",
                    icon_url=user.display_avatar.url,
                )

                embed.set_image(
                    url="attachment://collage.png",
                )
                await ctx.reply(
                    embed=embed,
                    file=image,
                )

async def setup(bot):
    await bot.add_cog(information(bot))
