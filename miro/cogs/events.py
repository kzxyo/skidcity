import discord
from discord.ext import commands
from colorama import Fore, Style

class events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel_count = len(guild.text_channels) + len(guild.voice_channels)
        invite = "N/A"
        if guild.vanity_url is not None:
            invite = f"[{guild.vanity_url_code}]({guild.vanity_url})"
        e = discord.Embed(
            color=0x4c5264,
            title=f"{guild.name} ({guild.id})",
            description=f'Created {discord.utils.format_dt(guild.created_at, style="F")}',
        )
        e.add_field(
            name="Members",
            value=f"**Total:** {guild.member_count}\n"
            f"**Humans:** {len(list(filter(lambda m: not m.bot, guild.members)))}\n"
            f"**Bots:** {len(list(filter(lambda m: m.bot, guild.members)))}",
        )
        e.add_field(
            name="Channels",
            value=f"**Total:** {channel_count}\n"
            f"**Text:** {len(guild.text_channels)}\n"
            f"**Voice:** {len(guild.voice_channels)}",
        )
        e.add_field(
            name="Other",
            value=f"**Categories:** {len(guild.categories)}\n"
            f"**Roles:** {len(guild.roles)}\n"
            f"**Emotes:** {len(guild.emojis)}",
        )
        e.add_field(
            name="Boost",
            value=f"**Level:** {guild.premium_tier}/3\n"
            f"**Boosts:** {guild.premium_subscription_count}",
        )
        e.add_field(
            name="Information",
            value=f"**Verification:** {guild.verification_level}\n"
            f"**Vanity:** {invite}",
        )
        e.set_footer(text=f"{guild.owner} ({guild.owner_id})")
        e.set_author(
            name=f"{self.bot.user.name}", icon_url=self.bot.user.display_avatar
        )
        channel = self.bot.get_channel(1109428406929608754)
        await channel.send("**Joined:**")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        channel_count = len(guild.text_channels) + len(guild.voice_channels)
        invite = "N/A"
        if guild.vanity_url is not None:
            invite = f"[{guild.vanity_url_code}]({guild.vanity_url})"
        e = discord.Embed(
            color=0x4c5264,
            title=f"{guild.name} ({guild.id})",
            description=f'Created {discord.utils.format_dt(guild.created_at, style="F")}',
        )
        e.add_field(
            name="Members",
            value=f"**Total:** {guild.member_count}\n"
            f"**Humans:** {len(list(filter(lambda m: not m.bot, guild.members)))}\n"
            f"**Bots:** {len(list(filter(lambda m: m.bot, guild.members)))}",
        )
        e.add_field(
            name="Channels",
            value=f"**Total:** {channel_count}\n"
            f"**Text:** {len(guild.text_channels)}\n"
            f"**Voice:** {len(guild.voice_channels)}",
        )
        e.add_field(
            name="Other",
            value=f"**Categories:** {len(guild.categories)}\n"
            f"**Roles:** {len(guild.roles)}\n"
            f"**Emotes:** {len(guild.emojis)}",
        )
        e.add_field(
            name="Boost",
            value=f"**Level:** {guild.premium_tier}/3\n"
            f"**Boosts:** {guild.premium_subscription_count}",
        )
        e.add_field(
            name="Information",
            value=f"**Verification:** {guild.verification_level}\n"
            f"**Vanity:** {invite}",
        )
        e.set_footer(text=f"{guild.owner} ({guild.owner_id})")
        e.set_author(
            name=f"{self.bot.user.name}", icon_url=self.bot.user.display_avatar
        )
        channel = self.bot.get_channel(1109428406929608754)
        await channel.send("**Left:**")
        await channel.send(embed=e)


async def sendmsg(self, ctx, content, embed, view, file, allowed_mentions):
    if ctx.guild is None:
        return
    try:
        await ctx.reply(
            content=content,
            embed=embed,
            view=view,
            file=file,
            allowed_mentions=allowed_mentions,
            mention_author=False,
        )
    except:
        await ctx.send(
            content=content,
            embed=embed,
            view=view,
            file=file,
            allowed_mentions=allowed_mentions,
        )


class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.bot.process_commands(after)


async def setup(bot) -> None:
    await bot.add_cog(events(bot))
