from moviepy.editor import *
import glob, re
from yt_dlp import YoutubeDL
from io import BytesIO

cookies = {}
regexes = [
    "https:\/\/www\.instagram\.com\/reel\/([a-zA-Z0-9_\-]*)",
]
regexes = [re.compile(x) for x in regexes]


async def download(url, filename):
    opts = {"outtmpl": f"{filename}.%(ext)s", "format": "bestaudio/best"}
    with YoutubeDL(opts) as ytdl:
        ytdl.download([str(url)])
    path = glob.glob(f"{filename}.*")[0]
    clip = VideoFileClip(path)
    clip1 = clip.subclip(0, 7)
    w1 = clip1.w
    h1 = clip1.h
    print("Width x Height of clip 1 : ", end=" ")
    print(str(w1) + " x ", str(h1))
    clip2 = clip1.resize(0.5)
    w2 = clip2.w
    h2 = clip2.h
    print("Width x Height of clip 2 : ", end=" ")
    print(str(w2) + " x ", str(h2))
    a = clip2.write_videofile("reel.mp4")


async def binary():
    with open("reel.mp4", "rb") as fh:
        return BytesIO(fh.read())


async def check_url(content):
    for regex in regexes:
        matches = re.search(regex, content)

        if matches:
            state = bool(matches)
            url = matches[0]
            id = matches[1]
            return state, url, id
    return False, None, None
