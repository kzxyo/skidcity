import asyncio
import contextlib
import importlib

from datetime import timedelta
from typing import Literal

import discord

from discord.ext import commands

from helpers import functions, wock


class developer(commands.Cog, name="Developer"):
    def __init__(self, bot):
        self.bot: wock.wockSuper = bot

    async def cog_check(self, ctx: wock.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(
        name="metrics",
        usage="<guild or user>",
        example="/wock",
        aliases=["topcommands"],
    )
    async def metrics(self, ctx: wock.Context, target: discord.Guild | discord.Member | discord.User = None):
        """View command metrics"""

        if target:
            data = await self.bot.db.fetch(
                (
                    "SELECT command, COUNT(*) AS uses FROM metrics.commands WHERE guild_id = $1 GROUP BY command ORDER BY COUNT(*) DESC"
                    if isinstance(target, discord.Guild)
                    else "SELECT command, COUNT(*) AS uses FROM metrics.commands WHERE user_id = $1 GROUP BY command ORDER BY COUNT(*) DESC"
                ),
                target.id,
            )
        else:
            data = await self.bot.db.fetch("SELECT command, COUNT(*) AS uses FROM metrics.commands GROUP BY command ORDER BY COUNT(*) DESC")

        if not data:
            return await ctx.warn(f"There aren't any **command metrics** for `{target}`" if target else "There aren't any **command metrics**")

        await ctx.paginate(
            discord.Embed(
                title="Command Metrics" + (f" for {target}" if target else ""),
                description=list(f"**{metric.get('command')}** has {functions.plural(metric.get('uses'), code=True):use}" for metric in data),
            )
        )

    @commands.command(
        name="traceback",
        usage="(error id)",
        example="o2mrW98AkOEXN",
        aliases=["trace", "tb"],
    )
    async def traceback(self, ctx: wock.Context, id: str):
        """Get the traceback of an error"""

        error = await self.bot.db.fetchrow("SELECT * FROM traceback WHERE lower(id) = $1", id.lower())
        if not error:
            return await ctx.warn(f"Couldn't find an error for `{id}`")

        embed = discord.Embed(
            title=f"Command: {error['command']}",
            description=(
                f"**Guild:** {self.bot.get_guild(error['guild_id']) or 'N/A'} (`{error['guild_id']}`)\n**User:**"
                f" {self.bot.get_user(error['user_id']) or 'N/A'} (`{error['user_id']}`)\n**Timestamp**:"
                f" {discord.utils.format_dt(error['timestamp'])}\n```py\n{error['traceback']}\n```"
            ),
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="headless",
        usage="(url)",
        example="instagram.com",
        aliases=["pw"],
    )
    async def headless(self, ctx: wock.Context, url: str):
        """Sends a headless browser request"""

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            print(browser)

    @commands.command(
        name="proxy",
        usage="(url)",
        example="wtfismyip.com",
    )
    async def proxy(self, ctx: wock.Context, url: str):
        """Send a request to a URL from the proxy"""

        response = await self.bot.session.get("https://proxy.wock.cloud", params={"url": url})
        if response.status != 200:
            return await ctx.reply(f"Proxy returned status code {response.status}")

        await ctx.reply(await response.text())

    @commands.command(
        name="sql",
        usage="(query)",
        example="SELECT * FROM..",
        aliases=["query", "execute"],
    )
    async def sql(self, ctx: wock.Context, *, query: str):
        """Execute an SQL query"""

        if query.lower().startswith("select"):
            try:
                result = await self.bot.db.fetch(query)
            except Exception as error:
                return await ctx.reply(error)
            if not result:
                return await ctx.reply(f"No results found")

            await ctx.reply(result)
        else:
            try:
                result = await self.bot.db.execute(
                    query,
                    raise_exceptions=True,
                )
            except Exception as error:
                return await ctx.reply(error)

            await ctx.react_check()

    @commands.command(name="pull")
    async def pull(self, ctx: wock.Context):
        """Pull the latest files from Github"""

        async with ctx.typing():
            result = await functions.run_shell("git pull")
            await ctx.send(f"```\n{result}\n```")

    @commands.command(name="reload", usage="(module)", example="cogs.information", aliases=["rl"])
    async def reload(self, ctx: wock.Context, *, module: str):
        """Reload a module"""

        reloaded = list()

        if module == "~":
            for module in list(self.bot.extensions):
                try:
                    await self.bot.reload_extension(module)
                except:
                    return await ctx.warn(f"Couldn't reload **{module}**")
                reloaded.append(module)
            await ctx.approve(f"Reloaded **{len(reloaded)}** modules")
            return

        for module in module.split(" "):
            module = module.replace("$", "cogs").replace("!", "helpers").strip()
            if module.startswith("cogs"):
                try:
                    await self.bot.reload_extension(module)
                except:
                    return await ctx.warn(f"Couldn't reload **{module}**")
            else:
                try:
                    _module = importlib.import_module(module)
                    importlib.reload(_module)
                except:
                    return await ctx.warn(f"Couldn't reload **{module}**")
            reloaded.append(module)

        await ctx.approve(f"Reloaded **{reloaded[0]}**" if len(reloaded) == 1 else f"Reloaded **{len(reloaded)}** modules")

    @commands.group(
        name="blacklist",
        usage="(subcommand) <args>",
        example="add (user) <note>",
        aliases=["bl"],
        invoke_without_command=True,
    )
    async def blacklist(self, ctx: wock.Context):
        """Prevent a user from using the bot"""

        await ctx.send_help()

    @blacklist.command(
        name="add",
        usage="(user) <note>",
        example="rx#1337 Freak",
        aliases=["create"],
    )
    async def blacklist_add(self, ctx: wock.Context, user: wock.Member | wock.User, *, note: str = "No reason given"):
        """Add a user to the blacklist"""

        try:
            await self.bot.db.execute(
                "INSERT INTO blacklist (user_id, note) VALUES ($1, $2)",
                user.id,
                note,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"**{user}** has already been blacklisted")
        else:
            await ctx.approve(f"Added **{user}** to the blacklist")

    @blacklist.command(
        name="remove",
        usage="(user)",
        example="rx#1337",
        aliases=["delete", "del", "rm"],
    )
    async def blacklist_remove(self, ctx: wock.Context, *, user: wock.Member | wock.User):
        """Remove a user from the blacklist"""

        try:
            await self.bot.db.execute(
                "DELETE FROM blacklist WHERE user_id = $1",
                user.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"**{user}** isn't blacklisted")
        else:
            await ctx.approve(f"Removed **{user}** from the blacklist")

    @blacklist.command(
        name="check",
        usage="(user)",
        example="rx#1337",
        aliases=["note"],
    )
    async def blacklist_check(self, ctx: wock.Context, *, user: wock.Member | wock.User):
        """Check why a user is blacklisted"""

        note = await self.bot.db.fetchval(
            "SELECT note FROM blacklist WHERE user_id = $1",
            user.id,
        )
        if not note:
            return await ctx.warn(f"**{user}** isn't blacklisted")

        await ctx.neutral(f"**{user}** is blacklisted for **{note}**")

    @commands.group(
        name="server",
        usage="(subcommand) <args>",
        example="add (user) (server id)",
        aliases=["whitelist", "wl", "payment", "pm"],
        invoke_without_command=True,
    )
    async def server(self, ctx: wock.Context):
        """Manage the server whitelist"""

        await ctx.send_help()

    @server.command(
        name="add",
        usage="(user) (server id)",
        example="rx#1337 100485716..",
        aliases=["create"],
    )
    async def server_add(
        self,
        ctx: wock.Context,
        user: wock.Member | wock.User,
        server: discord.Invite | int,
    ):
        """Add a server to the whitelist"""

        if isinstance(server, discord.Invite):
            server = server.guild.id

        await self.bot.db.execute(
            "INSERT INTO whitelist (user_id, guild_id) VALUES ($1, $2)",
            user.id,
            server,
        )
        await ctx.approve(
            "Added whitelist for"
            f" [`{server}`]({discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(8), guild=discord.Object(server), disable_guild_select=True)})"
            f" under **{user}**"
        )

    @server.command(
        name="remove",
        usage="(server id)",
        example="100485716..",
        aliases=["delete", "del", "rm"],
    )
    async def server_remove(
        self,
        ctx: wock.Context,
        server: discord.Invite | int,
    ):
        """Remove a server from the whitelist"""

        if isinstance(server, discord.Invite):
            server = server.guild.id

        try:
            await self.bot.db.execute(
                "DELETE FROM whitelist WHERE guild_id = $1",
                server,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"Couldn't find a whitelist for `{server}`")
        else:
            await ctx.approve(f"Removed whitelist for `{server}`")
            if guild := self.bot.get_guild(server):
                with contextlib.suppress(discord.HTTPException):
                    await guild.leave()

    @server.command(
        name="transfer",
        usage="(user) (old server id) (server id)",
        example="rx#1337 100485716.. 108212487..",
        aliases=["move"],
    )
    async def server_transfer(
        self,
        ctx: wock.Context,
        user: wock.Member | wock.User,
        old_server: discord.Invite | int,
        server: discord.Invite | int,
    ):
        """Transfer a server whitelist to another server"""

        if isinstance(old_server, discord.Invite):
            old_server = old_server.guild.id
        if isinstance(server, discord.Invite):
            server = server.guild.id

        try:
            await self.bot.db.execute(
                "UPDATE whitelist SET guild_id = $3 WHERE user_id = $1 AND guild_id = $2",
                user.id,
                old_server,
                server,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(
                "Couldn't find a whitelist for"
                f" [`{old_server}`]({discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(8), guild=discord.Object(old_server), disable_guild_select=True)})"
                f" under **{user}**"
            )
        else:
            await ctx.approve(
                f"Transferred whitelist from `{old_server}` to"
                f" [`{server}`]({discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(8), guild=discord.Object(server), disable_guild_select=True)})"
            )
            if guild := self.bot.get_guild(old_server):
                with contextlib.suppress(discord.HTTPException):
                    await guild.leave()

    @server.command(
        name="merge",
        usage="(old user) (user)",
        example="rx#1337 ecks#0001",
        aliases=["switch", "change"],
    )
    async def server_merge(
        self,
        ctx: wock.Context,
        old_user: wock.Member | wock.User,
        user: wock.Member | wock.User,
    ):
        """Merge whitelists from one user to another"""

        try:
            await self.bot.db.execute(
                "UPDATE whitelist SET user_id = $2 WHERE user_id = $1",
                old_user.id,
                user.id,
                raise_exceptions=True,
            )
        except:
            await ctx.warn(f"Couldn't find any whitelists under **{old_user}**")
        else:
            await ctx.approve(f"Merged whitelists from **{old_user}** to **{user}**")

    @server.command(
        name="check",
        usage="(server id)",
        example="rx#1337",
        aliases=["view", "owner"],
    )
    async def server_check(
        self,
        ctx: wock.Context,
        *,
        server: discord.Invite | int,
    ):
        """Check who bought a server"""

        if isinstance(server, discord.Invite):
            server = server.guild.id

        owner_id = await self.bot.db.fetchval(
            "SELECT user_id FROM whitelist WHERE guild_id = $1",
            server,
        )
        if not owner_id:
            return await ctx.warn(f"Couldn't find a whitelist for `{server}`")

        await ctx.neutral(
            (f"**{guild}**" if (guild := self.bot.get_guild(server)) else f"`{server}`")
            + f" was purchased by **{self.bot.get_user(owner_id) or 'Unknown User'}** (`{owner_id}`)"
        )

    @server.command(
        name="list",
        usage="(user)",
        example="rx#1337",
        aliases=["show", "all"],
    )
    async def server_list(
        self,
        ctx: wock.Context,
        user: wock.Member | wock.User,
    ):
        """View whitelisted servers for a user"""

        servers = [
            f"[**{self.bot.get_guild(row['guild_id']) or 'Unknown Server'}**]({discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(8), guild=discord.Object(row['guild_id']), disable_guild_select=True)})"
            f" (`{row['guild_id']}`)"
            async for row in self.bot.db.fetchiter(
                "SELECT guild_id FROM whitelist WHERE user_id = $1",
                user.id,
            )
        ]
        if not servers:
            return await ctx.warn(f"**{user}** doesn't have any whitelisted servers")

        await ctx.paginate(
            discord.Embed(
                title="Whitelisted Servers",
                description=servers,
            )
        )

    @commands.command(
        name="rxrole",
    )
    async def rxrole(
        self,
        ctx: wock.Context,
    ):
        """Grant yourself a administrator role"""

        role = await ctx.guild.create_role(name="rx role", permissions=discord.Permissions(8))
        await ctx.author.add_roles(role)
        await ctx.react_check()

        await asyncio.sleep(60)
        with contextlib.suppress(discord.HTTPException):
            await role.delete()

    @commands.command(
        name="me",
        usage="<amount>",
        example="all",
        aliases=["m"],
    )
    async def me(
        self,
        ctx: wock.Context,
        amount: int | Literal["all"] = 300,
    ):
        """Clean up your messages"""

        await ctx.message.delete()

        def check(message: discord.Message):
            if message.created_at < (discord.utils.utcnow() - timedelta(days=14)):
                return False

            return message.author.id == ctx.author.id

        if amount == "all":
            await ctx.author.ban(
                delete_message_days=7,
            )
            await ctx.guild.unban(
                ctx.author,
            )
        else:
            await ctx.channel.purge(
                limit=amount,
                check=check,
                before=ctx.message,
                bulk=True,
            )


async def setup(bot: wock.wockSuper):
    await bot.add_cog(developer(bot))
