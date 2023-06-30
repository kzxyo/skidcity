from typing import List, Literal, Optional

from pydantic import BaseModel


class Module(BaseModel):
    status: Optional[bool] = False
    punishment: Optional[Literal["ban", "kick", "stripstaff", None]] = None
    threshold: Optional[int] = 3
    command: Optional[bool] = False


class Permission(BaseModel):
    type: Literal["grant", "remove"]
    punishment: Literal["ban", "kick", "stripstaff"]
    permission: str


class Configuration(BaseModel):
    guild_id: Optional[int] = None
    whitelist: List[int] = list()
    admins: List[int] = list()

    botadd: Module = Module()
    webhook: Module = Module()
    emoji: Module = Module()
    ban: Module = Module()
    kick: Module = Module()
    channel: Module = Module()
    role: Module = Module()
    permissions: List[Permission] = list()
