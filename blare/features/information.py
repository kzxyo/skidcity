from structure import Blare
from structure.managers import Context

from discord import Message, Embed, Role, Member, User, ButtonStyle
from discord.ui import View, Button
from discord.utils import format_dt
from discord.ext.commands import Cog, command, Author

from psutil import Process
from jishaku.math import natural_size

class Information(Cog):
    def __init__(self, bot: Blare):
        self.bot: Blare = bot
        self.psutil = Process()

    @command(
        name="botinfo",
        aliases=[
            'about',
            'bi'
        ]
    )
    async def botinfo(
        self: "Information",
        ctx: Context
    ) -> Message:
        """
        Get info on bot
        """
        summary = [
            f"Blare was created and maintained by <@950183066805092372> <@1188955485462872226> <@1137846765576540171> <@1107903478451408936>\n"
            f"> Blare was started {format_dt(self.bot.uptime, style='R')}\n"
            ""
        ]

        with self.psutil.oneshot():

            mem = self.psutil.memory_full_info()

            summary.append(f"Using `{natural_size(mem.rss)} physical & {natural_size(mem.vms)} virtual memory`")

            summary.append(f"Utilizing `{len(set(self.bot.walk_commands())) - 34} command(s)`.")
  
            summary.append("")

        summary.append(f"This bot can see `{len(self.bot.guilds):,} guild(s)` and `{len(self.bot.users):,} user(s)`.")

        summary.append(f"**Average websocket latency: {round(self.bot.latency * 1000, 2)}ms**")

        e = Embed(
            description="\n".join(summary)
        )
        e.set_thumbnail(url=self.bot.user.display_avatar)

        return await ctx.send(embed=e)

    @command(
        name="bots",
    )
    async def bots(
        self: "Information",
        ctx: Context,
    ) -> Message:
        """
        View all bots
        """

        if not (
            bots := filter(
                lambda member: member.bot,
                ctx.guild.members,
            )
        ):
            return await ctx.alert(f"No bots have been found in {ctx.guild.name}!")

        return await ctx.paginate(
            [
                f"{bot.mention}" 
                for bot in bots
            ],
            Embed(title=f"Bots in {ctx.guild.name}")
        )

    @command(
        name="members",
        aliases=['inrole']
    )
    async def members(
        self: "Information",
        ctx: Context,
        *,
        role: Role = None
    ) -> Message:
        """
        View all members in a role
        """


        role = role or ctx.author.top_role

        if not role.members:
            return await ctx.alert(f"No members in the role {role.mention}!")

        return await ctx.paginate(
            [
                f"{user.mention}" 
                for user in role.members
            ],
            Embed(title=f"Members in {role.name}")
        )

    @command(
        name="roles",
    )
    async def roles(
        self: "Information",
        ctx: Context,
    ) -> Message:
        """
        View all roles
        """


        if not (
            roles := reversed(
                ctx.guild.roles[1:]
            )
        ):
            return await ctx.alert(f"No roles have been found in {ctx.guild.name}!")

        return await ctx.paginate(
            [
                f"{role.mention}" 
                for role in roles
            ],
            Embed(title=f"Roles in {ctx.guild.name}")
        )
    
    @command(
        name="emojis",
        aliases=['emotes']
    )
    async def emojis(
        self: "Information",
        ctx: Context,
    ) -> Message:
        """
        View all emojis
        """


        if not ctx.guild.emojis:
            return await ctx.alert(f"No emojis have been found in {ctx.guild.name}!")

        return await ctx.paginate(
            [
                f"{emoji} [`{emoji.name}`]({emoji.url})"
                for emoji in ctx.guild.emojis
            ],
            Embed(title=f"Emojis in {ctx.guild.name}")
        )

    @command(
        name="stickers",
    )
    async def stickers(
        self: "Information",
        ctx: Context,
    ) -> Message:
        """
        View all stickers
        """


        if not ctx.guild.stickers:
            return await ctx.alert(f"No stickers have been found in {ctx.guild.name}!")

        return await ctx.paginate(
            [
                f"[`{sticker.name}`]({sticker.url})"
                for sticker in ctx.guild.stickers
            ],
            Embed(title=f"Stickers in {ctx.guild.name}")
        )
    
    @command(
        name="invites",
    )
    async def invites(
        self: "Information",
        ctx: Context,
    ) -> Message:
        """
        View all invites
        """
        
        if not (
            invites := sorted(
                [
                    invite for invite in 
                    await ctx.guild.invites() 
                    if invite.expires_at
                ],
                key=lambda invite: invite.expires_at,
                reverse=True,
        )
        ):
            return await ctx.alert(f"No invites have been found in {ctx.guild.name}!")

        return await ctx.paginate(
                [
                    (
                        f"[`{invite.code}`]({invite.url}) expires "
                        + format_dt(
                            invite.expires_at,
                            style="R",
                        )
                    )
                    for invite in invites
                ],

            Embed(title=f"Invite in {ctx.guild.name}")
        )

    @command(
        name="avatar",
        aliases=[
            'av',
            'icon'
        ]
    )
    async def avatar(
        self: "Information",
        ctx: Context,
        *,
        user: Member | User = Author
    ) -> Message:
        """
        View a users avatar
        """

        view = View()

        view.add_item(
            Button(style=ButtonStyle.link, label='PNG', url=str(user.display_avatar.replace(size=4096, format='png')))
        )
        view.add_item(
            Button(style=ButtonStyle.link, label='JPG', url=str(user.display_avatar.replace(size=4096, format='jpg')))
        )
        view.add_item(
            Button(style=ButtonStyle.link, label='WEBP', url=str(user.display_avatar.replace(size=4096, format='webp')))
        )

        return await ctx.send(
            embed=Embed()
            .set_author(name=f"{user.name}'s avatar!")
            .set_image(url=user.display_avatar.url),
            view=view
        )
    
    @command(
        name="banner",
        aliases=[
            'ub',
            'userbanner'
        ]
    )
    async def banner(
        self: "Information",
        ctx: Context,
        *,
        user: Member | User = Author
    ) -> Message:
        """
        View a users banner
        """
        user = await self.bot.fetch_user(user.id)
        if not user.banner:
            return await ctx.alert(
                "You don't have a banner set!" 
                if user == ctx.author else 
                f"{user} does not have a banner set!"
            )
        
        view = View()

        view.add_item(
            Button(style=ButtonStyle.link, label='PNG', url=str(user.banner.replace(size=4096, format='png')))
        )
        view.add_item(
            Button(style=ButtonStyle.link, label='JPG', url=str(user.banner.replace(size=4096, format='jpg')))
        )
        view.add_item(
            Button(style=ButtonStyle.link, label='WEBP', url=str(user.banner.replace(size=4096, format='webp')))
        )

        return await ctx.send(
            embed=Embed()
            .set_author(name=f"{user.name}'s banner!")
            .set_image(url=user.banner),
            view=view
        )
    
async def setup(bot: Blare) -> None:
    await bot.add_cog(Information(bot))
