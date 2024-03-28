from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime
from discord import Attachment as DiscordAttachment
class Author(BaseModel):
    name: str
    id: int
    discriminator: str
    bot: bool
    nick: Optional[str]
    avatar: Optional[HttpUrl]
    
    def __init__(self, **data):
        super().__init__(**data)

class Channel(BaseModel):
    id: int
    name: str
    position: int
    category_id: Optional[int]
    
    def __init__(self, **data):
        super().__init__(**data)

class Guild(BaseModel):
    id: int
    name: str
    chunked: bool
    member_count: int
    
    def __init__(self, **data):
        super().__init__(**data)

class Field(BaseModel):
    name: Optional[str]
    value: Optional[str]

class Snipe(BaseModel):
    guild: Guild
    channel: Channel
    author: Author
    attachments: List[Dict]
    stickers: List[str]
    embeds: List[Dict]
    content: str
    timestamp: float
    id: int
    
    def __init__(self, **data):
        super().__init__(**data)
