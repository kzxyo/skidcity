from typing import Any, List, Optional
import aiohttp,humanize,arrow,discord,re
from pydantic import BaseModel, Field

def find_hashtags(text):
    r=re.findall("(#+[a-zA-Z0-9(_)]{1,})",text)
    return r

class ShareInfo(BaseModel):
    share_title: Optional[str]
    bool_persist: Optional[int]
    share_title_myself: Optional[str]
    share_signature_desc: Optional[str]
    share_signature_url: Optional[str]
    share_quote: Optional[str]
    share_desc_info: Optional[str]
    share_url: Optional[str]
    share_weibo_desc: Optional[str]
    share_desc: Optional[str]
    share_title_other: Optional[str]
    share_link_desc: Optional[str]


class VideoIcon(BaseModel):
    uri: Optional[str]
    url_list: Optional[List[str]]
    width: Optional[int]
    height: Optional[int]


class ShareQrcodeUrl(BaseModel):
    url_list: Optional[List]
    width: Optional[int]
    height: Optional[int]
    uri: Optional[str]


class Author(BaseModel):
    status: Optional[int]
    uniqueId: Optional[str] = Field(None, alias="unique_id")
    avatar_300x300: Optional[VideoIcon]
    has_youtube_token: Optional[bool]
    authority_status: Optional[int]
    shield_comment_notice: Optional[int]
    with_commerce_entry: Optional[bool]
    is_discipline_member: Optional[bool]
    unique_id_modify_time: Optional[int]
    sec_uid: Optional[str]
    user_tags: Optional[Any]
    advance_feature_item_order: Optional[Any]
    user_mode: Optional[int]
    aweme_count: Optional[int]
    region: Optional[str]
    prevent_download: Optional[bool]
    is_phone_binded: Optional[bool]
    accept_private_policy: Optional[bool]
    enterprise_verify_reason: Optional[str]
    youtube_channel_id: Optional[str]
    bind_phone: Optional[str]
    has_twitter_token: Optional[bool]
    fb_expire_time: Optional[int]
    room_id: Optional[int]
    live_verify: Optional[int]
    shield_digg_notice: Optional[int]
    avatar_medium: Optional[VideoIcon]
    shield_follow_notice: Optional[int]
    ins_id: Optional[str]
    download_setting: Optional[int]
    item_list: Optional[Any]
    live_agreement: Optional[int]
    download_prompt_ts: Optional[int]
    share_info: Optional[ShareInfo]
    user_canceled: Optional[bool]
    cover_url: Optional[List[VideoIcon]]
    comment_filter_status: Optional[int]
    need_points: Optional[Any]
    has_email: Optional[bool]
    cv_level: Optional[str]
    type_label: Optional[Any]
    homepage_bottom_toast: Optional[Any]
    bold_fields: Optional[Any]
    mutual_relation_avatars: Optional[Any]
    video_icon: Optional[VideoIcon]
    create_time: Optional[int]
    uid: Optional[str]
    nickname: Optional[str]
    follower_count: Optional[int]
    verify_info: Optional[str]
    followers_detail: Optional[Any]
    account_region: Optional[str]
    avatar_168x168: Optional[VideoIcon]
    total_favorited: Optional[int]
    hide_search: Optional[bool]
    commerce_user_level: Optional[int]
    platform_sync_info: Optional[Any]
    google_account: Optional[str]
    youtube_channel_title: Optional[str]
    custom_verify: Optional[str]
    is_ad_fake: Optional[bool]
    follower_status: Optional[int]
    live_commerce: Optional[bool]
    is_star: Optional[bool]
    relative_users: Optional[Any]
    avatar_thumb: Optional[VideoIcon]
    is_block: Optional[bool]
    show_image_bubble: Optional[bool]
    twitter_id: Optional[str]
    comment_setting: Optional[int]
    react_setting: Optional[int]
    signature: Optional[str]
    following_count: Optional[int]
    tw_expire_time: Optional[int]
    has_orders: Optional[bool]
    cha_list: Optional[Any]
    search_highlight: Optional[Any]
    avatar_larger: Optional[VideoIcon]
    need_recommend: Optional[int]
    duet_setting: Optional[int]
    share_qrcode_uri: Optional[str]
    user_period: Optional[int]
    user_rate: Optional[int]
    ad_cover_url: Optional[Any]
    short_id: Optional[str]
    special_lock: Optional[int]
    has_facebook_token: Optional[bool]
    with_shop_entry: Optional[bool]
    secret: Optional[int]
    apple_account: Optional[int]
    can_set_geofencing: Optional[Any]
    white_cover_url: Optional[Any]
    youtube_expire_time: Optional[int]
    verification_type: Optional[int]
    geofencing: Optional[Any]
    twitter_name: Optional[str]
    language: Optional[str]
    has_insights: Optional[bool]
    follow_status: Optional[int]
    favoriting_count: Optional[int]
    avatar_uri: Optional[str]
    stitch_setting: Optional[int]
    events: Optional[Any]

    @property
    def embed_icon(self):
        return next(filter(lambda x: "gif" or "jpeg" in x, self.avatar_medium.url_list))


class GroupIdList(BaseModel):
    groupd_id_list0: Optional[Any] = Field(None, alias="GroupdIdList0")
    groupd_id_list1: Optional[List[int]] = Field(None, alias="GroupdIdList1")


class DownloadAddr(BaseModel):
    height: Optional[int]
    data_size: Optional[int]
    uri: Optional[str]
    url_list: Optional[List[str]]
    width: Optional[int]


class PlayAddr(BaseModel):
    height: Optional[int]
    url_key: Optional[str]
    data_size: Optional[int]
    file_hash: Optional[str]
    file_cs: Optional[str]
    uri: Optional[str]
    url_list: Optional[List[str]]
    width: Optional[int]


class OriginCover(BaseModel):
    url_list: Optional[List[str]]
    width: Optional[int]
    height: Optional[int]
    uri: Optional[str]


class BitRateItem(BaseModel):
    gear_name: Optional[str]
    quality_type: Optional[int]
    bit_rate: Optional[int]
    play_addr: Optional[PlayAddr]
    is_h265: Optional[int]
    is_bytevc1: Optional[int]
    dub_infos: Optional[Any]


class Video(BaseModel):
    has_watermark: Optional[bool]
    bytes: Optional[bytes]
    download_addr: Optional[DownloadAddr]
    is_callback: Optional[bool]
    big_thumbs: Optional[Any]
    is_bytevc1: Optional[int]
    ai_dynamic_cover: Optional[VideoIcon]
    ai_dynamic_cover_bak: Optional[VideoIcon]
    ratio: Optional[str]
    height: Optional[int]
    need_set_token: Optional[bool]
    tags: Optional[Any]
    play_addr: Optional[PlayAddr]
    width: Optional[int]
    dynamic_cover: Optional[VideoIcon]
    origin_cover: Optional[OriginCover]
    bit_rate: Optional[List[BitRateItem]]
    duration: Optional[int]
    is_h265: Optional[int]
    cdn_url_expired: Optional[int]
    cover: Optional[VideoIcon]
    meta: Optional[str]


class RiskInfos(BaseModel):
    type: Optional[int]
    content: Optional[str]
    vote: Optional[bool]
    warn: Optional[bool]
    risk_sink: Optional[bool]




class CommerceInfo(BaseModel):
    auction_ad_invited: Optional[bool]
    with_comment_filter_words: Optional[bool]
    adv_promotable: Optional[bool]


class ReviewResult(BaseModel):
    review_status: Optional[int]


class Status(BaseModel):
    is_delete: Optional[bool]
    allow_comment: Optional[bool]
    private_status: Optional[int]
    reviewed: Optional[int]
    is_prohibited: Optional[bool]
    review_result: Optional[ReviewResult]
    aweme_id: Optional[str]
    allow_share: Optional[bool]
    in_reviewing: Optional[bool]
    self_see: Optional[bool]
    download_status: Optional[int]


class ChorusInfo(BaseModel):
    start_ms: Optional[int]
    duration_ms: Optional[int]


class MatchedSong(BaseModel):
    id: Optional[str]
    author: Optional[str]
    title: Optional[str]
    h5_url: Optional[str]
    cover_medium: Optional[VideoIcon]
    performers: Optional[Any]
    chorus_info: Optional[ChorusInfo]


class MatchedPgcSound(BaseModel):
    title: Optional[str]
    mixed_title: Optional[str]
    mixed_author: Optional[str]
    author: Optional[str]


class Music(BaseModel):
    user_count: Optional[int]
    external_song_info: Optional[List]
    is_author_artist: Optional[bool]
    lyric_short_position: Optional[Any]
    cover_medium: Optional[VideoIcon]
    extra: Optional[str]
    status: Optional[int]
    owner_handle: Optional[str]
    shoot_duration: Optional[int]
    is_original: Optional[bool]
    mid: Optional[str]
    sec_uid: Optional[str]
    artists: Optional[List]
    source_platform: Optional[int]
    duration: Optional[int]
    position: Optional[Any]
    author_position: Optional[Any]
    strong_beat_url: Optional[OriginCover]
    avatar_thumb: Optional[VideoIcon]
    id_str: Optional[str]
    album: Optional[str]
    collect_stat: Optional[int]
    owner_id: Optional[str]
    owner_nickname: Optional[str]
    avatar_medium: Optional[VideoIcon]
    tag_list: Optional[Any]
    matched_song: Optional[MatchedSong]
    search_highlight: Optional[Any]
    author: Optional[str]
    cover_large: Optional[VideoIcon]
    play_url: Optional[VideoIcon]
    audition_duration: Optional[int]
    video_duration: Optional[int]
    is_pgc: Optional[bool]
    is_matched_metadata: Optional[bool]
    is_audio_url_with_cookie: Optional[bool]
    offline_desc: Optional[str]
    binded_challenge_id: Optional[int]
    prevent_download: Optional[bool]
    preview_end_time: Optional[int]
    is_original_sound: Optional[bool]
    multi_bit_rate_play_info: Optional[Any]
    is_commerce_music: Optional[bool]
    mute_share: Optional[bool]
    dmv_auto_show: Optional[bool]
    id: Optional[int]
    title: Optional[str]
    cover_thumb: Optional[VideoIcon]
    author_deleted: Optional[bool]
    preview_start_time: Optional[int]
    matched_pgc_sound: Optional[MatchedPgcSound]


class VideoControl(BaseModel):
    allow_duet: Optional[bool]
    allow_download: Optional[bool]
    show_progress_bar: Optional[int]
    draft_progress_bar: Optional[int]
    allow_dynamic_wallpaper: Optional[bool]
    timer_status: Optional[int]
    allow_music: Optional[bool]
    allow_stitch: Optional[bool]
    share_type: Optional[int]
    allow_react: Optional[bool]
    prevent_download_type: Optional[int]


class Extra(BaseModel):
    fatal_item_ids: Optional[List]
    logid: Optional[str]
    now: Optional[int]


class LogPb(BaseModel):
    impr_id: Optional[str]


class Image(BaseModel):
    user_watermark_image: Optional[VideoIcon]
    thumbnail: Optional[VideoIcon]
    display_image: Optional[VideoIcon]
    owner_watermark_image: Optional[VideoIcon]


class ImagePostCover(BaseModel):
    thumbnail: Optional[VideoIcon]
    display_image: Optional[VideoIcon]
    owner_watermark_image: Optional[VideoIcon]
    user_watermark_image: Optional[VideoIcon]


class ImagePostInfo(BaseModel):
    music_volume: Optional[float]
    images: Optional[List[Image]]
    image_post_cover: Optional[ImagePostCover]


class TiktokPostRequest(BaseModel):
    url: str


class TikTokVideoResponse(BaseModel):
    video_url: Optional[str]
    filename: Optional[str]
    id: Optional[int] = Field(None, alias="aweme_id")
    heart_count: Optional[int] = Field(None, alias="digg_count")
    play_count: Optional[int]
    share_count: Optional[int]
    aweme_id: Optional[str]
    comment_count: Optional[int]
    lose_count: Optional[int]
    lose_comment_count: Optional[int]
    whatsapp_share_count: Optional[int]
    collect_count: Optional[int]
    download_count: Optional[int]
    forward_count: Optional[int]
    group_id: Optional[str]
    image_post_info: Optional[ImagePostInfo]
    item_comment_settings: Optional[int]
    desc_language: Optional[str]
    geofencing_regions: Optional[Any]
    search_highlight: Optional[Any]
    geofencing: Optional[Any]
    anchors: Optional[Any]
    playlist_blocked: Optional[bool]
    question_list: Optional[Any]
    share_info: Optional[ShareInfo]
    long_video: Optional[Any]
    without_watermark: Optional[bool]
    distribute_type: Optional[int]
    green_screen_materials: Optional[Any]
    content_desc: Optional[str]
    position: Optional[Any]
    is_pgcshow: Optional[bool]
    disable_search_trending_bar: Optional[bool]
    music_begin_time_in_ms: Optional[int]
    create_time: Optional[int]
    author: Optional[Author]
    video_labels: Optional[List]
    sort_label: Optional[str]
    video_text: Optional[List]
    label_top_text: Optional[Any]
    commerce_config_data: Optional[Any]
    item_stitch: Optional[int]
    group_id_list: Optional[GroupIdList]
    share_url: Optional[str]
    label_top: Optional[VideoIcon]
    nickname_position: Optional[Any]
    misc_info: Optional[str]
    video: Optional[Video]
    risk_infos: Optional[RiskInfos]
    is_relieve: Optional[bool]
    interaction_stickers: Optional[Any]
    origin_comment_ids: Optional[Any]
    mask_infos: Optional[List]
    distance: Optional[str]
    author_user_id: Optional[int]
    region: Optional[str]
    user_digged: Optional[int]
    text_extra: Optional[List]
    bodydance_score: Optional[int]
    collect_stat: Optional[int]
    prevent_download: Optional[bool]

    # statistics: Optional[Statistics] = Field(None, alias="stats")
    uniqid_position: Optional[Any]
    with_promotional_music: Optional[bool]
    challenge_position: Optional[Any]
    item_react: Optional[int]
    commerce_info: Optional[CommerceInfo]
    follow_up_publish_from_id: Optional[int]
    is_ads: Optional[bool]
    cmt_swt: Optional[bool]
    item_duet: Optional[int]
    is_preview: Optional[int]
    cha_list: Optional[Any]
    aweme_type: Optional[int]
    desc: Optional[str]
    rate: Optional[int]
    have_dashboard: Optional[bool]
    status: Optional[Status]
    is_top: Optional[int]
    is_vr: Optional[bool]
    hybrid_label: Optional[Any]
    products_info: Optional[Any]
    music: Optional[Music]
    image_infos: Optional[Any]
    is_hash_tag: Optional[int]
    video_control: Optional[VideoControl]
    cover_labels: Optional[Any]
    need_trim_step: Optional[bool]
    content_desc_extra: Optional[List]
    music_end_time_in_ms: Optional[int]
    direct_download_urls: Optional[List[str]]

    @property
    def images(self) -> List[str]:
        return [i.display_image.url_list[-1] for i in self.image_post_info.images] if self.image_post_info else None

    def format(self, text):
        if " thousand" in text:
            text=text.replace(" thousand", "k")
        if " million" in text:
            text=text.replace(" million", "m")
        return text

    def make_embed(self, requester: discord.User) -> discord.Embed:
        desc = self.desc
        hashtags = find_hashtags(desc)
        des=desc.split(" ")
        for d in des:
            if d.startswith("#"):
                des.remove(d)
        description=re.sub("#(\w+)",""," ".join(d for d in des))
        embed_desc = f"[TikTok]({self.share_url}) requested by {requester.mention}"
        if len(desc) > 3:
            embed_desc = embed_desc + "\n" + desc + "\n" + "Powered by [MelanieBot](https://melaniebot.gg)"

        embed = discord.Embed(color=3092790, description=description)

        embed.timestamp = arrow.get(self.create_time).datetime
        try:
            embed.set_footer(text=f"\n❤️  {self.format(humanize.intword(self.heart_count))}   👀  {self.format(humanize.intword(self.play_count))}   💬  {self.format(humanize.intword(self.comment_count))} ", icon_url="https://cdn.discordapp.com/emojis/1010602768660181012.png?size=256")
            embed.set_author(name=f"{self.author.uniqueId}", icon_url=self.author.embed_icon, url=f"https://www.tiktok.com/@{self.author.uniqueId}")

        except TypeError:
            log.exception("Building tiktok ")

        return embed

    def make_embeds(self, requester:discord.User, urls:list) -> list:
        embeds=[]
        desc = self.desc
        page_count=len(urls)
        c=0
        hashtags = find_hashtags(desc)
        des=desc.split(" ")
        for d in des:
            if d.startswith("#"):
                des.remove(d)
        description=" ".join(d for d in des)
        embed_desc = f"[TikTok]({self.share_url}) requested by {requester.mention}"
        if len(desc) > 3:
            embed_desc = embed_desc + "\n" + desc
        for fff in urls:
            embed = discord.Embed(color=3092790, description=description)
            c+=1
            embed.timestamp = arrow.get(self.create_time).datetime
            try:
                embed.set_image(url=fff)
                embed.set_footer(text=f"\n❤️  {self.format(humanize.intword(self.heart_count))}   👀  {self.format(humanize.intword(self.play_count))}   💬  {self.format(humanize.intword(self.comment_count))}\nPage {c}/{page_count}", icon_url="https://cdn.discordapp.com/emojis/1010602768660181012.png?size=256")
                embed.set_author(name=f"{self.author.uniqueId}", icon_url=self.author.embed_icon, url=f"https://www.tiktok.com/@{self.author.uniqueId}")
            except TypeError:
                log.exception("Building tiktok ")
            embeds.append(embed)
        return embeds


        

    @classmethod
    async def from_url(cls, session: aiohttp.ClientSession, ctx, url: str):
        async with session.post("https://dev.melaniebot.gg/api/tiktok/post", json={"url": url, "user_id": f"{ctx.author.id}", "guild_id": f"{ctx.guild.id}"}) as r:
            return cls.parse_raw(await r.read())
