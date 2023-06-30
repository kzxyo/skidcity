from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LastfmProfileInformation(BaseModel):
    registered: datetime
    country: Optional[str] = "Unknown"
    age: int
    pro: bool


class LastfmProfileLibrary(BaseModel):
    scrobbles: int
    artists: int
    albums: int
    tracks: int


class LastfmProfile(BaseModel):
    url: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    information: LastfmProfileInformation
    library: LastfmProfileLibrary
