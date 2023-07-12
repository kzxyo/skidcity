from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Tuple, Type

from discord.ext import commands
from jishaku.flags import Flags
from jishaku.repl import Scope

if TYPE_CHECKING:
    from ..lair import Lair


__all__: Tuple[str, ...] = ("Wrench",)


class Wrench(commands.Cog):
    if TYPE_CHECKING:
        emoji: Optional[str]
        brief: Optional[str]
        hidden: bool

    __slots__: Tuple[str, ...] = ("bot", "hidden", "brief", "emoji")

    def __init_subclass__(cls: Type[Wrench], **kwargs: Any) -> None:
        cls.emoji = kwargs.pop("emoji", None)
        cls.brief = kwargs.pop("brief", None)
        cls.hidden = kwargs.pop("hidden", False)
        return super().__init_subclass__(**kwargs)

    def __init__(self, bot: Lair, *args: Any, **kwargs: Any) -> None:
        self.bot: Lair = bot
        self._scope = Scope()
        self.last_result: Any = None
        self.retain = Flags.RETAIN
        super().__init__(*args, **kwargs)