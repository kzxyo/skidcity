from discord.ext.commands import FlagConverter


class BleedFlags(
    FlagConverter,
    case_insensitive=True,
    prefix="--",
    delimiter=" ",
):
    pass
