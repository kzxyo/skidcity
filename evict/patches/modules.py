from dataclasses import dataclass
import datetime
import asyncpg

@dataclass
class AntiNukeModule:
    module: str
    punishment: str # Ban, Warn and Kick
    threshold: int
    toggled: bool
    
    @classmethod
    async def from_database(cls, db: asyncpg.Connection, guild_id: int, module: str):
        data = await db.fetchrow('SELECT * FROM antinuke_modules WHERE guild_id = $1 AND module = $2', guild_id, module)
        if not data: return None
        return cls(
            module=module,
            punishment=data['punishment'],
            threshold=data['threshold'],
            toggled=data['toggled']
        )
    
    async def update(self, db: asyncpg.Connection, guild_id: int):
        return await db.execute('UPDATE antinuke_modules SET punishment = $1, threshold = $2, toggled = $3 WHERE guild_id = $4 AND module = $5', self.punishment, self.threshold, self.toggled, guild_id, self.module)
        
@dataclass
class AntiNukeUser:
    module: str
    user_id: int
    last_action: datetime.datetime
    amount: int