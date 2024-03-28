# I DIDNT MAKE THIS ONE EITHER HEHEHEH

from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

from typing import Optional, List, Sequence

class plural:
    def __init__(self, value: int | List, number: bool = True, code: bool = False):
        self.value: int = len(value) if isinstance(value, list) else value
        self.number: bool = number
        self.code: bool = code

    def __format__(self, format_spec: str) -> str:
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if self.number:
            result = f"`{v}` " if self.code else f"{v} "
        else:
            result = ""

        if abs(v) != 1:
            result += plural
        else:
            result += singular

        return result


def human_join(seq: Sequence[str], delim: str = ", ", final: str = "or") -> str:
    size = len(seq)
    if size == 0:
        return ""

    if size == 1:
        return seq[0]

    if size == 2:
        return f"{seq[0]} {final} {seq[1]}"

    return delim.join(seq[:-1]) + f" {final} {seq[-1]}"

def humanize(
    dt: datetime,
    *,
    source: Optional[datetime] = None,
    accuracy: Optional[int] = 3,
    brief: bool = False,
    suffix: bool = True,
) -> str:
    if isinstance(dt, timedelta):
        dt = datetime.utcfromtimestamp(dt.total_seconds())

    now = source or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    if dt > now:
        delta = relativedelta(dt, now)
        output_suffix = ""
    else:
        delta = relativedelta(now, dt)
        output_suffix = " ago" if suffix else ""

    attrs = [
        ("year", "y"),
        ("month", "mo"),
        ("day", "d"),
        ("hour", "h"),
        ("minute", "m"),
        ("second", "s"),
    ]

    output = []
    for attr, brief_attr in attrs:
        elem = getattr(delta, attr + "s")
        if not elem:
            continue

        if attr == "day":
            weeks = delta.weeks
            if weeks:
                elem -= weeks * 7
                if not brief:
                    output.append(format(plural(weeks), "week"))
                else:
                    output.append(f"{weeks}w")

        if elem <= 0:
            continue

        if brief:
            output.append(f"{elem}{brief_attr}")
        else:
            output.append(format(plural(elem), attr))

    if accuracy is not None:
        output = output[:accuracy]

    if len(output) == 0:
        return "now"
    else:
        if not brief:
            return human_join(output, final="and") + output_suffix
        else:
            return "".join(output) + output_suffix

def human_timedelta(
    dt: datetime,
    *,
    source: Optional[datetime] = None,
    accuracy: Optional[int] = 3,
    brief: bool = False,
    suffix: bool = True,
) -> str:
    if isinstance(dt, timedelta):
        dt = datetime.utcfromtimestamp(dt.total_seconds())

    now = source or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    if dt > now:
        delta = relativedelta(dt, now)
        output_suffix = ""
    else:
        delta = relativedelta(now, dt)
        output_suffix = " ago" if suffix else ""

    attrs = [
        ("year", "y"),
        ("month", "mo"),
        ("day", "d"),
        ("hour", "h"),
        ("minute", "m"),
        ("second", "s"),
    ]

    output = []
    for attr, brief_attr in attrs:
        elem = getattr(delta, attr + "s")
        if not elem:
            continue

        if attr == "day":
            weeks = delta.weeks
            if weeks:
                elem -= weeks * 7
                if not brief:
                    output.append(format(plural(weeks), "week"))
                else:
                    output.append(f"{weeks}w")

        if elem <= 0:
            continue

        if brief:
            output.append(f"{elem}{brief_attr}")
        else:
            output.append(format(plural(elem), attr))

    if accuracy is not None:
        output = output[:accuracy]

    if len(output) == 0:
        return "now"
    else:
        if not brief:
            return human_join(output, final="and") + output_suffix
        else:
            return "".join(output) + output_suffix
