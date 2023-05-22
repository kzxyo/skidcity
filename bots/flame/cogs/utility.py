import discord
from discord.ext import commands
from typing import Union

snipe_message_author = {}
snipe_message_content = {}
snipe_attachment = {}
afk_mbrs = {}
reason_afk = {}

class utility(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    async def afk(self, ctx: commands.Context, *, args=None):
     if args == None:
        args = "AFK"

     embed = discord.Embed(color=0xffffff, description=f"{ctx.author.mention} you are afk - {args}")
     msg = ' '.join(args)
     afk_mbrs[ctx.guild.id][ctx.author.id] = ctx.author.id
     reason_afk[ctx.guild.id][ctx.author.id] = msg
     await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
     if afk_mbrs[message.guild.id] is None:
        return 

     for i in range(len(afk_mbrs[message.guild.id])):
      if (f"<@{afk_mbrs[message.guild.id][i]}>" in message.content) and (not message.author.bot):
        await message.channel.send(f"<@{afk_mbrs[message.guild.id][i]}> is away right now, with status: {reason_afk[message.guild.id][i]}")
        return None
        break

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
     if afk_mbrs[channel.guild.id][user.id] is not None:
      afk_mbrs[channel.guild.id][user.id] = None
      reason_afk[channel.guild.id][user.id] = None
      await channel.send(f"{user.mention} has returned!")

      
    @commands.Cog.listener()
    async def on_message_delete(self, message): 
      snipe_message_author[message.channel.id] = message.author 
      snipe_message_content[message.channel.id] = message.content 
      if message.attachments:
        snipe_attachment[message.channel.id] = message.attachments[0].url
      else:
        snipe_attachment[message.channel.id] = None

    @commands.command(pass_context=True, name = "spotify", description = "Shows the Spotify song a user is listening to", usage = "$spotify [user]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def spotify(self, ctx, user: discord.Member = None):
        try:
            if user == None:
                user = ctx.author
                pass
            if user.activities:
                for activity in user.activities:
                    if str(activity).lower() == "spotify":
                        embed = discord.Embed(color=ctx.author.color)
                        embed.add_field(name = "**Song**", value = f"**[{activity.title}](https://open.spotify.com/embed/track/{activity.track_id})**", inline = False)
                        embed.add_field(name = "**Artist**", value = f"**[{activity.artist}](https://open.spotify.com/embed/track/{activity.track_id})**", inline = False)
                        embed.set_thumbnail(url=activity.album_cover_url)
                        embed.set_author(name = ctx.message.author.name, icon_url = ctx.message.author.avatar)
                        embed.set_footer(text = f"Album: {activity.album}", icon_url = activity.album_cover_url)
                        embed_msg = await ctx.reply(embed=embed)
                        await embed_msg.add_reaction("👍")
                        await embed_msg.add_reaction("👎")
                        return
            embed = discord.Embed(description = f"{ctx.message.author.mention}: **{user}** is not listening to spotify", colour=0xffffff)
            await ctx.reply(embed=embed)
            return 
        except Exception as e:
            print(e)


    @commands.command(aliases=["s"])
    async def snipe(self, ctx):
      try:
        em = discord.Embed(color=0xffffff, description=snipe_message_content[ctx.channel.id])
        em.set_author(name=snipe_message_author[ctx.channel.id])

        if snipe_attachment[ctx.channel.id] != None:
         em.set_image(url=snipe_attachment[ctx.channel.id])

        await ctx.reply(embed=em, mention_author=False)   
      except:
        await ctx.reply(f"there are not deleted messages in {ctx.channel.mention}", mention_author=False)
       
    @commands.command(aliases=["mc"])
    async def membercount(self, ctx: commands.Context):
        embed = discord.Embed(
            color=0xffffff,
            description=f"**{ctx.guild.member_count}** members")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["av"])
    async def avatar(self,
                     ctx: commands.Context,
                     *,
                     member: Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author

        embed = discord.Embed(color=0xffffff,
                              title=f"{member.name}'s avatar",
                              url=member.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    async def banner(self,
                     ctx: commands.Context,
                     *,
                     member: discord.User = None):
        if member == None:
            member = ctx.author

        user = await self.bot.fetch_user(member.id)
        if user.banner == None:
            em = discord.Embed(
                color=0xffffff,
                description=
                f"<:deny:1026158928687542302> {member.mention} doesn't have a banner"
            )
            await ctx.reply(embed=em, mention_author=False)
        else:
            banner_url = user.banner.url
            e = discord.Embed(color=0xffffff,
                              title=f"{member.name}'s banner",
                              url=user.banner.url)
            e.set_image(url=banner_url)
            await ctx.reply(embed=e, mention_author=False)

    @banner.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            e = discord.Embed(color=0xffffff,
                              description=f"{ctx.author.mention} {error}")
            await ctx.reply(embed=e, mention_author=False)

    @commands.command()
    async def voicecount(self, ctx: commands.Context):
        i = 0
        for channel in ctx.guild.voice_channels:
            i += len(channel.members)

        embed = discord.Embed(
            color=0xffffff,
            description=f"there are **{i}** members in voice channels")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["si"])
    async def serverinfo(self, ctx: commands.Context, arg=None):
        if arg is None:
            i = 0
            j = 0
            icon = ""
            splash = ""
            banner = ""
            if ctx.guild.icon is not None:
                icon = f"[icon]({ctx.guild.icon.url})"
            else:
                icon = "no icon"

            if ctx.guild.splash is not None:
                splash = f"[splash]({ctx.guild.splash.url})"
            else:
                splash = "no splash"

            if ctx.guild.banner is not None:
                banner = f"[banner]({ctx.guild.banner.url})"
            else:
                banner = "no banner"

            for member in ctx.guild.members:
                if member.bot:
                    j += 1
                else:
                    i += 1

            embed = discord.Embed(color=0xffffff)
            try:
                embed.set_author(name=ctx.guild.name,
                                 icon_url=ctx.guild.icon.url)
            except:
                embed.set_author(name=ctx.guild.name)

            if ctx.guild.icon is not None:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            embed.add_field(name="owner", value=ctx.guild.owner, inline=False)
            embed.add_field(
                name="created",
                value=f"<t:{int(ctx.guild.created_at.timestamp())}:F>",
                inline=False)
            embed.add_field(
                name="members",
                value=
                f"{ctx.guild.member_count} total\n{i} humans ({(i/ctx.guild.member_count) * 100:.2f}%)\n{j} bots({(j/ctx.guild.member_count) * 100:.2f}%)"
            )
            embed.add_field(
                name="channels",
                value=
                f"{len(ctx.guild.channels)} total\n{len(ctx.guild.text_channels)} text\n{len(ctx.guild.voice_channels)} voice\n{len(ctx.guild.categories)} categories"
            )
            embed.add_field(name="roles", value=len(ctx.guild.roles) - 1)
            embed.add_field(
                name="boosts",
                value=
                f"{ctx.guild.premium_subscription_count} (level {ctx.guild.premium_tier})"
            )
            embed.add_field(name="links", value=f"{icon}\n{splash}\n{banner}")
            embed.add_field(name="features",
                            value=ctx.guild.features,
                            inline=False)
            embed.set_footer(text=f"ID: {ctx.guild.id}")
            await ctx.reply(embed=embed, mention_author=False)
        elif arg == "banner":
            if ctx.guild.banner is None:
                e = discord.Embed(
                    color=0xffffff,
                    description=
                    f"{ctx.author.mention} this server has no banner")
                await ctx.reply(embed=e, mention_author=False)
                return

            embed = discord.Embed(color=0xffffff,
                                  title=f"{ctx.guild.name}'s banner",
                                  url=ctx.guild.banner.url)
            embed.set_image(url=ctx.guild.banner.url)
            await ctx.reply(embed=embed, mention_author=False)
        elif arg == "icon":
            if ctx.guild.icon is None:
                e = discord.Embed(
                    color=0xffffff,
                    description=f"{ctx.author.mention} this server has no icon"
                )
                await ctx.reply(embed=e, mention_author=False)
                return

            embed = discord.Embed(color=0xffffff,
                                  title=f"{ctx.guild.name}'s icon",
                                  url=ctx.guild.icon.url)
            embed.set_image(url=ctx.guild.icon.url)
            await ctx.reply(embed=embed, mention_author=False)
        elif arg == "splash":
            if ctx.guild.splash is None:
                e = discord.Embed(
                    color=0xffffff,
                    description=
                    f"{ctx.author.mention} this server has no splash")
                await ctx.reply(embed=e, mention_author=False)
                return

            embed = discord.Embed(color=0xffffff,
                                  title=f"{ctx.guild.name}'s splash",
                                  url=ctx.guild.splash.url)
            embed.set_image(url=ctx.guild.splash.url)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["ui", "whois"])
    async def userinfo(self,
                       ctx: commands.Context,
                       *,
                       member: Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author

        k = 0
        for guild in self.bot.guilds:
            if guild.get_member(member.id) is not None:
                k += 1

        if isinstance(member, discord.Member):
            if str(member.status) == "online":
                status = "<:d_online:1026469895543717948>"
            elif str(member.status) == "dnd":
                status = "<:dnd:1026469534523203604>"
            elif str(member.status) == "idle":
                status = "<:d_idle:1026469723128467467>"
            elif str(member.status) == "offline":
                status = "<:d_offline:1026469779948720170>"
            embed = discord.Embed(color=0xffffff)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=member.name,
                             icon_url=member.display_avatar.url)
            embed.add_field(
                name="joined",
                value=
                f"<t:{int(member.joined_at.timestamp())}:F>\n<t:{int(member.joined_at.timestamp())}:R>",
                inline=False)
            members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
            embed.add_field(name="join position",
                            value=str(members.index(member) + 1),
                            inline=False)
            if member.activity:
                activity = member.activity.name
            else:
                activity = ""

            embed.add_field(name="status",
                            value=status + " " + activity,
                            inline=False)
            embed.add_field(
                name="registered",
                value=
                f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>",
                inline=False)
            if len(member.roles) > 1:
                role_string = ' '.join([r.mention for r in member.roles][1:])
                embed.add_field(
                    name="roles [{}]".format(len(member.roles) - 1),
                    value=role_string,
                    inline=False)
            embed.set_footer(text='ID: ' + str(member.id) +
                             f" | {k} mutual server(s)")
            await ctx.reply(embed=embed, mention_author=False)
            return
        elif isinstance(member, discord.User):
            e = discord.Embed(color=0xffffff)
            e.set_author(name=f"{member}", icon_url=member.display_avatar.url)
            e.set_thumbnail(url=member.display_avatar.url)
            e.add_field(
                name="registered",
                value=
                f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>",
                inline=False)
            e.set_footer(text='ID: ' + str(member.id) +
                         f" | {k} mutual server(s)")
            await ctx.reply(embed=e, mention_author=False)


async def setup(bot) -> None:
    await bot.add_cog(utility(bot))