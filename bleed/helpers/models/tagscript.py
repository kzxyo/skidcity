from typing import Dict, Optional

from discord import Embed
from discord.ui import View
from pydantic import BaseModel


class ScriptObject(BaseModel):
    script: str
    content: Optional[str]
    embed: Optional[Embed] = Embed()
    view: Optional[View]

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    @property
    def dump(self) -> Dict:
        return {
            "content": self.content,
            "embed": (self.embed or None),
            "view": self.view,
        }

    @property
    def type(self) -> str:
        return "embed" if self.embed else "text"

    def __init__(self, script, **data) -> "Script":
        data["script"] = script
        super().__init__(**data)

    def __bool__(self) -> bool:
        return bool(self.content or self.embed or self.view.children)

    def __str__(self) -> str:
        return self.script
