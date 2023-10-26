import discord
from discord.ext.commands import (
    Cog,
    group,
    command,
    Context,
)
from discord.webhook import Webhook
from tools.bot import DiscordBot
from tools.context import HarmContext

class Welcome(Cog):
    def __init__(self: "Welcome", bot: DiscordBot, *args, **kwargs) -> None:
        self.bot: Margiela = bot

    @Cog.listener(name="on_member_join")
    async def MemberJoin(
        self: "Welcome", member: discord.Member | discord.User
    ) -> None:
        channel = self.bot.get_channel(1156514304347090974)
        await channel.send(
            content=f"{member.mention}",
            embeds=[
                discord.Embed(
                    title=member,
                    description=(
                        "welcome\n"
                        "boost & rep for perks <3\n"
                        "read <#1155904142506733648> & <#1155904509437018112>\n"
                        "be active in <#1156514304347090974> 4 perms"
                    ),
                    color=0x34343C,
                ).set_thumbnail(
                    url=member.display_avatar.url,
                )
            ],
        )


async def setup(bot):
    await bot.add_cog(Welcome(bot))