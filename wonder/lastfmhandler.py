import aiohttp, urllib.parse, json
apikey = "43693facbb24d1ac893a7d33846b15cc"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'}

async def get_track_playcount(user: str, track: str):
  async with aiohttp.ClientSession() as cs:
    async with cs.get(f"https://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={apikey}&artist={track['artist']['#text']}&track={urllib.parse.quote(track['name'].lower())}&format=json&username={user}", headers=headers) as r:
     z = await r.json() 
     return z['track']['userplaycount']

# from track
async def get_album_playcount(user: str, track: str):
    async with aiohttp.ClientSession() as cs:
     async with cs.get(f"https://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={apikey}&artist={track['artist']['#text']}&album={track['album']['#text']}&format=json&username={user}", headers=headers) as r:
      z = await r.json()  
      return z['album']['userplaycount']

# from track
async def get_artist_playcount(user: str, track: str):
   async with aiohttp.ClientSession() as cs:
     async with cs.get(f"https://ws.audioscrobbler.com/2.0/?method=artist.getInfo&api_key={apikey}&artist={track['artist']['#text']}&format=json&username={user}", headers=headers) as response:
      z = await response.json()
      return z['artist']['stats']['userplaycount']

# from track
async def get_album(track: str):
    async with aiohttp.ClientSession() as cs:
     async with cs.get(f"https://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key={apikey}&artist={track['artist']['#text']}&album={track['album']['#text']}&format=json&autocorrect=1", headers=headers) as response:
       z = await response.json()

       return z['album']

async def get_track(track: str):
    async with aiohttp.ClientSession() as cs:
     async with cs.get(f"https://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={apikey}&artist={track['artist']['#text']}&track={track['track']['#text']}&format=json", headers=headers) as response:
      z = await response.json()
      return z

async def get_user_info(user: str):
    async with aiohttp.ClientSession() as cs:
     async with cs.get(f"https://ws.audioscrobbler.com/2.0/?method=user.getInfo&user={user}&api_key={apikey}&format=json", headers=headers) as response:
       z = await response.json()
       return z

async def get_top_artists(user: str, count: int):
    async with aiohttp.ClientSession() as cs:
     async with cs.get(f"https://ws.audioscrobbler.com/2.0/?method=user.getTopArtists&user={user}&api_key={apikey}&format=json&limit={count}", headers=headers) as response:
      z = await response.json()
      return z

async def get_tracks_recent(user: str, count: int):
    async with aiohttp.ClientSession() as cs:
     async with cs.get(f'http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={user}&api_key={apikey}&format=json&limit=1', headers=headers) as res:
      z = await res.json()
      return z