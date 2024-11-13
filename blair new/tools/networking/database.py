from json import dumps, loads
from typing import Any, Optional

import asyncpg

import config
from tools.discord import logging

log = logging.getLogger(__name__)


class Record(asyncpg.Record):
    def __getattr__(self, attr: str):
        return self.get(attr)


async def setup(pool: asyncpg.Pool) -> asyncpg.Pool:
    with open("tools/networking/schema.sql", "r", encoding="UTF-8") as buffer:
        schema = buffer.read()
        await pool.execute(schema)

    return pool


async def connect():
    pool = await asyncpg.create_pool(dsn=config.Database.DSN, statement_cache_size=0)
    if not pool:
        raise Exception("Could not establish a connection to the PostgresSQL database!")

    return await setup(pool)
