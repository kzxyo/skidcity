import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class antinukeEvents(commands.Cog):
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
    async def on_member_join(self, member):

        age = datetime.now().astimezone() - member.created_at
        age = age.days
        try:
            ison = utils.read_json("antialt")[str(member.guild.id)]["enabled"]
            minage = utils.read_json("antialt")[str(member.guild.id)]["days"]
            if ison == "yes":
                aa = True
            if ison == "no":
                aa = False
        except Exception as e:
            print(f"error {e}")
            aa = False
            minage = 0
        if age < minage and aa == True:
            try:
                await member.kick(reason="vile anti-alt")
            except:
                pass

            try:
                modlog = utils.read_json("antialt")

                if modlog[str(member.guild.id)] != None:
                    made = datetime.fromtimestamp(datetime.timestamp(member.created_at))
                    h = made.strftime("%H")
                    if h == 00:
                        hour = 12

                    else:
                        hour = h

                    embed = discord.Embed(
                        color=self.warning,
                        title=f"{self.warn} Possible Alt-Account Kicked",
                        timestamp=datetime.now(),
                    )
                    embed.set_footer(
                        text=f"Vile Anti-Alt",
                        icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                    )
                    embed.set_author(name=member, icon_url=member.avatar)
                    embed.add_field(
                        name=f"{self.dash} Account's age",
                        value=f"{self.reply} {age} days",
                        inline=True,
                    )
                    embed.add_field(
                        name=f"{self.dash} Age required:",
                        value=f"{self.reply} {minage} days",
                        inline=True,
                    )
                    embed.add_field(
                        name=f"{self.dash} Account Creation",
                        value=f"{self.reply} {made.strftime('%B %d').replace('0', '')}, {made.strftime('%Y')} {hour}:{made.strftime('%M %p')}",
                        inline=True,
                    )

                    await self.bot.get_channel(
                        modlog[str(member.guild.id)]["channel"]
                    ).send(embed=embed)

                else:

                    pass
            except:
                pass

        try:
            if member.bot:
                async for logs in member.guild.audit_logs(
                    limit=1,
                    after=datetime.now() - timedelta(seconds=3),
                    action=discord.AuditLogAction.bot_add,
                ):
                    executor = await member.guild.fetch_member(logs.user.id)
                    target = await member.guild.fetch_member(logs.target.id)
                reason = "vile antinuke: anti bot is enabled"
                anti = utils.read_json("antinuke")[str(member.guild.id)]
                if (
                    executor.id != member.guild.owner.id
                    and executor.id not in anti["whitelisted"]
                    and executor.id != self.bot.user.id
                    and anti["antibot"] == "on"
                ):

                    punishments = ["ban", "kick", "strip", "jail"]
                    pment = anti["punishment"]
                    if pment == "ban":

                        await executor.ban(reason=reason)
                        try:
                            await executor.send(
                                f"{self.dash} you were banned from **{member.guild.name}**\n{self.reply} **{reason}**"
                            )
                        except:
                            pass

                    elif pment == "kick":

                        await executor.kick(reason=reason)
                        try:
                            await executor.send(
                                f"{self.dash} you were kicked from **{member.guild.name}**\n{self.reply} **{reason}**"
                            )
                        except:
                            pass

                    elif pment == "strip":

                        await executor.edit(roles=[])
                        try:
                            await executor.send(
                                f"{self.dash} you were stripped from your roles in **{member.guild.name}**\n{self.reply} **{reason}**"
                            )
                        except:
                            pass

                    elif pment == "jail":

                        await executor.edit(roles=[])
                        role = discord.utils.get(member.guild.roles, name="jailed")
                        if not role:
                            await member.guild.create_role(name="jailed")

                        db = utils.read_json("jail")
                        try:
                            db[str(executor.guild.id)][str(executor.id)] = [
                                role.id
                                async for role in utils.aiter(executor.roles[1:])
                            ]
                            utils.write_json(db, "jail")
                        except:
                            db[str(executor.guild.id)] = {}
                            db[str(executor.guild.id)][str(executor.id)] = [
                                role.id
                                async for role in utils.aiter(executor.roles[1:])
                            ]
                            utils.write_json(db, "jail")

                        jail = discord.utils.get(
                            member.guild.text_channels, name="jail"
                        )
                        if not jail:
                            try:
                                overwrites = {
                                    member.guild.default_role: discord.PermissionOverwrite(
                                        read_messages=False, send_messages=False
                                    ),
                                    member.guild.me: discord.PermissionOverwrite(
                                        read_messages=True
                                    ),
                                }
                                jail = await member.guild.create_text_channel(
                                    "jail", overwrites=overwrites
                                )
                            except discord.Forbidden:
                                return

                        for channel in member.guild.channels:
                            if channel.name == "jail":
                                perms = channel.overwrites_for(executor)
                                perms.send_messages = True
                                perms.read_messages = True
                                await channel.set_permissions(executor, overwrite=perms)
                            else:
                                perms = channel.overwrites_for(executor)
                                perms.send_messages = False
                                perms.read_messages = False
                                perms.view_channel = False
                                await channel.set_permissions(executor, overwrite=perms)

                        role = discord.utils.get(member.guild.roles, name="jailed")
                        await executor.add_roles(role, reason=reason)
                        try:
                            await executor.send(
                                f"{self.dash} you were jailed in **{member.guild.name}**\n{self.reply} **{reason}**"
                            )
                        except:
                            pass

                    await target.kick(reason=f"vile antinuke: anti bot is enabled")
                    log = utils.read_json("antinuke")[str(member.guild.id)][
                        "logchannel"
                    ]

                    embed = discord.Embed(
                        color=self.warning,
                        title=f"Bot Kicked",
                        timestamp=datetime.now(),
                    )
                    embed.set_footer(
                        text=f"Vile Anti-Bot",
                        icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                    )
                    embed.set_author(name=target, icon_url=executor.display_avatar)
                    embed.add_field(
                        name=f"{self.dash} Added by", value=f"{self.reply} {executor}"
                    )
                    embed.add_field(
                        name=f"{self.dash} Actions taken:",
                        value=f"{self.reply} {pment}",
                        inline=True,
                    )
                    await self.bot.get_channel(log).send(embed=embed)

                else:
                    pass
        except:
            pass

        # try:
        #    x = utils.read_json('joinlock')[str(member.guild.id)]['enabled']
        #    if x == 'yes':
        #        jl = True
        #    if x == 'no':
        #        jl = False
        # except Exception as e:
        #    print(f"error {e}")
        #    jl = False

        # if jl == True:
        #    try:
        #        await member.kick(reason=f"joinlock is enabled")
        #    except:
        #        pass
        # else:
        #    pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):

        async for logs in member.guild.audit_logs(
            limit=1, action=discord.AuditLogAction.ban
        ):
            target = member
        db = utils.read_json("restore")
        try:
            db[str(target.guild.id)][str(target.id)] = [
                role.id async for role in utils.aiter(target.roles[1:])
            ]
            utils.write_json(db, "restore")
        except:
            db[str(target.guild.id)] = {}
            db[str(target.guild.id)][str(target.id)] = [
                role.id async for role in utils.aiter(target.roles[1:])
            ]
            utils.write_json(db, "restore")

        try:
            async for logs in guild.audit_logs(
                limit=1, action=discord.AuditLogAction.ban
            ):
                executor = await guild.fetch_member(logs.user.id)
                target = member
                antireason = logs.reason

            reason = "vile antinuke: anti ban is enabled"
            anti = utils.read_json("antinuke")[str(guild.id)]
            try:
                modlogs = utils.read_json("modlog")[str(guild.id)]

                embed = discord.Embed(color=self.warning, timestamp=datetime.now())
                embed.set_footer(
                    text=f"Vile Mod-Logs",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name="Modlog Entry", icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Information",
                    value=f"{self.reply} action: **ban**\n{self.reply} user: **{target}** ( `{target.id}` )\n{self.reply} moderator: **{executor}** ( `{executor.id}` )\n{self.reply} reason: **{'no reason' if not antireason else antireason}**",
                )
                await self.bot.get_channel(modlogs).send(embed=embed)
            except:
                pass

            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["ban"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    await executor.ban(reason=reason)
                    try:
                        await executor.send(
                            f"{self.dash} you were banned from **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "kick":

                    await executor.kick(reason=reason)
                    try:
                        await executor.send(
                            f"{self.dash} you were kicked from **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "strip":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were stripped from your roles in **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "jail":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were jailed in **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    role = discord.utils.get(guild.roles, name="jailed")
                    if not role:
                        await guild.create_role(name="jailed")

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    jail = discord.utils.get(guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    async for channel in utils.aiter(guild.channels):
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor, overwrite=perms)

                    role = discord.utils.get(guild.roles, name="jailed")
                    await executor.add_roles(role, reason=reason)
                await guild.unban(member)
                log = utils.read_json("antinuke")[str(member.guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning, title=f"Member Banned", timestamp=datetime.now()
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=target, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Banned by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                return

        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        try:
            async for logs in member.guild.audit_logs(
                limit=1,
                after=datetime.now().astimezone() - timedelta(seconds=5),
                action=discord.AuditLogAction.kick,
            ):
                target = member
            db = utils.read_json("restore")
            try:
                db[str(target.guild.id)][str(target.id)] = [
                    role.id async for role in utils.aiter(target.roles[1:])
                ]
                utils.write_json(db, "restore")
            except:
                db[str(target.guild.id)] = {}
                db[str(target.guild.id)][str(target.id)] = [
                    role.id async for role in utils.aiter(target.roles[1:])
                ]
                utils.write_json(db, "restore")
        except:
            pass

        try:
            x = utils.read_json("antinuke")[str(member.guild.id)]["whitelisted"]
            x.remove(member.id)
        except:
            pass

        try:
            async for logs in member.guild.audit_logs(
                limit=1, action=discord.AuditLogAction.kick
            ):
                executor = await member.guild.fetch_member(logs.user.id)
                target = member
                antireason = logs.reason

            reason = "vile antinuke: anti kick is enabled"
            anti = utils.read_json("antinuke")[str(member.guild.id)]
            try:
                modlogs = utils.read_json("modlog")[str(member.guild.id)]

                embed = discord.Embed(color=self.warning, timestamp=datetime.now())
                embed.set_footer(
                    text=f"Vile Mod-Logs",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name="Modlog Entry", icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Information",
                    value=f"{self.reply} action: **kick**\n{self.reply} user: **{target}** ( `{target.id}` )\n{self.reply} moderator: **{executor}** ( `{executor.id}` )\n{self.reply} reason: **{'no reason' if not antireason else antireason}**",
                )
                await self.bot.get_channel(modlogs).send(embed=embed)
            except:
                pass

            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["kick"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    await executor.ban(reason=reason)
                    try:
                        await executor.send(
                            f"{self.dash} you were banned from **{member.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "kick":

                    await executor.kick(reason=reason)
                    try:
                        await executor.send(
                            f"{self.dash} you were kicked from **{member.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "strip":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were stripped from your roles in **{member.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "jail":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were jailed in **{member.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    role = discord.utils.get(member.guild.roles, name="jailed")
                    if not role:
                        await member.guild.create_role(name="jailed")

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    jail = discord.utils.get(member.guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                member.guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                member.guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await member.guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    async for channel in utils.aiter(member.guild.channels):
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor, overwrite=perms)

                    role = discord.utils.get(member.guild.roles, name="jailed")
                    await executor.add_roles(role, reason=reason)

                log = utils.read_json("antinuke")[str(member.guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning, title=f"Member Kicked", timestamp=datetime.now()
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=target, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Kicked by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                return

        except:
            pass

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        try:
            async for logs in channel.guild.audit_logs(
                limit=1, action=discord.AuditLogAction.channel_create
            ):
                executor = await channel.guild.fetch_member(logs.user.id)

            reason = "vile antinuke: anti channel create is enabled"
            anti = utils.read_json("antinuke")[str(channel.guild.id)]

            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["channelcreate"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    await executor.ban(reason=reason)
                    try:
                        await executor.send(
                            f"{self.dash} you were banned from **{channel.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "kick":

                    await executor.kick(reason=reason)
                    try:
                        await executor.send(
                            f"{self.dash} you were kicked from **{channel.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "strip":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were stripped from your roles in **{channel.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "jail":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were jailed in **{channel.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    role = discord.utils.get(channel.guild.roles, name="jailed")
                    if not role:
                        await channel.guild.create_role(name="jailed")

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    jail = discord.utils.get(channel.guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                channel.guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                channel.guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await channel.guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    for channel in channel.guild.channels:
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor, overwrite=perms)

                    role = discord.utils.get(channel.guild.roles, name="jailed")
                    await executor.add_roles(role, reason=reason)

                await channel.delete()
                log = utils.read_json("antinuke")[str(channel.guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning,
                    title=f"Channel Created",
                    timestamp=datetime.now(),
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=executor, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Created by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                return
        except:
            pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        try:
            async for logs in channel.guild.audit_logs(
                limit=1, action=discord.AuditLogAction.channel_delete
            ):
                executor = await channel.guild.fetch_member(logs.user.id)

            reason = "vile antinuke: anti channel delete is enabled"
            anti = utils.read_json("antinuke")[str(channel.guild.id)]
            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["channeldelete"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    await executor.ban(reason=reason)
                    try:
                        await executor.send(
                            f"{self.dash} you were banned from **{channel.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "kick":

                    await executor.kick(reason=reason)
                    try:
                        await executor.send(
                            f"{self.dash} you were kicked from **{channel.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "strip":

                    try:
                        await executor.send(
                            f"{self.dash} you were stripped from your roles in **{channel.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.edit(roles=[])

                elif pment == "jail":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were jailed in **{channel.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    role = discord.utils.get(channel.guild.roles, name="jailed")
                    if not role:
                        await channel.guild.create_role(name="jailed")

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    jail = discord.utils.get(channel.guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                channel.guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                channel.guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await channel.guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    for channel in channel.guild.channels:
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor, overwrite=perms)

                    role = discord.utils.get(channel.guild.roles, name="jailed")
                    await executor.add_roles(role, reason=reason)
                await channel.clone(name=channel.name)
                log = utils.read_json("antinuke")[str(channel.guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning,
                    title=f"Channel Deleted",
                    timestamp=datetime.now(),
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=executor, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Deleted by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                return
        except:
            pass

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):

        try:
            async for logs in role.guild.audit_logs(
                limit=1, action=discord.AuditLogAction.role_create
            ):
                executor = await role.guild.fetch_member(logs.user.id)

            reason = "vile antinuke: anti role create is enabled"
            anti = utils.read_json("antinuke")[str(role.guild.id)]
            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["rolecreate"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    try:
                        await executor.send(
                            f"{self.dash} you were banned from **{role.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.ban(reason=reason)

                elif pment == "kick":

                    try:
                        await executor.send(
                            f"{self.dash} you were kicked from **{role.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.kick(reason=reason)

                elif pment == "strip":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were stripped from your roles in **{role.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass

                elif pment == "jail":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were jailed in **{role.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    rr = discord.utils.get(role.guild.roles, name="jailed")
                    if not rr:
                        await role.guild.create_role(name="jailed")

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    jail = discord.utils.get(role.guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                role.guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                role.guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await role.guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    for channel in role.guild.channels:
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor, overwrite=perms)

                    rr = discord.utils.get(role.guild.roles, name="jailed")
                    await executor.add_roles(rr, reason=reason)
                await role.delete()
                log = utils.read_json("antinuke")[str(channel.guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning, title=f"Role Created", timestamp=datetime.now()
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=executor, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Created by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                return
        except:
            pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):

        try:
            async for logs in role.guild.audit_logs(
                limit=1, action=discord.AuditLogAction.role_delete
            ):
                executor = await role.guild.fetch_member(logs.user.id)

            reason = "vile antinuke: anti role delete is enabled"
            anti = utils.read_json("antinuke")[str(role.guild.id)]
            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["roledelete"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    try:
                        await executor.send(
                            f"{self.dash} you were banned from **{role.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.ban(reason=reason)

                elif pment == "kick":

                    try:
                        await executor.send(
                            f"{self.dash} you were kicked from **{role.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.kick(reason=reason)

                elif pment == "strip":

                    try:
                        await executor.send(
                            f"{self.dash} you were stripped from your roles in **{role.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.edit(roles=[])

                elif pment == "jail":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were jailed in **{role.guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    rr = discord.utils.get(role.guild.roles, name="jailed")
                    if not rr:
                        await role.guild.create_role(name="jailed")

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    jail = discord.utils.get(role.guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                role.guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                role.guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await role.guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    for channel in role.guild.channels:
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor, overwrite=perms)

                    rr = discord.utils.get(role.guild.roles, name="jailed")
                    await executor.add_roles(rr, reason=reason)
                await role.guild.create_role(
                    name=role.name,
                    color=role.color,
                    hoist=role.hoist,
                    mentionable=role.mentionable,
                    permissions=role.permissions,
                    display_icon=role.display_icon,
                )
                log = utils.read_json("antinuke")[str(channel.guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning, title=f"Role Deleted", timestamp=datetime.now()
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=executor, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Deleted by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                return
        except:
            pass

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):

        try:
            guild = after
            async for logs in guild.audit_logs(
                limit=1, action=discord.AuditLogAction.guild_update
            ):
                executor = await guild.fetch_member(logs.user.id)

            reason = "vile antinuke: anti guild update is enabled"
            anti = utils.read_json("antinuke")[str(guild.id)]

            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["guild"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    try:
                        await executor.send(
                            f"{self.dash} you were banned from **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.ban(reason=reason)

                elif pment == "kick":

                    try:
                        await executor.send(
                            f"{self.dash} you were kicked from **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.kick(reason=reason)

                elif pment == "strip":

                    try:
                        await executor.send(
                            f"{self.dash} you were stripped from your roles in **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.edit(roles=[])

                elif pment == "jail":

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were jailed in **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    role = discord.utils.get(guild.roles, name="jailed")
                    if not role:
                        await guild.create_role(name="jailed")

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    jail = discord.utils.get(guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    async for channel in utils.aiter(guild.channels):
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor, overwrite=perms)

                    role = discord.utils.get(guild.roles, name="jailed")
                    await executor.add_roles(role, reason=reason)

                bg = before
                await guild.edit(
                    name=bg.name,
                    description=bg.description,
                    afk_channel=bg.afk_channel,
                    afk_timeout=bg.afk_timeout,
                    default_notifications=bg.default_notifications,
                    verification_level=bg.verification_level,
                    explicit_content_filter=bg.explicit_content_filter,
                    system_channel=bg.system_channel,
                    system_channel_flags=bg.system_channel_flags,
                    preferred_locale=bg.preferred_locale,
                    rules_channel=bg.rules_channel,
                    public_updates_channel=bg.public_updates_channel,
                    premium_progress_bar_enabled=bg.premium_progress_bar_enabled,
                )
                try:
                    await guild.edit(vanity_code=bg.vanity_url_code)
                except:
                    pass
                log = utils.read_json("antinuke")[str(guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning, title=f"Guild Updated", timestamp=datetime.now()
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=executor, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Updated by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                pass
        except:
            pass

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):

        try:
            guild = channel.guild
            async for logs in guild.audit_logs(
                limit=1,
                after=(datetime.now() - timedelta(seconds=3)),
                action=discord.AuditLogAction.webhook_create,
            ):
                executor = await guild.fetch_member(logs.user.id)

            reason = "vile antinuke: anti webhook spam is enabled"
            anti = utils.read_json("antinuke")[str(guild.id)]
            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["webhook"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    try:
                        await executor.send(
                            f"{self.dash} you were banned from **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.ban(reason=reason)

                elif pment == "kick":

                    try:
                        await executor.send(
                            f"{self.dash} you were kicked from **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.kick(reason=reason)

                elif pment == "strip":

                    try:
                        await executor.send(
                            f"{self.dash} you were stripped from your roles in **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    await executor.edit(roles=[])

                elif pment == "jail":

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    await executor.edit(roles=[])
                    try:
                        await executor.send(
                            f"{self.dash} you were jailed in **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    role = discord.utils.get(guild.roles, name="jailed")
                    if not role:
                        await guild.create_role(name="jailed")

                    jail = discord.utils.get(guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    async for channel in utils.aiter(guild.channels):
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor, overwrite=perms)

                    role = discord.utils.get(guild.roles, name="jailed")
                    await executor.add_roles(role, reason=reason)

                log = utils.read_json("antinuke")[str(channel.guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning,
                    title=f"Webhook Created",
                    timestamp=datetime.now(),
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=executor, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Created by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                return

            async for logs2 in guild.audit_logs(
                limit=1,
                after=(datetime.now() - timedelta(seconds=3)),
                action=discord.AuditLogAction.webhook_delete,
            ):
                executor2 = await guild.fetch_member(logs2.user.id)

            reason2 = "vile antinuke: anti webhook spam is enabled"
            anti = utils.read_json("antinuke")[str(guild.id)]
            if (
                executor.id != anti["owner"]
                and executor.id not in anti["whitelisted"]
                and executor.id != self.bot.user.id
                and anti["state"] == "enabled"
                and anti["webhook"] == "on"
            ):

                punishments = ["ban", "kick", "strip", "jail"]
                pment = anti["punishment"]
                if pment == "ban":

                    try:
                        await executor2.send(
                            f"{self.dash} you were banned from **{guild.name}**\n{self.reply} **{reason2}**"
                        )
                    except:
                        pass
                    await executor2.ban(reason=reason2)

                elif pment == "kick":

                    try:
                        await executor2.send(
                            f"{self.dash} you were kicked from **{guild.name}**\n{self.reply} **{reason2}**"
                        )
                    except:
                        pass
                    await executor2.kick(reason=reason2)

                elif pment == "strip":

                    try:
                        await executor2.send(
                            f"{self.dash} you were stripped from your roles in **{guild.name}**\n{self.reply} **{reason2}**"
                        )
                    except:
                        pass
                    await executor2.edit(roles=[])

                elif pment == "jail":

                    await executor2.edit(roles=[])
                    try:
                        await executor2.send(
                            f"{self.dash} you were jailed in **{guild.name}**\n{self.reply} **{reason}**"
                        )
                    except:
                        pass
                    role = discord.utils.get(guild.roles, name="jailed")
                    if not role:
                        await guild.create_role(name="jailed")

                    db = utils.read_json("jail")
                    try:
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")
                    except:
                        db[str(executor.guild.id)] = {}
                        db[str(executor.guild.id)][str(executor.id)] = [
                            role.id async for role in utils.aiter(executor.roles[1:])
                        ]
                        utils.write_json(db, "jail")

                    jail = discord.utils.get(guild.text_channels, name="jail")
                    if not jail:
                        try:
                            overwrites = {
                                guild.default_role: discord.PermissionOverwrite(
                                    read_messages=False, send_messages=False
                                ),
                                guild.me: discord.PermissionOverwrite(
                                    read_messages=True
                                ),
                            }
                            jail = await guild.create_text_channel(
                                "jail", overwrites=overwrites
                            )
                        except discord.Forbidden:
                            return

                    async for channel in utils.aiter(guild.channels):
                        if channel.name == "jail":
                            perms = channel.overwrites_for(executor2)
                            perms.send_messages = True
                            perms.read_messages = True
                            await channel.set_permissions(executor2, overwrite=perms)
                        else:
                            perms = channel.overwrites_for(executor2)
                            perms.send_messages = False
                            perms.read_messages = False
                            perms.view_channel = False
                            await channel.set_permissions(executor2, overwrite=perms)

                    role = discord.utils.get(guild.roles, name="jailed")
                    await executor2.add_roles(role, reason=reason2)

                log = utils.read_json("antinuke")[str(channel.guild.id)]["logchannel"]

                embed = discord.Embed(
                    color=self.warning,
                    title=f"Webhook Deleted",
                    timestamp=datetime.now(),
                )
                embed.set_footer(
                    text=f"Vile Anti-Nuke",
                    icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                )
                embed.set_author(name=executor, icon_url=executor.display_avatar)
                embed.add_field(
                    name=f"{self.dash} Deleted by", value=f"{self.reply} {executor}"
                )
                embed.add_field(
                    name=f"{self.dash} Actions taken:",
                    value=f"{self.reply} {pment}",
                    inline=True,
                )
                await self.bot.get_channel(log).send(embed=embed)

            else:
                return
        except:
            pass


async def setup(bot):
    await bot.add_cog(antinukeEvents(bot))
