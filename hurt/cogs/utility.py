import requests
import instaloader
from discord.ext.commands import Context
import emojis
import spotify
import humanfriendly
from datetime import datetime
import datetime
from discord.ext import commands
from discord import Embed, Member, Color
from email import utils
from asyncpg import WrongObjectTypeError
from click import Command, CommandCollection
import discord
import aiohttp
import button_paginator as pg
import json
import random
import asyncio
import datetime
import os
import io
from discord import Embed, Member, Spotify, User, AllowedMentions, Message
from discord.ext import tasks
from discord.ext.commands import (
    Cog,
    command,
    Context,
    cooldown,
    BucketType,
    AutoShardedBot as Bot,
)
from pyparsing import Optional
from .utils.util import Emojis, Colors
from typing import Union
from discord.ui import View, Button, Select
from cogs.utilevents import blacklist, sendmsg, noperms, commandhelp
from cogs.utils import http
from .utils.embedparser import to_object
from io import BytesIO
from .modules.tiktokapi import for_you

DISCORD_API_LINK = "https://discord.com/api/invite/"


class BlackTea:
    """BlackTea backend variables"""

    MatchStart = {}
    lifes = {}

    async def get_string():
        lis = await BlackTea.get_words()
        word = random.choice(lis)
        return word[:3]

    async def get_words():
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://www.mit.edu/~ecprice/wordlist.10000") as r:
                byte = await r.read()
                data = str(byte, "utf-8")
                return data.splitlines()


class utility(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.guild:
            return
        if message.author.bot:
            return
        if message.mentions:
            async with self.bot.db.cursor() as cursor:
                for mem in message.mentions:
                    await cursor.execute(
                        "SELECT * from afk where guild_id = {} AND user_id = {}".format(
                            message.guild.id, mem.id
                        )
                    )
                    check = await cursor.fetchone()
                    if check is not None:
                        em = Embed(
                            color=0xF7F9F8,
                            description=f"{mem.mention} is AFK since <t:{int(check[3])}:R> - **{check[2]}**",
                        )
                        await sendmsg(self, message, None, em, None, None, None)

        async with self.bot.db.cursor() as curs:
            await curs.execute(
                "SELECT * from afk where guild_id = {} AND user_id = {}".format(
                    message.guild.id, message.author.id
                )
            )
            check = await curs.fetchone()
            if check is not None:
                embed = Embed(
                    color=0xF7F9F8,
                    description=f"👋 Welcome back {message.author.mention}! You were AFK since <t:{int(check[3])}:R>",
                )
                await sendmsg(self, message, None, embed, None, None, None)
                await curs.execute(
                    "DELETE FROM afk WHERE guild_id = {} AND user_id = {}".format(
                        message.guild.id, message.author.id
                    )
                )
        await self.bot.db.commit()

    @command(help="create an embed", description="fun", aliases=["ce"])
    @blacklist()
    async def createembed(self, ctx, *, code: str = None):
        if not ctx.author.guild_permissions.manage_guild:
            await noperms(self, ctx, "manage_guild")
            return
        if not code:
            e = discord.Embed(
                description=f"> {Emojis.warn} please provide embed code [here](https://crimebot.site/embed)",
                color=0xF7F9F8,
            )
            return await ctx.reply(embed=e)
            return
        e = await to_object(code)
        await ctx.send(**e)

    @command(help="returns a random bible verse", description="fun", aliases=["verse"])
    @blacklist()
    @cooldown(1, 4, BucketType.guild)
    async def bible(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "https://labs.bible.org/api/?passage=random&type=json"
            ) as r:
                byte = await r.read()
                data = str(byte, "utf-8")
                data = data.replace("[", "").replace("]", "")
                bible = json.loads(data)
                embed = discord.Embed(
                    color=0x2F3136, description=bible["text"]
                ).set_author(
                    name="{} {}:{}".format(
                        bible["bookname"], bible["chapter"], bible["verse"]
                    ),
                    icon_url="https://imgs.search.brave.com/gQ1kfK0nmHlQe2XrFIoLH9vtFloO3HRTDaCwY5oc0Ow/rs:fit:1200:960:1/g:ce/aHR0cDovL3d3dy5w/dWJsaWNkb21haW5w/aWN0dXJlcy5uZXQv/cGljdHVyZXMvMTAw/MDAvdmVsa2EvNzU3/LTEyMzI5MDY0MTlC/MkdwLmpwZw",
                )
                await ctx.reply(embed=embed, mention_author=False)

    @command(
        name="seticon",
        aliases=["changeserverav", "changeicon", "setavatar"],
        description="change guild avatar",
        extras={"perms": "administrator"},
        brief="url/image",
        usage="```Syntax: !setsplash <url/image>\nExample: !setsplash https://rival.rocks/image.png```",
    )
    @blacklist()
    async def seticon(self, ctx, url: str = None):
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None
        if not ctx.author.guild_permissions.manage_guild:
            await noperms(self, ctx, "manage_guild")
            return
        try:
            bio = await http.get(url, res_method="read")
            guild = ctx.guild
            await guild.edit(icon=bio)
            embed = discord.Embed(
                description=f"*guild icon is now set to:*", color=0x2F3136
            )
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        except aiohttp.InvalidURL:
            embed = discord.Embed(
                description=f"*Please enter a real url or upload an image*",
                color=0x2F3136,
            )
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            embed = discord.Embed(
                description=f"*Please enter a real url or upload an image*",
                color=0x2F3136,
            )
            await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(
                description=f"*Your current url is not a supported image.*",
                color=0x2F3136,
            )
            await ctx.reply(embed=embed, mention_author=False)

    @command(
        name="setbanner",
        aliases=["changebnr"],
        description="change guild banner",
        extras={"perms": "administrator"},
        usage="```Syntax: !setbanner <url/image>\nExample: !setbanner https://crimebot.site/image.png```",
    )
    @blacklist()
    async def setbanner(self, ctx, url: str = None):
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None
        if not ctx.author.guild_permissions.manage_guild:
            await noperms(self, ctx, "manage_guild")
            return
        try:
            bio = await http.get(url, res_method="read")
            guild = ctx.guild
            await guild.edit(banner=bio)
            embed = discord.Embed(
                description=f"*guild banner is now set to:*", color=0x2F3136
            )
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        except aiohttp.InvalidURL:
            await ctx.reply(embed=embed, mention_author=False)
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            embed = discord.Embed(
                description=f"*Please enter a real url or upload an image*",
                color=0x2F3136,
            )
            await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(
                description=f"*Your current url is not a supported image.*",
                color=0x2F3136,
            )
            await ctx.reply(embed=embed, mention_author=False)

    @command(
        name="setsplash",
        aliases=["changesplash"],
        description="change guild splash",
        extras={"perms": "administrator"},
        usage="```Syntax: !setsplash <url/image>\nExample: !setsplash https://crimebot.site/image.png```",
    )
    @blacklist()
    async def setsplash(self, ctx, url: str = None):
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None
        if not ctx.author.guild_permissions.manage_guild:
            await noperms(self, ctx, "manage_guild")
            return
        try:
            bio = await http.get(url, res_method="read")
            guild = ctx.guild
            await guild.edit(splash=bio)
            embed = discord.Embed(
                description=f"*guild splash is now set to:*", color=0x2F3136
            )
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        except aiohttp.InvalidURL:
            embed = discord.Embed(
                description=f"*Please enter a real url or upload an image*",
                color=0x2F3136,
            )
            await ctx.reply(embed=embed, mention_author=False)
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            embed = discord.Embed(
                description=f"*Please enter a real url or upload an image*",
                color=0x2F3136,
            )
            await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(
                description=f"*Your current url is not a supported image.*",
                color=0x2F3136,
            )
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="shows someone's avatar", usage="<member>", aliases=["av"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def avatar(
        self,
        ctx: commands.Context,
        *,
        member: Union[discord.Member, discord.User] = None,
    ):
        if member is None:
            member = ctx.author

        embed = discord.Embed(
            color=0x2F3136, title=f"{member.name}'s avatar", url=member.avatar.url
        )
        if isinstance(member, discord.Member):
            if not member.avatar:
                embed = discord.Embed(
                    color=0x2F3136,
                    title=f"{member.name}'s avatar",
                    url=member.display_avatar.url,
                )
                embed.set_image(url=member.display_avatar.url)
            else:
                embed = discord.Embed(
                    color=0x2F3136,
                    title=f"{member.name}'s avatar",
                    url=member.avatar.url,
                )
                embed.set_image(url=member.avatar.url)

            await ctx.reply(embed=embed, mention_author=False)

        elif isinstance(member, discord.User):
            embed = discord.Embed(
                color=0x2F3136,
                title=f"{member.name}'s avatar",
                url=member.display_avatar.url,
            )
            embed.set_image(url=member.display_avatar.url)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(
        description="Displays a user's avatar", aliases=["sav"], usage="sav"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serveravatar(self, ctx, *, member: discord.User = None):
        try:
            member = ctx.author if not member else member
            embed = discord.Embed(color=member.color)
            if member.guild_avatar:
                embed.set_image(url=member.display_avatar)
                embed.set_author(
                    name=member.name + "#" + member.discriminator,
                    icon_url=member.guild_avatar,
                )
            else:
                await ctx.send(
                    f"{ctx.message.author.mention}: You don't have a server avatar set"
                )
            await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @command(help="see someone's banner", description="utility", usage="<user>")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def banner(self, ctx: Context, *, member: User = None):
        if member is None:
            member = ctx.author

        user = await self.bot.fetch_user(member.id)
        if not user.banner:
            # Fix: Add a check to ensure user.accent_colour is not None before accessing its 'value'
            if user.accent_colour is not None:
                hexcolor = hex(user.accent_colour.value)
                hex2 = hexcolor.replace("0x", "")
                e = Embed(
                    color=0xF7F9F8,
                    title=f"{user.name}'s banner",
                    url=f"https://singlecolorimage.com/get/{hex2}/400x100",
                )
                e.set_image(url=f"https://singlecolorimage.com/get/{hex2}/400x100")
            else:
                # Handle the case when user.accent_colour is None
                # You may want to provide a default color or handle the situation accordingly
                hex2 = "000000"  # Default color is black
                e = Embed(
                    color=0xF7F9F8,
                    title=f"{user.name}'s banner",
                    description="User has no banner or accent colour.",
                )

            await sendmsg(self, ctx, None, e, None, None, None)
        else:
            embed = Embed(
                color=0xF7F9F8, title=f"{user.name}'s banner", url=user.banner.url
            )
            embed.set_image(url=user.banner.url)
            await sendmsg(self, ctx, None, embed, None, None, None)

    @command(help="play blacktea with your friends", description="fun")
    @cooldown(1, 20, BucketType.guild)
    @blacklist()
    async def blacktea(self, ctx: Context):
        try:
            if BlackTea.MatchStart[ctx.guild.id] is True:
                return await ctx.reply(
                    "somebody in this server is already playing blacktea",
                    mention_author=False,
                )
        except KeyError:
            pass

        BlackTea.MatchStart[ctx.guild.id] = True
        embed = Embed(
            color=0xF7F9F8,
            title="BlackTea Matchmaking",
            description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **20 seconds**",
        )
        embed.add_field(
            name="goal",
            value="You have **10 seconds** to say a word containing the given group of **3 letters.**\nIf failed to do so, you will lose a life. Each player has **2 lifes**",
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        mes = await ctx.send(embed=embed)
        await mes.add_reaction("🍵")
        await asyncio.sleep(20)
        me = await ctx.channel.fetch_message(mes.id)
        players = [user.id async for user in me.reactions[0].users()]
        players.remove(self.bot.user.id)

        if len(players) < 2:
            BlackTea.MatchStart[ctx.guild.id] = False
            return await ctx.send(
                "😦 {}, not enough players joined to start blacktea".format(
                    ctx.author.mention
                ),
                allowed_mentions=AllowedMentions(users=True),
            )

        while len(players) > 1:
            for player in players:
                strin = await BlackTea.get_string()
                await ctx.send(
                    f"⏰ <@{player}>, type a word containing **{strin.upper()}** in **10 seconds**",
                    allowed_mentions=AllowedMentions(users=True),
                )

                def is_correct(msg):
                    return msg.author.id == player

                try:
                    message = await self.bot.wait_for(
                        "message", timeout=10, check=is_correct
                    )
                except asyncio.TimeoutError:
                    try:
                        BlackTea.lifes[player] = BlackTea.lifes[player] + 1
                        if BlackTea.lifes[player] == 3:
                            await ctx.send(
                                f" <@{player}>, you're eliminated ☠️",
                                allowed_mentions=AllowedMentions(users=True),
                            )
                            BlackTea.lifes[player] = 0
                            players.remove(player)
                            continue
                    except KeyError:
                        BlackTea.lifes[player] = 0
                    await ctx.send(
                        f"💥 <@{player}>, you didn't reply on time! **{2-BlackTea.lifes[player]}** lifes remaining",
                        allowed_mentions=AllowedMentions(users=True),
                    )
                    continue
                if (
                    not strin.lower() in message.content.lower()
                    or not message.content.lower() in await BlackTea.get_words()
                ):
                    try:
                        BlackTea.lifes[player] = BlackTea.lifes[player] + 1
                        if BlackTea.lifes[player] == 3:
                            await ctx.send(
                                f" <@{player}>, you're eliminated ☠️",
                                allowed_mentions=AllowedMentions(users=True),
                            )
                            BlackTea.lifes[player] = 0
                            players.remove(player)
                            continue
                    except KeyError:
                        BlackTea.lifes[player] = 0
                    await ctx.send(
                        f"💥 <@{player}>, incorrect word! **{2-BlackTea.lifes[player]}** lifes remaining",
                        allowed_mentions=AllowedMentions(users=True),
                    )
                else:
                    await message.add_reaction("✅")

        await ctx.send(
            f"👑 <@{players[0]}> won the game!",
            allowed_mentions=AllowedMentions(users=True),
        )
        BlackTea.lifes[players[0]] = 0
        BlackTea.MatchStart[ctx.guild.id] = False

    @command(aliases=["ocr"])
    @blacklist()
    async def opticalcharacterrecognition(self, ctx, image: discord.Attachment):
        await ctx.typing()
        if isinstance(image, discord.Attachment):
            payload = {
                "url": image.url,
                "isOverlayRequired": False,
                "apikey": "K88991768788957",
                "language": "eng",
            }
            x = await self.bot.session.post(
                "https://api.ocr.space/parse/image", data=payload
            )

            x = await x.read()
            await ctx.reply(
                embed=discord.Embed(
                    color=0x2F3136,
                    description=json.loads(x.decode())["ParsedResults"][0][
                        "ParsedText"
                    ],
                )
            )

        elif isinstance(image, str):
            payload = {
                "url": __import__("yarl").URL(image),
                "isOverlayRequired": False,
                "apikey": "K88991768788957",
                "language": "eng",
            }
            x = await self.bot.session.post(
                "https://api.ocr.space/parse/image", data=payload
            )

            x = await x.read()
            await ctx.reply(
                embed=discord.Embed(
                    color=0x2F3136,
                    description=json.loads(x.decode())["ParsedResults"][0][
                        "ParsedText"
                    ],
                )
            )

    @command(
        help="view the first message of the channel",
        description="utility",
        usage="[none]",
        aliases=["firstmsg"],
    )
    @blacklist()
    async def firstmessage(self, ctx):
        async for message in ctx.channel.history(limit=1, oldest_first=True):
            await ctx.reply(
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label="first message",
                        url=message.jump_url,
                    )
                )
            )

    @command(
        help=f"crime repeats the message you request",
        description="utility",
        usage="[user]",
        aliases=["move"],
    )
    @blacklist()
    async def say(self, ctx, message=None):
        if not message:
            e = Embed(
                description=f"{Emojis.warn} tell crime to say something", color=0xF7F9F8
            )
            await ctx.reply(embed=e, mention_author=False)
            return
        e = Embed(description=f"**{message}**", color=0xF7F9F8).set_footer(
            text=f"requested by {ctx.author}"
        )
        await ctx.send(embed=e, mention_author=False)

    @command(
        help=f"deletes the channel and clones it",
        description="utility",
        usage="[NONE]",
        aliases=["clone"],
    )
    @blacklist()
    async def nuke(self, ctx):
        if not ctx.author.guild_permissions.manage_channels:
            await noperms(self, ctx, "manage_channels")
            return
        invoker = ctx.author.id
        channel = ctx.channel

        class disabledbuttons(discord.ui.View):
            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=True,
                emoji=Emojis.check,
            )
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(
                    name=interaction.channel.name,
                    reason=f"original channel nuked by {invoker}",
                )
                ch = await interaction.guild.fetch_channel(ch.id)
                e = discord.Embed(
                    description=f"<@{invoker}>: channel has been nuked successfully",
                    color=0xF7F9F8,
                )
                await ch.send(embed=e)

            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=True,
                emoji=Emojis.deny,
            )
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                embed = discord.Embed(
                    description="Are you sure you want to nuke this channel?\nIt will remove all webhooks and invites.",
                    color=0xF7F9F8,
                )
                await interaction.response.edit_message(
                    content=None, embed=embed, view=None
                )
                embed = discord.Embed(
                    description=f"<@{interaction.user.id}>: channel nuke has been cancelled",
                    color=0xF7F9F8,
                )
                await interaction.channel.send(embed=embed)

        class buttons(discord.ui.View):
            @discord.ui.button(style=discord.ButtonStyle.grey, emoji=Emojis.check)
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(
                    name=interaction.channel.name,
                    reason=f"original channel nuked by {invoker}",
                )
                ch = await interaction.guild.fetch_channel(ch.id)
                e = discord.Embed(
                    description=f"<@{invoker}>: channel has been nuked successfully",
                    color=0xF7F9F8,
                )
                await ch.send(embed=e)

            @discord.ui.button(style=discord.ButtonStyle.grey, emoji=Emojis.deny)
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                embed = discord.Embed(
                    description="Are you sure you want to nuke this channel?\nIt will remove all webhooks and invites.",
                    color=0xF7F9F8,
                )
                await interaction.response.edit_message(
                    content=None, embed=embed, view=disabledbuttons()
                )
                embed = discord.Embed(
                    description=f"<@{interaction.user.id}>: channel nuke has been cancelled",
                    color=0xF7F9F8,
                )
                await interaction.channel.send(embed=embed)

        embed = discord.Embed(
            description="Are you sure you want to nuke this channel?\nIt will remove all webhooks and invites.",
            color=0xF7F9F8,
        )
        await ctx.reply(embed=embed, view=buttons())

    @commands.command(aliases=["webshoty", "sa"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def webshot(self, ctx, *, link: str = None) -> None:
        if link == None:
            em = discord.Embed(
                color=0x2F3136, description=f"> You dont type a __site__ for search"
            )
            await ctx.send(embed=em)
            return
        links = ["https://", "http://"]
        if not (link.startswith(tuple(links))):
            await ctx.send(
                embed=discord.Embed(
                    color=0x2F3136,
                    description=f"> You didn't input __https __ before the link provided",
                )
            )
            return
        else:
            n = discord.Embed(
                description=f"> Preview {link.replace('https://', '').replace('http://', '')}",
                color=0x2F3136,
            )
            n.set_image(
                url="https://api.popcat.xyz/screenshot?url="
                + str(link.replace("http://", "https://"))
            )
            await ctx.reply(embed=n, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def summer(self, ctx: commands.Context):
        # x = dt.datetime(2022, 12, 25) - dt.datetime.today()
        xx = datetime(2023, 6, 14)
        xxx = datetime.now()
        x = xx - xxx
        duration_secs = int(x.total_seconds())
        weeks = int(duration_secs / (86400 * 7))
        duration_secs = int(duration_secs % 86400 * 7)
        days = int(duration_secs / 86400)
        duration_secs = int(duration_secs % 86400)
        hours = int(duration_secs / 3600)
        duration_secs = int(duration_secs % 3600)
        minutes = int(duration_secs / 60)
        seconds = int(duration_secs % 60)
        embed = discord.Embed(
            title=f"Summer countdown",
            description=f"> **Left:** __{weeks} weeks, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds__",
            color=0x2F3136,
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def xmas(self, ctx: commands.Context):
        # x = dt.datetime(2022, 12, 25) - dt.datetime.today()
        xx = datetime(2022, 12, 25)
        xxx = datetime.now()
        x = xx - xxx
        duration_secs = int(x.total_seconds())
        weeks = int(duration_secs / (86400 * 7))
        duration_secs = int(duration_secs % 86400 * 7)
        days = int(duration_secs / 86400)
        duration_secs = int(duration_secs % 86400)
        hours = int(duration_secs / 3600)
        duration_secs = int(duration_secs % 3600)
        minutes = int(duration_secs / 60)
        seconds = int(duration_secs % 60)
        embed = discord.Embed(
            title=f"Christmas countdown",
            description=f"> **Left:** __{weeks} weeks, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds__",
            color=0x2F3136,
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def vancheck(self, ctx: commands.Context):
        if ctx.guild.vanity_url_code is None:
            embed = discord.Embed(
                color=0x2F3136, description=f"> **This server has no vanity**"
            )
            embed.set_footer(text="No Vanity")

        elif ctx.guild.vanity_url_code is not None:
            embed = discord.Embed(
                color=0x2F3136,
                description=f"> **Guild Vanity:** `{ctx.guild.vanity_url_code}`",
            )
            embed.set_footer(text="Server Vanity")

        await ctx.send(embed=embed)

    @command(
        help=f"returns the boost count of your guild",
        description="utility",
        usage="[NONE]",
    )
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def boostcount(self, ctx):
        embed = discord.Embed(
            description=f"> **{ctx.guild.name}**'s Boost Count is {str(ctx.guild.premium_subscription_count)}",
            colour=0xF7F9F8,
        )
        await ctx.reply(embed=embed, mention_author=False)

    @command(
        help=f"returns the boost count of your guild",
        description="utility",
        usage="[member]",
        aliases=["ui", "whois"],
    )
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def userinfo(
        self, ctx, *, member: Union[discord.Member, discord.User] = None
    ):
        if member is None:
            member = ctx.author
        k = 0
        for guild in self.bot.guilds:
            if guild.get_member(member.id) is not None:
                k += 1

        if isinstance(member, discord.Member):
            if str(member.status) == "online":
                status = "<:online:1109854282699780096>"
            elif str(member.status) == "dnd":
                status = "<a:dnd2:1103800854567452722>"
            elif str(member.status) == "idle":
                status = "<:Idle:1128563126216949770>"
            elif str(member.status) == "offline":
                status = "<:offline:1128563287458582528>"
            embed = discord.Embed(color=0xF7F9F8)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            embed.add_field(
                name="joined",
                value=f"<t:{int(member.joined_at.timestamp())}:F>\n<t:{int(member.joined_at.timestamp())}:R>",
                inline=True,
            )
            if member.activity:
                activity = member.activity.name
            else:
                activity = ""

            embed.add_field(
                name="> __status__", value=status + " " + activity, inline=True
            )
            embed.add_field(
                name="> registered",
                value=f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>",
                inline=False,
            )
            if len(member.roles) > 1:
                role_string = " ".join([r.mention for r in member.roles][1:])
                embed.add_field(
                    name="> roles [{}]".format(len(member.roles) - 1),
                    value=role_string,
                    inline=True,
                )
            embed.set_footer(text="ID: " + str(member.id))
            await ctx.reply(embed=embed, mention_author=True)
            return
        elif isinstance(member, discord.User):
            e = discord.Embed(color=0xF7F9F8)
            e.set_author(name=f"{member}", icon_url=member.display_avatar.url)
            e.set_thumbnail(url=member.display_avatar.url)
            e.add_field(
                name="> registered",
                value=f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>",
                inline=False,
            )
            embed.set_footer(text="ID: " + str(member.id))

            await ctx.reply(embed=e, mention_author=False)

    @command(
        help=f"returns the urban dictionary meaning of the word",
        description="utility",
        usage="[word]",
        aliases=["ud"],
    )
    @blacklist()
    async def urban(self, ctx, *, word):
        if word is None:
            e = discord.Embed(description="> please provide a word")
            await ctx.send(embed=e)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.urbandictionary.com/v0/define?term={word}"
                ) as resp:
                    data = await resp.json()
            if not data["list"]:
                await ctx.send(f"No results found for {word}.")
                return
            definition = data["list"][0]["definition"]
            example = data["list"][0]["example"]
            embed = discord.Embed(title=f"Urban Dictionary: {word}", color=0x2B2D31)
            embed.add_field(name="Definition", value=definition, inline=False)
            embed.add_field(name="Example", value=example, inline=False)
            embed.set_thumbnail(
                url="https://imgs.search.brave.com/CrwNIBGq0wryzQTxOpFlsZTHvf7jCqcXU7Di-qqkU60/rs:fit:512:512:1/g:ce/aHR0cHM6Ly9zbGFj/ay1maWxlczIuczMt/dXMtd2VzdC0yLmFt/YXpvbmF3cy5jb20v/YXZhdGFycy8yMDE4/LTAxLTExLzI5NzM4/NzcwNjI0NV84NTg5/OWE0NDIxNmNlMTYw/NGM5M181MTIuanBn"
            )
            await ctx.send(embed=embed)

    @command(
        help=f"reverse image searches your image",
        description="utility",
        usage="[image]",
        aliases=["rev"],
    )
    @blacklist()
    async def reverse(self, ctx, *, img):
        try:
            link = f"https://images.google.com/searchbyimage?image={img}"
            em = discord.Embed(
                description=f"{ctx.author}'s reverse search", color=0xF7F9F8
            ).set_footer(text=f"Requested by {ctx.author}")
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link, label="reverse", url=link
                )
            )
            await ctx.send(embed=em, view=view)
        except Exception as e:
            print(f"[ERROR]: {e}")

    @command(
        help=f"reverse image searches your avatar",
        description="utility",
        usage="[user]",
        aliases=["revav", "rav"],
    )
    @blacklist()
    async def reverseav(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        if user is None:
            user = ctx.author
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
        try:
            link = (
                f"https://images.google.com/searchbyimage?image={user.display_avatar}"
            )
            em = discord.Embed(
                color=0xF7F9F8, description=f"{user.name}'s reverse search"
            ).set_footer(text=f"Requested by {ctx.author}")
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label=f"{user.name}'s revav",
                    url=link,
                )
            )
            await ctx.send(embed=em, view=view)
        except Exception as e:
            print(f"[ERROR]: {e}")

    @command(
        name="ben", description="utility", help="ask ben a question", usage="(question)"
    )
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def ben(self, ctx, *, question: str = None):
        if not question:
            await commandhelp(self, ctx, ctx.command.name)
            return
        async with ctx.typing():
            video = random.choice(os.listdir("ben"))
            await ctx.reply(file=discord.File(f"ben/{video}"))

    @command(name="xbox", description="show a xbox account", brief="username")
    @blacklist()
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
                    description=f"{Emojis.warn} Gamertag **`{username}`** not found",
                    color=int("f7f9f8", 16),
                )
            )

    @command(
        help="add an emoji",
        description="emoji",
        usage="[emoji] <name>",
        aliases=["steal", "add", "emojiadd"],
    )
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def addemoji(
        self,
        ctx,
        emoji: Union[discord.Emoji, discord.PartialEmoji] = None,
        *,
        name=None,
    ):
        if not ctx.author.guild_permissions.manage_emojis_and_stickers:
            await noperms(self, ctx, "manage_emojis_and_stickers")
            return
        if emoji is None:
            return await commandhelp(self, ctx, ctx.command.name)
        if name == None:
            name = emoji.name

        url = emoji.url
        async with aiohttp.ClientSession() as ses:
            async with ses.get(url) as r:
                try:
                    img = BytesIO(await r.read())
                    bytes = img.getvalue()
                    emoji = await ctx.guild.create_custom_emoji(image=bytes, name=name)
                    await sendmsg(
                        self,
                        ctx,
                        f"added emoji `{name}` | {emoji}",
                        None,
                        None,
                        None,
                        None,
                    )
                except discord.HTTPException as re:
                    pass

    @command(
        help="add multiple emojis",
        description="emoji",
        usage="[emojis]",
        aliases=["am]"],
    )
    @cooldown(1, 6, BucketType.guild)
    @blacklist()
    async def addmultiple(
        self, ctx: Context, *emoji: Union[discord.Emoji, discord.PartialEmoji]
    ):
        if not ctx.author.guild_permissions.manage_emojis_and_stickers:
            await noperms(self, ctx, "manage_emojis_and_stickers")
            return
        if len(emoji) == 0:
            return await commandhelp(self, ctx, ctx.command.name)
        if len(emoji) > 20:
            return await ctx.reply("you can only add up to 20 emojis at once")
        emojis = []
        await ctx.channel.typing()
        for emo in emoji:
            url = emo.url
            async with aiohttp.ClientSession() as ses:
                async with ses.get(url) as r:
                    try:
                        img = BytesIO(await r.read())
                        bytes = img.getvalue()
                        emoj = await ctx.guild.create_custom_emoji(
                            image=bytes, name=emo.name
                        )
                        emojis.append(f"{emoj}")
                    except discord.HTTPException as re:
                        pass

        embed = discord.Embed(color=0xF7F9F8, title=f"added {len(emoji)} emojis")
        embed.description = "".join(map(str, emojis))
        await sendmsg(self, ctx, None, embed, None, None, None)

    @command(
        help="returns a list of server's emojis",
        description="emoji",
        aliases=["guildemojis"],
    )
    @cooldown(1, 3, BucketType.user)
    @blacklist()
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
        if l == 10:
            messages.append(mes)
        number.append(
            discord.Embed(
                color=0xF7F9F8,
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
                color=0xF7F9F8,
                title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]",
                description=messages[i],
            )
        )
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button("prev", emoji="<:crimeleft:1082120060556021781>")
        paginator.add_button("delete", emoji="<:stop:1018156487232720907>")
        paginator.add_button("next", emoji="<:crimeright:1082120065853423627>")
        await paginator.start()

    @command(
        aliases=["downloademoji", "e"],
        help="gets an image version of your emoji",
        description="emoji",
        usage="[emoji]",
    )
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def enlarge(self, ctx, emoji: Union[discord.PartialEmoji, str] = None):
        if emoji is None:
            await commandhelp(self, ctx, ctx.command.name)
            return
        elif isinstance(emoji, discord.PartialEmoji):
            await sendmsg(self, ctx, emoji.url, None, None, None, None)
            return
        elif isinstance(emoji, str):
            ordinal = ord(emoji)
            await sendmsg(
                self,
                ctx,
                f"https://twemoji.maxcdn.com/v/latest/72x72/{ordinal:x}.png",
                None,
                None,
                None,
                None,
            )
        else:
            e = discord.Embed(
                color=Colors.yellow,
                description=f"{Emojis.warn} {ctx.author.mention}: emoji not found",
            )
            await sendmsg(self, ctx, None, e, None, None, None)

    @command(
        help="gets the banner from a server based on an invite code",
        description="utility",
        usage="[invite code]",
    )
    @blacklist()
    async def sbanner(self, ctx, *, link=None):
        if link is None:
            if ctx.guild.banner:
                embed = Embed(color=0xF7F9F8, title=f"{ctx.guild.name}'s banner")
                embed.set_image(url=ctx.guild.banner.url)
                await sendmsg(self, ctx, None, embed, None, None, None)
            else:
                await ctx.send("The server does not have a banner.")
        else:
            invite_code = link.split("/")[
                -1
            ]  # Extract the invite code from the link, if provided
            async with aiohttp.ClientSession() as cs:
                async with cs.get(DISCORD_API_LINK + invite_code) as r:
                    if r.status != 200:
                        await ctx.send("Invalid invite code or unable to fetch data.")
                        return
                    data = await r.json()
            guild_data = data.get("guild")

            if guild_data is not None:
                format = ".gif" if "a_" in guild_data.get("banner", "") else ".png"

                embed = Embed(color=0xF7F9F8, title=f"{guild_data['name']}'s banner")
                embed.set_image(
                    url="https://cdn.discordapp.com/banners/"
                    + str(guild_data["id"])
                    + "/"
                    + guild_data["banner"]
                    + f"{format}?size=1024"
                )
                await sendmsg(self, ctx, None, embed, None, None, None)
            else:
                await ctx.send("Invalid invite code or guild data not found.")

    @command(
        help="gets the icon from a server based on an invite code",
        description="utility",
        usage="[invite code]",
    )
    @blacklist()
    async def sicon(self, ctx, *, link=None):
        async def send_message(embed):
            await ctx.send(embed=embed)

        if link is None:
            embed = Embed(color=0xF7F9F8, title=f"{ctx.guild.name}'s icon")
            embed.set_image(url=ctx.guild.icon_url)
            await send_message(embed)
        else:
            invite_code = link.strip("/").split("/")[
                -1
            ]  # Extract the invite code from the link if provided

            async with aiohttp.ClientSession() as cs:
                async with cs.get(DISCORD_API_LINK + invite_code) as r:
                    if r.status == 200:
                        data = await r.json()
                        guild_name = data.get("guild", {}).get("name")
                        guild_icon_id = data.get("guild", {}).get("icon")
                        if guild_name and guild_icon_id:
                            format = ".gif" if "a_" in guild_icon_id else ".png"
                            embed = Embed(color=0xF7F9F8, title=f"{guild_name}'s icon")
                            embed.set_image(
                                url=f"https://cdn.discordapp.com/icons/{data['guild']['id']}/{guild_icon_id}{format}?size=1024"
                            )
                            await send_message(embed)
                        else:
                            await ctx.send("Failed to retrieve server information.")
                    else:
                        await ctx.send("Invalid invite code or server not accessible.")

    @command(help="repost a random tiktok video")
    @blacklist()
    async def fyp(self, ctx):
        async with ctx.typing():
            fyp_videos = await for_you()
            videos = []
            for video in fyp_videos:
                videos.append(video)
            data = random.choice(videos)
            download = data["download_urls"]["no_watermark"]
            async with aiohttp.ClientSession() as session:
                async with session.get(download) as r:
                    data = await r.read()
            file = discord.File(
                io.BytesIO(data), filename=f"{self.bot.user.name}tok.mp4"
            )
            await ctx.reply(file=file)
            return

    @command()
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def mods(self, ctx):
        """Check which mods are online on current guild"""
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "<:online:1103800966551191655>"},
            "idle": {"users": [], "emoji": "<:Idle:1128563126216949770>"},
            "dnd": {"users": [], "emoji": "<a:dnd2:1128561446033305660>"},
            "offline": {"users": [], "emoji": "<:offline:1128563287458582528>"},
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += (
                    f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"
                )
        await ctx.send(
            embed=Embed(
                title="All Discord Moderators Online", description=f">>> {message}"
            )
        )

    @commands.hybrid_command(
        name="afk",
        description="Go afk with a reason",
        aliases=["dnd"],
        usage="afk (reason)",
    )
    @commands.cooldown(1, 4, commands.BucketType.guild)
    async def afk(self, ctx, *, status="AFK"):
        db = utils.read_json("afk")
        ls = datetime.now().timestamp()
        db[str(ctx.author.id)] = {"guild": [], "status": status, "lastseen": ls}
        db[str(ctx.author.id)]["guild"].append(ctx.guild.id)
        utils.write_json(db, "afk")
        db = utils.read_json("afk")[str(ctx.author.id)]
        embed = discord.Embed(
            color=self.success,
            description=f'{self.done} {ctx.author.mention}**:** you\'re now afk with the status **{db["status"]}**',
        )
        await ctx.reply(embed=embed)

    @commands.command(
        name="weather",
        description="View weather in country/location",
        aliases=["temptature"],
        usage="weather [location]",
    )
    @commands.cooldown(1, 6, commands.BucketType.guild)
    async def weather(self, ctx, *, location: str):
        location = location.replace(" ", "+")
        req = await (
            await self.bot.session.get(
                f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?unitGroup=metric&key=4G437RNSM6FDH6EFGXCJ5VX5Q&contentType=json"
            )
        ).json()
        title = req["resolvedAddress"]
        description = req["days"][0]["description"]
        feelslike = int(req["days"][0]["feelslike"]) * 1.8 + 32
        temperature = int(req["days"][0]["temp"]) * 1.8 + 32
        embed = discord.Embed(color=utils.color("main"))
        embed.description = description
        embed.title = title
        embed.add_field(name="Temperature", value=f"{temperature} °F")
        embed.add_field(name="Feels Like", value=f"{feelslike} °F", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.set_thumbnail(url=ctx.author.display_avatar)
        await ctx.reply(embed=embed)

    @commands.command(
        description="See a member's past avatars",
        help="utility",
        usage="<member>",
        aliases=["avh"],
    )
    async def avatarhistory(self, ctx, *, member: Member = None):
        if not member:
            member = ctx.author

        # You can change the RGB values to customize the embed color
        embed_color = Color.from_rgb(255, 0, 0)

        avatar_url = f"https://api.pretend.space/avatars/{member.id}"
        embed = Embed(
            description=f"See **{member}'s** past [avatars]({avatar_url})",
            color=embed_color,
        )
        await ctx.reply(embed=embed)

    @commands.command(
        help="see when a user was last seen", description="utility", usage="[member]"
    )
    @commands.cooldown(1, 4, BucketType.user)
    @blacklist()
    async def seen(self, ctx, *, member: discord.Member = None):
        if member is None:
            return await commandhelp(self, ctx, ctx.command.name)

        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM seen WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, member.id),
            )
            check = await cursor.fetchone()
            if check is None:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=discord.Color.orange(),
                        description=f"{ctx.author.mention}: I didn't see **{member}**",
                    )
                )

            ts = check[2]
            await ctx.reply(
                embed=discord.Embed(
                    color=discord.Color.default(),
                    description="{}: **{}** was last seen <t:{}:R>".format(
                        ctx.author.mention, member, ts
                    ),
                )
            )

    @commands.command(
        name="spotifyglobal",
        description="Show entire guild spotify listeners",
        aliases=["spotify", "spot"],
        usage="spotify",
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @blacklist()
    async def spotifyglobal(self, ctx: Context):
        async with ctx.typing():
            embeds = []
            page = 0
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
            if not members:
                return await ctx.send("No one is listening to Spotify in this server.")
            members.sort(
                key=lambda member: discord.utils.find(
                    lambda activity: activity.type == discord.ActivityType.listening
                    and activity.name == "Spotify",
                    member.activities,
                ).title
            )
            for member in members:
                activity = discord.utils.find(
                    lambda activity: activity.type == discord.ActivityType.listening
                    and activity.name == "Spotify",
                    member.activities,
                )
                embed = discord.Embed(
                    title=f"{member}'s Spotify",
                    description=f"**Song:** {activity.title}\n**Album:** {activity.album}\n**Artist:** {activity.artist}",
                    color=0x4C5264,
                )
                embed.set_thumbnail(url=activity.album_cover_url)
                embeds.append(embed)
            if len(embeds) == 1:
                return await ctx.send(embed=embeds[0])
            from modules import paginator as pg

            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button(
                "prev",
                emoji="<:icons_leftarrow:1135806089473032262>",
                style=discord.ButtonStyle.blurple,
            )
            paginator.add_button(
                "next",
                emoji="<:icons_rightarrow:1135806059366322186>",
                style=discord.ButtonStyle.blurple,
            )
            paginator.add_button(
                "goto",
                emoji="<:goto1:1139300180143910994>",
                style=discord.ButtonStyle.gray,
            )
            paginator.add_button(
                "delete",
                emoji="<:cancel:1139300177052713061>",
                style=discord.ButtonStyle.red,
            )
            await paginator.start()

    @commands.command()
    async def instagram(self, ctx, username):
        L = instaloader.Instaloader()

        try:
            profile = instaloader.Profile.from_username(L.context, username)

            embed = discord.Embed(title=f"", color=discord.Color.purple())
            embed.set_thumbnail(url=profile.profile_pic_url)
            embed.add_field(
                name="<:004:1143040752381874269> **Followers**",
                value=f"**{profile.followers}**",
                inline=True,
            )
            embed.add_field(
                name="<:004:1143040752381874269> **Following**",
                value=f"**{profile.followees}**",
                inline=True,
            )
            embed.add_field(
                name="<:004:1143040752381874269> **Posts**",
                value=f"**{profile.mediacount}**",
                inline=True,
            )

            profile_url = f"https://www.instagram.com/{username}/"
            if profile.is_private:
                embed.set_author(name=f"{username} 🔒", icon_url="")
                embed.set_footer(text="**This user's account is private**")
            else:
                embed.set_author(name=username, url=profile_url)

            await ctx.send(embed=embed)

        except instaloader.exceptions.ProfileNotExistsException:
            error_embed = discord.Embed(
                title="",
                description="<:deny:1139298463658553364> **Sorry, the provided Instagram username does not exist**",
                color=discord.Color.purple(),
            )
            await ctx.send(embed=error_embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="",
                description="<:deny:1139298463658553364> **Sorry, there was an error fetching the information. Please try again later**",
                color=discord.Color.purple(),
            )
            await ctx.send(embed=error_embed)


async def setup(bot):
    await bot.add_cog(utility(bot))
