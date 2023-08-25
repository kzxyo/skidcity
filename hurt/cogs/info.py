import asyncio
from io import BytesIO
from tkinter import BOTH, BOTTOM
from typing import TypeVar
from click import Context
import discord
import platform
import time
import datetime
import aiohttp
from discord import BotIntegration, Embed
from discord.ext import commands
from .utils.util import Emojis
from cogs.utilevents import blacklist, commandhelp, sendmsg
import button_paginator as pg
from discord.ui import Button, View
from .utils.util import Colors, Emojis
import re
from io import BytesIO
import requests

DISCORD_API_LINK = "https://discord.com/api/invite/"

my_system = platform.uname()
start_time = time.time()


class info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def ping(self, ctx):
        e = discord.Embed(
            color=Colors.green,
            description=f"Took **{round(self.bot.latency * 1000)}ms** To Call A Hot Asian",
        )
        await ctx.reply(embed=e, mention_author=True)

    @commands.command(help="check the bot's uptime", description="info", aliases=["up"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def uptime(self, ctx: commands.Context):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        e = discord.Embed(
            title="",
            description=f" {self.bot.user.name}'s current uptime is **{text}**",
            color=0xF7F9F8,
        )
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(
        help="credits to users that supported crime",
        aliases=["cred", "creds"],
        description="info",
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def credits(self, ctx):
        embed = (
            discord.Embed(color=0xF7F9F8, description="")
            .add_field(
                name="**cys , bleed , monarch**",
                value="main developer's of hurt",
                inline=True,
            )
            .add_field(name="", value="", inline=True)
            .add_field(name="", value="", inline=True)
            .add_field(name="", value="", inline=True)
        )
        await ctx.reply(embed=embed, mention_author=True)

    @commands.command(
        help="check bot's statistics",
        aliases=["about", "bi", "hurt"],
        description="info",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def botinfo(self, ctx: commands.Context):
        lis = []
        for i in self.bot.owner_ids:
            user = await self.bot.fetch_user(i)
            lis.append(user.name + "#" + user.discriminator)
        embed = discord.Embed(color=0xF7F9F8, title="about hurt").set_thumbnail(
            url=self.bot.user.display_avatar
        )
        embed.add_field(
            name="dev info",
            value=f"devs - **[sorrow](https://discord.com/users/1032866404736708678)** **&** **[willow](https://discord.com/users/961409108286795917)**\nsupport: **[/hurt](https://discord.gg/wkMg56ZtMk)**\n invite: **[hurt](https://discord.com/api/oauth2/authorize?client_id=1116511589013655552&permissions=8&scope=bot)**",
        )
        embed.add_field(
            name="main",
            value=f"users: {sum(g.member_count for g in self.bot.guilds)}\nservers: {len(self.bot.guilds)}\n cmds: {len(set(self.bot.walk_commands())) + 45}",
        )
        embed.add_field(
            name="system:",
            value=f"latency: {round(self.bot.latency * 1000)}ms\nlanguage: discord.py\nsystem: {my_system.system}",
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(
        help="invite the bot in your server", aliases=["inv"], description="info"
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def invite(self, ctx):
        embed = discord.Embed(
            color=0xF7F9F8, description="invite **hurt** in your server"
        )
        button = discord.ui.Button(
            label="invite",
            style=discord.ButtonStyle.url,
            url=discord.utils.oauth_url(
                client_id=self.bot.user.id, permissions=discord.Permissions.all()
            ),
        )
        view = discord.ui.View()
        view.add_item(button)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @commands.command(
        help="check bot's guild count",
        aliases=["gc", "guilds", "guildc"],
        description="info",
    )
    async def guildcount(self, ctx: commands.Context):
        lis = []
        for i in self.bot.owner_ids:
            user = await self.bot.fetch_user(i)
            lis.append(user.name + "#" + user.discriminator)
        embed = discord.Embed(
            color=0xF7F9F8, description=f"*guild count:* **{len(self.bot.guilds)}**"
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["h"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx):
        try:
            embed = (
                discord.Embed(color=0xF7F9F8)
                .set_footer(text="powered by hurt (1/14)")
                .set_thumbnail(url=self.bot.user.display_avatar.url)
            )
            embed.add_field(
                name=f"Update Log",
                value=f"**8/8/23**\nAdded update log, help menu updated, (+ plenty of more commands)",
                inline=False,
            )
            embed.add_field(
                name="**Do you need help with hurt?**",
                value=f"Contact **[cys](https://discord.com/users/1032866404736708678)** or **[monarch](https://discord.com/users/1133822924906844202)**\nUse the buttons to go through our help embed",
                inline=False,
            )
            embed.add_field(
                name="**Useful links**",
                value=f"**[Support](https://hurt.bot)** — **[Invite](https://discord.com/api/oauth2/authorize?client_id=1116511589013655552&permissions=8&scope=bot)** — **[Docs](https://cry.docs)**",
                inline=False,
            )
            info = discord.Embed(
                color=0xF7F9F8, description="**Information:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            info.add_field(
                name="commands",
                value="```fix\nhelp, guildcount, botinfo, rtfm, roleinfo, invite, latency, weather, image, userinfo, poll, twitter, minecraft, appstore, instagram, boostcount, guildvanity, urban, xbox```",
                inline=False,
            )
            info.set_footer(text=f"powered by hurt (2/13)")

            config = discord.Embed(
                color=0xF7F9F8, description="**Configuration:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            config.add_field(
                name="commands",
                value="```fix\njoindm*, altdentifier*, voicemaster*, setme, autoresponder*, vanity*, ticket*, logs*, reactionrole```",
                inline=False,
            )
            config.set_footer(text=f"powered by hurt (3/13)")

            lastfm = discord.Embed(
                color=0xF7F9F8, description="**LastFM:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            lastfm.add_field(
                name="commands",
                value="```fix\nset, unset, topartists, toptracks, topalbums, whoknows, globalwhoknows, nowplaying```",
                inline=False,
            )
            lastfm.set_footer(text=f"powered by hurt (4/13)")

            utility = discord.Embed(
                color=0xF7F9F8, description="**Utility:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            utility.add_field(
                name="commands",
                value="```fix\nrolegive*, roletake*, rolecreate*, roledelete*, rolerename*, rolecolor*, nuke, avatar, banner, tags, setbanner, setavatar, emojiadd, addmultiple, emojilist, snipe, createchannel, deletechannel, createvoice, deletevoice, pin, unpin, tiktok, categorycreate, categorydelete, vmute, vumute, vdeafen, vudeafen, vdisconnect, drag, say, massmove, reverse, reverseav```",
                inline=False,
            )
            utility.set_footer(text=f"powered by hurt (5/13)")

            moderation = discord.Embed(
                color=0xF7F9F8, description="**Moderation:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            moderation.add_field(
                name="commands",
                value="```fix\njail, unjail, roleall*, restore, lock, warn*, unban, ban, slowmode*, nickname, kick, role, unlock, stripstaff, unmute, mute, botpurge, purge*, stfu, unstfu```",
                inline=False,
            )
            moderation.set_footer(text=f"powered by hurt (6/13)")

            greeting = discord.Embed(
                color=0xF7F9F8, description="**Greeting:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            greeting.add_field(
                name="welcome commands",
                value="```fix\nwelcome message, welcome channel, welcome test, welcome config, welcome delete```",
                inline=False,
            )
            greeting.add_field(
                name="boost commands",
                value="```fix\nboost message, boost channel, boost test, boost config, boost delete```",
                inline=False,
            )
            greeting.add_field(
                name="goodbye commands",
                value="```fix\ngoodbye message, goodbye channel, goodbye test, goodbye config, goodbye delete```",
                inline=False,
            )
            greeting.add_field(
                name="joindm commands",
                value="```fix\njoindm message, joindm test, joindm config, joindm delete```",
                inline=False,
            )
            greeting.set_footer(text=f"powered by hurt (7/13)")

            security = discord.Embed(
                color=0xF7F9F8, description="**Security:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            security.add_field(
                name="commands",
                value="```fix\nantinuke settings, antinuke vanity, antinuke ban, antinuke kick, antinuke channelcreate, antinuke channeldelete, antinuke rolecreate, antinuke roledelete, antinuke webhook, antinuke botadd, antinuke alt, antinuke guildupdate```",
                inline=False,
            )
            security.add_field(
                name="punishments",
                value="```fix\nban, kick, strip, jail```",
                inline=False,
            )
            security.set_footer(text=f"powered by hurt (8/13)")

            autopost = discord.Embed(
                color=0xF7F9F8, description="**Autopost:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            autopost.add_field(
                name="commands",
                value="```fix\nautopfp add, autogif add, autopfp remove, autogif remove```",
                inline=False,
            )
            autopost.add_field(
                name="genres",
                value="```fix\nmale, female, anime, random, agifs, mgifs, fgifs```",
                inline=False,
            )
            autopost.set_footer(text=f"powered by hurt (9/13)")

            music = discord.Embed(
                color=0xF7F9F8, description="**Music:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            music.add_field(
                name="commands",
                value="```fix\nautoplay, clearqueue, filters, grab, join, leave, loop, lyrics, nowplaying, pause, play, track, remove, resume, search, seek, shuffle, skip, skipto, stop, volume, 247, adddj, removedj, toogledj, create, delete, plinfo, list, load, removetrack, savecurrent, savequeue```",
                inline=False,
            )
            music.set_footer(text=f"powered by hurt (10/13)")

            roleplay = discord.Embed(
                color=0xF7F9F8, description="**Roleplay:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            roleplay.add_field(
                name="commands",
                value="```fix\ncuddle, slap, pat, hug, kiss, feed, tickle, cry, funny, poke, baka```",
                inline=False,
            )
            roleplay.set_footer(text=f"powered by hurt (11/13)")

            fun = discord.Embed(color=0xF7F9F8, description="**Fun:**").set_thumbnail(
                url=self.bot.user.display_avatar.url
            )
            fun.add_field(
                name="commands",
                value="```fix\nblacktea, fyp, meme, remind, spotify, translate, bible, ask, screenshot, pack, cum, ben, roast, drake, fry, bihw, cheems, mb, mordor,marry,simp,lyric,dog,cat,roblox,wordcloud,hack,github```",
                inline=False,
            )
            fun.set_footer(text=f"powered by hurt (12/13)")

            games = discord.Embed(
                color=0xF7F9F8, description="**Games:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            games.add_field(
                name="commands",
                value="```fix\nconnect4, fasttype, flood, guessthepokemon, hangman, rockpaperscissors, slots, snake, teams, trivia, wordle, wouldyourather```",
                inline=False,
            )
            games.set_footer(text=f"powered by hurt (13/13)")

            donor = discord.Embed(
                color=0xF7F9F8, description="**donor:**"
            ).set_thumbnail(url=self.bot.user.display_avatar.url)
            donor.add_field(
                name="commands",
                value="```fix\nselfpurge, bj, nut, genratepassword hexgen,  hentai, hd, boobs, lewd,```",
                inline=False,
            )
            donor.set_footer(text=f"powered by hurt (14/14)")

            embeds = (
                embed,
                info,
                config,
                lastfm,
                utility,
                moderation,
                greeting,
                security,
                autopost,
                music,
                roleplay,
                fun,
                games,
                donor,
            )
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:icons_leftarrow:1135806089473032262>")
            paginator.add_button("delete", emoji="<:icons_Wrong:1135642272092926054>")
            paginator.add_button(
                "next", emoji="<:icons_rightarrow:1135806059366322186>"
            )
            paginator.add_button("goto", emoji="<:skip:1136737495887925268>")
            await paginator.start()
        except Exception as e:
            print(e)

    @commands.command(
        help="gets the splash from a server based on invite code",
        description="utility",
        usage="[invite code]",
    )
    @blacklist()
    async def splash(self, ctx, *, link=None):
        if link is None:
            if ctx.guild is not None and ctx.guild.splash is not None:
                embed = Embed(color=Colors.default, title=f"{ctx.guild.name}'s splash")
                embed.set_image(url=ctx.guild.splash)
            else:
                embed = Embed(
                    color=Colors.default,
                    description="This server doesn't have a splash image.",
                )
            await sendmsg(self, ctx, None, embed, None, None, None)
        else:
            invite_code_match = re.search(
                r"(discord\.gg/|discordapp\.com/invite/)([A-Za-z0-9-]+)", link
            )
            if invite_code_match:
                invite_code = invite_code_match.group(2)
            else:
                embed = Embed(
                    color=Colors.default,
                    description="Invalid invite link. Please provide a valid Discord invite link.",
                )
                await sendmsg(self, ctx, None, embed, None, None, None)
                return

            async with aiohttp.ClientSession() as cs:
                async with cs.get(DISCORD_API_LINK + invite_code) as r:
                    if r.status != 200:
                        embed = Embed(
                            color=Colors.default,
                            description="Invalid invite code or unable to fetch data.",
                        )
                        await sendmsg(self, ctx, None, embed, None, None, None)
                        return
                    data = await r.json()

            if "guild" in data and "id" in data["guild"] and "splash" in data["guild"]:
                server_id = str(data["guild"]["id"])
                splash_hash = str(data["guild"]["splash"])
                embed = Embed(
                    color=Colors.default, title=f"{data['guild']['name']}'s splash"
                )
                splash_url = f"https://cdn.discordapp.com/splashes/{server_id}/{splash_hash}.png?size=1024"
                embed.set_image(url=splash_url)
            else:
                embed = Embed(
                    color=Colors.default,
                    description="This server doesn't have a splash image.",
                )

            await sendmsg(self, ctx, None, embed, None, None, None)

    @commands.command(
        aliases=["mc"],
        help="check how many members does your server have",
        description="utility",
    )
    @blacklist()
    async def membercount(self, ctx):
        await ctx.reply(
            embed=Embed(
                color=0xF7F9F8,
                description="**{}** members".format(ctx.guild.member_count),
            ),
            mention_author=False,
        )

    @commands.command(help="see all server boosters", description="utility")
    @blacklist()
    async def boosters(self, ctx):
        if not ctx.guild.premium_subscriber_role:
            e = Embed(
                color=Colors.red,
                description=f"{Emojis.deny} booster role doesn't exist",
            )
            await sendmsg(self, ctx, None, e, None, None, None)
            return
        if len(ctx.guild.premium_subscriber_role.members) == 0:
            e = Embed(
                color=Colors.red,
                description=f"{Emojis.deny} this server doesn't have any boosters",
            )
            await sendmsg(self, ctx, None, e, None, None, None)
            return

        i = 0
        k = 1
        l = 0
        mes = ""
        number = []
        messages = []
        for member in ctx.guild.premium_subscriber_role.members:
            mes = f"{mes}`{k}` {member} - <t:{int(member.premium_since.timestamp())}:R> \n"
            k += 1
            l += 1
            if l == 10:
                messages.append(mes)
                number.append(
                    Embed(
                        color=Colors.default,
                        title=f"{ctx.guild.name} boosters [{len(ctx.guild.premium_subscriber_role.members)}]",
                        description=messages[i],
                    )
                )
                i += 1
                mes = ""
                l = 0

        messages.append(mes)
        embed = Embed(
            color=Colors.default,
            title=f"{ctx.guild.name} boosters [{len(ctx.guild.premium_subscriber_role.members)}]",
            description=messages[i],
        )
        number.append(embed)
        if len(number) > 1:
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:icons_leftarrow:1135806089473032262>")
            paginator.add_button("delete", emoji="<:icons_delete:1051864845416419418>")
            paginator.add_button(
                "next", emoji="<:icons_rightarrow:1135806059366322186>"
            )
            await paginator.start()
        else:
            await sendmsg(self, ctx, None, embed, None, None, None)

    @commands.command(help="see all server roles", description="utility")
    @blacklist()
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
                        color=Colors.default,
                        title=f"{ctx.guild.name} roles [{len(ctx.guild.roles)}]",
                        description=messages[i],
                    )
                )
                i += 1
                mes = ""
                l = 0

        messages.append(mes)
        embed = Embed(
            color=Colors.default,
            title=f"{ctx.guild.name} roles [{len(ctx.guild.roles)}]",
            description=messages[i],
        )
        number.append(embed)
        if len(number) > 1:
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:icons_leftarrow:1135806089473032262>")
            paginator.add_button("delete", emoji="<:icons_delete:1051864845416419418>")
            paginator.add_button(
                "next", emoji="<:icons_rightarrow:1135806059366322186>"
            )
            await paginator.start()
        else:
            await sendmsg(self, ctx, None, embed, None, None, None)

    @commands.command(help="see all server's bots", description="utility")
    @blacklist()
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
                            color=Colors.default,
                            title=f"{ctx.guild.name} bots [{b}]",
                            description=messages[i],
                        )
                    )
                    i += 1
                    mes = ""
                    l = 0

        messages.append(mes)
        embed = Embed(
            color=Colors.default,
            title=f"{ctx.guild.name} bots [{b}]",
            description=messages[i],
        )
        number.append(embed)
        if len(number) > 1:
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:icons_leftarrow:1135806089473032262>")
            paginator.add_button("delete", emoji="<:icons_delete:1051864845416419418>")
            paginator.add_button(
                "next", emoji="<:icons_rightarrow:1135806059366322186>"
            )
            await paginator.start()
        else:
            await sendmsg(self, ctx, None, embed, None, None, None)

    @commands.command(
        help="show server information",
        aliases=["guild", "si"],
        description="utility",
        usage="[subcommand] <server id>",
        brief="server info - shows server info\nserver avatar - shows server's avatar\nserver banner - shows server's banner\nserver splash - shows server's invite background",
    )
    @blacklist()
    async def serverinfo(self, ctx, arg=None, *, id: int = None):
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

            embed = Embed(color=0xFFFFFF)
            try:
                embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
            except:
                embed.set_author(name=ctx.guild.name)

            if ctx.guild.icon is not None:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            embed.add_field(
                name="",
                value=f"*information 4 **{ctx.guild.name}**, created by {ctx.guild.owner.mention}*",
                inline=False,
            )
            embed.add_field(
                name="",
                value=f"**created:** <t:{int(ctx.guild.created_at.timestamp())}:f> (<t:{int(ctx.guild.created_at.timestamp())}:R>)",
                inline=False,
            )
            embed.add_field(
                name="main",
                value=f"members: `{ctx.guild.member_count}`\nemojis: `{len(ctx.guild.emojis)}`\n roles: `{len(ctx.guild.roles)}`",
            )
            embed.add_field(
                name="other",
                value=f"channels: `{len(ctx.guild.channels)}`\ndescription: `{ctx.guild.description}`\nverification: `{ctx.guild.verification_level}`",
            )
            embed.add_field(
                name="more",
                value=f"categories: `{len(ctx.guild.categories)}`\nboosts: `{ctx.guild.premium_subscription_count}`\nvanity: `{ctx.guild.vanity_url_code}`",
            )
            embed.set_footer(text=f"ID: {ctx.guild.id} • requested by {ctx.author}")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command
    async def count(ctx):
        member_count = len(ctx.guild.members)
        embed = discord.Embed(title="Member Count", color=discord.Color.yellow())
        embed.add_field(name="Total Members", value=str(member_count))
        await ctx.send(embed=embed)


async def make_request(url, params=None, action=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if action == "read":
                return await response.read()
            return await response.json()


async def do_again(url):
    for _ in range(5):  # Maximum 5 retries
        await asyncio.sleep(5)  # Wait for 5 seconds before checking again
        re = await make_request(url)
        if re["status"] == "converting":
            continue
        elif re["status"] == "failed":
            return None
        else:
            return tuple([re["url"], re["filename"]])
    return None


@commands.command(
    aliases=["yttomp3"],
    help="utility",
    description="download yt video to mp3",
    usage="[video link]",
)
async def youtubetomp3(ctx: commands.Context, url: str):
    async with ctx.typing():
        rq = await make_request(
            "https://srv4.onlymp3.to/listFormats", params={"url": url}
        )
        link = rq["formats"]["audio"][2]["url"]
        r = await make_request(link)
        newurl = r["url"]
        re = await make_request(newurl)
        if re["status"] == "converting":
            rele = await do_again(newurl)
        elif re["status"] == "failed":
            return await ctx.send_warning("Failed to download the video as an mp3")
        else:
            rele = tuple([re["url"], re["filename"]])

        if rele is None:
            return await ctx.send_warning("Failed to download the video as an mp3")

        req = await make_request(rele[0], action="read")
        file = discord.File(BytesIO(req), filename=rele[1].replace("onlymp3.to - ", ""))
        return await ctx.reply(file=file)


async def setup(bot):
    await bot.add_cog(info(bot))
