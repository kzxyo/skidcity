from datetime import *
from typing import *

from pydantic import *


class CashAppAvatar(BaseModel):
    image_url: str
    accent_color: str


class CashApp(BaseModel):
    url: str
    cashtag: str
    display_name: str
    country_code: str
    avatar: CashAppAvatar
    qr: str


class ValorantAccount(BaseModel):
    region: str
    username: str
    level: int
    rank: str
    elo: int
    elo_change: int
    card: str
    updated_at: datetime


class ValorantMatch(BaseModel):
    map: str
    status: str
    rounds: int
    kills: int
    deaths: int
    started_at: datetime


class TwitterUser(BaseModel):
    url: str
    name: str
    screen_name: str
    avatar: str


class TwitterStatistics(BaseModel):
    likes: int
    replies: int
    retweets: int


class TwitterAssets(BaseModel):
    images: Optional[List[str]]
    video: Optional[str]


class TwitterPost(BaseModel):
    id: int
    url: str
    text: Optional[str]
    created_at: datetime
    user: TwitterUser
    statistics: TwitterStatistics
    assets: TwitterAssets


class InstagramUser(BaseModel):
    id: int
    url: str
    name: str
    avatar: str


class InstagramStatistics(BaseModel):
    likes: int
    comments: int


class InstagramMedia(BaseModel):
    type: Literal["image", "video"]
    url: str


class InstagramPost(BaseModel):
    shortcode: str
    share_url: str
    caption: Optional[str]
    created_at: datetime
    user: InstagramUser
    statistics: InstagramStatistics
    media: InstagramMedia
    results: int


class PinterestStatistics(BaseModel):
    comments: int
    saves: int


class PinterestUserStatistics(BaseModel):
    pins: int
    followers: int
    following: int


class PinterestUser(BaseModel):
    url: str
    id: int
    username: str
    display_name: str
    avatar: str
    bio: Optional[str]
    statistics: Optional[PinterestUserStatistics]


PinterestMedia = InstagramMedia


class PinterestPin(BaseModel):
    url: str
    id: int
    title: str
    created_at: str
    media: PinterestMedia
    user: PinterestUser
    statistics: PinterestStatistics


class GrailedStatistics(BaseModel):
    sales: int
    followers: int
    following: int


class GrailedSeller(BaseModel):
    url: str
    id: int
    username: str
    bio: Optional[str]
    avatar: Optional[str]
    statistics: GrailedStatistics


class GrailedListing(BaseModel):
    url: str
    id: int
    title: str
    description: str
    created_at: datetime
    price: int
    currency: str
    size: str
    images: List[str]
    seller: GrailedSeller


class WeHeartItStatistics(BaseModel):
    hearts: str
    posts: str
    followers: str
    following: str


class WeHeartItUser(BaseModel):
    url: str
    username: str
    display_name: str
    avatar: str
    description: Optional[str]
    statistics: WeHeartItStatistics


class TikTokUserStatistics(BaseModel):
    likes: str
    followers: str
    following: str


class TikTokPostBasic(BaseModel):
    id: int
    url: str


class TikTokUser(BaseModel):
    id: Optional[int]
    url: str
    username: str
    nickname: str
    avatar: str
    signature: Optional[str]
    verified: bool = False
    statistics: Optional[TikTokUserStatistics]
    videos: Optional[List[TikTokPostBasic]]


class TikTokStatistics(BaseModel):
    plays: int
    likes: int
    comments: int
    shares: int


class TikTokAssets(BaseModel):
    cover: str
    dynamic_cover: str
    images: Optional[List[str]]
    video: Optional[str]


class TikTokPost(BaseModel):
    id: int
    share_url: str
    caption: Optional[str]
    created_at: datetime
    user: TikTokUser
    statistics: TikTokStatistics
    assets: TikTokAssets
