import os
from dataclasses import dataclass


@dataclass
class emojis:
    slash: str = "<:v_slash:1067034025895665745>"
    done: str = "<:v_done:1067033981452828692>"
    fail: str = "<:v_fail:1067034031381807124>"
    warn: str = "<:v_warn:1067034029569888266>"
    dash: str = ""
    reply: str = "<:vile_reply:997487959093825646>"
    
    
@dataclass
class colors:
    main: int = 0xb1aad8
    invisible: int = 0x2b2d31
    
    
@dataclass
class api:
    discord: str = os.environ.get("TOKEN", "")
    rival: str = os.environ.get("RIVAL_API_KEY", "")
    apininjas: str = os.environ.get("APININJAS_API_KEY")
    lastfm: str = ""
    wolfram: str = ""
    
