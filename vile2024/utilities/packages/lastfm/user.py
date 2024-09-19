from .main import LastFM


class User:
    get_info = LastFM.get_user_info
    top_tracks = LastFM.get_user_top_tracks
    top_albums = LastFM.get_user_top_albums
    recent_tracks = LastFM.get_user_recent_tracks
    top_artists = LastFM.get_user_top_artists