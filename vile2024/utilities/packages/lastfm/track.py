from .main import LastFM


class Track:
    get_info = LastFM.get_track_info
    find = LastFM.find_track
    get_lyrics = LastFM.get_track_lyrics