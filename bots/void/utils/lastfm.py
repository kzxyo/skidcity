import traceback
from . import DL as http, utils
from typing import Dict, Optional, Any


API_KEY = '1b6567ff20617da36b3f7e5b335651c8'

class LastFM:
    def __init__(self, username: str, artist: Optional[str] = None, track: Optional[str] = None, album: Optional[str] = None):
        self.username = username
        self.artist = artist
        self.track = track
        self.album = album


    async def now_playing(self, limit: Optional[int] = 1) -> Optional[Dict[str, Dict[str, Any]]]:

        try:
            data = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'user.getRecentTracks', 'user': self.username, 'api_key': API_KEY, 'format': 'json', 'limit': str(limit)})
            track = data['recenttracks']['track'][0]

            # if track.get('@attr') is None:
            #     return None

            trackinfo = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'track.getInfo', 'username': self.username, 'api_key': API_KEY, 'artist': track['artist']['#text'], 'track': track['name'], 'format': 'json', 'autocorrect': '1'})
            artistinfo = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'artist.getInfo', 'username': self.username, 'api_key': API_KEY, 'artist': track['artist']['#text'], 'format': 'json', 'autocorrect': '1'})

            trackinfo['track'].setdefault('album', {'title': ''})
            trackinfo['track'].setdefault('userplaycount', 0)
            artistinfo['artist']['stats'].setdefault('userplaycount', 0)

            ret = {
                'artist': {
                    'name': artistinfo['artist']['name'],
                    'url': artistinfo['artist']['url'],
                    'hyper': f"[{artistinfo['artist']['name']}]({artistinfo['artist']['url']})",
                    'hyper.lower': f"[{artistinfo['artist']['name'].lower()}]({artistinfo['artist']['url']})",
                    'image': artistinfo['artist']['image'][3]['#text'],
                    'color': await utils.dominant_color(artistinfo['artist']['image'][3]['#text']),
                    'plays': int(artistinfo['artist']['stats']['userplaycount'])
                },
                'track': {
                    'name': trackinfo['track']['name'],
                    'url': trackinfo['track']['url'],
                    'hyper': f"[{trackinfo['track']['name']}]({trackinfo['track']['url']})",
                    'hyper.lower': f"[{trackinfo['track']['name'].lower()}]({trackinfo['track']['url']})",
                    'image': track['image'][3]['#text'],
                    'album': trackinfo['track']['album']['title'],
                    'color': await utils.dominant_color(track['image'][3]['#text']),
                    'plays': int(trackinfo['track']['userplaycount'])
                },
                'scrobbles': int(data['recenttracks']['@attr']['total'])
            }

            return ret
        except:
            return None


    async def top_artists(self, limit: Optional[int] = 10) -> Optional[Dict[str, Dict[str, Any]]]:
        
        data = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'user.gettopartists', 'user': self.username, 'period': 'overall', 'api_key': API_KEY, 'format': 'json', 'limit': str(limit)})
        
        ret = list()
        for artist in data['topartists']['artist']:
            ret.append(
                {
                    'name': artist['name'],
                    'hyper': f"[{artist['name']}]({artist['url']})",
                    'hyper.lower': f"[{artist['name'].lower()}]({artist['url']})",
                    'image': artist['image'][3]['#text'],
                    'rank': int(artist['@attr']['rank']),
                    'plays': int(artist.get('playcount')) or 0
                }
            )

        return ret


    async def top_albums(self, limit: Optional[int] = 10) -> Optional[Dict[str, Dict[str, Any]]]:
        
        data = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'user.gettopalbums', 'user': self.username, 'api_key': API_KEY, 'format': 'json', 'limit': str(limit)})
        
        ret = list()
        for album in data['topalbums']['album']:
            ret.append(
                {
                    'artist': album['artist']['name'],
                    'artist.hyper': f"[{album['artist']['name']}]({album['artist']['url']})",
                    'name': album['name'],
                    'hyper': f"[{album['name']}]({album['url']})",
                    'hyper.lower': f"[{album['name'].lower()}]({album['url']})",
                    'image': album['image'][3]['#text'],
                    'rank': int(album['@attr']['rank']),
                    'color': await utils.dominant_color(album['image'][3]['#text']),
                    'plays': int(album.get('playcount')) or 0
                }
            )

        return ret


    async def top_tracks(self, limit: Optional[int] = 10) -> Optional[Dict[str, Dict[str, Any]]]:
        
        data = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'user.gettoptracks', 'user': self.username, 'api_key': API_KEY, 'format': 'json', 'limit': str(limit)})
        
        ret = list()
        for track in data['toptracks']['track']:
            ret.append(
                {
                    'name': track['name'],
                    'artist': track['artist']['name'],
                    'artist.hyper': f"[{track['artist']['name']}]({track['artist']['url']})",
                    'hyper': f"[{track['name']}]({track['url']})",
                    'hyper.lower': f"[{track['name'].lower()}]({track['url']})",
                    'image': track['image'][3]['#text'],
                    'rank': int(track['@attr']['rank']),
                    'plays': int(track.get('playcount')) or 0
                }
            )

        return ret


    async def recent_tracks(self, limit: Optional[int] = 10) -> Optional[Dict[str, Dict[str, Any]]]:
        
        data = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'user.getRecentTracks', 'user': self.username, 'api_key': API_KEY, 'format': 'json', 'limit': str(limit)})
        ret = list()
        num = 0
        for track in data['recenttracks']['track']:
            trackk = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'track.getInfo', 'username': self.username, 'api_key': API_KEY, 'artist': track['artist']['#text'], 'track': track['name'], 'format': 'json', 'autocorrect': '1'})
            num += 1
            ret.append(
                {
                    'name': trackk['track']['name'],
                    'artist.hyper': f"[{trackk['track']['artist']['name']}]({trackk['track']['artist']['url']})",
                    'hyper': f"[{trackk['track']['name']}]({trackk['track']['url']})",
                    'hyper.lower': f"[{trackk['track']['name'].lower()}]({trackk['track']['url']})",
                    'image': track['image'][3]['#text'],
                    'rank': num,
                    'plays': int(trackk['track'].get('userplaycount', 0)),
                    'scrobbles': int(data['recenttracks']['@attr']['total'])
                }
            )

        return ret


    async def artist_plays(self) -> int:

        if self.artist is None:
            return 0

        try:
            artistinfo = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'artist.getInfo', 'username': self.username, 'api_key': API_KEY, 'artist': self.artist, 'format': 'json', 'autocorrect': '1'})
            return int(artistinfo['artist']['stats']['userplaycount'])
        except:
            return 0


    async def track_plays(self) -> int:

        if self.artist is None or self.track is None:
            return 0

        try:
            trackinfo = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'track.getInfo', 'username': self.username, 'api_key': API_KEY, 'artist': self.artist, 'track': self.track, 'format': 'json', 'autocorrect': '1'})
            return int(trackinfo['track']['userplaycount'])
        except:
            return 0


    async def artist_info(self) -> Optional[Dict[str, Dict[str, Any]]]:

        if self.artist is None:
            return None

        try:
            artistinfo = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'artist.getInfo', 'username': self.username, 'api_key': API_KEY, 'artist': self.artist, 'format': 'json', 'autocorrect': '1'})
            artistinfo['artist']['stats'].setdefault('userplaycount', 0)

            ret = {
                'artist': {
                    'name': artistinfo['artist']['name'],
                    'url': artistinfo['artist']['url'],
                    'hyper': f"[{artistinfo['artist']['name']}]({artistinfo['artist']['url']})",
                    'hyper.lower': f"[{artistinfo['artist']['name'].lower()}]({artistinfo['artist']['url']})",
                    'image': artistinfo['artist']['image'][3]['#text'],
                    'plays': int(artistinfo['artist']['stats']['userplaycount'])
                }
            }

            return ret
        except:
            return None


    async def track_info(self) -> Optional[Dict[str, Dict[str, Any]]]:

        if self.artist is None or self.track is None:
            return None

        try:
            trackinfo = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'track.getInfo', 'username': self.username, 'api_key': API_KEY, 'artist': self.artist, 'track': self.track, 'format': 'json', 'autocorrect': '1'}) 
            trackinfo['track'].setdefault('album', {'title': ''})
            trackinfo['track'].setdefault('userplaycount', 0)

            ret = {
                'track': {
                    'name': trackinfo['track']['name'],
                    'url': trackinfo['track']['url'],
                    'hyper': f"[{trackinfo['track']['name']}]({trackinfo['track']['url']})",
                    'hyper.lower': f"[{trackinfo['track']['name'].lower()}]({trackinfo['track']['url']})",
                    'image': trackinfo['track']['image'][3]['#text'],
                    'album': trackinfo['track']['album']['title'],
                    'plays': int(trackinfo['track']['userplaycount'])
                }
            }

            return ret
        except:
            return None


    async def album_info(self) -> Optional[Dict[str, Dict[str, Any]]]:

        if self.artist is None or self.album is None:
            return None

        try:
            albuminfo = await http.get('https://ws.audioscrobbler.com/2.0/', params={'method': 'album.getInfo', 'username': self.username, 'api_key': API_KEY, 'artist': self.artist, 'album': self.album, 'format': 'json'}) 
            albuminfo['album'].setdefault('userplaycount', 0)

            ret = {
                'album': {
                    'name': albuminfo['album']['name'],
                    'url': albuminfo['album']['url'],
                    'hyper': f"[{albuminfo['album']['name']}]({albuminfo['album']['url']})",
                    'hyper.lower': f"[{albuminfo['album']['name'].lower()}]({albuminfo['album']['url']})",
                    'image': albuminfo['album']['image'][3]['#text'],
                    'color': await utils.dominant_color(albuminfo['album']['image'][3]['#text']),
                    'plays': int(albuminfo['album']['userplaycount'])
                }
            }

            return ret
        except:
            return traceback.format_exc()