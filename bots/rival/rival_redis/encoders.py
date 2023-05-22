from __future__ import annotations

import loguru as log
import orjson
from loguru import logger as log
from redis.asyncio.client import Pipeline as _Pipeline
from redis.commands.json.commands import JSONCommands


class JSONPipeline(JSONCommands, _Pipeline):
    """Pipeline for the module."""


class ORJSONDecoder:
    def __init__(self, **kwargs):
        # eventually take into consideration when deserializing
        self.options = kwargs

    def decode(self, obj):
        if isinstance(obj, int):
            return obj
        try:
            return orjson.loads(obj)
        except:
            log.exception("Redis JSON not load {}", obj)
            raise


class ORJSONEncoder:
    def __init__(self, **kwargs):
        # eventually take into consideration when serializing
        self.options = kwargs

    def encode(self, obj):
        # decode back to str, as orjson returns bytes
        try:
            return orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS).decode("utf-8")
        except:
            log.exception("Redis JSON could not decode {}", obj)
            raise
