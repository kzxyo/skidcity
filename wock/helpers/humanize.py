from datetime import timedelta

import humanize


def size(value: int):
    return humanize.naturalsize(value).replace(" ", "")


def time(value: timedelta, short: bool = False):
    value = humanize.precisedelta(value, format="%0.f").replace("ago", "").replace("from now", "")
    if value.endswith("s") and value[:-1].isdigit() and int(value[:-1]) == 1:
        value = value[:-1]

    if short:
        value = " ".join(value.split(" ", 2)[:2])
        if value.endswith(","):
            value = value[:-1]
        return value

    return value


def ordinal(value: int):
    return humanize.ordinal(value)


def comma(value: int):
    return humanize.intcomma(value)


def percentage(small: int, big: int = 100):
    return "%.0f%%" % int((small / big) * 100)
