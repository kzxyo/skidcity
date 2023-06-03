from __future__ import annotations

from redis.asyncio.lock import Lock

class RivalLock(Lock):
    pass
