import discord, datetime, difflib, typing
from discord.ext import tasks, commands
from discord import Embed, Role
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils
from typing import Literal, Optional, Union



class mod(commands.Cog):
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

    @commands.hybrid_command(aliases=["deport"], usage="ban (user) [reason]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild, wait=True)
    @commands.bot_has_permissions(ban_members=True)
    @utils.perms("ban_members")
    async def ban(self, ctx, user: discord.Member = None, *, reason: str = None):
        if not user:
            e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e.set_footer(
                text="moderation",
                icon_url=None,
            )
            e.set_author(name="ban", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{self.dash} Info",
                value=f"{self.reply} **description:** bans the mentioned user\n{self.reply} **aliases:** ban, deport",
                inline=False,
            )
            e.add_field(
                name=f"{self.dash} Usage",
                value=f"{self.reply} syntax: ;ban <user> <reason>\n{self.reply} example: ;ban {ctx.author.name} breaking rules",
                inline=False,
            )
            return await ctx.reply(embed=e)

        if user == ctx.author:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** you can't **ban** yourself",
                )
            )
        elif user not in ctx.guild.members:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** provide a **valid** username",
                )
            )

        truereason = None
        banmsg = ""
        if not reason:
            reason = f"ban: used by {ctx.author}"
        else:
            truereason = reason
            reason = f'"{reason}" used by {ctx.author}'

        try:
            msg = utils.read_json("banmessage")[str(ctx.guild.id)]
            mod = ctx.author
            guild = ctx.guild
            if not truereason:
                r = "no reason"
                msg = msg.format(reason=r, user=user, guild=guild, mod=mod)
            else:
                r = truereason
                msg = msg.format(reason=r, user=user, guild=guild, mod=mod)
        except:
            msg = ":thumbsup:"

        dm = f"you were banned in **{ctx.guild.name}** for {'no reason' if not truereason else truereason}"

        banned = False
        try:
            await user.ban(reason=reason)
            banned = True
        except:
            banned = False
        try:
            if banned == True:
                await user.send(dm)
                dmed = True
        except:
            dmed = False
            pass
        if banned != False:
            await ctx.reply(msg)
            await ctx.send(
                "unable to dm user :thumbsdown:"
            ) if dmed == False else print("")
        else:
            pass

    @commands.command(
        name="unban",
        usage="unban (user) <reason>",
        aliases=["ub"],
    )
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        ctx,
        user: discord.User,
        *,
        reason: str = "No reason provided",
    ):

        try:
            await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
        except discord.NotFound:
            await ctx.warn(f"Unable to find a ban for **{user}**")
        except discord.Forbidden:
            await ctx.warn(f"I don't have **permissions** to unban **{user}**")
        else:
            await self.invoke_message(ctx, ctx.check, user=user, reason=reason)
            await self.moderation_entry(ctx, user, "unban", reason)

    @commands.hybrid_group(aliases=["c"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def purge(self, ctx, amount: int = None):
        ex = discord.Embed(color=0x4c5264, timestamp=datetime.now())

        ex.set_author(name="purge", icon_url=self.bot.user.display_avatar)

        ex.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** purge msgs in a channel\n{self.reply} **aliases:** clear, p, c\n{utils.read_json('emojis')['dash']} **sub commands:** user, bots, files, mention, link, invite, match",
        )

        ex.add_field(
            name="Sub Cmds",
            value="```YAML\n;purge <amount> - purge messages from a channel\n;purge user <@member> <amount> - purge messages from a user\n;purge mentions <amount> - purge role & user mentions\n;purge bots <amount> - purge messages from bots\n;purge files <amount> - purge files & attachments\n;purge links/embeds <amount> - purge links & embeds\n;purge invites <amount> - purge discord invites\n;purge match (word) <amount> - purge messages matching the word/substring\n\n```",
            inline=False,
        )

        ex.set_footer(
            text="Moderation",
            icon_url=None,
        )

        try:
            if not amount:
                return await ctx.reply(embed=ex)
            if amount > 100000:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cant purge more than **100,000** msgs",
                    )
                )
            if amount == 0:
                await ctx.message.delete(limit=1)
                return await ctx.send(f":thumbsup:", delete_after=5)
            # await ctx.message.delete()
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f":thumbsup:", delete_after=5)
        except Exception as e:
            return await ctx.send(embed=ex)

    @purge.command(name="user")
    #
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def purge_user(self, ctx, user: discord.Member = None, amount: int = None):
        ex = discord.Embed(color=0x4c5264, timestamp=datetime.now())

        ex.set_author(name="purge", icon_url=self.bot.user.display_avatar)

        ex.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** purge msgs in a channel\n{self.reply} **aliases:** clear, p, c\n{utils.read_json('emojis')['dash']} **sub commands:** user, bots, files, mention, link, invite, match",
        )

        ex.add_field(
            name="Sub Cmds",
            value="```YAML\n;purge <amount> - purge messages from a channel\n;purge user <@member> <amount> - purge messages from a user\n;purge mentions <amount> - purge role & user mentions\n;purge bots <amount> - purge messages from bots\n;purge files <amount> - purge files & attachments\n;purge links/embeds <amount> - purge links & embeds\n;purge invites <amount> - purge discord invites\n;purge match (word) <amount> - purge messages matching the word/substring\n\n```",
            inline=False,
        )

        ex.set_footer(
            text="moderation",
            icon_url=None,
        )

        try:
            if not amount:
                return await ctx.reply(embed=ex)
            if amount > 100000:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cant purge more than **100,000** msgs",
                    )
                )
            msgs = 0
            async for message in ctx.channel.history(limit=100):
                msgs += 1
            if amount in [0, 1]:
                await ctx.message.delete()
                return await ctx.send(
                    f"{utils.read_json('emojis')['done']} purged `0/{msgs}` msgs",
                    delete_after=5,
                )
            await ctx.message.delete()
            amount = amount if amount <= msgs else msgs
            await ctx.channel.purge(limit=amount, check=lambda m: m.author == user)
            await ctx.send(
                f"{utils.read_json('emojis')['done']} purged `{amount}/{msgs}` msgs from {user.name}",
                delete_after=5,
            )
        except Exception as e:
            return await ctx.send(embed=ex)

    @purge.command(name="bots")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def purge_bots(self, ctx: discord.ext.commands.Context, amount: int = None):
        try:
            ex = discord.Embed(color=0x4c5264, timestamp=datetime.now())

            ex.set_author(
                name="purge",
                icon_url=None,
            )

            ex.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** purge msgs in a channel\n{self.reply} **aliases:** clear, p, c\n{utils.read_json('emojis')['dash']} **sub commands:** user, bots, files, mention, link, invite, match",
            )

            ex.add_field(
                name="Sub Cmds",
                value="```YAML\n;purge <amount> - purge messages from a channel\n;purge user <@member> <amount> - purge messages from a user\n;purge mentions <amount> - purge role & user mentions\n;purge bots <amount> - purge messages from bots\n;purge files <amount> - purge files & attachments\n;purge links/embeds <amount> - purge links & embeds\n;purge invites <amount> - purge discord invites\n;purge match (word) <amount> - purge messages matching the word/substring\n\n```",
                inline=False,
            )

            ex.set_footer(
                text="moderation",
                icon_url=None,
            )

            try:
                if not amount:
                    return await ctx.reply(embed=ex)
                if amount > 100000:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=self.error,
                            description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cant purge more than **100,000** msgs",
                        )
                    )
                msgs = 0
                async for message in ctx.channel.history(limit=100):
                    msgs += 1
                if amount in [0, 1]:
                    await ctx.message.delete()
                    return await ctx.send(
                        f"{utils.read_json('emojis')['done']} purged `0/{msgs}` msgs",
                        delete_after=5,
                    )
                await ctx.message.delete()
                amount = amount if amount <= msgs else msgs
                await ctx.channel.purge(limit=amount, check=lambda m: m.author.bot)
                await ctx.send(
                    f"{utils.read_json('emojis')['done']} purged `{amount}/{msgs}` msgs from bots",
                    delete_after=5,
                )
            except Exception as e:
                return await ctx.send(embed=ex)
        except:
            pass

    @purge.command(name="files", aliases=["images", "imgs", "image", "pics", "pic"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def purge_files(self, ctx, amount: int = None):
        ex = discord.Embed(color=0x4c5264, timestamp=datetime.now())

        ex.set_author(name="purge", icon_url=self.bot.user.display_avatar)

        ex.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** purge msgs in a channel\n{self.reply} **aliases:** clear, p, c\n{utils.read_json('emojis')['dash']} **sub commands:** user, bots, files, mention, link, invite, match",
        )

        ex.add_field(
            name="Sub Cmds",
            value="```YAML\n;purge <amount> - purge messages from a channel\n;purge user <@member> <amount> - purge messages from a user\n;purge mentions <amount> - purge role & user mentions\n;purge bots <amount> - purge messages from bots\n;purge files <amount> - purge files & attachments\n;purge links/embeds <amount> - purge links & embeds\n;purge invites <amount> - purge discord invites\n;purge match (word) <amount> - purge messages matching the word/substring\n\n```",
            inline=False,
        )

        ex.set_footer(
            text="moderation",
            icon_url=None,
        )

        try:
            if not amount:
                return await ctx.reply(embed=ex)
            if amount > 100000:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cant purge more than **100,000** msgs",
                    )
                )
            msgs = 0
            async for message in ctx.channel.history(limit=100):
                msgs += 1
            if amount in [0, 1]:
                await ctx.message.delete()
                return await ctx.send(
                    f"{utils.read_json('emojis')['done']} purged `0/{msgs}` msgs",
                    delete_after=5,
                )
            await ctx.message.delete()
            amount = amount if amount <= msgs else msgs
            await ctx.channel.purge(limit=amount, check=lambda m: m.attachments)
            await ctx.send(
                f"{utils.read_json('emojis')['done']} purged `{amount}/{msgs}` msgs with files",
                delete_after=5,
            )
        except Exception as e:
            return await ctx.send(embed=ex)

    @purge.command(name="mentions")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def purge_mentions(self, ctx, amount: int = None):
        ex = discord.Embed(color=0x4c5264, timestamp=datetime.now())

        ex.set_author(name="purge", icon_url=self.bot.user.display_avatar)

        ex.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** purge msgs in a channel\n{self.reply} **aliases:** clear, p, c\n{utils.read_json('emojis')['dash']} **sub commands:** user, bots, files, mention, link, invite, match",
        )

        ex.add_field(
            name="Sub Cmds",
            value="```YAML\n;purge <amount> - purge messages from a channel\n;purge user <@member> <amount> - purge messages from a user\n;purge mentions <amount> - purge role & user mentions\n;purge bots <amount> - purge messages from bots\n;purge files <amount> - purge files & attachments\n;purge links/embeds <amount> - purge links & embeds\n;purge invites <amount> - purge discord invites\n;purge match (word) <amount> - purge messages matching the word/substring\n\n```",
            inline=False,
        )

        ex.set_footer(
            text="moderation",
            icon_url=None,
        )

        try:
            if not amount:
                return await ctx.reply(embed=ex)
            if amount > 100000:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cant purge more than **100,000** msgs",
                    )
                )
            msgs = 0
            async for message in ctx.channel.history(limit=100):
                msgs += 1
            if amount in [0, 1]:
                await ctx.message.delete()
                return await ctx.send(
                    f"{utils.read_json('emojis')['done']} purged `0/{msgs}` msgs",
                    delete_after=5,
                )
            await ctx.message.delete()
            amount = amount if amount <= msgs else msgs
            await ctx.channel.purge(limit=amount, check=lambda m: m.mentions)
            await ctx.send(
                f"{utils.read_json('emojis')['done']} purged `{amount}/{msgs}` msgs with mentions",
                delete_after=5,
            )
        except Exception as e:
            return await ctx.send(embed=ex)

    @purge.command(name="link", aliases=["embeds", "links"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def purge_link(self, ctx, amount: int = None):
        ex = discord.Embed(color=0x4c5264, timestamp=datetime.now())

        ex.set_author(name="purge", icon_url=self.bot.user.display_avatar)

        ex.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** purge msgs in a channel\n{self.reply} **aliases:** clear, p, c\n{utils.read_json('emojis')['dash']} **sub commands:** user, bots, files, mention, link, invite, match",
        )

        ex.add_field(
            name="Sub Cmds",
            value="```YAML\n;purge <amount> - purge messages from a channel\n;purge user <@member> <amount> - purge messages from a user\n;purge mentions <amount> - purge role & user mentions\n;purge bots <amount> - purge messages from bots\n;purge files <amount> - purge files & attachments\n;purge links/embeds <amount> - purge links & embeds\n;purge invites <amount> - purge discord invites\n;purge match (word) <amount> - purge messages matching the word/substring\n\n```",
            inline=False,
        )

        ex.set_footer(
            text="moderation",
            icon_url=None,
        )

        try:
            if not amount:
                return await ctx.reply(embed=ex)
            if amount > 100000:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cant purge more than **100,000** msgs",
                    )
                )
            msgs = 0
            async for message in ctx.channel.history(limit=100):
                msgs += 1
            if amount in [0, 1]:
                await ctx.message.delete()
                return await ctx.send(
                    f"{utils.read_json('emojis')['done']} purged `0/{msgs}` msgs",
                    delete_after=5,
                )
            await ctx.message.delete()
            amount = amount if amount <= msgs else msgs
            await ctx.channel.purge(
                limit=amount, check=lambda m: m.embeds or "https://" in m.content
            )
            await ctx.send(
                f"{utils.read_json('emojis')['done']} purged `{amount}/{msgs}` msgs with links/embeds",
                delete_after=5,
            )
        except Exception as e:
            return await ctx.send(embed=ex)

    @purge.command(name="invite", aliases=["invites"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def purge_invite(self, ctx, amount: int = None):
        ex = discord.Embed(color=0x4c5264, timestamp=datetime.now())

        ex.set_author(name="purge", icon_url=self.bot.user.display_avatar)

        ex.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** purge msgs in a channel\n{self.reply} **aliases:** clear, p, c\n{utils.read_json('emojis')['dash']} **sub commands:** user, bots, files, mention, link, invite, match",
        )

        ex.add_field(
            name="Sub Cmds",
            value="```YAML\n;purge <amount> - purge messages from a channel\n;purge user <@member> <amount> - purge messages from a user\n;purge mentions <amount> - purge role & user mentions\n;purge bots <amount> - purge messages from bots\n;purge files <amount> - purge files & attachments\n;purge links/embeds <amount> - purge links & embeds\n;purge invites <amount> - purge discord invites\n;purge match (word) <amount> - purge messages matching the word/substring\n\n```",
            inline=False,
        )

        ex.set_footer(
            text="moderation",
            icon_url=None,
        )

        try:
            if not amount:
                return await ctx.reply(embed=ex)
            if amount > 100000:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cant purge more than **100,000** msgs",
                    )
                )
            msgs = 0
            async for message in ctx.channel.history(limit=100):
                msgs += 1
            if amount in [0, 1]:
                await ctx.message.delete()
                return await ctx.send(
                    f"{utils.read_json('emojis')['done']} purged `0/{msgs}` msgs",
                    delete_after=5,
                )
            await ctx.message.delete()
            amount = amount if amount <= msgs else msgs
            await ctx.channel.purge(
                limit=amount,
                check=lambda m: "discord.gg/" in m.content
                or "discord.com/invite/" in m.content,
            )
            await ctx.send(
                f"{utils.read_json('emojis')['done']} purged `{amount}/{msgs}` msgs with invites",
                delete_after=5,
            )
        except Exception as e:
            return await ctx.send(embed=ex)

    @purge.command(name="match", aliases=["matches"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.perms("manage_messages")
    async def purge_match(self, ctx, word: str = None, amount: int = None):
        ex = discord.Embed(color=0x4c5264, timestamp=datetime.now())

        ex.set_author(name="purge", icon_url=self.bot.user.display_avatar)

        ex.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** purge msgs in a channel\n{self.reply} **aliases:** clear, p, c\n{utils.read_json('emojis')['dash']} **sub commands:** user, bots, files, mention, link, invite, match",
        )

        ex.add_field(
            name="Sub Cmds",
            value="```YAML\n;purge <amount> - purge messages from a channel\n;purge user <@member> <amount> - purge messages from a user\n;purge mentions <amount> - purge role & user mentions\n;purge bots <amount> - purge messages from bots\n;purge files <amount> - purge files & attachments\n;purge links/embeds <amount> - purge links & embeds\n;purge invites <amount> - purge discord invites\n;purge match (word) <amount> - purge messages matching the word/substring\n\n```",
            inline=False,
        )

        ex.set_footer(
            text="moderation",
            icon_url=None,
        )

        try:
            if not amount:
                return await ctx.reply(embed=ex)
            if amount > 100000:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cant purge more than **100,000** msgs",
                    )
                )
            msgs = 0
            async for message in ctx.channel.history(limit=100):
                msgs += 1
            if amount in [0, 1]:
                await ctx.message.delete()
                return await ctx.reply(
                    f"{utils.read_json('emojis')['done']} purged `0/{msgs}` msgs",
                    delete_after=5,
                )
            await ctx.message.delete()
            amount = amount if amount <= msgs else msgs
            await ctx.channel.purge(
                limit=amount, check=lambda m: word.lower() in m.content.lower()
            )
            await ctx.send(
                f"{utils.read_json('emojis')['done']} purged `{amount}/{msgs}` msgs matching `{word}`",
                delete_after=5,
            )
        except Exception as e:
            return await ctx.send(embed=ex)

    @commands.hybrid_command(usage="kick (user) [reason]", aliases=["k"], description = "Kick a user")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild, wait=True)
    @commands.bot_has_permissions(kick_members=True)
    @utils.perms("kick_members")
    async def kick(self, ctx, user: discord.Member = None, *, reason: str = None):
        if not user:
            e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e.set_footer(
                text="moderation",
                icon_url=None,
            )
            e.set_author(name="kick", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** kicks the mentioned user\n{self.reply} **aliases:** kick",
                inline=False,
            )
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ;kick <user> <reason>\n{self.reply} example: ;kick @Claqz",
                inline=False,
            )
            return await ctx.reply(embed=e)

        elif user == ctx.author:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** you can't **kick** yourself",
                )
            )
        elif user not in ctx.guild.members:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** provide a **valid** username",
                )
            )

        truereason = None

        if not reason:
            reason = f"kick: used by {ctx.author}"
        else:
            truereason = reason
            reason = f'"{reason}" - used by {ctx.author}'

        dm = f"you were kicked from **{ctx.guild.name}** for {'no reason' if not truereason else truereason}"

        try:
            await user.send(dm)
            dmed = True
        except:
            dmed = False
            pass

        kicked = False
        try:
            await user.kick(reason=reason)
            kicked = True
        except:
            kicked = False
        if kicked != False:
            await ctx.reply(":thumbsup:")
            await ctx.send(
                "unable to dm user :thumbsdown:"
            ) if dmed == False else print("")
        else:
            await ctx.reply(":thumbsdown:")

    @commands.hybrid_command(name = "jail", description = "Jail a user",aliases=["j", "lockup"], usage = "jail [user] (reason)")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(administrator=True)
    @utils.perms("manage_messages")
    async def jail(self, ctx, user: discord.Member = None):
        if user is None:
            e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e.set_footer(
                text=f"moderation",
                icon_url=None,
            )
            e.set_author(name=f"jail", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** jails the mentioned user\n{self.reply} **aliases:** jail, j, lockup",
                inline=False,
            )
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ;jail <user>\n{self.reply} example: ;jail {ctx.author.name} breaking rules",
                inline=False,
            )
            await ctx.reply(embed=e)

        elif user == ctx.author:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** you can't **jail** yourself",
                )
            )

        elif user.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** user is above you in the **role hierarchy**",
                )
            )

        db = utils.read_json("jail")
        try:
            db[str(ctx.guild.id)][str(user.id)] = [
                role.id async for role in utils.aiter(user.roles[1:])
            ]
            utils.write_json(db, "jail")
        except:
            db[str(ctx.guild.id)] = {}
            utils.write_json(db, "jail")
            db = utils.read_json("jail")
            db[str(ctx.guild.id)][str(user.id)] = [
                role.id async for role in utils.aiter(user.roles[1:])
            ]
            utils.write_json(db, "jail")

        async for role in utils.aiter(user.roles[1:]):
            await user.remove_roles(role, reason=f"jail: used by {ctx.author}")
        role = discord.utils.get(ctx.guild.roles, name="jailed")
        if not role:
            await ctx.guild.create_role(name="jailed")
        role = discord.utils.get(ctx.guild.roles, name="jailed")
        await user.add_roles(role, reason=f"jail: used by {ctx.author}")

        jail = discord.utils.get(ctx.guild.text_channels, name="jail")
        if not jail:
            try:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        read_messages=False, send_messages=False
                    ),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                }
                jail = await ctx.guild.create_text_channel(
                    "jail", overwrites=overwrites
                )
                await ctx.reply(
                    embed=discord.Embed(
                        description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}: **jail** channel binded to {jail.mention}",
                        color=0x85ED91,
                    )
                )
            except discord.Forbidden:
                return

        async for channel in utils.aiter(ctx.guild.channels):
            if channel.name == "jail":
                perms = channel.overwrites_for(user)
                perms.send_messages = True
                perms.read_messages = True
                await channel.set_permissions(user, overwrite=perms)
            else:
                perms = channel.overwrites_for(user)
                perms.send_messages = False
                perms.read_messages = False
                perms.view_channel = False
                await channel.set_permissions(user, overwrite=perms)

        await jail.send(
            content=user.mention,
            embed=discord.Embed(
                description=f"{utils.read_json('emojis')['warn']} {user.mention}: you were **jailed** by {ctx.author.mention}",
                color=self.warning,
            ),
        )
        await ctx.reply(":thumbsup:")

    @commands.hybrid_command(name = "unjail", description = "Jail a user",aliases=["uj", "release"], usage = "unjail [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @utils.perms("manage_messages")
    async def unjail(self, ctx, user: discord.Member = None):
        if user is None:
            e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e.set_footer(
                text=f"moderation",
                icon_url=None,
            )
            e.set_author(name=f"unjail", icon_url=self.clint.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** unjails the mentioned user\n{self.reply} **aliases:** unjail, uj, release",
                inline=False,
            )
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ;unjail <user>\n{self.reply} example: ;unjail {ctx.author.name}",
                inline=False,
            )
            await ctx.reply(embed=e)

        elif user == ctx.author:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** you can't **unjail** yourself",
                )
            )

        elif user.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** user is above you in the **role hierarchy**",
                )
            )

        db = utils.read_json("jail")
        jailrole = discord.utils.get(ctx.guild.roles, name="jailed")
        roles = db[str(ctx.guild.id)][str(user.id)]
        for r in roles:
            role = discord.utils.get(ctx.guild.roles, id=r)
            await user.add_roles(role, reason=f"unjail: used by {ctx.author}")

        async for channel in utils.aiter(ctx.guild.channels):
            if channel.name == "jail":
                perms = channel.overwrites_for(user)
                perms.send_messages = None
                perms.read_messages = None
                await channel.set_permissions(user, overwrite=perms)
            else:
                perms = channel.overwrites_for(user)
                perms.send_messages = None
                perms.read_messages = None
                perms.view_channel = None
                await channel.set_permissions(user, overwrite=perms)

        await user.remove_roles(jailrole, reason=f"unjail: used by {ctx.author}")
        await ctx.reply(":thumbsup:")

    @commands.group(
        name="role", aliases=["arole", "r", "addrole"], invoke_without_command=True
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def role(
        self,
        ctx,
        user: discord.Member = None,
        *,
        role: typing.Union[discord.Role, str] = None,
    ):  # roles: commands.Greedy[discord.Role]=None):
        # if not ctx.invoked_subcommand:
        if user == None:
            from modules import paginator as pg

            e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e.set_author(name="role", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** adds role to a user\n{self.reply} **aliases:** role, ar, arole\n{self.reply} **sub commands:** create, delete, all, bots, humans, withrole",
                inline=False,
            )
            e1 = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e1.set_author(name="role", icon_url=self.bot.user.avatar)
            e1.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** adds role to a user\n{self.reply} **aliases:** role, ar, arole\n{self.reply} **sub commands:** create, delete, all, bots, humans, withrole",
                inline=False,
            )
            e1.add_field(
                name=f"{utils.read_json('emojis')['dash']} Sub Cmds",
                value=f"```YAML\n\n;role (user) <role> - adds role to single user\n;role create (name) #<color> - creates a role\n;role delete <role> - deletes a role\n;role all <role> - adds role to everyone\n;role humans <role> - adds role to all humans\n;role bots <role> - adds role to bots\n;role inrole <inrole> <role> - adds to users having a role\n\n```",
                inline=False,
            )
            e1.set_footer(
                text="moderation - 1/2",
                icon_url=None,
            )
            e2 = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e2.set_author(name="role", icon_url=self.bot.user.avatar)
            e2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** adds role to a user\n{self.reply} **aliases:** role, ar, arole\n{self.reply} **sub commands:** create, delete, all, bots, humans, withrole",
                inline=False,
            )
            e2.add_field(
                name=f"{utils.read_json('emojis')['dash']} Usage",
                value=f"{self.reply} syntax: ;addrole <user> <role>\n{self.reply} example: ;addrole @claqz admin",
                inline=False,
            )
            e2.set_footer(
                text="moderation - 2/2",
                icon_url=None,
            )
            
            paginator = pg.Paginator(self.bot, [e1, e2], ctx, timeout=30, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            return await paginator.start()

        elif role == None:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** role",
                )
            )
        if isinstance(role, discord.Role):
            if ctx.guild.me.top_role.position < role.position:
                return await ctx.send("i cant access that role")  # ; continue
            if ctx.author.top_role.position < role.position:
                return await ctx.send("you cant access that role")  # ; continue

            if user.get_role(role.id) != None:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** user **already** has that role",
                    )
                )
            await user.add_roles(role, reason=f"addrole: used by {ctx.author}")
            await ctx.reply(":thumbsup:")
        if isinstance(role, str):
            roles = [
                role.name.lower()
                async for role in utils.aiter(ctx.guild.roles)
                if role.is_assignable()
            ]
            closest = difflib.get_close_matches(role.lower(), roles, n=3, cutoff=0.5)
            if closest:
                async for r in utils.aiter(ctx.guild.roles):
                    if r.name.lower() == closest[0].lower():
                        rr = r
                if ctx.author.top_role.position < rr.position:
                    return await ctx.send("you cant access that role")  # ; continue
                await user.add_roles(rr, reason=f"addrole: used by {ctx.author}")
                await ctx.reply(":thumbsup:")

    @role.command(name="create")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def role_create(self, ctx, color: str = None, *, name: str = None):
        # if ctx.invoked_subcommand is all:

        if not color or len(color) > 6:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** hex",
                )
            )
        elif not name:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** name",
                )
            )
        else:
            await ctx.guild.create_role(
                name=name, color=eval(f'0x{color.replace("#", "")}')
            )
            await ctx.reply(":thumbsup:")

    @role.command(name="delete")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def role_delete(self, ctx, *, role: typing.Union[discord.Role, str] = None):
        if role == None:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** role",
                )
            )
        if isinstance(role, discord.Role):
            if ctx.author.top_role.position < role.position:
                return await ctx.send("you cant access that role")
            await role.delete()
            await ctx.reply(":thumbsup:")

        if isinstance(role, str):
            roles = [
                r.name.lower()
                async for r in utils.aiter(ctx.guild.roles)
                if r.is_assignable()
            ]
            closest = difflib.get_close_matches(role.lower(), roles, n=3, cutoff=0.5)
            if closest:
                async for r in utils.aiter(ctx.guild.roles):
                    if r.name.lower() == closest[0].lower():
                        rr = r
                if ctx.author.top_role.position < rr.position:
                    return await ctx.send("you cant access that role")
                await rr.delete()
                await ctx.reply(":thumbsup:")

    @role.command(name="all")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def role_all(self, ctx, *, role: typing.Union[discord.Role, str] = None):
        # if ctx.invoked_subcommand is all:

        if role == None:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{self.warn} {ctx.author.mention}**:** please enter a **valid** role",
                )
            )

        if isinstance(role, discord.Role):
            if ctx.guild.me.top_role.position < role.position:
                return await ctx.send("i cant access that role")
            if ctx.author.top_role.position < role.position:
                return await ctx.send("you cant access that role")  # ; continue
            await ctx.message.add_reaction("👍")
            async with ctx.channel.typing():
                async for m in utils.aiter(ctx.guild.members):
                    if role not in m.roles:
                        try:
                            await m.add_roles(
                                role, reason=f"role all: used by {ctx.author}"
                            )
                        except:
                            pass
            await ctx.reply(":thumbsup:")

        if isinstance(role, str):
            roles = [
                r.name.lower()
                async for r in utils.aiter(ctx.guild.roles)
                if r.is_assignable()
            ]
            closest = difflib.get_close_matches(role.lower(), roles, n=3, cutoff=0.5)
            if closest:
                async for r in utils.aiter(ctx.guild.roles):
                    if r.name.lower() == closest[0].lower():
                        rr = r
                if ctx.author.top_role.position < rr.position:
                    return await ctx.send("you cant access that role")
                async for m in utils.aiter(ctx.guild.members):
                    if rr not in m.roles:
                        try:
                            await m.add_role(
                                rr, reason=f"role all: used by {ctx.author}"
                            )
                        except:
                            pass

    @role.command(name="humans")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def role_humans(self, ctx, *, role: typing.Union[discord.Role, str] = None):
        # if ctx.invoked_subcommand is all:
        if role == None:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** role",
                )
            )

        if isinstance(role, discord.Role):
            r = role
            if ctx.guild.me.top_role.position < r.position:
                return await ctx.send("i cant access that role")
            if ctx.author.top_role.position < r.position:
                return await ctx.send("you cant access that role")
            # if user.get_role(role.id) != None:
            # await ctx.reply(embed=discord.Embed(color=0xf3dc6c, description=f"<:sorrow_warning:960170729582772313> {ctx.author.mention}**:** User **already** has that role"))
            # else:
            await ctx.message.add_reaction("👍")
            async with ctx.channel.typing():
                async for m in utils.aiter(ctx.guild.members):
                    if not m.bot:
                        if r not in m.roles:
                            try:
                                await m.add_roles(
                                    r, reason=f"role humans: used by {ctx.author}"
                                )
                            except:
                                pass
            await ctx.reply(":thumbsup:")
        if isinstance(role, str):
            roles = [
                r.name.lower()
                async for r in utils.aiter(ctx.guild.roles)
                if r.is_assignable()
            ]
            closest = difflib.get_close_matches(role.lower(), roles, n=3, cutoff=0.5)
            if closest:
                async for r in utils.aiter(ctx.guild.roles):
                    if r.name.lower() == closest[0].lower():
                        rr = r
                if ctx.author.top_role.position < rr.position:
                    return await ctx.send("you cant access that role")
                async for m in utils.aiter(ctx.guild.members):
                    if not m.bot:
                        if rr not in m.roles:
                            try:
                                await m.add_roles(
                                    rr, reason=f"role humans: used by {ctx.author}"
                                )
                            except:
                                pass
            await ctx.reply(":thumbsup:")
            # await ctx.reply(embed=discord.Embed(color=self.warning, description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** can't find that role"))

    @role.command(name="bots")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def role_bots(self, ctx, *, role: typing.Union[discord.Role, str] = None):
        # if ctx.invoked_subcommand is all:

        if role == None:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** role",
                )
            )

        if isinstance(role, discord.Role):
            if ctx.guild.me.top_role.position < role.position:
                return await ctx.send("i cant access that role")
            if ctx.author.top_role.position < role.position:
                return await ctx.send("you cant access that role")
            await ctx.message.add_reaction("👍")
            async with ctx.channel.typing():
                async for m in utils.aiter(ctx.guild.members):
                    if m.bot:
                        if role not in m.roles:
                            try:
                                await m.add_roles(
                                    role, reason=f"role all: used by {ctx.author}"
                                )
                            except:
                                pass
            await ctx.reply(":thumbsup:")

        if isinstance(role, str):
            if ctx.guild.me.top_role.position < role.position:
                return await ctx.send("i cant access that role")
            roles = [
                r.name.lower()
                async for r in utils.aiter(ctx.guild.roles)
                if role.is_assignable()
            ]
            closest = difflib.get_close_matches(role.lower(), roles, n=3, cutoff=0.5)
            if closest:
                async for r in utils.aiter(ctx.guild.roles):
                    if r.name.lower() == closest[0].lower():
                        rr = r
                if ctx.author.top_role.position < rr.position:
                    return await ctx.send("you cant access that role")
                async for m in utils.aiter(ctx.guild.members):
                    if m.bot:
                        if rr not in m.roles:
                            try:
                                await m.add_roles(
                                    rr, reason=f"role bots: used by {ctx.author}"
                                )
                            except:
                                pass

            await ctx.reply(":thumbsup")

    @role.command(name="inrole", aliases=["withrole"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def role_inrole(
        self, ctx, *, inrole: discord.Role = None, role: discord.Role = None
    ):
        # if ctx.invoked_subcommand is all:

        if role == None:
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** role",
                )
            )

        elif ctx.guild.me.top_role.position < role.position:
            return await ctx.send("i cant access that role")
        else:
            try:
                # if user.get_role(role.id) != None:
                # await ctx.reply(embed=discord.Embed(color=0xf3dc6c, description=f"<:sorrow_warning:960170729582772313> {ctx.author.mention}**:** User **already** has that role"))
                # else:
                await ctx.message.add_reaction("👍")
                async with ctx.channel.typing():
                    async for m in utils.aiter(ctx.guild.members):
                        if m.get_role(inrole.id) != None:
                            try:
                                await m.add_roles(
                                    role, reason=f"role all: used by {ctx.author}"
                                )
                            except:
                                pass
                await ctx.reply(":thumbsup:")

            except Exception as e:
                await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** can't find that role",
                    )
                )

    @commands.group(
        name="removerole", aliases=["rrole", "remove"], invoke_without_command=True
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def removerole(
        self,
        ctx,
        user: discord.Member = None,
        *,
        role: typing.Union[discord.Role, str] = None,
    ):
        if user == None:
            e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e.set_footer(
                text="moderation",
                icon_url=None,
            )
            e.set_author(name="removerole", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** adds role to a user\n{self.reply} **aliases:** role, ar, arole",
                inline=False,
            )
            await ctx.invoke()
            return await ctx.reply(embed=e)

        elif role == None:
            e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
            e.set_footer(
                text="moderation",
                icon_url=None,
            )
            e.set_author(name="removerole", icon_url=self.bot.user.avatar)
            e.add_field(
                name=f"{utils.read_json('emojis')['dash']} Info",
                value=f"{self.reply} **description:** adds role to a user\n{self.reply} **aliases:** role, ar, arole",
                inline=False,
            )
            return await ctx.reply(embed=e)

        if isinstance(role, discord.Role):
            if ctx.guild.me.top_role.position < role.position:
                return await ctx.send("i cant access that role")
            if ctx.author.top_role.position < role.position:
                return await ctx.send("you cant access that role")

            await user.remove_roles(role, reason=f"removerole: used by {ctx.author}")
            await ctx.reply(":thumbsup:")

        if isinstance(role, str):
            roles = [
                r.name.lower()
                async for r in utils.aiter(ctx.guild.roles)
                if r.is_assignable()
            ]
            closest = difflib.get_close_matches(role.lower(), roles, n=3, cutoff=0.5)
            if closest:
                async for r in utils.aiter(ctx.guild.roles):
                    if r.name.lower() == closest[0].lower():
                        rr = r
                if ctx.author.top_role.position < rr.position:
                    return await ctx.send("you cant access that role")

                await user.remove_roles(rr, reason=f"removerole: used by {ctx.author}")
                await ctx.reply(":thumbsup:")

    @removerole.command(name="all")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_roles")
    async def removerole_all(
        self, ctx, *, role: typing.Union[discord.Role, str] = None
    ):
        # if ctx.invoked_subcommand is all:

        if role == None:
            await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please enter a **valid** role",
                )
            )
        if isinstance(role, discord.Role):
            if ctx.guild.me.top_role.position < role.position:
                return await ctx.send("i cant access that role")
            if ctx.author.top_role.position < role.position:
                return await ctx.send("you cant access that role")
            await ctx.message.add_reaction("👍")
            async with ctx.channel.typing():
                async for m in utils.aiter(ctx.guild.members):
                    await m.remove_roles(
                        role, reason=f"removerole all: used by {ctx.author}"
                    )
            await ctx.reply(":thumbsup:")
        if isinstance(role, str):
            roles = [
                role.name.lower()
                async for role in utils.aiter(ctx.guild.roles)
                if role.is_assignable()
            ]
            closest = difflib.get_close_matches(role.lower(), roles, n=3, cutoff=0.5)
            if closest:
                async for r in utils.aiter(ctx.guild.roles):
                    if r.name.lower() == closest[0].lower():
                        rr = r
                if ctx.author.top_role.position < rr.position:
                    return await ctx.send("you cant access that role")

                await ctx.message.add_reaction("👍")
                async with ctx.channel.typing():
                    async for m in utils.aiter(ctx.guild.members):
                        await m.remove_roles(
                            rr, reason=f"removerole all: used by {ctx.author}"
                        )
                await ctx.reply(":thumbsup:")






    @commands.hybrid_command(name = "lock", description = "Locks a channel",aliases=["lockchannel"], usage = "lock")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_channels=True)
    @utils.perms("manage_messages")
    async def lock(self, ctx):
        try:
            overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await ctx.channel.set_permissions(
                ctx.guild.default_role, overwrite=overwrite
            )
            await ctx.reply(":thumbsup:")

        except:
            pass

    @commands.hybrid_command(name = "unlock", description = "Unlocks a channel",aliases=["unlockchannel"], usage = "unlock")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_channels=True)
    @utils.perms("manage_messages")
    async def unlock(self, ctx):
        try:
            overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = True
            await ctx.channel.set_permissions(
                ctx.guild.default_role, overwrite=overwrite
            )
            await ctx.reply(":thumbsup:")

        except:
            pass

    @commands.hybrid_command(name = "slowmode", description = "Put slowmode on a channel",aliases=["sm"], usage = "slowmode [time]")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_channels=True)
    @utils.perms("manage_channels")
    async def slowmode(self, ctx, seconds=None):
        try:
            if not seconds:
                e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
                e.set_footer(
                    text=f"moderation",
                    icon_url=None,
                )
                e.set_author(name=f"slowmode", icon_url=self.bot.user.display_avatar)
                e.add_field(
                    name=f"{utils.read_json('emojis')['dash']} Info",
                    value=f"{self.reply} **description:** change the slowmode for the channel\n{self.reply} **aliases:** slowmode, sm",
                    inline=False,
                )
                e.add_field(
                    name=f"{utils.read_json('emojis')['dash']} Usage",
                    value=f"{self.reply} syntax: ;slowmode <time s>\n{self.reply} example: ;slowmode 5",
                    inline=False,
                )
                return await ctx.reply(embed=e)

            await ctx.channel.edit(slowmode_delay=seconds)
            await ctx.reply(":thumbsup:")
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** please **provide** a mumber under 21,600",
                )
            )

    @commands.hybrid_command(name = "mute", description = "Mutes a user",aliases=["m"], usage = "mute [user] (reason)")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild, wait=True)
    @commands.bot_has_permissions(moderate_members=True)
    @utils.perms("manage_messages")
    async def mute(self, ctx, user: discord.Member = None, time=None):
        try:
            if not user:
                e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
                e.set_footer(
                    text="moderation",
                    icon_url=None,
                )
                e.set_author(name="mute", icon_url=self.bot.user.display_avatar)
                e.add_field(
                    name=f"{utils.read_json('emojis')['dash']} Info",
                    value=f"{self.reply} **description:** mutes the mentioned user\n{self.reply} **aliases:** mute",
                    inline=False,
                )
                e.add_field(
                    name=f"{utils.read_json('emojis')['dash']} Usage",
                    value=f"{self.reply} syntax: ;mute <user> <time d/h/m/s>\n{self.reply} example: ;mute @Claqz 10m",
                    inline=False,
                )
                return await ctx.reply(embed=e)

            elif user == ctx.author:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{self.fail} {ctx.author.mention}**:** don't mute **yourself**, you're too cute to be muted!",
                    )
                )
            elif user not in ctx.guild.members:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** provide a **valid** username",
                    )
                )
            else:
                reason = f"mute: used by {ctx.author}"
                dm = f"you were muted in **{ctx.guild.name}**"

                import humanfriendly

                muted = False
                try:
                    tt = humanfriendly.parse_timespan(time)
                except:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=self.warning,
                            description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** provide a **valid** time for the mute",
                        )
                    )
                if user.timed_out_until != None:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=self.error,
                            description=f"{self.fail} {ctx.author.mention}**:** that user is already muted",
                        )
                    )
                try:
                    await user.edit(
                        timed_out_until=datetime.now().astimezone()
                        + timedelta(seconds=tt),
                        reason=reason,
                    )
                    muted = True
                except:
                    muted = False
                if muted == True:
                    try:
                        await user.send(dm)
                        dmed = True

                    except:
                        dmed = False
                        pass

                if muted != False:
                    await ctx.reply(":thumbsup:")
                    await ctx.send(
                        "unable to dm user :thumbsdown:"
                    ) if dmed == False else print("")
                else:
                    await ctx.reply(":thumbsdown:")
        except:
            pass

    @commands.hybrid_group(name = "unmute", description = "Unmutes a user", aliases=["um"], usage = "unmute [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild, wait=True)
    @commands.bot_has_permissions(moderate_members=True)
    @utils.perms("manage_messages")
    async def unmute(self, ctx, user: discord.Member = None):
        try:
            if not user:
                e = discord.Embed(color=0x4c5264, timestamp=datetime.now())
                e.set_footer(
                    text="moderation",
                    icon_url=None,
                )
                e.set_author(name="unmute", icon_url=self.bot.user.display_avatar)
                e.add_field(
                    name=f"{utils.read_json('emojis')['dash']} Info",
                    value=f"{self.reply} **description:** unmutes the mentioned user\n{self.reply} **aliases:** mute",
                    inline=False,
                )
                e.add_field(
                    name=f"{utils.read_json('emojis')['dash']} Usage",
                    value=f"{self.reply} syntax: ;unmute <user>\n{self.reply} example: ;unmute @Claqz",
                    inline=False,
                )
                return await ctx.reply(embed=e)

            elif user == ctx.author:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** you can't **unmute** yourself",
                    )
                )
            elif user not in ctx.guild.members:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.warning,
                        description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** provide a **valid** username",
                    )
                )
            else:
                reason = f"unmute: used by {ctx.author}"
                dm = f"you were unmuted in **{ctx.guild.name}**"

                try:
                    await user.send(dm)
                    dmed = True
                except:
                    dmed = False
                    pass

                import humanfriendly

                unmuted = False
                if not user.timed_out_until:
                    return await ctx.reply(
                        embed=discord.Embed(
                            color=self.error,
                            description=f"{self.fail} {ctx.author.mention}**:** that user is not muted",
                        )
                    )
                try:
                    await user.edit(timed_out_until=None, reason=reason)
                    unmuted = True
                except:
                    unmuted = False
                if unmuted != False:
                    await ctx.reply(":thumbsup:")
                    await ctx.send(
                        "unable to dm user :thumbsdown:"
                    ) if dmed == False else print("")
                else:
                    await ctx.reply(":thumbsdown:")
        except:
            pass

    @unmute.command(name="all")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @utils.perms("manage_messages")
    async def unmute_all(self, ctx):
        await ctx.typing()
        async for m in utils.aiter(ctx.guild.members):
            if m.timed_out_until:
                await m.edit(
                    timed_out_until=None, reason=f"unmute all: used by {ctx.author}"
                )
        await ctx.reply(":thumbsup:")

    @commands.hybrid_command(name = "restore", description = "Restores a user's roles",aliases=["res"], usage = "Restore [user]")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_roles=True)
    @utils.perms("manage_guild")
    async def restore(self, ctx, user: discord.Member = None):
        if not user:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.warning,
                    description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** provide a **valid** username",
                )
            )
        db = utils.read_json("restore")
        try:
            roles = db[str(ctx.guild.id)][str(user.id)]
            async for r in utils.aiter(roles):
                role = discord.utils.get(ctx.guild.roles, id=r)
                await user.add_roles(role, reason=f"restore: used by {ctx.author}")
            await ctx.reply(":thumbsup:")

        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** no roles to **restore**",
                )
            )

    @commands.command(name = "muted", description = "View all muted users",aliases=["mutedlist"], usage = "mutedlist")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @utils.perms("manage_messages")
    async def muted(self, ctx):
        ret = []
        num = 0
        pagenum = 0
        embeds = []
        async for m in utils.aiter(ctx.guild.members):
            if m.timed_out_until:
                num += 1
                ret.append(f"`{num}` {m.mention} ( `{m.id}` )\n")
        pages = [p async for p in utils.aiter(discord.utils.as_chunks(ret, 10))]
        async for page in utils.aiter(pages):
            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x4c5264,
                    description=" ".join(page),
                    title=f"muted list",
                    timestamp=datetime.now(),
                ).set_footer(
                    text=f"{pagenum}/{len(pages)} ({num} entries)",
                    icon_url=None,
                )
            )
        from modules import paginator as pg
        paginator = pg.Paginator(self.bot, embeds, ctx, timeout=30, invoker=ctx.author.id)
        paginator.add_button("prev", emoji="<:left:1107307769582850079>")
        paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
        paginator.add_button("next", emoji="<:right:1107307767041105920>")
        paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
        await paginator.start()


    @commands.command(name = "forcenickname", description = "Forces a nickname upon a user",aliases=["forcenick"], usage = "forcenickname [user] [nickname]")
    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True)
    async def forcenickname(self, ctx, member: discord.Member, *, nickname):
        try:
            await member.edit(nick=nickname)

            embed = discord.Embed(
                title="Nickname Forced",
                description=f"<:miroapprove:1117144152363245638> The nickname of {member.mention} has been set to **{nickname}**.",
                color=0x79fc5a
            )
            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"<:mirodeny:1117144156507209829> An error occurred: {e}",
                color=0xfc5b6d
            )
            await ctx.send(embed=embed)


    @commands.command(name = "unforcenickname", description = "Stops forcing a nickname upon a user",aliases=["unforcenick"], usage = "unforcenickname [user]")
    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True)
    async def unforcenickname(self, ctx, member: discord.Member):
        try:
            await member.edit(nick=member.name)

            embed = discord.Embed(
                title="Nickname Unforced",
                description=f"<:miroapprove:1117144152363245638> The nickname of {member.mention} has been unforced.",
                color=0x79fc5a
            )
            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"<:mirodeny:1117144156507209829> An error occurred: {e}",
                color=0xfc5b6d
            )
            await ctx.send(embed=embed)


    @commands.command(name = "hardban", description = "Idbans a user",aliases=["idban"], usage = "idban [user id]")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(ban_members = True)
    async def hardban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.ban(user, reason="Hard Ban")
            embed = discord.Embed(
                title="Hard Ban",
                description=f"<:miroapprove:1117144152363245638> User {user.name}#{user.discriminator} has been hard banned.",
                color=0x79fc5a
            )
            await ctx.send(embed=embed)

        except discord.NotFound:
            embed = discord.Embed(
                title="User Not Found",
                description="<:mirow:1117144157992009728> The specified user ID is not valid.",
                color=0xfcbc5c
            )
            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="<:mirodeny:1117144156507209829> An error occurred",
                description=str(e),
                color=0xfc5b6d
            )
            await ctx.send(embed=embed)





async def setup(bot):
    await bot.add_cog(mod(bot))
