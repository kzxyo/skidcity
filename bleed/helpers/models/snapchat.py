from typing import List, Literal, Optional

from pydantic import BaseModel


class SnapchatHighlight(BaseModel):
    type: Literal["image", "video"]
    url: str


class SnapchatProfile(BaseModel):
    url: str
    username: str
    display_name: str
    description: Optional[str]
    snapcode: str
    bitmoji: Optional[str]
    subscribers: Optional[int] = 0
    stories: List[SnapchatHighlight] = []
    highlights: List[SnapchatHighlight] = []
