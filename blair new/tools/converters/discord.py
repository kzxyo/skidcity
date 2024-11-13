from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from discord import Member, Role
from discord.ext.commands import (
    BadArgument,
    CommandError,
    MemberConverter,
    RoleConverter,
    RoleNotFound,
)
from discord.utils import find

if TYPE_CHECKING:
    from tools.discord import Context


class FuzzyRole(RoleConverter):
    async def convert(self, ctx: Context, argument: str) -> Role:
        with suppress(CommandError, BadArgument):
            return await super().convert(ctx, argument)

        role = find(
            lambda r: (
                r.name.lower() == argument.lower() or r.name.lower() in argument.lower()
            ),
            ctx.guild.roles,
        )
        if not role:
            raise RoleNotFound(argument)

        return role


class StrictRole(FuzzyRole):
    check_dangerous: bool
    check_integrated: bool
    allow_default: bool

    def __init__(
        self,
        *,
        check_dangerous: bool = False,
        check_integrated: bool = True,
        allow_default: bool = False,
    ) -> None:
        self.check_dangerous = check_dangerous
        self.check_integrated = check_integrated
        self.allow_default = allow_default
        super().__init__()

    @staticmethod
    def dangerous(role: Role) -> bool:
        return any(
            value
            and permission
            in (
                "administrator",
                "kick_members",
                "ban_members",
                "manage_guild",
                "manage_roles",
                "manage_channels",
                "manage_emojis",
                "manage_webhooks",
                "manage_nicknames",
                "mention_everyone",
            )
            for permission, value in role.permissions
        )

    async def check(self, ctx: Context, role: Role) -> None:
        bot = ctx.guild.me
        author = ctx.author
        if self.check_dangerous and self.dangerous(role):
            raise BadArgument(
                f"{role.mention} is a dangerous role and cannot be assigned!"
            )

        if self.check_integrated and role.managed:
            raise BadArgument(
                f"{role.mention} is an integrated role and cannot be assigned!"
            )

        if not self.allow_default and role.is_default():
            raise BadArgument(
                f"{role.mention} is the default role and cannot be assigned!"
            )

        elif role >= bot.top_role and bot.id != ctx.guild.owner_id:
            raise BadArgument(f"{role.mention} is higher than my highest role!")

        elif role >= author.top_role and author.id != ctx.guild.owner_id:
            raise BadArgument(f"{role.mention} is higher than your highest role!")

    async def convert(self, ctx: Context, argument: str) -> Role:
        role = await super().convert(ctx, argument)

        await self.check(ctx, role)
        return role


class TouchableMember(MemberConverter):
    """
    Check if a member is punishable.
    """

    allow_author: bool

    def __init__(self, *, allow_author: bool = False) -> None:
        self.allow_author = allow_author
        super().__init__()

    async def check(self, ctx: Context, member: Member) -> None:
        bot = ctx.guild.me
        author = ctx.author
        command = ctx.command.qualified_name
        if author == member and not self.allow_author:
            raise BadArgument(f"You're not allowed to **{command}** yourself!")

        elif (
            member.top_role >= bot.top_role
            and bot.id != ctx.guild.owner_id
            and (member != bot if command == "nickname" else True)
        ):
            raise BadArgument(f"{member.mention} is higher than my highest role!")

        elif member.top_role >= author.top_role and author.id != ctx.guild.owner_id:
            raise BadArgument(
                f"You're not allowed to **{command}** {member.mention} due to hierarchy!"
            )

    async def convert(self, ctx: Context, argument: str) -> Member:
        member = await super().convert(ctx, argument)

        await self.check(ctx, member)
        return member
