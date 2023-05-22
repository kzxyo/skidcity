import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class messageEvents(commands.Cog):
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

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        try:
            members = message.mentions
            async for member in utils.aiter(members):

                try:
                    db = self.bot.db("afk").get(str(member.id))
                    embed = discord.Embed(
                        color=0x2F3136, description=f'> **Reason:** {db.get("status")}'
                    )
                    embed.set_author(
                        name=f"{member.name} is currently afk",
                        icon_url=member.display_avatar,
                    )
                    ls = utils.moment(datetime.fromtimestamp(db.get("lastseen")))
                    embed.set_footer(
                        text=f"last seen {ls} {'ago' if 'ago' not in ls else ''}",
                        icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                    )
                    if message.guild.id in db["guild"]:
                        await message.reply(embed=embed)
                    else:
                        pass

                except:
                    pass

        except:
            pass

        msgs = utils.read_json("messages")
        try:
            msgs[str(message.guild.id)][str(message.author.id)] += 1
            utils.write_json(msgs, "messages")
        except:
            try:
                msgs[str(message.guild.id)][str(message.author.id)] = 0
                msgs[str(message.guild.id)][str(message.author.id)] += 1
                utils.write_json(msgs, "messages")
            except:

                try:
                    msgs[str(message.guild.id)] = {}
                    msgs[str(message.guild.id)][str(message.author.id)] = 0
                    msgs[str(message.guild.id)][str(message.author.id)] += 1
                    utils.write_json(msgs, "messages")
                except:
                    pass

        if self.bot.user.mention in message.content:

            prefixes = []
            try:
                if utils.read_json("guildprefixes")[str(message.guild.id)]["prefix"]:
                    prefixes.append(
                        f"guild prefix: **`{utils.read_json('guildprefixes')[str(message.guild.id)]['prefix']}`**"
                    )
            except:
                pass
            try:
                if utils.read_json("prefixes")[str(message.author.id)]["prefix"]:
                    prefixes.append(
                        f"your prefix: **`{utils.read_json('prefixes')[str(message.author.id)]['prefix']}`**"
                    )
            except:
                pass
            try:
                await message.reply(
                    f"global prefix: **`{utils.read_json('config')['prefix']}`**{', ' if prefixes else ''}{', '.join(prefixes)}",
                    view=discord.ui.View().add_item(
                        discord.ui.Button(
                            style=discord.ButtonStyle.link,
                            label="invite vile",
                            url="https://discord.com/api/oauth2/authorize?self.bot_id=991695573965099109&permissions=8&scope=self.bot%20applications.commands",
                        )
                    ),
                    delete_after=10,
                )
            except:
                await message.reply(
                    f"global prefix: **`{utils.read_json('config')['prefix']}`**",
                    view=discord.ui.View().add_item(
                        discord.ui.Button(
                            style=discord.ButtonStyle.link,
                            label="invite vile",
                            url="https://discord.com/api/oauth2/authorize?self.bot_id=991695573965099109&permissions=8&scope=self.bot%20applications.commands",
                        )
                    ),
                    delete_after=10,
                )

        try:
            x = utils.read_json("prefixes")[str(message.author.id)]["prefix"]
            if x == "…":
                return

        except:
            pass

        try:
            db = utils.read_json("autoresponder")
            words = message.content.lower().split()
            async for w, v in utils.aiter(db[str(message.guild.id)].items()):
                if w in words:
                    try:
                        x = await utils.to_object(
                            await utils.embed_replacement(message.author, v)
                        )
                        if "--reply" in v:
                            await message.reply(**x)
                        else:
                            await message.channel.send(**x)
                    except:
                        pass
        except:
            pass

        try:
            if not message.author.bot:
                db = utils.read_json("autoreact")
                words = message.content.lower().split(" ")
                async for word in utils.aiter(words):
                    try:
                        [
                            await message.add_reaction(self.bot.get_emoji(emoji))
                            async for emoji in utils.aiter(
                                db[str(message.guild.id)][word]
                            )
                        ]
                    except:
                        pass
        except:
            pass

        try:
            if not message.author.bot:
                if message.author.guild_permissions.administrator != False:
                    db = utils.read_json("chatfilter")
                    words = message.content.lower().replace("\n", " ").split(" ")
                    async for word in utils.aiter(words):
                        if word in db[str(message.guild.id)]:
                            await message.reply(
                                embed=discord.Embed(
                                    color=utils.color("fail"),
                                    description=f"{utils.emoji('fail')} {message.author.mention} watch your mouth, that word is **filtered** in this guild",
                                )
                            )
                            try:
                                await message.delete()
                            except:
                                pass
        except:
            pass

        try:
            words = ["discord.gg/", "discord.com/invite/"]
            async for word in utils.aiter(words):
                if word in message.content:

                    if message.guild.id != 924215436042698792:
                        x = self.bot.db("antiinvite")
                        p = x.get(str(message.guild.id))
                        if p.get("state") == "on":
                            if (
                                message.author.guild_permissions.manage_messages
                                == False
                            ):
                                try:
                                    await message.delete()
                                except:
                                    pass
                                try:
                                    import humanfriendly

                                    await message.author.edit(
                                        timed_out_until=datetime.now().astimezone()
                                        + timedelta(
                                            seconds=humanfriendly.parse_timespan("11m")
                                        ),
                                        reason="muted by my anti invite",
                                    )
                                    try:
                                        await message.author.send(
                                            f"{utils.emoji('dash')} you were muted in **{message.guild.name}**\n{utils.emoji('reply')} **muted by my anti invite**"
                                        )
                                    except:
                                        pass
                                    await message.channel.send(
                                        embed=discord.Embed(
                                            color=0x2F3136,
                                            description=f"{utils.emoji('done')} {self.bot.user.mention}**: {message.author}** has been muted for **11m**\n{utils.emoji('reply')} muted by my **anti invite**",
                                        )
                                    )
                                except:
                                    pass

        except:
            pass

        try:

            if len(message.mentions) >= 5:
                if message.author.guild_permissions.manage_guild == False:
                    try:
                        await message.delete()
                    except:
                        pass
                    try:
                        import humanfriendly

                        await message.author.edit(
                            timed_out_until=datetime.now().astimezone()
                            + timedelta(seconds=humanfriendly.parse_timespan("11m")),
                            reason="vile anti-spam",
                        )
                        try:
                            await message.author.send(
                                f"{utils.emoji('dash')} you were muted in **{message.guild.name}**\n{utils.emoji('reply')} **muted by my anti spam**"
                            )
                        except:
                            pass
                        await message.channel.send(
                            embed=discord.Embed(
                                color=0x2F3136,
                                description=f"{utils.emoji('done')} {self.bot.user.mention}**: {message.author}** has been muted for **11m**\n{utils.emoji('reply')} muted by my **anti spam**",
                            )
                        )
                    except:
                        pass

        except:
            pass

        try:
            if len(message.content) > 750:
                if message.author.guild_permissions.manage_guild == False:
                    try:
                        await message.delete()
                    except:
                        pass
                    try:
                        import humanfriendly

                        await message.author.edit(
                            timed_out_until=datetime.now().astimezone()
                            + timedelta(seconds=humanfriendly.parse_timespan("11m")),
                            reason="vile anti-spam",
                        )
                        try:
                            await message.author.send(
                                f"{utils.emoji('dash')} you were muted in **{message.guild.name}**\n{utils.emoji('reply')} **muted by my anti spam**"
                            )
                        except:
                            pass
                        await message.channel.send(
                            embed=discord.Embed(
                                color=0x2F3136,
                                description=f"{utils.emoji('done')} {self.bot.user.mention}**: {message.author}** has been muted for **11m**\n{utils.emoji('reply')} muted by my **anti spam**",
                            )
                        )
                    except:
                        pass
        except:
            pass

        try:
            x = self.bot.db("uwulock")
            if message.author.id in x[str(message.guild.id)]:
                from utils import converter

                await message.delete()
                await message.channel.send(
                    f"{converter.send_uwu(message.content)} - **{message.author}**"
                )
        except:
            pass


async def setup(bot):
    await bot.add_cog(messageEvents(bot))
