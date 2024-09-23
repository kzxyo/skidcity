import aiohttp

class LastFMHandler(object): 
  def __init__(self, api_key: str):
   self.apikey = api_key 
   self.baseurl = "https://ws.audioscrobbler.com/2.0/"

  async def do_request(self, data: dict):  
   async with aiohttp.ClientSession() as cs: 
    async with cs.get(self.baseurl, params=data) as r: 
      return await r.json() 

  async def get_track_playcount(self, user: str, track: dict) -> int:
   data = { 
    'method': 'track.getInfo',
    'api_key': self.apikey,
    'artist': track['artist']['#text'],
    'track': track['name'],
    'format': 'json',
    'username': user 
   }
   return (await self.do_request(data))['track']['userplaycount']

  async def get_album_playcount(self, user: str, track: dict) -> int:
   data = {
    'method': 'album.getInfo',
    'api_key': self.apikey,
    'artist': track['artist']['#text'],
    'album': track['album']['#text'],
    'format': 'json',
    'username': user 
   }
   return (await self.do_request(data))['album']['userplaycount']

  async def get_artist_playcount(self, user: str, artist: str) -> int:
   data = {
    'method': 'artist.getInfo',
    'api_key': self.apikey,
    'artist': artist,
    'format': 'json', 
    'username': user
    }
   return (await self.do_request(data))['artist']['stats']['userplaycount']

  async def get_album(self, track: dict) -> dict:
    data = {
      'method': 'album.getInfo',
      'api_key': self.apikey, 
      'artist': track['artist']['#text'],
      'album': track['album']['#text'],
      'format': 'json'
    }
    return (await self.do_request(data))['album']

  async def get_track(self, track: dict) -> dict:
    data = {
      'method': 'album.getInfo',
      'api_key': self.apikey, 
      'artist': track['artist']['#text'],
      'track': track['track']['#text'],
      'format': 'json'
    }
    return await self.do_request(data)

  async def get_user_info(self, user: str) -> dict:
    data = {
      'method': 'user.getinfo',
      'user': user,
      'api_key': self.apikey,
      'format': 'json'
    } 
    return await self.do_request(data)

  async def get_top_artists(self, user: str, count: int) -> dict:
    data = {
      'method': 'user.getTopArtists',
      'user': user, 
      'api_key': self.apikey,
      'format': 'json',
      'limit': count
    }
    return await self.do_request(data)

  async def get_top_tracks(self, user: str, count: int) -> dict:
    data = {
      'method': 'user.getTopTracks',
      'user': user, 
      'api_key': self.apikey,
      'format': 'json',
      "period" : "overall",
      'limit': count
    }
    return await self.do_request(data)
  
  async def get_top_albums(self, user: str, count: int) -> dict: 
    params= {
      "api_key" : self.apikey,
      "user" : user,
      "period" : "overall",
      "limit" : count,
      "method":"user.getTopAlbums",
      "format":"json"
      }
    return await self.do_request(params)

  async def get_tracks_recent(self, user: str, count: int) -> dict:
    data = {
      'method': 'user.getrecenttracks',
      'user': user,
      'api_key': self.apikey,
      'format': 'json',
      'limit': count
    } 
    return await self.do_request(data)