import sys


sys.path.append("../")

import asyncio
import json
import random

from datetime import datetime
from functools import wraps
from urllib import parse

import aiohttp
import pytube

from bs4 import BeautifulSoup
from instaloader import Instaloader, Post
from markdownify import markdownify as md
from quart import Blueprint, jsonify, request, websocket
from xxhash import xxh64_hexdigest

from helpers import regex


router = Blueprint("dev", __name__, subdomain="dev")
instagram = Instaloader(quiet=True, sleep=False, max_connection_attempts=1)
tiktok_lock = asyncio.Lock()


@router.before_request
async def before_request():
    if not "/shard" in str(request.url):
        authorizzation = request.headers.get("Authorization") or request.args.get("authorization")
        if not authorizzation == router.config["api"].get("wock"):
            raise ValueError("This API is private.")


@router.after_request
async def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
    return response


@router.route("/", methods=["GET"])
async def index():
    routes = [f"{route.rule}" for route in router.app.url_map.iter_rules() if route.subdomain and route.subdomain == "dev" and route.rule != "/"]
    return (
        jsonify(
            {
                "routes": [str(route) for route in routes],
                "support": "https://wock.cloud/discord",
            }
        ),
        200,
    )


@router.get(
    "/shard/status",
)
async def shard_status():
    data = await router.ipc.request("shard")

    return jsonify(data["shard"])


@router.get(
    "/shard/commands",
)
async def shard_commands():
    data = await router.ipc.request("shard_commands")

    return jsonify(data["shard"])


@router.get(
    "/shard/avatars",
)
async def shard_avatars():
    user_id = request.args.get("user_id")
    if not user_id:
        raise ValueError("Parameter 'user_id' is required.")

    data = await router.ipc.request("avatars", user_id=user_id)
    if error := data.get("error"):
        raise ValueError(error)

    return jsonify(data)


@router.get(
    "/google/ocr",
    # name="Google Optical Character Recognition",
    # description="Extract text from images using Google Cloud Vision API.",
    # parameters={
    #     "content": "The content to extract text from.",
    # },
)
async def google_ocr():
    content = request.args.get("content") or request.args.get("url") or request.args.get("uri")

    if not content:
        raise ValueError("Parameter 'content' is required.")

    key = f"vision:{xxh64_hexdigest(content)}"
    output = await router.redis.get(key) or dict()

    if not output:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://vision.googleapis.com/v1/images:annotate",
                params=dict(key=router.config["api"].get("gcloud")),
                json={
                    "requests": [
                        {
                            "image": {"source": {"imageUri": content}},
                            "features": [{"type": "TEXT_DETECTION"}],
                        }
                    ]
                },
            ) as response:
                data = await response.json()

                if response.status != 200:
                    raise ValueError(data["error"]["message"])

                output = {
                    "text": data["responses"][0]["textAnnotations"][0]["description"],
                    "vertices": data["responses"][0]["textAnnotations"][0]["boundingPoly"]["vertices"],
                }

            await router.redis.set(key, output, ex=86400)
    else:
        output["cached"] = True

    return jsonify(output), 200


@router.get(
    "/pinterest/pin",
    # name="Get Pinterest Pin",
    # description="Download a Pinterest pin. Assets are redistributed via wock-CDN",
    # parameters={
    #     "content": "The content to download.",
    # },
)
async def pinterest_pin():
    content = request.args.get("content") or request.args.get("url") or request.args.get("uri")

    if not content:
        raise ValueError("Parameter 'content' is required.")

    match = regex.PINTEREST_PIN_URL.match(content) or regex.PINTEREST_PIN_APP_URL.match(content)
    if not match:
        raise ValueError("Invalid Pinterest URL.")

    async with aiohttp.ClientSession() as session:
        if regex.PINTEREST_PIN_APP_URL.match(content):
            async with session.get(match.group()) as response:
                match = regex.PINTEREST_PIN_URL.match(str(response.url))
                if not match:
                    raise ValueError("Invalid Pinterest URL.")

        async with session.get(
            "https://www.pinterest.com/resource/PinResource/get/",
            params=dict(
                source_url=match.group(),
                data=json.dumps(
                    {
                        "options": {
                            "id": match.group(1),
                            "field_set_key": "unauth_react_main_pin",
                            "add_connection_type": False,
                            "fetch_pin_join_by_default": True,
                        },
                        "context": {},
                    }
                ),
            ),
        ) as response:
            if response.status != 200:
                raise ValueError("Invalid Pinterest URL.")

            data = await response.json()

    pin = data["resource_response"]["data"]

    output = {
        "url": match.group(),
        "id": int(pin["id"]),
        "title": pin.get("title") or pin.get("description"),
        "created_at": pin["created_at"],
        "media": {},
        "user": {
            "url": f"https://www.pinterest.com/{pin['pinner']['username']}/",
            "id": int(pin["pinner"]["id"]),
            "username": pin["pinner"]["username"],
            "display_name": pin["pinner"]["full_name"],
            "avatar": pin["pinner"]["image_medium_url"],
        },
        "statistics": {
            "comments": pin["aggregated_pin_data"]["comment_count"],
            "saves": pin["aggregated_pin_data"]["aggregated_stats"]["saves"],
        },
    }

    if videos := pin.get("videos"):
        video = videos["video_list"]["V_720P"]
        output["media"] = {
            "type": "video",
            "url": video["url"],
        }
    elif story_pin := pin.get("story_pin_data"):
        block = story_pin["pages"][0]["blocks"][0]
        if block["type"] == "story_pin_video_block":
            # Get first video from video.video_list dict using key
            video = list(block["video"]["video_list"].values())[0]
            output["media"] = {
                "type": "video",
                "url": video["url"],
            }
        elif block["type"] == "story_pin_image_block":
            image = block["images"]["orig"]
            output["media"] = {
                "type": "image",
                "url": image["url"],
            }

    elif images := pin.get("images"):
        image = images["orig"]
        output["media"] = {
            "type": "image",
            "url": image["url"],
        }

    return jsonify(output), 200


@router.get(
    "/pinterest/profile",
    # name="Get Pinterest Profile",
    # description="Download a Pinterest profile. Assets are redistributed via wock-CDN",
    # parameters={
    #     "username": "The username of the user.",
    # },
)
async def pinterest_profile():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")
    else:
        username = username.replace("@", "")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.pinterest.com/resource/UserResource/get/",
            params=dict(
                source_url=f"/{username}/",
                data=json.dumps(
                    {
                        "options": {
                            "field_set_key": "unauth_profile",
                            "username": username,
                            "is_mobile_fork": True,
                        },
                        "context": {},
                    }
                ),
            ),
        ) as response:
            if response.status != 200:
                raise ValueError("Invalid Pinterest username.")

            data = await response.json()

    user = data["resource_response"]["data"]

    return (
        jsonify(
            {
                "url": f"https://www.pinterest.com/{user['username']}/",
                "id": int(user["id"]),
                "username": user["username"],
                "display_name": user["full_name"],
                "avatar": user["image_xlarge_url"],
                "bio": user["about"] or user.get("website_url"),
                "statistics": {
                    "pins": user["pin_count"],
                    "followers": user["follower_count"],
                    "following": user["following_count"],
                },
            }
        ),
        200,
    )


@router.get(
    "/grailed/listing",
    # name="Get Grailed Listing",
    # description="Download a Grailed listing. Assets are redistributed via wock-CDN",
    # parameters={
    #     "content": "The content to download.",
    # },
)
async def grailed_listing():
    content = request.args.get("content") or request.args.get("url") or request.args.get("uri")

    if not content:
        raise ValueError("Parameter 'content' is required.")

    match = regex.GRAILED_LISTING_URL.match(content) or regex.GRAILED_LISTING_APP_URL.match(content)
    if not match:
        raise ValueError("Invalid Grailed URL.")

    async with aiohttp.ClientSession(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"}
    ) as session:
        async with session.get(
            "https://proxy.wock.cloud",
            params=dict(
                url=match.group(),
            ),
        ) as response:
            if response.status != 200:
                raise ValueError("Invalid Grailed URL.")

            data = await response.text()
            soup = BeautifulSoup(data, "html.parser")
            data = soup.find("script", {"id": "__NEXT_DATA__"}).text
            data = json.loads(data)

    listing = data["props"]["pageProps"]["listing"]

    return (
        jsonify(
            {
                "url": match.group(),
                "id": listing["id"],
                "title": listing["title"],
                "description": listing["description"],
                "created_at": listing["createdAt"],
                "price": listing["price"],
                "currency": listing["currency"],
                "size": {
                    "s": "small",
                    "m": "medium",
                    "l": "large",
                    "xl": "extra large",
                }.get(listing["size"], listing["size"]),
                "images": [photo["url"] for photo in listing["photos"]],
                "seller": {
                    "url": "https://grailed.com/" + listing["seller"]["username"],
                    "id": listing["seller"]["id"],
                    "username": listing["seller"]["username"],
                    "bio": listing["seller"]["bio"],
                    "avatar": listing["seller"]["avatarUrl"],
                    "statistics": {
                        "sales": listing["seller"]["sellerScore"]["soldCount"],
                        "followers": listing["seller"]["followerCount"],
                        "following": listing["seller"]["followingCount"],
                    },
                },
            }
        ),
        200,
    )


@router.get(
    "/whi/profile",
    # name="Get WHI Profile",
    # description="Download a We Heart It profile. Assets are redistributed via wock-CDN",
    # parameters={
    #     "username": "The username of the user.",
    # },
)
async def whi_profile():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    async with aiohttp.ClientSession(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"}
    ) as session:
        async with session.get("https://weheartit.com/" + username.replace("@", "")) as response:
            if response.status != 200:
                raise ValueError("Invalid WHI username.")

            data = await response.text()
            soup = BeautifulSoup(data, "html.parser")
            if not soup.find("h1", class_="h1 no-margin text-overflow"):
                raise ValueError("Invalid WHI username.")

    return jsonify(
        {
            "url": str(response.url),
            "username": username.lower().strip().replace("@", ""),
            "display_name": soup.find("h1", class_="h1 no-margin text-overflow").text.strip(),
            "avatar": soup.find("img", class_="avatar").attrs["src"],
            "description": (description.text if (description := soup.find("small", class_="text-gray-dark")) and description.text else None),
            "statistics": {
                "hearts": soup.find("ul", class_="tabs-light tabs-big tabs-xs-scroll header-offset-avatar bg-white")
                .findAll("a")[0]
                .text.strip()
                .split(" ")[0],
                "posts": soup.find("ul", class_="tabs-light tabs-big tabs-xs-scroll header-offset-avatar bg-white")
                .findAll("a")[2]
                .text.strip()
                .split(" ")[0],
                "followers": soup.find("ul", class_="tabs-light tabs-big tabs-xs-scroll header-offset-avatar bg-white")
                .findAll("a")[4]
                .text.strip()
                .split(" ")[0],
                "following": soup.find("ul", class_="tabs-light tabs-big tabs-xs-scroll header-offset-avatar bg-white")
                .findAll("a")[3]
                .text.strip()
                .split(" ")[0],
            },
        }
    )


@router.get(
    "/tiktok/profile",
    # name="Get TikTok Profile",
    # description="Download a TikTok profile. Assets are redistributed via wock-CDN",
    # parameters={
    #     "username": "The username of the user.",
    # },
)
async def tiktok_profile():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    async with aiohttp.ClientSession(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"}
    ) as session:
        async with session.get("https://proxy.wock.cloud?url=https://www.tiktok.com/@" + username.replace("@", "")) as response:
            if response.status != 200:
                raise ValueError("Invalid TikTok username.")

            data = await response.text()
            soup = BeautifulSoup(data, "html.parser")

    return jsonify(
        {
            "url": str(response.url),
            "username": soup.find("h2", class_="tiktok-arkop9-H2ShareTitle ekmpd5l5").text.strip(),
            "nickname": soup.find("h1", class_="tiktok-qpyus6-H1ShareSubTitle ekmpd5l6").text.strip(),
            "avatar": soup.find("img", class_="tiktok-1zpj2q-ImgAvatar e1e9er4e1").attrs["src"],
            "signature": (
                description.text
                if (description := soup.find("h2", class_="tiktok-1n8z9r7-H2ShareDesc e1457k4r3")) and description.text != "No bio yet."
                else None
            ),
            "verified": bool(soup.find("circle", fill="#20D5EC")),
            "statistics": {
                "likes": soup.find(title="Likes").text,
                "followers": soup.find(title="Followers").text,
                "following": soup.find(title="Following").text,
            },
            "videos": [
                {
                    "id": int(video.find("a").attrs["href"].split("/")[5]),
                    "url": video.find("a").attrs["href"],
                }
                for video in soup.findAll("div", class_="tiktok-yz6ijl-DivWrapper e1cg0wnj1")
            ],
        }
    )


@router.get(
    "/tiktok/post",
    # name="Get TikTok Post",
    # description="Download a TikTok post. Assets are redistributed via wock-CDN",
    # parameters={
    #     "content": "The content to download.",
    #     "user_id": "The user ID of the invocation.",
    #     "guild_id": "The guild ID of the invocation.",
    # },
)
async def tiktok_post():
    content = request.args.get("content") or request.args.get("url") or request.args.get("uri")
    user_id = request.args.get("user_id") or request.args.get("user")
    guild_id = request.args.get("guild_id") or request.args.get("guild")

    if not content:
        raise ValueError("Parameter 'content' is required.")
    if not user_id:
        raise ValueError("Parameter 'user_id' is required.")
    if not guild_id:
        raise ValueError("Parameter 'guild_id' is required.")

    match = regex.TIKTOK_MOBILE_URL.match(content) or regex.TIKTOK_DESKTOP_URL.match(content)
    if not match:
        raise ValueError("Invalid TikTok URL.")

    async with tiktok_lock:
        async with aiohttp.ClientSession() as session:
            for _ in range(5):
                async with session.get("https://tikwm.com/api", params={"url": match.group()}) as response:
                    data = await response.json()
                    if response.status == 200:
                        break

                    if "second" in data.get("msg", ""):
                        await asyncio.sleep(1)
                        continue
                    else:
                        raise ValueError("Invalid TikTok URL.")
            else:
                raise ValueError("Invalid TikTok URL.")

    if not data.get("data"):
        raise ValueError("Invalid TikTok URL.")
    else:
        data = data["data"]

    output = {
        "id": data["id"],
        "share_url": f"https://www.tiktok.com/@{data['author']['unique_id']}/video/{data['id']}",
        "caption": data["title"],
        "created_at": datetime.fromtimestamp(data["create_time"]).timestamp(),
        "user": {
            "id": data["author"]["id"],
            "url": f"https://www.tiktok.com/@{data['author']['unique_id']}",
            "username": data["author"]["unique_id"],
            "nickname": data["author"]["nickname"],
            "avatar": data["author"]["avatar"],
        },
        "statistics": {
            "plays": data["play_count"],
            "likes": data["digg_count"],
            "comments": data["comment_count"],
            "shares": data["share_count"],
        },
        "assets": {
            "cover": data["origin_cover"],
            "dynamic_cover": data["cover"],
        },
    }
    if images := data.get("images"):
        output["assets"]["images"] = images
    else:
        output["assets"]["video"] = data["play"]

    return jsonify(output), 200


@router.get(
    "/twitter/post",
    # name="Get Twitter Post",
    # description="Download a Twitter post. Assets are redistributed via wock-CDN",
    # parameters={
    #     "content": "The content to download.",
    #     "user_id": "The user ID of the invocation.",
    #     "guild_id": "The guild ID of the invocation.",
    # },
)
async def twitter_post():
    content = request.args.get("content") or request.args.get("url") or request.args.get("uri")
    user_id = request.args.get("user_id") or request.args.get("user")
    guild_id = request.args.get("guild_id") or request.args.get("guild")

    if not content:
        raise ValueError("Parameter 'content' is required.")
    if not user_id:
        raise ValueError("Parameter 'user_id' is required.")
    if not guild_id:
        raise ValueError("Parameter 'guild_id' is required.")

    match = regex.TWITTER_URL.match(content)
    if not match:
        raise ValueError("Invalid Twitter URL.")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.fxtwitter.com/{match.group('screen_name')}/status/{match.group('id')}") as response:
            data = await response.json()
            if response.status != 200:
                raise ValueError("Invalid Twitter URL.")
            data = data["tweet"]

    return jsonify(
        {
            "id": int(data["id"]),
            "url": data["url"],
            "text": data.get("text"),
            "created_at": data["created_timestamp"],
            "user": {
                "url": f"https://twitter.com/{data['author']['screen_name']}",
                "name": data["author"]["name"],
                "screen_name": data["author"]["screen_name"],
                "avatar": data["author"]["avatar_url"],
            },
            "statistics": {
                "likes": data["likes"],
                "replies": data["replies"],
                "retweets": data["retweets"],
            },
            "assets": {
                "images": [image["url"] for image in data["media"].get("photos", [])],
                "video": [video["url"] for video in data["media"].get("videos", [])][0] if data["media"].get("videos") else None,
            },
        }
    )


@router.get(
    "/instagram/post",
    # name="Get Instagram Post",
    # description="Download an Instagram post, story, or reel. Assets are redistributed via wock-CDN",
    # parameters={
    #     "content": "The content to download.",
    #     "user_id": "The user ID of the invocation.",
    #     "guild_id": "The guild ID of the invocation.",
    # },
)
async def instagram_post():
    content = request.args.get("content") or request.args.get("url") or request.args.get("uri")
    user_id = request.args.get("user_id") or request.args.get("user")
    guild_id = request.args.get("guild_id") or request.args.get("guild")

    if not content:
        raise ValueError("Parameter 'content' is required.")
    if not user_id:
        raise ValueError("Parameter 'user_id' is required.")
    if not guild_id:
        raise ValueError("Parameter 'guild_id' is required.")

    match = regex.INSTAGRAM_URL.match(content)
    if not match:
        raise ValueError("Invalid Instagram URL.")
    shortcode = match.group("shortcode")

    key = f"instagram:{xxh64_hexdigest(shortcode)}"
    output = await router.redis.get(key) or dict()

    if not output:
        if not instagram.context.username:
            instagram.load_session_from_file(router.config["api"].get("instagram"))

        try:
            post = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    Post.from_shortcode,
                    instagram.context,
                    shortcode,
                ),
                timeout=6,
            )
        except Exception as err:
            raise ValueError(f"Invalid Instagram URL. ({err})")

        output = {
            "shortcode": post.shortcode,
            "share_url": f"https://www.instagram.com/p/{post.shortcode}",
            "caption": post.caption,
            "created_at": post.date.timestamp(),
            "user": {
                "id": post.owner_profile.userid,
                "url": f"https://www.instagram.com/{post.owner_username}",
                "name": post.owner_username,
                "avatar": post.owner_profile.profile_pic_url,
            },
            "statistics": {
                "likes": post.likes,
                "comments": post.comments,
            },
            "media": list(),
            "results": post.mediacount,
        }
        if post.is_video:
            output["media"].append(
                {
                    "type": "video",
                    "url": post.video_url,
                }
            )
        else:
            for item in post.get_sidecar_nodes():
                output["media"].append(
                    {
                        "type": "image" if not item.is_video else "video",
                        "url": item.display_url if not item.is_video else item.video_url,
                    }
                )
            if not output["media"] and post.url:
                output["media"].append(
                    {
                        "type": "image",
                        "url": post.url,
                    }
                )
        await router.redis.set(key, output, ex=86400)
    else:
        output["cached"] = True

    if identifier := request.args.get("identifier"):
        if not identifier.isdigit():
            raise ValueError("Invalid identifier.")
        identifier = int(identifier) - 1
        if identifier < 0 or identifier >= len(output["media"]):
            raise ValueError("Invalid identifier.")

        output["media"] = output["media"][identifier]

    return jsonify(output), 200


@router.get(
    "/cashapp/profile",
    # name="Get CashApp Profile",
    # description="Download a CashApp profile. Assets are redistributed via wock-CDN",
    # parameters={
    #     "username": "The username of the user.",
    # },
)
async def cashapp_profile():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://cash.app/$" + username.replace("$", "")) as response:
            if response.status != 200:
                raise ValueError("Invalid CashApp username.")
            data = await response.text()
            soup = BeautifulSoup(data, "html.parser")
            data = soup.findAll("script")[1].text
            data = data.split("var bootstrap = ")[1].split("profile: ")[1].split("}")[0].replace("false", '"false"').replace("true", '"true"') + "}}"
            data = json.loads(data)

    return jsonify(
        {
            "url": f"https://cash.app/{data['formatted_cashtag']}",
            "cashtag": data["formatted_cashtag"],
            "display_name": data["display_name"],
            "country_code": data["country_code"],
            "avatar": {"image_url": data["avatar"].get("image_url"), "accent_color": data["avatar"].get("accent_color")},
            "qr": f"https://cash.app/qr/{data['formatted_cashtag']}",
        }
    )


@router.get(
    "/snapchat/profile",
    # name="Get Snapchat Profile",
    # description="Download a Snapchat profile. Assets are redistributed via wock-CDN",
    # parameters={
    #     "username": "The username of the user.",
    # },
)
async def snapchat_profile():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://story.snapchat.com/add/" + username) as response:
            if response.status != 200:
                raise ValueError("Invalid Snapchat username.")

            data = await response.text()
            soup = BeautifulSoup(data, "html.parser")
            data = soup.find("script", {"id": "__NEXT_DATA__"}).text
            data = json.loads(data)

    user = data["props"]["pageProps"]["userProfile"].get("publicProfileInfo") or data["props"]["pageProps"]["userProfile"].get("userInfo")

    output = {
        "url": f"https://www.snapchat.com/add/{user['username']}",
        "username": user["username"],
        "display_name": user.get("displayName") or user.get("title") or user["username"],
        "snapcode": user["snapcodeImageUrl"].replace("SVG", "PNG"),
        "bitmoji": (user["bitmoji3d"]["avatarImage"].get("url") if user.get("bitmoji3d") else None),
        "bio": user.get("bio"),
        "subscribers": int(user.get("subscriberCount", 0)),
        "stories": list(),
        "highlights": list(),
    }

    if stories := data["props"]["pageProps"].get("story", {}).get("snapList"):
        for story in stories:
            output["stories"].append(
                {
                    "type": "image" if story["snapMediaType"] == 0 else "video",
                    "url": story["snapUrls"]["mediaUrl"],
                }
            )
    if curatedHighlights := data["props"]["pageProps"].get("curatedHighlights", []):
        for curatedHighlight in curatedHighlights:
            for highlight in curatedHighlight.get("snapList", []):
                output["highlights"].append(
                    {
                        "type": "image" if highlight["snapMediaType"] == 0 else "video",
                        "url": highlight["snapUrls"]["mediaPreviewUrl"]["value"],
                    }
                )

    return jsonify(output), 200


@router.get(
    "/youtube/search",
    # name="Search YouTube",
    # description="Search YouTube for videos matching a query.",
    # parameters={
    #     "query": "The query to search for.",
    #     "channel": "Return only channels (default: 0)",
    # },
)
async def youtube_search():
    query = request.args.get("query") or request.args.get("q") or request.args.get("search")
    if not query:
        raise ValueError("Parameter 'query' is required.")

    channel = 1 if request.args.get("channel") else 0

    key = f"youtube:{channel}:{xxh64_hexdigest(query.lower())}"
    bucket = await router.redis.get(key)
    if bucket:
        return (
            jsonify(bucket),
            200,
        )

    async with aiohttp.ClientSession() as session:
        async with session.get(
            (
                "https://www.googleapis.com/youtube/v3/search"
                if not regex.YOUTUBE_CHANNEL_URL.match(query)
                else "https://www.googleapis.com/youtube/v3/channels"
            ),
            params=dict(
                q=query,
                id=(regex.YOUTUBE_CHANNEL_URL.match(query).group("id") if regex.YOUTUBE_CHANNEL_URL.match(query) else ""),
                maxResults=10,
                part="snippet",
                type="video, channel",
                safeSearch="none" if request.args.get("nsfw") else "strict",
                key=random.choice(router.config["api"].get("google")),
            ),
        ) as response:
            data = await response.json()

            results = list()
            for item in data["items"]:
                if data["kind"] == "youtube#channelListResponse":
                    results.append(
                        {
                            "type": "channel",
                            "url": f"https://www.youtube.com/channel/{item['id']}",
                            "channel": {
                                "id": item["id"],
                                "url": f"https://www.youtube.com/channel/{item['id']}",
                                "name": item["snippet"]["title"],
                            },
                        }
                    )
                    continue

                _type = item["id"]["kind"].split("#")[1]

                _item = {
                    "type": _type,
                    "url": f"https://www.youtube.com/{'watch?v=' if _type == 'video' else f'{_type}/'}{item['id'][_type + 'Id']}",
                    "channel": {
                        "id": item["snippet"]["channelId"],
                        "url": f"https://www.youtube.com/channel/{item['snippet']['channelId']}",
                        "name": item["snippet"]["channelTitle"],
                        # "description": item["snippet"]["description"] or None,
                    },
                }
                if _type != "channel":
                    _item["video"] = {
                        "id": item["id"]["videoId"],
                        "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"] or None,
                        "published": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                    }
                results.append(_item)

            if request.args.get("channel"):
                _results = list()
                for result in list(results):
                    if not result["channel"]["id"] in [channel["id"] for channel in _results]:
                        _results.append(result["channel"])
                results = _results

            output = {
                "results": results,
                "total": data["pageInfo"]["totalResults"],
            }
            await router.redis.set(key, output, ex=86400)

            return (
                jsonify(output),
                200,
            )


@router.get(
    "/youtube/video",
    # name="Get YouTube Video",
    # description="Download a YouTube video",
    # parameters={
    #     "content": "The content to download.",
    #     "user_id": "The user ID of the invocation.",
    #     "guild_id": "The guild ID of the invocation.",
    # },
)
async def youtube_video():
    content = request.args.get("content") or request.args.get("url") or request.args.get("uri")
    user_id = request.args.get("user_id") or request.args.get("user")
    guild_id = request.args.get("guild_id") or request.args.get("guild")

    if not content:
        raise ValueError("Parameter 'content' is required.")
    if not user_id:
        raise ValueError("Parameter 'user_id' is required.")
    if not guild_id:
        raise ValueError("Parameter 'guild_id' is required.")

    match = regex.YOUTUBE_URL.match(content) or regex.YOUTUBE_SHORT_URL.match(content) or regex.YOUTUBE_SHORTS_URL.match(content)
    if not match:
        raise ValueError("Invalid YouTube URL.")
    video_url, video_id = match.group(), match.group("id")

    key = f"youtube:video:{xxh64_hexdigest(video_id)}"
    output = await router.redis.get(key) or dict()

    if not output:
        try:
            video = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    pytube.YouTube,
                    video_url,
                ),
                timeout=5,
            )
        except asyncio.TimeoutError:
            raise ValueError("YouTube video timed out.")
        except pytube.exceptions.VideoUnavailable:
            raise ValueError("YouTube video is unavailable.")
        except pytube.exceptions.LiveStreamError:
            raise ValueError("YouTube video is unavailable.")
        except Exception as err:
            raise ValueError(f"Invalid YouTube URL. ({err})")

        stream = (
            video.streams.filter(
                progressive=True,
                file_extension="mp4",
                subtype="mp4",
            )
            .order_by("resolution")
            .desc()
            .first()
        )

        output = {
            "id": video_id,
            "url": video_url,
            "title": video.title,
            "thumbnail": video.thumbnail_url,
            "created_at": video.publish_date.timestamp(),
            "user": {
                "id": video.channel_id,
                "url": video.channel_url,
                "name": video.author,
            },
            "statistics": {
                "views": video.views,
            },
            "download": {
                "fps": stream.fps,
                "bitrate": stream.bitrate,
                "duration": video.length,
                "url": stream.url,
            },
        }

        await router.redis.set(key, output, ex=(stream.expiration - datetime.now()).seconds)
    else:
        output["cached"] = True

    return jsonify(output), 200


@router.get(
    "/github/profile",
    # name="Get GitHub Profile",
    # description="Get information about a GitHub profile.",
    # parameters={
    #     "username": "The username of the user.",
    # },
)
async def github_user():
    username = request.args.get("username") or request.args.get("user")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.github.com/users/" + username,
        ) as response:
            data = await response.json()
            if "message" in data:
                raise ValueError("Invalid username.")

            async with session.get(
                "https://api.github.com/users/" + username + "/repos",
            ) as response:
                repos = await response.json()
                repos = [
                    {
                        "url": repo["html_url"],
                        "name": repo["name"],
                        "description": repo["description"] or None,
                        "language": repo["language"],
                        "created": repo["created_at"][:-1] + "+00:00",
                        "statistics": {
                            "stars": repo["stargazers_count"],
                            "forks": repo["forks_count"],
                            "issues": repo["open_issues_count"],
                            "watchers": repo["watchers_count"],
                        },
                    }
                    for repo in repos
                ]

            return (
                jsonify(
                    {
                        "user": {
                            "id": data["id"],
                            "url": data["html_url"],
                            "name": data["login"],
                            "username": data["name"],
                            "avatar": data["avatar_url"],
                            "bio": data["bio"],
                            "created": data["created_at"][:-1] + "+00:00",
                            "location": {
                                "name": data["location"],
                                "url": "https://maps.google.com/?q=" + parse.quote(data["location"]),
                            }
                            if data["location"]
                            else None,
                            "company": data["company"],
                            "connections": {
                                "email": data["email"],
                                "twitter": data["twitter_username"],
                                "website": data["blog"],
                            },
                            "statistics": {
                                "repos": data["public_repos"],
                                "gists": data["public_gists"],
                                "followers": data["followers"],
                                "following": data["following"],
                            },
                        },
                        "repositories": repos,
                    }
                )
            ), 200


@router.get(
    "/dictionary/define",
    # name="Get Dictionary Information",
    # description="Get information about a word.",
    # parameters={
    #     "word": "The word to search for.",
    # },
)
async def dictionary_define():
    word = request.args.get("word") or request.args.get("query") or request.args.get("search")
    if not word:
        raise ValueError("Parameter 'word' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.dictionaryapi.dev/api/v2/entries/en/" + word,
        ) as response:
            data = await response.json()
            if "title" in data:
                raise ValueError("Invalid word.")

            definition = data[0]["meanings"][0]["definitions"][0]
            for meaning in data[0]["meanings"]:
                for _definition in meaning["definitions"]:
                    if _definition.get("example"):
                        definition = _definition
                        break
            phonetic = data[0]["phonetics"][0]
            for _phonetic in data[0]["phonetics"]:
                if _phonetic.get("text"):
                    phonetic = _phonetic
                    break

            return (
                jsonify(
                    {
                        "url": data[0]["sourceUrls"][0],
                        "word": data[0]["word"],
                        "meaning": {
                            "speech": data[0]["meanings"][0]["partOfSpeech"],
                            "pronunciation": phonetic.get("text"),
                            "pronunciation_url": phonetic.get("sourceUrl"),
                            "definition": definition.get("definition"),
                            "example": definition.get("example"),
                        },
                    }
                ),
                200,
            )


@router.get(
    "/imdb/search",
    # name="Get IMDB Search Results",
    # description="Get search results from IMDB.",
    # parameters={
    #     "query": "The query to search for.",
    # },
)
async def imdb_search():
    query = request.args.get("query") or request.args.get("q") or request.args.get("search")
    if not query:
        raise ValueError("Parameter 'query' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.popcat.xyz/imdb", params=dict(q=query)) as response:
            data = await response.json()
            if "error" in data:
                raise ValueError("Movie not found.")

            return (
                jsonify(
                    {
                        "url": data.get("imdburl"),
                        "title": data.get("title"),
                        "plot": data.get("plot"),
                        "poster": data.get("poster"),
                        "credits": {
                            "director": data.get("director"),
                            "writer": data.get("writer"),
                            "cast": data.get("actors"),
                        },
                        "information": {
                            "country": data.get("country"),
                            "released": data.get("released"),
                            "runtime": data.get("runtime"),
                            "rated": data.get("rated"),
                            "genre": data.get("genre") or data.get("genres"),
                            "series": {"seasons": data.get("totalseasons")} if data.get("series") else False,
                        },
                        "rating": data.get("rating"),
                        "ratings": data.get("ratings"),
                    }
                ),
                200,
            )


@router.get(
    "/genius/lyrics",
    # name="Get Genius Lyrics",
    # description="Get lyrics from Genius.",
    # parameters={
    #     "query": "The query to search for.",
    # },
)
async def genius_lyrics():
    query = request.args.get("query") or request.args.get("q") or request.args.get("search")
    if not query:
        raise ValueError("Parameter 'query' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.genius.com/search",
            params=dict(q=query),
            headers=dict(
                Authorization="Bearer " + router.config["api"].get("genius"),
            ),
        ) as response:
            data = await response.json()
            if not data["response"].get("hits"):
                raise ValueError("No results found.")

            output = {
                "id": data["response"]["hits"][0]["result"]["id"],
                "url": data["response"]["hits"][0]["result"]["url"],
                "title": data["response"]["hits"][0]["result"]["title"],
                "artist": data["response"]["hits"][0]["result"]["primary_artist"]["name"],
                "thumbnail": data["response"]["hits"][0]["result"]["song_art_image_thumbnail_url"],
                "lyrics": [],
            }

            async with session.get(
                f"https://sing.whatever.social{data['response']['hits'][0]['result']['path']}",
            ) as response:
                if response.status != 200:
                    raise ValueError("No results found.")

                data = await response.text(encoding="utf-8")
                soup = BeautifulSoup(data, "html.parser")
                lyrics_filter = soup.find("div", id="lyrics")

                lyrics = md(str(lyrics_filter), strip=["a"])
                output["lyrics"] = lyrics

            return (
                jsonify(output),
                200,
            )


@router.get(
    "/soundcloud/search",
    # name="Get SoundCloud Search Results",
    # description="Get search results from SoundCloud.",
    # parameters={
    #     "query": "The query to search for.",
    # },
)
async def soundcloud_search():
    query = request.args.get("query") or request.args.get("q") or request.args.get("search")
    if not query:
        raise ValueError("Parameter 'query' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api-v2.soundcloud.com/search/tracks", params=dict(q=query), headers=dict(Authorization=router.config["api"].get("soundcloud"))
        ) as response:
            data = await response.json()
            if not data.get("collection"):
                raise ValueError("No results found.")

            return (
                jsonify(
                    [
                        {
                            "url": track["permalink_url"],
                            "title": track["title"],
                            "artist": track["user"]["username"],
                            "thumbnail": track["artwork_url"],
                            "duration": track["duration"],
                            "genre": track["genre"],
                            "plays": track["playback_count"],
                            "likes": track["likes_count"],
                            "reposts": track["reposts_count"],
                            "comments": track["comment_count"],
                        }
                        for track in data["collection"]
                    ]
                ),
                200,
            )


@router.get(
    "/itunes/search",
    # name="Get iTunes Search Results",
    # description="Get search results from iTunes.",
    # parameters={
    #     "query": "The query to search for.",
    # },
)
async def itunes_search():
    query = request.args.get("query") or request.args.get("q") or request.args.get("search")
    if not query:
        raise ValueError("Parameter 'query' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://itunes.apple.com/search",
            params=dict(term=query, media="music", limit=25),
        ) as response:
            data = await response.text()
            data = json.loads(data.strip())
            if not data.get("results"):
                raise ValueError("No results found.")

            return (
                jsonify(
                    [
                        {
                            "url": track["trackViewUrl"],
                            "title": track["trackName"],
                            "artist": track["artistName"],
                            "thumbnail": track["artworkUrl100"],
                            "genre": track["primaryGenreName"],
                        }
                        for track in data["results"]
                    ]
                ),
                200,
            )


@router.get(
    "/minecraft/profile",
    # name="Get Minecraft Profile",
    # description="Get a Minecraft profile.",
    # parameters={
    #     "username": "The username to search for.",
    # },
)
async def minecraft_profile():
    username = request.args.get("username") or request.args.get("user") or request.args.get("name")
    if not username:
        raise ValueError("Parameter 'username' is required.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://playerdb.co/api/player/minecraft/" + username) as response:
            data = await response.json()
            if "error" in data:
                raise ValueError("Invalid username.")

            player = data["data"]["player"]
            return (
                jsonify(
                    {
                        "username": player["username"],
                        "uuid": player["id"],
                        "name_history": player["name_history"],
                        "meta": {
                            "avatar": "https://blob.wock.cloud/minecraft/avatar/" + player["id"],
                            "head": "https://blob.wock.cloud/minecraft/head/" + player["id"],
                            "body": "https://blob.wock.cloud/minecraft/body/" + player["id"],
                        },
                    }
                ),
                200,
            )


music_connections = dict()


def collect_music_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Add ticket logic here later :/
        global music_connections

        guild_id = kwargs.get("guild_id")
        if not guild_id in music_connections:
            music_connections[guild_id] = set()

        music_connections[guild_id].add(websocket._get_current_object())
        try:
            return await func(*args, **kwargs)
        finally:
            music_connections[guild_id].remove(websocket._get_current_object())

    return wrapper


@router.websocket("/socket-OYGNn43REKA8p")
async def socket_recv():
    while True:
        data = await websocket.receive()
        data = json.loads(data)
        payload = data["data"]

        if data["type"] == "PING":
            await websocket.send_json({"type": "PONG"})
        elif data["type"] == "MUSIC":
            if connections := music_connections.get(str(data["guild_id"])):
                for socket in connections:
                    await socket.send_json(payload)


@router.websocket("/music/<guild_id>")
@collect_music_websocket
async def music_socket(guild_id):
    await websocket.accept()

    while True:
        data = await websocket.receive_json()
        if data.get("op") == "PING":
            await websocket.send_json({"op": "PONG"})
