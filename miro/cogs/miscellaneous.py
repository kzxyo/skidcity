import discord, aiohttp, button_paginator as pg, random, giphy_client, requests, time
from pytube import YouTube
from discord import Embed, Guild, Invite, Message, Role
from discord.ext import commands, tasks
from PIL import Image
from discord.utils import format_dt
from colorthief import ColorThief
from discord.ext.commands import (
    Cog,
    command,
    Context,
    cooldown,
    BucketType,
    AutoShardedBot as Bot,
)
from typing import Union
from discord.ui import View, Button, Select
from io import BytesIO
from modules import utils
from data.database import Async




class youtube(commands.Cog):
    def __init__(self, client):
        self.client = client


class hotcmds(commands.Cog):
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
        self.av = "https://cdn.discordapp.com/attachments/1116443743831199814/1118245305352200332/Cherry_Blossoms.png"



    @commands.hybrid_command(name = "spotify_global", description = "Show entire guild spotify listeners",aliases=['spotify', 'spot'], usage = "spotify")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def spotify_global(self, ctx: Context):
        async with ctx.typing():
            embeds = []
            page = 0

            # Get all the members listening to spotify
            members = [
                member
                for member in ctx.guild.members
                if member.activities
                and any(
                    activity.type == discord.ActivityType.listening
                    and activity.name == "Spotify"
                    for activity in member.activities
                )
            ]

            # If there are no members listening to spotify, return
            if not members:
                return await ctx.error(
                    content="No one is listening to spotify in this server"
                )

            # Sort the members by their spotify activity
            members.sort(
                key=lambda member: discord.utils.find(
                    lambda activity: activity.type == discord.ActivityType.listening
                    and activity.name == "Spotify",
                    member.activities,
                ).title
            )

            # Create the embeds
            for member in members:
                activity = discord.utils.find(
                    lambda activity: activity.type == discord.ActivityType.listening
                    and activity.name == "Spotify",
                    member.activities,
                )

                embed = discord.Embed(
                    title=f"{member}'s Spotify",
                    description=f"**Song:** {activity.title}\n**Album:** {activity.album}\n**Artist:** {activity.artist}",
                    color=0x4c5264,
                )

                embed.set_thumbnail(url=activity.album_cover_url)

                embeds.append(embed)

            if len(embeds) == 1:
                return await ctx.send(embed=embeds[0])

            # Create the paginator
            from modules import paginator as pg

            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button(
                "prev",
                emoji="<:left:1107307769582850079>",
                style=discord.ButtonStyle.blurple,
            )
            paginator.add_button(
                "next",
                emoji="<:right:1107307767041105920>",
                style=discord.ButtonStyle.blurple,
            )
            paginator.add_button(
                "goto",
                emoji="<:filter:1113850464832868433>",
                style=discord.ButtonStyle.gray,
            )
            paginator.add_button(
                "delete",
                emoji="<:page_cancel:1121826948520362045>",
                style=discord.ButtonStyle.red,
            )
            await paginator.start()


    @commands.command(name = "nickname", description = "Make miro set a nickname for user",aliases=['nick', 'setnick'], usage = "setnick [nickname]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nickname: str = None):
        if nickname is None:
            await ctx.send(
                embed=discord.Embed(
                    description="<:miroapprove:1117144152363245638> {}: successfully reset {}'s nickname".format(
                        ctx.author.mention, member.mention, nickname
                    ),
                    color=0x4c5264,
                )
            )
            await member.edit(nick=nickname)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description="<:miroapprove:1117144152363245638> {}: changed {}'s nickname to {}".format(
                        ctx.author.mention, member.mention, nickname
                    ),
                    color=0x4c5264,
                )
            )
            await member.edit(nick=nickname)

    @commands.command(name = "hide", description = "Make miro hide a text channel",aliases=["hc", "hidechan", "hchannel", "hidechannel"], usage = "hidechannel")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.has_permissions(manage_channels=True)
    async def hide(ctx: commands.Context, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        perms = ctx.channel.overwrites_for(ctx.guild.default_role)
        perms.view_channel = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)
        await ctx.send(
            embed=discord.Embed(
                description="<:miroapprove:1117144152363245638> {}: successfully hid channel".format(
                    ctx.author.mention
                ),
                color=0x4c5264,
            )
        )

    @commands.command(name = "unhide", description = "Make miro unhide a text channel",aliases=["uhc", "unhidechan", "uhchannel", "unhidechannel"], usage = "unhidechannel")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.has_permissions(manage_channels=True)
    async def unhide(self, ctx: commands.Context, channel: discord.TextChannel = None):
        try:
            channel = channel or ctx.channel
            perms = ctx.channel.overwrites_for(ctx.guild.default_role)
            perms.view_channel = True
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)
            await ctx.send(
                embed=discord.Embed(
                    description="<:miroapprove:1117144152363245638> {}: successfully unhid channel".format(
                        ctx.author.mention
                    ),
                    color=0x4c5264,
                )
            )
        except discord.Forbidden:
            await ctx.send(
                embed=discord.Embed(
                    description="<:mirow:1117144157992009728> {}: I don't have permission to unhide the channel.".format(
                        ctx.author.mention
                    ),
                    color=0x4c5264,
                )
            )
        except Exception as e:
            await ctx.send(
                embed=discord.Embed(
                    description="<:mirodeny:1117144156507209829> {}: An error occurred while unhiding the channel.".format(
                        ctx.author.mention
                    ),
                    color=0x4c5264,
                )
            )
            print(e)

    @commands.command(name = "setname", description = "Make miro set the servername", aliases=["sname", "servername"], usage = "servername [name]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def setname(self, ctx, *, name=None):
        try:
            if name is None:
                raise ValueError("Specify a name for me to set")

            await ctx.guild.edit(name=name)
            await ctx.send(
                embed=discord.Embed(
                    description="<:miroapprove:1117144152363245638> {}: Server name has been set to `{name}`".format(
                        ctx.author.mention
                    ),
                    color=0x4c5264,
                )
            )
        except discord.Forbidden:
            await ctx.send(
                embed=discord.Embed(
                    description="<:mirow:1117144157992009728> {}: I don't have permission to change the server name.".format(
                        ctx.author.mention
                    ),
                    color=0x4c5264,
                )
            )
        except ValueError as ve:
            await ctx.send(
                embed=discord.Embed(
                    description=f"<:mirodeny:1117144156507209829> {ctx.author.mention}: {str(ve)}",
                    color=0x4c5264,
                )
            )

    @commands.command(
        name="serverbanner",
        description="View the banner of a server",
        brief="guild",
        usage="Syntax: <guild>",
        aliases=["sb"],
    )
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def serverbanner(self, ctx, *, guild: discord.Guild = None):
        ctx.typing()
        guild = ctx.guild if guild is None else guild
        e = discord.Embed(
            title=f"{guild.name}'s server banner", url=guild.banner, color=0x4c5264
        )
        e.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        e.set_image(url=guild.banner)
        await ctx.send(embed=e)

    @commands.command(
        name="serversplash",
        description="View the splash of a server",
        brief="guild",
        usage="serversplash <guild>",
        aliases=["splash", "guildsplash"],
    )
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def serversplash(self, ctx, *, guild: discord.Guild = None):
        ctx.typing()
        guild = ctx.guild if guild is None else guild
        e = discord.Embed(
            color=0x4c5264, title=f"{guild.name}'s server splash", url=guild.splash
        )
        e.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        e.set_image(url=guild.splash)
        await ctx.send(embed=e)

    @commands.command(name = "inrole", description = "Show users in a specified role",aliases=["ir"], usage = "inrole [role]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
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
                    embeds.append(
                        discord.Embed(
                            color=0x4c5264,
                            title=f"Users with {role.name}",
                            description=x,
                        )
                        .set_author(
                            name=ctx.author.name, icon_url=ctx.author.display_avatar
                        )
                        .set_footer(
                            text=f"{page}/{int(len(role.members)/10)+1 if len(role.members)/10 > int(len(role.members)/10) and int(len(role.members)/10) < int(len(role.members)/10)+1 else int(len(role.members)/10)} ({len(role.members)} entries)"
                        )
                    )
                    page += 1
                    x = ""
                    members = 0
            if len(role.members) < 1:
                await ctx.reply("Nobody has that role")
            else:
                embeds.append(
                    discord.Embed(
                        color=0x4c5264, title=f"Users with {role.name}", description=x
                    )
                    .set_author(
                        name=ctx.author.name, icon_url=ctx.author.display_avatar
                    )
                    .set_footer(
                        text=f"{page}/{int(len(role.members)/10)+1 if len(role.members)/10 > int(len(role.members)/10) and int(len(role.members)/10) < int(len(role.members)/10)+1 else int(len(role.members)/10)} ({len(role.members)} entries)"
                    )
                )
                paginator = pg.Paginator(self.bot, embeds, ctx, timeout=100, invoker=ctx.author.id)
                paginator.add_button("prev", emoji="<:left:1107307769582850079>")
                paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
                paginator.add_button("next", emoji="<:right:1107307767041105920>")
                await paginator.start()
        except Exception as e:
            await ctx.send(e)

    @commands.command(name = "iq", description = "Show's your iq rate",aliases=["iqrate"], usage = "iq [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def iq(self, ctx, user: discord.Member = None):
        if user == None:
            embed = discord.Embed(
                color=0x4c5264,
                title="iq test",
                description=f"{ctx.author.mention} has `{random.randrange(201)}` iq :brain:",
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed = discord.Embed(
                color=0x4c5264,
                title="iq test",
                description=f"{user.mention} has `{random.randrange(201)}` iq :brain:",
            )
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "hot", description = "Show's your hot rate",aliases=["howhot", "hotrate"], usage = "hot [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def hot(self, ctx, user: discord.Member = None):
        if user == None:
            embed = discord.Embed(
                color=0x4c5264,
                title="hot rate",
                description=f"{ctx.author.mention} is `{random.randrange(101)}%` hot :hot_face:",
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed = discord.Embed(
                color=0x4c5264,
                title="hot r8",
                description=f"{user.mention} is `{random.randrange(101)}%` hot :hot_face:",
            )
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "bitches", description = "Show's your bitch rate",aliases=["bitchrate"], usage = "bitchrate [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def bitches(self, ctx, user: discord.Member = None):
        if user == None:
            embed = discord.Embed(
                color=0x4c5264,
                description=f"{ctx.author.mention} has `{random.randrange(51)}` bitches",
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed = discord.Embed(
                color=0x4c5264,
                description=f"{user.mention} has `{random.randrange(51)}` bitches",
            )
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name = "meme", description = "Return's random meme",aliases=["rmeme"], usage = "meme")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://api.popcat.xyz/meme") as response3:
                data3 = await response3.json()

                image = data3["image"]
                title = data3["title"]
                url = data3["url"]
                upvotes = data3["upvotes"]
                comments = data3["comments"]
                embed3 = discord.Embed(color=0x4c5264)
                embed3.set_image(url=image)
                e = discord.Embed(color=0x4c5264, description=f"[{title}]({url})")
                e.set_footer(text=f"❤️ {upvotes}  💬 {comments}")
                await ctx.reply(embeds=[embed3, e], mention_author=False)

    @commands.command(
        help="utility", description="see all emojis", aliases=["guildemojis"], usage = "emojilist"
    )
    @commands.cooldown(1, 6, commands.BucketType.guild)
    async def emojilist(self, ctx: Context):
        i = 0
        k = 1
        l = 0
        mes = ""
        number = []
        messages = []
        for emoji in ctx.guild.emojis:
            mes = f"{mes}`{k}` {emoji} - ({emoji.name})\n"
        k += 1
        l += 1
        if l == 100:
            messages.append(mes)
        number.append(
            discord.Embed(
                color=0x4c5264,
                title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]",
                description=messages[i],
            )
        )
        i += 1
        mes = ""
        l = 0

        messages.append(mes)
        number.append(
            discord.Embed(
                color=0x4c5264,
                title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]",
                description=messages[i],
            )
        )
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button("prev", emoji="<:left:1107307769582850079>")
        paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
        paginator.add_button("next", emoji="<:right:1107307767041105920>")
        await paginator.start()

    @commands.command(name="xbox", description="show a xbox account", usage=" xbox [username]", aliases=["xb"])
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def xbox(self, ctx, *, username):
        try:
            try:
                username = username.replace(" ", "%20")
            except:
                pass
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as client:
                async with client.get(
                    f"https://playerdb.co/api/player/xbox/{username}"
                ) as r:
                    data = await r.json()
                    try:
                        embed = (
                            discord.Embed(
                                title=data["data"]["player"]["username"],
                                color=int("0f7c0f", 16),
                                url=f"https://xboxgamertag.com/search/{username}",
                            )
                            .add_field(
                                name="Gamerscore",
                                value=data["data"]["player"]["meta"]["gamerscore"],
                                inline=True,
                            )
                            .add_field(
                                name="Tenure",
                                value=data["data"]["player"]["meta"]["tenureLevel"],
                                inline=True,
                            )
                            .add_field(
                                name="Tier",
                                value=data["data"]["player"]["meta"]["accountTier"],
                                inline=True,
                            )
                            .add_field(
                                name="Rep",
                                value=data["data"]["player"]["meta"][
                                    "xboxOneRep"
                                ].strip("Player"),
                                inline=True,
                            )
                            .set_author(
                                name=ctx.author, icon_url=ctx.author.display_avatar
                            )
                            .set_footer(
                                text="Xbox",
                                icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png",
                            )
                        )
                        embed.set_thumbnail(
                            url=data["data"]["player"]["avatar"]
                        ).add_field(
                            name="ID", value=data["data"]["player"]["id"], inline=True
                        )
                        if data["data"]["player"]["meta"]["bio"]:
                            embed.description = data["data"]["player"]["meta"]["bio"]
                        await ctx.reply(embed=embed)
                    except:
                        embed = (
                            discord.Embed(
                                title=data["data"]["player"]["username"],
                                color=int("0f7c0f", 16),
                                url=f"https://xboxgamertag.com/search/{username}",
                            )
                            .add_field(
                                name="Gamerscore",
                                value=data["data"]["player"]["meta"]["gamerscore"],
                                inline=True,
                            )
                            .add_field(
                                name="Tenure",
                                value=data["data"]["player"]["meta"]["tenureLevel"],
                                inline=True,
                            )
                            .add_field(
                                name="Tier",
                                value=data["data"]["player"]["meta"]["accountTier"],
                                inline=True,
                            )
                            .add_field(
                                name="Rep",
                                value=data["data"]["player"]["meta"][
                                    "xboxOneRep"
                                ].strip("Player"),
                                inline=True,
                            )
                            .set_author(
                                name=ctx.author, icon_url=ctx.author.display_avatar
                            )
                            .set_footer(
                                text="Xbox",
                                icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png",
                            )
                            .add_field(
                                name="ID",
                                value=data["data"]["player"]["id"],
                                inline=True,
                            )
                        )
                        if data["data"]["player"]["meta"]["bio"]:
                            embed.description = data["data"]["player"]["meta"]["bio"]
                        await ctx.reply(embed=embed)
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"<:mirow:1117144157992009728> Gamertag **`{username}`** not found",
                    color=int("f7f9f8", 16),
                )
            )

    @commands.command(name = "roles", description = "See all server roles",aliases=["rl"], usage = "roles")
    @commands.cooldown(1, 6, commands.BucketType.guild)
    async def roles(self, ctx):
        i = 0
        k = 1
        l = 0
        mes = ""
        number = []
        messages = []
        for role in ctx.guild.roles:
            mes = f"{mes}`{k}` {role.mention} - <t:{int(role.created_at.timestamp())}:R> ({len(role.members)} members)\n"
            k += 1
            l += 1
            if l == 10:
                messages.append(mes)
                number.append(
                    Embed(
                        color=0x4c5264,
                        title=f"{ctx.guild.name} roles [{len(ctx.guild.roles)}]",
                        description=messages[i],
                    )
                )
                i += 1
                mes = ""
                l = 0

        messages.append(mes)
        embed = Embed(
            color=0x4c5264,
            title=f"{ctx.guild.name} roles [{len(ctx.guild.roles)}]",
            description=messages[i],
        )
        number.append(embed)
        if len(number) > 1:
            paginator = pg.Paginator(self.bot, number, ctx, timeout=44, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()

    @commands.command(name = "bots", description = "see all server bots",aliases=["botlist"], usage = "bots")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def bots(self, ctx):
        i = 0
        k = 1
        l = 0
        b = 0
        mes = ""
        number = []
        messages = []
        for member in ctx.guild.members:
            if member.bot:
                b += 1
                mes = f"{mes}`{k}` {member} - ({member.id})\n"
                k += 1
                l += 1
                if l == 10:
                    messages.append(mes)
                    number.append(
                        Embed(
                            color=0x4c5264,
                            title=f"{ctx.guild.name} bots [{b}]",
                            description=messages[i],
                        )
                    )
                    i += 1
                    mes = ""
                    l = 0

        messages.append(mes)
        embed = Embed(
            color=0x4c5264,
            title=f"{ctx.guild.name} bots [{b}]",
            description=messages[i],
        )
        number.append(embed)
        if len(number) > 1:
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()
        else:
            await ctx.reply(embed=embed)


    @commands.command(aliases = ['he'])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def helpembed(self, ctx):
        try:
            dev = self.bot.get_user(129857040855072768)
            embed = discord.Embed(color=0x4c5264)
            embed.set_footer(text="1/11")
            embed.set_thumbnail(url=self.bot.user.avatar)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
            embed.add_field(name="**Looking for help?**",
                    value=f"use the **buttons** listed below to navigate the help embed.",
                    inline=False)
            
            embed.add_field(name=f"> for regular commands do ;[cmd]\n> for subcommands do ;help [subcmd]\n\u200b",
                value="an asterisk(*) means the command has subcommands",
                inline=False)
            embed2 = discord.Embed(                color=0x4c5264,
                title="**Information  commands**",
                description="""`help, botinfo*, invite*, ping*, userinfo*, upvote*, serversplash*, serverbanner*, inviteinfo*, channelinfo*, roleinfo*, credits*, firstmessage*, servericon*, donate*, wolfram*, btcinfo*, google*`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 2/11")
            embed3 = discord.Embed(                color=0x4c5264,
                title="**Utility  commands**",  
                description="""`afk*, invites*, messages*, ocr*, emojify*, avatar*, banner*, vanitycheck*, github*, tts*, urban*, snipe*, bots*, editsnipe*, vmute*, vumute*, vdeafen*, vudeafen*, vdisconnect*, massmove*, xbox*, spotify*, image*, joinpos*, tiktok*, youtube*, anime*, animenews*, extract*, color*, membercount*, roles*, boosts*, weather*, names, clearnames, clear, fyp*`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 3/11")
            embed4 = discord.Embed(                color=0x4c5264,
                title="**Moderation  commands**",
                description="""`jail*, unjail*, slowmode*, lock*, unlock*, unban*, ban*, nickname*, kick*, unmute*, mute*, botclean*, purge*, muted*, role*, banmsg*, inrole*, hidechannel*, unhidechannel*, servername*, forcenick*, unforcenick*, deletevoice*, createvoice*, nuke*, hardban*`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 4/11")
            embed5 = discord.Embed(                color=0x4c5264,
                title="**Configuration commands**",
                description="""`boost*, welcome*, voicemaster*, skullboard*, setauditlogs*, logs*, vm set, vm unset, createembed*, guildprefix*, autoresponder*, ar add, ar delete, ar list, autorole*, reactionrole*, ignorechannel*, unignorechannel*​, reminder*, gp set, rr add, rr delete, rr list, vanity, vanity role, vanity message, vanity channel, vanity clear, vanity set`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 5/11")
            embed6 = discord.Embed(                color=0x4c5264,
                title="**Fun commands**",
                description="""`rps*, blacktea*, tictactoe*, ship*, howretarded*, howcool*, howgay*, spotifyuser*, translate*, cum*, simp*, hack*, uselessfact*, eject*, pp*, coinflip*, 8ball*, meme*, iq*, hot*, bitches*, fatrate*, lizard*, dog*, cat*, goose*, fox*, roll*, morse*, reverse*, emojify*, scrapbook*`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 6/11")
            embed7 = discord.Embed(                color=0x4c5264,
                title="**Greeting commands**",
                description="""`welcome message, welcome channel, welcome test, welcome clear, pingonjoin, boost message, boost channel, boost test, boost clear`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 7/11")
            embed8 = discord.Embed(                color=0x4c5264,
                title="**Roleplay  commands**",
                description="""`cuddle*, slap*, pat*, laugh*, kiss*, feed*, tickle*, cry*, poke*, baka*`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 8/11")
            embed9 = discord.Embed(                color=0x4c5264,
                title="**Antinuke commands**",
                description="""`settings*, antisetup*, logchannel*, massunban*, whitelist*, whitelisted*, unwhitelist*, punishment*\n\nkick - punishment 1/4\nban - punishment 2/4\nstrip - punishment 3/4\njail - punishment 4/4`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 9/11")
            embed10 = discord.Embed(                color=0x4c5264,
                title="**Crypto commands**",
                description="""`ltc, btc, bnb, eth, usdt, usdc, xrp, busd, sol, ada, dai, doge, ada, matic, dot, shib, trx, wbtc, xlm, bch, neo, leo, uni, cro, near, atom, algo, zec, usdd, usdn, ldo`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 10/11")
            embed11 = discord.Embed(   color=0x4c5264,
                title="**Misc commands**",
                description="""`enlarge*, addemoji*, deleteemoji*, addmultiple*, emojiinfo*, joinlock, modules*, stickers*, emotes*`""",
            ).set_thumbnail(url=self.bot.user.display_avatar.url,
            ).set_footer(text=f"miro bot, page 11/11")
            embeds = (embed, embed2, embed3, embed4, embed5, embed6, embed7, embed8, embed9, embed10, embed11)
            paginator = pg.Paginator(self.bot, embeds, ctx, timeout=30, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()
        except Exception as e:
            print(e)


    @command(
        name="channelinfo",
        description="See info about channel",
        usage="ci <channel>",
        aliases=[
            "cinfo",
            "ci",
        ],
    )
    async def channelinfo(
        self,
        ctx: Context,
        *,
        channel: discord.TextChannel
        | discord.VoiceChannel
        | discord.CategoryChannel = None,
    ) -> Message:
        """
        View information about a channel
        """

        channel = channel or ctx.channel
        if not isinstance(
            channel,
            (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel),
        ):
            return await ctx.send_help()

        embed = Embed(title=channel.name)

        embed.add_field(
            name="Channel ID",
            value=f"`{channel.id}`",
            inline=True,
        )
        embed.add_field(
            name="Type",
            value=f"`{channel.type}`",
            inline=True,
        )
        embed.add_field(
            name="Guild",
            value=f"{ctx.guild} (`{ctx.guild.id}`)",
            inline=True,
        )

        if category := channel.category:
            embed.add_field(
                name="Category",
                value=f"{category} (`{category.id}`)",
                inline=False,
            )

        if isinstance(channel, discord.TextChannel) and channel.topic:
            embed.add_field(
                name="Topic",
                value=channel.topic,
                inline=False,
            )

        elif isinstance(channel, discord.VoiceChannel):
            embed.add_field(
                name="Bitrate",
                value=f"{int(channel.bitrate / 1000)} kbps",
                inline=False,
            )
            embed.add_field(
                name="User Limit",
                value=(channel.user_limit or "Unlimited"),
                inline=False,
            )

        elif isinstance(channel, discord.CategoryChannel) and channel.channels:
            embed.add_field(
                name=f"{len(channel.channels)} Children",
                value=", ".join([child.name for child in channel.channels]),
                inline=False,
            )

        embed.add_field(
            name="Creation Date",
            value=(
                format_dt(channel.created_at, style="f")
                + " **("
                + format_dt(channel.created_at, style="R")
                + ")**"
            ),
            inline=False,
        )

        return await ctx.send(embed=embed)

    @command(
        name="inviteinfo",
        description="see info about guild of given invite code",
        usage="ii (invite)",
        aliases=[
            "ii",
        ],
    )
    async def inviteinfo(self, ctx: Context, invite: Invite) -> Message:
        """
        View basic invite code information
        """

        embed = Embed(title=f"Invite Code: {invite.code}")
        embed.set_thumbnail(url=invite.guild.icon)

        embed.add_field(
            name="Channel & Invite",
            value=(
                f"**Name:** {invite.channel.name} (`{invite.channel.type}`)\n"
                f"**ID:** `{invite.channel.id}`\n"
                "**Created:** "
                + format_dt(
                    invite.channel.created_at,
                    style="f",
                )
                + "\n"
                "**Invite Expiration:** "
                + (
                    format_dt(
                        invite.expires_at,
                        style="R",
                    )
                    if invite.expires_at
                    else "Never"
                )
                + "\n"
                "**Inviter:** Unknown\n"
                "**Temporary:** N/A\n"
                "**Usage:** N/A"
            ),
            inline=True,
        )
        embed.add_field(
            name="Guild",
            value=(
                f"**Name:** {invite.guild.name}\n"
                f"**ID:** `{invite.guild.id}`\n"
                "**Created:** "
                + format_dt(
                    invite.guild.created_at,
                    style="f",
                )
                + "\n"
                f"**Members:** {invite.approximate_member_count:,}\n"
                f"**Members Online:** {invite.approximate_presence_count:,}\n"
                f"**Verification Level:** {invite.guild.verification_level.name.title()}"
            ),
            inline=True,
        )

        view = View()
        for button in [
            Button(
                emoji=emoji,
                label=key,
                url=asset.url,
            )
            for emoji, key, asset in [
                ("🖼", "Icon", invite.guild.icon),
                ("🎨", "Splash", invite.guild.splash),
                ("🏳", "Banner", invite.guild.banner),
            ]
            if asset
        ]:
            view.add_item(button)

        return await ctx.send(embed=embed, view=view)




    @commands.command(name = "color", description = "View hex color",aliases=["hex"], usage = "hex [color]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def color(self, ctx, hex_code: str):
        try:
            # Remove the '#' symbol from the hex code if present
            hex_code = hex_code.strip("#")

            # Convert the hex code to an integer
            color_int = int(hex_code, 16)

            # Create a color object from the integer value
            color = discord.Color(color_int)

            # Create the embed
            embed = discord.Embed(
                title="Color",
                description=f"Hex Code: {hex_code}",
                color=color
            )
            embed.set_thumbnail(url=f"https://dummyimage.com/200x200/{hex_code}/{hex_code}.png")

            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"<:mirodeny:1117144156507209829> An error occurred: {e}",
                color=0xfc5b6d
            )
            await ctx.send(embed=embed)

   
    @commands.command(name = "extract", description = "show dominant color from image",aliases=["et"], usage = "et [attachment]")
    async def extract(self, ctx, attachment: discord.Attachment):
        try:
            image_data = await attachment.read()
            image = Image.open(BytesIO(image_data))
            image = image.resize((200, 200))

            dominant_color = self.extract_dominant_color(image)
            color_image_url = self.upload_color_image(dominant_color)

            embed = discord.Embed(
                title="Dominant Color",
                description="Here is the dominant color extracted from the image:",
                color=int(dominant_color[1:], 16)  # Convert hex color to decimal color value
            )
            embed.add_field(
                name="Hex Color",
                value=dominant_color,
                inline=True
            )
            embed.set_thumbnail(url=color_image_url)

            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"<:mirodeny:1117144156507209829> An error occurred: {e}",
                color=0xfc5b6d
            )
            await ctx.send(embed=embed)

    def extract_dominant_color(self, image):
        temp_file = "temp_image.png"
        image.save(temp_file)

        color_thief = ColorThief(temp_file)
        dominant_color = color_thief.get_color(quality=1)

        hex_color = '#{:02x}{:02x}{:02x}'.format(dominant_color[0], dominant_color[1], dominant_color[2])

        return hex_color

    def upload_color_image(self, hex_color):
        url = f"https://dummyimage.com/100x100/{hex_color[1:]}/{hex_color[1:]}.png"
        response = requests.get(url)
        if response.status_code == 200:
            return url
        return None
    


    @command(
        name="roleinfo",
        usage="ri <role>",
        aliases=[
            "rinf2",
            "ri",
        ],
    )
    async def roleinfo(self, ctx: Context, *, role: Role = None) -> Message:

        role = role or ctx.author.top_role

        embed = Embed(
            color=role.color,
            title=role.name,
        )
        if isinstance(role.display_icon, discord.Asset):
            embed.set_thumbnail(url=role.display_icon)

        embed.add_field(
            name="Role ID",
            value=f"`{role.id}`",
            inline=True,
        )
        embed.add_field(
            name="Guild",
            value=f"{ctx.guild} (`{ctx.guild.id}`)",
            inline=True,
        )
        embed.add_field(
            name="Color",
            value=f"`{str(role.color).upper()}`",
            inline=True,
        )
        embed.add_field(
            name="Creation Date",
            value=(
                format_dt(role.created_at, style="f")
                + " **("
                + format_dt(role.created_at, style="R")
                + ")**"
            ),
            inline=False,
        )
        embed.add_field(
            name=f"{len(role.members):,} Member(s)",
            value=(
                "No members in this role"
                if not role.members
                else ", ".join([user.name for user in role.members][:7])
                + ("..." if len(role.members) > 7 else "")
            ),
            inline=False,
        )

        return await ctx.send(embed=embed)




async def setup(bot):
    await bot.add_cog(hotcmds(bot))
