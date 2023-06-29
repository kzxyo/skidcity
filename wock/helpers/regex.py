import re


DISCORD_ID = re.compile(r"(\d+)")
DISCORD_DISCRIMINATOR = re.compile(r"(\d{4})")
DISCORD_USER_MENTION = re.compile(r"<@?(\d+)>")
DISCORD_ROLE_MENTION = re.compile(r"<@&(\d+)>")
DISCORD_CHANNEL_MENTION = re.compile(r"<#(\d+)>")
DISCORD_MESSAGE = re.compile(
    r"(?:https?://)?(?:canary\.|ptb\.|www\.)?discord(?:app)?.(?:com/channels|gg)/(?P<guild_id>[0-9]{17,22})/(?P<channel_id>[0-9]{17,22})/(?P<message_id>[0-9]{17,22})"
)
DISCORD_INVITE = re.compile(r"(?:https?://)?discord(?:app)?.(?:com/invite|gg)/[a-zA-Z0-9]+/?")
DISCORD_ATTACHMENT = re.compile(
    r"(https://|http://)?(cdn\.|media\.)discord(app)?\.(com|net)/(attachments|avatars|icons|banners|splashes)/[0-9]{17,22}/([0-9]{17,22}/(?P<filename>.{1,256})|(?P<hash>.{32}))\.(?P<mime>[0-9a-zA-Z]{2,4})?"
)
DISCORD_EMOJI = re.compile(r"<(?P<animated>a)?:(?P<name>[a-zA-Z0-9_]+):(?P<id>\d+)>")

TIKTOK_DESKTOP_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?tiktok\.com\/@.*\/video\/\d+")
TIKTOK_MOBILE_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www|vm|vt|m).tiktok\.com\/(?:t/)?(\w+)")
INSTAGRAM_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?instagram\.com\/(?:p|tv|reel)\/(?P<shortcode>[a-zA-Z0-9_-]+)\/*")
TWITTER_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?twitter\.com\/(?P<screen_name>[a-zA-Z0-9_-]+)\/status\/(?P<id>\d+)")
YOUTUBE_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?youtube\.com\/watch\?v=(?P<id>[a-zA-Z0-9_-]+)")
YOUTUBE_SHORT_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?youtu\.be\/(?P<id>[a-zA-Z0-9_-]+)")
YOUTUBE_SHORTS_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?youtube\.com\/shorts\/(?P<id>[a-zA-Z0-9_-]+)")
YOUTUBE_CLIP_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?youtube\.com\/clip\/Ug(?P<id>[a-zA-Z0-9_-]+)")
YOUTUBE_CHANNEL_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?youtube\.com\/(?P<type>channel/|user/|c/|@)(?P<id>[a-zA-Z0-9_-]+)")
SOUNDCLOUD_TRACK_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?soundcloud\.com\/(?P<user>[a-zA-Z0-9_-]+)\/(?P<slug>[a-zA-Z0-9_-]+)")
SOUNDCLOUD_PLAYLIST_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?soundcloud\.com\/(?P<user>[a-zA-Z0-9_-]+)\/sets\/(?P<slug>[a-zA-Z0-9_-]+)")
PINTEREST_PIN_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?pinterest\.com\/pin\/(?P<id>[0-9]+)")
PINTEREST_PIN_APP_URL = re.compile(r"(?:http\:|https\:)?\/\/pin\.it\/(?P<id>[a-zA-Z0-9]+)")
GRAILED_LISTING_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?grailed\.com\/listings\/(?P<id>[0-9]+)")
GRAILED_LISTING_APP_URL = re.compile(r"(?:http\:|https\:)?\/\/(?:www\.)?grailed\.app\.link\/(?P<id>[a-zA-Z0-9]+)")

IMAGE_URL = re.compile(r"(?:http\:|https\:)?\/\/.*\.(?P<mime>png|jpg|jpeg|webp|gif)")
MEDIA_URL = re.compile(r"(?:http\:|https\:)?\/\/.*\.(?P<mime>mp3|mp4|mpeg|mpga|m4a|wav|mov|webm)")
URL = re.compile(r"(?:http\:|https\:)?\/\/[^\s]*")

PERCENTAGE = re.compile(r"(?P<percentage>\d+)%")
BITRATE = re.compile(r"(?P<bitrate>\d+)kbps")
TIME = re.compile(r"(?P<time>\d+)(?P<unit>[smhdw])")
TIME_HHMMSS = re.compile(r"(?P<h>\d{1,2}):(?P<m>\d{1,2}):(?P<s>\d{1,2})")
TIME_SS = re.compile(r"(?P<m>\d{1,2}):(?P<s>\d{1,2})")
TIME_HUMAN = re.compile(r"(?:(?P<m>\d+)\s*m\s*)?(?P<s>\d+)\s*[sm]")
TIME_OFFSET = re.compile(r"(?P<s>(?:\-|\+)\d+)\s*s", re.IGNORECASE)

MINECRAFT_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
NUMBER = re.compile(r"\d{1,3}(,\d{3})*")
STRING = re.compile(r"[a-zA-Z0-9 ]+")
INDICES = re.compile(r"{(\d*)}")
