import sys


sys.path.append("../")

import io

import aiohttp

from quart import Blueprint, request, send_file
from xxhash import xxh64_hexdigest

from helpers import regex


router = Blueprint("blob", __name__, subdomain="blob")


@router.route("/", methods=["GET"])
async def index():
    node = "node" + xxh64_hexdigest(request.user_agent.string).upper()[:8]
    return "wock @ " + node


@router.get(
    "/minecraft/avatar/<string:uuid>",
)
async def minecraft_avatar(uuid):
    if uuid := regex.MINECRAFT_UUID.match(uuid):
        uuid = uuid.group(0).strip("-")
    else:
        raise ValueError("Invalid UUID")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://crafatar.com/avatars/{uuid}?overlay=true") as response:
            if response.status == 200:
                image = await response.read()
                return await send_file(
                    io.BytesIO(image),
                    mimetype="image/png",
                )
            else:
                raise ValueError("Invalid UUID")


@router.get(
    "/minecraft/head/<string:uuid>",
)
async def minecraft_head(uuid):
    if uuid := regex.MINECRAFT_UUID.match(uuid):
        uuid = uuid.group(0).strip("-")
    else:
        raise ValueError("Invalid UUID")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://crafatar.com/renders/head/{uuid}") as response:
            if response.status == 200:
                image = await response.read()
                return await send_file(
                    io.BytesIO(image),
                    mimetype="image/png",
                )
            else:
                raise ValueError("Invalid UUID")


@router.get(
    "/minecraft/body/<string:uuid>",
)
async def minecraft_body(uuid):
    if uuid := regex.MINECRAFT_UUID.match(uuid):
        uuid = uuid.group(0).strip("-")
    else:
        raise ValueError("Invalid UUID")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://crafatar.com/renders/body/{uuid}") as response:
            if response.status == 200:
                image = await response.read()
                return await send_file(
                    io.BytesIO(image),
                    mimetype="image/png",
                )
            else:
                raise ValueError("Invalid UUID")


@router.get(
    "/collage/<string:path>",
)
async def collage(path):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://lastcollage.io/images/{path}.webp") as response:
            if response.status == 200:
                image = await response.read()
                return await send_file(
                    io.BytesIO(image),
                    mimetype="image/png",
                )
            else:
                raise ValueError("Invalid path")
