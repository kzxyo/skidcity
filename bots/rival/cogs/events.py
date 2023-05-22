import asyncio,typing,random,datetime,arrow,discord
from discord.ext import commands, tasks

from libraries import emoji_literals
from modules import emojis, log, queries, util
from modules.asynciterations import aiter
import logging
logger = logging.getLogger(__name__)
command_logger = logger


class Events(commands.Cog):
    """Event handlers for various discord events"""

    def __init__(self, bot):
        self.bot = bot
        self.activities = {"playing": 0, "streaming": 1, "listening": 2, "watching": 3}
        self.xp_cache = {}
        self.emoji_usage_cache = {"unicode": {}, "custom": {}}
        self.current_status = None
        self.guildlog = 652916681299066900
        self.xp_limit = 150
        self.stats_messages = 0
        self.stats_reactions = 0
        self.messaged=[]
        self.cd={}
        self.stats_commands = 0
        self.bot.loop.create_task(self.start_tasks())

    def cog_unload(self):
        self.status_loop.cancel()

    async def start_tasks(self):
        """Start tasks."""
        await self.bot.wait_until_ready()
        await self.xp_loop.start()

    async def insert_stats(self):
        self.bot.logger.info("inserting usage stats")
        ts = arrow.now().floor("minute")
        await self.bot.db.execute(
            """
            INSERT INTO stats (
                ts, messages, reactions, commands_used,
                guild_count, member_count, notifications_sent,
                lastfm_api_requests, html_rendered
            )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                messages = messages + VALUES(messages),
                reactions = reactions + VALUES(reactions),
                commands_used = commands_used + VALUES(commands_used),
                guild_count = VALUES(guild_count),
                member_count = VALUES(member_count),
                notifications_sent = notifications_sent + values(notifications_sent),
                lastfm_api_requests = lastfm_api_requests + values(lastfm_api_requests),
                html_rendered = html_rendered + values(html_rendered)
            """,
            ts.datetime,
            self.stats_messages,
            self.stats_reactions,
            self.stats_commands,
            len(self.bot.guilds),
            len(set(self.bot.get_all_members())),
            self.bot.cache.stats_notifications_sent,
            self.bot.cache.stats_lastfm_requests,
            self.bot.cache.stats_html_rendered,
        )
        self.stats_messages = 0
        self.stats_reactions = 0
        self.stats_commands = 0
        self.bot.cache.stats_notifications_sent = 0
        self.bot.cache.stats_lastfm_requests = 0
        self.bot.cache.stats_html_rendered = 0

    async def write_usage_data(self):
        self.messaged.clear()
        values = []
        total_messages = 0
        total_users = 0
        total_xp = 0
        async for guild_id in aiter(self.xp_cache):
            async for user_id, value in aiter(self.xp_cache[guild_id].items()):
                xp = min(value["xp"], self.xp_limit)
                values.append(
                    (
                        int(guild_id),
                        int(user_id),
                        value["bot"],
                        xp,
                        value["messages"],
                    )
                )
                total_messages += value["messages"]
                total_xp += xp
                total_users += 1

        sql_tasks = []
        if values:
            currenthour = arrow.utcnow().hour
            async for activity_table in aiter([
                "user_activity",
                "user_activity_day",
                "user_activity_week",
                "user_activity_month",
            ]):
                sql_tasks.append(
                    self.bot.db.executemany(
                        f"""
                    INSERT INTO {activity_table} (guild_id, user_id, is_bot, h{currenthour}, message_count)
                        VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        h{currenthour} = h{currenthour} + VALUES(h{currenthour}),
                        message_count = message_count + VALUES(message_count)
                    """,
                        values,
                    )
                )
        self.xp_cache = {}

        # unicode_emoji_values = []
        # for guild_id in self.emoji_usage_cache["unicode"]:
        #     for user_id in self.emoji_usage_cache["unicode"][guild_id]:
        #         for emoji_name, value in self.emoji_usage_cache["unicode"][guild_id][
        #             user_id
        #         ].items():
        #             unicode_emoji_values.append((int(guild_id), int(user_id), emoji_name, value))

        # if unicode_emoji_values:
        #     sql_tasks.append(
        #         self.bot.db.executemany(
        #             """
        #         INSERT INTO unicode_emoji_usage (guild_id, user_id, emoji_name, uses)
        #             VALUES (%s, %s, %s, %s)
        #         ON DUPLICATE KEY UPDATE
        #             uses = uses + VALUES(uses)
        #         """,
        #             unicode_emoji_values,
        #         )
        #     )
        # self.emoji_usage_cache["unicode"] = {}

        # custom_emoji_values = []
        # for guild_id in self.emoji_usage_cache["custom"]:
        #     for user_id in self.emoji_usage_cache["custom"][guild_id]:
        #         for emoji_id, value in self.emoji_usage_cache["custom"][guild_id][user_id].items():
        #             custom_emoji_values.append(
        #                 (int(guild_id), int(user_id), value["name"], emoji_id, value["uses"])
        #             )

        # if custom_emoji_values:
        #     sql_tasks.append(
        #         self.bot.db.executemany(
        #             """
        #         INSERT INTO custom_emoji_usage (guild_id, user_id, emoji_name, emoji_id, uses)
        #             VALUES (%s, %s, %s, %s, %s)
        #         ON DUPLICATE KEY UPDATE
        #             uses = uses + VALUES(uses)
        #         """,
        #             custom_emoji_values,
        #         )
        #     )
        # self.emoji_usage_cache["custom"] = {}
        if sql_tasks:
            await asyncio.gather(*sql_tasks)
            logger.info(
                f"Inserted {total_messages} messages from {total_users} users, "
                f"average {total_messages/300:.2f} messages / second, {total_xp/total_users} xp per user"
            )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild.premium_subscriber_role in after.roles and before.guild.premium_subscriber_role not in after.roles and await self.bot.db.execute("""SELECT * FROM lostboost WHERE guild_id = %s and user_id = %s""", before.guild.id, before.id):
            await self.bot.db.execute("""DELETE FROM lostboost where user_id = %s AND guild_id = %s""", before.id, before.guild.id)
        if before.guild.premium_subscriber_role in before.roles and before.guild.premium_subscriber_role not in after.roles:
            await self.bot.db.execute("""INSERT INTO lostboost VALUES(%s, %s, %s)""", before.guild.id, before.id, datetime.datetime.now())
        if before.guild.premium_subscriber_role not in before.roles and after.guild.premium_subscriber_role in after.roles:
            if await self.bot.db.execute("""SELECT * FROM lostboost WHERE guild_id = %s AND user_id = %s""", before.guild.id, after.id):
                await self.bot.db.execute("""DELETE FROM lostboost WHERE guild_id = %s AND user_id = %s""", before.guild.id, after.id)
        data=await self.bot.db.execute("""SELECT role_id FROM boostrole WHERE user_id = %s AND guild_id = %s""", before.id, before.guild.id, one_value=True)
        if data and before.guild.premium_subscriber_role in before.roles and before.guild.premium_subscriber_role not in after.roles:
            role=before.guild.get_role(data)
            await role.delete()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Runs when any command is completed succesfully."""
        # prevent double invocation for subcommands
        if ctx.invoked_subcommand is None:
            command = str(ctx.command)
            guild = ctx.guild.name if ctx.guild is not None else "DM"
            user = str(ctx.author)
            extra=" "
            command_logger.info(f'{command:19} > {guild} : {user} "{ctx.message.content}" {extra}')
            self.stats_commands += 1
           # if ctx.guild is not None:
                #await queries.save_command_usage(ctx)
        if ctx.guild.id in self.bot.cache.delete:
            await ctx.message.delete()

    @tasks.loop(minutes=1.0)
    async def stats_loop(self):
        try:
            await self.insert_stats()
        except Exception as e:
            logger.error(f"stats_loop: {e}")

    @tasks.loop(minutes=1.0)
    async def xp_loop(self):
        try:
            await self.write_usage_data()
        except Exception as e:
            logger.error(f"xp_loop: {e}")



    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild."""
        self.bot.cache.event_triggers["guild_join"] += 1
        blacklisted = await self.bot.db.execute(
            "SELECT reason FROM blacklisted_guild WHERE guild_id = %s", guild.id, one_value=True
        )
        if blacklisted:
            logger.info(f"Tried to join guild {guild}. Reason for blacklist: {blacklisted}")
            return await guild.leave()
        await self.bot.wait_until_ready()
        logger.info(f"New guild : {guild}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Called when the bot leaves a guild."""
        self.bot.cache.event_triggers["guild_remove"] += 1

        await self.bot.wait_until_ready()
        logger.info(f"Left guild {guild}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Called when a new member joins a guild."""
        self.bot.cache.event_triggers["member_join"] += 1
        if member.id in self.bot.cache.globalban:
            try:
                return await member.ban(reason="Globally Banned User")
            except:
                pass
        ##joins=await self.bot.db.execute("""SELECT amount FROM joins WHERE guild_id = %s""", member.guild.id, one_value=True)
        #trig=await self.bot.db.execute("""SELECT * FROM antiraidtrigger WHERE guild_id = %s""", member.guild.id)
        try:    
            if 0 not in self.cd:
                self.cd[0]=[]
        except Exception as e:
            print(e)
        try:
            try:
                self.cd[0]+=1
            except:
                self.cd[0]=1
        except Exception as e:
            print(e)
        try:
            if len(self.cd[0]) > 10:
                return
        except:
            pass
        if member.guild.id in self.bot.cache.antiraid_joins:
            joins=self.bot.cache.antiraid_joins.get(member.guild.id)
        else:
            joins=False
        #trig=await self.bot.db.execute("""SELECT * FROM antiraidtrigger WHERE guild_id = %s""", member.guild.id)
        if member.guild.id in self.bot.cache.antiraid_trigger:
            trig=self.bot.cache.antiraid_trigger.get(member.guild.id)
        else:
            trig=False
        if trig and joins:
            if trig<=int(joins):
                return
        roles = self.bot.cache.autoroles.get(str(member.guild.id), [])
        for role_id in roles:
            role = member.guild.get_role(role_id)
            if role == None:
                return
            if role.permissions.administrator or role.permissions.manage_guild or role.permissions.kick_members or role.permissions.ban_members or role.permissions.manage_channels:
                await self.bot.db.execute("DELETE FROM autorole WHERE guild_id = %s AND role_id = %s",member.guild.id,role.id)
            if role is None:
                continue
            try:
                await member.add_roles(role)
            except Exception as e:
                print("e")
                pass
        # welcome message
        await asyncio.sleep(1)
        greeter = await self.bot.db.execute(
            "SELECT is_enabled, message_format FROM greeter_settings WHERE guild_id = %s",
            member.guild.id,
            one_row=True,
        )

        if greeter:
            is_enabled, message_format = greeter
            if is_enabled:
                if message_format is not None:
                    try:
                        view = discord.ui.View()
                        view.add_item(discord.ui.Button(custom_id='yer', style=discord.ButtonStyle.grey, disabled=True, label=f"Sent from: {member.guild.name}"))
                        await member.send(content=util.create_welcome_embed(member, member.guild, message_format), view=view)
                    except discord.errors.Forbidden:
                        pass
                    except discord.errors.HTTPException:
                        pass

    @tasks.loop(minutes=1)
    async def threshold_clear(self):
        if self.cd:
            self.cd.clear()


    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """Listener that gets called when any message is deleted."""
        if not self.bot.is_ready():
            return

        self.bot.cache.event_triggers["message_delete"] += 1

        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            return

        message = payload.cached_message
        if message is None:
            return

        # ignore bots
        if message.author.bot:
            return

        # ignore DMs
        if message.guild is None:
            return
        self.bot.cache.last_seen.update({str(message.author.id):datetime.datetime.now()})

        # ignore empty messages
        if len(message.content) == 0 and len(message.attachments) == 0:
            return

        channel_id = None
        logging_settings = self.bot.cache.logging_settings.get(str(message.guild.id))
        if logging_settings:
            channel_id = logging_settings.get("message_log_channel_id")
        if channel_id:
            log_channel = message.guild.get_channel(channel_id)
            if log_channel is not None and message.channel != log_channel:
                # ignored channels
                ignored_channels = await self.bot.db.execute(
                    "SELECT channel_id FROM message_log_ignore WHERE guild_id = %s",
                    message.guild.id,
                    as_list=True,
                )
                if message.channel.id not in ignored_channels:
                    try:
                        await log_channel.send(embed=util.message_embed(message))
                    except discord.errors.Forbidden:
                        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener that gets called on every message."""
        if not self.bot.is_ready():
            return
        self.stats_messages += 1
        self.bot.cache.event_triggers["message"] += 1

        # temp fix
       # return

        # ignore DMs
        if message.guild is None:
            return
        if message.author.bot:
            return
        if not await self.bot.db.execute("""SELECT * FROM leveling WHERE guild_id = %s""", message.guild.id):
            return

        # xp gain
        message_xp = util.xp_from_message(message)
        activity_data = await self.bot.db.execute(
            """
            SELECT h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13,h14,h15,h16,h17,h18,h19,h20,h21,h22,h23
                FROM user_activity
            WHERE user_id = %s AND guild_id = %s
            """,
            message.author.id,
            message.guild.id,
            one_row=True,
            )
        xp = sum(activity_data) if activity_data else 0
        before = util.get_level(xp)
        try:
            if self.xp_cache[str(message.guild.id)][str(message.author.id)]["xp"]:
                aftt=self.xp_cache[str(message.guild.id)][str(message.author.id)]["xp"]
            else:
                aftt=0
        except:
            aftt=0
        after=util.get_level(xp+message_xp+aftt)
        try:
            if self.bot.cache.levelupmessage[str(message.guild.id)] == True and util.get_level(xp+message_xp+aftt) != before:
                if message.author.id in self.messaged:
                    pass
                else:
                    try:
                        await message.author.send(content=f"You leveled up to **level** `{after}`")
                        self.messaged.append(message.author.id)
                    except:
                        pass
        except:
            pass
        if self.xp_cache.get(str(message.guild.id)) is None:
            self.xp_cache[str(message.guild.id)] = {}
        try:
            self.xp_cache[str(message.guild.id)][str(message.author.id)]["xp"] += message_xp
            self.xp_cache[str(message.guild.id)][str(message.author.id)]["messages"] += 1
        except KeyError:
            self.xp_cache[str(message.guild.id)][str(message.author.id)] = {
                "xp": message_xp,
                "messages": 1,
                "bot": message.author.bot,
            }

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Starboard event handler."""
        if not self.bot.is_ready():
            return
        # skulls=[":skull_crossbones:", ":skull:", ":skull_and_crossbones:"]
        # #print(emoji_literals.UNICODE_TO_NAME.get(payload.emoji.name))
        # if emoji_literals.UNICODE_TO_NAME.get(payload.emoji.name) in skulls:
        #     message_channel = self.bot.get_channel(payload.channel_id)
        #     user = self.bot.get_user(payload.user_id)
        #     if user.bot:
        #         return
        #     if message_channel.guild.id == 1014050111367684146:
        #         try:
        #             message = await message_channel.fetch_message(payload.message_id)
        #         except (discord.errors.Forbidden, discord.errors.NotFound):
        #             pass
        #     try:
        #         if message:
        #             if not message.author.bot:
        #                 await self.bot.db.execute("""INSERT INTO skull (user_id) VALUES (%s) ON DUPLICATE KEY UPDATE amount = amount + 1""", message.author.id)
        #     except:
        #         pass

        self.stats_reactions += 1
        self.bot.cache.event_triggers["reaction_add"] += 1
        user = self.bot.get_user(payload.user_id)
        if user.bot:
            return
        self.bot.cache.last_seen.update({str(payload.user_id):datetime.datetime.now()})

        if payload.channel_id in self.bot.cache.starboard_blacklisted_channels:
            return

        starboard_settings = self.bot.cache.starboard_settings.get(str(payload.guild_id))
        if not starboard_settings:
            return

        (
            is_enabled,
            board_channel_id,
            required_reaction_count,
            emoji_name,
            emoji_id,
            emoji_type,
            log_channel_id,
        ) = starboard_settings

        if not is_enabled:
            return

        board_channel = self.bot.get_channel(board_channel_id)
        if board_channel is None:
            return

        if (
            emoji_type == "custom"
            and emoji_id is not None
            and payload.emoji.id is not None
            and payload.emoji.id == emoji_id
        ) or (
            (emoji_type == "unicode" or emoji_type is None)
            and emoji_literals.UNICODE_TO_NAME.get(payload.emoji.name) == emoji_name
        ):
            message_channel = self.bot.get_channel(payload.channel_id)

            # trying to star a starboard message
            if message_channel.id == board_channel_id:
                return
            try:
                message = await message_channel.fetch_message(payload.message_id)
            except (discord.errors.Forbidden, discord.errors.NotFound):
                return

            reaction_count = 0
            reacted_users = []
            for react in message.reactions:
                if emoji_type == "custom":
                    if (
                        isinstance(react.emoji, (discord.Emoji, discord.PartialEmoji))
                        and react.emoji.id == payload.emoji.id
                    ):
                        reaction_count = react.count
                        reacted_users = [user async for user in react.users()]
                        break
                else:
                    if react.emoji == payload.emoji.name:
                        reaction_count = react.count
                        reacted_users = [user async for user in react.users()]
                        break

            reacted_users = set(reacted_users)
            reacted_users.add(user)
            for reacted_user in reacted_users:
                if reaction_count < required_reaction_count:
                    if reacted_user.guild_permissions.administrator:
                        pass
                    else:
                        return

            board_message_id = await self.bot.db.execute(
                "SELECT starboard_message_id FROM starboard_message WHERE original_message_id = %s",
                payload.message_id,
                one_value=True,
            )
            emoji_display = (
                "⭐" if emoji_type == "custom" else emoji_literals.NAME_TO_UNICODE[emoji_name]
            )

            board_message = None
            if board_message_id:
                try:
                    board_message = await board_channel.fetch_message(board_message_id)
                except discord.errors.NotFound:
                    pass

            if board_message is None:
                if message.reference:
                    message_channel=self.bot.get_channel(message.channel.id)
                    ms=await message_channel.fetch_message(message.reference.message_id)
                    msg=f"<@{ms.author.id}> "
                else:
                    msg=""
                # message is not on board yet, or it was deleted
                content = discord.Embed(color=int("303135", 16))
                content.set_author(name=f"{message.author}", icon_url=message.author.display_avatar)
                content.description = msg+message.content
                content.timestamp = message.created_at
                content.set_footer(
                    text=f"{reaction_count} {emoji_display} #{message.channel.name}"
                )
                if len(message.attachments) > 0:
                    content.set_image(url=message.attachments[0].url)
                view = discord.ui.View()
                view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Message", url=message.jump_url))
                board_message = await board_channel.send(embed=content, view=view)
                await self.bot.db.execute(
                    """
                    INSERT INTO starboard_message (original_message_id, starboard_message_id)
                        VALUES(%s, %s)
                    ON DUPLICATE KEY UPDATE
                        starboard_message_id = VALUES(starboard_message_id)
                    """,
                    payload.message_id,
                    board_message.id,
                )
                log_channel = self.bot.get_channel(log_channel_id)
                if log_channel is not None:
                    content = discord.Embed(
                        color=int("303135", 16), title="Message added to starboard"
                    )
                    content.add_field(
                        name="Board message",
                        value=f"[{board_message.id}]({board_message.jump_url})",
                    )
                    content.add_field(
                        name="Reacted users",
                        value="\n".join(str(x) for x in reacted_users)[:1023],
                        inline=False,
                    )
                    content.add_field(name="Most recent reaction by", value=str(user))
                    try:
                        view = discord.ui.View()
                        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Message", url=board_message.jump_url))
                        await log_channel.send(embed=content, view=view)
                    except Exception as e:
                        await log_channel.send(f"`error in starboard log: {e}`")

            else:
                # message is on board, update star count
                content = board_message.embeds[0]
                content.set_footer(
                    text=f"{reaction_count} {emoji_display} #{message.channel.name}"
                )
                await board_message.edit(embed=content)


async def setup(bot):
    await bot.add_cog(Events(bot))
