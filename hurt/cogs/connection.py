import discord
from discord.ext import tasks, commands
import datetime
import time


class connectin(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.start_time = time.time()
        self.status_message = None
        self.update_status.start()

    @commands.command(
        name="connection", description="get my connection", aliases=["stat"]
    )
    @commands.guild_only()
    @commands.is_owner()
    @commands.cooldown(1, 60, commands.cooldowns.BucketType.user)
    async def connection(self, ctx):
        self.status_message = await ctx.send(embed=self.create_status_embed())

    @tasks.loop(seconds=10)  # dont put it under 5 bcuz u can get rate limited
    async def update_status(self):
        if self.status_message:
            try:
                embed = (
                    self.create_status_embed()
                )  # Refactored to check if the embed was actually different or if it was the exact same.
                if embed != self.status_message.embeds[0]:
                    await self.status_message.edit(embed=self.create_status_embed())
            except Exception as e:
                print(f"Failed to update status: {e}")

    def create_status_embed(self):
        current_time = (
            datetime.datetime.now().timestamp()
        )  # Refactored this to use datetime instead of io bound time
        uptime_seconds = int(round(current_time - self.start_time))
        uptime_string = str(datetime.timedelta(seconds=uptime_seconds))

        latency = self.bot.latency * 1000

        guild_count = len(self.bot.guilds)

        user_count = sum(
            list(self.bot.get_all_members())
        )  # Refactored this for a shortcut method

        version_number = "1.5.2"

        shard_count = self.bot.shard_count

        embed = discord.Embed(
            title="<:clock:1117637386218782801> `hurt's status`", color=0xFFB6C1
        )
        embed.add_field(
            name="<:dot:1117638189453164674> Latency",
            value=f"> `{round(latency)}ms`",
            inline=True,
        )
        embed.add_field(
            name="<:ping:1117637470440390706> Shards",
            value=f"> `{shard_count}`",
            inline=False,
        )
        embed.add_field(
            name="<:server:1117637419869667470> Servers",
            value=f"> `{guild_count}`",
            inline=False,
        )
        embed.add_field(
            name="<:server:1117637419869667470> Users",
            value=f"> `{user_count}`",
            inline=False,
        )
        embed.add_field(
            name="<:clock:1117637386218782801> Uptime",
            value=f"> `{uptime_string}`",
            inline=False,
        )
        embed.add_field(
            name="<:update:1117637514912612352> Version",
            value=f"> `{version_number}`",
            inline=False,
        )

        return embed


async def setup(bot):
    await bot.add_cog(connectin(bot))
