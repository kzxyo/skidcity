import asyncio, contextlib
from typing import NamedTuple, Optional
from .context import Context


class CommandTask(NamedTuple):
    index: int
    ctx: Context
    task: Optional[asyncio.Task]


@contextlib.contextmanager
def submit(ctx: Context):

    try:
        current_task = asyncio.current_task()
    except RuntimeError:
        current_task = None

    cmdtask = CommandTask(len(ctx.bot.tasks.setdefault(ctx.guild.id, list())), ctx, current_task)

    ctx.bot.tasks[ctx.guild.id].append(cmdtask)

    try:
        yield cmdtask
    finally:
        if cmdtask in ctx.bot.tasks[ctx.guild.id]:
            ctx.bot.tasks[ctx.guild.id].remove(cmdtask)