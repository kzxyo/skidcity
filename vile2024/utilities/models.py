from typing import (
    Optional as pos,
    Union as one, 
    Dict as obj, 
    List as array, 
    Any
)

from pydantic import (
    BaseModel, 
    Field
)

from munch import DefaultMunch


class BaseEmbedModel(BaseModel):
    id: int
    name: str
    created_at: str # Formatted datetime
    
    
    def __str__(self: "BaseModel") -> str:
        return self.name


class EUser(BaseEmbedModel):
    mention: str
    avatar: str
    color: str
    joined_at: str # Formatted datetime
    

class Moderator(EUser):
    pass


class Guild(BaseEmbedModel):
    count: int
    count_formatted: str # Ordinal
    boost_count: int
    boost_count_formatted: str # Ordinal
    booster_count: int
    booster_count_formatted: str # Ordinal
    boost_tier: int
    icon: str
    

class Tempature(BaseModel):
    celsius: one[ int, float ]
    fahrenheit: one[ int, float ]

class Weather(BaseModel):
    cloud_pct: one[ int, float ]
    temp: Tempature
    feels_like: Tempature
    humidity: one[ int, float ]
    min_temp: Tempature
    max_temp: Tempature
    wind_speed: one[ int, float ]
    wind_degrees: one[ int, float ]
    sunrise: one[ int, float ]
    sunset: one[ int, float ]
    
    
class Definition(BaseModel):
    definition: str
    word: str
    valid: bool
    
    
class UrbanDefinition(BaseModel):
    definition: str
    permalink: str
    thumbs_up: int
    author: str
    word: str
    defid: int
    current_vote: str
    written_on: str
    example: str
    thumbs_down: int


class Sentiment(BaseModel):
    score: float
    text: str
    sentiment: str


class Carrier(BaseModel):
    name: pos[str]
    mcc: pos[str]
    mnc: pos[str]


class Company(BaseModel):
    domain: str
    name: str
    type: str


class Connection(BaseModel):
    asn: int
    domain: str
    organization: str
    route: str
    type: str


class CurrencyFormat(BaseModel):
    prefix: str
    suffix: str


class Currency(BaseModel):
    code: str
    name: str
    name_native: str
    plural: str
    plural_native: str
    symbol: str
    symbol_native: str
    format: obj[ str, CurrencyFormat ]


class Continent(BaseModel):
    code: str
    name: str


class CountryFlag(BaseModel):
    emoji: str
    emoji_unicode: str
    emojitwo: str
    noto: str
    twemoji: str
    wikimedia: str


class CountryLanguage(BaseModel):
    code: str
    name: str
    native: str


class Country(BaseModel):
    area: int
    borders: array[str]
    calling_code: str
    capital: str
    code: str
    name: str
    population: int
    population_density: float
    flag: CountryFlag
    languages: array[CountryLanguage]
    tld: str


class Region(BaseModel):
    code: str
    name: str


class Location(BaseModel):
    continent: Continent
    country: Country
    region: Region
    city: str
    postal: str
    latitude: float
    longitude: float
    language: CountryLanguage
    in_eu: bool


class Security(BaseModel):
    is_abuser: bool
    is_attacker: bool
    is_bogon: bool
    is_cloud_provider: bool
    is_proxy: bool
    is_relay: bool
    is_tor: bool
    is_tor_exit: bool
    is_vpn: bool
    is_anonymous: bool
    is_threat: bool


class TimeZone(BaseModel):
    id: str
    abbreviation: str
    current_time: str
    name: str
    offset: int
    in_daylight_saving: bool


class GeoIP(BaseModel):
    ip: str
    type: str
    hostname: one[ str, None ]
    carrier: pos[Carrier]
    company: Company
    connection: Connection
    currency: Currency
    location: Location
    security: Security
    time_zone: TimeZone
    
    
class BioLink(BaseModel):
    title: pos[str] = None
    lynx_url: pos[str] = None
    url: pos[str] = None
    link_type: pos[str] = None


class BiographyWithEntities(BaseModel):
    raw_text: pos[str] = None
    entities: pos[array] = None


class EdgeFollowedBy(BaseModel):
    count: pos[int] = None


class EdgeFollow(BaseModel):
    count: pos[int] = None


class EdgeMutualFollowedBy(BaseModel):
    count: pos[int] = None
    edges: pos[array] = None


class PageInfo(BaseModel):
    has_next_page: pos[bool] = None
    end_cursor: pos[str] = None


class Dimensions(BaseModel):
    height: pos[int] = None
    width: pos[int] = None


class User1(BaseModel):
    full_name: pos[str] = None
    followed_by_viewer: pos[bool] = None
    id: pos[str] = None
    is_verified: pos[bool] = None
    profile_pic_url: pos[str] = None
    username: pos[str] = None


class Node1(BaseModel):
    user: pos[User1] = None
    x: pos[float] = None
    y: pos[float] = None


class Edge1(BaseModel):
    node: pos[Node1] = None


class EdgeMediaToTaggedUser(BaseModel):
    edges: pos[array[Edge1]] = None


class SharingFrictionInfo(BaseModel):
    should_have_sharing_friction: pos[bool] = None
    bloks_app_url: pos[Any] = None


class Owner(BaseModel):
    id: pos[str] = None
    username: pos[str] = None


class DashInfo(BaseModel):
    is_dash_eligible: pos[bool] = None
    video_dash_manifest: pos[Any] = None
    number_of_qualities: pos[int] = None


class Node2(BaseModel):
    text: pos[str] = None


class Edge2(BaseModel):
    node: pos[Node2] = None


class EdgeMediaToCaption(BaseModel):
    edges: pos[array[Edge2]] = None


class EdgeMediaToComment(BaseModel):
    count: pos[int] = None


class EdgeLikedBy(BaseModel):
    count: pos[int] = None


class EdgeMediaPreviewLike(BaseModel):
    count: pos[int] = None


class ThumbnailResource(BaseModel):
    src: pos[str] = None
    config_width: pos[int] = None
    config_height: pos[int] = None


class CoauthorProducer(BaseModel):
    id: pos[str] = None
    is_verified: pos[bool] = None
    profile_pic_url: pos[str] = None
    username: pos[str] = None


class Node(BaseModel):
    typename: pos[str] = None
    id: pos[str] = None
    shortcode: pos[str] = None
    dimensions: pos[Dimensions] = None
    display_url: pos[str] = None
    edge_media_to_tagged_user: pos[EdgeMediaToTaggedUser] = None
    fact_check_overall_rating: pos[Any] = None
    fact_check_information: pos[Any] = None
    gating_info: pos[Any] = None
    sharing_friction_info: pos[SharingFrictionInfo] = None
    media_overlay_info: pos[Any] = None
    media_preview: pos[pos[str]] = None
    owner: pos[Owner] = None
    is_video: pos[bool] = None
    has_upcoming_event: pos[bool] = None
    accessibility_caption: pos[Any] = None
    dash_info: pos[DashInfo] = None
    has_audio: pos[bool] = None
    tracking_token: pos[str] = None
    video_url: pos[str] = None
    video_view_count: pos[int] = None
    edge_media_to_caption: pos[EdgeMediaToCaption] = None
    edge_media_to_comment: pos[EdgeMediaToComment] = None
    comments_disabled: pos[bool] = None
    taken_at_timestamp: pos[int] = None
    edge_liked_by: pos[EdgeLikedBy] = None
    edge_media_preview_like: pos[EdgeMediaPreviewLike] = None
    location: pos[Any] = None
    nft_asset_info: pos[Any] = None
    thumbnail_src: pos[str] = None
    thumbnail_resources: pos[array[ThumbnailResource]] = None
    felix_profile_grid_crop: pos[Any] = None
    coauthor_producers: pos[array[CoauthorProducer]] = None
    pinned_for_users: pos[array] = None
    viewer_can_reshare: pos[bool] = None
    encoding_status: pos[Any] = None
    is_published: pos[bool] = None
    product_type: pos[str] = None
    title: pos[str] = None
    video_duration: pos[float] = None


class Edge(BaseModel):
    node: pos[Node] = None


class EdgeFelixVideoTimeline(BaseModel):
    count: pos[int] = None
    page_info: pos[PageInfo] = None
    edges: pos[array[Edge]] = None


class PageInfo1(BaseModel):
    has_next_page: pos[bool] = None
    end_cursor: pos[str] = None


class Dimensions1(BaseModel):
    height: pos[int] = None
    width: pos[int] = None


class User2(BaseModel):
    full_name: pos[str] = None
    followed_by_viewer: pos[bool] = None
    id: pos[str] = None
    is_verified: pos[bool] = None
    profile_pic_url: pos[str] = None
    username: pos[str] = None


class Node4(BaseModel):
    user: pos[User2] = None
    x: pos[float] = None
    y: pos[float] = None


class Edge4(BaseModel):
    node: pos[Node4] = None


class EdgeMediaToTaggedUser1(BaseModel):
    edges: pos[array[Edge4]] = None


class SharingFrictionInfo1(BaseModel):
    should_have_sharing_friction: pos[bool] = None
    bloks_app_url: pos[Any] = None


class Owner1(BaseModel):
    id: pos[str] = None
    username: pos[str] = None


class Node5(BaseModel):
    text: pos[str] = None


class Edge5(BaseModel):
    node: pos[Node5] = None


class EdgeMediaToCaption1(BaseModel):
    edges: pos[array[Edge5]] = None


class EdgeMediaToComment1(BaseModel):
    count: pos[int] = None


class EdgeLikedBy1(BaseModel):
    count: pos[int] = None


class EdgeMediaPreviewLike1(BaseModel):
    count: pos[int] = None


class ThumbnailResource1(BaseModel):
    src: pos[str] = None
    config_width: pos[int] = None
    config_height: pos[int] = None


class CoauthorProducer1(BaseModel):
    id: pos[str] = None
    is_verified: pos[bool] = None
    profile_pic_url: pos[str] = None
    username: pos[str] = None


class Dimensions2(BaseModel):
    height: pos[int] = None
    width: pos[int] = None


class User3(BaseModel):
    full_name: pos[str] = None
    followed_by_viewer: pos[bool] = None
    id: pos[str] = None
    is_verified: pos[bool] = None
    profile_pic_url: pos[str] = None
    username: pos[str] = None


class Node7(BaseModel):
    user: pos[User3] = None
    x: pos[float] = None
    y: pos[float] = None


class Edge7(BaseModel):
    node: pos[Node7] = None


class EdgeMediaToTaggedUser2(BaseModel):
    edges: pos[array[Edge7]] = None


class SharingFrictionInfo2(BaseModel):
    should_have_sharing_friction: pos[bool] = None
    bloks_app_url: pos[Any] = None


class Owner2(BaseModel):
    id: pos[str] = None
    username: pos[str] = None


class Node6(BaseModel):
    typename: pos[str] = None
    id: pos[str] = None
    shortcode: pos[str] = None
    dimensions: pos[Dimensions2] = None
    display_url: pos[str] = None
    edge_media_to_tagged_user: pos[EdgeMediaToTaggedUser2] = None
    fact_check_overall_rating: pos[Any] = None
    fact_check_information: pos[Any] = None
    gating_info: pos[Any] = None
    sharing_friction_info: pos[SharingFrictionInfo2] = None
    media_overlay_info: pos[Any] = None
    media_preview: pos[pos[str]] = None
    owner: pos[Owner2] = None
    is_video: pos[bool] = None
    has_upcoming_event: pos[bool] = None
    accessibility_caption: pos[str] = None


class Edge6(BaseModel):
    node: pos[Node6] = None


class EdgeSidecarToChildren(BaseModel):
    edges: pos[array[Edge6]] = None


class DashInfo1(BaseModel):
    is_dash_eligible: pos[bool] = None
    video_dash_manifest: pos[Any] = None
    number_of_qualities: pos[int] = None


class ClipsMusicAttributionInfo(BaseModel):
    artist_name: pos[str] = None
    song_name: pos[str] = None
    uses_original_audio: pos[bool] = None
    should_mute_audio: pos[bool] = None
    should_mute_audio_reason: pos[str] = None
    audio_id: pos[str] = None


class Node3(BaseModel):
    typename: pos[str] = None
    id: pos[str] = None
    shortcode: pos[str] = None
    dimensions: pos[Dimensions1] = None
    display_url: pos[str] = None
    edge_media_to_tagged_user: pos[EdgeMediaToTaggedUser1] = None
    fact_check_overall_rating: pos[Any] = None
    fact_check_information: pos[Any] = None
    gating_info: pos[Any] = None
    sharing_friction_info: pos[SharingFrictionInfo1] = None
    media_overlay_info: pos[Any] = None
    media_preview: pos[pos[str]] = None
    owner: pos[Owner1] = None
    is_video: pos[bool] = None
    has_upcoming_event: pos[bool] = None
    accessibility_caption: pos[pos[str]] = None
    edge_media_to_caption: pos[EdgeMediaToCaption1] = None
    edge_media_to_comment: pos[EdgeMediaToComment1] = None
    comments_disabled: pos[bool] = None
    taken_at_timestamp: pos[int] = None
    edge_liked_by: pos[EdgeLikedBy1] = None
    edge_media_preview_like: pos[EdgeMediaPreviewLike1] = None
    location: pos[Any] = None
    nft_asset_info: pos[Any] = None
    thumbnail_src: pos[str] = None
    thumbnail_resources: pos[array[ThumbnailResource1]] = None
    coauthor_producers: pos[array[CoauthorProducer1]] = None
    pinned_for_users: pos[array] = None
    viewer_can_reshare: pos[bool] = None
    edge_sidecar_to_children: pos[EdgeSidecarToChildren] = None
    dash_info: pos[DashInfo1] = None
    has_audio: pos[bool] = None
    tracking_token: pos[str] = None
    video_url: pos[str] = None
    video_view_count: pos[int] = None
    felix_profile_grid_crop: pos[Any] = None
    product_type: pos[str] = None
    clips_music_attribution_info: pos[ClipsMusicAttributionInfo] = None


class Edge3(BaseModel):
    node: pos[Node3] = None


class EdgeOwnerToTimelineMedia(BaseModel):
    count: pos[int] = None
    page_info: pos[PageInfo1] = None
    edges: pos[array[Edge3]] = None


class PageInfo2(BaseModel):
    has_next_page: pos[bool] = None
    end_cursor: pos[Any] = None


class EdgeSavedMedia(BaseModel):
    count: pos[int] = None
    page_info: pos[PageInfo2] = None
    edges: pos[array] = None


class PageInfo3(BaseModel):
    has_next_page: pos[bool] = None
    end_cursor: pos[Any] = None


class EdgeMediaCollections(BaseModel):
    count: pos[int] = None
    page_info: pos[PageInfo3] = None
    edges: pos[array] = None


class Node8(BaseModel):
    id: pos[str] = None
    full_name: pos[str] = None
    is_private: pos[bool] = None
    is_verified: pos[bool] = None
    profile_pic_url: pos[str] = None
    username: pos[str] = None


class Edge8(BaseModel):
    node: pos[Node8] = None


class EdgeRelatedProfiles(BaseModel):
    edges: pos[array[Edge8]] = None


class User(BaseModel):
    ai_agent_type: pos[Any] = None
    biography: pos[str] = None
    bio_links: pos[array[BioLink]] = None
    fb_profile_biolink: pos[Any] = None
    biography_with_entities: pos[BiographyWithEntities] = None
    blocked_by_viewer: pos[bool] = None
    restricted_by_viewer: pos[Any] = None
    country_block: pos[bool] = None
    eimu_id: pos[str] = None
    external_url: pos[str] = None
    external_url_linkshimmed: pos[str] = None
    edge_followed_by: pos[EdgeFollowedBy] = None
    fbid: pos[str] = None
    followed_by_viewer: pos[bool] = None
    edge_follow: pos[EdgeFollow] = None
    follows_viewer: pos[bool] = None
    full_name: pos[str] = None
    group_metadata: pos[Any] = None
    has_ar_effects: pos[bool] = None
    has_clips: pos[bool] = None
    has_guides: pos[bool] = None
    has_channel: pos[bool] = None
    has_blocked_viewer: pos[bool] = None
    highlight_reel_count: pos[int] = None
    has_requested_viewer: pos[bool] = None
    hide_like_and_view_counts: pos[bool] = None
    id: pos[str] = None
    is_business_account: pos[bool] = None
    is_professional_account: pos[bool] = None
    is_supervision_enabled: pos[bool] = None
    is_guardian_of_viewer: pos[bool] = None
    is_supervised_by_viewer: pos[bool] = None
    is_supervised_user: pos[bool] = None
    is_embeds_disabled: pos[bool] = None
    is_joined_recently: pos[bool] = None
    guardian_id: pos[Any] = None
    business_address_json: pos[str] = None
    business_contact_method: pos[str] = None
    business_email: pos[Any] = None
    business_phone_number: pos[Any] = None
    business_category_name: pos[Any] = None
    overall_category_name: pos[Any] = None
    category_enum: pos[Any] = None
    category_name: pos[str] = None
    is_private: pos[bool] = None
    is_verified: pos[bool] = None
    is_verified_by_mv4b: pos[bool] = None
    is_regulated_c18: pos[bool] = None
    edge_mutual_followed_by: pos[EdgeMutualFollowedBy] = None
    pinned_channels_array_count: pos[int] = None
    profile_pic_url: pos[str] = None
    profile_pic_url_hd: pos[str] = None
    requested_by_viewer: pos[bool] = None
    should_show_category: pos[bool] = None
    should_show_public_contacts: pos[bool] = None
    show_account_transparency_details: pos[bool] = None
    remove_message_entrypoint: pos[bool] = None
    transparency_label: pos[Any] = None
    transparency_product: pos[Any] = None
    username: pos[str] = None
    connected_fb_page: pos[Any] = None
    pronouns: pos[array] = None
    edge_felix_video_timeline: pos[EdgeFelixVideoTimeline] = None
    edge_owner_to_timeline_media: pos[EdgeOwnerToTimelineMedia] = None
    edge_saved_media: pos[EdgeSavedMedia] = None
    edge_media_collections: pos[EdgeMediaCollections] = None
    edge_related_profiles: pos[EdgeRelatedProfiles] = None


class Object:
    def __init__(self, data: dict):
        return DefaultMunch(object(), data)


class YouTubeChannel(BaseModel):
    id: pos[str] = None
    name: pos[str] = ""
    channel_url: pos[str] = None
    is_live: pos[bool] = False
    follower_count: pos[int] = 0


class YouTubePost(BaseModel):
    id: pos[str] = None
    title: pos[str] = ""
    thumbnail: pos[str] = None
    description: pos[str] = ""
    full_title: pos[str] = ""
    was_live: pos[bool] = False
    url: pos[str] = None
    duration: pos[int] = 0
    fps: pos[int] = 0
    created_at: pos[int] = 0
    author: pos[YouTubeChannel] = None
    view_count: pos[int] = 0
    original_url: pos[str] = None
    comment_count: pos[int] = 0


class FanClubInfo(BaseModel):
    fan_club_id: pos[Any] = None
    fan_club_name: pos[Any] = None
    is_fan_club_referral_eligible: pos[Any] = None
    fan_consideration_page_revamp_eligiblity: pos[Any] = None
    is_fan_club_gifting_eligible: pos[Any] = None
    subscriber_count: pos[Any] = None
    connected_member_count: pos[Any] = None
    autosave_to_exclusive_highlight: pos[Any] = None
    has_enough_subscribers_for_ssc: pos[Any] = None


class FriendshipStatus(BaseModel):
    following: pos[bool] = None
    is_bestie: pos[bool] = None
    is_restricted: pos[bool] = None
    is_feed_favorite: pos[bool] = None


class HdProfilePicUrlInfo(BaseModel):
    url: pos[str] = None
    width: pos[int] = None
    height: pos[int] = None


class HdProfilePicVersion(BaseModel):
    width: pos[int] = None
    height: pos[int] = None
    url: pos[str] = None


class InstagramMetrics(BaseModel):
    count: int


class InstagramProfile(BaseModel):
    id: int
    username: str
    full_name: str
    biography: pos[str]
    avatar: str
    profile_pic_url_hd: str
    is_private: bool
    is_verified: bool
    edge_owner_to_timeline_media: InstagramMetrics
    edge_followed_by: InstagramMetrics
    edge_follow: InstagramMetrics


class UUSER(BaseModel):
    fbid_v2: pos[int] = None
    feed_post_reshare_disabled: pos[bool] = None
    full_name: pos[str] = None
    id: pos[str] = None
    is_private: pos[bool] = None
    is_unpublished: pos[bool] = None
    pk: pos[int] = None
    pk_id: pos[str] = None
    show_account_transparency_details: pos[bool] = None
    strong_id__: pos[str] = None
    third_party_downloads_enabled: pos[int] = None
    username: pos[str] = None
    account_badges: pos[array] = None
    fan_club_info: pos[FanClubInfo] = None
    friendship_status: pos[FriendshipStatus] = None
    has_anonymous_profile_picture: pos[bool] = None
    hd_profile_pic_url_info: pos[HdProfilePicUrlInfo] = None
    hd_profile_pic_versions: pos[array[HdProfilePicVersion]] = None
    is_favorite: pos[bool] = None
    is_verified: pos[bool] = None
    latest_reel_media: pos[int] = None
    profile_pic_id: pos[str] = None
    profile_pic_url: pos[str] = None
    transparency_product_enabled: pos[bool] = None


class Caption(BaseModel):
    pk: pos[str] = None
    user_id: pos[int] = None
    user: pos[UUSER] = None
    type: pos[int] = None
    text: pos[str] = None
    did_report_as_spam: pos[bool] = None
    created_at: pos[int] = None
    created_at_utc: pos[int] = None
    content_type: pos[str] = None
    status: pos[str] = None
    bit_flags: pos[int] = None
    share_enabled: pos[bool] = None
    is_ranked_comment: pos[bool] = None
    is_covered: pos[bool] = None
    private_reply_status: pos[int] = None
    media_id: pos[int] = None


class CommentInformTreatment(BaseModel):
    should_have_inform_treatment: pos[bool] = None
    text: pos[str] = None
    url: pos[Any] = None
    action_type: pos[Any] = None


class SharingFrictionInfo(BaseModel):
    should_have_sharing_friction: pos[bool] = None
    bloks_app_url: pos[Any] = None
    sharing_friction_payload: pos[Any] = None


class MediaAppreciationSettings(BaseModel):
    media_gifting_state: pos[str] = None
    gift_count_visibility: pos[str] = None


class FbUserTags(BaseModel):
    in_: pos[array] = Field(None, alias="in")


class HighlightsInfo(BaseModel):
    added_to: pos[array] = None


class SquareCrop(BaseModel):
    crop_bottom: pos[float] = None
    crop_left: pos[float] = None
    crop_right: pos[float] = None
    crop_top: pos[float] = None


class MediaCroppingInfo(BaseModel):
    feed_preview_crop: pos[Any] = None
    square_crop: pos[SquareCrop] = None
    three_by_four_preview_crop: pos[Any] = None


class FanClubInfo1(BaseModel):
    fan_club_id: pos[Any] = None
    fan_club_name: pos[Any] = None
    is_fan_club_referral_eligible: pos[Any] = None
    fan_consideration_page_revamp_eligiblity: pos[Any] = None
    is_fan_club_gifting_eligible: pos[Any] = None
    subscriber_count: pos[Any] = None
    connected_member_count: pos[Any] = None
    autosave_to_exclusive_highlight: pos[Any] = None
    has_enough_subscribers_for_ssc: pos[Any] = None


class FriendshipStatus1(BaseModel):
    following: pos[bool] = None
    is_bestie: pos[bool] = None
    is_restricted: pos[bool] = None
    is_feed_favorite: pos[bool] = None


class HdProfilePicUrlInfo1(BaseModel):
    url: pos[str] = None
    width: pos[int] = None
    height: pos[int] = None


class HdProfilePicVersion1(BaseModel):
    width: pos[int] = None
    height: pos[int] = None
    url: pos[str] = None


class User1(BaseModel):
    fbid_v2: pos[int] = None
    feed_post_reshare_disabled: pos[bool] = None
    full_name: pos[str] = None
    id: pos[str] = None
    is_private: pos[bool] = None
    is_unpublished: pos[bool] = None
    pk: pos[int] = None
    pk_id: pos[str] = None
    show_account_transparency_details: pos[bool] = None
    strong_id__: pos[str] = None
    third_party_downloads_enabled: pos[int] = None
    username: pos[str] = None
    account_badges: pos[array] = None
    fan_club_info: pos[FanClubInfo1] = None
    friendship_status: pos[FriendshipStatus1] = None
    has_anonymous_profile_picture: pos[bool] = None
    hd_profile_pic_url_info: pos[HdProfilePicUrlInfo1] = None
    hd_profile_pic_versions: pos[array[HdProfilePicVersion1]] = None
    is_favorite: pos[bool] = None
    is_verified: pos[bool] = None
    latest_reel_media: pos[int] = None
    profile_pic_id: pos[str] = None
    profile_pic_url: pos[str] = None
    transparency_product_enabled: pos[bool] = None


class Candidate(BaseModel):
    width: pos[int] = None
    height: pos[int] = None
    url: pos[str] = None


class IgtvFirstFrame(BaseModel):
    width: pos[int] = None
    height: pos[int] = None
    url: pos[str] = None


class FirstFrame(BaseModel):
    width: pos[int] = None
    height: pos[int] = None
    url: pos[str] = None


class AdditionalCandidates(BaseModel):
    igtv_first_frame: pos[IgtvFirstFrame] = None
    first_frame: pos[FirstFrame] = None
    smart_frame: pos[Any] = None


class ImageVersions2(BaseModel):
    candidates: pos[array[Candidate]] = None
    additional_candidates: pos[AdditionalCandidates] = None
    smart_thumbnail_enabled: pos[bool] = None


class FanClubInfo2(BaseModel):
    fan_club_id: pos[Any] = None
    fan_club_name: pos[Any] = None
    is_fan_club_referral_eligible: pos[Any] = None
    fan_consideration_page_revamp_eligiblity: pos[Any] = None
    is_fan_club_gifting_eligible: pos[Any] = None
    subscriber_count: pos[Any] = None
    connected_member_count: pos[Any] = None
    autosave_to_exclusive_highlight: pos[Any] = None
    has_enough_subscribers_for_ssc: pos[Any] = None


class FriendshipStatus2(BaseModel):
    following: pos[bool] = None
    is_bestie: pos[bool] = None
    is_restricted: pos[bool] = None
    is_feed_favorite: pos[bool] = None


class HdProfilePicUrlInfo2(BaseModel):
    url: pos[str] = None
    width: pos[int] = None
    height: pos[int] = None


class HdProfilePicVersion2(BaseModel):
    width: pos[int] = None
    height: pos[int] = None
    url: pos[str] = None


class Owner(BaseModel):
    fbid_v2: pos[int] = None
    feed_post_reshare_disabled: pos[bool] = None
    full_name: pos[str] = None
    id: pos[str] = None
    is_private: pos[bool] = None
    is_unpublished: pos[bool] = None
    pk: pos[int] = None
    pk_id: pos[str] = None
    show_account_transparency_details: pos[bool] = None
    strong_id__: pos[str] = None
    third_party_downloads_enabled: pos[int] = None
    username: pos[str] = None
    account_badges: pos[array] = None
    fan_club_info: pos[FanClubInfo2] = None
    friendship_status: pos[FriendshipStatus2] = None
    has_anonymous_profile_picture: pos[bool] = None
    hd_profile_pic_url_info: pos[HdProfilePicUrlInfo2] = None
    hd_profile_pic_versions: pos[array[HdProfilePicVersion2]] = None
    is_favorite: pos[bool] = None
    is_verified: pos[bool] = None
    latest_reel_media: pos[int] = None
    profile_pic_id: pos[str] = None
    profile_pic_url: pos[str] = None
    transparency_product_enabled: pos[bool] = None


class VideoVersion(BaseModel):
    type: pos[int] = None
    width: pos[int] = None
    height: pos[int] = None
    url: pos[str] = None
    id: pos[str] = None


class MusicAssetInfo(BaseModel):
    audio_asset_id: pos[str] = None
    audio_cluster_id: pos[str] = None
    id: pos[str] = None
    title: pos[str] = None
    sanitized_title: pos[Any] = None
    subtitle: pos[str] = None
    display_artist: pos[str] = None
    artist_id: pos[str] = None
    is_explicit: pos[bool] = None
    cover_artwork_uri: pos[str] = None
    cover_artwork_thumbnail_uri: pos[str] = None
    progressive_download_url: pos[str] = None
    reactive_audio_download_url: pos[Any] = None
    fast_start_progressive_download_url: pos[str] = None
    web_30s_preview_download_url: pos[str] = None
    highlight_start_times_in_ms: pos[array[int]] = None
    dash_manifest: pos[Any] = None
    has_lyrics: pos[bool] = None
    duration_in_ms: pos[int] = None
    dark_message: pos[Any] = None
    allows_saving: pos[bool] = None
    ig_username: pos[str] = None
    is_eligible_for_audio_effects: pos[bool] = None


class IgArtist(BaseModel):
    pk: pos[int] = None
    pk_id: pos[str] = None
    username: pos[str] = None
    full_name: pos[str] = None
    is_private: pos[bool] = None
    strong_id__: pos[str] = None
    is_verified: pos[bool] = None
    profile_pic_id: pos[str] = None
    profile_pic_url: pos[str] = None


class AudioMutingInfo(BaseModel):
    allow_audio_editing: pos[bool] = None
    mute_audio: pos[bool] = None
    mute_reason: pos[Any] = None
    mute_reason_str: pos[str] = None
    show_muted_audio_toast: pos[bool] = None


class MusicConsumptionInfo(BaseModel):
    ig_artist: pos[IgArtist] = None
    placeholder_profile_pic_url: pos[str] = None
    should_mute_audio: pos[bool] = None
    should_mute_audio_reason: pos[str] = None
    should_mute_audio_reason_type: pos[Any] = None
    is_bookmarked: pos[bool] = None
    overlap_duration_in_ms: pos[int] = None
    audio_asset_start_time_in_ms: pos[int] = None
    allow_media_creation_with_music: pos[bool] = None
    is_trending_in_clips: pos[bool] = None
    trend_rank: pos[Any] = None
    formatted_clips_media_count: pos[Any] = None
    display_labels: pos[Any] = None
    should_allow_music_editing: pos[bool] = None
    derived_content_id: pos[Any] = None
    audio_filter_infos: pos[array] = None
    audio_muting_info: pos[AudioMutingInfo] = None
    contains_lyrics: pos[Any] = None
    should_render_soundwave: pos[bool] = None


class MusicInfo(BaseModel):
    music_asset_info: pos[MusicAssetInfo] = None
    music_consumption_info: pos[MusicConsumptionInfo] = None
    music_canonical_id: pos[Any] = None


class MashupInfo(BaseModel):
    mashups_allowed: pos[bool] = None
    can_toggle_mashups_allowed: pos[bool] = None
    has_been_mashed_up: pos[bool] = None
    is_light_weight_check: pos[bool] = None
    formatted_mashups_count: pos[Any] = None
    original_media: pos[Any] = None
    privacy_filtered_mashups_media_count: pos[Any] = None
    non_privacy_filtered_mashups_media_count: pos[Any] = None
    mashup_type: pos[Any] = None
    is_creator_requesting_mashup: pos[bool] = None
    has_nonmimicable_additional_audio: pos[bool] = None
    is_pivot_page_available: pos[bool] = None


class Color(BaseModel):
    count: pos[int] = None
    hex_rgba_color: pos[str] = None


class ReusableTextInfoItem(BaseModel):
    id: pos[int] = None
    text: pos[str] = None
    start_time_ms: pos[float] = None
    end_time_ms: pos[float] = None
    width: pos[float] = None
    height: pos[float] = None
    offset_x: pos[float] = None
    offset_y: pos[float] = None
    z_index: pos[int] = None
    rotation_degree: pos[float] = None
    scale: pos[float] = None
    alignment: pos[str] = None
    colors: pos[array[Color]] = None
    text_format_type: pos[str] = None
    font_size: pos[float] = None
    text_emphasis_mode: pos[str] = None
    is_animated: pos[int] = None


class BrandedContentTagInfo(BaseModel):
    can_add_tag: pos[bool] = None


class AudioReattributionInfo(BaseModel):
    should_allow_restore: pos[bool] = None


class AdditionalAudioInfo(BaseModel):
    additional_audio_username: pos[Any] = None
    audio_reattribution_info: pos[AudioReattributionInfo] = None


class AudioRankingInfo(BaseModel):
    best_audio_cluster_id: pos[str] = None


class Pill(BaseModel):
    action_type: pos[str] = None
    priority: pos[int] = None


class Comment(BaseModel):
    action_type: pos[str] = None


class EntryPointContainer(BaseModel):
    pill: pos[Pill] = None
    comment: pos[Comment] = None
    overflow: pos[Any] = None
    ufi: pos[Any] = None


class ContentAppreciationInfo(BaseModel):
    enabled: pos[bool] = None
    entry_point_container: pos[EntryPointContainer] = None


class AchievementsInfo(BaseModel):
    show_achievements: pos[bool] = None
    num_earned_achievements: pos[Any] = None


class ClipsMetadata(BaseModel):
    music_info: pos[MusicInfo] = None
    original_sound_info: pos[Any] = None
    audio_type: pos[str] = None
    music_canonical_id: pos[str] = None
    featured_label: pos[Any] = None
    mashup_info: pos[MashupInfo] = None
    reusable_text_info: pos[array[ReusableTextInfoItem]] = None
    reusable_text_attribute_string: pos[str] = None
    nux_info: pos[Any] = None
    viewer_interaction_settings: pos[Any] = None
    branded_content_tag_info: pos[BrandedContentTagInfo] = None
    shopping_info: pos[Any] = None
    additional_audio_info: pos[AdditionalAudioInfo] = None
    is_shared_to_fb: pos[bool] = None
    breaking_content_info: pos[Any] = None
    challenge_info: pos[Any] = None
    reels_on_the_rise_info: pos[Any] = None
    breaking_creator_info: pos[Any] = None
    asset_recommendation_info: pos[Any] = None
    contextual_highlight_info: pos[Any] = None
    clips_creation_entry_point: pos[str] = None
    audio_ranking_info: pos[AudioRankingInfo] = None
    template_info: pos[Any] = None
    is_fan_club_promo_video: pos[bool] = None
    disable_use_in_clips_client_cache: pos[bool] = None
    content_appreciation_info: pos[ContentAppreciationInfo] = None
    achievements_info: pos[AchievementsInfo] = None
    show_achievements: pos[bool] = None
    show_tips: pos[Any] = None
    merchandising_pill_info: pos[Any] = None
    is_public_chat_welcome_video: pos[bool] = None
    professional_clips_upsell_type: pos[int] = None
    external_media_info: pos[Any] = None
    cutout_sticker_info: pos[Any] = None


class Item(BaseModel):
    taken_at: pos[int] = None
    pk: pos[int] = None
    id: pos[str] = None
    device_timestamp: pos[int] = None
    client_cache_key: pos[str] = None
    filter_type: pos[int] = None
    caption_is_edited: pos[bool] = None
    like_and_view_counts_disabled: pos[bool] = None
    strong_id__: pos[str] = None
    is_reshare_of_text_post_app_media_in_ig: pos[bool] = None
    is_post_live_clips_media: pos[bool] = None
    deleted_reason: pos[int] = None
    integrity_review_decision: pos[str] = None
    has_shared_to_fb: pos[int] = None
    is_unified_video: pos[bool] = None
    should_request_ads: pos[bool] = None
    is_visual_reply_commenter_notice_enabled: pos[bool] = None
    commerciality_status: pos[str] = None
    explore_hide_comments: pos[bool] = None
    has_delayed_metadata: pos[bool] = None
    is_quiet_post: pos[bool] = None
    mezql_token: pos[str] = None
    shop_routing_user_id: pos[Any] = None
    can_see_insights_as_brand: pos[bool] = None
    is_organic_product_tagging_eligible: pos[bool] = None
    fb_like_count: pos[int] = None
    has_liked: pos[bool] = None
    has_privately_liked: pos[bool] = None
    like_count: pos[int] = None
    facepile_top_likers: pos[array] = None
    top_likers: pos[array] = None
    video_subtitles_confidence: pos[float] = None
    video_subtitles_uri: pos[str] = None
    media_type: pos[int] = None
    code: pos[str] = None
    can_viewer_reshare: pos[bool] = None
    caption: pos[Caption] = None
    clips_tab_pinned_user_ids: pos[array] = None
    comment_inform_treatment: pos[CommentInformTreatment] = None
    sharing_friction_info: pos[SharingFrictionInfo] = None
    play_count: pos[int] = None
    fb_play_count: pos[int] = None
    media_appreciation_settings: pos[MediaAppreciationSettings] = None
    original_media_has_visual_reply_media: pos[bool] = None
    fb_user_tags: pos[FbUserTags] = None
    invited_coauthor_producers: pos[array] = None
    can_viewer_save: pos[bool] = None
    is_in_profile_grid: pos[bool] = None
    profile_grid_control_enabled: pos[bool] = None
    featured_products: pos[array] = None
    is_comments_gif_composer_enabled: pos[bool] = None
    highlights_info: pos[HighlightsInfo] = None
    media_cropping_info: pos[MediaCroppingInfo] = None
    product_suggestions: pos[array] = None
    user: pos[User1] = None
    image_versions2: pos[ImageVersions2] = None
    original_width: pos[int] = None
    original_height: pos[int] = None
    is_artist_pick: pos[bool] = None
    enable_media_notes_production: pos[bool] = None
    product_type: pos[str] = None
    is_paid_partnership: pos[bool] = None
    music_metadata: pos[Any] = None
    organic_tracking_token: pos[str] = None
    is_third_party_downloads_eligible: pos[bool] = None
    ig_media_sharing_disabled: pos[bool] = None
    open_carousel_submission_state: pos[str] = None
    is_open_to_public_submission: pos[bool] = None
    comment_threading_enabled: pos[bool] = None
    max_num_visible_preview_comments: pos[int] = None
    has_more_comments: pos[bool] = None
    preview_comments: pos[array] = None
    comments: pos[array] = None
    comment_count: pos[int] = None
    can_view_more_preview_comments: pos[bool] = None
    hide_view_all_comment_entrypoint: pos[bool] = None
    inline_composer_display_condition: pos[str] = None
    is_auto_created: pos[bool] = None
    is_cutout_sticker_allowed: pos[bool] = None
    enable_waist: pos[bool] = None
    owner: pos[Owner] = None
    is_dash_eligible: pos[int] = None
    video_dash_manifest: pos[str] = None
    number_of_qualities: pos[int] = None
    video_versions: pos[array[VideoVersion]] = None
    video_duration: pos[float] = None
    has_audio: pos[bool] = None
    clips_metadata: pos[ClipsMetadata] = None


class InstagramMedia(BaseModel):
    items: pos[array[Item]] = None
    num_results: pos[int] = None
    more_available: pos[bool] = None
    auto_load_more_enabled: pos[bool] = None
    showQRModal: pos[bool] = None


class EdgeOwnerToTimelineMedia(BaseModel):
    count: int


class EdgeFollowedBy(BaseModel):
    count: int


class EdgeFollow(BaseModel):
    count: int


class InstagramUser(BaseModel):
    id: pos[int] = None
    username: pos[str] = None
    full_name: pos[str] = None
    biography: pos[str] = None
    avatar: pos[str] = None
    profile_pic_url_hd: pos[str] = None
    is_private: pos[bool] = None
    is_verified: pos[bool] = None
    edge_owner_to_timeline_media: pos[EdgeOwnerToTimelineMedia] = None
    edge_followed_by: pos[EdgeFollowedBy] = None
    edge_follow: pos[EdgeFollow] = None
    posts: pos[array] = None


class GoogleImageResult(BaseModel):
    url: pos[str] = None
    title: pos[str] = None
    source: pos[str] = None
    domain: pos[str] = None
    color: pos[str] = None


class GoogleImageRequest(BaseModel):
    query_time: pos[float] = None
    status: pos[str] = None
    results: pos[array[GoogleImageResult]] = []


class GoogleSearchResult(BaseModel):
    title: pos[str] = None
    alt: pos[str] = None
    website: pos[str] = None
    url: pos[str] = None
    color: pos[str] = None


class GoogleSearchRequest(BaseModel):
    RootModel: array[GoogleSearchResult]


class TikTokUser(BaseModel):
    id: pos[str] = None
    username: pos[str] = None
    display_name: pos[str] = None
    avatar: pos[str] = None
    bio: pos[str] = None
    verified: pos[one[str, bool]] = False
    private: pos[one[str, bool]] = False
    likes: pos[int] = 0
    followers: pos[int] = 0
    following: pos[int] = 0
    videos: pos[int] = 0
    tiktok_logo: pos[str] = None
    tiktok_color: pos[str] = None
    avatar_color: pos[str] = None


class TikTokVideoStatistics(BaseModel):
    aweme_id: pos[str] = None
    comment_count: pos[int] = 0
    digg_count: pos[int] = 0
    download_count: pos[int] = 0
    play_count: pos[int] = 0
    share_count: pos[int] = 0
    lose_count: pos[int] = 0
    lose_comment_count: pos[int] = 0
    whatsapp_share_count: pos[int] = 0
    collect_count: pos[int] = 0


class TikTokPost(BaseModel):
    is_video: pos[bool] = False
    items: array[str]
    desc: pos[str] = None
    username: pos[str] = None
    nickname: pos[str] = None
    avatar: pos[str] = None
    stats: TikTokVideoStatistics
    url: pos[str] = None


class TwitterLinks(BaseModel):
    display_url: pos[str] = None
    expanded_url: pos[str] = None
    url: pos[str] = None
    indices: array[int]


class TwitterUser(BaseModel):
    error: pos[str] = None
    username: pos[str] = None
    nickname: pos[str] = None
    bio: pos[str] = None
    location: pos[str] = None
    links: pos[array[TwitterLinks]] = None
    avatar: pos[str] = None
    banner: pos[str] = None
    tweets: pos[int] = 0
    media: pos[int] = None
    followers: pos[int] = 0
    following: pos[int] = 0
    creation: pos[int] = 0
    private: pos[bool] = False
    verified: pos[bool] = False
    id: pos[one[str, int]] = None


class ColorSearch(BaseModel):
    hex: pos[str] = None


class Card(BaseModel):
    small: str
    large: str
    wide: str
    id: str


class VData(BaseModel):
    puuid: str
    region: str
    account_level: int
    name: str
    tag: str
    card: Card
    last_update: str
    last_update_raw: int


class Valorant(BaseModel):
    error: pos[str] = None
    status: pos[int] = None
    data: pos[VData] = None


class Fields(BaseModel):
    name: str
    value: str
    inline: bool


class Author(BaseModel):
    name: str
    url: str
    icon_url: str


class Image(BaseModel):
    url: str


class Thumbnail(BaseModel):
    url: str


class Footer(BaseModel):
    text: str
    icon_url: str


class Embeds(BaseModel):
    fields: array[Fields]
    author: Author
    title: str
    description: str
    image: Image
    thumbnail: Thumbnail
    color: int
    footer: Footer
    timestamp: str


class Embed(BaseModel):
    error: pos[str] = None
    content: pos[str] = None
    embed: pos[Embeds] = None
    delete_after: pos[int] = None


class EmbedFetch(BaseModel):
    status: pos[str] = None
    embed: pos[str] = None


class RobloxStatistics(BaseModel):
    friends: pos[int] = 0
    followers: pos[int] = 0
    following: pos[int] = 0


class Roblox(BaseModel):
    error: pos[str] = None
    url: pos[str] = None
    id: pos[int] = None
    username: pos[str] = None
    display_name: pos[str] = None
    avatar_url: pos[str] = None
    description: pos[Any] = None
    created_at: pos[int] = None
    last_online: pos[Any] = None
    last_location: pos[Any] = None
    badges: pos[array] = None
    statistics: pos[RobloxStatistics] = None


class EmbedException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.kwargs = kwargs


class InvalidURL(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.kwargs = kwargs


class Transcribe(BaseModel):
    time_elapsed: pos[one[float, str]] = 0.0
    text: pos[str] = None
    
    
class DiscordUser(BaseModel):
    id: str
    username: str
    avatar: pos[str]
    discriminator: str
    public_flags: int
    premium_type: pos[int]
    flags: int
    banner: pos[str]
    accent_color: int
    global_name: str
    avatar_decoration_data: pos[dict]
    banner_color: str
    tag: str
    createdAt: str
    createdTimestamp: int
    public_flags_array: array[str]
    defaultAvatarURL: str
    avatarURL: pos[str]
    bannerURL: pos[str]
    bio: pos[str]
    premium_since: pos[str]
    premium_guild_since: pos[str]