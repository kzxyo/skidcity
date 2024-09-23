from dataclasses import dataclass
from typing import Optional

@dataclass
class InstagramUser:
    username: str
    full_name: str
    profile_picture_url: str

@dataclass
class InstagramVideo:
    url: str
    play_count: int
    view_count: int

@dataclass
class InstagramPost:
    url: str
    user: InstagramUser
    video: Optional[InstagramVideo]
    caption: str
    likes: int
    comments: int
    views: int
    
    @classmethod
    def from_dict(cls, data: dict, url: str):
        return cls(
            url=url,
            user=InstagramUser(
                username=data['owner']['username'],
                full_name=data['owner']['full_name'],
                profile_picture_url=data['owner']['profile_pic_url']
            ),
            video=InstagramVideo(
                url=data['video_url'],
                play_count=data['video_view_count'],
                view_count=data['video_view_count']
            ) if 'video_url' in data else None,
            caption=data['edge_media_to_caption']['edges'][0]['node']['text'] if len(data['edge_media_to_caption']['edges']) >= 1 else 'No Caption',
            likes=data['edge_media_preview_like']['count'],
            comments=data['edge_media_preview_comment']['count'],
            views=data['edge_media_preview_like']['count']
            if 'is_video' in data else 0
        )
