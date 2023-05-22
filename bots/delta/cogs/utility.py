import discord
from discord.ext import commands
from discord.ext import tasks
from typing import Union
from core.utils.views import Views
from datetime import datetime
from datetime import datetime, timedelta
now = datetime.now
import datetime as dt
import os
import aiohttp
import json
import requests
import asyncio
import random

snipe_message_author = {}
snipe_message_content = {}
snipe_attachment = {}
afk_mbrs = {}
reason_afk = {}

class utility(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
        self.deleted_messages = {}
        self.removed_reactions = {}
        self.edited_messages = {}
        self.available_tags = []
        
        self.clean_tags_cache.start()
           
    @commands.command(aliases=["webshoty", "sa"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def webshot(self, ctx, *, link:str = None) -> None:
      if link == None:
          em = discord.Embed(color=0x2f3136,description=f"> You dont type a __site__ for search")
          await ctx.send(embed=em)
          return
      links = ["https://", "http://"]
      if not (link.startswith(tuple(links))):
          await ctx.send(embed=discord.Embed(color=0x2f3136, description=f"> You didn't input __https __ before the link provided"))
          return
      else:
          n = discord.Embed(description=f"> Preview {link.replace('https://', '').replace('http://', '')}", color=0x2f3136)
          n.set_image(url='https://api.popcat.xyz/screenshot?url=' + str(link.replace("http://", "https://")))
          await ctx.reply(embed=n, mention_author=False)
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def newyear(self, ctx: commands.Context):
        #x = dt.datetime(2022, 12, 25) - dt.datetime.today()
        xx = datetime(2022,12,31)
        xxx = datetime.now()
        x = xx - xxx
        duration_secs = int(x.total_seconds())
        weeks = int(duration_secs/(86400*7))
        duration_secs = int(duration_secs%86400*7)
        days = int(duration_secs/86400)
        duration_secs = int(duration_secs%86400)
        hours = int(duration_secs/3600)
        duration_secs = int(duration_secs%3600)
        minutes = int(duration_secs/60)
        seconds = int(duration_secs%60)
        embed = discord.Embed(
            title=f"NewYear countdown",
            description=f'> **Left:** __{weeks} weeks, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds__',color=0x2f3136
        )
        await ctx.reply(embed=embed, mention_author=False)
    
    @commands.command()
    @commands.cooldown(1,3, commands.BucketType.channel)
    async def invites(self, ctx, member: discord.Member = None):
     member = ctx.author if not member else member

     totalInvites = 0
     for i in await ctx.guild.invites():
         if i.inviter == member:
              totalInvites += i.uses
     embed = discord.Embed(color=0x2f3136,description=f"> **{member.name}** Have __{str(totalInvites)}__ invites")
     await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def xmas(self, ctx: commands.Context):
        #x = dt.datetime(2022, 12, 25) - dt.datetime.today()
        xx = datetime(2022,12,25)
        xxx = datetime.now()
        x = xx - xxx
        duration_secs = int(x.total_seconds())
        weeks = int(duration_secs/(86400*7))
        duration_secs = int(duration_secs%86400*7)
        days = int(duration_secs/86400)
        duration_secs = int(duration_secs%86400)
        hours = int(duration_secs/3600)
        duration_secs = int(duration_secs%3600)
        minutes = int(duration_secs/60)
        seconds = int(duration_secs%60)
        embed = discord.Embed(
            title=f"Christmas countdown",
            description=f'> **Left:** __{weeks} weeks, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds__',color=0x2f3136
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def summer(self, ctx: commands.Context):
        #x = dt.datetime(2022, 12, 25) - dt.datetime.today()
        xx = datetime(2023,6,14)
        xxx = datetime.now()
        x = xx - xxx
        duration_secs = int(x.total_seconds())
        weeks = int(duration_secs/(86400*7))
        duration_secs = int(duration_secs%86400*7)
        days = int(duration_secs/86400)
        duration_secs = int(duration_secs%86400)
        hours = int(duration_secs/3600)
        duration_secs = int(duration_secs%3600)
        minutes = int(duration_secs/60)
        seconds = int(duration_secs%60)
        embed = discord.Embed(
            title=f"Summer countdown",
            description=f'> **Left:** __{weeks} weeks, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds__',color=0x2f3136
        )
        await ctx.reply(embed=embed, mention_author=False)
        
    @commands.Cog.listener()
    async def on_user_update(self, before:discord.User, after:discord.User):
        if before.avatar == after.avatar:
            if before.discriminator == "0001" and before.name.islower(): #checks if 0001 and if lowercase
                self.bot.dispatch('available_tag', before)
    
    @commands.Cog.listener()
    async def on_available_tag(self, user:discord.User):
        self.available_tags.insert(0,
            {
                "user": user,
                "time": datetime.now()
            }
        )
        
    @tasks.loop(seconds=1800)
    async def clean_tags_cache(self):
        print("cogs.utility - cleaning tags cache")
        now = datetime.now()
        for tag in self.available_tags:
            tag_time = tag["time"]
            difference = now - tag_time
            if difference.seconds > 21600:
                self.available_tags.remove(tag)
    
    @commands.command(name = "tags", description="See available 0001 tags")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def tags(self, ctx:commands.Context):
        async with ctx.typing():
            available_tags = self.available_tags.copy()
            if available_tags:
                max_tags = 10
                tags = tuple(available_tags[x:x + max_tags]  for x in range(0, len(available_tags), max_tags))
                pages = []

                i = 0
                for group in tags:
                    page = discord.Embed()
                    page.set_author(name=ctx.author.name,icon_url=ctx.author.display_avatar.url)
                    page.title = f"Recent Usernames With __0001__"
                    page.description = '\n'.join([f"`{idx+1+i}` **-** {x['user']}: {discord.utils.format_dt(x['time'], style='R')}" for idx, x in enumerate(group)])
                    pages.append(page)
                    i += len(group) +1
                
                if len(pages) == 1:
                    await ctx.reply(embed=pages[0], mention_author=False)
                else:
                    paginator = Views.Paginator()
                    await paginator.start(ctx,pages)
            else:
                embed = discord.Embed()
                embed.description = "> There are no available __tags__!"
                await ctx.reply(embed=embed, mention_author=False)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload:discord.RawReactionActionEvent):
        self.removed_reactions[payload.channel_id] = payload
    
    @commands.command(name = "reactionsnipe", description="Snipe a removed reaction", aliases=['rs','rsnipe'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    async def reactionsnipe(self, ctx:commands.Context):
        async with ctx.typing():
            removed_reaction: discord.RawReactionActionEvent = self.removed_reactions.get(ctx.channel.id, None)
            if removed_reaction:
                member = await self.bot.fetch_user(removed_reaction.user_id)
                embed = discord.Embed()
                embed.set_author(name=member,icon_url=member.avatar.url)

                emoji = removed_reaction.emoji
                if emoji.is_unicode_emoji():
                    embed.description = f"> {emoji}"
                elif emoji.is_custom_emoji():
                    if emoji.animated:
                        embed.set_image(url=emoji.url.replace('.png','.gif'))
                    else:
                        embed.set_image(url=emoji.url)

                message: discord.Message = await self.bot.get_channel(removed_reaction.channel_id).fetch_message(removed_reaction.message_id)
                class JumpToMessage(discord.ui.View):
                    def __init__(self, *, timeout=180):
                        super().__init__(timeout=timeout)
                        self.add_item(discord.ui.Button(label="Jump to message",url=message.jump_url))

                await ctx.reply(embed=embed, view=JumpToMessage(), mention_author=False)
            else:
                embed = discord.Embed()
                embed.description = "> There is no __deleted emoji in this channel!__"
                await ctx.reply(embed=embed, mention_author=False)   
  
    @commands.command(aliases=["mc"])
    async def membercount(self, ctx: commands.Context):
        embed = discord.Embed(
        description = f"**Member's in {ctx.guild.name}**",
        color=0x2f3136
        )
        embed.add_field(name="**Total**",value=f"> {ctx.guild.member_count}",inline=False)
        embed.add_field(name="**Members**",value=f"> {len([member for member in ctx.guild.members if not member.bot])}",inline=False)
        embed.add_field(name="**Bots**",value=f"> {len([m for m in ctx.guild.members if m.bot])}",inline=False)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["vt"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.is_owner()
    async def vote(self, ctx: commands.Context):
        embed = discord.Embed(title=f"**Axie** a multi-purpose discord bot",description=f"<:topgg_ico_discord:1038135397663908001> [Top.gg]()ĺk",color=0x992d22)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["s2"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serversetup2(self, ctx):
        embed=discord.Embed(description=f"> Click below to get role for update/downtime ping\n \n > react with <:icons_hammer:1022917170730111131> for **updates** \n > react with <:check_warning:1023193803877785710> for **downtimes**", title="Roles",  color=0x2f3136)
        await ctx.send(embed=embed)
   
    @commands.command(aliases=["bc"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def boostcount(self, ctx):
        embed = discord.Embed(
        title = f'> __{ctx.guild.name}__\'s Boost Count',
        description = f'{str(ctx.guild.premium_subscription_count)}',
         colour=0x2f3136
         )
        await ctx.reply(embed = embed, mention_author=False)

    @commands.command(aliases=["ui", "whois"])
    @commands.cooldown(1, 3, commands.BucketType.user)
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
                status = "<:online:1049000510167973898>"
            elif str(member.status) == "dnd":
                status = "<:dnd:1048996799920210020>"
            elif str(member.status) == "idle":
                status = "<:inactive:1048997004212174919>"
            elif str(member.status) == "offline":
                status = "<:offline:1048996780076978256>"
            embed = discord.Embed(color=0x2f3136)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=member.name,
                             icon_url=member.display_avatar.url)
            embed.add_field(
                name="joined",
                value=
                f"<t:{int(member.joined_at.timestamp())}:F>\n<t:{int(member.joined_at.timestamp())}:R>",
                inline=False)
            members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
            embed.add_field(name="> __join position__",
                            value=str(members.index(member) + 1),
                            inline=False)
            if member.activity:
                activity = member.activity.name
            else:
                activity = ""

            embed.add_field(name="> __status__",
                            value=status + " " + activity,
                            inline=False)
            embed.add_field(
                name="> __registered__",
                value=
                f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>",
                inline=False)
            if len(member.roles) > 1:
                role_string = ' '.join([r.mention for r in member.roles][1:])
                embed.add_field(
                    name="> __roles [{}]__".format(len(member.roles) - 1),
                    value=role_string,
                    inline=False)
            embed.set_footer(text='ID: ' + str(member.id) +
                             f" | {k} mutual server(s)")
            await ctx.reply(embed=embed, mention_author=False)
            return
        elif isinstance(member, discord.User):
            e = discord.Embed(color=0x2f3136)
            e.set_author(name=f"{member}", icon_url=member.display_avatar.url)
            e.set_thumbnail(url=member.display_avatar.url)
            e.add_field(
                name="> __registered__",
                value=
                f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>",
                inline=False)
            e.set_footer(text='ID: ' + str(member.id) +
                         f"{k} mutual server(s)")
            await ctx.reply(embed=e, mention_author=False)

    @commands.Cog.listener()

    async def on_message_delete(self, message): 

      snipe_message_author[message.channel.id] = message.author 

      snipe_message_content[message.channel.id] = message.content 

      if message.attachments:

        snipe_attachment[message.channel.id] = message.attachments[0].url

      else:

        snipe_attachment[message.channel.id] = None

            

    @commands.command(aliases=["s"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def snipe(self, ctx):

      try:

        em = discord.Embed(color=0x2f3136, description=snipe_message_content[ctx.channel.id])

        em.set_author(name=snipe_message_author[ctx.channel.id])

        if snipe_attachment[ctx.channel.id] != None:

         em.set_image(url=snipe_attachment[ctx.channel.id])

        await ctx.reply(embed=em, mention_author=False)   

      except:

        await ctx.reply(f"> there are not deleted messages in __{ctx.channel.mention}__", mention_author=False)

       
       
    @commands.command(aliases=["av"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def avatar(self,
                     ctx: commands.Context,
                     *,
                     member: Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author

        embed = discord.Embed(color=0x2f3136,
                              title=f"> {member.name}'s avatar",
                              url=member.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)
      
    @commands.command(name="nick")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nick(self, ctx):
        embed = discord.Embed(
            color=0x2f3136
            )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="**nickset**",value="> __change the nickname of the mentioned user__",inline=False)
        embed.add_field(name="**category**",value="> __utility__",inline=False)
        embed.add_field(name="**permission**",value="> __manage_nicknames__",inline=False)
        embed.add_field(name="**ussage**",value="> `.nickset (user) <nickname>`",inline=False)
        embed.add_field(name="**aliases**",value="> __none__",inline=False)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="nickset")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_nicknames=True)
    async def nickset(self, context, member: discord.Member, *, nickname=None):
        """
        Nick setter
        """
        try:
            await member.edit(nick=nickname)
            embed = discord.Embed(
                title="**Changed the user** __nickname__",
                description=f"**> {member}'s** __nickname__ had been updated to **{nickname}**!",
                color=0x2f3136
            )
            await context.send(embed=embed)
        except:
            embed = discord.Embed(
                title="**Error**",
                description="> __I cant change the mentioned user's nickname because is higher than me!__",
                color=0x2f3136
            )
            await context.message.channel.send(embed=embed)
   
    @nickset.error
    async def nickset_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
            description = "> __You need  `manage_Nicknames` permission to use this command__",
             colour = 0xff0000
             )
            await ctx.reply(embed=embed, mention_author=False)
    
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def vanity(self, ctx: commands.Context):
        if ctx.guild.vanity_url_code is None:
            embed=discord.Embed(color=0x2f3136, description=f"> **This server has no vanity**")
            embed.set_footer(text="No Vanity")

        elif ctx.guild.vanity_url_code is not None:
            embed=discord.Embed(color=0x2f3136, description=f"> **Guild Vanity:** `{ctx.guild.vanity_url_code}`")
            embed.set_footer(text="Server Vanity")
            
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    async def mods(self, ctx):
        """ Check which mods are online on current guild """
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "<:online:1022917246168875028>"},
            "idle": {"users": [], "emoji": "<:o_idle:1022917254024810597>"},
            "dnd": {"users": [], "emoji": "<:o_dnd:1022917263524909066>"},
            "offline": {"users": [], "emoji": "<:offline:1022917249805332521>"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"
        await ctx.send(f"> <:icons_settings:1022917201663115307> All Users with Administrator in __**{ctx.guild.name}**__\n{message}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def banner(self,
                     ctx: commands.Context,
                     *,
                     member: discord.User = None):
        if member == None:
            member = ctx.author

        user = await self.bot.fetch_user(member.id)
        if user.banner == None:
            em = discord.Embed(
                color=0x2f3136,
                description=
                f"> {member.mention} doesn't have a __banner__"
            )
            await ctx.reply(embed=em, mention_author=False)
        else:
            banner_url = user.banner.url
            e = discord.Embed(color=0x2f3136,
                              title=f"> {member.name}'s __banner__",
                              url=user.banner.url)
            e.set_image(url=banner_url)
            await ctx.reply(embed=e, mention_author=False)

    @banner.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            e = discord.Embed(color=0x2f3136,
                              description=f"> __{ctx.author.mention}__ {error}")
            await ctx.reply(embed=e, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def voicecount(self, ctx: commands.Context):
        i = 0
        for channel in ctx.guild.voice_channels:
            i += len(channel.members)

        embed = discord.Embed(
            color=0x2f3136,
            description=f"> There are __**{i}**__ members in __voice channels__")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=['sinfo'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def server(self, ctx: commands.Context, arg=None):
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

            embed = discord.Embed(color=0x2f3136)
            try:
                embed.set_author(name=ctx.guild.name,
                                 icon_url=ctx.guild.icon.url)
            except:
                embed.set_author(name=ctx.guild.name)

            if ctx.guild.icon is not None:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            embed.add_field(name="> **owner**", value=ctx.guild.owner, inline=False)
            embed.add_field(
                name="> **created**",
                value=f"<t:{int(ctx.guild.created_at.timestamp())}:F>",
                inline=False)
            embed.add_field(
                name="> **members**",
                value=
                f"{ctx.guild.member_count} total\n{i} humans ({(i/ctx.guild.member_count) * 100:.2f}%)\n{j} bots({(j/ctx.guild.member_count) * 100:.2f}%)"
            )
            embed.add_field(
                name="> **channels**",
                value=
                f"{len(ctx.guild.channels)} total\n{len(ctx.guild.text_channels)} text\n{len(ctx.guild.voice_channels)} voice\n{len(ctx.guild.categories)} categories"
            )
            embed.add_field(name="> **roles**", value=len(ctx.guild.roles) - 1)
            embed.add_field(
                name="> **boosts**",
                value=
                f"{ctx.guild.premium_subscription_count} (level {ctx.guild.premium_tier})"
            )
            embed.add_field(name="> **links**", value=f"{icon}\n{splash}\n{banner}")
            embed.add_field(name="> **features**",
                            value=f"`{', '.join(feature for feature in ctx.guild.features)}`",
                            inline=False)
            embed.set_footer(text=f"ID: {ctx.guild.id}")
            await ctx.reply(embed=embed, mention_author=False)
        elif arg == "banner":
            if ctx.guild.banner is None:
                e = discord.Embed(
                    color=0xff0000,
                    description=
                    f"> __{ctx.author.mention}__ this server has no **banner**")
                await ctx.reply(embed=e, mention_author=False)
                return

            embed = discord.Embed(color=0x2f3136,
                                  title=f"> {ctx.guild.name} __banner__",
                                  url=ctx.guild.banner.url)
            embed.set_image(url=ctx.guild.banner.url)
            await ctx.reply(embed=embed, mention_author=False)
        elif arg == "icon":
            if ctx.guild.icon is None:
                e = discord.Embed(
                    color=0xff0000,
                    description=f"> __{ctx.author.mention}__ this server has no **icon**"
                )
                await ctx.reply(embed=e, mention_author=False)
                return

            embed = discord.Embed(color=0x2f3136,
                                  title=f"> __{ctx.guild.name}__ **icon**",
                                  url=ctx.guild.icon.url)
            embed.set_image(url=ctx.guild.icon.url)
            await ctx.reply(embed=embed, mention_author=False)
        elif arg == "splash":
            if ctx.guild.splash is None:
                e = discord.Embed(
                    color=0xff0000,
                    description=
                    f"> __{ctx.author.mention}__ this server has no **splash**")
                await ctx.reply(embed=e, mention_author=False)
                return

            embed = discord.Embed(color=0x2f3136,
                                  title=f"> {ctx.guild.name} **splash**",
                                  url=ctx.guild.splash.url)
            embed.set_image(url=ctx.guild.splash.url)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["screenshot"], usage="[topic]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ss(awlf, ctx, *, ssig):
        """Returns With Screenshot Of Given Link"""
        idk = ctx.message.content.lower()
        if "porn" in idk or "sex" in idk or "xxxx" in idk or "xham" in idk or "hellmom" in idk or "xvid" in idk or "shameless" in idk or "play-asia.com" in idk or "miakhal" in idk or "cum" in idk or "orgasm" in idk or "xvid" in idk or "slut" in idk or "naked" in idk or "brazzers" in idk or "nig" in idk or "slut" in idk or "horny" in idk or "rule34video" in idk or "fuck" in idk:
            await ctx.reply(f"**18+ websites are not allowed!!**",
                            mention_author=True,
                            delete_after=3)
        elif "jerk" in idk or "redgif" in idk or "anybunny" in idk or "hentai" in idk or "nude" in idk or "bangbros" in idk or "onlyfans" in idk or "naught" in idk or "boobs" in idk or "blonde" in idk or "tits" in idk or "titties" in idk or "wetgif" in idk or "pussy" in idk or "hanime" in idk or "gay" in idk or " tiava" in idk or "blowjob" in idk or "beeg" in idk:
            await ctx.reply(f"** 18+ websites aren't allowed!**",
                            mention_author=True,
                            delete_after=5)
        elif "bit.ly" in idk or "shorturl" in idk or "cutt.ly" in idk:
            await ctx.reply(f"**url shorteners aren't allowed!**",
                            mention_author=True,
                            delete_after=5)
        elif "https" in idk or "http" in idk:
            embed = discord.Embed(title=f"Screenshot of {ssig}", color = 0x2f3136)
            embed.set_image(url=f"https://image.thum.io/get/{ssig}")
            await ctx.reply(embed=embed, mention_author=True)
        else:
            embed = discord.Embed(title=f"Screenshot Of {ssig}", color = 0x2f3136)
            embed.set_image(url=f"https://image.thum.io/get/https://{ssig}")
            await ctx.reply(embed=embed, mention_author=False)
   
    @commands.command(usage="[ip]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def geoip(self, ctx, ip):
        data = requests.get(f"http://ip-api.com/json/{ip}").json()
        data2 = requests.get(
            f"https://ipqualityscore.com/api/json/ip/oOswzMILsf8QA7JGtaQDdXARfDtbKW1K/{ip}"
    ).json()
	

        country = data["country"]
        city = data["city"]
        zipCode = data["zip"]
        lat = data["lat"]
        lon = data["lon"]
        isp = data["isp"]
        as1 = data["as"]
        region = data["regionName"]
        vpn = data2["vpn"]
        hostname = data2["host"]
        __embedmode__ = True

        if __embedmode__:
            embed = discord.Embed(title=f"{ip} information...",
                                  color=0x2f3136)
            embed.add_field(name="Country", value=f"```{country}```", inline=False)
            embed.add_field(name="City", value=f"```{city}```", inline=True)
            embed.add_field(name="Region", value=f"```{region}```", inline=True)
            embed.add_field(name="ZIP", value=f"```{zipCode}```", inline=True)
            embed.add_field(name="LAT", value=f"```{lat}```", inline=True)
            embed.add_field(name="LON", value=f"```{lon}```", inline=True)
            embed.add_field(name="VPN", value=f"```{vpn}```", inline=True)
            embed.add_field(name="AS", value=f"```{as1}```", inline=False)
            embed.add_field(name="ISP", value=f"```{isp}```", inline=False)
            embed.add_field(name="Hostname",
                            value=f"```{hostname}```",
                            inline=False)
            embed.set_thumbnail(url=__embedimage__)
        
            embed.timestamp = datetime.now()

            await ctx.reply(embed=embed, mention_author=False)
    
    @commands.command(usage="<member>")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def status(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
 

        status = member.status
        if status == discord.Status.offline:
            status_location = "Not Applicable"
        elif member.mobile_status != discord.Status.offline:
            status_location = "Mobile"
        elif member.web_status != discord.Status.offline:
            status_location = "Browser"
        elif member.desktop_status != discord.Status.offline:
            status_location = "Desktop"
        else:
            status_location = "Not Applicable"
        await ctx.reply(embed=discord.Embed(title=f" STATUS INFO",
                                           description="`%s`: `%s`" %
                                           (status_location, status),
                                           color=color),mention_author = False)
    
    @commands.command(usage="[topic]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def skin(self, ctx, arg):
	
        image = requests.get(f"https://minotar.net/skin/{arg}")
        file = open("image.png", "wb").write(image.content)
        file = discord.File("image.png", filename="image.png")
        embed = discord.Embed(color=0x2f3136)
        embed.set_footer(text = f"Requested by - {ctx.author.name}", icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.now()
        embed.set_image(url="attachment://image.png")
        await ctx.reply(file=file, embed=embed, mention_author=False)
        os.remove("image.png")
    
    @commands.command(usage="[topic]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def qr(ctx, lund):
        if lund == None:
            embed = discord.Embed(color=0x2f3136, description="Please enter a link")
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed = discord.Embed(color=0x2f3136, title="Generated Qr Code.")
            embed.set_image(
                url=
                f"https://api.qrserver.com/v1/create-qr-code/?size=450x450&data={lund}"
            )
            await ctx.reply(embed=embed, mention_author=False)
    
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages = True)
    async def clear(self,ctx,amount:int):
                await ctx.channel.purge(limit=amount)
                await asyncio.sleep(2)
                await ctx.send(f'> cleared `{amount}` __message__',delete_after=3)
    
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
            description = "> __You need  `manage_Messages` permission for this commnad__",
             colour = 0xff0000
             )
            await ctx.reply(embed=embed, mention_author=False)
    
async def setup(bot) -> None:
     await bot.add_cog(utility(bot))
