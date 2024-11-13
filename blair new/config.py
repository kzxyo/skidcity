from typing import Tuple, List

__all__: Tuple[str, ...] = (
    "TOKEN",
    "PREFIX",
    "OWNER_IDS",
)

TOKEN: str = "OTEyMjY4MzU4NDE2NzU2ODE2.GKVyfs.wB38bR_e-UF3P1gDGIuXEE7j3CX4EJaOPAoM98"
PUBLIC_KEY: str = "8f7ecf0f061b6043297290d3af428e05952be0ddd62eacb1d1e5a12374120938"
APPLICATION_ID: int = 1285774777537007697
PREFIX: str = ","
SUPPORT: str = "https://discord.gg/blairbot"
OWNER_IDS: List[int] = [
    1083861728380584038,
    1114247260474196098,
    1107903478451408936,
]

class Database:
    DSN: str = (
        "postgresql://postgres.incpddplqzpbxmhdotvu:oOYk1rnF9RrathJQ@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )


class Redis:
    DB: int = 0
    HOST: str = "localhost"
    PORT: int = 6379


class Authorization:
    class Lastfm: ...
