from async_timeout import timeout as Timeout

from typing import (
    Dict,
    Optional
)

from typing_extensions import NoReturn

from ... import literals
from ...vile import HTTPClient

from .errors import HTTPException


class LastFM:
    def __init__(self: "LastFM") -> NoReturn:
        self.__BASE_URL = "http://ws.audioscrobbler.com/2.0/"
        self.__session = HTTPClient(proxy=False)
    
    
    async def __request(
        self: "LastFM", 
        method: str, 
        params: Optional[dict] = None, 
    ) -> dict:
        
        params.update({
            "api_key": literals.api.lastfm,
            "format": "json"
        })
        
        async with Timeout(15):
            data = await self.__session.get(
                self.__BASE_URL, 
                command_error=False, 
                params={
                    "method": method,
                    **params
                }
            )
            
        if "error" in data:
            raise HTTPException(data["message"])
        
        return data
    
    
    async def get_artist_info(self: "LastFM", artist: str) -> Dict:
        data = await self.__request(
            method="artist.getinfo", 
            params={
                "artist": artist
            }
        )
        
        return data["artist"]
    
    
    async def get_artist_top_tracks(
        self: "LastFM", 
        artist: str,
        limit: Optional[int] = 10
    ) -> Dict:
        data = await self.__request(
            method="artist.gettoptracks", 
            params={
                "artist": artist,
                "limit": limit
            }
        )
        
        return data["toptracks"]["track"]
    
    
    async def get_artist_top_albums(
        self: "LastFM", 
        artist: str,
        limit: Optional[int] = 10
    ) -> Dict:
        data = await self.__request(
            method="artist.gettopalbums", 
            params={
                "artist": artist,
                "limit": limit
            }
        )
        
        return data["topalbums"]["album"]
    
    
    async def find_artist(self: "LastFM", artist: str) -> Dict:
        data = await self.__request(
            method="artist.search", 
            params={
                "artist": artist
            }
        )
        
        return data["results"]["artistmatches"]["artist"]
    
    
    async def get_similar_artists(
        self: "LastFM", 
        artist: str,
        limit: Optional[int] = 10
    ) -> Dict:
        data = await self.__request(
            method="artist.getsimilar", 
            params={
                "artist": artist,
                "limit": limit
            }
        )
        
        return data["similarartists"]["artist"]
    
    
    async def get_track_info(
        self: "LastFM", 
        track: str, 
        artist: str
    ) -> Dict:
        data = await self.__request(
            method="track.getInfo", 
            params={
                "artist": artist,
                "track": track
            }
        )
        
        return data["track"]
    
    
    async def find_track(self: "LastFM", track: str) -> Dict:
        data = await self.__request(
            method="track.search", 
            params={
                "track": track
            }
        )
        
        return data["results"]["trackmatches"]["track"]


    async def get_track_lyrics(
        self: "LastFM", 
        artist: str, 
        track: str
    ) -> Dict:
        data = await self.__request(
            method="track.getLyrics", 
            params={
                "artist": artist,
                "track": track
            }
        )
        
        return data["lyrics"]["lyrics_body"]

    
    
    async def get_user_info(self: "LastFM", username: str) -> Dict:
        data = await self.__request(
            method="user.getInfo", 
            params={
                "user": username
            }
        )
        
        return data["user"]
    
    
    async def get_user_top_artists(
        self: "LastFM", 
        username: str,
        limit: Optional[int] = 10
    ) -> Dict:
        data = await self.__request(
            method="user.gettopartists", 
            params={
                "user": username,
                "limit": limit
            }
        )
        
        return data["topartists"]["artist"]
    
    
    async def get_user_recent_tracks(
        self: "LastFM", 
        username: str,
        limit: Optional[int] = 10
    ) -> Dict:
        data = await self.__request(
            method="user.getrecenttracks", 
            params={
                "user": username,
                "limit": limit
            }
        )
        
        return data["recenttracks"]["track"]
    
    
    async def get_user_top_tracks(
        self: "LastFM", 
        username: str,
        limit: Optional[int] = 10
    ):
        data = await self.__request(
            method="user.gettoptracks", 
            params={
                "user": username,
                "limit": limit
            }
        )
        
        return data["toptracks"]["track"]


    async def get_user_top_albums(
        self: "LastFM", 
        username: str,
        limit: Optional[int] = 10
    ) -> Dict:
        data = await self.__request(
            method="user.gettopalbums", 
            params={
                "user": username,
                "limit": limit
            }
        )
        
        return data["topalbums"]["album"]