from typing import Tuple, List

__all__: Tuple[str, ...] = (
    "TOKEN",
    "PREFIX",
    "OWNER_IDS",
)

TOKEN: str = "yeah"
PUBLIC_KEY: str = "yeah"
APPLICATION_ID: int = yeah
PREFIX: str = ","
SUPPORT: str = "https://discord.gg/bleed"
OWNER_IDS: List[int] = [
    1107903478451408936
]

class Database:
    DSN: str = (
        "yeah"
    )


class Redis:
    DB: int = 0
    HOST: str = "localhost"
    PORT: int = 6379


class Authorization:
    class Lastfm: ...
