import re

from discord.ext.commands import CommandError, Converter
from typing import Optional, List, Dict
from datetime import timedelta

from tools.discord import Context

DURATION_PATTERN = r"\s?".join(
    [
        r"((?P<years>\d+?)\s?(years?|y))?",
        r"((?P<months>\d+?)\s?(months?|mo))?",
        r"((?P<weeks>\d+?)\s?(weeks?|w))?",
        r"((?P<days>\d+?)\s?(days?|d))?",
        r"((?P<hours>\d+?)\s?(hours?|hrs|hr?))?",
        r"((?P<minutes>\d+?)\s?(minutes?|mins?|m(?!o)))?",
        r"((?P<seconds>\d+?)\s?(seconds?|secs?|s))?",
    ]
)


class Duration(Converter[timedelta]):
    def __init__(
        self: "Duration",
        min: Optional[timedelta] = None,
        max: Optional[timedelta] = None,
        units: Optional[List[str]] = None,
    ):
        self.min = min
        self.max = max
        self.units = units or [
            "weeks",
            "days",
            "hours",
            "minutes",
            "seconds",
        ]

    async def convert(self: "Duration", ctx: Context, argument: str) -> timedelta:
        if not (matches := re.fullmatch(DURATION_PATTERN, argument, re.IGNORECASE)):
            raise CommandError("The duration provided didn't pass validation!")

        units: Dict[str, int] = {
            unit: int(amount) for unit, amount in matches.groupdict().items() if amount
        }
        for unit in units:
            if unit not in self.units:
                raise CommandError(f"The unit `{unit}` is not valid for this command!")

        try:
            duration = timedelta(**units)
        except OverflowError as exc:
            raise CommandError("The duration provided is too long!") from exc

        if self.min and duration < self.min:
            raise CommandError("The duration provided is too short!")

        if self.max and duration > self.max:
            raise CommandError("The duration provided is too long!")

        return duration
