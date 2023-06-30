from typing import Optional

from pydantic import BaseModel


class TikTokProfileStatistics(BaseModel):
    verified: Optional[bool] = False
    likes: Optional[str] = "0"
    followers: Optional[str] = "0"
    following: Optional[str] = "0"


class TikTokProfile(BaseModel):
    url: str
    username: str
    display_name: str
    description: Optional[str]
    avatar_url: str
    statistics: TikTokProfileStatistics = TikTokProfileStatistics()
