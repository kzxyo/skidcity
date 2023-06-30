from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RobloxStatistics(BaseModel):
    friends: Optional[int] = 0
    followers: Optional[int] = 0
    following: Optional[int] = 0


class RobloxProfile(BaseModel):
    url: str
    id: int
    username: str
    display_name: str
    description: Optional[str]
    avatar_url: str
    created_at: datetime
    last_online: Optional[datetime]
    presence: str
    badges: List[str]
    statistics: RobloxStatistics
