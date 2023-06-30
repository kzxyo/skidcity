from random import choice
from typing import Dict

from yarl import URL

import config

from helpers.managers import BaseModel, ClientSession
from helpers.models import LastfmProfile, LastfmProfileInformation, LastfmProfileLibrary


async def request(
    session: ClientSession,
    payload: Dict,
    slug: str = None,
    **kwargs,
) -> BaseModel:
    payload.pop("autocorrect", 0)
    payload.update(
        {
            "api_key": choice(config.Authorization.lastfm),
            "autocorrect": 0,
            "format": "json",
        }
    )

    data = await session.request(
        "GET",
        f"http://ws.audioscrobbler.com/2.0/",
        params=payload,
        **kwargs,
    )

    if not slug:
        return data
    else:
        return getattr(data, slug, None)


async def profile(
    session: ClientSession,
    username: str,
) -> LastfmProfile:
    data = await request(
        session,
        payload={
            "method": "user.getInfo",
            "username": username,
        },
        slug="user",
        raise_for={
            404: f"[**{username}**]({URL(f'https://last.fm/user/{username}')}) is not a valid **Last.fm** account"
        },
    )

    return LastfmProfile(
        url=data.url,
        username=data.name,
        display_name=data.realname,
        avatar_url=data.image[-1].text,
        information=LastfmProfileInformation(
            registered=data.registered.text,
            country=(data.country if data.country != "None" else "Unknown"),
            age=data.age,
            pro=data.subscriber == "1",
        ),
        library=LastfmProfileLibrary(
            scrobbles=data.playcount,
            artists=data.artist_count,
            albums=data.artist_count,
            tracks=data.track_count,
        ),
    )
