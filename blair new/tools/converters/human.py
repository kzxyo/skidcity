from datetime import datetime, timedelta
from humanize import naturaltime


def natural_duration(value: float, ms: bool = True) -> str:
    h = int((value / (1000 * 60 * 60)) % 24) if ms else int((value / (60 * 60)) % 24)
    m = int((value / (1000 * 60)) % 60) if ms else int((value / 60) % 60)
    s = int((value / 1000) % 60) if ms else int(value % 60)

    result = ""
    if h:
        result += f"{h}:"

    result += f"{m}:" if m else "00:"
    result += f"{str(s).zfill(2)}" if s else "00"

    return result


def natural_timedelta(
    value: datetime | timedelta | float, suffix: bool = False, **kwargs
) -> str:
    output = naturaltime(value, **kwargs)
    return output if suffix else output.removesuffix("ago")
