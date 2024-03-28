import time as t
import asyncio
from puke import Puke
from puke.utils import humanize, human_timedelta
from puke.managers import Context
from typing import Union

from discord import Message, Embed, Member, User 
from discord.utils import format_dt
from discord.ext.commands import Cog, command, Author

from discord.ui import Button, View
from jishaku.features.root_command import *

class Miscellaneous(Cog):
    def __init__(self, bot):
        self.bot: Puke = bot

    @Cog.listener("on_message")
    async def check_afk(
        self: "Miscellaneous", 
        message: Message
    ):
        if (ctx := await self.bot.get_context(message)) and ctx.command:
            return

        elif afk := await self.bot.db.fetchval(
            """
            DELETE FROM afk
            WHERE user_id = $1
            RETURNING date
            """,
            message.author.id,
        ):
            return await ctx.neutral(f"Welcome back! You were away for **{humanize(afk, suffix=False)}**!")

        elif len(message.mentions) == 1 and (user := message.mentions[0]):
            if afk2 := await self.bot.db.fetchrow(
                """
                SELECT reason, date FROM afk
                WHERE user_id = $1
                """,
                user.id,
            ):
                return await ctx.neutral(f"{user.mention} is AFK! **{afk2['reason']}** - `{humanize(afk2['date'], suffix=False)}`")

    @command(
        name="ping",
        aliases=['latency']
    )
    async def ping(
        self: "Miscellaneous",
        ctx: Context
    ):
        """
        Get the latency of the bot
        """
        start, end = t.time(), await asyncio.sleep(0.1) or t.time()
        try:
          return await ctx.neutral(
                    f">>> 🛰️ Average latency: `{int(self.bot.latency * 1000)}ms` (edit: `{round((end - start) * 1000, 2)}ms`)"
                   )
        except Exception as error:
                  await ctx.warn(
                           f"Unexpected **error** has occurred\n> {error}"
                 )
    
    @command(
        name="afk"
    )
    async def afk(
        self: "Miscellaneous",
        ctx: Context,
        *,
        reason: str ="AFK"
    ):
        """
        Become AFK and notify members when mentioned
        """

        await self.bot.db.execute(
            """
            INSERT INTO afk (
                user_id,
                reason
            ) VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING;
            """,
            ctx.author.id,
            reason[:100],
        )

        await ctx.approve(f">>> {ctx.author.mention} You're now AFK with the status: **{reason}**!")

    @command(
        name="botinfo",
        aliases=[
            'about',
            'bi'
        ]
    )
    async def botinfo(
        self: "Miscellaneous",
        ctx: Context
    ):
        """
        Get info on bot
        """

        summary = [
            f"Bot created and maintained by <@188253074349883392>\n"
            f"> Bot was started `{human_timedelta(self.bot.uptime, suffix=False)} ago`\n"
            ""
        ]

        if psutil:
            try:
                proc = psutil.Process()

                with proc.oneshot():
                    try:
                        mem = proc.memory_full_info()
                        summary.append(f"Using `{natural_size(mem.rss)} physical memory` and "
                                       f"`{natural_size(mem.vms)} virtual memory`, "
                                       f"`{natural_size(mem.uss)}` of which unique to this process.")
                    except psutil.AccessDenied:
                        pass

                    try:

                        summary.append(f"Utilizing `{len(self.bot.commandss)} command(s)`.")
                    except psutil.AccessDenied:
                        pass

                    summary.append("")  # blank line
            except psutil.AccessDenied:
                summary.append(
                    "psutil is installed, but this process does not have high enough access rights "
                    "to query process information."
                )
                summary.append("")  # blank line

        cache_summary = f"`{len(self.bot.guilds):,} guild(s)` and `{len(self.bot.users):,} user(s)`"

        shard_ids = ', '.join(str(i) for i in self.bot.shards.keys())
        summary.append(
            f"This bot is sharded (Shards {shard_ids} of {self.bot.shard_count})"
            f" and can see {cache_summary}."
        )

        summary.append(f"**Average websocket latency: {round(self.bot.latency * 1000, 2)}ms**")

        e = Embed(
            description="\n".join(summary)
        ).set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=e)


    @command(
        name="userinfo",
        aliases=[
            "whois", 
            "ui", 
            "user"
        ]
    )
    async def userinfo(
        self: "Miscellaneous", 
        ctx: Context, 
        *, 
        member: Member | User = Author
    ):
        await ctx.typing()

        e = Embed()  
        if isinstance(member, Member): 
            e.description = ""
            e.set_author(
                name=f"{member}", 
                icon_url=member.display_avatar.url
            )
            e.add_field(
                name="dates", 
                value=(
                    f"**joined:** {format_dt(member.joined_at, "D")}\n"
                    f"**created:** {format_dt(member.created_at, "D")}\n"
                    f"{f'**boosted:** {format_dt(member.premium_since, "D")}' if member.premium_since else ''}"
                ),
                inline=False
            )

            roles = member.roles[1:][::-1]
        
            if len(roles) > 0: 
                e.add_field(
                    name=f"roles ({len(roles)})", 
                    value=' '.join([r.mention for r in roles]) 
                    if len(roles) < 5 
                    else ' '.join([r.mention for r in roles[:4]]) 
                    + f" ... and {len(roles)-4} more"
                )

            elif isinstance(member, User): 
                e.add_field(name="dates", value=f"**created:** {format_dt(member.created_at, "D")}", inline=False)  

            e.set_thumbnail(url=member.display_avatar.url)
            try: e.set_footer(text='ID: ' + str(member.id) + f" | {len(member.mutual_guilds)} mutual server(s)")
            except: e.set_footer(text='ID: ' + str(member.id)) 
            await ctx.send(embed=e)
        
    @command(aliases=["support", "inv"])
    async def invite(
   self, 
   ctx
   ):
     avatar_url = self.bot.user.avatar.url
     embed = discord.Embed( 
     description="Add the bot in your server!")
     embed.set_author(name=self.bot.user.name, icon_url=f"{avatar_url}")
     button1 = discord.ui.Button(label="invite",  style=discord.ButtonStyle.url,  url=discord.utils.oauth_url(client_id=self.bot.user.id,  permissions=discord.Permissions.all()))
     view = View()
     view.add_item(button1)
     await ctx.reply(embed=embed, view=view)
        


async def setup(bot: Puke):
    await bot.add_cog(Miscellaneous(bot))
