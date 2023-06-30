from discord.ext.commands import Flag

from helpers.flags import BleedFlags


class Parameters(BleedFlags):
    self_destruct: int = Flag(
        aliases=["delete_after"],
        default=None,
    )
