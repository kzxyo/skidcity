from discord import Role
from discord.ext.commands import RoleConverter

from helpers.managers import Context


class Role(RoleConverter):
    async def convert(self, ctx: Context, argument: str) -> Role:
        return await super().convert(ctx, argument)
