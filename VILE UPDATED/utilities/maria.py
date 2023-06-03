import asyncio, aiomysql
from . import config
from typing import Any
from typing_extensions import Self


class MariaDB:
    def __init__(self):
        self.pool = None

    
    async def __aenter__(self) -> Self:
        if self.pool is None:
            await self.initialize_pool()
        return self

    
    async def __aexit__(self, *_) -> None:
        return await self.cleanup()


    async def wait_for_pool(self) -> bool:

        num = 0
        while self.pool is None and num < 10:
            await asyncio.sleep(1)
            num += 1

        if self.pool is None:
            return False

        return True


    async def initialize_pool(self) -> None:
        credentials = config.database
        data = {'db': credentials.db, 'host': credentials.host, 'port': credentials.port, 'user': credentials.user, 'password': 'Glory9191'}
        self.pool = await aiomysql.create_pool(**data, maxsize=10, autocommit=True, echo=False)


    async def cleanup(self) -> None:
        self.pool.close()
        return await self.pool.wait_closed()


    async def execute(self, statement: str, *params: Any, one_row: bool = False, one_value: bool = False, as_list: bool = False) -> Any:
        
        if await self.wait_for_pool():
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(statement, params)
                    data = await cursor.fetchall()

            if data is None:
                return tuple()

            if data:
                if one_value:
                    return data[0][0]

                if one_row:
                    return data[0]

                if as_list:
                    return [row[0] for row in data]

                return data

            return tuple()
        
        return tuple()


    async def fetchrow(self, statement: str, *params: Any) -> Any:
        return await self.execute(statement, *params, one_row=True)
    

    async def fetchval(self, statement: str, *params: Any) -> Any:
        return await self.execute(statement, *params, one_value=True)


    async def fetch(self, statement: str, *params: Any) -> Any:
        return await self.execute(statement, *params, as_list=True)
