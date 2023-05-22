import os
import random
import discord
import asyncio
import aiohttp
import datetime
import requests
import animec
import giphy_client
import psutil
import arrow
import button_paginator as pg
import timeago
import typing
from io import BytesIO
from pathlib import Path
from discord.ext import commands
from tools import *
from bs4 import BeautifulSoup
from wordcloud import WordCloud, STOPWORDS
from giphy_client.rest import ApiException
now = datetime.datetime.now()
diff = datetime.datetime(now.year, 12, 25) - \
    datetime.datetime.today()  # Days until Christmas

PERMS_LIST = ['add_reactions', 'administrator', 'attach_files', 'ban_members',
    'change_nickname', 'connect', 'create_instant_invite', 'deafen_members',
    'embed_links', 'external_emojis', 'kick_members', 'manage_channels',
    'manage_emojis', 'manage_guild', 'manage_messages', 'manage_nicknames',
    'manage_permissions', 'manage_roles', 'manage_webhooks', 'mention_everyone',
    'move_members', 'mute_members', 'priority_speaker', 'read_message_history',
    'read_messages', 'send_messages', 'send_tts_messages', 'speak', 'stream',
    'use_external_emojis', 'use_voice_activation', 'view_audit_log',
    'view_channel', 'view_guild_insights']

snipe_message_author = {}
snipe_message_content = {}
snipe_message_attachment = {}
snipe_message_author_avatar = {}
snipe_message_time = {}



class utility(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.launch_time = round(datetime.datetime.now().timestamp())

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
     if not message.guild: return 
     if message.author.bot: return
     if message.attachments:
        snipe_message_attachment[message.channel.id] = message.attachments[0].url
     else:
        snipe_message_attachment[message.channel.id] = None

     snipe_message_author[message.channel.id] = message.author
     snipe_message_content[message.channel.id] = message.content
     snipe_message_author_avatar[message.channel.id] = message.author.display_avatar.url
     snipe_message_time[message.channel.id] = message.created_at


    @commands.command(aliases=["s"], help="check the latest deleted message from a channel", usage="<channel>", description="utility")
    async def snipe(self, ctx): 
     try:
        if snipe_message_content[ctx.channel.id] == "this message contains filtered content": 
          return await ctx.reply(embed=discord.Embed(color=0x2f3136, description=snipe_message_content[ctx.channel.id]), mention_author=False)
        em = discord.Embed(color=0x2f3136, description=snipe_message_content[ctx.channel.id])
        em.set_footer(text=f'Message sent {arrow.get(snipe_message_time[ctx.channel.id]).humanize()}')
        em.set_author(name=snipe_message_author[ctx.channel.id], icon_url=snipe_message_author_avatar[ctx.channel.id])

        if snipe_message_attachment[ctx.channel.id] != None:
         if ".mp4" in snipe_message_attachment[ctx.channel.id] or ".mov" in snipe_message_attachment[ctx.channel.id]:
          url = snipe_message_attachment[ctx.channel.id]
          async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
              data = await r.read()
              bytes_io = BytesIO(data)
              file = discord.File(fp=bytes_io, filename="video.mp4")
              await ctx.reply(embed=em, file=file, mention_author=False)
              return 
         else:
           em.set_image(url=snipe_message_attachment[ctx.channel.id])

        await ctx.reply(embed=em, mention_author=False)
     except KeyError as e: 
        await ctx.reply(f"nothing to snipe", mention_author=False)
        await ctx.reply(e)

    @commands.command(aliases = ['h'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx, command = None):
        try:
            if command == None:
                dev = self.bot.get_user(565627105552105507)
                return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")
            else:
                cmd = self.bot.get_command(command)
                embed = discord.Embed(
                    color = 0x2f3136,
                    title = f"Command: {cmd.name}",
                    description = f"{'N/A' if not cmd.description else cmd.description}")
                embed.add_field(
                    name = "**Aliases**",
                    value = f"{'N/A' if not cmd.aliases else ', '.join(a for a in cmd.aliases)}",
                    inline = False
                )
                embed.add_field(
                    name = "**Usage**",
                    value = f"```{ctx.clean_prefix}{cmd.usage}```",
                    inline = False
                )
                embed.set_author(name = self.bot.user.name, icon_url = self.bot.user.avatar)
                embed.set_thumbnail(url = self.bot.user.avatar)
                embed.set_footer(text = f"Module: {cmd.cog_name}")
                await ctx.send(embed = embed)
        except Exception as e:
            await ctx.send(e)

    @commands.command(pass_context=True, aliases = ['serverinfo'],description = "Shows information on the guild", usage = "serverinfo")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def si(self, ctx):
        try:
            embed = discord.Embed(colour=0x2f3136)
            humans = len([m for m in ctx.guild.members if not m.bot]) / len(ctx.guild.members) * 100
            bots = sum(1 for member in ctx.guild.members if member.bot) / len(ctx.guild.members) * 100
            embed.add_field(name="**Members**", value = f"""**Total:** {len(ctx.guild.members)}
**Bots:** {bots}
**Humans:** {humans}""", inline = False)
            embed.add_field(name="**Counts**", value = f"""**Emojis:** {len([e for e in ctx.guild.emojis if not e.animated])} static & {len([e for e in ctx.guild.emojis if e.animated])} animated
**Roles:** {len(ctx.guild.roles)}
**Channels:** {len(ctx.guild.text_channels)} text & {len(ctx.guild.voice_channels)} voice""", inline = False)
            embed.add_field(name="**Misc**", value = f"""**Verification:** {ctx.guild.verification_level}
**Created:** `{timeago.format(ctx.guild.created_at, datetime.datetime.now().astimezone())}`
**Owner:** {ctx.guild.owner.mention}""", inline = False)
            embed.add_field(name="**Boosts**", value = f"""**Total:** {ctx.guild.premium_subscription_count}
**Boosters:** {len(ctx.guild.premium_subscribers)}
**Boost tier:** {ctx.guild.premium_tier}""", inline = False)
            embed.set_author(name = ctx.guild.name, icon_url = ctx.guild.icon.url if ctx.guild.icon.url else ctx.author.display_avatar)
            embed.set_thumbnail(url = ctx.guild.icon.url if ctx.guild.icon.url else ctx.author.display_avatar)
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)


    @commands.command(name = "whois", description = "Shows information on a user",aliases=['userinfo','stats', 'ui'], usage = "whois [user]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def whois(self, ctx, member: discord.Member=None):
        try:
            x = ""
            member = ctx.author if not member else member
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name = member.name, icon_url = member.display_avatar)
            embed.set_thumbnail(url = member.display_avatar)
            embed.add_field(name = "**Created**", value = f"<t:{round(member.created_at.timestamp())}:D>\n<t:{round(member.created_at.timestamp())}:R>")
            embed.add_field(name = "**Joined**", value = f"<t:{round(member.joined_at.timestamp())}:D>\n<t:{round(member.joined_at.timestamp())}:R>")
            if member.premium_since:
                embed.add_field(name = "**Boosted**", value = f"<t:{round(member.premium_since.timestamp())}:D>\n<t:{round(member.premium_since.timestamp())}:R>")
            embed.add_field(name = "**Roles**", value = ", ".join(role.mention for role in member.roles), inline = False)
            embed.set_footer(text=f"{f'{len(member.mutual_guilds)} mutual guild' if len(member.mutual_guilds) == 1 else f'{len(member.mutual_guilds)} mutual guilds'}")
            data = await self.bot.db2.fetch("SELECT username, discriminator FROM pastusernames WHERE user_id = $1", member.id,)
            if data:
                x += f", ".join(f"{table[0]}#{table[1]}" for table in data)
                embed.add_field(name = "**Username history**", value = x, inline = False)
            await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.send(e)


    @commands.command(name = "donate", description = "Shows payment methods to donate", usage = "donate")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def donate(self, ctx):
        icon_url = ctx.author.avatar
        embed = discord.Embed(title = "All donations are appreciated", colour=0x2F3136)
        embed.add_field(name = "Bitcoin", value = "bc1q60j9jrhjqq0667epr2smp8x95kzaw8gvvhap3n")
        embed.add_field(name = "Ethereum", value = "0x77ec755F387dE024d185530e9526236D9af3B691")
        embed.add_field(name = "Litecoin", value = "LdCmcAZuzM1d62PYUeBuCEskKpa5ZT6tZS")
        embed.set_footer(text = "All donations go towards hosting & api expenses", icon_url = self.bot.user.avatar)
       
        
        await ctx.reply(embed=embed)


    @commands.command(description = "Displays a user's avatar",aliases = ['av'], usage = "av")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def avatar(self, ctx, *,member: discord.User=None):
        try:
            member = ctx.author if not member else member
            embed = discord.Embed(color = member.color)
            embed.set_image(url = member.avatar)
            embed.set_author(name = member.name + "#" + member.discriminator, icon_url = member.avatar)
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(description = "Displays a user's avatar",aliases = ['sav'], usage = "sav")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serveravatar(self, ctx, *,member: discord.User=None):
        try:
            member = ctx.author if not member else member
            embed = discord.Embed(color = member.color)
            if member.guild_avatar:
                embed.set_image(url = member.display_avatar)
                embed.set_author(name = member.name + "#" + member.discriminator, icon_url = member.guild_avatar)
            else:
                await ctx.send(f"{ctx.message.author.mention}: You don't have a server avatar set")
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)


    @commands.command(name = "invite", description = "sends the bot's invite link", aliases = ['inv'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        embed = discord.Embed(description = """Invite me **[here](https://discord.com/api/oauth2/authorize?client_id=1029786157829075047&permissions=8&scope=bot)**""", colour=ctx.author.color)
        embed.set_thumbnail(url = self.bot.user.avatar)
        embed.set_author(name = "Invite the bot", icon_url = self.bot.user.avatar)
        
        await ctx.reply(embed=embed)

    @commands.command(aliases = ['mc'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def membercount(self, ctx):
        embed = discord.Embed(colour=ctx.author.color)
        embed.add_field(name = "**Total members**", value = f"{len(ctx.guild.members)}")
        embed.add_field(name = "**Bots**", value = f"{sum(1 for member in ctx.guild.members if member.bot)}")
        embed.add_field(name = "**Humans**", value = f"{len([m for m in ctx.guild.members if not m.bot])}")
        embed.set_author(name = ctx.guild.name, icon_url = ctx.guild.icon.url)
        
        await ctx.reply(embed=embed)


    @commands.command(name = "",  description = "")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def banner(self, ctx, user: discord.User = None):
        try:
            if user == None:
                user = ctx.author
            else:
                user = user
            user = await self.bot.fetch_user(user.id)
            
            if user.banner:
                embed = discord.Embed(color = user.color)
                embed.set_image(url = user.banner)
                embed.set_author(name = user.name + "#" + user.discriminator, icon_url = user.avatar)
            else:
                embed = discord.Embed(description = f"{ctx.message.author.mention}: **{user.name}** does not have a banner", colour=0x2F3136)

            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)
    

    @commands.command(pass_context=True, name = "spotify", description = "Shows the Spotify song a user is listening to", usage = "spotify [user]")
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
            embed = discord.Embed(description = f"{ctx.message.author.mention}: **{user}** is not listening to spotify", colour=0x2F3136)
            await ctx.reply(embed=embed)
            return 
        except Exception as e:
            print(e)

    @commands.command(name = "gif",  description = "Search for a GIF on Giphy", usage = "gif <something>")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def gif(self, ctx, *, q = None):
        api_key = 'uTes5E5qctsxG6qMnQQCPgN2MxX8DvXx'
        api_instance = giphy_client.DefaultApi()
        try:
            api_responce = api_instance.gifs_search_get(api_key, q, limit = 5, rating = 'g')
            lst = list(api_responce.data)
            giff = random.choice(lst)

            embed = discord.Embed(title = q, colour=ctx.author.color)
            embed.set_image(url = f"https://media.giphy.com/media/{giff.id}/giphy.gif")
            embed.set_author(name = ctx.message.author.name, icon_url = ctx.message.author.avatar)
            
            await ctx.channel.send(embed=embed)

        except ApiException as r:
            print("Exception for the api")

    @commands.command(name = "ping",  description = "Shows the bot's latency", usage = "ping")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        embed = discord.Embed(color = 0x58F288, description = f"<:ping:1038865958133039174> websocket latency: **{round(self.bot.latency * 1000, 2)}** ms (uptime: <t:{self.bot.launch_time}:R>)")
        await ctx.reply(embed=embed)

    @commands.command(name = "servericon",  description = "Displays the server's icon", usage = "servericon")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def servericon(self, ctx):
        if ctx.guild.icon:
            embed = discord.Embed(colour=ctx.author.color)
            embed.set_image(url = ctx.guild.icon.url)
            embed.set_author(name = ctx.guild.name, icon_url = ctx.guild.icon.url)
        else:
            embed = discord.Embed(description = f"{ctx.message.author.mention}: {ctx.guild.name} does not have an icon", colour=0x2F3136)
        
        
        await ctx.reply(embed=embed)

    @commands.command(name = "serverbanner",  description = "Displays the server's banner", usage = "serverbanner")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverbanner(self, ctx):
        if ctx.guild.banner:
            embed = discord.Embed(colour=ctx.author.color)
            embed.set_image(url = ctx.guild.banner)
            embed.set_author(name = ctx.guild.name, icon_url = ctx.guild.icon.url)
        else:
            embed = discord.Embed(description = f"{ctx.message.author.mention}: **{ctx.guild.name}** does not have a banner", colour=ctx.author.color)
        
        
        await ctx.reply(embed=embed)


    @commands.command(name = "reverse",  description = "Reverses text", usage = "reverse <text>")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def reverse(self, ctx,*,msg):
                msg = list(msg)
                msg.reverse()
                embed = discord.Embed(description = "".join(msg), timestamp=ctx.message.created_at, colour=ctx.author.color)
                embed.set_author(name = ctx.message.author, icon_url = ctx.message.author.avatar)
                await ctx.reply(embed=embed)

    @commands.command(aliases = ['emoji', 'steal'], name = "addemoji", description = "Adds an emoji", usage = "addemoji <image_url>")
    @commands.has_permissions(manage_emojis = True)
    async def addemoji(self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji]):
        await ctx.guild.create_custom_emoji(name=emoji.name, image=await emoji.read())
        embed = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> {ctx.author.mention}: Successfully added emoji with the name **{emoji.name}**")
        await ctx.reply(embed=embed)
    @commands.command(name = "deleteemoji", description = "Deletes an emoji", usage = "deleteemoji <emojiname>")
    @commands.has_permissions(manage_emojis = True)
    async def deleteemoji(self, ctx, emoji: discord.Emoji):
        await emoji.delete()
        embed = discord.Embed(description = f"{ctx.message.author.mention}: Emoji **{emoji}** has been deleted",colour=0x2F3136)
        
        await ctx.reply(embed=embed)
        

    @commands.command(aliases=["fancy"], name = "fancify", description = "Turns text into a fancy font", usage = "fancify <text>")
    async def fancify(self, ctx, *, text):
        try:
            def strip_non_ascii(string):
                stripped = (c for c in string if 0 < ord(c) < 127)
                return ''.join(stripped)

            text = strip_non_ascii(text)
            if len(text.strip()) < 1:
                return await self.ctx.reply("ASCII characters only please")
            output = ""
            for letter in text:
                if 65 <= ord(letter) <= 90:
                    output += chr(ord(letter) + 119951)
                elif 97 <= ord(letter) <= 122:
                    output += chr(ord(letter) + 119919)
                elif letter == " ":
                    output += " "
            await ctx.reply(output)

        except:
            await ctx.reply(config.err_mesg_generic)

    @commands.command(aliases=['ud'], name = "urban", description = "Searches the urban dictionary for the definition of a word", usage = "urban <word>")
    async def urban(self, ctx, *msg):
        try:
            word = ' '.join(msg)
            api = "http://api.urbandictionary.com/v0/define"
            # Send request to the Urban Dictionary API and grab info
            response = requests.get(api, params=[("term", word)]).json()
            embeds = []
            embed = discord.Embed(description="No results found", colour=0x2F3136)
            if len(response["list"]) == 0:
                return await ctx.reply(embed=embed)
            if response['list'][1]['definition']:
                embed2 = discord.Embed(title = f"{word}", description = f"{response['list'][1]['definition']}", colour=0x2F3136)
                if response['list'][2]['example']:
                    embed2.add_field(name="Examples:", value=f"{response['list'][1]['example']}")
            if response['list'][2]['definition']:
                embed3 = discord.Embed(title = f"{word}", description = f"{response['list'][2]['definition']}", colour=0x2F3136)
                if response['list'][2]['example']:
                    embed3.add_field(name="Examples:", value=f"{response['list'][2]['example']}")

            embed = discord.Embed(title = f"{word}", description = f"{response['list'][0]['definition']}", colour=0x2F3136)
            embed.add_field(name="Examples:", value=f"{response['list'][0]['example']}")
            embeds = (embed, embed2, embed3)
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=None)
            paginator.add_button('prev')
            paginator.add_button('delete')
            paginator.add_button('next')
            await paginator.start()
        except Exception as e:
            print(e)

            

    @commands.command(aliases=["xmas"], name = "christmas", description = "Shows how many days are left until Christmas", usage = "christmas")
    async def christmas(self, ctx):
        await ctx.reply("**{0}** day(s) left until Christmas :christmas_tree:".format(str(diff.days)))

    @commands.command(name = "covid", description = "Shows COVID-19 statistics for a country", usage = "covid <country>")
    async def covid(self, ctx, *, countryName = None):
        try:
            if countryName is None:
                await ctx.reply("Provide a country")


            else:
                embed = discord.Embed(description = f"Fetching COVID-19 statistics for {countryName}", colour=0x2F3136)
                message = await ctx.reply(embed=embed)
                url = f"https://coronavirus-19-api.herokuapp.com/countries/{countryName}"
                stats = requests.get(url)
                json_stats = stats.json()
                country = json_stats["country"]
                totalCases = json_stats["cases"]
                todayCases = json_stats["todayCases"]
                totalDeaths = json_stats["deaths"]
                todayDeaths = json_stats["todayDeaths"]
                recovered = json_stats["recovered"]
                active = json_stats["active"]
                critical = json_stats["critical"]
                casesPerOneMillion = json_stats["casesPerOneMillion"]
                deathsPerOneMillion = json_stats["deathsPerOneMillion"]
                totalTests = json_stats["totalTests"]
                testsPerOneMillion = json_stats["testsPerOneMillion"]

                embed = discord.Embed(colour=0x2F3136, timestamp=ctx.message.created_at)
                embed.add_field(name = "**Cases**", value = f"""**Total Cases:** {totalCases}
**Cases Today:** {todayCases}
**Cases Per Million:** {casesPerOneMillion}""")
                embed.add_field(name = "**Deaths**", value = f"""**Total Deaths:** {totalDeaths}
**Deaths Today:** {todayDeaths}
**Deaths Per Million:** {deathsPerOneMillion}""")
                embed.add_field(name = "**Tests**", value = f"""**Total tests:** {totalTests}
**Tests Per Milion:** {testsPerOneMillion}""")
                embed.add_field(name = "**Misc**", value = f"""**Recovered:** {recovered}
**Active:** {active}
**Critical:** {critical}""")
                embed.set_author(name = f"COVID-19 Statistics for {country}", icon_url = ctx.message.author.avatar)

                embed.set_thumbnail(url=ctx.message.author.avatar)
                await message.delete()
                await ctx.reply(embed=embed)

        except Exception as e:
            print(e)

    @commands.command(aliases=["perms"], name = "permissions", description = "Shows a list of a user's guild permissions", usage = "permissions [user]")
    async def permissions(self, ctx, *, member:discord.Member=None):
        try:
            member = member or ctx.author
            perms = member.guild_permissions

            message = ""
            embed = discord.Embed(colour=0x2F3136)
            for perm in PERMS_LIST:
                if getattr(perms, perm):
                    message += f"{perm.replace('_', ' ')}, "

            embed.description = f"```{message}```"
            embed.set_author(name = member.name, icon_url = member.avatar)
            embed.set_footer(text=f"Permissions code: {perms.value}")
            
            if not message:
                embed.description = "No guild permissions given to this member"

            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)


    @commands.command(aliases=["rperms"], name = "roleperms", description = "Shows a list of a role's perms", usage = "roleperms <role>")
    async def roleperms(self, ctx, *, role:discord.Role):
        try:
            perms = role.permissions

            message = ""
            embed = discord.Embed(colour=0x2F3136)
            
            for perm in PERMS_LIST:
                if getattr(perms, perm):
                    message += f"{perm.replace('_', ' ')}, "

            embed.description = f"```{message}```"
            embed.set_author(name = role, icon_url = ctx.guild.icon.url)
            embed.set_footer(text=f"Permissions code: {perms.value}")
            if not message:
                embed.description = "No guild permissions assigned to this role"

            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(name = "roleinfo", description = "Shows information on a role", usage = "roleinfo <role_name/id>")
    async def roleinfo(self, ctx, *, role:discord.Role):
        try:
            timestamp = round(role.created_at.timestamp())
            members, percentage = len(role.members), len(role.members) / len(ctx.guild.members) * 100
            members = f"Members: {members} | {percentage:.2f}%"  # defined separately to be able to perform logic on them

            embed = discord.Embed(colour=0x2F3136)
            embed.description = f"""**{members}**
**Created at:** <t:{timestamp}:F> (<t:{timestamp}:R>)
**Hoisted:** {role.hoist}
**Mentionable:** {role.mentionable}
**Position:** {role.position}"""
            embed.set_author(name = role.name, icon_url = ctx.guild.icon.url)
            
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(name = "Emojis", description = "Shows all emojis in a guild", usage = "emojis")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def emojis(self, ctx):
        try:
            lis = ctx.guild.emojis, 64
            if not lis:
                return await ctx.reply("This guild has no emojis")

            for i in lis:
                embed = discord.Embed(description = ",".join(list(map(str, i))), color =0x2F3136)
                embed.set_author(name = ctx.guild.name, icon_url = ctx.guild.icon.url)
                
                await ctx.reply(embed=embed)
                await asyncio.sleep(0.51)
        except Exception as e:
            print(e)

    @commands.command(case_insensitive = True, aliases = ["remind", "remindme", "remind_me"], description = "Schedules a reminder to help you remind something", usage = "reminder <something> <time>")
    async def reminder(self, ctx, time, *, reminder):
        try:
            user = ctx.message.author
            embed = discord.Embed(colour=0x2F3136)
            
            seconds = 0
            if reminder is None:
                embed.description = f"{ctx.message.author.mention}: Specify something to be reminded about" # Error message
            if time.lower().endswith("d"):
                seconds += int(time[:-1]) * 60 * 60 * 24
                counter = f"{seconds // 60 // 60 // 24} days"
            if time.lower().endswith("h"):
                seconds += int(time[:-1]) * 60 * 60
                counter = f"{seconds // 60 // 60} hours"
            elif time.lower().endswith("m"):
                seconds += int(time[:-1]) * 60
                counter = f"{seconds // 60} minutes"
            elif time.lower().endswith("s"):
                seconds += int(time[:-1])
                counter = f"{seconds} seconds"
            if seconds == 0:
                embed.description = f'{ctx.message.author.mention}: Specify a proper duration'
            elif seconds < 5:
                embed.description = f'{ctx.message.author.mention}: Minimum duration is 5 seconds'
            elif seconds > 7776000:
                embed.description = f'{ctx.message.author.mention}: Maximum duration is 90 days'
            else:
                embed = discord.Embed(description = f"{ctx.message.author.mention}: I will remind you about `{reminder}` in {counter}",color=0xA8EA7B)
                await ctx.reply(embed=embed)
                await asyncio.sleep(seconds)
                await ctx.reply(f"{ctx.message.author.mention}, {reminder}")
                return
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)


    @commands.command(description = "Shows information on an anime", usage = "anime <name>")
    async def anime(self, ctx, *, query):
        try:
            embed = discord.Embed(description = f"Fetching anime information", colour=0x2F3136)
            message = await ctx.reply(embed=embed)
            anime = animec.Anime(query)
        except:
            embed = discord.Embed(description = "No results found")
            await ctx.reply(embed=embed)

        try:
                title = str(anime.title_english) if str(anime.title_english) else str(anime.title_japanese)
                embed = discord.Embed(title = "Anime search results", url = anime.url, description = f"""**{str(anime.title_english)}**
**Description:** {anime.description[:500]}...""", colour=0x2F3136)
                embed.add_field(name = "General", value = f"""**Genres:** {str(anime.genres)}
**Aired:** {str(anime.aired)}
**Broadcast:** {str(anime.broadcast)}
**Popularity:** {str(anime.popularity)}""")
                embed.add_field(name = "Overview", value = f"""**Episodes:** {str(anime.episodes)}
**NSFW:** {str(anime.is_nsfw())}
**Status:** {str(anime.status)}""")
                embed.add_field(name = "Scores", value = f"""**Favorites:** {str(anime.favorites)}
**Rating:** {str(anime.rating)}
**Rank:** {str(anime.ranked)}""")
                embed.set_thumbnail(url = anime.poster)
                embed.set_author(name = ctx.message.author.name, icon_url = ctx.message.author.avatar)
                await message.delete()
                await ctx.reply(embed = embed)
        except Exception as e:
            print(e)

    @commands.command(description = "Posts text to hastebin", usage = "hastebin <text>")
    async def hastebin(self, ctx, *, code):
        try:
            if code.startswith('```') and code.endswith('```'):
                code = code[3:-3]
            else:
                code = code.strip('` \n')
            async with aiohttp.ClientSession() as cs:
                async with cs.post("https://hastebin.com/documents", data=code) as resp:
                    data = await resp.json()
                    key = data['key']
            embed = discord.Embed(description=f"https://hastebin.com/{key}", colour=0x2F3136)
            embed.set_author(name = "Hastebin code", icon_url = ctx.message.author.avatar)
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command()
    async def inrole(self, ctx, *, role: discord.Role):
        try:
            embeds = []
            x = ""
            page = 1
            num = 0
            members = 0
            for member in role.members:
                num += 1
                members += 1
                x += f"`{num}` **{member.name}#{member.discriminator}**\n"
                if members == 10:
                    embeds.append(discord.Embed(color = 0x2f3136, title = f"Users with {role.name}", description = x).set_author(name=ctx.author.name, icon_url = ctx.author.display_avatar).set_footer(text=f"{page}/{int(len(role.members)/10)+1 if len(role.members)/10 > int(len(role.members)/10) and int(len(role.members)/10) < int(len(role.members)/10)+1 else int(len(role.members)/10)} ({len(role.members)} entries)"))
                    page += 1
                    x = ""
                    members = 0
            if len(role.members) < 1:
                await ctx.reply("Nobody has that role")
            else:
                embeds.append(discord.Embed(color = 0x2f3136, title = f"Users with {role.name}", description = x).set_author(name=ctx.author.name, icon_url = ctx.author.display_avatar).set_footer(text=f"{page}/{int(len(role.members)/10)+1 if len(role.members)/10 > int(len(role.members)/10) and int(len(role.members)/10) < int(len(role.members)/10)+1 else int(len(role.members)/10)} ({len(role.members)} entries)"))
                paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
                paginator.add_button('prev')
                paginator.add_button('next')
                await paginator.start()
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases = ['bl', 'boosters'])
    async def boosterlist(self, ctx):
        try:
            embeds = []
            x = ""
            page = 1
            num = 0
            boosters = 0
            for booster in ctx.guild.premium_subscribers[::-1]:
                num += 1
                boosters += 1
                x += f"`{num}` {booster.mention} boosted **{timeago.format(booster.premium_since, datetime.datetime.now().astimezone())}**\n"
                if boosters == 10:
                    embeds.append(discord.Embed(color = 0x2f3136, title = f"{ctx.guild.name}'s boosters", description = x).set_author(name=ctx.author.name, icon_url = ctx.author.display_avatar).set_footer(text=f"{page}/{int(len(ctx.guild.premium_subscribers)/10)+1 if len(ctx.guild.premium_subscribers)/10 > int(len(ctx.guild.premium_subscribers)/10) and int(len(ctx.guild.premium_subscribers)/10) < int(len(ctx.guild.premium_subscribers)/10)+1 else int(len(ctx.guild.premium_subscribers)/10)} ({len(ctx.guild.premium_subscribers)} entries)"))
                    page += 1
                    x = ""
                    boosters = 0
            if len(ctx.guild.premium_subscribers) < 1:
                await ctx.reply("No boosters in this guild")
            else:
                embeds.append(discord.Embed(color = 0x2f3136, title = f"{ctx.guild.name}'s boosters", description = x).set_author(name=ctx.author.name, icon_url = ctx.author.display_avatar).set_footer(text=f"{page}/{int(len(ctx.guild.premium_subscribers)/10)+1 if len(ctx.guild.premium_subscribers)/10 > int(len(ctx.guild.premium_subscribers)/10) and int(len(ctx.guild.premium_subscribers)/10) < int(len(ctx.guild.premium_subscribers)/10)+1 else int(len(ctx.guild.premium_subscribers)/10)} ({len(ctx.guild.premium_subscribers)} entries)"))
                paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
                paginator.add_button('prev')
                paginator.add_button('next')
                await paginator.start()
        except Exception as e:
            print(e)

            
    @commands.command(description = "Shows the latest anime news", usage = "aninews")
    async def aninews(self, ctx, amount:int = 4):
        try:
            embed = discord.Embed(description = f"Fetching anime news", colour=0x2F3136)
            message = await ctx.reply(embed=embed)
            await asyncio.sleep(1)
            news = animec.Aninews(amount)
            links = news.links
            titles = news.titles
            descriptions = news.description

            embed = discord.Embed(title = "Latest Anime News", timestamp = datetime.datetime.utcnow(), colour=0x2F3136)
            embed.set_thumbnail(url = news.images[0])

            for i in range(amount):
                embed.add_field(name = f"{i+1}) {titles[i]}", value = f"{descriptions[i][:200]}...\n[Read more]({links[i]})", inline = False)
            await message.delete()
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(aliases = ['e'], description = "Enlarges an emoji", usage = "enlarge <emoji>")
    async def enlarge(self, ctx, *,em : discord.Emoji = None):
        embed = discord.Embed(color = 0x2F3136)
        embed.set_image(url = em.url)
        await ctx.send(embed=embed)



    @commands.command(description = "Shows a picture of an anime character", usage = "anime <character_name>")
    async def character(self, ctx, *, query):
        try:
            embed = discord.Embed(description = f"Fetching character", colour=0x2F3136)
            message = await ctx.reply(embed=embed)
            try:
                char = animec.Charsearch(query)
            except Exception as e:
                embed = discord.Embed(description = f"<:warn:1012642863701565481>  Something went wrong: {e}", colour=0x2F3136)
                await message.delete()
                await ctx.reply(embed=embed)
                return

            embed = discord.Embed(title = char.title, url = char.url, colour=0x2F3136)
            embed.set_image(url = char.image_url)
            embed.set_footer(text = ", ".join(list(char.references.keys())[:2]))
            await message.delete()
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(aliases = ['info'], description = "Shows some information about the bot", usage = "botinfo")
    async def botinfo(self, ctx):
        try:
            lines=0
            pathh=Path(os.getcwd())
            paths=[p for p in pathh.iterdir()]
            for path in paths:
                if path.is_file() and path.suffix == '.py':
                    z=path.open(mode='r')
                    lines+=len(z.readlines())
                    z.close()
                elif path.is_dir():
                    for p in path.iterdir():
                        if p.is_file() and p.suffix=='.py':
                            z=p.open(mode='r')
                            lines+=len(z.readlines())
                            z.close()
            x = 0
            z = 0
            y = 0
            for guild in self.bot.guilds:
                x += len(guild.channels)
            for guild in self.bot.guilds:
                z += len(guild.categories)
            for guild in self.bot.guilds:
                y += len(guild.roles)
            dev = self.bot.get_user(565627105552105507)
            embed = discord.Embed(color = 0x2f3136, description = f"""Developed & maintained by **[{dev.name}#{dev.discriminator}](https://discord.com/users/{dev.id})**""")
            embed.add_field(name = "**Statistics**", value = f"""**Guilds:** {len(self.bot.guilds)}
**Channels:** {x}
**Categories:** {z}
**Roles:** {y}
**Users: ** {len(self.bot.users)}""", inline = False)
            embed.add_field(name = "**Client**", value = f"""**Memory used:** {psutil.Process().memory_full_info().rss / 102400000 * 100} MB
**Total memory:** {round(round(psutil.virtual_memory().total) / 102400000) / 10} GB
**Commands:** {len(set(self.bot.walk_commands()))}
**Lines:** {lines}
**Ping:** {round(self.bot.latency * 1000, 2)} ms
**Last boot: ** <t:{self.bot.launch_time}:R>""", inline = False)
            embed.set_author(name = "wonder", icon_url = self.bot.user.avatar)
            embed.set_thumbnail(url=self.bot.user.avatar)
            embed.set_footer(text = "contact artist for support")
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)


    @commands.command(aliases = ['rl', 'roles'])
    async def rolelist(self, ctx):
        try:
            embeds = []
            x = ""
            page = 1
            num = 0
            roles = 0
            for role in ctx.guild.roles[::-1]:
                num += 1
                roles += 1
                x += f"`{num}` {role.mention} ({len(role.members)} members)\n"
                if roles == 10:
                    embeds.append(discord.Embed(color = 0x2f3136, title = f"{ctx.guild.name}'s roles", description = x).set_author(name=ctx.author.name, icon_url = ctx.author.display_avatar).set_footer(text=f"{page}/{int(len(ctx.guild.roles)/10)+1 if len(ctx.guild.roles)/10 > int(len(ctx.guild.roles)/10) and int(len(ctx.guild.roles)/10) < int(len(ctx.guild.roles)/10)+1 else int(len(ctx.guild.roles)/10)} ({len(ctx.guild.roles)} entries)"))
                    page += 1
                    x = ""
                    roles = 0
            if len(ctx.guild.roles) < 1:
                await ctx.reply("No roles in this guild")
            else:
                embeds.append(discord.Embed(color = 0x2f3136, title = f"{ctx.guild.name}'s roles", description = x).set_author(name=ctx.author.name, icon_url = ctx.author.display_avatar).set_footer(text=f"{page}/{int(len(ctx.guild.roles)/10)+1 if len(ctx.guild.roles)/10 > int(len(ctx.guild.roles)/10) and int(len(ctx.guild.roles)/10) < int(len(ctx.guild.roles)/10)+1 else int(len(ctx.guild.roles)/10)} ({len(ctx.guild.roles)} entries)"))
                paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
                paginator.add_button('prev')
                paginator.add_button('next')
                await paginator.start()
        except Exception as e:
            print(e)
    @commands.command(aliases = ['cl', 'channels'])
    async def channellist(self, ctx):
        try:
            embeds = []
            x = ""
            page = 1
            num = 0
            channels = 0
            for channel in ctx.guild.channels[::-1]:
                if channel is not discord.CategoryChannel:
                    num += 1
                    channels += 1
                    x += f"`{num}` {channel.mention} ({round(channel.created_at.timestamp())})\n"
                    if channels == 10:
                        embeds.append(discord.Embed(color = 0x2f3136, title = f"{ctx.guild.name}'s channels", description = x).set_author(name=ctx.author.name, icon_url = ctx.author.display_avatar).set_footer(text=f"{page}/{int(len(ctx.guild.channels)/10)+1 if len(ctx.guild.channels)/10 > int(len(ctx.guild.channels)/10) and int(len(ctx.guild.channels)/10) < int(len(ctx.guild.channels)/10)+1 else int(len(ctx.guild.channels)/10)} ({len(ctx.guild.channels)} entries)"))
                        page += 1
                        x = ""
                        channels = 0
            if len(ctx.guild.channels) < 1:
                await ctx.reply("No channels in this guild")
            else:
                embeds.append(discord.Embed(color = 0x2f3136, title = f"{ctx.guild.name}'s channels", description = x).set_author(name=ctx.author.name, icon_url = ctx.author.display_avatar).set_footer(text=f"{page}/{int(len(ctx.guild.channels)/10)+1 if len(ctx.guild.channels)/10 > int(len(ctx.guild.channels)/10) and int(len(ctx.guild.channels)/10) < int(len(ctx.guild.channels)/10)+1 else int(len(ctx.guild.channels)/10)} ({len(ctx.guild.channels)} entries)"))
                paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
                paginator.add_button('prev')
                paginator.add_button('next')
                await paginator.start()
        except Exception as e:
            print(e)

    
    @commands.command(aliases = ['whi'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def weheartit(self, ctx, *, query = None):
        try:
            async with ctx.typing():
                url=f"https://weheartit.com/search/entries?query=%7B{query.replace(' ', '+')}"
                z = 0
                links=[]
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as x:
                        soup=BeautifulSoup(await x.text(), features='html.parser')
                        divs=str(soup.find_all('div', class_='entry grid-item'))
                        soup2=BeautifulSoup(divs, features='html.parser')
                        badge=soup2.find_all(class_='entry-badge')
                        images=soup2.find_all('img')
                        for image in images:
                            if 'data.whicdn.com/images/' in str(image):
                                z += 1
                                links.append(discord.Embed(color=0x2f3136).set_image(url=image['src']).set_author(name = f"{query}", icon_url = ctx.author.display_avatar).set_footer(text=f"{z}/{len(images)}"))

                paginator = pg.Paginator(self.bot, links, ctx, invoker = ctx.author.id)
                paginator.add_button('prev')
                paginator.add_button('delete')
                paginator.add_button('next')
                await paginator.start()
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases=['wc'])
    async def wordcloud(self, ctx, limit: int=100):
        async with ctx.typing():

            text=[message.content async for message in ctx.channel.history(limit=limit)]
            wc = WordCloud(mode = "RGBA", background_color=None,  height=400, width=700)
            wc.generate(' '.join(text))
            wc.to_file(filename=f'{ctx.author.id}.png')
    
            await ctx.send(file=discord.File(f"{ctx.author.id}.png"))
            os.remove(f'{ctx.author.id}.png')

    @commands.command(aliases=['ce'])
    async def embed(self, ctx, *, code):
        x = await to_object(await embed_replacement(ctx.author, code))
        await ctx.send(file=x[0], content=x[1], embed=x[2], view=x[3])


    @commands.command()
    async def bladee(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:7777/bladee") as resp:
                sex = await resp.json()
        await ctx.send(embed=discord.Embed(color=0x2f3136).set_image(url=sex['image']))

async def setup(bot):
    await bot.add_cog(utility(bot))
