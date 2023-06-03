from __future__ import annotations
import logging
from time import time

import asyncio
import logging
import os
import queue
import sys
import threading
import time

from limits import parse, strategies
from loguru import logger

LOG_LEVEL = os.getenv("LOG_LEVEL") or "INFO"

LOG_LOCK = threading.Lock()
from limits import storage

import coloredlogs,asyncio


def fitler_log(record):
    if error := record.get("exception"):
        if type(error) == asyncio.CancelledError:
            return False
    return True


def hook():
    pass


def print_chunk(msg):
    print(msg, file=sys.stderr, end="", flush=True)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        from loguru import logger

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class AsyncLogEmitter(object):
    def __init__(self, name=None) -> None:

        self.name = name
        self.queue = queue.SimpleQueue()
        self.thread = threading.Thread(target=self.runner)
        self.thread.daemon = True
        self.thread.start()

    def test(self):
        while not self.window.test(self.per_sec, "global", "log"):
            time.sleep(0.01)
        self.window.hit(self.per_sec, "global", "log")

    def runner(self):
        discards = False
        self.per_sec = parse("55/second")
        self.storage = storage.MemoryStorage()
        self.window = strategies.MovingWindowRateLimiter(self.storage)
        while True:
            msg: str = self.queue.get()
            if self.name:
                msg = msg.replace("MainThread", self.name)

            while self.queue.qsize() > 250:
                if not discards:
                    logger.warning("Queue is at max! - Supressing logging to prevent high CPU blockage.")
                    discards = True
                msg = self.queue.get()
            discards = False
            self.test()
            print(msg, file=sys.stderr, end="", flush=True)

    def emit(self, msg: str):
        self.queue.put(msg)


def make_dask_sink(name=None, log_emitter=None):

    if log_emitter:
        logger.info(log_emitter)
        emitter = log_emitter

    else:
        _emitter = AsyncLogEmitter(name=name)
        logger.info(_emitter.queue)
        emitter = _emitter.emit

    logger.configure(
        handlers=[
            dict(
                sink=emitter,
                colorize=True,
                backtrace=True,
                enqueue=False,
                level=LOG_LEVEL,
                filter=fitler_log,
                diagnose=True,
                catch=True,
                format="<le>{time:HH:mm:ss.SSS}</le>|<ly>{thread.name}</ly> |<level>{level:<7}</level>|<cyan>{name}</cyan>(<cyan>{function}</cyan>:<cyan>{line}</cyan>) <level>{message}</level>",
            )
        ]
    )
    logger.level(name="DEBUG", color="<magenta>")
    intercept = InterceptHandler()
    logging.basicConfig(handlers=[intercept], level=LOG_LEVEL, force=True)
    logging.captureWarnings(True)
    logger.success("Logger recofigured")
    logger.disable("distributed.utils")
    return emitter, logger