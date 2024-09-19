from .main import LastFM


class Artist:
    get_info = LastFM.get_artist_info
    top_tracks = LastFM.get_artist_top_tracks
    top_albums = LastFM.get_artist_top_albums
    find = LastFM.find_artist
    similar_artists = LastFM.get_similar_artists