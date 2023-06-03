import random
from enum import Enum

VIVISMIRK = "<:vivismirk:749950217218162719>"

UPVOTE = "<:upvote:943946200137216010>"
DOWNVOTE = "<:downtriangle:943946738119606292>"

GREEN_UP = "<:uptriangle:943947249099100261>"
RED_DOWN = "<:red_triangle_down:749966805908455526>"

LOADING = "<a:loading:940728015640481822>"
TYPING = "<a:typing:749966793480732694>"

LASTFM = "<:lfm:945412052074242139>"


class Status(Enum):
    online = "<:online:918448221729222678>"
    idle = "<:away:918448096197894154>"
    dnd = "<:dnd:918447677677645824>"
    offline = "<:offline:918448174924955679>"
    streaming = "<:streaming:888859420191256668>"
    mobile = "<:mobile:918446884459274240>"


class Badge(Enum):
    staff = "<:DBE_DiscordStaff:910240590128615425>"
    partner = "<:DBE_partner:929524203651215390>"
    nitro = "<:x_Nitro:910602220842672168>"
    hypesquad = "<:x_HypeSquadEvents:910247032055300106>"
    hypesquad_brilliance = "<:x_HypeSquadBrilliance:910240944526356500>"
    hypesquad_bravery = "<:x_HypeSquadBravery:910240943062540359>"
    hypesquad_balance = "<:x_HypeSquadBalance:910240941737119765>"
    verified_bot_developer = "<:DBE_EarlyVerifiedBotDeveloper:910240588991967294>"
    early_supporter = "<:x_EarlySupporter:910247033321975818>"
    bug_hunter = "<:bughunter:943944180948959233>"
    bug_hunter_level_2 = "<:DBE_BugHunterTier2:929519765473599499>"
    team_user = "<a:a_verified:906294820690096138>"
    system = ""
    verified_bot = "<:DBE_verifiedbot:910240636253380679>"
    boosting = "<:booster:943944869464911902>"


HUGS = [
    "<:miso_hug_muses:749948266006839346>",
    "<:miso_hug_gugu:749948228681597008>",
    "<:miso_hug_gidle_2:749948199271268432>",
    "<:miso_hug_gidle:749948173430161449>",
    "<:miso_hug_fromis:749948142467678268>",
    "<:miso_hug_dc:749948105335636010>",
    "<:miso_hug_clc:749948066399780915>",
    "<:miso_hug_chungha:749948024469585972>",
]

ANIMATED_HUGS = [
    "<a:miso_a_hug_loona_3:749948536853889024>",
    "<a:miso_a_hug_loona_2:749948506780729344>",
    "<a:miso_a_hug_itzy_2:749949471449940039>",
    "<a:miso_a_hug_loona:749949983351898143>",
    "<a:miso_a_hug_itzy:749949194835460138>",
    "<a:miso_a_hug_gidle:749949555558055966>",
    "<a:miso_a_hug_twice:749951935490293810>",
]


def random_hug(a=True):
    return random.choice(HUGS + ANIMATED_HUGS if a else [])
