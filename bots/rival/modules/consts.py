from collections import namedtuple

import discord

CUSTOM_TICKS = {
    True: ':tickYes:',
    False: ':tickNo:',
    None: ':tickNone:',
}

DEFAULT_TICKS = {
    True: '✅',
    False: '❌',
    None: '➖',
}

CUSTOM_EMOJIS = {
    'bal': ':bamboo:'
}

down=" └ "
dot=" ・ "
add="<:plus:947812413267406848>"
yes="<:yes:940723483204255794>"
rem="<:rem:947812531509026916>"
no="<:no:940723951947120650>"
good=0x77b255
bad=0xff6465
color=0xffffff
ch='<:yes:940723483204255794>'
error=0xfaa61a
warn='<:warn:940732267406454845>'

USER_FLAGS = {
    'staff': ':staff:',
    'partner': ':partnernew:',
    'hypesquad': ':hypesquad:',
    'bug_hunter': ':bughunter:',
    'hypesquad_bravery': ':bravery:',
    'hypesquad_brilliance': ':brilliance:',
    'hypesquad_balance': ':balance:',
    'early_supporter': ':supporter:',
    'bug_hunter_level_2': ':bughunter_gold:',
    'verified_bot_developer': ':verifiedbotdev:',
    'verified_bot': ':Verified:',
    'discord_certified_moderator': ':certified_moderator:'
            }

GUILD_FEATURES = {
    'ANIMATED_ICON': 'Animated Server Icon',
    'BANNER': 'Server Banner',
    'COMMERCE': 'Commerce',
    'COMMUNITY': 'Community Server',
    'DISCOVERABLE': 'Discoverable',
    'FEATURABLE': 'Featured',
    'INVITE_SPLASH': 'Invite Splash',
    'MEMBER_VERIFICATION_GATE_ENABLED': 'Membership Screening',
    'MONETIZATION_ENABLED': 'Monetization',
    'MORE_EMOJI': 'More Emoji',
    'MORE_STICKERS': 'More Stickers',
    'NEWS': 'News Channels',
    'PARTNERED': 'Partnered',
    'PREVIEW_ENABLED': 'Preview Enabled',
    'PRIVATE_THREADS': 'Private Threads',
    'SEVEN_DAY_THREAD_ARCHIVE': '1 Week Thread Archive',
    'THREE_DAY_THREAD_ARCHIVE': '3 Day Thread Archive',
    'TICKETED_EVENTS_ENABLED': 'Ticketed Events',
    'VANITY_URL': 'Vanity Invite URL',
    'VERIFIED': 'Verified',
    'VIP_REGIONS': 'VIP Voice Regions',
    'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            }


st_nt = namedtuple('statuses', ['ONLINE', 'IDLE', 'DND', 'OFFLINE'])

statuses = st_nt(
    ONLINE='<:online:918448221729222678>',
    IDLE='<:away:918448096197894154>',
    DND='<:dnd:918447677677645824>',
    OFFLINE='<:offline:918448174924955679>',
            )