import re

import arrow
import discord
from discord.ext import commands, tasks
from tweepy.asynchronous import AsyncClient

from modules import exceptions, menus, queries, util
from modules.twitter_renderer import TwitterRenderer


class Twitterr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitter_renderer = TwitterRenderer(self.bot)

    async def cog_load(self):
        self.api = AsyncClient(
            bearer_token="AAAAAAAAAAAAAAAAAAAAAHbRggEAAAAA%2BCuuSYLDtOOxpKmmYEgY96MF8KE%3DxgCBX8fwb0QXv8qMbOTFARy7oZirRb8QFaW3KO4wz4TDF3VxMP",
            wait_on_rate_limit=True,
        )

    async def follow(self, channel, user_id, username, timestamp):
        await self.bot.db.execute(
            """
            INSERT INTO twitter_user VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE username = %s
            """,
            user_id,
            username,
            username,
        )
        await self.bot.db.execute(
            "INSERT INTO follow VALUES (%s, %s, %s, %s)",
            channel.id,
            channel.guild.id,
            user_id,
            timestamp,
        )

    async def unfollow(self, channel_id, user_id):
        await self.bot.db.execute(
            "DELETE FROM follow WHERE twitter_user_id = %s AND channel_id = %s",
            user_id,
            channel_id,
        )

    @commands.group(name='stream', description="stream twitter tweets")
    async def stream(self, ctx):
        if ctx.invoked_subcommand is None:
            await util.command_group_help(ctx)

    @stream.command(name='add', description="add a twitter to the stream list", brief='channel, usernames', extras={'perms':'Manage_Guild'}, usage="```Swift\nSyntax: !stream add <channel> <usernames>\nExample: !stream add #text cop rival```")
    @commands.has_permissions(manage_guild=True)
    async def stream_add(self, ctx, channel: discord.TextChannel, *usernames):
        """Add users to the follow list."""
        if not usernames:
            raise exceptions.Info("You must give at least one twitter user to follow!")

        rows = []
        time_now = arrow.now().datetime
        current_users = await self.bot.db.execute(
            "SELECT twitter_user_id FROM follow WHERE channel_id = %s", channel.id
        )
        guild_follow_current, guild_follow_limit = await queries.get_follow_limit(
            self.bot.db, channel.guild.id
        )
        successes = 0
        for username in usernames:
            status = None
            try:
                user = (await self.api.get_user(username=username)).data
            except Exception as e:
                status = f":x: Error {e}"
                await ctx.send(status)
            else:
                if (user.id,) in current_users:
                    status = ":x: User already being followed on this channel"
                    await ctx.send(status)
                else:
                    if guild_follow_current >= guild_follow_limit:
                        status = f":lock: Guild follow count limit reached ({guild_follow_limit})"
                    else:
                        await self.follow(channel, user.id, user.username, time_now)
                        status = ":white_check_mark: Success"
                        successes += 1
                        guild_follow_current += 1

            rows.append(f"**@{user.username}** {status}")

        content = discord.Embed(
            title=f":notepad_spiral: Added {successes}/{len(usernames)} users to {channel.name}",
            color=self.bot.twitter_blue,
        )
        content.set_footer(text="Changes will take effect within a minute")
        pages = menus.Menu(source=menus.ListMenu(rows, embed=content), clear_reactions_after=True)
        await pages.start(ctx)

    @stream.command(name="del", aliases=["delete", "remove"], brief='channel, usernames', extras={'perms':'Manage_Guild'}, usage="```Swift\nSyntax: !stream remove <channel> <usernames>\nExample: !stream remove #text cop rival```")
    @commands.has_permissions(manage_guild=True)
    async def stream_remove(self, ctx, channel: discord.TextChannel, *usernames):
        """Remove users from the follow list."""
        if not usernames:
            raise exceptions.Info("You must give at least one twitter user to remove!")

        rows = []
        current_users = await self.bot.db.execute(
            "SELECT twitter_user_id FROM follow WHERE channel_id = %s", channel.id
        )
        successes = 0
        for username in usernames:
            status = None
            try:
                user_id = (await self.api.get_user(username=username)).data.id
            except Exception as e:
                # user not found, maybe changed username
                # try finding username from cache
                user_id = await self.bot.db.execute(
                    "SELECT user_id FROM twitter_user WHERE username = %s", username
                )
                if user_id:
                    user_id = user_id[0][0]
                else:
                    status = f":x: Error {e.args[0][0]['code']}: {e.args[0][0]['message']}"

            if status is None:
                if (user_id,) not in current_users:
                    status = ":x: User is not being followed on this channel"
                else:
                    await self.unfollow(channel.id, user_id)
                    status = ":white_check_mark: Success"
                    successes += 1

            rows.append(f"**@{username}** {status}")

        content = discord.Embed(
            title=f":notepad_spiral: Removed {successes}/{len(usernames)} users from {channel.name}",
            color=self.bot.twitter_blue,
        )
        content.set_footer(text="Changes will take effect within a minute")
        pages = menus.Menu(source=menus.ListMenu(rows, embed=content), clear_reactions_after=True)
        await pages.start(ctx)

    @stream.command(name="list", aliases=["follows"])
    async def followslist(self, ctx, channel: discord.TextChannel = None):
        """List all followed accounts on server or channel"""
        data = await self.bot.db.execute(
            """
            SELECT twitter_user.username, channel_id, added_on
            FROM follow LEFT JOIN twitter_user
            ON twitter_user.user_id = follow.twitter_user_id WHERE follow.guild_id = %s
            """
            + (f" AND channel_id = {channel.id}" if channel is not None else "")
            + " ORDER BY channel_id, added_on DESC",
            ctx.guild.id,
        )
        content = discord.Embed(title="Followed twitter users", color=self.bot.twitter_blue)
        rows = []
        for username, channel_id, added_on in data:
            rows.append(
                (f"<#{channel_id}> < " if channel is None else "")
                + f"**@{username}** (since {added_on} UTC)"
            )

        if not rows:
            rows.append("Nothing yet :(")

        pages = menus.Menu(source=menus.ListMenu(rows, embed=content), clear_reactions_after=True)
        await pages.start(ctx)

    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def mediaonly(self, ctx):
        """
        Ignore tweets without any media in them.
        Config hierarchy is as follows:
            1. User settings overwrite everything else.
            2. Channel settings overwrite guild settings.
            2. Guild settings overwrite default settings.
            3. If nothing is set, default option is post everything.
        """
        if ctx.invoked_subcommand is None:
            await util.command_group_help(ctx)

    @mediaonly.command(name="guild", brief='state', description='twitter guild media only', extras={'perms':'Manage_Guild'}, usage="```Swift\nSyntax: !mediaonly guild <state>\nExample: !mediaonly guild true```")
    async def mediaonly_guild(self, ctx, value: bool):
        """Guild level setting."""
        await queries.set_config_guild(self.bot.db, ctx.guild.id, "media_only", value)
        await ctx.send(f":white_check_mark: Guild setting **Media only** is now **{value}**")

    @mediaonly.command(name="channel", description='twitter channel media only', brief='channel, state', extras={'perms':'Manage_Guild'}, usage="```Swift\nSyntax: !mediaonly channel <channel> <state>\nExample: !mediaonly channel #text true```")
    async def mediaonly_channel(self, ctx, channel: discord.TextChannel, value: bool):
        """Channel level setting."""
        await queries.set_config_channel(self.bot.db, channel, "media_only", value)
        await ctx.send(
            f":white_check_mark: Channel setting **Media only** is now **{value}** in {channel.mention}"
        )

    @mediaonly.command(name="user", description='twitter user media only', brief='username, state', extras={'perms':'Manage_Guild'}, usage="```Swift\nSyntax: !mediaonly user <username> <state>\nExample: !mediaonly user cop true```")
    async def mediaonly_user(self, ctx, username, value: bool):
        """User level setting."""
        user_id = await self.bot.db.execute(
            """
            SELECT twitter_user.user_id
            FROM follow RIGHT JOIN twitter_user
            ON twitter_user.user_id = follow.twitter_user_id
            WHERE twitter_user.username = %s AND guild_id = %s""",
            username,
            ctx.guild.id,
            one_value=True,
        )
        if not user_id:
            raise exceptions.Info(f'No channel on this server is following "@{username}"')

        await queries.set_config_user(self.bot.db, ctx.guild.id, user_id, "media_only", value)
        await ctx.send(
            f":white_check_mark: User setting **Media only** is now **{value}** for **@{username}**"
        )

    @mediaonly.command(name="clear", description='clear current config',extras={'perms':'Manage_Guild'})
    async def mediaonly_clear(self, ctx):
        """Clear all current config."""
        await queries.clear_config(self.bot.db, ctx.guild)
        await ctx.send(":white_check_mark: Settings cleared")

    @mediaonly.command(name="current",description='show current config',extras={'perms':'Manage_Guild'})
    async def mediaonly_current(self, ctx):
        """Show the current configuration."""
        channel_setting = await self.bot.db.execute(
            "SELECT channel_id, media_only FROM channel_setting WHERE guild_id = %s",
            ctx.guild.id,
        )
        guild_setting = await self.bot.db.execute(
            "SELECT media_only FROM guild_setting WHERE guild_id = %s",
            ctx.guild.id,
            one_value=True,
        )
        user_setting = await self.bot.db.execute(
            """
            SELECT twitter_user.username, media_only
            FROM user_setting RIGHT OUTER JOIN twitter_user
            ON twitter_user.user_id = user_setting.twitter_user_id
            WHERE guild_id = %s
            """,
            ctx.guild.id,
        )

        content = discord.Embed(title="Current configuration", color=self.bot.twitter_blue)
        content.add_field(
            name="Guild setting",
            value=f"Media only {':white_check_mark:' if guild_setting else ':x:'}",
        )
        if channel_setting:
            content.add_field(
                name="Channel settings",
                value="\n".join(
                    f"<#{cid}> Media only {':white_check_mark:' if val else ':x:'}"
                    for cid, val in channel_setting
                ),
            )
        if user_setting:
            content.add_field(
                name="User settings",
                value="\n".join(
                    f"**@{uname}** Media only {':white_check_mark:' if val else ':x:'}"
                    for uname, val in user_setting
                ),
            )
        await ctx.send(embed=content)

    @commands.command()
    async def get(self, ctx, *links):
        """Manually get tweets."""
        if len(links) > 10:
            raise exceptions.CommandWarning("Only 10 links at a time please!")

        for tweet_url in links:
            if "status" in tweet_url:
                tweet_id = re.search(r"status/(\d+)", tweet_url).group(1)
            else:
                tweet_id = tweet_url

            await self.twitter_renderer.send_tweet(int(tweet_id), channels=[ctx.channel])

        try:
            await ctx.message.edit(suppress=True)
        except (discord.Forbidden, discord.NotFound):
            pass

    @commands.command()
    @commands.is_owner()
    async def pppurge(self, ctx: commands.Context):
        """Remove all follows from unavailable guilds and channels."""
        data = await self.bot.db.execute(
            """
            SELECT channel_id, guild_id, twitter_user_id, username
            FROM follow
            JOIN twitter_user
            ON twitter_user_id=user_id
            """
        )
        actions = []
        guilds_to_delete = []
        channels_to_delete = []
        users_to_delete = []
        twitter_usernames = {}
        usernames_to_change = []
        for channel_id, guild_id, twitter_uid, username in data:
            if self.bot.get_guild(guild_id) is None:
                actions.append(f"Could not find guild with id: [{guild_id}]")
                guilds_to_delete.append(guild_id)
            elif self.bot.get_channel(channel_id) is None:
                actions.append(f"Could not find channel with id: [{channel_id}]")
                channels_to_delete.append(channel_id)
            else:
                twitter_usernames[twitter_uid] = username

        uids = list(twitter_usernames.keys())
        for uids_chunk in [uids[i : i + 100] for i in range(0, len(uids), 100)]:
            userdata = await self.api.get_users(ids=uids_chunk)
            if userdata.errors:
                for error in userdata.errors:
                    actions.append(error["detail"])
                    users_to_delete.append(int(error["value"]))
            if userdata.data:
                for user in userdata.data:
                    if twitter_usernames[user.id] != user.username:
                        actions.append(
                            f"User has changed username from @{twitter_usernames[user.id]} to @{user.username}"
                        )
                        usernames_to_change.append((user.id, user.username))

        if not actions:
            return await ctx.send("There is nothing to do.")

        content = discord.Embed(
            title="Purge results",
            color=self.bot.twitter_blue,
        )
        pages = menus.Menu(
            source=menus.ListMenu(actions, embed=content),
            clear_reactions_after=True,
        )
        await pages.start(ctx)
        confirm = await menus.Confirm("Run actions?").prompt(ctx)
        if confirm:
            await ctx.send("Running purge...")
            if guilds_to_delete:
                await self.bot.db.execute(
                    "DELETE FROM follow WHERE guild_id IN %s", guilds_to_delete
                )
            if channels_to_delete:
                await self.bot.db.execute(
                    "DELETE FROM follow WHERE channel_id IN %s", channels_to_delete
                )
            if users_to_delete:
                await self.bot.db.execute(
                    "DELETE FROM twitter_user WHERE user_id IN %s", users_to_delete
                )
            for uid, new_name in usernames_to_change:
                await self.bot.db.execute(
                    "UPDATE twitter_user SET username = %s WHERE user_id = %s", new_name, uid
                )
            await ctx.send("Purge complete!")


async def setup(bot):
    await bot.add_cog(Twitterr(bot))