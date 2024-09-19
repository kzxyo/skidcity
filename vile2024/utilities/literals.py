from munch import Munch
from os import environ
from typing import Any


Emojis = emojis = Munch({
    "slash": "<:v_slash:1067034025895665745>",
    "done": "<:v_done:1067033981452828692>",
    "fail": "<:v_fail:1067034031381807124>",
    "warn": "<:v_warn:1067034029569888266>",
    "dash": "",
    "reply": "<:vile_reply:997487959093825646>"
})
    
    
Colors = colors = Munch({
    "main": 0xb1aad8,
    "invisible": 0x2b2d31
})


KEYS = API = keys = api = Munch({
    "discord": environ.get("DISCORD_TOKEN"),
    "proxies": environ.get("PROXIES"),
    "rival": environ.get("RIVAL_API_KEY"),
    "fernet": environ.get("FERNET_KEY"),
    "apininjas": environ.get("APININJAS_API_KEY"),
    "huggingface": environ.get("HUGGINGFACE_API_KEY"),
    "sightengine": environ.get("SIGHTENGINE_API_KEY"),
    "redis": environ.get("REDIS_PASSWD"),
    "spotify": environ.get("SPOTIFY_AUTH"),
    "mariadb": environ.get("MARIADB_PASSWORD"),
    "lastfm": environ.get("LASTFM_API_KEY"),
    "wolfram": environ.get("WOLFRAM_API_KEY")
})