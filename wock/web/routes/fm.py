import sys


sys.path.append("../")

import asyncio
import io
import json
import random

from urllib.parse import quote

import aiohttp

from quart import Blueprint, jsonify, request, send_file
from xxhash import xxh64_hexdigest

from helpers.functions import extract_color


router = Blueprint("fm", __name__, subdomain="fm")


@router.before_request
async def before_request():
    if not request.headers.get("Authorization", "") == router.config["api"].get("wock"):
        raise ValueError("This API is private.")


@router.route("/", methods=["GET"])
async def index():
    node = "FM" + xxh64_hexdigest(request.user_agent.string).upper()[:8]
    return "wock @ " + node


@router.get(
    "/profile",
    # name="Get Last.fm Profile",
    # description="Get a Last.fm user's profile",
    # parameters={
    #    "username": "Last.fm username",
    #    "library": "Indicate top item in library",
    # },
)
async def profile():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    data = await response(
        {
            "method": "user.getInfo",
            "username": username,
        },
        "user",
    )

    output = {
        "url": data["url"],
        "username": data["name"],
        "full_name": data["realname"] or None,
        "avatar": data["image"][-1]["#text"].replace(".png", ".gif") or None,
        "library": {
            "scrobbles": int(data["playcount"]),
            "artists": int(data["artist_count"]),
            "albums": int(data["album_count"]),
            "tracks": int(data["track_count"]),
        },
        "meta": {
            "registered": data["registered"]["#text"],
            "country": (data["country"] if data["country"] != "None" else None),
            "age": int(data["age"]),
            "pro": data["type"] == "subscriber",
        },
    }

    if request.args.get("library"):
        tasks = list()
        tasks.append(
            response(
                {
                    "method": "user.getTopArtists",
                    "username": username,
                    "limit": 1,
                    "autocorrect": 1,
                },
                "topartists",
            )
        )
        tasks.append(
            response(
                {
                    "method": "user.getTopAlbums",
                    "username": username,
                    "limit": 1,
                    "autocorrect": 1,
                },
                "topalbums",
            )
        )
        tasks.append(
            response(
                {
                    "method": "user.getTopTracks",
                    "username": username,
                    "limit": 1,
                    "autocorrect": 1,
                },
                "toptracks",
            )
        )

        artist, album, track = await asyncio.gather(*tasks)
        if artist:
            artist = artist["artist"][0]
            output["library"]["artist"] = {
                "url": artist["url"],
                "name": artist["name"],
                "image": artist["image"][-1]["#text"] or None,
                "plays": int(artist["playcount"]),
            }
        if album:
            album = album["album"][0]
            output["library"]["album"] = {
                "url": album["url"],
                "name": album["name"],
                "image": album["image"][-1]["#text"] or None,
                "plays": int(album["playcount"]),
                "artist": {
                    "url": album["artist"]["url"],
                    "name": album["artist"]["name"],
                },
            }
        if track:
            track = track["track"][0]
            output["library"]["track"] = {
                "url": track["url"],
                "name": track["name"],
                "image": track["image"][-1]["#text"] or None,
                "plays": int(track["playcount"]),
                "artist": {
                    "url": track["artist"]["url"],
                    "name": track["artist"]["name"],
                },
            }

    return (
        jsonify(output),
        200,
    )


@router.get(
    "/nowplaying",
    # name="Get Last.fm Now Playing",
    # description="Get a Last.fm user's currently playing track",
    # parameters={
    #    "username": "Last.fm username",
    # },
)
async def nowplaying():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    tracks = await response(
        {
            "method": "user.getRecentTracks",
            "username": username,
            "limit": 1,
            "autocorrect": 1 if request.args.get("simple") else 0,
        },
        "recenttracks",
    )
    track, _track = tracks["track"][0], tracks["track"][0]

    if request.args.get("simple"):
        return (
            jsonify(
                {
                    "url": track["url"],
                    "name": track["name"],
                    "image": track["image"][-1]["#text"] or None,
                    "artist": track["artist"]["#text"],
                    "album": track["album"]["#text"] or None,
                }
            ),
            200,
        )

    tasks = list()
    tasks.append(
        response(
            {
                "method": "user.getInfo",
                "username": username,
            },
            "user",
        )
    )
    tasks.append(
        response(
            {
                "method": "track.getInfo",
                "username": username,
                "artist": track["artist"]["#text"],
                "track": track["name"],
                "autocorrect": 1,
            },
            "track",
        )
    )
    tasks.append(
        response(
            {
                "method": "artist.getInfo",
                "username": username,
                "artist": track["artist"]["#text"],
                "autocorrect": 1,
            },
            "artist",
        )
    )
    if track["album"]["#text"]:
        tasks.append(
            response(
                {
                    "method": "album.getInfo",
                    "username": username,
                    "artist": track["artist"]["#text"],
                    "album": track["album"]["#text"],
                    "autocorrect": 1,
                },
                "album",
                null_output=True,
            )
        )
    else:
        tasks.append(null())

    user, track, artist, album = await asyncio.gather(*tasks)

    output = {
        "url": track["url"],
        "name": track["name"],
        "image": {
            "url": _track["image"][-1]["#text"],
            "palette": str(
                await extract_color(
                    router.redis,
                    _track["image"][-1]["#text"],
                )
            ),
        }
        if _track["image"][-1].get("#text")
        else None,
        "plays": int(track["userplaycount"]),
        "playing": not bool(_track.get("date")),
        "artist": {
            "url": artist["url"],
            "name": artist["name"],
            "image": artist["image"][-1]["#text"] or None,
            "plays": int(artist["stats"]["userplaycount"]),
        },
    }
    if album:
        output["album"] = {
            "url": album["url"],
            "name": album["name"],
            "image": album["image"][-1]["#text"] or None,
            "plays": int(album["userplaycount"]),
            "tracks": [
                {
                    "url": _track["url"],
                    "name": _track["name"],
                }
                for _track in album["tracks"]["track"]
            ]
            if album.get("tracks") and not isinstance(album["tracks"]["track"], dict)
            else [],
        }
    output["user"] = {
        "url": user["url"],
        "username": user["name"],
        "full_name": user["realname"] or None,
        "avatar": user["image"][-1]["#text"].replace(".png", ".gif") or None,
        "library": {
            "scrobbles": int(user["playcount"]),
            "artists": int(user["artist_count"]),
            "albums": int(user["album_count"]),
            "tracks": int(user["track_count"]),
        },
        "meta": {
            "registered": user["registered"]["#text"],
            "country": (user["country"] if user["country"] != "None" else None),
            "age": int(user["age"]),
            "pro": user["type"] == "subscriber",
        },
    }

    return (
        jsonify(output),
        200,
    )


@router.get(
    "/recenttracks",
    # name="Get Last.fm Recent Tracks",
    # description="Get a Last.fm user's recently played tracks",
    # parameters={
    #    "username": "Last.fm username",
    #    "artist": "Artist name (optional)",
    #    "limit": "Result limit (default: 10)",
    # },
)
async def recenttracks():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    tracks = await response(
        {
            "method": "user.getRecentTracks",
            "username": username,
            "limit": min(
                (int(request.args.get("limit") or 10) if not request.args.get("artist") else 200),
                1000,
            ),
            "autocorrect": 1,
        },
        "recenttracks",
    )

    if artist := request.args.get("artist"):
        tracks = [track for track in tracks["track"] if track["artist"]["#text"].lower() == artist.lower()]
    else:
        tracks = tracks["track"]

    return (
        jsonify(
            [
                {
                    "url": track["url"],
                    "name": track["name"],
                    "image": track["image"][-1]["#text"] or None,
                    "artist": {
                        "name": track["artist"]["#text"],
                        "url": "https://www.last.fm/music/{}".format(
                            quote(track["artist"]["#text"], safe=""),
                        ),
                    },
                    "album": {
                        "name": track["album"]["#text"],
                        "url": "https://www.last.fm/music/{}/{}".format(
                            quote(track["artist"]["#text"], safe=""),
                            quote(track["album"]["#text"], safe=""),
                        ),
                    }
                    if track["album"]["#text"]
                    else None,
                    "date": int(track["date"]["uts"]) if track.get("date") else None,
                }
                for track in tracks[: int(request.args.get("limit") or 10)]
            ]
        ),
        200,
    )


@router.get(
    "/topartists",
    # name="Get Last.fm Top Artists",
    # description="Get a Last.fm user's top artists",
    # parameters={
    #    "username": "Last.fm username",
    #    "period": "Result tiemframe (default: overall)",
    #    "limit": "Result limit (default: 10)",
    # },
)
async def topartists():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    period = replace_timeframe(request.args.get("period", "overall"))

    data = await response(
        {
            "method": "user.getTopArtists",
            "username": username,
            "period": period,
            "limit": min(int(request.args.get("limit", 10)), 1000),
            "page": 1,
            "autocorrect": 1,
        },
        "topartists",
    )

    return (
        jsonify(
            {
                "artists": [
                    {
                        "url": artist["url"],
                        "name": artist["name"],
                        "image": artist["image"][-1]["#text"] or None,
                        "plays": int(artist["playcount"]),
                    }
                    for artist in data["artist"]
                ],
                "period": replace_timeframe(period, human=True),
            }
        ),
        200,
    )


@router.get(
    "/topalbums",
    # name="Get Last.fm Top Albums",
    # description="Get a Last.fm user's top albums",
    # parameters={
    #    "username": "Last.fm username",
    #    "period": "Result tiemframe (default: overall)",
    #    "limit": "Result limit (default: 10)",
    # },
)
async def topalbums():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    period = replace_timeframe(request.args.get("period", "overall"))

    data = await response(
        {
            "method": "user.getTopAlbums",
            "username": username,
            "period": period,
            "limit": min(int(request.args.get("limit", 10)), 1000),
            "page": 1,
            "autocorrect": 1,
        },
        "topalbums",
    )

    return (
        jsonify(
            {
                "albums": [
                    {
                        "url": album["url"],
                        "name": album["name"],
                        "image": album["image"][-1]["#text"] or None,
                        "artist": {
                            "url": album["artist"]["url"],
                            "name": album["artist"]["name"],
                        },
                        "plays": int(album["playcount"]),
                    }
                    for album in data["album"]
                ],
                "period": replace_timeframe(period, human=True),
            }
        ),
        200,
    )


@router.get(
    "/favorites",
    # name="Get Last.fm Loved Tracks",
    # description="Get a Last.fm user's loved tracks",
    # parameters={
    #    "username": "Last.fm username",
    #    "limit": "Result limit (default: 50)",
    # },
)
async def favorites():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    data = await response(
        {
            "method": "user.getLovedTracks",
            "username": username,
            "limit": min(int(request.args.get("limit", 50)), 1000),
            "page": 1,
            "autocorrect": 1,
        },
        "lovedtracks",
    )

    return (
        jsonify(
            {
                "tracks": [
                    {
                        "url": track["url"],
                        "name": track["name"],
                        "image": track["image"][-1]["#text"] or None,
                        "artist": {
                            "name": track["artist"]["name"],
                            "url": "https://www.last.fm/music/{}".format(
                                quote(track["artist"]["name"], safe=""),
                            ),
                        },
                        "date": int(track["date"]["uts"]),
                    }
                    for track in data["track"]
                ]
            }
        ),
        200,
    )


@router.get(
    "/toptracks",
    # name="Get Last.fm Top Tracks",
    # description="Get a Last.fm user's top tracks",
    # parameters={
    #    "username": "Last.fm username",
    #    "period": "Result tiemframe (default: overall)",
    #    "limit": "Result limit (default: 10)",
    # },
)
async def toptracks():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    period = replace_timeframe(request.args.get("period", "overall"))

    data = await response(
        {
            "method": "user.getTopTracks",
            "username": username,
            "period": period,
            "limit": min(int(request.args.get("limit", 10)), 1000),
            "page": 1,
            "autocorrect": 1,
        },
        "toptracks",
    )

    return (
        jsonify(
            {
                "tracks": [
                    {
                        "url": track["url"],
                        "name": track["name"],
                        "image": track["image"][-1]["#text"] or None,
                        "artist": {
                            "url": track["artist"]["url"],
                            "name": track["artist"]["name"],
                        },
                        "plays": int(track["playcount"]),
                    }
                    for track in data["track"]
                ],
                "period": replace_timeframe(period, human=True),
            }
        ),
        200,
    )


@router.get(
    "/collage",
    # name="Generate Last.fm Collage",
    # description="Generate a collage of a Last.fm user's top albums",
    # parameters={
    #    "username": "Last.fm username",
    #    "period": "Result tiemframe (default: overall)",
    #    "size": "Collage size (default: 3x3)",
    # },
)
async def collage():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    period = replace_timeframe(request.args.get("period", "overall"))
    row, col = replace_size(request.args.get("size", "3x3"))

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://lastcollage.io/api/collage",
            json={
                "username": username,
                "type": "albums",
                "period": replace_timeframe(period, collage=True),
                "rowNum": row,
                "colNum": col,
                "showName": "false",
                "hideMissing": "true",
            },
        ) as response:
            data = await response.json()

            if message := data.get("message"):
                raise ValueError(message)

            return jsonify(
                {
                    "url": "https://blob.wock.cloud/collage" + data["path"].split("images")[1].split(".webp")[0],
                    "period": replace_timeframe(period, human=True),
                }
            )

            async with session.get("https://lastcollage.io/" + data["path"]) as response:
                return await send_file(
                    io.BytesIO(await response.read()),
                    mimetype="image/png",
                )


@router.get(
    "/artist/search",
    # name="Search Last.fm Artist",
    # description="Search for an artist on Last.fm",
    # parameters={
    #    "username": "Last.fm username",
    #    "artist": "Artist name",
    # },
)
async def artist_search():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    artist = request.args.get("artist")
    if not artist:
        raise ValueError("Parameter 'artist' is required.")

    data = await response(
        {
            "method": "artist.search",
            "artist": artist,
            "limit": 1,
        },
        "results",
    )
    if not data["artistmatches"]["artist"]:
        raise ValueError("Artist not found", 404)

    artist = data["artistmatches"]["artist"][0]

    data = await response(
        {
            "method": "artist.getInfo",
            "username": username,
            "artist": artist["name"],
            "autocorrect": 1,
        },
        "artist",
    )

    return (
        jsonify(
            {
                "url": data["url"],
                "name": data["name"].replace("LUCKI", "Lucki"),
                "image": data["image"][-1]["#text"] or None,
                "plays": int(data["stats"]["userplaycount"]),
            }
        ),
        200,
    )


@router.get(
    "/album/search",
    # name="Search Last.fm album",
    # description="Search for an album on Last.fm",
    # parameters={
    #    "username": "Last.fm username",
    #    "album": "Album name",
    #    "artist": "Artist name (optional)",
    # },
)
async def album_search():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    album = request.args.get("album")
    if not album:
        raise ValueError("Parameter 'album' is required.")

    artist = request.args.get("artist")
    if not artist:
        data = await response(
            {
                "method": "album.search",
                "album": album,
                "limit": 1,
            },
            "results",
        )
        if not data["albummatches"]["album"]:
            raise ValueError("Album not found", 404)

        album = data["albummatches"]["album"][0]["name"]
        artist = data["albummatches"]["album"][0]["artist"]

    data = await response(
        {
            "method": "album.getInfo",
            "username": username,
            "album": album,
            "artist": artist,
            "autocorrect": 1,
        },
        "album",
    )
    if not data:
        raise ValueError("Album not found", 404)

    return (
        jsonify(
            {
                "url": data["url"],
                "name": data["name"],
                "artist": data["artist"].replace("LUCKI", "Lucki"),
                "image": data["image"][-1]["#text"] or None,
                "plays": int(data["userplaycount"]),
            }
        ),
        200,
    )


@router.get(
    "/track/search",
    # name="Search Last.fm Track",
    # description="Search for a track on Last.fm",
    # parameters={
    #    "username": "Last.fm username",
    #    "track": "Track name",
    #    "artist": "Artist name (optional)",
    # },
)
async def track_search():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    track = request.args.get("track")
    if not track:
        raise ValueError("Parameter 'track' is required.")

    artist = request.args.get("artist")
    if not artist:
        data = await response(
            {
                "method": "track.search",
                "track": track,
                "limit": 1,
            },
            "results",
        )
        if not data["trackmatches"]["track"]:
            raise ValueError("Track not found", 404)

        track = data["trackmatches"]["track"][0]["name"]
        artist = data["trackmatches"]["track"][0]["artist"]

    data = await response(
        {
            "method": "track.getInfo",
            "username": username,
            "track": track,
            "artist": artist,
            "autocorrect": 1,
        },
        "track",
    )
    if not data:
        raise ValueError("Track not found", 404)

    return (
        jsonify(
            {
                "url": data["url"],
                "name": data["name"],
                "artist": data["artist"]["name"],
                "image": data["album"]["image"][-1]["#text"] or None if data.get("album") else None,
                "plays": int(data["userplaycount"]),
            }
        ),
        200,
    )


@router.get(
    "/library/artists",
    # name="Index Last.fm Artist Library",
    # description="Index a Last.fm user's artist library",
    # parameters={
    #    "username": "Last.fm username",
    # },
)
async def library_artists():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    data = await response(
        {
            "method": "user.getTopArtists",
            "username": username,
            "limit": 1000,
            "page": 1,
            "autocorrect": 1,
        },
        "topartists",
    )
    pages = int(data["@attr"]["totalPages"])

    artists = list()
    artists.extend(
        [
            {
                "name": artist["name"],
                "plays": int(artist["playcount"]),
            }
            for artist in data["artist"]
        ]
    )

    if pages > 1:
        tasks = list()
        for page in range(2, pages + 1):
            tasks.append(
                response(
                    {
                        "method": "user.getTopArtists",
                        "username": username,
                        "limit": 1000,
                        "page": page,
                        "autocorrect": 1,
                    },
                    "topartists",
                )
            )
        data = await asyncio.gather(*tasks)
        for item in data:
            artists.extend(
                [
                    {
                        "name": artist["name"],
                        "plays": int(artist["playcount"]),
                    }
                    for artist in item["artist"]
                ]
            )

    return (
        jsonify(artists),
        200,
    )


@router.get(
    "/library/albums",
    # name="Index Last.fm Album Library",
    # description="Index a Last.fm user's album library",
    # parameters={
    #    "username": "Last.fm username",
    # },
)
async def library_albums():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    data = await response(
        {
            "method": "user.getTopAlbums",
            "username": username,
            "limit": 1000,
            "page": 1,
            "autocorrect": 1,
        },
        "topalbums",
    )
    pages = int(data["@attr"]["totalPages"])

    albums = list()
    albums.extend(
        [
            {
                "artist": album["artist"]["name"],
                "name": album["name"],
                "plays": int(album["playcount"]),
            }
            for album in data["album"]
        ]
    )

    if pages > 1:
        tasks = list()
        for page in range(2, pages + 1):
            tasks.append(
                response(
                    {
                        "method": "user.getTopAlbums",
                        "username": username,
                        "limit": 1000,
                        "page": page,
                        "autocorrect": 1,
                    },
                    "topalbums",
                )
            )
        data = await asyncio.gather(*tasks)
        for item in data:
            albums.extend(
                [
                    {
                        "artist": album["artist"]["name"],
                        "name": album["name"],
                        "plays": int(album["playcount"]),
                    }
                    for album in item["album"]
                ]
            )

    return (
        jsonify(albums),
        200,
    )


@router.get(
    "/library/tracks",
    # name="Index Last.fm Track Library",
    # description="Index a Last.fm user's track library",
    # parameters={
    #    "username": "Last.fm username",
    # },
)
async def library_tracks():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    data = await response(
        {
            "method": "user.getTopTracks",
            "username": username,
            "limit": 1000,
            "page": 1,
            "autocorrect": 1,
        },
        "toptracks",
    )
    pages = int(data["@attr"]["totalPages"])

    tracks = list()
    tracks.extend(
        [
            {
                "artist": track["artist"]["name"],
                "name": track["name"],
                "plays": int(track["playcount"]),
            }
            for track in data["track"]
        ]
    )

    if pages > 1:
        tasks = list()
        for page in range(2, pages + 1):
            tasks.append(
                response(
                    {
                        "method": "user.getTopTracks",
                        "username": username,
                        "limit": 1000,
                        "page": page,
                        "autocorrect": 1,
                    },
                    "toptracks",
                )
            )
        data = await asyncio.gather(*tasks)
        for item in data:
            tracks.extend(
                [
                    {
                        "artist": track["artist"]["name"],
                        "name": track["name"],
                        "plays": int(track["playcount"]),
                    }
                    for track in item["track"]
                ]
            )

    return (
        jsonify(tracks),
        200,
    )


async def response(payload: dict, parameter: str = None, **kwargs: dict):
    autocorrect = payload.pop("autocorrect", 0)
    payload.update(
        {
            "api_key": random.choice(router.config["api"].get("lastfm")),
            "format": "json",
            "autocorrect": 0,
        }
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://ws.audioscrobbler.com/2.0/",
            params=payload,
        ) as response:
            if not response.ok:
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    raise ValueError("Last.fm API appears to be down", 503)
                else:
                    if kwargs.get("null_output"):
                        return None
                    else:
                        raise ValueError(data["message"], response.status)
            elif response.status == 429:
                raise ValueError("Last.fm API rate limit exceeded", 429)
            else:
                data = await response.json()
                if parameter and not data.get(parameter):
                    raise ValueError("Last.fm API returned an empty response", 404)

                if autocorrect:
                    data = json.dumps(data)
                    data = replace_artist(
                        data,
                        "Lucky Twice",
                        "Lucki",
                    )
                    data = replace_artist(
                        data,
                        "LUCKI",
                        "Lucki",
                    )
                    data = replace_artist(
                        data,
                        "yeat",
                        "Yeat",
                    )
                    data = replace_artist(
                        data,
                        "Ken Car$on",
                        "Ken Carson",
                    )
                    data = replace_artist(
                        data,
                        "SLEEPY HALLOW",
                        "Sleepy Hallow",
                    )
                    data = replace_artist(
                        data,
                        "LIL TRACY",
                        "Lil Tracy",
                    )
                    data = json.loads(data)
                return data if not parameter else data[parameter]


def replace_artist(text: str, source: str, output: str):
    return (
        text.replace(f'"artist": "{source}"', f'"artist": "{output}"')
        .replace(f'"name": "{source}"', f'"name": "{output}"')
        .replace(f'"#text": "{source}"', f'"#text": "{output}"')
    )


def replace_timeframe(period: str, human: bool = False, collage: bool = False):
    period = period.lower().replace(" ", "")
    if not human:
        if period in (
            "weekly",
            "week",
            "1week",
            "7days",
            "7day",
            "7ds",
            "7d",
        ):
            period = "7day" if not collage else "1week"
        elif period in (
            "monthly",
            "month",
            "1month",
            "1m",
            "30days",
            "30day",
            "30ds",
            "30d",
        ):
            period = "1month"
        elif period in (
            "3months",
            "3month",
            "3ms",
            "3m",
            "90days",
            "90day",
            "90ds",
            "90d",
        ):
            period = "3month"
        elif period in (
            "halfyear",
            "6months",
            "6month",
            "6mo",
            "6ms",
            "6m",
            "180days",
            "180day",
            "180ds",
            "180d",
        ):
            period = "6month"
        elif period in (
            "yearly",
            "year",
            "yr",
            "1year",
            "1y",
            "12months",
            "12month",
            "12mo",
            "12ms",
            "12m",
            "365days",
            "365day",
            "365ds",
            "365d",
        ):
            period = "12month" if not collage else "1year"
        else:
            period = "overall" if not collage else "forever"
    else:
        if period == "7day":
            period = "weekly"
        elif period == "1month":
            period = "monthly"
        elif period == "3month":
            period = "past 3 months"
        elif period == "6month":
            period = "past 6 months"
        elif period == "12month":
            period = "yearly"
        else:
            period = "overall"

    return period


def replace_size(size: str):
    if not "x" in size:
        raise ValueError("Collage size invalid")
    if not len(size.split("x")) == 2:
        raise ValueError("Collage size invalid")
    row, col = size.split("x")
    if not row.isdigit() or not col.isdigit():
        raise ValueError("Collage size invalid")
    if (int(row) + int(col)) < 2:
        raise ValueError("Collage size is too small")
    elif (int(row) + int(col)) > 20:
        raise ValueError("Collage size is too large")

    return (
        int(row),
        int(col),
    )


async def null():
    return None
