import discord, datetime, time, aiohttp, humanize, platform, random
from ttapi import TikTokApi
tiktok = TikTokApi(debug=True)
from discord.ext import commands
from collections import deque
from discord import Embed, Message
from discord.ext.commands import Paginator
my_system = platform.uname()
from discord.ext.commands import (
    Cog,
    command,
    Context,
    AutoShardedBot as Bot,
    hybrid_command,
    hybrid_group,
    group,
    check,
)
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils
from modules import paginator as pg
from typing import Optional
from typing import Union
from discord import Embed, File, TextChannel, Member, User, Role
from random import choice
from io import BytesIO
from discord.ui import Button, View


def human_format(number):
    if number > 999: return humanize.naturalsize(number, False, True) 
    return number 


NUM_TO_STORE = 1000
snipe_limit = NUM_TO_STORE
snipes = {}
deleted_msgs = {}
reaction = {}
restore = {}
edited_msgs = {}
emsgat = {}

sc = {}
si = {}
sav = {}
sa = {}
st = {}

esa = {}
esav = {}
esbefore = {}
esafter = {}
est = {}



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
        self.av = "https://cdn.discordapp.com/attachments/1116443743831199814/1118245305352200332/Cherry_Blossoms.png"



    @commands.command(
        name="ping", aliases=["latency"], description="get the bot's latency in ms", usage = "ping"
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def ping(self, ctx):
        start = int(time.time())
        await (await ctx.reply(f"ws: **`{round(self.bot.latency * 1000)}`**")).edit(
            content=f"ws: **`{round(self.bot.latency * 1000)}`**, rest: **`{round((time.time()-start)*1000)}`**"
        )

    @commands.hybrid_command(name = "uptime", description = "Shows uptime of miro",aliases=['upt'], usage = "uptime")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def uptime(self, ctx):
        x = f"Miro has been up for {utils.moment(self.bot.uptime).replace('ago', '')}"
        await ctx.reply(x)

    @commands.hybrid_command(name = "credits", description = "Shows Miro credits",aliases=['owners'], usage = "credits")
    async def _credits(self, ctx):
        embed = (
            discord.Embed(
                color=utils.color("main"),
                title="Miro Credit Menu",
                timestamp=datetime.now(),
            )
            .set_footer(text="Miro")
            .set_thumbnail(url=self.bot.user.avatar)
        )
        embed.add_field(
            name=f"{utils.read_json('emojis')['dash']} Credits",
            value=f"{self.reply} `1` ***{await self.bot.fetch_user(129857040855072768)}*** - Developer & Owner (`129857040855072768`)\n{self.reply} `2` ***{await self.bot.fetch_user(1089940105604636683)}*** - Sponsor/helper (`1089940105604636683`)\n{self.reply} `3` ***{await self.bot.fetch_user(916094817849729054)}*** - Admin/helper (`916094817849729054`)",
        )
        view = discord.ui.View().add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.grey, label="owners", disabled=True
            )
        )
        await ctx.reply(embed=embed, view=view)

    @commands.command(name = "useravatar", description = "Shows avatar of user",aliases=['av','avatar', 'pfp'], usage = "avatar [user]")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def useravatar(self, ctx, member: discord.User = None):
        if member == None:
            useravatar = ctx.author.display_avatar
            embed = discord.Embed(color=0x4c5264)
            embed.set_author(
                name=f"{ctx.author.display_name}#{ctx.author.discriminator}'s avatar",
                icon_url=ctx.author.display_avatar,
                url=f"https://discord.com/users/{ctx.author.id}",
            )
            embed.set_image(url=useravatar)
            await ctx.reply(embed=embed)
            return
        useravatar = member.display_avatar
        embed = discord.Embed(color=0x4c5264)
        embed.set_author(
            name=f"{member.display_name}#{member.discriminator}'s avatar",
            icon_url=member.display_avatar,
            url=f"https://discord.com/users/{member.id}",
        )
        embed.set_image(url=useravatar)
        await ctx.reply(embed=embed)


    @commands.command(aliases = ['hs'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def helpsite(self, ctx, command = None):
        try:
            if command == None:
                dev = self.bot.get_user(129857040855072768)
                return await ctx.reply(f"<:icons_info:1120768285043077252> {ctx.author.mention}: view the commands @ <https://mirobot.gitbook.io/miro/commands>, for support contact **{dev.name}**\n\n<:mail:1107718445845467168> help <command> for more info about the command")
            else:
                cmd = self.bot.get_command(command)
                embed = discord.Embed(
                    color = 0x4c5264,
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

    @commands.command(name = "vote", description = "Returns upvote link",aliases=['upvote', 'upvt'], usage = "upvote")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def vote(self, ctx: commands.Context):
        embed = discord.Embed(
            title=f"**Miro** a multi-purpose discord bot",
            description=f"<a:topgg:1110175782011150367> [vote here](https://discordbotlist.com/bots/miro/upvote)",
            color=0x4c5264,
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(name = "membercount", description = "Return server member count",aliases=['mc'], usage = "membercount")
    @commands.cooldown(1, 3, commands.BucketType.guild)
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



    @commands.hybrid_command(name='invite', description='Get the invite link for Miro.', usage='invite', aliases=['addmiro', 'inv'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def invite(self, ctx: commands.Context):
        embed = discord.Embed(colour=0x4c5264, description=f"Miro\'s Invite: [**Click Here**](https://discord.com/api/oauth2/authorize?client_id=1107283467655458866&permissions=8&scope=bot)")
        await ctx.send(embed=embed)  



    @commands.command(name = "webshot", description = "Return screenshot of site",aliases=['screenshot', 'sa'], usage = "screenshot [link]")
    @commands.guild_only()
    @commands.cooldown(1, 7, commands.BucketType.guild)
    async def webshot(self, ctx, *, link: str = None) -> None:
        if link == None:
            em = discord.Embed(
                color=0x4c5264, description=f"> <:mirodeny:1117144156507209829> You dont type a __site__ for search"
            )
            await ctx.send(embed=em)
            return
        links = ["https://", "http://"]
        if not (link.startswith(tuple(links))):
            await ctx.send(
                embed=discord.Embed(
                    color=0x4c5264,
                    description=f"> <:mirow:1117144157992009728> You didn't input __https __ before the link provided",
                )
            )
            return
        else:
            n = discord.Embed(
                description=f"> Showing {link.replace('https://', '').replace('http://', '')}",
                color=0x4c5264,
            )
            n.set_image(
                url="https://api.popcat.xyz/screenshot?url="
                + str(link.replace("http://", "https://"))
            )
            await ctx.reply(embed=n, mention_author=False)

    @commands.command(name = "github", description = "Return specified user github info",aliases=['git'], usage = "github [user]")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def github(self, ctx, *, user=None):
        if user == None:
            return
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://api.github.com/users/{user}") as r:
                    res = await r.json()
                    name = res["login"]
                    avatar_url = res["avatar_url"]
                    html_url = res["html_url"]
                    email = res["email"]
                    public_repos = res["public_repos"]
                    followers = res["followers"]
                    following = res["following"]
                    twitter = res["twitter_username"]
                    location = res["location"]
                    embed = Embed(color=0x4c5264, title=f"@{name}", url=html_url)
                    embed.set_thumbnail(url=avatar_url)
                    embed.add_field(name="Followers", value=followers)
                    embed.add_field(name="Following", value=following)
                    embed.add_field(name="Repos", value=public_repos)
                    if email:
                        embed.add_field(name="Email", value=email)
                    if location:
                        embed.add_field(name="Location", value=location)
                    if twitter:
                        embed.add_field(name="Twitter", value=twitter)

                    embed.set_thumbnail(url=avatar_url)
                    await ctx.reply(embed=embed)
        except:
            e = Embed(
                color=0x4c5264,
                description=f"<:mirow:1117144157992009728> {ctx.author.mention}: Could not find [@{user}](https://github.com/@{user})",
            )
            await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        datacheck = self.bot.db("nodata")
        if datacheck.get(str(message.author.id)):
            if datacheck.get(str(message.author.id)).get("data") == False:
                return

        ch_id = message.channel.id
        try:
            if not message.author.bot:
                sc[message.channel.id] = message.content
                try:
                    si[message.channel.id] = message.attachments[0]
                except:
                    pass
                sa[message.channel.id] = message.author
                sav[message.channel.id] = message.author.avatar
                st[message.channel.id] = datetime.now()
                if message.content:
                    if ch_id not in deleted_msgs:
                        deleted_msgs[ch_id] = []

                    deleted_msgs[ch_id].append(message)
                else:
                    if ch_id not in deleted_msgs:
                        deleted_msgs[ch_id] = []
                    deleted_msgs[ch_id].append(message)

                if len(deleted_msgs[ch_id]) > snipe_limit:
                    deleted_msgs[ch_id].pop(0)

                modlog = utils.read_json("modlog")

            try:
                if modlog[str(message.guild.id)] != None:
                    embed = discord.Embed(
                        description=f"msg by {message.author.mention} deleted in <#{message.channel.id}>\nmsg deleted <t:{round(st[message.channel.id].timestamp())}:R>",
                        timestamp=datetime.now(),
                    )
                    embed.set_author(
                        name=sa[message.channel.id], icon_url=sav[message.channel.id]
                    )
                    embed.add_field(
                        name="msg content",
                        value=f"***{sa[message.channel.id]}***: {sc[message.channel.id]}",
                    )
                    try:
                        embed.set_image(url=si[message.channel.id].proxy_url)
                    except:
                        pass
                    embed.set_footer(
                        text=f"user ID: {sa[message.channel.id].id}",
                        icon_url=None,
                    )
                    await self.bot.get_channel(modlog[str(message.guild.id)]).send(
                        embed=embed
                    )

                else:
                    pass

            except:
                pass
        except:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        try:
            datacheck = self.bot.db("nodata")
            if datacheck.get(str(after.author.id)):
                if datacheck.get(str(after.author.id)).get("data") == False:
                    return
            ch_id = before.channel.id

            if not before.author.bot:
                channel = before.channel
                esbefore[ch_id] = before.content
                esafter[ch_id] = after.content
                esa[ch_id] = before.author
                esav[ch_id] = before.author.avatar
                est[ch_id] = datetime.now()
                if before.content and after.content:
                    if ch_id not in edited_msgs:
                        edited_msgs[ch_id] = []
                    edited_msgs[ch_id].append((before, after))
                    emsgat[ch_id] = datetime.now()
                else:
                    if ch_id not in edited_msgs:
                        edited_msgs[ch_id] = []
                    edited_msgs[ch_id].append((before, after))
                    emsgat[ch_id] = datetime.now()
                try:
                    if len(edited_msgs[ch_id]) > snipe_limit:
                        edited_msgs[ch_id].pop(0)
                except:
                    pass

                modlog = utils.read_json("modlog")

            try:
                if modlog[str(before.guild.id)] != None:
                    try:
                        embed = discord.Embed(
                            description=f"msg by {before.author.mention} edited in <#{before.channel.id}>\nmsg edited <t:{round(est[before.channel.id].timestamp())}:R>",
                            timestamp=datetime.now(),
                        )
                        embed.set_author(
                            name=esa[before.channel.id],
                            icon_url=esav[before.channel.id],
                        )
                        embed.add_field(
                            name="before edit",
                            value=f"**{esa[before.channel.id]}**: {esbefore[before.channel.id]}",
                        )
                        embed.add_field(
                            name="after edit",
                            value=f"**{esa[before.channel.id]}**: {esafter[before.channel.id]}",
                            inline=False,
                        )
                        embed.set_footer(
                            text=f"user ID: {esa[before.channel.id].id}",
                            icon_url=None,
                        )
                        await self.bot.get_channel(modlog[str(before.guild.id)]).send(
                            embed=embed
                        )

                    except Exception as e:
                        print(e)
            except:
                pass

            try:
                if not after.author.bot:
                    if after.author.guild_permissions.administrator != False:
                        db = utils.read_json("chatfilter")
                        words = after.content.lower().replace("\n", " ").split(" ")
                        async for word in utils.aiter(words):
                            if word in db[str(after.guild.id)]:
                                await after.reply(
                                    embed=discord.Embed(
                                        color=utils.color("fail"),
                                        description=f"{utils.emoji('fail')} {after.author.mention} watch your mouth, that word is **filtered** in this guild",
                                    )
                                )
                                try:
                                    await after.delete()
                                except:
                                    pass
            except:
                pass
        except Exception as e:
            pass

        try:
            await self.bot.process_commands(after)
        except:
            pass


    @commands.command(name = "whois", description = "Shows information on a user",aliases=['userinfo','stats', 'ui'], usage = "whois [user]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def whois(self, ctx, member: discord.Member=None):
        try:
            x = ""
            member = ctx.author if not member else member
            embed = discord.Embed(color=0x4c5264)
            embed.set_author(name = member.name, icon_url = member.display_avatar)
            embed.set_thumbnail(url = member.display_avatar)
            embed.add_field(name = "**Created**", value = f"<t:{round(member.created_at.timestamp())}:D>\n<t:{round(member.created_at.timestamp())}:R>")
            embed.add_field(name = "**Joined**", value = f"<t:{round(member.joined_at.timestamp())}:D>\n<t:{round(member.joined_at.timestamp())}:R>")
            if member.premium_since:
                embed.add_field(name = "**Boosted**", value = f"<t:{round(member.premium_since.timestamp())}:D>\n<t:{round(member.premium_since.timestamp())}:R>")
            embed.add_field(name = "**Roles**", value = ", ".join(role.mention for role in member.roles), inline = False)
            embed.set_footer(text=f"{f'{len(member.mutual_guilds)} mutual guild' if len(member.mutual_guilds) == 1 else f'{len(member.mutual_guilds)} mutual guilds'}")
            await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.send(e)


    @commands.command(description="get a random tiktok video", help="utility", aliases=["foryou"], usage = "fyp")
    async def fyp(self, ctx: Context):
      await ctx.typing()
      fyp_videos = await tiktok.feed.for_you(count=1)
      videos = []
      for vid in fyp_videos:
       videos.append(vid)
      
      video = choice(videos)
      no_watermark_download = video["download_urls"]["no_watermark"]
      video_binary = await tiktok.video.get_video_binary(no_watermark_download)
      bytes_io = BytesIO(video_binary) 
      embed = Embed(color=self.bot.color)
      embed.description = f'[{video["description"]}]({video["video_url"]})'
      embed.set_author(name="@"+video["author"]["username"], icon_url=video["author"]["avatar_url"])
      embed.set_footer(text=f"❤️ {human_format(video['stats']['likes'])} 💬 {human_format(video['stats']['comment_count'])} 🔗 {human_format(video['stats']['shares'])} ({human_format(video['stats']['views'])} views)")
      await ctx.reply(embed=embed, file=File(fp=bytes_io, filename="Mirotiktok.mp4"))



    @commands.command(aliases=["cl"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def changelog(self, ctx):
        try:
            embed = (
                discord.Embed(
                    color=0x4c5264,
                    title="last update: 22/06/2023 (June 22th)",
                    description="**+** added stickers\n**+** added emotes\n**+** added scrapbook\n**-** removed useless commands",
                )
                .set_footer(text="miro bot, changelogs")
                .set_thumbnail(url=self.bot.user.display_avatar.url)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)


    @commands.command(
        name="google",
        usage="google (query)",
        aliases=["g", "search", "ggl"],
        description="Search for results on the web",
    )
    async def google(self, ctx, *, query: str):
        """Search for something on Google"""

        async with ctx.typing():
            response = await self.bot.session.get(
                "https://notsobot.com/api/search/google",
                params=dict(
                    query=query.replace(" ", ""),
                    safe="true" if not ctx.channel.is_nsfw() else "false",
                ),
            )
            data = await response.json()

        if not data.get("total_result_count"):
            return await ctx.reply(f"Couldn't find any images for **{query}**")

        embed = discord.Embed(title=f"Google Search: {query}", description="")

        for card in data.get("cards", []):
            embed.description += f"**Rich Card Information:** `{card.get('title')}`\n"
            if card.get("description"):
                embed.description += f"{card.get('description')}\n"
            for field in card.get("fields"):
                embed.description += f"> **{field.get('name')}:** `{field.get('value')}`\n"
            for section in card.get("sections"):
                embed.description += f"> **{section.get('title')}:** `{section['fields'][0].get('name')}`\n"
            if card.get("image"):
                embed.set_image(url=card.get("image"))

        for entry in data.get("results")[:2] if data.get("cards", []) else data.get("results")[:3]:
            embed.add_field(
                name=entry.get("title"),
                value=f"{entry.get('url')}\n{entry.get('description')}",
                inline=False,
            )
        await ctx.send(embed=embed)


    @commands.group(
        name="btcaddy",
        usage="btcinfo (address)",
        description="Show info about btc",
        aliases=["bitcoinaddy", "btcinfo", "btctransactions"],
        invoke_without_command=True,
    )
    async def btcaddy(self, ctx, address: str):
        """View information about a bitcoin address"""

        response = await self.bot.session.get(
            "https://blockchain.info/rawaddr/" + str(address),
        )
        data = await response.json()

        if data.get("error"):
            return await ctx.warn(f"Couldn't find an **address** for `{address}`")

        response = await self.bot.session.get(
            "https://min-api.cryptocompare.com/data/price",
            params=dict(fsym="BTC", tsyms="USD"),
        )
        price = await response.json()
        price = price["USD"]

        embed = discord.Embed(
            url=f"https://mempool.space/address/{address}",
            title="Bitcoin Address",
        )

        embed.add_field(
            name="Balance",
            value=f"{(data['final_balance'] / 100000000 * price):,.2f} USD",
        )
        embed.add_field(
            name="Received",
            value=f"{(data['total_received'] / 100000000 * price):,.2f} USD",
        )
        embed.add_field(name="Sent", value=f"{(data['total_sent'] / 100000000 * price):,.2f} USD")
        if data["txs"]:
            embed.add_field(
                name="Transactions",
                value="\n".join(
                    f"> [`{tx['hash'][:19]}..`](https://mempool.space/tx/{tx['hash']}) {(tx['result'] / 100000000 * price):,.2f} USD"
                    for tx in data["txs"][:5]
                ),
            )

        await ctx.send(embed=embed)


    @commands.hybrid_command(name = "snipe", description = "Return deleted messages",aliases=['s'], usage = "snipe")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def snipe(self, ctx: commands.Context, limit: int = 1):
        if limit > snipe_limit:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** current **snipe limit** is {snipe_limit}",
                )
            )
        try:
            msgs: list[discord.Message] = deleted_msgs[ctx.channel.id][::-1]  # [:limit]
            embeds = []
            num = 0
            async for msg in utils.aiter(msgs):
                num += 1
                cf = 0
                try:
                    chatfilter = utils.read_json("chatfilter")[str(ctx.guild.id)]
                    words = msg.content.split(" ")
                    async for word in utils.aiter(words):
                        if word in chatfilter:
                            cf += 1
                except:
                    pass
                # if cf != 0: return await ctx.reply(embed=discord.Embed(color=self.error, description=f"{self.fail} {ctx.author.mention}**:** you can't snipe filtered messages"))
                snipe_embed = (
                    discord.Embed(color=ctx.author.color)
                    .set_author(name=msg.author, icon_url=msg.author.display_avatar)
                    .set_footer(
                        text=f"deleted {utils.moment(msg.created_at)} ago | {num}/{len(deleted_msgs[ctx.channel.id])}",
                        icon_url=None,
                    )
                )
                if cf != 0:
                    snipe_embed.description = "CENSORED MESSAGE"
                else:
                    if msg.content:
                        snipe_embed.description = msg.content
                    if msg.attachments:
                        snipe_embed.set_image(url=msg.attachments[0].proxy_url)
                embeds.append(snipe_embed)

            from modules import paginator as pg

            paginator = pg.Paginator(self.bot, embeds, ctx, timeout=30, invoker=None)
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()

        except KeyError:
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** no recently **deleted** msgs",
                )
            )

    @commands.hybrid_command(name = "editsnipe", description = "Return edited messages",aliases=['es'], usage = "editsnipe")
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def editsnipe(self, ctx: commands.Context, limit: int = 1):
        if limit > snipe_limit:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** current **snipe limit** is {snipe_limit}",
                )
            )
        try:
            msgs = edited_msgs[ctx.channel.id][::-1]  # [:limit]
            embeds = []
            num = 0
            async for msg in utils.aiter(msgs):
                num += 1
                cf = 0
                try:
                    chatfilter = utils.read_json("chatfilter")[str(ctx.guild.id)]
                    words = msg.content.split(" ")
                    async for word in utils.aiter(words):
                        if word in chatfilter:
                            cf += 1
                except:
                    pass
                editsnipe_embed = (
                    discord.Embed(color=ctx.author.color)
                    .set_author(
                        name=msg[0].author, icon_url=msg[0].author.display_avatar
                    )
                    .set_footer(
                        text=f"edited {utils.moment(emsgat[ctx.channel.id])} {'ago' if 'ago' not in utils.moment(emsgat[ctx.channel.id]) else ''} | {num}/{len(edited_msgs[ctx.channel.id])}",
                        icon_url=None,
                    )
                )
                if cf != 0:
                    editsnipe_embed.description = "CENSORED MESSAGE"
                else:
                    if msg[0].content:
                        editsnipe_embed.description = msg[0].content
                    if msg[0].attachments:
                        editsnipe_embed.set_image(url=msg[0].attachments[0].proxy_url)
                embeds.append(editsnipe_embed)

            from modules import paginator as pg
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()

            # await ctx.reply(embed=editsnipe_embed)

        except KeyError:
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** no recently **edited** msgs",
                )
            )




    @commands.command(name="clearsnipe", description="Clear snipe history", aliases=["cs"])
    @commands.has_permissions(manage_messages=True)
    async def clearsnipe(self, ctx):
        channel_id = ctx.channel.id

        if channel_id in deleted_msgs:
            deleted_msgs[channel_id] = []
        
        if channel_id in edited_msgs:
            edited_msgs[channel_id] = []

        embed = discord.Embed(
            title="Snipe History Cleared",
            description="The snipe history has been cleared.",
            color=0x4c5264
        )

        await ctx.send(embed=embed)


    @commands.command(
        name="wolfram",
        usage="wolfram (query)",
        example="integral of x^2",
        aliases=["wolframalpha", "wa", "w"],
    )
    async def wolfram(self, ctx, *, query: str):
        """Search a query on Wolfram Alpha"""

        async with ctx.typing():
            response = await self.bot.session.get(
                "https://notsobot.com/api/search/wolfram-alpha",
                params=dict(query=query),
            )
            data = await response.json()

        if not data.get("fields"):
            return await ctx.warn("Couldn't **understand** your input")

        embed = discord.Embed(
            url=data.get("url"),
            title=query,
        )

        for index, field in enumerate(data.get("fields")[:4]):
            if index == 2:
                continue

            embed.add_field(
                name=field.get("name"),
                value=(">>> " if index == 3 else "") + field.get("value").replace("( ", "(").replace(" )", ")").replace("(", "(`").replace(")", "`)"),
                inline=(False if index == 3 else True),
            )
        embed.set_footer(
            text="Wolfram Alpha",
            icon_url="https://cdn.discordapp.com/attachments/1107734070659653652/1121513483385708554/Cherry_Blossoms.png",
        )
        await ctx.send(embed=embed)


    @commands.command(
        help="Check bot's statistics",
        aliases=["about", "bi", "miro"],
        description="Displays information about the bot.",
        usage="botinfo",
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def botinfo(self, ctx: commands.Context):
        owner_names = []
        for owner_id in self.bot.owner_ids:
            user = await self.bot.fetch_user(owner_id)
            owner_names.append(f"{user.name}#{user.discriminator}")

        guild_count = len(self.bot.guilds)
        member_count = sum(g.member_count for g in self.bot.guilds)
        command_count = len(set(self.bot.walk_commands()))

        embed = discord.Embed(
            color=0x4c5264, title="About Miro", description="Information about the bot."
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="Developer Info",
            value=f"<:mirowner:1107719611484487755> Dev: {', '.join(owner_names)}\n<:icons_invite:1118181609640837130> Support: [Server](https://discord.gg/mirobot)\n<:links:1107308143924494436> Invite: [Miro](https://discord.com/api/oauth2/authorize?client_id=1107283467655458866&permissions=8&scope=bot)",
        )
        embed.add_field(
            name="Main Statistics",
            value=f"<:miroconf:1107719174643515454> Users: {member_count}\n<:mail:1107718445845467168> Servers: {guild_count}\n<:miroutil:1107719274929340536> Commands: 275",
        )
        embed.add_field(
            name="System Information",
            value=f"<:miroclock:1115307569284644916> Latency: {round(self.bot.latency * 1000)}ms\n<:miroprem:1115307610447560805> Language: Python\n<:mirofun:1107719404642390046> System: {platform.system()}",
        )
        await ctx.reply(embed=embed, mention_author=False)


    @commands.command(
        name="image",
        usage="image (query)",
        example="image Clairo",
        aliases=["img", "im", "i"],
        description="Search the web for images",
    )
    async def image(self, ctx, *, query: str):

        response = await self.bot.session.get(
            "https://notsobot.com/api/search/google/images",
            params=dict(
                query=query.replace(" ", ""),
                safe="true" if not ctx.channel.is_nsfw() else "false",
            ),
        )
        data = await response.json()

        if not data:
            return await ctx.warn(f"Couldn't find any images for **{query}**")

        embeds = [
            discord.Embed(
                url=entry.get("url"),
                title=entry.get("header"),
                description=entry.get("description"),
            ).set_image(url=entry["image"]["url"])
            for entry in data
            if not entry.get("header") in ("TikTok", "Facebook")
        ]

        from modules import paginator as pg
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
        paginator.add_button("prev", emoji="<:left:1107307769582850079>")
        paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
        paginator.add_button("next", emoji="<:right:1107307767041105920>")
        paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
        await paginator.start()



    @commands.command(description="See donation info", help="donor", aliases=["payment"], usage = "donate")
    async def donate(self, ctx: commands.Context): 
        embed = discord.Embed(color=self.bot.color, title="donation methods", description=f"<:paypal:1125060101133320192> - [`xotic0001`](https://paypal.me/xotic0001)\n<:booststar:1125060039653216296> - [`/mirobot`](https://discord.gg/mirobot)\n<:cashapp:1110036898912677971> - [`$xotic0001`](https://cash.app/$xotic0001)\n<:btc:1110037192669138994> - `bc1qy2dx64xq6mxyvup098z3hk82teqy6cy6q7zqs9`\n<:eth:1110036897490796606> - `0x1bbed1a48dEf83EC7D78a4662831E017d47E7c8b`\n <:ltc:1125061132231655536> - `Lg1aL3haSfEBSUf5dSd6eiT8Qb4FuTdYVP`\nBoosting will get you premium perks, for help dm inflating")
        paypal = discord.ui.Button(emoji="<:paypal:1125060101133320192>")
        boost = discord.ui.Button(emoji="<:booststar:1125060039653216296>")
        cashapp = discord.ui.Button(emoji="<:cashapp:1110036898912677971>")
        btc = discord.ui.Button(emoji="<:btc:1110037192669138994>")
        eth = discord.ui.Button(emoji="<:eth:1110036897490796606>")
        ltc = discord.ui.Button(emoji="<:ltc:1125061132231655536>")
        view = discord.ui.View(timeout=None)
    
        async def paypal_callback(interaction: discord.Interaction): 
            await interaction.response.send_message("https://paypal.me/xotic0001", ephemeral=True)

        async def boost_callback(interaction: discord.Interaction): 
            await interaction.response.send_message("boost https://discord.gg/mirobot for perks", ephemeral=True)

        async def cashapp_callback(interaction: discord.Interaction): 
            await interaction.response.send_message("https://cash.app/$xotic0001", ephemeral=True)

        async def btc_callback(interaction: discord.Interaction): 
            await interaction.response.send_message("`bc1qy2dx64xq6mxyvup098z3hk82teqy6cy6q7zqs9`", ephemeral=True)  

        async def eth_callback(interaction: discord.Interaction): 
            await interaction.response.send_message("`0x1bbed1a48dEf83EC7D78a4662831E017d47E7c8b`", ephemeral=True)   

        async def ltc_callback(interaction: discord.Interaction): 
            await interaction.response.send_message("`Lg1aL3haSfEBSUf5dSd6eiT8Qb4FuTdYVP`", ephemeral=True)   
    
        paypal.callback = paypal_callback
        boost.callback = boost_callback
        cashapp.callback = cashapp_callback
        btc.callback = btc_callback
        eth.callback = eth_callback 
        ltc.callback = ltc_callback 
    
        view.add_item(paypal)
        view.add_item(boost)
        view.add_item(cashapp)
        view.add_item(btc)
        view.add_item(eth)
        await ctx.reply(embed=embed, view=view, mention_author=False)



async def setup(bot):
    await bot.add_cog(info(bot))
