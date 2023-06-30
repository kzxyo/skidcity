from typing import Literal

from discord.ext.commands import Flag, Range

from helpers.converters import Status
from helpers.flags import BleedFlags


class Parameters(BleedFlags):
    punishment: Literal["ban", "kick", "stripstaff"] = Flag(
        aliases=["action", "do"],
        default="kick",
    )
    threshold: Range[int, 1, 6] = 3
    command: Status = False
