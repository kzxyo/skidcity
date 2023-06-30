import re


PERCENTAGE = re.compile(r"(?P<percentage>\d+)%")
BITRATE = re.compile(r"(?P<bitrate>\d+)kbps")
IMAGE_URL = re.compile(r"(?:http\:|https\:)?\/\/.*\.(?P<mime>png|jpg|jpeg|webp|gif)")
URL = re.compile(r"(?:http\:|https\:)?\/\/[^\s]*")


class Position:
    HH_MM_SS = re.compile(r"(?P<h>\d{1,2}):(?P<m>\d{1,2}):(?P<s>\d{1,2})")
    MM_SS = re.compile(r"(?P<m>\d{1,2}):(?P<s>\d{1,2})")
    HUMAN = re.compile(r"(?:(?P<m>\d+)\s*m\s*)?(?P<s>\d+)\s*[sm]")
    OFFSET = re.compile(r"(?P<s>(?:\-|\+)\d+)\s*s")


DISCORD_FILE = re.compile(
    r"(https://|http://)?(cdn\.|media\.)discord(app)?\.(com|net)/(attachments|avatars|icons|banners|splashes)/[0-9]{17,22}/([0-9]{17,22}/(?P<filename>.{1,256})|(?P<hash>.{32}))\.(?P<mime>[0-9a-zA-Z]{2,4})?"
)
