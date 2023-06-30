from discord import Member, User
from discord.ext.commands import MemberConverter, UserConverter

from helpers.managers import Context


class User(UserConverter):
    async def convert(self, ctx: Context, argument: str) -> User:
        return await super().convert(ctx, argument)


class Member(MemberConverter):
    async def convert(self, ctx: Context, argument: str) -> Member:
        return await super().convert(ctx, argument)
