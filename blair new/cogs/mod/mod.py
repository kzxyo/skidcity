import asyncio

from discord import Member, User, Message, NotFound
from discord.ext.commands import Range, Cog, command, has_permissions, group

from typing import Optional

from tools.blair import Blair
from tools.discord import Context


class Mod(Cog, name="Moderation"):
    def __init__(self, bot: "Blair") -> None:
        self.bot: Blair = bot

    @group(name="ban", aliases=["b", "deport"], invoke_without_command=True)
    @has_permissions(ban_members=True)
    async def ban(
        self: "Mod",
        ctx: Context,
        user: Member | User,
        history: Optional[Range[int, 0, 7]] = None,
        *,
        reason: str = "No reason",
    ) -> Optional[Message]:
        """
        Ban a member from the guild.
        """

        await ctx.guild.ban(
            user,
            delete_message_days=history or 0,
            reason=f"{ctx.author} / {reason}",
        )

        return await ctx.check()
    
    @ban.command(name="reason", aliases=["why", "rzn", "rsn"])
    @has_permissions(ban_members=True)
    async def ban_reason(
        self: "Mod",
        ctx: Context,
        user: User
    ) -> Message:
        """
        View the reasoning behind a user's ban.
        """

        bans = [entry async for entry in ctx.guild.bans()]
        entry = next((b for b in bans if b.user.id == user.id), None)

        if not entry:
            return await ctx.respond(f"{user.name} isn't banned from the server.")
        
        return await ctx.respond(f"{user.name} was banned with the reasoning: `{entry.reason}`")
    
    @ban.group(name="pardon", aliases=["revoke", "forgive", "remove", "rm"])
    @has_permissions(ban_members=True)
    async def ban_pardon(
        self: "Mod",
        ctx: Context,
        user: User
    ) -> Message:
        """
        Unban a user.
        """

        try:
            await ctx.guild.unban(user, reason=f"unbanned by {ctx.author.name}")
            return await ctx.check()
        except NotFound:
            return await ctx.respond(f"{user.name} isn't banned from the server.")
        
    @ban_pardon.group(name="all", aliases=["everyone"])
    @has_permissions(ban_members=True)
    async def ban_pardon_all(
        self: "Mod",
        ctx: Context
    ) -> Message:
        """
        Unbans **every** user from the guild.
        Caution is advised when running this command.
        """

        users = [entry.user async for entry in ctx.guild.bans()]

        amt = await ctx.respond(f"Unbanning **{len(users):,}, please wait.")
        await asyncio.gather(
            *[
                ctx.guild.unban(entry, reason=f"{ctx.author.name} / mass pardon")
                for entry in users
            ]
        )

        embed = amt.embeds[0]
        embed.description = f"Unbanned **{len(users):,}** from your server!"

        return await amt.edit(embed=embed)
