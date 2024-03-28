from structure.managers import ClientSession
from structure.config import API


from typing import Any, Optional

from munch import Munch
from pydantic import BaseModel

class Profile(BaseModel):
    url: str
    username: str
    display_name: Optional[str]
    avatar: str
    country: Optional[str] = "Unknown"
    tracks: int
    artists: int
    albums: int
    registered: int
    pro: bool
    scrobbles: int

class FMHandler():

    async def request(
        self: "FMHandler", 
        slug: Optional[str] = None, 
        **params: Any
    ) -> Munch:
        data: Munch = await ClientSession().request(
            "http://ws.audioscrobbler.com/2.0/",
            params={
                "api_key": API.lastfm,
                "format": "json",
                **params,
            },
            slug=slug,
        )
        return data

    async def profile(
        self: "FMHandler",
        username: str,
    ) -> Profile:
    
        data = await self.request(
            method="user.getinfo",
            username=username,
            slug="user",
        )

        return Profile(
            url=data.url,
            username=data.name,
            display_name=data.realname,
            country=data.country if data.country != "None" else "Unknown",
            avatar=data.image[-1]["#text"],
            tracks=int(data.track_count),
            albums=int(data.album_count),
            artists=int(data.artist_count),
            scrobbles=int(data.playcount),
            registered=int(data.registered.unixtime),
            pro=data.subscriber == "1",
        )
        