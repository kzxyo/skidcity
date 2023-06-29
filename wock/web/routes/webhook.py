import sys

import aiohttp
import xmltodict


sys.path.append("../")

from quart import Blueprint, jsonify, request


router = Blueprint("webhook", __name__, subdomain="webhook")


@router.route("/", methods=["GET"])
async def index():
    return "get out!!", 200


@router.post(
    "/github/vvk9jcOPBOZL9NfEet6uk1C7uq2yk5",
)
async def github():
    data = await request.get_json()
    if not data["commits"]:
        return "ok, no commits", 200

    await router.ipc.request(
        "webhook",
        event="github",
        info={
            "repository": {
                "name": data["repository"]["full_name"],
                "url": data["repository"]["html_url"],
                "language": data["repository"]["language"],
            },
            "author": {
                "name": data["sender"]["login"],
                "url": data["sender"]["html_url"],
                "avatar": data["sender"]["avatar_url"],
            },
            "commits": [
                {
                    "id": commit["id"],
                    "url": commit["url"],
                    "message": commit["message"],
                    "files": {
                        "added": commit["added"],
                        "removed": commit["removed"],
                        "modified": commit["modified"],
                    },
                }
                for commit in data["commits"]
            ],
        },
    )

    return "ok", 200


@router.route("/youtube/6qlQ31dJgPs9ALXsL94hEyghcKhGRZ", methods=["GET", "POST"])
async def youtube_webhook():
    if request.method == "GET":
        # Verifies the subscription challenge
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == router.config.get("secret"):
            return request.args.get("hub.challenge"), 200
        else:
            return "Invalid request", 404

    elif request.method == "POST":
        # Notifies us of a new video
        data = await request.get_data(as_text=True)
        data = xmltodict.parse(data)  # Converts the XML (yucky) to JSON
        if not data["feed"].get("entry"):
            return "", 200

        data = data["feed"]["entry"]

        await router.ipc.request(
            "dispatch",
            event="youtube_post",
            post={
                "id": data["yt:videoId"],
                "url": "https://youtu.be/" + data["yt:videoId"],
                "title": data["title"],
                "channel": {
                    "id": data["yt:channelId"],
                    "url": data["author"]["uri"],
                    "name": data["author"]["name"],
                },
            },
        )

        return "", 200


@router.post(
    "/youtube/subscribe",
    # parameters={
    #    "channel_id": "The channel ID to subscribe to",
    # },
)
async def youtube_subscribe():
    if not request.args.get("channel_id"):
        raise ValueError("Parameter 'channel_id' is required")

    if request.headers.get("Authorization", "") != router.config.get("secret"):
        raise ValueError("Invalid authorization token")

    channel_id = request.args.get("channel_id")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://pubsubhubbub.appspot.com/subscribe",
            data={
                "hub.callback": f"https://webhook.{router.config.get('domain')}/youtube/6qlQ31dJgPs9ALXsL94hEyghcKhGRZ",
                "hub.topic": f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}",
                "hub.mode": "subscribe",
                "hub.verify": "async",
                "hub.verify_token": router.config.get("secret"),
            },
        ) as resp:
            if resp.status != 202:
                raise ValueError(await resp.text(), resp.status)
            else:
                return (
                    jsonify(
                        {
                            "message": "Subscribed to channel",
                            "channel_id": channel_id,
                        }
                    ),
                    200,
                )


@router.get(
    "/tiktok/callback",
)
async def tiktok_callback():
    if request.args.get("code"):
        print(request.args)
        return "ok", 200
    else:
        return "no code", 400


@router.route(
    "/tiktok/lvEEnYM58CcqSrQ0ukO5uHB2UXOj8q",
    methods=["GET", "POST"],
)
async def tiktok_webhook():
    data = await request.json
    print(data)
    return "ok", 200
