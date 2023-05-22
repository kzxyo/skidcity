from .lock import *
from .redis import *


def get_redis() -> RivalRedis:
    
    from rival.redis.redis import GLOBAL_REDIS

    return GLOBAL_REDIS["client"]


def redis_client() -> RivalRedis:
    return get_redis()
